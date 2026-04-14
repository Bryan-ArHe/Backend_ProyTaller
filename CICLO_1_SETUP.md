# Guía de Implementación - Ciclo 1: Vehículos e Incidentes

## Archivos Creados/Modificados

### Nuevos Modelos
```
models/
├── marca_modelo.py          (NUEVO - 130 líneas)
│   ├── class Marca          - Catálogo maestro de marcas
│   └── class Modelo         - Modelos dentro de cada marca
├── vehiculo.py              (NUEVO - 70 líneas)
│   └── class Vehiculo       - Vehículos de clientes
└── incidente.py             (NUEVO - 180 líneas)
    ├── class Incidente      - Reportes de emergencias
    └── class Evidencia      - Archivos multimedia
```

### Modelos Existentes Modificados
```
models/
└── user.py                  (ACTUALIZADO)
    └── Agregadas relaciones con Vehiculo e Incidente
```

### Nuevos Esquemas Pydantic
```
schemas/
├── vehiculo.py              (NUEVO - 150 líneas)
│   ├── MarcaCreate, MarcaResponse
│   ├── ModeloCreate, ModeloResponse, ModeloUpdate
│   ├── VehiculoCreate, VehiculoUpdate, VehiculoResponse
│   └── VehiculoDetailedResponse, VehiculoListResponse
└── incidente.py             (NUEVO - 120 líneas)
    ├── EvidenciaCreate, EvidenciaResponse
    ├── IncidenteCreate, IncidenteResponse
    ├── IncidenteDetailedResponse, IncidenteListResponse
    └── TriajeAIResponse
```

### Nuevas Funciones CRUD
```
crud/
├── __init__.py              (NUEVO)
├── vehiculo.py              (NUEVO - 380 líneas)
│   └── Funciones CRUD para Marca, Modelo, Vehículo
│       - crear_marca, obtener_marca_por_id, eliminar_marca
│       - crear_modelo, obtener_modelo_por_id, actualizar_modelo, eliminar_modelo
│       - crear_vehiculo, obtener_vehiculo_por_id, obtener_vehiculos_por_cliente
│       - actualizar_vehiculo, eliminar_vehiculo
└── incidente.py             (NUEVO - 420 líneas)
    ├── Sistema de Triaje IA
    │   └── calcular_prioridad_ia() - Lógica de priorización automática
    └── Funciones CRUD para Incidente y Evidencia
        - crear_incidente (con múltiples evidencias)
        - obtener_incidente_por_id, obtener_incidentes_por_cliente
        - obtener_incidentes_por_estado, obtener_incidentes_por_prioridad
        - actualizar_estado_incidente, actualizar_prioridad_incidente
        - crear_evidencia, obtener_evidencias_incidente, eliminar_evidencia
```

### Nuevos Routers/Endpoints
```
routers/
├── vehiculos.py             (NUEVO - 380 líneas)
│   ├── Endpoints: Marcas (CRUD)
│   ├── Endpoints: Modelos (CRUD)
│   └── Endpoints: Vehículos (CRUD protegido, solo del usuario)
└── incidentes.py            (NUEVO - 420 líneas)
    ├── Endpoints: Reportar incidente
    ├── Endpoints: Gestión de evidencias
    ├── Endpoints: Filtros y búsqueda
    ├── Endpoints: Operaciones de triaje
    └── Endpoints: Estadísticas
```

### Configuración Principal Actualizada
```
main.py                      (ACTUALIZADO)
└── Agregados imports de nuevos modelos y routers
    - from models.marca_modelo import Marca, Modelo
    - from models.vehiculo import Vehiculo
    - from models.incidente import Incidente, Evidencia
    - from routers import vehiculos, incidentes
    - app.include_router(vehiculos.router)
    - app.include_router(incidentes.router)
```

### Ejemplos de Test
```
requests.http                (ACTUALIZADO)
└── Agregar +50 ejemplos de requests para:
    - Gestión de marcas y modelos
    - CRUD de vehículos
    - Reportes de incidentes
    - Gestión de evidencias
    - Filtros y búsqueda
    - Operaciones de triaje
```

### Documentación
```
CICLO_1_DOCUMENTACION.md     (NUEVO - Guía completa)
CICLO_1_SETUP.md             (ESTE ARCHIVO)
```

## Estructura de Tablas en BD

