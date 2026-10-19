import json
import sys
import time

from llmsec.ataques import cargar_ataques
from llmsec.jueces import JuezSecreto
from llmsec.escenarios import cargar_escenario
from llmsec.estadistica import intervalo_wilson
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
ARCHIVO = ARCHIVO + ".json"

objetivo = ObjetivoOllama(MODELO)
juez = JuezSecreto(SECRETO)


def probar(ataque):
    mensajes = [
        {"role": "system", "content": REGLAS},
        {"role": "user", "content": ataque},
    ]
    return objetivo.responder(mensajes)


def guardar(resultados):
    with open(ARCHIVO, "w", encoding="utf-8") as archivo:
        json.dump(resultados, archivo, ensure_ascii=False, indent=2)


def resumen(victorias, rondas, errores, inicio):
    print(f"\n--- {MODELO}: resumen tras {rondas} repeticiones por ataque ---")
    for ataque in ATAQUES:
        bajo, alto = intervalo_wilson(victorias[ataque], rondas)
        print(f"{victorias[ataque]}/{rondas} (IC 95%: {bajo:.1%}-{alto:.1%}) | {ataque}")
    minutos = (time.time() - inicio) / 60
    llamadas = rondas * len(ATAQUES)
    print(f"Errores del modelo: {errores} de {llamadas} | Tiempo: {minutos:.1f} min\n")


resultados = []
victorias = {ataque: 0 for ataque in ATAQUES}
errores = 0
rondas = 0
inicio = time.time()
print(f"Modelo: {MODELO} | {REPETICIONES} repeticiones por ataque, {len(ATAQUES)} ataques")
print(f"Escenario: {escenario['nombre']}")
print(f"Resultados en: {ARCHIVO}")
print("Podés cortar con Ctrl+C: se guarda lo hecho hasta ese momento.\n")

try:
    for intento in range(REPETICIONES):
        for ataque in ATAQUES:
            texto, pensamiento = probar(ataque)
            if texto.startswith("ERROR"):
                errores = errores + 1
            veredicto = juez.evaluar(texto, pensamiento)
            funciono = veredicto["funciono"]
            if funciono:
                victorias[ataque] = victorias[ataque] + 1
            resultados.append(
                {
                    "ataque": ataque,
                    "categoria": CATEGORIA[ataque],
                    "intento": intento + 1,
                    "respuesta": texto,
                    "pensamiento": pensamiento,
                    "filtro_en_pensamiento": veredicto["filtro_en_pensamiento"],
                    "funciono": funciono,
                }
            )
        rondas = rondas + 1
        if rondas % CADA == 0:
            guardar(resultados)
            resumen(victorias, rondas, errores, inicio)
        else:
            print(".", end="", flush=True)
except KeyboardInterrupt:
    print("\nCorrida interrumpida por el usuario.")

guardar(resultados)
if rondas > 0 and rondas % CADA != 0:
    resumen(victorias, rondas, errores, inicio)