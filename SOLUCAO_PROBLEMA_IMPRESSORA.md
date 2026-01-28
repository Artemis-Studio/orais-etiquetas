# Solução: Usuário Sem Acesso à Impressora

## 🔍 Problema

Quando você cria um novo usuário no Windows, ele pode não ter acesso às impressoras instaladas por outro usuário. Isso acontece porque:

- **Impressoras são configuradas por usuário** no Windows
- Cada usuário precisa ter a impressora instalada separadamente
- O serviço da API roda com as permissões do usuário atual

## ✅ Soluções

### Solução 1: Instalar Impressora para o Novo Usuário (Recomendado)

1. **Faça login com o novo usuário**
2. **Abra Configurações do Windows:**
   - Pressione `Win + I`
   - Vá em **Dispositivos** > **Impressoras e scanners**
3. **Adicione a impressora:**
   - Clique em **"Adicionar impressora ou scanner"**
   - Selecione sua impressora na lista
   - Siga o assistente de instalação

### Solução 2: Compartilhar Impressora do Usuário Original

1. **Faça login com o usuário que tem a impressora instalada**
2. **Compartilhe a impressora:**
   - Abra **Painel de Controle** > **Dispositivos e Impressoras**
   - Clique com botão direito na impressora
   - Selecione **"Propriedades da impressora"**
   - Vá na aba **"Compartilhamento"**
   - Marque **"Compartilhar esta impressora"**
   - Dê um nome para o compartilhamento
3. **No novo usuário, conecte à impressora compartilhada:**
   - Abra **Configurações** > **Impressoras e scanners**
   - Clique em **"Adicionar impressora ou scanner"**
   - Clique em **"A impressora que eu quero não está listada"**
   - Selecione **"Selecionar uma impressora compartilhada por nome"**
   - Digite: `\\NOME_DO_COMPUTADOR\NOME_DA_IMPRESSORA_COMPARTILHADA`

### Solução 3: Executar API como Administrador

Se você executar a API como Administrador, ela pode ter acesso a mais impressoras:

1. **Execute o serviço como Administrador:**
   ```bash
   # Pare o serviço atual
   net stop LabelPrintingAPI
   
   # Reinstale como Administrador
   # Execute install_service.bat como Administrador
   ```

2. **Ou execute diretamente como Administrador:**
   - Clique com botão direito em `run_api.py`
   - Selecione **"Executar como administrador"**

### Solução 4: Usar Impressora de Rede

Se a impressora estiver em rede, ela pode estar acessível para todos os usuários:

1. **Adicione a impressora de rede:**
   - Abra **Configurações** > **Impressoras e scanners**
   - Clique em **"Adicionar impressora ou scanner"**
   - Se a impressora aparecer na lista, selecione-a
   - Ou use o endereço IP da impressora

## 🔧 Diagnóstico

Execute o script de diagnóstico para verificar o acesso:

```bash
python diagnostico_impressoras.py
```

Este script mostra:
- ✅ Impressoras locais do usuário atual
- ✅ Impressoras conectadas
- ✅ Impressoras compartilhadas
- ✅ Impressora padrão
- ✅ Recomendações de solução

## 📋 Verificar Impressoras via CLI

```bash
# Listar impressoras localmente (sem API)
python cli.py list-printers

# Listar impressoras via API
python cli.py list-printers-api
```

## 🎯 Código Atualizado

O código foi atualizado para buscar impressoras de **todas as fontes**:
- ✅ Impressoras locais (`PRINTER_ENUM_LOCAL`)
- ✅ Impressoras conectadas (`PRINTER_ENUM_CONNECTED`)
- ✅ Impressoras compartilhadas (`PRINTER_ENUM_SHARED`)

Isso aumenta as chances de encontrar impressoras mesmo com diferentes configurações de usuário.

## ⚠️ Importante

**Após instalar a impressora para o novo usuário:**
1. Reinicie a API (se estiver rodando como serviço):
   ```bash
   net stop LabelPrintingAPI
   net start LabelPrintingAPI
   ```

2. Ou reinicie o processo se estiver rodando diretamente:
   - Pare o processo atual
   - Execute novamente: `python run_api.py`

3. Verifique se a impressora aparece:
   ```bash
   python cli.py list-printers-api
   ```

## 📞 Verificação Rápida

Execute estes comandos para verificar:

```bash
# 1. Diagnóstico completo
python diagnostico_impressoras.py

# 2. Listar via CLI local
python cli.py list-printers

# 3. Listar via API
python cli.py list-printers-api --api-url http://100.80.127.36:8000

# 4. Verificar status da API
python cli.py status --api-url http://100.80.127.36:8000
```

Se ainda não aparecer nenhuma impressora após seguir as soluções acima, pode ser necessário:
- Verificar se o serviço de impressão do Windows está rodando
- Verificar permissões do usuário
- Reinstalar os drivers da impressora
