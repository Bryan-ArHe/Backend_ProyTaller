"""
models/database.py - Configuración de la conexión a la base de datos
Proporciona el engine de SQLAlchemy, SessionLocal y Base para los modelos
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from config import get_settings
import os

# Obtener la URL de la base de datos desde la configuración
settings = get_settings()
DATABASE_URL = settings.database_url

# Detectar si estamos en producción (Vercel)
IS_PRODUCTION = os.getenv("VERCEL") == "1" or not settings.debug_mode

# Configurar parámetros adicionales para conexión
connect_args = {
    "connect_timeout": 10,  # Timeout de 10 segundos para la conexión
}

if "supabase.co" in DATABASE_URL:
    connect_args["sslmode"] = "require"

# En producción, usar NullPool para evitar problemas de conexión
# En desarrollo, usar pool regular
pool_config = {
    "pool_pre_ping": True,  # Verificar conexiones antes de usarlas
    "pool_recycle": 3600,  # Reciclar conexiones cada hora
    "connect_args": connect_args
}

if IS_PRODUCTION:
    # Para Vercel: usar NullPool para no mantener conexiones abiertas
    pool_config["poolclass"] = NullPool
    print("📦 Configuración PRODUCCIÓN: NullPool habilitado")
else:
    # Para desarrollo: pool normal
    pool_config["pool_size"] = 5
    pool_config["max_overflow"] = 10
    print("🔧 Configuración DESARROLLO: Pool normal")

# Crear el motor (engine) de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=settings.debug_mode,  # Mostrar sentencias SQL en consola si DEBUG=True
    **pool_config
)

# SessionLocal: Factory para crear sesiones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: Clase base para todos los modelos ORM
Base = declarative_base()


def get_db():
    """
    Dependencia de FastAPI que proporciona una sesión de base de datos.
    Se usa en los endpoints para acceder a la BD.
    
    Ejemplo de uso:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(Usuario).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
