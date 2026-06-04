# src/schemas/zonacobertura.py

from pydantic import BaseModel

class ZonaCoberturaBase(BaseModel):
    nombre: str
    descripcion: str
    estado: bool

class ZonaCoberturaCreate(ZonaCoberturaBase):
    poligono_area: str

class ZonaCoberturaResponse(ZonaCoberturaBase):
    id: int
    class Config:
        from_attributes = True  # Usa orm_mode = True si tienes una versión antigua de Pydantic