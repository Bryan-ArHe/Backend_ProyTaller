# crud/auth.py
from sqlalchemy.orm import Session
from models.user import Usuario
from schemas.user import UsuarioCreate
from passlib.context import CryptContext

# Configuramos el hasher para las contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_usuario_by_email(db: Session, email: str):
    """Busca un usuario por email"""
    return db.query(Usuario).filter(Usuario.email == email).first()

def crear_usuario(db: Session, usuario_in: UsuarioCreate):
    """Crea un nuevo usuario con contraseña hasheada"""
    hashed_password = pwd_context.hash(usuario_in.password)
    
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

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que la contraseña plana coincida con el hash"""
    return pwd_context.verify(plain_password, hashed_password)