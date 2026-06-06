from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, DateTime, Enum as SQLEnum, func
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
    # 1. ATRIBUTO DE CONTROL MULTI-TENANT: Vive físicamente aquí para blindar la seguridad
    id_gestor = Column(Integer, ForeignKey("gestor_taller.id_gestor", ondelete="RESTRICT"), nullable=False, index=True)


    # Campos de control de estado y negocio
    estado = Column(SQLEnum(EstadoSolicitud), default=EstadoSolicitud.PENDIENTE, nullable=False)
    descripcion_trabajo = Column(String, nullable=True)
    observaciones_tecnicas = Column(String, nullable=True)

    # Atributos financieros detallados para un control exhaustivo del servicio
    total_mano_obra = Column(Numeric(10, 2), nullable=False, default=0.00)
    total_repuestos = Column(Numeric(10, 2), nullable=False, default=0.00)
    total_general = Column(Numeric(10, 2), nullable=False, default=0.00)
    
    # Tiempos
    fecha_asignacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_finalizacion = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # --- RELACIONES RELACIONALES (Para cargas anidadas/lazy loading) ---
    incidente = relationship("Incidente", back_populates="solicitud")
    tecnico = relationship("Tecnico", back_populates="solicitudes_servicio")
    taller = relationship("Taller", back_populates="solicitudes")

    # Relación de Composición: Limpieza automática de líneas de detalle en cascada
    detalles_repuestos = relationship(
        "DetalleServicio", 
        back_populates="solicitud", 
        cascade="all, delete-orphan"
    )

    # Relación de Composición: Si muere la solicitud, mueren sus mensajes in-app relacionados
    mensajes_inapp = relationship(
        "MensajeInApp", 
        back_populates="solicitud", 
        cascade="all, delete-orphan"
    )

    # Relación de Composición: Si muere la solicitud, muere su calificación relacionada
    calificacion = relationship(
        "Calificacion", 
        back_populates="solicitud",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<SolicitudServicio(id={self.id_solicitud}, codigo={self.codigo_orden}, estado={self.estado})>"
    
class DetalleServicio(Base):
    """
    Entidad Componente: DetalleServicio (Las líneas de la Orden)
    Tabla intermedia que rompe el Muchos a Muchos entre Solicitud y Repuesto.
    """
    __tablename__ = "detalle_servicio"

    id_detalle = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Llaves foráneas del Muchos a Muchos
    id_solicitud = Column(Integer, ForeignKey("solicitud_servicio.id_solicitud", ondelete="CASCADE"), nullable=False, index=True)
    id_repuesto = Column(Integer, ForeignKey("repuesto.id_repuesto", ondelete="RESTRICT"), nullable=False, index=True)

    # Atributos transaccionales
    cantidad_consumida = Column(Integer, nullable=False, default=1)
    subtotal_repuesto = Column(Numeric(10, 2), nullable=False, comment="(cantidad * precio_unitario) - descuento")
    
    estado_entrega = Column(String(30), default="USADO", nullable=False) # 'SOLICITADO', 'USADO', 'DEVUELTO'

    # --- RELACIONES SINCRONIZADAS ---
    solicitud = relationship("SolicitudServicio", back_populates="detalles_repuestos")
    repuesto = relationship("Repuesto")

    def __repr__(self):
        return f"<DetalleServicio(id={self.id_detalle}, solicitud_id={self.id_solicitud}, repuesto_id={self.id_repuesto}, cant={self.cantidad_consumida})>"

class MensajeInApp(Base):
    """
    Modelo MensajeInApp - Comunicación segura (Chat) entre Cliente y Técnico
    durante la ejecución de una solicitud de servicio.
    """
    __tablename__ = "mensaje_inapp"
    
    id_mensaje = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Composición estricta: Si se elimina la solicitud de auxilio, el chat se borra en cascada
    id_solicitud = Column(Integer, ForeignKey("solicitud_servicio.id_solicitud", ondelete="CASCADE"), nullable=False, index=True)
    
    emisor = Column(String(30), nullable=False)  # 'CLIENTE' o 'TECNICO'
    contenido = Column(String(2000), nullable=False)
    fecha_envio = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # --- Relación Bidireccional Sincronizada ---
    solicitud = relationship("SolicitudServicio", back_populates="mensajes_inapp")
    
    def __repr__(self):
        # Comillas simples agregadas en emisor para un debug más limpio en consola
        return f"<MensajeInApp(id={self.id_mensaje}, emisor='{self.emisor}', fecha={self.fecha_envio})>"
    
class Calificacion(Base):
    """
    Modelo Calificacion - Feedback del cliente sobre el servicio recibido.
    Composición estricta: Si se elimina la solicitud, se elimina la calificación.
    """
    __tablename__ = "calificacion"

    id_calificacion = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Composición estricta: Si se elimina la solicitud de auxilio, la calificación se borra en cascada
    id_solicitud = Column(Integer, ForeignKey("solicitud_servicio.id_solicitud", ondelete="CASCADE"), nullable=False, index=True)
    
    puntaje = Column(Integer, nullable=False)  # 1 a 5
    comentario = Column(String(1000), nullable=True)
    fecha_calificacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # --- Relación Bidireccional Sincronizada ---
    solicitud = relationship("SolicitudServicio", back_populates="calificacion")

    def __repr__(self):
        return f"<Calificacion(id={self.id_calificacion}, puntaje={self.puntaje}, fecha={self.fecha_calificacion})>"