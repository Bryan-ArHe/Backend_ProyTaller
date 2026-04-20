"""
models/user.py - Modelos SQLAlchemy para Rol y Usuario
Define la estructura de las tablas en la base de datos
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Table, Boolean
from sqlalchemy.orm import relationship
from models.database import Base
import enum

# Evitar circular imports - estos se importan al final del archivo
# para que las relaciones puedan resolverse correctamente

# Tabla de asociación many-to-many entre Rol y Permiso
rol_permisos = Table(
    'rol_permiso',
    Base.metadata,
    Column('id_rol', Integer, ForeignKey('rol.id_rol'), primary_key=True),
    Column('id_permiso', Integer, ForeignKey('permiso.id_permiso'), primary_key=True)
)


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
    __tablename__ = "rol"
    
    id_rol = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False, index=True)
    descripcion = Column(String(255), nullable=True)
    
    # Relación con usuarios
    usuarios = relationship("Usuario", back_populates="rol")
    # Relación many-to-many con permisos
    permisos = relationship("Permiso", secondary=rol_permisos, back_populates="roles")
    
    def __repr__(self):
        return f"<Rol(id={self.id}, nombre='{self.nombre}')>"


class Permiso(Base):
    """
    Modelo Permiso - Representa los permisos del sistema
    Los permisos se asignan a roles, y los usuarios heredan los permisos de su rol
    
    Atributos:
        id: Identificador único del permiso
        nombre: Nombre del permiso (ej: "crear_incidente", "ver_usuarios", "editar_rol")
        descripcion: Descripción detallada del permiso
        recurso: Recurso sobre el cual actúa el permiso (ej: "incidente", "usuario", "rol")
        accion: Acción permitida (ej: "crear", "leer", "actualizar", "eliminar")
    """
    __tablename__ = "permiso"
    
    id_permiso = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False, index=True)
    descripcion = Column(String(255), nullable=True)
    recurso = Column(String(50), nullable=False, index=True)  # ej: "incidente", "usuario", "vehiculo"
    accion = Column(String(50), nullable=False)  # ej: "crear", "leer", "actualizar", "eliminar"
    
    # Relación many-to-many con roles
    roles = relationship("Rol", secondary=rol_permisos, back_populates="permisos")
    
    def __repr__(self):
        return f"<Permiso(id={self.id}, nombre='{self.nombre}', recurso='{self.recurso}', accion='{self.accion}')>"


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
    __tablename__ = "usuario"
    
    id_usuario = Column(Integer, primary_key=True, index=True)
    id_rol = Column(Integer, ForeignKey("rol.id_rol"), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    telefono = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    estado_cuenta = Column(Enum(EstadoCuenta), default=EstadoCuenta.ACTIVO, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    rol = relationship("Rol", back_populates="usuarios")
    cliente = relationship("Cliente", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    gestor_taller = relationship("GestorTaller", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    tecnico = relationship("Tecnico", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    notificaciones = relationship("NotificacionPush", back_populates="usuario", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, email='{self.email}', estado={self.estado_cuenta})>"


class Cliente(Base):
    """
    Modelo Cliente - Usuario final que reporta emergencias vehiculares
    Hereda de Usuario (relación 1-a-1)
    
    Atributos:
        id: Identificador único del cliente
        id_usuario: Clave foránea única a Usuario
        nombres: Nombres del cliente
        apellidos: Apellidos del cliente
        ci: Cédula de identidad única
    """
    __tablename__ = "cliente"
    
    id_cliente = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    ci = Column(String(20), unique=True, nullable=False, index=True)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="cliente")
    vehiculos = relationship("Vehiculo", back_populates="cliente", cascade="all, delete-orphan")
    incidentes = relationship("Incidente", back_populates="cliente", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Cliente(id={self.id}, nombres='{self.nombres}', ci='{self.ci}')>"


class GestorTaller(Base):
    """
    Modelo GestorTaller - Responsable administrativo de un taller
    Hereda de Usuario (relación 1-a-1)
    
    Atributos:
        id: Identificador único del gestor/taller
        id_usuario: Clave foránea única a Usuario
        razon_social: Nombre comercial del taller
        nit: NIT único del taller
        direccion: Dirección de ubicación del taller
    """
    __tablename__ = "gestores_taller"
    
    id_taller = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    razon_social = Column(String(150), nullable=False)
    nit = Column(String(30), unique=True, nullable=False, index=True)
    direccion = Column(String(250), nullable=False)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="gestor_taller")
    tecnicos = relationship("Tecnico", back_populates="gestor_taller", cascade="all, delete-orphan")
    repuestos = relationship("Repuesto", back_populates="gestor_taller", cascade="all, delete-orphan")
    asignaciones_candidato = relationship("AsignacionCandidato", back_populates="gestor_taller")
    
    def __repr__(self):
        return f"<GestorTaller(id={self.id}, razon_social='{self.razon_social}', nit='{self.nit}')>"


class Tecnico(Base):
    """
    Modelo Técnico - Operador en campo que atiende emergencias
    Hereda de Usuario (relación 1-a-1)
    Pertenece a un GestorTaller (relación muchos-a-1)
    
    Atributos:
        id: Identificador único del técnico
        id_usuario: Clave foránea única a Usuario
        id_taller: Clave foránea al gestor/taller al que pertenece
        nombres: Nombres del técnico
        especialidad: Especialidad técnica (ej: electricidad, mecánica, etc.)
        esta_disponible: Flag que indica si está disponible para asignaciones
    """
    __tablename__ = "tecnico"
    
    id_tecnico = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    id_taller = Column(Integer, ForeignKey("gestores_taller.id_taller"), nullable=True, index=True)
    nombres = Column(String(150), nullable=False)
    especialidad = Column(String(100), nullable=True)
    esta_disponible = Column(Integer, default=1, nullable=False)  # 1=True, 0=False para SQL Server
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="tecnico")
    gestor_taller = relationship("GestorTaller", back_populates="tecnicos")
    solicitudes_servicio = relationship("SolicitudServicio", back_populates="tecnico")
    ubicaciones_tracking = relationship("UbicacionTracking", back_populates="tecnico", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tecnico(id={self.id}, nombres='{self.nombres}', especialidad='{self.especialidad}')>"


class NotificacionPush(Base):
    """
    Modelo NotificacionPush - Notificaciones enviadas a usuarios
    
    Atributos:
        id: Identificador único de la notificación
        id_usuario: Clave foránea al usuario destino
        titulo: Título de la notificación
        cuerpo: Contenido de la notificación
        es_leida: Flag que indica si fue leída
        fecha_envio: Fecha y hora del envío
    """
    __tablename__ = "notificaciones_push"
    
    id_notificacion = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), nullable=False, index=True)
    titulo = Column(String(150), nullable=False)
    cuerpo = Column(String(1000), nullable=False)
    es_leida = Column(Integer, default=0, nullable=False)  # 1=True, 0=False para SQL Server
    fecha_envio = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="notificaciones")
    
    def __repr__(self):
        return f"<NotificacionPush(id={self.id}, usuario_id={self.id_usuario}, leida={self.es_leida})>"


# Importar al final para resolver relaciones sin circular imports
from models.vehiculo import Vehiculo  # noqa: E402, F401
from models.incidente import Incidente  # noqa: E402, F401
