import unittest
from unittest.mock import Mock, patch
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from app.modelos import Bobina
from app.navegador import (
    Navegador, SalvamentoNaoConfirmado, SEL_RUA, SEL_DIAMETRO,
    SEL_FORMATO, SEL_PESO, SEL_GRAMATURA, SEL_OBSERVACAO,
)


class TestPreenchimento(unittest.TestCase):
    def setUp(self):
        self.navegador = Navegador()
        self.page = Mock()
        self.navegador.page = self.page
        self.bobina = Bobina("00123", "MIOLO", 90, 1130, 1200, 800)
        self.valores = {}
        self.page.fill.side_effect = lambda seletor, valor: self.valores.update({seletor: valor})
        self.page.input_value.side_effect = lambda seletor: self.valores.get(seletor, "")
        logger = patch("app.navegador.logger")
        logger.start()
        self.addCleanup(logger.stop)

    def test_aviso_peso_nao_apaga_rua_diametro_formato(self):
        # Reproduz um aviso que recria os campos iniciais em branco.
        def aviso():
            self.valores.clear()

        with patch.object(self.navegador, "_fechar_popup_peso", side_effect=aviso):
            self.navegador.preencher_bobina(self.bobina)
        for seletor, esperado in ((SEL_RUA, "1"), (SEL_DIAMETRO, "1200"),
                                  (SEL_FORMATO, "1130"), (SEL_OBSERVACAO, "00123")):
            self.assertEqual(self.valores[seletor + ":visible"], esperado)
        primeira = self.page.fill.call_args_list[0].args[0]
        self.assertEqual(primeira, SEL_RUA + ":visible")

    def test_refaz_campos_apagados_no_recalculo(self):
        calculos = 0

        def recalcular():
            nonlocal calculos
            calculos += 1
            if calculos == 1:
                self.valores[SEL_FORMATO + ":visible"] = ""

        with patch.object(self.navegador, "_aguardar_campos_calculados", side_effect=recalcular):
            self.navegador.preencher_bobina(self.bobina)
        self.assertEqual(calculos, 2)
        self.assertEqual(self.valores[SEL_FORMATO + ":visible"], "1130")

    def test_campos_que_continuam_vazios_impedem_sucesso(self):
        def apagar():
            self.valores[SEL_RUA + ":visible"] = ""

        with patch.object(self.navegador, "_aguardar_campos_calculados", side_effect=apagar):
            with self.assertRaisesRegex(RuntimeError, "não será salvo"):
                self.navegador.preencher_bobina(self.bobina)
        self.assertIsNone(self.navegador._campos_esperados)

    def test_valor_que_nao_fica_no_campo_interrompe_preenchimento(self):
        self.page.input_value.side_effect = ["", "", "", ""]
        with self.assertRaisesRegex(RuntimeError, "não reteve"):
            self.navegador._fill_verificado(SEL_RUA, "1")
        self.assertEqual(self.page.fill.call_count, 4)

    def test_preenchimento_normal_nao_tem_pausas_fixas(self):
        with patch.object(self.navegador, "_fechar_popup_peso", return_value=False):
            self.navegador.preencher_bobina(self.bobina)
        self.page.wait_for_timeout.assert_not_called()
        self.assertEqual(self.page.fill.call_args_list[0].args[0], SEL_RUA + ":visible")

    def test_aviso_ausente_nao_espera_click_expirar(self):
        aviso = self.page.get_by_text.return_value.filter.return_value.first
        aviso.wait_for.side_effect = PlaywrightTimeoutError("timeout")
        self.assertFalse(self.navegador._fechar_popup_peso())
        aviso.wait_for.assert_called_once_with(state="visible", timeout=3000)
        aviso.locator.assert_not_called()

    def test_aviso_presente_e_fechado(self):
        aviso = self.page.get_by_text.return_value.filter.return_value.first
        popup = aviso.locator.return_value
        botao = popup.get_by_role.return_value
        self.assertTrue(self.navegador._fechar_popup_peso())
        aviso.wait_for.assert_called_once_with(state="visible", timeout=3000)
        botao.click.assert_called_once_with(timeout=3000)
        popup.wait_for.assert_called_once_with(state="hidden", timeout=3000)

    def test_falha_ao_clicar_aviso_identificado_nao_e_ignorada(self):
        aviso = self.page.get_by_text.return_value.filter.return_value.first
        botao = aviso.locator.return_value.get_by_role.return_value
        botao.click.side_effect = RuntimeError("click failed")
        with self.assertRaisesRegex(RuntimeError, "apareceu, mas não foi possível fechá-lo"):
            self.navegador._fechar_popup_peso()

    def test_campo_apagado_antes_salvar_nao_clica_salvar(self):
        self.navegador.preencher_bobina(self.bobina)
        self.valores[SEL_DIAMETRO + ":visible"] = ""
        self.page.click.reset_mock()
        with self.assertRaises(SalvamentoNaoConfirmado):
            self.navegador.salvar(peso=800, saldo_antes=1600)
        self.page.click.assert_not_called()


if __name__ == "__main__":
    unittest.main()
