@echo off
echo Downloading pre-integrated NPU-based models.

huggingface-cli download thuniverse-ai/Llama-v3.2-3B-Chat-GENIE
huggingface-cli download thuniverse-ai/Llama-v3.1-8B-Chat-GENIE
huggingface-cli download thuniverse-ai/Phi-3.5-Mini-Instruct-GENIE 
huggingface-cli download thuniverse-ai/TAIDE-LX-8B-Chat-GENIE
huggingface-cli download --revision "d6d71e0" qualcomm/Whisper-Base-En Whisper-Base-En_WhisperDecoderInf.onnx.zip
huggingface-cli download --revision "d6d71e0" qualcomm/Whisper-Base-En Whisper-Base-En_WhisperEncoderInf.onnx.zip