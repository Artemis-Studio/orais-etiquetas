# Solução: Usar Impressoras do Usuário Padrão

## 🎯 Problema

- Usuário `remoto` (SSH) não tem impressoras instaladas
- Usuário padrão (sem senha) já tem impressoras funcionando
- API precisa acessar as impressoras do usuário padrão

## ✅ Soluções (Escolha uma)

### Solução 1: Configurar Serviço para Rodar como Usuário Padrão (Recomendado)

**Vantagens:**
- ✅ Acessa impressoras do usuário padrão automaticamente
- ✅ Funciona mesmo após reiniciar
- ✅ Mais seguro e estável

**Passo a passo:**

1. **Descubra o nome do usuário padrão:**
   ```bash
   whoami
   ```
   Ou veja em: Configurações > Contas > Suas informações

2. **Pare o serviço atual** (se estiver rodando):
   ```bash
   net stop LabelPrintingAPI
   ```

3. **Configure o serviço para rodar como usuário padrão:**
   ```bash
   sc config LabelPrintingAPI obj= ".\NOME_DO_USUARIO_PADRAO" password= ""
   ```
   Exemplo: `sc config LabelPrintingAPI obj= ".\UsuarioPadrao" password= ""`

4. **Ou use o script criado:**
   ```bash
   configurar_servico_usuario_padrao.bat
   ```

5. **Inicie o serviço:**
   ```bash
   net start LabelPrintingAPI
   ```

6. **Verifique:**
   ```bash
   curl http://localhost:8000/printers
   ```

---

### Solução 2: Compartilhar Impressoras do Usuário Padrão

**Vantagens:**
- ✅ Não precisa mudar configuração do serviço
- ✅ Usuário remoto pode acessar as impressoras

**Passo a passo:**

1. **Faça login como usuário padrão** (fisicamente ou RDP)

2. **Compartilhe as impressoras:**
   - Abra **Painel de Controle** > **Dispositivos e Impressoras**
   - Para cada impressora:
     - Clique com botão direito > **Propriedades da impressora**
     - Aba **"Compartilhamento"**
     - Marque **"Compartilhar esta impressora"**
     - Dê um nome (ex: `Zebra_ZT230`)
     - Clique em **OK**

3. **No usuário `remoto`, conecte às impressoras compartilhadas:**
   - Abra **Configurações** (`Win + I`)
   - **Dispositivos** > **Impressoras e scanners**
   - **"Adicionar impressora ou scanner"**
   - **"A impressora que eu quero não está listada"**
   - **"Selecionar uma impressora compartilhada por nome"**
   - Digite: `\\ESCRITORIO2\NOME_DA_IMPRESSORA`
   - Siga o assistente

4. **Verifique:**
   ```bash
   listar_impressoras.bat
   ```

---

### Solução 3: Executar API com Credenciais do Usuário Padrão

**Vantagens:**
- ✅ Funciona sem configurar serviço
- ✅ Útil para testes

**Passo a passo:**

1. **Crie um script que executa como usuário padrão:**
   ```bash
   executar_com_usuario_padrao.bat
   ```

2. **Ou use runas manualmente:**
   ```bash
   runas /user:NOME_DO_USUARIO_PADRAO "python run_api.py"
   ```

---

### Solução 4: Usar Impressora por Nome Direto (Temporário)

**Se você souber o nome exato da impressora do usuário padrão:**

1. **Descubra o nome da impressora:**
   - Faça login como usuário padrão
   - Execute: `wmic printer get Name`
   - Anote o nome exato

2. **Configure na API:**
   - Edite `config/config.yaml`:
     ```yaml
     printer:
       default_printer: "Nome_Exato_da_Impressora"
     ```

3. **Ou especifique na requisição:**
   ```json
   {
     "printer_name": "Nome_Exato_da_Impressora"
   }
   ```

**Nota:** Isso pode não funcionar se o usuário remoto não tiver acesso à impressora.

---

## 🎯 Recomendação

**Use a Solução 1** (configurar serviço como usuário padrão) porque:
- ✅ É a mais estável
- ✅ Funciona automaticamente
- ✅ Não precisa compartilhar impressoras
- ✅ Mantém funcionando após reiniciar

---

## 📋 Verificação

Após aplicar qualquer solução:

```bash
# 1. Verificar impressoras via API
curl http://localhost:8000/printers

# 2. Verificar status
curl http://localhost:8000/status

# 3. Testar impressão
curl -X POST http://localhost:8000/print \
  -H "Content-Type: application/json" \
  -d '{"label_type":"produto","data":{"codigo":"123","descricao":"Teste"}}'
```

---

## 🔧 Scripts Criados

- `configurar_servico_usuario_padrao.bat` - Configura serviço automaticamente
- `executar_com_usuario_padrao.bat` - Executa API como outro usuário
- `descobrir_usuario_padrao.bat` - Descobre nome do usuário padrão
