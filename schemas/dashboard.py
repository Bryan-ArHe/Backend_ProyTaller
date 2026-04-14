"""
schemas/dashboard.py - Esquemas Pydantic para respuestas del Dashboard
Define las estructuras de datos que se envían al frontend según el rol del usuario
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class MetricaBase(BaseModel):
    """Estructura base para una métrica"""
    titulo: str = Field(..., description="Título de la métrica")
    valor: Any = Field(..., description="Valor de la métrica")
    icono: Optional[str] = Field(None, description="Nombre del ícono (ej: 'car', 'alert')")
    color: Optional[str] = Field(None, description="Color de la métrica (ej: 'success', 'warning')")


class DashboardAdminResponse(BaseModel):
    """Métricas para usuarios con rol ADMIN"""
    total_usuarios: int = Field(..., description="Total de usuarios registrados")
    usuarios_activos: int = Field(..., description="Usuarios con cuenta activa")
    usuarios_inactivos: int = Field(..., description="Usuarios con cuenta inactiva")
    total_roles: int = Field(..., description="Total de roles disponibles")
    
    metricas_adicionales: Optional[Dict[str, Any]] = Field(
        None, 
        description="Métricas adicionales personalizadas"
    )

    class Config:
        from_attributes = True


class DashboardOperadorResponse(BaseModel):
    """Métricas para usuarios con rol OPERADOR"""
    ordenes_pendientes: int = Field(..., description="Cantidad de órdenes pendientes")
    ordenes_en_proceso: int = Field(..., description="Cantidad de órdenes en proceso")
    ordenes_completadas_hoy: int = Field(..., description="Órdenes completadas hoy")
    tecnicos_disponibles: int = Field(..., description="Técnicos disponibles para asignación")
    
    metricas_adicionales: Optional[Dict[str, Any]] = Field(
        None, 
        description="Métricas adicionales personalizadas"
    )

    class Config:
        from_attributes = True


class DashboardUsuarioResponse(BaseModel):
    """Métricas para usuarios con rol USUARIO (clientes)"""
    vehiculos_registrados: int = Field(..., description="Total de vehículos registrados")
    incidentes_activos: int = Field(..., description="Cantidad de incidentes activos")
    solicitudes_pendientes: int = Field(..., description="Solicitudes pendientes de respuesta")
    ultimo_incidente: Optional[str] = Field(None, description="Fecha del último incidente")
    
    metricas_adicionales: Optional[Dict[str, Any]] = Field(
        None, 
        description="Métricas adicionales personalizadas"
    )

    class Config:
        from_attributes = True


class DashboardTecnicoResponse(BaseModel):
    """Métricas para usuarios con rol TECNICO"""
    orden_asignada: bool = Field(..., description="¿Tiene orden de trabajo asignada?")
    descripcion_orden: Optional[str] = Field(None, description="Descripción de la orden actual")
    tareas_completadas_hoy: int = Field(..., description="Tareas completadas hoy")
    calificacion_promedio: float = Field(..., description="Calificación promedio por clientes")
    
    metricas_adicionales: Optional[Dict[str, Any]] = Field(
        None, 
        description="Métricas adicionales personalizadas"
    )

    class Config:
        from_attributes = True


class DashboardGenericoResponse(BaseModel):
    """Respuesta genérica para roles no específicos o desconocidos"""
    mensaje: str = Field(..., description="Mensaje para el usuario")
    rol: str = Field(..., description="Rol del usuario")
    datos: Optional[Dict[str, Any]] = Field(None, description="Datos genéricos disponibles")

    class Config:
        from_attributes = True


class DashboardErrorResponse(BaseModel):
    """Respuesta de error en el dashboard"""
    detalle: str = Field(..., description="Descripción del error")
    codigo_error: int = Field(..., description="Código de error")

    class Config:
        from_attributes = True


# Unión de tipos para respuesta flexible
DashboardResponse = (
    DashboardAdminResponse | 
    DashboardOperadorResponse | 
    DashboardUsuarioResponse | 
    DashboardTecnicoResponse | 
    DashboardGenericoResponse
)
