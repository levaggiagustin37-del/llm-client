import json


def cargar_escenario(ruta):
    with open(ruta, encoding="utf-8") as archivo:
        datos = json.load(archivo)
    datos["reglas"] = datos["reglas"].replace("{secreto}", datos["secreto"])
    return datos