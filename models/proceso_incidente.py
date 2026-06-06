# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.database import Base

class Cotizacion(Base):
    """
    Modelo Cotizacion - Gestión financiera del auxilio mecánico.
    Un incidente puede tener múltiples cotizaciones (ej. si se rechaza la primera por precio).
    """
    __tablename__ = "cotizacion"

    id_cotizacion = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # Relación de asociación (1 Incidente obligatorio)
    id_incidente = Column(Integer, ForeignKey("incidente.id_incidente", ondelete="RESTRICT"), nullable=False, index=True)
    
    # Estados: 'PENDIENTE', 'ACEPTADA', 'RECHAZADA', 'VENCIDA'
    estado_cotizacion = Column(String(30), default="PENDIENTE", nullable=False)
    
    # Manejo preciso de dinero con Numeric
    monto_estimado = Column(Numeric(10, 2), nullable=False, comment="Cálculo inicial automático del ERP")
    monto_presupuesto_taller = Column(Numeric(10, 2), nullable=True, comment="Monto final cargado por el taller/mecánico")
    
    # Sugerencias adicionales de valor financiero
    monto_repuestos = Column(Numeric(10, 2), nullable=True, default=0.00)
    monto_mano_obra = Column(Numeric(10, 2), nullable=True, default=0.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación inversa hacia Incidente
    incidente = relationship("Incidente", back_populates="cotizaciones")


class IncidenteAsignado(Base):
    """
    Modelo IncidenteAsignado - Mapea la COMPOSICIÓN con Incidente.
    Guarda los técnicos óptimos evaluados por PostGIS y la IA para un servicio.
    """
    __tablename__ = "incidente_asignado"

    id_asignado = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # FK obligatoria por relación de Composición estricta (Si muere el incidente, mueren sus candidatos)
    id_incidente = Column(Integer, ForeignKey("incidente.id_incidente", ondelete="CASCADE"), nullable=False, index=True)
    
    # Técnico evaluado como candidato
    id_tecnico = Column(Integer, ForeignKey("tecnico.id_tecnico", ondelete="RESTRICT"), nullable=False, index=True)
    
    # Atributos base solicitados
    distancia_estimada_km = Column(Numeric(6, 2), nullable=False, comment="Calculado mediante ST_DistanceSphere en PostGIS")
    es_seleccionado = Column(Boolean, default=False, nullable=False, comment="Verdadero si es el técnico que finalmente irá al auxilio")
    score_ia = Column(Numeric(5, 4), nullable=True, comment="Puntaje de compatibilidad asignado por el modelo de IA (0.0000 a 1.0000)")
    
    # Sugerencias añadidas para robustecer la asignación logística
    tiempo_estimado_minutos = Column(Integer, nullable=True, comment="ETA calculado en base a la distancia")
    motivo_rechazo = Column(String(255), nullable=True, comment="Por qué no fue seleccionado o por qué rechazó el técnico")
    evaluado_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones inversas
    incidente = relationship("Incidente", back_populates="asignados")
    tecnico = relationship("Tecnico", back_populates="asignaciones")