from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from models.database import Base

class Repuesto(Base):
    __tablename__ = 'repuesto'

    id_repuesto = Column(Integer, primary_key=True, index=True, autoincrement=True )
    id_taller = Column(Integer, ForeignKey("taller.id_taller", ondelete="CASCADE"), nullable=False)
    
    nombre = Column(String(100), nullable=False)
    cantidad = Column(Integer, nullable=False, default=0)
    stock_minimo = Column(Integer, nullable=False, default=5)
    precio = Column(Numeric(10, 2), nullable=False)

    taller = relationship("Taller", back_populates="repuestos")
