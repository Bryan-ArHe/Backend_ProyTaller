# Plataforma Inteligente de Atención de Emergencias Vehiculares - Backend

## 📋 Estructura del Proyecto

```
Backend_ProyTaller/
├── main.py                          # Punto de entrada de la aplicación
├── config.py                         # Configuración centralizada
├── requirements.txt                  # Dependencias del proyecto
├── .env                             # Variables de entorno (no versionar)
├── .gitignore                       # Archivos a ignorar en git
│
├── models/                          # Modelos ORM (SQLAlchemy)
│   ├── __init__.py
│   ├── database.py                  # Configuración de BD
│   └── user.py                      # Modelos Rol y Usuario
│
├── schemas/                         # Esquemas de validación (Pydantic)
│   ├── __init__.py
│   └── user.py                      # Esquemas de usuario y login
│
├── security/                        # Lógica de seguridad
│   ├── __init__.py
│   ├── password.py                  # Hash y verificación de contraseñas
│   └── jwt_handler.py               # Generación y validación de JWT
│
├── routers/                         # Endpoints de la API
│   ├── __init__.py
│   └── auth.py                      # Endpoints de autenticación
│
└── dependencies.py                  # Dependencias compartidas (get_current_user)
```

## 🚀 Instalación y Ejecución

### 1. Crear y activar el entorno virtual

```bash
# En Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1


### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar la base de datos

Edita el archivo `.env` y actualiza la conexión a PostgreSQL:

```
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/emergencias_db
SECRET_KEY=tu_clave_secreta_segura_cambiar_en_produccion
```

**Nota:** Asegúrate de que PostgreSQL esté instalado y corriendo, y que hayas creado la base de datos `emergencias_db`.

### 4. Inicializar la base de datos

Antes de la primera ejecución, inicializa la BD con datos de prueba:

```bash
python reset_db.py
```

Esto crea las tablas y usuarios de prueba necesarios.

### 5. Ejecutar la aplicación

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

O simplemente:

```bash
uvicorn main:app --reload
```

La aplicación estará disponible en: `http://localhost:8000`

## 📚 Documentación de la API

Una vez que la aplicación esté corriendo:

- **API Docs (Swagger UI):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔐 Módulo 1: Identidad, Accesos y Seguridad

### Componentes Implementados

#### 1. **Modelos de Base de Datos** (`models/user.py`)

- **Rol:** Almacena los roles del sistema (admin, operador, usuario)
- **Usuario:** Almacena información de usuarios con referencia al rol

#### 2. **Esquemas Pydantic** (`schemas/user.py`)

- `UsuarioCreate`: Para registrar nuevos usuarios
- `UsuarioResponse`: Para devolver datos sin la contraseña hasheada
- `LoginData`: Para las credenciales de login
- `Token`: Para la respuesta del JWT

#### 3. **Seguridad** (`security/`)

- **password.py:**
  - `hash_password()`: Hashea contraseñas con bcrypt
  - `verify_password()`: Verifica contraseñas hasheadas

- **jwt_handler.py:**
  - `create_access_token()`: Crea un JWT con datos del usuario
  - `decode_access_token()`: Decodifica y valida el JWT

#### 4. **Dependencias** (`dependencies.py`)

- `get_current_user`: Dependencia que valida el JWT y retorna el usuario autenticado
- Usa OAuth2PasswordBearer para extraer el token del header

#### 5. **Endpoints** (`routers/auth.py`)

- `POST /auth/register`: Registrar nuevo usuario
- `POST /auth/login`: Autenticación y generación de JWT
- `GET /auth/me`: Obtener datos del usuario autenticado

#### 6. **CORS** (Configurado en `main.py`)

Configuracion de CORS mejorada para permitir peticiones desde el frontend Angular:
- Orígenes permitidos: `localhost:4200`, `127.0.0.1:4200`, `localhost:3000`
- Métodos permitidos: GET, POST, PUT, DELETE, OPTIONS
- Headers: Content-Type, Authorization
- Credenciales: Habilitadas

## 📝 Ejemplos de Uso

### 1. Registrar un usuario

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan@example.com",
    "telefono": "3001234567",
    "password": "123456",
    "id_rol": 3
  }'
```

**Respuesta (201 Created):**
```json
{
  "id": 1,
  "email": "juan@example.com",
  "telefono": "3001234567",
  "estado_cuenta": "ACTIVO",
  "id_rol": 3,
  "fecha_registro": "2024-01-15T10:30:00",
  "rol": {
    "id": 3,
    "nombre": "usuario",
    "descripcion": "Usuario estándar"
  }
}
```

### 2. Iniciar sesión

**Con usuario de prueba:**

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "123456"
  }'
```

