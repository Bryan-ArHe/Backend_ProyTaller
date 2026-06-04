from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from models.database import get_db
from auth.dependencies import get_current_user, require_admin
from schemas.user import UsuarioResponse
from utils.bitacora_helper import registrar_evento_bitacora
from schemas.incidente import (
    IncidenteCreate, IncidenteResponse, IncidenteDetailedResponse,
    IncidenteListResponse, EvidenciaCreate, EvidenciaResponse,
    TriajeAIResponse
)
from crud.incidente import (
    crear_incidente, obtener_incidente_por_id, obtener_incidentes_por_cliente,
    obtener_incidentes_por_vehiculo, obtener_incidentes_por_estado,
    obtener_incidentes_por_prioridad, actualizar_estado_incidente,
    actualizar_prioridad_incidente, obtener_resumen_incidentes,
    crear_evidencia, obtener_evidencias_incidente, eliminar_evidencia,
    calcular_prioridad_ia
)

# Crear el router con configuración
router = APIRouter(
    prefix="/incidentes",
    tags=["Incidentes y Emergencias"],
    dependencies=[Depends(get_current_user)]  # Todos los endpoints requieren autenticación
)


# ============================================================================
# ENDPOINTS: REPORTE DE INCIDENTES (USUARIOS)
# ============================================================================

@router.post("/reportar", response_model=IncidenteDetailedResponse, status_code=201)
def reportar_incidente(
    datos: IncidenteCreate,
    request: Request,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reporta un nuevo incidente/emergencia vehicular con triaje automático.
    """
    incidente = crear_incidente(db, current_user.id_usuario, datos)
    
    # Registrar evento CREATE en bitácora
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=current_user.id_usuario,
        nombre_usuario=f"{current_user.nombre} {current_user.apellido}",
        evento="CREATE",
        recurso="INCIDENTE",
        accion=f"Nuevo incidente creado para vehículo ID {datos.id_vehiculo}. Prioridad: {incidente.prioridad}",
        payload=f"descripcion={datos.descripcion[:100]}..."
    )
    
    return incidente


@router.get("", response_model=IncidenteListResponse, status_code=200)
def listar_mis_incidentes(
    skip: int = 0,
    limit: int = 100,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene historial de incidentes reportados por el usuario actual (RBAC).
    """
    try:
        incidentes = obtener_incidentes_por_cliente(db, current_user.id_usuario, skip=skip, limit=limit)
        return IncidenteListResponse(
            total=len(incidentes),
            incidentes=incidentes
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cargando incidentes: {str(e)}"
        )


@router.get("/{id_incidente}", response_model=IncidenteDetailedResponse, status_code=200)
def obtener_detalles_incidente(
    id_incidente: int,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene detalles completos de un incidente específico validando pertenencia.
    """
    incidente = obtener_incidente_por_id(db, id_incidente)
    
    # Validar que pertenece al usuario (RBAC) - CORREGIDO id -> id_usuario
    if incidente.id_cliente != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para ver este incidente"
        )
    
    return incidente


# ============================================================================
# ENDPOINTS: GESTIÓN DE EVIDENCIAS
# ============================================================================

@router.post("/{id_incidente}/evidencias", response_model=EvidenciaResponse, status_code=201)
def agregar_evidencia_incidente(
    id_incidente: int,
    datos: EvidenciaCreate,
    request: Request,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Añade una nueva evidencia multimedia a un incidente ya reportado.
    """
    incidente = obtener_incidente_por_id(db, id_incidente)
    
    # Validar propiedad del incidente - CORREGIDO id -> id_usuario
    if incidente.id_cliente != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede agregar evidencias a este incidente"
        )
    
    evidencia = crear_evidencia(db, id_incidente, datos)
    
    # Registrar evento CREATE en bitácora
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=current_user.id_usuario,
        nombre_usuario=f"{current_user.nombre} {current_user.apellido}",
        evento="CREATE",
        recurso="EVIDENCIA",
        accion=f"Nueva evidencia agregada al incidente #{id_incidente}. Tipo: {datos.tipo}"
    )
    
    return evidencia


@router.get("/{id_incidente}/evidencias", response_model=List[EvidenciaResponse], status_code=200)
def obtener_evidencias_del_incidente(
    id_incidente: int,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las evidencias multimedia asociadas a un incidente.
    """
    incidente = obtener_incidente_por_id(db, id_incidente)
    
    # Validar acceso - CORREGIDO id -> id_usuario
    if incidente.id_cliente != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene acceso a estas evidencias"
        )
    
    evidencias = obtener_evidencias_incidente(db, id_incidente)
    return evidencias


@router.delete("/{id_incidente}/evidencias/{id_evidencia}", status_code=204)
def eliminar_evidencia_incidente(
    id_incidente: int,
    id_evidencia: int,
    request: Request,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina una evidencia específica de un incidente.
    """
    incidente = obtener_incidente_por_id(db, id_incidente)
    
    # Validar propiedad
    if incidente.id_cliente != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede eliminar evidencias de este incidente"
        )
    
    eliminar_evidencia(db, id_evidencia)
    
    # Registrar evento DELETE en bitácora
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=current_user.id_usuario,
        nombre_usuario=f"{current_user.nombre} {current_user.apellido}",
        evento="DELETE",
        recurso="EVIDENCIA",
        accion=f"Evidencia #{id_evidencia} eliminada del incidente #{id_incidente}"
    )
    
    return None


