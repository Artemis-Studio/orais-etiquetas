# Script PowerShell para testar requisição completa via cURL
# Uso: .\teste_curl.ps1

$API_URL = "http://100.80.127.36:8000"
$JSON_FILE = "requisicao_completa.json"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Teste de Requisição Completa via cURL (sem API key)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verifica se o arquivo JSON existe
if (-not (Test-Path $JSON_FILE)) {
    Write-Host "ERRO: Arquivo $JSON_FILE não encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host "[1] Lendo arquivo JSON..." -ForegroundColor Yellow
$jsonContent = Get-Content $JSON_FILE -Raw
Write-Host "Arquivo carregado: $JSON_FILE" -ForegroundColor Green
Write-Host ""

Write-Host "[2] Enviando requisição para: $API_URL/print" -ForegroundColor Yellow
Write-Host ""

# Método 1: Usando Get-Content e pipe
try {
    $response = Get-Content $JSON_FILE -Raw | curl.exe -X POST "$API_URL/print" `
        -H "Content-Type: application/json" `
        -d "@-"
    
    Write-Host ""
    Write-Host "Resposta:" -ForegroundColor Green
    Write-Host $response
}
catch {
    Write-Host "ERRO ao enviar requisição: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Teste concluído!" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
