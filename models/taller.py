# Dentro de models/taller.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base

class Taller(Base):
    __tablename__ = "taller"

    id_taller = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_gestor = Column(Integer, ForeignKey("gestor_taller.id_gestor", ondelete="RESTRICT"), nullable=False)
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(250), nullable=False)
    telefono = Column(String(20), nullable=True)

    # Relaciones obligatorias
    gestor = relationship("GestorTaller", back_populates="talleres")
    tecnicos = relationship("Tecnico", back_populates="taller")
    solicitudes = relationship("SolicitudServicio", back_populates="taller")