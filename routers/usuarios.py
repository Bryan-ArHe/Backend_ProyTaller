"""
routers/usuarios.py - Router para gestión de perfiles y administración de usuarios
Módulo 1: Identidad y Accesos - Endpoints para CRUD de usuarios y perfiles
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload
from models.database import get_db
from models.user import Usuario, Rol, EstadoCuenta
from schemas.user import (
    UsuarioResponse,
    UsuarioUpdate,
    UsuarioCreate,
    UsuarioRolUpdate,
)
from auth.dependencies import get_current_user, check_permissions
from crud import usuarios as crud_usuarios
from utils.bitacora_helper import registrar_evento_bitacora
from security.password import hash_password
from typing import List

# Crear el router de usuarios
router = APIRouter(
    prefix="/usuarios",
    tags=["Gestion de Usuarios"],
    responses={
        401: {"description": "No autorizado"},
        403: {"description": "Acceso denegado"},
        404: {"description": "Usuario no encontrado"},
    }
)


@router.put("/me", response_model=UsuarioResponse)
def update_current_profile(
    usuario_data: UsuarioUpdate,
    request: Request,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    
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
    
    # Registrar evento en bitácora
    cambios = []
    if usuario_data.nombre:
        cambios.append(f"nombre='{usuario_data.nombre}'")
    if usuario_data.apellido:
        cambios.append(f"apellido='{usuario_data.apellido}'")
    if usuario_data.telefono:
        cambios.append(f"teléfono='{usuario_data.telefono}'")
    if usuario_data.password:
        cambios.append("contraseña=actualizada")
    
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=current_user.id_usuario,
        nombre_usuario=f"{current_user.nombre} {current_user.apellido}",
        evento="UPDATE",
        recurso="PERFIL",
        accion=f"Actualizó su perfil: {', '.join(cambios) if cambios else 'sin cambios'}"
    )
    
    return UsuarioResponse.model_validate(usuario_actualizado)


@router.get("/me", response_model=UsuarioResponse)
def get_current_profile(
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtiene los datos del perfil del usuario autenticado.
    
    Retorna todos los datos del usuario actual incluyendo rol y permisos.
    """
    # Buscar el usuario actual en la BD con todas sus relaciones cargadas
    usuario = db.query(Usuario).options(
        joinedload(Usuario.rol)
    ).filter(Usuario.id_usuario == current_user.id_usuario).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return UsuarioResponse.model_validate(usuario)


@router.get("/", response_model=List[UsuarioResponse])
def list_all_users(
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    
    # Verificar que el usuario actual sea administrador
    if current_user.rol.nombre != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden listar usuarios"
        )
    
    # Obtener todos los usuarios con sus roles cargados
    usuarios = db.query(Usuario).options(
        joinedload(Usuario.rol)
    ).all()
    
    # Convertir a UsuarioResponse
    return [
        UsuarioResponse.model_validate(usuario)
        for usuario in usuarios
    ]


@router.patch("/{usuario_id}/estado", response_model=UsuarioResponse)
def update_user_estado(
    usuario_id: int,
    estado_data: UsuarioUpdate,
    request: Request,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    
    # Verificar que el usuario actual sea administrador
    if current_user.rol.nombre != "Administrador":
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
    
    # Guardar el estado anterior
    estado_anterior = usuario.estado_cuenta.value
    
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
    
    # Registrar evento en bitácora
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=current_user.id_usuario,
        nombre_usuario=f"{current_user.nombre} {current_user.apellido}",
        evento="UPDATE",
        recurso="USUARIO",
        accion=f"Cambió estado del usuario '{usuario.email}' de {estado_anterior} a {usuario.estado_cuenta.value}"
    )
    
    # Recargar el usuario con su rol cargado con joinedload
    usuario = db.query(Usuario).options(
        joinedload(Usuario.rol)
    ).filter(Usuario.id_usuario == usuario_id).first()
    
    return UsuarioResponse.model_validate(usuario)


@router.patch("/{usuario_id}/rol", response_model=UsuarioResponse)
def update_user_rol(
    usuario_id: int,
    rol_data: UsuarioRolUpdate,  # 🌟 SOLUCIÓN AL ATTRIBUTE-ERROR: Ahora sí tiene id_rol
    request: Request,
    current_user: Usuario = Depends(get_current_user),  # 🛡️ TIPADO CORREGIDO: Viene el modelo ORM de SQLAlchemy
    db: Session = Depends(get_db),
):
    
    # 1. Verificar que el usuario actual sea administrador
    # Obtenemos de forma segura el nombre del rol del usuario autenticado
    rol_actual_nombre = current_user.rol.nombre if current_user.rol else ""
    
    # Damos soporte tanto a "Administrador" como a tu variación "Admistrador"
    if rol_actual_nombre not in ["Administrador", "Admistrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden cambiar roles de usuarios"
        )
    
    # 2. Buscar el usuario a actualizar
    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == usuario_id
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    # 3. Verificar que el nuevo rol exista en el catálogo físico
    rol = db.query(Rol).filter(Rol.id_rol == rol_data.id_rol).first()
    
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rol con ID {rol_data.id_rol} no encontrado"
        )
    
    # Guardar el rol anterior antes del cambio para auditarlo
    rol_anterior = usuario.rol.nombre if usuario.rol else "desconocido"
    
    # 4. Actualizar la clave foránea en caliente
    usuario.id_rol = rol_data.id_rol
    
    # Guardar cambios en la base de datos
    db.commit()
    
    # 5. Registrar evento en bitácora de forma segura
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=current_user.id_usuario,
        nombre_usuario=f"{current_user.nombre} {current_user.apellido}",
        evento="UPDATE",
        recurso="USUARIO",
        accion=f"Cambió rol del usuario '{usuario.email}' de {rol_anterior} a {rol.nombre}"
    )
    
    # 6. Recargar el usuario con su nueva relación de rol usando joinedload
    usuario_actualizado = db.query(Usuario).options(
        joinedload(Usuario.rol)
    ).filter(Usuario.id_usuario == usuario_id).first()
    
    # Pydantic v2 usa model_validate en lugar de from_orm
    return UsuarioResponse.model_validate(usuario_actualizado)


