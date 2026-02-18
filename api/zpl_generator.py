"""Gerador de comandos ZPL para etiquetas.
Compatível com layout do Sistema de Etiquetas v07.2 (50x25mm, 2 colunas).
"""
from typing import Dict, Optional
from config.config_loader import get_config


class ZPLGenerator:
    """Gera comandos ZPL para impressão de etiquetas Zebra."""
    
    def __init__(self):
        """Inicializa o gerador ZPL."""
        pass
    
    def _escape_zpl(self, text: str) -> str:
        """Escapa caracteres especiais para ZPL.
        
        Args:
            text: Texto a escapar
            
        Returns:
            Texto escapado
        """
        # Caracteres especiais do ZPL que precisam ser escapados
        # ^ é usado para comandos, então precisa ser escapado como ^^
        # \ precisa ser escapado como \\
        text = text.replace('^', '^^')
        text = text.replace('\\', '\\\\')
        return text
    
    def generate_product_label(self, data: Dict) -> str:
        """Gera comando ZPL para etiqueta de produto.
        
        Args:
            data: Dicionário com dados do produto:
                - codigo: Código do produto (usado como REF se ref não fornecido)
                - descricao: Descrição principal (ex: JG DENTE ENDO 21 AO 27 RADIO)
                - descricao2: Descrição secundária (ex: PACOS)
                - ref: Referência do produto
                - pedido: Número do pedido
                - codigo_barras ou ean: EAN-13 (13 dígitos, ex: 7890000005098) - OBRIGATÓRIO para código de barras
                - lote: Número do lote (opcional)
                - validade: Data de validade (opcional)
        
        Returns:
            String com comando ZPL completo
        """
        # Extrai dados - compatível com Sistema v07.2 (ean) e API (codigo_barras)
        codigo = self._escape_zpl(str(data.get('codigo', '')))
        descricao = self._escape_zpl(str(data.get('descricao', '')))
        descricao2 = self._escape_zpl(str(data.get('descricao2', '')))
        ref = self._escape_zpl(str(data.get('ref', codigo)))
        pedido = self._escape_zpl(str(data.get('pedido', '')))
        # IMPORTANTE: Usar codigo_barras ou ean (EAN-13). NUNCA usar codigo (ex: 1420) no código de barras!
        codigo_barras = str(data.get('codigo_barras') or data.get('ean') or '').strip()
        lote = self._escape_zpl(str(data.get('lote', '')))
        validade = self._escape_zpl(str(data.get('validade', '')))
        
        # Dimensões: rolo 2 colunas
        try:
            cfg = get_config()
            dpi = cfg.get_label_dpi()
            label_width_mm = cfg.get_label_width_mm()
            margin_left_mm = cfg.get_label_margin_left()
            margin_right_mm = cfg.get_label_margin_right()
        except Exception:
            dpi, label_width_mm = 300, 50
            margin_left_mm, margin_right_mm = 3, 10
        dots_per_mm = dpi / 25.4
        label_width = int(label_width_mm * dots_per_mm)
        label_height = int(25 * dots_per_mm)  # 25mm
        margin_left = int(margin_left_mm * dots_per_mm)   # evita corte no vão
        margin_right = int(margin_right_mm * dots_per_mm)  # borda DIR no final
        total_width = margin_left + label_width * 2 + margin_right
        margin = max(5, int(8 * dots_per_mm / 8))
        # Escala de fontes (base para 203 dpi, maior para 300 dpi)
        scale = dpi / 203
        f_desc = max(18, int(18 * scale))
        f_desc2 = max(15, int(15 * scale))
        f_ref = max(14, int(14 * scale))
        f_barcode = max(28, int(36 * scale))
        f_lote = max(12, int(12 * scale))
        
        # ^LH = desloca origem à direita (evita borda no vão)
        # ^PW = largura total
        # ^PQ1 = 1 cópia
        zpl = f"^XA\n^CI28\n^PQ1\n^LH{margin_left},0^PW{total_width}^LL{label_height}\n"
        
        # Conteúdo: x=0 agora é após margin_left (fora do vão)
        y_pos = margin
        
        # Descrição: quebra em múltiplas linhas (max ~28 chars/linha, max 3 linhas)
        # Evita truncar - nomes longos como "JG DENTE ENDO 21 AO 27 RADIO ETC ETC" quebram corretamente
        desc_completa = f"{descricao} {descricao2}".strip() if (descricao or descricao2) else ""
        if desc_completa:
            max_chars_linha = 28  # cabe na coluna esquerda (50mm, fonte ~22)
            max_linhas_desc = 3   # limite para caber barcode, REF, etc
            linhas_desc = self._wrap_text(desc_completa, max_chars_linha)[:max_linhas_desc]
            for linha in linhas_desc:
                if linha.strip():  # evita linha vazia
                    zpl += f"^FO{margin},{y_pos}^A0N,{f_desc},{f_desc}^FD{linha}^FS\n"
                    y_pos += int(f_desc * 1.2)
        
        # REF e Pedido na mesma linha - AMBOS na coluna esquerda (evitar que Pedido vá para direita)
        # REF à esquerda, Pedido logo após (mantém tudo dentro da etiqueta da esquerda)
        ref_pedido_x_offset = int(130 * scale)  # espaço entre REF e Pedido
        if ref or pedido:
            if ref:
                zpl += f"^FO{margin},{y_pos}^A0N,{f_ref},{f_ref}^FDREF:{ref}^FS\n"
            if pedido:
                # Pedido à direita do REF, mas sempre na coluna esquerda (x < label_width - margem)
                x_pedido = margin + ref_pedido_x_offset
                zpl += f"^FO{x_pedido},{y_pos}^A0N,{f_ref},{f_ref}^FDPedido:{pedido[:12]}^FS\n"
            y_pos += int(f_ref * 1.2)
        
        # Código de barras centralizado (cálculo manual - mais confiável que ^FB)
        barcode_width_est = 220  # EAN-13 ~220 dots com ^BY2
        x_barcode = (label_width - barcode_width_est) // 2
        if codigo_barras:
            if len(codigo_barras) == 13 and codigo_barras.isdigit():
                zpl += f"^FO{x_barcode},{y_pos}^BY2^BEN,{f_barcode},Y,N^FD{codigo_barras}^FS\n"
            else:
                zpl += f"^FO{x_barcode},{y_pos}^BY2^BCN,{f_barcode},Y,N,N^FD{codigo_barras}^FS\n"
            y_pos += int(f_barcode * 1.4)
        
        # Lote e Validade centralizados (cálculo manual)
        if lote or validade:
            linha_extra = []
            if lote:
                linha_extra.append(f"Lote:{lote[:8]}")
            if validade:
                linha_extra.append(f"Val:{validade[:10]}")
            texto_lote_val = ' '.join(linha_extra)
            # ~0.7 dots por ponto de fonte por caractere (fonte Zebra 0)
            texto_width_est = int(len(texto_lote_val) * f_lote * 0.7)
            x_lote = max(margin, (label_width - texto_width_est) // 2)
            zpl += f"^FO{x_lote},{y_pos}^A0N,{f_lote},{f_lote}^FD{texto_lote_val}^FS\n"
        
        zpl += "^XZ"
        
        return zpl.strip()
    
    def generate_calibration_label(self, dual_column: bool = True) -> str:
        """Gera etiqueta de calibração com marcações para validar tamanho real.
        Baseado no Sistema de Etiquetas v07.2. Apenas bordas e números - sem ticks
        que possam gerar risco no meio. Fontes 24-28 para máxima legibilidade."""
        try:
            cfg = get_config()
            dpi = cfg.get_label_dpi()
            label_width_mm = cfg.get_label_width_mm()
            margin_left_mm = cfg.get_label_margin_left()
            margin_right_mm = cfg.get_label_margin_right()
        except Exception:
            dpi, label_width_mm = 300, 50
            margin_left_mm, margin_right_mm = 3, 10
        dots_per_mm = dpi / 25.4
        label_width = int(label_width_mm * dots_per_mm)
        label_height = int(25 * dots_per_mm)
        margin_left = int(margin_left_mm * dots_per_mm)
        margin_right = int(margin_right_mm * dots_per_mm)
        total_width = margin_left + label_width * 2 + margin_right if dual_column else margin_left + label_width
        t = 6  # espessura bordas (6 dots = visível em 300dpi)
        f_num = 32   # números da régua - máximo legibilidade (antes 28)
        f_tit = 24   # títulos [ESQ]/[DIR]
        f_ref = 22   # 0mm, 50mm, etc.
        # ^MD20 = densidade alta (0-30) para números não ficarem fracos na base
        zpl = f"^XA\n^CI28\n^PQ1\n^MD20\n^LS0\n^LH{margin_left},0^PW{total_width}^LL{label_height}\n"
        
        # === COLUNA ESQUERDA: só as 4 bordas (sem ticks no meio - evita "risco") ===
        zpl += f"^FO0,0^GB{label_width},{t},{t}^FS\n"
        zpl += f"^FO0,{label_height-t}^GB{label_width},{t},{t}^FS\n"
        zpl += f"^FO0,0^GB{t},{label_height},{t}^FS\n"
        zpl += f"^FO{label_width-t},0^GB{t},{label_height},{t}^FS\n"
        
        # Números horizontal (10,20,30,40mm) - na base, fonte grande
        for mm in range(10, min(50, label_width_mm), 10):
            x = int(mm * dots_per_mm)
            x_num = max(0, x - 14)
            zpl += f"^FO{x_num},{label_height - 38}^A0N,{f_num},{f_num}^FD{mm}^FS\n"
        
        # Números vertical (5,10,15,20mm) - à esquerda
        for mm in range(5, 25, 5):
            y = int(mm * dots_per_mm)
            y_num = max(0, y - 14)
            zpl += f"^FO8,{y_num}^A0N,{f_num},{f_num}^FD{mm}^FS\n"
        
        # Título e referências
        zpl += f"^FO{max(0, label_width//2 - 60)},6^A0N,{f_tit},{f_tit}^FD[ESQ] {label_width_mm}x25mm^FS\n"
        zpl += f"^FO8,{label_height//2 - 12}^A0N,{f_ref},{f_ref}^FD0mm^FS\n"
        zpl += f"^FO{max(0, label_width-50)},{label_height//2 - 12}^A0N,{f_ref},{f_ref}^FD{label_width_mm}mm^FS\n"
        zpl += f"^FO8,{label_height-36}^A0N,{f_ref},{f_ref}^FD10,20,30,40=mm^FS\n"
        
        if dual_column:
            x_dir = label_width
            zpl += f"^FO{x_dir},0^GB{label_width},{t},{t}^FS\n"
            zpl += f"^FO{x_dir},{label_height-t}^GB{label_width},{t},{t}^FS\n"
            zpl += f"^FO{x_dir},0^GB{t},{label_height},{t}^FS\n"
            zpl += f"^FO{x_dir + label_width - t},0^GB{t},{label_height},{t}^FS\n"
            for mm in range(10, min(50, label_width_mm), 10):
                x = x_dir + int(mm * dots_per_mm)
                x_num = max(x_dir, x - 14)
                zpl += f"^FO{x_num},{label_height - 38}^A0N,{f_num},{f_num}^FD{mm}^FS\n"
            for mm in range(5, 25, 5):
                y = int(mm * dots_per_mm)
                y_num = max(0, y - 14)
                zpl += f"^FO{x_dir + 8},{y_num}^A0N,{f_num},{f_num}^FD{mm}^FS\n"
            zpl += f"^FO{x_dir + max(0, label_width//2 - 50)},6^A0N,{f_tit},{f_tit}^FD[DIR] {label_width_mm}x25mm^FS\n"
        
        zpl += "^XZ"
        return zpl.strip()
    
    def generate_dual_column_test_label(self, data: Optional[Dict] = None) -> str:
        """Gera ZPL para testar as duas colunas - mesmo conteúdo em esquerda e direita.
        
        Imprime a mesma etiqueta nas duas colunas do rolo (uma linha) para verificar
        se ambas imprimem corretamente e o layout está certo.
        
        Args:
            data: Dados do produto (usa dados de teste se None)
            
        Returns:
            String ZPL com conteúdo nas duas colunas
        """
        import re
        if data is None:
            data = {
                "codigo": "TESTE",
                "descricao": "Teste Duas Colunas",
                "descricao2": "ESQ + DIR",
                "ref": "999",
                "pedido": "12345",
                "codigo_barras": "7890000005098",
                "lote": "LOTE001",
                "validade": "31/12/2025",
            }
        zpl = self.generate_product_label(data)
        try:
            cfg = get_config()
            dpi = cfg.get_label_dpi()
            label_width_mm = cfg.get_label_width_mm()
        except Exception:
            dpi, label_width_mm = 300, 50
        dots_per_mm = dpi / 25.4
        label_width = int(label_width_mm * dots_per_mm)
        # Extrai o corpo (linhas com ^FO) e duplica com offset para coluna direita
        parts = zpl.split('^XZ')
        if len(parts) < 1:
            return zpl
        before_xz = parts[0].rstrip()
        lines = before_xz.split('\n')
        body_lines = [l for l in lines if '^FO' in l]
        if not body_lines:
            return zpl
        first_fo_idx = next(i for i, l in enumerate(lines) if '^FO' in l)
        header = '\n'.join(lines[:first_fo_idx]) + '\n'
        body = '\n'.join(body_lines)
        body_right = re.sub(r'\^FO(\d+),', lambda m: f"^FO{int(m.group(1)) + label_width},", body)
        return header + body + '\n' + body_right + '\n^XZ'
    
    def generate_custom_label(self, data: Dict, template: Optional[str] = None) -> str:
        """Gera comando ZPL customizado.
        
        Args:
            data: Dados para preencher a etiqueta
            template: Template ZPL customizado (opcional)
        
        Returns:
            String com comando ZPL
        """
        if template:
            # Substitui placeholders no template
            zpl = template
            for key, value in data.items():
                zpl = zpl.replace(f"{{{key}}}", str(value))
            return zpl
        
        # Fallback para etiqueta de produto
        return self.generate_product_label(data)
    
    def _wrap_text(self, text: str, max_length: int) -> list:
        """Quebra texto em linhas respeitando palavras e tamanho máximo.
        
        Args:
            text: Texto a quebrar (ex: "JG DENTE ENDO 21 AO 27 RADIO ETC ETC")
            max_length: Tamanho máximo por linha em caracteres
            
        Returns:
            Lista de linhas
        """
        if not text or not text.strip():
            return []
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            # Palavra maior que max_length: quebra no meio
            if word_length > max_length:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line, current_length = [], 0
                for i in range(0, word_length, max_length):
                    lines.append(word[i:i + max_length])
                continue
            if current_length + word_length + 1 <= max_length:
                current_line.append(word)
                current_length += word_length + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def validate_zpl(self, zpl: str) -> bool:
        """Valida se o comando ZPL está bem formado.
        
        Args:
            zpl: Comando ZPL a validar
            
        Returns:
            True se válido, False caso contrário
        """
        # Verifica se começa com ^XA e termina com ^XZ
        zpl_clean = zpl.strip()
        return zpl_clean.startswith('^XA') and zpl_clean.endswith('^XZ')

