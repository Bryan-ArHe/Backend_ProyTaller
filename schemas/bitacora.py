from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class BitacoraBase: 
    id_usuario: int
    nombre_usuario: str
    evento: str
    recurso: str
    accion: str
    ip: str
    endpoint: str
    payload: Optional[str] = None
    dispositivo: Optional[str] = None

@dataclass
class BitacoraCreate(BitacoraBase):
    """Schema para crear un nuevo registro de bitácora"""
    pass

@dataclass
class BitacoraResponse:
    """Schema para respuesta de bitácora"""
    id_bitacora: int
    fecha: datetime
    id_usuario: int
    nombre_usuario: str
    evento: str
    recurso: str
    accion: str
    ip: str
    endpoint: str
    payload: Optional[str] = None
    dispositivo: Optional[str] = None

@dataclass
class FiltrosBitacora:
    id_usuario: Optional[int] = None
    nombre_usuario: Optional[str] = None
    evento: Optional[str] = None
    recurso: Optional[str] = None
    accion: Optional[str] = None
    ip: Optional[str] = None
    endpoint: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None