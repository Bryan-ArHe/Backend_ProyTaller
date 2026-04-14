"""
dependencies.py - Dependencias compartidas de FastAPI
Incluye funciones que se usan en múltiples endpoints como get_current_user
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models.database import get_db
from models.user import Usuario
from security.jwt_handler import decode_access_token
from schemas.user import UsuarioResponse

# Esquema OAuth2 que extrae el token del header "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UsuarioResponse:
    """
    Dependencia que valida el token JWT y retorna el usuario actual.
    
    Se usa en los endpoints que requieren autenticación:
        @app.get("/auth/me", response_model=UsuarioResponse)
        def get_me(current_user: UsuarioResponse = Depends(get_current_user)):
            return current_user
    
    Args:
        token: Token JWT extraído del header Authorization
        db: Sesión de base de datos
        
    Returns:
        Usuario autenticado con sus datos
        
    Raises:
        HTTPException 401: Si el token es inválido, expirado o el usuario no existe
    """
    # Credenciales inválidas - respuesta HTTP 401
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decodificar el token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # Extraer el email del payload (guardado como "sub")
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    # Buscar el usuario en la base de datos
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario is None:
        raise credentials_exception
    
    # Verificar que la cuenta esté activa
    if usuario.estado_cuenta.value == "INACTIVO":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta del usuario está inactiva"
        )
    
    return UsuarioResponse.from_orm(usuario)
