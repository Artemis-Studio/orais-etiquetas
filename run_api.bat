@echo off
cd /d "%~dp0"

REM Usar Python embeddable se existir; senao usar python do PATH
REM -m run_api: CWD (pasta do projeto) entra em sys.path, evita ModuleNotFoundError
if exist "%~dp0python312\python.exe" (
    "%~dp0python312\python.exe" -m run_api %*
) else (
    python -m run_api %*
)

if errorlevel 1 pause
