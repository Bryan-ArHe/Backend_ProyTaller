"""
routers/roles.py - Router para gestión de roles y permisos
Módulo 1: Identidad y Accesos - Endpoints para administración de matriz de Roles y Permisos
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.user import Usuario
from schemas.user import (
    RolConPermisosResponse,
    PermisoResponse,
    ActualizarPermisosRequest,
)
from schemas.converters import orm_to_dataclass
from dependencies import get_current_user
from crud import roles as crud_roles
from typing import List

# Crear el router de roles
router = APIRouter(
    prefix="/roles",
    tags=["Roles y Permisos"],
    responses={
        401: {"description": "No autorizado"},
        403: {"description": "Acceso denegado - solo administrador"},
        404: {"description": "Rol o Permiso no encontrado"},
    }
)


@router.get("/", response_model=List[RolConPermisosResponse])
def listar_roles(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    GET /roles/
    
    Lista todos los roles del sistema con sus permisos anidados.
    Útil para la matriz de administración de Roles y Permisos.
    
    **Protección:** Requiere token JWT válido
    
    **Retorna:**
        - List[RolConPermisosResponse]: Lista de roles con permisos anidados
    
    **Estructura de respuesta:**
        [
            {
                "id_rol": 1,
                "nombre": "admin",
                "descripcion": "Administrador del sistema",
                "permisos": [
                    {
                        "id_permiso": 1,
                        "nombre": "crear_usuario",
                        "descripcion": "Crear nuevo usuario",
                        "recurso": "usuario",
                        "accion": "crear"
                    },
                    ...
                ]
            },
            ...
        ]
    
    **Errores:**
        - 401 Unauthorized: Token inválido o expirado
    """
    roles = crud_roles.get_all_roles(db)
    
    # Convertir a dataclass
    respuesta = [
        RolConPermisosResponse(
            id_rol=rol.id_rol,
            nombre=rol.nombre,
            descripcion=rol.descripcion,
            permisos=[
                PermisoResponse(
                    id_permiso=p.id_permiso,
                    nombre=p.nombre,
                    descripcion=p.descripcion,
                    recurso=p.recurso,
                    accion=p.accion,
                )
                for p in rol.permisos
            ]
        )
        for rol in roles
    ]
    
    return respuesta


@router.get("/permisos", response_model=List[PermisoResponse])
def listar_permisos(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    GET /roles/permisos
    
    Retorna el catálogo completo de permisos disponibles en el sistema.
    Usado para el frontend al construir la matriz de Roles y Permisos.
    
    **Protección:** Requiere token JWT válido
    
    **Retorna:**
        - List[PermisoResponse]: Todos los permisos del sistema
    
    **Estructura de respuesta:**
        [
            {
                "id_permiso": 1,
                "nombre": "crear_usuario",
                "descripcion": "Crear nuevo usuario",
                "recurso": "usuario",
                "accion": "crear"
            },
            {
                "id_permiso": 2,
                "nombre": "leer_usuario",
                "descripcion": "Leer datos de usuario",
                "recurso": "usuario",
                "accion": "leer"
            },
            ...
        ]
    
    **Errores:**
        - 401 Unauthorized: Token inválido o expirado
    """
    permisos = crud_roles.get_all_permisos(db)
    
    respuesta = [
        PermisoResponse(
            id_permiso=p.id_permiso,
            nombre=p.nombre,
            descripcion=p.descripcion,
            recurso=p.recurso,
            accion=p.accion,
        )
        for p in permisos
    ]
    
    return respuesta


@router.put("/{id_rol}/permisos", response_model=RolConPermisosResponse)
def actualizar_permisos_rol(
    id_rol: int,
    datos: ActualizarPermisosRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    PUT /roles/{id_rol}/permisos
    
    Actualiza los permisos asignados a un rol específico.
    **SOLO ADMINISTRADOR puede acceder.**
    
    **Protección:** 
        - Requiere token JWT válido
        - Solo usuarios con rol 'admin' pueden acceder
    
    **Parámetros:**
        - id_rol (path): ID del rol a actualizar
        - datos (body): { "permisos_ids": [1, 2, 3, ...] }
    
    **Pasos:**
        1. Valida que el usuario sea administrador
        2. Verifica que el rol exista
        3. Obtiene los permisos por sus IDs
        4. Limpia los permisos actuales del rol
        5. Asigna los nuevos permisos
        6. Retorna el rol actualizado con sus permisos
    
    **Retorna:**
        - RolConPermisosResponse: Rol actualizado con la nueva lista de permisos
    
    **Estructura de solicitud:**
        {
            "permisos_ids": [1, 2, 5, 7, 10]
        }
    
    **Estructura de respuesta:**
        {
            "id_rol": 2,
            "nombre": "tecnico",
            "descripcion": "Técnico de servicio",
            "permisos": [
                {
                    "id_permiso": 1,
                    "nombre": "crear_usuario",
                    "descripcion": "Crear nuevo usuario",
                    "recurso": "usuario",
                    "accion": "crear"
                },
                ...
            ]
        }
    
    **Errores:**
        - 401 Unauthorized: Token inválido o expirado
        - 403 Forbidden: Usuario no es administrador
        - 404 Not Found: Rol no existe
        - 400 Bad Request: Alguno de los permisos no existe
    
    **Ejemplo cURL:**
        curl -X PUT http://localhost:8000/roles/2/permisos \\
            -H "Authorization: Bearer <token>" \\
            -H "Content-Type: application/json" \\
            -d '{"permisos_ids": [1, 2, 5, 7]}'
    """
    # Obtener el usuario actual de la BD con su rol
    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == current_user["id_usuario"]
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Validar que sea administrador
    # Buscar el rol del usuario en la BD
    if usuario.rol.nombre.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden actualizar permisos de roles"
        )
    
    try:
        # Actualizar los permisos del rol
        rol_actualizado = crud_roles.actualizar_permisos_rol(
            db=db,
            id_rol=id_rol,
            permisos_ids=datos.permisos_ids
        )
        
        if not rol_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol con ID {id_rol} no encontrado"
            )
        
        # Convertir a dataclass
        respuesta = RolConPermisosResponse(
            id_rol=rol_actualizado.id_rol,
            nombre=rol_actualizado.nombre,
            descripcion=rol_actualizado.descripcion,
            permisos=[
                PermisoResponse(
                    id_permiso=p.id_permiso,
                    nombre=p.nombre,
                    descripcion=p.descripcion,
                    recurso=p.recurso,
                    accion=p.accion,
                )
                for p in rol_actualizado.permisos
            ]
        )
        
        return respuesta
        
    except ValueError as e:
        # Error validando permisos
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
