# -*- coding: utf-8 -*-
"""
reset_db.py - Script para reiniciar la base de datos y cargar datos de prueba
Uso: python reset_db.py
"""
import sys
from sqlalchemy import text
from models.database import SessionLocal, engine, Base
from models.user import Usuario, Rol, Permiso, EstadoCuenta
from models.taller import Taller
from models.tecnico import Tecnico
from models.vehiculo import Vehiculo
from models.incidente import Incidente
from models.bitacora import Bitacora
from models.solicitud import SolicitudServicio
from security.password import hash_password


def reset_database():
    """Elimina y recrea todas las tablas (optimizado para PostgreSQL)"""
    print('🗑️  Eliminando todas las tablas y limpiando esquema...')
    
    with engine.connect() as conn:
        # Para PostgreSQL: usar DROP SCHEMA CASCADE para limpieza total
        try:
            print('   - Eliminando schema public (y todos sus objetos)...')
            conn.execute(text("DROP SCHEMA public CASCADE;"))
            conn.commit()
            print('   ✓ Schema eliminado')
        except Exception as e:
            print(f'   ⚠️  Schema no existía o error: {e}')
            conn.rollback()
        
        # Recrear el schema public
        try:
            print('   - Creando schema public...')
            conn.execute(text("CREATE SCHEMA public;"))
            print('   - Asignando permisos...')
            conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
            conn.commit()
            print('   ✓ Schema recreado con permisos')
        except Exception as e:
            print(f'   ⚠️  Error recreando schema: {e}')
            conn.rollback()
    
    print('🏗️  Creando nuevas tablas desde los modelos...')
    Base.metadata.create_all(bind=engine)
    print('✅ Tablas creadas correctamente')


