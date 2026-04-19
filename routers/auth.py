"""
routers/auth.py - Router con los endpoints de autenticación
Incluye: registro, login y obtención de datos del usuario autenticado
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dataclasses import dataclass, field
from models.database import get_db
from models.user import Usuario, Rol, EstadoCuenta
from schemas.user import UsuarioCreate, UsuarioResponse, LoginData, Token
from schemas.converters import orm_to_dataclass
from security.password import hash_password, verify_password
from security.jwt_handler import create_access_token
from dependencies import get_current_user
from config import get_settings
from typing import List

# Crear el router de autenticación
router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
    responses={
        400: {"description": "Solicitud inválida"},
        401: {"description": "No autorizado"},
        404: {"description": "No encontrado"},
    }
)


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def register(usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Endpoint para registrar un nuevo usuario.
    
    **Requisitos:**
    - El email debe ser único
    - La contraseña debe tener mínimo 8 caracteres
    - El id_rol debe existir en la base de datos
    
    **Pasos:**
    1. Valida que el email no exista
    2. Valida que el rol exista
    3. Hashea la contraseña con bcrypt
    4. Crea y guarda el usuario en la BD
    
    Args:
        usuario_data: Datos del usuario a registrar (UsuarioCreate)
        db: Sesión de base de datos
        
    Returns:
        UsuarioResponse: Datos del usuario creado (sin password_hash)
        
    Raises:
        HTTPException 400: Si el email ya existe o el rol no existe
        
    Ejemplo de request:
        POST /auth/register
        {
            "email": "juan@example.com",
            "telefono": "3001234567",
            "password": "MiContraseña123",
            "id_rol": 1
        }
    """
    
    # 1. Verificar que el email no esté registrado
    usuario_existente = db.query(Usuario).filter(
        Usuario.email == usuario_data.email
    ).first()
    
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # 2. Verificar que el rol exista
    rol = db.query(Rol).filter(Rol.id == usuario_data.id_rol).first()
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El rol con ID {usuario_data.id_rol} no existe"
        )
    
    # 3. Hashear la contraseña
    password_hash = hash_password(usuario_data.password)
    
    # 4. Crear el nuevo usuario
    nuevo_usuario = Usuario(
        email=usuario_data.email,
        telefono=usuario_data.telefono,
        password_hash=password_hash,
        id_rol=usuario_data.id_rol,
        estado_cuenta=EstadoCuenta.ACTIVO
    )
    
    # 5. Guardar en la base de datos
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return orm_to_dataclass(nuevo_usuario, UsuarioResponse)


@router.post("/login", response_model=Token)
def login(credenciales: LoginData, db: Session = Depends(get_db)):
    """
    Endpoint para autenticar un usuario y obtener un token JWT.
    
    **Pasos:**
    1. Busca el usuario por email
    2. Verifica que la contraseña sea correcta
    3. Verifica que la cuenta esté activa
    4. Genera un token JWT
    
    Args:
        credenciales: Email y contraseña del usuario (LoginData)
        db: Sesión de base de datos
        
    Returns:
        Token: Objeto con access_token y token_type
        
    Raises:
        HTTPException 401: Si el email no existe, contraseña es incorrecta o cuenta inactiva
        
    Ejemplo de request:
        POST /auth/login
        {
            "email": "juan@example.com",
            "password": "MiContraseña123"
        }
    """
    
    # 1. Buscar usuario por email
    usuario = db.query(Usuario).filter(
        Usuario.email == credenciales.email
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Verificar contraseña
    if not verify_password(credenciales.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Verificar que la cuenta esté activa
    if usuario.estado_cuenta == EstadoCuenta.INACTIVO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta de este usuario está inactiva"
        )
    
    # 4. Generar token JWT
    access_token = create_access_token(data={"sub": usuario.email})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UsuarioResponse)
def get_current_user_info(current_user: UsuarioResponse = Depends(get_current_user)):
    """
    Endpoint para obtener los datos del usuario autenticado.
    
    **Seguridad:**
    - Requiere un token JWT válido en el header Authorization
    - Solo retorna los datos del usuario autenticado
    
    Args:
        current_user: Usuario autenticado (inyectado por la dependencia)
        
    Returns:
        UsuarioResponse: Datos del usuario autenticado
        
    Raises:
        HTTPException 401: Si el token es inválido o expirado
        HTTPException 403: Si la cuenta está inactiva
        
    Ejemplo de request:
        GET /auth/me
        Headers:
            Authorization: Bearer <token_jwt>
    """
    return current_user


# ============================================================================
# ESQUEMAS PARA SEED DATA
# ============================================================================

@dataclass
class UsuarioTestData:
    """Esquema para datos de usuario de prueba con credenciales"""
    email: str
    password: str
    telefono: str
    id_rol: int
    rol_nombre: str
    descripcion: str


@dataclass
class SeedDataResponse:
    """Respuesta del endpoint de seed con lista de usuarios creados"""
    mensaje: str
    total_usuarios_creados: int
    usuarios: List[UsuarioTestData] = field(default_factory=list)


# ============================================================================
# ENDPOINT: GENERAR DATOS DE PRUEBA
# ============================================================================

