# ARQUITECTURA - Módulo 1: Identidad, Accesos y Seguridad

## Diagrama de Capas

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENTE HTTP                            │
│  (Postman, curl, navegador, aplicación móvil, etc.)        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY (FastAPI)                     │
│                       main.py                                │
│  - Middleware CORS                                           │
│  - Events (startup, shutdown)                               │
│  - Registro de routers                                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
            ┌─────────────┴────────────────────┐
            ▼                                  ▼
    ┌──────────────────┐         ┌──────────────────────┐
    │  ROUTER (auth)   │         │  HEALTH CHECK        │
    │  routers/auth.py │         │  GET /health         │
    │                  │         │  GET /               │
    │  POST /register  │         └──────────────────────┘
    │  POST /login     │
    │  GET /me         │
    └────────┬─────────┘
             │
        ┌────┴──────────────────────────────┐
        ▼                                    ▼
   ┌──────────────┐          ┌──────────────────────┐
   │ ENDPOINTS    │          │ DEPENDENCIAS (deps)  │
   │              │          │                      │
   │ register()   │◄────────►│ get_current_user()   │
   │ login()      │          │ oauth2_scheme        │
   │ get_me()     │          │ get_db()             │
   └──────┬───────┘          └──────────────────────┘
          │
        ┌─┴──────────────────────────┬────────────────────┐
        ▼                            ▼                    ▼
   ┌──────────────┐    ┌──────────────────┐   ┌─────────────────┐
   │  SECURITY    │    │    SCHEMAS       │   │    MODELS       │
   │              │    │                  │   │                 │
   │ password.py  │    │ UsuarioCreate    │   │ database.py     │
   │ - hash_pw()  │    │ UsuarioResponse  │   │ - engine        │
   │ - verify_pw()│    │ LoginData        │   │ - SessionLocal  │
   │              │    │ Token            │   │ - Base          │
   │ jwt_handler  │    │ RolResponse      │   │ - get_db()      │
   │ - create_tk()│    └──────────────────┘   │                 │
   │ - decode_tk()│                           │ user.py         │
   └──────┬───────┘                           │ - Rol           │
          │                                   │ - Usuario       │
          │                                   │ - EstadoCuenta  │
          │                                   └────────┬────────┘
          │                                           │
          └───────────────────────┬───────────────────┘
                                  ▼
                        ┌─────────────────────┐
                        │   CONFIG            │
                        │   config.py         │
                        │                     │
                        │ settings:           │
                        │ - DATABASE_URL      │
                        │ - SECRET_KEY        │
                        │ - ALGORITHM         │
                        │ - EXPIRE_MINUTES    │
                        └────────┬────────────┘
                                 │
                                 ▼
                        ┌─────────────────────┐
                        │  .env               │
                        │  (variables locales)│
                        └────────┬────────────┘
                                 │
                                 ▼
                        ┌─────────────────────┐
                        │  POSTGRESQL         │
                        │  Base de Datos      │
                        │                     │
                        │ ┌─────────────────┐ │
                        │ │    usuarios     │ │
                        │ │ ─────────────── │ │
                        │ │ id (PK)         │ │
                        │ │ email (UNIQUE)  │ │
                        │ │ telefono        │ │
                        │ │ password_hash   │ │
                        │ │ estado_cuenta   │ │
                        │ │ id_rol (FK)     │ │
                        │ │ fecha_registro  │ │
                        │ └─────────────────┘ │
                        │                     │
                        │ ┌─────────────────┐ │
                        │ │      roles      │ │
                        │ │ ─────────────── │ │
                        │ │ id (PK)         │ │
                        │ │ nombre (UNIQUE) │ │
                        │ │ descripcion     │ │
                        │ └─────────────────┘ │
                        └─────────────────────┘
