"""
schemas/incidente.py - Esquemas Pydantic para CRUD de Incidentes
Validación y serialización para Incidentes y Evidencia Multimedia
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================================================
# ESQUEMAS PARA EVIDENCIA
# ============================================================================

class EvidenciaCreate(BaseModel):
    """Esquema para capturar una evidencia en el reporte de incidente"""
    tipo: str = Field(..., description="Tipo: FOTO, VIDEO, AUDIO, DOCUMENTO")
    url: str = Field(..., min_length=5, max_length=500, description="URL del archivo")
    tamano_bytes: Optional[int] = Field(None, ge=1, description="Tamaño en bytes")
    descripcion: Optional[str] = Field(None, max_length=300, description="Descripción opcional")


class EvidenciaResponse(BaseModel):
    """Esquema de respuesta para Evidencia"""
    id: int
    id_incidente: int
    tipo: str
    url: str
    tamano_bytes: Optional[int]
    descripcion: Optional[str]
    fecha_captura: datetime
    fecha_registro: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# ESQUEMAS PARA INCIDENTE
# ============================================================================

class IncidenteCreate(BaseModel):
    """
    Esquema para reporte inicial de incidente
    Incluye datos del incidente y lista de evidencias
    """
    id_vehiculo: int = Field(..., description="ID del vehículo involucrado")
    descripcion: str = Field(
        ..., 
        min_length=10, 
        max_length=1000, 
        description="Descripción detallada del incidente"
    )
    ubicacion_lat: Optional[float] = Field(None, ge=-90, le=90, description="Latitud del incidente")
    ubicacion_long: Optional[float] = Field(None, ge=-180, le=180, description="Longitud del incidente")
    
    # Lista de evidencias capturadas
    evidencias: List[EvidenciaCreate] = Field(
        default=[],
        description="Lista de evidencias (fotos, videos, etc.)"
    )


class IncidenteResponse(BaseModel):
    """Esquema de respuesta para Incidente"""
    id: int
    id_vehiculo: int
    id_cliente: int
    descripcion: str
    estado: str
    prioridad: str
    ubicacion_lat: Optional[float]
    ubicacion_long: Optional[float]
    fecha_reporte: datetime
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True


class IncidenteDetailedResponse(IncidenteResponse):
    """
    Incidente con información completa incluyendo:
    - Datos del vehículo involucrado
    - Información del cliente
    - Lista completa de evidencias
    """
    evidencias: List[EvidenciaResponse] = []


class IncidenteListResponse(BaseModel):
    """Respuesta para lista de incidentes del usuario"""
    total: int = Field(description="Total de incidentes")
    incidentes: List[IncidenteDetailedResponse] = Field(description="Lista de incidentes")


class TriajeAIResponse(BaseModel):
    """
    Respuesta del sistema de Triaje IA
    (Placeholder para lógica futura de priorización automática)
    """
    id_incidente: int
    prioridad_asignada: str = Field(description="BAJA, MEDIA, ALTA, CRITICA")
    razon_prioridad: str = Field(description="Explicación breve de la prioridad asignada")
    tiempo_respuesta_estimado_minutos: int = Field(description="Tiempo estimado para atención")
    
    class Config:
        from_attributes = True
