# -*- coding: utf-8 -*-
"""
reset_db.py - Script optimizado para reiniciar la base de datos y cargar datos de prueba
Alineado estrictamente con el diseño físico de 27 tablas del 2do Parcial.
Uso: python reset_db.py
"""
import sys
from sqlalchemy import text
from models.database import SessionLocal, engine, Base

# === IMPORTACIONES OBLIGATORIAS ===
import models  
from models.user import Rol, Permiso, Usuario, EstadoCuenta
from models.taller import Taller
from models.tecnico import Tecnico
from models.incidente import Incidente
from models.solicitud import SolicitudServicio
# Añadimos la importación de los modelos extendidos para que SQLAlchemy reconozca las tablas hijas
from models.cliente import Cliente
from models.gestor import GestorTaller 
from models.ubicacion_tracking import UbicacionTracking
from models.proceso_incidente import IncidenteAsignado, Cotizacion
from models.zona_cobertura import ZonaCobertura
from models.vehiculo import Vehiculo
from models.repuesto import Repuesto
from models.bitacora import Bitacora
# =============================================

from security.password import hash_password


def reset_database():
    """Elimina y recrea todas las tablas (optimizado para PostgreSQL)"""
    print('🗑️  Eliminando todas las tablas y limpiando esquema...')
    
    with engine.connect() as conn:
        try:
            print('   - Eliminando schema public (y todos sus objetos)...')
            conn.execute(text("DROP SCHEMA public CASCADE;"))
            conn.commit()
            print('   ✓ Schema eliminado')
        except Exception as e:
            print(f'   ⚠️  Schema no existía o error: {e}')
            conn.rollback()
        
        try:
            print('   - Creando schema public...')
            conn.execute(text("CREATE SCHEMA public;"))
            print('   - Asignando permisos...')
            conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
            conn.commit()
            
            print('   - Asegurando extensión PostGIS...')
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            conn.commit()
            print('   ✓ Schema recreado con permisos y PostGIS')
        except Exception as e:
            print(f'   ⚠️  Error recreando schema o postgis: {e}')
            conn.rollback()
    
    print('🏗️  Creando nuevas tablas desde los modelos...')
    Base.metadata.create_all(bind=engine)
    print('✅ Tablas creadas correctamente')


