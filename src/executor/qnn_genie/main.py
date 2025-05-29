import os
import sys
import gc
import logging
import contextlib
from pathlib import Path
from transformers import AutoTokenizer
from functools import lru_cache
import multiprocessing as mp
from dataclasses import dataclass

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(Path(__file__).parent)))

from kuwa.executor import LLMExecutor, Modelfile
from qai_appbuilder.geniecontext import GenieContext
from huggingface_hub import snapshot_download

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger(__name__)


class DecodeBuffer:
    """
    Decodes a byte stream, handling partial decoding.
    """

    def __init__(self, coding="utf-8"):
        self.coding = coding
        self.buffer = bytearray()

    def push(self, chunk: bytes):
        """
        Adds a chunk to buffer and decode partially.

        Args:
            chunk: The byte chunk to add.

        Returns:
            The decoded UTF-8 string (as much as possible)
        """
        self.buffer += chunk
        decoded_string = ""
        i = len(self.buffer)
        while i > 0:
            try:
                decoded_string = self.buffer[:i].decode(self.coding)
                break
            except UnicodeDecodeError:
                i -= 1
        self.buffer = self.buffer[i:]
        return decoded_string

    def finalize(self, chunk: bytes = b""):
        self.buffer += chunk
        if len(self.buffer) != 0:
            logger.debug(f"[DecodeBuffer] undecoded buffer content: {self.buffer}")
        return self.buffer.decode(self.coding, "replace")


@contextlib.contextmanager
# temporarily change to a different working directory
def temporaryWorkingDirectory(path):
    old_wd = os.getcwd()
    os.chdir(os.path.abspath(path))
    try:
        yield
    finally:
        os.chdir(old_wd)


class ModelLoader:
    """
    Model loader with LRU cache and memory release management.
    """

    def __init__(self, cache_size=1):
        self.cached_model = {}
        self.cache_size = cache_size

    def load_model(self, model_path_or_id):
        if os.path.exists(model_path_or_id):
            model_dir = model_path_or_id
        else:
            print(
                f"Model path {model_path_or_id} not found. Trying download it from HF Hub.",
                flush=True,
            )
            model_dir = snapshot_download(repo_id=model_path_or_id)

        model = self.cached_model.pop(model_dir, None)
        if model is None:
            if len(self.cached_model) >= self.cache_size:
                self._unload_least_used_model()

            with temporaryWorkingDirectory(model_dir):
                model = GenieContext("genie_config.json")

        self.cached_model[model_dir] = model

        return model

    def _unload_least_used_model(self):
        least_use_model_id = next(iter(self.cached_model))
        model_to_free = self.cached_model.pop(least_use_model_id)
        model_to_free.Release()
        del model_to_free
        gc.collect()
        print(f"Unloaded {least_use_model_id}", flush=True)


@dataclass
class Work:
    model_id: str = ""
    prompt: str = ""


def producer_process(
    work_queue: mp.Queue,
    resp_queue: mp.Queue,
    stop: mp.Event,
    debug: bool,
    cache_size: int,
):
    model_loader = ModelLoader(cache_size=cache_size)

    def genie_callback(result):
        nonlocal resp_queue
        if debug:
            print(result, end="", flush=True)
        resp_queue.put_nowait(result)
        return bool(stop.is_set())

    while True:
        work = work_queue.get()
        print(f"producer_process(): Got work: {str(work)}", flush=True)
        model_id = work.model_id
        prompt = work.prompt
        model = model_loader.load_model(model_id)
        if prompt == "":
            continue
        model.Query(prompt=prompt, callback=genie_callback)
        resp_queue.put_nowait("")  # EOF
        stop.clear()
        print("producer_process(): Done", flush=True)


class QnnGenieExecutor(LLMExecutor):
    def __init__(self):
        super().__init__()

    def extend_arguments(self, parser):
        parser.add_argument(
            "--tokenizer",
            type=str,
            default="thuniverse-ai/Llama-v3.2-3B-Chat-GENIE",
            help="HF repository ID of the default tokenizer.",
        )
        parser.add_argument(
            "--model",
            type=str,
            default="thuniverse-ai/Llama-v3.2-3B-Chat-GENIE",
            help="Path or HF repository ID of default model",
        )
        parser.add_argument(
            "--cache_size",
            type=int,
            default=1,
            help="How many models can be loaded to memory simultaneously.",
        )

    def setup(self):
        self.model_id = self.args.model
        self.hf_hub_model_id = self.args.tokenizer
        self.stop = mp.Event()
        self.tokenizer = self.get_tokenizer(self.hf_hub_model_id)
        self.cmd_queue = mp.Queue()
        self.resp_queue = mp.Queue()
        self.producer_proc = mp.Process(
            target=producer_process,
            args=(
                self.cmd_queue,
                self.resp_queue,
                self.stop,
                self.in_debug(),
                self.args.cache_size,
            ),
        )
        self.producer_proc.start()
        work = Work(model_id=self.model_id, prompt="")
        logger.info(f"Put work: {str(work)}")
        self.cmd_queue.put_nowait(work)

    @lru_cache
    def get_tokenizer(self, hf_hub_model_id):
        tokenizer = AutoTokenizer.from_pretrained(hf_hub_model_id)
        return tokenizer

    async def llm_compute(self, history: list[dict], modelfile: Modelfile):
        model_id = modelfile.parameters["llm_"].get("model", self.model_id)
        tokenizer_id = modelfile.parameters["llm_"].get(
            "tokenizer", self.hf_hub_model_id
        )

        # Apply modelfile
        msg = modelfile.messages + history
        if modelfile.override_system_prompt is not None:
            msg = [
                {"content": modelfile.override_system_prompt, "role": "system"}
            ] + msg

        msg[-1]["content"] = (
            modelfile.before_prompt + msg[-1]["content"] + modelfile.after_prompt
        )

        self.tokenizer = self.get_tokenizer(tokenizer_id)
        prompt = self.tokenizer.apply_chat_template(
            msg, tokenize=False, add_generation_prompt=True
        )

        # Clear queue and event
        while not self.resp_queue.empty():
            self.resp_queue.get(False, 0)
        self.stop.clear()

        # Put work
        work = Work(model_id=model_id, prompt=prompt)
        logger.info(f"Put work: {str(work)}")
        self.cmd_queue.put(work)

        # Get result
        while not self.stop.is_set():
            resp = self.resp_queue.get()
            if resp == "":
                break
            yield resp

        logger.info("Done")

    async def abort(self):
        self.stop.set()
        logger.debug("aborted")
        return "Aborted"


if __name__ == "__main__":
    executor = QnnGenieExecutor()
    executor.run()
