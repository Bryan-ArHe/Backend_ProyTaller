from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class TallerBase(BaseModel):
    nombre: str
    direccion: str
    ubicacion_wkt: Optional[str] = Field(None, description="Punto geográfico en formato WKT: POINT(longitud latitud)")

class TallerCreate(TallerBase):
    pass

class TallerSimpleResponse(TallerBase):
    id_taller: int
    id_gestor: int
    fecha_creacion: datetime
