from sqlalchemy.orm import Session
from models.taller import Taller
from schemas.taller import TallerCreate, TallerUpdate
# Importamos el modelo de Usuario para tipar correctamente la validación de roles
from models.user import Usuario 

# --- LECTURA ---
def get_taller(db: Session, taller_id: int):
    """Busca un taller específico por su ID."""
    return db.query(Taller).filter(Taller.id_taller == taller_id).first()

def get_talleres(db: Session, usuario_actual: Usuario, skip: int = 0, limit: int = 100):
    query = db.query(Taller).filter(Taller.estado_activo == True)
    
    # Obtenemos de forma segura el nombre del rol del usuario actual
    rol_nombre = usuario_actual.rol.nombre if usuario_actual.rol else ""

    # 🌟 SOPORTE COMPLETO A TUS ROLES EXACTOS:
    if rol_nombre == "Gestor":
        # Aislamiento Multi-tenant estricto
        query = query.filter(Taller.id_gestor == usuario_actual.id_usuario)
        
    elif rol_nombre in ["Administrador", "Admistrador"]:
        # El administrador pasa de largo y visualiza todo en su dashboard global
        pass
        
    else:
        # Clientes o Técnicos no tienen acceso a este listado plano masivo
        return []

    return query.offset(skip).limit(limit).all()