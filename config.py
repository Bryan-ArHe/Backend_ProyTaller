"""
config.py - Configuración centralizada de la aplicación
Carga las variables de entorno y proporciona configuraciones globales
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from functools import lru_cache

# Cargar variables de entorno desde .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


class Settings:
    """Configuración de la aplicación basada en variables de entorno"""
    
    def __init__(self):
        # Base de datos
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:123456@localhost:5432/gestiontaller"
        )
        
        # JWT
        self.secret_key = os.getenv(
            "SECRET_KEY",
            "tu_clave_secreta_super_segura_cambiar_en_produccion"
        )
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )
        
        # API
        self.api_title = os.getenv(
            "API_TITLE",
            "Plataforma Inteligente de Atención de Emergencias Vehiculares"
        )
        self.api_version = os.getenv("API_VERSION", "1.0.0")
        self.debug = os.getenv("DEBUG", "True").lower() == "true"
        
        # Generación de datos de prueba
        self.debug_mode = os.getenv("DEBUG_MODE", "True").lower() == "true"


@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la instancia única de Settings (patrón Singleton)
    Reutiliza la instancia entre llamadas para eficiencia
    """
    return Settings()
