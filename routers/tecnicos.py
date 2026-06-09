from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import Usuario
from models.tecnico import Tecnico
from models.taller import Taller
from schemas.tecnico import TecnicoSimpleResponse, TecnicoCreate, TecnicoBase
from dependencies import get_db
from auth.dependencies import get_current_gestor_id
from auth.dependencies import check_tenant_active, verify_tenant_quota
router = APIRouter(prefix="/tecnicos", tags=["Técnicos"])

# Dentro de routers/tecnico.py

def mapear_tecnico_a_dict(t: Tecnico) -> dict:
    # Esta función limpia extrae los datos alineando la herencia 1:1 con el Schema
    return {
        "id_tecnico": t.id_tecnico,
        "id_taller": t.id_taller if t.id_taller else 0, # Asegura un entero si llega a ser None
        
        # SOLUCIÓN AL ERROR DE id_usuario: El ID del técnico es el mismo ID de usuario por la FK integrada
        "id_usuario": t.id_tecnico, 
        
        # SOLUCIÓN AL ERROR DE id_gestor (None): Extraemos el ID del gestor dueño de la sucursal/taller
        "id_gestor": t.taller.id_gestor if t.taller else (t.id_gestor if t.id_gestor else 0),
        
        # Campos heredados de TecnicoBase (Tu esquema pide 'disponible')
        "disponible": t.disponibilidad,
        
        # Campos de TecnicoSimpleResponse
        "especialidad": t.especialidad if t.especialidad else "General",
        "disponibilidad": t.disponibilidad,
        
        # Datos aplanados desde la relación 1:1 con la tabla raíz Usuario
        "email": t.usuario.email if t.usuario else "sin_email@correo.com",
        "nombre": t.usuario.nombre if t.usuario else "Sin Nombre",
        "apellido": t.usuario.apellido if t.usuario else "Sin Apellido",
        "telefono": t.usuario.telefono if t.usuario else None
    }

@router.get("/", response_model=list[TecnicoSimpleResponse])
def listar_tecnicos(
    db: Session = Depends(get_db),
    id_gestor: int = Depends(get_current_gestor_id)
):
    # Usamos joinedload para traer los datos del Usuario y Taller en una sola query eficiente
    tecnicos_db = db.query(Tecnico).join(Taller).options(
        joinedload(Tecnico.usuario),
        joinedload(Tecnico.taller)
    ).filter(Taller.id_gestor == id_gestor).all()
    
    return [mapear_tecnico_a_dict(t) for t in tecnicos_db]


@router.get("/libres", response_model=list[TecnicoSimpleResponse])
def listar_tecnicos_libres(
    db: Session = Depends(get_db),
    id_gestor: int = Depends(get_current_gestor_id)
):
    # Misma optimización para la lista de técnicos disponibles
    tecnicos_libres = db.query(Tecnico).join(Taller).options(
        joinedload(Tecnico.usuario),
        joinedload(Tecnico.taller)
    ).filter(
        Taller.id_gestor == id_gestor, 
        Tecnico.disponibilidad == "Libre"
    ).all()
    
    return [mapear_tecnico_a_dict(t) for t in tecnicos_libres]

@router.post("/crear-tecnico")
async def registrar_operador_ruta(
    payload: TecnicoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(check_tenant_active)
):
    # 1. Determinar de forma segura el id_gestor (Tenant ID) según el Rol del usuario autenticado
    if current_user.id_rol == 2:
        # Si es el Administrador (Dueño de la franquicia), su id_usuario es la raíz del Tenant
        tenant_id = current_user.id_usuario
    elif current_user.id_rol == 3:
        # Si es un Gestor, el Tenant ID se extrae buscando de forma asíncrona el dueño del taller asignado
        from sqlalchemy import text
        if not current_user.id_taller_asignado:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El Gestor no tiene un taller asignado para poder registrar personal."
            )
        
        query_taller = await db.execute(
            text("SELECT id_gestor FROM TALLER WHERE id_taller = :taller_id"),
            {"taller_id": current_user.id_taller_asignado}
        )
        tenant_id = query_taller.scalar_one_or_none()
    else:
        # Los roles 4 (Técnico) y 5 (Cliente) no tienen permitido bajo ninguna circunstancia crear técnicos
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Su rol no posee los privilegios necesarios para registrar operadores técnicos."
        )

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo asociar la solicitud a un Tenant corporativo válido."
        )

    # 2. VALIDACIÓN DE CUOTA: Detiene el flujo de la base de datos si el plan SaaS está lleno
    await verify_tenant_quota(resource_type="TECNICO", tenant_id=tenant_id, db=db)
    
    # 3. CONTINUACIÓN DEL FLUJO OPERATIVO (Inserción Atómica de datos reales)
    # Aquí puedes proceder con tu lógica original del script (por ejemplo, usando db.add() y await db.commit())
    # ...