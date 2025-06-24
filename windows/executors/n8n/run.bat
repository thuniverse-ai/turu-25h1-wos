@echo off

pushd ..\..\src
call variables.bat
popd

:: Set environment variables
set N8N_RUNNERS_ENABLED=true
@REM set N8N_ENDPOINT_WEBHOOK_WAIT=app/com.github.n8n-io.n8n/webhook-waiting
@REM set N8N_ENDPOINT_WEBHOOK_TEST=app/com.github.n8n-io.n8n/webhook-test
@REM set N8N_ENDPOINT_WEBHOOK=app/com.github.n8n-io.n8n/webhook
@REM set N8N_ENDPOINT_REST=rest
@REM set N8N_ENDPOINT_REST=app/com.github.n8n-io.n8n/rest
@REM set N8N_PATH=/app/com.github.n8n-io.n8n/
set N8N_PORT=38788

:: Start n8n
echo Starting n8n.
start /b "" ..\..\packages\%RunHiddenConsole_folder%\x64\RunHiddenConsole.exe n8n