from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class IncidenteBase(BaseModel):
    descripcion: str
    ubicacion_inicial_wkt: str # Recibimos/enviamos texto plano WKT para interactuar con PostGIS

class IncidenteCreate(IncidenteBase):
    id_cliente: int

class IncidenteSimpleResponse(IncidenteBase):
    id_incidente: int
    id_cliente: int
    estado_incidente: str
    fecha_incidente: datetime