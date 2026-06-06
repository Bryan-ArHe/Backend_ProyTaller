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
    # 1. Traemos las columnas y usamos el nuevo campo de tu modelo
    talleres_db = db.query(
        Taller.id_taller,
        Taller.id_gestor,
        Taller.nombre,
        Taller.direccion,
        func.ST_AsText(Taller.ubicacion).label("ubicacion_wkt"),
        Taller.fecha_registro  # 👈 Sincronizado
    ).filter(Taller.id_gestor == id_gestor).all()
    
    resultado = []
    for fila in talleres_db:
        datos = fila._asdict() 
        resultado.append({
            "id_taller": datos["id_taller"],
            "id_gestor": datos["id_gestor"],
            "nombre": datos["nombre"],
            "direccion": datos["direccion"],
            "ubicacion_wkt": datos["ubicacion_wkt"],
            # ⬇️ Leemos de 'fecha_registro' (BD) y alimentamos 'fecha_registro' (Pydantic)
            "fecha_registro": datos["fecha_registro"]  
        })
        
    return resultado


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
            telefono=payload.telefono,
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
            "ubicacion_wkt": payload.ubicacion_wkt,
            "fecha_registro": nuevo_taller.fecha_registro  # 👈 Corregido el atributo del modelo
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
    # 1. BUG RESUELTO: Cambiado Taller.created_at por Taller.fecha_registro
    taller_db = db.query(
        Taller.id_taller,
        Taller.id_gestor,
        Taller.nombre,
        Taller.direccion,
        func.ST_AsText(Taller.ubicacion).label("ubicacion_wkt"),
        Taller.fecha_registro  # 👈 Sincronizado
    ).filter(Taller.id_taller == id_taller, Taller.id_gestor == id_gestor).first()
    
    if not taller_db:
        raise HTTPException(status_code=404, detail="Taller no encontrado o acceso no autorizado")
        
    datos = taller_db._asdict()
    return {
        "id_taller": datos["id_taller"],
        "id_gestor": datos["id_gestor"],
        "nombre": datos["nombre"],
        "direccion": datos["direccion"],
        "ubicacion_wkt": datos["ubicacion_wkt"],
        "fecha_registro": datos["fecha_registro"]  # 👈 Corregido el retorno para Pydantic
    }