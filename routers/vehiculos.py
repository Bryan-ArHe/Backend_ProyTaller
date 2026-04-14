"""
routers/vehiculos.py - Endpoints para gestión de Vehículos
CRUD protegido con autenticación JWT
Implementa inyección de dependencias para DB y usuario autenticado
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from models.database import get_db
from dependencies import get_current_user
from schemas.user import UsuarioResponse
from schemas.vehiculo import (
    VehiculoCreate, VehiculoUpdate, VehiculoResponse,
    VehiculoDetailedResponse, VehiculoListResponse,
    MarcaCreate, MarcaResponse, MarcaWithModelos,
    ModeloCreate, ModeloUpdate, ModeloResponse, ModeloWithMarca
)
from crud.vehiculo import (
    crear_vehiculo, obtener_vehiculo_por_id, obtener_vehiculos_por_cliente,
    actualizar_vehiculo, eliminar_vehiculo,
    crear_marca, obtener_marca_por_id, obtener_todas_marcas, eliminar_marca,
    crear_modelo, obtener_modelo_por_id, obtener_modelos_por_marca, actualizar_modelo, eliminar_modelo
)

# Crear el router con configuración
router = APIRouter(
    prefix="/vehiculos",
    tags=["Vehículos"],
    dependencies=[Depends(get_current_user)]  # Todos los endpoints requieren autenticación
)


# ============================================================================
# ENDPOINTS: CATÁLOGO DE MARCAS
# ============================================================================

@router.get("/marcas", response_model=list[MarcaResponse], status_code=200)
def listar_marcas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene lista de todas las marcas disponibles en el sistema
    
    Query Parameters:
        skip: Número de registros a saltar (paginación)
        limit: Máximo de registros a retornar
    
    Returns:
        Lista de marcas disponibles
    """
    marcas = obtener_todas_marcas(db, skip=skip, limit=limit)
    return marcas


