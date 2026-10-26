"""Leitura opcional de itens de NF-e DANFE ADF e conciliação com romaneio."""

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
import re
import unicodedata

import pdfplumber

from app.agrupamento import agrupar_bobinas


@dataclass
class ItemNotaFiscal:
    numero: str
    codigo: str
    descricao: str
    produto: str
    largura: int | None
    peso: Decimal


@dataclass
class NotaFiscal:
    numero: str
    romaneio: str | None
    itens: list[ItemNotaFiscal]


@dataclass
class ConferenciaNota:
    associacoes: dict[str, ItemNotaFiscal] = field(default_factory=dict)
    pendencias: list[str] = field(default_factory=list)
    alertas: list[str] = field(default_factory=list)
    referencia_compativel: bool = True


def _extrair_texto(caminho):
    with pdfplumber.open(caminho) as pdf:
        return "\n".join(pagina.extract_text() or "" for pagina in pdf.pages)


def _normalizar(texto):
    decomposed = unicodedata.normalize("NFKD", texto or "")
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _numero_decimal_br(valor):
    valor = valor.strip()
    if not re.fullmatch(r"(?:\d{1,3}(?:\.\d{3})+|\d+),\d+", valor):
        raise ValueError(f"Quantidade inválida na NF: {valor!r}.")
    texto = valor.replace(".", "").replace(",", ".")
    try:
        return Decimal(texto)
    except InvalidOperation as erro:
        raise ValueError(f"Quantidade inválida na NF: {valor!r}.") from erro


def _extrair_numero_nota(texto):
    normalizado = _normalizar(texto)
    match = re.search(r"\bN[^\d]{0,6}(\d{3}\.\d{3}\.\d{3})\b",
                      normalizado, re.I)
    if not match:
        inicio = normalizado.upper().find("DANFE")
        trecho = normalizado[inicio:] if inicio >= 0 else normalizado
        match = re.search(r"(\d{3}\.\d{3}\.\d{3})", trecho)
    if not match:
        raise ValueError("Número da NF-e não identificado no PDF DANFE.")
    return match.group(1)


def _extrair_referencia_nf(texto):
    normalizado = _normalizar(texto)
    match = re.search(
        r"\bromaneio\s+faturado\s+n(?:[º°.]|o)?\s*(\d+)\b",
        normalizado, re.I,
    )
    return match.group(1) if match else None


def _normalizar_produto(descricao):
    normalizado = _normalizar(descricao).upper()
    palavras = re.findall(r"[A-Z0-9]+", normalizado)
    if "RECICLADO" in palavras:
        return "RECICLADO"
    if "MIOLO" in palavras:
        return "MIOLO"
    return palavras[0] if palavras else ""


def _extrair_largura(descricao):
    normalizado = _normalizar(descricao)
    match = re.search(r"\blargura\s*(\d+)\s*mm\b", normalizado, re.I)
    return int(match.group(1)) if match else None


def ler_nota_fiscal(caminho):
    """Lê itens KG de DANFE ADF; layouts/unidades não reconhecidos são recusados."""
    texto = _extrair_texto(caminho)
    normalizado = _normalizar(texto)
    if "DANFE" not in normalizado.upper() or "NF-E" not in normalizado.upper():
        raise ValueError("PDF não reconhecido como NF-e DANFE suportada.")

    inicio = normalizado.upper().find("DADOS DOS PRODUTOS")
    if inicio < 0:
        raise ValueError("Tabela de produtos/serviços não encontrada no DANFE.")
    fim = normalizado.upper().find("DADOS ADICIONAIS", inicio)
    linhas = texto[inicio: fim if fim >= 0 else None].splitlines()[1:]
    marcador_item = re.compile(
        r"(?P<ncm>\d{8})\s+\d/\d{2}\s+\d{4}\s+"
        r"(?P<unidade>[A-Z]{1,4})\s+(?P<peso>\d\S*)",
        re.I,
    )
    linhas_itens = []
    linha_atual = ""
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        inicio_item = re.match(r"^\d{1,16}\s+", linha)
        if linha_atual and inicio_item:
            raise ValueError(
                "Item incompleto na tabela do DANFE antes da próxima linha; "
                "nenhuma importação parcial foi aceita."
            )
        if not linha_atual:
            if not inicio_item:
                continue
            linha_atual = linha
        else:
            linha_atual += " " + linha
        if marcador_item.search(linha_atual):
            linhas_itens.append(linha_atual)
            linha_atual = ""

    if linha_atual:
        raise ValueError(
            "Último item da tabela do DANFE está incompleto ou tem layout "
            "não reconhecido; nenhuma importação parcial foi aceita."
        )
    if not linhas_itens:
        raise ValueError(
            "Nenhum item foi reconhecido na tabela do DANFE ADF; "
            "confira o layout e a unidade de medida."
        )

    itens = []
    for indice, linha in enumerate(linhas_itens, start=1):
        match = marcador_item.search(linha)
        prefixo = linha[:match.start()].split()
        if len(prefixo) < 2:
            raise ValueError(f"Descrição/código ausente no item {indice} da NF.")
        codigo, descricao_tokens = prefixo[0], prefixo[1:]
        unidade = match.group("unidade").upper()
        if unidade != "KG":
            raise ValueError(
                f"Unidade {unidade!r} não suportada no item {indice}; "
                "a leitura automática exige KG."
            )
        descricao = " ".join(descricao_tokens)
        itens.append(ItemNotaFiscal(
            numero=str(indice),
            codigo=codigo,
            descricao=descricao,
            produto=_normalizar_produto(descricao),
            largura=_extrair_largura(descricao),
            peso=_numero_decimal_br(match.group("peso")),
        ))

    return NotaFiscal(
        numero=_extrair_numero_nota(texto),
        romaneio=_extrair_referencia_nf(texto),
        itens=itens,
    )


