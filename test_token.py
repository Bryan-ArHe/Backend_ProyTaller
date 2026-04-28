"""
test_token.py - Generador manual de JWT tokens para testing
Uso: python test_token.py
"""
from security.jwt_handler import create_access_token
from datetime import timedelta

print("=" * 70)
print("🔐 GENERADOR DE JWT TOKENS")
print("=" * 70)

# Generar tokens para cada rol
usuarios_prueba = [
    {"email": "admin@example.com", "id": 1, "rol": "Administrador"},
    {"email": "tecnico@example.com", "id": 2, "rol": "Tecnico"},
    {"email": "cliente@example.com", "id": 3, "rol": "Cliente"},
    {"email": "gestor@example.com", "id": 4, "rol": "GestorTaller"},
]

for usuario in usuarios_prueba:
    # Crear token con duración de 7 días
    token = create_access_token(
        data={
            "sub": usuario["email"],
            "id_usuario": usuario["id"],
            "rol": usuario["rol"]
        },
        expires_delta=timedelta(days=7)
    )
    
    print(f"\n👤 Usuario: {usuario['email']}")
    print(f"   Rol: {usuario['rol']}")
    print(f"   Token (válido 7 días):")
    print(f"   {token}")
    print()

print("=" * 70)
print("💡 CÓMO USAR EN POSTMAN/SWAGGER:")
print("   1. Copiar uno de los tokens arriba")
print("   2. En Postman: Header 'Authorization: Bearer <token>'")
print("   3. En Swagger: Click 'Authorize' y pegar el token")
print("=" * 70)
