from sqlalchemy.orm import Session, joinedload
from models.taller import Taller
from schemas.taller import TallerCreate
from models.user import Usuario 

# --- LECTURA ---
def get_taller(db: Session, taller_id: int):
    """Busca un taller específico por su ID."""
    return db.query(Taller).filter(Taller.id_taller == taller_id).first()

def get_talleres(db: Session, usuario_actual: Usuario):
    # 🏢 CASO 1: El usuario es el Administrador de la empresa (SaaS Tenant Owner)
    if usuario_actual.rol and usuario_actual.rol.nombre == "Administrador":
        return db.query(Taller).filter(
            Taller.id_usuario_admin == usuario_actual.id_usuario
        ).options(joinedload(Taller.gestor)).all() # 🚀 joinedload carga los datos del gestor para Angular

    # 👤 CASO 2: El usuario es un Gestor de Taller (Solo ve su sucursal asignada)
    elif usuario_actual.rol and usuario_actual.rol.nombre == "Gestor":
        taller_asignado = db.query(Taller).filter(
            Taller.id_gestor == usuario_actual.id_usuario
        ).options(joinedload(Taller.gestor)).first()
        
        # Como el endpoint espera una lista (list[TallerSimpleResponse]), 
        # envolvemos el resultado en un arreglo o devolvemos una lista vacía si es None
        return [taller_asignado] if taller_asignado else []

    # 🚫 CASO 3: Cualquier otro rol no autorizado (ej. Técnicos o Clientes)
    else:
        return []