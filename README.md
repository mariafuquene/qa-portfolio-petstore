# QA Portfolio: Petstore API

Portafolio de práctica de QA y Scrum sobre la API pública [Swagger Petstore](https://petstore.swagger.io). Cubre el ciclo completo: historias de usuario, diseño de casos de prueba, ejecución de pruebas de API, reporte de defectos y automatización.

## Resultados

| Indicador                       | Resultado                                                        |
| ------------------------------- | ---------------------------------------------------------------- |
| Historias de usuario            | 3, con criterios de aceptación en formato Gherkin                |
| Casos de prueba diseñados       | 16 (partición de equivalencia, valores límite y casos negativos) |
| Pruebas de API en Postman       | 16 casos, 26 verificaciones automáticas                          |
| Pruebas automatizadas en Python | 12 (pytest)                                                      |
| Defectos reportados             | 5, uno de ellos de seguridad, gestionados en Jira                |

**Conclusión:** la API cumple sus funciones principales, pero no valida los datos de entrada: acepta estados y nombres inválidos, responde con códigos incorrectos y expone mensajes de error internos.

## Contenido

| Carpeta                                  | Qué contiene                                                                                                             |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| [`01-gestion-agil`](01-gestion-agil)     | Historias de usuario, casos de prueba, matriz de trazabilidad, reportes de defectos y capturas del tablero Scrum en Jira |
| [`02-pruebas-api`](02-pruebas-api)       | Colección y environment de Postman, informe de ejecución y evidencia del Collection Runner                               |
| [`03-automatizacion`](03-automatizacion) | Pruebas automatizadas en Python con pytest y requests                                                                    |

## Cómo ejecutar las pruebas automatizadas

```bash
cd 03-automatizacion
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest -v
```

Resultado esperado: `11 passed, 1 xfailed`. La prueba marcada como `xfail` corresponde a un defecto conocido (BUG-01) que permanece abierto.

## Sincronización automática de la documentación

[`scripts/sincronizar_qa.py`](scripts/sincronizar_qa.py) ejecuta pytest y la colección de Postman (con Newman), consolida un resultado por caso de prueba y actualiza la documentación:

- **Matriz de trazabilidad:** resultado por criterio, defectos asociados, métricas de cobertura y detalle por caso con el código HTTP observado.
- **Reportes de defectos:** si un caso falla y no tiene un BUG asociado, agrega un `BUG-XX` nuevo con severidad, endpoint, resultado esperado y obtenido.
- **Jira (opcional):** crea en el proyecto `PQA` las historias y los bugs que aún no existen, y vincula cada bug con su historia.

Requisitos: las dependencias de `03-automatizacion/requirements.txt` y, para Postman, Newman (`npm install -g newman`). Para Jira, las variables de entorno `JIRA_EMAIL` y `JIRA_API_TOKEN`.

```bash
python scripts/sincronizar_qa.py --solo-mostrar          # ejecuta y muestra los cambios, sin escribir nada
python scripts/sincronizar_qa.py                         # actualiza los archivos .md
python scripts/sincronizar_qa.py --jira --solo-mostrar   # muestra qué crearía o vincularía en Jira
python scripts/sincronizar_qa.py --jira --commit --push  # todo el flujo, con commit y push a main
```

Cada prueba de pytest declara los casos que cubre con `@pytest.mark.casos("CP-XX")`. La relación entre bugs y casos sale del campo **Caso** de cada defecto en `reportes_defectos.md`.

## Herramientas

Jira (Scrum) · Swagger · Postman · Python · pytest · Git · GitHub · VS Code

## Aprendizajes y siguientes pasos

- Una prueba en verde no siempre es correcta: el resultado esperado debe salir del criterio de aceptación, no del comportamiento actual del sistema.
- Antes de reportar un fallo, verifico si el error está en el sistema, en el código de la prueba o en los datos enviados.
- **Siguientes pasos:** practicar SQL para validar datos en base de datos y aprender pruebas de interfaz con Selenium o Playwright.
