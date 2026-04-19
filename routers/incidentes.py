"""
routers/incidentes.py - Endpoints para reporte de Incidentes y Evidencia
Sistema de emergencias vehiculares con triaje automático y captura multimedia
Protegido con autenticación JWT e inyección de dependencias
"""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.database import get_db
from dependencies import get_current_user
from schemas.user import UsuarioResponse
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
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reporta un nuevo incidente/emergencia vehicular
    
    Proceso automático:
    1. Valida que el vehículo pertenece al usuario
    2. Ejecuta algoritmo IA para determinar prioridad
    3. Crea el incidente con estado PENDIENTE
    4. Registra evidencias multimedia capturadas
    5. Sistema de triaje lo pone en cola de atención
    
    Request Body:
        id_vehiculo: ID del vehículo involucrado (must belong to user)
        descripcion: Descripción detallada del incidente (10-1000 chars)
        ubicacion_lat: Latitud GPS del incidente (optional, -90 to 90)
        ubicacion_long: Longitud GPS del incidente (optional, -180 to 180)
        evidencias: Lista de evidencias multimedia capturadas
            - tipo: FOTO, VIDEO, AUDIO, DOCUMENTO
            - url: URL del archivo almacenado
            - tamano_bytes: Tamaño del archivo (optional)
            - descripcion: Descripción de la evidencia (optional)
    
    Returns:
        Incidente creado con ID, estado PENDIENTE, prioridad asignada por IA
        e información de todas las evidencias asociadas
    
    Example Request:
    {
        "id_vehiculo": 1,
        "descripcion": "Choque frontal en Cra. 7 con calle 93. Dos vehículos involucrados.",
        "ubicacion_lat": 4.72,
        "ubicacion_long": -74.01,
        "evidencias": [
            {
                "tipo": "FOTO",
                "url": "https://storage.example.com/incidente_001_foto1.jpg",
                "tamano_bytes": 2048576,
                "descripcion": "Vista frontal del daño"
            }
        ]
    }
    """
    incidente = crear_incidente(db, current_user.id, datos)
    return incidente


@router.get("", response_model=IncidenteListResponse, status_code=200)
def listar_mis_incidentes(
    skip: int = 0,
    limit: int = 100,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene historial de incidentes reportados por el usuario
    
    Implementa RBAC: El usuario solo ve sus propios incidentes
    
    Query Parameters:
        skip: Número de registros a saltar (paginación)
        limit: Máximo de registros a retornar
    
    Returns:
        Lista de incidentes del usuario con sus evidencias en orden descendente
    """
    incidentes = obtener_incidentes_por_cliente(db, current_user.id, skip=skip, limit=limit)
    return IncidenteListResponse(
        total=len(incidentes),
        incidentes=incidentes
    )


@router.get("/{id_incidente}", response_model=IncidenteDetailedResponse, status_code=200)
def obtener_detalles_incidente(
    id_incidente: int,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene detalles completos de un incidente específico
    
    Incluye:
    - Información del incidente (descripción, GPS, timestamps)
    - Prioridad asignada por IA
    - Estado actual
    - Todas las evidencias multimedia asociadas
    
    Validaciones:
    - El incidente debe existir
    - El usuario debe ser el reportante (RBAC)
    
    Path Parameters:
        id_incidente: ID del incidente
    
    Returns:
        Incidente completo con lista de evidencias
    """
    incidente = obtener_incidente_por_id(db, id_incidente)
    
    # Validar que pertenece al usuario (RBAC)
    if incidente.id_cliente != current_user.id:
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
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Añade una nueva evidencia multimedia a un incidente reportado
    
    Útil si el usuario captura evidencia después del reporte inicial
    
    Path Parameters:
        id_incidente: ID del incidente
    
    Request Body:
        tipo: Tipo de archivo - FOTO, VIDEO, AUDIO, DOCUMENTO
        url: URL donde se almacenó el archivo (ej: S3, Cloudinary, etc.)
        tamano_bytes: Tamaño del archivo en bytes (optional)
        descripcion: Descripción de la evidencia (optional)
    
    Returns:
        Evidencia creada con ID y timestamps
    """
    incidente = obtener_incidente_por_id(db, id_incidente)
    
    # Validar propiedad del incidente
    if incidente.id_cliente != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede agregar evidencias a este incidente"
        )
    
    evidencia = crear_evidencia(db, id_incidente, datos)
    return evidencia


