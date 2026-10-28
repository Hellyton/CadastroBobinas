import sys
import unittest
from decimal import Decimal
from queue import Empty
from threading import Event
from unittest.mock import Mock, patch

from app.controle import ControleCadastro, CadastroInterrompido
from app.interface import App
from app.modelos import Bobina
from app.nota_fiscal import NotaFiscal, ItemNotaFiscal, conferir_nota


@unittest.skipUnless(sys.platform == "win32", "Interface desktop Windows")
class TestInterface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = App()
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        for timer in cls.app.tk.call("after", "info"):
            cls.app.after_cancel(timer)
        cls.app.destroy()

    def setUp(self):
        self.app._executando = False
        self.app._fechando = False
        self.app._pedido = None
        self.app._controle = None
        self.app.bobinas = [
            Bobina("001", "MIOLO", 90, 420, 1200, 500),
            Bobina("002", "MIOLO", 80, 420, 1100, 650),
            Bobina("003", "MIOLO", 90, 520, 1200, 700),
            Bobina("004", "RECICLADO", 90, 1000, 1200, 800),
        ]
        self.app.ajuste_peso = -50
        self.app.numero_romaneio.set("77")
        self.app._atualizar_romaneio()
        self.addCleanup(self.limpar_eventos)

    def limpar_eventos(self):
        self.app._fechar_confirmacao()
        if self.app._timer_eventos:
            self.app.after_cancel(self.app._timer_eventos)
            self.app._timer_eventos = None
        while True:
            try:
                self.app._eventos.get_nowait()
            except Empty:
                break

    def test_totais_separam_pontas_e_aplicam_ajuste_so_ao_geral(self):
        self.assertEqual(self.app.totais_produtos, {
            "MIOLO · Ponta 420": (2, 1150),
            "MIOLO · Ponta 520": (1, 700), "RECICLADO": (1, 800),
        })
        self.assertEqual(self.app.indicador_peso.valor.cget("text"), "2.600 kg")
        self.assertEqual(self.app.indicador_produtos.valor.cget("text"), "3")

    def test_filtro_preserva_totais_e_exporta_todo_romaneio(self):
        self.app.filtro_produto.set("MIOLO · Ponta 420")
        self.app.busca.set("002")
        itens = self.app.tabela.get_children()
        self.assertEqual(len(itens), 1)
        self.assertEqual(str(self.app.tabela.item(itens[0], "values")[0]), "002")
        self.assertEqual(self.app.indicador_peso.valor.cget("text"), "2.600 kg")
        self.assertEqual(self.app.totais_produtos["MIOLO · Ponta 420"], (2, 1150))
        workbook = Mock()
        with patch("app.interface.filedialog.asksaveasfilename", return_value="simulado.xlsx"), \
                patch("app.interface.Workbook", return_value=workbook), \
                patch.object(self.app, "_mostrar_mensagem"):
            self.app.exportar_excel()
        linhas = [chamada.args[0] for chamada in workbook.active.append.call_args_list]
        self.assertEqual(len(linhas), 5)
        self.assertEqual([linha[0] for linha in linhas[1:]], ["001", "002", "003", "004"])
        self.assertEqual([linha[5] for linha in linhas[1:]], [500, 650, 700, 800])

    def test_erro_de_importacao_desabilita_lote_anterior(self):
        with patch("app.interface.ler_romaneio", side_effect=OSError("PDF indisponível")), \
                patch("app.interface.logger"), patch.object(self.app, "_mostrar_mensagem") as mensagem:
            self.app.processar_pdf("ADF")
        self.assertEqual(self.app.bobinas, [])
        self.assertEqual(self.app.totais_produtos, {})
        self.assertFalse(self.app.tabela.get_children())
        self.assertEqual(self.app.botao_cadastro.cget("state"), "disabled")
        self.assertEqual(self.app.botao_exportar.cget("state"), "disabled")
        mensagem.assert_called_once()
        self.assertEqual(self.app.numero_romaneio.get(), "")

    def test_importacao_preenche_romaneio_e_permite_informar_quando_ausente(self):
        bobinas = list(self.app.bobinas)
        self.app.caminho_pdf = "romaneio_simulado.pdf"
        with patch("app.interface.ler_romaneio", return_value=(bobinas, "ADF", 0)), \
                patch("app.interface.ler_numero_romaneio", return_value="00077"):
            self.app.processar_pdf(None)
        self.assertEqual(self.app.numero_romaneio.get(), "00077")
        with patch("app.interface.ler_romaneio", return_value=(bobinas, "ADF", 0)), \
                patch("app.interface.ler_numero_romaneio", return_value=None):
            self.app.processar_pdf("ADF")
        self.assertEqual(self.app.numero_romaneio.get(), "")
        self.assertEqual(self.app.campo_romaneio.cget("state"), "normal")
        with patch("app.interface.Thread") as thread, \
                patch.object(self.app, "_mostrar_mensagem") as mensagem:
            self.app.iniciar_cadastro()
        thread.assert_not_called()
        mensagem.assert_called_once()

    def test_romaneio_capturado_antes_do_worker_e_enviado_ao_cadastro(self):
        self.app.numero_romaneio.set(" 00077 ")
        with patch("app.interface.Thread") as thread:
            self.app.iniciar_cadastro()
        argumentos = thread.call_args.kwargs["args"]
        self.assertEqual(argumentos[4], "00077")
        self.assertIsNone(argumentos[5])
        self.assertFalse(argumentos[6].is_set())
        self.assertEqual(self.app.campo_romaneio.cget("state"), "disabled")
        with patch("app.interface.CadastroBobinas") as cadastro:
            self.app.executar_cadastro(*argumentos)
        self.assertEqual(cadastro.return_value.iniciar.call_args.kwargs["numero_romaneio"], "00077")

    def test_confirmacao_entrega_grupo_ao_worker(self):
        pedido = dict(mensagem="Escolha o próximo produto", pronto=Event(),
                      opcoes=["MIOLO · Ponta 420", "MIOLO · Ponta 520"], resposta=None)
        self.app._eventos.put(("confirmacao", {"pedido": pedido}))
        with patch("app.interface.Dialogo") as dialogo:
            self.app.processar_eventos()
            self.assertEqual(dialogo.call_args.kwargs["opcoes"], pedido["opcoes"])
            self.app.confirmar_etapa("MIOLO · Ponta 520")
        self.assertTrue(pedido["pronto"].is_set())
        self.assertEqual(pedido["resposta"], "MIOLO · Ponta 520")
        self.assertIsNone(self.app._pedido)

    def test_interromper_libera_pausa_e_fecha_confirmacao(self):
        self.app._executando = True
        self.app._controle = ControleCadastro()
        self.app._controle.pausar()
        self.app._dialogo_confirmacao = Mock()
        dialogo = self.app._dialogo_confirmacao
        self.app.interromper_cadastro()
        dialogo.fechar.assert_called_once()
        with self.assertRaises(CadastroInterrompido):
            self.app._controle.verificar()
        self.assertEqual(self.app.botao_interromper.cget("state"), "disabled")

    def test_resultado_parcial_nao_exibe_cem_porcento(self):
        resultado = dict(sucessos=1, falhas=1, total=3, ignoradas=0,
                         interrompido=False, motivo_parada="Confira o saldo da nota.")
        with patch.object(self.app, "_mostrar_mensagem"):
            self.app.encerrar_cadastro("finalizado", {"resultado": resultado})
        self.assertEqual(self.app.rotulo_progresso.cget("text"), "67%")
        self.assertIn("1 não processadas", self.app.status.cget("text"))
        self.assertEqual(self.app.botao_cadastro.cget("state"), "normal")

    def nota_simulada(self, referencia="77"):
        return NotaFiscal("000.000.123", referencia, [
            ItemNotaFiscal("1", "9", "MIOLO Largura 420mm", "MIOLO", 420, Decimal(1150)),
            ItemNotaFiscal("2", "9", "MIOLO Largura 520mm", "MIOLO", 520, Decimal(700)),
            ItemNotaFiscal("3", "9", "RECICLADO Largura 1000mm", "RECICLADO", 1000, Decimal(800)),
        ])

    def test_nf_opcional_so_aplica_rotulos_apos_confirmacao(self):
        nota = self.nota_simulada()
        self.app.caminho_pdf = "romaneio_simulado.pdf"
        with patch("app.interface.filedialog.askopenfilename", return_value="nf_simulada.pdf"), \
                patch("app.interface.ler_nota_fiscal", return_value=nota), \
                patch("app.interface.ler_numero_romaneio", return_value="77"), \
                patch("app.interface.Dialogo") as dialogo:
            self.app.abrir_nf()
            self.assertIsNone(self.app._nota_fiscal)
            self.assertFalse(self.app._associacoes_nf)
            dialogo.call_args.kwargs["confirmar"]("")
        self.assertEqual(len(self.app._associacoes_nf), 3)
        self.assertIn("item 1", self.app._rotulos_cadastro()["MIOLO · Ponta 420"])
        self.assertEqual(self.app.totais_produtos["MIOLO · Ponta 420"], (2, 1150))
        self.assertEqual(self.app.indicador_peso.valor.cget("text"), "2.600 kg")

    def test_nf_com_referencia_diferente_nao_pode_ser_aplicada(self):
        nota = self.nota_simulada("88")
        conferencia = conferir_nota(nota, self.app.bobinas, "77")
        self.app._aceitar_nf(nota, conferencia)
        self.assertIsNone(self.app._nota_fiscal)
        self.assertFalse(self.app._associacoes_nf)

    def test_reprocessar_romaneio_remove_associacoes_nf_anteriores(self):
        nota = self.nota_simulada()
        self.app._aceitar_nf(nota, conferir_nota(nota, self.app.bobinas, "77"))
        self.assertEqual(len(self.app._associacoes_nf), 3)
        self.app._atualizar_romaneio()
        self.assertFalse(self.app._associacoes_nf)
        self.assertIsNone(self.app._nota_fiscal)
        self.assertNotIn("item 1", self.app._rotulos_cadastro()["MIOLO · Ponta 420"])

    def test_correcao_do_romaneio_descarta_nf_e_confere_nova_referencia(self):
        nota = self.nota_simulada()
        self.app._aceitar_nf(nota, conferir_nota(nota, self.app.bobinas, "77"))
        self.app.numero_romaneio.set("88")
        self.assertIsNone(self.app._nota_fiscal)
        self.assertFalse(self.app._associacoes_nf)
        with patch("app.interface.filedialog.askopenfilename", return_value="nf_simulada.pdf"), \
                patch("app.interface.ler_nota_fiscal", return_value=nota), \
                patch("app.interface.Dialogo") as dialogo:
            self.app.abrir_nf()
            dialogo.return_value.botao_confirmar.configure.assert_called_once_with(state="disabled")
            dialogo.call_args.kwargs["confirmar"]("")
            self.assertIsNone(self.app._nota_fiscal)

    def test_variacoes_usam_descricao_e_juntam_larguras_no_mesmo_grupo(self):
        self.app.bobinas = [
            Bobina("EX-1", "MIOLO", 90, 420, 1200, 300, descricao_original="MIOLO // MIOLO"),
            Bobina("EX-2", "MIOLO", 90, 620, 1200, 400, descricao_original="MIOLO // MIOLO"),
            Bobina("EX-3", "MIOLO", 90, 620, 1200, 500, descricao_original="MIOLO // MIOLO PF P2A"),
        ]
        self.app._atualizar_romaneio()
        self.assertEqual(self.app.totais_produtos["MIOLO // MIOLO"], (2, 700))
        self.app.filtro_produto.set("MIOLO PF P2A")
        self.app.filtrar_bobinas()
        linhas = self.app.tabela.get_children()
        self.assertEqual(len(linhas), 1)
        self.assertEqual(self.app.tabela.item(linhas[0], "values")[1], "MIOLO PF P2A")

    def test_novo_cadastro_fecha_navegador_mantido_pelo_anterior(self):
        anterior = self.app._encerrar_navegador
        with patch("app.interface.Thread") as thread:
            self.app.iniciar_cadastro()
        self.assertTrue(anterior.is_set())
        novo = thread.call_args.kwargs["args"][6]
        self.assertIs(novo, self.app._encerrar_navegador)
        self.assertFalse(novo.is_set())

    def bobinas_com_variantes_que_colidem(self):
        return [
            Bobina("V-1", "MIOLO", 90, 1830, 1200, 1000, descricao_original="MIOLO"),
            Bobina("V-2", "MIOLO", 90, 1030, 1200, 800, descricao_original="MIOLO // MIOLO"),
            Bobina("V-3", "RECICLADO", 90, 1200, 1200, 900, descricao_original="RECICLADO"),
            Bobina("V-4", "RECICLADO", 90, 1100, 1200, 700,
                   descricao_original="RECICLADO // RECICLADO"),
        ]

    def test_variantes_que_encurtam_igual_mantem_rotulos_distintos_no_cadastro(self):
        self.app.bobinas = self.bobinas_com_variantes_que_colidem()
        self.app._atualizar_romaneio()
        rotulos = self.app._rotulos_cadastro()
        self.assertEqual(rotulos, {
            "MIOLO": "MIOLO", "MIOLO // MIOLO": "MIOLO // MIOLO",
            "RECICLADO": "RECICLADO", "RECICLADO // RECICLADO": "RECICLADO // RECICLADO",
        })
        self.app.filtro_produto.set("MIOLO // MIOLO")
        self.app.filtrar_bobinas()
        linhas = self.app.tabela.get_children()
        self.assertEqual([self.app.tabela.item(l, "values")[0] for l in linhas], ["V-2"])

    def test_nf_com_item_unico_envia_lote_inteiro_em_uma_etapa(self):
        self.app.bobinas = self.bobinas_com_variantes_que_colidem()
        self.app._atualizar_romaneio()
        nota = NotaFiscal("000.001.525", None, [
            ItemNotaFiscal("1", "143", "MIOLO", "MIOLO", None, Decimal("3400.0000"))])
        with patch("app.interface.filedialog.askopenfilename", return_value="nf_simulada.pdf"), \
                patch("app.interface.ler_nota_fiscal", return_value=nota), \
                patch("app.interface.Dialogo") as dialogo:
            self.app.abrir_nf()
            dialogo.return_value.botao_confirmar.configure.assert_not_called()
            self.assertIn("única etapa", dialogo.call_args.args[2])
            dialogo.call_args.kwargs["confirmar"]("")
        self.assertEqual(len(self.app._associacoes_nf), 4)
        with patch("app.interface.Thread") as thread:
            self.app.iniciar_cadastro()
        argumentos = thread.call_args.kwargs["args"]
        self.assertEqual(argumentos[5], "NF 1525 · item 1 · MIOLO")
        with patch("app.interface.CadastroBobinas") as cadastro:
            self.app.executar_cadastro(*argumentos)
        self.assertEqual(cadastro.return_value.iniciar.call_args.kwargs["grupo_unico"],
                         "NF 1525 · item 1 · MIOLO")
        self.app._atualizar_romaneio()
        self.assertIsNone(self.app._grupo_unico_nf())


if __name__ == "__main__":
    unittest.main()
