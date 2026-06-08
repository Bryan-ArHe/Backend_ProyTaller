from ast import List
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import crud
from models.taller import Taller
from models.user import Usuario
from schemas.taller import TallerSimpleResponse, TallerCreate
from dependencies import get_db
from auth.dependencies import get_current_gestor_id, get_current_user

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
            "fecha_registro": datos["fecha_registro"]  
        })
        
    return resultado

@router.get("/", response_model=list[TallerSimpleResponse])
def listar_talleres(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    talleres = crud.taller.get_talleres(db, usuario_actual=usuario_actual)
    return talleres



@router.post("/", response_model=TallerSimpleResponse, status_code=201)
def crear_taller_espacial(
    payload: TallerCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) # 🌟 Traemos al Administrador logueado
):
    # 1. Seguridad: Solo el dueño de la empresa (Administrador) puede crear talleres
    if current_user.rol.nombre != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Operación exclusiva para administradores de empresas SaaS"
        )

    # 2. Control de Cuotas SaaS: Extraemos la suscripción activa de este Administrador
    suscripcion = current_user.suscripciones[0] if current_user.suscripciones else None
    if not suscripcion or suscripcion.estado_suscripcion != "Activo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Tu suscripción comercial no está activa. No puedes registrar nuevos talleres."
        )

    # 3. Control de Límites: Contamos cuántos talleres ya creó este Administrador en PostgreSQL
    talleres_creados = db.query(Taller).filter(Taller.id_usuario_admin == current_user.id_usuario).count()
    
    if talleres_creados >= suscripcion.plan.limite_talleres:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Límite excedido. Tu plan actual permite un máximo de {suscripcion.plan.limite_talleres} talleres."
        )

    # 4. Inserción Segura en la Base de Datos
    try:
        nuevo_taller = Taller(
            id_usuario_admin=current_user.id_usuario, # 🌟 Mapeamos el taller a la Empresa/Tenant
            id_gestor=None,             # Opcional: Puede iniciar en None y asignarse después
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
            "id_usuario_admin": nuevo_taller.id_usuario_admin,
            "id_gestor": nuevo_taller.id_gestor,
            "nombre": nuevo_taller.nombre,
            "direccion": nuevo_taller.direccion,
            "ubicacion_wkt": payload.ubicacion_wkt,
            "fecha_registro": nuevo_taller.fecha_registro
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


@router.patch("/{id_taller}/asignar-gestor")
def asignar_encargado_taller(
    id_taller: int,
    id_gestor: Optional[int] = None, # 🌟 Si pasan None, remueves al gestor actual
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Seguridad del Tenant: El taller debe ser del Administrador logueado
    taller = db.query(Taller).filter(Taller.id_taller == id_taller, Taller.id_usuario_admin == current_user.id_usuario).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado o no pertenece a tu empresa")
    
    # Si envían un ID de gestor, verificamos que ese usuario exista y sea Gestor
    if id_gestor:
        gestor_existe = db.query(Usuario).filter(Usuario.id_usuario == id_gestor, Usuario.id_rol == 3).first() # Asumiendo rol 3 = Gestor
        if not gestor_existe:
            raise HTTPException(status_code=400, detail="El ID proporcionado no pertenece a un Gestor válido")

    # Impactamos el cambio en PostgreSQL
    taller.id_gestor = id_gestor
    db.commit()
    
    return {"status": "success", "message": "Personal encargado actualizado correctamente"}