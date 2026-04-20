"""
schemas/user.py - Esquemas con Dataclasses para validaciÃ³n de datos de entrada/salida
Valida automÃ¡ticamente los datos recibidos en las peticiones HTTP
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
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
    Esquema para la creaciÃ³n de un nuevo usuario.
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
    Se devuelve despuÃ©s del login exitoso.
    """
    access_token: str
    token_type: str = "bearer"


@dataclass
class UsuarioUpdate:
    """
    Esquema para que el usuario actualice su propio perfil.
    Permite actualizar telÃ©fono y contraseÃ±a (ambos opcionales).
    Se recibe en PUT /usuarios/me
    """
    telefono: Optional[str] = None
    password: Optional[str] = None
    
    def __post_init__(self):
        if self.telefono:
            validate_string_length(self.telefono, min_length=7, max_length=20, field_name="telefono")
        if self.password:
            validate_string_length(self.password, min_length=8, field_name="password")


@dataclass
class UsuarioEstadoUpdate:
    """
    Esquema para que el ADMINISTRADOR cambiÃ© el estado de la cuenta de un usuario.
    Solo permite cambiar entre ACTIVO e INACTIVO.
    Se recibe en PATCH /usuarios/{usuario_id}/estado
    """
    estado_cuenta: str
    
    def __post_init__(self):
        if self.estado_cuenta not in ["ACTIVO", "INACTIVO"]:
            raise ValueError("estado_cuenta debe ser 'ACTIVO' o 'INACTIVO'")


@dataclass
class UsuarioRolUpdate:
    """
    Esquema para que el ADMINISTRADOR cambie el rol de un usuario.
    Se recibe en PATCH /usuarios/{usuario_id}/rol
    """
    id_rol: int
    
    def __post_init__(self):
        if self.id_rol < 1:
            raise ValueError("id_rol debe ser un nÃºmero positivo")


@dataclass
class UsuarioAdminResponse:
    """
    Esquema detallado para listar usuarios en el panel de administraciÃ³n.
    Incluye informaciÃ³n completa del usuario y su rol.
    Se devuelve en GET /usuarios/
    """
    id_usuario: int
    email: str
    telefono: str
    estado_cuenta: str
    id_rol: int
    fecha_registro: datetime
    rol: RolResponse


@dataclass
class PermisoResponse:
    """
    Esquema para la respuesta de datos de Permiso.
    Usado en listados y en relaciones many-to-many.
    """
    id_permiso: int
    nombre: str
    descripcion: Optional[str] = None
    recurso: Optional[str] = None
    accion: Optional[str] = None


@dataclass
class RolConPermisosResponse:
    """
    Esquema detallado para Rol con sus permisos anidados.
    Se devuelve en GET /roles/ y en la matriz de administraciÃ³n.
    """
    id_rol: int
    nombre: str
    descripcion: Optional[str] = None
    permisos: List[PermisoResponse] = None


@dataclass
class ActualizarPermisosRequest:
    """
    Esquema de peticiÃ³n para actualizar los permisos de un rol.
    Se recibe en PUT /roles/{id_rol}/permisos
    """
    permisos_ids: List[int]
    
    def __post_init__(self):
        if not isinstance(self.permisos_ids, list):
            raise ValueError("permisos_ids debe ser una lista de enteros")
        if not all(isinstance(pid, int) and pid > 0 for pid in self.permisos_ids):
            raise ValueError("Todos los permisos_ids deben ser enteros positivos")
