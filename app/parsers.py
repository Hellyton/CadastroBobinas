import re

import pdfplumber

from app.modelos import Bobina


def _extrair_texto(caminho):
    """Extração simples de texto (todas as páginas concatenadas)."""

    texto = ""

    with pdfplumber.open(caminho) as pdf:
        for pagina in pdf.pages:
            texto += (pagina.extract_text() or "") + "\n"

    return texto


def extrair_bobinas_adf(caminho):
    """Parser do romaneio da ADF - Empresas Reunidas.
    Retorna (bobinas, ajuste_peso) - ADF não tem ajustes, ajuste_peso=0."""

    texto = _extrair_texto(caminho)
    bobinas = []

    padrao = re.compile(
        r"^(\d+)\s+"
        r"\d+\s+"
        r"(.+?)\s+"
        r"\S+\s+"  # Código do cliente; produto-base vem da descrição.
        r"(\d+)\s+"
        r"(\d+)\s+"
        r"(\d+)\s+"
        r"[\d\.]+\s+\S+\s+"  # Qtd ML seguido da unidade (KG, N/A, etc.)
        r"([\d\.]+)"
        r"(?:\s+[\d\.]+)*\s*$"
    )

    for linha in texto.split("\n"):
        linha = linha.strip()
        if not linha:
            continue

        resultado = padrao.match(linha)
        if not resultado:
            continue

        try:
            numero = resultado.group(1)
            descricao_original = resultado.group(2).strip()
            produto = descricao_original.split()[0]
            gramatura = int(resultado.group(3))
            formato = int(resultado.group(4))
            diametro = int(resultado.group(5))
            peso = int(resultado.group(6).replace(".", ""))
        except (ValueError, AttributeError):
            continue

        bobinas.append(
            Bobina(numero, produto, gramatura, formato, diametro, peso,
                   descricao_original=descricao_original)
        )

    return bobinas, 0

# Letra do campo "Papel" (ex: M090) -> nome do produto
MAPA_PRODUTO_HP = {
    "M": "MIOLO",
}


def extrair_bobinas_hp(caminho):
    """Parser do romaneio da HP (Indústria de Papelão).
    Retorna (bobinas, ajuste_peso) - HP não tem ajustes, ajuste_peso=0."""

    texto = _extrair_texto(caminho)

    bobinas = []

    linhas = texto.split("\n")

    padrao = (
        r"^([A-Z])(\d{3})\s+"   # Papel: letra (produto) + gramatura
        r"\d+\s+"               # Pedido
        r"\d+\s+"               # Ped. Cliente
        r"(\d+)\s+"             # Cod. Bobinas
        r"([\d\.]+)\s+"         # Largura -> Formato
        r"([\d\.]+)\s+"         # Diâmetro
        r"\d+\s+"               # Tub. (não usado)
        r"([\d\.]+)$"           # Peso
    )

    for linha in linhas:

        linha = linha.strip()

        if not linha:
            continue

        resultado = re.search(padrao, linha)

        if resultado:

            letra = resultado.group(1)

            gramatura = int(resultado.group(2))

            numero = resultado.group(3)  # Cod. Bobinas, mantém como veio

            formato = int(resultado.group(4).replace(".", ""))

            diametro = int(resultado.group(5).replace(".", ""))

            peso = int(resultado.group(6).replace(".", ""))

            produto = MAPA_PRODUTO_HP.get(letra, letra)

            bobinas.append(

                Bobina(
                    numero,
                    produto,
                    gramatura,
                    formato,
                    diametro,
                    peso
                )

            )

    return bobinas, 0


# Prefixo de letras do código do produto Novakraft -> nome do produto
MAPA_PRODUTO_NOVAKRAFT = {
    "NEBX": "MIOLO",
}

