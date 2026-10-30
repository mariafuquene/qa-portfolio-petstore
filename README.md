# qa-portfolio-petstore

Portafolio de práctica QA: historias de usuario, pruebas de API y automatización con Python sobre Swagger Petstore

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

## Herramientas

Jira (Scrum) · Swagger · Postman · Python · pytest · Git · GitHub · VS Code

## Aprendizajes y siguientes pasos

- Una prueba en verde no siempre es correcta: el resultado esperado debe salir del criterio de aceptación, no del comportamiento actual del sistema.
- Antes de reportar un fallo, verifico si el error está en el sistema, en el código de la prueba o en los datos enviados.
- **Siguientes pasos:** practicar SQL para validar datos en base de datos y aprender pruebas de interfaz con Selenium o Playwright.
