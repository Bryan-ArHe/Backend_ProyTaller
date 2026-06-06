from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.incidente import Incidente
from schemas.incidente import IncidenteSimpleResponse, IncidenteCreate
from dependencies import get_db
from auth.dependencies import get_current_user

router = APIRouter(prefix="/incidentes", tags=["Incidentes"])

@router.get("/", response_model=list[IncidenteSimpleResponse])
def listar_incidentes_activos(db: Session = Depends(get_db)):
    incidentes_db = db.query(
        Incidente.id_incidente,
        Incidente.id_cliente,
        Incidente.descripcion,
        Incidente.estado_incidente,
        Incidente.fecha_incidente,
        func.ST_AsText(Incidente.ubicacion_averia).label("ubicacion_inicial_wkt")
    ).filter(Incidente.estado_incidente != "resuelto").all()
    
    return [
        {
            "id_incidente": i[0],
            "id_cliente": i[1],
            "descripcion": i[2],
            "estado_incidente": i[3],
            "fecha_incidente": i[4],
            "ubicacion_inicial_wkt": i[5]
        } for i in incidentes_db
    ]

@router.post("/", response_model=IncidenteSimpleResponse, status_code=201)
def registrar_incidente(payload: IncidenteCreate, db: Session = Depends(get_db)):
    try:
        nuevo_incidente = Incidente(
            id_cliente=payload.id_cliente,
            descripcion=payload.descripcion,
            placa=payload.placa,
            estado_incidente="pendiente",
            ubicacion_inicial=func.ST_GeomFromText(payload.ubicacion_inicial_wkt, 4326)
        )
        db.add(nuevo_incidente)
        db.commit()
        db.refresh(nuevo_incidente)
        
        return {
            "id_incidente": nuevo_incidente.id_incidente,
            "id_cliente": nuevo_incidente.id_cliente,
            "descripcion": nuevo_incidente.descripcion,
            "placa": nuevo_incidente.placa,
            "estado_incidente": nuevo_incidente.estado_incidente,
            "fecha_incidente": nuevo_incidente.fecha_incidente,
            "ubicacion_inicial_wkt": payload.ubicacion_inicial_wkt
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error espacial: {str(e)}")