# Código do produto Novakraft (ex: NEBX09012001130):
# letras + 3 dígitos (gramatura) + 4 dígitos (diâmetro) + 4 dígitos (formato)
PADRAO_PRODUTO_NOVAKRAFT = re.compile(r"^([A-Z]+)(\d{3})(\d{4})(\d{4})$")

# Procura, em qualquer lugar do texto, ou um código de produto, ou uma
# linha de dados de bobina (Arm, Lote, Peso, Quant., Quebras, Transf.,
# Data, Turno). Não depende de quebra de linha entre uma bobina e outra -
# em romaneios escaneados o pdfplumber às vezes perde essas quebras e
# gruda tudo numa linha só. O código do produto usa \d+ (sem tamanho
# fixo) porque, em alguns PDFs, o primeiro código de cada página vem com
# cada caractere duplicado (bug de renderização de negrito do PDF de
# origem) - a desduplicação é tratada em _desduplicar_codigo.
TOKEN_NOVAKRAFT = re.compile(
    r"(?P<produto>[A-Z]{2,16}\d+)"
    r"|"
    r"(?P<arm>\d{2})\s+"
    r"(?P<lote>[A-Z0-9]+)\s+"
    r"(?P<peso>[\d\.,]+)\s+"
    r"(?P<quant>\d+)\s+"
    r"(?P<quebras>\d+)\s+"
    r"(?:SIM|N[ÃA]O)\s+"
    r"\d{2}/\d{2}/\d{4}\s+"
    r"\S+"
)


def _desduplicar_codigo(codigo):
    """
    Alguns PDFs renderizam o primeiro código de produto de cada página com
    cada caractere duplicado (ex: 'NNEEBBXX...' em vez de 'NEBX...'),
    aparentemente por causa de negrito "falso" no PDF de origem. Se o
    código bate nesse padrão (todo par de caracteres igual), devolve a
    versão desduplicada. Caso contrário, devolve None.
    """

    if len(codigo) % 2 != 0:
        return None

    duplicado = all(
        codigo[i] == codigo[i + 1] for i in range(0, len(codigo), 2)
    )

    if not duplicado:
        return None

    return codigo[0::2]


def _interpretar_codigo_produto(codigo_bruto):
    """
    Tenta casar o código de produto com o padrão esperado. Se não bater
    de primeira, tenta desduplicar (ver _desduplicar_codigo) e tenta de
    novo. Retorna o resultado do regex (ou None se não reconhecer de
    jeito nenhum).
    """

    resultado = PADRAO_PRODUTO_NOVAKRAFT.match(codigo_bruto)

    if resultado:
        return resultado

    codigo_normalizado = _desduplicar_codigo(codigo_bruto)

    if codigo_normalizado:
        return PADRAO_PRODUTO_NOVAKRAFT.match(codigo_normalizado)

    return None


def extrair_bobinas_novakraft(caminho):
    """Parser da Novakraft. Despacha entre os dois layouts que compartilham
    o mesmo cabeçalho "SIGA /FATR01" (por isso caem no mesmo fornecedor em
    detectar_fornecedor):
    - romaneio "Relacao de Estoque/Pedido de Venda" -> _extrair_bobinas_novakraft_romaneio
    - "Laudo Técnico da Qualidade" -> _extrair_bobinas_novakraft_laudo
    Retorna (bobinas, ajuste_peso) - Novakraft não tem ajustes, ajuste_peso=0."""

    texto = _extrair_texto(caminho)

    if "Laudo Técnico da Qualidade" in texto:
        return _extrair_bobinas_novakraft_laudo(texto)

    return _extrair_bobinas_novakraft_romaneio(texto)


