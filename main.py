"""
main.py - Punto de entrada de la aplicación FastAPI
Inicializa la aplicación, crea las tablas en BD y registra los routers
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from models.database import engine, Base
from routers import auth, dashboard, vehiculos, incidentes

# Importar todos los modelos para que SQLAlchemy los reconozca en metadata
# IMPORTANTE: Estos imports son necesarios para que Base.metadata.create_all() funcione
from models.user import Usuario, Rol
from models.marca_modelo import Marca, Modelo
from models.vehiculo import Vehiculo
from models.incidente import Incidente, Evidencia

# Obtener configuración
settings = get_settings()

# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Backend para la Plataforma Inteligente de Atención de Emergencias Vehiculares",
)

# Configurar CORS (Control de acceso desde otros orígenes)
# Permite que el frontend en Angular (localhost:4200) acceda a la API
# En DESARROLLO: permitir todos los orígenes (*)
# En PRODUCCIÓN: especificar solo los dominios permitidos
app.add_middleware(
    CORSMiddleware,
    # Orígenes permitidos:
    # - localhost:4200 para desarrollo Angular
    # - localhost:3000 para otros frameworks (React, Vue, etc.)
    # - En producción, agregar dominios reales
    allow_origins=[
        "http://localhost:4200",      # Angular (desarrollo)
        "http://localhost:3000",      # Otros frameworks (desarrollo)
        "http://127.0.0.1:4200",      # Angular (IP local)
        "http://127.0.0.1:3000",      # Otros frameworks (IP local)
        "*"  # TEMPORAL: En producción cambiar a dominios específicos
    ],
    # Permitir credenciales (cookies, Authorization headers)
    allow_credentials=True,
    # Métodos HTTP permitidos
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    # Headers permitidos (incluyendo Authorization para JWT)
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    # Tiempo de caché para las respuestas preflight (en segundos)
    max_age=3600,
)


# Evento de inicio: crear tablas si no existen
@app.on_event("startup")
def startup_event():
    """
    Se ejecuta al iniciar la aplicación.
    Crea todas las tablas definidas en los modelos ORM si no existen.
    """
    print("🚀 Iniciando aplicación...")
    
    # Crear las tablas en la base de datos
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas de base de datos creadas/verificadas")
    
    # Crear roles por defecto si no existen (opcional pero recomendado)
    _create_default_roles()
    
    print("✅ Aplicación lista!")


def _create_default_roles():
    """
    Helper que crea los roles por defecto en la base de datos.
    Se ejecuta solo si los roles no existen.
    
    Roles creados:
    1. admin - Administrador del sistema (acceso completo)
    2. operador - Operador de emergencias (gestión de incidentes)
    3. tecnico - Técnico de taller (atención de usuarios)
    4. cliente - Usuario final (reporte de incidentes)
    5. gestor_taller - Gestor de taller (admin de recursos)
    """
    from models.database import SessionLocal
    from models.user import Rol
    
    db = SessionLocal()
    try:
        # Definir roles por defecto (orden importante, se usan los IDs en seed-test-users)
        roles_default = [
            {"nombre": "admin", "descripcion": "Administrador del sistema - Acceso completo"},
            {"nombre": "operador", "descripcion": "Operador de emergencias - Gestión de incidentes"},
            {"nombre": "tecnico", "descripcion": "Técnico de taller - Atención de usuarios"},
            {"nombre": "cliente", "descripcion": "Cliente/Usuario final - Reporte de incidentes"},
            {"nombre": "gestor_taller", "descripcion": "Gestor de taller - Administración de recursos"},
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
# REGISTRAR ROUTERS
# ============================================================================
# Los routers se registran en orden. El prefijo define la ruta base.
# Ejemplo: router auth con prefix="/auth" → POST /auth/register, POST /auth/login, etc.

# Router de Autenticación - Maneja registro, login, obtener usuario actual
app.include_router(auth.router)

# Router de Dashboard - Proporciona métricas según el rol del usuario
app.include_router(dashboard.router)

# Router de Vehículos - Gestión de marcas, modelos y vehículos del usuario
app.include_router(vehiculos.router)

# Router de Incidentes - Reporte de emergencias y evidencia multimedia
app.include_router(incidentes.router)


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