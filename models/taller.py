# Dentro de models/taller.py
from datetime import datetime
from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base

class Taller(Base):
    __tablename__ = "taller"

    id_taller = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario_admin = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), nullable=False)
    id_gestor = Column(Integer, ForeignKey("gestor_taller.id_gestor", ondelete="RESTRICT"), nullable=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(250), nullable=False)
    telefono = Column(String(20), nullable=True)
    ubicacion = Column(Geometry("POINT", srid=4326), nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)  # Fecha de creación en formato ISO

    # Relaciones obligatorias
    gestor = relationship("GestorTaller", back_populates="talleres")
    tecnicos = relationship("Tecnico", back_populates="taller")
    solicitudes = relationship("SolicitudServicio", back_populates="taller")

    # Relación de Composición: Al eliminar un taller, se destruyen sus zonas de cobertura de forma atómica
    zona_cobertura = relationship( "ZonaCobertura", back_populates="taller", cascade="all, delete-orphan")
    # Relación de Composición con Repuesto
    repuestos = relationship("Repuesto", back_populates="taller", cascade="all, delete-orphan")