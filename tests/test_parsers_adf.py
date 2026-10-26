import unittest
from unittest.mock import patch

from app.modelos import Bobina
from app.parsers import extrair_bobinas_adf


class TestParserADF(unittest.TestCase):
    def test_preserva_descricao_completa_sem_alterar_produto_base(self):
        texto = "\n".join([
            "11111 2222 MIOLO // MIOLO PF P2A MIOLO 100 620 1300 8.097 KG 502 502 502",
            "22222 3333 MIOLO // MIOLO-P2A MIOLO 100 620 1290 8.194 KG 508 508 508",
            "33333 4444 RECICLADO RECICLAD 100 620 1280 8.177 KG 507 507 507",
        ])

        with patch("app.parsers._extrair_texto", return_value=texto):
            bobinas, ajuste = extrair_bobinas_adf("romaneio-sintetico.pdf")

        self.assertEqual(ajuste, 0)
        self.assertEqual([bob.produto for bob in bobinas],
                         ["MIOLO", "MIOLO", "RECICLADO"])
        self.assertEqual([bob.descricao_original for bob in bobinas], [
            "MIOLO // MIOLO PF P2A",
            "MIOLO // MIOLO-P2A",
            "RECICLADO",
        ])
        self.assertEqual([bob.peso for bob in bobinas], [502, 508, 507])

    def test_descricao_opcional_preserva_construtores_posicionais(self):
        bobina = Bobina("001", "MIOLO", 90, 620, 1280, 502, 3, "ADF")

        self.assertEqual(bobina.rua, 3)
        self.assertEqual(bobina.fornecedor, "ADF")
        self.assertEqual(bobina.descricao_original, "")


if __name__ == "__main__":
    unittest.main()
