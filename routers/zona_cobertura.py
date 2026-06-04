from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from schemas.zona_cobertura import ZonaCoberturaCreate, ZonaCoberturaResponse
from crud.zona_cobertura import crear_zona

router = APIRouter(
    prefix="/zonas",
    tags=["Zonas de Cobertura"]
)

@router.post("/", response_model=ZonaCoberturaResponse, status_code=status.HTTP_201_CREATED)
def crear_nueva_zona(zona: ZonaCoberturaCreate, db: Session = Depends(get_db)):
    try:
        return crear_zona(db=db, zona=zona)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar el polígono en PostGIS: {str(e)}"
        )