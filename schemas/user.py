"""
schemas/user.py - Esquemas con Dataclasses para validaciÃ³n de datos de entrada/salida
Valida automÃ¡ticamente los datos recibidos en las peticiones HTTP
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator
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
    nombre: str
    apellido: str
    email: str
    telefono: str
    password: str
    id_rol: int
    
    def __post_init__(self):
        validate_string_length(self.nombre, min_length=2, max_length=100, field_name="nombre")
        validate_string_length(self.apellido, min_length=2, max_length=100, field_name="apellido")
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
    nombre: str
    apellido: str
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


class UsuarioUpdate(BaseModel):
    """
    Esquema para que el usuario actualice su propio perfil.
    Permite actualizar nombre, apellido, teléfono y contraseña (todos opcionales).
    Se recibe en PUT /usuarios/me
    """
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    password: Optional[str] = None
    
    @field_validator('nombre')
    @classmethod
    def validate_nombre(cls, v):
        if v:
            validate_string_length(v, min_length=2, max_length=100, field_name="nombre")
        return v
    
    @field_validator('apellido')
    @classmethod
    def validate_apellido(cls, v):
        if v:
            validate_string_length(v, min_length=2, max_length=100, field_name="apellido")
        return v
    
    @field_validator('telefono')
    @classmethod
    def validate_telefono(cls, v):
        if v:
            validate_string_length(v, min_length=7, max_length=20, field_name="telefono")
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v:
            validate_string_length(v, min_length=8, field_name="password")
        return v


class UsuarioEstadoUpdate(BaseModel):
    """
    Esquema para que el ADMINISTRADOR cambie el estado de la cuenta de un usuario.
    Solo permite cambiar entre ACTIVO e INACTIVO.
    Se recibe en PATCH /usuarios/{usuario_id}/estado
    """
    estado_cuenta: str
    
    @field_validator('estado_cuenta')
    @classmethod
    def validate_estado(cls, v):
        if v not in ["ACTIVO", "INACTIVO"]:
            raise ValueError("estado_cuenta debe ser 'ACTIVO' o 'INACTIVO'")
        return v


class UsuarioRolUpdate(BaseModel):
    """
    Esquema para que el ADMINISTRADOR cambie el rol de un usuario.
    Se recibe en PATCH /usuarios/{usuario_id}/rol
    """
    id_rol: int
    
    @field_validator('id_rol')
    @classmethod
    def validate_id_rol(cls, v):
        if v < 1:
            raise ValueError("id_rol debe ser un número positivo")
        return v


@dataclass
class UsuarioAdminResponse:
    """
    Esquema detallado para listar usuarios en el panel de administración.
    Incluye información completa del usuario y su rol.
    Se devuelve en GET /usuarios/
    """
    id_usuario: int
    nombre: str
    apellido: str
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


@dataclass
class ClienteCreate:
    """
    Esquema para la creación de un nuevo cliente.
    Datos adicionales al usuario básico que se almacenan en la tabla cliente.
    """
    ci: str
    fecha_nacimiento: Optional[str] = None
    
    def __post_init__(self):
        validate_string_length(self.ci, min_length=5, max_length=20, field_name="ci")


@dataclass
class ClienteResponse:
    """
    Esquema para la respuesta con datos del cliente.
    Combina información de usuario y datos específicos del cliente.
    """
    id_cliente: int
    ci: str
    fecha_nacimiento: Optional[datetime] = None
    usuario: Optional[UsuarioResponse] = None


@dataclass
class ClienteUpdate:
    """
    Esquema para actualizar datos del cliente.
    Permite actualizar cédula y fecha de nacimiento.
    """
    ci: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    
    def __post_init__(self):
        if self.ci:
            validate_string_length(self.ci, min_length=5, max_length=20, field_name="ci")
