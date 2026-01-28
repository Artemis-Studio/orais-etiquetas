@echo off
cd /d "%~dp0"

echo ========================================
echo Instalacao Automatica com Python Embeddable
echo ========================================
echo.

REM Servico Windows exige Executar como Administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Este script precisa ser executado como ADMINISTRADOR
    echo para instalar o servico Windows e evitar "Acesso negado".
    echo.
    echo Como fazer:
    echo   1. Clique com o botao direito em install_with_embedded_python.bat
    echo   2. Escolha "Executar como administrador"
    echo.
    echo Ou abra CMD/PowerShell como Administrador, va ate a pasta do projeto
    echo e execute: install_with_embedded_python.bat
    echo.
    choice /C SN /M "Abrir como Administrador agora"
    if errorlevel 2 (
        echo Execute o script como Administrador quando quiser instalar o servico.
        pause
        exit /b 1
    )
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs -WorkingDirectory '%~dp0'"
    exit /b 0
)

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

REM Verifica se python312.zip existe (necessario para Python embeddable funcionar)
if not exist "%PYTHON_DIR%\python312.zip" (
    echo ERRO: python312.zip nao encontrado apos descompactacao!
    pause
    exit /b 1
)

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
    
    REM Verifica se ja tem "import site" ativo (sem #) no arquivo
    findstr /C:"^import site" "%PTH_FILE%" >nul 2>&1
    if errorlevel 1 (
        REM Usa PowerShell para ler o arquivo original, processar e salvar SEM BOM (UTF-8 sem BOM)
        REM Isso e critico - Python embeddable nao aceita BOM no arquivo ._pth
        powershell -Command "$lines = Get-Content '%PTH_FILE%'; $newLines = @(); $hasActiveImport = $false; foreach ($line in $lines) { $trimmed = $line.Trim(); if ($trimmed -eq 'import site') { $hasActiveImport = $true; $newLines += 'import site' } elseif ($trimmed -eq '#import site') { $hasActiveImport = $true; $newLines += 'import site' } else { $newLines += $line } }; if (-not $hasActiveImport) { $newLines += 'import site' }; $utf8NoBom = New-Object System.Text.UTF8Encoding $false; [System.IO.File]::WriteAllLines('%PTH_FILE%', $newLines, $utf8NoBom)"
        if errorlevel 1 (
            REM Fallback: metodo mais simples
            REM Remove linhas com import site (com ou sem #) e adiciona no final
            findstr /V /C:"import site" "%PTH_FILE%" > "%PTH_FILE%.tmp"
            echo import site >> "%PTH_FILE%.tmp"
            REM Remove BOM se existir usando PowerShell
            powershell -Command "$content = Get-Content '%PTH_FILE%.tmp' -Raw; $utf8NoBom = New-Object System.Text.UTF8Encoding $false; [System.IO.File]::WriteAllText('%PTH_FILE%', $content, $utf8NoBom)"
            del "%PTH_FILE%.tmp" >nul 2>&1
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

REM Garante que site-packages existe
if not exist "%PYTHON_DIR%\Lib\site-packages" (
    mkdir "%PYTHON_DIR%\Lib\site-packages"
)

REM Mostra o conteudo do arquivo ._pth para debug
echo.
echo Verificando arquivo ._pth:
type "%PTH_FILE%"
echo.

REM Testa se pip esta funcionando
echo Testando instalacao do pip...
"%PYTHON_EXE%" -m pip --version
if errorlevel 1 (
    echo.
    echo ERRO: pip nao esta funcionando.
    echo Verifique o arquivo ._pth acima.
    echo O arquivo deve terminar com "import site" em uma linha separada.
    pause
    exit /b 1
)

:install_deps
echo [5/5] Instalando dependencias do projeto...
"%PYTHON_EXE%" -m pip install -r "%~dp0requirements.txt"
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
echo Para rodar a API sem servico (teste): execute run_api.bat
echo Para iniciar o servico com duplo clique: execute start_service.bat
echo.
pause
