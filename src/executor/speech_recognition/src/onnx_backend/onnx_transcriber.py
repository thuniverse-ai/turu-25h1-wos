# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# Copyright (c) 2025 Yung-Hsiang Hu. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
import os
import sys
import re
import onnxruntime
import argparse
import time
import glob
import logging
import functools
import zipfile
import numpy as np
from datetime import datetime
from pathlib import Path
from huggingface_hub import hf_hub_download

from qai_hub_models.models._shared.whisper.app import WhisperApp
from qai_hub_models.utils.executable_onnx_model import ExecutableOnnxModel

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)

def parse_model_path(model_path):
    if os.path.isfile(model_path):
        return Path(model_path).resolve()
    regex = r"hf://([^?]+)\?(.*)"
    match = re.match(regex, model_path)
    if not match:
        raise Exception(f"Invalid model_path format: {model_path}")

    repo_id = match.group(1)
    filename = match.group(2)
    downloaded_path = Path(hf_hub_download(repo_id=repo_id, filename=filename))
    logger.debug(f"Downloaded model from HF. Path: {downloaded_path}")

    # Check if the downloaded file is a zip file
    if downloaded_path.suffix.lower() == '.zip':
        logger.info(f"Downloaded file is a zip archive: {downloaded_path}. Extracting...")
        # Create a temporary directory for extraction
        extract_dir = Path(downloaded_path.parent / downloaded_path.stem)
        extract_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created directory for extraction: {extract_dir}")

        try:
            with zipfile.ZipFile(downloaded_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            logger.info(f"Successfully extracted {downloaded_path} to {extract_dir}")
            
            onnx_paths = glob.glob(str(extract_dir / "**/model.onnx"), recursive=True)
            model_paths = [p for p in onnx_paths if Path(p).is_file()]

            if len(model_paths) == 0:
                raise RuntimeError("Zip file does't contain any model.onnx file.")
            if len(model_paths) > 1:
                logger.warning(f"Zip file contained multiple model.onnx files. Using the first one: {model_paths[0]}")
            model_path = Path(model_paths[0]).resolve()
        except zipfile.BadZipFile:
            logger.error(f"Downloaded file {downloaded_path} is not a valid zip file.")
            raise Exception(f"Downloaded file is corrupted or not a valid zip: {downloaded_path}")
        except Exception as e:
            logger.error(f"Error extracting zip file {downloaded_path}: {e}")
            raise Exception(f"Failed to extract zip file {downloaded_path}: {e}")

    else:
        model_path = downloaded_path

    return Path(model_path).resolve()

class OnnxTranscriber:
    """
    Encapsulation of WhisperS2T process for multi-processing.
    """

    def __init__(self, encoder_path, decoder_path):
        self.encoder_path = encoder_path
        self.decoder_path = decoder_path
        self.load_model()

    @functools.lru_cache
    def load_model(self, **model_params):
        if self.encoder_path is None or self.decoder_path is None:
            return None

        logger.debug(
            f"Available Execution Providers: {onnxruntime.get_available_providers()}"
        )
        logger.debug(f"Parameters to load model: {model_params}")
        # Load whisper model
        logger.debug("Loading model...")
        start_time = time.time()
        logger.debug(f"Encoder path: {self.encoder_path}")
        logger.debug(f"Decoder path: {self.decoder_path}")
        whisper = WhisperApp(
            ExecutableOnnxModel.OnNPU(parse_model_path(self.encoder_path)),
            ExecutableOnnxModel.OnNPU(parse_model_path(self.decoder_path)),
            num_decoder_blocks=6,
            num_decoder_heads=8,
            attention_dim=512,
            mean_decode_len=224,
        )
        end_time = time.time()
        logger.debug(f"Model {self.encoder_path}; {self.decoder_path} loaded")
        logger.debug(f"Model loading time: {end_time - start_time:.4f}")
        return whisper

    def transcribe(
        self,
        model_name: str,
        model_backend: str = "ONNX",
        model_params: dict = None,
        audio_files: list = [],
        **transcribe_kwargs,
    ):
        logger.debug("Transcribing...")
        result = None
        try:
            model = self.load_model()
            start_time = time.time()
            text = model.transcribe(audio_files[0])
            end_time = time.time()

            result = {
                "start_time": 0,  # [TODO] Timestamp
                "end_time": 0,
                "text": text,
            }

        except Exception:
            logger.exception("Error when generating transcription")
            raise

        logger.debug("Done transcribing.")
        logger.debug(f"Transcribing time: {end_time - start_time:.4f}")
        return [[result]]
