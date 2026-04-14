"""
models/incidente.py - Modelos para Incidentes y Evidencia Multimedia
Sistema de reporte de emergencias vehiculares con captura de evidencia
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Enum
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
    FOTO = "FOTO"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    DOCUMENTO = "DOCUMENTO"


class Incidente(Base):
    """
    Modelo Incidente - Registro de emergencias vehiculares
    
    Atributos:
        id: Identificador único del incidente
        id_vehiculo: Clave foránea al vehículo involucrado
        id_cliente: Clave foránea al usuario who reported (cliente)
        descripcion: Descripción detallada del incidente
        estado: Estado actual del incidente
        prioridad: Prioridad asignada por el sistema de IA (BAJA, MEDIA, ALTA, CRITICA)
        ubicacion_lat: Latitud de la ubicación del incidente
        ubicacion_long: Longitud de la ubicación del incidente
        fecha_reporte: Fecha y hora del reporte
        fecha_actualizacion: Última fecha de actualización
    """
    __tablename__ = "incidentes"
    
    id = Column(Integer, primary_key=True, index=True)
    id_vehiculo = Column(Integer, ForeignKey("vehiculos.id"), nullable=False, index=True)
    id_cliente = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    
    descripcion = Column(Text, nullable=False)
    estado = Column(Enum(EstadoIncidente), default=EstadoIncidente.PENDIENTE, nullable=False)
    prioridad = Column(Enum(PrioridadIncidente), default=PrioridadIncidente.MEDIA, nullable=False)
    
    # Ubicación del incidente (GPS)
    ubicacion_lat = Column(Float, nullable=True)
    ubicacion_long = Column(Float, nullable=True)
    
    fecha_reporte = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    vehiculo = relationship("Vehiculo", back_populates="incidentes")
    cliente = relationship("Usuario", back_populates="incidentes")
    evidencias = relationship("Evidencia", back_populates="incidente", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Incidente(id={self.id}, vehiculo_id={self.id_vehiculo}, prioridad={self.prioridad}, estado={self.estado})>"


class Evidencia(Base):
    """
    Modelo Evidencia - Archivos multimedia asociados a un incidente
    Soporta fotos, videos, audios y documentos
    
    Atributos:
        id: Identificador único de la evidencia
        id_incidente: Clave foránea al incidente
        tipo: Tipo de archivo (FOTO, VIDEO, AUDIO, DOCUMENTO)
        url: URL del archivo almacenado (ej: en S3, storage local, etc.)
        tamano_bytes: Tamaño del archivo en bytes
        descripcion: Descripción opcional de la evidencia
        fecha_captura: Fecha y hora de la captura
        fecha_registro: Fecha de registro en el sistema
    """
    __tablename__ = "evidencias"
    
    id = Column(Integer, primary_key=True, index=True)
    id_incidente = Column(Integer, ForeignKey("incidentes.id"), nullable=False, index=True)
    
    tipo = Column(Enum(TipoEvidencia), nullable=False)
    url = Column(String(500), nullable=False)
    tamano_bytes = Column(Integer, nullable=True)
    descripcion = Column(String(300), nullable=True)
    
    fecha_captura = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    incidente = relationship("Incidente", back_populates="evidencias")
    
    def __repr__(self):
        return f"<Evidencia(id={self.id}, id_incidente={self.id_incidente}, tipo={self.tipo})>"
