"""
Funciones auxiliares para registrar eventos en la bitácora
"""
from sqlalchemy.orm import Session
from fastapi import Request
from schemas.bitacora import BitacoraCreate
from crud import bitacora as crud_bitacora


def obtener_ip_cliente(request: Request) -> str:
    """
    Obtiene la dirección IP del cliente.
    Considera proxies (X-Forwarded-For) y conexión directa.
    """
    if request.headers.get('x-forwarded-for'):
        return request.headers.get('x-forwarded-for').split(',')[0].strip()
    return request.client.host


def registrar_evento_bitacora(
    db: Session,
    request: Request,
    id_usuario: int,
    nombre_usuario: str,
    evento: str,
    recurso: str,
    accion: str,
    payload: str = None,
    dispositivo: str = None
) -> None:
    """
    Registra un evento en la bitácora.
    
    Args:
        db: Sesión de base de datos
        request: Objeto Request de FastAPI (para obtener IP y endpoint)
        id_usuario: ID del usuario que realiza la acción
        nombre_usuario: Nombre del usuario (para registro rápido)
        evento: Tipo de evento (ej: "login", "crear", "actualizar", "eliminar")
        recurso: Recurso afectado (ej: "usuario", "incidente", "vehículo")
        accion: Descripción de la acción realizada
        payload: Datos adicionales (JSON en string, opcional)
        dispositivo: Tipo de dispositivo (opcional)
    """
    try:
        ip = obtener_ip_cliente(request)
        endpoint = str(request.url.path)
        
        datos_bitacora = BitacoraCreate(
            id_usuario=id_usuario,
            nombre_usuario=nombre_usuario,
            evento=evento,
            recurso=recurso,
            accion=accion,
            ip=ip,
            endpoint=endpoint,
            payload=payload,
            dispositivo=dispositivo
        )
        
        crud_bitacora.crear_bitacora(db, datos_bitacora)
        db.commit()  # Commit de la transacción
    except Exception as e:
        # Log del error pero no interrumpe la ejecución
        print(f"Error al registrar evento en bitácora: {str(e)}")
