pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model:qnn/qualcomm/whisper
pushd ..\..\..\src\multi-chat
php artisan model:config ".model:qnn/qualcomm/whisper" "Whisper @NPU" --order=130001 --image "..\..\windows\executors\whisper_onnx\whisper.png"
popd
pushd ..\..\..\src\executor\speech_recognition\
start /b "" "python" main.py "--access_code" ".model:qnn/qualcomm/whisper" "--model" "base" "--use_onnx" "--encoder_path" "hf://qualcomm/Whisper-Base-En?Whisper-Base-En_WhisperEncoderInf.onnx" "--decoder_path" "hf://qualcomm/Whisper-Base-En?Whisper-Base-En_WhisperDecoderInf.onnx"  "--log" "debug"
popd
