from threading import Event


class CadastroInterrompido(Exception):
    """Interrupção solicitada pelo operador, entre operações completas."""


class ControleCadastro:
    def __init__(self):
        self._liberado = Event()
        self._liberado.set()
        self._interrompido = Event()

    @property
    def pausado(self):
        return not self._liberado.is_set()

    def pausar(self):
        self._liberado.clear()

    def continuar(self):
        self._liberado.set()

    def interromper(self):
        self._interrompido.set()
        self._liberado.set()

    def verificar(self):
        if self._interrompido.is_set():
            raise CadastroInterrompido()
        self._liberado.wait()
        if self._interrompido.is_set():
            raise CadastroInterrompido()
