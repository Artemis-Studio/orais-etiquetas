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
        
        # Dimensões da etiqueta (ajuste conforme necessário)
        # Padrão: 4x2 polegadas (101.6mm x 50.8mm)
        width = 400  # pontos (4 polegadas * 100 dpi)
        height = 200  # pontos (2 polegadas * 100 dpi)
        
        # Inicia comando ZPL
        zpl = "^XA\n"
        
        # Primeira linha: Descrição principal (ex: "JG DENTE ENDO 21 AO 27 RADIO")
        y_pos = 20
        if descricao:
            # Limita tamanho da descrição para caber na etiqueta
            desc_linha1 = descricao[:35] if len(descricao) > 35 else descricao
            zpl += f"^FO20,{y_pos}^A0N,25,25^FD{desc_linha1}^FS\n"
            y_pos += 30
        
        # Segunda linha: Descrição secundária (ex: "PACOS")
        if descricao2:
            zpl += f"^FO20,{y_pos}^A0N,25,25^FD{descricao2}^FS\n"
            y_pos += 30
        
        # Linha com REF e Pedido lado a lado
        if ref or pedido:
            # REF no lado esquerdo
            if ref:
                zpl += f"^FO20,{y_pos}^A0N,20,20^FDREF: {ref}^FS\n"
            # Pedido no lado direito (alinhado com REF)
            if pedido:
                # Calcula posição X para alinhar à direita (largura da etiqueta - margem - tamanho do texto)
                # Aproximadamente 200 pontos de largura útil, então posiciona a partir de 180
                zpl += f"^FO180,{y_pos}^A0N,20,20^FDPedido: {pedido}^FS\n"
            y_pos += 25
        
        # Código de barras (Code 128) abaixo de REF/Pedido
        if codigo_barras:
            # Posição Y após REF/Pedido
            zpl += f"^FO20,{y_pos}^BY2^BCN,50,Y,N,N^FD{codigo_barras}^FS\n"
            # Altura do código de barras + texto abaixo dele
            y_pos += 60
        
        # Lote abaixo do código de barras
        if lote:
            zpl += f"^FO20,{y_pos}^A0N,20,20^FDLote: {lote}^FS\n"
            y_pos += 25
        
        # Validade abaixo do lote
        if validade:
            zpl += f"^FO20,{y_pos}^A0N,20,20^FDValidade: {validade}^FS\n"
        
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