def ler_numero_romaneio(caminho):
    """Lê a referência numérica impressa em um romaneio ou na informação da NF."""
    texto = _normalizar(_extrair_texto(caminho))
    padroes = (
        r"\bnumero\s*:\s*(\d+)\b",
        r"\bromaneio\s+faturado\s+n(?:[º°.]|o)?\s*(\d+)\b",
    )
    for padrao in padroes:
        match = re.search(padrao, texto, re.I)
        if match:
            return match.group(1)
    return None


def _digitos_referencia(valor):
    return re.sub(r"\D", "", str(valor or ""))


def conferir_nota(nota, bobinas, numero_romaneio=None):
    """Sugere associações one-to-one somente por produto e peso exatos."""
    resultado = ConferenciaNota()
    grupos = agrupar_bobinas(bobinas)

    if nota.romaneio and numero_romaneio:
        nf_ref = _digitos_referencia(nota.romaneio)
        rom_ref = _digitos_referencia(numero_romaneio)
        resultado.referencia_compativel = nf_ref == rom_ref
        if not resultado.referencia_compativel:
            resultado.alertas.append(
                f"Referência incompatível: NF vinculada ao romaneio "
                f"{nota.romaneio}, mas o romaneio carregado é "
                f"{numero_romaneio}; associações bloqueadas."
            )
            resultado.pendencias.extend(
                f"Grupo {grupo!r} não associado devido à referência incompatível."
                for grupo in grupos
            )
            return resultado
    elif not nota.romaneio or not numero_romaneio:
        resultado.alertas.append(
            "Não foi possível validar a referência NF/romaneio; "
            "as associações permanecem sugestões para revisão."
        )

    resumo_grupos = []
    for nome, bobinas_grupo in grupos.items():
        produtos = {_normalizar_produto(b.produto) for b in bobinas_grupo}
        larguras = {b.formato for b in bobinas_grupo}
        resumo_grupos.append({
            "nome": nome,
            "produto": next(iter(produtos)) if len(produtos) == 1 else "",
            "peso": sum(b.peso for b in bobinas_grupo),
            "larguras": larguras,
        })

    candidatos_por_grupo = {}
    grupos_por_item = {indice: [] for indice in range(len(nota.itens))}
    for indice_grupo, grupo in enumerate(resumo_grupos):
        candidatos = [
            indice_item for indice_item, item in enumerate(nota.itens)
            if grupo["produto"]
            and grupo["produto"] == item.produto
            and Decimal(grupo["peso"]) == item.peso
        ]
        candidatos_por_grupo[indice_grupo] = candidatos
        for indice_item in candidatos:
            grupos_por_item[indice_item].append(indice_grupo)

    grupos_associados = set()
    itens_associados = set()
    for indice_grupo, candidatos in candidatos_por_grupo.items():
        grupo = resumo_grupos[indice_grupo]
        if len(candidatos) == 1 and len(grupos_por_item[candidatos[0]]) == 1:
            indice_item = candidatos[0]
            item = nota.itens[indice_item]
            resultado.associacoes[grupo["nome"]] = item
            grupos_associados.add(indice_grupo)
            itens_associados.add(indice_item)
            if item.largura is not None and grupo["larguras"] != {item.largura}:
                resultado.alertas.append(
                    f"Grupo {grupo['nome']!r} foi associado ao item NF "
                    f"{item.numero} pelo peso, mas as larguras diferem "
                    f"(romaneio: {sorted(grupo['larguras'])}; NF: {item.largura} mm). "
                    "Revise antes de usar a associação."
                )
        elif candidatos:
            item_nums = [nota.itens[i].numero for i in candidatos]
            resultado.pendencias.append(
                f"Grupo {grupo['nome']!r} tem correspondência por peso não única "
                f"(itens NF candidatos: {item_nums or 'duplicados entre grupos'}); "
                "nenhuma associação automática foi feita."
            )
        else:
            resultado.pendencias.append(
                f"Grupo {grupo['nome']!r} sem item NF de mesmo produto e peso exato."
            )

    for indice_item, item in enumerate(nota.itens):
        if indice_item not in itens_associados:
            resultado.pendencias.append(
                f"Item NF {item.numero} ({item.produto}, {item.peso} kg) "
                "não associado a um único grupo."
            )
    return resultado
