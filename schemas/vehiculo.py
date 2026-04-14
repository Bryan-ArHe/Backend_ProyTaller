"""
schemas/vehiculo.py - Esquemas Pydantic para CRUD de Vehículos
Validación y serialización de datos para Marca, Modelo y Vehículo
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================================================
# ESQUEMAS PARA MARCA
# ============================================================================

class MarcaCreate(BaseModel):
    """Esquema para crear una nueva marca"""
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre de la marca")
    pais_origen: Optional[str] = Field(None, max_length=100, description="País de origen")


class MarcaResponse(BaseModel):
    """Esquema de respuesta para Marca"""
    id: int
    nombre: str
    pais_origen: Optional[str]
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True


class MarcaWithModelos(MarcaResponse):
    """Marca con sus modelos asociados"""
    modelos: List["ModeloResponse"] = []


# ============================================================================
# ESQUEMAS PARA MODELO
# ============================================================================

class ModeloCreate(BaseModel):
    """Esquema para crear un nuevo modelo"""
    id_marca: int = Field(..., description="ID de la marca")
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre del modelo")
    año_inicio: Optional[int] = Field(None, ge=1900, le=2100, description="Año de inicio de producción")
    año_fin: Optional[int] = Field(None, ge=1900, le=2100, description="Año de fin de producción")


class ModeloUpdate(BaseModel):
    """Esquema para actualizar un modelo"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    año_inicio: Optional[int] = Field(None, ge=1900, le=2100)
    año_fin: Optional[int] = Field(None, ge=1900, le=2100)


class ModeloResponse(BaseModel):
    """Esquema de respuesta para Modelo"""
    id: int
    id_marca: int
    nombre: str
    año_inicio: Optional[int]
    año_fin: Optional[int]
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True


class ModeloWithMarca(ModeloResponse):
    """Modelo con información de su marca"""
    marca: MarcaResponse


# ============================================================================
# ESQUEMAS PARA VEHÍCULO
# ============================================================================

class VehiculoCreate(BaseModel):
    """Esquema para registrar un nuevo vehículo"""
    id_modelo: int = Field(..., description="ID del modelo del vehículo")
    placa: str = Field(..., min_length=3, max_length=20, description="Placa del vehículo (ÚNICA)")
    vin: Optional[str] = Field(None, max_length=50, description="VIN (Número de serie)")
    color: Optional[str] = Field(None, max_length=30, description="Color del vehículo")
    año: Optional[int] = Field(None, ge=1900, le=2100, description="Año de fabricación")


class VehiculoUpdate(BaseModel):
    """Esquema para actualizar un vehículo"""
    placa: Optional[str] = Field(None, min_length=3, max_length=20)
    vin: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=30)
    año: Optional[int] = Field(None, ge=1900, le=2100)
    estado: Optional[str] = Field(None, description="ACTIVO, INACTIVO, MANTENIMIENTO")


class VehiculoResponse(BaseModel):
    """Esquema de respuesta para Vehículo"""
    id: int
    id_cliente: int
    id_modelo: int
    placa: str
    vin: Optional[str]
    color: Optional[str]
    año: Optional[int]
    estado: str
    fecha_registro: datetime
    
    class Config:
        from_attributes = True


class VehiculoDetailedResponse(VehiculoResponse):
    """Vehículo con información completa de marca y modelo"""
    modelo: ModeloWithMarca


class VehiculoListResponse(BaseModel):
    """Respuesta para lista de vehículos del usuario"""
    total: int = Field(description="Total de vehículos")
    vehiculos: List[VehiculoDetailedResponse] = Field(description="Lista de vehículos")
