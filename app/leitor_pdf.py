import pdfplumber
from app.parsers import FORNECEDORES, detectar_fornecedor


def ler_romaneio(caminho, fornecedor=None):
    """
    Lê o PDF do romaneio e extrai as bobinas.

    Se `fornecedor` não for informado, tenta detectar automaticamente
    pelo conteúdo (texto) do PDF. Se for informado (ex: "ADF", "HP",
    "Novakraft" ou "Cocelpa"), força o uso daquele parser - útil quando
    a detecção automática erra ou não reconhece um romaneio novo.

    Retorna (bobinas, fornecedor_usado, ajuste_peso).
    - `fornecedor_usado` é None se nenhum parser foi encontrado/
      reconhecido (nesse caso `bobinas` vem vazia e `ajuste_peso` é 0).
    - `ajuste_peso` é a soma (em kg) de ajustes/descontos do romaneio
      que não correspondem a nenhuma bobina específica (ex: uma linha
      de quebra no romaneio da Cocelpa) - já contabilizados no peso
      líquido total oficial do documento, mas não em nenhuma bobina
      individual. É usado na conferência de saldo do cadastro.

    Cada parser recebe o `caminho` do arquivo (não o texto já extraído),
    porque alguns fornecedores (ex: Cocelpa) precisam da posição de cada
    palavra na página, não só do texto puro.
    """

    if fornecedor is None:

        texto = ""

        with pdfplumber.open(caminho) as pdf:
            for pagina in pdf.pages:
                texto += (pagina.extract_text() or "") + "\n"

        fornecedor = detectar_fornecedor(texto)

    parser = FORNECEDORES.get(fornecedor)

    if parser is None:
        return [], fornecedor, 0

    bobinas, ajuste_peso = parser(caminho)

    return bobinas, fornecedor, ajuste_peso