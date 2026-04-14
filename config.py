"""
config.py - Configuración centralizada de la aplicación
Carga las variables de entorno y proporciona configuraciones globales
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación basada en variables de entorno"""
    
    # Base de datos
    database_url: str = "postgresql://postgres:123456@localhost:5432/gestiontaller"
    
    # JWT
    secret_key: str = "tu_clave_secreta_super_segura_cambiar_en_produccion"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API
    api_title: str = "Plataforma Inteligente de Atención de Emergencias Vehiculares"
    api_version: str = "1.0.0"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la instancia única de Settings (patrón Singleton)
    Reutiliza la instancia entre llamadas para eficiencia
    """
    return Settings()
