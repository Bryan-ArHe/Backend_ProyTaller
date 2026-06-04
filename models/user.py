from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from models.database import Base
import enum

# 1. Tabla de asociación para permisos
rol_permisos = Table(
    'rol_permiso',
    Base.metadata,
    Column('id_rol', Integer, ForeignKey('rol.id_rol'), primary_key=True),
    Column('id_permiso', Integer, ForeignKey('permiso.id_permiso'), primary_key=True)
)

class EstadoCuenta(str, enum.Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"

class Rol(Base):
    __tablename__ = "rol"
    id_rol = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False, index=True)
    descripcion = Column(String(255), nullable=True)

    usuarios = relationship("Usuario", back_populates="rol")
    permisos = relationship("Permiso", secondary=rol_permisos, back_populates="roles")

class Permiso(Base):
    __tablename__ = "permiso"
    id_permiso = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(String(255), nullable=True)
    recurso = Column(String(50), nullable=False) # ej: "usuario", "vehiculo"
    accion = Column(String(50), nullable=False)  # ej: "crear", "leer", "actualizar"

    roles = relationship("Rol", secondary=rol_permisos, back_populates="permisos")

class Usuario(Base):
    __tablename__ = "usuario"
    
    id_usuario = Column(Integer, primary_key=True, index=True)
    id_rol = Column(Integer, ForeignKey("rol.id_rol"), nullable=False)
    
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    telefono = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    estado_cuenta = Column(Enum(EstadoCuenta), default=EstadoCuenta.ACTIVO)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    # --- RELACIONES DINÁMICAS (El secreto para evitar errores) ---
    rol = relationship("Rol", back_populates="usuarios")
    bitacoras = relationship("Bitacora", back_populates="usuario", cascade="all, delete-orphan")
    
    # Usamos lazy='dynamic' o el path completo para evitar bloqueos
    tecnico = relationship("Tecnico", back_populates="usuario", uselist=False)
    solicitudes_servicio = relationship("SolicitudServicio", back_populates="cliente")
    incidentes = relationship("Incidente", back_populates="cliente")

    def __repr__(self):
        return f"<Usuario(email='{self.email}', rol='{self.id_rol}')>"