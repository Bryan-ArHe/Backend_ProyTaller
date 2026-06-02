"""
crud/roles.py - Funciones CRUD para roles y permisos
Maneja la lógica de base de datos para la gestión de roles y permisos
"""

from sqlalchemy.orm import Session, joinedload
from models.user import Rol, Permiso
from typing import Optional, List


def get_rol_by_id(db: Session, rol_id: int) -> Optional[Rol]:
    """
    Obtiene un rol por su ID con sus permisos anidados.
    
    Args:
        db: Sesión de base de datos
        rol_id: ID del rol
    
    Returns:
        Rol con permisos o None si no existe
    """
    return db.query(Rol).options(
        joinedload(Rol.permisos)
    ).filter(Rol.id_rol == rol_id).first()


def get_rol_by_name(db: Session, nombre: str) -> Optional[Rol]:
    """
    Obtiene un rol por su nombre con sus permisos anidados.
    
    Args:
        db: Sesión de base de datos
        nombre: Nombre del rol
    
    Returns:
        Rol con permisos o None si no existe
    """
    return db.query(Rol).options(
        joinedload(Rol.permisos)
    ).filter(Rol.nombre == nombre).first()


def get_all_roles(db: Session) -> List[Rol]:
    """
    Obtiene todos los roles del sistema con sus permisos.
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        Lista de todos los roles con sus permisos anidados
    """
    return db.query(Rol).options(
        joinedload(Rol.permisos)
    ).all()


def get_permiso_by_id(db: Session, permiso_id: int) -> Optional[Permiso]:
    """
    Obtiene un permiso por su ID.
    
    Args:
        db: Sesión de base de datos
        permiso_id: ID del permiso
    
    Returns:
        Permiso o None si no existe
    """
    return db.query(Permiso).filter(Permiso.id_permiso == permiso_id).first()


def get_all_permisos(db: Session) -> List[Permiso]:
    """
    Obtiene todos los permisos del sistema.
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        Lista de todos los permisos
    """
    return db.query(Permiso).all()


def get_permisos_by_ids(db: Session, permisos_ids: List[int]) -> List[Permiso]:
    """
    Obtiene múltiples permisos por sus IDs.
    
    Args:
        db: Sesión de base de datos
        permisos_ids: Lista de IDs de permisos
    
    Returns:
        Lista de permisos encontrados
    """
    return db.query(Permiso).filter(Permiso.id_permiso.in_(permisos_ids)).all()


def actualizar_permisos_rol(db: Session, id_rol: int, permisos_ids: List[int]) -> Optional[Rol]:
    """
    Actualiza los permisos asignados a un rol.
    
    Características:
    - Limpia todos los permisos actuales del rol
    - Busca los nuevos permisos por sus IDs
    - Asigna los nuevos permisos al rol
    - Valida que todos los permisos existan
    
    Args:
        db: Sesión de base de datos
        id_rol: ID del rol a actualizar
        permisos_ids: Lista de IDs de los nuevos permisos
    
    Returns:
        Rol actualizado con sus nuevos permisos o None si no existe el rol
    
    Raises:
        ValueError: Si alguno de los permisos no existe
    """
    # Buscar el rol
    rol = db.query(Rol).filter(Rol.id_rol == id_rol).first()
    
    if not rol:
        return None
    
    # Obtener los permisos nuevos
    permisos_nuevos = get_permisos_by_ids(db, permisos_ids)
    
    # Validar que encontramos todos los permisos solicitados
    if len(permisos_nuevos) != len(permisos_ids):
        permisos_encontrados = {p.id_permiso for p in permisos_nuevos}
        permisos_solicitados = set(permisos_ids)
        permisos_faltantes = permisos_solicitados - permisos_encontrados
        raise ValueError(
            f"Los siguientes IDs de permisos no existen: {permisos_faltantes}"
        )
    
    # Limpiar permisos actuales
    rol.permisos.clear()
    
    # Agregar nuevos permisos
    for permiso in permisos_nuevos:
        rol.permisos.append(permiso)
    
    # Guardar cambios
    db.commit()
    db.refresh(rol)
    
    return rol