**Con cualquier usuario personalizado:**

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "su_contraseña"
  }'
```

**Respuesta (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Obtener datos del usuario (requiere autenticación)

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Respuesta (200 OK):**
```json
{
  "id": 1,
  "email": "juan@example.com",
  "telefono": "3001234567",
  "estado_cuenta": "ACTIVO",
  "id_rol": 3,
  "fecha_registro": "2024-01-15T10:30:00",
  "rol": {
    "id": 3,
    "nombre": "usuario",
    "descripcion": "Usuario estándar"
  }
}
```

## � Integración por Plataforma

### Frontend Web (Angular - localhost:4200)

El frontend web está destinado al **Administrador** y **Gestor de Taller** para gestionar la plataforma.

**Credenciales recomendadas:**
- Admin: `admin@example.com` / `123456`
- Gestor: `gestor_taller@example.com` / `123456`

**Endpoints clave:**
- `POST /auth/login` - Autenticación
- `GET /auth/me` - Obtener perfil del usuario autenticado
- `GET /dashboard` - Dashboard del gestor/admin

**Headers requeridos:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

### App Móvil (iOS/Android)

La app móvil está destinada al **Cliente** (reportar emergencias) y **Técnico** (atender servicios).

**Credenciales para testing:**
- Cliente: `cliente@example.com` / `123456`
- Técnico: `tecnico@example.com` / `123456`

**Endpoints clave:**
- `POST /auth/login` - Autenticación
- `GET /auth/me` - Obtener perfil del usuario
- `POST /incidentes` - Crear nuevo incidente (Cliente)
- `GET /incidentes/{id}` - Obtener detalles del incidente
- `PATCH /incidentes/{id}/estado` - Actualizar estado del servicio (Técnico)

**Consideraciones para producción:**
- Cambiar contraseñas en archivo `.env`
- Implementar registro de usuarios (CU1)
- Agregar autenticación con SMS/OTP para clientes
- Gestionar sesiones de técnicos con validación GPS

## �🛡️ Buenas Prácticas Implementadas

1. **Separación de responsabilidades:** Cada módulo tiene una función específica
2. **Seguridad:**
   - Contraseñas hasheadas con bcrypt
   - Tokens JWT con expiración
   - Validación de permisos con OAuth2
   - Nunca se retorna password_hash en respuestas

3. **Validación:**
   - Esquemas con Dataclasses para entrada/salida
   - Validación de email, teléfono, contraseña
   - Manejo de excepciones HTTP approppiadas
   - Conversión automática de ORM a Dataclasses incluyendo relaciones

4. **Mantenibilidad:**
   - Código comentado y estructurado
   - Uso de dependencias inyectadas
   - Configuración centralizada
   - Dataclasses en lugar de Pydantic para mayor control

5. **Escalabilidad:**
   - Estructura lista para agregar más módulos
   - Separación clara de rutas
   - Fácil de agregar más endpoints

## 🔧 Variables de Entorno (.env)

```env
# Base de datos
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/emergencias_db

# JWT
SECRET_KEY=clave_secreta_larga_y_aleatoria  # Cambiar en producción!
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Aplicación
API_TITLE=Plataforma Inteligente de Atención de Emergencias Vehiculares
API_VERSION=1.0.0
DEBUG=True  # Cambiar a False en producción
```

## 📦 Tecnologías Utilizadas

- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para manejo de base de datos
- **PostgreSQL** - Base de datos relacional
- **Pydantic** - Validación de datos
- **Passlib + bcrypt** - Hasheo seguro de contraseñas
- **python-jose** - Manejo de JWT

## � Usuarios de Prueba

La BD se inicializa con los siguientes usuarios (ejecutar `python reset_db.py`):

### 🌐 Frontend Web (localhost:4200)

| Email | Rol | Contraseña | Descripción |
|-------|-----|-----------|-------------|
| admin@example.com | admin | 123456 | Acceso total a la plataforma |
| gestor_taller@example.com | gestor_taller | 123456 | Gestión de taller y técnicos |

### 📱 App Móvil (Desarrollo/Testing)

| Email | Rol | Contraseña | Descripción |
|-------|-----|-----------|-------------|
| tecnico@example.com | tecnico | 123456 | Técnico operativo en campo |
| cliente@example.com | cliente | 123456 | Usuario final reportando emergencias |

## �🚨 Próximos Pasos (Módulos Futuros)

- Módulo 2: Gestión de Emergencias
- Módulo 3: Sistema de Alertas
- Módulo 4: Análisis y Reportes
- Implementar Alembic para migraciones de BD
- Agregar tests unitarios
- Documentación de API mejorada

## 📧 Contacto y Soporte

Para cualquier duda sobre el módulo de autenticación, revisa la documentación en los endpoints:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
