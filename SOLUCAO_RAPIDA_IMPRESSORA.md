# Solução Rápida: Impressora Não Encontrada

## 🚨 Problema Atual

A API está rodando mas não encontra impressora padrão:
```
ERROR - Erro ao obter impressora padrão: The default printer was not found.
WARNING - Impressora não disponível: padrão
```

## ✅ Solução Rápida

### Opção 1: Listar Impressoras Disponíveis

Execute:
```bash
listar_impressoras.bat
```

Ou via API (se estiver rodando):
```bash
curl http://localhost:8000/printers
```

### Opção 2: Configurar Impressora no config.yaml

1. **Descubra o nome exato da impressora:**
   ```bash
   listar_impressoras.bat
   ```

2. **Edite `config/config.yaml`:**
   ```yaml
   printer:
     default_printer: "Nome_Exato_da_Impressora"  # Coloque o nome aqui
   ```

3. **Reinicie a API**

### Opção 3: Especificar Impressora na Requisição

Na requisição JSON, especifique a impressora:
```json
{
  "label_type": "produto",
  "data": { ... },
  "printer_name": "Nome_Exato_da_Impressora"
}
```

### Opção 4: Instalar/Configurar Impressora no Windows

1. **Abra Configurações do Windows** (`Win + I`)
2. **Vá em:** Dispositivos > Impressoras e scanners
3. **Clique em:** "Adicionar impressora ou scanner"
4. **Selecione sua impressora** e instale
5. **Defina como padrão** (opcional, mas recomendado)

## 🔧 Código Atualizado

O código foi atualizado para:
- ✅ Usar a **primeira impressora disponível** quando não há padrão
- ✅ Buscar impressoras de **todas as fontes** (local, conectada, compartilhada)
- ✅ Logar qual impressora está sendo usada

## 📋 Verificação

Após configurar, verifique:

```bash
# 1. Listar impressoras
listar_impressoras.bat

# 2. Verificar status da API
curl http://localhost:8000/status

# 3. Verificar impressoras via API
curl http://localhost:8000/printers
```

## ⚠️ Importante

**Se não aparecer nenhuma impressora:**

1. **Execute o diagnóstico:**
   ```bash
   diagnostico.bat
   ```

2. **Instale a impressora no Windows** (veja Opção 4 acima)

3. **Verifique se o serviço de impressão está rodando:**
   - Abra `services.msc`
   - Verifique se "Spooler de Impressão" está rodando

4. **Reinicie a API** após instalar a impressora

## 🎯 Resumo

1. Execute `listar_impressoras.bat` para ver impressoras disponíveis
2. Se aparecer alguma, configure em `config.yaml` ou use na requisição
3. Se não aparecer nenhuma, instale a impressora no Windows primeiro
4. Reinicie a API após configurar
