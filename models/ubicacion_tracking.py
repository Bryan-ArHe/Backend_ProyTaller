# -*- coding: utf-8 -*-
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.database import Base

class UbicacionTracking(Base):
    __tablename__ = "ubicacion_tracking"

    id_tracking = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_tecnico = Column(Integer, ForeignKey("tecnico.id_tecnico", ondelete="CASCADE"), nullable=False, index=True)
    
    # Punto geográfico nativo de PostGIS (Maneja lat/lon de forma eficiente en una sola columna)
    ubicacion = Column(Geometry("POINT", srid=4326), nullable=False)
    
    # Marca de tiempo exacta del envío de coordenadas
    fecha_hora = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relación inversa hacia el Técnico
    tecnico = relationship("Tecnico", back_populates="tracking_ubicaciones")