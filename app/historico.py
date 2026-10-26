import json
import os
import tempfile


CAMINHO_HISTORICO = "historico_cadastro.json"


class HistoricoInvalido(ValueError):
    """O arquivo existe, mas não contém o formato esperado pelo aplicativo."""


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


def _ler_dados(caminho=None):
    caminho = caminho or CAMINHO_HISTORICO
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except FileNotFoundError:
        return set(), {}
    except (json.JSONDecodeError, OSError) as erro:
        raise HistoricoInvalido(f"Não foi possível ler o histórico: {erro}") from erro
    if not isinstance(dados, dict) or not isinstance(dados.get("cadastradas"), list):
        raise HistoricoInvalido("O histórico não possui uma lista 'cadastradas' válida.")
    chaves = dados["cadastradas"]
    if any(not isinstance(chave, str) or not chave for chave in chaves):
        raise HistoricoInvalido("O histórico contém uma chave vazia ou inválida.")
    conjunto = set(chaves)
    romaneios = dados.get("romaneios", {})
    if not isinstance(romaneios, dict):
        raise HistoricoInvalido("O histórico possui um mapa 'romaneios' inválido.")
    if any(not isinstance(chave, str) or not chave or chave not in conjunto
           or not isinstance(numero, str) or not numero or numero != numero.strip()
           for chave, numero in romaneios.items()):
        raise HistoricoInvalido("O histórico contém metadados de romaneio inválidos.")
    return conjunto, dict(romaneios)


def _ler_chaves(caminho=None):
    return _ler_dados(caminho)[0]


def carregar_historico():
    """Retorna as chaves registradas; mantém o contrato histórico de retornar set."""
    try:
        return _ler_chaves()
    except HistoricoInvalido:
        # Compatibilidade para o filtro do cadastro; operações de escrita usam
        # _ler_chaves diretamente para nunca substituir um arquivo inválido.
        return set()


def _salvar_dados(chaves, romaneios, caminho=None):
    caminho = os.path.abspath(caminho or CAMINHO_HISTORICO)
    pasta = os.path.dirname(caminho) or os.curdir
    temporario = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=pasta,
                                         delete=False, suffix=".tmp") as arquivo:
            temporario = arquivo.name
            dados = {"cadastradas": sorted(chaves)}
            if romaneios:
                dados["romaneios"] = dict(sorted(romaneios.items()))
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, caminho)
    except OSError as erro:
        raise HistoricoInvalido(f"Não foi possível salvar o histórico: {erro}") from erro
    finally:
        if temporario and os.path.exists(temporario):
            try:
                os.remove(temporario)
            except OSError:
                pass


def listar_registros(caminho=None):
    """Lista as chaves sem inventar atributos que não são guardados no JSON."""
    registros = []
    chaves, romaneios = _ler_dados(caminho)
    for chave in sorted(chaves):
        if "|" in chave:
            fornecedor, numero = chave.split("|", 1)
        else:
            fornecedor, numero = "", chave
        registros.append({"chave": chave, "fornecedor": fornecedor,
                          "numero": numero, "romaneio": romaneios.get(chave, "")})
    return registros


def adicionar_cadastrada(numero, fornecedor, caminho=None, romaneio=None):
    """Marca manualmente uma chave local; não interage com o EGS."""
    fornecedor = str(fornecedor).strip() if fornecedor is not None else ""
    numero = str(numero).strip()
    if not fornecedor or not numero:
        raise ValueError("Informe fornecedor e número da bobina.")
    if "|" in fornecedor:
        raise ValueError("O fornecedor não pode conter '|'.")
    chaves, romaneios = _ler_dados(caminho)
    nova = _chave(str(numero), fornecedor)
    if bobina_ja_cadastrada(chaves, str(numero), fornecedor):
        raise ValueError("Esta bobina já está no histórico local.")
    chaves.add(nova)
    romaneio = str(romaneio).strip() if romaneio is not None else ""
    if romaneio:
        romaneios[nova] = romaneio
    _salvar_dados(chaves, romaneios, caminho)


def editar_registro(chave_atual, numero, fornecedor, caminho=None, romaneio=None):
    """Edita a identidade local e o romaneio; None preserva o romaneio atual."""
    fornecedor = str(fornecedor).strip() if fornecedor is not None else ""
    numero = str(numero).strip()
    if not fornecedor or not numero:
        raise ValueError("Informe fornecedor e número da bobina.")
    if "|" in fornecedor:
        raise ValueError("O fornecedor não pode conter '|'.")
    chaves, romaneios = _ler_dados(caminho)
    if chave_atual not in chaves:
        raise ValueError("O registro selecionado não existe mais no histórico.")
    nova = _chave(str(numero), fornecedor)
    if nova != chave_atual and bobina_ja_cadastrada(chaves - {chave_atual}, str(numero), fornecedor):
        raise ValueError("Já existe um registro que representa esta bobina.")
    chaves.remove(chave_atual)
    chaves.add(nova)
    romaneio_existente = romaneios.pop(chave_atual, None)
    if romaneio is None:
        romaneio_novo = romaneio_existente
    else:
        romaneio_novo = str(romaneio).strip()
    if romaneio_novo:
        romaneios[nova] = romaneio_novo
    _salvar_dados(chaves, romaneios, caminho)


def excluir_registro(chave, caminho=None):
    chaves, romaneios = _ler_dados(caminho)
    if chave not in chaves:
        raise ValueError("O registro selecionado não existe mais no histórico.")
    chaves.remove(chave)
    romaneios.pop(chave, None)
    _salvar_dados(chaves, romaneios, caminho)


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


def marcar_cadastrada(numero, fornecedor=None, romaneio=None):
    """Adiciona uma bobina ao histórico (usando fornecedor+número como
    chave, quando o fornecedor for informado) e salva no arquivo
    imediatamente."""

    cadastradas, romaneios = _ler_dados()
    cadastradas.add(_chave(numero, fornecedor))
    chave = _chave(numero, fornecedor)
    romaneio = str(romaneio).strip() if romaneio is not None else ""
    if romaneio:
        romaneios[chave] = romaneio
    _salvar_dados(cadastradas, romaneios)
