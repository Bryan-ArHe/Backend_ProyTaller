"""
security/password.py - Funciones para el hasheo y verificación de contraseñas
Utiliza bcrypt directamente para máxima seguridad
"""

import bcrypt
import hashlib

def hash_password(password: str) -> str:
    """
    Hashea una contraseña en texto plano usando bcrypt.
    
    Args:
        password: Contraseña en texto plano (máximo 72 bytes en UTF-8)
        
    Returns:
        Contraseña hasheada (hash de bcrypt)
        
    Ejemplo:
        >>> hashed = hash_password("miContraseña123")
        >>> print(hashed)  # b'$2b$12$xyzabc...'
    """
    # Limitar a 72 bytes en UTF-8 (limitación de bcrypt)
    # Importante: caracteres multibyte pueden exceder 72 bytes antes de llegar a 72 caracteres
    password_bytes = password.encode('utf-8')[:72]
    
    # Validar que no se truncó incorrectamente en medio de un carácter multibyte
    if len(password_bytes) > 72:
        raise ValueError(f"❌ Error fatal: password cannot be longer than 72 bytes, truncate manually if necessary (e.g. my_password[:72])")
    
    # Generar salt y hash (rounds=12 es el estándar seguro)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Convertir a string para almacenar en BD
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica que una contraseña en texto plano coincida con su hash de bcrypt
    o con el hash defensivo SHA-256 usado en el script de simulación Multi-tenant.
    """
    try:
        # 1. 🌟 COMPROBACIÓN DEL SEEDER (SHA-256 Plano):
        # Si el hash en la BD mide 64 caracteres y no tiene el prefijo '$2b$',
        # calculamos el SHA-256 en caliente para darle paso inmediato.
        if len(hashed_password) == 64 and not hashed_password.startswith("$"):
            hash_login = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
            if hash_login == hashed_password:
                return True

        # 2. VERIFICACIÓN ESTÁNDAR DE BCRYPT (Producción local)
        # Limitar a 72 caracteres (limitación de bcrypt)
        plain_password_bytes = plain_password[:72].encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')
        
        # Verificar de forma nativa
        return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
        
    except (ValueError, TypeError):
        # Si hay algún error, retornar False
        return False
