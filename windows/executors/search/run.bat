pushd ..\..\src
call variables.bat
popd
set EXECUTOR_ACCESS_CODE=.tool/kuwa/search
pushd ..\..\..\src\multi-chat
php artisan model:config ".tool/kuwa/search" "Search" --order=990020 --image "..\..\windows\executors\search\SearchQA.png"
popd
pushd ..\..\..\src\executor\docqa\
start /b "" "python" searchqa.py "--access_code" ".tool/kuwa/search" --log debug
popd
