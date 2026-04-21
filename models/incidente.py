"""
models/incidente.py - Modelos para Incidentes, Evidencia y análisis con IA
Sistema de reporte de emergencias vehiculares con captura de evidencia y triaje automático
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Enum, Numeric
from sqlalchemy.orm import relationship
from models.database import Base
from datetime import datetime
import enum


class EstadoIncidente(str, enum.Enum):
    """Estados posibles de un incidente"""
    PENDIENTE = "PENDIENTE"
    EN_TRIAJE = "EN_TRIAJE"
    ASIGNADO = "ASIGNADO"
    EN_ATENCION = "EN_ATENCION"
    RESUELTO = "RESUELTO"
    CANCELADO = "CANCELADO"


class PrioridadIncidente(str, enum.Enum):
    """Niveles de prioridad asignados por el sistema de IA"""
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"


class TipoEvidencia(str, enum.Enum):
    """Tipos de evidencia multimedia soportados"""
    AUDIO = "AUDIO"
    FOTOGRAFIA = "FOTOGRAFIA"
    TEXTO = "TEXTO"


class Incidente(Base):
    """
    Modelo Incidente - Registro de emergencias vehiculares
    
    Atributos:
        id: Identificador único del incidente
        id_cliente: Clave foránea al cliente que reporta
        id_vehiculo: Clave foránea al vehículo involucrado
        fecha_incidente: Fecha y hora del incidente
        latitud: Coordenada de latitud GPS
        longitud: Coordenada de longitud GPS
        estado_incidente: Estado actual del incidente
    """
    __tablename__ = "incidente"
    
    id_incidente = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=True, index=True)
    id_vehiculo = Column(Integer, ForeignKey("vehiculo.id_vehiculo"), nullable=True, index=True)
    
    fecha_incidente = Column(DateTime, default=datetime.utcnow, nullable=False)
    latitud = Column(Numeric(10, 7), nullable=False)
    longitud = Column(Numeric(10, 7), nullable=False)
    estado_incidente = Column(String(30), default="PENDIENTE", nullable=False)
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="incidentes")
    vehiculo = relationship("Vehiculo", back_populates="incidentes")
    evidencias = relationship("Evidencia", back_populates="incidente", cascade="all, delete-orphan")
    triaje = relationship("TriajeIA", back_populates="incidente", uselist=False, cascade="all, delete-orphan")
    historial = relationship("HistorialIncidente", back_populates="incidente", cascade="all, delete-orphan")
    solicitud_servicio = relationship("SolicitudServicio", back_populates="incidente", uselist=False)
    asignaciones_candidato = relationship("AsignacionCandidato", back_populates="incidente", cascade="all, delete-orphan")

    
    def __repr__(self):
        return f"<Incidente(id={self.id}, estado={self.estado_incidente}, latitud={self.latitud}, longitud={self.longitud})>"


class Evidencia(Base):
    """
    Modelo Evidencia - Archivos multimedia asociados a un incidente
    Soporta audio, fotografías y texto
    
    Atributos:
        id: Identificador único de la evidencia
        id_incidente: Clave foránea al incidente
        tipo: Tipo de archivo (AUDIO, FOTOGRAFIA, TEXTO)
        url_archivo: URL del archivo almacenado
        tamano_mb: Tamaño del archivo en megabytes
        fecha_captura: Fecha de captura original
    """
    __tablename__ = "evidencia"
    
    id_evidencia = Column(Integer, primary_key=True, index=True)
    id_incidente = Column(Integer, ForeignKey("incidente.id_incidente", ondelete="CASCADE"), nullable=False, index=True)
    
    tipo = Column(String(20), nullable=False)  # AUDIO, FOTOGRAFIA, TEXTO
    url_archivo = Column(String(400), nullable=False)
    tamano_mb = Column(Numeric(8, 2), nullable=True)
    
    fecha_captura = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    incidente = relationship("Incidente", back_populates="evidencias")
    
    def __repr__(self):
        return f"<Evidencia(id={self.id}, id_incidente={self.id_incidente}, tipo={self.tipo})>"


class TriajeIA(Base):
    """
    Modelo TriajeIA - Análisis automático de incidentes por IA
    Contiene transcripción, análisis visual, categorización y prioridad
    
    Atributos:
        id: Identificador único del triaje
        id_incidente: Clave foránea única al incidente
        transcripcion_audio: Transcripción automática del audio
        analisis_visual: Análisis de imágenes enviadas
        categoria_sugerida: Categoría del problema sugerida
        nivel_prioridad: Nivel de prioridad (1-5)
        nivel_confianza: Confianza de la IA en el análisis (0-1)
    """
    __tablename__ = "triaje_ia"
    
    id_triaje = Column(Integer, primary_key=True, index=True)
    id_incidente = Column(Integer, ForeignKey("incidente.id_incidente", ondelete="CASCADE"), unique=True, nullable=False)
    
    transcripcion_audio = Column(String(2000), nullable=True)
    analisis_visual = Column(String(2000), nullable=True)
    categoria_sugerida = Column(String(80), nullable=True)
    nivel_prioridad = Column(Integer, nullable=True)
    nivel_confianza = Column(Numeric(5, 4), nullable=True)
    
    fecha_analisis = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    incidente = relationship("Incidente", back_populates="triaje")
    
    def __repr__(self):
        return f"<TriajeIA(id={self.id}, incidente_id={self.id_incidente}, prioridad={self.nivel_prioridad})>"


class HistorialIncidente(Base):
    """
    Modelo HistorialIncidente - Registro de cambios de estado del incidente
    Auditoría de todos los cambios realizados
    
    Atributos:
        id: Identificador único del registro
        id_incidente: Clave foránea al incidente
        estado_anterior: Estado previo
        estado_actual: Estado nuevo
        fecha_cambio: Fecha del cambio
    """
    __tablename__ = "historial_incidente"
    
    id_historial = Column(Integer, primary_key=True, index=True)
    id_incidente = Column(Integer, ForeignKey("incidente.id_incidente", ondelete="CASCADE"), nullable=False, index=True)
    
    estado_anterior = Column(String(30), nullable=True)
    estado_actual = Column(String(30), nullable=False)
    fecha_cambio = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    incidente = relationship("Incidente", back_populates="historial")
    
    def __repr__(self):
        return f"<HistorialIncidente(id={self.id}, incidente_id={self.id_incidente}, {self.estado_anterior}->{self.estado_actual})>"


class MensajeInApp(Base):
    """
    Modelo MensajeInApp - Comunicación entre cliente y técnico
    Chat seguro dentro de la aplicación durante la solicitud de servicio
    
    Atributos:
        id: Identificador único del mensaje
        id_solicitud: Clave foránea a la solicitud de servicio
        emisor: Quién envía el mensaje (CLIENTE, TECNICO)
        contenido: Contenido del mensaje
        fecha_envio: Fecha y hora de envío
    """
    __tablename__ = "mensaje_inapp"
    
    id_mensaje = Column(Integer, primary_key=True, index=True)
    id_solicitud = Column(Integer, ForeignKey("solicitud_servicio.id_solicitud", ondelete="CASCADE"), nullable=False, index=True)
    
    emisor = Column(String(30), nullable=False)  # CLIENTE, TECNICO
    contenido = Column(String(2000), nullable=False)
    fecha_envio = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    solicitud_servicio = relationship("SolicitudServicio", back_populates="mensajes")
    
    def __repr__(self):
        return f"<MensajeInApp(id={self.id}, emisor={self.emisor}, fecha={self.fecha_envio})>"
