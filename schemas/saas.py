from pydantic import BaseModel, EmailStr, Field, condecimal
from typing import Optional, Dict, Any
from datetime import date

# ==========================================
# SCHEMAS PARA EL CATÁLOGO DE PLANES MAESTROS
# ==========================================

class PlanBase(BaseModel):
    nombre: str = Field(..., max_length=100, description="Nombre único del Plan SaaS")
    precio_mensual: float = Field(..., ge=0.0, description="Monto mensual de suscripción en Bs.")
    limite_talleres: int = Field(..., gt=0, description="Cantidad máxima de talleres permitidos")
    limite_tecnicos: int = Field(..., gt=0, description="Cantidad máxima de técnicos en ruta")
    caracteristicas: Optional[Dict[str, Any]] = Field(default={}, description="Flags de módulos habilitados")

class PlanCreate(PlanBase):
    pass

class PlanResponse(PlanBase):
    id_plan: int

    class Config:
        from_attributes = True

# ==========================================
# SCHEMAS PARA EL APROVISIONAMIENTO DE TENANTS
# ==========================================

class TenantCreate(BaseModel):
    # Datos de la Cuenta de Acceso del Propietario (Rol 2)
    propietario_nombre: str = Field(..., max_length=100)
    propietario_apellido: str = Field(..., max_length=100)
    email_corporativo: EmailStr
    password_plana: str = Field(..., min_length=8, description="Contraseña de acceso inicial")
    
    # Datos Fiscales de la Franquicia (Tenant)
    razon_social: str = Field(..., max_length=150, description="Nombre corporativo de la empresa")
    nit: str = Field(..., max_length=30, description="Número de Identificación Tributaria")
    
    # Asignación de Contrato Inicial
    id_plan_inicial: int
    meses_vigencia: int = Field(default=12, gt=0)

class TenantCapacidadResponse(BaseModel):
    talleres_creados: int
    talleres_maximos: int
    tecnicos_activos: int
    tecnicos_maximos: int

class TenantGridResponse(BaseModel):
    id_gestor: int
    razon_social: str
    nit: str
    propietario_completo: str
    email_corporativo: str
    plan_actual: str
    capacidad: TenantCapacidadResponse
    estado_cuenta: str
    fecha_fin_contrato: date

    class Config:
        from_attributes = True