"""Modelos Pydantic para validação de dados."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class PrintRequest(BaseModel):
    """Modelo para requisição de impressão."""
    label_type: str = Field(default="produto", description="Tipo de etiqueta")
    data: Dict[str, Any] = Field(..., description="Dados da etiqueta")
    printer_name: Optional[str] = Field(None, description="Nome da impressora (opcional)")
    zpl_template: Optional[str] = Field(None, description="Template ZPL customizado (opcional)")
    duas_colunas: bool = Field(default=False, description="Imprimir nas 2 colunas")
    data_col2: Optional[Dict[str, Any]] = Field(None, description="Dados da coluna direita (se vazio, usa data em ambas)")


class PrintResponse(BaseModel):
    """Modelo para resposta de impressão."""
    success: bool
    queue_id: Optional[str] = None
    message: str


class StatusResponse(BaseModel):
    """Modelo para resposta de status."""
    status: str
    printer_available: bool
    printer_name: Optional[str] = None
    queue_stats: Dict[str, int]


class QueueItemResponse(BaseModel):
    """Modelo para item da fila."""
    id: str
    created_at: str
    status: str
    attempts: int
    error_message: Optional[str] = None
    printer_name: Optional[str] = None