@router.post("/seed-test-users", response_model=SeedDataResponse, status_code=201)
def seed_test_users(db: Session = Depends(get_db)):
    """
    Endpoint para generar usuarios de prueba con todos los roles del sistema.
    
    ⚠️ **SOLO DISPONIBLE EN MODO DEBUG**
    
    Este endpoint crea automáticamente 5 usuarios de prueba, uno para cada rol:
    - Admin: Administrador del sistema (acceso completo)
    - Operador: Operador de emergencias (gestión de incidentes)
    - Técnico: Técnico de taller (atención de usuarios)
    - Cliente: Usuario final (reporte de incidentes)
    - Gestor Taller: Gestor de taller (admin de recursos)
    
    **Validaciones:**
    - Solo funciona si DEBUG_MODE=True en config
    - Valida que los usuarios no existan antes de crearlos
    - Si un usuario ya existe, lo omite
    - Devuelve lista de usuarios creados con sus credenciales
    
    **Respuesta:**
    ```json
    {
        "mensaje": "Usuarios de prueba creados exitosamente",
        "total_usuarios_creados": 5,
        "usuarios": [
            {
                "email": "admin@example.com",
                "password": "TestPassword123!",
                "telefono": "3001111111",
                "id_rol": 1,
                "rol_nombre": "admin",
                "descripcion": "Admin del sistema"
            },
            ...
        ]
    }
    ```
    
    Returns:
        SeedDataResponse: Mensaje de éxito y lista de usuarios creados con credenciales
        
    Raises:
        HTTPException 403: Si DEBUG_MODE está deshabilitado (no es desarrollo)
        HTTPException 400: Si ocurre un error al crear usuarios
        
    Ejemplo de request:
        POST /auth/seed-test-users
        (Sin body, no requiere autenticación)
    """
    # Obtener config
    settings = get_settings()
    
    # Verificar que el endpoint solo está disponible en modo debug
    if not settings.debug_mode:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El endpoint /auth/seed-test-users solo está disponible en modo DEBUG. "
                   "Habilita DEBUG_MODE=True en .env para modo desarrollo."
        )
    
    # Definir usuarios de prueba
    usuarios_prueba = [
        {
            "email": "admin@example.com",
            "password": "TestPassword123!",
            "telefono": "3001111111",
            "id_rol": 1,
            "rol_nombre": "admin",
            "descripcion": "Admin del sistema - Acceso completo"
        },
        {
            "email": "operador@example.com",
            "password": "TestPassword123!",
            "telefono": "3002222222",
            "id_rol": 2,
            "rol_nombre": "operador",
            "descripcion": "Operador de emergencias - Gestión de incidentes"
        },
        {
            "email": "tecnico@example.com",
            "password": "TestPassword123!",
            "telefono": "3003333333",
            "id_rol": 3,
            "rol_nombre": "tecnico",
            "descripcion": "Técnico de taller - Atención de usuarios"
        },
        {
            "email": "cliente@example.com",
            "password": "TestPassword123!",
            "telefono": "3004444444",
            "id_rol": 4,
            "rol_nombre": "cliente",
            "descripcion": "Cliente/Usuario final - Reporte de incidentes"
        },
        {
            "email": "gestor_taller@example.com",
            "password": "TestPassword123!",
            "telefono": "3005555555",
            "id_rol": 5,
            "rol_nombre": "gestor_taller",
            "descripcion": "Gestor de taller - Admin de recursos"
        }
    ]
    
    usuarios_creados = []
    
    try:
        for usuario_data in usuarios_prueba:
            # Verificar que el usuario no exista
            usuario_existente = db.query(Usuario).filter(
                Usuario.email == usuario_data["email"]
            ).first()
            
            if usuario_existente:
                print(f"⏭️  Usuario {usuario_data['email']} ya existe, omitiendo...")
                continue
            
            # Verificar que el rol existe
            rol = db.query(Rol).filter(Rol.id == usuario_data["id_rol"]).first()
            if not rol:
                print(f"⚠️  Rol {usuario_data['id_rol']} no existe, omitiendo usuario {usuario_data['email']}")
                continue
            
            # Crear usuario
            password_hash = hash_password(usuario_data["password"])
            nuevo_usuario = Usuario(
                email=usuario_data["email"],
                telefono=usuario_data["telefono"],
                password_hash=password_hash,
                id_rol=usuario_data["id_rol"],
                estado_cuenta=EstadoCuenta.ACTIVO
            )
            
            db.add(nuevo_usuario)
            db.flush()  # Flush para obtener el ID
            
            # Agregar a lista de creados (con credenciales)
            usuarios_creados.append(
                UsuarioTestData(
                    email=usuario_data["email"],
                    password=usuario_data["password"],  # Retornar la contraseña en texto plano SOLO para desarrollo
                    telefono=usuario_data["telefono"],
                    id_rol=usuario_data["id_rol"],
                    rol_nombre=usuario_data["rol_nombre"],
                    descripcion=usuario_data["descripcion"]
                )
            )
            
            print(f"✅ Usuario {usuario_data['email']} creado exitosamente")
        
        # Commit final
        db.commit()
        
        return SeedDataResponse(
            mensaje="Usuarios de prueba creados exitosamente. "
                    "Usa estas credenciales para testear el sistema.",
            total_usuarios_creados=len(usuarios_creados),
            usuarios=usuarios_creados
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear usuarios de prueba: {str(e)}"
        )
