# Informe de pruebas de API: Petstore QA

**API bajo prueba:** https://petstore.swagger.io/v2 · **Herramienta:** Postman (Collection Runner) · **Fecha:** 2026-10-27

## Resumen

| Indicador                         | Resultado                                    |
| --------------------------------- | -------------------------------------------- |
| Casos de prueba ejecutados        | 16                                           |
| Verificaciones automáticas        | 26 (16 aprobadas, 10 fallidas)               |
| Casos aprobados                   | 8                                            |
| Casos fallidos                    | 8                                            |
| Defectos reportados               | 5 (BUG-01 a BUG-05, en Jira PQA-15 a PQA-19) |
| Duración de la ejecución completa | 5 segundos                                   |

## Conclusión

Todos los casos positivos pasaron y todos los negativos fallaron. La API cumple sus funciones principales (registrar, consultar y buscar mascotas), pero no valida los datos de entrada: acepta estados inválidos, nombres vacíos e identificadores con formato incorrecto, y expone mensajes de error internos.

## Cómo ejecutar las pruebas

1. Importar `petstore.postman_collection.json` y `petstore.postman_environment.json` en Postman.
2. Activar el environment **Petstore**.
3. Ejecutar la colección **Petstore QA** con el Collection Runner. CP-01 debe ejecutarse antes que CP-06, porque guarda el `petId` que CP-06 utiliza.

## Evidencia

- Resultados del Runner: `capturas/runner_resultados.png`
- Detalle de los defectos: `../01-gestion-agil/reportes_defectos.md`
- Trazabilidad completa: `../01-gestion-agil/matriz_trazabilidad.md`
