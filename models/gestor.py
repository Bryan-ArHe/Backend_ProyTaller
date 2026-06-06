# -*- coding: utf-8 -*-
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base

class GestorTaller(Base):
    __tablename__ = "gestor_taller"

    # id_gestor es PK y FK al mismo tiempo para la herencia 1:1 y actúa como el Tenant ID
    id_gestor = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), primary_key=True)
    razon_social = Column(String(150), nullable=False)
    nit = Column(String(30), unique=True, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)

    # Relación con Usuario
    usuario = relationship("Usuario", back_populates="gestor_taller", uselist=False)

    # Relación con Talleres
    talleres = relationship("Taller", back_populates="gestor", cascade="all, delete-orphan")
    
    # Relacion de Asignacion con Tecnico
    tecnicos = relationship("Tecnico", back_populates="gestor", cascade="all, delete-orphan")
    