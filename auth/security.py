"""
auth/security.py - JWT y manejo de tokens
Refactorizado sin passlib (bcrypt está en security/password.py)
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

# --- CONFIGURACIÓN CRÍTICA ---
SECRET_KEY = "TU_LLAVE_SUPER_SECRETA_SANTACRUZ_2026"  # ⚠️ Cambia por algo aleatorio en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # El token durará 24 horas

def crear_token_acceso(data: dict):
    """
    Genera un JWT (carnet digital) con los datos del usuario.
    
    Args:
        data: Diccionario con datos del usuario (sub, id_usuario, rol, etc.)
        
    Returns:
        String con el token JWT codificado
        
    Ejemplo:
        >>> token = crear_token_acceso({
        ...     "sub": "usuario@email.com",
        ...     "id_usuario": 1,
        ...     "rol": "admin"
        ... })
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt