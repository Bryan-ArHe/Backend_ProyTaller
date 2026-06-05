from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class TallerBase(BaseModel):
    nombre: str
    direccion: str
    telefono: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    especialidad: Optional[str] = None
    capacidad_vehiculos: int = 1
    estado_activo: bool = True

class TallerCreate(TallerBase):
    id_propietario: int

class TallerUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    especialidad: Optional[str] = None
    capacidad_vehiculos: Optional[int] = None
    estado_activo: Optional[bool] = None

# === ESQUEMA DE SALIDA CORREGIDO ===
class TallerResponse(TallerBase):
    id_taller: int  
    id_propietario: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)