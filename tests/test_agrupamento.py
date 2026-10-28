import unittest
from unittest.mock import Mock, patch

from app.agrupamento import (
    agrupar_bobinas,
    nome_grupo,
    produtos_com_variantes,
)
from app.cadastro import CadastroBobinas
from app.modelos import Bobina


def bobina(numero, produto, formato):
    return Bobina(str(numero), produto, 90, formato, 1200, 500)


class TestAgrupamentoBobinas(unittest.TestCase):
    def test_limite_separa_ponta_999_de_produto_1000(self):
        ponta = bobina(1, "MIOLO", 999)
        produto = bobina(2, "MIOLO", 1000)

        self.assertEqual(nome_grupo(ponta), "MIOLO · Ponta 999")
        self.assertEqual(nome_grupo(produto), "MIOLO")
        self.assertEqual(list(agrupar_bobinas([ponta, produto])),
                         ["MIOLO · Ponta 999", "MIOLO"])

    def test_mesma_largura_de_produtos_distintos_permanece_separada(self):
        miolo = bobina(1, "MIOLO", 940)
        reciclado = bobina(2, "RECICLADO", 940)

        grupos = agrupar_bobinas([miolo, reciclado])

        self.assertEqual(list(grupos),
                         ["MIOLO · Ponta 940", "RECICLADO · Ponta 940"])
        self.assertEqual(grupos["MIOLO · Ponta 940"], [miolo])
        self.assertEqual(grupos["RECICLADO · Ponta 940"], [reciclado])

    def test_bobinas_da_mesma_ponta_compartilham_grupo_e_peso_proprio(self):
        primeira = bobina(1, "MIOLO", 940)
        segunda = bobina(2, "MIOLO", 940)

        grupos = agrupar_bobinas([primeira, segunda])

        self.assertEqual(list(grupos), ["MIOLO · Ponta 940"])
        self.assertEqual(grupos["MIOLO · Ponta 940"], [primeira, segunda])
        self.assertEqual(sum(b.peso for b in grupos["MIOLO · Ponta 940"]), 1000)

    def test_variantes_da_mesma_familia_agrupam_pela_descricao_completa(self):
        bobinas = [
            bobina(1, "MIOLO", 520),
            bobina(2, "MIOLO", 620),
            bobina(3, "MIOLO", 420),
            bobina(4, "MIOLO", 620),
            bobina(5, "MIOLO", 620),
        ]
        descricoes = [
            "MIOLO // MIOLO",
            "MIOLO // MIOLO",
            "MIOLO // MIOLO PF P2A",
            "MIOLO // MIOLO PF P2A",
            "MIOLO // MIOLO-P2A",
        ]
        for bob, descricao in zip(bobinas, descricoes):
            bob.descricao_original = descricao

        grupos = agrupar_bobinas(bobinas)

        self.assertEqual(list(grupos), [
            "MIOLO // MIOLO",
            "MIOLO // MIOLO PF P2A",
            "MIOLO // MIOLO-P2A",
        ])
        self.assertEqual([len(grupo) for grupo in grupos.values()], [2, 2, 1])
        self.assertEqual(produtos_com_variantes(bobinas), frozenset({"MIOLO"}))
        self.assertEqual(nome_grupo(bobinas[0], {"MIOLO"}), "MIOLO // MIOLO")

    def test_mesma_descricao_sem_variantes_mantem_fallback_por_largura(self):
        bobinas = [bobina(1, "MIOLO", 520), bobina(2, "MIOLO", 620)]
        for bob in bobinas:
            bob.descricao_original = "MIOLO // MIOLO"

        self.assertEqual(list(agrupar_bobinas(bobinas)),
                         ["MIOLO · Ponta 520", "MIOLO · Ponta 620"])

    def test_cadastro_apresenta_e_processa_grupos_por_largura(self):
        bobinas = [
            bobina(1, "MIOLO", 940),
            bobina(2, "MIOLO", 940),
            bobina(3, "MIOLO", 720),
            bobina(4, "MIOLO", 720),
        ]
        bobinas[0].peso, bobinas[1].peso = 400, 500
        bobinas[2].peso, bobinas[3].peso = 300, 200
        navegador = Mock()
        navegador.ler_saldo_classificar.side_effect = [
            5000, 5000, 4600, 4100, 3800, 3600,
        ]
        chamadas_solicitar = []

        def solicitar(mensagem, opcoes=None):
            chamadas_solicitar.append((mensagem, opcoes))
            if opcoes is not None:
                return "MIOLO · Ponta 720"
            return ""

        with patch("app.cadastro.logger"), \
                patch("app.cadastro.Navegador", return_value=navegador), \
                patch("builtins.input", return_value=""):
            resultado = CadastroBobinas().iniciar(
                bobinas, usar_historico=False, solicitar=solicitar)

        selecao = next((opcoes for mensagem, opcoes in chamadas_solicitar
                        if mensagem.startswith("Escolha o próximo produto:")), None)
        self.assertEqual(selecao,
                         ["MIOLO · Ponta 940", "MIOLO · Ponta 720"])
        confirmacoes = [mensagem for mensagem, opcoes in chamadas_solicitar
                        if opcoes is None and mensagem.startswith("\nPróximo produto:")]
        self.assertEqual(len(confirmacoes), 2)
        self.assertIn("MIOLO · Ponta 720", confirmacoes[0])
        self.assertIn("Bobinas: 2\nPeso total: 500 kg", confirmacoes[0])
        self.assertIn("MIOLO · Ponta 940", confirmacoes[1])
        self.assertIn("Bobinas: 2\nPeso total: 900 kg", confirmacoes[1])
        self.assertEqual(navegador.preencher_bobina.call_args_list,
                         [unittest.mock.call(bobinas[2]),
                          unittest.mock.call(bobinas[3]),
                          unittest.mock.call(bobinas[0]),
                          unittest.mock.call(bobinas[1])])
        self.assertEqual(resultado["sucessos"], 4)
        self.assertEqual(resultado["falhas"], 0)

    def test_grupo_unico_da_nf_cadastra_lote_inteiro_sem_troca_de_produto(self):
        bobinas = [bobina(1, "MIOLO", 1830), bobina(2, "MIOLO", 1030),
                   bobina(3, "RECICLADO", 1200)]
        bobinas[0].descricao_original = "MIOLO"
        bobinas[1].descricao_original = "MIOLO // MIOLO"
        navegador = Mock()
        navegador.ler_saldo_classificar.side_effect = [5000, 5000, 4500, 4000, 3500]
        chamadas_solicitar = []

        def solicitar(mensagem, opcoes=None):
            chamadas_solicitar.append((mensagem, opcoes))
            return ""

        with patch("app.cadastro.logger"), \
                patch("app.cadastro.Navegador", return_value=navegador), \
                patch("builtins.input", return_value=""):
            resultado = CadastroBobinas().iniciar(
                bobinas, usar_historico=False, solicitar=solicitar,
                rotulos_grupos={"MIOLO": "MIOLO", "MIOLO // MIOLO": "MIOLO"},
                grupo_unico="NF 1525 · item 1 · MIOLO")

        self.assertFalse(any(opcoes for _mensagem, opcoes in chamadas_solicitar))
        self.assertFalse(any(mensagem.startswith("\nPróximo produto:")
                             for mensagem, _opcoes in chamadas_solicitar))
        self.assertEqual(navegador.preencher_bobina.call_args_list,
                         [unittest.mock.call(b) for b in bobinas])
        self.assertEqual(resultado["sucessos"], 3)

    def test_rotulo_nf_e_contexto_de_variantes_sobrevivem_ao_filtro_historico(self):
        primeira = bobina(1, "MIOLO", 520)
        primeira.descricao_original = "MIOLO // MIOLO"
        historica = bobina(2, "MIOLO", 620)
        historica.descricao_original = "MIOLO // MIOLO PF P2A"
        navegador = Mock()
        navegador.ler_saldo_classificar.side_effect = [1000, 1000, 500]
        eventos = []
        rotulo_nf = "NF item 1 — MIOLO // MIOLO"

        with patch("app.cadastro.logger"), \
                patch("app.cadastro.Navegador", return_value=navegador), \
                patch("app.cadastro.carregar_historico", return_value=set()), \
                patch("app.cadastro.marcar_cadastrada"), \
                patch("app.cadastro.bobina_ja_cadastrada",
                      side_effect=lambda _hist, numero, _fornecedor=None:
                      numero == historica.numero), \
                patch("builtins.input", return_value=""):
            resultado = CadastroBobinas().iniciar(
                [primeira, historica], usar_historico=True,
                solicitar=lambda *args: "",
                evento=lambda tipo, **dados: eventos.append((tipo, dados)),
                rotulos_grupos={"MIOLO // MIOLO": rotulo_nf},
            )

        status = [dados["texto"] for tipo, dados in eventos
                  if tipo == "status" and "Cadastrando bobina" in dados.get("texto", "")]
        self.assertEqual(resultado["sucessos"], 1)
        self.assertTrue(any(rotulo_nf in texto for texto in status))
        navegador.preencher_bobina.assert_called_once_with(primeira)


if __name__ == "__main__":
    unittest.main()