```sql
-- Existentes (Módulo 1)
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion VARCHAR(255)
);

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    id_rol INTEGER NOT NULL REFERENCES roles(id),
    email VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    estado_cuenta ENUM('ACTIVO', 'INACTIVO') DEFAULT 'ACTIVO',
    fecha_registro TIMESTAMP DEFAULT NOW()
);

-- Nuevas (Ciclo 1)
CREATE TABLE marcas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    pais_origen VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

CREATE TABLE modelos (
    id SERIAL PRIMARY KEY,
    id_marca INTEGER NOT NULL REFERENCES marcas(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL,
    año_inicio INTEGER,
    año_fin INTEGER,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

CREATE TABLE vehiculos (
    id SERIAL PRIMARY KEY,
    id_cliente INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    id_modelo INTEGER NOT NULL REFERENCES modelos(id),
    placa VARCHAR(20) UNIQUE NOT NULL,
    vin VARCHAR(50) UNIQUE,
    color VARCHAR(30),
    año INTEGER,
    estado VARCHAR(20) DEFAULT 'ACTIVO',
    fecha_registro TIMESTAMP DEFAULT NOW()
);

CREATE TABLE incidentes (
    id SERIAL PRIMARY KEY,
    id_vehiculo INTEGER NOT NULL REFERENCES vehiculos(id),
    id_cliente INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    descripcion TEXT NOT NULL,
    estado ENUM('PENDIENTE', 'EN_TRIAJE', 'ASIGNADO', 'EN_ATENCION', 'RESUELTO', 'CANCELADO') DEFAULT 'PENDIENTE',
    prioridad ENUM('BAJA', 'MEDIA', 'ALTA', 'CRITICA') DEFAULT 'MEDIA',
    ubicacion_lat FLOAT,
    ubicacion_long FLOAT,
    fecha_reporte TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW() ON UPDATE NOW()
);

CREATE TABLE evidencias (
    id SERIAL PRIMARY KEY,
    id_incidente INTEGER NOT NULL REFERENCES incidentes(id) ON DELETE CASCADE,
    tipo ENUM('FOTO', 'VIDEO', 'AUDIO', 'DOCUMENTO') NOT NULL,
    url VARCHAR(500) NOT NULL,
    tamano_bytes INTEGER,
    descripcion VARCHAR(300),
    fecha_captura TIMESTAMP DEFAULT NOW(),
    fecha_registro TIMESTAMP DEFAULT NOW()
);
```

## Requisitos

### Sistema
- Python 3.10+
- PostgreSQL 12+
- pip o conda

### Dependencias Python (requirements.txt)
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose==3.3.0
bcrypt==5.0.0
email-validator==2.1.0
python-multipart==0.0.6
pytest==7.4.3
httpx==0.25.2
```

## Instalación y Ejecución

### 1. Crear entorno virtual
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Verificar archivo .env
```env
DATABASE_URL=postgresql://user:password@localhost:5432/emergencias_db
SECRET_KEY=tu-clave-secreta-muy-larga-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_TITLE=Plataforma de Emergencias Vehiculares
API_VERSION=1.0.0
DEBUG=True
```

### 4. Crear base de datos PostgreSQL
```sql
CREATE DATABASE emergencias_db;
```

### 5. Ejecutar la aplicación
```bash
# Desarrollo (con auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

La API estará disponible en: **http://localhost:8000**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

### Ejecutar tests automatizados
```bash
# Todos los tests
pytest test_api.py -v

# Solo autenticación
pytest test_api.py::test_register -v
pytest test_api.py::test_login -v

# Con cobertura
pytest test_api.py --cov=. --cov-report=html
```

### Requests HTTP interactivos
Usar la extensión "REST Client" en VS Code y abrir `requests.http`:
1. Copiar token JWT de un login
2. Pegarlo en la variable `@token = ...`
3. Ejecutar requests directamente desde VS Code

## Flujo de Trabajo Típico

### Como Usuario (rol: usuario)
```
1. Registrarse:           POST /auth/register
2. Loguearse:             POST /auth/login → obtener TOKEN
3. Ver vehículos:         GET /vehiculos (sin datos, es primer acceso)
4. Registrar vehículo:    POST /vehiculos (necesita id_modelo)
   - Primero obtenemos id_modelo: GET /vehiculos/marcas → GET /vehiculos/marcas/1/modelos
5. Ver vehículos:         GET /vehiculos ✅ Ahora aparence el registrado
6. Reportar incidente:    POST /incidentes/reportar (requiere id_vehiculo)
7. Ver mis incidentes:    GET /incidentes
8. Ver detalles:          GET /incidentes/{id} (con evidencias)
9. Agregar evidencia:     POST /incidentes/{id}/evidencias
10. Verificar estado:     GET /incidentes/{id} (estado sigue PENDIENTE hasta que operador lo atienda)
```

