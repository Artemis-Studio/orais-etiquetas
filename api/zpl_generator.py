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
                - codigo: Código do produto
                - descricao: Descrição do produto
                - quantidade: Quantidade (opcional)
                - preco: Preço (opcional)
                - codigo_barras: Código de barras (opcional, usa codigo se não fornecido)
                - outras informações customizadas
        
        Returns:
            String com comando ZPL completo
        """
        # Extrai dados e escapa caracteres especiais
        codigo = self._escape_zpl(str(data.get('codigo', '')))
        descricao = self._escape_zpl(str(data.get('descricao', '')))
        quantidade = self._escape_zpl(str(data.get('quantidade', '')))
        preco = self._escape_zpl(str(data.get('preco', '')))
        codigo_barras = str(data.get('codigo_barras', codigo))  # Código de barras não precisa escape
        
        # Dimensões da etiqueta (ajuste conforme necessário)
        # Padrão: 4x2 polegadas (101.6mm x 50.8mm)
        width = 400  # pontos (4 polegadas * 100 dpi)
        height = 200  # pontos (2 polegadas * 100 dpi)
        
        # Inicia comando ZPL
        zpl = f"""
^XA
^FO20,20^A0N,30,30^FDCODIGO:^FS
^FO20,50^A0N,25,25^FD{codigo}^FS
"""
        
        # Código de barras (Code 128)
        if codigo_barras:
            zpl += f"^FO20,80^BY2^BCN,50,Y,N,N^FD{codigo_barras}^FS\n"
        
        # Descrição
        if descricao:
            # Quebra linha se muito longa
            desc_lines = self._wrap_text(descricao, 30)
            y_pos = 140
            for line in desc_lines[:2]:  # Máximo 2 linhas
                zpl += f"^FO20,{y_pos}^A0N,20,20^FD{line}^FS\n"
                y_pos += 25
        
        # Quantidade
        if quantidade:
            zpl += f"^FO20,{y_pos}^A0N,20,20^FDQTD: {quantidade}^FS\n"
            y_pos += 25
        
        # Preço
        if preco:
            zpl += f"^FO20,{y_pos}^A0N,25,25^FDR$ {preco}^FS\n"
        
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

