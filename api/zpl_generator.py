"""Gerador de comandos ZPL para etiquetas."""
from typing import Dict, Optional


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
                - descricao: Descrição principal do produto (primeira linha)
                - descricao2: Descrição secundária (segunda linha, opcional)
                - ref: Referência do produto (opcional, usa codigo se não fornecido)
                - pedido: Número do pedido (opcional)
                - codigo_barras: Código de barras (opcional, usa codigo se não fornecido)
                - lote: Número do lote (opcional)
                - validade: Data de validade (opcional)
                - quantidade: Quantidade (opcional, mantido para compatibilidade)
                - preco: Preço (opcional, mantido para compatibilidade)
        
        Returns:
            String com comando ZPL completo
        """
        # Extrai dados e escapa caracteres especiais
        codigo = self._escape_zpl(str(data.get('codigo', '')))
        descricao = self._escape_zpl(str(data.get('descricao', '')))
        descricao2 = self._escape_zpl(str(data.get('descricao2', '')))
        ref = self._escape_zpl(str(data.get('ref', codigo)))  # Usa codigo se ref não fornecido
        pedido = self._escape_zpl(str(data.get('pedido', '')))
        codigo_barras = str(data.get('codigo_barras', codigo))  # Código de barras não precisa escape
        lote = self._escape_zpl(str(data.get('lote', '')))
        validade = self._escape_zpl(str(data.get('validade', '')))
        
        # Dimensões da etiqueta: 50mm x 25mm, 2 colunas (203 dpi: ~8 pontos/mm)
        width_dots = 400   # 50mm
        height_dots = 200  # 25mm
        margin = 5
        
        # Inicia comando ZPL com tamanho da etiqueta (^PW = largura, ^LL = comprimento)
        zpl = f"^XA\n^PW{width_dots}^LL{height_dots}^LH0,0\n"
        
        # Layout compacto para caber em 25mm de altura
        y_pos = margin
        # Primeira linha: Descrição principal (fonte menor)
        if descricao:
            desc_linha1 = descricao[:28] if len(descricao) > 28 else descricao
            zpl += f"^FO{margin},{y_pos}^A0N,14,14^FD{desc_linha1}^FS\n"
            y_pos += 16
        
        # Segunda linha: Descrição secundária
        if descricao2:
            zpl += f"^FO{margin},{y_pos}^A0N,12,12^FD{descricao2}^FS\n"
            y_pos += 14
        
        # REF e Pedido na mesma linha (fonte pequena)
        if ref or pedido:
            if ref:
                zpl += f"^FO{margin},{y_pos}^A0N,11,11^FDREF:{ref}^FS\n"
            if pedido:
                zpl += f"^FO{width_dots - 120},{y_pos}^A0N,11,11^FDPed:{pedido}^FS\n"
            y_pos += 13
        
        # Código de barras (Code 128) compacto
        if codigo_barras:
            zpl += f"^FO{margin},{y_pos}^BY1^BCN,28,Y,N,N^FD{codigo_barras}^FS\n"
            y_pos += 38
        
        # Lote e Validade numa linha (fonte pequena)
        if lote or validade:
            linha_extra = []
            if lote:
                linha_extra.append(f"Lote:{lote}")
            if validade:
                linha_extra.append(f"Val:{validade}")
            zpl += f"^FO{margin},{y_pos}^A0N,10,10^FD{' '.join(linha_extra)}^FS\n"
        
        # Fim do comando
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