def _extrair_bobinas_novakraft_romaneio(texto):
    """Parser do romaneio da Novakraft ("Relacao de Estoque/Pedido de Venda")."""

    bobinas = []

    produto_atual = None
    gramatura_atual = None
    diametro_atual = None
    formato_atual = None

    for resultado in TOKEN_NOVAKRAFT.finditer(texto):

        codigo_produto = resultado.group("produto")

        if codigo_produto:

            produto_resultado = _interpretar_codigo_produto(codigo_produto)

            if produto_resultado:

                letras = produto_resultado.group(1)

                produto_atual = MAPA_PRODUTO_NOVAKRAFT.get(letras, letras)
                gramatura_atual = int(produto_resultado.group(2))
                diametro_atual = int(produto_resultado.group(3))
                formato_atual = int(produto_resultado.group(4))

            else:
                # Código de produto não reconhecido (nem direto, nem
                # desduplicado). Não dá pra confiar no produto anterior
                # pra essas próximas bobinas, então zera - as linhas
                # seguintes serão puladas até aparecer um código válido.
                produto_atual = None

            continue

        if produto_atual is None:
            # Linha de dados apareceu antes de qualquer produto válido
            # ser identificado - não dá pra saber gramatura/diâmetro/
            # formato, então pula. Isso reduz o total de bobinas lidas,
            # o que a conferência de saldo (ao final do cadastro) deve
            # acusar como divergência - sinal pra conferir manualmente.
            continue

        numero = resultado.group("lote")

        peso = int(round(float(resultado.group("peso").replace(",", "."))))

        bobinas.append(

            Bobina(
                numero,
                produto_atual,
                gramatura_atual,
                formato_atual,
                diametro_atual,
                peso
            )

        )

    return bobinas, 0


# "Laudo Técnico da Qualidade" da Novakraft - layout diferente do romaneio
# de estoque: uma linha por bobina com Arm/Lote/Peso/Qtd seguidos de
# colunas de resultado de ensaio (Gramatura medida, Rasgo Lg/Tr, Tração
# Lg/Tr, Cobb, Mullen, Umidade, RCT, Porosidade). Cada valor de ensaio
# pode vir "-" (não medido) ou com um "*" na frente (fora de
# especificação) - ambos os casos são aceitos e ignorados, já que o
# cadastro de bobinas só precisa do lote e do peso; gramatura/formato/
# diâmetro nominais continuam vindo do código de produto (ex:
# NEBX08012002400), igual no romaneio.
PADRAO_LINHA_LAUDO_NOVAKRAFT = re.compile(
    r"^(?P<arm>\d{2})\s+"
    r"(?P<lote>[A-Z0-9]+)\s+"
    r"(?P<peso>[\d\.,]+)\s+"
    r"(?P<qtd>\d+)\s+"
    r"(?:\*?[\d\.]+|-)"                       # Gramat (obrigatório)
    r"(?:\s+(?:\*?[\d\.]+|-)){0,9}"           # demais colunas de ensaio (0 a 9), quantidade variável
    r"\s*$"
)


def _extrair_bobinas_novakraft_laudo(texto):
    """Parser do "Laudo Técnico da Qualidade" da Novakraft."""

    bobinas = []

    produto_atual = None
    gramatura_atual = None
    diametro_atual = None
    formato_atual = None

    for linha in texto.split("\n"):

        linha = linha.strip()

        if not linha:
            continue

        # Linha só com o código de produto (ex: NEBX08012002400) - vale
        # pras bobinas seguintes até aparecer um código novo.
        produto_resultado = _interpretar_codigo_produto(linha)

        if produto_resultado:

            letras = produto_resultado.group(1)

            produto_atual = MAPA_PRODUTO_NOVAKRAFT.get(letras, letras)
            gramatura_atual = int(produto_resultado.group(2))
            diametro_atual = int(produto_resultado.group(3))
            formato_atual = int(produto_resultado.group(4))

            continue

        resultado = PADRAO_LINHA_LAUDO_NOVAKRAFT.match(linha)

        if not resultado:
            continue

        if produto_atual is None:
            # Linha de dados apareceu antes de qualquer código de produto
            # válido - não dá pra saber gramatura/diâmetro/formato, pula.
            continue

        numero = resultado.group("lote")

        peso = int(round(float(resultado.group("peso").replace(",", ""))))

        bobinas.append(

            Bobina(
                numero,
                produto_atual,
                gramatura_atual,
                formato_atual,
                diametro_atual,
                peso
            )

        )

    return bobinas, 0


