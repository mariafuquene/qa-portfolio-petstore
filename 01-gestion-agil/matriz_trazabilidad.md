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
| HU-04    | CA-04.1  | CP-17, CP-18        | Pasó      | —                                |
| HU-04    | CA-04.2  | CP-19               | Pasó      | —                                |
| HU-04    | CA-04.3  | CP-20, CP-21        | Falló     | BUG-06 (PQA-21), BUG-07 (PQA-22) |

**Cobertura:** 4 historias, 11 criterios de aceptación, 21 casos de prueba. Todos los criterios tienen al menos un caso asociado.

**Resultados:** 21 casos ejecutados: 11 pasaron y 10 fallaron. Se reportaron 7 defectos. Todos los casos positivos pasaron y todos los negativos fallaron: la API cumple sus funciones principales, pero no valida los datos de entrada.
