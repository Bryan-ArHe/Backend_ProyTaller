"""
routers/usuarios.py - Router para gestión de perfiles y administración de usuarios
Módulo 1: Identidad y Accesos - Endpoints para CRUD de usuarios y perfiles
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from models.database import get_db
from models.user import Usuario, Rol, EstadoCuenta
from schemas.user import (
    UsuarioResponse,
    UsuarioUpdate,
    UsuarioEstadoUpdate,
    UsuarioRolUpdate,
    UsuarioAdminResponse,
)
from schemas.converters import orm_to_dataclass
from dependencies import get_current_user
from crud import usuarios as crud_usuarios
from typing import List

# Crear el router de usuarios
router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
    responses={
        401: {"description": "No autorizado"},
        403: {"description": "Acceso denegado"},
        404: {"description": "Usuario no encontrado"},
    }
)


@router.get("/me", response_model=UsuarioResponse)
def get_current_profile(
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    GET /usuarios/me
    
    Obtiene el perfil del usuario autenticado.
    
    **Protección:** Requiere token JWT válido
    
    **Retorna:**
        - UsuarioResponse: Datos del usuario autenticado (email, teléfono, rol, etc.)
    
    **Errores:**
        - 401 Unauthorized: Token inválido o expirado
        - 403 Forbidden: Cuenta inactiva
    
    **Ejemplo:**
        GET /usuarios/me
        Headers: Authorization: Bearer <token>
        
        Response 200:
        {
            "id_usuario": 3,
            "email": "cliente@example.com",
            "telefono": "3004",
            "estado_cuenta": "ACTIVO",
            "id_rol": 3,
            "fecha_registro": "2026-04-19T19:50:05.105097",
            "rol": {
                "id_rol": 3,
                "nombre": "cliente",
                "descripcion": "Cliente"
            }
        }
    """
    return current_user


@router.put("/me", response_model=UsuarioResponse)
def update_current_profile(
    usuario_data: UsuarioUpdate,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    PUT /usuarios/me
    
    Permite que el usuario autenticado actualice su propio perfil.
    Soporta actualización de teléfono y contraseña (ambos opcionales).
    
    **Protección:** Requiere token JWT válido
    
    **Parámetros de entrada:**
        - telefono (opcional): Nuevo número de teléfono
        - password (opcional): Nueva contraseña (mínimo 8 caracteres)
    
    **Pasos:**
        1. Obtiene el usuario actual de la BD usando get_current_user
        2. Valida que el usuario exista
        3. Actualiza los campos proporcionados
        4. Si password se proporciona, lo hashea y actualiza
        5. Hace commit de los cambios
        6. Devuelve el usuario actualizado
    
    **Retorna:**
        - UsuarioResponse: Usuario con los datos actualizados
    
    **Errores:**
        - 401 Unauthorized: Token inválido o expirado
        - 403 Forbidden: Cuenta inactiva
        - 404 Not Found: Usuario no encontrado en la BD
    
    **Ejemplo con solo teléfono:**
        PUT /usuarios/me
        Headers: Authorization: Bearer <token>
        Body:
        {
            "telefono": "3001234567"
        }
    
    **Ejemplo con teléfono y contraseña:**
        PUT /usuarios/me
        Headers: Authorization: Bearer <token>
        Body:
        {
            "telefono": "3001234567",
            "password": "NuevaContraseña123"
        }
    
    **Ejemplo vacío (sin cambios):**
        PUT /usuarios/me
        Headers: Authorization: Bearer <token>
        Body:
        {
            "telefono": null,
            "password": null
        }
        
        Response 200: (UsuarioResponse sin cambios)
    """
    # Buscar el usuario actual en la BD
    usuario = crud_usuarios.get_usuario_by_id(db, current_user.id_usuario)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Actualizar el usuario usando la función CRUD
    # que valida automáticamente el password opcional
    usuario_actualizado = crud_usuarios.update_usuario(
        db=db,
        usuario_id=current_user.id_usuario,
        datos=usuario_data
    )
    
    return orm_to_dataclass(usuario_actualizado, UsuarioResponse)


@router.get("/", response_model=List[UsuarioAdminResponse])
def list_all_users(
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    GET /usuarios/
    
    Lista todos los usuarios del sistema.
    **Solo accesible para administradores.**
    
    **Protección:** 
        - Requiere token JWT válido
        - Solo usuarios con rol 'admin' pueden acceder
    
    **Pasos:**
        1. Verifica que el usuario actual sea administrador
        2. Obtiene todos los usuarios con joinedload para traer los datos del rol
        3. Retorna lista de UsuarioAdminResponse
    
    **Retorna:**
        - List[UsuarioAdminResponse]: Lista de todos los usuarios con sus roles
    
    **Errores:**
        - 401 Unauthorized: Token inválido o expirado
        - 403 Forbidden: Usuario no es administrador
    
    **Ejemplo:**
        GET /usuarios/
        Headers: Authorization: Bearer <admin_token>
        
        Response 200:
        [
            {
                "id_usuario": 1,
                "email": "admin@example.com",
                "telefono": "3001",
                "estado_cuenta": "ACTIVO",
                "id_rol": 1,
                "fecha_registro": "2026-04-19T19:49:40.930000",
                "rol": {
                    "id_rol": 1,
                    "nombre": "admin",
                    "descripcion": "Administrador"
                }
            },
            ...
        ]
    """
    # Verificar que el usuario actual sea administrador
    if current_user.rol.nombre.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden listar usuarios"
        )
    
    # Obtener todos los usuarios con sus roles cargados
    usuarios = db.query(Usuario).options(
        joinedload(Usuario.rol)
    ).all()
    
    # Convertir a UsuarioAdminResponse
    return [
        orm_to_dataclass(usuario, UsuarioAdminResponse)
        for usuario in usuarios
    ]


