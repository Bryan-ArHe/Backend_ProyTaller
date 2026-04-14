"""
models/user.py - Modelos SQLAlchemy para Rol y Usuario
Define la estructura de las tablas en la base de datos
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.database import Base
import enum


class EstadoCuenta(str, enum.Enum):
    """Estados posibles de una cuenta de usuario"""
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"


class Rol(Base):
    """
    Modelo Rol - Representa los roles/permisos de los usuarios
    
    Atributos:
        id: Identificador único del rol
        nombre: Nombre del rol (ej: "admin", "usuario", "operador")
        descripcion: Descripción detallada del rol
    """
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False, index=True)
    descripcion = Column(String(255), nullable=True)
    
    # Relación con usuarios
    usuarios = relationship("Usuario", back_populates="rol")
    
    def __repr__(self):
        return f"<Rol(id={self.id}, nombre='{self.nombre}')>"


class Usuario(Base):
    """
    Modelo Usuario - Representa a los usuarios del sistema
    
    Atributos:
        id: Identificador único del usuario
        id_rol: Clave foránea al rol del usuario
        email: Email único del usuario
        telefono: Número de teléfono de contacto
        password_hash: Contraseña hasheada con bcrypt (nunca se almacena en texto plano)
        estado_cuenta: Estado de la cuenta (ACTIVO o INACTIVO)
        fecha_registro: Fecha y hora de registro del usuario
    """
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    id_rol = Column(Integer, ForeignKey("roles.id"), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    telefono = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    estado_cuenta = Column(Enum(EstadoCuenta), default=EstadoCuenta.ACTIVO, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    rol = relationship("Rol", back_populates="usuarios")
    vehiculos = relationship("Vehiculo", back_populates="cliente", cascade="all, delete-orphan")
    incidentes = relationship("Incidente", back_populates="cliente", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, email='{self.email}', estado={self.estado_cuenta})>"
