"""
security/jwt_handler.py - Funciones para la creación y validación de tokens JWT
Utiliza python-jose para manejar JWT de forma segura
"""

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from config import get_settings
from typing import Optional

settings = get_settings()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT con los datos proporcionados.
    
    Args:
        data: Diccionario con los datos a codificar en el token
              Por lo general contiene el "sub" (subject) con el email del usuario
        expires_delta: Timedelta opcional para personalizar el tiempo de expiración.
                      Si no se proporciona, usa ACCESS_TOKEN_EXPIRE_MINUTES de config.
                      
    Returns:
        Token JWT codificado como string
        
    Ejemplo:
        >>> token = create_access_token({"sub": "usuario@email.com"})
        >>> print(token)  # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    to_encode = data.copy()
    
    # Calcular tiempo de expiración
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    # Agregar el tiempo de expiración al payload
    to_encode.update({"exp": expire})
    
    # Codificar y firmar el token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida un token JWT.
    
    Args:
        token: Token JWT a decodificar
        
    Returns:
        Diccionario con los datos del token si es válido, None si es inválido o expirado
        
    Ejemplo:
        >>> payload = decode_access_token(token)
        >>> if payload:
        ...     email = payload.get("sub")
        ... else:
        ...     print("Token inválido o expirado")
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        # Token inválido, expirado o firma incorrecta
        return None
