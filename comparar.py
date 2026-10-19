import glob
import json
import os

from llmsec.estadistica import intervalo_wilson


def nombre_modelo(archivo):
    base = os.path.splitext(os.path.basename(archivo))[0]
    return base[len("resultados_"):]


def leer(archivo):
    with open(archivo, encoding="utf-8") as f:
        if archivo.endswith(".jsonl"):
            return [json.loads(linea) for linea in f if linea.strip()]
        return json.load(f)


def cargar():
    modelos = {}
    archivos = sorted(glob.glob("resultados_*.json") + glob.glob("resultados_*.jsonl"))
    for archivo in archivos:
        modelos.setdefault(nombre_modelo(archivo), []).extend(leer(archivo))
    return modelos


def tasa(registros):
    total = len(registros)
    exitos = sum(1 for r in registros if r["funciono"])
    bajo, alto = intervalo_wilson(exitos, total)
    return exitos, total, bajo, alto


modelos = cargar()
ataques = []
for registros in modelos.values():
    for r in registros:
        if r["ataque"] not in ataques:
            ataques.append(r["ataque"])

for ataque in ataques:
    print(f"\n{ataque}")
    for nombre, registros in modelos.items():
        propios = [r for r in registros if r["ataque"] == ataque]
        if not propios:
            continue
        exitos, total, bajo, alto = tasa(propios)
        print(f"  {nombre:<16} {exitos:>5}/{total:<5} {exitos / total:>6.1%} (IC 95%: {bajo:.1%}-{alto:.1%})")

print("\n--- Total por modelo ---")
for nombre, registros in modelos.items():
    if not registros:
        continue
    exitos, total, bajo, alto = tasa(registros)
    errores = sum(1 for r in registros if r["respuesta"].startswith("ERROR"))
    solo_pensando = sum(1 for r in registros if r.get("filtro_en_pensamiento") and not r["funciono"])
    print(
        f"{nombre:<16} filtró {exitos}/{total} ({exitos / total:.1%}, IC 95%: {bajo:.1%}-{alto:.1%})"
        f" | errores: {errores} | clave solo en el pensamiento: {solo_pensando}"
    )