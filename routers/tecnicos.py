from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importamos la dependencia de base de datos
from dependencies import get_db 

# Importamos nuestras operaciones y contratos de técnicos
from crud import tecnico as crud_tecnico
from schemas.tecnico import TecnicoCreate, TecnicoUpdate, TecnicoResponse

router = APIRouter(
    prefix="/tecnicos",
    tags=["Gestión de Técnicos"]
)

# --- POST: Registrar un nuevo técnico ---
@router.post("/", response_model=TecnicoResponse, status_code=status.HTTP_201_CREATED)
def create_tecnico(tecnico: TecnicoCreate, db: Session = Depends(get_db)):
    """Registra un nuevo técnico vinculado a un usuario y a un taller."""
    # (Opcional: Aquí podrías añadir una validación para asegurarte de que el id_usuario o id_taller existan antes de crearlo)
    return crud_tecnico.create_tecnico(db=db, tecnico=tecnico)

# --- GET ESTRATÉGICO: Obtener técnicos libres para emergencias ---
# IMPORTANTE: Esta ruta debe ir antes de "/{id_tecnico}" para que FastAPI no confunda la palabra "libres" con un ID.
@router.get("/libres", response_model=List[TecnicoResponse])
def get_tecnicos_libres(db: Session = Depends(get_db)):
    """Devuelve la lista de técnicos listos para ser despachados."""
    return crud_tecnico.get_tecnicos_libres(db)

# --- GET ESTRATÉGICO: Obtener técnicos por taller ---
@router.get("/taller/{id_taller}", response_model=List[TecnicoResponse])
def get_tecnicos_por_taller(id_taller: int, db: Session = Depends(get_db)):
    """Filtra los técnicos pertenecientes a un taller específico."""
    return crud_tecnico.get_tecnicos_by_taller(db, id_taller=id_taller)

# --- GET: Listar todos los técnicos activos ---
@router.get("/", response_model=List[TecnicoResponse])
def get_tecnicos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Devuelve la lista general de técnicos."""
    return crud_tecnico.get_tecnicos(db, skip=skip, limit=limit)

# --- GET: Obtener un solo técnico por su ID ---
@router.get("/{id_tecnico}", response_model=TecnicoResponse)
def get_tecnico(id_tecnico: int, db: Session = Depends(get_db)):
    """Busca los detalles de un técnico específico."""
    db_tecnico = crud_tecnico.get_tecnico(db, id_tecnico=id_tecnico)
    if db_tecnico is None:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    return db_tecnico

# --- PUT: Actualizar técnico (Rastreo móvil y estado) ---
@router.put("/{id_tecnico}", response_model=TecnicoResponse)
def update_tecnico(id_tecnico: int, tecnico: TecnicoUpdate, db: Session = Depends(get_db)):
    """
    Actualiza el perfil. 
    Se usará en segundo plano para actualizar 'latitud_actual' y 'longitud_actual'.
    """
    db_tecnico = crud_tecnico.update_tecnico(db, id_tecnico=id_tecnico, tecnico_data=tecnico)
    if db_tecnico is None:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    return db_tecnico

# --- DELETE: Desactivar un técnico (Borrado Lógico) ---
@router.delete("/{id_tecnico}", response_model=TecnicoResponse)
def delete_tecnico(id_tecnico: int, db: Session = Depends(get_db)):
    """Marca al técnico como Inactivo en lugar de borrarlo de la DB."""
    db_tecnico = crud_tecnico.delete_tecnico(db, id_tecnico=id_tecnico)
    if db_tecnico is None:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    return db_tecnico