# Como Enviar Impressão via API

Este guia mostra diferentes formas de enviar requisições de impressão para a API.

## 📋 Pré-requisitos

1. **API rodando**: A API deve estar em execução
   - Como serviço Windows: `net start LabelPrintingAPI`
   - Ou diretamente: `python run_api.py`
   - Ou em background: `run_api_background.bat`

2. **URL da API**: Por padrão `http://localhost:8000`
   - Para acesso remoto: `http://IP_DO_COMPUTADOR:8000`

3. **API Key** (se autenticação estiver habilitada):
   - Verifique em `config/config.yaml` se `api_key` está configurado
   - Se estiver vazio, autenticação está desabilitada

---

## 🚀 Métodos de Envio

### 1. Via CLI (Mais Fácil)

A forma mais simples de enviar uma impressão:

```bash
python cli.py print-via-api \
  --codigo "1420" \
  --descricao "JG DENTE ENDO 21 AO 27 RADIO" \
  --descricao2 "PACOS" \
  --ref "1420" \
  --pedido "10511" \
  --codigo-barras "7890000005098" \
  --lote "10111150126" \
  --validade "31/12/2025" \
  --printer "Nome_da_Impressora"
```

**Com API Key:**
```bash
python cli.py print-via-api \
  --codigo "1420" \
  --descricao "Produto XYZ" \
  --api-key "sua-chave-secreta"
```

**Com URL customizada:**
```bash
python cli.py print-via-api \
  --codigo "1420" \
  --descricao "Produto XYZ" \
  --api-url "http://192.168.1.100:8000"
```

---

### 2. Via Python (requests)

```python
import requests
import json

# Configurações
API_URL = "http://localhost:8000"
API_KEY = ""  # Deixe vazio se autenticação estiver desabilitada

# Headers
headers = {
    "Content-Type": "application/json"
}

# Adiciona API key se configurada
if API_KEY:
    headers["X-API-Key"] = API_KEY

# Dados da etiqueta
data = {
    "label_type": "produto",
    "data": {
        "codigo": "1420",
        "descricao": "JG DENTE ENDO 21 AO 27 RADIO",
        "descricao2": "PACOS",
        "ref": "1420",
        "pedido": "10511",
        "codigo_barras": "7890000005098",
        "lote": "10111150126",
        "validade": "31/12/2025"
    },
    "printer_name": "Zebra_Printer"  # Opcional
}

# Envia requisição
try:
    response = requests.post(
        f"{API_URL}/print",
        json=data,
        headers=headers,
        timeout=10
    )
    response.raise_for_status()
    
    result = response.json()
    print("✅ Sucesso!")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
except requests.exceptions.RequestException as e:
    print(f"❌ Erro: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Resposta: {e.response.text}")
```

**Ou use o arquivo de exemplo:**
```bash
python example_request.py
```

---

### 3. Via cURL (Terminal/CMD)

**Windows PowerShell:**
```powershell
curl.exe -X POST http://localhost:8000/print `
  -H "Content-Type: application/json" `
  -H "X-API-Key: sua-chave-secreta" `
  -d '{\"label_type\":\"produto\",\"data\":{\"codigo\":\"1420\",\"descricao\":\"JG DENTE ENDO 21 AO 27 RADIO\",\"descricao2\":\"PACOS\",\"ref\":\"1420\",\"pedido\":\"10511\",\"codigo_barras\":\"7890000005098\",\"lote\":\"10111150126\",\"validade\":\"31/12/2025\"}}'
```

**Linux/Mac:**
```bash
curl -X POST http://localhost:8000/print \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave-secreta" \
  -d '{
    "label_type": "produto",
    "data": {
      "codigo": "1420",
      "descricao": "JG DENTE ENDO 21 AO 27 RADIO",
      "descricao2": "PACOS",
      "ref": "1420",
      "pedido": "10511",
      "codigo_barras": "7890000005098",
      "lote": "10111150126",
      "validade": "31/12/2025"
    }
  }'
