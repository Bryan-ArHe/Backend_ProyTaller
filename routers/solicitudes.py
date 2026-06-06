from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

# Importaciones de configuración y Base de Datos compartida
from models.database import get_db
from models.solicitud import SolicitudServicio
from auth.dependencies import get_current_user  # Importación de seguridad centralizada
from schemas.solicitud import (
    SolicitudServicioCreate, 
    SolicitudServicioUpdate, 
    SolicitudServicioResponse, 
    SolicitudServicioDetalladaResponse
)
from crud import solicitud as crud_solicitud
from utils.bitacora_helper import registrar_evento_bitacora

router = APIRouter(
    prefix="/solicitudes-servicio",  # Sincronizado exactamente con tu test_admin_endpoints.py
    tags=["Órdenes de Trabajo / Solicitudes de Servicio"]
)


@router.post("/asignar/", response_model=SolicitudServicioResponse, status_code=status.HTTP_201_CREATED)
def asignar_incidente(
    payload: SolicitudServicioCreate,
    request: Request, 
    usuario_actual = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para que el Gestor asigne un incidente a un Técnico y Taller específico.
    Cambia automáticamente el estado del incidente a ASIGNADO en el flujo de trabajo.
    """
    # Ejecuta el CRUD transaccional en la base de datos
    nueva_orden = crud_solicitud.crear_orden_asignacion(db=db, obj_in=payload)
    
    # Registro automatizado en la Bitácora de Auditoría
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=usuario_actual.id_usuario, 
        nombre_usuario=usuario_actual.email,  # Ajustado de username a email corporativo
        evento="CREAR",
        recurso="solicitud_servicio",
        accion=f"Incidente #{payload.id_incidente} asignado a Técnico #{payload.id_tecnico}. OT Generada: {nueva_orden.codigo_orden}",
        dispositivo="WEB"
    )
    
    return nueva_orden


@router.put("/{id}/estado/", response_model=SolicitudServicioResponse)
def actualizar_estado_ot(
    id: int,
    payload: SolicitudServicioUpdate,
    request: Request, 
    usuario_actual = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint de movilidad para que el Técnico actualice el progreso de su orden (Ej: EN_PROCESO, RESUELTO)
    o añada observaciones técnicas desde la app móvil.
    """
    orden_actualizada = crud_solicitud.actualizar_estado_orden(db=db, orden_id=id, obj_in=payload)
    
    # Registro en bitácora mapeado a tu estructura real
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=usuario_actual.id_usuario, 
        nombre_usuario=usuario_actual.email, 
        evento="ACTUALIZAR",
        recurso="solicitud_servicio",
        accion=f"Orden {orden_actualizada.codigo_orden} actualizada a estado: {payload.estado}. Observaciones: {payload.observaciones_tecnicas or 'Ninguna'}",
        dispositivo="MOBILE"  # El técnico opera desde la app móvil de asistencia viciada
    )
    
    return orden_actualizada


@router.get("/tecnico/{tecnico_id}/", response_model=List[SolicitudServicioDetalladaResponse])
def listar_ordenes_por_tecnico(tecnico_id: int, db: Session = Depends(get_db)):
    """
    Retorna la lista de órdenes detalladas asignadas a un técnico específico. 
    Ideal para el consumo del dashboard operativo del técnico asignado.
    """
    # CORRECCIÓN DE COLUMNA: .tecnico_id cambiado por .id_tecnico para mantener la normalización
    ordenes = db.query(SolicitudServicio).filter(SolicitudServicio.id_tecnico == tecnico_id).all()
    return ordenes


@router.get("/", response_model=List[SolicitudServicioResponse])
def listar_solicitudes(db: Session = Depends(get_db)):
    """
    Retorna el listado global de solicitudes de servicio registradas en el sistema.
    """
    return db.query(SolicitudServicio).all()