# ---------------------------------------------------------------------
# Cocelpa - "ROMANEIO E CONTROLE DE EMBARQUE"
#
# Esse layout tem DUAS colunas de bobinas lado a lado na mesma página.
# O texto puro (extract_text) não deixa claro qual token pertence à
# coluna esquerda ou direita quando uma linha só tem bobina de um dos
# lados - por isso usamos extract_words(), que traz a posição (x0) de
# cada palavra, pra separar as duas colunas com segurança.
# ---------------------------------------------------------------------

PADRAO_FABRICACAO = re.compile(r"^\d{10}$")


def _agrupar_palavras_por_linha(palavras, tolerancia=2.5):
    """Agrupa palavras da mesma linha visual (coordenada 'top' próxima)."""

    palavras = sorted(palavras, key=lambda w: (w["top"], w["x0"]))

    linhas = []
    atual = []
    top_atual = None

    for palavra in palavras:

        if top_atual is None or abs(palavra["top"] - top_atual) <= tolerancia:
            atual.append(palavra)
            top_atual = top_atual if top_atual is not None else palavra["top"]
        else:
            linhas.append(atual)
            atual = [palavra]
            top_atual = palavra["top"]

    if atual:
        linhas.append(atual)

    return linhas


def _tentar_valor_ajuste(tokens):
    """
    Algumas linhas trazem só um valor solto (ex: '-0,110'), sem número de
    fabricação - parecem ser ajustes/descontos do lote (ex: quebra),
    já contabilizados no peso líquido total oficial do romaneio. Se
    reconhecer esse padrão, devolve o valor em kg (pode ser negativo);
    caso contrário, devolve None (linha realmente não reconhecida).
    """

    if len(tokens) != 1:
        return None

    texto = tokens[0]

    if not re.match(r"^-?[\d,]+$", texto):
        return None

    try:
        valor_toneladas = float(texto.replace(",", "."))
    except ValueError:
        return None

    return int(round(valor_toneladas * 1000))


def _processar_coluna_cocelpa(linhas_tokens):
    """
    Processa uma coluna (esquerda ou direita) já separada em linhas de
    tokens. Formato/Gramatura/Diâmetro só aparecem na primeira linha de
    cada grupo e valem (carry-forward) pras linhas seguintes, até
    aparecer um novo grupo. O marcador "KE" (Kraft Ecológico) indica que
    o grupo INTEIRO é de um produto diferente (KRAFT ECOLOGICO em vez de
    MIOLO) - mas como ele só aparece na 2ª linha do grupo (não na 1ª,
    onde vem o Form./Gram./Diâm.), primeiro juntamos todas as linhas de
    cada grupo pra só depois decidir o produto do grupo inteiro (senão a
    1ª bobina do grupo ficaria com o produto errado).

    Retorna (bobinas, ajuste_peso) - ajuste_peso é a soma (em kg) de
    linhas soltas de ajuste/desconto (ver _tentar_valor_ajuste).
    """

    grupos = []
    grupo_atual = None
    ajuste_peso = 0

    for tokens in linhas_tokens:

        if not tokens:
            continue

        fabricacao = tokens[0]

        if not PADRAO_FABRICACAO.match(fabricacao):

            ajuste = _tentar_valor_ajuste(tokens)

            if ajuste is not None:
                ajuste_peso += ajuste

            # Se não for nem número de fabricação válido nem um ajuste
            # reconhecível, ignora a linha silenciosamente.
            continue

        if len(tokens) < 2:
            continue

        try:
            peso_toneladas = float(tokens[1].replace(",", "."))
        except ValueError:
            continue

        peso = int(round(peso_toneladas * 1000))

        resto = tokens[2:]

        if len(resto) >= 3:

            try:
                formato = int(resto[0].replace(".", ""))
                gramatura = int(resto[1])
                diametro = int(resto[2].replace(".", ""))

                grupo_atual = {
                    "formato": formato,
                    "gramatura": gramatura,
                    "diametro": diametro,
                    "produto": "MIOLO",
                    "linhas": [],
                }
                grupos.append(grupo_atual)

            except ValueError:
                pass

        elif resto == ["KE"] and grupo_atual is not None:
            grupo_atual["produto"] = "KRAFT ECOLOGICO"

        if grupo_atual is None:
            # Linha de dados apareceu antes de qualquer grupo válido -
            # não dá pra saber os valores, pula.
            continue

        grupo_atual["linhas"].append((fabricacao, peso))

    bobinas = []

    for grupo in grupos:

        for fabricacao, peso in grupo["linhas"]:

            bobinas.append(

                Bobina(
                    fabricacao,
                    grupo["produto"],
                    grupo["gramatura"],
                    grupo["formato"],
                    grupo["diametro"],
                    peso
                )

            )

    return bobinas, ajuste_peso


