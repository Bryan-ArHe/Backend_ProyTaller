from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.database import Base

class SolicitudServicio(Base):
    __tablename__ = "solicitud_servicio"

    id_solicitud = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # El cliente que reporta la emergencia
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), nullable=False, index=True)
    
    # El técnico que acudirá al rescate (Es nulo al principio hasta que el algoritmo o un humano lo asigne)
    id_tecnico = Column(Integer, ForeignKey("tecnico.id_tecnico"), nullable=True, index=True)

    # Detalles del incidente
    tipo_emergencia = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    evidencia_multimedia = Column(JSON, nullable=True) 

    # Coordenadas exactas del cliente varado
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    
    # Ciclo de vida de la emergencia (Pendiente, Asignada, En Curso, Resuelta, Cancelada)
    estado = Column(String(50), default="Pendiente", nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True) # Para medir tiempos de respuesta

    # --- Relaciones Bidireccionales ---
    cliente = relationship("models.user.Usuario", back_populates="solicitudes_servicio")
    tecnico = relationship("models.tecnico.Tecnico", back_populates="solicitudes_servicio")

    def __repr__(self):
        return f"<SolicitudServicio(id={self.id_solicitud}, tipo='{self.tipo_emergencia}', estado='{self.estado}')>"