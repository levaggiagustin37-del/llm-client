import json

import ollama


def preguntar(modelo, pregunta):
    try:
        respuesta = ollama.chat(
            model=modelo,
            messages=[{"role": "user", "content": pregunta}],
        )
        return respuesta["message"]["content"]
    except Exception as error:
        return f"ERROR: {error}"


preguntas = [
    "Explicame en dos frases qué es un agente de IA.",
    "¿Qué es la inyección de prompts?",
]

resultados = []
for pregunta in preguntas:
    texto = preguntar("llama3.2", pregunta)
    resultados.append({"pregunta": pregunta, "respuesta": texto})
    print(f"P: {pregunta}\nR: {texto}\n")

with open("resultados.json", "w", encoding="utf-8") as archivo:
    json.dump(resultados, archivo, ensure_ascii=False, indent=2)