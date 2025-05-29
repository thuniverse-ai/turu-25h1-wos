pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model:qnn
pushd ..\..\..\src\multi-chat
php artisan model:config ".model:qnn" "Qualcomm QNN Genie" --order=110001 --image "..\..\windows\executors\qnn-genie\snapdragon-x.jpg" --do_not_create_bot
popd
pushd ..\..\..\src\executor\qnn_genie
start /b "" "python" main.py "--access_code" ".model:qnn" --log debug 
popd