@echo off
cd /d "%~dp0"

REM Usar Python embeddable se existir; senao usar python do PATH
if exist "%~dp0python312\python.exe" (
    "%~dp0python312\python.exe" "%~dp0run_api.py" %*
) else (
    python "%~dp0run_api.py" %*
)

if errorlevel 1 pause
