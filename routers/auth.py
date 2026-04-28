# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.user import Usuario
from auth.security import crear_token_acceso
from schemas.user import UsuarioCreate, UsuarioResponse, LoginData, Token
from crud import auth as auth_crud
from fastapi.security import OAuth2PasswordRequestForm
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth",
                   tags=["Autenticación"],
                   responses={
                        400: {"description": "Solicitud inválida"},
                        401: {"description": "No autorizado"},
                        404: {"description": "No encontrado"},
                    }
                )

@router.post("/register", response_model=UsuarioResponse)
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # 1. Verificar si el email ya existe
    db_user = auth_crud.get_usuario_by_email(db, email=usuario.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    # 2. Crear el usuario
    return auth_crud.crear_usuario(db=db, usuario_in=usuario)


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login endpoint. Espera:
    - username: email del usuario
    - password: contraseña en texto plano
    """
    # El email viene como 'username' en OAuth2PasswordRequestForm
    email = form_data.username
    
    logger.info(f"🔐 Intento de login: {email}")
    
    # 1. Buscar el usuario
    user = auth_crud.get_usuario_by_email(db, email=email)
    
    if not user:
        logger.warning(f"❌ Usuario no encontrado: {email}")
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    # 2. Verificar contraseña
    if not auth_crud.verificar_password(form_data.password, user.password_hash):
        logger.warning(f"❌ Contraseña incorrecta para: {email}")
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    # 3. Verificar que el usuario esté activo
    if user.estado_cuenta.value == "INACTIVO":
        logger.warning(f"❌ Usuario inactivo: {email}")
        raise HTTPException(status_code=401, detail="Usuario inactivo")
    
    # 4. Generar token
    logger.info(f"✅ Login exitoso: {email}")
    access_token = crear_token_acceso(
        data={"sub": user.email, "id_usuario": user.id_usuario, "rol": user.rol.nombre}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

from auth.dependencies import get_current_user

@router.get("/me", response_model=UsuarioResponse)
def leer_mi_perfil(current_user: Usuario = Depends(get_current_user)):
    """
    Este endpoint es privado. Solo usuarios con Token válido pueden entrar.
    """
    return current_user