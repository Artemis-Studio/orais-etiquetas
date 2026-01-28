@echo off
REM Script batch para enviar requisição completa via cURL
REM Uso: curl_completo.bat [nome_da_impressora]
REM      Se não especificar, usa impressora padrão

echo ============================================================
echo Teste de Requisicao Completa via cURL (sem API key)
echo ============================================================
echo.

set API_URL=http://100.80.127.36:8000
set JSON_FILE=requisicao_completa.json
set PRINTER_NAME=%1

echo [1] Verificando arquivo JSON...
if not exist "%JSON_FILE%" (
    echo ERRO: Arquivo %JSON_FILE% nao encontrado!
    pause
    exit /b 1
)

echo Arquivo encontrado: %JSON_FILE%
echo.

echo [2] Listando impressoras disponiveis...
curl.exe -X GET "%API_URL%/printers" -H "Content-Type: application/json"
echo.
echo.

if "%PRINTER_NAME%"=="" (
    echo [3] Nenhuma impressora especificada - usando impressora padrao
    echo      Para especificar uma impressora, use: curl_completo.bat "Nome_da_Impressora"
) else (
    echo [3] Usando impressora: %PRINTER_NAME%
)

echo.

echo [4] Enviando requisicao para: %API_URL%/print
echo.

REM Cria JSON temporário com impressora especificada se fornecida
if not "%PRINTER_NAME%"=="" (
    echo Criando JSON temporario com impressora especificada...
    powershell -Command "(Get-Content '%JSON_FILE%' -Raw) -replace '\"printer_name\": \"\"', '\"printer_name\": \"%PRINTER_NAME%\"' | Out-File -Encoding utf8 temp_requisicao.json"
    set JSON_FILE=temp_requisicao.json
)

REM Usa type para ler o arquivo e pipe para curl
type "%JSON_FILE%" | curl.exe -X POST "%API_URL%/print" ^
    -H "Content-Type: application/json" ^
    -d "@-"

REM Remove arquivo temporário se foi criado
if exist temp_requisicao.json del temp_requisicao.json

echo.
echo ============================================================
echo Teste concluido!
echo ============================================================
pause
