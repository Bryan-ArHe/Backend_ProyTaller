from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.taller import Taller
from schemas.taller import TallerSimpleResponse, TallerCreate
from dependencies import get_db
from auth.dependencies import get_current_gestor_id

router = APIRouter(prefix="/talleres", tags=["Talleres"])

@router.get("/", response_model=list[TallerSimpleResponse])
def listar_talleres_por_tenant(
    db: Session = Depends(get_db),
    id_gestor: int = Depends(get_current_gestor_id)
):
    # Solicitamos columnas primitivas de forma explícita
    talleres_db = db.query(
        Taller.id_taller,
        Taller.id_gestor,
        Taller.nombre,
        Taller.direccion,
        func.ST_AsText(Taller.ubicacion).label("ubicacion_wkt")
    ).filter(Taller.id_gestor == id_gestor).all()
    
    # Construimos un mapeo de diccionarios planos. 
    # Al no haber objetos intermedios de SQLAlchemy, Pydantic lo serializa al instante.
    return [
        {
            "id_taller": t[0],
            "id_gestor": t[1],
            "nombre": t[2],
            "direccion": t[3],
            "ubicacion_wkt": t[5]
        } for t in talleres_db
    ]

@router.post("/", response_model=TallerSimpleResponse, status_code=201)
def crear_taller_espacial(
    payload: TallerCreate,
    db: Session = Depends(get_db),
    id_gestor: int = Depends(get_current_gestor_id)
):
    try:
        nuevo_taller = Taller(
            id_gestor=id_gestor,
            nombre=payload.nombre,
            direccion=payload.direccion,
            ubicacion=func.ST_GeomFromText(payload.ubicacion_wkt, 4326) if payload.ubicacion_wkt else None
        )
        db.add(nuevo_taller)
        db.commit()
        db.refresh(nuevo_taller)
        
        return {
            "id_taller": nuevo_taller.id_taller,
            "id_gestor": nuevo_taller.id_gestor,
            "nombre": nuevo_taller.nombre,
            "direccion": nuevo_taller.direccion,
            "ubicacion_wkt": payload.ubicacion_wkt
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al guardar taller: {str(e)}")

@router.get("/{id_taller}", response_model=TallerSimpleResponse)
def obtener_detalle_taller(
    id_taller: int,
    db: Session = Depends(get_db),
    id_gestor: int = Depends(get_current_gestor_id)
):
    taller_db = db.query(
        Taller.id_taller,
        Taller.id_gestor,
        Taller.nombre,
        Taller.direccion,
        func.ST_AsText(Taller.ubicacion).label("ubicacion_wkt")
    ).filter(Taller.id_taller == id_taller, Taller.id_gestor == id_gestor).first()
    
    if not taller_db:
        raise HTTPException(status_code=404, detail="Taller no encontrado o acceso no autorizado")
        
    return {
        "id_taller": taller_db.id_taller,
        "id_gestor": taller_db.id_gestor,
        "nombre": taller_db.nombre,
        "direccion": taller_db.direccion,
        "ubicacion_wkt": taller_db.ubicacion_wkt
    }