from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from models.database import Base
from datetime import datetime

class Bitacora(Base):
    __tablename__ = "bitacora"

    id_bitacora = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    nombre_usuario = Column(String(50), nullable=False)
    evento = Column(String(20), nullable=False)
    recurso = Column(String(50), nullable=False)
    accion = Column(String(255), nullable=False)
    ip = Column(String(50), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow, index=True)
    dispositivo = Column(String(10), nullable=True)

    usuario = relationship("models.user.Usuario", back_populates="bitacoras")
    def __repr__(self):
        return f"<Bitacora(id={self.id_bitacora}, accion='{self.accion}', usuario={self.id_usuario})>"