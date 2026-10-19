import glob
import json
import os


def cargar_ataques(carpeta):
    ataques = []
    for ruta in sorted(glob.glob(os.path.join(carpeta, "*.json"))):
        with open(ruta, encoding="utf-8") as archivo:
            datos = json.load(archivo)
        for ataque in datos["ataques"]:
            ataque["categoria"] = datos["categoria"]
            ataques.append(ataque)
    return ataques