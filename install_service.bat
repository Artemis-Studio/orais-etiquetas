@echo off
cd /d "%~dp0"
echo Instalando Servico de Impressao de Etiquetas...
echo.

REM Preferir Python embeddable (python312) se existir
set "PYTHON_EXE="
if exist "%~dp0python312\python.exe" (
    set "PYTHON_EXE=%~dp0python312\python.exe"
    echo Usando Python embeddable: %PYTHON_EXE%
    echo.
)

if not defined PYTHON_EXE (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ERRO: Python nao encontrado.
        echo.
        echo Opcoes:
        echo   1. Instale o Python e adicione ao PATH, ou
        echo   2. Execute install_with_embedded_python.bat como Administrador
        echo      para usar Python embeddable na pasta do projeto.
        echo.
        pause
        exit /b 1
    )
    set "PYTHON_EXE=python"
)

REM Instala dependencias
echo Instalando dependencias...
if "%PYTHON_EXE%"=="python" (
    pip install -r requirements.txt
) else (
    "%PYTHON_EXE%" -m pip install -r requirements.txt
)
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias.
    pause
    exit /b 1
)

REM Instala o servico (exige Executar como Administrador)
echo.
echo Instalando servico Windows...
net session >nul 2>&1
if errorlevel 1 (
    echo AVISO: Execute este script como Administrador para instalar o servico.
    echo Clique com o botao direito em install_service.bat e escolha "Executar como administrador".
    echo.
    pause
    exit /b 1
)

"%PYTHON_EXE%" "%~dp0service\windows_service.py" install
if errorlevel 1 (
    echo ERRO: Falha ao instalar servico.
    pause
    exit /b 1
)

echo.
echo Servico instalado com sucesso!
echo.
echo Para iniciar o servico, execute (como Administrador):
echo   net start LabelPrintingAPI
echo.
echo Para parar o servico:
echo   net stop LabelPrintingAPI
echo.
echo Para desinstalar o servico:
echo   "%PYTHON_EXE%" "%~dp0service\windows_service.py" remove
echo.
pause