@router.patch("/{usuario_id}/estado", response_model=UsuarioAdminResponse)
def update_user_estado(
    usuario_id: int,
    estado_data: UsuarioEstadoUpdate,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    PATCH /usuarios/{usuario_id}/estado
    
    Permite al administrador cambiar el estado de la cuenta de un usuario.
    
    **Protección:**
        - Requiere token JWT válido
        - Solo usuarios con rol 'admin' pueden acceder
    
    **Parámetros:**
        - usuario_id (path): ID del usuario cuyo estado se va a cambiar
        - estado_account (body): Nuevo estado ('ACTIVO' o 'INACTIVO')
    
    **Pasos:**
        1. Verifica que el usuario actual sea administrador
        2. Busca el usuario por ID
        3. Valida que el nuevo estado sea válido
        4. Actualiza el estado
        5. Hace commit y refresh
        6. Retorna el usuario actualizado
    
    **Retorna:**
        - UsuarioAdminResponse: Usuario con el estado actualizado
    
    **Errores:**
        - 401 Unauthorized: Token inválido o expirado
        - 403 Forbidden: Usuario no es administrador
        - 404 Not Found: Usuario con ese ID no existe
    
    **Ejemplo:**
        PATCH /usuarios/5/estado
        Headers: Authorization: Bearer <admin_token>
        Body:
        {
            "estado_cuenta": "INACTIVO"
        }
        
        Response 200: (UsuarioAdminResponse con nuevo estado)
    """
    # Verificar que el usuario actual sea administrador
    if current_user.rol.nombre.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden cambiar el estado de usuarios"
        )
    
    # Buscar el usuario a actualizar
    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == usuario_id
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    # Actualizar el estado
    if estado_data.estado_cuenta == "ACTIVO":
        usuario.estado_cuenta = EstadoCuenta.ACTIVO
    elif estado_data.estado_cuenta == "INACTIVO":
        usuario.estado_cuenta = EstadoCuenta.INACTIVO
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado inválido. Debe ser 'ACTIVO' o 'INACTIVO'"
        )
    
    # Guardar cambios
    db.commit()
    db.refresh(usuario)
    
    # Recargar el rol para la respuesta
    db.refresh(usuario, attribute_names=['rol'])
    
    return orm_to_dataclass(usuario, UsuarioAdminResponse)


@router.patch("/{usuario_id}/rol", response_model=UsuarioAdminResponse)
def update_user_rol(
    usuario_id: int,
    rol_data: UsuarioRolUpdate,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    PATCH /usuarios/{usuario_id}/rol
    
    Permite al administrador cambiar el rol de un usuario.
    
    **Protección:**
        - Requiere token JWT válido
        - Solo usuarios con rol 'admin' pueden acceder
    
    **Parámetros:**
        - usuario_id (path): ID del usuario cuyo rol se va a cambiar
        - id_rol (body): ID del nuevo rol
    
    **Pasos:**
        1. Verifica que el usuario actual sea administrador
        2. Busca el usuario por ID
        3. Verifica que el rol exista
        4. Actualiza el id_rol del usuario
        5. Hace commit y refresh
        6. Retorna el usuario actualizado
    
    **Retorna:**
        - UsuarioAdminResponse: Usuario con el nuevo rol
    
    **Errores:**
        - 401 Unauthorized: Token inválido o expirado
        - 403 Forbidden: Usuario no es administrador
        - 404 Not Found: Usuario o rol no encontrado
    
    **Ejemplo:**
        PATCH /usuarios/5/rol
        Headers: Authorization: Bearer <admin_token>
        Body:
        {
            "id_rol": 2
        }
        
        Response 200: (UsuarioAdminResponse con nuevo rol)
    """
    # Verificar que el usuario actual sea administrador
    if current_user.rol.nombre.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden cambiar roles de usuarios"
        )
    
    # Buscar el usuario a actualizar
    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == usuario_id
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    # Verificar que el rol exista
    rol = db.query(Rol).filter(Rol.id_rol == rol_data.id_rol).first()
    
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rol con ID {rol_data.id_rol} no encontrado"
        )
    
    # Actualizar el rol
    usuario.id_rol = rol_data.id_rol
    
    # Guardar cambios
    db.commit()
    db.refresh(usuario)
    
    # Recargar el rol para la respuesta
    db.refresh(usuario, attribute_names=['rol'])
    
    return orm_to_dataclass(usuario, UsuarioAdminResponse)
