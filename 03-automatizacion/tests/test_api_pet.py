import pytest
import requests


@pytest.mark.casos("CP-07")
def test_cp07_id_inexistente_responde_404(base_url):
    r = requests.get(f"{base_url}/pet/9999999999", timeout=10)
    assert r.status_code == 404
    assert r.json()["message"] == "Pet not found"


@pytest.mark.casos("CP-01", "CP-06")
def test_cp01_cp06_registrar_y_consultar_mascota(base_url):
    mascota = {"id": 482913590, "name": "Luna", "status": "available"}

    creada = requests.post(f"{base_url}/pet", json=mascota, timeout=10)
    assert creada.status_code == 200

    consultada = requests.get(f"{base_url}/pet/{mascota['id']}", timeout=10)
    assert consultada.status_code == 200
    assert consultada.json()["name"] == "Luna"


@pytest.mark.parametrize("estado", [
    pytest.param("sold", marks=pytest.mark.casos("CP-10")),
    pytest.param("available", marks=pytest.mark.casos("CP-11")),
    pytest.param("pending", marks=pytest.mark.casos("CP-12")),
])
def test_cp10_cp12_buscar_por_estado(base_url, estado):
    r = requests.get(f"{base_url}/pet/findByStatus",
                     params={"status": estado}, timeout=10)
    assert r.status_code == 200
    for mascota in r.json():
        assert mascota["status"] == estado


@pytest.mark.casos("CP-08")
@pytest.mark.xfail(reason="BUG-01 (PQA-15): responde 404 en lugar de 400")
def test_cp08_id_con_letras_responde_400(base_url):
    r = requests.get(f"{base_url}/pet/abc", timeout=10)
    assert r.status_code == 400