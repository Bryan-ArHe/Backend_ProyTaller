"""
schemas/user.py - Esquemas Pydantic para validación de datos de entrada/salida
Valida automáticamente los datos recibidos en las peticiones HTTP
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class RolResponse(BaseModel):
    """Esquema para la respuesta de datos de Rol"""
    id: int
    nombre: str
    descripcion: Optional[str] = None
    
    class Config:
        from_attributes = True  # Permite leer datos desde objetos ORM


class UsuarioCreate(BaseModel):
    """
    Esquema para la creación de un nuevo usuario.
    Se recibe en el endpoint POST /auth/register
    """
    email: EmailStr = Field(..., description="Correo electrónico único")
    telefono: str = Field(..., min_length=7, max_length=20, description="Número de teléfono")
    password: str = Field(..., min_length=8, description="Contraseña (mínimo 8 caracteres)")
    id_rol: int = Field(..., description="ID del rol a asignar al usuario")


class UsuarioResponse(BaseModel):
    """
    Esquema para la respuesta con datos del usuario.
    NO incluye password_hash por razones de seguridad.
    """
    id: int
    email: str
    telefono: str
    estado_cuenta: str
    id_rol: int
    fecha_registro: datetime
    rol: RolResponse
    
    class Config:
        from_attributes = True


class LoginData(BaseModel):
    """
    Esquema para las credenciales en el login.
    Se recibe en el endpoint POST /auth/login
    """
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., description="Contraseña del usuario")


class Token(BaseModel):
    """
    Esquema para la respuesta del token JWT.
    Se devuelve después del login exitoso.
    """
    access_token: str = Field(..., description="Token JWT para autenticación")
    token_type: str = Field(default="bearer", description="Tipo de token")
