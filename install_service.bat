@echo off
echo Instalando Servico de Impressao de Etiquetas...
echo.

REM Verifica se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado. Por favor, instale o Python primeiro.
    pause
    exit /b 1
)

REM Instala dependencias
echo Instalando dependencias...
pip install -r requirements.txt

REM Instala o servico
echo.
echo Instalando servico Windows...
python service/windows_service.py install

echo.
echo Servico instalado com sucesso!
echo.
echo Para iniciar o servico, execute:
echo   net start LabelPrintingAPI
echo.
echo Para parar o servico, execute:
echo   net stop LabelPrintingAPI
echo.
echo Para desinstalar o servico, execute:
echo   python service/windows_service.py remove
echo.
pause

