from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# --- CONFIGURACIÓN CRÍTICA ---
SECRET_KEY = "TU_LLAVE_SUPER_SECRETA_SANTACRUZ_2026" # Cambia esto por algo aleatorio
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # El token durará 24 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def crear_token_acceso(data: dict):
    """Genera el carnet digital (JWT)"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt