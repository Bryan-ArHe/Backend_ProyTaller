from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List

# --- SCHEMAS DE PERMISOS ---

class PermisoResponse(BaseModel):
    """Esquema para la respuesta de datos de Permiso"""
    id_permiso: int
    nombre: str
    descripcion: Optional[str] = None
    recurso: str
    accion: str
    
    model_config = ConfigDict(from_attributes=True)

# --- SCHEMAS DE ROLES ---

class RolResponse(BaseModel):
    """Esquema básico para la respuesta de Rol """
    id_rol: int
    nombre: str
    descripcion: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class RolConPermisosResponse(RolResponse):
    """Esquema detallado de Rol con sus permisos anidados [cite: 13]"""
    permisos: List[PermisoResponse] = []

# --- SCHEMAS DE USUARIO ---

class UsuarioCreate(BaseModel):
    """Esquema para la creación de un nuevo usuario (POST /auth/register) [cite: 2]"""
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefono: str = Field(..., min_length=7, max_length=20)
    password: str = Field(..., min_length=8, max_length=72, description="Contraseña (max 72 caracteres - limitación de bcrypt)")
    id_rol: int

class UsuarioResponse(BaseModel):
    """Esquema estándar de respuesta de usuario [cite: 3]"""
    id_usuario: int
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str
    estado_cuenta: str
    id_rol: int
    fecha_registro: datetime
    rol: RolResponse # Relación 1-a-1
    
    model_config = ConfigDict(from_attributes=True)

class UsuarioUpdate(BaseModel):
    """Esquema para actualización de perfil propio [cite: 6]"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido: Optional[str] = Field(None, min_length=2, max_length=100)
    telefono: Optional[str] = Field(None, min_length=7, max_length=20)
    password: Optional[str] = Field(None, min_length=8, max_length=72)

class UsuarioRolUpdate(BaseModel):
    """Esquema específico para la actualización administrativa del rol de un usuario"""
    id_rol: int

    model_config = ConfigDict(from_attributes=True)

# --- SCHEMAS DE SEGURIDAD ---

class LoginData(BaseModel):
    """Esquema para credenciales de login [cite: 4]"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)

class Token(BaseModel):
    """Esquema para la respuesta del token JWT [cite: 5]"""
    access_token: str
    token_type: str = "bearer"

class ActualizarPermisosRequest(BaseModel):
    """Petición para asignar permisos a un rol [cite: 15]"""
    permisos_ids: List[int]