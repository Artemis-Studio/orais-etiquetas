@echo off
REM Script batch para enviar requisição com impressora específica
REM Uso: curl_com_impressora.bat "Nome_da_Impressora"

if "%1"=="" (
    echo ============================================================
    echo ERRO: Especifique o nome da impressora!
    echo ============================================================
    echo.
    echo Uso: curl_com_impressora.bat "Nome_da_Impressora"
    echo.
    echo Exemplo: curl_com_impressora.bat "Zebra_ZT230"
    echo.
    pause
    exit /b 1
)

set API_URL=http://100.80.127.36:8000
set PRINTER_NAME=%1

echo ============================================================
echo Enviando requisicao com impressora: %PRINTER_NAME%
echo ============================================================
echo.

echo [1] Criando JSON com impressora especificada...
powershell -Command "$json = Get-Content 'requisicao_completa.json' -Raw | ConvertFrom-Json; $json.printer_name = '%PRINTER_NAME%'; $json | ConvertTo-Json -Depth 10 | Out-File -Encoding utf8 temp_print.json"

if not exist temp_print.json (
    echo ERRO: Nao foi possivel criar JSON temporario!
    pause
    exit /b 1
)

echo [2] Enviando requisicao...
echo.

type temp_print.json | curl.exe -X POST "%API_URL%/print" ^
    -H "Content-Type: application/json" ^
    -d "@-"

echo.
echo.

REM Limpa arquivo temporário
del temp_print.json

echo ============================================================
echo Requisicao enviada!
echo ============================================================
pause
