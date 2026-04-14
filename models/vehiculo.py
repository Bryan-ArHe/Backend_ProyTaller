"""
models/vehiculo.py - Modelo para Vehículos
Relaciona Marca/Modelo con Cliente (Usuario) para la gestión de vehículos
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.database import Base
from datetime import datetime


class Vehiculo(Base):
    """
    Modelo Vehiculo - Representa los vehículos registrados en el sistema
    Relaciones:
        - Muchos-a-Uno con Usuario (propietario/cliente)
        - Muchos-a-Uno con Modelo (referencia al modelo)
        - Uno-a-Muchos con Incidente (historial de incidentes)
    
    Normalización 3FN:
        - Marca y Modelo están normalizados en tablas separadas
        - Información del propietario en tabla de Usuarios
        - Evita redundancia de datos
    
    Atributos:
        id: Identificador único del vehículo
        id_cliente: Clave foránea al Usuario (propietario)
        id_modelo: Clave foránea al Modelo de vehículo
        placa: Placa de registro único del vehículo (UNIQUE)
        vin: Número de Serie del Vehículo (VIN)
        color: Color del vehículo
        año: Año de fabricación del vehículo
        estado: Estado del vehículo (ACTIVO, INACTIVO, MANTENIMIENTO)
        fecha_registro: Fecha de registro en el sistema
    """
    __tablename__ = "vehiculos"
    
    id = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    id_modelo = Column(Integer, ForeignKey("modelos.id"), nullable=False, index=True)
    
    placa = Column(String(20), unique=True, nullable=False, index=True)
    vin = Column(String(50), unique=True, nullable=True)
    color = Column(String(30), nullable=True)
    año = Column(Integer, nullable=True)
    estado = Column(String(20), default="ACTIVO", nullable=False)  # ACTIVO, INACTIVO, MANTENIMIENTO
    
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    cliente = relationship("Usuario", back_populates="vehiculos")
    modelo = relationship("Modelo", back_populates="vehiculos")
    incidentes = relationship("Incidente", back_populates="vehiculo", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Vehiculo(id={self.id}, placa='{self.placa}', cliente_id={self.id_cliente})>"
