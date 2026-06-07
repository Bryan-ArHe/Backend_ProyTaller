from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.user import SuscripcionTaller, PlanSaas
from auth.dependencies import get_current_user, require_admin
from datetime import datetime, timedelta

router = APIRouter(prefix="/saas", tags=["Administración SaaS (SuperAdmin)"])

@router.put("/suscripcion/{id_usuario_admin}", status_code=status.HTTP_200_OK)
def modificar_o_crear_suscripcion_empresa(
    id_usuario_admin: int, 
    id_nuevo_plan: int, 
    estado: str, # "Activo", "Suspendido", "Vencido"
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) # Tu dependencia de sesión
):
    # 1. Validar que el usuario sea un superAdmin real
    if current_user.rol.nombre != "superAdmin":
        raise HTTPException(status_code=403, detail="Operación exclusiva del proveedor SaaS")
        
    # 2. Validar que el nuevo plan exista en los catálogos
    plan = db.query(PlanSaas).filter(PlanSaas.id_plan == id_nuevo_plan).first()
    if not plan:
        raise HTTPException(status_code=404, detail="El Plan SaaS especificado no existe")
        
    # 3. Buscar si el administrador ya registra una suscripción previa
    suscripcion = db.query(SuscripcionTaller).filter(
        SuscripcionTaller.id_usuario_admin == id_usuario_admin
    ).first()
    
    if not suscripcion:
        # 🌟 SOLUCIÓN: Si NO existe la suscripción (Nueva Empresa), la CREAMOS desde cero
        ahora = datetime.utcnow()
        fecha_expiracion = ahora + timedelta(days=30)
        suscripcion = SuscripcionTaller(
            id_usuario_admin=id_usuario_admin,
            id_plan=id_nuevo_plan,
            estado_suscripcion=estado,
            fecha_inicio=ahora,
            fecha_fin=fecha_expiracion
        )
        db.add(suscripcion)
        message = "Suscripción inicial creada y vinculada exitosamente"
    else:
        # ACTUALIZAR PLAN (Si el admin ya tenía un plan y lo está cambiando o renovando)
        ahora_renovacion = datetime.utcnow()
        nueva_expiracion = ahora_renovacion + timedelta(days=30) # 🌟 Opcional: Renovamos 30 días más
        
        suscripcion.id_plan = id_nuevo_plan
        suscripcion.estado_suscripcion = estado
        suscripcion.fecha_inicio = ahora_renovacion  # 🌟 Seteamos la fecha del cambio
        suscripcion.fecha_fin = nueva_expiracion      # 🌟 Extendemos el contrato 30 días más
        message = "Plan SaaS y cuotas de almacenamiento actualizados con éxito"
    
    db.commit()
    db.refresh(suscripcion)
    
    return {
        "status": "success",
        "message": message,
        "limites_actuales": {
            "plan": plan.nombre_plan,
            "limite_talleres": plan.limite_talleres,
            "limite_tecnicos": plan.limite_tecnicos,
            "estado": suscripcion.estado_suscripcion,
            "fecha_expiracion": suscripcion.fecha_fin.strftime("%Y-%m-%d %H:%M:%S")
        }
    }