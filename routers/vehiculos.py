from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.vehiculo import Vehiculo
from schemas.vehiculo import VehiculoSimpleResponse
from dependencies import get_db
from auth.dependencies import get_current_user

router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])

@router.get("/", response_model=list[VehiculoSimpleResponse])
def listar_mis_vehiculos(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Extraemos solo las columnas necesarias en una tupla plana
    vehiculos_raw = db.query(
        Vehiculo.id_vehiculo,
        Vehiculo.id_usuario,
        Vehiculo.placa,
        Vehiculo.marca,
        Vehiculo.modelo,
        Vehiculo.color,
        Vehiculo.anio,
        Vehiculo.fecha_registro
    ).filter(Vehiculo.id_usuario == current_user.id_usuario).all()
    
    return [
        {
            "id_vehiculo": v[0],
            "id_usuario": v[1],
            "placa": v[2],
            "marca": v[3],
            "modelo": v[4],
            "color": v[5],
            "anio": v[6],
            "fecha_registro": v[7]
        } for v in vehiculos_raw
    ]