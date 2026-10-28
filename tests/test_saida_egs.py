import unittest
from unittest.mock import Mock

from playwright.sync_api import sync_playwright

from app.navegador import Navegador


PAGINA_CLASSIFICACAO = """
    <div id="h-icons">
      <button type="button"><span class="icon far fa-bell"></span></button>
      <button type="button" onclick="confirmarSaida()">
        <div><span class="icon far fa-power-off"></span></div>
      </button>
    </div>
    <div id="classificacao" class="modal ng-scope ng-isolate-scope in">
      <div><div><div class="modal-footer ng-scope"><div><div>
        <egs-button-close-popup>
          <button type="button" class="btn-footer-modal pull-left ng-binding"
                  onclick="setTimeout(() => document.querySelector('#classificacao').remove(), 200)">Sair</button>
        </egs-button-close-popup>
      </div></div></div></div></div>
    </div>
    <script>
      window.ordem = [];
      function confirmarSaida() {
        window.ordem.push(document.querySelector('#classificacao') ? 'modal aberto' : 'desligar');
        const modal = document.createElement('div');
        modal.className = 'modal ng-scope in';
        modal.innerHTML = '<div class="modal-footer"><button type="button" id="btnSimConfirm">Sim</button></div>';
        document.body.appendChild(modal);
        document.querySelector('#btnSimConfirm').onclick = () => setTimeout(() => {
          document.body.innerHTML = '<div id="login"><div><div></div><div><div><form>'
            + '<div></div><div><input></div></form></div></div></div></div>';
        }, 300);
      }
    </script>
"""


class TestSaidaEgsPlaywright(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        try:
            cls.browser = cls.playwright.chromium.launch(headless=True)
        except Exception as erro:
            cls.playwright.stop()
            raise unittest.SkipTest(f"Chromium local indisponível: {erro}")

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page()
        self.navegador = Navegador()
        self.navegador.page = self.page

    def tearDown(self):
        self.page.close()

    def test_fecha_classificacao_desliga_confirma_e_aguarda_login(self):
        self.page.set_content(PAGINA_CLASSIFICACAO)

        self.assertTrue(self.navegador.sair_do_sistema())

        self.assertEqual(self.page.evaluate("window.ordem"), ["desligar"])
        self.assertEqual(self.page.locator("#login input").count(), 1)

    def test_sem_modal_de_classificacao_ainda_encerra_sessao(self):
        self.page.set_content(PAGINA_CLASSIFICACAO)
        self.page.evaluate("document.querySelector('#classificacao').remove()")

        self.assertTrue(self.navegador.sair_do_sistema())


class TestSaidaEgsFalha(unittest.TestCase):
    def test_falha_ao_sair_e_registrada_sem_propagar(self):
        navegador = Navegador()
        navegador.page = Mock()
        navegador.page.locator.return_value.filter.return_value.count.return_value = 0
        navegador.page.click.side_effect = TimeoutError("Botão de desligar ausente")

        self.assertFalse(navegador.sair_do_sistema())
        navegador.page.wait_for_selector.assert_not_called()


if __name__ == "__main__":
    unittest.main()
