pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.tool/kuwa/rag
pushd ..\..\..\src\multi-chat
php artisan model:config ".tool/kuwa/rag" "RAG" --image "..\..\windows\executors\rag\loupe.png" --order "990000"
popd
pushd ..\..\..\src\executor\docqa
start /b "" "python" "docqa.py" "--access_code" ".tool/kuwa/rag" --mmr_k 6 --mmr_fetch_k 12 --limit 3072
popd
