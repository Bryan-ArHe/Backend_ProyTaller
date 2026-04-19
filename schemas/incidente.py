"""
schemas/incidente.py - Esquemas con Dataclasses para CRUD de Incidentes
Validación y serialización para Incidentes y Evidencia Multimedia
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from .validators import validate_string_length, validate_latitude, validate_longitude


# ============================================================================
# ESQUEMAS PARA EVIDENCIA
# ============================================================================

@dataclass
class EvidenciaCreate:
    """Esquema para capturar una evidencia en el reporte de incidente"""
    tipo: str
    url: str
    tamano_bytes: Optional[int] = None
    descripcion: Optional[str] = None
    
    def __post_init__(self):
        validate_string_length(self.url, min_length=5, max_length=500, field_name="url")
        if self.descripcion:
            validate_string_length(self.descripcion, max_length=300, field_name="descripcion")
        if self.tamano_bytes is not None and self.tamano_bytes < 1:
            raise ValueError("tamano_bytes debe ser mayor a 0")


@dataclass
class EvidenciaResponse:
    """Esquema de respuesta para Evidencia"""
    id_evidencia: int
    id_incidente: int
    tipo: str
    url: str
    tamano_bytes: Optional[int]
    descripcion: Optional[str]
    fecha_captura: datetime
    fecha_registro: datetime


# ============================================================================
# ESQUEMAS PARA INCIDENTE
# ============================================================================

@dataclass
class IncidenteCreate:
    """
    Esquema para reporte inicial de incidente
    Incluye datos del incidente y lista de evidencias
    """
    id_vehiculo: int
    descripcion: str
    ubicacion_lat: Optional[float] = None
    ubicacion_long: Optional[float] = None
    evidencias: List[EvidenciaCreate] = field(default_factory=list)
    
    def __post_init__(self):
        validate_string_length(self.descripcion, min_length=10, max_length=1000, field_name="descripcion")
        if self.ubicacion_lat:
            validate_latitude(self.ubicacion_lat)
        if self.ubicacion_long:
            validate_longitude(self.ubicacion_long)


@dataclass
class IncidenteResponse:
    """Esquema de respuesta para Incidente"""
    id_incidente: int
    id_vehiculo: int
    id_cliente: int
    descripcion: str
    estado: str
    prioridad: str
    ubicacion_lat: Optional[float]
    ubicacion_long: Optional[float]
    fecha_reporte: datetime
    fecha_actualizacion: datetime


@dataclass
class IncidenteDetailedResponse(IncidenteResponse):
    """
    Incidente con información completa incluyendo:
    - Datos del vehículo involucrado
    - Información del cliente
    - Lista completa de evidencias
    """
    evidencias: List[EvidenciaResponse] = field(default_factory=list)


@dataclass
class IncidenteListResponse:
    """Respuesta para lista de incidentes del usuario"""
    total: int
    incidentes: List[IncidenteDetailedResponse] = field(default_factory=list)


@dataclass
class TriajeAIResponse:
    """
    Respuesta del sistema de Triaje IA
    (Placeholder para lógica futura de priorización automática)
    """
    id_incidente: int
    prioridad_asignada: str
    razon_prioridad: str
    tiempo_respuesta_estimado_minutos: int
