# Guia de Uso da CLI

A CLI (Command Line Interface) permite gerenciar e validar a API de Impressão de Etiquetas diretamente pelo terminal.

## Instalação

A CLI é instalada automaticamente com as dependências:

```bash
pip install -r requirements.txt
```

## Comandos Disponíveis

### 1. Listar Impressoras Locais

Lista todas as impressoras disponíveis no sistema Windows:

```bash
python cli.py list-printers
```

**Exemplo de saída:**
```
🔍 Buscando impressoras disponíveis...

📋 Impressoras encontradas (2):

⭐ 1. Zebra_ZT230
     (Impressora padrão do sistema)
  2. HP_LaserJet

✅ Total: 2 impressora(s)
```

### 2. Testar Impressão

Envia uma etiqueta de teste para a impressora:

```bash
python cli.py test-printer
```

Ou especifique uma impressora:

```bash
python cli.py test-printer --printer "Zebra_ZT230"
```

### 3. Imprimir Etiqueta Diretamente

Imprime uma etiqueta sem usar a API (comunicação direta com impressora):

```bash
python cli.py print-label \
  --codigo "12345" \
  --descricao "Produto XYZ" \
  --quantidade "10" \
  --preco "29.90"
```

**Opções:**
- `-c, --codigo`: Código do produto (obrigatório)
- `-d, --descricao`: Descrição do produto (obrigatório)
- `-q, --quantidade`: Quantidade (opcional)
- `--preco`: Preço (opcional)
- `--codigo-barras`: Código de barras (opcional)
- `-p, --printer`: Nome da impressora (opcional)

### 4. Verificar Status da API

Verifica se a API está rodando e mostra estatísticas:

```bash
python cli.py status
```

Ou com API key:

```bash
python cli.py status --api-key "sua-chave"
```

**Exemplo de saída:**
```
📊 Status da API:
   Status: online
   Impressora disponível: ✅ Sim
   Impressora: Zebra_ZT230

📋 Estatísticas da Fila:
   Pendentes: 0
   Processando: 0
   Concluídas: 10
   Falhas: 0
```

### 5. Visualizar Fila

Mostra itens na fila de impressão:

```bash
python cli.py queue
```

Filtrar por status:

```bash
python cli.py queue --status-filter pending
```

Limitar número de itens:

```bash
python cli.py queue --limit 20
```

### 6. Processar Fila

Força processamento imediato da fila pendente:

```bash
python cli.py process-queue
```

### 7. Imprimir via API

Envia requisição de impressão através da API:

```bash
python cli.py print-via-api \
  --codigo "12345" \
  --descricao "Produto XYZ" \
  --quantidade "10" \
  --preco "29.90"
```

### 8. Listar Impressoras via API

Lista impressoras através da API (requer API rodando):

```bash
python cli.py list-printers-api
```

### 9. Validar Configuração

Valida se o sistema está configurado corretamente:

```bash
python cli.py validate-setup
```

**Verifica:**
- ✓ Python instalado
- ✓ Arquivo de configuração
- ✓ Impressoras disponíveis
- ✓ Dependências instaladas

## Opções Globais

Todos os comandos aceitam opções globais:

- `--api-url`: URL da API (padrão: http://localhost:8000)
- `--api-key`: API key para autenticação

**Exemplo:**
```bash
python cli.py status --api-url "http://192.168.1.100:8000" --api-key "minha-chave"
```

## Exemplos de Uso

### Validação Completa do Sistema

```bash
# 1. Validar configuração
python cli.py validate-setup

# 2. Listar impressoras
python cli.py list-printers

# 3. Testar impressão
python cli.py test-printer

# 4. Verificar status da API
python cli.py status
```

### Teste de Impressão Completo

```bash
# 1. Listar impressoras disponíveis
python cli.py list-printers

# 2. Testar impressão direta
python cli.py print-label \
  --codigo "TEST001" \
  --descricao "Teste de Impressão" \
  --quantidade "1"

# 3. Testar via API (se API estiver rodando)
python cli.py print-via-api \
  --codigo "TEST002" \
  --descricao "Teste via API" \
  --quantidade "1"
```

### Diagnóstico de Problemas

```bash
# 1. Validar setup
python cli.py validate-setup

# 2. Verificar status da API
python cli.py status

# 3. Ver fila pendente
python cli.py queue --status-filter pending

# 4. Processar fila manualmente
python cli.py process-queue
```

## Códigos de Saída

- `0`: Sucesso
- `1`: Erro (conexão, validação, etc.)

## Dicas

1. **Use `validate-setup` primeiro** para garantir que tudo está configurado
2. **Teste com `test-printer`** antes de imprimir etiquetas reais
3. **Use `--api-key`** se autenticação estiver habilitada
4. **Monitore a fila** com `queue` para ver requisições pendentes
5. **Use `process-queue`** para forçar processamento imediato

## Troubleshooting

### Erro: "Não foi possível conectar à API"

- Verifique se a API está rodando: `python run_api.py`
- Verifique a URL: `--api-url "http://IP:PORTA"`
- Verifique firewall/antivírus

### Erro: "Nenhuma impressora encontrada"

- Verifique se a impressora está instalada no Windows
- Verifique se a impressora está ligada e conectada
- Execute como administrador se necessário

### Erro: "API key inválida"

- Verifique se a API key está correta
- Verifique se autenticação está habilitada no `config.yaml`
- Use `--api-key "sua-chave"` no comando

