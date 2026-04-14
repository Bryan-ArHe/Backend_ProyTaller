"""
routers/dashboard.py - Router para el Dashboard
Proporciona métricas y estadísticas personalizadas según el rol del usuario autenticado
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.database import get_db
from models.user import Usuario, Rol
from schemas.dashboard import (
    DashboardAdminResponse,
    DashboardOperadorResponse,
    DashboardUsuarioResponse,
    DashboardTecnicoResponse,
    DashboardGenericoResponse,
)
from dependencies import get_current_user
from schemas.user import UsuarioResponse

# Crear el router del dashboard
router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    responses={
        401: {"description": "No autorizado - token inválido"},
        403: {"description": "Forbidden - acceso denegado"},
    }
)


@router.get("/metrics")
def obtener_metricas_dashboard(
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Endpoint que devuelve métricas personalizadas del dashboard según el rol del usuario.
    
    El usuario debe estar autenticado (token JWT válido).
    
    Returns:
        - DashboardAdminResponse: Si el usuario tiene rol 'admin'
        - DashboardOperadorResponse: Si el usuario tiene rol 'operador'
        - DashboardUsuarioResponse: Si el usuario tiene rol 'usuario'
        - DashboardTecnicoResponse: Si el usuario tiene rol 'tecnico'
        - DashboardGenericoResponse: Para otros roles
        
    Raises:
        HTTPException 401: Si el token es inválido
        HTTPException 403: Si el usuario es inactivo
    """
    
    # El usuario ya fue validado por get_current_user
    rol_nombre = current_user.rol.nombre.lower()
    
    # ==========================================
    # MÉTRICAS PARA ADMIN
    # ==========================================
    if rol_nombre == "admin":
        return _obtener_metricas_admin(db)
    
    # ==========================================
    # MÉTRICAS PARA OPERADOR
    # ==========================================
    elif rol_nombre == "operador":
        return _obtener_metricas_operador(db, current_user)
    
    # ==========================================
    # MÉTRICAS PARA USUARIO (Cliente)
    # ==========================================
    elif rol_nombre == "usuario":
        return _obtener_metricas_usuario(db, current_user)
    
    # ==========================================
    # MÉTRICAS PARA TÉCNICO
    # ==========================================
    elif rol_nombre == "tecnico":
        return _obtener_metricas_tecnico(db, current_user)
    
    # ==========================================
    # RESPUESTA GENÉRICA PARA ROLES DESCONOCIDOS
    # ==========================================
    else:
        return DashboardGenericoResponse(
            mensaje=f"Dashboard disponible para el rol: {rol_nombre}",
            rol=rol_nombre,
            datos={
                "usuario_id": current_user.id,
                "email": current_user.email,
                "fecha_ingreso": current_user.fecha_registro
            }
        )


def _obtener_metricas_admin(db: Session) -> DashboardAdminResponse:
    """
    Obtiene métricas para el administrador del sistema.
    
    Métricas:
    - Total de usuarios registrados
    - Usuarios activos e inactivos
    - Total de roles disponibles
    """
    
    # Contar total de usuarios
    total_usuarios = db.query(func.count(Usuario.id)).scalar() or 0
    
    # Contar usuarios activos
    from models.user import EstadoCuenta
    usuarios_activos = (
        db.query(func.count(Usuario.id))
        .filter(Usuario.estado_cuenta == EstadoCuenta.ACTIVO)
        .scalar() or 0
    )
    
    # Contar usuarios inactivos
    usuarios_inactivos = (
        db.query(func.count(Usuario.id))
        .filter(Usuario.estado_cuenta == EstadoCuenta.INACTIVO)
        .scalar() or 0
    )
    
    # Contar total de roles
    total_roles = db.query(func.count(Rol.id)).scalar() or 0
    
    return DashboardAdminResponse(
        total_usuarios=total_usuarios,
        usuarios_activos=usuarios_activos,
        usuarios_inactivos=usuarios_inactivos,
        total_roles=total_roles,
        metricas_adicionales={
            "timestamp": "2026-04-14T12:00:00",
            "sistema_operativo": True,
            "base_datos": "PostgreSQL"
        }
    )


