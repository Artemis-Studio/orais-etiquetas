@echo off
cd /d "%~dp0"
if not exist "%~dp0logs" mkdir "%~dp0logs"

set "PYEXE="
if exist "%~dp0python312\python.exe" (
    set "PYEXE=%~dp0python312\python.exe"
) else (
    set "PYEXE=python"
)

set "WRK=%~dp0"
if "%WRK:~-1%"=="\" set "WRK=%WRK:~0,-1%"
set "ERRLOG=%~dp0logs\api_background_err.txt"
set "OUTLOG=%~dp0logs\api_background_out.txt"

REM PYTHONPATH=projeto no processo filho (embeddable nao poe CWD em sys.path)
powershell -NoProfile -Command "$env:PYTHONPATH = '%WRK%'; Start-Process -FilePath \"%PYEXE%\" -ArgumentList \"%~dp0run_api.py\" -WorkingDirectory \"%WRK%\" -WindowStyle Hidden -RedirectStandardError \"%ERRLOG%\" -RedirectStandardOutput \"%OUTLOG%\""

echo API iniciada em background.
echo Logs: logs\api.log
echo.
echo Se a API nao responder, veja erros em: logs\api_background_err.txt
echo.
echo Comandos (CMD):
echo   Ver processos Python: tasklist ^| findstr python
echo   Parar API:           taskkill /F /IM python.exe
echo.
