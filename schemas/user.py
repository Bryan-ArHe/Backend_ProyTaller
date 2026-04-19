"""
schemas/user.py - Esquemas con Dataclasses para validación de datos de entrada/salida
Valida automáticamente los datos recibidos en las peticiones HTTP
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .validators import validate_string_length, validate_email


@dataclass
class RolResponse:
    """Esquema para la respuesta de datos de Rol"""
    id_rol: int
    nombre: str
    descripcion: Optional[str] = None


@dataclass
class UsuarioCreate:
    """
    Esquema para la creación de un nuevo usuario.
    Se recibe en el endpoint POST /auth/register
    """
    email: str
    telefono: str
    password: str
    id_rol: int
    
    def __post_init__(self):
        validate_email(self.email)
        validate_string_length(self.telefono, min_length=7, max_length=20, field_name="telefono")
        validate_string_length(self.password, min_length=8, field_name="password")


@dataclass
class UsuarioResponse:
    """
    Esquema para la respuesta con datos del usuario.
    NO incluye password_hash por razones de seguridad.
    """
    id_usuario: int
    email: str
    telefono: str
    estado_cuenta: str
    id_rol: int
    fecha_registro: datetime
    rol: RolResponse


@dataclass
class LoginData:
    """
    Esquema para las credenciales en el login.
    Se recibe en el endpoint POST /auth/login
    """
    email: str
    password: str
    
    def __post_init__(self):
        validate_email(self.email)


@dataclass
class Token:
    """
    Esquema para la respuesta del token JWT.
    Se devuelve después del login exitoso.
    """
    access_token: str
    token_type: str = "bearer"
