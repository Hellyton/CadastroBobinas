from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import config
import math
import re
from app.logger import logger



SEL_USUARIO = "#login > div > div:nth-child(2) > div > form > div:nth-child(2) > input"
SEL_SENHA = "#password"
SEL_CHAVE_ACESSO = "#login > div > div:nth-child(2) > div > form > div:nth-child(4) > input"
SEL_BOTAO_ENTRAR = "#login > div > div:nth-child(2) > div > form > button"
SEL_BOTAO_NOVO = "#egsForm > div:nth-child(7) > ul > li:nth-child(1) > egs-button-new > button > i"
SEL_QUANTIDADE_CLASSIFICADA = "#egsForm > egs-input-number:nth-child(3) > input"
SEL_SALDO_CLASSIFICAR = "#egsForm > egs-input-number:nth-child(4) > input"
SEL_RUA = "#egsForm > div > egs-input-text:nth-child(1) > input"
SEL_DIAMETRO = "#egsForm > div > egs-input-text:nth-child(2) > input"
SEL_FORMATO = "#egsForm > div > egs-input-text:nth-child(3) > input"
SEL_PESO = "#egsForm > div > egs-input-text:nth-child(4) > input"
SEL_GRAMATURA = "#egsForm > div > egs-input-text:nth-child(5) > input"
SEL_OBSERVACAO = "#egsForm > div > egs-input-text:nth-child(10) > input"
SEL_GRAMATURA_MEDIA = "#egsForm > div > egs-input-text:nth-child(6) > input"
SEL_METRAGEM = "#egsForm > div > egs-input-text:nth-child(7) > input"
SEL_NAO_CONFORMIDADE = "#egsForm > div > egs-input-text:nth-child(9) > input"
SEL_BOTAO_SALVAR = (
    "body > div:nth-child(1) > div > div > div.modal-footer.ng-scope "
    "> div > div:nth-child(2) > egs-button-save-popup > button"
)
SEL_OK_POPUP_PESO = (
    "body > div.modal.zindex.ng-scope.ng-isolate-scope.in "
    "> div > div > div.modal-footer.ng-scope > div > button"
)
SEL_BOTAO_SAIR = (
    "body > div:nth-child(1) > div > div > div.modal-footer.ng-scope "
    "> div > div.col-xs-6.btn-after > egs-button-close-popup > button"
)
SEL_SAIR_CLASSIFICACAO = (
    "body > div.modal.in div.modal-footer egs-button-close-popup > button"
)
SEL_BOTAO_DESLIGAR = "#h-icons > button:has(.fa-power-off)"
SEL_CONFIRMAR_SAIR = "#btnSimConfirm"


class SalvamentoNaoConfirmado(RuntimeError):
    """O EGS não apresentou evidência suficiente para registrar sucesso."""


