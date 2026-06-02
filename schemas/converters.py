"""
schemas/converters.py - Funciones auxiliares para convertir ORM a dataclasses
"""

from dataclasses import is_dataclass, fields, asdict
from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from typing import TypeVar, Type

T = TypeVar('T')


def orm_to_dict(orm_obj):
    """Convierte un objeto ORM de SQLAlchemy a diccionario, incluyendo relaciones"""
    if orm_obj is None:
        return None
    
    result = {}
    mapper = sqlalchemy_inspect(orm_obj.__class__)
    
    # Convertir columnas
    for column in mapper.columns:
        value = getattr(orm_obj, column.name)
        result[column.name] = value
    
    # Convertir relaciones (si existen)
    for relationship in mapper.relationships:
        rel_name = relationship.key
        rel_obj = getattr(orm_obj, rel_name, None)
        
        if rel_obj is None:
            result[rel_name] = None
        elif isinstance(rel_obj, list):
            # Si es una colección, convertir cada elemento
            result[rel_name] = rel_obj
        else:
            # Si es un objeto único, convertir a dict
            rel_mapper = sqlalchemy_inspect(rel_obj.__class__)
            rel_dict = {}
            for col in rel_mapper.columns:
                rel_dict[col.name] = getattr(rel_obj, col.name)
            result[rel_name] = rel_dict
    
    return result


def orm_to_dataclass(orm_obj, dataclass_type: Type[T]) -> T:
    """
    Convierte un objeto ORM a una instancia de dataclass
    
    Args:
        orm_obj: Objeto ORM de SQLAlchemy
        dataclass_type: Clase dataclass destino
        
    Returns:
        Instancia del dataclass con datos del ORM
    """
    if orm_obj is None:
        return None
    
    # Obtener diccionario del ORM
    data_dict = orm_to_dict(orm_obj)
    
    # Obtener los nombres de los campos del dataclass
    dc_field_map = {f.name: f for f in fields(dataclass_type)}
    
    # Procesar cada campo
    filtered_data = {}
    for field_name, field_obj in dc_field_map.items():
        if field_name in data_dict:
            value = data_dict[field_name]
            
            # Si el valor es un diccionario y el campo espera un dataclass, convertir
            if isinstance(value, dict) and is_dataclass(field_obj.type):
                filtered_data[field_name] = field_obj.type(**value)
            else:
                filtered_data[field_name] = value
    
    # Crear instancia del dataclass
    return dataclass_type(**filtered_data)
