"""
test_admin_endpoints.py - Verifica que el admin tiene acceso a TODOS los módulos
Prueba login, auth, y acceso a endpoints críticos con permisos de admin
"""

import requests
import json
import sys

# Configuración
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "123456"

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
            print(f"   {RED}Error: {error}{RESET}")
        self.results["failed"].append(f"{message} - {error}")
    
    def log_blocked(self, message: str):
        print(f"{YELLOW}⚠️  {message}{RESET}")
        self.results["blocked"].append(message)
    
    def test_login(self) -> bool:
        """1. Prueba login del admin"""
        print(f"\n{BOLD}1️⃣  PROBANDO LOGIN DEL ADMIN{RESET}")
        try:
            data = {
                "username": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                data=data
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
                if user["rol"]["nombre"] == "Administrador":
                    self.log_success(f"✓ /auth/me retorna usuario admin")
                    self.log_success(f"  - Email: {user['email']}")
                    self.log_success(f"  - Nombre: {user['nombre']} {user['apellido']}")
                    self.log_success(f"  - Rol: {user['rol']['nombre']}")
                    return True
                else:
                    self.log_error(f"Usuario no es admin: {user['rol']['nombre']}")
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
                self.log_error(f"{method} {endpoint}", f"Status {status}: {response.text[:100]}")
                return False
        except Exception as e:
            self.log_error(f"{method} {endpoint}", str(e))
            return False
    
    def test_usuarios_endpoints(self) -> bool:
        """3. Prueba acceso a endpoints de USUARIOS"""
        print(f"\n{BOLD}3️⃣  PROBANDO MÓDULO: USUARIOS{RESET}")
        results = []
        
        # GET /usuarios (listar todos)
        results.append(self.test_endpoint("GET", "/usuarios", description="(Listar usuarios)"))
        
        # GET /usuarios/me (obtener perfil propio)
        results.append(self.test_endpoint("GET", "/usuarios/me", description="(Obtener mi perfil)"))
        
        # PUT /usuarios/me (actualizar perfil propio)
        update_data = {
            "nombre": "Bryan",
            "apellido": "Arauz Herrera",
            "telefono": "70012355"
        }
        results.append(self.test_endpoint("PUT", "/usuarios/me", [200], update_data, 
                                         "(Actualizar mi perfil)"))
        
        return all(results)
    
    def test_talleres_endpoints(self) -> bool:
        """4. Prueba acceso a endpoints de TALLERES"""
        print(f"\n{BOLD}4️⃣  PROBANDO MÓDULO: TALLERES{RESET}")
        results = []
        
        # GET /talleres (listar)
        results.append(self.test_endpoint("GET", "/talleres", 
                                         description="(Listar talleres)"))
        
        # POST /talleres (crear)
        new_taller = {
            "nombre": "Test Taller",
            "direccion": "Cra 7 #50-10",
            "telefono": "555-1234",
            "id_propietario": 1,
            "activo": True
        }
        results.append(self.test_endpoint("POST", "/talleres", [201], new_taller, 
                                         "(Crear taller)"))
        
        # GET /talleres/1 (obtener taller)
        results.append(self.test_endpoint("GET", "/talleres/1", 
                                         description="(Obtener taller)"))
        
        return all(results)
    
    def test_tecnicos_endpoints(self) -> bool:
        """5. Prueba acceso a endpoints de TÉCNICOS"""
        print(f"\n{BOLD}5️⃣  PROBANDO MÓDULO: TÉCNICOS{RESET}")
        results = []
        
        # GET /tecnicos (listar)
        results.append(self.test_endpoint("GET", "/tecnicos", 
                                         description="(Listar técnicos)"))
        
        # GET /tecnicos/libres (obtener libres)
        results.append(self.test_endpoint("GET", "/tecnicos/libres", 
                                         description="(Técnicos libres)"))
        
        return all(results)
    
    def test_vehiculos_endpoints(self) -> bool:
        """6. Prueba acceso a endpoints de VEHÍCULOS"""
        print(f"\n{BOLD}6️⃣  PROBANDO MÓDULO: VEHÍCULOS{RESET}")
        results = []
        
        # GET /vehiculos (listar)
        results.append(self.test_endpoint("GET", "/vehiculos", 
                                         description="(Listar vehículos)"))
        
        return all(results)
    
    def test_incidentes_endpoints(self) -> bool:
        """7. Prueba acceso a endpoints de INCIDENTES"""
        print(f"\n{BOLD}7️⃣  PROBANDO MÓDULO: INCIDENTES{RESET}")
        results = []
        
        # GET /incidentes (listar)
        results.append(self.test_endpoint("GET", "/incidentes", 
                                         description="(Listar incidentes)"))
        
        return all(results)
    
    def test_dashboard_endpoints(self) -> bool:
        """8. Prueba acceso a endpoints de DASHBOARD"""
        print(f"\n{BOLD}8️⃣  PROBANDO MÓDULO: DASHBOARD{RESET}")
        results = []
        
        # GET /dashboard/metrics
        results.append(self.test_endpoint("GET", "/dashboard/metrics", 
                                         description="(Obtener métricas)"))
        
        return all(results)
    
    def test_bitacora_endpoints(self) -> bool:
        """9. Prueba acceso a endpoints de BITÁCORA"""
        print(f"\n{BOLD}9️⃣  PROBANDO MÓDULO: BITÁCORA{RESET}")
        results = []
        
        # GET /bitacora
        results.append(self.test_endpoint("GET", "/bitacora", 
                                         description="(Listar eventos)"))
        
        return all(results)
    
    def test_roles_endpoints(self) -> bool:
        """10. Prueba acceso a endpoints de ROLES"""
        print(f"\n{BOLD}🔟 PROBANDO MÓDULO: ROLES{RESET}")
        results = []
        
        # GET /roles
        results.append(self.test_endpoint("GET", "/roles", 
                                         description="(Listar roles)"))
        
        # GET /roles/permisos
        results.append(self.test_endpoint("GET", "/roles/permisos", 
                                         description="(Listar permisos)"))
        
        return all(results)
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas"""
        print(f"\n{BOLD}{'='*80}{RESET}")
        print(f"{BOLD}🧪 PRUEBA COMPLETA DE ACCESO DE ADMIN{RESET}")
        print(f"{BOLD}{'='*80}{RESET}")
        
        # 1. Login
        if not self.test_login():
            print(f"\n{RED}❌ Login fallido - No se pueden continuar las pruebas{RESET}")
            return False
        
        # 2. Get current user
        if not self.test_auth_me():
            print(f"\n{RED}❌ /auth/me falló - Token inválido{RESET}")
            return False
        
        # Pruebas de módulos
        self.test_usuarios_endpoints()
        self.test_talleres_endpoints()
        self.test_tecnicos_endpoints()
        self.test_vehiculos_endpoints()
        self.test_incidentes_endpoints()
        self.test_dashboard_endpoints()
        self.test_bitacora_endpoints()
        self.test_roles_endpoints()
        
        # Resumen final
        self.print_summary()
    
    def print_summary(self):
        """Imprime resumen de resultados"""
        print(f"\n{BOLD}{'='*80}{RESET}")
        print(f"{BOLD}📊 RESUMEN DE PRUEBAS{RESET}")
        print(f"{BOLD}{'='*80}{RESET}")
        
        total_passed = len(self.results["passed"])
        total_failed = len(self.results["failed"])
        total_blocked = len(self.results["blocked"])
        total = total_passed + total_failed + total_blocked
        
        print(f"\n{GREEN}✅ Exitosas: {total_passed}/{total}{RESET}")
        print(f"{RED}❌ Fallidas:  {total_failed}/{total}{RESET}")
        print(f"{YELLOW}⚠️  Bloqueadas: {total_blocked}/{total}{RESET}")
        
        if total_failed > 0:
            print(f"\n{RED}{BOLD}Pruebas Fallidas:{RESET}")
            for i, failure in enumerate(self.results["failed"], 1):
                print(f"  {i}. {failure}")
        
        if total_blocked > 0:
            print(f"\n{YELLOW}{BOLD}Acceso Bloqueado (Admin debería tener acceso):{RESET}")
            for i, blocked in enumerate(self.results["blocked"], 1):
                print(f"  {i}. {blocked}")
        
        success_rate = (total_passed / total * 100) if total > 0 else 0
        print(f"\n{BOLD}Tasa de éxito: {success_rate:.1f}%{RESET}\n")
        
        if total_failed == 0 and total_blocked == 0:
            print(f"{GREEN}{BOLD}🎉 ¡TODAS LAS PRUEBAS PASARON! El admin tiene acceso completo.{RESET}\n")
            return True
        else:
            print(f"{RED}{BOLD}⚠️  Hay problemas que necesitan ser corregidos.{RESET}\n")
            return False


if __name__ == "__main__":
    try:
        tester = AdminAccessTester()
        tester.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Prueba interrumpida por el usuario{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Error inesperado: {str(e)}{RESET}")
        sys.exit(1)
