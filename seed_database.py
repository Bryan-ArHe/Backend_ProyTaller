"""
seed_database.py - Script para generar usuarios de prueba
Ejecuta: python seed_database.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🚀 Iniciando proceso de migración de usuarios de prueba...\n")
    
    # Paso 1: Verificar que el servidor está activo
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ El servidor no está respondiendo. Inicia la app con:")
            print("   python -m uvicorn main:app --reload")
            return
        print("✅ Servidor activo en", BASE_URL)
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        print("   Inicia la app con: python -m uvicorn main:app --reload")
        return
    
    # Paso 2: Ejecutar seed-test-users
    print("\n📝 Ejecutando endpoint seed-test-users...")
    try:
        response = requests.post(f"{BASE_URL}/auth/seed-test-users")
        
        if response.status_code == 201:
            data = response.json()
            print(f"\n✅ {data['mensaje']}")
            print(f"\n📊 Usuarios creados: {data['total_usuarios_creados']}\n")
            
            # Mostrar los usuarios creados
            print("=" * 70)
            print("👥 USUARIOS GENERADOS:")
            print("=" * 70)
            for usuario in data['usuarios']:
                print(f"\n📧 Email: {usuario['email']}")
                print(f"   Contraseña: {usuario['password']}")
                print(f"   Rol: {usuario['rol_nombre'].upper()} (ID: {usuario['id_rol']})")
                print(f"   Teléfono: {usuario['telefono']}")
                print(f"   Descripción: {usuario['descripcion']}")
            
            print("\n" + "=" * 70)
            print("✅ MIGRACIÓN COMPLETADA")
            print("=" * 70)
            print("\n💡 Próximos pasos:")
            print("   1. Abre pgAdmin y verifica que aparezcan los 5 usuarios")
            print("   2. Usa estas credenciales para testear el frontend")
            print("   3. Prueba el RBAC (filtrado dinámico de menú por rol)")
            
        elif response.status_code == 403:
            error_data = response.json()
            print(f"\n❌ {error_data['detail']}")
            print("\n📍 Solución: Asegúrate que DEBUG_MODE=True en .env")
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.json())
            
    except Exception as e:
        print(f"\n❌ Error ejecutando seed: {e}")
        print("   Verifica que el servidor está activo")

if __name__ == "__main__":
    main()
