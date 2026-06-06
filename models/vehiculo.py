"""
models/vehiculo.py - Modelo para Vehículos
Relaciona Marca/Modelo con Usuario para la gestión de vehículos
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.database import Base
from datetime import datetime


class Vehiculo(Base):
    """
    Modelo Vehiculo - Representa los vehículos registrados por usuarios
    Relaciones:
        - Muchos-a-Uno con Usuario (propietario)
        - Uno-a-Muchos con Incidente (historial de incidentes)
    
    Atributos:
        id_vehiculo: Identificador único del vehículo
        id_usuario: Clave foránea al Usuario (propietario)
        placa: Placa de registro único del vehículo
        marca: Marca del vehículo
        modelo: Modelo del vehículo
        tipo: Tipo de vehículo
        color: Color del vehículo
        anio: Año de fabricación del vehículo
        fecha_registro: Fecha de registro en el sistema
    """
    __tablename__ = "vehiculo"
    
    id_vehiculo = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente", ondelete="CASCADE"), nullable=False, index=True)
    
    placa = Column(String(15), unique=True, nullable=False, index=True)
    marca = Column(String(60), nullable=False)
    modelo = Column(String(80), nullable=False)
    tipo = Column(String(50), nullable=True)  # 'Automóvil', 'Motocicleta', 'Camión', etc.
    color = Column(String(30), nullable=True)
    anio = Column(Integer, nullable=True)
    
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="vehiculos")
    incidentes = relationship("Incidente", back_populates="vehiculo", cascade="all")
    