### Como Operador (rol: operador)
```
1. Loguearse:             POST /auth/login → TOKEN
2. Ver incidentes pendientes:  GET /incidentes/filtros/por-estado?estado=PENDIENTE
3. Ver detalles:          GET /incidentes/{id}
4. Iniciar triaje:        PATCH /incidentes/{id}/estado?nuevo_estado=EN_TRIAJE
5. Entrar en atención:    PATCH /incidentes/{id}/estado?nuevo_estado=EN_ATENCION
6. Resolver:              PATCH /incidentes/{id}/estado?nuevo_estado=RESUELTO
7. Ver resumen:           GET /incidentes/stats/resumen
```

### Como Administrador (rol: admin)
```
1. Loguearse:             POST /auth/login → TOKEN
2. Crear marca:           POST /vehiculos/marcas {nombre: "Toyota", ...}
3. Crear modelo:          POST /vehiculos/modelos {id_marca: 1, nombre: "Corolla"}
4. Ver estadísticas:      GET /incidentes/stats/resumen
5. Manejario incidentes:  GET /incidentes/filtros/por-prioridad?prioridad=CRITICA
```

## Árbol de Directorios Final

```
Backend_ProyTaller/
├── models/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── database.py
│   ├── user.py
│   ├── marca_modelo.py         [NUEVO]
│   ├── vehiculo.py             [NUEVO]
│   └── incidente.py            [NUEVO]
│
├── schemas/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── user.py
│   ├── vehiculo.py             [NUEVO]
│   ├── incidente.py            [NUEVO]
│   └── dashboard.py
│
├── crud/                        [NUEVO]
│   ├── __init__.py
│   ├── vehiculo.py             [NUEVO]
│   └── incidente.py            [NUEVO]
│
├── routers/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── auth.py
│   ├── dashboard.py
│   ├── vehiculos.py            [NUEVO]
│   └── incidentes.py           [NUEVO]
│
├── security/
│   ├── __init__.py
│   ├── password.py
│   └── jwt_handler.py
│
├── .env
├── .gitignore
├── config.py
├── dependencies.py
├── main.py                     [ACTUALIZADO]
├── requirements.txt            [ACTUALIZADO]
├── test_api.py
├── requests.http               [ACTUALIZADO]
│
├── ARCHITECTURE.md
├── README.md
├── TROUBLESHOOTING.md
├── CICLO_1_DOCUMENTACION.md    [NUEVO]
├── CICLO_1_SETUP.md            [NUEVO - Este archivo]
│
├── venv/                       (Virtual Environment)
├── .git/                       (Git repository)
└── __pycache__/
```

## Estadísticas de la Implementación

| Componente | Líneas | Descripción |
|-----------|--------|-------------|
| models/marca_modelo.py | 130 | Marca, Modelo |
| models/vehiculo.py | 70 | Vehículo |
| models/incidente.py | 180 | Incidente, Evidencia, Enums |
| schemas/vehiculo.py | 150 | Pydantic models para vehículos |
| schemas/incidente.py | 120 | Pydantic models para incidentes |
| crud/vehiculo.py | 380 | CRUD functions |
| crud/incidente.py | 420 | CRUD + Triaje IA |
| routers/vehiculos.py | 380 | 12+ endpoints |
| routers/incidentes.py | 420 | 15+ endpoints |
| **Total Nuevo Código** | **2,250** | **~70 KB** |

## Puntos Clave de Diseño

1. **Inyección de Dependencias**: Todos los endpoints usan FastAPI `Depends()` para DB y usuario autenticado
2. **RBAC**: Control de acceso basado en roles a nivel de endpoint
3. **Lazy Loading**: SQLAlchemy relationships se cargan bajo demanda
4. **Normalización 3FN**: Catálogos maestros (Marca, Modelo) separados
5. **Error Handling**: HTTP status codes apropiados (400, 401, 403, 404)
6. **Validación**: Pydantic schemas validan inputs automáticamente
7. **Cascadas**: Eliminaciones en cascada mantienen integridad referencial
8. **Timestamps**: Auditoría automática con `datetime.utcnow`

## Próximos Pasos (Ciclo 2)

- [ ] Asignación de incidentes a técnicos
- [ ] Sistema de notificaciones (WebSocket, Email, SMS)
- [ ] Upload de archivos multimedia (S3 o similar)
- [ ] Calificación de servicios
- [ ] Reportes y analytics avanzados
- [ ] Integración con Google Maps API
- [ ] Machine Learning para triaje mejorado
- [ ] Tests unitarios completos
- [ ] CI/CD con GitHub Actions

## Soporte

Para problemas comunes, ver: **TROUBLESHOOTING.md**

Para armitecio general, ver: **ARCHITECTURE.md**

Para documentación del Ciclo 1 completo, ver: **CICLO_1_DOCUMENTACION.md**
