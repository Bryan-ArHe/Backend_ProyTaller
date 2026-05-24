from sqlalchemy.orm import Session
from models.bitacora import Bitacora
from schemas.bitacora import BitacoraCreate

def registrar_evento(db: Session, bitacora_in: BitacoraCreate):
    db_bitacora = Bitacora(
        id_usuario=bitacora_in.id_usuario,
        nombre_usuario=bitacora_in.nombre_usuario,
        evento=bitacora_in.evento,
        recurso=bitacora_in.recurso,
        accion=bitacora_in.accion,
        ip=bitacora_in.ip,
        dispositivo=bitacora_in.dispositivo
    )
    db.add(db_bitacora)
    db.commit()
    db.refresh(db_bitacora)
    return db_bitacora