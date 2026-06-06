from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.tecnico import Tecnico
from models.taller import Taller
from schemas.tecnico import TecnicoSimpleResponse
from dependencies import get_db
from auth.dependencies import get_current_gestor_id

router = APIRouter(prefix="/tecnicos", tags=["Técnicos"])

def mapear_tecnico_a_dict(t: Tecnico) -> dict:
    # Esta función limpia extrae los datos de la relación 1:1 evitando recursiones
    return {
        "id_tecnico": t.id_tecnico,
        "id_taller": t.id_taller,
        "id_usuario": t.id_usuario,
        "especialidad": t.especialidad,
        "disponible": t.disponible,
        "email": t.usuario.email,
        "nombre": t.usuario.nombre,
        "apellido": t.usuario.apellido,
        "telefono": t.usuario.telefono
    }

@router.get("/", response_model=list[TecnicoSimpleResponse])
def listar_tecnicos(
    db: Session = Depends(get_db),
    id_gestor: int = Depends(get_current_gestor_id)
):
    tecnicos_db = db.query(Tecnico).join(Taller).filter(Taller.id_gestor == id_gestor).all()
    return [mapear_tecnico_a_dict(t) for t in tecnicos_db]

@router.get("/libres", response_model=list[TecnicoSimpleResponse])
def listar_tecnicos_libres(
    db: Session = Depends(get_db),
    id_gestor: int = Depends(get_current_gestor_id)
):
    tecnicos_libres = db.query(Tecnico).join(Taller).filter(
        Taller.id_gestor == id_gestor, 
        Tecnico.disponible == "Libre"
    ).all()
    return [mapear_tecnico_a_dict(t) for t in tecnicos_libres]