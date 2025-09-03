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
    set "PYTHON_FOUND=!errorlevel!"
)

if "!PYTHON_FOUND!" neq "0" (
    ECHO Python not found, stopping services manually...
    IF "%HTTP_Server_Runtime%" == "nginx" (
        pushd "packages\%nginx_folder%"
        .\nginx.exe -s quit
        popd
    )
    IF "%HTTP_Server_Runtime%" == "apache" (
        taskkill /F /IM "httpd.exe" /T >nul 2>&1
    )
    REM Stop Redis server gracefully
    pushd "packages\%redis_folder%"
    redis-cli.exe shutdown
    popd
    REM Cleanup everything
    pushd "..\src\multi-chat\"
    call php artisan worker:stop
    popd
    echo Force stopping any remaining processes.
    taskkill /F /IM "nginx.exe" /T >nul 2>&1
    taskkill /F /IM "redis-server.exe" /T >nul 2>&1
    taskkill /F /IM "php-cgi.exe" /T >nul 2>&1
    taskkill /F /IM "php.exe" /T >nul 2>&1
    taskkill /F /IM "node.exe" /T >nul 2>&1
    taskkill /F /IM "python.exe" /T >nul 2>&1
) else (
    echo Python found, running graceful shutdown script.
    cd "%~dp0"
    python stop.py
)