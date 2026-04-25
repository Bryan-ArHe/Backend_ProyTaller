from sqlalchemy.orm import Session, joinedload
from models.bitacora import Bitacora
from models.user import Usuario
from schemas.bitacora import BitacoraCreate
from datetime import datetime

def crear_bitacora(db: Session, datos_bitacora: BitacoraCreate) -> Bitacora:
    """
    Crea un nuevo registro en la bitácora.
    
    Args:
        db: Sesión de base de datos
        datos_bitacora: Datos del evento a registrar
        
    Returns:
        Bitacora: El registro creado
    """
    nuevo_registro = Bitacora(
        id_usuario=datos_bitacora.id_usuario,
        nombre_usuario=datos_bitacora.nombre_usuario,
        evento=datos_bitacora.evento,
        recurso=datos_bitacora.recurso,
        accion=datos_bitacora.accion,
        ip=datos_bitacora.ip,
        endpoint=datos_bitacora.endpoint,
        payload=datos_bitacora.payload,
        dispositivo=datos_bitacora.dispositivo,
        fecha=datetime.utcnow()
    )
    
    db.add(nuevo_registro)
    db.flush()  # Usar flush en lugar de commit para que el commit lo maneje el router padre
    return nuevo_registro

def get_bitacora_by_id(db: Session, skip: int = 0, limit: int = 100,
                       tipo: str = None, user_id: int = None) :
    query = db.query(Bitacora).options(joinedload(Bitacora.usuario))
    if tipo:
        query = query.filter(Bitacora.evento == tipo)
    if user_id:
        query = query.filter(Bitacora.id_usuario == user_id)
    
    return query.order_by(Bitacora.fecha.desc()).offset(skip).limit(limit).all()
