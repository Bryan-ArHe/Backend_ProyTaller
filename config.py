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
            "postgresql://postgres.fcjnirrnaeemalxkqfwz:Db_PryTaller@aws-1-us-west-2.pooler.supabase.com:6543/postgres"
        )
        
        # JWT
        self.secret_key = os.getenv(
            "SECRET_KEY",
            "tu_clave_secreta_super_segura_cambiar_en_produccion"
        )
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")  # 24 horas (1440 minutos)
        )
        
        # API
        self.api_title = os.getenv(
            "API_TITLE",
            "Plataforma Inteligente de Atención de Emergencias Vehiculares"
        )
        self.api_version = os.getenv("API_VERSION", "1.0.0")
        
        # Debug: Modo de depuración (para crear tablas automáticamente)
        self.debug_mode = os.getenv("DEBUG_MODE", "True").lower() == "true"
        self.debug = self.debug_mode  # Alias para compatibilidad
        
        # CORS: Orígenes permitidos (separados por comas)
        cors_origins_str = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:4200,http://localhost:3000,http://localhost:8000,backend-proy-taller.vercel.app/"
        )
        self.cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la instancia única de Settings (patrón Singleton)
    Reutiliza la instancia entre llamadas para eficiencia
    """
    return Settings()