def _obtener_metricas_operador(
    db: Session, 
    current_user: UsuarioResponse
) -> DashboardOperadorResponse:
    """
    Obtiene métricas para el operador de emergencias.
    
    Métricas (simuladas por ahora):
    - Órdenes pendientes
    - Órdenes en proceso
    - Órdenes completadas hoy
    - Técnicos disponibles
    """
    
    # NOTA: Estos datos son simulados (mock) porque aún no tenemos
    # los modelos de Orden, Incidente, etc.
    # Cuando agregues esas tablas, reemplaza con consultas reales.
    
    return DashboardOperadorResponse(
        ordenes_pendientes=5,
        ordenes_en_proceso=3,
        ordenes_completadas_hoy=8,
        tecnicos_disponibles=2,
        metricas_adicionales={
            "operador_id": current_user.id,
            "ultima_actualizacion": "2026-04-14T12:15:30",
            "próximas_tareas": [
                {"id": 1, "descripcion": "Revisar orden #102", "prioridad": "alta"},
                {"id": 2, "descripcion": "Asignar técnico a orden #103", "prioridad": "media"}
            ]
        }
    )


def _obtener_metricas_usuario(
    db: Session,
    current_user: UsuarioResponse
) -> DashboardUsuarioResponse:
    """
    Obtiene métricas para el usuario cliente.
    
    Métricas (simuladas por ahora):
    - Vehículos registrados
    - Incidentes activos
    - Solicitudes pendientes
    - Último incidente
    """
    
    # NOTA: Datos simulados - reemplazar cuando tengamos el modelo de Vehículos/Incidentes
    
    return DashboardUsuarioResponse(
        vehiculos_registrados=2,
        incidentes_activos=1,
        solicitudes_pendientes=0,
        ultimo_incidente="2026-04-10T14:30:00",
        metricas_adicionales={
            "usuario_id": current_user.id,
            "email": current_user.email,
            "estado_membresia": "activa",
            "próximo_vencimiento": "2026-05-14",
            "vehículos": [
                {
                    "placa": "ABC-123",
                    "marca": "Toyota",
                    "modelo": "Corolla",
                    "estado": "activo"
                },
                {
                    "placa": "XYZ-789",
                    "marca": "Honda",
                    "modelo": "Civic",
                    "estado": "activo"
                }
            ]
        }
    )


def _obtener_metricas_tecnico(
    db: Session,
    current_user: UsuarioResponse
) -> DashboardTecnicoResponse:
    """
    Obtiene métricas para el técnico.
    
    Métricas (simuladas por ahora):
    - Orden asignada
    - Descripción de orden
    - Tareas completadas hoy
    - Calificación promedio
    """
    
    # NOTA: Datos simulados - reemplazar cuando tengamos el modelo de Órdenes
    
    return DashboardTecnicoResponse(
        orden_asignada=True,
        descripcion_orden="Reparación de batería - Toyota Corolla - Placa ABC-123",
        tareas_completadas_hoy=3,
        calificacion_promedio=4.8,
        metricas_adicionales={
            "tecnico_id": current_user.id,
            "especialidad": "Electricidad Automotriz",
            "años_experiencia": 5,
            "orden_actual": {
                "id": 1,
                "cliente": "Juan Pérez",
                "telefono": "3001234567",
                "ubicacion": "Calle 10 #20-30",
                "tiempo_estimado": "1 hora"
            },
            "historial_hoy": [
                {
                    "id": 1,
                    "tipo": "Cambio de aceite",
                    "cliente": "María López",
                    "duracion": "30 min",
                    "calificacion": "5"
                },
                {
                    "id": 2,
                    "tipo": "Revisión general",
                    "cliente": "Carlos Toro",
                    "duracion": "45 min",
                    "calificacion": "4.5"
                }
            ]
        }
    )


# ==========================================
# ENDPOINTS ADICIONALES OPCIONALES
# ==========================================

@router.get("/health")
def health_check():
    """
    Endpoint de verificación de salud del dashboard.
    Útil para testing y monitoreo.
    """
    return {
        "status": "ok",
        "servicio": "Dashboard",
        "version": "1.0.0"
    }


@router.get("/resumen")
def obtener_resumen_rapido(
    current_user: UsuarioResponse = Depends(get_current_user),
):
    """
    Endpoint alternativo que devuelve un resumen muy rápido sin cálculos complejos.
    Útil para actualizaciones frecuentes en el frontend.
    """
    return {
        "usuario_id": current_user.id,
        "rol": current_user.rol.nombre,
        "email": current_user.email,
        "timestamp": "2026-04-14T12:00:00Z"
    }
