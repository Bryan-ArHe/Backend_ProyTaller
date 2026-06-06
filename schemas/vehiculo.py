from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VehiculoBase(BaseModel):
    placa: str
    marca: str
    modelo: str
    color: Optional[str] = None
    anio: Optional[int] = None  # Sincronizado con tu columna 'anio'

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoSimpleResponse(VehiculoBase):
    id_vehiculo: int
    id_usuario: int
    fecha_registro: datetime
