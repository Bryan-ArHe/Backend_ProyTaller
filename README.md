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

# En Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

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

### 4. Ejecutar la aplicación

```bash
python main.py
```

O con uvicorn directamente:

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

## 📝 Ejemplos de Uso

### 1. Registrar un usuario

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan@example.com",
    "telefono": "3001234567",
    "password": "MiContraseña123",
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

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan@example.com",
    "password": "MiContraseña123"
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

## 🛡️ Buenas Prácticas Implementadas

1. **Separación de responsabilidades:** Cada módulo tiene una función específica
2. **Seguridad:**
   - Contraseñas hasheadas con bcrypt
   - Tokens JWT con expiración
   - Validación de permisos con OAuth2
   - Nunca se retorna password_hash en respuestas

3. **Validación:**
   - Esquemas Pydantic para entrada/salida
   - Validación de email, teléfono, contraseña
   - Manejo de excepciones HTTP aproppiadas

4. **Mantenibilidad:**
   - Código comentado y estructurado
   - Uso de dependencias inyectadas
   - Configuración centralizada

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

## 🚨 Próximos Pasos (Módulos Futuros)

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
