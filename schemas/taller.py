from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# 🌟 1. NUEVO SUB-ESQUEMA: Mapea los atributos que Angular necesita pintar del encargado
class GestorResumenResponse(BaseModel):
    nombre: str
    apellido: str

    class Config:
        from_attributes = True

class TallerBase(BaseModel):
    nombre: str
    direccion: str
    telefono: Optional[str] = None # 🌟 Añadido si manejas teléfonos en el formulario
    ubicacion_wkt: Optional[str] = Field(None, description="Punto geográfico en formato WKT: POINT(longitud latitud)")

class TallerCreate(TallerBase):
    pass

class TallerSimpleResponse(TallerBase):
    id_taller: int
    # 🌟 CAMBIO: Hacemos id_gestor Opcional porque si el taller es vacante (None), 
    # de lo contrario Pydantic lanzaría un ValidationError
    id_gestor: Optional[int] = None 
    fecha_registro: datetime
    
    # 🌟 LA CLAVE: Declaramos la relación para que Pydantic le dé paso en el JSON
    gestor: Optional[GestorResumenResponse] = None 

    class Config:
        from_attributes = True