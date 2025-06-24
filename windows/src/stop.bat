@echo off
chcp 65001 > NUL
set PYTHONUTF8=1
set PYTHONIOENCODING=utf8
setlocal enabledelayedexpansion
call src\variables.bat

set FORCE_NO_PYTHON=0
IF "%FORCE_NO_PYTHON%" == "1" (
    set "PYTHON_FOUND=1"
) ELSE (
    where python >nul 2>nul
    set "PYTHON_FOUND=%errorlevel%"
)

if "%PYTHON_FOUND%" neq "0" (
    IF "%HTTP_Server_Runtime%" == "nginx" (
        pushd "packages\%nginx_folder%"
        .\nginx.exe -s quit
        popd
    )
    IF "%HTTP_Server_Runtime%" == "apache" (
        taskkill /F /IM "httpd"
    )
    REM Stop Redis server gracefully
    pushd "packages\%redis_folder%"
    redis-cli.exe shutdown
    popd
    REM Cleanup everything
    pushd "..\src\multi-chat\"
    call php artisan worker:stop
    popd
    taskkill /F /IM "nginx.exe"
    taskkill /F /IM "redis-server.exe"
    taskkill /F /IM "php-cgi.exe"
    taskkill /F /IM "php.exe"
    taskkill /F /IM "node.exe"
    taskkill /F /IM "python.exe"
) else (
    cd "%~dp0"
    python stop.py
)