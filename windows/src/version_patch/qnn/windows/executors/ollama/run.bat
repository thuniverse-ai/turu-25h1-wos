pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.model:ollama
pushd ..\..\..\src\multi-chat
php artisan model:config ".model:ollama" "Ollama" --order=318000 --image "..\..\windows\executors\ollama\ollama.png" --do_not_create_bot
popd
start /b "" "kuwa-executor" "ollama" "--access_code" ".model:ollama" "--ollama_host" "http://127.0.0.1:11434" "--model" "llama3.2"