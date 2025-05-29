pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model:qnn/qualcomm/stable-diffusion
pushd ..\..\..\src\multi-chat
php artisan model:config ".model:qnn/qualcomm/stable-diffusion" "Painter @NPU" --order=120001 --image "..\..\windows\executors\qnn-stable-diffusion\sd_qnn.png"
popd
start /b "" "python" .\main.py "--access_code" ".model:qnn/qualcomm/stable-diffusion" "--model_version" "SD_1_5"
