import unittest
from threading import Event, Thread
from unittest.mock import Mock, patch

from app.cadastro import CadastroBobinas
from app.controle import ControleCadastro, CadastroInterrompido
from app.modelos import Bobina


class TestControleCadastro(unittest.TestCase):
    def setUp(self):
        logger = patch("app.cadastro.logger")
        logger.start()
        self.addCleanup(logger.stop)

    def test_pausa_bloqueia_ate_continuar(self):
        controle = ControleCadastro()
        controle.pausar()
        entrou, terminou = Event(), Event()

        def executar():
            entrou.set()
            controle.verificar()
            terminou.set()

        thread = Thread(target=executar)
        thread.start()
        try:
            self.assertTrue(entrou.wait(1))
            self.assertFalse(terminou.wait(0.05))
            controle.continuar()
            self.assertTrue(terminou.wait(1))
        finally:
            controle.interromper()
            thread.join(1)

    def test_interromper_desbloqueia_pausa(self):
        controle = ControleCadastro()
        controle.pausar()
        controle.interromper()
        with self.assertRaises(CadastroInterrompido):
            controle.verificar()

    def executar_cadastro(self, navegador, controle=None, evento=None, solicitar=None):
        bobinas = [Bobina(str(i), "MIOLO", 90, 1130, 1200, 800)
                   for i in (1, 2)]
        with patch("app.cadastro.Navegador", return_value=navegador):
            return CadastroBobinas().iniciar(
                bobinas, usar_historico=False, controle=controle,
                evento=evento, solicitar=solicitar or (lambda *args: ""))

    def test_interrupcao_termina_salvamento_e_nao_inicia_proxima(self):
        controle = ControleCadastro()
        navegador = Mock()
        navegador.salvar.side_effect = controle.interromper
        resultado = self.executar_cadastro(navegador, controle)
        self.assertTrue(resultado["interrompido"])
        self.assertEqual(resultado["sucessos"], 1)
        navegador.salvar.assert_called_once()
        navegador.clicar_novo.assert_called_once()
        navegador.fechar.assert_called_once()

    def test_falha_no_login_fecha_navegador(self):
        navegador = Mock()
        navegador.fazer_login.side_effect = RuntimeError("Login falhou")
        with self.assertRaisesRegex(RuntimeError, "Login falhou"):
            self.executar_cadastro(navegador)
        navegador.fechar.assert_called_once()

    def test_progresso_contabiliza_sucessos_e_falhas(self):
        navegador = Mock()
        navegador.ler_saldo_classificar.return_value = None
        navegador.salvar.side_effect = [None, RuntimeError("Falha ao salvar")]
        eventos = []
        resultado = self.executar_cadastro(
            navegador, evento=lambda tipo, **dados: eventos.append((tipo, dados)))
        self.assertEqual(resultado["sucessos"], 1)
        self.assertEqual(resultado["falhas"], 1)
        self.assertFalse(resultado["interrompido"])
        progresso = [dados["concluidas"] for tipo, dados in eventos
                     if tipo == "progresso"]
        self.assertEqual(progresso, [0, 1, 2])
        navegador.tentar_fechar_modal.assert_called_once()
        navegador.fechar.assert_called_once()

    def test_pausa_durante_salvamento_segura_proxima_bobina(self):
        controle = ControleCadastro()
        navegador = Mock()
        navegador.ler_saldo_classificar.return_value = None
        primeira_salva, segunda_iniciada = Event(), Event()
        resultados = []

        def salvar():
            if not primeira_salva.is_set():
                controle.pausar()
                primeira_salva.set()
            else:
                segunda_iniciada.set()

        navegador.salvar.side_effect = salvar
        thread = Thread(target=lambda: resultados.append(
            self.executar_cadastro(navegador, controle)))
        thread.start()
        try:
            self.assertTrue(primeira_salva.wait(1))
            self.assertFalse(segunda_iniciada.wait(0.05))
            self.assertEqual(navegador.clicar_novo.call_count, 1)
            controle.continuar()
            thread.join(2)
            self.assertFalse(thread.is_alive())
            self.assertEqual(resultados[0]["sucessos"], 2)
        finally:
            controle.interromper()
            thread.join(2)

    def test_interrupcao_enquanto_aguarda_confirmacao_na_janela(self):
        from queue import Queue
        from types import SimpleNamespace
        from app.interface import App

        controle = ControleCadastro()
        janela = SimpleNamespace(_eventos=Queue())
        navegador = Mock()
        bobinas = [Bobina("1", "MIOLO", 90, 1130, 1200, 800)]
        with patch("app.cadastro.Navegador", return_value=navegador):
            thread = Thread(target=App.executar_cadastro,
                            args=(janela, bobinas, 0, controle))
            thread.start()
            try:
                while True:
                    tipo, dados = janela._eventos.get(timeout=2)
                    if tipo == "confirmacao":
                        break
                controle.interromper()
                thread.join(2)
                self.assertFalse(thread.is_alive())
                tipo, dados = janela._eventos.get(timeout=2)
                self.assertEqual(tipo, "finalizado")
                self.assertTrue(dados["resultado"]["interrompido"])
                navegador.salvar.assert_not_called()
                navegador.fechar.assert_called_once()
            finally:
                controle.interromper()
                thread.join(2)


if __name__ == "__main__":
    unittest.main()
