from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from fastapi import HTTPException, status
from models.solicitud import SolicitudServicio, EstadoSolicitud
from models.user import Usuario
from models.tecnico import Tecnico
from models.incidente import Incidente, EstadoIncidente 
from schemas.solicitud import SolicitudServicioCreate, SolicitudServicioUpdate

def generar_codigo_orden(db: Session) -> str:
    """
    Genera un código correlativo único para la Orden de Trabajo.
    Ejemplo: OT-2026-0001
    """
    anio_actual = datetime.now().year
    prefix = f"OT-{anio_actual}-"
    
    # Contamos cuántas órdenes se han creado en el año actual para calcular el secuencial
    count = db.query(func.count(SolicitudServicio.id)).filter(
        SolicitudServicio.codigo_orden.like(f"{prefix}%")
    ).scalar()
    
    secuencial = count + 1
    return f"{prefix}{secuencial:04d}"

def crear_orden_asignacion(db: Session, obj_in: SolicitudServicioCreate, usuario_gestor_id: int) -> SolicitudServicio:
    """
    1. Valida que el incidente exista y esté en un estado asignable.
    2. Valida que el técnico exista.
    3. Genera el código único de la orden.
    4. Crea la orden de trabajo y actualiza el estado del incidente a ASIGNADO.
    """
    # 1. Validar el Incidente
    incidente = db.query(Incidente).filter(Incidente.id == obj_in.incidente_id).first()
    if not incidente:
        raise HTTPException(status_code=404, detail="El incidente especificado no existe.")
    
    if incidente.estado in [EstadoIncidente.RESUELTO, EstadoIncidente.CANCELADO]:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede asignar un técnico a un incidente en estado {incidente.estado}."
        )
    
    # 2. Validar que el Técnico exista en la tabla operativa
    tecnico = db.query(Tecnico).filter(Tecnico.id_tecnico == obj_in.tecnico_id).first()
    if not tecnico:
        raise HTTPException(status_code=404, detail="El técnico especificado no está registrado.")

    # Generar el código único antes de abrir el bloque de transacción explícito si fuera necesario,
    # o usar la sesión activa.
    codigo_ot = generar_codigo_orden(db)

    try:
        incidente.estado = EstadoIncidente.ASIGNADO
        incidente.updated_at = datetime.utcnow()

        # 3. Crear la Orden de Trabajo
        nueva_orden = SolicitudServicio(
            codigo_orden=codigo_ot,
            incidente_id=obj_in.incidente_id,
            tecnico_id=obj_in.tecnico_id,
            taller_id=obj_in.taller_id,
            descripcion_trabajo=obj_in.descripcion_trabajo,
            estado=EstadoSolicitud.PENDIENTE, # Inicia en pendiente de aceptación por el técnico
            fecha_asignacion=datetime.utcnow()
        )
        
        db.add(nueva_orden)
        db.commit() # Confirma ambas operaciones a la vez en Supabase/PostgreSQL
        db.refresh(nueva_orden)
        
        return nueva_orden

    except Exception as e:
        db.rollback() # Si algo truena (ej. caída de red o constraint), deshace todo
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error crítico al procesar la asignación: {str(e)}"
        )

def actualizar_estado_orden(db: Session, orden_id: int, obj_in: SolicitudServicioUpdate) -> SolicitudServicio:
    """
    Permite al técnico o gestor avanzar el flujo de la orden (EN_PROCESO, RESUELTO, CANCELADO).
    Si la orden pasa a RESUELTO, se puede sincronizar opcionalmente el cierre del incidente.
    """
    orden = db.query(SolicitudServicio).filter(SolicitudServicio.id == orden_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada.")

    update_data = obj_in.model_dump(exclude_unset=True)
    
    try:
        for field, value in update_data.items():
            setattr(orden, field, value)
        
        # Lógica cruzada: Si el técnico resuelve la orden, cerramos el incidente de origen
        if obj_in.estado == EstadoSolicitud.RESUELTO:
            orden.fecha_finalizacion = datetime.utcnow()
            incidente = db.query(Incidente).filter(Incidente.id == orden.incidente_id).first()
            if incidente:
                incidente.estado = EstadoIncidente.RESUELTO
                incidente.updated_at = datetime.utcnow()

        orden.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(orden)
        return orden

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la orden: {str(e)}"
        )