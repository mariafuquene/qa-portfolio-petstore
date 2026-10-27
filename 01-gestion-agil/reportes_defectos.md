# Reportes de defectos: Petstore QA

## BUG-01: GET /pet/{petId} responde 404 en lugar de 400 cuando el id no es numérico

- **Historia:** HU-02 (PQA-4) · **Criterio:** CA-02.3 · **Caso:** CP-08 · **Jira:** PQA-15
- **Ambiente:** https://petstore.swagger.io/v2 · **Herramienta:** Postman · **Fecha:** 2026-10-26
- **Severidad:** Media · **Prioridad:** Media

**Pasos para reproducir:**

1. Enviar una solicitud GET a `https://petstore.swagger.io/v2/pet/abc`
2. El mismo comportamiento se reproduce con `@#` (codificado como `%40%23`), caso CP-09.

**Resultado esperado:** código 400 "Invalid ID supplied", según CA-02.3 y la documentación de Swagger.

**Resultado obtenido:** código 404 Not Found.

**Impacto:** quien consume la API no puede distinguir un id mal formado de una mascota inexistente.

**Nota:** Swagger UI bloquea este valor desde el navegador, por lo que el defecto solo se observa enviando la solicitud directamente a la API.

## BUG-02: GET /pet/{petId} expone un error interno de Java cuando el id no es numérico

- **Historia:** HU-02 (PQA-4) · **Criterio:** CA-02.3 · **Caso:** CP-08 · **Jira:** PQA-16
- **Ambiente:** https://petstore.swagger.io/v2 · **Herramienta:** Postman · **Fecha:** 2026-10-26
- **Severidad:** Media · **Prioridad:** Alta

**Pasos para reproducir:**

1. Enviar una solicitud GET a `https://petstore.swagger.io/v2/pet/abc`
2. El mismo comportamiento se reproduce con `@#` (codificado como `%40%23`), caso CP-09.

**Resultado esperado:** un mensaje de error genérico, sin detalles técnicos internos.

**Resultado obtenido:** el campo "message" contiene "java.lang.NumberFormatException: For input string: \"abc\""

**Impacto:** no expone datos de usuarios, pero revela la tecnología del servidor y detalles de su funcionamiento interno, lo que puede facilitar ataques dirigidos.

**Nota:** Este defecto debe reportarse como debilidad de seguridad.

## BUG-03: POST /pet acepta y guarda una mascota con un estado inválido o vacío

- **Historia:** HU-01 (PQA-3) · **Criterio:** CA-01.2 · **Caso:** CP-02, CP-03 · **Jira:** PQA-17
- **Ambiente:** https://petstore.swagger.io/v2 · **Herramienta:** Postman · **Fecha:** 2026-10-26
- **Severidad:** Media · **Prioridad:** Alta

**Pasos para reproducir:**

1. Enviar una solicitud POST a `https://petstore.swagger.io/v2/pet` con el Body `{"id": 482913578, "name": "Luna", "status": "perdido"}` (CP-02).
2. Repetir con `"status": ""` (CP-03).

**Resultado esperado:** la solicitud se rechaza con un código 4xx y la mascota no se guarda, según CA-01.2.

**Resultado obtenido:** código 200 OK; la API guarda la mascota con `"status": "perdido"` y con `"status": ""`.

**Impacto:** problema de integridad de datos. Las mascotas guardadas con un estado inválido no aparecen en ninguna búsqueda por estado válido (available, pending, sold). Además, la búsqueda con estado vacío (CP-14) devuelve mascotas guardadas por este defecto.

## BUG-04: POST /pet acepta y guarda una mascota sin nombre o con nombre vacío

- **Historia:** HU-01 (PQA-3) · **Criterio:** CA-01.3 · **Caso:** CP-04, CP-05 · **Jira:** PQA-18
- **Ambiente:** https://petstore.swagger.io/v2 · **Herramienta:** Postman · **Fecha:** 2026-10-26
- **Severidad:** Media · **Prioridad:** Media

**Pasos para reproducir:**

1. Enviar una solicitud POST a `https://petstore.swagger.io/v2/pet` con el Body `{"id": 482913580, "status": "available"}`, sin el campo `name` (CP-04).
2. Repetir con `"name": ""` (CP-05).

**Resultado esperado:** la solicitud se rechaza con un código 4xx y la mascota no se guarda, según CA-01.3.

**Resultado obtenido:** código 200 OK; la API guarda la mascota sin el campo `name` y con `"name": ""`.

**Impacto:** problema de integridad de datos. Se pueden registrar mascotas que los empleados no pueden identificar en el catálogo.

## BUG-05: GET /pet/findByStatus no rechaza un estado inválido o vacío

- **Historia:** HU-03 (PQA-5) · **Criterio:** CA-03.2 · **Caso:** CP-13, CP-14 · **Jira:** PQA-19
- **Ambiente:** https://petstore.swagger.io/v2 · **Herramienta:** Postman · **Fecha:** 2026-10-27
- **Severidad:** Media · **Prioridad:** Media

**Pasos para reproducir:**

1. Enviar una solicitud GET a `https://petstore.swagger.io/v2/pet/findByStatus?status=perdido` (CP-13).
2. Repetir con el estado vacío: `https://petstore.swagger.io/v2/pet/findByStatus?status=` (CP-14).

**Resultado esperado:** código 400; la solicitud se rechaza, según CA-03.2.

**Resultado obtenido:** código 200 OK en ambos casos. Con `perdido` devuelve una lista vacía `[]`; con el estado vacío devuelve mascotas guardadas con estado vacío.

**Impacto:** quien consume la API no puede distinguir "no hay mascotas en ese estado" de "ese estado no existe". El caso CP-14 además confirma el efecto de BUG-03: las mascotas guardadas con estado vacío existen en la base de datos.
