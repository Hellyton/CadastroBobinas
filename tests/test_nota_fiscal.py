from decimal import Decimal
import unittest
from unittest.mock import patch

from app.modelos import Bobina
from app.nota_fiscal import (
    ItemNotaFiscal,
    NotaFiscal,
    conferir_nota,
    ler_nota_fiscal,
    ler_numero_romaneio,
)


class TestLeituraNotaFiscal(unittest.TestCase):
    def setUp(self):
        self.texto = """NF-e
DANFE
N°. 000.123.456
DADOS DOS PRODUTOS / SERVIÇOS
CÓDIGO PRODUTO DESCRIÇÃO NCM/SH O/CST CFOP UN QUANT VALOR UNITÁRIO
91 MIOLO Largura 520mm 48051900 0/00 6101 KG 1.234,0000 3,8000 4.689,20
91 MIOLO Largura 620mm 48051900 0/00 6101 KG 2.000,0000 3,8000 7.600,00
91 MIOLO Largura 620mm 48051900 0/00 6101 KG 2.000,0000 3,8000 7.600,00
91 RECICLADO - P A
Largura 620mm 48051900 0/00 6101 KG 500,0000 3,8000 1.900,00
DADOS ADICIONAIS
Inf. Contribuinte: Romaneio Faturado n° 3617
"""

    def texto_com_linhas(self, linhas):
        cabecalho = self.texto.split("91 MIOLO Largura 520mm", 1)[0]
        rodape = self.texto[self.texto.index("DADOS ADICIONAIS"):]
        return cabecalho + "\n".join(linhas) + "\n" + rodape

    def test_le_linhas_preserva_repetidas_unidade_peso_e_referencia(self):
        with patch("app.nota_fiscal._extrair_texto", return_value=self.texto):
            nota = ler_nota_fiscal("nf-sintetica.pdf")

        self.assertEqual(nota.numero, "000.123.456")
        self.assertEqual(nota.romaneio, "3617")
        self.assertEqual([item.numero for item in nota.itens], ["1", "2", "3", "4"])
        self.assertEqual([item.codigo for item in nota.itens], ["91"] * 4)
        self.assertEqual([item.peso for item in nota.itens], [
            Decimal("1234.0000"), Decimal("2000.0000"),
            Decimal("2000.0000"), Decimal("500.0000"),
        ])
        self.assertEqual(nota.itens[3].descricao, "RECICLADO - P A Largura 620mm")
        self.assertEqual(nota.itens[3].produto, "RECICLADO")
        self.assertEqual(nota.itens[3].largura, 620)

    def test_recusa_unidade_nao_kg(self):
        texto = self.texto.replace("KG 1.234,0000", "UN 1.234,0000")
        with patch("app.nota_fiscal._extrair_texto", return_value=texto):
            with self.assertRaisesRegex(ValueError, "exige KG"):
                ler_nota_fiscal("nf-sintetica.pdf")

    def test_extrai_peso_com_valores_monetarios_concatenados_e_linha_reciclado(self):
        linhas = [
            "143 MIOLO 48051900 0/00 6101 KG 8.500,0000 "
            "2,150018.275,00 0,0018.275,00 2.193,00 500,00 12,00 3,25",
            "144 RECICLADO - P A",
            "Largura 620mm 48051900 0/00 6101 KG 620,0000 "
            "2,15001.333,00 0,001.333,00 160,00 30,00 12,00 3,25",
        ]
        texto = self.texto_com_linhas(linhas)
        with patch("app.nota_fiscal._extrair_texto", return_value=texto):
            nota = ler_nota_fiscal("nf-sintetica.pdf")

        self.assertEqual([item.peso for item in nota.itens], [
            Decimal("8500.0000"), Decimal("620.0000"),
        ])
        self.assertEqual(nota.itens[1].produto, "RECICLADO")

    def test_recusa_quantidade_malformada_sem_importacao_parcial(self):
        linha_valida = "91 MIOLO Largura 520mm 48051900 0/00 6101 KG 1.234,0000 3,8000 4.689,20"
        for quantidade in ("8.500,0000X", "8.50,0000"):
            with self.subTest(quantidade=quantidade):
                linha_invalida = (
                    "92 MIOLO Largura 620mm 48051900 0/00 6101 KG "
                    f"{quantidade} 3,8000 4.689,20"
                )
                texto = self.texto_com_linhas([linha_valida, linha_invalida])
                with patch("app.nota_fiscal._extrair_texto", return_value=texto):
                    with self.assertRaisesRegex(ValueError, "Quantidade inválida"):
                        ler_nota_fiscal("nf-sintetica.pdf")

    def test_recusa_layout_sem_itens_reconhecidos(self):
        texto = "NF-e DANFE N°. 000.123.456\nDADOS DOS PRODUTOS / SERVIÇOS\n"
        texto += "DADOS ADICIONAIS\n"
        with patch("app.nota_fiscal._extrair_texto", return_value=texto):
            with self.assertRaisesRegex(ValueError, "Nenhum item foi reconhecido"):
                ler_nota_fiscal("nf-layout-desconhecido.pdf")

    def test_nao_ignora_item_incompleto_depois_de_um_item_valido(self):
        linha_valida = "91 MIOLO Largura 520mm 48051900 0/00 6101 KG 1.234,0000 3,8000 4.689,20"
        linha_invalida = "92 MIOLO Largura 620mm 48051900 0/00 6101 KG quantidade-indefinida"
        texto = self.texto_com_linhas([linha_valida, linha_invalida])
        with patch("app.nota_fiscal._extrair_texto", return_value=texto):
            with self.assertRaisesRegex(ValueError, "incompleto"):
                ler_nota_fiscal("nf-sintetica.pdf")

    def test_nao_junta_item_incompleto_com_a_proxima_linha(self):
        linha_valida = "91 MIOLO Largura 520mm 48051900 0/00 6101 KG 1.234,0000 3,8000 4.689,20"
        linha_invalida = "92 MIOLO Largura 620mm 48051900 0/00 6101 KG quantidade-indefinida"
        linha_seguinte = "93 MIOLO Largura 620mm 48051900 0/00 6101 KG 2.000,0000 3,8000 7.600,00"
        texto = self.texto_com_linhas(
            [linha_valida, linha_invalida, linha_seguinte])
        with patch("app.nota_fiscal._extrair_texto", return_value=texto):
            with self.assertRaisesRegex(ValueError, "antes da próxima linha"):
                ler_nota_fiscal("nf-sintetica.pdf")

    def test_le_numero_de_romaneio_do_campo_impresso(self):
        with patch("app.nota_fiscal._extrair_texto", return_value="Número: 3617"):
            self.assertEqual(ler_numero_romaneio("rom-sintetico.pdf"), "3617")

    def test_le_pedido_do_cliente_no_romaneio_novakraft(self):
        texto = "\n".join([
            "SIGA /ESTR01/v.12 Relacao de Estoque/Pedido de Venda",
            "Cliente: ADF - EMPRESAS REUNIDAS LTDA - ME",
            "Pedido: V26654/01 Quant. Ped. : 32.028,20 ( 20 Reels)",
        ])
        with patch("app.nota_fiscal._extrair_texto", return_value=texto):
            self.assertEqual(ler_numero_romaneio("rom-novakraft.pdf"), "V26654/01")

    def test_pedido_fora_do_layout_novakraft_nao_vira_romaneio(self):
        with patch("app.nota_fiscal._extrair_texto", return_value="Pedido: V26654/01"):
            self.assertIsNone(ler_numero_romaneio("rom-sintetico.pdf"))


