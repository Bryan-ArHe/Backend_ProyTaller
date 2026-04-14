"""
models/marca_modelo.py - Modelos para Marca y Modelo de Vehículos
Normalización 3FN: Separación de catálogos maestros para reutilización
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.database import Base
from datetime import datetime


class Marca(Base):
    """
    Modelo Marca - Catálogo maestro de marcas de vehículos
    Normalización: Se separa de Vehículo para evitar redundancia
    
    Atributos:
        id: Identificador único de la marca
        nombre: Nombre de la marca (ej: "Toyota", "Ford", "Chevrolet")
        pais_origen: País de origen de la marca
        fecha_creacion: Fecha de registro en el sistema
    """
    __tablename__ = "marcas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False, index=True)
    pais_origen = Column(String(100), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relación 1:N con Modelo
    modelos = relationship("Modelo", back_populates="marca", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Marca(id={self.id}, nombre='{self.nombre}')>"


class Modelo(Base):
    """
    Modelo Modelo - Catálogo de modelos dentro de cada marca
    Normalización: Evita duplicación si la misma marca tiene múltiples modelos
    
    Atributos:
        id: Identificador único del modelo
        id_marca: Clave foránea a Marca
        nombre: Nombre del modelo (ej: "Corolla", "Mustang")
        año_inicio: Año en que la marca comenzó a producir este modelo
        año_fin: Año en que terminó la producción (NULL si sigue en producción)
        fecha_creacion: Fecha de registro en el sistema
    """
    __tablename__ = "modelos"
    
    id = Column(Integer, primary_key=True, index=True)
    id_marca = Column(Integer, ForeignKey("marcas.id"), nullable=False, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    año_inicio = Column(Integer, nullable=True)
    año_fin = Column(Integer, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relación N:1 con Marca
    marca = relationship("Marca", back_populates="modelos")
    
    # Relación 1:N con Vehículo
    vehiculos = relationship("Vehiculo", back_populates="modelo", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Modelo(id={self.id}, nombre='{self.nombre}', marca='{self.marca.nombre}')>"
