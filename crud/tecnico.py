from sqlalchemy.orm import Session
from models.tecnico import Tecnico
from schemas.tecnico import TecnicoCreate, TecnicoUpdate

# --- LECTURA GENERAL ---
def get_tecnico(db: Session, id_tecnico: int):
    """Obtiene un técnico específico por su ID."""
    return db.query(Tecnico).filter(Tecnico.id_tecnico == id_tecnico).first()

def get_tecnicos(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene la lista de todos los técnicos que no estén inactivos."""
    return db.query(Tecnico).filter(Tecnico.estado_disponibilidad != "Inactivo").offset(skip).limit(limit).all()

# --- LECTURA ESTRATÉGICA (Para reglas de negocio) ---
def get_tecnicos_by_taller(db: Session, id_taller: int):
    """Devuelve únicamente los técnicos que trabajan en un taller específico."""
    return db.query(Tecnico).filter(
        Tecnico.id_taller == id_taller, 
        Tecnico.estado_disponibilidad != "Inactivo"
    ).all()

def get_tecnicos_libres(db: Session):
    """Devuelve a todos los técnicos que están listos para atender una emergencia."""
    return db.query(Tecnico).filter(Tecnico.estado_disponibilidad == "Libre").all()

# --- CREACIÓN ---
def create_tecnico(db: Session, tecnico: TecnicoCreate):
    """Registra un nuevo técnico vinculándolo a un usuario y a un taller."""
    db_tecnico = Tecnico(**tecnico.model_dump())
    db.add(db_tecnico)
    db.commit()
    db.refresh(db_tecnico)
    return db_tecnico

# --- ACTUALIZACIÓN ---
def update_tecnico(db: Session, id_tecnico: int, tecnico_data: TecnicoUpdate):
    """
    Actualiza datos del técnico. 
    Crucial para actualizar la latitud/longitud en tiempo real desde la app móvil.
    """
    db_tecnico = get_tecnico(db, id_tecnico)
    
    if db_tecnico:
        update_dict = tecnico_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(db_tecnico, key, value)
            
        db.commit()
        db.refresh(db_tecnico)
        
    return db_tecnico

# --- BORRADO LÓGICO ---
def delete_tecnico(db: Session, id_tecnico: int):
    """En lugar de borrar el registro, lo marcamos como Inactivo."""
    db_tecnico = get_tecnico(db, id_tecnico)
    
    if db_tecnico:
        db_tecnico.estado_disponibilidad = "Inactivo"
        db.commit()
        db.refresh(db_tecnico)
        
    return db_tecnico