"""
crud/vehiculo.py - Funciones CRUD para Vehículos, Marcas y Modelos
Data Access Layer para operaciones de base de datos
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from dataclasses import asdict
from models.vehiculo import Vehiculo
from models.user import Usuario, Cliente
from schemas.vehiculo import VehiculoCreate, VehiculoUpdate
from fastapi import HTTPException, status

# ============================================================================
# OPERACIONES CRUD - VEHÍCULO
# ============================================================================

def crear_vehiculo(db: Session, id_cliente: int, datos: VehiculoCreate) -> Vehiculo:
    """
    Crea un nuevo vehículo para un cliente
    
    Validaciones:
        - La placa debe ser única
        - El cliente debe existir y estar activo
    
    Args:
        db: Sesión de base de datos
        id_cliente: ID del cliente (de tabla Cliente) propietario del vehículo
        datos: Datos del vehículo a crear
    
    Returns:
        Objeto Vehiculo creado
    
    Raises:
        HTTPException: Si hay errores de validación
    """
    # Verificar que el cliente existe en la tabla Cliente
    cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado. El usuario debe ser un cliente registrado para crear vehículos."
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
            marca=datos.marca,
            modelo=datos.modelo,
            placa=datos.placa,
            color=datos.color,
            anio=datos.anio
        )
        db.add(nuevo_vehiculo)
        db.commit()
        db.refresh(nuevo_vehiculo)
        return nuevo_vehiculo
    except IntegrityError as e:
        db.rollback()
        # Imprimimos el error real en la terminal para que puedas debuggear si algo falla
        print(f"\n{'='*80}")
        print(f"💥 ERROR DE BASE DE DATOS AL CREAR VEHÍCULO")
        print(f"{'='*80}")
        print(f"📍 Tipo de error: {type(e).__name__}")
        print(f"📍 Mensaje original: {str(e)}")
        print(f"📍 Detalles de la excepción: {e.orig}")
        print(f"📍 Código de error: {e.orig.pgcode if hasattr(e.orig, 'pgcode') else 'N/A'}")
        print(f"\n🔍 DATOS QUE SE INTENTARON INSERTAR:")
        print(f"   - id_cliente: {id_cliente}")
        print(f"   - marca: {datos.marca}")
        print(f"   - modelo: {datos.modelo}")
        print(f"   - placa: {datos.placa}")
        print(f"   - color: {datos.color}")
        print(f"   - anio: {datos.anio}")
        print(f"{'='*80}\n")
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al guardar el vehículo. Verifique que todos los datos sean correctos."
        )


def obtener_vehiculo_por_id(db: Session, id_vehiculo: int) -> Vehiculo:
    """Obtiene un vehículo específico por ID"""
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id_vehiculo == id_vehiculo).first()
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


def obtener_vehiculos_disponibles(db: Session, skip: int = 0, limit: int = 100) -> list:
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
            Vehiculo.id_vehiculo != id_vehiculo
        ).first()
        if placa_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La placa '{datos.placa}' ya está registrada"
            )
    
    # Actualizar solo los campos proporcionados
    datos_dict = asdict(datos)
    for campo, valor in datos_dict.items():
        if valor is not None:  # Solo actualizar campos no-None
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
