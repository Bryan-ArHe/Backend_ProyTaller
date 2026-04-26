from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.bitacora import Bitacora
from models.user import Usuario
from schemas.bitacora import BitacoraResponse
from dependencies import get_current_user
from crud import bitacora as crud_bitacora
from typing import List

route = APIRouter( prefix="/bitacora", tags=["Bitácora"])

@route.get("/", response_model=List[BitacoraResponse])
def listar_bitacora(
    tipo: str = None,
    user_id: int = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    GET /bitacora/
    
    Lista los eventos registrados en la bitácora con filtros opcionales.
    
    **Protección:** Requiere token JWT válido
    
    **Parámetros de consulta:**
        - tipo (str, opcional): Filtra por tipo de evento (e.g., "login", "error")
        - user_id (int, opcional): Filtra por ID de usuario
    """
    usuario = db.query(Usuario).filter(Usuario.id_usuario == current_user.id_usuario).first()
    if not usuario or not usuario.rol or usuario.rol.nombre != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado - solo administrador")
    bitacora_registros = crud_bitacora.get_bitacora_by_id(db, tipo=tipo, user_id=user_id)

    return [
        BitacoraResponse(
            id_bitacora=l.id_bitacora,
            fecha=l.fecha,
            id_usuario=l.id_usuario,
            nombre_usuario=l.nombre_usuario,
            evento=l.evento,
            recurso=l.recurso,
            accion=l.accion,
            ip=l.ip,
            endpoint=l.endpoint,
            payload=l.payload,
            dispositivo=l.dispositivo
        ) for l in bitacora_registros
    ] 