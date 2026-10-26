"""Indicadores e diálogos do aplicativo. Todos pertencem à thread do Tk."""

import customtkinter as ctk
from app.tema import CORES, texto, botao, menu


class Indicador(ctk.CTkFrame):
    def __init__(self, master, titulo, valor, legenda, compacto=False):
        super().__init__(master, fg_color=CORES["cartao"],
                         border_color=CORES["borda"], border_width=1, corner_radius=10)
        self.grid_columnconfigure(0, weight=1)
        margem = (10, 10) if compacto else (12, 0)
        texto(self, titulo, 12, "muted").grid(row=0, column=0, sticky="w", padx=(16, 6), pady=margem)
        self.valor = texto(self, valor, 24, negrito=True)
        self.valor.grid(row=0, column=1, sticky="e", padx=(0, 16), pady=margem)
        self.legenda = texto(self, legenda, 11, "muted")
        if not compacto:
            self.legenda.grid(row=1, column=0, columnspan=2, sticky="w", padx=16, pady=(4, 12))

    def atualizar(self, valor, legenda=None):
        self.valor.configure(text=valor)
        if legenda is not None:
            self.legenda.configure(text=legenda)


class Dialogo(ctk.CTkToplevel):
    """Diálogo escuro com mensagem rolável e escolha opcional de produto."""

    def __init__(self, master, titulo, mensagem, confirmar=None, cancelar=None,
                 opcoes=None, acao="Entendi", tom="muted",
                 texto_cancelar="Interromper cadastro", altura=None):
        super().__init__(master)
        self.withdraw()
        self.title(titulo)
        self.configure(fg_color=CORES["fundo"])
        self.transient(master)
        self.minsize(480, 300)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._confirmar = confirmar
        self._cancelar = cancelar
        self._texto_cancelar = texto_cancelar
        self.protocol("WM_DELETE_WINDOW", self.cancelar)
        self.bind("<Escape>", lambda event: self.cancelar())

        texto(self, "CONFIRMAÇÃO NECESSÁRIA" if opcoes or cancelar else "BOBINAS",
              11, tom, True).grid(row=0, column=0, sticky="w", padx=24, pady=(22, 4))
        texto(self, titulo, 22, negrito=True).grid(row=1, column=0, sticky="w", padx=24, pady=(0, 14))
        self.mensagem = ctk.CTkTextbox(
            self, fg_color=CORES["cartao"], text_color=CORES["texto"],
            border_color=CORES["borda"], border_width=1, corner_radius=8,
            font=("Segoe UI", 13), wrap="word", height=150,
            scrollbar_button_color=CORES["borda"],
            scrollbar_button_hover_color=CORES["hover"]
        )
        self.mensagem.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 14))
        self.mensagem.insert("1.0", mensagem)
        self.mensagem.configure(state="disabled")
        self.escolha = None
        if opcoes:
            self.escolha = menu(self, opcoes, width=400)
            self.escolha.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 16))
            self.escolha.set(opcoes[0])
        acoes = ctk.CTkFrame(self, fg_color="transparent")
        acoes.grid(row=4, column=0, sticky="ew", padx=24, pady=(0, 22))
        acoes.grid_columnconfigure(0, weight=1)
        if cancelar:
            botao(acoes, self._texto_cancelar, self.cancelar, "perigo", width=170).grid(row=0, column=0, sticky="w")
        self.botao_confirmar = botao(acoes, acao, self.confirmar, "primario", width=140)
        self.botao_confirmar.grid(row=0, column=1, sticky="e")

        escala = self._get_window_scaling()
        largura = min(600, round(master.winfo_screenwidth() / escala) - 40)
        altura = min(altura or (440 if opcoes else 380), round(master.winfo_screenheight() / escala) - 90)
        master.update_idletasks()
        x = max(0, master.winfo_rootx() + round((master.winfo_width() - largura * escala) / 2))
        y = max(0, master.winfo_rooty() + round((master.winfo_height() - altura * escala) / 2))
        self.geometry(f"{largura}x{altura}+{x}+{y}")
        self.deiconify()
        self.lift()
        self.grab_set()
        self._timer_foco = self.after(100, self.botao_confirmar.focus_set)

    def confirmar(self):
        resposta = self.escolha.get() if self.escolha else ""
        self.fechar()
        if self._confirmar:
            self._confirmar(resposta)

    def cancelar(self):
        self.fechar()
        if self._cancelar:
            self._cancelar()

    def fechar(self):
        if self.winfo_exists():
            self.after_cancel(self._timer_foco)
            self.grab_release()
            self.destroy()