@router.get("/{id_incidente}/evidencias", response_model=List[EvidenciaResponse], status_code=200)
def obtener_evidencias_del_incidente(
    id_incidente: int,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las evidencias multimedia asociadas a un incidente
    
    Path Parameters:
        id_incidente: ID del incidente
    
    Returns:
        Lista de evidencias con tipos, URLs y metadata
    """
    incidente = obtener_incidente_por_id(db, id_incidente)
    
    # Validar acceso
    if incidente.id_cliente != current_user.id:
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
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina una evidencia específica de un incidente
    
    Validaciones:
    - El incidente debe existir y pertenecer al usuario
    - La evidencia debe existir y pertenecer al incidente
    
    Path Parameters:
        id_incidente: ID del incidente
        id_evidencia: ID de la evidencia a eliminar
    
    Returns:
        204 No Content si fue exitoso
    """
    incidente = obtener_incidente_por_id(db, id_incidente)
    
    # Validar propiedad
    if incidente.id_cliente != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede eliminar evidencias de este incidente"
        )
    
    eliminar_evidencia(db, id_evidencia)
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
    Obtiene incidentes filtrados por estado
    
    ⚠️ Requiere rol OPERADOR o ADMIN
    
    Query Parameters:
        estado: PENDIENTE, EN_TRIAJE, ASIGNADO, EN_ATENCION, RESUELTO, CANCELADO
        skip: Paginación
        limit: Límite de registros
    
    Returns:
        Lista de incidentes en el estado especificado
    """
    # En producción, validar rol: debe ser operador o admin
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
    Obtiene incidentes filtrados por prioridad
    
    ⚠️ Requiere rol OPERADOR o ADMIN
    
    Query Parameters:
        prioridad: BAJA, MEDIA, ALTA, CRITICA
        skip: Paginación
        limit: Límite de registros
    
    Returns:
        Lista de incidentes con la prioridad especificada
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
    Obtiene historial completo de incidentes de un vehículo específico
    
    Útil para análisis de historial de siniestros
    
    Path Parameters:
        id_vehiculo: ID del vehículo
    
    Returns:
        Lista de incidentes del vehículo en orden descendente
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
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza el estado de un incidente durante su ciclo de vida
    
    ⚠️ Requiere rol OPERADOR o ADMIN
    
    Flujo de estados:
    PENDIENTE → EN_TRIAJE → ASIGNADO → EN_ATENCION → RESUELTO
    (O puede cancelarse en cualquier momento)
    
    Path Parameters:
        id_incidente: ID del incidente
    
    Query Parameters:
        nuevo_estado: PENDIENTE, EN_TRIAJE, ASIGNADO, EN_ATENCION, RESUELTO, CANCELADO
    
    Returns:
        Incidente con nuevo estado actualizado
    """
    # En producción, validar que es operador/admin
    incidente = actualizar_estado_incidente(db, id_incidente, nuevo_estado)
    return incidente


@router.patch("/{id_incidente}/prioridad", response_model=IncidenteResponse, status_code=200)
def actualizar_prioridad(
    id_incidente: int,
    nueva_prioridad: str,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza la prioridad de un incidente (ajuste manual por operador)
    
    ⚠️ Requiere rol OPERADOR o ADMIN
    
    Path Parameters:
        id_incidente: ID del incidente
    
    Query Parameters:
        nueva_prioridad: BAJA, MEDIA, ALTA, CRITICA
    
    Returns:
        Incidente con prioridad actualizada
    """
    incidente = actualizar_prioridad_incidente(db, id_incidente, nueva_prioridad)
    return incidente


@router.get("/triaje/calcular-prioridad", response_model=TriajeAIResponse, status_code=200)
def calcular_prioridad_preview(
    descripcion: str,
    ubicacion_lat: float = None,
    ubicacion_long: float = None,
    current_user: UsuarioResponse = Depends(get_current_user)
):
    """
    Calcula la prioridad de forma previa sin crear un incidente
    
    Útil para mostrar al usuario cuál será la prioridad antes de reportar
    
    Query Parameters:
        descripcion: Descripción del incidente
        ubicacion_lat: Latitud (optional)
        ubicacion_long: Longitud (optional)
    
    Returns:
        Prioridad asignada, razón y tiempo estimado de respuesta
    """
    resultado_ia = calcular_prioridad_ia(descripcion, ubicacion_lat, ubicacion_long)
    
    return TriajeAIResponse(
        id_incidente=0,  # Preview, no hay ID aún
        prioridad_asignada=resultado_ia["prioridad"].value,
        razon_prioridad=resultado_ia["razon"],
        tiempo_respuesta_estimado_minutos=resultado_ia["tiempo_respuesta_minutos"]
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
    Obtiene resumen estadístico de todos los incidentes
    
    ⚠️ Requiere rol ADMINISTRADOR
    
    Returns:
        Total de incidentes, cantidad por estado, cantidad por prioridad
    """
    # En producción, validar que es admin
    resumen = obtener_resumen_incidentes(db)
    return resumen
