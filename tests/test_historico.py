import json
import os
import tempfile
import unittest
from unittest.mock import patch

from app import historico


class TestGestaoHistorico(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.temp.name, "historico.json")

    def tearDown(self):
        self.temp.cleanup()

    def gravar(self, chaves):
        with open(self.caminho, "w", encoding="utf-8") as arquivo:
            json.dump({"cadastradas": chaves}, arquivo)

    def ler(self):
        with open(self.caminho, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    def test_lista_separa_fornecedor_e_preserva_numero_textual_e_legado(self):
        self.gravar(["ADF|0007", "0008"])
        self.assertEqual(historico.listar_registros(self.caminho), [
            {"chave": "0008", "fornecedor": "", "numero": "0008", "romaneio": ""},
            {"chave": "ADF|0007", "fornecedor": "ADF", "numero": "0007", "romaneio": ""},
        ])

    def test_schema_legado_sem_romaneios_permanece_compatível(self):
        self.gravar(["0007"])
        with patch.object(historico, "CAMINHO_HISTORICO", self.caminho):
            self.assertEqual(historico.carregar_historico(), {"0007"})
        self.assertEqual(historico.listar_registros(self.caminho)[0]["romaneio"], "")

    def test_adicao_manual_e_recusada_quando_chave_nova_ou_legada_ja_existe(self):
        historico.adicionar_cadastrada("0007", " adf ", self.caminho)
        self.assertEqual(historico.listar_registros(self.caminho)[0]["chave"], "ADF|0007")
        with self.assertRaises(ValueError):
            historico.adicionar_cadastrada("0007", "ADF", self.caminho)
        with self.assertRaises(ValueError):
            historico.adicionar_cadastrada("", "ADF", self.caminho)
        self.gravar(["0008"])
        with self.assertRaises(ValueError):
            historico.adicionar_cadastrada("0008", "HP", self.caminho)

    def test_adicao_remove_espacos_externos_do_numero_e_detecta_duplicata(self):
        historico.adicionar_cadastrada(" 0007 ", "ADF", self.caminho)
        self.assertEqual(historico.listar_registros(self.caminho)[0]["chave"], "ADF|0007")
        with self.assertRaises(ValueError):
            historico.adicionar_cadastrada("0007", "ADF", self.caminho)
        historico.adicionar_cadastrada(" 00 08 ", "HP", self.caminho)
        self.assertIn("HP|00 08", {r["chave"] for r in historico.listar_registros(self.caminho)})

    def test_fornecedor_com_delimitador_e_rejeitado_sem_alterar_registro(self):
        self.gravar(["ADF|0007"])
        with self.assertRaises(ValueError):
            historico.adicionar_cadastrada("0008", "FORN|ECEDOR", self.caminho)
        with self.assertRaises(ValueError):
            historico.editar_registro("ADF|0007", "0008", "FORN|ECEDOR", self.caminho)
        self.assertEqual({r["chave"] for r in historico.listar_registros(self.caminho)},
                         {"ADF|0007"})

    def test_marcar_com_romaneio_preserva_deduplicacao_e_numero_textual(self):
        with patch.object(historico, "CAMINHO_HISTORICO", self.caminho):
            historico.marcar_cadastrada("0007", "ADF", " NF 003 ")
            self.assertEqual(historico.carregar_historico(), {"ADF|0007"})
            self.assertTrue(historico.bobina_ja_cadastrada(
                historico.carregar_historico(), "0007", "ADF"))
            historico.marcar_cadastrada("0007", "ADF")
            self.assertEqual(historico.listar_registros(self.caminho)[0]["romaneio"], "NF 003")
            historico.marcar_cadastrada("0007", "ADF", "NF 004")
            self.assertEqual(historico.listar_registros(self.caminho)[0]["romaneio"], "NF 004")

    def test_metadados_sobrevivem_a_escritas_e_seguem_edicao_da_chave(self):
        with open(self.caminho, "w", encoding="utf-8") as arquivo:
            json.dump({"cadastradas": ["ADF|0001", "HP|0002"],
                       "romaneios": {"ADF|0001": "NF 10", "HP|0002": "NF 20"}}, arquivo)

        historico.adicionar_cadastrada("0003", "Cocelpa", self.caminho, " NF 30 ")
        dados = self.ler()
        self.assertEqual(dados["romaneios"], {
            "ADF|0001": "NF 10", "HP|0002": "NF 20", "COCELPA|0003": "NF 30"})

        historico.editar_registro("ADF|0001", "0001", "Novakraft", self.caminho)
        historico.editar_registro("HP|0002", "0002", "HP", self.caminho, "")
        historico.marcar_cadastrada("0003", "Cocelpa")
        dados = self.ler()
        self.assertEqual(dados["romaneios"], {
            "NOVAKRAFT|0001": "NF 10", "COCELPA|0003": "NF 30"})

        historico.excluir_registro("COCELPA|0003", self.caminho)
        dados = self.ler()
        self.assertEqual(dados["romaneios"], {"NOVAKRAFT|0001": "NF 10"})

    def test_edicao_e_exclusao_alteram_chaves_usadas_na_prevencao(self):
        self.gravar(["0007"])
        historico.editar_registro("0007", "0007", "ADF", self.caminho)
        self.assertEqual({r["chave"] for r in historico.listar_registros(self.caminho)},
                         {"ADF|0007"})
        historico.excluir_registro("ADF|0007", self.caminho)
        self.assertEqual(historico.listar_registros(self.caminho), [])

    def test_json_invalido_nao_e_substituido_por_marcacao(self):
        original = "{arquivo incompleto"
        with open(self.caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write(original)
        with patch.object(historico, "CAMINHO_HISTORICO", self.caminho):
            self.assertEqual(historico.carregar_historico(), set())
            with self.assertRaises(historico.HistoricoInvalido):
                historico.marcar_cadastrada("0007", "ADF")
        with open(self.caminho, "r", encoding="utf-8") as arquivo:
            self.assertEqual(arquivo.read(), original)

    def test_schema_json_invalido_bloqueia_gestao_sem_alterar_original(self):
        casos = [
            {"cadastradas": "ADF|0007"},
            {"cadastradas": None},
            {"cadastradas": [7]},
            ["ADF|0007"],
            {"cadastradas": ["ADF|0007"], "romaneios": "NF 01"},
            {"cadastradas": ["ADF|0007"], "romaneios": {"OUTRA|0001": "NF 01"}},
            {"cadastradas": ["ADF|0007"], "romaneios": {"ADF|0007": 1}},
        ]
        operacoes = (
            lambda: historico.listar_registros(self.caminho),
            lambda: historico.adicionar_cadastrada("0008", "ADF", self.caminho),
            lambda: historico.editar_registro("ADF|0007", "0008", "ADF", self.caminho),
            lambda: historico.excluir_registro("ADF|0007", self.caminho),
        )
        for dados in casos:
            with self.subTest(dados=dados):
                original = json.dumps(dados, ensure_ascii=False)
                with open(self.caminho, "w", encoding="utf-8") as arquivo:
                    arquivo.write(original)
                with patch.object(historico, "CAMINHO_HISTORICO", self.caminho):
                    for operacao in operacoes + (
                            lambda: historico.marcar_cadastrada("0008", "ADF"),):
                        with self.assertRaises(historico.HistoricoInvalido):
                            operacao()
                        with open(self.caminho, "r", encoding="utf-8") as arquivo:
                            self.assertEqual(arquivo.read(), original)

    def test_falha_de_replace_preserva_json_original_e_remove_temporario(self):
        with open(self.caminho, "w", encoding="utf-8") as arquivo:
            json.dump({"cadastradas": ["0007"], "romaneios": {"0007": "NF 10"}}, arquivo)
        with patch.object(historico.os, "replace", side_effect=OSError("falha simulada")):
            with self.assertRaises(historico.HistoricoInvalido):
                historico.adicionar_cadastrada("0008", "ADF", self.caminho)
        dados = self.ler()
        self.assertEqual(dados, {"cadastradas": ["0007"], "romaneios": {"0007": "NF 10"}})
        self.assertEqual(os.listdir(self.temp.name), ["historico.json"])


if __name__ == "__main__":
    unittest.main()
