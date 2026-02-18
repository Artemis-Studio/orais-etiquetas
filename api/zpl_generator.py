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
        
        # Dimensões: rolo 2 colunas 50x25mm
        try:
            cfg = get_config()
            dpi = cfg.get_label_dpi()
            label_width_mm = cfg.get_label_width_mm()
            label_height_mm = cfg.get_label_height_mm()
            margin_left_mm = cfg.get_label_margin_left()
            margin_top_mm = cfg.get_label_margin_top()
            margin_right_mm = cfg.get_label_margin_right()
            gap_mm = cfg.get_gap_between_columns_mm()
            font_scale = cfg.get_font_scale()
        except Exception:
            dpi, label_width_mm, label_height_mm = 203, 50, 25
            margin_left_mm, margin_top_mm, margin_right_mm, gap_mm = 4, 2, 8, 1
            font_scale = 1.25
        dots_per_mm = dpi / 25.4
        label_width = int(label_width_mm * dots_per_mm)
        label_height = int(label_height_mm * dots_per_mm)
        margin_left = int(margin_left_mm * dots_per_mm)
        margin_top = int(margin_top_mm * dots_per_mm)
        margin_right = int(margin_right_mm * dots_per_mm)
        gap_dots = int(gap_mm * dots_per_mm)
        total_width = margin_left + label_width + gap_dots + label_width + margin_right
        # Margem interna igual à calibração: ~1,5mm (8-12 dots a 203dpi)
        content_margin = max(8, int(1.5 * dots_per_mm))
        # Escala de fontes (base 203 dpi + font_scale do config)
        scale = dpi / 203 * font_scale
        f_desc = max(18, int(18 * scale))
        f_desc2 = max(15, int(15 * scale))
        f_ref = max(14, int(14 * scale))
        f_barcode = max(28, int(36 * scale))
        f_lote = max(12, int(12 * scale))
        
        # ^LH = desloca origem (x=margin_left evita vão, y=margin_top evita topo)
        # ^PW = largura total, ^LL = altura
        zpl = f"^XA\n^CI28\n^PQ1\n^LH{margin_left},{margin_top}^PW{total_width}^LL{label_height}\n"
        
        # Layout: tudo alinhado à esquerda (evita problema de calibração no centro)
        # Ordem: Descrição → REF | Pedido → Lote | Val → Código de barras (último)
        y_pos = content_margin
        line_spacing = 1.2
        x_left = content_margin  # posição fixa à esquerda - não depende de label_width

        # 1. Descrição
        desc_completa = f"{descricao} {descricao2}".strip() if (descricao or descricao2) else ""
        if desc_completa:
            max_chars_linha = 22
            linhas_desc = self._wrap_text(desc_completa, max_chars_linha)[:2]
            for linha in linhas_desc:
                if linha.strip():
                    zpl += f"^FO{x_left},{y_pos}^A0N,{f_desc},{f_desc}^FD{linha}^FS\n"
                    y_pos += int(f_desc * line_spacing)
            y_pos += int(2 * dots_per_mm)

        # 2. REF e Pedido (mesma linha, ambos à esquerda)
        if ref or pedido:
            partes = []
            if ref:
                partes.append(f"REF:{ref[:10]}")
            if pedido:
                partes.append(f"Ped:{pedido[:10]}")
            zpl += f"^FO{x_left},{y_pos}^A0N,{f_ref},{f_ref}^FD{'  '.join(partes)}^FS\n"
            y_pos += int(f_ref * line_spacing)

        # 3. Lote e Validade (mesma linha, alinhado à esquerda)
        if lote or validade:
            partes = []
            if lote:
                partes.append(f"Lote:{lote[:8]}")
            if validade:
                partes.append(f"Val:{validade[:10]}")
            zpl += f"^FO{x_left},{y_pos}^A0N,{f_lote},{f_lote}^FD{'  '.join(partes)}^FS\n"
            y_pos += int(f_lote * line_spacing)
            y_pos += int(3 * dots_per_mm)

        # 4. Código de barras (último, alinhado à esquerda - evita erro de centralização)
        if codigo_barras:
            if len(codigo_barras) == 13 and codigo_barras.isdigit():
                zpl += f"^FO{x_left},{y_pos}^BY2^BEN,{f_barcode},Y,N^FD{codigo_barras}^FS\n"
            else:
                zpl += f"^FO{x_left},{y_pos}^BY2^BCN,{f_barcode},Y,N,N^FD{codigo_barras}^FS\n"
        
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
            label_height_mm = cfg.get_label_height_mm()
            margin_left_mm = cfg.get_label_margin_left()
            margin_top_mm = cfg.get_label_margin_top()
            margin_right_mm = cfg.get_label_margin_right()
            gap_mm = cfg.get_gap_between_columns_mm()
        except Exception:
            dpi, label_width_mm, label_height_mm = 203, 50, 25
            margin_left_mm, margin_top_mm, margin_right_mm, gap_mm = 4, 2, 8, 1
        dots_per_mm = dpi / 25.4
        label_width = int(label_width_mm * dots_per_mm)
        label_height = int(label_height_mm * dots_per_mm)
        margin_left = int(margin_left_mm * dots_per_mm)
        margin_top = int(margin_top_mm * dots_per_mm)
        margin_right = int(margin_right_mm * dots_per_mm)
        gap_dots = int(gap_mm * dots_per_mm)
        if dual_column:
            total_width = margin_left + label_width + gap_dots + label_width + margin_right
        else:
            total_width = margin_left + label_width + margin_right
        t = 6  # espessura bordas (6 dots = visível em 300dpi)
        f_num = 32   # números da régua - máximo legibilidade (antes 28)
        f_tit = 24   # títulos [ESQ]/[DIR]
        f_ref = 22   # 0mm, 50mm, etc.
        # ^MD20 = densidade alta, ^LS0 = sem deslocamento
        zpl = f"^XA\n^CI28\n^PQ1\n^MD20\n^LS0\n^LT0\n^LH{margin_left},{margin_top}^PW{total_width}^LL{label_height}\n"
        
        # === COLUNA ESQUERDA: retângulo completo (^GB w,h,t = largura, altura, espessura borda) ===
        # ^GB desenha as 4 bordas de uma vez - mais confiável que 4 linhas separadas
        zpl += f"^FO0,0^GB{label_width},{label_height},{t}^FS\n"
        
        # Números horizontal (10,20,30,40mm) - na base, fonte grande
        for mm in range(10, min(50, label_width_mm), 10):
            x = int(mm * dots_per_mm)
            x_num = max(0, x - 14)
            zpl += f"^FO{x_num},{label_height - 38}^A0N,{f_num},{f_num}^FD{mm}^FS\n"
        
        # Números vertical (5,10,15,20mm) - à esquerda
        for mm in range(5, min(25, label_height_mm), 5):
            y = int(mm * dots_per_mm)
            y_num = max(0, y - 14)
            zpl += f"^FO8,{y_num}^A0N,{f_num},{f_num}^FD{mm}^FS\n"
        
        # Título e referências
        zpl += f"^FO{max(0, label_width//2 - 60)},6^A0N,{f_tit},{f_tit}^FD[ESQ] {label_width_mm}x{label_height_mm}mm^FS\n"
        zpl += f"^FO8,{label_height//2 - 12}^A0N,{f_ref},{f_ref}^FD0mm^FS\n"
        zpl += f"^FO{max(0, label_width-50)},{label_height//2 - 12}^A0N,{f_ref},{f_ref}^FD{label_width_mm}mm^FS\n"
        zpl += f"^FO8,{label_height-36}^A0N,{f_ref},{f_ref}^FD10,20,30,40=mm^FS\n"
        
        if dual_column:
            x_dir = label_width + gap_dots
            # COLUNA DIREITA: retângulo completo (4 bordas em um ^GB)
            zpl += f"^FO{x_dir},0^GB{label_width},{label_height},{t}^FS\n"
            for mm in range(10, min(50, label_width_mm), 10):
                x = x_dir + int(mm * dots_per_mm)
                x_num = max(x_dir, x - 14)
                zpl += f"^FO{x_num},{label_height - 38}^A0N,{f_num},{f_num}^FD{mm}^FS\n"
            for mm in range(5, min(25, label_height_mm), 5):
                y = int(mm * dots_per_mm)
                y_num = max(0, y - 14)
                zpl += f"^FO{x_dir + 8},{y_num}^A0N,{f_num},{f_num}^FD{mm}^FS\n"
            zpl += f"^FO{x_dir + max(0, label_width//2 - 50)},6^A0N,{f_tit},{f_tit}^FD[DIR] {label_width_mm}x{label_height_mm}mm^FS\n"
        
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
            gap_mm = cfg.get_gap_between_columns_mm()
        except Exception:
            dpi, label_width_mm, gap_mm = 203, 50, 1
        dots_per_mm = dpi / 25.4
        label_width = int(label_width_mm * dots_per_mm)
        gap_dots = int(gap_mm * dots_per_mm)
        offset_right = label_width + gap_dots
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
        body_right = re.sub(r'\^FO(\d+),', lambda m: f"^FO{int(m.group(1)) + offset_right},", body)
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

