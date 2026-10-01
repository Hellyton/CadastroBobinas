"""
Testa o cadastro completo com um romaneio REAL (PDF), mas rodando contra
o mock local (mock/mock_sistema.html) em vez do sistema de verdade.

Não afeta a operação real:
- não acessa o EGS de verdade (usa o mock local);
- não grava nada no historico_cadastro.json real (usar_historico=False).

Como usar:
1. Num terminal, na raiz do projeto:
     python -m http.server 8000
2. Noutro terminal:
     python teste_ambiente.py
   (abre uma janela pra você escolher o PDF do romaneio; se preferir,
   também dá pra passar o caminho direto: python teste_ambiente.py caminho.pdf)
"""

import sys

from app.leitor_pdf import ler_romaneio
from app.cadastro import CadastroBobinas
import config

URL_TESTE = "http://localhost:8000/mock/mock_sistema.html"

FORNECEDORES_DISPONIVEIS = ["ADF", "HP", "Novakraft", "Cocelpa"]


def escolher_arquivo():
    """Usa o argumento de linha de comando, se houver; senão abre uma
    janela de seleção de arquivo (mesmo diálogo usado na interface)."""

    if len(sys.argv) > 1:
        return sys.argv[1]

    from tkinter import Tk, filedialog

    raiz = Tk()
    raiz.withdraw()

    caminho = filedialog.askopenfilename(
        title="Selecione o Romaneio para teste",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )

    raiz.destroy()

    return caminho


def escolher_fornecedor_manualmente():

    print("\nNão foi possível identificar o fornecedor automaticamente.")
    print("Selecione manualmente:")

    for indice, nome in enumerate(FORNECEDORES_DISPONIVEIS, start=1):
        print(f"  {indice}. {nome}")

    while True:
        escolha = input("Fornecedor: ").strip()

        if escolha.isdigit() and 1 <= int(escolha) <= len(FORNECEDORES_DISPONIVEIS):
            return FORNECEDORES_DISPONIVEIS[int(escolha) - 1]

        print("Opção inválida, tente novamente.")


if __name__ == "__main__":

    caminho_pdf = escolher_arquivo()

    if not caminho_pdf:
        print("Nenhum arquivo selecionado. Encerrando.")
        sys.exit(1)

    bobinas, fornecedor, ajuste_peso = ler_romaneio(caminho_pdf)

    if fornecedor is None:
        fornecedor = escolher_fornecedor_manualmente()
        bobinas, fornecedor, ajuste_peso = ler_romaneio(
            caminho_pdf, fornecedor=fornecedor
        )

    print(f"\nFornecedor: {fornecedor}")
    print(f"Bobinas encontradas no romaneio: {len(bobinas)}")
    print(f"Ajuste de peso do romaneio: {ajuste_peso} kg")

    # Necessário pro histórico não confundir bobinas de fornecedores
    # diferentes que por coincidência tenham o mesmo número.
    for bobina in bobinas:
        bobina.fornecedor = fornecedor or ""

    produtos = sorted(set(bobina.produto for bobina in bobinas))
    print(f"Produto(s) no romaneio: {produtos}")

    if not bobinas:
        print("Nenhuma bobina foi reconhecida nesse PDF. Encerrando.")
        sys.exit(1)

    input("\nPressione ENTER para iniciar o teste contra o mock local...")

    # Aponta pro config.URL_TESTE se você preferir centralizar no
    # config.py em vez de hardcoded aqui - basta trocar a linha abaixo
    # por: url = getattr(config, "URL_TESTE", URL_TESTE)
    cadastro = CadastroBobinas()
    cadastro.iniciar(
        bobinas,
        ajuste_peso=ajuste_peso,
        url=URL_TESTE,
        usar_historico=False,
    )