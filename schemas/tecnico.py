from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

# 1. ESQUEMA BASE: Propiedades comunes
class TecnicoBase(BaseModel):
    especialidad: Optional[str] = Field(None, description="Ej: Mecánica General, Electricidad, Chaperío")
    estado_disponibilidad: str = Field(default="Libre", description="Valores permitidos: Libre, Ocupado, Inactivo")
    
    # Coordenadas que se actualizarán constantemente desde la app del técnico
    latitud_actual: Optional[float] = None
    longitud_actual: Optional[float] = None

# 2. ESQUEMA DE CREACIÓN (Lo que Angular manda en el POST)
class TecnicoCreate(TecnicoBase):
    # Llaves foráneas obligatorias para vincular al técnico con su cuenta y su taller
    id_usuario: int  # (Cambiar a str si en Supabase el id de usuario es UUID)
    id_taller: int

# 3. ESQUEMA DE ACTUALIZACIÓN (Lo que Angular manda en el PUT/PATCH)
class TecnicoUpdate(BaseModel):
    # Todo es opcional. Por seguridad, no permitimos que se actualice el id_usuario o id_taller por esta vía
    especialidad: Optional[str] = None
    estado_disponibilidad: Optional[str] = None
    latitud_actual: Optional[float] = None
    longitud_actual: Optional[float] = None

# 4. ESQUEMA DE RESPUESTA (Lo que Angular recibe)
class TecnicoResponse(TecnicoBase):
    id_tecnico: int
    id_usuario: int
    id_taller: int
    created_at: datetime

    # Permite a Pydantic leer los datos directamente del objeto SQLAlchemy
    model_config = ConfigDict(from_attributes=True)