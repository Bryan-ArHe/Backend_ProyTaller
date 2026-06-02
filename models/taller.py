from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from models.database import Base
from sqlalchemy.orm import relationship

class Taller(Base):
    __tablename__ = "taller"

    # Campos existentes en tu imagen
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    id_propietario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Nuevos atributos para la lógica de emergencias
    telefono = Column(String, nullable=True)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    especialidad = Column(String, nullable=True)
    capacidad_vehiculos = Column(Integer, default=1)
    estado_activo = Column(Boolean, default=True)

    # Relación bidireccional con el modelo Tecnico
    tecnicos_asignados = relationship("models.tecnico.Tecnico", back_populates="taller")