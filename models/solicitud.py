from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from models.database import Base # Usamos tu Base compartida

class EstadoSolicitud(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    RESUELTO = "RESUELTO"
    CANCELADO = "CANCELADO"

class SolicitudServicio(Base):
    __tablename__ = "solicitud_servicio"

    id_solicitud = Column(Integer, primary_key=True, index=True)
    codigo_orden = Column(String, unique=True, index=True, nullable=False)
    
    # Llaves foráneas
    incidente_id = Column(Integer, ForeignKey("incidente.id_incidente", ondelete="CASCADE"), nullable=False)
    tecnico_id = Column(Integer, ForeignKey("tecnico.id_tecnico", ondelete="RESTRICT"), nullable=False)
    taller_id = Column(Integer, ForeignKey("taller.id_taller", ondelete="SET NULL"), nullable=True)
    
    # Campos de control de estado y negocio
    estado = Column(SQLEnum(EstadoSolicitud), default=EstadoSolicitud.PENDIENTE, nullable=False)
    descripcion_trabajo = Column(String, nullable=True)
    observaciones_tecnicas = Column(String, nullable=True)
    
    # Tiempos
    fecha_asignacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_finalizacion = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # --- RELACIONES RELACIONALES (Para cargas anidadas/lazy loading) ---
    incidente = relationship("Incidente", back_populates="solicitud")
    tecnico = relationship("Tecnico", back_populates="solicitudes_servicio")
    taller = relationship("Taller", back_populates="solicitudes")

    def __repr__(self):
        return f"<SolicitudServicio(id={self.id_solicitud}, codigo={self.codigo_orden}, estado={self.estado})>"