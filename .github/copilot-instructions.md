# Instrucciones Globales para GitHub Copilot (Backend)

Eres un desarrollador experto en Python y FastAPI, asistiendo en la construcción del backend para una Plataforma Inteligente de Atención de Emergencias Vehiculares. El proyecto se gestiona bajo la metodología SCRUM y requiere una trazabilidad documental estricta basada en PUDS (Proceso Unificado de Desarrollo de Sistemas).

Al generar código, autocompletar o refactorizar en este repositorio, debes adherirte ESTRICTAMENTE a las siguientes reglas:

## 1. Trazabilidad y Metodología (PUDS)
* **Casos de Uso:** Relaciona siempre el código con los artefactos de PUDS. Al documentar endpoints en `routers/` o funciones en `crud/`, utiliza Docstrings de Python que incluyan la referencia al Caso de Uso (Ejemplo: `""" Implementa la lógica de persistencia para el [CU-08] Registrar Incidente """`).
* **Nomenclatura de Dominio:** Los nombres de las funciones deben reflejar las acciones de negocio documentadas (ej. `asignar_auxilio()` en lugar de `update_status()`).

## 2. Arquitectura Multicapa en FastAPI
Debes respetar estrictamente la separación de responsabilidades de las siguientes capas. Nunca mezcles la lógica de una capa en otra:
* **`models/` (Capa de Datos):** Exclusivo para modelos de SQLAlchemy. Aquí se definen las tablas de la base de datos y sus relaciones.
* **`schemas/` (Capa de Transferencia/DTO):** Exclusivo para modelos de Pydantic. Define aquí la validación de entrada (Ej. `IncidenteCreate`) y serialización de salida (Ej. `IncidenteResponse`).
* **`crud/` (Capa de Lógica de Negocio):** Toda la lógica de interacción con la base de datos va aquí. Las funciones deben recibir la sesión de la DB y los datos validados del schema.
* **`routers/` (Capa de Presentación de API):** Los controladores (endpoints). Solo deben inyectar dependencias (como la sesión de BD o el usuario actual), llamar a la función correspondiente en `crud/` y retornar el esquema Pydantic. No debe haber lógica compleja de base de datos aquí.

## 3. Calidad de Código y Python Moderno
* **Type Hinting Estricto:** Utiliza anotaciones de tipo (Type Hints) en TODAS las variables, parámetros de funciones y retornos (`def crear_incidente(db: Session, incidente: schemas.IncidenteCreate) -> models.Incidente:`).
* **Inyección de Dependencias:** Utiliza el sistema de dependencias de FastAPI (`Depends`) para inyectar la sesión de la base de datos (`get_db`) y las validaciones de seguridad (tokens JWT).
* **Manejo de Errores:** En la capa `routers/`, si una operación de negocio falla (ej. intentar asignar un técnico que no está disponible), levanta excepciones HTTP claras (`HTTPException(status_code=400, detail="...")`) en lugar de retornar errores genéricos.
* **Documentación de Funciones:** Agrega docstrings concisos en todos los endpoints en `routers/` y funciones en `crud/` que incluyan la referencia al Caso de Uso (Ej: `""" [CU-08] Registrar Incidente - Crear nuevo incidente en el sistema """`).
* **Optimización de Código:** Cuando se te pida generar código a partir de un "esqueleto" (stub) completo con firma de función, autocompleta solo el interior de las funciones. No reescribas la firma ni el archivo completo a menos que se te solicite explícitamente.