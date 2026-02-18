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
        total_width = label_width * 2         # 100mm - largura total do rolo (2 colunas)
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
        
        # Layout: descricao, descricao2, REF|Pedido, código de barras
        y_pos = margin
        
        # Primeira linha: Descrição principal
        if descricao:
            desc_linha1 = descricao[:28] if len(descricao) > 28 else descricao
            zpl += f"^FO{margin},{y_pos}^A0N,{f_desc},{f_desc}^FD{desc_linha1}^FS\n"
            y_pos += int(f_desc * 1.2)
        
        # Segunda linha: Descrição secundária (ex: PACOS)
        if descricao2:
            zpl += f"^FO{margin},{y_pos}^A0N,{f_desc2},{f_desc2}^FD{descricao2}^FS\n"
            y_pos += int(f_desc2 * 1.2)
        
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
        
        # Código de barras (altura proporcional ao DPI)
        if codigo_barras:
            if len(codigo_barras) == 13 and codigo_barras.isdigit():
                zpl += f"^FO{margin},{y_pos}^BY2^BEN,{f_barcode},Y,N^FD{codigo_barras}^FS\n"
            else:
                zpl += f"^FO{margin},{y_pos}^BY2^BCN,{f_barcode},Y,N,N^FD{codigo_barras}^FS\n"
            y_pos += int(f_barcode * 1.4)
        
        # Lote e Validade (opcional)
        if lote or validade:
            linha_extra = []
            if lote:
                linha_extra.append(f"Lote:{lote[:8]}")
            if validade:
                linha_extra.append(f"Val:{validade[:10]}")
            zpl += f"^FO{margin},{y_pos}^A0N,{f_lote},{f_lote}^FD{' '.join(linha_extra)}^FS\n"
        
        zpl += "^XZ"
        
        return zpl.strip()
    
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
        """Quebra texto em linhas respeitando o tamanho máximo.
        
        Args:
            text: Texto a quebrar
            max_length: Tamanho máximo por linha
            
        Returns:
            Lista de linhas
        """
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
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
        
        return lines if lines else [text[:max_length]]
    
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

