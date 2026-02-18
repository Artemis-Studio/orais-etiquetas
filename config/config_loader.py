"""Sistema de carregamento de configurações."""
import yaml
import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Classe para gerenciar configurações da aplicação."""
    
    def __init__(self, config_path: str = None):
        """Inicializa a configuração.
        
        Args:
            config_path: Caminho para o arquivo de configuração YAML.
                        Se None, usa config/config.yaml
        """
        if config_path is None:
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "config.yaml"
        
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.load()
    
    def load(self):
        """Carrega configurações do arquivo YAML."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f) or {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor de configuração usando notação de ponto.
        
        Args:
            key: Chave no formato 'section.subsection.key'
            default: Valor padrão se a chave não existir
            
        Returns:
            Valor da configuração ou default
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_api_key(self) -> str:
        """Retorna a API key ou string vazia se não configurada."""
        return self.get('api.api_key', '')
    
    def is_auth_enabled(self) -> bool:
        """Verifica se autenticação está habilitada."""
        api_key = self.get_api_key()
        return bool(api_key and api_key.strip())
    
    def get_host(self) -> str:
        """Retorna o host da API."""
        return self.get('api.host', '0.0.0.0')
    
    def get_port(self) -> int:
        """Retorna a porta da API."""
        return self.get('api.port', 8000)
    
    def get_default_printer(self) -> str:
        """Retorna o nome da impressora padrão."""
        return self.get('printer.default_printer', '')
    
    def get_printer_timeout(self) -> int:
        """Retorna o timeout da impressora em segundos."""
        return self.get('printer.timeout', 30)
    
    def get_label_dpi(self) -> int:
        """Retorna o DPI da impressora para etiquetas (203 ou 300)."""
        return self.get('printer.label_dpi', 300)
    
    def get_label_margin_left(self) -> int:
        """Retorna margem esquerda em mm (evita corte no vão)."""
        return self.get('printer.label_margin_left', 3)

    def get_label_margin_top(self) -> int:
        """Retorna margem superior em mm (evita conteúdo no topo)."""
        return self.get('printer.label_margin_top', 0)
    
    def get_label_margin_right(self) -> int:
        """Retorna margem direita em mm (borda DIR chegar no final)."""
        return self.get('printer.label_margin_right', 10)
    
    def get_label_width_mm(self) -> int:
        """Retorna largura real da etiqueta em mm (45 se régua mostrar menor)."""
        return self.get('printer.label_width_mm', 50)

    def get_label_height_mm(self) -> int:
        """Retorna altura da etiqueta em mm (padrão 25)."""
        return self.get('printer.label_height_mm', 25)

    def get_gap_between_columns_mm(self) -> float:
        """Retorna espaço entre colunas em mm (0 = adjacentes)."""
        return float(self.get('printer.gap_between_columns_mm', 0))
    
    def get_retry_attempts(self) -> int:
        """Retorna o número de tentativas de retry."""
        return self.get('printer.retry_attempts', 3)
    
    def get_queue_check_interval(self) -> int:
        """Retorna o intervalo de verificação da fila em segundos."""
        return self.get('queue.check_interval', 5)
    
    def get_max_retries(self) -> int:
        """Retorna o máximo de tentativas na fila."""
        return self.get('queue.max_retries', 3)
    
    def get_log_level(self) -> str:
        """Retorna o nível de log."""
        return self.get('logging.level', 'INFO')
    
    def get_log_file(self) -> str:
        """Retorna o caminho do arquivo de log."""
        log_file = self.get('logging.file', 'logs/api.log')
        # Garante que o diretório existe
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return str(log_path)


# Instância global de configuração
_config_instance: Config = None


def get_config() -> Config:
    """Retorna a instância global de configuração."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

