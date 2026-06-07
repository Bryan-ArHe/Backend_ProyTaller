from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.user import SuscripcionTaller, PlanSaas
from auth.dependencies import require_admin # Tu dependencia actualizada

router = APIRouter(prefix="/saas", tags=["Administración SaaS (SuperAdmin)"])

@router.put("/suscripcion/{id_usuario_admin}", status_code=status.HTTP_200_OK)
def modificar_atributos_empresa(
    id_usuario_admin: int, 
    id_nuevo_plan: int, 
    estado: str, # "Activo", "Suspendido", "Vencido"
    db: Session = Depends(get_db),
    current_user = Depends(require_admin) # Protegido para jerarquía superior
):
    # 1. Validar que el usuario que ejecuta sea un superAdmin real
    if current_user.rol.nombre != "superAdmin":
        raise HTTPException(status_code=403, detail="Operación exclusiva del proveedor SaaS")
        
    # 2. Buscar la suscripción activa de la empresa
    suscripcion = db.query(SuscripcionTaller).filter(
        SuscripcionTaller.id_usuario_admin == id_usuario_admin
    ).first()
    
    if not suscripcion:
        raise HTTPException(status_code=404, detail="La empresa o administrador no registra suscripciones")
        
    # 3. Validar que el nuevo plan exista
    plan = db.query(PlanSaas).filter(PlanSaas.id_plan == id_nuevo_plan).first()
    if not plan:
        raise HTTPException(status_code=404, detail="El Plan SaaS especificado no existe")
        
    # 4. Actualizar atributos relacionales en caliente
    suscripcion.id_plan = id_nuevo_plan
    suscripcion.estado_suscripcion = estado
    
    db.commit()
    db.refresh(suscripcion)
    
    return {
        "status": "success",
        "message": "Atributos de la empresa actualizados correctamente",
        "limites_actuales": {
            "plan": plan.nombre_plan,
            "limite_talleres": plan.limite_talleres,
            "limite_tecnicos": plan.limite_tecnicos,
            "estado": suscripcion.estado_suscripcion
        }
    }