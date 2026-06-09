# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import Column, Float, Integer, String, DateTime, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from models.database import Base
import enum

# 1. Tabla de asociación para permisos (Match perfecto con tu BD)
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
    id_taller_asignado = Column(Integer, ForeignKey("taller.id_taller"), nullable=True)
    
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    telefono = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    estado_cuenta = Column(Enum(EstadoCuenta), default=EstadoCuenta.ACTIVO, native_enum=False)
    # Cambiado a datetime.utcnow sin los paréntesis () para que se ejecute en caliente al insertar
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    # --- RELACIONES DE CONTROL Y SEGURIDAD ---
    rol = relationship("Rol", back_populates="usuarios")
    bitacoras = relationship("Bitacora", back_populates="usuario", cascade="all, delete-orphan")
    
    # --- RELACIONES DE HERENCIA 1:1 (Sincronizadas con uselist=False) ---
    cliente = relationship("Cliente", back_populates="usuario", uselist=False)
    tecnico = relationship("Tecnico", back_populates="usuario", uselist=False)
    gestor_taller = relationship("GestorTaller", back_populates="usuario", uselist=False)
    suscripciones = relationship("SuscripcionTaller", back_populates="superAdministrador")

    def __repr__(self):
        return f"<Usuario(email='{self.email}', rol='{self.id_rol}')>"
    

class PlanSaas(Base):
    __tablename__ = "plan_saas"

    id_plan = Column(Integer, primary_key=True, index=True)
    nombre_plan = Column(String(100), nullable=False, unique=True)
    precio_mensual = Column(Float, nullable=False)
    limite_talleres = Column(Integer, nullable=False)
    limite_tecnicos = Column(Integer, nullable=False)

    # Relación inversa hacia las suscripciones
    suscripciones = relationship("SuscripcionTaller", back_populates="plan")


class SuscripcionTaller(Base):
    __tablename__ = "suscripcion_taller"

    id_suscripcion = Column(Integer, primary_key=True, index=True)
    # 🌟 La relación va directo al Administrador (Dueño corporativo)
    id_usuario_admin = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), nullable=False)
    id_plan = Column(Integer, ForeignKey("plan_saas.id_plan"), nullable=False)
    
    fecha_inicio = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    estado_suscripcion = Column(String(50), default="Activo", nullable=False) # Activo, Vencido, Suspendido

    # Relaciones anidadas
    plan = relationship("PlanSaas", back_populates="suscripciones")
    superAdministrador = relationship("Usuario", back_populates="suscripciones")