import unittest
from unittest.mock import Mock, patch

from app.cadastro import CadastroBobinas
from app.modelos import Bobina
from app.navegador import Navegador, SalvamentoNaoConfirmado


class TestSaldoClassificacao(unittest.TestCase):
    def executar(self, saldos, erro=None):
        navegador = Mock()
        navegador.ler_saldo_classificar.side_effect = saldos
        if erro:
            navegador.salvar.side_effect = erro
        bobinas = [Bobina(str(i), "MIOLO", 90, 1130, 1200, 800, fornecedor="ADF")
                   for i in (1, 2)]
        with patch("app.cadastro.Navegador", return_value=navegador), \
                patch("app.cadastro.carregar_historico", return_value=set()), \
                patch("app.cadastro.marcar_cadastrada") as historico, \
                patch("app.cadastro.logger"):
            resultado = CadastroBobinas().iniciar(
                bobinas, solicitar=lambda *args: "")
        return resultado, navegador, historico

    def test_saldo_inicial_zero_nao_tenta_cadastrar(self):
        resultado, navegador, historico = self.executar([0, 0])
        self.assertTrue(resultado["motivo_parada"])
        self.assertEqual(resultado["sucessos"], 0)
        self.assertEqual(resultado["falhas"], 0)
        navegador.clicar_novo.assert_not_called()
        historico.assert_not_called()

    def test_ultima_bobina_zera_saldo_e_seguinte_fica_pendente(self):
        resultado, navegador, historico = self.executar([800, 800, 0])
        self.assertEqual(resultado["sucessos"], 1)
        self.assertEqual(resultado["falhas"], 0)
        self.assertTrue(resultado["motivo_parada"])
        navegador.salvar.assert_called_once_with(peso=800, saldo_antes=800)
        historico.assert_called_once_with("1", "ADF")

    def test_peso_maior_que_saldo_nao_tenta_cadastrar(self):
        # Regressão do erro EGS 1442056: só restam 35 kg na nota.
        resultado, navegador, historico = self.executar([35, 35])
        self.assertTrue(resultado["motivo_parada"])
        navegador.salvar.assert_not_called()
        historico.assert_not_called()

    def test_saldo_ilegivel_para_sem_gravar_historico(self):
        resultado, navegador, historico = self.executar([None, None])
        self.assertTrue(resultado["motivo_parada"])
        navegador.clicar_novo.assert_not_called()
        historico.assert_not_called()

    def test_salvamento_nao_confirmado_para_lote_sem_historico(self):
        resultado, navegador, historico = self.executar(
            [1600, 1600], SalvamentoNaoConfirmado("EGS rejeitou"))
        self.assertEqual(resultado["sucessos"], 0)
        self.assertEqual(resultado["falhas"], 1)
        self.assertTrue(resultado["motivo_parada"])
        navegador.salvar.assert_called_once()
        historico.assert_not_called()
        navegador.fechar.assert_called_once()

    def test_formulario_fechado_sem_saldo_atualizado_nao_e_sucesso(self):
        navegador = Navegador()
        navegador.page = Mock()
        navegador.page.wait_for_function.side_effect = TimeoutError("Saldo não mudou")
        with self.assertRaises(SalvamentoNaoConfirmado):
            navegador.salvar(peso=800, saldo_antes=800)

    def test_confirmacao_aceita_saldo_final_zero(self):
        navegador = Navegador()
        navegador.page = Mock()
        navegador.salvar(peso=800, saldo_antes=800)
        dados = navegador.page.wait_for_function.call_args.kwargs["arg"]
        self.assertEqual(dados["esperado"], 0)

    def test_salvar_com_saldo_zero_nao_clica(self):
        navegador = Navegador()
        navegador.page = Mock()
        with self.assertRaises(SalvamentoNaoConfirmado):
            navegador.salvar(peso=800, saldo_antes=0)
        navegador.page.click.assert_not_called()


if __name__ == "__main__":
    unittest.main()
