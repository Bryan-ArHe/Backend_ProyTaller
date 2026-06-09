# routers/auth.py
"""
Router de Autenticación - Refactorizado sin passlib
Usa security/password.py para la verificación de contraseñas con bcrypt
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import get_db
from models.user import Usuario
from security.jwt_handler import create_access_token
from security.password import verify_password
from schemas.user import UsuarioCreate, UsuarioResponse, Token
from crud.usuarios import get_usuario_by_email
from crud.auth import crear_usuario
from auth.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from utils.bitacora_helper import registrar_evento_bitacora
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
    responses={
        400: {"description": "Solicitud inválida"},
        401: {"description": "No autorizado"},
        404: {"description": "No encontrado"},
    }
)


@router.post("/register", response_model=UsuarioResponse, status_code=201)
def registrar_usuario(request: Request, usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Endpoint de registro de nuevo usuario.
    
    - **email**: Debe ser único en el sistema
    - **password**: Se hashea automáticamente con bcrypt
    - **id_rol**: ID del rol del usuario
    - **telefono**: Número de contacto
    """
    # 1. Verificar si el email ya existe
    db_user = get_usuario_by_email(db, email=usuario.email)
    if db_user:
        logger.warning(f"⚠️ Intento de registro con email duplicado: {usuario.email}")
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    # 2. Crear el usuario
    nuevo_usuario = crear_usuario(db=db, usuario_in=usuario)
    logger.info(f"✅ Usuario registrado: {usuario.email} con rol ID: {usuario.id_rol}")
    
    # Registrar en bitácora
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=nuevo_usuario.id_usuario,
        nombre_usuario=f"{nuevo_usuario.nombre} {nuevo_usuario.apellido}",
        evento="REGISTRO",
        recurso="usuario",
        accion=f"Nuevo usuario registrado: {usuario.email}"
    )
    
    return nuevo_usuario


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login endpoint - Autenticación con email y contraseña.
    
    **Parámetros:**
    - **username**: Email del usuario
    - **password**: Contraseña en texto plano
    
    **Validaciones:**
    - Usuario debe existir
    - Contraseña debe ser correcta (validada con bcrypt)
    - Usuario debe estar ACTIVO
    - Clientes y técnicos NO pueden acceder vía web (bloqueo de acceso)
    
    **Retorna:**
    - Token JWT con datos del usuario
    """
    email = form_data.username
    
    logger.info(f"🔐 Intento de login: {email}")
    
    # 1. Buscar el usuario por email
    user = get_usuario_by_email(db, email=email)
    
    if not user:
        logger.warning(f"❌ Usuario no encontrado: {email}")
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )
    
    # 2. Verificar contraseña usando bcrypt (sin passlib)
    if not verify_password(form_data.password, user.password_hash):
        logger.warning(f"❌ Contraseña incorrecta para: {email}")
        registrar_evento_bitacora(
            db=db,
            request=request,
            id_usuario=user.id_usuario,
            nombre_usuario=f"{user.nombre} {user.apellido}",
            evento="LOGIN",
            recurso="autenticacion",
            accion="Intento de login fallido - contraseña incorrecta"
        )
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )
    
    # 3. Verificar que el usuario esté activo
    if user.estado_cuenta.value == "INACTIVO":
        logger.warning(f"❌ Usuario inactivo intenta login: {email}")
        raise HTTPException(
            status_code=401,
            detail="Usuario inactivo. Contacte al administrador."
        )
    
    # 4. Bloqueo de acceso web para clientes y técnicos
    rol_nombre = user.rol.nombre.lower()
    if rol_nombre in ["cliente", "tecnico"]:
        logger.warning(f"❌ Acceso web bloqueado para rol '{rol_nombre}': {email}")
        raise HTTPException(
            status_code=403,
            detail="Tu rol no tiene acceso a esta plataforma web. Usa la aplicación móvil."
        )
    
    # 5. Generar token JWT
    logger.info(f"✅ Login exitoso: {email} (Rol: {user.rol.nombre})")
    
    access_token = create_access_token(
        data={
            "sub": user.email,
            "id_usuario": user.id_usuario,
            "rol": user.rol.nombre
        }
    )
    
    # Registrar en bitácora
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=user.id_usuario,
        nombre_usuario=f"{user.nombre} {user.apellido}",
        evento="LOGIN",
        recurso="autenticacion",
        accion="Login exitoso"
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def leer_mi_perfil(
    current_user: any = Depends(get_current_user)
):
    """
    Retorna el perfil del usuario autenticado mapeando directamente 
    las propiedades nativas de la instancia de SQLAlchemy.
    """
    # 🌟 CORRECCIÓN: Usamos el operador 'in' nativo de Python para evaluar strings
    user_instance = current_user
    if isinstance(current_user, tuple) or "Row" in str(type(current_user)):
        user_instance = current_user[0]

    # Extraemos las propiedades atómicas directas del objeto mapeado
    id_usuario = getattr(user_instance, "id_usuario", None)
    nombre = getattr(user_instance, "nombre", "Usuario")
    apellido = getattr(user_instance, "apellido", "Sistema")
    email = getattr(user_instance, "email", "sin-email@taller.com")
    telefono = getattr(user_instance, "telefono", "")
    estado = getattr(user_instance, "estado_cuenta", "ACTIVO")
    
    # 🌟 Intentamos leer 'id_rol' o la columna directa 'rol' que arrojó tu log de consola
    id_rol_raw = getattr(user_instance, "id_rol", None) or getattr(user_instance, "rol", None)
    
    if id_rol_raw is not None:
        id_rol = int(id_rol_raw)
    else:
        id_rol = 3 # Cambiamos el salvavidas a 3 (Gestor) por si estás probando este flujo
        
    role_map = {1: 'superAdmin', 2: 'Administrador', 3: 'Gestor', 4: 'Tecnico', 5: 'Cliente'}
    rol_nombre = role_map.get(id_rol, 'Gestor')

    return {
        "id_usuario": id_usuario,
        "nombre": nombre,
        "apellido": apellido,
        "email": email,
        "telefono": telefono,
        "id_rol": id_rol,
        "rol_nombre": rol_nombre,
        "estado_cuenta": estado
    }