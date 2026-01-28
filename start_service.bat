@echo off
cd /d "%~dp0"

if "%~1"=="elevated" goto :do_start

REM Iniciar o servico exige Executar como Administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Iniciar o servico exige Administrador.
    echo Abrindo como Administrador...
    powershell -Command "Start-Process -FilePath '%~f0' -ArgumentList 'elevated' -Verb RunAs -WorkingDirectory '%~dp0'"
    exit /b 0
)

:do_start
net start LabelPrintingAPI
if errorlevel 1 (
    echo.
    echo Se o servico nao estiver instalado, execute install_with_embedded_python.bat
    echo ou install_service.bat como Administrador.
    pause
    exit /b 1
)

echo.
echo Servico LabelPrintingAPI iniciado. Continua rodando em segundo plano.
echo Para parar: net stop LabelPrintingAPI
pause
