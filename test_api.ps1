# API Testing - Comandos CURL
# Ejecuta estos comandos desde PowerShell o cmd para probar los endpoints

# ==========================================
# 1. HEALTH CHECK
# ==========================================

# Verificar que la API está activa
curl -X GET "http://localhost:8000/health"


# ==========================================
# 2. REGISTRO DE USUARIO
# ==========================================

# Registrar un nuevo usuario
curl -X POST "http://localhost:8000/auth/register" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "juan@example.com",
    "telefono": "3001234567",
    "password": "MiContraseña123",
    "id_rol": 3
  }'

# Registrar otro usuario
curl -X POST "http://localhost:8000/auth/register" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "maria@example.com",
    "telefono": "3009876543",
    "password": "OtraContraseña456",
    "id_rol": 2
  }'

# Intentar registrar con email duplicado (debe fallar con 400)
curl -X POST "http://localhost:8000/auth/register" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "juan@example.com",
    "telefono": "3119999999",
    "password": "OtraContraseña789",
    "id_rol": 1
  }'

# Intentar registrar con rol inexistente (debe fallar con 400)
curl -X POST "http://localhost:8000/auth/register" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "pedro@example.com",
    "telefono": "3108888888",
    "password": "ContraseñaValida123",
    "id_rol": 999
  }'


# ==========================================
# 3. LOGIN - OBTENER TOKEN
# ==========================================

# Login exitoso (almacena el token)
$response = curl -X POST "http://localhost:8000/auth/login" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "juan@example.com",
    "password": "MiContraseña123"
  }' | ConvertFrom-Json

$token = $response.access_token

Write-Host "Token obtenido:" $token

# Login con contraseña incorrecta (debe fallar con 401)
curl -X POST "http://localhost:8000/auth/login" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "juan@example.com",
    "password": "ContraseñaIncorrecta"
  }'

# Login con email no registrado (debe fallar con 401)
curl -X POST "http://localhost:8000/auth/login" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "noexiste@example.com",
    "password": "MiContraseña123"
  }'


# ==========================================
# 4. OBTENER DATOS DEL USUARIO AUTENTICADO
# ==========================================

# Nota: Reemplaza TOKEN_AQUI con el token obtenido en login

# Solicitar datos del usuario autenticado (requiere token válido)
curl -X GET "http://localhost:8000/auth/me" `
  -H "Authorization: Bearer TOKEN_AQUI"

# Sin token (debe fallar con 403)
curl -X GET "http://localhost:8000/auth/me"

# Con token inválido (debe fallar con 401)
curl -X GET "http://localhost:8000/auth/me" `
  -H "Authorization: Bearer token_invalido_xyz"


# ==========================================
# 5. DOCUMENTACIÓN INTERACTIVA
# ==========================================

# Acceso a la documentación Swagger UI
# Abre en el navegador: http://localhost:8000/docs

# Acceso a la documentación ReDoc
# Abre en el navegador: http://localhost:8000/redoc


# ==========================================
# SCRIPT COMPLETO DE PRUEBA
# ==========================================

param(
    [string]$email = "test_user@example.com",
    [string]$telefono = "3105551234",
    [string]$password = "TestPassword123"
)

Write-Host "🔵 Iniciando pruebas de API..." -ForegroundColor Cyan

# 1. Health Check
Write-Host "`n✓ Health Check" -ForegroundColor Green
curl -X GET "http://localhost:8000/health" | Write-Host

# 2. Registrar usuario
Write-Host "`n✓ Registrando usuario..." -ForegroundColor Green
$register_response = curl -X POST "http://localhost:8000/auth/register" `
  -H "Content-Type: application/json" `
  -d @"
{
    "email": "$email",
    "telefono": "$telefono",
    "password": "$password",
    "id_rol": 3
}
"@ -s | ConvertFrom-Json

Write-Host ($register_response | ConvertTo-Json)

# 3. Login
Write-Host "`n✓ Realizando login..." -ForegroundColor Green
$login_response = curl -X POST "http://localhost:8000/auth/login" `
  -H "Content-Type: application/json" `
  -d @"
{
    "email": "$email",
    "password": "$password"
}
"@ -s | ConvertFrom-Json

$token = $login_response.access_token
Write-Host "Token: $($token.Substring(0, 50))..."

# 4. Obtener datos del usuario
Write-Host "`n✓ Obteniendo datos del usuario..." -ForegroundColor Green
curl -X GET "http://localhost:8000/auth/me" `
  -H "Authorization: Bearer $token" | Write-Host

Write-Host "`n✅ Pruebas completadas" -ForegroundColor Green