```

## Flujo de Registro (POST /auth/register)

```
┌─────────────────────────────────────┐
│  Cliente envia datos de registro     │
│  {email, telefono, password, id_rol}│
└────────────┬────────────────────────┘
             │
             ▼
      ┌──────────────────────────┐
      │  Validación Pydantic     │
      │  (UsuarioCreate schema)  │
      │  ✓ TokenEmail válido     │
      │  ✓ Longitud password ≥ 8 │
      │  ✓ Teléfono válido       │
      └────────────┬─────────────┘
                   │
        ┌──────────▼───────────┐
        │  ¿Email existe?      │
        │  SELECT * FROM ...   │
        └──────────┬───────────┘
                   │
        ┌──────────▼───────────┐
        │  ¿SI? ─────► 400 ERR │
        │  ¿NO? Continuar      │
        └──────────┬───────────┘
                   │
        ┌──────────▼──────────────┐
        │ ¿Rol existe?            │
        │ SELECT * FROM roles ... │
        └──────────┬──────────────┘
                   │
        ┌──────────▼───────────┐
        │  ¿SI? Continuar      │
        │  ¿NO? ──► 400 ERR    │
        └──────────┬───────────┘
                   │
        ┌──────────▼──────────────────┐
        │  Hash password (bcrypt)     │
        │  hash_password(plain_text)  │
        └──────────┬──────────────────┘
                   │
        ┌──────────▼────────────────────┐
        │  Crear objeto Usuario         │
        │  - email                      │
        │  - telefono                   │
        │  - password_hash (no plain!)  │
        │  - id_rol                     │
        │  - estado_cuenta = ACTIVO     │
        └──────────┬────────────────────┘
                   │
        ┌──────────▼──────────────────┐
        │  Guardar en BD               │
        │  db.add(usuario)             │
        │  db.commit()                 │
        └──────────┬──────────────────┘
                   │
        ┌──────────▼──────────────────┐
        │  Respuesta 201 Created       │
        │  UsuarioResponse (sin hash)  │
        └──────────────────────────────┘
```

## Flujo de Login (POST /auth/login)

```
┌─────────────────────────────────────┐
│  Cliente envía credenciales         │
│  {email, password}                  │
└────────────┬────────────────────────┘
             │
             ▼
      ┌──────────────────────────────┐
      │  Validación Pydantic         │
      │  (LoginData schema)          │
      │  ✓ Email válido              │
      │  ✓ Password requerido        │
      └────────────┬─────────────────┘
                   │
        ┌──────────▼────────────────┐
        │  ¿Usuario existe?         │
        │  SELECT * FROM usuarios.. │
        └──────────┬────────────────┘
                   │
        ┌──────────▼───────────────┐
        │  ¿SI? Continuar          │
        │  ¿NO? ──► 401 UNAUTH     │
        └──────────┬───────────────┘
                   │
        ┌──────────▼────────────────────────┐
        │  Verificar contraseña             │
        │  verify_password(plain, hash_bd)  │
        └──────────┬─────────────────────────┘
                   │
        ┌──────────▼──────────────┐
        │  ¿Correcta? Continuar   │
        │  ¿Incorrecta? ─► 401    │
        └──────────┬──────────────┘
                   │
        ┌──────────▼────────────────┐
        │  ¿Cuenta ACTIVA?          │
        │  estado_cuenta == ACTIVO  │
        └──────────┬────────────────┘
                   │
        ┌──────────▼──────────────┐
        │  ¿SI? Continuar         │
        │  ¿NO? ──► 403 FORBIDDEN │
        └──────────┬──────────────┘
                   │
        ┌──────────▼─────────────────────┐
        │  Generar JWT                   │
        │  - payload = {"sub": email}    │
        │  - exp = ahora + 30 minutos    │
        │  - sign(SECRET_KEY, HS256)     │
        └──────────┬─────────────────────┘
                   │
        ┌──────────▼──────────────────┐
        │  Respuesta 200 OK           │
        │  {access_token, token_type} │
        └──────────────────────────────┘
