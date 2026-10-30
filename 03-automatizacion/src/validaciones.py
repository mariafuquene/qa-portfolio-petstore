def clasificar_edad(edad: int) -> str:
    if edad < 0:
        raise ValueError("La edad no puede ser negativa")
    if edad < 18:
        return "menor"
    if edad < 60:
        return "adulto"
    return "adulto mayor"