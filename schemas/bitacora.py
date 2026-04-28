from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class BitacoraBase(BaseModel):
    id_usuario: int
    nombre_usuario: str
    evento: str
    recurso: str
    accion: str
    dispositivo: Optional[str] = None

class BitacoraCreate(BitacoraBase):
    """Esquema para crear un registro de bitácora. IP es opcional al crear."""
    ip: Optional[str] = None

class BitacoraResponse(BitacoraBase):
    """Esquema de respuesta de bitácora con ID y fecha"""
    id_bitacora: int
    fecha: datetime
    ip: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)