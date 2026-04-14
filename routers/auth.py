"""
routers/auth.py - Router con los endpoints de autenticación
Incluye: registro, login y obtención de datos del usuario autenticado
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.user import Usuario, Rol, EstadoCuenta
from schemas.user import UsuarioCreate, UsuarioResponse, LoginData, Token
from security.password import hash_password, verify_password
from security.jwt_handler import create_access_token
from dependencies import get_current_user

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
    
    return UsuarioResponse.from_orm(nuevo_usuario)


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
