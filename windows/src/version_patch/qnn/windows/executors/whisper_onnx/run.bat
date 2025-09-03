pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model:qnn/qualcomm/whisper
pushd ..\..\..\src\multi-chat
php artisan model:config ".model:qnn/qualcomm/whisper" "Whisper @NPU" --order=130001 --image "..\..\windows\executors\whisper_onnx\whisper.png"
popd
pushd ..\..\..\src\executor\speech_recognition\
start /b "" "python" main.py "--access_code" ".model:qnn/qualcomm/whisper" "--backend" "ONNX" ^
   "--encoder_path" "hf://qualcomm/Whisper-Small-V2?precompiled/qualcomm-snapdragon-x-elite/Whisper-Small-V2_HfWhisperEncoder.onnx.zip" ^
   "--decoder_path" "hf://qualcomm/Whisper-Small-V2?precompiled/qualcomm-snapdragon-x-elite/Whisper-Small-V2_HfWhisperDecoder.onnx.zip" ^
   "--model" "openai/whisper-small" "--log" "debug"
popd
