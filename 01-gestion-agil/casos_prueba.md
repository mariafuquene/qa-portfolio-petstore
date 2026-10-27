# Casos de prueba: Petstore QA

**API bajo prueba:** https://petstore.swagger.io/v2
**Técnicas aplicadas:** partición de equivalencia, casos negativos y trazabilidad a criterios de aceptación.

## HU-01: Registrar mascota

| ID    | Criterio | Título                              | Solicitud | Datos de entrada                                 | Resultado esperado                                           | Tipo     |
| ----- | -------- | ----------------------------------- | --------- | ------------------------------------------------ | ------------------------------------------------------------ | -------- |
| CP-01 | CA-01.1  | Registrar mascota válida            | POST /pet | id: 482913577, name: "Luna", status: "available" | Código 200; devuelve la mascota con su id y nombre           | Positivo |
| CP-02 | CA-01.2  | Estado inexistente                  | POST /pet | name: "Luna", status: "perdido"                  | Solicitud rechazada (código 4xx)                             | Negativo |
| CP-03 | CA-01.2  | Estado vacío                        | POST /pet | name: "Luna", status: ""                         | Solicitud rechazada (código 4xx)                             | Negativo |
| CP-04 | CA-01.3  | Sin campo nombre                    | POST /pet | status: "available" (sin name)                   | Solicitud rechazada (código 4xx)                             | Negativo |
| CP-05 | CA-01.3  | Nombre vacío                        | POST /pet | name: "", status: "available"                    | Solicitud rechazada (código 4xx)                             | Negativo |
| CP-15 | CA-01.1  | Registrar mascota en estado sold    | POST /pet | name: "Kira", status: "sold"                     | Código 200; devuelve la mascota con su id y estado "sold"    | Positivo |
| CP-16 | CA-01.1  | Registrar mascota en estado pending | POST /pet | name: "Max", status: "pending"                   | Código 200; devuelve la mascota con su id y estado "pending" | Positivo |

## HU-02: Consultar mascota por id

| ID    | Criterio | Título                       | Solicitud        | Datos de entrada                 | Resultado esperado                                | Tipo     |
| ----- | -------- | ---------------------------- | ---------------- | -------------------------------- | ------------------------------------------------- | -------- |
| CP-06 | CA-02.1  | Consultar id existente       | GET /pet/{petId} | id de la mascota creada en CP-01 | Código 200; devuelve los mismos datos registrados | Positivo |
| CP-07 | CA-02.2  | Id válido que no existe      | GET /pet/{petId} | 9999999999                       | Código 404; mascota no encontrada                 | Negativo |
| CP-08 | CA-02.3  | Id con letras                | GET /pet/{petId} | abc                              | Código 400; solicitud rechazada                   | Negativo |
| CP-09 | CA-02.3  | Id con caracteres especiales | GET /pet/{petId} | @#                               | Código 400; solicitud rechazada                   | Negativo |

## HU-03: Buscar mascotas por estado

| ID    | Criterio | Título                  | Solicitud             | Datos de entrada | Resultado esperado                                            | Tipo     |
| ----- | -------- | ----------------------- | --------------------- | ---------------- | ------------------------------------------------------------- | -------- |
| CP-10 | CA-03.1  | Buscar estado sold      | GET /pet/findByStatus | status=sold      | Código 200; todas las mascotas devueltas tienen estado "sold" | Positivo |
| CP-11 | CA-03.1  | Buscar estado available | GET /pet/findByStatus | status=available | Código 200; todas tienen estado "available"                   | Positivo |
| CP-12 | CA-03.1  | Buscar estado pending   | GET /pet/findByStatus | status=pending   | Código 200; todas tienen estado "pending"                     | Positivo |
| CP-13 | CA-03.2  | Estado inexistente      | GET /pet/findByStatus | status=perdido   | Código 400; solicitud rechazada                               | Negativo |
| CP-14 | CA-03.2  | Estado vacío            | GET /pet/findByStatus | status= (vacío)  | Código 400; solicitud rechazada                               | Negativo |

## Observaciones para el Product Owner

- Los criterios CA-01.2 y CA-01.3 dicen "rechaza la solicitud" sin indicar el código exacto. Por eso el resultado esperado es "código 4xx". Se recomienda definir el código esperado con el PO.
- No está definido qué pasa si el estado se envía en mayúsculas (por ejemplo, "SOLD"). Se recomienda aclararlo antes de probar.
- CA-01.1 solo menciona “available” y hay que confirmar si los otros estados son válidos al registrar.
- No está definido qué debe pasar si en la búsqueda se envían varios estados a la vez, combinando uno válido y uno inválido (por ejemplo, `status=sold&status=perdido`). Se recomienda aclararlo con el PO.
