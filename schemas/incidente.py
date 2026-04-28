"""
schemas/incidente.py - Esquemas Pydantic V2 para CRUD de Incidentes
Validación y serialización para Incidentes y Evidencia Multimedia
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ============================================================================
# ESQUEMAS PARA EVIDENCIA
# ============================================================================

class EvidenciaCreate(BaseModel):
    """Esquema para capturar una evidencia en el reporte de incidente"""
    tipo: str = Field(..., min_length=1, max_length=50)
    url: str = Field(..., min_length=5, max_length=500)
    tamano_bytes: Optional[int] = Field(None, gt=0)
    descripcion: Optional[str] = Field(None, max_length=300)


class EvidenciaResponse(BaseModel):
    """Esquema de respuesta para Evidencia"""
    id_evidencia: int
    id_incidente: int
    tipo: str
    url: str
    tamano_bytes: Optional[int]
    descripcion: Optional[str]
    fecha_captura: datetime
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ESQUEMAS PARA INCIDENTE
# ============================================================================

class IncidenteCreate(BaseModel):
    """
    Esquema para reporte inicial de incidente
    Incluye datos del incidente y lista de evidencias
    """
    id_vehiculo: int = Field(..., gt=0)
    descripcion: str = Field(..., min_length=10, max_length=1000)
    ubicacion_lat: Optional[float] = Field(None, ge=-90, le=90)
    ubicacion_long: Optional[float] = Field(None, ge=-180, le=180)
    evidencias: List[EvidenciaCreate] = Field(default_factory=list)


class IncidenteResponse(BaseModel):
    """Esquema de respuesta para Incidente"""
    id_incidente: int
    id_vehiculo: int
    id_usuario: int
    descripcion: str
    estado: str
    prioridad: str
    ubicacion_lat: Optional[float]
    ubicacion_long: Optional[float]
    fecha_reporte: datetime
    fecha_actualizacion: datetime

    model_config = ConfigDict(from_attributes=True)


class IncidenteDetailedResponse(IncidenteResponse):
    """
    Incidente con información completa incluyendo:
    - Datos del vehículo involucrado
    - Información del cliente
    - Lista completa de evidencias
    """
    evidencias: List[EvidenciaResponse] = Field(default_factory=list)


class IncidenteListResponse(BaseModel):
    """Respuesta para lista de incidentes del usuario"""
    total: int = Field(..., ge=0)
    incidentes: List[IncidenteDetailedResponse] = Field(default_factory=list)


class TriajeAIResponse(BaseModel):
    """Esquema para la respuesta del análisis de IA"""
    nivel_prioridad: str
    diagnostico_presuntivo: str
    recomendaciones: List[str]
    taller_sugerido_id: Optional[int] = None

    # Esto es vital para que FastAPI pueda leer objetos de la DB
    model_config = ConfigDict(from_attributes=True)
