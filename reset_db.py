# -*- coding: utf-8 -*-
"""
reset_db.py - Script optimizado para reiniciar la base de datos y cargar datos de prueba
Alineado estrictamente con el diseño físico de 27 tablas del 2do Parcial y Multi-tenant.
Uso: python reset_db.py
"""
import sys
import hashlib
from sqlalchemy import text, func
from models.database import SessionLocal, engine, Base

# === IMPORTACIONES OBLIGATORIAS ===
import models  
from models.user import Rol, Permiso, Usuario, EstadoCuenta
from models.taller import Taller
from models.tecnico import Tecnico
from models.incidente import Incidente
from models.solicitud import SolicitudServicio
from models.cliente import Cliente
from models.gestor import GestorTaller 
from models.ubicacion_tracking import UbicacionTracking
from models.proceso_incidente import IncidenteAsignado, Cotizacion
from models.zona_cobertura import ZonaCobertura
from models.vehiculo import Vehiculo
from models.repuesto import Repuesto
from models.bitacora import Bitacora
# =============================================

def hash_seguro_defensivo(password: str) -> str:
    """Genera hash SHA-256 compatible con el puente de seguridad de la autenticación"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


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
    """Crea datos de prueba respetando la jerarquía relacional y restricciones Multi-tenant"""
    db = SessionLocal()
    try:
        print('\n📋 CREANDO ROLES BASE (RBAC)...')
        roles_data = [
            Rol(nombre='Administrador', descripcion='Administrador del sistema con acceso completo'),
            Rol(nombre='Tecnico', descripcion='Técnico de taller para atención de emergencias'),
            Rol(nombre='Cliente', descripcion='Cliente/Usuario final para reportar incidentes'),
            Rol(nombre='Gestor', descripcion='Gestor de taller para administrar recursos'),
        ]
        for r in roles_data:
            db.add(r)
        db.flush() # Sincroniza IDs en caliente
        print(f'   ✓ {len(roles_data)} roles creados')
        
        # Mapeo de objetos de roles para asignaciones posteriores
        admin_rol = next(r for r in roles_data if r.nombre == 'Administrador')
        tecnico_rol = next(r for r in roles_data if r.nombre == 'Tecnico')
        cliente_rol = next(r for r in roles_data if r.nombre == 'Cliente')
        gestor_rol = next(r for r in roles_data if r.nombre == 'Gestor')
        
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

            Permiso(nombre='crear_taller', descripcion='Crear nuevo taller', recurso='taller', accion='crear'),
            Permiso(nombre='leer_taller', descripcion='Visualizar todos los talleres en el sistema', recurso='taller', accion='leer'),
            Permiso(nombre='actualizar_taller', descripcion='Actualizar información del taller', recurso='taller', accion='actualizar'),
            Permiso(nombre='eliminar_taller', descripcion='Eliminar taller', recurso='taller', accion='eliminar'),
           
            Permiso(nombre='crear_tecnico', descripcion='Crear nuevo técnico', recurso='tecnico', accion='crear'),
             Permiso(nombre='leer_tecnico', descripcion='Visualizar todos los técnicos en el sistema', recurso='tecnico', accion='leer'),
            Permiso(nombre='actualizar_tecnico', descripcion='Actualizar información del técnico', recurso='tecnico', accion='actualizar'),
            Permiso(nombre='eliminar_tecnico', descripcion='Eliminar técnico', recurso='tecnico', accion='eliminar'),
        ]
        for p in permisos:
            db.add(p)
        db.flush()
        print(f'   ✓ {len(permisos)} permisos creados')
        
        print('\n👥 ASIGNANDO PERMISOS A ROLES...')
        admin_rol.permisos = permisos
        tecnico_rol.permisos = [p for p in permisos if p.nombre in ['leer_incidente', 'actualizar_incidente', 'leer_solicitud_servicio', 'actualizar_solicitud_servicio', 'leer_usuario', 'ver_dashboard']]
        cliente_rol.permisos = [p for p in permisos if p.nombre in ['crear_incidente', 'leer_incidente', 'crear_vehiculo', 'leer_vehiculo', 'actualizar_vehiculo', 'leer_solicitud_servicio']]
        gestor_rol.permisos = [p for p in permisos if p.nombre in ['crear_usuario', 'leer_usuario', 'actualizar_usuario', 'crear_solicitud_servicio', 'leer_solicitud_servicio', 'actualizar_solicitud_servicio', 'asignar_tecnico', 'leer_incidente', 'ver_dashboard']]
        db.flush()
        print('   ✓ Permisos asignados a roles')
        
        # =====================================================================
        # 👤 SECCIÓN 1: USUARIO ADMINISTRADOR CENTRAL
        # =====================================================================
        print('\n👤 CREANDO CUENTA DE ADMINISTRADOR CENTRAL...')
        u_admin = Usuario(
            nombre='Admin', apellido='System', 
            email='admin@example.com', telefono='+1001', 
            password_hash=hash_seguro_defensivo('12345678'), 
            id_rol=admin_rol.id_rol, estado_cuenta=EstadoCuenta.ACTIVO
        )
        db.add(u_admin)
        db.flush()

        # =====================================================================
        # 🌍 SECCIÓN 2: TENANT HEMISFERIO NORTE
        # =====================================================================
        print('\n🌍 CONFIGURANDO TENANT: HEMISFERIO NORTE...')
        
        u_gestor_norte = Usuario(
            nombre='Carlos', apellido='Mendoza', 
            email='gestor.norte@taller.com', telefono='+59170000001',
            password_hash=hash_seguro_defensivo('gestor123'),
            id_rol=gestor_rol.id_rol, estado_cuenta=EstadoCuenta.ACTIVO
        )
        db.add(u_gestor_norte)
        db.flush()

        perfil_gestor_norte = GestorTaller(usuario=u_gestor_norte, razon_social='Talleres del Norte Corp', nit='123456789', activo=True)
        db.add(perfil_gestor_norte)
        db.flush()

        # Talleres del Norte (Santa Cruz de la Sierra)
        taller_n1 = Taller(
            id_gestor=perfil_gestor_norte.id_gestor,
            nombre='Norteño Express - Santa Cruz',
            direccion='Downtown Santa Cruz, Bolivia',
            telefono='+59170000001',
            ubicacion=func.ST_GeomFromText('POINT(-63.182130 -17.783120)', 4326),
            fecha_registro=func.NOW()
        )
        taller_n2 = Taller(
            id_gestor=perfil_gestor_norte.id_gestor,
            nombre='EuroTaller - Santa Cruz',
            direccion='Av. Banzer, Bolivia',
            telefono='+59170000002',
            ubicacion=func.ST_GeomFromText('POINT(-63.182130 -17.783120)', 4326),
            fecha_registro=func.NOW()
        )
        db.add_all([taller_n1, taller_n2])
        db.flush()

        # Técnicos del Taller Norte 1 (tecnico1 y tecnico2)
        for i, (nom, ape) in enumerate([("John", "Doe"), ("Robert", "Smith")], start=1):
            u_tec = Usuario(nombre=nom, apellido=ape, email=f"tecnico{i}.norte@example.com", telefono=f"+10000000{i}", password_hash=hash_seguro_defensivo("tecnico123"), id_rol=tecnico_rol.id_rol, estado_cuenta=EstadoCuenta.ACTIVO)
            db.add(u_tec); db.flush()
            t_tec = Tecnico(usuario=u_tec, id_taller=taller_n1.id_taller, id_gestor=perfil_gestor_norte.id_gestor, especialidad='Mecánica General', disponibilidad='Libre')
            db.add(t_tec)

        # Técnicos del Taller Norte 2 (tecnico3 y tecnico4)
        for i, (nom, ape) in enumerate([("Jean", "Dupont"), ("Hans", "Müller")], start=3):
            u_tec = Usuario(nombre=nom, apellido=ape, email=f"tecnico{i}.norte@example.com", telefono=f"+10000000{i}", password_hash=hash_seguro_defensivo("tecnico123"), id_rol=tecnico_rol.id_rol, estado_cuenta=EstadoCuenta.ACTIVO)
            db.add(u_tec); db.flush()
            t_tec = Tecnico(usuario=u_tec, id_taller=taller_n2.id_taller, id_gestor=perfil_gestor_norte.id_gestor, especialidad='Sistemas de Inyección', disponibilidad='Libre')
            db.add(t_tec)

        # =====================================================================
        # 🌍 SECCIÓN 3: TENANT HEMISFERIO SUR
        # =====================================================================
        print('\n🌍 CONFIGURANDO TENANT: HEMISFERIO SUR...')
        
        u_gestor_sur = Usuario(
            nombre='Andrés', apellido='Silva', 
            email='gestor.sur@taller.com', telefono='+59170000002',
            password_hash=hash_seguro_defensivo('gestor123'),
            id_rol=gestor_rol.id_rol, estado_cuenta=EstadoCuenta.ACTIVO
        )
        db.add(u_gestor_sur)
        db.flush()

        perfil_gestor_sur = GestorTaller(usuario=u_gestor_sur, razon_social='Consorcio Mecánico del Sur', nit='987654321', activo=True)
        db.add(perfil_gestor_sur)
        db.flush()

        # Talleres del Sur (Santa Cruz de la Sierra)
        taller_s1 = Taller(
            id_gestor=perfil_gestor_sur.id_gestor,
            nombre='Taller Central - Santa Cruz',
            direccion='Av. Busch, 2do Anillo, Santa Cruz',
            telefono='+59170000011',
            ubicacion=func.ST_GeomFromText('POINT(-63.182130 -17.783120)', 4326),
            fecha_registro=func.NOW()
        )
        taller_s2 = Taller(
            id_gestor=perfil_gestor_sur.id_gestor,
            nombre='Taller Austral - Santa Cruz',
            direccion='Av. Corrientes,Santa Cruz',
            telefono='+59170000022',
            ubicacion=func.ST_GeomFromText('POINT(-63.182130 -17.783120)', 4326),
            fecha_registro=func.NOW()
        )
        db.add_all([taller_s1, taller_s2])
        db.flush()

        # Técnicos del Taller Sur 1 (tecnico1 y tecnico2)
        for i, (nom, ape) in enumerate([("Hugo", "Chávez"), ("Mario", "Flores")], start=1):
            u_tec = Usuario(nombre=nom, apellido=ape, email=f"tecnico{i}.sur@example.com", telefono=f"+5917000001{i}", password_hash=hash_seguro_defensivo("tecnico123"), id_rol=tecnico_rol.id_rol, estado_cuenta=EstadoCuenta.ACTIVO)
            db.add(u_tec); db.flush()
            t_tec = Tecnico(usuario=u_tec, id_taller=taller_s1.id_taller, id_gestor=perfil_gestor_sur.id_gestor, especialidad='Alineación y Balanceo', disponibilidad='Libre')
            db.add(t_tec)

        # Técnicos del Taller Sur 2 (tecnico3 y tecnico4)
        for i, (nom, ape) in enumerate([("Diego", "Maradona"), ("Lionel", "Messi")], start=3):
            u_tec = Usuario(nombre=nom, apellido=ape, email=f"tecnico{i}.sur@example.com", telefono=f"+5917000002{i}", password_hash=hash_seguro_defensivo("tecnico123"), id_rol=tecnico_rol.id_rol, estado_cuenta=EstadoCuenta.ACTIVO)
            db.add(u_tec); db.flush()
            t_tec = Tecnico(usuario=u_tec, id_taller=taller_s2.id_taller, id_gestor=perfil_gestor_sur.id_gestor, especialidad='Electrónica Automotriz', disponibilidad='Libre')
            db.add(t_tec)

        db.commit()
        print('\n✨ Base de datos consolidada e inicializada exitosamente')
        print('\n📝 RESUMEN DE LA ARQUITECTURA DISTRIBUIDA:')
        print(f'   - {len(roles_data)} Roles Base del Sistema (RBAC)')
        print(f'   - {len(permisos)} Permisos Estrictos Mapeados')
        print(f'   - 1 Administrador Central del Sistema')
        print(f'   - 2 Gestores de Talleres distribuidos por Hemisferio (Tenants)')
        print(f'   - 4 Establecimientos Físicos con PostGIS Activado')
        print(f'   - 8 Técnicos Operativos distribuidos y aislados')

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
        print('🔄 REINICIANDO ENTIDADES - ARQUITECTURA MULTI-TENANT')
        print('=' * 60)
        reset_database()
        create_test_data()
        print('=' * 60)
        print('✅ SISTEMA TOTALMENTE CONSOLIDADO Y LISTO')
        print('=' * 60)
    except Exception as e:
        print(f'\n❌ Error fatal en ejecución: {e}')
        sys.exit(1)