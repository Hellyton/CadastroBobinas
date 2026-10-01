import json
import os


CAMINHO_HISTORICO = "historico_cadastro.json"


def _chave(numero, fornecedor=None):
    """
    Monta a chave usada no histórico. Combina fornecedor + número pra
    evitar que bobinas de fornecedores diferentes com o mesmo código
    colidam entre si. Se o fornecedor não for informado, cai pro
    comportamento antigo (só o número) - usado como fallback de
    compatibilidade, não pra gravar entradas novas.
    """

    if fornecedor:
        return f"{fornecedor.strip().upper()}|{numero}"

    return str(numero)


def carregar_historico():
    """Retorna o conjunto de chaves (fornecedor+número) já cadastradas
    com sucesso."""

    if not os.path.exists(CAMINHO_HISTORICO):
        return set()

    try:
        with open(CAMINHO_HISTORICO, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            return set(dados.get("cadastradas", []))

    except (json.JSONDecodeError, OSError):
        # Histórico corrompido ou ilegível: melhor seguir sem ele do que
        # travar o cadastro por causa disso.
        return set()


def bobina_ja_cadastrada(historico, numero, fornecedor=None):
    """
    Confere se uma bobina já está no histórico. Primeiro tenta a chave
    nova (fornecedor+número); se não achar, tenta o número puro, pra
    continuar reconhecendo entradas gravadas ANTES dessa mudança (que
    não tinham fornecedor associado) - assim nenhuma bobina já
    cadastrada antes passa a ser relançada por engano.
    """

    if _chave(numero, fornecedor) in historico:
        return True

    return str(numero) in historico


def marcar_cadastrada(numero, fornecedor=None):
    """Adiciona uma bobina ao histórico (usando fornecedor+número como
    chave, quando o fornecedor for informado) e salva no arquivo
    imediatamente."""

    cadastradas = carregar_historico()
    cadastradas.add(_chave(numero, fornecedor))

    with open(CAMINHO_HISTORICO, "w", encoding="utf-8") as arquivo:
        json.dump(
            {"cadastradas": sorted(cadastradas)},
            arquivo,
            ensure_ascii=False,
            indent=2
        )