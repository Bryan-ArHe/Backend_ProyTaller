from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importamos la dependencia para conectarnos a la base de datos
from models.database import get_db 
from auth.dependencies import get_current_user, require_admin
from models.user import Usuario

# Importamos nuestras operaciones y contratos
from crud import taller as crud_taller
from schemas.taller import TallerCreate, TallerUpdate, TallerResponse

# Creamos el enrutador. 
# prefix="/talleres" significa que todas estas rutas empezarán con esa URL.
router = APIRouter(
    prefix="/talleres",
    tags=["Gestión de Talleres"],
    dependencies=[Depends(get_current_user)]  # Todos los endpoints requieren autenticación
)

# --- POST: Registrar un nuevo taller ---
@router.post("/", response_model=TallerResponse, status_code=status.HTTP_201_CREATED)
def create_taller(
    taller: TallerCreate, 
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Recibe los datos de Angular, los valida y crea el taller. SOLO ADMIN."""
    return crud_taller.create_taller(db=db, taller=taller)

# --- GET: Listar todos los talleres activos ---
@router.get("/", response_model=List[TallerResponse])
def read_talleres(
    skip: int = 0, 
    limit: int = 100, 
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Devuelve la lista de talleres. Útil para la tabla en Angular."""
    return crud_taller.get_talleres(db, skip=skip, limit=limit)

# --- GET: Obtener un solo taller por su ID ---
@router.get("/{taller_id}", response_model=TallerResponse)
def read_taller(
    taller_id: int, 
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Busca los detalles de un taller específico."""
    db_taller = crud_taller.get_taller(db, taller_id=taller_id)
    if db_taller is None:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    return db_taller

# --- PUT: Actualizar un taller ---
@router.put("/{taller_id}", response_model=TallerResponse)
def update_taller(
    taller_id: int, 
    taller: TallerUpdate, 
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Sobreescribe los datos permitidos de un taller. SOLO ADMIN."""
    db_taller = crud_taller.update_taller(db, taller_id=taller_id, taller_data=taller)
    if db_taller is None:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    return db_taller

# --- DELETE: Desactivar un taller (Borrado Lógico) ---
@router.delete("/{taller_id}", response_model=TallerResponse)
def delete_taller(
    taller_id: int, 
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Desactiva el taller para que no reciba más incidentes. SOLO ADMIN."""
    db_taller = crud_taller.delete_taller(db, taller_id=taller_id)
    if db_taller is None:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    return db_taller