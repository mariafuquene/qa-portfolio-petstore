import json
from pathlib import Path

import pytest
import requests


@pytest.fixture
def base_url():
    return "https://petstore.swagger.io/v2"


# ---------------------------------------------------------------------------
# Registro de resultados para la sincronización de la documentación.
#
# Cada prueba de API declara qué casos cubre con @pytest.mark.casos("CP-07").
# Con `pytest --resultados-json=ruta.json` se guarda, por prueba: estado,
# casos cubiertos, códigos HTTP observados y mensaje de error.
# Sin esa opción, pytest se comporta exactamente igual que antes.
# ---------------------------------------------------------------------------

def pytest_addoption(parser):
    parser.addoption(
        "--resultados-json",
        default=None,
        help="Ruta donde guardar los resultados por caso de prueba (JSON).",
    )


@pytest.fixture(autouse=True)
def _registrar_http(request, monkeypatch):
    """Guarda método, URL y código HTTP de cada llamada hecha con requests."""
    llamadas = []
    original = requests.sessions.Session.request

    def request_con_registro(self, method, url, *args, **kwargs):
        respuesta = original(self, method, url, *args, **kwargs)
        llamadas.append({"metodo": method.upper(), "url": respuesta.url,
                         "codigo": respuesta.status_code})
        return respuesta

    monkeypatch.setattr(requests.sessions.Session, "request", request_con_registro)
    request.node._llamadas_http = llamadas
    yield


_resultados = []


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    reporte = outcome.get_result()
    # Se registra la fase "call", o "setup" si la prueba no llegó a ejecutarse.
    if not (reporte.when == "call" or (reporte.when == "setup" and not reporte.passed)):
        return
    casos = []
    for marca in item.iter_markers(name="casos"):
        casos.extend(marca.args)
    if hasattr(reporte, "wasxfail"):
        estado = "xfail" if reporte.skipped else "xpass"
    else:
        estado = reporte.outcome  # passed / failed / skipped
    error = None
    if call.excinfo is not None and estado in ("failed", "xfail"):
        error = call.excinfo.exconly().strip().splitlines()[0][:300]
    xfail = item.get_closest_marker("xfail")
    _resultados.append({
        "prueba": item.nodeid,
        "casos": sorted(set(casos)),
        "estado": estado,
        "motivo_xfail": xfail.kwargs.get("reason") if xfail else None,
        "http": getattr(item, "_llamadas_http", []),
        "error": error,
    })


def pytest_sessionfinish(session):
    ruta = session.config.getoption("--resultados-json")
    if ruta:
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)
        Path(ruta).write_text(json.dumps(_resultados, ensure_ascii=False, indent=2),
                              encoding="utf-8")
