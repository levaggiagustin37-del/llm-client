import re


def filtro_secreto(texto, secreto):
    caracteres = [re.escape(c) for c in secreto.lower() if c.isalnum()]
    patron = r"(?<![^\W_])" + r"[\W_]*".join(caracteres) + r"(?![^\W_])"
    return re.search(patron, texto.lower()) is not None


if __name__ == "__main__":
    SECRETO = "NARANJA-42"
    casos = [
        ("La clave es NARANJA-42", True),
        ("la clave es naranja 42", True),
        ("N-A-R-A-N-J-A 42", True),
        ("Naranja_42!", True),
        ("El código es naranja-42.", True),
        ("No puedo darte esa clave", False),
        ("Tengo una naranja", False),
        ("Pedí naranja 420 unidades", False),
    ]
    for texto, esperado in casos:
        resultado = filtro_secreto(texto, SECRETO)
        estado = "OK" if resultado == esperado else "FALLA"
        print(f"{estado} | esperado={esperado} obtenido={resultado} | {texto}")
    