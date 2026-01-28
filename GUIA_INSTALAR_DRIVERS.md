# Guia: Instalar Drivers da Impressora

## 🔍 Problema Identificado

O usuário `remoto` provavelmente não tem os **drivers da impressora instalados**. Sem drivers, a impressora não aparece na lista mesmo que esteja conectada.

## ✅ Solução: Instalar Drivers

### Passo 1: Identificar o Modelo da Impressora

**Opções para descobrir:**

1. **Verificar na própria impressora:**
   - Olhe na etiqueta/modelo físico
   - Exemplos: "Zebra ZT230", "Zebra ZD420", etc.

2. **Verificar dispositivos conectados:**
   ```bash
   verificar_dispositivos_conectados.bat
   ```
   Isso pode mostrar dispositivos conectados mas sem drivers.

3. **Verificar em outro usuário/computador:**
   - Se outro usuário tem a impressora funcionando
   - Veja o nome/modelo nas propriedades da impressora

### Passo 2: Baixar os Drivers

**Opções:**

#### Opção A: Download Automático pelo Windows

1. **Conecte a impressora** (USB ou rede)
2. **Abra Configurações** (`Win + I`)
3. **Dispositivos** > **Impressoras e scanners**
4. **"Adicionar impressora ou scanner"**
5. Se aparecer "Impressora não encontrada", clique em **"A impressora que eu quero não está listada"**
6. Escolha **"Adicionar uma impressora local ou de rede com configurações manuais"**
7. O Windows tentará instalar drivers automaticamente

#### Opção B: Download Manual do Fabricante

**Para impressoras Zebra (mais comum):**

1. **Acesse:** https://www.zebra.com/us/en/support-downloads/printers.html
2. **Selecione seu modelo** (ex: ZT230, ZD420, etc.)
3. **Baixe o driver** (geralmente "ZDesigner Driver" ou "Zebra Setup Utilities")
4. **Execute o instalador** como Administrador

**Para outras marcas:**
- **HP:** https://support.hp.com/drivers
- **Epson:** https://epson.com/Support
- **Brother:** https://support.brother.com
- **Etc.**

### Passo 3: Instalar os Drivers

#### Método 1: Instalador Automático (Recomendado)

1. **Execute o arquivo baixado** como **Administrador**
   - Clique com botão direito > **"Executar como administrador"**
2. **Siga o assistente de instalação**
3. **Conecte a impressora** quando solicitado
4. **Complete a instalação**

#### Método 2: Instalação Manual via Windows

1. **Baixe e extraia** os drivers
2. **Abra Configurações** > **Impressoras e scanners**
3. **"Adicionar impressora ou scanner"**
4. **"A impressora que eu quero não está listada"**
5. **"Adicionar uma impressora local ou de rede com configurações manuais"**
6. **"Usar uma porta existente"** ou criar nova
7. **"Instalar um driver de impressora"**
8. **"Tenho um disco"** e navegue até a pasta dos drivers
9. **Selecione o arquivo .inf** dos drivers
10. **Complete a instalação**

### Passo 4: Verificar Instalação

Após instalar os drivers:

```bash
listar_impressoras.bat
```

A impressora deve aparecer agora!

## 🚨 Problemas Comuns

### "Windows não encontra os drivers automaticamente"

**Solução:**
- Baixe manualmente do site do fabricante
- Use o método de instalação manual acima

### "Erro ao instalar drivers"

**Soluções:**
1. **Execute como Administrador**
2. **Desative temporariamente antivírus**
3. **Verifique se o driver é compatível** com sua versão do Windows
4. **Tente drivers genéricos** se disponível (ex: Generic / Text Only)

### "Driver instalado mas impressora não aparece"

**Soluções:**
1. **Reinicie o serviço de impressão:**
   ```bash
   net stop spooler
   net start spooler
   ```

2. **Reinicie o computador**

3. **Adicione a impressora manualmente** nas Configurações

### "Não sei qual é o modelo da impressora"

**Soluções:**
1. **Verifique na etiqueta física** da impressora
2. **Verifique em outro computador** que tem a impressora funcionando
3. **Use drivers genéricos** como teste:
   - Generic / Text Only
   - Generic PostScript Printer
   - Zebra Generic (se for Zebra)

## 📋 Checklist de Instalação

- [ ] Identifiquei o modelo da impressora
- [ ] Baixei os drivers corretos
- [ ] Executei como Administrador
- [ ] Instalei os drivers com sucesso
- [ ] Executei `listar_impressoras.bat` e a impressora apareceu
- [ ] Configurei em `config/config.yaml` (opcional)

## 🎯 Resumo Rápido

1. **Descubra o modelo** da impressora
2. **Baixe os drivers** do site do fabricante
3. **Instale como Administrador**
4. **Adicione a impressora** nas Configurações do Windows
5. **Verifique** com `listar_impressoras.bat`

## 💡 Dica

**Para impressoras Zebra**, geralmente você precisa:
- **ZDesigner Driver** (driver principal)
- **Zebra Setup Utilities** (ferramentas de configuração)

Ambos podem ser baixados do site da Zebra.

---

**Após instalar os drivers e a impressora, execute `listar_impressoras.bat` para confirmar!**
