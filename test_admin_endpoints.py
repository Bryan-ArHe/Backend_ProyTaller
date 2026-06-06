# -*- coding: utf-8 -*-
"""
test_admin_endpoints.py - Verifica que el admin tiene acceso a TODOS los módulos
Prueba login, auth, y acceso a endpoints críticos con permisos de admin.
Incluye validación para el núcleo transaccional de incidentes, cotizaciones y órdenes.
"""

import requests
import json
import sys

# Configuración
BASE_URL = "http://localhost:8000"  # Cambiar si usas prefijos como /api/v1
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "12345678"

# Colores para terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


class AdminAccessTester:
    def __init__(self):
        self.token = None
        self.session = requests.Session()
        self.results = {
            "passed": [],
            "failed": [],
            "blocked": []
        }
    
    def log_success(self, message: str):
        print(f"{GREEN}✅ {message}{RESET}")
        self.results["passed"].append(message)
    
    def log_error(self, message: str, error: str = ""):
        print(f"{RED}❌ {message}{RESET}")
        if error:
            print(f"   {RED}Error: {error[:200]}{RESET}")  # Truncado para no saturar
        self.results["failed"].append(f"{message} - {error[:100]}")
    
    def log_blocked(self, message: str):
        print(f"{YELLOW}⚠️  {message}{RESET}")
        self.results["blocked"].append(message)
    
    def test_login(self) -> bool:
        """1. Prueba login del admin"""
        print(f"\n{BOLD}1️⃣  PROBANDO LOGIN DEL ADMIN{RESET}")
        try:
            form_data = {
                "username": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                data=form_data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.token = result.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                self.log_success(f"Login exitoso - Token obtenido")
                return True
            else:
                self.log_error(f"Login fallido (Status: {response.status_code})", response.text)
                return False
        except Exception as e:
            self.log_error("Error en login", str(e))
            return False
    
    def test_auth_me(self) -> bool:
        """2. Prueba GET /auth/me"""
        print(f"\n{BOLD}2️⃣  PROBANDO /auth/me{RESET}")
        try:
            response = self.session.get(f"{BASE_URL}/auth/me")
            
            if response.status_code == 200:
                user = response.json()
                rol_data = user.get("rol", {})
                rol_nombre = rol_data.get("nombre") if isinstance(rol_data, dict) else rol_data
                
                if rol_nombre in ["Administrador", "Gestor"]:
                    self.log_success(f"✓ /auth/me retorna usuario autorizado")
                    self.log_success(f"  - Email: {user.get('email')}")
                    self.log_success(f"  - Rol: {rol_nombre}")
                    return True
                else:
                    self.log_error(f"Usuario no es admin/gestor: {rol_nombre}")
                    return False
            else:
                self.log_error(f"GET /auth/me falló (Status: {response.status_code})", response.text)
                return False
        except Exception as e:
            self.log_error("Error en /auth/me", str(e))
            return False
    
    def test_endpoint(self, method: str, endpoint: str, expected_status: list = [200, 201], 
                      data: dict = None, description: str = "") -> bool:
        """Prueba genérica de un endpoint"""
        try:
            url = f"{BASE_URL}{endpoint}"
            
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PUT":
                response = self.session.put(url, json=data)
            elif method == "DELETE":
                response = self.session.delete(url)
            else:
                self.log_error(f"Método {method} no soportado")
                return False
            
            status = response.status_code
            
            if status in expected_status:
                self.log_success(f"✓ {method} {endpoint} → {status} {description}")
                return True
            elif status == 403:
                self.log_blocked(f"⚠️  {method} {endpoint} → 403 FORBIDDEN (Admin bloqueado)")
                return False
            else:
                self.log_error(f"{method} {endpoint}", f"Status {status}: {response.text[:120]}")
                return False
        except Exception as e:
            self.log_error(f"{method} {endpoint}", str(e))
            return False
    
    def test_usuarios_endpoints(self):
        print(f"\n{BOLD}3️⃣  PROBANDO MÓDULO: USUARIOS{RESET}")
        self.test_endpoint("GET", "/usuarios/", description="(Listar usuarios)") # Agregada /
        self.test_endpoint("GET", "/usuarios/me/", description="(Obtener mi perfil)")
    
    def test_talleres_endpoints(self):
        print(f"\n{BOLD}4️⃣  PROBANDO MÓDULO: TALLERES{RESET}")
        self.test_endpoint("GET", "/talleres", description="(Listar talleres del tenant)")
        
        # Ajustado a payload JSON serializable esperado por Pydantic para PostGIS
        new_taller = {
            "nombre": "Sucursal Norte Express",
            "direccion": "Av. Banzer entre 4to y 5to Anillo",
            "ubicacion_coordenadas": {"longitude": -63.1720, "latitude": -17.7634}
        }
        self.test_endpoint("POST", "/talleres", [201], new_taller, "(Crear taller con coordenadas)")
        self.test_endpoint("GET", "/talleres/1", description="(Obtener taller y técnicos)")
    
    def test_tecnicos_endpoints(self):
        print(f"\n{BOLD}5️⃣  PROBANDO MÓDULO: TÉCNICOS{RESET}")
        self.test_endpoint("GET", "/tecnicos/", description="(Listar técnicos)") # Agregada /
        self.test_endpoint("GET", "/tecnicos/libres/", description="(Técnicos libres)") # Agregada /

    def test_vehiculos_endpoints(self):
        print(f"\n{BOLD}6️⃣  PROBANDO MÓDULO: VEHÍCULOS{RESET}")
        self.test_endpoint("GET", "/vehiculos/", description="(Listar vehículos)") # Agregada /
    
    def test_incidentes_endpoints(self):
        print(f"\n{BOLD}7️⃣  PROBANDO MÓDULO: INCIDENTES (E INTEGRADAS){RESET}")
        self.test_endpoint("GET", "/incidentes", description="(Listar incidentes activos)")
        
        # Ajustado a esquema de entrada JSON plano para el motor de triaje
        new_incidente = {
            "id_cliente": 1,
            "id_vehiculo": 1,
            "descripcion": "Auxilio: Motor sobrecalentado en Av. Las Américas",
            "ubicacion_averia": {"longitude": -63.1812, "latitude": -17.7924}
        }
        self.test_endpoint("POST", "/incidentes", [201], new_incidente, "(Reportar incidente espacial)")

    def test_nuevas_tablas_transaccionales(self):
        """NUEVO: Verifica accesos a Cotizaciones, Solicitudes y Mensajes"""
        print(f"\n{BOLD}🆕 PROBANDO NÚCLEO FINANCIERO Y LOGÍSTICO{RESET}")
        
        # Pruebas en el flujo de Cotizaciones
        self.test_endpoint("GET", "/cotizaciones", description="(Listar cotizaciones emitidas)")
        
        # Pruebas en el flujo de Solicitudes de Servicio (Las Órdenes)
        self.test_endpoint("GET", "/solicitudes-servicio", description="(Listar órdenes de trabajo)")
        self.test_endpoint("GET", "/solicitudes-servicio/1/detalles", description="(Ver repuestos e histórico consumido de una orden)")
        
        # Pruebas en el flujo de Mensajes In-App
        self.test_endpoint("GET", "/solicitudes-servicio/1/mensajes", description="(Auditar historial del chat de la orden)")

    def test_dashboard_endpoints(self):
        print(f"\n{BOLD}8️⃣  PROBANDO MÓDULO: DASHBOARD{RESET}")
        self.test_endpoint("GET", "/dashboard/metrics", description="(Obtener métricas)")
    
    def test_bitacora_endpoints(self):
        print(f"\n{BOLD}9️⃣  PROBANDO MÓDULO: BITÁCORA{RESET}")
        self.test_endpoint("GET", "/bitacora", description="(Listar eventos de auditoría)")
    
    def test_roles_endpoints(self):
        print(f"\n{BOLD}🔟 PROBANDO MÓDULO: ROLES{RESET}")
        self.test_endpoint("GET", "/roles", description="(Listar roles)")
        self.test_endpoint("GET", "/roles/permisos", description="(Listar permisos)")
    
    def run_all_tests(self):
        """Ejecuta la suite de pruebas completa"""
        print(f"\n{BOLD}{'='*80}{RESET}")
        print(f"{BOLD}🧪 SUITE DE VERIFICACIÓN DE CONTROLADORES - ACCESO ADMIN{RESET}")
        print(f"{BOLD}{'='*80}{RESET}")
        
        if not self.test_login():
            print(f"\n{RED}❌ Login fallido - Deteniendo ejecución de la suite{RESET}")
            return False
        
        if not self.test_auth_me():
            print(f"\n{RED}❌ /auth/me falló - Sesión denegada{RESET}")
            return False
        
        # Ejecución secuencial de módulos
        self.test_usuarios_endpoints()
        self.test_talleres_endpoints()
        self.test_tecnicos_endpoints()
        self.test_vehiculos_endpoints()
        self.test_incidentes_endpoints()
        self.test_nuevas_tablas_transaccionales()  # Activación de nuevas pruebas
        self.test_dashboard_endpoints()
        self.test_bitacora_endpoints()
        self.test_roles_endpoints()
        
        self.print_summary()
    
    def print_summary(self):
        print(f"\n{BOLD}{'='*80}{RESET}")
        print(f"{BOLD}📊 RESUMEN DE COMPILACIÓN Y ACCESOS{RESET}")
        print(f"{BOLD}{'='*80}{RESET}")
        
        passed = len(self.results["passed"])
        failed = len(self.results["failed"])
        blocked = len(self.results["blocked"])
        total = passed + failed + blocked
        
        print(f"\n{GREEN}✅ Exitosas: {passed}/{total}{RESET}")
        print(f"{RED}❌ Fallidas:  {failed}/{total}{RESET}")
        print(f"{YELLOW}⚠️  Bloqueadas: {blocked}/{total}{RESET}")
        
        if failed > 0:
            print(f"\n{RED}{BOLD}Rutas con fallas o desajustes de esquemas:{RESET}")
            for i, failure in enumerate(self.results["failed"], 1):
                print(f"  {i}. {failure}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"\n{BOLD}Tasa de Cobertura Exitosa: {success_rate:.1f}%{RESET}\n")
        
        if failed == 0 and blocked == 0:
            print(f"{GREEN}{BOLD}🎉 ¡SISTEMA INTEGRADO EXITOSAMENTE! Las rutas son totalmente accesibles.{RESET}\n")
        else:
            print(f"{RED}{BOLD}⚠️  Revisa los códigos de error en la consola del Backend.{RESET}\n")


if __name__ == "__main__":
    try:
        tester = AdminAccessTester()
        tester.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Suite de pruebas cancelada por el operador.{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Excepción del script de pruebas: {str(e)}{RESET}")
        sys.exit(1)