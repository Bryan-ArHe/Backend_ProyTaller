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
    Modelo Vehiculo - Representa los vehículos registrados por clientes
    Relaciones:
        - Muchos-a-Uno con Cliente (propietario)
        - Muchos-a-Uno con Modelo (referencia técnica)
        - Uno-a-Muchos con Incidente (historial de incidentes)
    
    Atributos:
        id: Identificador único del vehículo
        id_cliente: Clave foránea al Cliente (propietario)
        placa: Placa de registro único del vehículo
        marca: Marca del vehículo
        modelo: Modelo del vehículo
        color: Color del vehículo
        anio: Año de fabricación del vehículo
        fecha_registro: Fecha de registro en el sistema
    """
    __tablename__ = "VEHICULO"
    
    id_vehiculo = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey("CLIENTE.id_cliente"), nullable=False, index=True)
    
    placa = Column(String(15), unique=True, nullable=False, index=True)
    marca = Column(String(60), nullable=False)
    modelo = Column(String(80), nullable=False)
    color = Column(String(30), nullable=True)
    anio = Column(Integer, nullable=True)
    
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="vehiculos")
    incidentes = relationship("Incidente", back_populates="vehiculo", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Vehiculo(id={self.id}, placa='{self.placa}', cliente_id={self.id_cliente})>"


# Importar al final para resolver relaciones sin circular imports
from models.incidente import Incidente  # noqa: E402, F401
