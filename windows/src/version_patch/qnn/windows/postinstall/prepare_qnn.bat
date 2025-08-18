@echo off
pushd "%~dp0"
echo Installing QNN SDK
python prepare_qnn.py
popd