@router.get("/marcas/{id_marca}", response_model=MarcaWithModelos, status_code=200)
def obtener_marca(
    id_marca: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene detalles de una marca incluyendo todos sus modelos
    
    Path Parameters:
        id_marca: ID de la marca
    
    Returns:
        Marca con lista de modelos asociados
    """
    marca = obtener_marca_por_id(db, id_marca)
    return marca


@router.post("/marcas", response_model=MarcaResponse, status_code=201)
def crear_nueva_marca(
    datos: MarcaCreate,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva marca de vehículos
    ⚠️ Requiere rol de ADMINISTRADOR
    
    Request Body:
        nombre: Nombre único de la marca
        pais_origen: País de origen (opcional)
    
    Returns:
        Marca creada con su ID
    """
    # En producción, validar que es admin
    marca = crear_marca(db, nombre=datos.nombre, pais_origen=datos.pais_origen)
    return marca


@router.delete("/marcas/{id_marca}", status_code=204)
def eliminar_marca_endpoint(
    id_marca: int,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina una marca (y sus modelos/vehículos asociados)
    ⚠️ Requiere rol de ADMINISTRADOR
    """
    eliminar_marca(db, id_marca)
    return None


# ============================================================================
# ENDPOINTS: CATÁLOGO DE MODELOS
# ============================================================================

@router.get("/marcas/{id_marca}/modelos", response_model=list[ModeloResponse], status_code=200)
def listar_modelos_marca(
    id_marca: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los modelos de una marca específica
    
    Path Parameters:
        id_marca: ID de la marca
    
    Returns:
        Lista de modelos de la marca
    """
    modelos = obtener_modelos_por_marca(db, id_marca)
    return modelos


@router.get("/modelos/{id_modelo}", response_model=ModeloWithMarca, status_code=200)
def obtener_modelo(
    id_modelo: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene detalles de un modelo incluyendo su marca
    
    Path Parameters:
        id_modelo: ID del modelo
    """
    modelo = obtener_modelo_por_id(db, id_modelo)
    return modelo


@router.post("/modelos", response_model=ModeloResponse, status_code=201)
def crear_nuevo_modelo(
    datos: ModeloCreate,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo modelo de vehículos
    ⚠️ Requiere rol de ADMINISTRADOR
    
    Request Body:
        id_marca: ID de la marca a la que pertenece
        nombre: Nombre del modelo
        año_inicio: Año de inicio de producción (opcional)
        año_fin: Año de fin de producción (opcional)
    """
    modelo = crear_modelo(
        db,
        id_marca=datos.id_marca,
        nombre=datos.nombre,
        año_inicio=datos.año_inicio,
        año_fin=datos.año_fin
    )
    return modelo


@router.put("/modelos/{id_modelo}", response_model=ModeloResponse, status_code=200)
def actualizar_modelo_endpoint(
    id_modelo: int,
    datos: ModeloUpdate,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza información de un modelo
    ⚠️ Requiere rol de ADMINISTRADOR
    """
    modelo = actualizar_modelo(db, id_modelo, datos)
    return modelo


@router.delete("/modelos/{id_modelo}", status_code=204)
def eliminar_modelo_endpoint(
    id_modelo: int,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina un modelo (y sus vehículos asociados)
    ⚠️ Requiere rol de ADMINISTRADOR
    """
    eliminar_modelo(db, id_modelo)
    return None


# ============================================================================
# ENDPOINTS: VEHÍCULOS DEL USUARIO
# ============================================================================

@router.get("", response_model=VehiculoListResponse, status_code=200)
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
        Lista de vehículos del usuario con información completa
    """
    vehiculos = obtener_vehiculos_por_cliente(db, current_user.id, skip=skip, limit=limit)
    return VehiculoListResponse(
        total=len(vehiculos),
        vehiculos=vehiculos
    )


@router.get("/{id_vehiculo}", response_model=VehiculoDetailedResponse, status_code=200)
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
    
    # Validar propiedad (RBAC)
    if vehiculo.id_cliente != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para acceder a este vehículo"
        )
    
    return vehiculo


@router.post("", response_model=VehiculoResponse, status_code=201)
def registrar_vehiculo(
    datos: VehiculoCreate,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo vehículo para el usuario autenticado
    
    Validaciones:
        - La placa debe ser única en el sistema
        - El modelo debe existir
        - El usuario debe estar activo
    
    Request Body:
        id_modelo: ID del modelo del vehículo
        placa: Placa de registro (única)
        vin: VIN/Número de serie (opcional, debe ser único)
        color: Color del vehículo (opcional)
        año: Año de fabricación (opcional)
    
    Returns:
        Vehículo creado con su ID
    """
    vehiculo = crear_vehiculo(db, current_user.id, datos)
    return VehiculoResponse.from_orm(vehiculo)


@router.put("/{id_vehiculo}", response_model=VehiculoResponse, status_code=200)
def actualizar_mi_vehiculo(
    id_vehiculo: int,
    datos: VehiculoUpdate,
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
        vin: Nuevo VIN (opcional)
        color: Nuevo color (opcional)
        año: Nuevo año (opcional)
        estado: Nuevo estado (opcional)
    
    Returns:
        Vehículo actualizado
    """
    vehiculo = actualizar_vehiculo(db, id_vehiculo, current_user.id, datos)
    return VehiculoResponse.from_orm(vehiculo)


@router.delete("/{id_vehiculo}", status_code=204)
def eliminar_mi_vehiculo(
    id_vehiculo: int,
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
    eliminar_vehiculo(db, id_vehiculo, current_user.id)
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
    
    Useful para validar antes de crear un incidente
    """
    vehiculo = obtener_vehiculo_por_id(db, id_vehiculo)
    
    if vehiculo.id_cliente != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para ver este vehículo"
        )
    
    return {
        "id_vehiculo": vehiculo.id,
        "placa": vehiculo.placa,
        "estado": vehiculo.estado,
        "disponible": vehiculo.estado == "ACTIVO"
    }


# Importar HTTPException aquí para evitar circular imports
from fastapi import HTTPException
