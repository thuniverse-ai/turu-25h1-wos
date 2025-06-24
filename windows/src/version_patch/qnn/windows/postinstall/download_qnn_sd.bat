@echo off
pushd "%~dp0"
echo Installing dependency of stable diffusion
call ..\src\download_extract.bat "https://dl.thuniverse.ai/turu-25h1-wos/qnn-stable-diffusion.zip" executors\qnn-stable-diffusion executors\. qnn-stable-diffusion.zip
popd