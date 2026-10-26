import os
from queue import Queue, Empty
from threading import Thread, Event
from tkinter import filedialog, ttk, StringVar

import customtkinter as ctk
from openpyxl import Workbook

from app.agrupamento import agrupar_bobinas, nome_grupo, produtos_com_variantes
from app.cadastro import CadastroBobinas
from app.componentes import Indicador, Dialogo
from app.controle import ControleCadastro
from app.leitor_pdf import ler_romaneio
from app.logger import logger
from app.tema import CORES, cartao, texto, botao, menu, configurar_tabela, numero
from app.janela_historico import JanelaHistorico
from app.nota_fiscal import ler_nota_fiscal, ler_numero_romaneio, conferir_nota


ctk.set_appearance_mode("dark")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bobinas | Classificação de romaneios")
        self.configure(fg_color=CORES["fundo"])
        escala = self._get_window_scaling()
        largura = min(1180, round(self.winfo_screenwidth() / escala) - 48)
        altura = min(800, round(self.winfo_screenheight() / escala) - 48)
        self._compacto = altura < 720
        x = max(0, round((self.winfo_screenwidth() - largura * escala) / 2))
        y = max(10, round((self.winfo_screenheight() - altura * escala) / 2) - 16)
        self.geometry(f"{largura}x{altura}+{x}+{y}")
        self.minsize(min(940, largura), min(680, altura))
        self._eventos = Queue()
        self._executando = False
        self._fechando = False
        self._pedido = None
        self._controle = None
        self._dialogo_confirmacao = None
        self._janela_historico = None
        self._concluidas = 0
        self._total_execucao = 0
        self.bobinas = []
        self._grupos = {}
        self._variantes = frozenset()
        self._grupos_por_rotulo = {}
        self._nota_fiscal = None
        self._associacoes_nf = {}
        self._dialogo_nf = None
        self.caminho_pdf = None
        self.ajuste_peso = 0
        self.busca = StringVar(master=self, value="")
        self.numero_romaneio = StringVar(master=self, value="")
        self.protocol("WM_DELETE_WINDOW", self.fechar_janela)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.conteudo = ctk.CTkFrame(self, fg_color="transparent")
        self.conteudo.grid(row=0, column=0, sticky="nsew", padx=24, pady=16 if self._compacto else 20)
        self.conteudo.grid_columnconfigure(0, weight=1)
        self.conteudo.grid_rowconfigure(3, weight=1)
        self._estilo = configurar_tabela(self.conteudo)
        self._montar_cabecalho()
        self._montar_importacao()
        self._montar_indicadores()
        self._montar_conferencia()
        self._montar_execucao()
        self.busca.trace_add("write", lambda *args: self.filtrar_bobinas())
        self.numero_romaneio.trace_add("write", self._romaneio_alterado)
        self.bind("<Control-o>", self._atalho_importar)
        self.bind("<Control-f>", self._atalho_buscar)
        self._timer_eventos = self.after(100, self.processar_eventos)

    def _montar_cabecalho(self):
        cabecalho = ctk.CTkFrame(self.conteudo, fg_color="transparent")
        cabecalho.grid(row=0, column=0, sticky="ew", pady=(0, 12 if self._compacto else 18))
        cabecalho.grid_columnconfigure(1, weight=1)
        marca = ctk.CTkFrame(cabecalho, width=42, height=42, corner_radius=10,
                             fg_color=CORES["primario"])
        marca.grid(row=0, column=0, rowspan=2, padx=(0, 14))
        marca.grid_propagate(False)
        texto(marca, "◎", 31, CORES["fundo"], True).place(relx=.5, rely=.5, anchor="center")
        self.titulo = texto(cabecalho, "Cadastro de bobinas", 24, negrito=True)
        self.titulo.grid(row=0, column=1, sticky="w")
        texto(cabecalho, "Importe, confira e classifique seu romaneio.", 12, "muted").grid(row=1, column=1, sticky="w")
        self.botao_historico = botao(cabecalho, "Histórico", self.abrir_historico,
                                      width=110)
        self.botao_historico.grid(row=0, column=2, rowspan=2, padx=(14, 0))
        self.botao_nf = botao(cabecalho, "Importar NF", self.abrir_nf,
                             width=120, state="disabled")
        self.botao_nf.grid(row=0, column=3, rowspan=2, padx=(10, 0))
        self.botao_pdf = botao(cabecalho, "Selecionar romaneio", self.abrir_pdf,
                                "primario", width=180)
        self.botao_pdf.grid(row=0, column=4, rowspan=2, padx=(10, 0))

    def _montar_importacao(self):
        self.frame_fornecedor = cartao(self.conteudo)
        self.frame_fornecedor.grid(row=1, column=0, sticky="ew", pady=(0, 10 if self._compacto else 14))
        self.frame_fornecedor.grid_columnconfigure(1, weight=1)
        texto(self.frame_fornecedor, "PDF", 12, "muted", True,
              width=46, height=42, fg_color=CORES["superficie"], corner_radius=7).grid(
                  row=0, column=0, rowspan=2, padx=(16, 12), pady=10 if self._compacto else 14)
        self.arquivo = texto(self.frame_fornecedor, "Nenhum romaneio selecionado", 13,
                              negrito=True, anchor="w", width=1)
        self.arquivo.grid(row=0, column=1, sticky="ew", pady=(12, 0))
        self.detalhe_arquivo = texto(self.frame_fornecedor,
            "Selecione um PDF para começar a conferência.", 11, "muted", anchor="w", width=1)
        self.detalhe_arquivo.grid(row=1, column=1, sticky="ew", pady=(0, 12))
        texto(self.frame_fornecedor, "Nº do romaneio", 11, "muted").grid(
            row=0, column=2, sticky="w", padx=(16, 0), pady=(4 if self._compacto else 8, 0))
        self.campo_romaneio = ctk.CTkEntry(
            self.frame_fornecedor, textvariable=self.numero_romaneio,
            width=125, height=32 if self._compacto else 36,
            fg_color=CORES["fundo"], border_color=CORES["borda"],
            text_color=CORES["texto"], state="disabled")
        self.campo_romaneio.grid(row=1, column=2, padx=(16, 0), pady=(0, 8 if self._compacto else 12))
        self.label_fornecedor = texto(self.frame_fornecedor, "Fornecedor", 11, "muted")
        self.label_fornecedor.grid(row=0, column=3, sticky="w", padx=(20, 16), pady=(4 if self._compacto else 8, 0))
        self.combo_fornecedor = menu(self.frame_fornecedor,
            ["Detectar automaticamente", "ADF", "HP", "Novakraft", "Cocelpa"],
            self.fornecedor_alterado, width=205)
        self.combo_fornecedor.grid(row=1, column=3, padx=(20, 16), pady=(0, 8 if self._compacto else 12))
        if self._compacto:
            self.combo_fornecedor.configure(height=32)
        self.combo_fornecedor.set("Detectar automaticamente")
        self.arquivo_nf = texto(self.frame_fornecedor, "", 11, "muted",
                                wraplength=650, justify="left", anchor="w")
        self.arquivo_nf.grid(row=2, column=1, columnspan=3, sticky="ew", pady=(0, 8), padx=(0, 16))
        self.arquivo_nf.grid_remove()

    def _montar_indicadores(self):
        linha = ctk.CTkFrame(self.conteudo, fg_color="transparent")
        linha.grid(row=2, column=0, sticky="ew", pady=(0, 12 if self._compacto else 18))
        linha.grid_columnconfigure((0, 1, 2), weight=1, uniform="indicadores")
        self.indicador_bobinas = Indicador(linha, "Bobinas no romaneio", "0", "Aguardando importação", self._compacto)
        self.indicador_peso = Indicador(linha, "Peso total", "0 kg", "Peso líquido do romaneio", self._compacto)
        self.indicador_produtos = Indicador(linha, "Classificações", "0", "Produtos, variações e pontas", self._compacto)
        for indice, indicador in enumerate((self.indicador_bobinas, self.indicador_peso, self.indicador_produtos)):
            indicador.grid(row=0, column=indice, sticky="ew", padx=(0 if indice == 0 else 7, 0 if indice == 2 else 7))

    def _montar_conferencia(self):
        corpo = ctk.CTkFrame(self.conteudo, fg_color="transparent")
        corpo.grid(row=3, column=0, sticky="nsew")
        corpo.grid_columnconfigure(0, weight=1)
        corpo.grid_columnconfigure(1, minsize=270)
        corpo.grid_rowconfigure(0, weight=1)
        self.frame_tabela = cartao(corpo)
        self.frame_tabela.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        self.frame_tabela.grid_columnconfigure(0, weight=1)
        self.frame_tabela.grid_rowconfigure(2, weight=1)
        topo = ctk.CTkFrame(self.frame_tabela, fg_color="transparent")
        topo.grid(row=0, column=0, sticky="ew", padx=16, pady=12)
        topo.grid_columnconfigure(1, weight=1)
        texto(topo, "Bobinas do romaneio", 15, negrito=True).grid(row=0, column=0, sticky="w")
        filtros = ctk.CTkFrame(topo, fg_color="transparent")
        filtros.grid(row=0, column=1, sticky="ew", padx=(16, 0))
        filtros.grid_columnconfigure(0, weight=1)
        self.campo_busca = ctk.CTkEntry(filtros,
            placeholder_text="Buscar bobina, produto ou largura...", height=36,
            fg_color=CORES["fundo"], border_color=CORES["borda"],
            text_color=CORES["texto"], placeholder_text_color=CORES["discreto"],
            font=("Segoe UI", 12), corner_radius=7)
        self.campo_busca.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.campo_busca.bind("<KeyRelease>", lambda event: self.busca.set(self.campo_busca.get()))
        self.campo_busca.bind("<Escape>", lambda event: self.busca.set(""))
        self.filtro_produto = menu(filtros, ["Todos os produtos"],
                                   lambda valor: self.filtrar_bobinas(), width=180,
                                   dynamic_resizing=False)
        self.filtro_produto.grid(row=0, column=1)
        self.filtro_produto.set("Todos os produtos")
        self.frame_dados = ctk.CTkFrame(self.frame_tabela, fg_color="transparent")
        self.frame_dados.grid(row=2, column=0, sticky="nsew", padx=1)
        self.frame_dados.grid_columnconfigure(0, weight=1)
        self.frame_dados.grid_rowconfigure(0, weight=1)
        colunas = ("numero", "produto", "gramatura", "formato", "diametro", "peso")
        self.tabela = ttk.Treeview(self.frame_dados, columns=colunas, show="headings",
                                   height=4, style="Bobinas.Treeview", selectmode="browse")
        configuracao = (
            ("numero", "Bobina", 120, "w"), ("produto", "Produto", 150, "w"),
            ("gramatura", "Gram.", 65, "center"), ("formato", "Largura", 75, "center"),
            ("diametro", "Diâm.", 75, "center"), ("peso", "Peso (kg)", 90, "e"),
        )
        for chave, titulo, largura, ancora in configuracao:
            self.tabela.heading(chave, text=titulo, anchor=ancora)
            self.tabela.column(chave, width=largura, minwidth=largura, anchor=ancora)
        self.tabela.tag_configure("alternada", background="#161619")
        self.tabela.grid(row=0, column=0, sticky="nsew")
        barra = ctk.CTkScrollbar(self.frame_dados, command=self.tabela.yview,
            fg_color=CORES["cartao"], button_color=CORES["borda"],
            button_hover_color=CORES["discreto"], width=10)
        barra.grid(row=0, column=1, sticky="ns")
        horizontal = ctk.CTkScrollbar(self.frame_dados, orientation="horizontal",
            command=self.tabela.xview, fg_color=CORES["cartao"],
            button_color=CORES["borda"], button_hover_color=CORES["discreto"], height=10)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.tabela.configure(yscrollcommand=barra.set, xscrollcommand=horizontal.set)
        self.estado_vazio = ctk.CTkFrame(self.frame_dados, fg_color=CORES["cartao"])
        self.estado_vazio.grid_columnconfigure(0, weight=1)
        self.titulo_vazio = texto(self.estado_vazio, "Seu romaneio começa aqui", 16, negrito=True)
        self.titulo_vazio.grid(row=0, column=0, pady=(10, 4))
        self.ajuda_vazio = texto(self.estado_vazio, "Selecione um PDF para visualizar as bobinas.",
                                12, "muted", wraplength=360, justify="center")
        self.ajuda_vazio.grid(row=1, column=0, pady=(0, 10))
        self.estado_vazio.place(relx=.5, rely=.55, anchor="center", relwidth=.9)
        self.rodape_tabela = texto(self.frame_tabela, "Os dados do romaneio aparecerão nesta tabela.", 11, "muted")
        self.rodape_tabela.grid(row=3, column=0, sticky="w", padx=16, pady=(6, 10))

        self.frame_resumo = cartao(corpo, width=270)
        self.frame_resumo.grid(row=0, column=1, sticky="nsew")
        self.frame_resumo.grid_columnconfigure(0, weight=1)
        self.frame_resumo.grid_rowconfigure(2, weight=1)
        texto(self.frame_resumo, "Peso por produto", 15, negrito=True).grid(
            row=0, column=0, sticky="w", padx=16, pady=(12, 0))
        texto(self.frame_resumo, "Produtos e variações do romaneio.", 11, "muted").grid(
            row=1, column=0, sticky="w", padx=16, pady=(0, 8))
        self.resumo_produtos = ctk.CTkScrollableFrame(self.frame_resumo,
            fg_color=CORES["cartao"], corner_radius=0, width=236,
            scrollbar_button_color=CORES["borda"], scrollbar_button_hover_color=CORES["discreto"])
        self.resumo_produtos.grid(row=2, column=0, sticky="nsew", padx=8)
        self.resumo_produtos.grid_columnconfigure(0, weight=1)
        texto(self.resumo_produtos, "Os totais aparecerão aqui.", 12, "muted").grid(
            row=0, column=0, sticky="w", padx=8, pady=20)
        self.nota_resumo = texto(self.frame_resumo, "Soma dos pesos de todas as bobinas.",
                                  11, "muted", wraplength=230, justify="left")
        self.nota_resumo.grid(row=3, column=0, sticky="w", padx=16, pady=(8, 14))

    def _montar_execucao(self):
        self.frame_execucao = cartao(self.conteudo)
        self.frame_execucao.grid(row=4, column=0, sticky="ew", pady=(12 if self._compacto else 16, 0))
        self.frame_execucao.grid_columnconfigure(0, weight=1)
        topo = ctk.CTkFrame(self.frame_execucao, fg_color="transparent")
        topo.grid(row=0, column=0, sticky="ew", padx=16, pady=(10, 0))
        topo.grid_columnconfigure(0, weight=1)
        texto(topo, "Cadastro no EGS", 14, negrito=True).grid(row=0, column=0, sticky="w")
        self.selo_status = texto(topo, "● Aguardando romaneio", 11, "muted")
        self.selo_status.grid(row=0, column=1, sticky="e", padx=(10, 0))
        self.status = texto(self.frame_execucao, "Selecione um romaneio para começar.",
                             12, "muted", anchor="w", justify="left", wraplength=1000)
        self.status.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 4))
        progresso = ctk.CTkFrame(self.frame_execucao, fg_color="transparent")
        progresso.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8 if self._compacto else 12))
        progresso.grid_columnconfigure(0, weight=1)
        self.progresso = ctk.CTkProgressBar(progresso, height=5, corner_radius=3,
            fg_color=CORES["borda"], progress_color=CORES["primario"])
        self.progresso.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.progresso.set(0)
        self.rotulo_progresso = texto(progresso, "0%", 11, "muted", width=40, height=16)
        self.rotulo_progresso.grid(row=0, column=1)
        self.frame_botoes = ctk.CTkFrame(self.frame_execucao, fg_color="transparent")
        self.frame_botoes.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 10 if self._compacto else 14))
        self.frame_botoes.grid_columnconfigure(3, weight=1)
        self.botao_exportar = botao(self.frame_botoes, "Exportar Excel", self.exportar_excel,
                                     width=140, state="disabled")
        self.botao_exportar.grid(row=0, column=0, padx=(0, 10))
        self.botao_pausa = botao(self.frame_botoes, "Pausar", self.alternar_pausa,
                                  width=100, state="disabled")
        self.botao_pausa.grid(row=0, column=1, padx=(0, 10))
        self.botao_interromper = botao(self.frame_botoes, "Interromper", self.interromper_cadastro,
                                        "perigo", width=110, state="disabled")
        self.botao_interromper.grid(row=0, column=2)
        self.botao_cadastro = botao(self.frame_botoes, "Iniciar cadastro", self.iniciar_cadastro,
                                     "primario", width=180, state="disabled")
        self.botao_cadastro.grid(row=0, column=4, padx=(20, 0))
        self.frame_execucao.bind("<Configure>", self._ajustar_status)

    def _ajustar_status(self, evento):
        self.status.configure(wraplength=max(300, round(evento.width / self.frame_execucao._get_widget_scaling()) - 32))

    def _atalho_importar(self, evento=None):
        if not self._executando:
            self.abrir_pdf()
        return "break"

    def abrir_historico(self):
        if self._executando:
            return
        if self._janela_historico and self._janela_historico.winfo_exists():
            self._janela_historico.lift()
            self._janela_historico.focus_set()
            return
        self._janela_historico = JanelaHistorico(
            self, ao_fechar=self._historico_fechado)

    def _historico_fechado(self, janela):
        if self._janela_historico is janela:
            self._janela_historico = None

    def _atalho_buscar(self, evento=None):
        self.campo_busca.focus_set()
        return "break"

    def _definir_estado(self, rotulo, tom="muted"):
        self.selo_status.configure(text="● " + rotulo, text_color=CORES[tom])

    def _mostrar_mensagem(self, titulo, mensagem, tom="muted"):
        dialogo = Dialogo(self, titulo, mensagem, tom=tom)
        self.wait_window(dialogo)

    def _fechar_confirmacao(self):
        if self._dialogo_confirmacao is not None:
            self._dialogo_confirmacao.fechar()
            self._dialogo_confirmacao = None

    def filtrar_bobinas(self):
        if self.campo_busca.get() != self.busca.get():
            self.campo_busca.delete(0, "end")
            if self.busca.get():
                self.campo_busca.insert(0, self.busca.get())
        termo = self.busca.get().strip().casefold()
        escolha = self.filtro_produto.get()
        grupo = self._grupos_por_rotulo.get(escolha, escolha)
        visiveis = [b for b in self.bobinas
                    if (grupo == "Todos os produtos" or nome_grupo(b, self._variantes) == grupo)
                    and (not termo or termo in " ".join(map(str, (
                        b.numero, nome_grupo(b, self._variantes), b.gramatura,
                        b.formato, b.diametro, b.peso))).casefold())]
        itens = self.tabela.get_children()
        if itens:
            self.tabela.delete(*itens)
        for indice, bobina in enumerate(visiveis):
            produto = (self._rotulo_grupo(nome_grupo(bobina, self._variantes))
                       if bobina.produto in self._variantes else bobina.produto)
            self.tabela.insert("", "end", values=(bobina.numero, produto,
                bobina.gramatura, bobina.formato, bobina.diametro, numero(bobina.peso)),
                tags=("alternada",) if indice % 2 else ())
        self.rodape_tabela.configure(text=(
            f"Exibindo {numero(len(visiveis))} de {numero(len(self.bobinas))} bobinas · Pesos em kg"
            if self.bobinas else "Os dados do romaneio aparecerão nesta tabela."))
        if visiveis:
            self.estado_vazio.place_forget()
        else:
            self.titulo_vazio.configure(text="Nenhuma bobina encontrada" if self.bobinas else "Seu romaneio começa aqui")
            self.ajuda_vazio.configure(text="Tente outra busca ou escolha outro produto."
                if self.bobinas else "Selecione um PDF para visualizar as bobinas.")
            self.estado_vazio.place(relx=.5, rely=.55, anchor="center", relwidth=.9)

    def abrir_pdf(self):
        if self._executando:
            return
        caminho = filedialog.askopenfilename(
            parent=self, title="Selecione o romaneio",
            filetypes=[("Arquivos PDF", "*.pdf")])
        if not caminho:
            return
        self.caminho_pdf = caminho
        nome = os.path.basename(caminho)
        self.arquivo.configure(text=nome if len(nome) <= 62 else nome[:34] + "…" + nome[-24:])
        self.botao_pdf.configure(text="Trocar romaneio")
        self.combo_fornecedor.set("Detectar automaticamente")
        self.processar_pdf(fornecedor=None)

    def fornecedor_alterado(self, valor):
        if not self.caminho_pdf or self._executando:
            return
        self.processar_pdf(None if valor == "Detectar automaticamente" else valor)

    def processar_pdf(self, fornecedor):
        if self._executando:
            return
        self.status.configure(text="Lendo o romaneio e identificando as bobinas...")
        self._definir_estado("Lendo PDF")
        self.update_idletasks()
        self.numero_romaneio.set("")
        try:
            bobinas, fornecedor_usado, ajuste = ler_romaneio(self.caminho_pdf, fornecedor=fornecedor)
        except Exception:
            logger.exception("Não foi possível importar o romaneio")
            self.bobinas, self.ajuste_peso = [], 0
            self._atualizar_romaneio()
            self._definir_estado("Falha na importação", "erro")
            self.detalhe_arquivo.configure(text="Não foi possível ler este arquivo.")
            self.status.configure(text="Escolha outro PDF ou confira o fornecedor selecionado.")
            self._mostrar_mensagem("Não foi possível ler o PDF",
                "Confira se o arquivo é um romaneio válido e se está acessível. "
                "Você pode tentar novamente ou selecionar outro arquivo.", "erro")
            return

        self.bobinas, self.ajuste_peso = bobinas, ajuste
        if bobinas:
            try:
                self.numero_romaneio.set(ler_numero_romaneio(self.caminho_pdf) or "")
            except Exception:
                logger.warning("Número do romaneio não identificado; informe-o na interface.")
        for bobina in self.bobinas:
            bobina.fornecedor = fornecedor_usado or ""
        if fornecedor is None and fornecedor_usado:
            self.combo_fornecedor.set(fornecedor_usado)
        self._atualizar_romaneio()
        if fornecedor_usado is None:
            self.detalhe_arquivo.configure(text="Fornecedor não identificado · selecione ao lado.")
            self._definir_estado("Confira o fornecedor", "alerta")
            self.status.configure(text="Selecione o fornecedor correto para ler este romaneio.")
            self._mostrar_mensagem("Fornecedor não reconhecido",
                "Selecione o fornecedor correto no menu ao lado do arquivo para continuar.", "alerta")
        elif self.bobinas:
            self.detalhe_arquivo.configure(text=f"PDF importado · Fornecedor {fornecedor_usado}")
            self._definir_estado("Pronto para cadastrar", "sucesso")
            self.status.configure(text=("Confira as bobinas e os pesos por produto antes de iniciar."
                if self.numero_romaneio.get() else "Informe o número do romaneio para registrar o histórico."))
        else:
            self.detalhe_arquivo.configure(text=f"Fornecedor {fornecedor_usado} · nenhuma bobina encontrada")
            self._definir_estado("Romaneio sem bobinas", "alerta")
            self.status.configure(text="Confira o arquivo e o fornecedor selecionado.")

    def _atualizar_romaneio(self):
        self._limpar_nf()
        self.campo_romaneio.configure(state="normal" if self.bobinas else "disabled")
        peso = sum(b.peso for b in self.bobinas) + self.ajuste_peso
        self.indicador_bobinas.atualizar(numero(len(self.bobinas)),
            "Importadas do PDF" if self.bobinas else "Aguardando importação")
        self.indicador_peso.atualizar(f"{numero(peso)} kg",
            f"Inclui ajuste de {numero(self.ajuste_peso)} kg" if self.ajuste_peso else "Soma dos pesos das bobinas")
        self.atualizar_resumo_produtos()
        self._atualizar_filtro_produtos()
        self.busca.set("")
        self.filtrar_bobinas()
        self.progresso.set(0)
        self.rotulo_progresso.configure(text="0%")
        estado = "normal" if self.bobinas else "disabled"
        self.botao_exportar.configure(state=estado)
        self.botao_cadastro.configure(state=estado)

    def _limpar_nf(self):
        if self._dialogo_nf:
            self._dialogo_nf.fechar()
            self._dialogo_nf = None
        self._nota_fiscal = None
        self._associacoes_nf = {}
        self.arquivo_nf.grid_remove()
        self.botao_nf.configure(state="normal" if self.bobinas else "disabled")

    def _romaneio_alterado(self, *_):
        if not self._nota_fiscal and not self._dialogo_nf:
            return
        self._limpar_nf()
        self.atualizar_resumo_produtos()
        self._atualizar_filtro_produtos()
        self.filtrar_bobinas()
        self.status.configure(text="Número do romaneio alterado. Importe a NF novamente para conferir.")

    def atualizar_resumo_produtos(self):
        self._variantes = produtos_com_variantes(self.bobinas)
        self._grupos = agrupar_bobinas(self.bobinas)
        self.indicador_produtos.atualizar(numero(len(self._grupos)))
        self.totais_produtos = {}
        for widget in self.resumo_produtos.winfo_children():
            widget.destroy()
        for indice, (grupo, bobinas) in enumerate(self._grupos.items()):
            peso = sum(b.peso for b in bobinas)
            self.totais_produtos[grupo] = (len(bobinas), peso)
            item = cartao(self.resumo_produtos)
            item.grid(row=indice, column=0, sticky="ew", padx=(2, 4), pady=(0, 8))
            item.grid_columnconfigure(0, weight=1)
            titulo = self._rotulo_grupo(grupo)
            item_nf = self._associacoes_nf.get(grupo)
            if item_nf:
                titulo = f"Item {item_nf.numero} · {titulo}"
            texto(item, titulo, 11, "muted", True,
                  wraplength=205, anchor="w").grid(row=0, column=0, sticky="w", padx=12, pady=(9, 0))
            texto(item, f"{numero(peso)} kg", 22, negrito=True).grid(
                row=1, column=0, sticky="w", padx=12)
            larguras = sorted({b.formato for b in bobinas})
            ponta = all(largura < 1000 for largura in larguras)
            detalhe = f"{len(bobinas)} bobina(s)"
            if ponta:
                detalhe += " · Ponta " + "/".join(map(str, larguras))
            texto(item, detalhe, 11, "alerta" if ponta else "muted").grid(
                row=2, column=0, sticky="w", padx=12, pady=(0, 9))
        if not self._grupos:
            texto(self.resumo_produtos, "Nenhum produto encontrado.", 12, "muted").grid(
                row=0, column=0, sticky="w", padx=8, pady=20)
        nota = "Totais de todas as bobinas, mesmo com filtros ativos."
        if self.ajuste_peso:
            nota += f"\nAjuste de {numero(self.ajuste_peso)} kg aplicado apenas ao total geral."
        self.nota_resumo.configure(text=nota)

    @staticmethod
    def _rotulo_grupo(grupo):
        return grupo.split(" // ", 1)[-1]

    def _atualizar_filtro_produtos(self):
        self._grupos_por_rotulo = {}
        for grupo in self._grupos:
            rotulo = self._rotulo_grupo(grupo)
            item_nf = self._associacoes_nf.get(grupo)
            if item_nf:
                rotulo = f"Item {item_nf.numero} · {rotulo}"
            if rotulo in self._grupos_por_rotulo:
                rotulo = grupo
            self._grupos_por_rotulo[rotulo] = grupo
        self.filtro_produto.configure(values=["Todos os produtos"] + list(self._grupos_por_rotulo))
        self.filtro_produto.set("Todos os produtos")

    @staticmethod
    def _peso_nf(valor):
        return numero(int(valor)) if valor == int(valor) else str(valor).replace(".", ",")

    @staticmethod
    def _numero_nf(nota):
        digitos = nota.numero.replace(".", "")
        return str(int(digitos)) if digitos.isdigit() else nota.numero

    def abrir_nf(self):
        if self._executando or not self.bobinas:
            return
        caminho = filedialog.askopenfilename(
            parent=self, title="Selecione a NF para conferir (opcional)",
            filetypes=[("Arquivos PDF", "*.pdf")])
        if not caminho:
            return
        try:
            nota = ler_nota_fiscal(caminho)
            referencia = self.numero_romaneio.get().strip() or None
            conferencia = conferir_nota(nota, self.bobinas, referencia)
        except Exception as erro:
            logger.exception("Não foi possível conferir a NF")
            self._mostrar_mensagem("Não foi possível importar a NF", str(erro), "erro")
            return

        linhas = [f"NF {self._numero_nf(nota)} · {len(nota.itens)} itens",
                  "Confira as sugestões por produto e peso antes de usá-las."]
        if conferencia.alertas or conferencia.pendencias:
            linhas.insert(1, f"Atenção: {len(conferencia.alertas)} alerta(s) e "
                          f"{len(conferencia.pendencias)} pendência(s) para conferir.")
        linhas.append(f"Total NF: {self._peso_nf(sum(item.peso for item in nota.itens))} kg · "
                      f"Bobinas: {numero(sum(b.peso for b in self.bobinas))} kg")
        if nota.romaneio:
            linhas.append(f"Romaneio citado na NF: {nota.romaneio}")
        for item in nota.itens:
            grupo = next((g for g, candidato in conferencia.associacoes.items()
                          if candidato.numero == item.numero), None)
            linhas.append(f"\nItem {item.numero} · {item.descricao} · {self._peso_nf(item.peso)} kg")
            linhas.append("Grupo: " + self._rotulo_grupo(grupo) if grupo else "Sem associação única.")
        if conferencia.alertas:
            linhas.append("\nConferências necessárias:\n" + "\n".join(conferencia.alertas))
        if conferencia.pendencias:
            linhas.append("\nPendências:\n" + "\n".join(conferencia.pendencias))
        linhas.append("\nAs sugestões não selecionam abas no EGS. Confira o número do item ao classificar.")
        self._dialogo_nf = Dialogo(
            self, "Conferir NF e romaneio", "\n".join(linhas),
            confirmar=lambda resposta="": self._aceitar_nf(nota, conferencia),
            cancelar=self._cancelar_conferencia_nf, texto_cancelar="Cancelar",
            acao="Usar associações", altura=520,
            tom="alerta" if conferencia.alertas or conferencia.pendencias else "sucesso")
        if not conferencia.referencia_compativel or not conferencia.associacoes:
            self._dialogo_nf.botao_confirmar.configure(state="disabled")

    def _cancelar_conferencia_nf(self):
        self._dialogo_nf = None

    def _aceitar_nf(self, nota, conferencia):
        self._dialogo_nf = None
        if not conferencia.referencia_compativel or not conferencia.associacoes:
            return
        self._nota_fiscal = nota
        self._associacoes_nf = dict(conferencia.associacoes)
        self.atualizar_resumo_produtos()
        self._atualizar_filtro_produtos()
        self.filtrar_bobinas()
        mensagem = f"NF {self._numero_nf(nota)} · {len(self._associacoes_nf)} de {len(nota.itens)} itens associados"
        if conferencia.alertas or conferencia.pendencias:
            mensagem += " · Confira os alertas antes de classificar."
        self.arquivo_nf.configure(text=mensagem,
            text_color=CORES["alerta"] if conferencia.alertas or conferencia.pendencias else CORES["sucesso"])
        self.arquivo_nf.grid()
        self.status.configure(text="Associações da NF confirmadas. Confira o número do item no EGS ao cadastrar.")

    def _rotulos_cadastro(self):
        rotulos = {}
        for grupo in self._grupos:
            rotulo = self._rotulo_grupo(grupo)
            item = self._associacoes_nf.get(grupo)
            if item and self._nota_fiscal:
                rotulo = f"NF {self._numero_nf(self._nota_fiscal)} · item {item.numero} · {rotulo}"
            rotulos[grupo] = rotulo
        return rotulos

    def iniciar_cadastro(self):
        if self._executando or not getattr(self, "bobinas", None):
            return
        numero_romaneio = self.numero_romaneio.get().strip()
        if not numero_romaneio:
            self._mostrar_mensagem("Número do romaneio",
                "Informe o número do romaneio no campo ao lado do fornecedor para registrar o histórico.", "alerta")
            self.campo_romaneio.focus_set()
            return
        if self._janela_historico and self._janela_historico.winfo_exists():
            self._janela_historico.bloquear()
        self._executando = True
        self._controle = ControleCadastro()
        self._concluidas = 0
        self._total_execucao = len(self.bobinas)
        self.progresso.set(0)
        self.rotulo_progresso.configure(text="0%")
        self._definir_estado("Em andamento")
        self.status.configure(text="Preparando cadastro...")
        for botao in (self.botao_pdf, self.combo_fornecedor, self.botao_cadastro,
                      self.botao_historico, self.botao_nf, self.campo_romaneio):
            botao.configure(state="disabled")
        self.botao_pausa.configure(state="normal", text="Pausar")
        self.botao_interromper.configure(state="normal")
        self._thread = Thread(target=self.executar_cadastro,
                              args=(list(self.bobinas), self.ajuste_peso, self._controle,
                                    self._rotulos_cadastro(), numero_romaneio),
                              daemon=False)
        self._thread.start()

    def executar_cadastro(self, bobinas, ajuste_peso, controle, rotulos_grupos=None,
                          numero_romaneio=None):
        # A thread de trabalho só publica mensagens; widgets pertencem
        # exclusivamente à thread principal do Tkinter.
        def evento(tipo, **dados):
            self._eventos.put((tipo, dados))

        def solicitar(mensagem, opcoes):
            pedido = {"mensagem": mensagem, "opcoes": opcoes,
                      "pronto": Event(), "resposta": None}
            evento("confirmacao", pedido=pedido)
            while not pedido["pronto"].wait(0.1):
                controle.verificar()
            controle.verificar()
            return pedido["resposta"]

        try:
            resultado = CadastroBobinas().iniciar(
                bobinas, ajuste_peso, controle=controle,
                evento=evento, solicitar=solicitar, rotulos_grupos=rotulos_grupos,
                numero_romaneio=numero_romaneio)
            evento("finalizado", resultado=resultado)
        except Exception as erro:
            logger.exception("Cadastro encerrado por erro")
            evento("erro", texto=str(erro))

    def processar_eventos(self):
        try:
            while True:
                tipo, dados = self._eventos.get_nowait()
                if tipo in ("status", "progresso"):
                    texto = dados["texto"]
                    if self._controle and self._controle.pausado:
                        texto += " | Pausa solicitada; aguardando continuar."
                    self.status.configure(text=texto)
                    if tipo == "progresso":
                        total = dados["total"]
                        self._concluidas = dados["concluidas"]
                        self._total_execucao = total
                        fracao = self._concluidas / total if total else 0
                        self.progresso.set(fracao)
                        self.rotulo_progresso.configure(text=f"{fracao:.0%}")
                elif tipo == "confirmacao":
                    self._fechar_confirmacao()
                    self._pedido = dados["pedido"]
                    texto = self._pedido["mensagem"].replace(
                        "Pressione ENTER", "Clique em Continuar")
                    opcoes = self._pedido["opcoes"]
                    self._definir_estado("Aguardando sua confirmação", "alerta")
                    self._dialogo_confirmacao = Dialogo(
                        self, "Escolha a classificação" if opcoes else "Confira o sistema",
                        texto, confirmar=self.confirmar_etapa,
                        cancelar=self.interromper_cadastro, opcoes=opcoes,
                        acao="Continuar", tom="alerta")
                elif tipo in ("finalizado", "erro"):
                    self.encerrar_cadastro(tipo, dados)
        except Empty:
            pass
        if self._fechando and not self._thread.is_alive():
            self.destroy()
            return
        self._timer_eventos = self.after(100, self.processar_eventos)

    def confirmar_etapa(self, resposta=""):
        if self._pedido:
            self._pedido["resposta"] = resposta if self._pedido["opcoes"] else ""
            self._pedido["pronto"].set()
            self._pedido = None
            self._fechar_confirmacao()
            pausado = self._controle and self._controle.pausado
            self._definir_estado("Pausa solicitada" if pausado else "Em andamento",
                                 "alerta" if pausado else "muted")

    def alternar_pausa(self):
        if not self._executando:
            return
        if self._controle.pausado:
            self._controle.continuar()
            self.botao_pausa.configure(text="Pausar")
            self._definir_estado("Em andamento")
            self.status.configure(text="Continuando cadastro...")
        else:
            self._controle.pausar()
            self.botao_pausa.configure(text="Continuar")
            self._definir_estado("Pausa solicitada", "alerta")
            self.status.configure(text="Pausa solicitada. A bobina em andamento será concluída.")

    def interromper_cadastro(self):
        if self._executando:
            self._controle.interromper()
            self.botao_pausa.configure(state="disabled")
            self.botao_interromper.configure(state="disabled")
            self._fechar_confirmacao()
            self._definir_estado("Interrompendo", "alerta")
            self.status.configure(text="Interrompendo após a operação em andamento...")

    def encerrar_cadastro(self, tipo, dados):
        self._executando = False
        self._pedido = None
        self._fechar_confirmacao()
        self.botao_pausa.configure(state="disabled", text="Pausar")
        self.botao_interromper.configure(state="disabled")
        if self._fechando:
            return
        self.botao_pdf.configure(state="normal")
        self.combo_fornecedor.configure(state="normal")
        self.campo_romaneio.configure(state="normal" if self.bobinas else "disabled")
        self.botao_cadastro.configure(state="normal" if self.bobinas else "disabled")
        self.botao_historico.configure(state="normal")
        self.botao_nf.configure(state="normal" if self.bobinas else "disabled")
        if tipo == "erro":
            self.status.configure(text="Cadastro encerrado por erro. Confira o sistema antes de retomar.")
            self._definir_estado("Erro no cadastro", "erro")
            self._mostrar_mensagem("Erro no cadastro", dados["texto"], "erro")
        else:
            resultado = dados["resultado"]
            titulo = "Cadastro interrompido" if resultado["interrompido"] else "Cadastro finalizado"
            motivo = resultado.get("motivo_parada", "")
            if motivo:
                titulo = "Cadastro parado para conferência"
            pendentes = resultado["total"] - resultado["sucessos"] - resultado["falhas"]
            texto = (f"{titulo}: {resultado['sucessos']} cadastradas, "
                     f"{resultado['falhas']} falhas, {pendentes} não processadas e "
                     f"{resultado['ignoradas']} já no histórico.")
            if motivo:
                texto += "\n" + motivo
            self.status.configure(text=texto)
            processadas = resultado["sucessos"] + resultado["falhas"]
            fracao = processadas / resultado["total"] if resultado["total"] else 1
            self.progresso.set(fracao)
            self.rotulo_progresso.configure(text=f"{fracao:.0%}")
            tom = "alerta" if motivo or resultado["interrompido"] or resultado["falhas"] else "sucesso"
            self._definir_estado(titulo, tom)
            self._mostrar_mensagem(titulo, texto, tom)

    def fechar_janela(self):
        if not self._executando:
            self.destroy()
            return
        self._fechando = True
        self.interromper_cadastro()
        self.status.configure(text="Encerrando a operação em andamento para fechar...")

    def destroy(self):
        if getattr(self, "_timer_eventos", None):
            self.after_cancel(self._timer_eventos)
            self._timer_eventos = None
        self._fechar_confirmacao()
        if self._dialogo_nf and self._dialogo_nf.winfo_exists():
            self._dialogo_nf.fechar()
        if self._janela_historico and self._janela_historico.winfo_exists():
            self._janela_historico.fechar()
        super().destroy()

    def exportar_excel(self):

        if not getattr(self, "bobinas", None):
            return

        caminho = filedialog.asksaveasfilename(
            parent=self,
            title="Salvar como",
            defaultextension=".xlsx",
            filetypes=[("Planilha Excel", "*.xlsx")]
        )

        if not caminho:
            return

        workbook = Workbook()
        planilha = workbook.active
        planilha.title = "Bobinas"

        planilha.append([
            "Bobina",
            "Produto",
            "Gramatura",
            "Formato",
            "Diâmetro",
            "Peso",
            "Rua"
        ])

        for bobina in self.bobinas:

            planilha.append([
                bobina.numero,
                bobina.produto,
                bobina.gramatura,
                bobina.formato,
                bobina.diametro,
                bobina.peso,
                bobina.rua
            ])

        try:
            workbook.save(caminho)
        except OSError:
            self._mostrar_mensagem("Não foi possível exportar",
                "Confira se a planilha está aberta no Excel e se você pode gravar na pasta escolhida.", "erro")
            return
        self._mostrar_mensagem("Exportação concluída", f"Planilha salva em:\n{caminho}", "sucesso")
