# Reglas de Desarrollo del Sistema de Gestión de Emergencias

1. **Separación Estricta de Responsabilidades (Capas):**
   - NUNCA escribas consultas a la base de datos (SQLAlchemy) dentro de la carpeta `routers/`.
   - NUNCA importes objetos web (como `HTTPException` o `Request`) dentro de la carpeta `crud/` o `models/`.
   - Los archivos en `routers/` SOLO deben recibir la petición, llamar a la función correspondiente en `crud/`, y retornar la respuesta.

2. **Convenciones de Código (FastAPI + SQLAlchemy + Pydantic):**
   - Usa Pydantic (carpeta `schemas/`) estrictamente para la validación de entrada y salida de datos.
   - Usa SQLAlchemy (carpeta `models/`) estrictamente para la definición de tablas y mapeo objeto-relacional.
   - Al responder, genera únicamente el código solicitado para el archivo específico en el que estamos trabajando. No intentes generar el flujo completo (Schema + Model + CRUD + Router) en una sola respuesta.

3. **Manejo de Errores y Bitácora:**
   - Todos los errores lógicos o de base de datos deben registrarse utilizando las herramientas disponibles en `utils/bitacora_helper.py`.
   - Los endpoints deben manejar excepciones atrapando los errores del `crud/` y lanzando `HTTPException` con códigos de estado HTTP precisos (400, 404, 500).

4. **Restricción de Tamaño de Respuesta:**
   - Proporciona respuestas cortas, directas y limitadas al bloque de código que requiere corrección o creación. Omite explicaciones largas a menos que se soliciten explícitamente.