# ============================================================================
# ENDPOINTS: ADMINISTRACIÓN DE USUARIOS (SOLO ADMIN)
# ============================================================================

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario_admin(
    usuario_data: UsuarioCreate,
    request: Request,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verificar que el usuario actual sea administrador
    if current_user.rol.nombre != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden crear nuevos usuarios"
        )
    
    # Verificar que el email no esté registrado
    usuario_existente = db.query(Usuario).filter(
        Usuario.email == usuario_data.email
    ).first()
    
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El email '{usuario_data.email}' ya está registrado"
        )
    
    # Verificar que el rol exista
    rol = db.query(Rol).filter(Rol.id_rol == usuario_data.id_rol).first()
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El rol con ID {usuario_data.id_rol} no existe"
        )
    
    # Hashear la contraseña (truncar a 72 bytes en UTF-8)
    password_truncated = usuario_data.password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    password_hash = hash_password(password_truncated)
    
    # Crear el nuevo usuario
    nuevo_usuario = Usuario(
        nombre=usuario_data.nombre,
        apellido=usuario_data.apellido,
        email=usuario_data.email,
        telefono=usuario_data.telefono,
        password_hash=password_hash,
        id_rol=usuario_data.id_rol,
        estado_cuenta=EstadoCuenta.ACTIVO
    )
    
    # Guardar en la base de datos
    db.add(nuevo_usuario)
    db.flush()
    
    # Registrar evento CREATE en bitácora
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=current_user.id_usuario,
        nombre_usuario=f"{current_user.nombre} {current_user.apellido}",
        evento="CREATE",
        recurso="USUARIO",
        accion=f"Admin creó nuevo usuario: {nuevo_usuario.email} (Rol: {rol.nombre})"
    )
    
    db.commit()
    db.refresh(nuevo_usuario)
    
    # Cargar el rol para la respuesta
    nuevo_usuario = db.query(Usuario).options(
        joinedload(Usuario.rol)
    ).filter(Usuario.id_usuario == nuevo_usuario.id_usuario).first()
    
    return UsuarioResponse.model_validate(nuevo_usuario)


@router.put("/{usuario_id}", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
def actualizar_usuario_admin(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    request: Request,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
   
    # Verificar que el usuario actual sea administrador
    if current_user.rol.nombre != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden actualizar usuarios"
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
    
    # Rastrear cambios
    cambios = []
    
    # Actualizar nombre
    if usuario_data.nombre:
        cambios.append(f"nombre: '{usuario.nombre}' → '{usuario_data.nombre}'")
        usuario.nombre = usuario_data.nombre
    
    # Actualizar apellido
    if usuario_data.apellido:
        cambios.append(f"apellido: '{usuario.apellido}' → '{usuario_data.apellido}'")
        usuario.apellido = usuario_data.apellido
    
    # Actualizar teléfono
    if usuario_data.telefono:
        cambios.append(f"teléfono: '{usuario.telefono}' → '{usuario_data.telefono}'")
        usuario.telefono = usuario_data.telefono
    
    # Actualizar contraseña
    if usuario_data.password:
        cambios.append("contraseña: *** → ***")
        password_truncated = usuario_data.password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        usuario.password_hash = hash_password(password_truncated)
    
    # Guardar cambios
    db.commit()
    
    # Registrar evento en bitácora
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=current_user.id_usuario,
        nombre_usuario=f"{current_user.nombre} {current_user.apellido}",
        evento="UPDATE",
        recurso="USUARIO",
        accion=f"Admin actualizó usuario '{usuario.email}': {', '.join(cambios) if cambios else 'sin cambios'}"
    )
    
    # Recargar el usuario con su rol cargado
    usuario = db.query(Usuario).options(
        joinedload(Usuario.rol)
    ).filter(Usuario.id_usuario == usuario_id).first()
    
    return UsuarioResponse.model_validate(usuario)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario_admin(
    usuario_id: int,
    request: Request,
    current_user: UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    
    # Verificar que el usuario actual sea administrador
    if current_user.rol.nombre != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden eliminar usuarios"
        )
    
    # Buscar el usuario a eliminar
    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == usuario_id
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    # Validar que no sea el propio administrador
    if usuario_id == current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propio usuario"
        )
    
    # Guardar datos del usuario para el registro
    email_usuario = usuario.email
    nombre_usuario = f"{usuario.nombre} {usuario.apellido}"
    
    # Eliminar el usuario
    db.delete(usuario)
    db.commit()
    
    # Registrar evento DELETE en bitácora
    registrar_evento_bitacora(
        db=db,
        request=request,
        id_usuario=current_user.id_usuario,
        nombre_usuario=f"{current_user.nombre} {current_user.apellido}",
        evento="DELETE",
        recurso="USUARIO",
        accion=f"Admin eliminó usuario: {email_usuario} ({nombre_usuario})"
    )
    
    return None
