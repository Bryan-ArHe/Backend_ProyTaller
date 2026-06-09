# -*- coding: utf-8 -*-
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload
from models.database import get_db
from models.user import Usuario
from models.taller import Taller
from config import get_settings

settings = get_settings()
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la sesión",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        # 🔍 PRINT DE CONTROL 1: Ver si el token se decodifica bien o se va al catch
        print(f"📡 DEBUG TOKEN - Email extraído del JWT: '{email}'")
        
        if email is None:
            raise credentials_exception
    except JWTError as e:
        # 🔍 PRINT DE CONTROL 2: Ver si la firma secreta (SECRET_KEY) falló
        print(f"❌ DEBUG TOKEN - Error al decodificar JWT: {str(e)}")
        raise credentials_exception
        
    user = db.query(Usuario).options(
        joinedload(Usuario.rol)
    ).filter(Usuario.email == email).first()
    
    # 🔍 PRINT DE CONTROL 3: Ver si el usuario realmente existía en la BD con ese correo
    print(f"🔍 DEBUG BD - Usuario encontrado en la consulta: {user}")
    
    if user is None:
        raise credentials_exception


def check_permissions(required_role: str):
    """
    Fábrica de dependencias para validar roles de manera blindada.
    Soporta la jerarquía: superAdmin > Administrador > Roles Operativos
    """
    def role_checker(current_user: Usuario = Depends(get_current_user)):
        rol_obj = getattr(current_user, "rol", None)
        rol_nombre = getattr(rol_obj, "nombre", "Cliente") if rol_obj else "Cliente"

        # 👑 El superAdmin y el Administrador heredan por defecto accesos de visualización
        if rol_nombre not in [required_role, "Administrador", "superAdmin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permisos suficientes. Se requiere rol: {required_role}"
            )
        return current_user
    return role_checker


def require_admin(current_user: Usuario = Depends(get_current_user)):
    """
    Asegura que solo roles de jerarquía administrativa (Administrador / superAdmin) entren al endpoint.
    """
    rol_obj = getattr(current_user, "rol", None)
    rol_nombre = getattr(rol_obj, "nombre", "Cliente") if rol_obj else "Cliente"

    # 🌟 Añadimos superAdmin al pase autorizado
    if rol_nombre not in ["Administrador", "superAdmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo personal de administración o la plataforma Saas pueden realizar esta acción"
        )
    return current_user


def get_current_gestor_id(current_user: Usuario = Depends(get_current_user)) -> int:
    """
    Inyecta el ID del gestor validando el rol. Si es Administrador global o superAdmin,
    retorna su propio id_usuario para evitar fallos de aislamiento relacional.
    """
    rol_obj = getattr(current_user, "rol", None)
    rol_nombre = getattr(rol_obj, "nombre", "Cliente") if rol_obj else "Cliente"
    
    # Añadimos soporte para evitar que el superAdmin y Admin se queden bloqueados en vistas operativas
    if rol_nombre not in ["Gestor", "Administrador", "superAdmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere el rol de Gestor de Taller o jerarquía superior."
        )
        
    return current_user.id_usuario


async def check_tenant_active(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Usuario:
    """
    Hook de validación perimetral: Intercepta peticiones de Roles 2, 3 y 4 
    y bloquea el acceso si la suscripción de su Tenant no está 'Activo'[cite: 2, 3].
    """
    if current_user.id_rol == 1:
        return current_user

    tenant_id = None
    if current_user.id_rol == 2:
        tenant_id = current_user.id_usuario
    
    elif current_user.id_rol in [3, 4]:
        taller_id = current_user.id_taller_asignado if current_user.id_rol == 3 else getattr(current_user, 'id_taller', None)
        if not taller_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario operativo sin asignación física de taller."
            )
            
        query_taller = await db.execute(
            select(Taller.id_gestor).where(Taller.id_taller == taller_id)
        )
        tenant_id = query_taller.scalar_one_or_none()

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se pudo determinar el Tenant de origen para este usuario."
        )

    # Validar el contrato en la tabla real 'suscripcion_taller'[cite: 3]
    query_sub = await db.execute(
        text("""
            SELECT estado_suscripcion, fecha_fin 
            FROM suscripcion_taller 
            WHERE id_usuario_admin = :tenant_id 
            ORDER BY id_suscripcion DESC LIMIT 1
        """), {"tenant_id": tenant_id}
    )
    sub_record = query_sub.fetchone()

    if not sub_record:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La franquicia asociada no posee un registro de suscripción SaaS."
        )

    if sub_record.estado_suscripcion != "Activo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado. La franquicia se encuentra en estado: {sub_record.estado_suscripcion}."
        )

    if sub_record.fecha_fin < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. La suscripción comercial de la empresa ha expirado."
        )

    return current_user


async def verify_tenant_quota(
    resource_type: str, 
    tenant_id: int,     
    db: AsyncSession
):
    """
    Verifica en caliente los límites de capacidad contratados frente al consumo físico actual de la base de datos.
    """
    from fastapi import HTTPException, status
    
    query_limits = await db.execute(
        text("""
            SELECT p.limite_talleres, p.limite_tecnicos 
            FROM plan_saas p
            JOIN suscripcion_taller s ON s.id_plan = p.id_plan
            WHERE s.id_usuario_admin = :tenant_id AND s.estado_suscripcion = 'Activo'
        """), {"tenant_id": tenant_id}
    )
    limits = query_limits.fetchone()
    
    if not limits:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La franquicia no posee una suscripción SaaS activa asignada."
        )

    if resource_type == "TALLER":
        query_count = await db.execute(
            text("SELECT COUNT(*) FROM taller WHERE id_gestor = :tenant_id"), 
            {"tenant_id": tenant_id}
        )
        actual_count = query_count.scalar()
        
        if actual_count >= limits.limite_talleres:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Límite de Infraestructura alcanzado. Su plan actual solo le permite registrar un máximo de {limits.limite_talleres} sucursales físicas."
            )

    elif resource_type == "TECNICO":
        query_count = await db.execute(
            text("""
                SELECT COUNT(*) FROM tecnico t
                JOIN taller w ON t.id_taller = w.id_taller
                WHERE w.id_gestor = :tenant_id
            """), {"tenant_id": tenant_id}
        )
        actual_count = query_count.scalar()
        
        if actual_count >= limits.limite_tecnicos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Límite de Personal alcanzado. Su plan actual solo le permite registrar un máximo de {limits.limite_tecnicos} operadores técnicos simultáneos."
            )