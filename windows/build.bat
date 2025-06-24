@echo off
chcp 65001 > NUL
set PYTHONUTF8=1
setlocal enabledelayedexpansion
set PYTHONIOENCODING="utf8"
cd "%~dp0"
if "%1" equ "__start__" (shift & goto main)
if not exist "logs" mkdir logs
cmd /s /c "%0 __start__ %* 2>&1 | src\bin\tee.exe logs\build.log"
exit /b

:main
REM Initialize global configurations
pushd "%~dp0"
call src\switch.bat %1
popd
pushd "%~dp0"
call src\variables.bat
call src\switch.bat qnn
popd

echo PWD: %cd%

REM Check if VCredist is installed

for /F "tokens=*" %%i in ('reg query "HKLM\SOFTWARE\Microsoft\VisualStudio" /s /f "Installed" 2^>nul') do (
    goto found_vcredist
)

echo No Visual C++ Redistributable found, Please download vcredist from https://learn.microsoft.com/zh-tw/cpp/windows/latest-supported-vc-redist?view=msvc-170
echo Press any key to continue building...
pause

:found_vcredist
echo Visual C++ Redistributable found.

if not exist "packages" mkdir packages

REM Download and extract RunHiddenConsole if not exists
call src\download_extract.bat %url_RunHiddenConsole% packages\%RunHiddenConsole_folder% packages\%RunHiddenConsole_folder% RunHiddenConsole.zip

REM Download and extract Node.js if not exists
call src\download_extract.bat %url_NodeJS% packages\%node_folder% packages\. node.zip

REM Download and extract PHP if not exists
call src\download_extract.bat %url_PHP% packages\%php_folder% packages\%php_folder% php.zip

REM Download and extract fallback version of PHP if the latest release not found
if not exist "packages\%php_folder%" (
    echo Downloading fallback version of PHP
    call src\download_extract.bat %url_PHP_Fallback% packages\%php_folder_Fallback% packages\%php_folder_Fallback% php.zip
    set "php_folder=%php_folder_Fallback%"
) 

REM Download and extract git bash if not exists
call src\download_extract.bat %url_gitbash% packages\%gitbash_folder% packages\%gitbash_folder% gitbash.7z.exe

REM Download and extract Python if not exists
IF EXIST packages\%python_folder% (
    echo Python folder already exists.
) ELSE (
    call src\download_extract.bat %url_Python% packages\%python_folder% packages\%python_folder% python.zip
    REM Overwrite the python310._pth file
    echo Overwrite the python310._pth file.
    copy /Y src\python310._pth "packages\%python_folder%\python310._pth"
)

REM Download and extract Redis if not exists
call src\download_extract.bat %url_Redis% packages\%redis_folder% packages\. redis.zip

IF "%HTTP_Server_Runtime%" == "apache" (
    IF EXIST packages\Apache_%apache_folder% (
        echo Apache folder already exists. Skipping download.
    ) ELSE (
        REM Download and extract Apache if not exists
        call src\download_extract.bat %url_Apache% packages\%apache_folder% packages\Apache_%apache_folder% apache.zip
    )

    IF EXIST packages\%mod_fcgid_folder% (
        echo mod_fcgid folder already exists. Skipping download.
    ) ELSE (
        REM Download and extract mod_fcgid if not exists
        call src\download_extract.bat %url_mod_fcgid% packages\%mod_fcgid_folder% packages\%mod_fcgid_folder% mod_fcgid.zip
    )

    if not exist "packages\Apache_%apache_folder%\Apache24\modules\mod_fcgid.so" (
        copy packages\%mod_fcgid_folder%\mod_fcgid.so packages\Apache_%apache_folder%\Apache24\modules\mod_fcgid.so
    ) else (
        echo mod_fcgid.so already exists, skipping copy and pasting.
    )

    set "target=packages\Apache_%apache_folder%\Apache24\conf\httpd.conf"
    if not exist "%target%.old" (
        if exist "%target%" move /Y "%target%" "%target%.old"
        copy /Y src\httpd.conf "%target%"
    )

    if not exist "packages\Apache_%apache_folder%\Apache24\conf\extra\httpd-fcgid.conf" (
        copy src\httpd-fcgid.conf packages\Apache_%apache_folder%\Apache24\conf\extra\httpd-fcgid.conf
    ) else (
        echo mod_fcgid.so already exists, skipping copy and pasting.
    )
) else (
    IF EXIST packages\%nginx_folder% (
        echo Nginx folder already exists. Skipping download.
    ) ELSE (
        REM Download and extract Nginx if not exists
        call src\download_extract.bat %url_Nginx% packages\%nginx_folder% packages\. nginx.zip
        ren "packages\%nginx_folder%\conf\nginx.conf" "nginx.conf.old"
    )
    IF NOT EXIST packages\%nginx_folder%\conf\nginx.conf (
        echo Copying default nginx configuration.
        copy /Y src\nginx.conf "packages\%nginx_folder%\conf\nginx.conf"
    )
)

REM Copy php.ini if not exists
if not exist "packages\%php_folder%\php.ini" (
    copy ..\src\multi-chat\php.ini "packages\%php_folder%\php.ini"
) else (
    echo php.ini already exists, skipping copy and pasting.
)

REM Copy php_redis.dll if not exists
if not exist "packages\%php_folder%\ext\php_redis.dll" (
    copy src\php_redis.dll "packages\%php_folder%\ext\php_redis.dll"
) else (
    echo php_redis.dll already exists, skipping copy and pasting.
)

