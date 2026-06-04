# 🚀 Guía de Despliegue en Vercel

## Pasos para Desplegar tu Backend FastAPI en Vercel

### Paso 1: Preparar la Base de Datos

**Opción A: Vercel Postgres (Recomendado)**
1. Accede a [vercel.com](https://vercel.com)
2. Crea un proyecto
3. Ve a la pestaña **Storage** → **Create Database** → **Postgres**
4. Copia la `DATABASE_URL` que Vercel te proporciona

**Opción B: Otros Servicios**
- **Supabase** (https://supabase.com) - Postgres + Auth
- **Railway** (https://railway.app) - Base de datos completa
- **Render** (https://render.com) - Postgres serverless

### Paso 2: Preparar el Repositorio

1. **Crear un repositorio en GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/tu_usuario/Backend_ProyTaller.git
   git push -u origin main
   ```

2. **Crear `.gitignore`** (si no existe):
   ```
   venv/
   __pycache__/
   *.pyc
   .env
   .env.local
   *.db
   .DS_Store
   ```

3. **NO incluir `.env` en git** (solo `.env.example`)

### Paso 3: Conectar con Vercel

1. Ve a https://vercel.com y accede con tu cuenta de GitHub
2. Haz clic en **"New Project"**
3. Selecciona tu repositorio de GitHub
4. Haz clic en **"Import"**

### Paso 4: Configurar Variables de Entorno

En Vercel:
1. Ir a **Settings** → **Environment Variables**
2. Agregar las siguientes variables:

```
DATABASE_URL = postgresql://user:password@host:port/dbname
SECRET_KEY = tu_clave_secreta_muy_larga_y_aleatoria
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
API_TITLE = Plataforma Inteligente de Atención de Emergencias Vehiculares
API_VERSION = 1.0.0
DEBUG = False
DEBUG_MODE = False
```

**⚠️ IMPORTANTE:** Cambiar `DEBUG=False` y `DEBUG_MODE=False` en producción

### Paso 5: Desplegar

1. Haz clic en **"Deploy"**
2. Espera a que se complete el build (3-5 minutos)
3. Tu aplicación estará disponible en `https://tu-proyecto.vercel.app`

### Paso 6: Inicializar la Base de Datos

La aplicación crea automáticamente las tablas en la primera ejecución (en `main.py`).

**Para agregar datos de prueba:**

Si necesitas usar `reset_db.py`, deberás ejecutarlo localmente apuntando a la BD de Vercel:

```bash
# En tu .env local durante desarrollo:
DATABASE_URL=postgresql://user:password@vercel-host:5432/dbname
python reset_db.py
```

### Paso 7: Actualizar CORS para Producción

En `main.py`, actualiza los orígenes permitidos:

```python
allow_origins=[
    "http://localhost:4200",      # Local dev
    "http://localhost:3000",      # Local dev
    "https://tu-frontend.vercel.app",  # Tu frontend en Vercel
    "https://tudominio.com",      # Tu dominio
]
```

### Paso 8: Verificar el Despliegue

1. Accede a `https://tu-proyecto.vercel.app/docs` para ver Swagger UI
2. Prueba el endpoint `/auth/login`:
   ```bash
   curl -X POST "https://tu-proyecto.vercel.app/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@example.com", "password": "12345678"}'
   ```

## 🔧 Problemas Comunes

### Error: "DATABASE_URL not set"
- Verifica que la variable esté configurada en Settings → Environment Variables
- Redeploy después de agregar variables

### Error: "Connection refused" a la BD
- Asegúrate de que la BD está accesible desde internet
- Si usas un firewall, añade la IP de Vercel (suele ser variable)

### Error: "Module not found"
- Asegúrate de que `requirements.txt` está en la raíz del proyecto
- Ejecuta `pip freeze > requirements.txt` localmente para actualizar

### Los datos de prueba no existen
- Ejecuta `python reset_db.py` localmente apuntando a tu BD de Vercel
- O usa los datos que crea automáticamente `main.py`

## 📊 Monitorear el Despliegue

En Vercel Dashboard:
1. **Logs** → Ver los logs de la aplicación en tiempo real
2. **Deployments** → Ver historial de despliegues
3. **Analytics** → Ver métricas de uso

## 🔐 Buenas Prácticas de Seguridad

- [ ] `SECRET_KEY` es una cadena larga y aleatoria
- [ ] `DEBUG = False` en producción
- [ ] Base de datos usa contraseña fuerte
- [ ] CORS solo permite orígenes específicos
- [ ] Nunca commit `.env` con datos reales
- [ ] Cambiar contraseñas de usuarios de prueba en producción
- [ ] Habilitar HTTPS (Vercel lo hace automáticamente)

## 🚀 Despliegues Futuros

Para actualizar tu aplicación:
1. Haz cambios en tu código
2. Commit y push a GitHub
3. Vercel redeploy automáticamente
4. O usa `vercel deploy` en terminal

## 📚 Referencias Útiles

- [Vercel + Python Docs](https://vercel.com/docs/functions/serverless-functions/python)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/concepts/)
- [Vercel Postgres Docs](https://vercel.com/docs/storage/vercel-postgres)
