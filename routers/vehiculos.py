"""
routers/vehiculos.py - Endpoints para gestión de Vehículos
CRUD protegido con autenticación JWT
Implementa inyección de dependencias para DB y usuario autenticado
"""

from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from models.database import get_db
from models.user import Usuario
from auth.dependencies import get_current_user
from schemas.user import UsuarioResponse
from utils.bitacora_helper import registrar_evento_bitacora
from schemas.vehiculo import (
    VehiculoCreate, VehiculoUpdate, VehiculoResponse,
    VehiculoDetailedResponse, VehiculoListResponsePydantic,
    VehiculoResponsePydantic, VehiculoDetailedResponsePydantic
)
from crud.vehiculo import (
    crear_vehiculo, obtener_vehiculo_por_id, obtener_vehiculos_por_cliente,
    actualizar_vehiculo, eliminar_vehiculo,
)

# Crear el router con configuración
router = APIRouter(
    prefix="/vehiculos",
    tags=["Vehículos"],
    dependencies=[Depends(get_current_user)]  # Todos los endpoints requieren autenticación
)

# ============================================================================
# ENDPOINTS: VEHÍCULOS DEL USUARIO
# ============================================================================

@router.get("", response_model=List[VehiculoResponsePydantic], status_code=200)
def listar_mis_vehiculos(
    skip: int = 0,
    limit: int = 100,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los vehículos registrados del usuario autenticado
    
    Implementa RBAC: El usuario solo ve sus propios vehículos
    
    Query Parameters:
        skip: Número de registros a saltar (paginación)
        limit: Máximo de registros a retornar
    
    Returns:
        Array de vehículos del usuario con información completa
    """
    try:
        vehiculos_orm = obtener_vehiculos_por_cliente(db, current_user.id_usuario, skip=skip, limit=limit)
        
        # Convertir ORM objects a modelos Pydantic (JSON serializable)
        vehiculos_pydantic = []
        for v in vehiculos_orm:
            v_pydantic = VehiculoResponsePydantic.model_validate(v)
            vehiculos_pydantic.append(v_pydantic)
        
        return vehiculos_pydantic
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cargar vehiculos: {str(e)}"
        )


@router.get("/{id_vehiculo}", response_model=VehiculoDetailedResponsePydantic, status_code=200)
def obtener_mi_vehiculo(
    id_vehiculo: int,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene detalles completos de un vehículo específico
    
    Valida que el vehículo pertenece al usuario autenticado
    
    Path Parameters:
        id_vehiculo: ID del vehículo
    
    Returns:
        Vehículo con información de marca y modelo
    """
    vehiculo = obtener_vehiculo_por_id(db, id_vehiculo)
    
    # Obtener el Cliente asociado al Usuario autenticado
    cliente = db.query(Usuario).filter(Usuario.id_usuario == current_user.id_usuario).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario actual no tiene un perfil de cliente."
        )
    
    # Validar propiedad (RBAC)
    if vehiculo.id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para acceder a este vehículo"
        )
    
    return VehiculoDetailedResponsePydantic.model_validate(vehiculo)