REM Download composer.phar if not exists
if not exist "packages\composer.phar" (
    echo Downloading composer
    curl -o packages\composer.phar https://getcomposer.org/download/latest-stable/composer.phar
) else (
    echo Composer already exists, skipping download.
)

REM Prepare RunHiddenConsole.exe if not exists
if not exist "packages\%php_folder%\RunHiddenConsole.exe" (
    copy packages\%RunHiddenConsole_folder%\x64\RunHiddenConsole.exe packages\%php_folder%\
) else (
    echo RunHiddenConsole.exe already exists, skipping copy.
)

REM Prepare get-pip.py
if not exist "packages\%python_folder%\get-pip.py" (
    echo Downloading get-pip.py
	curl -o "packages\%python_folder%\get-pip.py" https://bootstrap.pypa.io/get-pip.py
) else (
    echo get-pip.py already exists, skipping download.
)

REM Install pip for python
echo Installing updated version of pip and uv
if not exist "packages\%python_folder%\Scripts\pip.exe" (
	pushd "packages\%python_folder%"
	python get-pip.py --no-warn-script-location
	popd
)
python -m pip install -U pip uv

REM Check if .env file exists
if not exist "..\src\multi-chat\.env" (
    REM Kuwa Chat
    echo Copying environment configuration file ^(.env^) of multi-chat
    copy ..\src\multi-chat\.env.dev ..\src\multi-chat\.env
) else (
    echo Environment configuration file ^(.env^) of multi-chat already exists, skipping copy.
)

set "PATH=%~dp0packages\%node_folder%;%PATH%"

REM Production update
echo Initializing multi-chat
SET HTTP_PROXY_REQUEST_FULLURI=0
pushd "..\src\multi-chat"
call php ..\..\windows\packages\composer.phar install --no-dev --optimize-autoloader --no-interaction
call php artisan key:generate --force
call php artisan db:seed --class=InitSeeder --force
call php artisan migrate --force
rmdir /Q /S public\storage
call php artisan storage:link
call npm.cmd install
call npm.cmd audit fix
call npm.cmd ci --no-audit --no-progress
call npm.cmd run build
call php artisan optimize
call php artisan route:cache
call php artisan view:cache
call php artisan config:cache
if exist "..\..\.git\test_pack_perm.priv" (
	call php artisan web:config --settings="updateweb_git_ssh_command=ssh -i .git/test_pack_perm.priv -o IdentitiesOnly=yes -o StrictHostKeyChecking=no"
)
popd


REM Sync locked Python dependencies
echo Syncing Python dependencies
pushd ".."
uv pip sync --system windows\src\requirements.txt.lock
popd

ollama --version >NUL
if !errorlevel! neq 0 (
    echo Downloading Ollama
    curl -L -C - -# -o packages\OllamaSetup.exe https://ollama.com/download/OllamaSetup.exe
    echo Installing Ollama
    call packages\OllamaSetup.exe /SILENT
)
echo Ollama installed.
ollama --version

echo Installing dependency of whisper
call src\download_extract.bat %url_ffmpeg% packages\%ffmpeg_folder% packages\. ffmpeg.zip
REM Install dependency of n8n
where n8n >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing n8n
    call npm.cmd install -g "n8n@1.73.1"
) else (
    for /f "delims=" %%i in ('n8n --version') do set "N8N_VERSION=%%i"
    if "%N8N_VERSION%" neq "1.73.1" (
        echo Updating n8n to 1.73.1
        call npm.cmd install -g "n8n@1.73.1"
    ) else (
        echo n8n 1.73.1 already installed, skipping
    )
)
REM Install dependency of Mermaid Tool
where mmdc >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing @mermaid-js/mermaid-cli...
    call npm.cmd install -g "@mermaid-js/mermaid-cli" --no-audit --no-fund
) else (
    for /f "delims=" %%i in ('mmdc -v') do set "MERMAID_VERSION=%%i"
    REM Optional: if you want to check a specific version, insert it here
    echo mermaid-cli %MERMAID_VERSION% already installed. Skipping.
)

for %%i in ("postinstall\*.bat") do (
    echo Running %%~nxi
    call "%%i"
)

REM Download Pre-integrated Model
echo Downloading pre-integrated models.
python ..\src\executor\docqa\download_model.py

REM Make Kuwa root
echo Initializing the filesystem hierarchy of Kuwa.
mkdir "%KUWA_ROOT%\bin"
mkdir "%KUWA_ROOT%\database"
mkdir "%KUWA_ROOT%\custom"
mkdir "%KUWA_ROOT%\bootstrap\bot"
xcopy /s /y /q ..\src\bot\init "%KUWA_ROOT%\bootstrap\bot"
xcopy /s /y /q ..\src\tools "%KUWA_ROOT%\bin"
rd /S /Q "%KUWA_ROOT%\bin\test"
pushd "%KUWA_ROOT%\bin"
for %%f in (*) do (
  attrib +r "%%f"
  icacls "%%f" /grant Everyone:RX
)
popd

echo Installation is complete. Please wait for any other open Command Prompts to exit. You may need to manually close them if they don't close automatically.
goto :eof

:: Sub-Routines

:: pip-install-requirements-txt sub-routine
:: Install each dependency in requirements.txt under current working directory to
:: prevent cascading failure.
:install-requirements-txt
echo Installing requirements.txt in %cd%
for /f "tokens=*" %%a in ('findstr /v /r /c:"^#" requirements.txt') do (
  echo Installing "%%a"...
  uv pip install --system "%%a"
)
goto :eof