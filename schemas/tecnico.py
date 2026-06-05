from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# 1. Esquema Base con los campos EXACTOS de tu modelo Tecnico
class TecnicoBase(BaseModel):
    id_usuario: int
    id_taller: Optional[int] = None
    especialidad: Optional[str] = None
    estado_disponibilidad: str = "Libre"
    latitud_actual: Optional[float] = None
    longitud_actual: Optional[float] = None

class TecnicoCreate(TecnicoBase):
    pass

class TecnicoUpdate(BaseModel):
    id_taller: Optional[int] = None
    especialidad: Optional[str] = None
    estado_disponibilidad: Optional[str] = None
    latitud_actual: Optional[float] = None
    longitud_actual: Optional[float] = None

# --- 2. ESQUEMA DE SALIDA PLANO (ROMPE EL BUCLE 10054) ---
class TecnicoResponse(TecnicoBase):
    id_tecnico: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- 3. ESQUEMAS ANIDADOS SEGUROS PARA EL FRONTEND ---
class UsuarioMinOut(BaseModel):
    """Para mostrar quién es el técnico en Angular sin traernos toda la BD"""
    id_usuario: int
    nombres: Optional[str] = None
    username: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class TecnicoDetalladoResponse(TecnicoResponse):
    """Este esquema incluye al usuario pero NO incluye al Taller completo"""
    usuario: Optional[UsuarioMinOut] = None
    
    model_config = ConfigDict(from_attributes=True)