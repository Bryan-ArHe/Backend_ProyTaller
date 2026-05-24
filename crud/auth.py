# crud/auth.py
"""
CRUD de autenticación - Refactorizado sin passlib
Utiliza security/password.py para hasheo y verificación con bcrypt
"""

from sqlalchemy.orm import Session
from models.user import Usuario
from schemas.user import UsuarioCreate
from security.password import hash_password

def get_usuario_by_email(db: Session, email: str):
    """
    Busca un usuario por email en la base de datos.
    
    Args:
        db: Sesión de SQLAlchemy
        email: Email del usuario a buscar
        
    Returns:
        Usuario si existe, None en caso contrario
    """
    return db.query(Usuario).filter(Usuario.email == email).first()

def crear_usuario(db: Session, usuario_in: UsuarioCreate):
    """
    Crea un nuevo usuario con contraseña hasheada usando bcrypt.
    
    Args:
        db: Sesión de SQLAlchemy
        usuario_in: Datos del usuario a crear (UsuarioCreate schema)
        
    Returns:
        Usuario creado en la base de datos
        
    Raises:
        ValueError: Si la contraseña excede 72 bytes (limitación de bcrypt)
    """
    # Hashear contraseña con bcrypt
    hashed_password = hash_password(usuario_in.password)
    
    # Crear nuevo usuario
    db_usuario = Usuario(
        nombre=usuario_in.nombre,
        apellido=usuario_in.apellido,
        email=usuario_in.email,
        telefono=usuario_in.telefono,
        password_hash=hashed_password,
        id_rol=usuario_in.id_rol
    )
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario