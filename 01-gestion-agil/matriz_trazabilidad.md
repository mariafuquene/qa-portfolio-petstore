# Matriz de trazabilidad: Petstore QA

Conecta cada requisito con sus pruebas, su resultado y los defectos encontrados. Se lee en ambas direcciones: del requisito al bug y del bug al requisito.

<!-- inicio: generado por scripts/sincronizar_qa.py -->

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

**Conclusión:** Todos los casos positivos pasaron y los 10 fallos corresponden a casos negativos: la API cumple sus funciones principales, pero no valida los datos de entrada.

## Métricas

Última ejecución: 2026-11-12 · Fuentes: pytest, Newman (Postman)

| Indicador                         | Valor                         |
| --------------------------------- | ----------------------------- |
| Historias de usuario              | 4                             |
| Criterios de aceptación con casos | 11 de 11 (100 %)              |
| Casos de prueba diseñados         | 21                            |
| Casos ejecutados                  | 21 de 21 (100 %)              |
| Casos aprobados                   | 11 (52,4 % de los ejecutados) |
| Casos fallidos                    | 10 (47,6 % de los ejecutados) |
| Casos automatizados en pytest     | 7 de 21 (33,3 %)              |
| Casos positivos aprobados         | 10 de 10                      |
| Casos negativos fallidos          | 10 de 11                      |
| Defectos reportados               | 7 (7 registrados en Jira)     |

## Detalle por caso de prueba

| Caso  | Historia | Criterio | Tipo     | Fuente         | HTTP | Resultado | Defecto        | Detalle                                                                                                        |
| ----- | -------- | -------- | -------- | -------------- | ---- | --------- | -------------- | -------------------------------------------------------------------------------------------------------------- |
| CP-01 | HU-01    | CA-01.1  | Positivo | pytest, Newman | 200  | Pasó      | —              | —                                                                                                              |
| CP-02 | HU-01    | CA-01.2  | Negativo | Newman         | 200  | Falló     | BUG-03         | CP-02: un estado inexistente se rechaza (4xx): expected 200 to be within 400..499                              |
| CP-03 | HU-01    | CA-01.2  | Negativo | Newman         | 200  | Falló     | BUG-03         | CP-03: un estado vacio se rechaza (4xx): expected 200 to be within 400..499                                    |
| CP-04 | HU-01    | CA-01.3  | Negativo | Newman         | 200  | Falló     | BUG-04         | CP-04: registrar sin nombre se rechaza (4xx): expected 200 to be within 400..499                               |
| CP-05 | HU-01    | CA-01.3  | Negativo | Newman         | 200  | Falló     | BUG-04         | CP-05: registrar con nombre vacio se rechaza (4xx): expected 200 to be within 400..499                         |
| CP-06 | HU-02    | CA-02.1  | Positivo | pytest, Newman | 200  | Pasó      | —              | —                                                                                                              |
| CP-07 | HU-02    | CA-02.2  | Negativo | pytest, Newman | 404  | Pasó      | —              | —                                                                                                              |
| CP-08 | HU-02    | CA-02.3  | Negativo | pytest, Newman | 404  | Falló     | BUG-01, BUG-02 | AssertionError: assert 404 == 400                                                                              |
| CP-09 | HU-02    | CA-02.3  | Negativo | Newman         | 404  | Falló     | BUG-01, BUG-02 | CP-09: un id con caracteres especiales responde 400: expected response to have status code 400 but got 404;... |
| CP-10 | HU-03    | CA-03.1  | Positivo | pytest, Newman | 200  | Pasó      | —              | —                                                                                                              |
| CP-11 | HU-03    | CA-03.1  | Positivo | pytest, Newman | 200  | Pasó      | —              | —                                                                                                              |
| CP-12 | HU-03    | CA-03.1  | Positivo | pytest, Newman | 200  | Pasó      | —              | —                                                                                                              |
| CP-13 | HU-03    | CA-03.2  | Negativo | Newman         | 200  | Falló     | BUG-05         | CP-13: un estado inexistente se rechaza con 400: expected response to have status code 400 but got 200         |
| CP-14 | HU-03    | CA-03.2  | Negativo | Newman         | 200  | Falló     | BUG-05         | CP-14: un estado vacio se rechaza con 400: expected response to have status code 400 but got 200               |
| CP-15 | HU-01    | CA-01.1  | Positivo | Newman         | 200  | Pasó      | —              | —                                                                                                              |
| CP-16 | HU-01    | CA-01.1  | Positivo | Newman         | 200  | Pasó      | —              | —                                                                                                              |
| CP-17 | HU-04    | CA-04.1  | Positivo | Newman         | 200  | Pasó      | —              | —                                                                                                              |
| CP-18 | HU-04    | CA-04.1  | Positivo | Newman         | 200  | Pasó      | —              | —                                                                                                              |
| CP-19 | HU-04    | CA-04.2  | Positivo | Newman         | 200  | Pasó      | —              | —                                                                                                              |
| CP-20 | HU-04    | CA-04.3  | Negativo | Newman         | 500  | Falló     | BUG-06         | CP-20: rechaza el id con letras (400 o 405): expected 500 to be one of [ 400, 405 ]                            |
| CP-21 | HU-04    | CA-04.3  | Negativo | Newman         | 415  | Falló     | BUG-07         | CP-21: rechaza el cuerpo vacío (400 o 405): expected 415 to be one of [ 400, 405 ]                             |

<!-- fin: generado por scripts/sincronizar_qa.py -->
