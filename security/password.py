"""
security/password.py - Funciones para el hasheo y verificación de contraseñas
Utiliza bcrypt directamente para máxima seguridad
"""

import bcrypt

def hash_password(password: str) -> str:
    """
    Hashea una contraseña en texto plano usando bcrypt.
    
    Args:
        password: Contraseña en texto plano (máximo 72 caracteres)
        
    Returns:
        Contraseña hasheada (hash de bcrypt)
        
    Ejemplo:
        >>> hashed = hash_password("miContraseña123")
        >>> print(hashed)  # b'$2b$12$xyzabc...'
    """
    # Limitar a 72 caracteres (limitación de bcrypt)
    password_bytes = password[:72].encode('utf-8')
    
    # Generar salt y hash (rounds=12 es el estándar seguro)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Convertir a string para almacenar en BD
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica que una contraseña en texto plano coincida con su hash de bcrypt.
    
    Args:
        plain_password: Contraseña en texto plano (del usuario)
        hashed_password: Contraseña hasheada (de la BD) como string
        
    Returns:
        True si la contraseña es correcta, False en caso contrario
        
    Ejemplo:
        >>> es_valida = verify_password("miContraseña123", hashed_from_db)
        >>> print(es_valida)  # True o False
    """
    try:
        # Limitar a 72 caracteres (limitación de bcrypt)
        plain_password_bytes = plain_password[:72].encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')
        
        # Verificar
        return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
    except (ValueError, TypeError):
        # Si hay algún error, retornar False
        return False
