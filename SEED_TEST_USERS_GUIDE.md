# Guía: Generación de Usuarios de Prueba (Seed Data)

## 📋 Descripción

El endpoint `POST /auth/seed-test-users` genera automáticamente **5 usuarios de prueba** con todos los roles del sistema para facilitar el testing del backend y frontend.

## 🚀 Uso Rápido

### 1. Asegúrate que DEBUG_MODE está habilitado

En `.env`:
```env
DEBUG_MODE=True  # O simplemente debug_mode=true
```

O en `config.py` (valor por defecto):
```python
debug_mode: bool = True
```

### 2. Ejecuta la aplicación
```bash
python -m uvicorn main:app --reload
```

### 3. Llama al endpoint (sin autenticación)
```bash
curl -X POST http://localhost:8000/auth/seed-test-users
```

O usa VS Code REST Client:
```http
POST http://localhost:8000/auth/seed-test-users
```

### 4. Respuesta esperada
```json
{
  "mensaje": "Usuarios de prueba creados exitosamente. Usa estas credenciales para testear el sistema.",
  "total_usuarios_creados": 5,
  "usuarios": [
    {
      "email": "admin@example.com",
      "password": "TestPassword123!",
      "telefono": "3001111111",
      "id_rol": 1,
      "rol_nombre": "admin",
      "descripcion": "Admin del sistema - Acceso completo"
    },
    {
      "email": "operador@example.com",
      "password": "TestPassword123!",
      "telefono": "3002222222",
      "id_rol": 2,
      "rol_nombre": "operador",
      "descripcion": "Operador de emergencias - Gestión de incidentes"
    },
    {
      "email": "tecnico@example.com",
      "password": "TestPassword123!",
      "telefono": "3003333333",
      "id_rol": 3,
      "rol_nombre": "tecnico",
      "descripcion": "Técnico de taller - Atención de usuarios"
    },
    {
      "email": "cliente@example.com",
      "password": "TestPassword123!",
      "telefono": "3004444444",
      "id_rol": 4,
      "rol_nombre": "cliente",
      "descripcion": "Cliente/Usuario final - Reporte de incidentes"
    },
    {
      "email": "gestor_taller@example.com",
      "password": "TestPassword123!",
      "telefono": "3005555555",
      "id_rol": 5,
      "rol_nombre": "gestor_taller",
      "descripcion": "Gestor de taller - Admin de recursos"
    }
  ]
}
```

## 👥 Usuarios y Roles Generados

| Email | Password | Rol | Descripción |
|-------|----------|-----|-------------|
| `admin@example.com` | `TestPassword123!` | 1 - Admin | Administrador del sistema (acceso completo) |
| `operador@example.com` | `TestPassword123!` | 2 - Operador | Operador de emergencias (gestión de incidentes) |
| `tecnico@example.com` | `TestPassword123!` | 3 - Técnico | Técnico de taller (atención de usuarios) |
| `cliente@example.com` | `TestPassword123!` | 4 - Cliente | Cliente/Usuario final (reporte de incidentes) |
| `gestor_taller@example.com` | `TestPassword123!` | 5 - Gestor | Gestor de taller (admin de recursos) |

## 🔐 Autenticar con los Usuarios Creados

Una vez ejecutado `seed-test-users`, puedes loguearte con cualquiera:

```bash
# Login como admin
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "TestPassword123!"
  }'
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Usar token en requests posteriores:
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer <token>"
```

## 🛡️ Seguridad

### ⚠️ IMPORTANTE

- **Solo disponible en MODO DEBUG** (`DEBUG_MODE=True`)
- No se ejecuta en producción (`DEBUG_MODE=False`)
- Retorna las contraseñas en texto plano ✅ (SOLO para desarrollo)
- No requiere autenticación previa ✅ (SOLO para desarrollo)

**Respuesta en producción (DEBUG_MODE=False):**
```json
{
  "detail": "El endpoint /auth/seed-test-users solo está disponible en modo DEBUG. Habilita DEBUG_MODE=True en .env para modo desarrollo."
}
```

HTTP Status: `403 Forbidden`

## 🔄 Comportamiento

1. **Primera ejecución:** Crea todos los 5 usuarios
2. **Ejecutar nuevamente:** Solo crea usuarios que NO existían
   - Si `admin@example.com` ya existe → Se omite
   - Si `operador@example.com` no existe → Se crea
   
   Mensaje en consola:
   ```
   ⏭️  Usuario admin@example.com ya existe, omitiendo...
   ✅ Usuario operador@example.com creado exitosamente
   ```

