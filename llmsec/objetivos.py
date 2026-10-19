import ollama


def separar(mensaje):
    contenido = mensaje.content or ""
    pensamiento = mensaje.thinking or ""
    if "</think>" in contenido:
        antes, _, despues = contenido.rpartition("</think>")
        pensamiento = pensamiento + antes.replace("<think>", "")
        contenido = despues
    return contenido.strip(), pensamiento.strip()


class Objetivo:
    """Contrato: cualquier cosa a la que le mandamos ataques."""

    nombre = "sin-nombre"

    def responder(self, mensajes):
        """Recibe la conversación y devuelve (respuesta, pensamiento)."""
        raise NotImplementedError("Cada objetivo tiene que implementar responder()")


class ObjetivoOllama(Objetivo):
    """Un modelo local servido por Ollama."""

    def __init__(self, modelo):
        self.nombre = modelo
        self.modelo = modelo
        self.usa_pensamiento = True

    def responder(self, mensajes):
        try:
            try:
                respuesta = ollama.chat(
                    model=self.modelo, messages=mensajes, think=self.usa_pensamiento
                )
            except ollama.ResponseError as error:
                if "think" not in str(error).lower():
                    raise
                self.usa_pensamiento = False
                respuesta = ollama.chat(model=self.modelo, messages=mensajes)
            return separar(respuesta["message"])
        except Exception as error:
            return f"ERROR: {error}", ""


class ObjetivoFalso(Objetivo):
    """Responde siempre lo mismo. Sirve para probar el programa sin gastar tiempo ni plata."""

    def __init__(self, respuesta, pensamiento=""):
        self.nombre = "falso"
        self.respuesta = respuesta
        self.pensamiento = pensamiento

    def responder(self, mensajes):
        return self.respuesta, self.pensamiento


if __name__ == "__main__":
    objetivo = ObjetivoFalso("La clave es NARANJA-42")
    texto, pensamiento = objetivo.responder([{"role": "user", "content": "hola"}])
    print(texto)
    try:
        Objetivo().responder([])
    except NotImplementedError as error:
        print("OK, el contrato exige responder():", error)