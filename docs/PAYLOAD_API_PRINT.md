# Payload da API de Impressão (`POST /print`)

Documentação dos campos aceitos no corpo da requisição e suas condições.

---

## Endpoint e método

| Item    | Valor              |
|---------|--------------------|
| Método  | `POST`             |
| URL     | `http://localhost:8000/print` (ou host/porta configurados) |
| Content-Type | `application/json` |

### Autenticação (opcional)

Se no `config/config.yaml` estiver definida uma `api_key` não vazia:

- **Header:** `X-API-Key: <sua_api_key>`
- Sem o header ou com chave inválida: `401` ou `403`

Se `api_key` estiver vazia, a autenticação é desabilitada e o header não é necessário.

---

## Campos do payload (raiz)

| Campo           | Tipo    | Obrigatório | Padrão     | Descrição |
|-----------------|---------|-------------|------------|-----------|
| `label_type`    | string  | Não         | `"produto"`| Tipo de etiqueta. Valores: `"produto"` ou outro (customizado). |
| `data`          | object  | **Sim**     | —          | Dados da etiqueta. Para `label_type: "produto"` segue o formato descrito em [Objeto `data` (etiqueta produto)](#objeto-data-etiqueta-produto). |
| `duas_colunas`  | boolean | Não         | `false`    | Se `true`, imprime em duas colunas (mesmo layout em cada metade do rolo). |
| `data_col2`     | object  | Não         | —          | Dados da coluna direita. Só faz sentido com `duas_colunas: true`. Se omitido, a coluna direita usa o mesmo `data`. |
| `printer_name`  | string  | Não         | impressora padrão do config | Nome exato da impressora no Windows. |
| `zpl_template`  | string  | Não         | —          | Template ZPL customizado. Usado apenas quando `label_type` **não** é `"produto"`. Placeholders no formato `{chave}` são substituídos pelos valores de `data`. |

---

## Condições e comportamento

### 1. `label_type`

- **`"produto"`** (padrão): gera ZPL pelo layout interno (descrição, REF, pedido, lote, validade, código de barras). Os campos de `data` e `data_col2` seguem a tabela abaixo.
- **Outro valor** (ex.: `"custom"`): usa `zpl_template` para montar o ZPL; se `zpl_template` for omitido, cai no mesmo layout de produto usando apenas `data`.

### 2. `duas_colunas`

- **`false`** (padrão): uma única etiqueta por comando (uma coluna).
- **`true`**: duas etiquetas lado a lado (duas colunas). A coluna esquerda usa `data`; a coluna direita usa `data_col2` se informado, senão usa `data`.

### 3. `data_col2`

- Só é considerado quando `duas_colunas` é `true`.
- Se não for enviado ou for `null`, a coluna direita recebe os mesmos dados de `data`.
- Para etiqueta produto, `data_col2` usa as mesmas chaves que `data` (ver tabela abaixo).

---

## Objeto `data` (etiqueta produto)

Quando `label_type` é `"produto"`, o objeto `data` (e `data_col2`, se usado) pode conter:

| Campo            | Tipo   | Obrigatório | Descrição |
|------------------|--------|-------------|-----------|
| `codigo`         | string | Não         | Código do produto. Se `ref` não for enviado, é usado como REF na etiqueta. |
| `descricao`      | string | Recomendado | Descrição principal (ex.: "DENTE ENDO 24 RADIOPACO"). |
| `descricao2`     | string | Não         | Segunda linha de descrição (ex.: "RADIOPACO"). Concatena com `descricao` no layout. |
| `ref`            | string | Não         | Referência. Se omitido, usa `codigo`. |
| `pedido`         | string | Não         | Número do pedido. |
| `codigo_barras`  | string | Recomendado | EAN-13 (13 dígitos) para código de barras. Alternativa: use `ean`. |
| `ean`            | string | Não         | Mesmo que `codigo_barras` (compatibilidade). |
| `lote`           | string | Não         | Número do lote. |
| `validade`       | string | Não         | Data de validade (ex.: "31/12/2025"). |

**Observações:**

- Para código de barras EAN-13, é necessário enviar `codigo_barras` ou `ean` com 13 dígitos; caso contrário o código de barras pode não ser gerado ou ser gerado em outro formato.
- Campos extras em `data` (ex.: `task_id`, `task_name`, `list_id`) são ignorados na geração do ZPL e não causam erro.

---

## Exemplos de payload

### Impressão simples (uma coluna)

```json
{
  "label_type": "produto",
  "data": {
    "codigo": "1424",
    "descricao": "DENTE ENDO 24 RADIOPACO",
    "codigo_barras": "7890000015776"
  }
}
```

### Impressão em duas colunas (mesmo conteúdo nas duas)

```json
{
  "label_type": "produto",
  "duas_colunas": true,
  "data": {
    "codigo": "1424",
    "descricao": "DENTE ENDO 24 RADIOPACO",
    "codigo_barras": "7890000015776"
  }
}
```

### Duas colunas com dados diferentes (esquerda e direita)

```json
{
  "label_type": "produto",
  "duas_colunas": true,
  "data": {
    "codigo": "1424",
    "descricao": "DENTE ENDO 24 RADIOPACO",
    "codigo_barras": "7890000015776"
  },
  "data_col2": {
    "codigo": "1425",
    "descricao": "OUTRO PRODUTO",
    "codigo_barras": "7890000015777"
  }
}
```

### Com impressora específica e campos opcionais

```json
{
  "label_type": "produto",
  "duas_colunas": false,
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
  "printer_name": "ZDesigner_Produto"
}
```

### Payload com campos extras (ignorados na impressão)

A API aceita outros campos na raiz (ex.: `task_id`, `task_name`, `list_id`, `task_ids`, `detected_at`, `printed_label`). Eles não são usados na geração do ZPL; apenas `label_type`, `duas_colunas`, `data`, `data_col2`, `printer_name` e `zpl_template` são considerados.

```json
{
  "label_type": "produto",
  "duas_colunas": true,
  "data": {
    "codigo": "1424",
    "descricao": "DENTE ENDO 24 RADIOPACO",
    "codigo_barras": "7890000015776"
  },
  "task_id": "86ad7wnjm",
  "task_name": "ORAIS(3032)_Qtd:1_cod:1424",
  "list_id": "901319664067",
  "task_ids": ["86ad7wnjm"],
  "detected_at": "2026-02-23T21:06:10Z",
  "printed_label": "enviado_impressao"
}
```

---

## Resposta (`PrintResponse`)

| Campo       | Tipo    | Descrição |
|------------|---------|-----------|
| `success`  | boolean | Sempre `true` quando a requisição é aceita (impressão imediata ou entrada na fila). |
| `message` | string  | Mensagem de sucesso. |
| `queue_id`| string (opcional) | Presente quando a impressão foi enfileirada (impressora indisponível ou falha na impressão imediata). |

Erros de validação (ex.: `data` ausente) retornam status 4xx com detalhe no corpo.
