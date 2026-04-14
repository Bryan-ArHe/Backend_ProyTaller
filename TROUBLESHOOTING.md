# GUÍA DE SOLUCIÓN DE PROBLEMAS

## 🔴 Error: `ModuleNotFoundError: No module named 'fastapi'`

**Causa:** No has instalado las dependencias del proyecto.

**Solución:**
```bash
# Activar el entorno virtual
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Linux/macOS

# Instalar dependencias
pip install -r requirements.txt
```

---

## 🔴 Error: `TypeError: init() got an unexpected keyword argument 'from_attributes'`

**Causa:** Estás usando una versión antigua de Pydantic.

**Solución:**
```bash
pip install --upgrade pydantic
# Asegúrate que sea versión 2.x
pip show pydantic
```

**Nota:** En Pydantic v1 se usaba `orm_mode = True`, pero en v2 es `from_attributes = True`.

---

## 🔴 Error: `psycopg2.OperationalError: could not connect to server`

**Causa:** PostgreSQL no está corriendo o la URL de conexión es incorrecta.

**Solución:**

1. Verifica que PostgreSQL esté corriendo:
```bash
# En Windows, abre Services y asegúrate que está en ejecución
# O en PowerShell:
Get-Service postgresql-x64-15  # Ajusta el nombre según tu versión
```

2. Verifica la URL en `.env`:
```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/emergencias_db
```

3. Crea la base de datos si no existe:
```bash
# En PowerShell, conectate a PostgreSQL
psql -U postgres

# Dentro de PostgreSQL:
CREATE DATABASE emergencias_db;
\q  # Salir
```

---

## 🔴 Error: `UnicodeDecodeError` al usar caracteres especiales

**Causa:** Codificación de caracteres incorrecta en el terminal.

**Solución:**
```bash
# En PowerShell, ejecuta al inicio:
chcp 65001
```

---

## 🔴 Error: `Port 8000 is already in use`

**Causa:** Otra aplicación está usando el puerto 8000.

**Solución:**

Opción 1: Detener la aplicación anterior
```bash
# Buscar el proceso que usa el puerto
netstat -ano | findstr :8000

# Terminar el proceso (reemplaza PID con el número encontrado)
taskkill /PID <PID> /F
```

Opción 2: Usar otro puerto
```bash
python main.py --port 8001
# O en uvicorn:
uvicorn main:app --port 8001
```

---

## 🔴 Error: Token JWT inválido o expirado

**Causa:** El token ha expirado (30 minutos por defecto) o es incorrecto.

**Solución:**

1. Obtén uno nuevo haciendo login:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "juan@example.com", "password": "MiContraseña123"}'
```

2. Para aumentar el tiempo de expiración, edita `.env`:
```env
ACCESS_TOKEN_EXPIRE_MINUTES=120  # Aumenta a 2 horas
```

---

## 🔴 Error: `401 Unauthorized` en GET /auth/me

**Causa:** No enviaste el token o es incorrecto.

**Solución:**

1. Verifica que incluyas el header correcto:
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

2. Asegúrate de que el formato sea: `Bearer <token>` (con espacio)

3. Verifica en el navegador en http://localhost:8000/docs y prueba el endpoint ahí.

---

## 🔴 Error: `403 Forbidden` - "La cuenta del usuario está inactiva"

**Causa:** La cuenta del usuario está en estado INACTIVO.

**Solución:**

Actualiza el estado directamente en BD:
```sql
UPDATE usuarios SET estado_cuenta = 'ACTIVO' WHERE email = 'usuario@example.com';
```

---

## 🔴 Error: `400 Bad Request` - "El email ya está registrado"

**Causa:** Intentaste registrar un correo que ya existe.

**Solución:**

1. Usa otro email:
```json
{
  "email": "otro_email@example.com",
  "telefono": "3001234567",
  "password": "ContraseñaNueva123",
  "id_rol": 3
}
```

2. O elimina el usuario anterior de la BD:
```sql
DELETE FROM usuarios WHERE email = 'viejo@example.com';
```

---

## 🔴 Error: `400 Bad Request` - "El rol con ID X no existe"

**Causa:** Intentaste asignar un rol que no existe.

**Solución:**

1. Verifica los roles disponibles:
```sql
SELECT * FROM roles;
```

2. Por defecto existen estos roles:
   - id=1: admin
   - id=2: operador
   - id=3: usuario

3. Usa uno de los IDs existentes al registrar.

---

## 🸂 Error: La base de datos no se crea automáticamente

**Causa:** La aplicación intentó crear tablas pero falló.

**Solución:**

1. Verifica los logs de la aplicación
2. Crea manualmente las tablas:
```bash
# Ejecuta desde el directorio del proyecto
psql -U postgres -d emergencias_db -f setup_db.sql
```

---

## 🔴 Error: `CORS` - "Access to XMLHttpRequest from origin blocked"

**Causa:** El frontend está en un origen diferente y CORS no está configurado.

**Solución:**

En `main.py`, actualmente aceptamos todos los orígenes (inseguro para producción):
```python
allow_origins=["*"]  # Cambiar en producción
```

Para especificar orígenes:
```python
allow_origins=[
    "http://localhost:3000",  # Frontend local
    "http://localhost:5173",  # Vite
    "https://tudominio.com"   # Producción
]
```

---

## ✅ Verificar que todo está bien

Ejecuta estas pruebas para confirmar:

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Acceso a docs
# Abre en navegador: http://localhost:8000/docs

# 3. Registra un usuario
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "telefono": "3001234567",
    "password": "TestPass123",
    "id_rol": 3
  }'

# 4. Haz login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'

# 5. Obtén datos del usuario (reemplaza TOKEN)
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer TOKEN_AQUI"
```

Si todos estos pasos funcionan, ¡tu configuración es correcta! ✅

---

## 📞 Soporte Adicional

1. **Swagger UI:** http://localhost:8000/docs - Interfaz interactiva
2. **ReDoc:** http://localhost:8000/redoc - Documentación alternativa
3. **Logs de consola:** Revisa el terminal donde ejecutaste `python main.py`
4. **Código fuente:** Todos los archivos tienen comentarios explicativos

---

## 🔍 Debugging

### Ver todas las rutas disponibles en la aplicación
```python
# En Python
from main import app
for route in app.routes:
    print(f"{route.path} - {route.methods}")
```

### Ver logs de SQL
En `config.py`, ya está `echo=settings.debug`, que imprime todas las queries SQL en consola.

### Inspeccionar el token JWT
```bash
# Decodifica un token online en: https://jwt.io
# O en Python:
from jose import jwt
decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
print(decoded)
```

### Verificar contraseça hasheada
```python
# En Python
from security.password import hash_password, verify_password

# Crear hash
hash_pwd = hash_password("MiContraseña123")
print(hash_pwd)  # $2b$12$...

# Verificar
resultado = verify_password("MiContraseña123", hash_pwd)
print(resultado)  # True o False
```

---

## 📚 Documentación Oficial

- FastAPI: https://fastapi.tiangolo.com
- SQLAlchemy: https://docs.sqlalchemy.org
- Pydantic: https://docs.pydantic.dev
- python-jose: https://github.com/mpdavis/python-jose
