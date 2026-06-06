from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from models.database import get_db
from models.user import Usuario
from config import get_settings

# Usar la misma configuración que security/jwt_handler.py
settings = get_settings()
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

# Esto le dice a FastAPI que busque el token en el Header "Authorization"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la sesión",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if user is None:
        raise credentials_exception
        
    # 🛡️ VALIDACIÓN BLINDADA CONTRA NULOS / ENUMS
    estado = getattr(user, "estado_cuenta", "ACTIVO")
    if hasattr(estado, "value"):  # Por si es un Enum de SQLAlchemy
        estado = estado.value
        
    if estado == "INACTIVO":
        raise HTTPException(status_code=400, detail="Usuario inactivo")
        
    return user


def check_permissions(required_role: str):
    """
    Fábrica de dependencias para validar roles de manera blindada.
    Uso: Depends(check_permissions("Administrador"))
    """
    def role_checker(current_user: Usuario = Depends(get_current_user)):
        # Extraemos el nombre del rol de forma 100% segura
        rol_obj = getattr(current_user, "rol", None)
        rol_nombre = getattr(rol_obj, "nombre", "Cliente") if rol_obj else "Cliente"

        if rol_nombre != required_role and rol_nombre != "Administrador":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permisos suficientes. Se requiere rol: {required_role}"
            )
        return current_user
    return role_checker


def require_admin(current_user: Usuario = Depends(get_current_user)):
    """
    Dependencia para asegurar que SOLO admin puede acceder a un endpoint.
    """
    rol_obj = getattr(current_user, "rol", None)
    rol_nombre = getattr(rol_obj, "nombre", "Cliente") if rol_obj else "Cliente"

    if rol_nombre != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden realizar esta acción"
        )
    return current_user


def get_current_gestor_id(current_user: Usuario = Depends(get_current_user)) -> int:
    """
    Inyecta el ID del gestor validando el rol. Si es Administrador global,
    retorna su propio id_usuario para evitar fallos de aislamiento relacional.
    """
    rol_obj = getattr(current_user, "rol", None)
    rol_nombre = getattr(rol_obj, "nombre", "Cliente") if rol_obj else "Cliente"
    
    # Soportamos todas las variaciones de nombres comunes en los seeds
    if rol_nombre != "GestorTaller" and rol_nombre != "Gestor de Taller" and rol_nombre != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere el rol de Gestor de Taller."
        )
        
    return current_user.id_usuario