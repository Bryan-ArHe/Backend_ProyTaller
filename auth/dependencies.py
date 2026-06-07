from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session, joinedload  # 🌟 Importamos joinedload
from models.database import get_db
from models.user import Usuario
from config import get_settings

settings = get_settings()
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

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
        
    # 🌟 ESTRATEGIA ANTE-ERRORES: Cargamos la relación del Rol en caliente con joinedload
    user = db.query(Usuario).options(
        joinedload(Usuario.rol)
    ).filter(Usuario.email == email).first()
    
    if user is None:
        raise credentials_exception
        
    estado = getattr(user, "estado_cuenta", "ACTIVO")
    if hasattr(estado, "value"):  
        estado = estado.value
        
    if estado == "INACTIVO":
        raise HTTPException(status_code=400, detail="Usuario inactivo")
        
    return user


def check_permissions(required_role: str):
    """
    Fábrica de dependencias para validar roles de manera blindada.
    Soporta la jerarquía: superAdmin > Administrador > Roles Operativos
    """
    def role_checker(current_user: Usuario = Depends(get_current_user)):
        rol_obj = getattr(current_user, "rol", None)
        rol_nombre = getattr(rol_obj, "nombre", "Cliente") if rol_obj else "Cliente"

        # 👑 El superAdmin y el Administrador heredan por defecto accesos de visualización
        if rol_nombre not in [required_role, "Administrador", "superAdmin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permisos suficientes. Se requiere rol: {required_role}"
            )
        return current_user
    return role_checker


def require_admin(current_user: Usuario = Depends(get_current_user)):
    """
    Asegura que solo roles de jerarquía administrativa (Administrador / superAdmin) entren al endpoint.
    """
    rol_obj = getattr(current_user, "rol", None)
    rol_nombre = getattr(rol_obj, "nombre", "Cliente") if rol_obj else "Cliente"

    # 🌟 Añadimos superAdmin al pase autorizado
    if rol_nombre not in ["Administrador", "superAdmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo personal de administración o la plataforma Saas pueden realizar esta acción"
        )
    return current_user


def get_current_gestor_id(current_user: Usuario = Depends(get_current_user)) -> int:
    """
    Inyecta el ID del gestor validando el rol. Si es Administrador global o superAdmin,
    retorna su propio id_usuario para evitar fallos de aislamiento relacional.
    """
    rol_obj = getattr(current_user, "rol", None)
    rol_nombre = getattr(rol_obj, "nombre", "Cliente") if rol_obj else "Cliente"
    
    # Añadimos soporte para evitar que el superAdmin y Admin se queden bloqueados en vistas operativas
    if rol_nombre not in ["Gestor", "Administrador", "superAdmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere el rol de Gestor de Taller o jerarquía superior."
        )
        
    return current_user.id_usuario