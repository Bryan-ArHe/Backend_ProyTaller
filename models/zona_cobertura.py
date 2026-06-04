from sqlalchemy import Column, Integer, String, Boolean
from geoalchemy2 import Geometry
from models.database import Base

class ZonaCobertura(Base):
    __tablename__ = 'zonas_cobertura'
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    estado = Column(Boolean, default=True)
    # Especificamos geometry_type y srid=4326 (que es el estándar GPS para latitud/longitud)
    poligono_area = Column(Geometry(geometry_type='POLYGON', srid=4326), nullable=False)