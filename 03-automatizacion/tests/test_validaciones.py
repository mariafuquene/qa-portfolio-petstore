import pytest
from src.validaciones import clasificar_edad


@pytest.mark.parametrize("edad, esperado", [
    (0, "menor"),
    (17, "menor"),
    (18, "adulto"),
    (59, "adulto"),
    (60, "adulto mayor"),
])
def test_clasificar_edad_valores_limite(edad, esperado):
    assert clasificar_edad(edad) == esperado


def test_edad_negativa_lanza_error():
    with pytest.raises(ValueError):
        clasificar_edad(-1)