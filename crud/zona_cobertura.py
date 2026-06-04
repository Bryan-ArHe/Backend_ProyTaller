from sqlalchemy.orm import Session
from sqlalchemy import func
from models.zona_cobertura import ZonaCobertura
from schemas.zona_cobertura import ZonaCoberturaCreate

def crear_zona(db: Session, zona: ZonaCoberturaCreate):
    # Creamos la instancia del modelo, convirtiendo el WKT (String) a Geometry (PostGIS)
    db_zona = ZonaCobertura(
        nombre=zona.nombre,
        descripcion=zona.descripcion,
        estado=zona.estado,
        # ST_GeomFromText transforma el string del polígono al formato espacial con SRID 4326 (GPS)
        poligono_area=func.ST_GeomFromText(zona.poligono_area, 4326)
    )
    
    db.add(db_zona)
    db.commit()
    db.refresh(db_zona)
    
    return db_zona