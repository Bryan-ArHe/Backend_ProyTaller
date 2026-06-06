from models.database import get_db

# Re-exponer get_db para los módulos que lo consuman desde la raíz
__all__ = ["get_db"]