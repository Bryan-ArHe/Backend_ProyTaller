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
    if user.estado_cuenta == "INACTIVO":
        raise HTTPException(status_code=400, detail="Usuario inactivo")
        
    return user

def check_permissions(required_role: str):
    """
    Fábrica de dependencias para validar roles.
    Uso: Depends(check_permissions("Administrador"))
    """
    def role_checker(current_user: Usuario = Depends(get_current_user)):
        if current_user.rol.nombre != required_role and current_user.rol.nombre != "Administrador":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permisos suficientes. Se requiere rol: {required_role}"
            )
        return current_user
    return role_checker

def require_admin(current_user: Usuario = Depends(get_current_user)):
    """
    Dependencia para asegurar que SOLO admin puede acceder a un endpoint.
    Uso en endpoints de modificación (POST, PUT, DELETE):
        current_user: Usuario = Depends(require_admin)
    """
    if current_user.rol.nombre != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden realizar esta acción"
        )
    return current_user