@router.post("", response_model=VehiculoResponsePydantic, status_code=201)
def registrar_vehiculo(
    datos: VehiculoCreate,
    request: Request,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo vehículo para el usuario autenticado
    
    Validaciones:
        - La placa debe ser única en el sistema
        - El usuario debe estar activo
    
    Request Body:
        placa: Placa de registro (única)
        marca: Marca del vehículo
        modelo: Modelo del vehículo
        anio: Año de fabricación (opcional)
        color: Color del vehículo (opcional)
    
    Returns:
        Vehículo creado con su ID
    """
    # Crear el vehículo con el id_usuario correcto
    vehiculo = crear_vehiculo(db, current_user.id_usuario, datos)
    
    # Registrar evento CREATE en bitácora
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=current_user.id_usuario,
        nombre_usuario=f"{current_user.nombre} {current_user.apellido}",
        evento="CREATE",
        recurso="VEHICULO",
        accion=f"Nuevo vehículo registrado: {datos.marca} {datos.modelo} (Placa: {datos.placa})"
    )
    
    return VehiculoResponsePydantic.model_validate(vehiculo)


@router.put("/{id_vehiculo}", response_model=VehiculoResponsePydantic, status_code=200)
def actualizar_mi_vehiculo(
    id_vehiculo: int,
    datos: VehiculoUpdate,
    request: Request,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza información de un vehículo del usuario
    
    Validaciones:
        - Solo el propietario puede actualizar
        - Si cambia placa, debe ser única
    
    Path Parameters:
        id_vehiculo: ID del vehículo a actualizar
    
    Request Body:
        placa: Nueva placa (opcional)
        color: Nuevo color (opcional)
        anio: Nuevo año (opcional)
    
    Returns:
        Vehículo actualizado
    """
    # Obtener el Cliente asociado al Usuario autenticado
    cliente = db.query(Usuario).filter(Usuario.id_usuario == current_user.id_usuario).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario actual no tiene un perfil de cliente."
        )
    
    # Obtener datos anteriores para el registro de bitácora
    vehiculo_anterior = obtener_vehiculo_por_id(db, id_vehiculo)
    cambios = []
    if datos.placa:
        cambios.append(f"placa={vehiculo_anterior.placa}→{datos.placa}")
    if datos.color:
        cambios.append(f"color={vehiculo_anterior.color}→{datos.color}")
    if datos.anio:
        cambios.append(f"año={vehiculo_anterior.anio}→{datos.anio}")
    
    vehiculo = actualizar_vehiculo(db, id_vehiculo, current_user.id_usuario, datos)
    
    # Registrar evento UPDATE en bitácora
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=current_user.id_usuario,
        nombre_usuario=f"{current_user.nombre} {current_user.apellido}",
        evento="UPDATE",
        recurso="VEHICULO",
        accion=f"Vehículo {vehiculo_anterior.placa} actualizado: {', '.join(cambios)}"
    )
    
    return VehiculoResponsePydantic.model_validate(vehiculo)


@router.delete("/{id_vehiculo}", status_code=204)
def eliminar_mi_vehiculo(
    id_vehiculo: int,
    request: Request,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina un vehículo del usuario
    
    Validaciones:
        - Solo el propietario puede eliminar
        - Elimina también todos los incidentes asociados
    
    Path Parameters:
        id_vehiculo: ID del vehículo a eliminar
    
    Returns:
        204 No Content si fue exitoso
    """
    # Obtener el Cliente asociado al Usuario autenticado
    cliente = db.query(Usuario).filter(Usuario.id_usuario == current_user.id_usuario).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario actual no tiene un perfil de cliente."
        )
    
    # Obtener datos del vehículo antes de eliminarlo
    vehiculo = obtener_vehiculo_por_id(db, id_vehiculo)
    placa = vehiculo.placa
    
    eliminar_vehiculo(db, id_vehiculo, current_user.id_usuario)
    
    # Registrar evento DELETE en bitácora
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=current_user.id_usuario,
        nombre_usuario=f"{current_user.nombre} {current_user.apellido}",
        evento="DELETE",
        recurso="VEHICULO",
        accion=f"Vehículo {placa} (ID: {id_vehiculo}) eliminado"
    )
    
    return None


# ============================================================================
# ENDPOINTS: INFORMACIÓN Y VERIFICACIÓN
# ============================================================================

@router.get("/{id_vehiculo}/disponibilidad", status_code=200)
def verificar_disponibilidad_vehiculo(
    id_vehiculo: int,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verifica si un vehículo está disponible y activo
    
    Útil para validar antes de crear un incidente
    """
    vehiculo = obtener_vehiculo_por_id(db, id_vehiculo)
    
    # Obtener el Cliente asociado al Usuario autenticado
    cliente = db.query(Usuario).filter(Usuario.id_usuario == current_user.id_usuario).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario actual no tiene un perfil de cliente."
        )
    
    if vehiculo.id_cliente != cliente.id_cliente:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para ver este vehículo"
        )
    
    return {
        "id_vehiculo": vehiculo.id_vehiculo,
        "placa": vehiculo.placa,
        "disponible": True  # Por ahora asumimos que está disponible si existe y pertenece al usuario
    }


# Importar HTTPException aquí para evitar circular imports
from fastapi import HTTPException