def create_test_data():
    """Crea datos de prueba respetando la jerarquía relacional y restricciones ACID"""
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
            Permiso(nombre='crear_usuario', descripcion='Crear nuevo usuario', recurso='usuario', accion='crear'),
            Permiso(nombre='leer_usuario', descripcion='Ver detalles del usuario', recurso='usuario', accion='leer'),
            Permiso(nombre='actualizar_usuario', descripcion='Actualizar datos del usuario', recurso='usuario', accion='actualizar'),
            Permiso(nombre='eliminar_usuario', descripcion='Eliminar usuario', recurso='usuario', accion='eliminar'),
            Permiso(nombre='crear_vehiculo', descripcion='Registrar nuevo vehículo', recurso='vehiculo', accion='crear'),
            Permiso(nombre='leer_vehiculo', descripcion='Ver detalles del vehículo', recurso='vehiculo', accion='leer'),
            Permiso(nombre='actualizar_vehiculo', descripcion='Actualizar información del vehículo', recurso='vehiculo', accion='actualizar'),
            Permiso(nombre='eliminar_vehiculo', descripcion='Eliminar vehículo', recurso='vehiculo', accion='eliminar'),
            Permiso(nombre='crear_incidente', descripcion='Crear nuevo incidente/emergencia', recurso='incidente', accion='crear'),
            Permiso(nombre='leer_incidente', descripcion='Ver detalles del incidente', recurso='incidente', accion='leer'),
            Permiso(nombre='actualizar_incidente', descripcion='Actualizar incidente', recurso='incidente', accion='actualizar'),
            Permiso(nombre='eliminar_incidente', descripcion='Eliminar incidente', recurso='incidente', accion='eliminar'),
            Permiso(nombre='crear_solicitud_servicio', descripcion='Crear solicitud de servicio', recurso='solicitud_servicio', accion='crear'),
            Permiso(nombre='leer_solicitud_servicio', descripcion='Ver solicitud de servicio', recurso='solicitud_servicio', accion='leer'),
            Permiso(nombre='actualizar_solicitud_servicio', descripcion='Actualizar solicitud de servicio', recurso='solicitud_servicio', accion='actualizar'),
            Permiso(nombre='asignar_tecnico', descripcion='Asignar técnico a solicitud', recurso='solicitud_servicio', accion='asignar'),
            Permiso(nombre='leer_bitacora', descripcion='Ver bitácora de auditoría', recurso='bitacora', accion='leer'),
            Permiso(nombre='ver_dashboard', descripcion='Ver dashboard', recurso='dashboard', accion='ver'),
        ]
        for p in permisos:
            db.add(p)
        db.commit()
        print(f'   ✓ {len(permisos)} permisos creados')
        
        print('\n👥 ASIGNANDO PERMISOS A ROLES...')
        admin_rol.permisos = db.query(Permiso).all()
        tecnico_rol.permisos = db.query(Permiso).filter(Permiso.nombre.in_(['leer_incidente', 'actualizar_incidente', 'leer_solicitud_servicio', 'actualizar_solicitud_servicio', 'leer_usuario', 'ver_dashboard'])).all()
        cliente_rol.permisos = db.query(Permiso).filter(Permiso.nombre.in_(['crear_incidente', 'leer_incidente', 'crear_vehiculo', 'leer_vehiculo', 'actualizar_vehiculo', 'leer_solicitud_servicio'])).all()
        gestor_rol.permisos = db.query(Permiso).filter(Permiso.nombre.in_(['crear_usuario', 'leer_usuario', 'actualizar_usuario', 'crear_solicitud_servicio', 'leer_solicitud_servicio', 'actualizar_solicitud_servicio', 'asignar_tecnico', 'leer_incidente', 'ver_dashboard'])).all()
        db.commit()
        print('   ✓ Permisos asignados a roles')
        
        print('\n👤 PASO 1: CREANDO CUENTAS DE USUARIO BASE...')
        password_hash = hash_password('12345678')
        
        u_admin = Usuario(nombre='Admin', apellido='System', email='admin@example.com', telefono='+1001', password_hash=password_hash, id_rol=admin_rol.id_rol, estado_cuenta=EstadoCuenta.ACTIVO)
        u_tecnico = Usuario(nombre='Carlos', apellido='Ruiz', email='tecnico@example.com', telefono='+1002', password_hash=password_hash, id_rol=tecnico_rol.id_rol, estado_cuenta=EstadoCuenta.ACTIVO)
        u_cliente = Usuario(nombre='Juan', apellido='Pérez', email='cliente@example.com', telefono='+1003', password_hash=password_hash, id_rol=cliente_rol.id_rol, estado_cuenta=EstadoCuenta.ACTIVO)
        u_gestor = Usuario(nombre='Roberto', apellido='García', email='gestor@example.com', telefono='+1004', password_hash=password_hash, id_rol=gestor_rol.id_rol, estado_cuenta=EstadoCuenta.ACTIVO)
        
        db.add_all([u_admin, u_tecnico, u_cliente, u_gestor])
        db.commit()
        print('   ✓ Cuentas de usuario persistidas.')

        print('\n👥 PASO 2: EXTENDIENDO PERFILES (HERENCIA 1:1)...')
        # Sembramos el Cliente real amarrado a su id_usuario
        perfil_cliente = Cliente(id_cliente=u_cliente.id_usuario, nombres='Juan', apellidos='Pérez', ci='1234567-SC')
        # Sembramos el Gestor real amarrado a su id_usuario
        perfil_gestor = GestorTaller(id_gestor=u_gestor.id_usuario, razon_social='Corporación Mecánica García S.R.L.', nit='987654321-011')
        
        db.add_all([perfil_cliente, perfil_gestor])
        db.commit()
        print('   ✓ Perfiles de Cliente y Gestor mapeados correctamente.')
        
        print('\n🏭 PASO 3: CREANDO ESTABLECIMIENTOS FÍSICOS (TALLERES)...')
        # El taller físico requiere obligatoriamente el id del gestor corporativo dueño
        taller_central = Taller(
            id_gestor=perfil_gestor.id_gestor,
            nombre='Taller Central Automotriz',
            direccion='Av. Busch, 2do Anillo, Santa Cruz',
            telefono='+591 3 3345678'
        )
        db.add(taller_central)
        db.commit()
        print(f'   ✓ Taller "{taller_central.nombre}" creado bajo la administración del Gestor ID: {taller_central.id_gestor}')
        
        print('\n🔧 PASO 4: REGISTRANDO PERSONAL ASIGNADO (TÉCNICOS)...')
        # El técnico ahora hereda de su usuario y se vincula físicamente al taller creado.
        perfil_tecnico = Tecnico(
            id_tecnico=u_tecnico.id_usuario,
            id_taller=taller_central.id_taller,
            especialidad='Mecánica y Sistemas de Inyección',
            disponibilidad='Libre'  # Sincronizado con el string por defecto del modelo
        )
        db.add(perfil_tecnico)
        db.commit()
        print('   ✓ Historial de Personal Técnico sembrado con éxito.')
        
        print('\n✨ Base de datos inicializada exitosamente')
        print('\n📝 RESUMEN DE LA SIEMBRA:')
        print(f'   - {len(roles_data)} Roles Base')
        print(f'   - {len(permisos)} Permisos del Sistema')
        print(f'   - 4 Entidades Usuario')
        print(f'   - 1 Actor Cliente Expandido')
        print(f'   - 1 Actor Gestor Expandido (Tenant Raíz)')
        print(f'   - 1 Taller Físico Vinculado')
        print(f'   - 1 Técnico Operativo en Sucursal')
        
    except Exception as e:
        db.rollback()
        print(f'\n❌ Error crítico al sembrar datos: {e}')
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == '__main__':
    try:
        print('=' * 60)
        print('🔄 REINICIANDO ENTIDADES - ARQUITECTURA 2DO PARCIAL')
        print('=' * 60)
        reset_database()
        create_test_data()
        print('=' * 60)
        print('✅ SISTEMA TOTALMENTE CONSOLIDADO')
        print('=' * 60)
    except Exception as e:
        print(f'\n❌ Error fatal en ejecución: {e}')
        sys.exit(1)