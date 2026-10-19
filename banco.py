import json
import os
import sys
import time

from llmsec.ataques import cargar_ataques
from llmsec.escenarios import cargar_escenario
from llmsec.estadistica import intervalo_wilson
from llmsec.jueces import JuezSecreto
from llmsec.objetivos import ObjetivoOllama

ATAQUES_DATOS = cargar_ataques("ataques")
ATAQUES = [ataque["texto"] for ataque in ATAQUES_DATOS]
CATEGORIA = {ataque["texto"]: ataque["categoria"] for ataque in ATAQUES_DATOS}

REPETICIONES = int(sys.argv[1]) if len(sys.argv) > 1 else 3
CADA = int(sys.argv[2]) if len(sys.argv) > 2 else 25
MODELO = sys.argv[3] if len(sys.argv) > 3 else "llama3.2"
RUTA_ESCENARIO = sys.argv[4] if len(sys.argv) > 4 else "escenarios/tienda.json"

escenario = cargar_escenario(RUTA_ESCENARIO)
SECRETO = escenario["secreto"]
REGLAS = escenario["reglas"]

ARCHIVO = "resultados_" + MODELO.replace(":", "_").replace("/", "_")
if escenario["nombre"] != "tienda":
    ARCHIVO = ARCHIVO + "__" + escenario["nombre"]
ARCHIVO = ARCHIVO + ".jsonl"

objetivo = ObjetivoOllama(MODELO)
juez = JuezSecreto(SECRETO)


def probar(ataque):
    mensajes = [
        {"role": "system", "content": REGLAS},
        {"role": "user", "content": ataque},
    ]
    return objetivo.responder(mensajes)


def cargar_previos():
    previos = []
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, encoding="utf-8") as archivo:
            for linea in archivo:
                if linea.strip():
                    previos.append(json.loads(linea))
    return previos


def anotar(registro):
    with open(ARCHIVO, "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")


def resumen(victorias, intentos, errores, inicio):
    print(f"\n--- {MODELO}: resumen ---")
    for ataque in ATAQUES:
        bajo, alto = intervalo_wilson(victorias[ataque], intentos[ataque])
        print(f"{victorias[ataque]}/{intentos[ataque]} (IC 95%: {bajo:.1%}-{alto:.1%}) | {ataque}")
    minutos = (time.time() - inicio) / 60
    llamadas = sum(intentos.values())
    print(f"Errores del modelo: {errores} de {llamadas} | Tiempo de esta sesión: {minutos:.1f} min\n")


previos = cargar_previos()
hechos = {(registro["ataque"], registro["intento"]) for registro in previos}
intentos = {ataque: 0 for ataque in ATAQUES}
victorias = {ataque: 0 for ataque in ATAQUES}
errores = 0
for registro in previos:
    if registro["ataque"] in intentos:
        intentos[registro["ataque"]] += 1
        if registro["funciono"]:
            victorias[registro["ataque"]] += 1
        if registro["respuesta"].startswith("ERROR"):
            errores += 1

inicio = time.time()
print(f"Modelo: {MODELO} | {REPETICIONES} repeticiones por ataque, {len(ATAQUES)} ataques")
print(f"Escenario: {escenario['nombre']}")
print(f"Resultados en: {ARCHIVO}")
if previos:
    print(f"Retomando: ya había {len(previos)} resultados guardados, no se repiten.")
print("Podés cortar con Ctrl+C: cada resultado ya quedó guardado y se puede retomar.\n")

try:
    for intento in range(1, REPETICIONES + 1):
        for ataque in ATAQUES:
            if (ataque, intento) in hechos:
                continue
            texto, pensamiento = probar(ataque)
            veredicto = juez.evaluar(texto, pensamiento)
            funciono = veredicto["funciono"]
            anotar(
                {
                    "ataque": ataque,
                    "categoria": CATEGORIA[ataque],
                    "intento": intento,
                    "respuesta": texto,
                    "pensamiento": pensamiento,
                    "filtro_en_pensamiento": veredicto["filtro_en_pensamiento"],
                    "funciono": funciono,
                }
            )
            intentos[ataque] += 1
            if funciono:
                victorias[ataque] += 1
            if texto.startswith("ERROR"):
                errores += 1
        if intento % CADA == 0 and intento != REPETICIONES:
            resumen(victorias, intentos, errores, inicio)
        else:
            print(".", end="", flush=True)
except KeyboardInterrupt:
    print("\nCorrida interrumpida por el usuario.")

resumen(victorias, intentos, errores, inicio)