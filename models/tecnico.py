# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.database import Base

class Tecnico(Base):
    __tablename__ = "tecnico"

    # CORRECCIÓN DE HERENCIA 1:1:
    # La PK es directamente el ID del usuario del cual hereda. Se elimina el id_usuario redundante.
    id_tecnico = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), primary_key=True, index=True)
    id_taller = Column(Integer, ForeignKey("taller.id_taller", ondelete="RESTRICT"), nullable=True, index=True)
    
    # Campos operativos (Normalizados: nombres y apellidos viven en la tabla usuario)
    especialidad = Column(String(100), nullable=True)
    estado_disponibilidad = Column(String, default="Libre")  # 'Libre', 'Ocupado', 'Inactivo'
    
    # Rastreo geográfico operativo para el despacho de emergencias
    latitud_actual = Column(Float, nullable=True)
    longitud_actual = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- Relaciones Sincronizadas ---
    # uselist=False asegura el comportamiento estricto de herencia 1:1 en Python
    usuario = relationship("Usuario", back_populates="tecnico", uselist=False)
    
    # CORRECCIÓN DE CRUCE: Sincronizado con property 'tecnicos' definida en models/taller.py
    taller = relationship("Taller", back_populates="tecnicos")
    
    # Sincronizado con property 'tecnico' en models/solicitud.py
    solicitudes_servicio = relationship("SolicitudServicio", back_populates="tecnico")

    def __repr__(self):
        return f"<Tecnico(id={self.id_tecnico}, especialidad='{self.especialidad}', estado='{self.estado_disponibilidad}')>"