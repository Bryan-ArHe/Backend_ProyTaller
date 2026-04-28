from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.database import Base

class Tecnico(Base):
    __tablename__ = "tecnicos"

    id_tecnico = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Llaves Foráneas
    # Vinculamos con 'usuario' (singular) e 'id_usuario' según tu DB
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Vinculamos con nuestra tabla de 'talleres'
    id_taller = Column(Integer, ForeignKey("talleres.id"), nullable=True, index=True)
    
    # Campos operativos
    # Nota: Quitamos 'nombres' de aquí porque ya existen en la tabla 'usuario' (Normalización)
    especialidad = Column(String(100), nullable=True)
    estado_disponibilidad = Column(String, default="Libre") # 'Libre', 'Ocupado', 'Inactivo'
    
    # Rastreo geográfico (Indispensable para el despacho de emergencias)
    latitud_actual = Column(Float, nullable=True)
    longitud_actual = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- Relaciones ---
    # Usamos rutas completas para evitar el error de 'Multiple classes'
    usuario = relationship("models.user.Usuario", back_populates="tecnico")
    taller = relationship("models.taller.Taller", back_populates="tecnicos_asignados")
    
    # Estas relaciones las usaremos en los siguientes módulos (Ciclo 2 y 3)
    #solicitudes_servicio = relationship("models.solicitud.SolicitudServicio", back_populates="tecnico")
    #ubicaciones_tracking = relationship("models.tracking.UbicacionTracking", back_populates="tecnico", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tecnico(id={self.id_tecnico}, especialidad='{self.especialidad}', estado='{self.estado_disponibilidad}')>"