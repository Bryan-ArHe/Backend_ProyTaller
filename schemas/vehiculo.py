"""
schemas/vehiculo.py - Esquemas con Dataclasses para CRUD de Vehículos
Validación y serialización de datos para Marca, Modelo y Vehículo
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from .validators import validate_string_length, validate_year


# ============================================================================
# ESQUEMAS PARA MARCA
# ============================================================================

@dataclass
class MarcaCreate:
    """Esquema para crear una nueva marca"""
    nombre: str
    pais_origen: Optional[str] = None
    
    def __post_init__(self):
        validate_string_length(self.nombre, min_length=3, max_length=100, field_name="nombre")
        if self.pais_origen:
            validate_string_length(self.pais_origen, max_length=100, field_name="pais_origen")


@dataclass
class MarcaResponse:
    """Esquema de respuesta para Marca"""
    id_marca: int
    nombre: str
    pais_origen: Optional[str]
    fecha_creacion: datetime


# ============================================================================
# ESQUEMAS PARA MODELO
# ============================================================================

@dataclass
class ModeloCreate:
    """Esquema para crear un nuevo modelo"""
    id_marca: int
    nombre: str
    año_inicio: Optional[int] = None
    año_fin: Optional[int] = None
    
    def __post_init__(self):
        validate_string_length(self.nombre, min_length=3, max_length=100, field_name="nombre")
        if self.año_inicio:
            validate_year(self.año_inicio)
        if self.año_fin:
            validate_year(self.año_fin)


@dataclass
class ModeloUpdate:
    """Esquema para actualizar un modelo"""
    nombre: Optional[str] = None
    año_inicio: Optional[int] = None
    año_fin: Optional[int] = None
    
    def __post_init__(self):
        if self.nombre:
            validate_string_length(self.nombre, min_length=3, max_length=100, field_name="nombre")
        if self.año_inicio:
            validate_year(self.año_inicio)
        if self.año_fin:
            validate_year(self.año_fin)


@dataclass
class ModeloResponse:
    """Esquema de respuesta para Modelo"""
    id_modelo: int
    id_marca: int
    nombre: str
    año_inicio: Optional[int]
    año_fin: Optional[int]
    fecha_creacion: datetime


@dataclass
class ModeloWithMarca(ModeloResponse):
    """Modelo con información de su marca"""
    marca: MarcaResponse


# Now we can define MarcaWithModelos after ModeloResponse
@dataclass
class MarcaWithModelos(MarcaResponse):
    """Marca con sus modelos asociados"""
    modelos: List[ModeloResponse] = field(default_factory=list)


# ============================================================================
# ESQUEMAS PARA VEHÍCULO
# ============================================================================

@dataclass
class VehiculoCreate:
    """Esquema para registrar un nuevo vehículo"""
    id_modelo: int
    placa: str
    vin: Optional[str] = None
    color: Optional[str] = None
    año: Optional[int] = None
    
    def __post_init__(self):
        validate_string_length(self.placa, min_length=3, max_length=20, field_name="placa")
        if self.vin:
            validate_string_length(self.vin, max_length=50, field_name="vin")
        if self.color:
            validate_string_length(self.color, max_length=30, field_name="color")
        if self.año:
            validate_year(self.año)


@dataclass
class VehiculoUpdate:
    """Esquema para actualizar un vehículo"""
    placa: Optional[str] = None
    vin: Optional[str] = None
    color: Optional[str] = None
    año: Optional[int] = None
    estado: Optional[str] = None
    
    def __post_init__(self):
        if self.placa:
            validate_string_length(self.placa, min_length=3, max_length=20, field_name="placa")
        if self.vin:
            validate_string_length(self.vin, max_length=50, field_name="vin")
        if self.color:
            validate_string_length(self.color, max_length=30, field_name="color")
        if self.año:
            validate_year(self.año)


@dataclass
class VehiculoResponse:
    """Esquema de respuesta para Vehículo"""
    id_vehiculo: int
    id_cliente: int
    id_modelo: int
    placa: str
    vin: Optional[str]
    color: Optional[str]
    año: Optional[int]
    estado: str
    fecha_registro: datetime


@dataclass
class VehiculoDetailedResponse(VehiculoResponse):
    """Vehículo con información completa de marca y modelo"""
    modelo: ModeloWithMarca


@dataclass
class VehiculoListResponse:
    """Respuesta para lista de vehículos del usuario"""
    total: int
    vehiculos: List[VehiculoDetailedResponse] = field(default_factory=list)
