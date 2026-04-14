"""
DOCUMENTACIÓN CICLO 1: GESTIÓN DE VEHÍCULOS E INCIDENTES
========================================================

Este documento describe la implementación completa del Ciclo 1 del proyecto:
- CU1 a CU4: Gestión de Usuarios, Roles y Permisos (implementado en Módulo 1)
- CU5 a CU7: Gestión de Vehículos, Marcas y Modelos
- CU8 y CU9: Reporte de Incidentes y Captura de Evidencia Multimedia

ESTRUCTURA DEL CÓDIGO
=====================

1. MODELOS DE BASE DE DATOS (SQLAlchemy ORM)
   └─ models/
      ├── user.py                  [Existente] Usuario, Rol, EstadoCuenta
      ├── marca_modelo.py         [NUEVO] Marca, Modelo (relación 1:N)
      ├── vehiculo.py             [NUEVO] Vehículo (relación con Usuario y Modelo)
      └── incidente.py            [NUEVO] Incidente, Evidencia, Estados, Prioridades

2. ESQUEMAS PYDANTIC (Validación y Serialización)
   └─ schemas/
      ├── user.py                 [Existente] UsuarioCreate, UsuarioResponse, etc.
      ├── vehiculo.py             [NUEVO] Vehículos, Marcas, Modelos
      └── incidente.py            [NUEVO] Incidentes, Evidencias, TriajeIA

3. FUNCIONES CRUD (Data Access Layer)
   └─ crud/
      ├── vehiculo.py             [NUEVO] CRUD completo para Vehículos, Marcas, Modelos
      └── incidente.py            [NUEVO] CRUD para Incidentes, Evidencias + Sistema IA

4. ROUTERS (Endpoints API)
   └─ routers/
      ├── auth.py                 [Existente] Autenticación
      ├── dashboard.py            [Existente] Métricas por rol
      ├── vehiculos.py            [NUEVO] Endpoints CRUD de vehículos
      └── incidentes.py           [NUEVO] Endpoints de reportes e incidentes

5. CONFIGURACIÓN E INTEGRACIÓN
   └─ main.py                     [ACTUALIZADO] Registro de nuevos routers


MODELO DE DATOS (Schema Físico)
===============================

RELACIONES 1:

  Rol (1) ──────── (N) Usuario
                       │
                       ├─── (1) ─────────── (N) Vehículo
                       │                         │
                       │                         └─── (1/N) Modelo
                       │
                       └─── (1) ─────────── (N) Incidente
                                                │
                                                └─── (1) ─── (N) Evidencia

TABLAS:
  - roles (nueva relación sin cambios)
  - usuarios (actualizada con relaciones)
  - marcas (NUEVA, normalización 3FN)
  - modelos (NUEVA, FK a marcas)
  - vehiculos (NUEVA, FK a usuarios + modelos)
  - incidentes (NUEVA, FK a vehiculos + usuarios)
  - evidencias (NUEVA, FK a incidentes)


NORMALIZACIÓN 3FN
=================

✅ Separación de Catálogos Maestros:
   - Marca y Modelo son tablas separadas (evita redundancia)
   - Ejemplo: Toyota aparece 1 vez, no se repite por cada modelo

✅ Relaciones N:1 bien definidas:
   - Vehículo pertenece a 1 Modelo
   - Modelo pertenece a 1 Marca
   - Vehículo pertenece a 1 Usuario (cliente)

✅ Cascadas de eliminación:
   - Eliminar Marca → Elimina sus Modelos → Elimina sus Vehículos
   - Eliminar Usuario → Elimina sus Vehículos e Incidentes
   - Eliminar Incidente → Elimina sus Evidencias


ENDPOINTS (RESUMEN)
===================

MARCAS:
  GET    /vehiculos/marcas              → Listar todas
  GET    /vehiculos/marcas/{id}         → Obtener con modelos
  POST   /vehiculos/marcas              → Crear (ADMIN)
  DELETE /vehiculos/marcas/{id}         → Eliminar (ADMIN)

MODELOS:
  GET    /vehiculos/marcas/{id}/modelos → Listar por marca
  GET    /vehiculos/modelos/{id}        → Obtener detalles
  POST   /vehiculos/modelos             → Crear (ADMIN)
  PUT    /vehiculos/modelos/{id}        → Actualizar (ADMIN)
  DELETE /vehiculos/modelos/{id}        → Eliminar (ADMIN)

VEHÍCULOS:
  GET    /vehiculos                     → Mis vehículos (usuario autenticado)
  GET    /vehiculos/{id}                → Detalles (propiedad validada)
  GET    /vehiculos/{id}/disponibilidad → Verificar estado
  POST   /vehiculos                     → Registrar nuevo (usuario)
  PUT    /vehiculos/{id}                → Actualizar (propietario)
  DELETE /vehiculos/{id}                → Eliminar (propietario)

INCIDENTES:
  POST   /incidentes/reportar           → Crear reporte (usuario)
  GET    /incidentes                    → Mis incidentes (usuario)
  GET    /incidentes/{id}               → Detalles (propiedad validada)

EVIDENCIAS:
  POST   /incidentes/{id}/evidencias    → Agregar multimedia
  GET    /incidentes/{id}/evidencias    → Obtener todas
  DELETE /incidentes/{id}/evidencias/{id} → Eliminar

FILTROS (OPERADORES):
  GET    /incidentes/filtros/por-estado?estado=PENDIENTE
  GET    /incidentes/filtros/por-prioridad?prioridad=CRITICA
  GET    /incidentes/vehiculo/{id}/historial

TRIAJE:
  PATCH  /incidentes/{id}/estado       → Cambiar estado
  PATCH  /incidentes/{id}/prioridad    → Cambiar prioridad
  GET    /incidentes/triaje/calcular-prioridad → Preview

ESTADÍSTICAS:
  GET    /incidentes/stats/resumen      → Dashboard admin


AUTENTICACIÓN Y AUTORIZACIÓN (RBAC)
====================================

Todos los endpoints requieren token JWT válido (Bearer token)

CONTROL DE ACCESO:
  - Usuarios ven solo sus propios vehículos e incidentes
  - Solo propietario puede editar/eliminar su vehículo
  - Admin puede gestionar catálogos (Marcas, Modelos)
  - Operadores pueden ver todos los incidentes y cambiar estados

TOKENS:
  - Obtenido en: POST /auth/login
  - Formato: "Authorization: Bearer {{token}}"
  - Duración: 30 minutos (configurable en config.py)
  - Renovación: Login nuevamente


SISTEMA DE TRIAJE IA (PLACEHOLDER)
===================================

Función: calcular_prioridad_ia(descripcion, lat, long) → dict

LÓGICA ACTUAL (Heurística Simple):
  1. Detecta palabras clave críticas:
     "choque", "volcamiento", "explosión", "incendio"
     → PRIORIDAD CRITICA (5 min respuesta)

  2. Valida ubicación:
     Si está en zona urbana de Bogotá (aprox)
     → PRIORIDAD ALTA (15 min respuesta)

  3. Default:
     → PRIORIDAD MEDIA (30 min respuesta)

PRÓXIMAS ITERACIONES:
  - Integrar ML/IA real (análisis de imagen de evidencias)
  - Análisis de congestión vial
  - Historial de incidentes por zona
  - Disponibilidad de técnicos cercanos


FLUJOS DE NEGOCIO
=================

FLUJO 1: Registro de Vehículo (CU5)
  1. Usuario autenticado → POST /vehiculos
  2. Sistema valida:
     ✓ Placa única
     ✓ Modelo existe
     ✓ Usuario activo
  3. Vehículo creado con estado ACTIVO
  4. Disponible para reportar incidentes

FLUJO 2: Reporte de Incidente (CU8-9)
  1. Usuario autenticado → POST /incidentes/reportar
  2. Datos:
     - id_vehiculo (debe ser del usuario)
     - descripción (10-1000 caracteres)
     - GPS (opcional pero recomendado)
     - evidencias multimedia (fotos, videos)
  
  3. Sistema automáticamente:
     ✓ Calcula prioridad con IA
     ✓ Crea incidente con estado PENDIENTE
     ✓ Registra todas las evidencias
     ✓ Pone en cola para triaje
  
  4. Respuesta:
     {
       id: 123,
       estado: "PENDIENTE",
       prioridad: "CRITICA",
       fecha_reporte: "2024-04-14T...",
       evidencias: [...]
     }

FLUJO 3: Gestión de Operador
  1. Operador ve: GET /incidentes/filtros/por-estado?estado=PENDIENTE
  2. Selecciona incidente → GET /incidentes/{id}
  3. Actualiza triaje:
     PATCH /incidentes/{id}/estado?nuevo_estado=EN_TRIAJE
     PATCH /incidentes/{id}/prioridad?nueva_prioridad=ALTA
  4. Asigna técnico (próximo ciclo)

FLUJO 4: Consulta de Historial
  1. Usuario → GET /incidentes
     Devuelve: Todos sus incidentes en orden DESC
  
  2. Operador → GET /incidentes/vehiculo/{id}/historial
     Devuelve: Todos los incidentes de ese vehículo
  
  3. Admin → GET /incidentes/stats/resumen
     Devuelve: Estadísticas globales


VALIDACIONES Y MANEJO DE ERRORES
==================================

ESTATUS HTTP USADOS:
  200 ✅ GET exitoso
  201 ✅ POST/creación exitosa
  204 ✅ DELETE exitoso
  400 ❌ Validación fallida (placa duplicada, modelo inexistente, etc.)
  401 ❌ No autenticado (falta token)
  403 ❌ No autenticado (no es propietario, no es admin)
  404 ❌ Recurso no encontrado

EJEMPLOS DE VALIDACIÓN:

1. Placa Duplicada:
   POST /vehiculos {placa: "ABC-1234"}
   → 400 Bad Request: "La placa 'ABC-1234' ya está registrada"

2. Vehículo no pertenece al usuario:
   GET /vehiculos/123 (usuario_id=1, vehiculo.id_cliente=2)
   → 403 Forbidden: "No tiene permiso para acceder a este vehículo"

3. Incidente sin evidencias:
   POST /incidentes/reportar {id_vehiculo: 1, ..., evidencias: []}
   → 201 Accepted (incidente sin evidencias también es válido)

4. Tipo de evidencia inválido:
   POST /incidentes/1/evidencias {tipo: "RAYOSX"}
   → 400 Bad Request: "Tipo de evidencia inválido..."

5. Prioridad fuera de rango:
   PATCH /incidentes/1/prioridad?nueva_prioridad=SUPER_URGENTE
   → 400 Bad Request: "Prioridad inválida..."


LAZY LOADING Y RELACIONES
==========================

SQLAlchemy está configurado para lazy loading en todas las relaciones:

vehículo = db.query(Vehiculo).filter(...).first()
print(vehículo.modelo)        # ✅ Carga automáticamente el modelo
print(vehículo.modelo.marca)  # ✅ Carga automáticamente la marca

Ventaja: Código más limpio y sencillo
Desventaja: Múltiples queries (N+1 problem en listas grandes)

⚠️ OPTIMIZACIÓN FUTURA: Usar eager loading para queries de listas:
  from sqlalchemy.orm import joinedload
  vehiculos = db.query(Vehiculo).options(
      joinedload(Vehiculo.modelo).joinedload(Modelo.marca)
  ).filter(Vehiculo.id_cliente == id_cliente).all()


CASOS DE USO CUBIERTOS
======================

CU5: Gestión de Vehículos
  ✅ Crear vehículo (registrar placa)
  ✅ Listar vehículos del usuario
  ✅ Actualizar información
  ✅ Eliminar vehículo
  ✅ Verificar disponibilidad

CU6: Gestión de Marcas (Admin)
  ✅ Listar catálogo de marcas
  ✅ Crear marca nueva
  ✅ Ver modelos por marca
  ✅ Eliminar marca

CU7: Gestión de Modelos (Admin)
  ✅ Crear modelo para marca
  ✅ Listar modelos de marca
  ✅ Actualizar modelo
  ✅ Eliminar modelo

CU8: Reporte de Incidentes
  ✅ Usuario reporta incidente
  ✅ Sistema calcula prioridad automáticamente
  ✅ Incidente entra en cola PENDIENTE
  ✅ Historial de incidentes del usuario

CU9: Captura de Evidencia Multimedia
  ✅ Agregar evidencias en reporte inicial
  ✅ Agregar evidencias posteriores
  ✅ Soporta: FOTO, VIDEO, AUDIO, DOCUMENTO
  ✅ Obtener lista de evidencias
  ✅ Eliminar evidencia


EXTENSIONES FUTURAS (CICLO 2)
==============================

1. Asignación a Técnicos:
   - Tabla: tecnico_asignacion (usuario_id, incidente_id, fecha)
   - Endpoint: POST /incidentes/{id}/asignar-tecnico
   - Estado: EN_ATENCION

2. Actualización de Estado por Cliente:
   - PUT /incidentes/{id} {descripcion_resolucion, fotos_finales}
   - Cambio de estado: EN_ATENCION → RESUELTO

3. Calificación de Servicio:
   - POST /incidentes/{id}/calificar {estrellas, comentario}
   - Tabla: incidente_calificacion

4. Integración con Almacenamiento de Archivos:
   - CloudStorage (AWS S3, Google Cloud, Azure Blob)
   - Generar URLs firmadas (signed URLs)
   - Validar tipo MIME en upload

5. Notificaciones:
   - WebSocket para actualizaciones en tiempo real
   - Email/SMS cuando cambia estado
   - Push notifications mobile

6. Reportes y Analytics:
   - Tiempo promedio de respuesta por prioridad
   - Técnicos con mayor calificación
   - Zonas con mayor incidencia


TESTING
=======

Ejecutar suite de tests:
  python -m pytest test_api.py -v

Archivo de requests HTTP (VS Code REST Client):
  requests.http
  - Ejemplos de cada endpoint
  - Tests de CRUD completo
  - Manejo de errores


STACK TECNOLÓGICO FINAL
=======================

Backend:
  ✅ FastAPI 0.104.1      (Framework web async)
  ✅ SQLAlchemy 2.0.23    (ORM + Query Builder)
  ✅ PostgreSQL           (Base de datos)
  ✅ Pydantic 2.5.0       (Validación de datos)
  ✅ Python-jose 3.3.0    (JWT tokens)
  ✅ Bcrypt 5.0.0         (Hashing de contraseñas)

Frontend (Requerido):
  Angular + TypeScript
  Interceptor para agregar token JWT
  Guards para proteger rutas
  Servicios para cada módulo

Autenticación:
  OAuth2 + Bearer Token (JWT)
  Expiración: 30 minutos
  Refresh: Login nuevamente

Base de Datos:
  PostgreSQL en localhost (config.DATABASE_URL)
  9 tablas normalizadas en 3FN
  Índices en foreign keys y campos de búsqueda


RESUMEN FINAL
=============

La implementación del Ciclo 1 proporciona:

✅ CRUD COMPLETO para vehículos y incidentes
✅ NORMALIZACIÓN 3FN con catálogos maestros
✅ AUTENTICACIÓN Y AUTORIZACIÓN basada en roles
✅ SISTEMA DE TRIAJE IA (placeholder para evolucionar)
✅ GESTIÓN DE EVIDENCIA MULTIMEDIA
✅ LAZY LOADING y relaciones SQLAlchemy
✅ INYECCIÓN DE DEPENDENCIAS en todos los endpoints
✅ MANEJO COMPLETO DE ERRORES con status HTTP apropiados
✅ DOCUMENTACIÓN en código con docstrings y tipos

Próximo paso: Implementar integración Angular, tests adicionales,
y sistema de upload de archivos multimedia.
"""
