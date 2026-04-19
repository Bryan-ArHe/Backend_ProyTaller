"""
schemas/dashboard.py - Esquemas con Dataclasses para respuestas del Dashboard
Define las estructuras de datos que se envían al frontend según el rol del usuario
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


@dataclass
class MetricaBase:
    """Estructura base para una métrica"""
    titulo: str
    valor: Any
    icono: Optional[str] = None
    color: Optional[str] = None


@dataclass
class DashboardAdminResponse:
    """Métricas para usuarios con rol ADMIN"""
    total_usuarios: int
    usuarios_activos: int
    usuarios_inactivos: int
    total_roles: int
    metricas_adicionales: Optional[Dict[str, Any]] = None


@dataclass
class DashboardOperadorResponse:
    """Métricas para usuarios con rol OPERADOR"""
    ordenes_pendientes: int
    ordenes_en_proceso: int
    ordenes_completadas_hoy: int
    tecnicos_disponibles: int
    metricas_adicionales: Optional[Dict[str, Any]] = None


@dataclass
class DashboardUsuarioResponse:
    """Métricas para usuarios con rol USUARIO (clientes)"""
    vehiculos_registrados: int
    incidentes_activos: int
    solicitudes_pendientes: int
    ultimo_incidente: Optional[str] = None
    metricas_adicionales: Optional[Dict[str, Any]] = None


@dataclass
class DashboardTecnicoResponse:
    """Métricas para usuarios con rol TECNICO"""
    orden_asignada: bool
    tareas_completadas_hoy: int
    calificacion_promedio: float
    descripcion_orden: Optional[str] = None
    metricas_adicionales: Optional[Dict[str, Any]] = None


@dataclass
class DashboardGenericoResponse:
    """Respuesta genérica para roles no específicos o desconocidos"""
    mensaje: str
    rol: str
    datos: Optional[Dict[str, Any]] = None


@dataclass
class DashboardErrorResponse:
    """Respuesta de error en el dashboard"""
    detalle: str
    codigo_error: int


# Unión de tipos para respuesta flexible
DashboardResponse = Union[
    DashboardAdminResponse,
    DashboardOperadorResponse,
    DashboardUsuarioResponse,
    DashboardTecnicoResponse,
    DashboardGenericoResponse
]
