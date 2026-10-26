import unittest

from playwright.sync_api import sync_playwright

from app.modelos import Bobina
from app.navegador import (
    Navegador, SEL_RUA, SEL_DIAMETRO, SEL_FORMATO, SEL_PESO, SEL_GRAMATURA,
)


class TestPopupPesoPlaywright(unittest.TestCase):
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

    def test_aguarda_popup_atrasado_fecha_so_peso_zero_e_aguarda_ocultar(self):
        self.page.set_content("""
            <section id="erro-geral" role="dialog">
              <p>Erro de validação da rua</p>
              <button onclick="window.outroClique = true">OK</button>
            </section>
            <section id="aviso-peso" role="dialog" style="display:none">
              <p>Peso da bobina não pode ser zero!</p>
              <button onclick="document.querySelector('#aviso-peso').remove()">OK</button>
            </section>
            <script>
              window.outroClique = false;
              setTimeout(() => {
                document.querySelector('#aviso-peso').style.display = 'block';
              }, 350);
            </script>
        """)

        self.assertTrue(self.navegador._fechar_popup_peso())

        self.assertFalse(self.page.locator("#aviso-peso").count())
        self.assertTrue(self.page.locator("#erro-geral").is_visible())
        self.assertFalse(self.page.evaluate("window.outroClique"))

    def test_aviso_ausente_nao_fecha_ok_de_outro_dialogo(self):
        self.page.set_content("""
            <div role="dialog"><p>Falha ao validar rua</p>
              <button onclick="window.cliques++">OK</button>
            </div>
            <script>window.cliques = 0;</script>
        """)

        self.assertFalse(self.navegador._fechar_popup_peso())

        self.assertEqual(self.page.evaluate("window.cliques"), 0)
        self.assertTrue(self.page.get_by_role("button", name="OK").is_visible())

    def test_preenche_dois_formularios_apos_popup_atrasado_e_preserva_campos(self):
        for numero, peso, formato, gramatura in (
                ("B-1", 800, 1130, 90), ("B-2", 950, 1020, 95)):
            with self.subTest(numero=numero):
                self.page.set_content(f"""
                    <div id="egsForm"><div>
                      <egs-input-text><input id="rua"></egs-input-text>
                      <egs-input-text><input id="diametro"></egs-input-text>
                      <egs-input-text><input id="formato"></egs-input-text>
                      <egs-input-text><input id="peso"></egs-input-text>
                      <egs-input-text><input id="gramatura"></egs-input-text>
                    </div></div>
                    <div id="aviso" role="dialog" style="display:none">
                      <p>Peso da bobina não pode ser zero!</p>
                      <button onclick="clearTimeout(window.popupTimer); document.querySelector('#aviso').style.display='none'; window.ordem.push('OK')">OK</button>
                    </div>
                    <span style="display:none">Peso da bobina não pode ser zero!</span>
                    <script>
                      window.ordem = [];
                      const peso = document.querySelector('#peso');
                      peso.addEventListener('focus', () => {{
                        if (!window.ordem.includes('focuspeso')) {{
                          window.ordem.push('focuspeso');
                        }}
                      }});
                      peso.addEventListener('click', () => {{
                        window.popupTimer = setTimeout(() => {{
                          document.querySelector('#aviso').style.display='block';
                        }}, 350);
                      }});
                      peso.addEventListener('input', () => {{
                        if (peso.value) window.ordem.push('fillpeso');
                      }});
                      document.querySelector('#gramatura').addEventListener('input',
                        () => window.ordem.push('fillgramatura'));
                    </script>
                """)
                bobina = Bobina(numero, "MIOLO", gramatura, formato, 1200, peso)

                self.navegador._preencher_campos(bobina)

                self.assertEqual(self.page.evaluate("window.ordem"), [
                    "focuspeso", "OK", "fillpeso", "fillgramatura",
                ])
                self.assertEqual(self.page.locator(SEL_RUA).input_value(), "1")
                self.assertEqual(self.page.locator(SEL_DIAMETRO).input_value(), "1200")
                self.assertEqual(self.page.locator(SEL_FORMATO).input_value(), str(formato))
                self.assertEqual(self.page.locator(SEL_PESO).input_value(), str(peso))
                self.assertEqual(self.page.locator(SEL_GRAMATURA).input_value(), str(gramatura))


if __name__ == "__main__":
    unittest.main()
