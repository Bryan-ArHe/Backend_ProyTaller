# models/__init__.py
from models.database import Base
from models.user import Usuario, Rol, Permiso
from models.bitacora import Bitacora
from models.tecnico import Tecnico
from models.solicitud import SolicitudServicio
from models.incidente import Incidente
from models.zona_cobertura import ZonaCobertura
from models.vehiculo import Vehiculo

