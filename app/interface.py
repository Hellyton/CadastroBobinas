import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
from queue import Queue, Empty
from threading import Thread, Event
from openpyxl import Workbook
from app.cadastro import CadastroBobinas
from app.controle import ControleCadastro
from app.logger import logger

from app.leitor_pdf import ler_romaneio


# Aparência
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Cadastro Automático de Bobinas")
        self.geometry("1000x780")
        self.minsize(900, 700)
        self._eventos = Queue()
        self._executando = False
        self._fechando = False
        self._pedido = None
        self._controle = None
        self.protocol("WM_DELETE_WINDOW", self.fechar_janela)

        # ==========================
        # Título
        # ==========================
        self.titulo = ctk.CTkLabel(
            self,
            text="Cadastro Automático de Bobinas",
            font=("Arial", 24, "bold")
        )
        self.titulo.pack(pady=(20, 10))

        # ==========================
        # Botão selecionar PDF
        # ==========================
        self.botao_pdf = ctk.CTkButton(
            self,
            text="Selecionar Romaneio",
            command=self.abrir_pdf
        )

        self.botao_pdf.pack()

        # ==========================
        # Nome do arquivo
        # ==========================
        self.arquivo = ctk.CTkLabel(
            self,
            text="Nenhum arquivo selecionado"
        )

        self.arquivo.pack(pady=10)

        # ==========================
        # Fornecedor (detectado ou manual)
        # ==========================
        self.frame_fornecedor = ctk.CTkFrame(self, fg_color="transparent")

        self.frame_fornecedor.pack(pady=(0, 10))

        self.label_fornecedor = ctk.CTkLabel(
            self.frame_fornecedor,
            text="Fornecedor:"
        )

        self.label_fornecedor.pack(side="left", padx=(0, 10))

        self.combo_fornecedor = ctk.CTkOptionMenu(
            self.frame_fornecedor,
            values=[
                "Detectar automaticamente", "ADF", "HP", "Novakraft", "Cocelpa"
            ],
            command=self.fornecedor_alterado
        )

        self.combo_fornecedor.set("Detectar automaticamente")

        self.combo_fornecedor.pack(side="left")

        self.caminho_pdf = None
        self.ajuste_peso = 0

        # ==========================
        # Total de bobinas
        # ==========================
        self.total = ctk.CTkLabel(
            self,
            text="Bobinas encontradas: 0  |  Peso total: 0 kg",
            font=("Arial", 16)
        )

        self.total.pack(pady=(0, 15))

        # ==========================
        # Frame da tabela
        # ==========================
        self.frame_tabela = ctk.CTkFrame(self)

        self.frame_tabela.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        # ==========================
        # Tabela
        # ==========================
        colunas = (
            "numero",
            "produto",
            "gramatura",
            "formato",
            "diametro",
            "peso"
        )

        self.tabela = ttk.Treeview(
            self.frame_tabela,
            columns=colunas,
            show="headings",
            height=18
        )

        self.tabela.heading("numero", text="Bobina")
        self.tabela.heading("produto", text="Produto")
        self.tabela.heading("gramatura", text="Gramatura")
        self.tabela.heading("formato", text="Formato")
        self.tabela.heading("diametro", text="Diâmetro")
        self.tabela.heading("peso", text="Peso")

        self.tabela.column("numero", width=100, anchor="center")
        self.tabela.column("produto", width=180, anchor="center")
        self.tabela.column("gramatura", width=100, anchor="center")
        self.tabela.column("formato", width=100, anchor="center")
        self.tabela.column("diametro", width=100, anchor="center")
        self.tabela.column("peso", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(
            self.frame_tabela,
            orient="vertical",
            command=self.tabela.yview
        )

        self.tabela.configure(yscrollcommand=scrollbar.set)

        self.tabela.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.status = ctk.CTkLabel(self, text="Selecione um romaneio para começar.",
                                   wraplength=900)
        self.status.pack(padx=20, pady=(2, 0))
        self.progresso = ctk.CTkProgressBar(self)
        self.progresso.set(0)
        self.progresso.pack(fill="x", padx=20, pady=5)

        self.frame_confirmacao = ctk.CTkFrame(self)
        self.instrucao = ctk.CTkLabel(self.frame_confirmacao, text="",
                                     wraplength=850, justify="left")
        self.instrucao.pack(padx=10, pady=5)
        self.escolha_produto = ctk.CTkOptionMenu(self.frame_confirmacao, values=[""])
        self.botao_confirmar = ctk.CTkButton(self.frame_confirmacao,
                                            text="Continuar", command=self.confirmar_etapa)
        self.botao_confirmar.pack(pady=5)

        # ==========================
        # Frame dos botões
        # ==========================
        self.frame_botoes = ctk.CTkFrame(self)

        self.frame_botoes.pack(
            fill="x",
            padx=20,
            pady=15
        )

        self.botao_exportar = ctk.CTkButton(
            self.frame_botoes,
            text="Exportar Excel",
            state="disabled",
            command=self.exportar_excel
        )

        self.botao_exportar.pack(
            side="left",
            padx=10
        )

        self.botao_cadastro = ctk.CTkButton(
            self.frame_botoes,
            text="Iniciar Cadastro",
            state="disabled",
            command=self.iniciar_cadastro
            
        )

        self.botao_cadastro.pack(
            side="right",
            padx=10
        )

        self.botao_pausa = ctk.CTkButton(self.frame_botoes, text="Pausar",
                                        state="disabled", command=self.alternar_pausa)
        self.botao_pausa.pack(side="left", padx=10)
        self.botao_interromper = ctk.CTkButton(self.frame_botoes, text="Interromper",
                                              state="disabled", command=self.interromper_cadastro)
        self.botao_interromper.pack(side="left", padx=10)
        self.after(100, self.processar_eventos)

    def abrir_pdf(self):

        caminho = filedialog.askopenfilename(
            title="Selecione o Romaneio",
            filetypes=[("Arquivos PDF", "*.pdf")]
        )

        if not caminho:
            return

        self.caminho_pdf = caminho

        self.arquivo.configure(
            text=os.path.basename(caminho)
        )

        self.combo_fornecedor.set("Detectar automaticamente")

        self.processar_pdf(fornecedor=None)

    def fornecedor_alterado(self, valor):

        if not self.caminho_pdf:
            return

        fornecedor = None if valor == "Detectar automaticamente" else valor

        self.processar_pdf(fornecedor=fornecedor)

    def processar_pdf(self, fornecedor):

        self.bobinas, fornecedor_usado, self.ajuste_peso = ler_romaneio(
            self.caminho_pdf,
            fornecedor=fornecedor
        )

        # Grava o fornecedor em cada bobina (o modelo Bobina não sabe
        # disso sozinho, o ler_romaneio() retorna separado) - necessário
        # pro histórico não confundir bobinas de fornecedores diferentes
        # que por coincidência tenham o mesmo número.
        for bobina in self.bobinas:
            bobina.fornecedor = fornecedor_usado or ""

        if fornecedor_usado is None:
            messagebox.showwarning(
                "Fornecedor não reconhecido",
                "Não consegui identificar o fornecedor desse romaneio "
                "automaticamente. Selecione o fornecedor correto na "
                "lista para continuar."
            )
        elif fornecedor is None:
            # Detecção automática deu certo: reflete o resultado no combo
            self.combo_fornecedor.set(fornecedor_usado)

        # Limpa a tabela
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        # Insere as novas linhas
        for bobina in self.bobinas:

            self.tabela.insert(
                "",
                "end",
                values=(
                    bobina.numero,
                    bobina.produto,
                    bobina.gramatura,
                    bobina.formato,
                    bobina.diametro,
                    bobina.peso
                )
            )

        peso_bobinas = sum(bobina.peso for bobina in self.bobinas)
        peso_liquido = peso_bobinas + self.ajuste_peso

        if self.ajuste_peso:
            texto_peso = (
                f"Peso total: {peso_liquido:,} kg "
                f"(bobinas: {peso_bobinas:,} kg, "
                f"ajuste do romaneio: {self.ajuste_peso:,} kg)"
            ).replace(",", ".")
        else:
            texto_peso = f"Peso total: {peso_bobinas:,} kg".replace(",", ".")

        self.total.configure(
            text=f"Bobinas encontradas: {len(self.bobinas)}  |  {texto_peso}"
        )

        if len(self.bobinas) > 0:
            self.botao_exportar.configure(state="normal")
            self.botao_cadastro.configure(state="normal")
        else:
            self.botao_exportar.configure(state="disabled")
            self.botao_cadastro.configure(state="disabled")

    def iniciar_cadastro(self):
        if self._executando or not getattr(self, "bobinas", None):
            return
        self._executando = True
        self._controle = ControleCadastro()
        self.progresso.set(0)
        self.status.configure(text="Preparando cadastro...")
        for botao in (self.botao_pdf, self.combo_fornecedor, self.botao_cadastro):
            botao.configure(state="disabled")
        self.botao_pausa.configure(state="normal", text="Pausar")
        self.botao_interromper.configure(state="normal")
        self._thread = Thread(target=self.executar_cadastro,
                              args=(list(self.bobinas), self.ajuste_peso, self._controle),
                              daemon=False)
        self._thread.start()

    def executar_cadastro(self, bobinas, ajuste_peso, controle):
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
                evento=evento, solicitar=solicitar)
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
                        self.progresso.set(dados["concluidas"] / total if total else 0)
                elif tipo == "confirmacao":
                    self._pedido = dados["pedido"]
                    texto = self._pedido["mensagem"].replace(
                        "Pressione ENTER", "Clique em Continuar")
                    self.instrucao.configure(text=texto)
                    opcoes = self._pedido["opcoes"]
                    if opcoes:
                        self.escolha_produto.configure(values=opcoes)
                        self.escolha_produto.set(opcoes[0])
                        self.escolha_produto.pack(before=self.botao_confirmar, pady=5)
                    else:
                        self.escolha_produto.pack_forget()
                    self.frame_confirmacao.pack(before=self.frame_botoes, fill="x", padx=20)
                elif tipo in ("finalizado", "erro"):
                    self.encerrar_cadastro(tipo, dados)
        except Empty:
            pass
        if self._fechando and not self._thread.is_alive():
            self.destroy()
            return
        self.after(100, self.processar_eventos)

    def confirmar_etapa(self):
        if self._pedido:
            self._pedido["resposta"] = (
                self.escolha_produto.get() if self._pedido["opcoes"] else "")
            self._pedido["pronto"].set()
            self._pedido = None
            self.frame_confirmacao.pack_forget()

    def alternar_pausa(self):
        if not self._executando:
            return
        if self._controle.pausado:
            self._controle.continuar()
            self.botao_pausa.configure(text="Pausar")
            self.status.configure(text="Continuando cadastro...")
        else:
            self._controle.pausar()
            self.botao_pausa.configure(text="Continuar")
            self.status.configure(text="Pausa solicitada. A bobina em andamento será concluída.")

    def interromper_cadastro(self):
        if self._executando:
            self._controle.interromper()
            self.botao_pausa.configure(state="disabled")
            self.botao_interromper.configure(state="disabled")
            self.frame_confirmacao.pack_forget()
            self.status.configure(text="Interrompendo após a operação em andamento...")

    def encerrar_cadastro(self, tipo, dados):
        self._executando = False
        self._pedido = None
        self.frame_confirmacao.pack_forget()
        self.botao_pausa.configure(state="disabled", text="Pausar")
        self.botao_interromper.configure(state="disabled")
        if self._fechando:
            return
        self.botao_pdf.configure(state="normal")
        self.combo_fornecedor.configure(state="normal")
        self.botao_cadastro.configure(state="normal" if self.bobinas else "disabled")
        if tipo == "erro":
            self.status.configure(text="Cadastro encerrado por erro. Confira o sistema antes de retomar.")
            messagebox.showerror("Erro no cadastro", dados["texto"], parent=self)
        else:
            resultado = dados["resultado"]
            titulo = "Cadastro interrompido" if resultado["interrompido"] else "Cadastro finalizado"
            pendentes = resultado["total"] - resultado["sucessos"] - resultado["falhas"]
            texto = (f"{titulo}: {resultado['sucessos']} cadastradas, "
                     f"{resultado['falhas']} falhas, {pendentes} não processadas e "
                     f"{resultado['ignoradas']} já no histórico.")
            self.status.configure(text=texto)
            messagebox.showinfo(titulo, texto, parent=self)

    def fechar_janela(self):
        if not self._executando:
            self.destroy()
            return
        self._fechando = True
        self.interromper_cadastro()
        self.status.configure(text="Encerrando a operação em andamento para fechar...")

    def exportar_excel(self):

        if not getattr(self, "bobinas", None):
            return

        caminho = filedialog.asksaveasfilename(
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

        workbook.save(caminho)

        messagebox.showinfo(
            "Exportação concluída",
            f"Planilha salva em:\n{caminho}"
        )
