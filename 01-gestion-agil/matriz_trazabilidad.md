# Matriz de trazabilidad: Petstore QA

Conecta cada requisito con sus pruebas, su resultado y los defectos encontrados. Se lee en ambas direcciones: del requisito al bug y del bug al requisito.

| Historia | Criterio | Casos de prueba     | Resultado | Defecto asociado                 |
| -------- | -------- | ------------------- | --------- | -------------------------------- |
| HU-01    | CA-01.1  | CP-01, CP-15, CP-16 | Pasó      | —                                |
| HU-01    | CA-01.2  | CP-02, CP-03        | Falló     | BUG-03 (PQA-17)                  |
| HU-01    | CA-01.3  | CP-04, CP-05        | Falló     | BUG-04 (PQA-18)                  |
| HU-02    | CA-02.1  | CP-06               | Pasó      | —                                |
| HU-02    | CA-02.2  | CP-07               | Pasó      | —                                |
| HU-02    | CA-02.3  | CP-08, CP-09        | Falló     | BUG-01 (PQA-15), BUG-02 (PQA-16) |
| HU-03    | CA-03.1  | CP-10, CP-11, CP-12 | Pasó      | —                                |
| HU-03    | CA-03.2  | CP-13, CP-14        | Falló     | BUG-05 (PQA-19)                  |

**Cobertura:** 3 historias, 8 criterios de aceptación, 16 casos de prueba. Todos los criterios tienen al menos un caso asociado.

**Resultados:** 16 casos ejecutados: 8 pasaron y 8 fallaron. Se reportaron 5 defectos. Todos los casos positivos pasaron y todos los negativos fallaron: la API cumple sus funciones principales, pero no valida los datos de entrada.
