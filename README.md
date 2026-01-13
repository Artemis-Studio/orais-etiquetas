# API de Impressão de Etiquetas

API REST para impressão de etiquetas Zebra (ZPL) que recebe requisições do n8n, processa impressões em tempo real quando o computador está ligado, e armazena requisições em fila quando offline.

## Características

- ✅ API REST com FastAPI
- ✅ Suporte para impressão Zebra via ZPL
- ✅ Sistema de fila com SQLite para requisições offline
- ✅ Processamento automático de fila quando serviço está online
- ✅ Serviço Windows que inicia automaticamente
- ✅ Autenticação opcional via API key
- ✅ Endpoints para monitoramento e gerenciamento

## Requisitos

- Python 3.8 ou superior
- Windows (para serviço Windows e integração com impressoras)
- Impressora Zebra configurada no Windows
- pywin32 (instalado automaticamente via requirements.txt)

## Instalação

### 1. Clone ou baixe o projeto

```bash
cd orais_etiquetas
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure a API

Edite o arquivo `config/config.yaml`:

```yaml
api:
  host: "0.0.0.0"  # Use 0.0.0.0 para aceitar conexões externas
  port: 8000
  api_key: "sua-chave-secreta-aqui"  # Deixe vazio para desabilitar autenticação

printer:
  default_printer: ""  # Nome da impressora ou deixe vazio para usar padrão
  timeout: 30
  retry_attempts: 3

queue:
  check_interval: 5  # Verifica fila a cada 5 segundos
  max_retries: 3
```

### 4. Instale como Serviço Windows (Recomendado)

Execute o script de instalação:

```bash
install_service.bat
```

Ou manualmente:

```bash
python service/windows_service.py install
net start LabelPrintingAPI
```

### 5. Ou execute diretamente (para testes)

```bash
python run_api.py
```

## Uso

### Endpoints da API

#### POST `/print` - Imprimir Etiqueta

Envia uma requisição para imprimir uma etiqueta.

**Headers:**
- `X-API-Key`: (Opcional) API key se autenticação estiver habilitada
- `Content-Type: application/json`

**Body:**
```json
{
  "label_type": "produto",
  "data": {
    "codigo": "12345",
    "descricao": "Produto XYZ",
    "quantidade": 10,
    "preco": "29.90",
    "codigo_barras": "1234567890123"
  },
  "printer_name": "Zebra_Printer"  // Opcional
}
```

**Resposta:**
```json
{
  "success": true,
  "queue_id": "uuid-da-requisicao",
  "message": "Impressão realizada com sucesso" ou "Requisição adicionada à fila"
}
```

#### GET `/status` - Status do Serviço

Verifica o status do serviço e impressora.

**Resposta:**
```json
{
  "status": "online",
  "printer_available": true,
  "printer_name": "Zebra_Printer",
  "queue_stats": {
    "pending": 0,
    "processing": 0,
    "completed": 10,
    "failed": 0
  }
}
```

#### GET `/queue` - Visualizar Fila

Lista itens na fila de impressão.

**Query Parameters:**
- `status`: (Opcional) Filtrar por status (pending, processing, completed, failed)
- `limit`: (Opcional) Número máximo de itens (padrão: 100)

#### GET `/printers` - Listar Impressoras

Lista todas as impressoras disponíveis no sistema.

#### POST `/queue/process` - Processar Fila

Força processamento imediato da fila pendente.

### Exemplo de Uso com cURL

```bash
# Imprimir etiqueta
curl -X POST http://localhost:8000/print \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave-secreta" \
  -d '{
    "label_type": "produto",
    "data": {
      "codigo": "12345",
      "descricao": "Produto XYZ",
      "quantidade": 10
    }
  }'

# Verificar status
curl http://localhost:8000/status \
  -H "X-API-Key: sua-chave-secreta"

# Ver fila
curl http://localhost:8000/queue \
  -H "X-API-Key: sua-chave-secreta"
```

### Integração com n8n

No n8n, use o nó "HTTP Request" para enviar requisições:

1. **Método**: POST
2. **URL**: `http://IP_DO_COMPUTADOR:8000/print`
3. **Headers**:
   - `Content-Type: application/json`
   - `X-API-Key: sua-chave-secreta` (se habilitado)
4. **Body**: JSON com estrutura conforme exemplo acima

## Gerenciamento do Serviço Windows

### Comandos Úteis

```bash
# Iniciar serviço
net start LabelPrintingAPI

# Parar serviço
net stop LabelPrintingAPI

# Ver status do serviço
sc query LabelPrintingAPI

# Desinstalar serviço
python service/windows_service.py remove
```

## Estrutura de Dados

### Etiqueta de Produto

A etiqueta de produto suporta os seguintes campos:

- `codigo`: Código do produto (obrigatório)
- `descricao`: Descrição do produto
- `quantidade`: Quantidade
- `preco`: Preço (formato: "29.90")
- `codigo_barras`: Código de barras (usa `codigo` se não fornecido)

### Etiquetas Customizadas

Para etiquetas customizadas, forneça um template ZPL:

```json
{
  "label_type": "custom",
  "data": {
    "campo1": "valor1",
    "campo2": "valor2"
  },
  "zpl_template": "^XA^FO50,50^A0N,30,30^FD{campo1}^FS^XZ"
}
```

## Logs

Os logs são salvos em `logs/api.log` e também exibidos no console.

## Solução de Problemas

### Impressora não encontrada

1. Verifique se a impressora está instalada no Windows
2. Use o endpoint `/printers` para listar impressoras disponíveis
3. Configure o nome correto em `config/config.yaml`

### Requisições ficam na fila

1. Verifique se a impressora está ligada e conectada
2. Verifique os logs em `logs/api.log`
3. Use o endpoint `/status` para verificar status da impressora

### Serviço não inicia

1. Verifique se o Python está no PATH
2. Verifique se todas as dependências foram instaladas
3. Verifique os logs do Windows Event Viewer

## Desenvolvimento

### Estrutura do Projeto

```
orais_etiquetas/
├── api/
│   ├── __init__.py
│   ├── main.py           # API FastAPI principal
│   ├── models.py         # Modelos Pydantic
│   ├── queue.py          # Sistema de fila SQLite
│   ├── queue_processor.py # Processador de fila
│   ├── printer.py         # Integração com impressora
│   └── zpl_generator.py   # Gerador de comandos ZPL
├── config/
│   ├── __init__.py
│   ├── config.yaml        # Configurações
│   └── config_loader.py   # Carregador de configurações
├── service/
│   ├── __init__.py
│   └── windows_service.py # Serviço Windows
├── data/                  # Banco de dados SQLite (criado automaticamente)
├── logs/                  # Logs (criado automaticamente)
├── requirements.txt
├── run_api.py            # Script para rodar diretamente
├── install_service.bat    # Script de instalação
└── README.md
```

## Licença

Este projeto é de uso interno.

## Suporte

Para problemas ou dúvidas, consulte os logs em `logs/api.log` ou verifique o status via endpoint `/status`.

