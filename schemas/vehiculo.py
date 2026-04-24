"""
schemas/vehiculo.py - Esquemas con Dataclasses para CRUD de Vehículos
Validación y serialización de datos para Marca, Modelo y Vehículo
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from .validators import validate_string_length, validate_year


# ============================================================================
# ESQUEMAS PARA VEHÍCULO
# ============================================================================

@dataclass
class VehiculoCreate:
    """Esquema para registrar un nuevo vehículo"""
    marca: str
    modelo: str
    placa: str
    anio: int
    color: Optional[str] = None
    
    
    def __post_init__(self):
        validate_string_length(self.placa, min_length=3, max_length=20, field_name="placa")
        if self.color:
            validate_string_length(self.color, max_length=30, field_name="color")
        if self.anio:
            validate_year(self.anio)


@dataclass
class VehiculoUpdate:
    """Esquema para actualizar un vehículo"""
    placa: Optional[str] = None
    color: Optional[str] = None
    anio: Optional[int] = None
    
    def __post_init__(self):
        if self.placa:
            validate_string_length(self.placa, min_length=3, max_length=20, field_name="placa")
        if self.color:
            validate_string_length(self.color, max_length=30, field_name="color")
        if self.anio:
            validate_year(self.anio)


@dataclass
class VehiculoResponse:
    """Esquema de respuesta para Vehículo (dataclass)"""
    id_vehiculo: int
    id_cliente: int
    marca: str
    modelo: str
    placa: str
    color: Optional[str]
    anio: Optional[int]
    fecha_registro: datetime


# ============================================================================
# ESQUEMAS PYDANTIC PARA RESPUESTAS (FastAPI serialization)
# ============================================================================

class VehiculoResponsePydantic(BaseModel):
    """Modelo Pydantic para respuesta de Vehículo (para serialización JSON)"""
    id_vehiculo: int
    id_cliente: int
    marca: str
    modelo: str
    placa: str
    color: Optional[str] = None
    anio: Optional[int] = None
    fecha_registro: datetime
    
    class Config:
        from_attributes = True  # Permite convertir desde ORM objects
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class VehiculoListResponsePydantic(BaseModel):
    """Modelo Pydantic para lista de vehículos"""
    total: int
    vehiculos: List[VehiculoResponsePydantic] = []
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class VehiculoDetailedResponsePydantic(VehiculoResponsePydantic):
    """Modelo Pydantic para respuesta detallada de Vehículo"""
    pass


@dataclass
class VehiculoDetailedResponse(VehiculoResponse):
    """Respuesta detallada de Vehículo (Hereda todo de VehiculoResponse)"""
    pass