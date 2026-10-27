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
