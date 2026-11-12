"""Sincronización automática de la documentación QA de Petstore.

Flujo:
  1. Ejecuta las pruebas: pytest (03-automatizacion) y Newman (colección de Postman).
  2. Consolida un resultado por caso de prueba (CP-XX) con código HTTP y error.
  3. Reporta como defectos nuevos los casos fallidos que no tienen BUG asociado
     (reportes_defectos.md).
  4. Regenera la matriz de trazabilidad y sus métricas (matriz_trazabilidad.md).
  5. Opcional: sincroniza historias y bugs con Jira (--jira).
  6. Opcional: hace commit (--commit) y push a main (--push).

Uso rápido (desde la raíz del repositorio):
  python scripts/sincronizar_qa.py --solo-mostrar        # no escribe nada
  python scripts/sincronizar_qa.py                       # actualiza los .md
  python scripts/sincronizar_qa.py --jira --solo-mostrar # muestra el plan en Jira
  python scripts/sincronizar_qa.py --jira --commit --push

Variables de entorno para Jira: JIRA_EMAIL, JIRA_API_TOKEN
(opcionales: JIRA_URL, JIRA_PROYECTO).
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
AGIL = RAIZ / "01-gestion-agil"
API = RAIZ / "02-pruebas-api"
AUTO = RAIZ / "03-automatizacion"

F_HISTORIAS = AGIL / "historias_usuario.md"
F_CASOS = AGIL / "casos_prueba.md"
F_MATRIZ = AGIL / "matriz_trazabilidad.md"
F_DEFECTOS = AGIL / "reportes_defectos.md"
F_COLECCION = API / "petstore.postman_collection.json"
F_ENTORNO = API / "petstore.postman_environment.json"

BASE_URL = "https://petstore.swagger.io/v2"
JIRA_URL = "https://camifuq.atlassian.net"
JIRA_PROYECTO = "PQA"
MENSAJE_COMMIT = ("test: ejecucion automatizada, actualizacion de matriz de "
                  "trazabilidad y reporte de defectos")

INICIO_GEN = "<!-- inicio: generado por scripts/sincronizar_qa.py -->"
FIN_GEN = "<!-- fin: generado por scripts/sincronizar_qa.py -->"

PASO, FALLO, NO_EJEC = "Pasó", "Falló", "No ejecutado"


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def leer(ruta: Path) -> tuple[str, str]:
    """Devuelve (texto con saltos \\n, salto de línea original)."""
    crudo = ruta.read_bytes().decode("utf-8")
    salto = "\r\n" if "\r\n" in crudo else "\n"
    return crudo.replace("\r\n", "\n"), salto


def escribir(ruta: Path, texto: str, salto: str) -> None:
    ruta.write_bytes(texto.replace("\n", salto).encode("utf-8"))


def clave_natural(ident: str) -> tuple:
    return tuple(int(n) for n in re.findall(r"\d+", ident))


def celdas(linea: str) -> list[str]:
    return [c.strip() for c in linea.strip().strip("|").split("|")]


def tabla_md(encabezado: list[str], filas: list[list[str]]) -> str:
    anchos = [max(len(str(f[i])) for f in [encabezado] + filas)
              for i in range(len(encabezado))]
    def linea(valores):
        return "| " + " | ".join(str(v).ljust(a) for v, a in zip(valores, anchos)) + " |"
    sep = "| " + " | ".join("-" * a for a in anchos) + " |"
    return "\n".join([linea(encabezado), sep] + [linea(f) for f in filas])


def pct(n: int, d: int) -> str:
    return f"{(100 * n / d):.1f} %".replace(".0 %", " %").replace(".", ",") if d else "—"


def log(msg: str = "") -> None:
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# Lectura de la documentación
# ---------------------------------------------------------------------------

@dataclass
class Historia:
    id: str
    titulo: str
    criterios: list[str]
    texto: str


@dataclass
class Caso:
    id: str
    historia: str
    criterio: str
    titulo: str
    solicitud: str
    datos: str
    esperado: str
    tipo: str


@dataclass
class Defecto:
    id: str
    titulo: str
    historia: str
    criterio: str
    casos: list[str]
    jira: str | None          # "PQA-15" o None si está pendiente
    texto: str                # bloque markdown completo
    nuevo: bool = False


def leer_historias() -> dict[str, Historia]:
    texto, _ = leer(F_HISTORIAS)
    historias = {}
    bloques = re.split(r"^## ", texto, flags=re.M)[1:]
    for bloque in bloques:
        m = re.match(r"(HU-\d+):?\s*(.*)", bloque)
        if not m:
            continue
        criterios = list(dict.fromkeys(re.findall(r"\*\*(CA-\d+(?:\.\d+)?)", bloque)))
        historias[m.group(1)] = Historia(m.group(1), m.group(2).strip(),
                                         criterios, "## " + bloque.strip())
    return historias


def leer_casos() -> dict[str, Caso]:
    texto, _ = leer(F_CASOS)
    casos, hu = {}, None
    for linea in texto.splitlines():
        m = re.match(r"^## (HU-\d+)", linea)
        if m:
            hu = m.group(1)
            continue
        if re.match(r"^\|\s*CP-\d+", linea):
            c = celdas(linea)
            if len(c) >= 7:
                casos[c[0]] = Caso(c[0], hu, c[1], c[2], c[3], c[4], c[5], c[6])
    return casos


def leer_defectos() -> tuple[str, dict[str, Defecto]]:
    texto, _ = leer(F_DEFECTOS)
    defectos = {}
    partes = re.split(r"^(?=## BUG-\d+)", texto, flags=re.M)
    for parte in partes[1:]:
        m = re.match(r"## (BUG-\d+):\s*(.*)", parte)
        meta = re.search(r"\*\*Historia:\*\*\s*(HU-\d+)", parte)
        crit = re.search(r"\*\*Criterio:\*\*\s*(CA-[\d.]+)", parte)
        casos = re.search(r"\*\*Casos?:\*\*\s*([^·\n]+)", parte)
        jira = re.search(r"\*\*Jira:\*\*\s*(PQA-\d+|[A-Z]+-\d+)", parte)
        defectos[m.group(1)] = Defecto(
            id=m.group(1), titulo=m.group(2).strip(),
            historia=meta.group(1) if meta else "",
            criterio=crit.group(1) if crit else "",
            casos=re.findall(r"CP-\d+", casos.group(1)) if casos else [],
            jira=jira.group(1) if jira else None,
            texto=parte.rstrip(),
        )
    return texto, defectos


def jira_de_historias(defectos: dict[str, Defecto]) -> dict[str, str]:
    """HU-XX -> PQA-YY, a partir de la línea de metadatos de los defectos."""
    texto, _ = leer(F_DEFECTOS)
    return dict(re.findall(r"\*\*Historia:\*\*\s*(HU-\d+)\s*\((\w+-\d+)\)", texto))


# ---------------------------------------------------------------------------
# Ejecución de pruebas
# ---------------------------------------------------------------------------

@dataclass
class Observacion:
    fuente: str               # "pytest" o "Newman"
    resultado: str            # PASO / FALLO
    http: list[int] = field(default_factory=list)
    error: str | None = None
    nota: str | None = None


def ejecutar_pytest(python: str, tmp: Path) -> list[dict] | None:
    salida = tmp / "pytest.json"
    cmd = [python, "-m", "pytest", "-q", "-p", "no:cacheprovider",
           f"--resultados-json={salida}"]
    log(f"> pytest ({AUTO.name})")
    r = subprocess.run(cmd, cwd=AUTO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    resumen = [l for l in r.stdout.splitlines() if l.strip()][-1:] or ["(sin salida)"]
    log(f"  {resumen[0]}")
    if not salida.exists():
        log("  ! pytest no generó resultados. Salida:\n" + r.stdout[-2000:] + r.stderr[-2000:])
        return None
    return json.loads(salida.read_text(encoding="utf-8"))


def comando_newman() -> list[str] | None:
    exe = shutil.which("newman")
    if exe:
        return [exe]
    npx = shutil.which("npx")
    if npx:
        r = subprocess.run([npx, "--no-install", "newman", "--version"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return [npx, "--no-install", "newman"]
    return None


def ejecutar_newman(base_url: str, tmp: Path) -> list[dict] | None:
    cmd = comando_newman()
    if not cmd:
        log("> Newman no está instalado (npm install -g newman); se omite Postman.")
        return None
    salida = tmp / "newman.json"
    log(f"> Newman ({F_COLECCION.name})")
    subprocess.run(cmd + ["run", str(F_COLECCION), "-e", str(F_ENTORNO),
                          "--env-var", f"baseUrl={base_url}",
                          "--reporters", "json", "--reporter-json-export", str(salida)],
                   cwd=API, capture_output=True, text=True)
    if not salida.exists():
        log("  ! Newman no generó resultados.")
        return None
    datos = json.loads(salida.read_text(encoding="utf-8"))
    est = datos["run"]["stats"]["assertions"]
    log(f"  {est['total'] - est['failed']} verificaciones aprobadas, {est['failed']} fallidas")
    return datos["run"]["executions"]


def consolidar(pytest_res, newman_res) -> dict[str, list[Observacion]]:
    obs: dict[str, list[Observacion]] = defaultdict(list)
    for r in pytest_res or []:
        if r["estado"] == "skipped" or not r["casos"]:
            continue
        resultado = PASO if r["estado"] in ("passed", "xpass") else FALLO
        nota = None
        if r["estado"] == "xfail":
            nota = f"fallo conocido: {r['motivo_xfail']}"
        elif r["estado"] == "xpass":
            nota = f"marcada xfail pero pasó: {r['motivo_xfail']} (¿defecto corregido?)"
        for cp in r["casos"]:
            obs[cp].append(Observacion("pytest", resultado,
                                       [h["codigo"] for h in r["http"]], r["error"], nota))
    for e in newman_res or []:
        m = re.search(r"CP-\d+", e["item"]["name"])
        if not m:
            continue
        codigo = (e.get("response") or {}).get("code")
        errores = [f"{a['assertion']}: {a['error']['message']}"
                   for a in e.get("assertions", []) if a.get("error")]
        if codigo is None:
            errores.insert(0, "sin respuesta del servidor")
        obs[m.group(0)].append(Observacion(
            "Newman", FALLO if errores else PASO,
            [codigo] if codigo else [], "; ".join(errores) or None))
    return obs


def resultado_caso(observaciones: list[Observacion]) -> str:
    if not observaciones:
        return NO_EJEC
    return FALLO if any(o.resultado == FALLO for o in observaciones) else PASO


# ---------------------------------------------------------------------------
# Defectos nuevos
# ---------------------------------------------------------------------------

def proponer_defectos(casos, resultados, obs, defectos, hu_jira, base_url, hoy):
    """Crea un BUG por cada grupo (historia, criterio, solicitud) de casos
    fallidos que no tienen ningún defecto asociado."""
    cubiertos = {cp for d in defectos.values() for cp in d.casos}
    sin_bug = [cp for cp, r in resultados.items() if r == FALLO and cp not in cubiertos]
    grupos = defaultdict(list)
    for cp in sorted(sin_bug, key=clave_natural):
        c = casos[cp]
        grupos[(c.historia, c.criterio, c.solicitud)].append(cp)

    siguiente = max((clave_natural(b)[0] for b in defectos), default=0) + 1
    nuevos = []
    for (hu, ca, solicitud), cps in grupos.items():
        bug = f"BUG-{siguiente:02d}"
        siguiente += 1
        metodo, _, ruta = solicitud.partition(" ")
        codigos = sorted({h for cp in cps for o in obs[cp] for h in o.http})
        severidad = "Alta" if any(h >= 500 for h in codigos) else "Media"
        fuentes = sorted({o.fuente for cp in cps for o in obs[cp]})
        titulo = f"{solicitud} no cumple {ca}: {casos[cps[0]].titulo.lower()}"
        pasos = "\n".join(
            f"{i}. Enviar una solicitud {metodo} a `{base_url}{ruta}` con: "
            f"{casos[cp].datos} ({cp})." for i, cp in enumerate(cps, 1))
        obtenido = "; ".join(
            f"{cp}: código {', '.join(map(str, sorted({h for o in obs[cp] for h in o.http}))) or 'sin respuesta'}"
            + (f" — {next((o.error for o in obs[cp] if o.error), '')}" if any(o.error for o in obs[cp]) else "")
            for cp in cps)
        hu_ref = f"{hu} ({hu_jira[hu]})" if hu in hu_jira else hu
        texto = (
            f"## {bug}: {titulo}\n\n"
            f"- **Historia:** {hu_ref} · **Criterio:** {ca} · **Caso:** {', '.join(cps)} · **Jira:** pendiente\n"
            f"- **Ambiente:** {base_url} · **Herramienta:** {' y '.join(fuentes)} (ejecución automatizada) · **Fecha:** {hoy}\n"
            f"- **Severidad:** {severidad} · **Prioridad:** {severidad}\n\n"
            f"**Pasos para reproducir:**\n\n{pasos}\n\n"
            f"**Resultado esperado:** {casos[cps[0]].esperado}, según {ca}.\n\n"
            f"**Resultado obtenido:** {obtenido}\n\n"
            f"**Impacto:** pendiente de análisis. Defecto generado automáticamente a partir "
            f"de la ejecución; revisar título, severidad e impacto."
        )
        d = Defecto(bug, titulo, hu, ca, cps, None, texto, nuevo=True)
        defectos[bug] = d
        nuevos.append(d)
    return nuevos


def texto_defectos(cabecera: str, defectos: dict[str, Defecto]) -> str:
    bloques = [d.texto for d in sorted(defectos.values(), key=lambda d: clave_natural(d.id))]
    return cabecera.rstrip() + "\n\n" + "\n\n".join(bloques) + "\n"


def fijar_jira_en_defecto(d: Defecto, clave: str) -> None:
    d.jira = clave
    d.texto = re.sub(r"(\*\*Jira:\*\*\s*)pendiente", rf"\g<1>{clave}", d.texto, count=1)


# ---------------------------------------------------------------------------
# Matriz de trazabilidad
# ---------------------------------------------------------------------------

def generar_matriz(historias, casos, obs, resultados, defectos, hoy, fuentes):
    texto_ant, salto = leer(F_MATRIZ)

    # Resultados previos por criterio, para filas sin ningún caso ejecutado.
    previo = {}
    for linea in texto_ant.splitlines():
        c = celdas(linea) if linea.startswith("|") else []
        if len(c) >= 4 and re.match(r"CA-", c[1]):
            previo[c[1]] = c[3]

    def ref_bug(d: Defecto) -> str:
        return f"{d.id} ({d.jira or 'Jira pendiente'})"

    bugs_por_caso = defaultdict(list)
    for d in sorted(defectos.values(), key=lambda d: clave_natural(d.id)):
        for cp in d.casos:
            bugs_por_caso[cp].append(d)

    filas_por_ca = defaultdict(list)
    for c in casos.values():
        filas_por_ca[(c.historia, c.criterio)].append(c.id)

    filas = []
    for (hu, ca) in sorted(filas_por_ca, key=lambda k: (clave_natural(k[0]), clave_natural(k[1]))):
        cps = sorted(filas_por_ca[(hu, ca)], key=clave_natural)
        res = [resultados[cp] for cp in cps]
        if FALLO in res:
            r = FALLO
        elif NO_EJEC not in res:
            r = PASO
        elif PASO in res:
            r = previo.get(ca, PASO)       # ejecución parcial sin fallos
        else:
            r = previo.get(ca, NO_EJEC)
        bugs = {d.id: d for cp in cps for d in bugs_por_caso[cp]}
        filas.append([hu, ca, ", ".join(cps), r,
                      ", ".join(ref_bug(d) for d in bugs.values()) or "—"])

    tabla = tabla_md(["Historia", "Criterio", "Casos de prueba", "Resultado", "Defecto asociado"], filas)

    # Detalle por caso
    detalle = []
    for cp in sorted(casos, key=clave_natural):
        c, o = casos[cp], obs.get(cp, [])
        http = ", ".join(str(h) for h in dict.fromkeys(h for x in o for h in x.http)) or "—"
        notas = [x.error for x in o if x.error] + [x.nota for x in o if x.nota]
        nota = (notas[0] if notas else "—").replace("|", "\\|")
        if len(nota) > 110:
            nota = nota[:107] + "..."
        detalle.append([cp, c.historia, c.criterio, c.tipo,
                        ", ".join(dict.fromkeys(x.fuente for x in o)) or "—",
                        http, resultados[cp],
                        ", ".join(d.id for d in bugs_por_caso[cp]) or "—", nota])
    tabla_det = tabla_md(["Caso", "Historia", "Criterio", "Tipo", "Fuente", "HTTP",
                          "Resultado", "Defecto", "Detalle"], detalle)

    # Métricas
    crit_hu = [ca for h in historias.values() for ca in h.criterios]
    crit_casos = {c.criterio for c in casos.values()}
    crit_cubiertos = [ca for ca in crit_hu if ca in crit_casos]
    sin_casos = [ca for ca in crit_hu if ca not in crit_casos]
    sin_definir = sorted(crit_casos - set(crit_hu), key=clave_natural)

    total = len(casos)
    ejecutados = [cp for cp in casos if resultados[cp] != NO_EJEC]
    pasaron = [cp for cp in ejecutados if resultados[cp] == PASO]
    fallaron = [cp for cp in ejecutados if resultados[cp] == FALLO]
    automat = [cp for cp in casos if any(o.fuente == "pytest" for o in obs.get(cp, []))]
    pos = [cp for cp in ejecutados if casos[cp].tipo.lower().startswith("positivo")]
    neg = [cp for cp in ejecutados if casos[cp].tipo.lower().startswith("negativo")]
    pos_ok = [cp for cp in pos if resultados[cp] == PASO]
    neg_ko = [cp for cp in neg if resultados[cp] == FALLO]
    con_jira = [d for d in defectos.values() if d.jira]

    metricas = tabla_md(["Indicador", "Valor"], [
        ["Historias de usuario", str(len(historias))],
        ["Criterios de aceptación con casos", f"{len(crit_cubiertos)} de {len(crit_hu)} ({pct(len(crit_cubiertos), len(crit_hu))})"],
        ["Casos de prueba diseñados", str(total)],
        ["Casos ejecutados", f"{len(ejecutados)} de {total} ({pct(len(ejecutados), total)})"],
        ["Casos aprobados", f"{len(pasaron)} ({pct(len(pasaron), len(ejecutados))} de los ejecutados)"],
        ["Casos fallidos", f"{len(fallaron)} ({pct(len(fallaron), len(ejecutados))} de los ejecutados)"],
        ["Casos automatizados en pytest", f"{len(automat)} de {total} ({pct(len(automat), total)})"],
        ["Casos positivos aprobados", f"{len(pos_ok)} de {len(pos)}"],
        ["Casos negativos fallidos", f"{len(neg_ko)} de {len(neg)}"],
        ["Defectos reportados", f"{len(defectos)} ({len(con_jira)} registrados en Jira)"],
    ])

    if not fallaron:
        conclusion = "Todos los casos ejecutados pasaron."
    elif pos and len(pos_ok) == len(pos) and set(fallaron) <= set(neg):
        conclusion = (f"Todos los casos positivos pasaron y los {len(fallaron)} fallos corresponden a "
                      "casos negativos: la API cumple sus funciones principales, pero no valida "
                      "los datos de entrada.")
    else:
        conclusion = (f"{len(fallaron)} casos fallaron; revisar el detalle por caso y los defectos asociados.")

    avisos = []
    if sin_casos:
        avisos.append(f"- Criterios definidos en `historias_usuario.md` sin casos de prueba: {', '.join(sin_casos)}.")
    if sin_definir:
        avisos.append(f"- Criterios usados en `casos_prueba.md` que no aparecen en `historias_usuario.md`: {', '.join(sin_definir)}.")
    no_ejec = [cp for cp in casos if resultados[cp] == NO_EJEC]
    if no_ejec:
        avisos.append(f"- Casos sin ejecutar en esta corrida: {', '.join(sorted(no_ejec, key=clave_natural))}.")
    for cp in sorted(obs, key=clave_natural):
        for o in obs[cp]:
            if o.nota and "corregido" in o.nota:
                avisos.append(f"- {cp}: {o.nota}.")

    generado = "\n\n".join(filter(None, [
        INICIO_GEN,
        tabla,
        f"**Conclusión:** {conclusion}",
        f"## Métricas\n\nÚltima ejecución: {hoy} · Fuentes: {', '.join(fuentes) or 'ninguna'}\n\n{metricas}",
        ("## Inconsistencias detectadas\n\n" + "\n".join(avisos)) if avisos else None,
        f"## Detalle por caso de prueba\n\n{tabla_det}",
        FIN_GEN,
    ]))

    if INICIO_GEN in texto_ant and FIN_GEN in texto_ant:
        antes = texto_ant.split(INICIO_GEN)[0]
        despues = texto_ant.split(FIN_GEN, 1)[1]
    else:  # primera vez: se conserva el encabezado y la introducción
        lineas = texto_ant.split("\n")
        idx = next((i for i, l in enumerate(lineas) if l.startswith("|")), len(lineas))
        antes, despues = "\n".join(lineas[:idx]), "\n"
    nuevo = antes.rstrip() + "\n\n" + generado + "\n" + despues.lstrip("\n")
    return nuevo, salto, {"crit": (len(crit_cubiertos), len(crit_hu)), "ejecutados": len(ejecutados),
                          "total": total, "pasaron": len(pasaron), "fallaron": len(fallaron),
                          "automat": len(automat), "avisos": avisos}


# ---------------------------------------------------------------------------
# Jira
# ---------------------------------------------------------------------------

def variable_entorno(nombre: str) -> str | None:
    valor = os.environ.get(nombre)
    if valor or os.name != "nt":
        return valor
    try:  # Windows: variable de usuario creada después de abrir la terminal
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            return winreg.QueryValueEx(k, nombre)[0]
    except OSError:
        return None


def adf(texto: str) -> dict:
    """Markdown simple -> Atlassian Document Format (un párrafo por línea)."""
    parrafos = []
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        linea = re.sub(r"\*\*|`", "", linea).lstrip("#").strip()
        parrafos.append({"type": "paragraph", "content": [{"type": "text", "text": linea}]})
    return {"type": "doc", "version": 1, "content": parrafos or [
        {"type": "paragraph", "content": [{"type": "text", "text": "-"}]}]}


class Jira:
    def __init__(self, url: str, proyecto: str, email: str, token: str):
        import requests
        self.url, self.proyecto = url.rstrip("/"), proyecto
        self.s = requests.Session()
        cred = base64.b64encode(f"{email}:{token}".encode()).decode()
        self.s.headers.update({"Authorization": f"Basic {cred}",
                               "Accept": "application/json",
                               "Content-Type": "application/json"})

    def _req(self, metodo, ruta, **kw):
        r = self.s.request(metodo, f"{self.url}/rest/api/3{ruta}", timeout=30, **kw)
        if r.status_code >= 400:
            raise RuntimeError(f"Jira {metodo} {ruta} -> {r.status_code}: {r.text[:300]}")
        return r.json() if r.text else {}

    def incidencias(self) -> list[dict]:
        res, token = [], None
        while True:
            params = {"jql": f"project={self.proyecto} ORDER BY key",
                      "fields": "summary,issuetype,parent,issuelinks", "maxResults": 100}
            if token:
                params["nextPageToken"] = token
            d = self._req("GET", "/search/jql", params=params)
            res += d.get("issues", [])
            token = d.get("nextPageToken")
            if not token:
                return res

    def tipos(self) -> list[str]:
        return [t["name"] for t in self._req("GET", f"/project/{self.proyecto}")["issueTypes"]]

    def crear(self, tipo: str, resumen: str, descripcion: str, padre: str | None = None) -> str:
        campos = {"project": {"key": self.proyecto}, "issuetype": {"name": tipo},
                  "summary": resumen[:250], "description": adf(descripcion)}
        if padre:
            campos["parent"] = {"key": padre}
        return self._req("POST", "/issue", json={"fields": campos})["key"]

    def vincular(self, a: str, b: str, tipo: str = "Relates") -> None:
        self._req("POST", "/issueLink", json={"type": {"name": tipo},
                                               "inwardIssue": {"key": a}, "outwardIssue": {"key": b}})

    def comentar(self, clave: str, texto: str) -> None:
        self._req("POST", f"/issue/{clave}/comment", json={"body": adf(texto)})


def sincronizar_jira(args, historias, defectos, obs, resultados, hu_jira, hoy) -> list[str]:
    email, token = variable_entorno("JIRA_EMAIL"), variable_entorno("JIRA_API_TOKEN")
    if not (email and token):
        log("! Faltan JIRA_EMAIL / JIRA_API_TOKEN; se omite Jira.")
        return []
    url = variable_entorno("JIRA_URL") or JIRA_URL
    proyecto = variable_entorno("JIRA_PROYECTO") or JIRA_PROYECTO
    j = Jira(url, proyecto, email, token)
    simular = args.solo_mostrar
    acciones = []

    def hacer(desc, funcion):
        acciones.append(desc)
        log(f"  {'[simulado] ' if simular else ''}{desc}")
        return None if simular else funcion()

    tipos = j.tipos()
    t_hist = next((t for t in ("Historia", "Story") if t in tipos), None)
    t_bug = next((t for t in ("Error", "Bug") if t in tipos), None)
    issues = j.incidencias()
    por_codigo, links = {}, {}
    padres = Counter()
    for i in issues:
        m = re.match(r"\s*((?:HU|BUG)-\d+)", i["fields"]["summary"])
        if m:
            por_codigo[m.group(1)] = i["key"]
        if i["fields"]["issuetype"]["name"] == t_hist and i["fields"].get("parent"):
            padres[i["fields"]["parent"]["key"]] += 1
        links[i["key"]] = {(l.get("outwardIssue") or l.get("inwardIssue"))["key"]
                           for l in i["fields"].get("issuelinks", [])}
    padre = padres.most_common(1)[0][0] if padres else None
    log(f"> Jira {url} · proyecto {proyecto} · {len(issues)} incidencias")

    # 1. Historias nuevas
    for hu in sorted(historias, key=clave_natural):
        if hu in por_codigo:
            hu_jira.setdefault(hu, por_codigo[hu])
            continue
        h = historias[hu]
        clave = hacer(f"Crear {t_hist} '{hu}: {h.titulo}'",
                      lambda h=h: j.crear(t_hist, f"{h.id}: {h.titulo}", h.texto, padre))
        if clave:
            hu_jira[hu] = clave
            por_codigo[hu] = clave

    # 2. Bugs nuevos o sin clave, y vínculo con su historia
    for d in sorted(defectos.values(), key=lambda d: clave_natural(d.id)):
        clave = d.jira or por_codigo.get(d.id)
        if not clave:
            clave = hacer(f"Crear {t_bug} '{d.id}: {d.titulo}'",
                          lambda d=d: j.crear(t_bug, f"{d.id}: {d.titulo}", d.texto))
        if clave and not d.jira:
            fijar_jira_en_defecto(d, clave)
        hu_clave = hu_jira.get(d.historia)
        if hu_clave and (not clave or hu_clave not in links.get(clave, set())):
            hacer(f"Vincular {clave or d.id} 'relates to' {hu_clave}",
                  lambda c=clave, h=hu_clave: j.vincular(c, h))

    # 3. Evidencia de la corrida en bugs con casos fallidos (opcional)
    if args.comentar_jira:
        for d in defectos.values():
            fallidos = [cp for cp in d.casos if resultados.get(cp) == FALLO]
            if d.jira and fallidos and not d.nuevo:
                det = "\n".join(
                    f"{cp} ({o.fuente}): HTTP {', '.join(map(str, o.http)) or '-'}"
                    + (f" - {o.error}" if o.error else "") for cp in fallidos for o in obs[cp])
                hacer(f"Comentar en {d.jira} ({', '.join(fallidos)} siguen fallando)",
                      lambda d=d, det=det: j.comentar(
                          d.jira, f"Ejecución automatizada {hoy}: el defecto se sigue reproduciendo.\n{det}"))

    if not acciones:
        log("  Jira ya está sincronizado; no hay cambios.")
    return acciones


# ---------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------

def git(*args, check=True) -> str:
    r = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout.strip()


def commit_y_push(archivos: list[Path], push: bool) -> None:
    rutas = [str(p.relative_to(RAIZ)) for p in archivos]
    git("add", "--", *rutas)
    if not git("diff", "--cached", "--name-only", "--", *rutas):
        log("> Git: no hay cambios en la documentación; no se hace commit.")
        return
    git("commit", "-m", MENSAJE_COMMIT, "--", *rutas)
    log(f"> Git: commit {git('rev-parse', '--short', 'HEAD')} — {MENSAJE_COMMIT}")
    if push:
        rama = git("rev-parse", "--abbrev-ref", "HEAD")
        if rama != "main":
            log(f"! Rama actual '{rama}': solo se hace push desde main. Se omite.")
            return
        git("push", "origin", "main")
        log("> Git: push a origin/main realizado.")


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--solo-mostrar", action="store_true",
                   help="ejecuta las pruebas y muestra los cambios sin escribir nada (ni archivos ni Jira)")
    p.add_argument("--sin-pytest", action="store_true", help="no ejecutar pytest")
    p.add_argument("--sin-newman", action="store_true", help="no ejecutar la colección de Postman")
    p.add_argument("--python", default=sys.executable, help="intérprete con pytest instalado")
    p.add_argument("--base-url", default=BASE_URL)
    p.add_argument("--jira", action="store_true", help="sincronizar historias y bugs con Jira")
    p.add_argument("--comentar-jira", action="store_true",
                   help="con --jira: comentar en cada bug cuyos casos siguen fallando")
    p.add_argument("--commit", action="store_true", help="hacer commit de la documentación")
    p.add_argument("--push", action="store_true", help="con --commit: hacer push a origin/main")
    args = p.parse_args()
    hoy = dt.date.today().isoformat()

    historias, casos = leer_historias(), leer_casos()
    cabecera_def, defectos = leer_defectos()
    cabecera_def = re.split(r"^## BUG-", cabecera_def, flags=re.M)[0]
    hu_jira = jira_de_historias(defectos)
    log(f"Documentación: {len(historias)} historias, {len(casos)} casos, {len(defectos)} defectos")

    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        res_pytest = None if args.sin_pytest else ejecutar_pytest(args.python, tmp)
        res_newman = None if args.sin_newman else ejecutar_newman(args.base_url, tmp)
    fuentes = [n for n, r in (("pytest", res_pytest), ("Newman (Postman)", res_newman)) if r]
    if not fuentes:
        log("! No se pudo ejecutar ninguna suite. No se actualiza nada.")
        return 2

    obs = consolidar(res_pytest, res_newman)
    desconocidos = sorted(set(obs) - set(casos), key=clave_natural)
    if desconocidos:
        log(f"! Casos ejecutados que no existen en casos_prueba.md: {', '.join(desconocidos)}")
    resultados = {cp: resultado_caso(obs.get(cp, [])) for cp in casos}

    log("\nResultado por caso:")
    for cp in sorted(casos, key=clave_natural):
        http = ",".join(str(h) for o in obs.get(cp, []) for h in o.http) or "-"
        log(f"  {cp:6} {resultados[cp]:13} HTTP {http:12} {', '.join(o.fuente for o in obs.get(cp, []))}")

    nuevos = proponer_defectos(casos, resultados, obs, defectos, hu_jira, args.base_url, hoy)
    log(f"\nDefectos nuevos: {', '.join(d.id + ' (' + ', '.join(d.casos) + ')' for d in nuevos) or 'ninguno'}")

    if args.jira:
        try:
            sincronizar_jira(args, historias, defectos, obs, resultados, hu_jira, hoy)
        except Exception as e:  # noqa: BLE001 - se informa y se continúa con los archivos
            log(f"! Error al sincronizar con Jira: {e}")

    texto_def = texto_defectos(cabecera_def, defectos)
    matriz, salto_m, m = generar_matriz(historias, casos, obs, resultados, defectos, hoy, fuentes)

    log(f"\nCobertura de criterios: {m['crit'][0]}/{m['crit'][1]} · ejecutados {m['ejecutados']}/{m['total']}"
        f" · pasaron {m['pasaron']} · fallaron {m['fallaron']} · automatizados en pytest {m['automat']}")
    for a in m["avisos"]:
        log("  " + a)

    texto_def_ant, salto_d = leer(F_DEFECTOS)
    cambios = []
    if texto_def != texto_def_ant:
        cambios.append(F_DEFECTOS)
    if matriz != leer(F_MATRIZ)[0]:
        cambios.append(F_MATRIZ)

    if args.solo_mostrar:
        log(f"\n[solo mostrar] Archivos que cambiarían: {', '.join(c.name for c in cambios) or 'ninguno'}")
        return 0
    if F_DEFECTOS in cambios:
        escribir(F_DEFECTOS, texto_def, salto_d)
    if F_MATRIZ in cambios:
        escribir(F_MATRIZ, matriz, salto_m)
    log(f"\nArchivos actualizados: {', '.join(c.name for c in cambios) or 'ninguno'}")

    if args.commit:
        commit_y_push([F_MATRIZ, F_DEFECTOS], args.push)
    return 0


if __name__ == "__main__":
    sys.exit(main())
