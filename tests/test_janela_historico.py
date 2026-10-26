import os
import sys
import tempfile
import unittest
from unittest.mock import patch

import customtkinter as ctk

from app.historico import adicionar_cadastrada, listar_registros
from app.janela_historico import JanelaHistorico, SEM_ROMANEIO


@unittest.skipUnless(sys.platform == "win32", "Interface desktop Windows")
class TestJanelaHistorico(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raiz = ctk.CTk()
        cls.raiz.withdraw()
        cls.erros_callback = []
        cls.raiz.report_callback_exception = lambda *erro: cls.erros_callback.append(erro)

    @classmethod
    def tearDownClass(cls):
        for timer in cls.raiz.tk.call("after", "info"):
            cls.raiz.after_cancel(timer)
        cls.raiz.destroy()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.temp.name, "historico.json")
        adicionar_cadastrada("0001", "ADF", self.caminho, romaneio="00077")
        adicionar_cadastrada("0002", "ADF", self.caminho, romaneio="00088")
        adicionar_cadastrada("0003", "HP", self.caminho)
        self.janela = JanelaHistorico(self.raiz, caminho=self.caminho)
        self.janela.withdraw()

    def tearDown(self):
        self.raiz.update_idletasks()
        self.janela.fechar()
        self.temp.cleanup()
        self.assertFalse(self.erros_callback)

    def test_coluna_busca_e_filtro_exato_por_romaneio_incluem_legados(self):
        self.assertEqual(self.janela.tabela.item("ADF|0001", "values")[0], "00077")
        self.janela.filtro_romaneio.set("00077")
        self.janela._recarregar()
        self.assertEqual(self.janela.tabela.get_children(), ("ADF|0001",))
        self.janela.busca.set("HP")
        self.assertFalse(self.janela.tabela.get_children())
        self.janela.busca.set("")
        self.janela.filtro_romaneio.set(SEM_ROMANEIO)
        self.janela._recarregar()
        self.assertEqual(self.janela.tabela.get_children(), ("HP|0003",))
        self.janela.filtro_romaneio.set("Todos os romaneios")
        self.janela.busca.set("00088")
        self.assertEqual(self.janela.tabela.get_children(), ("ADF|0002",))

    def test_edicao_completa_romaneio_antigo_sem_trocar_identidade(self):
        self.janela.tabela.selection_set("HP|0003")
        self.janela._selecionar()
        self.assertEqual(self.janela.romaneio.get(), "")
        self.janela.romaneio.insert(0, "00099")
        with patch("app.janela_historico.Dialogo") as dialogo:
            self.janela._confirmar_edicao()
            dialogo.call_args.kwargs["confirmar"]("")
        registro = next(r for r in listar_registros(self.caminho) if r["chave"] == "HP|0003")
        self.assertEqual(registro["romaneio"], "00099")
        self.assertEqual(self.janela.romaneio.get(), "00099")

    def test_inclusao_exige_romaneio_e_confirmacao_grava_o_numero(self):
        self.janela.fornecedor.insert(0, "ADF")
        self.janela.numero.insert(0, "0004")
        with patch("app.janela_historico.Dialogo") as dialogo:
            self.janela._confirmar_adicao()
            dialogo.assert_not_called()
            self.janela.romaneio.insert(0, "00100")
            self.janela._confirmar_adicao()
            self.assertNotIn("ADF|0004", {r["chave"] for r in listar_registros(self.caminho)})
            dialogo.call_args.kwargs["confirmar"]("")
        registro = next(r for r in listar_registros(self.caminho) if r["chave"] == "ADF|0004")
        self.assertEqual(registro["romaneio"], "00100")


if __name__ == "__main__":
    unittest.main()
