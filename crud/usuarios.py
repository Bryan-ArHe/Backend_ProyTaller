"""
crud/usuarios.py - Funciones CRUD para usuarios
Maneja la lógica de base de datos para la gestión de usuarios
"""

from sqlalchemy.orm import Session, joinedload
from models.user import Usuario, Rol
from security.password import hash_password
from typing import Optional, List


def get_usuario_by_id(db: Session, usuario_id: int) -> Optional[Usuario]:
    """
    Obtiene un usuario por su ID.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
    
    Returns:
        Usuario o None si no existe
    """
    return db.query(Usuario).options(
        joinedload(Usuario.rol)
    ).filter(Usuario.id_usuario == usuario_id).first()


def get_usuario_by_email(db: Session, email: str) -> Optional[Usuario]:
    """
    Obtiene un usuario por su email.
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario
    
    Returns:
        Usuario o None si no existe
    """
    return db.query(Usuario).options(
        joinedload(Usuario.rol)
    ).filter(Usuario.email == email).first()


def get_all_usuarios(db: Session) -> List[Usuario]:
    """
    Obtiene todos los usuarios del sistema.
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        Lista de todos los usuarios con sus roles
    """
    return db.query(Usuario).options(
        joinedload(Usuario.rol)
    ).all()


def update_usuario(db: Session, usuario_id: int, datos) -> Optional[Usuario]:
    """
    Actualiza un usuario existente.
    
    Características especiales:
    - Si password es None o string vacío, NO se actualiza
    - Solo actualiza los campos que tienen valores
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario a actualizar
        datos: Objeto dataclass con los nuevos datos (UsuarioUpdate)
    
    Returns:
        Usuario actualizado o None si no existe
    """
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    
    if not usuario:
        return None
    
    # Actualizar nombre si se proporciona
    if hasattr(datos, 'nombre') and datos.nombre:
        usuario.nombre = datos.nombre
    
    # Actualizar apellido si se proporciona
    if hasattr(datos, 'apellido') and datos.apellido:
        usuario.apellido = datos.apellido
    
    # Actualizar teléfono si se proporciona
    if hasattr(datos, 'telefono') and datos.telefono:
        usuario.telefono = datos.telefono
    
    # Actualizar contraseña SOLO si se proporciona un valor válido
    # Ignorar si es None o string vacío
    if hasattr(datos, 'password') and datos.password and isinstance(datos.password, str) and datos.password.strip():
        usuario.password_hash = hash_password(datos.password)
    
    db.commit()
    db.refresh(usuario)
    
    return usuario


def cambiar_estado_usuario(db: Session, usuario_id: int, nuevo_estado: str) -> Optional[Usuario]:
    """
    Cambia el estado de un usuario (ACTIVO/INACTIVO).
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
        nuevo_estado: Nuevo estado (ACTIVO o INACTIVO)
    
    Returns:
        Usuario actualizado o None si no existe
    """
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    
    if not usuario:
        return None
    
    usuario.estado_cuenta = nuevo_estado
    db.commit()
    db.refresh(usuario)
    
    return usuario


def cambiar_rol_usuario(db: Session, usuario_id: int, nuevo_rol_id: int) -> Optional[Usuario]:
    """
    Cambia el rol de un usuario.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
        nuevo_rol_id: ID del nuevo rol
    
    Returns:
        Usuario actualizado o None si no existe
    """
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    
    if not usuario:
        return None
    
    # Verificar que el rol existe
    rol = db.query(Rol).filter(Rol.id_rol == nuevo_rol_id).first()
    if not rol:
        return None
    
    usuario.id_rol = nuevo_rol_id
    db.commit()
    db.refresh(usuario)
    
    return usuario
