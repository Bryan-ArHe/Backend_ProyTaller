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
        conn.execute(text("DROP TYPE IF EXISTS estadocuenta CASCADE"))
        conn.commit()
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
            Permiso(nombre='crear_incidente', descripcion='Crear nuevo incidente', recurso='incidente', accion='crear'),
            Permiso(nombre='leer_incidente', descripcion='Ver detalles del incidente', recurso='incidente', accion='leer'),
            Permiso(nombre='actualizar_incidente', descripcion='Actualizar incidente', recurso='incidente', accion='actualizar'),
            Permiso(nombre='eliminar_incidente', descripcion='Eliminar incidente', recurso='incidente', accion='eliminar'),
            Permiso(nombre='crear_usuario', descripcion='Crear nuevo usuario', recurso='usuario', accion='crear'),
            Permiso(nombre='leer_usuario', descripcion='Ver detalles del usuario', recurso='usuario', accion='leer'),
            Permiso(nombre='actualizar_usuario', descripcion='Actualizar usuario', recurso='usuario', accion='actualizar'),
            Permiso(nombre='eliminar_usuario', descripcion='Eliminar usuario', recurso='usuario', accion='eliminar'),
            Permiso(nombre='crear_vehiculo', descripcion='Registrar vehículo', recurso='vehiculo', accion='crear'),
            Permiso(nombre='leer_vehiculo', descripcion='Ver detalles del vehículo', recurso='vehiculo', accion='leer'),
            Permiso(nombre='actualizar_vehiculo', descripcion='Actualizar vehículo', recurso='vehiculo', accion='actualizar'),
            Permiso(nombre='eliminar_vehiculo', descripcion='Eliminar vehículo', recurso='vehiculo', accion='eliminar'),
            Permiso(nombre='gestionar_roles', descripcion='Gestionar roles del sistema', recurso='rol', accion='gestionar'),
            Permiso(nombre='gestionar_permisos', descripcion='Gestionar permisos del sistema', recurso='permiso', accion='gestionar'),
        ]
        for p in permisos: db.add(p)
        db.commit()
        
        # Asignar permisos a roles
        all_permisos = db.query(Permiso).all()
        admin_rol.permisos = all_permisos
        
        tecnico_permisos = db.query(Permiso).filter((Permiso.nombre.like('%leer%')) | (Permiso.nombre.like('%actualizar%'))).all()
        tecnico_rol.permisos = tecnico_permisos
        
        cliente_permisos = db.query(Permiso).filter(Permiso.accion.in_(['crear', 'leer'])).all()
        cliente_rol.permisos = cliente_permisos
        
        gestor_permisos = db.query(Permiso).filter(Permiso.recurso.in_(['vehiculo', 'usuario'])).all()
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
        print('✅ Base de datos inicializada correctamente')
    except Exception as e:
        print('Error:', e)