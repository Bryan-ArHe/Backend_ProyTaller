"""
crud/vehiculo.py - Funciones CRUD para Vehículos, Marcas y Modelos
Data Access Layer para operaciones de base de datos
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.marca_modelo import Marca, Modelo
from models.vehiculo import Vehiculo
from models.user import Usuario
from schemas.vehiculo import VehiculoCreate, VehiculoUpdate, MarcaCreate, ModeloCreate, ModeloUpdate
from fastapi import HTTPException, status


# ============================================================================
# OPERACIONES CRUD - MARCA
# ============================================================================

def crear_marca(db: Session, nombre: str, pais_origen: str = None) -> Marca:
    """
    Crea una nueva marca en la base de datos
    
    Args:
        db: Sesión de base de datos
        nombre: Nombre de la marca (UNIQUE)
        pais_origen: País de origen (opcional)
    
    Returns:
        Objeto Marca creado
    
    Raises:
        HTTPException (400): Si el nombre ya existe
    """
    db_marca = db.query(Marca).filter(Marca.nombre == nombre).first()
    if db_marca:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La marca '{nombre}' ya existe en el sistema"
        )
    
    try:
        nueva_marca = Marca(nombre=nombre, pais_origen=pais_origen)
        db.add(nueva_marca)
        db.commit()
        db.refresh(nueva_marca)
        return nueva_marca
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear la marca. Verifique los datos."
        )


def obtener_marca_por_id(db: Session, id_marca: int) -> Marca:
    """Obtiene una marca por su ID con lazy loading de modelos"""
    marca = db.query(Marca).filter(Marca.id == id_marca).first()
    if not marca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Marca con ID {id_marca} no encontrada"
        )
    return marca


def obtener_todas_marcas(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene lista paginada de todas las marcas"""
    return db.query(Marca).offset(skip).limit(limit).all()


def eliminar_marca(db: Session, id_marca: int) -> bool:
    """
    Elimina una marca (y sus modelos asociados por cascada)
    
    Returns:
        True si la marca fue eliminada exitosamente
    """
    marca = obtener_marca_por_id(db, id_marca)
    db.delete(marca)
    db.commit()
    return True


# ============================================================================
# OPERACIONES CRUD - MODELO
# ============================================================================

def crear_modelo(db: Session, id_marca: int, nombre: str, año_inicio: int = None, año_fin: int = None) -> Modelo:
    """
    Crea un nuevo modelo de vehículo
    
    Args:
        db: Sesión de base de datos
        id_marca: ID de la marca
        nombre: Nombre del modelo
        año_inicio: Año de inicio de producción (opcional)
        año_fin: Año de fin de producción (opcional)
    
    Returns:
        Objeto Modelo creado
    
    Raises:
        HTTPException (400/404): Si la marca no existe o hay validación
    """
    # Verificar que la marca existe
    marca = obtener_marca_por_id(db, id_marca)
    
    # Validar que el nombre del modelo sea único dentro de la marca
    db_modelo = db.query(Modelo).filter(
        Modelo.id_marca == id_marca,
        Modelo.nombre == nombre
    ).first()
    
    if db_modelo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El modelo '{nombre}' ya existe para la marca '{marca.nombre}'"
        )
    
    try:
        nuevo_modelo = Modelo(
            id_marca=id_marca,
            nombre=nombre,
            año_inicio=año_inicio,
            año_fin=año_fin
        )
        db.add(nuevo_modelo)
        db.commit()
        db.refresh(nuevo_modelo)
        return nuevo_modelo
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el modelo. Verifique los datos."
        )


def obtener_modelo_por_id(db: Session, id_modelo: int) -> Modelo:
    """Obtiene un modelo por su ID"""
    modelo = db.query(Modelo).filter(Modelo.id == id_modelo).first()
    if not modelo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Modelo con ID {id_modelo} no encontrado"
        )
    return modelo


def obtener_modelos_por_marca(db: Session, id_marca: int) -> list:
    """Obtiene todos los modelos de una marca específica"""
    marca = obtener_marca_por_id(db, id_marca)
    return db.query(Modelo).filter(Modelo.id_marca == id_marca).all()


def actualizar_modelo(db: Session, id_modelo: int, datos_actualizacion: ModeloUpdate) -> Modelo:
    """Actualiza un modelo existente"""
    modelo = obtener_modelo_por_id(db, id_modelo)
    
    # Solo actualizar campos que fueron proporcionados
    datos = datos_actualizacion.dict(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(modelo, campo, valor)
    
    db.commit()
    db.refresh(modelo)
    return modelo


def eliminar_modelo(db: Session, id_modelo: int) -> bool:
    """Elimina un modelo (y sus vehículos asociados por cascada)"""
    modelo = obtener_modelo_por_id(db, id_modelo)
    db.delete(modelo)
    db.commit()
    return True


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
    
    # Verificar que el modelo existe
    modelo = obtener_modelo_por_id(db, datos.id_modelo)
    
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
