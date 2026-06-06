from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Boolean
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from models.database import Base

class ZonaCobertura(Base):
    __tablename__ = 'zonas_cobertura'
    
    id_zona = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_taller = Column(Integer, ForeignKey("taller.id_taller", ondelete="CASCADE"), nullable=False)
    nombre_zona = Column(String(100), nullable=False)
    tarifa_desplazamiento = Column(Numeric(10, 2), nullable=False)

    # El polígono que define el área de cobertura de esta zona
    poligono_area = Column(Geometry("POLYGON", srid=4326), nullable=False)
    
    taller = relationship("Taller", back_populates="zona_cobertura")