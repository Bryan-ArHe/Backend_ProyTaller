from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from models.database import get_db
from schemas.solicitud import (
    SolicitudServicioCreate, 
    SolicitudServicioUpdate, 
    SolicitudServicioResponse, 
    SolicitudServicioDetalladaResponse
)
from crud import solicitud as crud_solicitud
from utils.bitacora_helper import registrar_evento_bitacora
from routers.auth import get_current_user 

router = APIRouter(
    prefix="/solicitudes",
    tags=["Órdenes de Trabajo / Solicitudes de Servicio"]
)

@router.post("/asignar", response_model=SolicitudServicioResponse, status_code=status.HTTP_201_CREATED)
def asignar_incidente(
    payload: SolicitudServicioCreate,
    request: Request, 
    usuario_actual = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para que el Gestor asigne un incidente a un Técnico y Taller específico.
    Cambia automáticamente el estado del incidente a ASIGNADO.
    """
    # Ejecuta el CRUD transaccional
    nueva_orden = crud_solicitud.crear_orden_asignacion(db=db, obj_in=payload)
    
    # Registro automatizado usando los parámetros EXACTOS de tu utils.bitacora_helper
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=usuario_actual.id_usuario, # Ajustado de .id a .id_usuario
        nombre_usuario=usuario_actual.username, # Ajusta a .nombre o .email según tu modelo Usuario
        evento="CREAR",
        recurso="solicitud_servicio",
        accion=f"Incidente #{payload.incidente_id} asignado a Técnico #{payload.tecnico_id}. OT Generada: {nueva_orden.codigo_orden}",
        dispositivo="WEB"
    )
    
    return nueva_orden

@router.put("/{id}/estado", response_model=SolicitudServicioResponse)
def actualizar_estado_ot(
    id: int,
    payload: SolicitudServicioUpdate,
    request: Request, # <-- Agregado indispensable para tu helper de IP
    usuario_actual = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para que el Técnico actualice el progreso de su orden (Ej: EN_PROCESO, RESUELTO)
    o añada observaciones técnicas desde la app de Angular.
    """
    orden_actualizada = crud_solicitud.actualizar_estado_orden(db=db, orden_id=id, obj_in=payload)
    
    # Registro en bitácora mapeado a tu estructura real
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=usuario_actual.id_usuario, # Ajustado de .id a .id_usuario
        nombre_usuario=usuario_actual.username, # Ajusta a .nombre o .email según tu modelo Usuario
        evento="ACTUALIZAR",
        recurso="solicitud_servicio",
        accion=f"Orden {orden_actualizada.codigo_orden} actualizada a estado: {payload.estado}. Observaciones: {payload.observaciones_tecnicas or 'Ninguna'}",
        dispositivo="MOBILE" # Asumiendo que el técnico opera desde la App Móvil
    )
    
    return orden_actualizada

@router.get("/tecnico/{tecnico_id}", response_model=List[SolicitudServicioDetalladaResponse])
def listar_ordenes_por_tecnico(tecnico_id: int, db: Session = Depends(get_db)):
    """
    Retorna la lista de órdenes detalladas asignadas a un técnico específico. 
    Ideal para el consumo del dashboard de Angular del técnico.
    """
    from models.solicitud import SolicitudServicio
    # Realiza la consulta filtrando por la columna correcta de la tabla
    ordenes = db.query(SolicitudServicio).filter(SolicitudServicio.tecnico_id == tecnico_id).all()
    return ordenes