3. **Si un rol no existe:** Se omite ese usuario
   ```
   ⚠️  Rol 5 no existe, omitiendo usuario gestor_taller@example.com
   ```

## 🗄️ Verificación en Base de Datos

```sql
-- Verificar usuarios creados
SELECT id, email, id_rol, estado_cuenta FROM usuarios 
ORDER BY id;

-- Verificar roles
SELECT id, nombre FROM roles 
ORDER BY id;

-- Contar usuarios por rol
SELECT r.nombre, COUNT(u.id) as total 
FROM roles r 
LEFT JOIN usuarios u ON r.id = u.id_rol 
GROUP BY r.id, r.nombre;
```

Resultado esperado:
```
 id |      email              | id_rol | estado_cuenta
----+-------------------------+--------+---------------
  1 | admin@example.com       |      1 | ACTIVO
  2 | operador@example.com    |      2 | ACTIVO
  3 | tecnico@example.com     |      3 | ACTIVO
  4 | cliente@example.com     |      4 | ACTIVO
  5 | gestor_taller@example.com |    5 | ACTIVO
```

## 🧪 Flujo Completo de Testing

### Paso 1: Generar usuarios
```http
POST http://localhost:8000/auth/seed-test-users
```

### Paso 2: Copiar credenciales de la respuesta

### Paso 3: Testear cada rol

#### Admin:
```http
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "TestPassword123!"
}
```

#### Operador:
```http
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "email": "operador@example.com",
  "password": "TestPassword123!"
}
```

#### Cliente:
```http
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "email": "cliente@example.com",
  "password": "TestPassword123!"
}
```

### Paso 4: Obtener usuario actual (validar token)
```http
GET http://localhost:8000/auth/me
Authorization: Bearer {{token}}
```

### Paso 5: Testear endpoints protegidos
```http
GET http://localhost:8000/vehiculos
Authorization: Bearer {{token}}

GET http://localhost:8000/incidentes
Authorization: Bearer {{token}}
```

## 🎯 Casos de Uso

### 1. Testing del RBAC (Role-Based Access Control)
```javascript
// Frontend - Mostrar menú según rol del usuario
const userRole = user.rol.nombre;

if (userRole === 'admin') {
  // Mostrar: Dashboard Admin, Gestión de Marcas, Gestión de Usuarios
} else if (userRole === 'operador') {
  // Mostrar: Cola de Incidentes, Asignación de Técnicos
} else if (userRole === 'cliente') {
  // Mostrar: Mis Vehículos, Reportar Incidente
} else if (userRole === 'tecnico') {
  // Mostrar: Mis Órdenes, Captura de Evidencia
}
```

### 2. Testing de Endpoints por Rol
- Admin: Crear marcas, modelos, gestionar usuarios
- Operador: Ver incidentes pendientes, cambiar estados
- Cliente: Registrar vehículos, reportar incidentes
- Técnico: Ver asignaciones, actualizar estados

### 3. Testing del Frontend
1. Abre el frontend (Angular)
2. Llama al endpoint seed-test-users desde consola o Postman
3. Login con cada usuario de prueba
4. Verifica ruta y menú dinámico según rol

## 🚨 Troubleshooting

### Error: "403 Forbidden - DEBUG_MODE is disabled"
**Solución:** Activa `DEBUG_MODE=True` en `.env`

### Error: "Rol X no existe"
**Solución:** Verifica que los 5 roles fueron creados en startup. Busca en console:
```
✓ Rol 'admin' creado
✓ Rol 'operador' creado
✓ Rol 'tecnico' creado
✓ Rol 'cliente' creado
✓ Rol 'gestor_taller' creado
```

### Error: "Email ya está registrado"
**Solución:** El endpoint omitirá los usuarios que ya existan. Puedes:
- Ejecutar de nuevo (creará solo los faltantes)
- O eliminar los usuarios de la BD y ejecutar nuevamente

### Token inválido al hacer login
**Solución:** Verifica que:
1. La contraseña es exactamente `TestPassword123!` (¡incluyendo el `!`)
2. El email existe en la BD
3. El usuario está ACTIVO

## 📝 Próximas Mejoras

- [ ] Endpoint para resetear/limpiar usuarios de prueba
- [ ] Generar datos de prueba relacionados (vehículos, incidentes)
- [ ] Configurar contraseñas diferentes por rol
- [ ] Endpoint para cambiar rol de un usuario (admin only)

## 📚 Referencias

- Documentación de config: `config.py`
- Documentación de Auth: `routers/auth.py`
- Documentación de startup: `main.py`
- Todas las credenciales: Esta guía
