@echo off
echo ========================================
echo Instalacao Automatica com Python Embeddable
echo ========================================
echo.

REM Define diretorio do Python embeddable
set PYTHON_DIR=%~dp0python312
set PYTHON_EXE=%PYTHON_DIR%\python.exe
set PIP_EXE=%PYTHON_DIR%\Scripts\pip.exe

REM Verifica se ja existe Python embeddable (pergunta se quer reinstalar)
if exist "%PYTHON_EXE%" (
    echo Python embeddable ja existe em %PYTHON_DIR%
    echo Se houver problemas, delete a pasta python312 e execute novamente.
    echo.
    goto :install_deps
)

echo [1/5] Baixando Python embeddable 3.12.2...
cd /d "%~dp0"
curl -L -o python-embed.zip "https://www.python.org/ftp/python/3.12.2/python-3.12.2-embed-amd64.zip"
if errorlevel 1 (
    echo ERRO: Falha ao baixar Python embeddable
    pause
    exit /b 1
)

echo [2/5] Descompactando Python embeddable...
powershell -Command "Expand-Archive -Path python-embed.zip -DestinationPath python312 -Force"
if errorlevel 1 (
    echo ERRO: Falha ao descompactar
    pause
    exit /b 1
)

del python-embed.zip

REM Habilita site-packages no Python embeddable
echo [3/5] Configurando Python embeddable...
REM Encontra o arquivo ._pth (geralmente python312._pth para Python 3.12.2)
if exist "%PYTHON_DIR%\python312._pth" (
    set PTH_FILE=%PYTHON_DIR%\python312._pth
) else if exist "%PYTHON_DIR%\python._pth" (
    set PTH_FILE=%PYTHON_DIR%\python._pth
) else (
    echo ERRO: Arquivo ._pth nao encontrado!
    pause
    exit /b 1
)

REM Faz backup e configura o arquivo ._pth corretamente
if exist "%PTH_FILE%" (
    copy "%PTH_FILE%" "%PTH_FILE%.bak" >nul 2>&1
    
    REM Verifica se ja tem "import site" no arquivo
    findstr /C:"import site" "%PTH_FILE%" >nul 2>&1
    if errorlevel 1 (
        REM Adiciona "import site" no final preservando o conteudo original
        REM Usa PowerShell para garantir que adiciona corretamente
        powershell -Command "$lines = Get-Content '%PTH_FILE%'; $lines += 'import site'; $lines | Set-Content '%PTH_FILE%'"
        if errorlevel 1 (
            REM Fallback: metodo simples
            echo. >> "%PTH_FILE%"
            echo import site >> "%PTH_FILE%"
        )
        echo Arquivo ._pth configurado com import site
    ) else (
        echo Arquivo ._pth ja configurado com import site
    )
) else (
    echo ERRO: Arquivo ._pth nao encontrado apos descompactacao!
    pause
    exit /b 1
)

echo [4/5] Instalando pip...
curl -L -o "%PYTHON_DIR%\get-pip.py" "https://bootstrap.pypa.io/get-pip.py"
if errorlevel 1 (
    echo ERRO: Falha ao baixar get-pip.py
    pause
    exit /b 1
)

"%PYTHON_EXE%" "%PYTHON_DIR%\get-pip.py"
if errorlevel 1 (
    echo ERRO: Falha ao instalar pip
    pause
    exit /b 1
)

del "%PYTHON_DIR%\get-pip.py"

:install_deps
echo [5/5] Instalando dependencias do projeto...
"%PIP_EXE%" install -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias
    pause
    exit /b 1
)

echo.
echo ========================================
echo Instalando servico Windows...
echo ========================================
"%PYTHON_EXE%" "%~dp0service\windows_service.py" install
if errorlevel 1 (
    echo ERRO: Falha ao instalar servico
    pause
    exit /b 1
)

echo.
echo ========================================
echo Instalacao concluida com sucesso!
echo ========================================
echo.
echo Python embeddable instalado em: %PYTHON_DIR%
echo.
echo Para iniciar o servico, execute:
echo   net start LabelPrintingAPI
echo.
echo Para parar o servico, execute:
echo   net stop LabelPrintingAPI
echo.
echo Para ver status do servico:
echo   sc query LabelPrintingAPI
echo.
echo Para desinstalar o servico:
echo   "%PYTHON_EXE%" "%~dp0service\windows_service.py" remove
echo.
pause
