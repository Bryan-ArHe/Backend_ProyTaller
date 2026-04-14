"""
test_api.py - Script de prueba para los endpoints de autenticación
Ejecuta: python test_api.py
"""

import requests
import json
from typing import Dict, Any

# URL base de la API
BASE_URL = "http://localhost:8000"

# Headers por defecto
HEADERS = {"Content-Type": "application/json"}

# Token global para usar en pruebas autenticadas
token = None


def print_response(response: requests.Response, title: str = "Response"):
    """Imprime la respuesta de forma legible"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print()


def test_health_check():
    """Prueba el endpoint de health check"""
    print("\n🏥 Probando Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check")
    return response.status_code == 200


def test_register():
    """Prueba el registro de un nuevo usuario"""
    global token
    
    print("\n✍️ Probando Registro de Usuario...")
    
    user_data = {
        "email": "juan@example.com",
        "telefono": "3001234567",
        "password": "MiContraseña123",
        "id_rol": 3  # Usuario estándar
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=user_data,
        headers=HEADERS
    )
    
    print_response(response, "Registro de Usuario")
    
    if response.status_code == 201:
        print("✅ Usuario registrado exitosamente")
        return True
    else:
        print("❌ Error al registrar usuario")
        return False


def test_register_duplicate():
    """Prueba registrar un usuario con email duplicado"""
    print("\n⚠️ Probando Registro Duplicado (debe fallar)...")
    
    user_data = {
        "email": "juan@example.com",  # Mismo email
        "telefono": "3009999999",
        "password": "OtraContraseña123",
        "id_rol": 3
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=user_data,
        headers=HEADERS
    )
    
    print_response(response, "Registro Duplicado (Error Esperado)")
    
    if response.status_code == 400:
        print("✅ Validación correcta: rechazó email duplicado")
        return True
    else:
        print("❌ No se validó correctamente el email duplicado")
        return False


def test_login():
    """Prueba el login y obtención de token"""
    global token
    
    print("\n🔐 Probando Login...")
    
    login_data = {
        "email": "juan@example.com",
        "password": "MiContraseña123"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_data,
        headers=HEADERS
    )
    
    print_response(response, "Login")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Login exitoso")
        print(f"📍 Token obtenido: {token[:50]}...")
        return True
    else:
        print("❌ Error en el login")
        return False


def test_login_invalid_password():
    """Prueba login con contraseña incorrecta"""
    print("\n🔓 Probando Login con Contraseña Incorrecta (debe fallar)...")
    
    login_data = {
        "email": "juan@example.com",
        "password": "ContraseñaIncorrecta"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_data,
        headers=HEADERS
    )
    
    print_response(response, "Login Inválido (Error Esperado)")
    
    if response.status_code == 401:
        print("✅ Validación correcta: rechazó contraseña incorrecta")
        return True
    else:
        print("❌ No se validó correctamente la contraseña")
        return False


def test_get_current_user():
    """Prueba obtener datos del usuario autenticado"""
    global token
    
    if not token:
        print("\n⚠️ No hay token disponible. Ejecuta primero test_login()")
        return False
    
    print("\n👤 Probando Obtener Datos del Usuario Autenticado...")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers=headers
    )
    
    print_response(response, "Datos del Usuario Actual")
    
    if response.status_code == 200:
        print("✅ Datos del usuario obtenidos exitosamente")
        return True
    else:
        print("❌ Error al obtener datos del usuario")
        return False


def test_get_current_user_invalid_token():
    """Prueba acceso con token inválido"""
    print("\n🚫 Probando Acceso con Token Inválido (debe fallar)...")
    
    headers = HEADERS.copy()
    headers["Authorization"] = "Bearer token_invalido_xyz"
    
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers=headers
    )
    
    print_response(response, "Token Inválido (Error Esperado)")
    
    if response.status_code == 401:
        print("✅ Validación correcta: rechazó token inválido")
        return True
    else:
        print("❌ No se validó correctamente el token")
        return False


def test_get_current_user_without_token():
    """Prueba acceso sin token"""
    print("\n🔓 Probando Acceso sin Token (debe fallar)...")
    
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers=HEADERS
    )
    
    print_response(response, "Sin Token (Error Esperado)")
    
    if response.status_code == 403:
        print("✅ Validación correcta: rechazó solicitud sin token")
        return True
    else:
        print("❌ No se validó correctamente la falta de token")
        return False


def run_all_tests():
    """Ejecuta todas las pruebas"""
    
    print("\n" + "="*60)
    print("🧪 SUITE DE PRUEBAS - MÓDULO DE AUTENTICACIÓN")
    print("="*60)
    
    results = {
        "Health Check": test_health_check(),
        "Registro de Usuario": test_register(),
        "Login": test_login(),
        "Login con Contraseña Incorrecta": test_login_invalid_password(),
        "Registro Duplicado": test_register_duplicate(),
        "Obtener Datos del Usuario": test_get_current_user(),
        "Token Inválido": test_get_current_user_invalid_token(),
        "Sin Token": test_get_current_user_without_token(),
    }
    
    # Resumen de resultados
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📈 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron!")
    else:
        print(f"\n⚠️ {total - passed} prueba(s) fallaron")


if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar a la API")
        print(f"   Asegúrate de que la aplicación esté corriendo en {BASE_URL}")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
