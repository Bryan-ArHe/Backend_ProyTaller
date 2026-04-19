"""
crud/incidente.py - Funciones CRUD para Incidentes y Evidencias
Manejo de reportes de emergencias vehiculares y evidencia multimedia
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.incidente import Incidente, Evidencia, EstadoIncidente, PrioridadIncidente, TipoEvidencia
from models.vehiculo import Vehiculo
from models.user import Usuario
from schemas.incidente import IncidenteCreate, EvidenciaCreate, TriajeAIResponse
from fastapi import HTTPException, status
from datetime import datetime


# ============================================================================
# SISTEMA DE TRIAJE IA (MOCK/PLACEHOLDER)
# ============================================================================

def calcular_prioridad_ia(descripcion: str, ubicacion_lat: float = None, ubicacion_long: float = None) -> dict:
    """
    Placeholder para lógica futura de IA que determina prioridad automáticamente
    
    Actualmente utiliza heurística simple:
    - Palabras clave en descripción → CRITICA
    - Ubicación en zona urbana (latitud/longitud) → ALTA
    - Default → MEDIA
    
    Args:
        descripcion: Descripción del incidente
        ubicacion_lat: Latitud del incidente
        ubicacion_long: Longitud del incidente
    
    Returns:
        dict con prioridad y razón
    """
    palabras_criticas = ["choque", "volcamiento", "vuelco", "explosión", "fuego", "incendio"]
    descripcion_lower = descripcion.lower()
    
    # Detectar incidentes críticos
    for palabra in palabras_criticas:
        if palabra in descripcion_lower:
            return {
                "prioridad": PrioridadIncidente.CRITICA,
                "razon": f"Incidente crítico detectado: '{palabra}' en descripción",
                "tiempo_respuesta_minutos": 5
            }
    
    # Detectar incidentes de alta prioridad
    if ubicacion_lat is not None and ubicacion_long is not None:
        # Heurística: si está dentro de rango urbano (ej: Bogotá)
        if 4.5 < ubicacion_lat < 4.8 and -74.3 < ubicacion_long < -73.9:
            return {
                "prioridad": PrioridadIncidente.ALTA,
                "razon": "Incidente en zona urbana de alta circulación",
                "tiempo_respuesta_minutos": 15
            }
    
    # Default: prioridad media
    return {
        "prioridad": PrioridadIncidente.MEDIA,
        "razon": "Incidente evaluado como de prioridad media",
        "tiempo_respuesta_minutos": 30
    }


# ============================================================================
# OPERACIONES CRUD - INCIDENTE
# ============================================================================

def crear_incidente(db: Session, id_cliente: int, datos: IncidenteCreate) -> Incidente:
    """
    Crea un nuevo reporte de incidente con evidencias
    
    Proceso:
    1. Validar que el vehículo existe y pertenece al cliente
    2. Calcular prioridad automáticamente con IA
    3. Crear incidente con estado PENDIENTE
    4. Añadir evidencias capturadas
    
    Args:
        db: Sesión de base de datos
        id_cliente: ID del usuario que reporta
        datos: Datos del incidente (incluye lista de evidencias)
    
    Returns:
        Objeto Incidente creado con evidencias
    
    Raises:
        HTTPException: Si hay validaciones fallidas
    """
    # Validar que el vehículo existe y pertenece al cliente
    vehiculo = db.query(Vehiculo).filter(
        Vehiculo.id == datos.id_vehiculo,
        Vehiculo.id_cliente == id_cliente
    ).first()
    
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado o no pertenece al usuario"
        )
    
    # Calcular prioridad usando sistema IA
    calculo_ia = calcular_prioridad_ia(
        datos.descripcion,
        datos.ubicacion_lat,
        datos.ubicacion_long
    )
    
    try:
        # Crear incidente con prioridad automática
        nuevo_incidente = Incidente(
            id_vehiculo=datos.id_vehiculo,
            id_cliente=id_cliente,
            descripcion=datos.descripcion,
            estado=EstadoIncidente.PENDIENTE,
            prioridad=calculo_ia["prioridad"],
            ubicacion_lat=datos.ubicacion_lat,
            ubicacion_long=datos.ubicacion_long
        )
        
        db.add(nuevo_incidente)
        db.flush()  # Flush para obtener el ID sin hacer commit aún
        
        # Añadir evidencias asociadas
        for evidencia_data in datos.evidencias:
            nueva_evidencia = Evidencia(
                id_incidente=nuevo_incidente.id,
                tipo=evidencia_data.tipo,
                url=evidencia_data.url,
                tamano_bytes=evidencia_data.tamano_bytes,
                descripcion=evidencia_data.descripcion
            )
            db.add(nueva_evidencia)
        
        db.commit()
        db.refresh(nuevo_incidente)
        return nuevo_incidente
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el incidente. Verifique los datos."
        )


def obtener_incidente_por_id(db: Session, id_incidente: int) -> Incidente:
    """Obtiene un incidente específico con sus evidencias"""
    incidente = db.query(Incidente).filter(Incidente.id == id_incidente).first()
    if not incidente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incidente con ID {id_incidente} no encontrado"
        )
    return incidente


def obtener_incidentes_por_cliente(db: Session, id_cliente: int, skip: int = 0, limit: int = 100) -> list:
    """
    Obtiene todos los incidentes reportados por un cliente
    Implementa RBAC: el usuario solo ve sus propios incidentes
    """
    return db.query(Incidente).filter(
        Incidente.id_cliente == id_cliente
    ).order_by(Incidente.fecha_reporte.desc()).offset(skip).limit(limit).all()


def obtener_incidentes_por_vehiculo(db: Session, id_vehiculo: int) -> list:
    """Obtiene el historial de incidentes de un vehículo específico"""
    return db.query(Incidente).filter(
        Incidente.id_vehiculo == id_vehiculo
    ).order_by(Incidente.fecha_reporte.desc()).all()


def obtener_incidentes_por_estado(db: Session, estado: str, skip: int = 0, limit: int = 100) -> list:
    """Obtiene incidentes filtrados por estado (para operadores/admin)"""
    return db.query(Incidente).filter(
        Incidente.estado == estado
    ).order_by(Incidente.fecha_reporte.desc()).offset(skip).limit(limit).all()


def obtener_incidentes_por_prioridad(db: Session, prioridad: str, skip: int = 0, limit: int = 100) -> list:
    """Obtiene incidentes filtrados por prioridad (para operadores/admin)"""
    return db.query(Incidente).filter(
        Incidente.prioridad == prioridad
    ).order_by(Incidente.fecha_reporte.desc()).offset(skip).limit(limit).all()


def actualizar_estado_incidente(db: Session, id_incidente: int, nuevo_estado: str) -> Incidente:
    """
    Actualiza el estado de un incidente
    Usado por operadores/sistema de triaje
    """
    incidente = obtener_incidente_por_id(db, id_incidente)
    
    # Validar que el nuevo estado es válido
    if nuevo_estado not in [e.value for e in EstadoIncidente]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Estados permitidos: {[e.value for e in EstadoIncidente]}"
        )
    
    incidente.estado = nuevo_estado
    db.commit()
    db.refresh(incidente)
    return incidente


def actualizar_prioridad_incidente(db: Session, id_incidente: int, nueva_prioridad: str) -> Incidente:
    """
    Actualiza la prioridad de un incidente
    Usado para ajustes manuales por operadores
    """
    incidente = obtener_incidente_por_id(db, id_incidente)
    
    # Validar que la prioridad es válida
    if nueva_prioridad not in [p.value for p in PrioridadIncidente]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prioridad inválida. Prioridades permitidas: {[p.value for p in PrioridadIncidente]}"
        )
    
    incidente.prioridad = nueva_prioridad
    db.commit()
    db.refresh(incidente)
    return incidente


def obtener_resumen_incidentes(db: Session) -> dict:
    """
    Obtiene resumen estadístico de incidentes (para dashboard admin)
    """
    total = db.query(Incidente).count()
    por_estado = {}
    for estado in EstadoIncidente:
        por_estado[estado.value] = db.query(Incidente).filter(
            Incidente.estado == estado.value
        ).count()
    
    por_prioridad = {}
    for prioridad in PrioridadIncidente:
        por_prioridad[prioridad.value] = db.query(Incidente).filter(
            Incidente.prioridad == prioridad.value
        ).count()
    
    return {
        "total_incidentes": total,
        "por_estado": por_estado,
        "por_prioridad": por_prioridad
    }


# ============================================================================
# OPERACIONES CRUD - EVIDENCIA
# ============================================================================

def crear_evidencia(db: Session, id_incidente: int, datos: EvidenciaCreate) -> Evidencia:
    """
    Añade una nueva evidencia a un incidente existente
    
    Args:
        db: Sesión de base de datos
        id_incidente: ID del incidente
        datos: Datos de la evidencia (tipo, url, etc.)
    
    Returns:
        Objeto Evidencia creado
    """
    # Validar que el incidente existe
    incidente = obtener_incidente_por_id(db, id_incidente)
    
    # Validar que el tipo de evidencia es válido
    if datos.tipo not in [t.value for t in TipoEvidencia]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de evidencia inválido. Tipos permitidos: {[t.value for t in TipoEvidencia]}"
        )
    
    try:
        nueva_evidencia = Evidencia(
            id_incidente=id_incidente,
            tipo=datos.tipo,
            url=datos.url,
            tamano_bytes=datos.tamano_bytes,
            descripcion=datos.descripcion
        )
        db.add(nueva_evidencia)
        db.commit()
        db.refresh(nueva_evidencia)
        return nueva_evidencia
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear la evidencia. Verifique los datos."
        )


def obtener_evidencias_incidente(db: Session, id_incidente: int) -> list:
    """Obtiene todas las evidencias asociadas a un incidente"""
    # Validar que el incidente existe
    obtener_incidente_por_id(db, id_incidente)
    
    return db.query(Evidencia).filter(
        Evidencia.id_incidente == id_incidente
    ).all()


def eliminar_evidencia(db: Session, id_evidencia: int) -> bool:
    """
    Elimina una evidencia específica
    """
    evidencia = db.query(Evidencia).filter(Evidencia.id == id_evidencia).first()
    if not evidencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidencia con ID {id_evidencia} no encontrada"
        )
    
    db.delete(evidencia)
    db.commit()
    return True