# ============================================================================
# ENDPOINTS: FILTROS Y BÚSQUEDA (OPERADORES/ADMIN)
# ============================================================================

@router.get("/filtros/por-estado", response_model=IncidenteListResponse, status_code=200)
def incidentes_por_estado(
    estado: str,
    skip: int = 0,
    limit: int = 100,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene incidentes filtrados por estado (Para operadores/admin).
    """
    incidentes = obtener_incidentes_por_estado(db, estado, skip=skip, limit=limit)
    return IncidenteListResponse(
        total=len(incidentes),
        incidentes=incidentes
    )


@router.get("/filtros/por-prioridad", response_model=IncidenteListResponse, status_code=200)
def incidentes_por_prioridad(
    prioridad: str,
    skip: int = 0,
    limit: int = 100,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene incidentes filtrados por prioridad (Para operadores/admin).
    """
    incidentes = obtener_incidentes_por_prioridad(db, prioridad, skip=skip, limit=limit)
    return IncidenteListResponse(
        total=len(incidentes),
        incidentes=incidentes
    )


@router.get("/vehiculo/{id_vehiculo}/historial", response_model=List[IncidenteResponse], status_code=200)
def historial_incidentes_vehiculo(
    id_vehiculo: int,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial completo de incidentes de un vehículo específico.
    """
    incidentes = obtener_incidentes_por_vehiculo(db, id_vehiculo)
    return incidentes


# ============================================================================
# ENDPOINTS: OPERACIONES DE TRIAJE Y ASIGNACIÓN (OPERADORES/ADMIN)
# ============================================================================

@router.patch("/{id_incidente}/estado", response_model=IncidenteResponse, status_code=200)
def actualizar_estado(
    id_incidente: int,
    nuevo_estado: str,
    request: Request,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Actualiza el estado de un incidente durante su ciclo de vida (Solo Admin).
    """
    incidente_anterior = obtener_incidente_por_id(db, id_incidente)
    estado_anterior = incidente_anterior.estado
    incidente = actualizar_estado_incidente(db, id_incidente, nuevo_estado)
    
    # Registrar evento UPDATE en bitácora
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=current_user.id_usuario,
        nombre_usuario=f"{current_user.nombre} {current_user.apellido}",
        evento="UPDATE",
        recurso="INCIDENTE",
        accion=f"Estado del incidente #{id_incidente} actualizado de {estado_anterior} a {nuevo_estado}"
    )
    
    return incidente


@router.patch("/{id_incidente}/prioridad", response_model=IncidenteResponse, status_code=200)
def actualizar_prioridad(
    id_incidente: int,
    nueva_prioridad: str,
    request: Request,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Actualiza la prioridad de un incidente (Ajuste manual por administrador).
    """
    incidente_anterior = obtener_incidente_por_id(db, id_incidente)
    prioridad_anterior = incidente_anterior.prioridad
    incidente = actualizar_prioridad_incidente(db, id_incidente, nueva_prioridad)
    
    # Registrar evento UPDATE en bitácora
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=current_user.id_usuario,
        nombre_usuario=f"{current_user.nombre} {current_user.apellido}",
        evento="UPDATE",
        recurso="INCIDENTE",
        accion=f"Prioridad del incidente #{id_incidente} actualizada de {prioridad_anterior} a {nueva_prioridad}"
    )
    
    return incidente


@router.get("/triaje/calcular-prioridad", response_model=TriajeAIResponse, status_code=200)
def calcular_prioridad_preview(
    descripcion: str,
    ubicacion_lat: float = None,
    ubicacion_long: float = None,
    current_user: UsuarioResponse = Depends(get_current_user)
):
    """
    Calcula la prioridad de forma previa alineado al Schema TriajeAIResponse de Pydantic V2.
    """
    resultado_ia = calcular_prioridad_ia(descripcion, ubicacion_lat, ubicacion_long)
    
    # CORREGIDO: Mapeo de nombres exactos para que coincidan con schemas/incidente.py
    return TriajeAIResponse(
        nivel_prioridad=str(resultado_ia["prioridad"]),
        diagnostico_presuntivo=resultado_ia["razon"],
        recomendaciones=[
            f"Tiempo estimado de atención en zona: {resultado_ia['tiempo_respuesta_minutos']} minutos.",
            "Mantenga la calma y espere la asignación de una unidad móvil de asistencia."
        ],
        taller_sugerido_id=None
    )


# ============================================================================
# ENDPOINTS: ESTADÍSTICAS Y DASHBOARD
# ============================================================================

@router.get("/stats/resumen", status_code=200)
def resumen_incidentes(
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el resumen estadístico de todos los incidentes para el Dashboard de administración.
    """
    resumen = obtener_resumen_incidentes(db)
    return resumen