def extrair_bobinas_cocelpa(caminho):
    """
    Parser do romaneio da Cocelpa ("ROMANEIO E CONTROLE DE EMBARQUE").
    Retorna (bobinas, ajuste_peso) - ver _processar_coluna_cocelpa.
    """

    bobinas = []
    ajuste_peso = 0

    with pdfplumber.open(caminho) as pdf:

        for pagina in pdf.pages:

            meio = pagina.width / 2

            palavras = pagina.extract_words()

            linhas = _agrupar_palavras_por_linha(palavras)

            tokens_esquerda = []
            tokens_direita = []

            for linha in linhas:

                esquerda = sorted(
                    (w for w in linha if w["x0"] < meio),
                    key=lambda w: w["x0"]
                )
                direita = sorted(
                    (w for w in linha if w["x0"] >= meio),
                    key=lambda w: w["x0"]
                )

                if esquerda:
                    tokens_esquerda.append([w["text"] for w in esquerda])

                if direita:
                    tokens_direita.append([w["text"] for w in direita])

            bobinas_esq, ajuste_esq = _processar_coluna_cocelpa(tokens_esquerda)
            bobinas_dir, ajuste_dir = _processar_coluna_cocelpa(tokens_direita)

            bobinas += bobinas_esq + bobinas_dir
            ajuste_peso += ajuste_esq + ajuste_dir

    return bobinas, ajuste_peso


# Cada fornecedor tem uma função extrair_bobinas(caminho) -> list[Bobina]
FORNECEDORES = {
    "ADF": extrair_bobinas_adf,
    "HP": extrair_bobinas_hp,
    "Novakraft": extrair_bobinas_novakraft,
    "Cocelpa": extrair_bobinas_cocelpa,
}


def detectar_fornecedor(texto):
    """
    Tenta identificar o fornecedor pelo layout/rótulos do romaneio.
    Usa marcadores estruturais (não o nome do cliente), já que o nome
    do cliente ("ADF") pode aparecer dentro do romaneio de outros
    fornecedores (ex: HP, Novakraft e Cocelpa entregam pra ADF).
    Retorna a chave em FORNECEDORES, ou None se não reconhecer.
    """

    if "Transportadora:" in texto or "Nota Fiscal:" in texto:
        return "ADF"

    if "Cod. Bobinas" in texto or "ROMANEIO N" in texto:
        return "HP"

    if "Relacao de Estoque" in texto or "SIGA /FATR01" in texto:
        return "Novakraft"

    if "ROMANEIO E CONTROLE DE EMBARQUE" in texto or "Cocelpa" in texto:
        return "Cocelpa"

    return None
