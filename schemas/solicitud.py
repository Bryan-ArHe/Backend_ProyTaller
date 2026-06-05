from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class EstadoSolicitud(str, Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    RESUELTO = "RESUELTO"
    CANCELADO = "CANCELADO"

# --- ESQUEMAS BASE ---
class SolicitudServicioBase(BaseModel):
    incidente_id: int = Field(..., description="ID del incidente origen")
    tecnico_id: int = Field(..., description="ID del técnico asignado")
    taller_id: Optional[int] = Field(None, description="ID del taller de soporte (opcional)")
    descripcion_trabajo: Optional[str] = Field(None, description="Detalles del trabajo a realizar")

# --- ESQUEMAS DE ENTRADA (Request) ---
class SolicitudServicioCreate(SolicitudServicioBase):
    """Esquema para crear una orden de trabajo de forma manual o automatizada"""
    pass

class SolicitudServicioUpdate(BaseModel):
    """Esquema para actualizar el estado o detalles por el Técnico o Gestor"""
    estado: Optional[EstadoSolicitud] = None
    descripcion_trabajo: Optional[str] = None
    observaciones_tecnicas: Optional[str] = None
    fecha_finalizacion: Optional[datetime] = None

# --- ESQUEMAS DE SALIDA (Response) ---
class SolicitudServicioResponse(SolicitudServicioBase):
    """Esquema estándar de retorno para los endpoints"""
    id: int
    codigo_orden: str = Field(..., description="Código único generado (ej. OT-2026-0001)")
    estado: EstadoSolicitud
    fecha_asignacion: datetime
    fecha_finalizacion: Optional[datetime] = None
    observaciones_tecnicas: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- ESQUEMAS ANIDADOS (Para Angular) ---
# Si en el frontend necesitas ver la orden con los datos básicos del Técnico e Incidente
class UsuarioMinOut(BaseModel):
    id: int
    nombre: str
    apellido: str
    celular: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class IncidenteMinOut(BaseModel):
    id: int
    codigo_incidente: str
    gravedad: str
    direccion: str
    model_config = ConfigDict(from_attributes=True)

class SolicitudServicioDetalladaResponse(SolicitudServicioResponse):
    """Retorna la orden de trabajo con relaciones incluidas para el dashboard"""
    tecnico: UsuarioMinOut
    incidente: IncidenteMinOut
    
    model_config = ConfigDict(from_attributes=True)