class Navegador:

    def __init__(self):

        self.playwright = None
        self.browser = None
        self.page = None

    def abrir(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=False
        )

        self.page = self.browser.new_page()

    def fazer_login(self):
        """Realiza o login automaticamente no sistema."""

        # Aguarda o formulário aparecer
        self.page.wait_for_selector(SEL_USUARIO)

        self.page.fill(SEL_USUARIO, config.USUARIO)
        self.page.fill(SEL_SENHA, config.SENHA)
        self.page.fill(SEL_CHAVE_ACESSO, config.CHAVE_ACESSO)

        self.page.click(SEL_BOTAO_ENTRAR)

        # Aguarda a página após o login carregar
        self.page.wait_for_load_state("networkidle")

    def acessar(self, url):

        self.page.goto(url)

    def clicar_novo(self):
        """
        Clica no botão '+' para abrir o modal de Classificação em branco
        e só retorna quando o campo Rua do modal já está visível na tela.
        Sem essa espera, em momentos em que o sistema demora um pouco mais
        pra renderizar o modal (rede lenta, máquina ocupada, etc.), o
        preencher_bobina() pode começar a preencher a Rua antes do campo
        estar pronto - causando falha intermitente nessa bobina.
        """

        self.page.click(SEL_BOTAO_NOVO)
        self.page.wait_for_selector(SEL_RUA, state="visible", timeout=10000)

    def ler_saldo_classificar(self):
        """
        Lê o peso (kg) que ainda falta classificar nessa nota, na tela de
        lista (Classificação de Bobinas). Retorna None se não conseguir
        ler (ex: seletor não encontrado nessa tela).
        """

        try:
            valor = self.page.input_value(SEL_SALDO_CLASSIFICAR)
            return self._parse_numero(valor)
        except Exception:
            return None

    def ler_quantidade_classificada(self):
        """
        Lê o peso (kg) já classificado nessa nota, na tela de lista.
        Retorna None se não conseguir ler.
        """

        try:
            valor = self.page.input_value(SEL_QUANTIDADE_CLASSIFICADA)
            return self._parse_numero(valor)
        except Exception:
            return None

    @staticmethod
    def _parse_numero(texto):
        """Converte um número no formato do sistema (ex: '35.000' ou
        '1.234,56') para float."""

        if texto is None:
            return None

        texto = texto.strip()

        if not texto:
            return None

        texto = texto.replace(".", "").replace(",", ".")

        try:
            return float(texto)
        except ValueError:
            return None

    def preencher_bobina(self, bobina):
        """Confere o formulário após os recálculos e refaz valores apagados."""
        self._campos_esperados = None
        campos = {
            SEL_RUA: str(bobina.rua),
            SEL_DIAMETRO: str(bobina.diametro),
            SEL_FORMATO: str(bobina.formato),
            SEL_PESO: str(bobina.peso),
            SEL_GRAMATURA: str(bobina.gramatura),
            SEL_OBSERVACAO: str(bobina.numero),
        }
        for tentativa in range(1, 4):
            self._preencher_campos(bobina)
            try:
                self._aguardar_campos_calculados()
            except Exception:
                divergencias = self._campos_divergentes(campos)
                if not divergencias or tentativa == 3:
                    raise
                logger.warning(f"EGS apagou/alterou campos antes do cálculo: {divergencias}. Refazendo preenchimento.")
                continue
            self.page.fill(SEL_OBSERVACAO + ":visible", str(bobina.numero))
            divergencias = self._campos_divergentes(campos)
            if not divergencias:
                self._campos_esperados = campos
                return
            logger.warning(f"Campos alterados pelo EGS após preenchimento ({tentativa}/3): {divergencias}")
        raise RuntimeError(
            f"O EGS apagou ou alterou campos da bobina {bobina.numero}: "
            f"{divergencias}. O formulário não será salvo.")

    def _campos_divergentes(self, campos):
        divergencias = {}
        for seletor, esperado in campos.items():
            atual = self.page.input_value(seletor + ":visible").strip()
            if seletor == SEL_OBSERVACAO:
                igual = atual == esperado
            else:
                igual = self._parse_numero(atual) == float(esperado)
            if not igual:
                divergencias[seletor] = {"esperado": esperado, "atual": atual}
        return divergencias

    def _preencher_campos(self, bobina):

        self._fill_verificado(SEL_RUA + ":visible", str(bobina.rua))
        self.page.fill(SEL_DIAMETRO + ":visible", str(bobina.diametro))
        self.page.fill(SEL_FORMATO + ":visible", str(bobina.formato))

        self.page.click(SEL_PESO + ":visible")
        self._fechar_popup_peso()
        self.page.fill(SEL_PESO + ":visible", str(bobina.peso))

        # Alguns avisos recriam os primeiros campos. Recupera somente
        # os valores que o EGS apagou, sem esperar ou refazer o modal.
        iniciais = {SEL_RUA: str(bobina.rua),
                    SEL_DIAMETRO: str(bobina.diametro),
                    SEL_FORMATO: str(bobina.formato)}
        for seletor in self._campos_divergentes(iniciais):
            self.page.fill(seletor + ":visible", iniciais[seletor])

        self.page.fill(SEL_GRAMATURA + ":visible", str(bobina.gramatura))

        # Tira o foco do campo Gramatura (dispara o blur) para o sistema
        # calcular Gramatura Média e Metragem da bobina, ANTES de mexer
        # na Observação — se preenchermos Observação antes desse cálculo,
        # o próprio recálculo do sistema pode estar resetando o campo.
        self.page.keyboard.press("Tab")

    def _fill_verificado(self, selector, valor, tentativas=4):
        """
        Confere o preenchimento sem uma pausa fixa por bobina.
        Alterações posteriores são verificadas após o cálculo e antes
        de salvar. Só aguarda brevemente quando o campo perdeu o valor.
        """

        for tentativa in range(1, tentativas + 1):

            self.page.fill(selector, valor)

            valor_atual = self.page.input_value(selector)
            if valor_atual == valor:
                return

            logger.warning(
                f"Campo {selector} não reteve o valor '{valor}' na "
                f"tentativa {tentativa}/{tentativas} (ficou "
                f"'{valor_atual}'). Tentando novamente..."
            )
            if tentativa < tentativas:
                self.page.wait_for_timeout(50)

        raise RuntimeError(
            f"Campo {selector} não reteve o valor '{valor}' após "
            f"{tentativas} tentativas (o sistema parece estar limpando "
            "o campo sozinho)."
        )

    def _aguardar_campos_calculados(self):
        """
        Espera o sistema preencher Gramatura Média e Metragem da bobina
        (campos calculados automaticamente) antes de liberar o Salvar.
        Se não calcular a tempo, tenta disparar o cálculo de novo (clica
        em Gramatura e sai do campo outra vez) antes de desistir de vez -
        às vezes o sistema simplesmente não pegou o blur na primeira.
        """

        try:
            self._esperar_calculo(timeout=8000)
            return
        except Exception:
            logger.warning(
                "Gramatura Média/Metragem não calcularam em 8s. "
                "Tentando disparar o cálculo de novo..."
            )

        self.page.click(SEL_GRAMATURA + ":visible")
        self.page.keyboard.press("Tab")

        self._esperar_calculo(timeout=8000)

    def _esperar_calculo(self, timeout):

        self.page.wait_for_function(
            """
            (selectors) => {
                const media = document.querySelector(selectors[0]);
                const metragem = document.querySelector(selectors[1]);
                return media && metragem
                    && media.value.trim() !== ""
                    && metragem.value.trim() !== "";
            }
            """,
            arg=[SEL_GRAMATURA_MEDIA, SEL_METRAGEM],
            timeout=timeout
        )

    def _fechar_popup_peso(self):
        """Fecha somente o aviso explícito de peso zero, se ele aparecer."""

        aviso = self.page.get_by_text(
            re.compile(r"^\s*Peso da bobina não pode ser zero!\s*$", re.I)
        ).filter(visible=True).first
        try:
            aviso.wait_for(state="visible", timeout=3000)
        except PlaywrightTimeoutError:
            # O aviso é opcional; outras falhas do Playwright devem aparecer.
            return False

        try:
            popup = aviso.locator(
                "xpath=ancestor-or-self::*[not(self::body or self::html) "
                "and .//button[normalize-space(.)='OK']][1]")
            botao_ok = popup.get_by_role("button", name="OK", exact=True)
            botao_ok.click(timeout=3000)
            popup.wait_for(state="hidden", timeout=3000)
        except Exception as erro:
            raise RuntimeError(
                "O aviso de peso zero apareceu, mas não foi possível fechá-lo "
                "pelo botão OK."
            ) from erro
        return True

    def salvar(self, peso=None, saldo_antes=None):
        """Só confirma sucesso com formulário fechado e saldo atualizado."""
        if saldo_antes is None:
            saldo_antes = self.ler_saldo_classificar()
        if peso is None:
            peso = self._parse_numero(self.page.input_value(SEL_PESO))
        if (saldo_antes is None or peso is None
                or not math.isfinite(saldo_antes) or not math.isfinite(peso)
                or peso <= 0 or saldo_antes <= 0 or peso > saldo_antes):
            raise SalvamentoNaoConfirmado(
                "Saldo insuficiente, zerado ou não reconhecido. "
                "Nenhum salvamento foi solicitado; confira a nota no EGS.")

        try:
            campos = getattr(self, "_campos_esperados", None)
            if campos:
                divergencias = self._campos_divergentes(campos)
                if divergencias:
                    raise SalvamentoNaoConfirmado(
                        f"O EGS alterou campos antes de salvar: {divergencias}.")
            self.page.click(SEL_BOTAO_SALVAR)
            # O fechamento isolado também pode ocorrer após uma rejeição.
            # Aguarda a atualização assíncrona do saldo, inclusive para zero.
            self.page.wait_for_function(
                """(dados) => {
                    if (document.querySelector(dados.salvar)) return false;
                    const campo = document.querySelector(dados.saldo);
                    if (!campo || !campo.value.trim()) return false;
                    const saldo = Number(campo.value.trim()
                        .replace(/\\./g, '').replace(',', '.'));
                    return Number.isFinite(saldo)
                        && Math.abs(saldo - dados.esperado) < 0.01;
                }""",
                arg=dict(salvar=SEL_BOTAO_SALVAR, saldo=SEL_SALDO_CLASSIFICAR,
                         esperado=saldo_antes - peso), timeout=10000)
        except SalvamentoNaoConfirmado:
            raise
        except Exception as erro:
            raise SalvamentoNaoConfirmado(
                "O salvamento não foi confirmado pelo saldo do EGS. "
                "A bobina não foi marcada no histórico. Confira se ela "
                "foi gravada no EGS antes de tentar novamente.") from erro

    def tentar_fechar_modal(self):
        """
        Usado quando algo dá errado no meio do preenchimento de uma bobina.
        Tenta fechar o modal (botão Sair, depois Escape) e CONFERE se ele
        realmente fechou - antes disso, o método só tentava fechar sem
        verificar, então se não conseguisse a bobina seguinte era
        preenchida em cima de uma tela ainda travada, causando falhas em
        cadeia. Tenta até 2 vezes. Retorna True se o modal fechou, False
        se continua aberto (nesse caso quem chamou deve parar e avisar,
        em vez de seguir tentando cadastrar a próxima bobina).
        """

        for _ in range(2):

            try:
                self.page.click(SEL_BOTAO_SAIR, timeout=3000)
            except Exception:
                pass

            try:
                self.page.keyboard.press("Escape")
            except Exception:
                pass

            try:
                self.page.wait_for_selector(
                    SEL_BOTAO_SALVAR,
                    state="detached",
                    timeout=3000
                )
                return True
            except Exception:
                continue

        return False

    def sair_do_sistema(self):
        """Fecha a Classificação de Bobinas e encerra a sessão no EGS.

        Retorna True somente quando a tela de login reaparece; falhas são
        registradas e não interrompem o encerramento do cadastro.
        """

        try:
            sair = self.page.locator(SEL_SAIR_CLASSIFICACAO).filter(has_text="Sair")
            if sair.count():
                sair.last.click(timeout=3000)
                sair.last.wait_for(state="hidden", timeout=5000)
            self.page.click(SEL_BOTAO_DESLIGAR, timeout=5000)
            self.page.click(SEL_CONFIRMAR_SAIR, timeout=5000)
            self.page.wait_for_selector(SEL_USUARIO, timeout=10000)
            return True
        except Exception as erro:
            logger.warning(f"Não foi possível sair do EGS automaticamente: {erro}")
            return False

    def aguardar_fechamento(self, encerrar):
        """Mantém o Chromium aberto até o operador fechá-lo ou `encerrar` ser sinalizado."""

        while (self.browser is not None and self.browser.is_connected()
               and not encerrar.is_set()):
            paginas = [p for contexto in self.browser.contexts for p in contexto.pages]
            if not paginas:
                return
            try:
                # Espera pelo Playwright para continuar processando os eventos do navegador.
                paginas[0].wait_for_timeout(500)
            except Exception:
                return

    def fechar(self):

        try:
            if self.browser is not None:
                self.browser.close()
        finally:
            if self.playwright is not None:
                self.playwright.stop()
