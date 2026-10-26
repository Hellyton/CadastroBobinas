"""Agrupamento das bobinas em produtos/abas de classificação."""

from collections import defaultdict


def produtos_com_variantes(bobinas):
    """Retorna produtos com mais de uma descrição original distinta."""
    descricoes = defaultdict(set)
    for bobina in bobinas:
        descricao = " ".join((bobina.descricao_original or "").split())
        if descricao:
            descricoes[bobina.produto].add(descricao.casefold())
    return frozenset(produto for produto, valores in descricoes.items()
                     if len(valores) > 1)


def nome_grupo(bobina, variantes_por_produto=None):
    """Retorna a chave visível, usando variantes quando o contexto foi dado."""
    if (variantes_por_produto
            and bobina.produto in variantes_por_produto
            and bobina.descricao_original):
        return " ".join(bobina.descricao_original.split())
    if bobina.formato < 1000:
        return f"{bobina.produto} · Ponta {bobina.formato}"
    return bobina.produto


def agrupar_bobinas(bobinas, variantes_por_produto=None):
    """Agrupa por contexto completo; preserva contexto após filtros posteriores."""
    bobinas = list(bobinas)
    variantes = (produtos_com_variantes(bobinas)
                 if variantes_por_produto is None else variantes_por_produto)
    grupos = {}
    for bobina in bobinas:
        grupos.setdefault(nome_grupo(bobina, variantes), []).append(bobina)
    return grupos
