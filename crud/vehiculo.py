"""
crud/vehiculo.py - Funciones CRUD para Vehículos, Marcas y Modelos
Data Access Layer para operaciones de base de datos
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.vehiculo import Vehiculo
from models.user import Usuario
from schemas.vehiculo import VehiculoCreate, VehiculoUpdate, MarcaCreate, ModeloCreate, ModeloUpdate
from fastapi import HTTPException, status

# ============================================================================
# OPERACIONES CRUD - VEHÍCULO
# ============================================================================

def crear_vehiculo(db: Session, id_cliente: int, datos: VehiculoCreate) -> Vehiculo:
    """
    Crea un nuevo vehículo para un usuario/cliente
    
    Validaciones:
        - La placa debe ser única
        - El modelo debe existir
        - El cliente debe existir y estar activo
    
    Args:
        db: Sesión de base de datos
        id_cliente: ID del usuario propietario del vehículo
        datos: Datos del vehículo a crear
    
    Returns:
        Objeto Vehiculo creado
    
    Raises:
        HTTPException: Si hay errores de validación
    """
    # Verificar que el cliente existe y está activo
    cliente = db.query(Usuario).filter(Usuario.id == id_cliente).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar que la placa sea única
    db_vehiculo = db.query(Vehiculo).filter(Vehiculo.placa == datos.placa).first()
    if db_vehiculo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La placa '{datos.placa}' ya está registrada en el sistema"
        )
    
    try:
        nuevo_vehiculo = Vehiculo(
            id_cliente=id_cliente,
            id_modelo=datos.id_modelo,
            placa=datos.placa,
            vin=datos.vin,
            color=datos.color,
            año=datos.año
        )
        db.add(nuevo_vehiculo)
        db.commit()
        db.refresh(nuevo_vehiculo)
        return nuevo_vehiculo
    except IntegrityError as e:
        db.rollback()
        if "placa" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La placa ya existe en el sistema"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el vehículo. Verifique los datos."
        )


def obtener_vehiculo_por_id(db: Session, id_vehiculo: int) -> Vehiculo:
    """Obtiene un vehículo específico por ID"""
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == id_vehiculo).first()
    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehículo con ID {id_vehiculo} no encontrado"
        )
    return vehiculo


def obtener_vehiculos_por_cliente(db: Session, id_cliente: int, skip: int = 0, limit: int = 100) -> list:
    """
    Obtiene todos los vehículos registrados por un cliente específico
    
    Usado para que el usuario vea solo sus propios vehículos
    """
    return db.query(Vehiculo).filter(
        Vehiculo.id_cliente == id_cliente
    ).offset(skip).limit(limit).all()


def obtener_vehculos_disponibles(db: Session, skip: int = 0, limit: int = 100) -> list:
    """Obtiene vehículos con estado ACTIVO"""
    return db.query(Vehiculo).filter(
        Vehiculo.estado == "ACTIVO"
    ).offset(skip).limit(limit).all()


def actualizar_vehiculo(db: Session, id_vehiculo: int, id_cliente: int, datos: VehiculoUpdate) -> Vehiculo:
    """
    Actualiza un vehículo (solo el propietario puede actualizarlo)
    
    Args:
        db: Sesión de base de datos
        id_vehiculo: ID del vehículo a actualizar
        id_cliente: ID del cliente (para verificar propiedad)
        datos: Datos a actualizar
    
    Returns:
        Vehiculo actualizado
    """
    vehiculo = obtener_vehiculo_por_id(db, id_vehiculo)
    
    # Verificar que el vehículo pertenece al cliente
    if vehiculo.id_cliente != id_cliente:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para actualizar este vehículo"
        )
    
    # Si intenta cambiar la placa, verificar que la nueva sea única
    if datos.placa and datos.placa != vehiculo.placa:
        placa_existente = db.query(Vehiculo).filter(
            Vehiculo.placa == datos.placa,
            Vehiculo.id != id_vehiculo
        ).first()
        if placa_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La placa '{datos.placa}' ya está registrada"
            )
    
    # Actualizar solo los campos proporcionados
    datos_dict = datos.dict(exclude_unset=True)
    for campo, valor in datos_dict.items():
        setattr(vehiculo, campo, valor)
    
    db.commit()
    db.refresh(vehiculo)
    return vehiculo


def eliminar_vehiculo(db: Session, id_vehiculo: int, id_cliente: int) -> bool:
    """
    Elimina un vehículo (solo el propietario puede eliminarlo)
    """
    vehiculo = obtener_vehiculo_por_id(db, id_vehiculo)
    
    # Verificar propiedad
    if vehiculo.id_cliente != id_cliente:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para eliminar este vehículo"
        )
    
    db.delete(vehiculo)
    db.commit()
    return True


def obtener_placa_disponible(db: Session, placa: str) -> bool:
    """Verifica si una placa está disponible (no registrada)"""
    vehiculo = db.query(Vehiculo).filter(Vehiculo.placa == placa).first()
    return vehiculo is None