class TestConferenciaNota(unittest.TestCase):
    @staticmethod
    def bobina(numero, produto, peso, largura, descricao=""):
        return Bobina(str(numero), produto, 90, largura, 1200, peso,
                      descricao_original=descricao)

    @staticmethod
    def item(numero, produto, peso, largura=None):
        return ItemNotaFiscal(str(numero), "91", produto, produto, largura,
                              Decimal(peso))

    def test_sugere_peso_unico_e_avisa_largura_divergente(self):
        bobinas = [self.bobina(1, "MIOLO", 600, 520)]
        nota = NotaFiscal("NF1", "3617", [self.item(1, "MIOLO", "600", 620)])

        resultado = conferir_nota(nota, bobinas, "3617")

        self.assertTrue(resultado.referencia_compativel)
        self.assertEqual(resultado.associacoes["MIOLO · Ponta 520"], nota.itens[0])
        self.assertTrue(any("larguras diferem" in alerta
                            for alerta in resultado.alertas))

    def test_peso_duplicado_nos_itens_nf_nao_cria_associacao_arbitraria(self):
        bobinas = [self.bobina(1, "MIOLO", 600, 520)]
        nota = NotaFiscal("NF1", "3617", [
            self.item(1, "MIOLO", "600", 520),
            self.item(2, "MIOLO", "600", 520),
        ])

        resultado = conferir_nota(nota, bobinas, "3617")

        self.assertEqual(resultado.associacoes, {})
        self.assertTrue(any("não única" in pendencia
                            for pendencia in resultado.pendencias))

    def test_grupos_com_peso_duplicado_tambem_sao_ambiguos(self):
        bobinas = [
            self.bobina(1, "MIOLO", 600, 520, "MIOLO A"),
            self.bobina(2, "MIOLO", 600, 620, "MIOLO B"),
        ]
        nota = NotaFiscal("NF1", "3617", [self.item(1, "MIOLO", "600")])

        resultado = conferir_nota(nota, bobinas, "3617")

        self.assertEqual(resultado.associacoes, {})
        self.assertTrue(any("não única" in pendencia
                            for pendencia in resultado.pendencias))

    def test_item_unico_com_peso_total_associa_todos_os_grupos(self):
        bobinas = [
            self.bobina(1, "MIOLO", 600, 1830, "MIOLO"),
            self.bobina(2, "MIOLO", 400, 1030, "MIOLO // MIOLO"),
            self.bobina(3, "RECICLADO", 500, 1200, "RECICLADO"),
        ]
        nota = NotaFiscal("NF1", None, [self.item(1, "MIOLO", "1500.0000")])

        resultado = conferir_nota(nota, bobinas, "3875")

        self.assertTrue(resultado.item_unico)
        self.assertEqual(set(resultado.associacoes),
                         {"MIOLO", "MIOLO // MIOLO", "RECICLADO"})
        self.assertTrue(all(item is nota.itens[0]
                            for item in resultado.associacoes.values()))
        self.assertEqual(resultado.pendencias, [])
        self.assertTrue(any("RECICLADO" in alerta and "item único" in alerta
                            for alerta in resultado.alertas))

    def test_item_unico_com_peso_total_diferente_nao_associa(self):
        bobinas = [
            self.bobina(1, "MIOLO", 600, 1830, "MIOLO"),
            self.bobina(2, "MIOLO", 400, 1030, "MIOLO // MIOLO"),
        ]
        nota = NotaFiscal("NF1", "3875", [self.item(1, "MIOLO", "999")])

        resultado = conferir_nota(nota, bobinas, "3875")

        self.assertFalse(resultado.item_unico)
        self.assertEqual(resultado.associacoes, {})
        self.assertTrue(resultado.pendencias)

    def test_item_unico_nao_ignora_referencia_divergente(self):
        bobinas = [self.bobina(1, "MIOLO", 600, 1830)]
        nota = NotaFiscal("NF1", "3617", [self.item(1, "MIOLO", "600")])

        resultado = conferir_nota(nota, bobinas, "9999")

        self.assertFalse(resultado.item_unico)
        self.assertEqual(resultado.associacoes, {})

    def test_referencia_divergente_bloqueia_associacoes(self):
        bobinas = [self.bobina(1, "MIOLO", 600, 520)]
        nota = NotaFiscal("NF1", "3617", [self.item(1, "MIOLO", "600", 520)])

        resultado = conferir_nota(nota, bobinas, "9999")

        self.assertFalse(resultado.referencia_compativel)
        self.assertEqual(resultado.associacoes, {})
        self.assertTrue(resultado.alertas)


if __name__ == "__main__":
    unittest.main()
