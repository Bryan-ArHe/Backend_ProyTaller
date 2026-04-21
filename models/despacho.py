"""
models/despacho.py - Modelos para Asignación, Despacho y Gestión de Servicios
Gestión de solicitudes de servicio, asignaciones, inventario y seguimiento
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Numeric, DECIMAL
from sqlalchemy.orm import relationship
from models.database import Base
from datetime import datetime


class AsignacionCandidato(Base):
    """
    Modelo AsignacionCandidato - Candidatos de talleres para un incidente
    Algoritmo calcula mejores candidatos por distancia y capacidad
    
    Atributos:
        id: Identificador único
        id_incidente: Clave foránea al incidente
        id_taller: Clave foránea al gestor/taller candidato
        distancia_estimada_km: Distancia estimada en km
        score_ia: Puntuación algorítmica del candidato
        es_seleccionado: Flag si fue seleccionado
    """
    __tablename__ = "asignacion_candidato"
    
    id_candidato = Column(Integer, primary_key=True, index=True)
    id_incidente = Column(Integer, ForeignKey("incidente.id_incidente", ondelete="CASCADE"), nullable=False, index=True)
    id_taller = Column(Integer, ForeignKey("gestores_taller.id_taller"), nullable=False, index=True)
    
    distancia_estimada_km = Column(Numeric(8, 2), nullable=True)
    score_ia = Column(Numeric(8, 4), nullable=True)
    es_seleccionado = Column(Integer, default=0, nullable=False)
    
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    incidente = relationship("Incidente", back_populates="asignaciones_candidato")
    gestor_taller = relationship("GestorTaller", back_populates="asignaciones_candidato")
    
    def __repr__(self):
        return f"<AsignacionCandidato(id={self.id}, taller_id={self.id_taller}, score={self.score_ia})>"


class SolicitudServicio(Base):
    """
    Modelo SolicitudServicio - Orden de trabajo asignada a un técnico
    Vincula incidente con técnico específico
    
    Atributos:
        id: Identificador único
        id_incidente: Clave foránea única al incidente
        id_tecnico: Clave foránea al técnico asignado
        fecha_asignacion: Fecha de asignación
        fecha_llegada_estimada: ETA calculada
        fecha_finalizacion: Fecha de cierre del servicio
    """
    __tablename__ = "solicitud_servicio"
    
    id_solicitud = Column(Integer, primary_key=True, index=True)
    id_incidente = Column(Integer, ForeignKey("incidente.id_incidente"), unique=True, nullable=False, index=True)
    id_tecnico = Column(Integer, ForeignKey("tecnico.id_tecnico"), nullable=False, index=True)
    
    fecha_asignacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_llegada_estimada = Column(DateTime, nullable=True)
    fecha_finalizacion = Column(DateTime, nullable=True)
    
    # Relaciones
    incidente = relationship("Incidente", back_populates="solicitud_servicio")
    tecnico = relationship("Tecnico", back_populates="solicitudes_servicio")
    detalles_servicio = relationship("DetalleServicio", back_populates="solicitud", cascade="all, delete-orphan")
    pago = relationship("Pago", back_populates="solicitud", uselist=False)
    calificacion = relationship("Calificacion", back_populates="solicitud", uselist=False)
    mensajes = relationship("MensajeInApp", back_populates="solicitud_servicio", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SolicitudServicio(id={self.id}, tecnico_id={self.id_tecnico}, incidente_id={self.id_incidente})>"


class Repuesto(Base):
    """
    Modelo Repuesto - Inventario de repuestos en el taller
    
    Atributos:
        id: Identificador único
        id_taller: Clave foránea al gestor/taller propietario
        nombre: Nombre del repuesto
        cantidad: Cantidad disponible
        precio: Precio unitario
    """
    __tablename__ = "repuesto"
    
    id_repuesto = Column(Integer, primary_key=True, index=True)
    id_taller = Column(Integer, ForeignKey("gestores_taller.id_taller", ondelete="CASCADE"), nullable=False, index=True)
    
    nombre = Column(String(150), nullable=False)
    cantidad = Column(Integer, default=0, nullable=False)
    precio = Column(Numeric(12, 2), nullable=False)
    
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    gestor_taller = relationship("GestorTaller", back_populates="repuestos")
    detalles_servicio = relationship("DetalleServicio", back_populates="repuesto")
    
    def __repr__(self):
        return f"<Repuesto(id={self.id}, nombre='{self.nombre}', cantidad={self.cantidad})>"


class DetalleServicio(Base):
    """
    Modelo DetalleServicio - Repuestos utilizados en un servicio
    Registro de consumo de inventario por servicio
    
    Atributos:
        id: Identificador único
        id_solicitud: Clave foránea a la solicitud de servicio
        id_repuesto: Clave foránea al repuesto utilizado
        cantidad_consumida: Cantidad de unidades consumidas
        subtotal_repuesto: Costo total de este repuesto
    """
    __tablename__ = "detalle_servicio"
    
    id_detalle = Column(Integer, primary_key=True, index=True)
    id_solicitud = Column(Integer, ForeignKey("solicitud_servicio.id_solicitud", ondelete="CASCADE"), nullable=False, index=True)
    id_repuesto = Column(Integer, ForeignKey("repuesto.id_repuesto"), nullable=False, index=True)
    
    cantidad_consumida = Column(Integer, nullable=False)
    subtotal_repuesto = Column(Numeric(12, 2), nullable=False)
    
    # Relaciones
    solicitud = relationship("SolicitudServicio", back_populates="detalles_servicio")
    repuesto = relationship("Repuesto", back_populates="detalles_servicio")
    
    def __repr__(self):
        return f"<DetalleServicio(id={self.id}, solicitud_id={self.id_solicitud}, repuesto_id={self.id_repuesto})>"


class UbicacionTracking(Base):
    """
    Modelo UbicacionTracking - Ubicación en tiempo real del técnico
    Permite ETA dinámico y seguimiento del servicio
    
    Atributos:
        id: Identificador único
        id_tecnico: Clave foránea al técnico
        latitud: Coordenada de latitud GPS
        longitud: Coordenada de longitud GPS
        fecha_hora: Timestamp del registro
    """
    __tablename__ = "ubicacion_tracking"
    
    id_tracking = Column(Integer, primary_key=True, index=True)
    id_tecnico = Column(Integer, ForeignKey("tecnico.id_tecnico", ondelete="CASCADE"), nullable=False, index=True)
    
    latitud = Column(Numeric(10, 7), nullable=False)
    longitud = Column(Numeric(10, 7), nullable=False)
    fecha_hora = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relaciones
    tecnico = relationship("Tecnico", back_populates="ubicaciones_tracking")
    
    def __repr__(self):
        return f"<UbicacionTracking(id={self.id}, tecnico_id={self.id_tecnico}, fecha={self.fecha_hora})>"


class Pago(Base):
    """
    Modelo Pago - Registro de pagos por servicios
    Gestión financiera de transacciones
    
    Atributos:
        id: Identificador único
        id_solicitud: Clave foránea única a solicitud de servicio
        monto_subtotal: Subtotal antes de comisión
        monto_total: Total incluyendo comisión
        metodo_pago: Método utilizado (tarjeta, efectivo, QR, etc.)
        estado_transaccion: Estado del pago (PENDIENTE, COMPLETADO, RECHAZADO)
    """
    __tablename__ = "pago"
    
    id_pago = Column(Integer, primary_key=True, index=True)
    id_solicitud = Column(Integer, ForeignKey("solicitud_servicio.id_solicitud", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    monto_subtotal = Column(Numeric(12, 2), nullable=False)
    monto_total = Column(Numeric(12, 2), nullable=False)
    metodo_pago = Column(String(50), nullable=True)
    estado_transaccion = Column(String(30), default="PENDIENTE", nullable=False)
    
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_pago = Column(DateTime, nullable=True)
    
    # Relaciones
    solicitud = relationship("SolicitudServicio", back_populates="pago")
    comision = relationship("Comision", back_populates="pago", uselist=False)
    
    def __repr__(self):
        return f"<Pago(id={self.id}, monto={self.monto_total}, estado={self.estado_transaccion})>"


class Comision(Base):
    """
    Modelo Comision - Comisión de la plataforma por servicio
    Cálculo automático de ingresos
    
    Atributos:
        id: Identificador único
        id_pago: Clave foránea única al pago
        porcentaje: Porcentaje de comisión
        monto: Monto de la comisión
    """
    __tablename__ = "comision"
    
    id_comision = Column(Integer, primary_key=True, index=True)
    id_pago = Column(Integer, ForeignKey("pago.id_pago", ondelete="CASCADE"), unique=True, nullable=False)
    
    porcentaje = Column(Numeric(5, 2), nullable=False)
    monto = Column(Numeric(12, 2), nullable=False)
    
    # Relaciones
    pago = relationship("Pago", back_populates="comision")
    
    def __repr__(self):
        return f"<Comision(id={self.id}, porcentaje={self.porcentaje}%, monto={self.monto})>"


class Calificacion(Base):
    """
    Modelo Calificacion - Evaluación del cliente sobre el servicio
    Reseñas y puntuaciones de satisfacción
    
    Atributos:
        id: Identificador único
        id_solicitud: Clave foránea única a solicitud de servicio
        puntuacion: Puntuación de 1 a 5 estrellas
        resena: Texto de la reseña
    """
    __tablename__ = "calificacion"
    
    id_calificacion = Column(Integer, primary_key=True, index=True)
    id_solicitud = Column(Integer, ForeignKey("solicitud_servicio.id_solicitud", ondelete="CASCADE"), unique=True, nullable=False)
    
    puntuacion = Column(Integer, nullable=False)  # 1-5
    resena = Column(String(1000), nullable=True)
    
    fecha_calificacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    solicitud = relationship("SolicitudServicio", back_populates="calificacion")
    
    def __repr__(self):
        return f"<Calificacion(id={self.id}, puntuacion={self.puntuacion})>"