def create_test_data():
    """Crea datos de prueba: roles, permisos, usuarios y talleres"""
    db = SessionLocal()
    try:
        print('\n📋 CREANDO ROLES...')
        roles_data = [
            Rol(nombre='Administrador', descripcion='Administrador del sistema con acceso completo'),
            Rol(nombre='Tecnico', descripcion='Técnico de taller para atención de emergencias'),
            Rol(nombre='Cliente', descripcion='Cliente/Usuario final para reportar incidentes'),
            Rol(nombre='GestorTaller', descripcion='Gestor de taller para administrar recursos'),
        ]
        for r in roles_data:
            db.add(r)
        db.commit()
        print(f'   ✓ {len(roles_data)} roles creados')
        
        # Obtener IDs de roles
        admin_rol = db.query(Rol).filter(Rol.nombre == 'Administrador').first()
        tecnico_rol = db.query(Rol).filter(Rol.nombre == 'Tecnico').first()
        cliente_rol = db.query(Rol).filter(Rol.nombre == 'Cliente').first()
        gestor_rol = db.query(Rol).filter(Rol.nombre == 'GestorTaller').first()
        
        print('\n🔐 CREANDO PERMISOS...')
        permisos = [
            # USUARIOS
            Permiso(nombre='crear_usuario', descripcion='Crear nuevo usuario', recurso='usuario', accion='crear'),
            Permiso(nombre='leer_usuario', descripcion='Ver detalles del usuario', recurso='usuario', accion='leer'),
            Permiso(nombre='actualizar_usuario', descripcion='Actualizar datos del usuario', recurso='usuario', accion='actualizar'),
            Permiso(nombre='eliminar_usuario', descripcion='Eliminar usuario', recurso='usuario', accion='eliminar'),
            
            # VEHÍCULOS
            Permiso(nombre='crear_vehiculo', descripcion='Registrar nuevo vehículo', recurso='vehiculo', accion='crear'),
            Permiso(nombre='leer_vehiculo', descripcion='Ver detalles del vehículo', recurso='vehiculo', accion='leer'),
            Permiso(nombre='actualizar_vehiculo', descripcion='Actualizar información del vehículo', recurso='vehiculo', accion='actualizar'),
            Permiso(nombre='eliminar_vehiculo', descripcion='Eliminar vehículo', recurso='vehiculo', accion='eliminar'),
            
            # INCIDENTES
            Permiso(nombre='crear_incidente', descripcion='Crear nuevo incidente/emergencia', recurso='incidente', accion='crear'),
            Permiso(nombre='leer_incidente', descripcion='Ver detalles del incidente', recurso='incidente', accion='leer'),
            Permiso(nombre='actualizar_incidente', descripcion='Actualizar incidente', recurso='incidente', accion='actualizar'),
            Permiso(nombre='eliminar_incidente', descripcion='Eliminar incidente', recurso='incidente', accion='eliminar'),
            
            # SOLICITUDES DE SERVICIO
            Permiso(nombre='crear_solicitud_servicio', descripcion='Crear solicitud de servicio', recurso='solicitud_servicio', accion='crear'),
            Permiso(nombre='leer_solicitud_servicio', descripcion='Ver solicitud de servicio', recurso='solicitud_servicio', accion='leer'),
            Permiso(nombre='actualizar_solicitud_servicio', descripcion='Actualizar solicitud de servicio', recurso='solicitud_servicio', accion='actualizar'),
            Permiso(nombre='asignar_tecnico', descripcion='Asignar técnico a solicitud', recurso='solicitud_servicio', accion='asignar'),
            
            # BITÁCORA
            Permiso(nombre='leer_bitacora', descripcion='Ver bitácora de auditoría', recurso='bitacora', accion='leer'),
            
            # DASHBOARD
            Permiso(nombre='ver_dashboard', descripcion='Ver dashboard', recurso='dashboard', accion='ver'),
        ]
        for p in permisos:
            db.add(p)
        db.commit()
        print(f'   ✓ {len(permisos)} permisos creados')
        
        print('\n👥 ASIGNANDO PERMISOS A ROLES...')
        # ADMINISTRADOR: todos los permisos
        all_permisos = db.query(Permiso).all()
        admin_rol.permisos = all_permisos
        
        # TÉCNICO: lectura y actualización de incidentes y solicitudes
        tecnico_permisos = db.query(Permiso).filter(
            Permiso.nombre.in_([
                'leer_incidente', 'actualizar_incidente',
                'leer_solicitud_servicio', 'actualizar_solicitud_servicio',
                'leer_usuario', 'ver_dashboard',
                'leer_bitacora',
            ])
        ).all()
        tecnico_rol.permisos = tecnico_permisos
        
        # CLIENTE: crear incidentes y vehículos, ver sus solicitudes
        cliente_permisos = db.query(Permiso).filter(
            Permiso.nombre.in_([
                'crear_incidente', 'leer_incidente',
                'crear_vehiculo', 'leer_vehiculo', 'actualizar_vehiculo',
                'crear_solicitud_servicio', 'leer_solicitud_servicio',
                'leer_usuario', 'ver_dashboard',
            ])
        ).all()
        cliente_rol.permisos = cliente_permisos
        
        # GESTOR TALLER: gestión completa de solicitudes, técnicos y vehículos
        gestor_permisos = db.query(Permiso).filter(
            Permiso.nombre.in_([
                'crear_usuario', 'leer_usuario', 'actualizar_usuario',
                'crear_vehiculo', 'leer_vehiculo', 'actualizar_vehiculo',
                'crear_solicitud_servicio', 'leer_solicitud_servicio', 'actualizar_solicitud_servicio', 'asignar_tecnico',
                'leer_incidente',
                'ver_dashboard', 'leer_bitacora',
            ])
        ).all()
        gestor_rol.permisos = gestor_permisos
        
        db.commit()
        print('   ✓ Permisos asignados a roles')
        
        print('\n👤 CREANDO USUARIOS...')
        password_hash = hash_password('password123')  # Contraseña por defecto: password123 (truncada a 72 bytes)
        
        usuarios_data = [
            Usuario(
                nombre='Admin',
                apellido='System',
                email='admin@example.com',
                telefono='+1001',
                password_hash=password_hash,
                id_rol=admin_rol.id_rol,
                estado_cuenta=EstadoCuenta.ACTIVO
            ),
            Usuario(
                nombre='Carlos',
                apellido='Ruiz',
                email='tecnico@example.com',
                telefono='+1002',
                password_hash=password_hash,
                id_rol=tecnico_rol.id_rol,
                estado_cuenta=EstadoCuenta.ACTIVO
            ),
            Usuario(
                nombre='Juan',
                apellido='Pérez',
                email='cliente@example.com',
                telefono='+1003',
                password_hash=password_hash,
                id_rol=cliente_rol.id_rol,
                estado_cuenta=EstadoCuenta.ACTIVO
            ),
            Usuario(
                nombre='Roberto',
                apellido='García',
                email='gestor@example.com',
                telefono='+1004',
                password_hash=password_hash,
                id_rol=gestor_rol.id_rol,
                estado_cuenta=EstadoCuenta.ACTIVO
            ),
        ]
        
        for u in usuarios_data:
            db.add(u)
        db.commit()
        print(f'   ✓ {len(usuarios_data)} usuarios creados')
        print('   Credenciales: email/password123')
        
        print('\n🏭 CREANDO TALLERES...')
        # Obtener usuario admin como propietario
        admin_user = db.query(Usuario).filter(Usuario.email == 'admin@example.com').first()
        
        talleres_data = [
            Taller(
                nombre='Taller Central',
                direccion='Cra 7 #25-80, Bogotá',
                telefono='+57 1 2345678',
                id_propietario=admin_user.id_usuario,
                especialidad='Mecánica General',
                capacidad_vehiculos=5,
                estado_activo=True
            ),
            Taller(
                nombre='Taller Oriente',
                direccion='Cra 50 #45-20, Bogotá',
                telefono='+57 1 9876543',
                id_propietario=admin_user.id_usuario,
                especialidad='Eléctrica',
                capacidad_vehiculos=3,
                estado_activo=True
            ),
        ]
        
        for t in talleres_data:
            db.add(t)
        db.commit()
        print(f'   ✓ {len(talleres_data)} talleres creados')
        
        print('\n🔧 CREANDO TÉCNICOS...')
        # Obtener usuarios técnicos
        tecnico_user = db.query(Usuario).filter(Usuario.email == 'tecnico@example.com').first()
        talleres = db.query(Taller).all()
        
        if tecnico_user and talleres:
            tecnico = Tecnico(
                id_usuario=tecnico_user.id_usuario,
                id_taller=talleres[0].id,
                especialidad='Mecánica General',
                estado_disponibilidad='Libre'
            )
            db.add(tecnico)
            db.commit()
            print('   ✓ 1 técnico creado')
        
        print('\n✨ Base de datos inicializada exitosamente')
        print('\n📝 RESUMEN:')
        print(f'   - {len(roles_data)} Roles')
        print(f'   - {len(permisos)} Permisos')
        print(f'   - {len(usuarios_data)} Usuarios')
        print(f'   - {len(talleres_data)} Talleres')
        print(f'   - 1 Técnico')
        
    except Exception as e:
        db.rollback()
        print(f'\n❌ Error al crear datos: {e}')
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == '__main__':
    try:
        print('=' * 60)
        print('🔄 REINICIANDO BASE DE DATOS')
        print('=' * 60)
        reset_database()
        create_test_data()
        print('=' * 60)
        print('✅ PROCESO COMPLETADO EXITOSAMENTE')
        print('=' * 60)
    except Exception as e:
        print(f'\n❌ Error fatal: {e}')
        sys.exit(1)

