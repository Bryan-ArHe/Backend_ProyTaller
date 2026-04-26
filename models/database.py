"""
models/database.py - Configuración de la conexión a la base de datos
Proporciona el engine de SQLAlchemy, SessionLocal y Base para los modelos
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_settings

# Obtener la URL de la base de datos desde la configuración
settings = get_settings()
DATABASE_URL = settings.database_url

# Configurar parámetros adicionales para Supabase
# Supabase requiere SSL mode=require
connect_args = {
    "connect_timeout": 10,  # Timeout de 10 segundos para la conexión
}

if "supabase.co" in DATABASE_URL:
    connect_args["sslmode"] = "require"

# Crear el motor (engine) de SQLAlchemy
# Para producción, considera usar asyncio con asyncpg para mejor rendimiento
engine = create_engine(
    DATABASE_URL,
    echo=settings.debug,  # Mostrar sentencias SQL en consola si DEBUG=True
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_size=5,  # Limitar tamaño del pool para evitar saturación
    max_overflow=10,  # Máximo de conexiones adicionales
    pool_recycle=3600,  # Reciclar conexiones cada hora
    connect_args=connect_args
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
