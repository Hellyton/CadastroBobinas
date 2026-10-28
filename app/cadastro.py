from app.navegador import Navegador, SalvamentoNaoConfirmado
from app.agrupamento import agrupar_bobinas, produtos_com_variantes
import math
from app.logger import logger
from app.controle import ControleCadastro, CadastroInterrompido
from app.historico import (
    carregar_historico,
    marcar_cadastrada,
    bobina_ja_cadastrada,
)
import config

class CadastroBobinas:

    @staticmethod
    def _escolher_proximo_produto(grupos):
        """
        Mostra os produtos ainda pendentes (com quantidade de bobinas e
        peso) e deixa o usuário escolher qual classificar agora. Chamado
        a cada troca de produto, não só uma vez no início - assim a
        ordem pode ser decidida aos poucos, conforme o cadastro avança.

        Se sobrar só um produto, retorna ele direto sem perguntar nada.
        ENTER mantém a ordem de aparição no romaneio (primeiro da lista).
        """

        produtos = list(grupos.keys())

        if len(produtos) == 1:
            return produtos[0]

        print("\nProdutos ainda pendentes:")
        for indice, produto in enumerate(produtos, start=1):
            lista_bobinas = grupos[produto]
            peso_total = sum(bobina.peso for bobina in lista_bobinas)
            print(
                f"  {indice}. {produto} "
                f"({len(lista_bobinas)} bobina(s), {peso_total:.0f} kg)"
            )

        while True:
            escolha = input(
                f"\nQual produto deseja classificar agora? "
                f"[1-{len(produtos)}, ENTER para '{produtos[0]}']: "
            ).strip()

            if not escolha:
                return produtos[0]

            if escolha.isdigit() and 1 <= int(escolha) <= len(produtos):
                return produtos[int(escolha) - 1]

            print("Opção inválida, tente novamente.")

    def iniciar(self, bobinas, ajuste_peso=0, url=None, usar_historico=True,
                controle=None, evento=None, solicitar=None,
                rotulos_grupos=None, numero_romaneio=None, grupo_unico=None,
                manter_navegador=False):
        # O navegador nasce, trabalha e fecha na mesma thread. Com
        # manter_navegador, quem chamou fecha `self.navegador` nessa thread.
        self.controle = controle or ControleCadastro()
        self.evento = evento or (lambda tipo, **dados: None)
        self.solicitar = solicitar
        self.sucessos = []
        self.falhas = []
        self.total = len(bobinas)
        self.ignoradas = 0
        self.motivo_parada = ""
        self.numero_romaneio = str(numero_romaneio).strip() if numero_romaneio is not None else ""
        navegador = self.navegador = Navegador()
        try:
            self.controle.verificar()
            return self._executar(navegador, bobinas, ajuste_peso, url,
                                  usar_historico, rotulos_grupos, grupo_unico)
        except CadastroInterrompido:
            return self._resultado(interrompido=True)
        finally:
            if not manter_navegador:
                navegador.fechar()

    def _resultado(self, interrompido=False):
        return dict(sucessos=len(self.sucessos), falhas=len(self.falhas),
                    total=self.total, ignoradas=self.ignoradas,
                    interrompido=interrompido, motivo_parada=self.motivo_parada)

    def _parar_por_saldo(self, motivo):
        self.motivo_parada = motivo
        logger.warning(motivo)
        self.evento("status", texto=motivo)
        print(motivo)
        return self._resultado()

    def _confirmar(self, mensagem, opcoes=None):
        self.controle.verificar()
        if self.solicitar:
            resposta = self.solicitar(mensagem, opcoes)
        else:
            resposta = input(mensagem)
        self.controle.verificar()
        return resposta

    def _executar(self, navegador, bobinas, ajuste_peso, url, usar_historico,
                  rotulos_grupos=None, grupo_unico=None):

        self.evento("status", texto="Abrindo o sistema e fazendo login...")
        navegador.abrir()
        self.controle.verificar()
        navegador.acessar(url or config.URL)
        self.controle.verificar()
        navegador.fazer_login()

        print("Sistema aberto.")
        self._confirmar(
            "abra Classificação de Bobinas, "
            "selecione a nota e clique em Classificar.\n"
            "Deixe a tela na LISTA de bobinas (não no modal).\n"
            "Pressione ENTER aqui para iniciar o cadastro automático..."
        )

        # A identidade por descrição precisa vir do lote completo; calcular
        # variantes após o filtro de histórico poderia mudar os grupos.
        variantes_produtos = produtos_com_variantes(bobinas)
        ja_cadastradas = carregar_historico() if usar_historico else set()

        saldo_inicial = navegador.ler_saldo_classificar()

        pendentes = []

        for bobina in bobinas:

            if bobina_ja_cadastrada(ja_cadastradas, bobina.numero, bobina.fornecedor):
                print(
                    f"Bobina {bobina.numero} já foi cadastrada "
                    "anteriormente (histórico). Pulando."
                )
                logger.info(
                    f"Bobina {bobina.numero} já estava no histórico, "
                    "pulada."
                )
                continue

            pendentes.append(bobina)

        # Agrupa por produto e separa pontas por largura, mantendo a ordem
        # de aparição; cada grupo pode corresponder a uma aba/nota diferente.
        # NF de item único define a divisão: todo o lote vai para uma etapa.
        rotulos_grupos = rotulos_grupos or {}
        grupos = {}
        if grupo_unico:
            if pendentes:
                grupos[grupo_unico] = pendentes
        else:
            for chave, lista in agrupar_bobinas(pendentes, variantes_produtos).items():
                rotulo = rotulos_grupos.get(chave, chave)
                if rotulo in grupos:
                    raise ValueError(f"Rótulo de grupo duplicado: {rotulo!r}.")
                grupos[rotulo] = lista

        total = len(pendentes)
        self.total = total
        self.ignoradas = len(bobinas) - total
        falhas = self.falhas
        sucessos = self.sucessos
        cadastradas = 0
        self.evento("progresso", concluidas=0, total=total,
                    texto=f"{total} bobinas pendentes; {self.ignoradas} já no histórico.")
        total_produtos_pendentes = len(grupos)

        logger.info(
            f"Iniciando cadastro de {total} bobinas pendentes em "
            f"{total_produtos_pendentes} produto(s): {list(grupos.keys())}."
        )

        # Em vez de definir a ordem toda de uma vez no início, escolhe um
        # produto por vez, a cada troca - assim dá pra decidir aos poucos
        # qual classificar em seguida, sem precisar planejar a ordem
        # completa antes de começar.
        while grupos:

            self.controle.verificar()
            if self.solicitar and len(grupos) > 1:
                opcoes = list(grupos)
                resumo = "\n".join(
                    f"{p}: {len(bs)} bobinas, {sum(b.peso for b in bs)} kg"
                    for p, bs in grupos.items()
                )
                produto = self._confirmar(
                    "Escolha o próximo produto:\n" + resumo, opcoes)
                if produto not in grupos:
                    raise ValueError("Produto selecionado inválido.")
            else:
                produto = self._escolher_proximo_produto(grupos)
            lista_bobinas = grupos.pop(produto)

            if total_produtos_pendentes > 1:

                peso_total = sum(bobina.peso for bobina in lista_bobinas)

                self._confirmar(
                    f"\nPróximo produto: '{produto}'\n"
                    f"Bobinas: {len(lista_bobinas)}\n"
                    f"Peso total: {peso_total:.0f} kg\n\n"
                    "Confira/selecione o registro (nota) correto para esse "
                    "produto na tela de Classificação de Bobinas.\n"
                    "Pressione ENTER quando estiver pronto para continuar..."
                )

            for bobina in lista_bobinas:

                # Não interrompe um salvamento em andamento: termina a
                # bobina atual e atende pausa/interrupção antes da próxima.
                self.controle.verificar()
                saldo = navegador.ler_saldo_classificar()
                if saldo is None or not math.isfinite(saldo):
                    return self._parar_por_saldo(
                        f"Não foi possível conferir o saldo da nota para a bobina "
                        f"{bobina.numero}. Cadastro parado; confira o EGS.")
                if saldo <= 0 or bobina.peso > saldo or bobina.peso <= 0:
                    return self._parar_por_saldo(
                        f"Cadastro parado antes da bobina {bobina.numero}: "
                        f"saldo da nota {saldo:g} kg, peso da bobina {bobina.peso} kg. "
                        "Confira o saldo e a nota no EGS. As restantes estão pendentes.")
                cadastradas += 1
                self.evento("status", texto=(
                    f"Cadastrando bobina {cadastradas} de {total} "
                    f"— nº {bobina.numero} ({produto})"))

                print(
                    f"Cadastrando bobina {cadastradas}/{total} "
                    f"(nº {bobina.numero}, produto {produto})..."
                )

                try:
                    navegador.clicar_novo()
                    navegador.preencher_bobina(bobina)
                    navegador.salvar(peso=bobina.peso, saldo_antes=saldo)

                    if usar_historico:
                        if self.numero_romaneio:
                            marcar_cadastrada(bobina.numero, bobina.fornecedor,
                                             romaneio=self.numero_romaneio)
                        else:
                            marcar_cadastrada(bobina.numero, bobina.fornecedor)

                    sucessos.append(bobina)

                    logger.info(
                        f"Bobina {bobina.numero} ({produto}) cadastrada "
                        "com sucesso."
                    )

                except SalvamentoNaoConfirmado as erro:
                    falhas.append(bobina)
                    return self._parar_por_saldo(
                        f"Bobina {bobina.numero}: {erro} Cadastro parado para conferência.")

                except Exception as erro:

                    logger.error(
                        f"Falha na bobina {bobina.numero} ({produto}): "
                        f"{erro} | dados: {bobina}"
                    )
                    print(
                        f"Erro ao cadastrar bobina {bobina.numero}: {erro}"
                    )

                    falhas.append(bobina)

                    modal_fechado = navegador.tentar_fechar_modal()

                    if not modal_fechado:
                        print(
                            "\nATENÇÃO: não consegui fechar a tela "
                            "travada automaticamente.\n"
                            "Verifique manualmente o sistema (feche algum "
                            "aviso/modal aberto) e deixe a tela na LISTA de "
                            "bobinas antes de continuar."
                        )
                        logger.warning(
                            f"Não foi possível fechar o modal após falha na "
                            f"bobina {bobina.numero}. Pausado para "
                            "intervenção manual."
                        )
                        self._confirmar(
                            "Pressione ENTER quando a tela estiver pronta "
                            "para continuar..."
                        )

                self.evento("progresso", concluidas=cadastradas, total=total,
                            texto=(f"{cadastradas} de {total} processadas | "
                                   f"{len(sucessos)} cadastradas | {len(falhas)} falhas"))

        self.controle.verificar()
        print("Cadastro finalizado.")

        saldo_final = navegador.ler_saldo_classificar()
        peso_esperado = sum(bobina.peso for bobina in sucessos) + ajuste_peso

        if saldo_inicial is not None and saldo_final is not None:

            reducao_real = saldo_inicial - saldo_final

            if abs(reducao_real - peso_esperado) > 1:

                extra_ajuste = (
                    f" (incluindo ajuste do romaneio de {ajuste_peso} kg)"
                    if ajuste_peso else ""
                )

                print(
                    f"\nATENÇÃO: o saldo a classificar caiu {reducao_real} "
                    f"kg, mas o esperado era {peso_esperado} kg{extra_ajuste} "
                    f"({len(sucessos)} bobina(s) cadastrada(s)). "
                    "Confira manualmente se o romaneio foi lido "
                    "corretamente e se não faltou/sobrou nenhuma bobina."
                )
                logger.warning(
                    f"Divergência no saldo: esperado {peso_esperado} kg, "
                    f"reduziu {reducao_real} kg (saldo inicial "
                    f"{saldo_inicial}, saldo final {saldo_final})."
                )
            else:
                print(
                    f"\nSaldo conferido: reduziu {reducao_real} kg, "
                    f"como esperado ({len(sucessos)} bobina(s))."
                )
        else:
            print(
                "\nNão foi possível conferir o saldo a classificar "
                "automaticamente (campo não encontrado na tela)."
            )

        if falhas:
            numeros = [bobina.numero for bobina in falhas]
            print(f"\n{len(falhas)} bobina(s) NÃO cadastrada(s): {numeros}")
            print("Dados para conferência/cadastro manual:")

            for bobina in falhas:
                print(f"  - {bobina}")

            logger.warning(f"Bobinas com falha: {numeros}")
        else:
            print("Todas as bobinas foram cadastradas com sucesso.")
            logger.info("Todas as bobinas foram cadastradas com sucesso.")

        # Só ao terminar normalmente: paradas e erros mantêm a sessão para conferência.
        self.evento("status", texto="Saindo do EGS...")
        if navegador.sair_do_sistema():
            logger.info("Sessão do EGS encerrada ao final do cadastro.")
        else:
            print("\nNão foi possível sair do EGS automaticamente; saia manualmente.")

        if not self.solicitar:
            input("Pressione ENTER para fechar...")
        return self._resultado()
