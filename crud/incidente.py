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
    Placeholder para lógica de IA que determina prioridad automáticamente.
    """
    palabras_criticas = ["choque", "volcamiento", "vuelco", "explosión", "fuego", "incendio"]
    descripcion_lower = descripcion.lower()
    
    for palabra in palabras_criticas:
        if palabra in descripcion_lower:
            return {
                "prioridad": PrioridadIncidente.CRITICA.value if hasattr(PrioridadIncidente, 'CRITICA') else "CRITICA",
                "razon": f"Incidente crítico detectado: '{palabra}' en descripción",
                "tiempo_respuesta_minutos": 5
            }
    
    # Rango urbano heurístico (Santa Cruz de la Sierra)
    if ubicacion_lat is not None and ubicacion_long is not None:
        if -17.85 < ubicacion_lat < -17.70 and -63.25 < ubicacion_long < -63.10:
            return {
                "prioridad": PrioridadIncidente.ALTA.value if hasattr(PrioridadIncidente, 'ALTA') else "ALTA",
                "razon": "Incidente en zona urbana de alta circulación",
                "tiempo_respuesta_minutos": 15
            }
    
    return {
        "prioridad": PrioridadIncidente.MEDIA.value if hasattr(PrioridadIncidente, 'MEDIA') else "MEDIA",
        "razon": "Incidente evaluado como de prioridad media",
        "tiempo_respuesta_minutos": 30
    }


# ============================================================================
# OPERACIONES CRUD - INCIDENTE
# ============================================================================

def crear_incidente(db: Session, id_cliente: int, datos: IncidenteCreate) -> Incidente:
    """
    Crea un nuevo reporte de incidente validando que el vehículo pertenezca al cliente.
    """
    # Validar vehículo y correspondencia al cliente
    vehiculo = db.query(Vehiculo).filter(
        Vehiculo.id == datos.id_vehiculo,
        Vehiculo.id_cliente == id_cliente
    ).first()
    
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado o no pertenece al usuario"
        )
    
    calculo_ia = calcular_prioridad_ia(
        datos.descripcion,
        datos.ubicacion_lat,
        datos.ubicacion_long
    )
    
    try:
        nuevo_incidente = Incidente(
            id_vehiculo=datos.id_vehiculo,
            id_cliente=id_cliente,
            descripcion=datos.descripcion,
            estado=EstadoIncidente.PENDIENTE.value if hasattr(EstadoIncidente, 'PENDIENTE') else "PENDIENTE",
            prioridad=calculo_ia["prioridad"],
            ubicacion_lat=datos.ubicacion_lat,
            ubicacion_long=datos.ubicacion_long
        )
        
        db.add(nuevo_incidente)
        db.flush()  # Obtener id_incidente sin cerrar la transacción
        
        for evidencia_data in datos.evidencias:
            nueva_evidencia = Evidencia(
                id_incidente=nuevo_incidente.id_incidente,  # CORREGIDO: id -> id_incidente
                tipo=evidencia_data.tipo,
                url=evidencia_data.url,
                tamano_bytes=evidencia_data.tamano_bytes,
                descripcion=evidencia_data.descripcion
            )
            db.add(nueva_evidencia)
        
        db.commit()
        db.refresh(nuevo_incidente)
        return nuevo_incidente
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el incidente. Verifique los datos de integridad relacional."
        )


def obtener_incidente_por_id(db: Session, id_incidente: int) -> Incidente:
    """Obtiene un incidente específico validando su existencia."""
    incidente = db.query(Incidente).filter(Incidente.id_incidente == id_incidente).first()  # CORREGIDO: id -> id_incidente
    if not incidente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incidente con ID {id_incidente} no encontrado"
        )
    return incidente


def obtener_incidentes_por_cliente(db: Session, id_usuario: int, skip: int = 0, limit: int = 100) -> list:
    """Obtiene el historial de incidentes de un usuario (Orden cronológico inverso)."""
    return db.query(Incidente).filter(
        Incidente.id_cliente == id_usuario  # CORREGIDO: id_usuario -> id_cliente conforme al modelo
    ).order_by(Incidente.fecha_reporte.desc()).offset(skip).limit(limit).all()  # CORREGIDO: fecha_incidente -> fecha_reporte


def obtener_incidentes_por_vehiculo(db: Session, id_vehiculo: int) -> list:
    """Obtiene el historial de incidentes de un vehículo específico."""
    return db.query(Incidente).filter(
        Incidente.id_vehiculo == id_vehiculo
    ).order_by(Incidente.fecha_reporte.desc()).all()  # CORREGIDO: fecha_incidente -> fecha_reporte


def obtener_incidentes_por_estado(db: Session, estado: str, skip: int = 0, limit: int = 100) -> list:
    """Obtiene incidentes filtrados por estado para operadores."""
    return db.query(Incidente).filter(
        Incidente.estado == estado  # CORREGIDO: estado_incidente -> estado
    ).order_by(Incidente.fecha_reporte.desc()).offset(skip).limit(limit).all()  # CORREGIDO: fecha_incidente -> fecha_reporte


def obtener_incidentes_por_prioridad(db: Session, prioridad: str, skip: int = 0, limit: int = 100) -> list:
    """Obtiene incidentes filtrados por prioridad."""
    return db.query(Incidente).filter(
        Incidente.prioridad == prioridad
    ).order_by(Incidente.fecha_reporte.desc()).offset(skip).limit(limit).all()  # CORREGIDO: Agregado filtro faltante


def actualizar_estado_incidente(db: Session, id_incidente: int, nuevo_estado: str) -> Incidente:
    """Actualiza el estado actual de la emergencia."""
    incidente = obtener_incidente_por_id(db, id_incidente)
    incidente.estado = nuevo_estado
    db.commit()
    db.refresh(incidente)
    return incidente


def actualizar_prioridad_incidente(db: Session, id_incidente: int, nueva_prioridad: str) -> Incidente:
    """Modificación manual de prioridad por parte del personal operativo."""
    incidente = obtener_incidente_por_id(db, id_incidente)
    incidente.prioridad = nueva_prioridad
    db.commit()
    db.refresh(incidente)
    return incidente


def obtener_resumen_incidentes(db: Session) -> dict:
    """Genera las estadísticas agregadas consumidas por el Dashboard."""
    total = db.query(Incidente).count()
    por_estado = {}
    for estado in EstadoIncidente:
        por_estado[estado.value] = db.query(Incidente).filter(Incidente.estado == estado.value).count()
    
    por_prioridad = {}
    for prioridad in PrioridadIncidente:
        por_prioridad[prioridad.value] = db.query(Incidente).filter(Incidente.prioridad == prioridad.value).count()
    
    return {
        "total_incidentes": total,
        "por_estado": por_estado,
        "por_prioridad": por_prioridad
    }


# ============================================================================
# OPERACIONES CRUD - EVIDENCIA
# ============================================================================

def crear_evidencia(db: Session, id_incidente: int, datos: EvidenciaCreate) -> Evidencia:
    """Añade una nueva evidencia multimedia a un incidente existente."""
    obtener_incidente_por_id(db, id_incidente)
    
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
    """Obtiene todas las evidencias asociadas a un incidente."""
    obtener_incidente_por_id(db, id_incidente)
    return db.query(Evidencia).filter(Evidencia.id_incidente == id_incidente).all()


def eliminar_evidencia(db: Session, id_evidencia: int) -> bool:
    """Elimina permanentemente el registro de una evidencia de la base de datos."""
    evidencia = db.query(Evidencia).filter(Evidencia.id_evidencia == id_evidencia).first()  # CORREGIDO: id -> id_evidencia
    if not evidencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidencia con ID {id_evidencia} no encontrada"
        )
    
    db.delete(evidencia)
    db.commit()
    return True