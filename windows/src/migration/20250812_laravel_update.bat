@echo off
REM Remove old PHP versions
rmdir /s /q packages\php-8.1.32-Win32-vs16-x64
rmdir /s /q packages\php-8.2.29-Win32-vs16-x64

REM Remove vendor and node_modules
rmdir /s /q ..\src\multi-chat\vendor
rmdir /s /q ..\src\multi-chat\node_modules

exit /b 0
