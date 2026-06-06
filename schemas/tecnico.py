from pydantic import BaseModel, EmailStr
from typing import Optional
from .user import UsuarioCreate
class TecnicoBase(BaseModel):
    especialidad: str
    disponibilidad: str  # 'Libre', 'Ocupado', 'Inactivo'

class TecnicoCreate(TecnicoBase):
    id_taller: int
    id_gestor: int
    usuario: UsuarioCreate  # Data requerida para poblar la tabla raíz 'usuario'

class TecnicoSimpleResponse(TecnicoBase):
    id_tecnico: int
    id_taller: int
    id_gestor: int
    id_usuario: int
    # Aplanamos la relación de herencia 1:1 para el Frontend en Angular
    email: EmailStr
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    especialidad: str
    disponibilidad: str

    class Config:
        from_attributes = True