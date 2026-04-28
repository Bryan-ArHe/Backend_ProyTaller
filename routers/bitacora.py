# routers/bitacora.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from models.database import get_db
from models.user import Usuario
from schemas.bitacora import BitacoraResponse
from auth.dependencies import get_current_user, check_permissions
import models.bitacora as bitacora_model

router = APIRouter(prefix="/bitacora", tags=["Auditoría y Logs"])

@router.get("/", response_model=List[BitacoraResponse])
def obtener_bitacora(
    skip: int = 0, 
    limit: int = 100, 
    evento: Optional[str] = Query(None, description="Filtrar por tipo de evento (LOGIN, CREAR, etc.)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permissions("Administrador"))
):
    """
    Obtiene el historial de actividades del sistema.
    Solo accesible para usuarios con rol 'Administrador'.
    """
    query = db.query(bitacora_model.Bitacora)
    
    if evento:
        query = query.filter(bitacora_model.Bitacora.evento == evento)
        
    logs = query.order_by(bitacora_model.Bitacora.fecha.desc()).offset(skip).limit(limit).all()
    return logs

@router.get("/usuario/{id_usuario}", response_model=List[BitacoraResponse])
def obtener_bitacora_por_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(check_permissions("Administrador"))
):
    """
    Obtiene todas las acciones realizadas por un usuario específico.
    """
    logs = db.query(bitacora_model.Bitacora).filter(
        bitacora_model.Bitacora.id_usuario == id_usuario
    ).order_by(bitacora_model.Bitacora.fecha.desc()).all()
    
    return logs