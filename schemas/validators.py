"""
schemas/validators.py - Validadores personalizados para dataclasses
Proporciona funciones de validación similares a Pydantic
"""

from typing import Optional, Any


def validate_string_length(value: str, min_length: int = None, max_length: int = None, field_name: str = "field") -> None:
    """Valida la longitud de un string"""
    if value is None:
        return
    if min_length is not None and len(value) < min_length:
        raise ValueError(f"{field_name} debe tener al menos {min_length} caracteres")
    if max_length is not None and len(value) > max_length:
        raise ValueError(f"{field_name} debe tener máximo {max_length} caracteres")


def validate_email(email: str) -> None:
    """Valida formato de email"""
    if not isinstance(email, str):
        raise ValueError("Email debe ser una cadena de texto")
    if "@" not in email or "." not in email.split("@")[1]:
        raise ValueError("Email inválido")


def validate_number_range(value: float, min_val: float = None, max_val: float = None, field_name: str = "field") -> None:
    """Valida que un número esté en un rango"""
    if value is None:
        return
    if min_val is not None and value < min_val:
        raise ValueError(f"{field_name} debe ser mayor o igual a {min_val}")
    if max_val is not None and value > max_val:
        raise ValueError(f"{field_name} debe ser menor o igual a {max_val}")


def validate_latitude(value: float) -> None:
    """Valida que un valor sea una latitud válida (-90 a 90)"""
    if value is None:
        return
    validate_number_range(value, -90, 90, "Latitud")


def validate_longitude(value: float) -> None:
    """Valida que un valor sea una longitud válida (-180 a 180)"""
    if value is None:
        return
    validate_number_range(value, -180, 180, "Longitud")


def validate_year(value: int) -> None:
    """Valida que un año esté en un rango válido (1900-2100)"""
    if value is None:
        return
    validate_number_range(value, 1900, 2100, "Año")