```

## Flujo de Obtener Usuario Actual (GET /auth/me)

```
┌─────────────────────────────┐
│  Cliente envía solicitud    │
│  + Header: Authorization    │
│    Bearer <token>           │
└────────────┬────────────────┘
             │
             ▼
      ┌──────────────────────────┐
      │  Middleware OAuth2       │
      │  extrae token del header │
      │  Authorization: Bearer X │
      └────────────┬─────────────┘
                   │
        ┌──────────▼─────────────────┐
        │  ¿Token presente?         │
        │  ¿NO? ──► 403 FORBIDDEN   │
        └──────────┬────────────────┘
                   │
        ┌──────────▼──────────────────┐
        │  Decodificar JWT            │
        │  jwt.decode(token, SECRET)  │
        └──────────┬───────────────────┘
                   │
        ┌──────────▼──────────────────┐
        │  ¿Token válido/NO expirado?│
        │  ¿NO? ──► 401 UNAUTHORIZED │
        └──────────┬──────────────────┘
                   │
        ┌──────────▼────────────────────┐
        │  Extraer email del payload   │
        │  payload["sub"] = email      │
        └──────────┬────────────────────┘
                   │
        ┌──────────▼──────────────────┐
        │  Buscar usuario en BD       │
        │  SELECT * FROM usuarios ... │
        └──────────┬──────────────────┘
                   │
        ┌──────────▼──────────────────┐
        │  ¿Usuario existe?           │
        │  ¿NO? ──► 401 UNAUTHORIZED  │
        └──────────┬──────────────────┘
                   │
        ┌──────────▼──────────────────┐
        │  ¿Cuenta ACTIVA?            │
        │  ¿NO? ──► 403 FORBIDDEN     │
        └──────────┬──────────────────┘
                   │
        ┌──────────▼────────────────────┐
        │  Respuesta 200 OK            │
        │  UsuarioResponse             │
        │  (datos completos, sin hash) │
        └────────────────────────────────┘
```

## Tabla de Códigos HTTP

| Código | Descripción | Cuándo |
|--------|-------------|--------|
| 200 | OK | Login exitoso, GET /me exitoso |
| 201 | Created | Usuario registrado exitosamente |
| 400 | Bad Request | Email duplicado, rol inexistente, datos inválidos |
| 401 | Unauthorized | Contraseña incorrecta, token inválido/expirado, usuario no existe |
| 403 | Forbidden | Cuenta inactiva, sin token |
| 404 | Not Found | Endpoint no encontrado |

## Seguridad - Capas de Validación

```
1. PYDANTIC VALIDATION
   ├─ EmailStr (validación de formato de email)
   ├─ Min/Max length (contraseña mínimo 8)
   ├─ Tipo de dato correcto
   └─ Campos requeridos

2. LÓGICA DE NEGOCIO
   ├─ Email único (no duplicados)
   ├─ Rol existe en BD
   ├─ Cuenta activa
   └─ Contraseña correcta

3. CRIPTOGRAFÍA
   ├─ Hashing con bcrypt (password_hash)
   ├─ JWT con firma (HS256)
   └─ Expiración de tokens

4. AUTENTICACIÓN
   ├─ OAuth2PasswordBearer
   ├─ Dependencia get_current_user
   └─ Header Authorization validado
```

## Relaciones de Base de Datos

```
┌────────────┐         ┌────────────┐
│   roles    │◄────────│  usuarios  │
├────────────┤    1:N  ├────────────┤
│ id (PK)    │         │ id (PK)    │
│ nombre     │         │ id_rol(FK) │
│ descripcion│         │ email      │
└────────────┘         │ telefono   │
                       │ password.. │
                       │ estado     │
                       │ fecha_reg  │
                       └────────────┘
```

## Ejemplo Completo de Petición y Respuesta

### 1. Registro
```
REQUEST:
POST /auth/register HTTP/1.1
Content-Type: application/json

{
  "email": "juan@example.com",
  "telefono": "3001234567",
  "password": "MiContraseña123",
  "id_rol": 3
}

RESPONSE (201):
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

### 2. Login
```
REQUEST:
POST /auth/login HTTP/1.1
Content-Type: application/json

{
  "email": "juan@example.com",
  "password": "MiContraseña123"
}

RESPONSE (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Obtener Usuario Actual
```
REQUEST:
GET /auth/me HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

RESPONSE (200):
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
