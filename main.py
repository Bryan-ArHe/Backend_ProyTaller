"""
main.py - Punto de entrada de la aplicación FastAPI
Inicializa la aplicación, crea las tablas en BD y registra los routers
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from routers import auth, dashboard, vehiculos, incidentes, usuarios, roles, bitacora, talleres, tecnicos, zona_cobertura
from models.database import Base, engine
import models  # Importar modelos para registrar con SQLAlchemy


# Obtener configuración
settings = get_settings()

# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Backend para la Plataforma Inteligente de Atención de Emergencias Vehiculares",
)

# Configurar CORS ANTES de cualquier otro middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["Content-Length", "Content-Range"],
    max_age=3600,
)


# Evento de inicio: crear tablas solo en modo DEBUG
@app.on_event("startup")
def startup_event():
    """
    Se ejecuta al iniciar la aplicación.
    En modo DEBUG: Crea todas las tablas definidas en los modelos ORM si no existen.
    En producción: Solo registra que la app está iniciada (NO intenta conectar a BD).
    """
    print("🚀 Iniciando aplicación...")
    print(f"📦 Modo DEBUG: {settings.debug_mode}")
    
    # IMPORTANTE: NO crear tablas en producción
    # Las tablas deben crearse una vez localmente con reset_db.py
    # Vercel puede no tener acceso a la BD en startup
    
    if settings.debug_mode:
        print("🔧 Modo DEBUG activado - Intentando crear tablas...")
        try:
            Base.metadata.create_all(bind=engine)
            print("✅ Tablas de base de datos creadas/verificadas")
            _create_default_roles()
            print("✅ Roles por defecto creados/verificados")
        except Exception as e:
            print(f"⚠️ Error al crear tablas: {e}")
            print("   Continuando sin tablas (asegúrate de haber ejecutado reset_db.py)")
    else:
        print("✅ Modo PRODUCCIÓN - BD debe estar pre-inicializada con reset_db.py")
    
    print("✅ Aplicación lista!")


def _create_default_roles():
    """
    Helper que crea los roles por defecto en la base de datos.
    Se ejecuta solo si los roles no existen.
    
    Roles creados:
    1. admin - Administrador del sistema (acceso completo)
    2. tecnico - Técnico de taller (atención de usuarios)
    3. cliente - Usuario final (reporte de incidentes)
    4. gestor_taller - Gestor de taller (admin de recursos)
    """
    from models.database import SessionLocal
    from models.user import Rol
    
    db = SessionLocal()
    try:
        # Definir roles por defecto
        roles_default = [
            {"nombre": "Administrador", "descripcion": "Administrador del sistema - Acceso completo"},
            {"nombre": "Tecnico", "descripcion": "Técnico de taller - Atención de usuarios"},
            {"nombre": "Cliente", "descripcion": "Cliente/Usuario final - Reporte de incidentes"},
            {"nombre": "GestorTaller", "descripcion": "Gestor de taller - Administración de recursos"},
        ]
        
        # Crear roles si no existen
        for rol_data in roles_default:
            rol_existente = db.query(Rol).filter(
                Rol.nombre == rol_data["nombre"]
            ).first()
            
            if not rol_existente:
                nuevo_rol = Rol(**rol_data)
                db.add(nuevo_rol)
                print(f"   ✓ Rol '{rol_data['nombre']}' creado")
        
        db.commit()
    finally:
        db.close()


# Evento de cierre
@app.on_event("shutdown")
def shutdown_event():
    """Se ejecuta al cerrar la aplicación"""
    print("🛑 Cerrando aplicación...")


# ============================================================================
# HEALTH CHECK ENDPOINT (sin dependencias de BD)
# ============================================================================
@app.get("/health", tags=["Health"])
def health_check():
    """
    Endpoint de verificación de salud de la aplicación.
    No requiere autenticación ni conexión a BD.
    Vercel lo usa para verificar que la app está activa.
    """
    return {
        "status": "healthy",
        "service": "Plataforma Inteligente de Atención de Emergencias Vehiculares",
        "version": settings.api_version
    }


@app.get("/", tags=["Info"])
def root():
    """Endpoint raíz - Información básica de la API"""
    return {
        "message": "Bienvenido a la API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


# ============================================================================
# REGISTRAR ROUTERS
# ============================================================================
# Los routers se registran en orden. El prefijo define la ruta base.
# Ejemplo: router auth con prefix="/auth" → POST /auth/register, POST /auth/login, etc.

# Router de Autenticación - Maneja registro, login, obtener usuario actual
app.include_router(auth.router)

# Router de Usuarios - Gestión de perfiles y administración de usuarios
app.include_router(usuarios.router)

# Router de Roles y Permisos - Matriz de administración de roles y permisos
app.include_router(roles.router)

# Router de Dashboard - Proporciona métricas según el rol del usuario
app.include_router(dashboard.router)

# Router de Vehículos - Gestión de marcas, modelos y vehículos del usuario
app.include_router(vehiculos.router)

# Router de Incidentes - Reporte de emergencias y evidencia multimedia
app.include_router(incidentes.router)

# Router de Bitácora - Registro de eventos y auditoría
app.include_router(bitacora.router)

# Router de Talleres - Gestión de talleres
app.include_router(talleres.router)

# Router de Técnicos - Gestión de técnicos
app.include_router(tecnicos.router)

# Router de Zonas de Cobertura - Gestión de áreas de cobertura (PostGIS)
app.include_router(zona_cobertura.router)


# Endpoint raíz para verificar que la API está activa
@app.get("/", tags=["Health Check"])
def root():
    """
    Endpoint de prueba para verificar que la API está activa
    """
    return {
        "mensaje": "Bienvenido a la Plataforma Inteligente de Atención de Emergencias Vehiculares",
        "version": settings.api_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health Check"])
def health_check():
    """
    Endpoint de health check para monitoreo
    """
    return {"status": "ok"}


# Ejecutar la aplicación
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )