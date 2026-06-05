from sqlalchemy.orm import Session
from models.taller import Taller
from schemas.taller import TallerCreate, TallerUpdate

# --- LECTURA ---
def get_taller(db: Session, taller_id: int):
    """Busca un taller específico por su ID."""
    return db.query(Taller).filter(Taller.id_taller == taller_id).first()

def get_talleres(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene una lista paginada de talleres (solo los activos)."""
    return db.query(Taller).filter(Taller.estado_activo == True).offset(skip).limit(limit).all()

# --- CREACIÓN ---
def create_taller(db: Session, taller: TallerCreate):
    """Crea un nuevo taller en la base de datos."""
    # Convertimos el esquema Pydantic a un diccionario y se lo pasamos al modelo ORM
    db_taller = Taller(**taller.model_dump())
    db.add(db_taller)
    db.commit()          # Guardamos los cambios físicos en la base de datos
    db.refresh(db_taller) # Recargamos el objeto para obtener el ID autogenerado y la fecha
    return db_taller

# --- ACTUALIZACIÓN ---
def update_taller(db: Session, taller_id: int, taller_data: TallerUpdate):
    """Actualiza los datos de un taller existente."""
    db_taller = db.query(Taller).filter(Taller.id_taller == taller_id).first()
    
    if db_taller:
        # Extraemos solo los campos que el usuario envió explícitamente (exclude_unset=True)
        update_dict = taller_data.model_dump(exclude_unset=True)
        
        for key, value in update_dict.items():
            setattr(db_taller, key, value)
            
        db.commit()
        db.refresh(db_taller)
        
    return db_taller

# --- BORRADO LÓGICO ---
def delete_taller(db: Session, taller_id: int):
    """Desactiva un taller sin borrarlo de la base de datos (Borrado lógico)."""
    db_taller = db.query(Taller).filter(Taller.id_taller == taller_id).first()
    
    if db_taller:
        db_taller.estado_activo = False
        db.commit()
        db.refresh(db_taller)
        
    return db_taller