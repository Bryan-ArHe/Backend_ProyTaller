# -*- coding: utf-8 -*-
import sys
from sqlalchemy import text
from models.database import SessionLocal, engine, Base
from models.user import Usuario, Rol, Permiso, EstadoCuenta, Cliente, GestorTaller, Tecnico
from models.vehiculo import Vehiculo
from models.incidente import Incidente, Evidencia, TriajeIA, HistorialIncidente, MensajeInApp
from models.despacho import SolicitudServicio, AsignacionCandidato, Repuesto, DetalleServicio, UbicacionTracking, Pago, Comision, Calificacion
from security.password import hash_password

def reset_database():
    print('Eliminando todas las tablas...')
    # Eliminar con CASCADE para quitar tipos ENUM y dependencias
    with engine.connect() as conn:
        pass # Original line modified
        pass
        pass
    Base.metadata.drop_all(bind=engine)
    print('Tablas eliminadas')
    print('Creando nuevas tablas...')
    Base.metadata.create_all(bind=engine)
    print('Tablas creadas')

def create_test_data():
    db = SessionLocal()
    try:
        print('Creando roles...')
        roles = [Rol(nombre='admin', descripcion='Administrador'), Rol(nombre='tecnico', descripcion='Tecnico'), Rol(nombre='cliente', descripcion='Cliente'), Rol(nombre='gestor_taller', descripcion='Gestor')]
        for r in roles: db.add(r)
        db.commit()
        
        # Obtener IDs de roles
        admin_rol = db.query(Rol).filter(Rol.nombre == 'admin').first()
        tecnico_rol = db.query(Rol).filter(Rol.nombre == 'tecnico').first()
        cliente_rol = db.query(Rol).filter(Rol.nombre == 'cliente').first()
        gestor_rol = db.query(Rol).filter(Rol.nombre == 'gestor_taller').first()
        
        print('Creando permisos...')
        permisos = [
            # ========== USUARIOS ==========
            Permiso(nombre='crear_usuario', descripcion='Crear nuevo usuario', recurso='usuario', accion='crear'),
            Permiso(nombre='leer_usuario', descripcion='Ver detalles del usuario', recurso='usuario', accion='leer'),
            Permiso(nombre='actualizar_usuario', descripcion='Actualizar datos del usuario', recurso='usuario', accion='actualizar'),
            Permiso(nombre='eliminar_usuario', descripcion='Eliminar usuario', recurso='usuario', accion='eliminar'),
            Permiso(nombre='cambiar_rol_usuario', descripcion='Cambiar rol de un usuario', recurso='usuario', accion='cambiar_rol'),
            Permiso(nombre='cambiar_estado_usuario', descripcion='Cambiar estado (ACTIVO/INACTIVO) de usuario', recurso='usuario', accion='cambiar_estado'),
            Permiso(nombre='listar_usuarios', descripcion='Listar todos los usuarios del sistema', recurso='usuario', accion='listar'),
            
            # ========== ROLES ==========
            Permiso(nombre='crear_rol', descripcion='Crear nuevo rol', recurso='rol', accion='crear'),
            Permiso(nombre='leer_rol', descripcion='Ver detalles del rol', recurso='rol', accion='leer'),
            Permiso(nombre='actualizar_rol', descripcion='Actualizar rol', recurso='rol', accion='actualizar'),
            Permiso(nombre='eliminar_rol', descripcion='Eliminar rol', recurso='rol', accion='eliminar'),
            Permiso(nombre='gestionar_rol', descripcion='Gestionar roles del sistema', recurso='rol', accion='gestionar'),
            
            # ========== PERMISOS ==========
            Permiso(nombre='crear_permiso', descripcion='Crear nuevo permiso', recurso='permiso', accion='crear'),
            Permiso(nombre='leer_permiso', descripcion='Ver detalles del permiso', recurso='permiso', accion='leer'),
            Permiso(nombre='actualizar_permiso', descripcion='Actualizar permiso', recurso='permiso', accion='actualizar'),
            Permiso(nombre='eliminar_permiso', descripcion='Eliminar permiso', recurso='permiso', accion='eliminar'),
            Permiso(nombre='gestionar_permiso', descripcion='Gestionar permisos del sistema', recurso='permiso', accion='gestionar'),
            
            # ========== VEHÍCULOS ==========
            Permiso(nombre='crear_vehiculo', descripcion='Registrar nuevo vehículo', recurso='vehiculo', accion='crear'),
            Permiso(nombre='leer_vehiculo', descripcion='Ver detalles del vehículo', recurso='vehiculo', accion='leer'),
            Permiso(nombre='actualizar_vehiculo', descripcion='Actualizar información del vehículo', recurso='vehiculo', accion='actualizar'),
            Permiso(nombre='eliminar_vehiculo', descripcion='Eliminar vehículo', recurso='vehiculo', accion='eliminar'),
            Permiso(nombre='listar_vehiculos', descripcion='Listar vehículos', recurso='vehiculo', accion='listar'),
            
            # ========== MARCAS Y MODELOS ==========
            Permiso(nombre='crear_marca', descripcion='Crear nueva marca de vehículo', recurso='marca', accion='crear'),
            Permiso(nombre='leer_marca', descripcion='Ver detalles de marca', recurso='marca', accion='leer'),
            Permiso(nombre='actualizar_marca', descripcion='Actualizar marca', recurso='marca', accion='actualizar'),
            Permiso(nombre='eliminar_marca', descripcion='Eliminar marca', recurso='marca', accion='eliminar'),
            Permiso(nombre='crear_modelo', descripcion='Crear nuevo modelo de vehículo', recurso='modelo', accion='crear'),
            Permiso(nombre='leer_modelo', descripcion='Ver detalles del modelo', recurso='modelo', accion='leer'),
            Permiso(nombre='actualizar_modelo', descripcion='Actualizar modelo', recurso='modelo', accion='actualizar'),
            Permiso(nombre='eliminar_modelo', descripcion='Eliminar modelo', recurso='modelo', accion='eliminar'),
            
            # ========== INCIDENTES ==========
            Permiso(nombre='crear_incidente', descripcion='Crear nuevo incidente/emergencia', recurso='incidente', accion='crear'),
            Permiso(nombre='leer_incidente', descripcion='Ver detalles del incidente', recurso='incidente', accion='leer'),
            Permiso(nombre='actualizar_incidente', descripcion='Actualizar incidente', recurso='incidente', accion='actualizar'),
            Permiso(nombre='eliminar_incidente', descripcion='Eliminar incidente', recurso='incidente', accion='eliminar'),
            Permiso(nombre='listar_incidentes', descripcion='Listar incidentes', recurso='incidente', accion='listar'),
            Permiso(nombre='asignar_incidente', descripcion='Asignar incidente a técnico', recurso='incidente', accion='asignar'),
            
            # ========== EVIDENCIA ==========
            Permiso(nombre='crear_evidencia', descripcion='Capturar evidencia multimedia', recurso='evidencia', accion='crear'),
            Permiso(nombre='leer_evidencia', descripcion='Ver evidencia', recurso='evidencia', accion='leer'),
            Permiso(nombre='eliminar_evidencia', descripcion='Eliminar evidencia', recurso='evidencia', accion='eliminar'),
            
            # ========== DESPACHO Y SOLICITUDES DE SERVICIO ==========
            Permiso(nombre='crear_solicitud_servicio', descripcion='Crear solicitud de servicio', recurso='solicitud_servicio', accion='crear'),
            Permiso(nombre='leer_solicitud_servicio', descripcion='Ver solicitud de servicio', recurso='solicitud_servicio', accion='leer'),
            Permiso(nombre='actualizar_solicitud_servicio', descripcion='Actualizar solicitud de servicio', recurso='solicitud_servicio', accion='actualizar'),
            Permiso(nombre='eliminar_solicitud_servicio', descripcion='Eliminar solicitud de servicio', recurso='solicitud_servicio', accion='eliminar'),
            Permiso(nombre='asignar_tecnico', descripcion='Asignar técnico a solicitud', recurso='solicitud_servicio', accion='asignar'),
            
            # ========== REPUESTOS ==========
            Permiso(nombre='crear_repuesto', descripcion='Crear repuesto/parte', recurso='repuesto', accion='crear'),
            Permiso(nombre='leer_repuesto', descripcion='Ver detalles del repuesto', recurso='repuesto', accion='leer'),
            Permiso(nombre='actualizar_repuesto', descripcion='Actualizar repuesto', recurso='repuesto', accion='actualizar'),
            Permiso(nombre='eliminar_repuesto', descripcion='Eliminar repuesto', recurso='repuesto', accion='eliminar'),
            
            # ========== PAGOS ==========
            Permiso(nombre='crear_pago', descripcion='Registrar pago', recurso='pago', accion='crear'),
            Permiso(nombre='leer_pago', descripcion='Ver detalles del pago', recurso='pago', accion='leer'),
            Permiso(nombre='actualizar_pago', descripcion='Actualizar estado del pago', recurso='pago', accion='actualizar'),
            Permiso(nombre='eliminar_pago', descripcion='Eliminar pago', recurso='pago', accion='eliminar'),
            
            # ========== COMISIONES ==========
            Permiso(nombre='crear_comision', descripcion='Crear comisión', recurso='comision', accion='crear'),
            Permiso(nombre='leer_comision', descripcion='Ver detalles de comisión', recurso='comision', accion='leer'),
            Permiso(nombre='actualizar_comision', descripcion='Actualizar comisión', recurso='comision', accion='actualizar'),
            Permiso(nombre='eliminar_comision', descripcion='Eliminar comisión', recurso='comision', accion='eliminar'),
            
            # ========== CALIFICACIONES ==========
            Permiso(nombre='crear_calificacion', descripcion='Crear calificación/reseña', recurso='calificacion', accion='crear'),
            Permiso(nombre='leer_calificacion', descripcion='Ver calificación', recurso='calificacion', accion='leer'),
            Permiso(nombre='eliminar_calificacion', descripcion='Eliminar calificación', recurso='calificacion', accion='eliminar'),
            
            # ========== TRACKING Y UBICACIÓN ==========
            Permiso(nombre='crear_tracking', descripcion='Crear punto de tracking', recurso='tracking', accion='crear'),
            Permiso(nombre='leer_tracking', descripcion='Ver ubicación en tiempo real', recurso='tracking', accion='leer'),
            
            # ========== DASHBOARD ==========
            Permiso(nombre='ver_dashboard_admin', descripcion='Ver dashboard administrativo', recurso='dashboard', accion='ver_admin'),
            Permiso(nombre='ver_dashboard_operador', descripcion='Ver dashboard de operador', recurso='dashboard', accion='ver_operador'),
            Permiso(nombre='ver_dashboard_cliente', descripcion='Ver dashboard de cliente', recurso='dashboard', accion='ver_cliente'),
            
            # ========== MENSAJES Y NOTIFICACIONES ==========
            Permiso(nombre='crear_mensaje', descripcion='Crear mensaje in-app', recurso='mensaje', accion='crear'),
            Permiso(nombre='leer_mensaje', descripcion='Leer mensajes', recurso='mensaje', accion='leer'),
            Permiso(nombre='eliminar_mensaje', descripcion='Eliminar mensaje', recurso='mensaje', accion='eliminar'),
            Permiso(nombre='crear_notificacion', descripcion='Crear notificación push', recurso='notificacion', accion='crear'),
            
            # ========== REPORTES ==========
            Permiso(nombre='generar_reporte', descripcion='Generar reportes del sistema', recurso='reporte', accion='generar'),
            Permiso(nombre='descargar_reporte', descripcion='Descargar reportes', recurso='reporte', accion='descargar'),
            
            # ========== CONFIGURACIÓN DEL SISTEMA ==========
            Permiso(nombre='ver_configuracion', descripcion='Ver configuración del sistema', recurso='configuracion', accion='ver'),
            Permiso(nombre='editar_configuracion', descripcion='Editar configuración del sistema', recurso='configuracion', accion='editar'),
        ]
        for p in permisos: db.add(p)
        db.commit()
        
        # ========== ASIGNAR PERMISOS A ROLES ==========
        all_permisos = db.query(Permiso).all()
        
        # ADMIN: Todos los permisos (superusuario con acceso total)
        admin_rol.permisos = all_permisos
        
        # TECNICO: Permisos para ver y actualizar incidentes, solicitudes, tracking y calificar
        tecnico_permisos = db.query(Permiso).filter(
            (Permiso.nombre.in_([
                'leer_incidente', 'actualizar_incidente', 'listar_incidentes',
                'leer_solicitud_servicio', 'actualizar_solicitud_servicio',
                'crear_tracking', 'leer_tracking',
                'crear_calificacion', 'leer_calificacion',
                'leer_evidencia', 'crear_evidencia',
                'leer_usuario',  # Ver su propio perfil
                'ver_dashboard_operador',
                'leer_mensaje', 'crear_mensaje',
                'leer_repuesto',
            ]))
        ).all()
        tecnico_rol.permisos = tecnico_permisos
        
        # CLIENTE: Permisos para crear incidentes, ver sus vehículos, ver su perfil
        cliente_permisos = db.query(Permiso).filter(
            (Permiso.nombre.in_([
                'crear_incidente', 'leer_incidente', 'listar_incidentes',
                'crear_evidencia', 'leer_evidencia',
                'crear_vehiculo', 'leer_vehiculo', 'listar_vehiculos', 'actualizar_vehiculo',
                'crear_calificacion', 'leer_calificacion',
                'leer_solicitud_servicio',
                'leer_usuario',  # Ver su propio perfil
                'ver_dashboard_cliente',
                'leer_mensaje', 'crear_mensaje',
                'leer_marca', 'leer_modelo',
            ]))
        ).all()
        cliente_rol.permisos = cliente_permisos
        
        # GESTOR_TALLER: Permisos para gestionar técnicos, vehículos, repuestos y solicitudes de servicio
        gestor_permisos = db.query(Permiso).filter(
            (Permiso.nombre.in_([
                'crear_usuario', 'leer_usuario', 'actualizar_usuario',
                'crear_vehiculo', 'leer_vehiculo', 'actualizar_vehiculo', 'listar_vehiculos',
                'crear_solicitud_servicio', 'leer_solicitud_servicio', 'actualizar_solicitud_servicio', 'asignar_tecnico',
                'crear_repuesto', 'leer_repuesto', 'actualizar_repuesto',
                'crear_tracking', 'leer_tracking',
                'leer_incidente', 'listar_incidentes',
                'leer_usuario',  # Ver su propio perfil
                'ver_dashboard_operador',
                'leer_mensaje', 'crear_mensaje',
                'crear_pago', 'leer_pago',
                'crear_comision', 'leer_comision',
                'generar_reporte',
            ]))
        ).all()
        gestor_rol.permisos = gestor_permisos
        
        db.commit()
        
        print('Creando usuarios y actores...')
        ph = hash_password('123456')
        
        # Usuario Admin
        admin_user = Usuario(email='admin@example.com', telefono='3001', password_hash=ph, id_rol=admin_rol.id_rol, estado_cuenta=EstadoCuenta.ACTIVO)
        db.add(admin_user)
        db.flush()
        
        # Usuario Técnico
        tecnico_user = Usuario(email='tecnico@example.com', telefono='3003', password_hash=ph, id_rol=tecnico_rol.id_rol, estado_cuenta=EstadoCuenta.ACTIVO)
        db.add(tecnico_user)
        db.flush()
        
        # Usuario Cliente
        cliente_user = Usuario(email='cliente@example.com', telefono='3004', password_hash=ph, id_rol=cliente_rol.id_rol, estado_cuenta=EstadoCuenta.ACTIVO)
        db.add(cliente_user)
        db.flush()
        
        # Usuario Gestor de Taller
        gestor_user = Usuario(email='gestor_taller@example.com', telefono='3005', password_hash=ph, id_rol=gestor_rol.id_rol, estado_cuenta=EstadoCuenta.ACTIVO)
        db.add(gestor_user)
        db.flush()
        
        # Crear instancias de Cliente, Gestor y Técnico
        cliente = Cliente(id_usuario=cliente_user.id_usuario, nombres='Juan', apellidos='Pérez', ci='1234567890')
        db.add(cliente)
        db.flush()
        
        gestor = GestorTaller(id_usuario=gestor_user.id_usuario, razon_social='Taller Mecánico El Ejecutivo', nit='900123456', direccion='Cra 7 #25-80')
        db.add(gestor)
        db.flush()
        
        tecnico = Tecnico(id_usuario=tecnico_user.id_usuario, id_taller=gestor.id_taller, nombres='Carlos', especialidad='Mecánica', esta_disponible=1)
        db.add(tecnico)
        db.flush()
        
        db.commit()
        print('Datos creados exitosamente')
    except Exception as e:
        db.rollback()
        print('Error:', e)
        raise
    finally:
        db.close()

if __name__ == '__main__':
    try:
        reset_database()
        create_test_data()
        print('? Base de datos inicializada correctamente')
    except Exception as e:
        print('Error:', e)

