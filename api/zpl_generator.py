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
        
        # Dimensões: rolo 2 colunas de 50x25mm (100mm largura total)
        try:
            dpi = get_config().get_label_dpi()
        except Exception:
            dpi = 300
        dots_per_mm = dpi / 25.4
        label_width = int(50 * dots_per_mm)   # 50mm - uma coluna
        label_height = int(25 * dots_per_mm)  # 25mm
        # Margem extra à direita (evita corte da etiqueta direita)
        try:
            margin_right_mm = get_config().get_label_margin_right()
        except Exception:
            margin_right_mm = 8
        margin_right = int(margin_right_mm * dots_per_mm)
        total_width = label_width * 2 + margin_right
        margin = max(5, int(8 * dots_per_mm / 8))
        # Escala de fontes (base para 203 dpi, maior para 300 dpi)
        scale = dpi / 203
        f_desc = max(18, int(18 * scale))
        f_desc2 = max(15, int(15 * scale))
        f_ref = max(14, int(14 * scale))
        f_barcode = max(28, int(36 * scale))
        f_lote = max(12, int(12 * scale))
        
        # ^PW = largura total do rolo (2 colunas)
        # ^LL = altura de uma etiqueta
        # Conteúdo restrito à coluna esquerda (x entre 0 e label_width)
        # ^PQ1 = 1 cópia apenas
        zpl = f"^XA\n^CI28\n^PQ1\n^PW{total_width}^LL{label_height}^LH0,0\n"
        
        # Layout: descricao (com quebra de linha), REF|Pedido, código de barras
        # Combina descricao + descricao2 e quebra por palavras (cabe na etiqueta esquerda)
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
        
        Inclui: bordas, réguas em mm, cantos marcados, identificação ESQ/DIR.
        Use para medir e relatar o que aparece impresso.
        
        Args:
            dual_column: True = duas colunas, False = apenas esquerda
            
        Returns:
            String ZPL de calibração
        """
        try:
            dpi = get_config().get_label_dpi()
        except Exception:
            dpi = 300
        dots_per_mm = dpi / 25.4
        label_width = int(50 * dots_per_mm)
        label_height = int(25 * dots_per_mm)
        try:
            margin_right = int(get_config().get_label_margin_right() * dots_per_mm)
        except Exception:
            margin_right = int(8 * dots_per_mm)
        total_width = label_width * 2 + margin_right if dual_column else label_width
        t = 2  # espessura das linhas (dots)
        
        zpl = f"^XA\n^CI28\n^PQ1\n^PW{total_width}^LL{label_height}^LH0,0\n"
        
        # Borda externa - esquerda (0 a label_width)
        zpl += f"^FO0,0^GB{label_width},{t},{t}^FS\n"      # topo
        zpl += f"^FO0,{label_height-t}^GB{label_width},{t},{t}^FS\n"  # base
        zpl += f"^FO0,0^GB{t},{label_height},{t}^FS\n"     # esquerda
        zpl += f"^FO{label_width-t},0^GB{t},{label_height},{t}^FS\n"  # direita col1
        
        # Marcações a cada 10mm na horizontal - ticks verticais (esquerda)
        for mm in range(10, 50, 10):
            x = int(mm * dots_per_mm)
            zpl += f"^FO{x},0^GB{t},6,{t}^FS\n"  # tick superior
            zpl += f"^FO{x},{label_height-6}^GB{t},6,{t}^FS\n"  # tick inferior
            zpl += f"^FO{x-5},{label_height-16}^A0N,10,10^FD{mm}^FS\n"  # número
        
        # Marcações a cada 5mm na vertical - ticks horizontais (esquerda)
        for mm in range(5, 25, 5):
            y = int(mm * dots_per_mm)
            zpl += f"^FO0,{y}^GB6,{t},{t}^FS\n"  # tick esquerdo
            zpl += f"^FO{label_width-6},{y}^GB6,{t},{t}^FS\n"  # tick direito
            zpl += f"^FO2,{y-5}^A0N,10,10^FD{mm}^FS\n"  # número
        
        # Identificação e referência
        zpl += f"^FO{label_width//2 - 45},2^A0N,14,14^FD[ESQ] 50x25mm 300dpi^FS\n"
        zpl += f"^FO2,{label_height//2 - 6}^A0N,10,10^FD0mm^FS\n"
        zpl += f"^FO{label_width-35},{label_height//2 - 6}^A0N,10,10^FD50mm^FS\n"
        zpl += f"^FO2,{label_height-14}^A0N,8,8^FD10,20,30,40=mm^FS\n"
        
        if dual_column:
            # Borda coluna direita
            x_dir = label_width
            zpl += f"^FO{x_dir},0^GB{label_width},{t},{t}^FS\n"
            zpl += f"^FO{x_dir},{label_height-t}^GB{label_width},{t},{t}^FS\n"
            zpl += f"^FO{x_dir},0^GB{t},{label_height},{t}^FS\n"
            zpl += f"^FO{x_dir + label_width - t},0^GB{t},{label_height},{t}^FS\n"
            # Marcações 10mm na coluna direita
            for mm in range(10, 50, 10):
                x = x_dir + int(mm * dots_per_mm)
                zpl += f"^FO{x},0^GB{t},8,{t}^FS\n"
                zpl += f"^FO{x},{label_height-8}^GB{t},8,{t}^FS\n"
                zpl += f"^FO{x-4},{label_height-18}^A0N,12,12^FD{mm}^FS\n"
            zpl += f"^FO{x_dir + label_width//2 - 30},5^A0N,18,18^FD[DIR 50x25mm]^FS\n"
        
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
            label_width = int(50 * (get_config().get_label_dpi() / 25.4))
        except Exception:
            label_width = 600
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