```

**Com arquivo JSON:**
```bash
curl -X POST http://localhost:8000/print \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave-secreta" \
  -d @etiqueta.json
```

Onde `etiqueta.json` contém:
```json
{
  "label_type": "produto",
  "data": {
    "codigo": "1420",
    "descricao": "JG DENTE ENDO 21 AO 27 RADIO",
    "descricao2": "PACOS",
    "ref": "1420",
    "pedido": "10511",
    "codigo_barras": "7890000005098",
    "lote": "10111150126",
    "validade": "31/12/2025"
  }
}
```

---

### 4. Via Postman / Insomnia

1. **Método**: `POST`
2. **URL**: `http://localhost:8000/print`
3. **Headers**:
   - `Content-Type: application/json`
   - `X-API-Key: sua-chave-secreta` (se autenticação habilitada)
4. **Body** (raw JSON):
```json
{
  "label_type": "produto",
  "data": {
    "codigo": "1420",
    "descricao": "JG DENTE ENDO 21 AO 27 RADIO",
    "descricao2": "PACOS",
    "ref": "1420",
    "pedido": "10511",
    "codigo_barras": "7890000005098",
    "lote": "10111150126",
    "validade": "31/12/2025"
  },
  "printer_name": "Zebra_Printer"
}
```

---

### 5. Via n8n (Automação)

No n8n, configure um nó **HTTP Request**:

- **Method**: `POST`
- **URL**: `http://IP_DO_COMPUTADOR:8000/print`
- **Authentication**: None (ou Basic se necessário)
- **Headers**:
  - `Content-Type`: `application/json`
  - `X-API-Key`: `{{ $env.API_KEY }}` (se usar variável de ambiente)
- **Body**:
```json
{
  "label_type": "produto",
  "data": {
    "codigo": "{{ $json.codigo }}",
    "descricao": "{{ $json.descricao }}",
    "descricao2": "{{ $json.descricao2 }}",
    "ref": "{{ $json.ref }}",
    "pedido": "{{ $json.pedido }}",
    "codigo_barras": "{{ $json.codigo_barras }}",
    "lote": "{{ $json.lote }}",
    "validade": "{{ $json.validade }}"
  }
}
```

---

## 📝 Estrutura da Requisição

### Endpoint
```
POST http://localhost:8000/print
```

### Headers
```
Content-Type: application/json
X-API-Key: sua-chave-secreta (opcional, se autenticação habilitada)
```

### Body (JSON)

#### Campos Obrigatórios
- `label_type`: Tipo de etiqueta (`"produto"` ou `"custom"`)
- `data.codigo`: Código do produto
- `data.descricao`: Descrição principal

#### Campos Opcionais
- `data.descricao2`: Descrição secundária (segunda linha)
- `data.ref`: Referência do produto (usa `codigo` se não fornecido)
- `data.pedido`: Número do pedido
- `data.codigo_barras`: Código de barras (usa `codigo` se não fornecido)
- `data.lote`: Número do lote
- `data.validade`: Data de validade
- `data.quantidade`: Quantidade (mantido para compatibilidade)
- `data.preco`: Preço (mantido para compatibilidade)
- `printer_name`: Nome da impressora (usa padrão se não fornecido)

### Exemplo Mínimo
```json
{
  "label_type": "produto",
  "data": {
    "codigo": "12345",
    "descricao": "Produto XYZ"
  }
}
```

### Exemplo Completo
```json
{
  "label_type": "produto",
  "data": {
    "codigo": "1420",
    "descricao": "JG DENTE ENDO 21 AO 27 RADIO",
    "descricao2": "PACOS",
    "ref": "1420",
    "pedido": "10511",
    "codigo_barras": "7890000005098",
    "lote": "10111150126",
    "validade": "31/12/2025"
  },
  "printer_name": "Zebra_ZT230"
}
```

---

## ✅ Resposta da API

### Sucesso (Impressão Imediata)
```json
{
  "success": true,
  "message": "Impressão realizada com sucesso"
}
```

### Sucesso (Adicionado à Fila)
```json
{
  "success": true,
  "queue_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Requisição adicionada à fila para processamento"
}
```

### Erro
```json
{
  "detail": "Mensagem de erro aqui"
}
```

---

## 🔍 Verificar Status

### Via CLI
```bash
python cli.py status
```

### Via Python
```python
response = requests.get(f"{API_URL}/status", headers=headers)
print(response.json())
```

### Via cURL
```bash
curl http://localhost:8000/status -H "X-API-Key: sua-chave"
```

---

## 📊 Verificar Fila

### Via CLI
```bash
python cli.py queue
python cli.py queue --status-filter pending
python cli.py queue --limit 20
```

### Via Python
```python
response = requests.get(
    f"{API_URL}/queue",
    headers=headers,
    params={"status": "pending", "limit": 10}
)
print(response.json())
```

### Via cURL
```bash
curl "http://localhost:8000/queue?status=pending&limit=10" \
  -H "X-API-Key: sua-chave"
```

---

## 🖨️ Listar Impressoras

### Via CLI
```bash
python cli.py list-printers-api
```

### Via Python
```python
response = requests.get(f"{API_URL}/printers", headers=headers)
print(response.json())
```

### Via cURL
```bash
curl http://localhost:8000/printers -H "X-API-Key: sua-chave"
```

---

## ⚡ Processar Fila Manualmente

### Via CLI
```bash
python cli.py process-queue
```

### Via Python
```python
response = requests.post(f"{API_URL}/queue/process", headers=headers)
print(response.json())
```

### Via cURL
```bash
curl -X POST http://localhost:8000/queue/process \
  -H "X-API-Key: sua-chave"
```

---

## 🐛 Troubleshooting

### Erro: "Não foi possível conectar à API"
- Verifique se a API está rodando: `python cli.py status`
- Verifique a URL: `--api-url "http://IP:PORTA"`
- Verifique firewall/antivírus

### Erro: "API key inválida"
- Verifique se a API key está correta
- Verifique se autenticação está habilitada em `config/config.yaml`
- Use `--api-key "sua-chave"` no comando CLI

### Requisição fica na fila
- Verifique se a impressora está ligada e conectada
- Verifique os logs: `logs/api.log`
- Use `python cli.py status` para verificar status da impressora

### Impressora não encontrada
- Liste impressoras: `python cli.py list-printers`
- Configure o nome correto em `config/config.yaml` ou use `--printer`

---

## 📚 Exemplos Práticos

### Exemplo 1: Impressão Simples
```bash
python cli.py print-via-api \
  --codigo "12345" \
  --descricao "Produto Teste"
```

### Exemplo 2: Impressão Completa
```bash
python cli.py print-via-api \
  --codigo "1420" \
  --descricao "JG DENTE ENDO 21 AO 27 RADIO" \
  --descricao2 "PACOS" \
  --ref "1420" \
  --pedido "10511" \
  --codigo-barras "7890000005098" \
  --lote "10111150126" \
  --validade "31/12/2025"
```

### Exemplo 3: Com Impressora Específica
```bash
python cli.py print-via-api \
  --codigo "12345" \
  --descricao "Produto XYZ" \
  --printer "Zebra_ZT230"
```

### Exemplo 4: Com API Key e URL Remota
```bash
python cli.py print-via-api \
  --codigo "12345" \
  --descricao "Produto XYZ" \
  --api-url "http://192.168.1.100:8000" \
  --api-key "minha-chave-secreta"
```

---

## 💡 Dicas

1. **Use o CLI para testes rápidos**: É a forma mais simples
2. **Use Python para automação**: Integre em seus scripts
3. **Use cURL para testes manuais**: Útil para debug
4. **Monitore a fila**: Use `python cli.py queue` para ver requisições pendentes
5. **Verifique logs**: Em caso de erro, consulte `logs/api.log`

---

## 📖 Documentação Adicional

- [CLI_USAGE.md](CLI_USAGE.md) - Guia completo da CLI
- [README.md](README.md) - Documentação geral do projeto
- [example_request.py](example_request.py) - Exemplos em Python
