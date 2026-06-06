# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base

class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), primary_key=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    ci = Column(String(20), unique=True, nullable=False)

    # Relación con Usuario
    usuario = relationship("Usuario", back_populates="cliente", uselist=False)
    # Relación con Vehículo
    vehiculos = relationship("Vehiculo", back_populates="cliente", cascade="all, delete-orphan")
    # Relación con Incidente
    incidentes = relationship("Incidente", back_populates="cliente", cascade="all, delete-orphan")