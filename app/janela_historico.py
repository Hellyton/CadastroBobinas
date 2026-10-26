"""Consulta e manutenção do histórico local de bobinas."""

import customtkinter as ctk
from tkinter import StringVar, ttk

from app.componentes import Dialogo
from app.historico import (
    HistoricoInvalido, adicionar_cadastrada, editar_registro,
    excluir_registro, listar_registros,
)
from app.tema import CORES, botao, configurar_tabela, menu, texto


FORNECEDORES = ("ADF", "HP", "Novakraft", "Cocelpa")
TODOS_ROMANEIOS = "Todos os romaneios"
SEM_ROMANEIO = "Sem romaneio"


class JanelaHistorico(ctk.CTkToplevel):
    """Editor modal: números são texto e só há os dados presentes no JSON."""

    def __init__(self, master, ao_fechar=None, caminho=None):
        super().__init__(master)
        self.withdraw()
        self.master_app = master
        self._ao_fechar = ao_fechar
        self.caminho = caminho
        self._chave_selecionada = None
        self._dialogo = None
        self._fechada = False
        self.busca = StringVar(master=self, value="")
        self.title("Histórico de bobinas")
        self.configure(fg_color=CORES["fundo"])
        escala = self._get_window_scaling()
        largura = min(760, round(master.winfo_screenwidth() / escala) - 40)
        altura = min(570, round(master.winfo_screenheight() / escala) - 80)
        self.minsize(min(580, largura), min(440, altura))
        master.update_idletasks()
        x = max(0, master.winfo_rootx() + round((master.winfo_width() - largura * escala) / 2))
        y = max(0, master.winfo_rooty() + round((master.winfo_height() - altura * escala) / 2))
        self.geometry(f"{largura}x{altura}+{x}+{y}")
        self.transient(master)
        self.protocol("WM_DELETE_WINDOW", self.fechar)
        self.bind("<Escape>", lambda evento: self.fechar())
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        texto(self, "HISTÓRICO LOCAL", 11, "muted", True).grid(
            row=0, column=0, sticky="w", padx=22, pady=(20, 4))
        texto(self, "Bobinas marcadas como cadastradas", 21, negrito=True).grid(
            row=1, column=0, sticky="w", padx=22, pady=(0, 10))

        self.tabela_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tabela_frame.grid(row=2, column=0, sticky="nsew", padx=22)
        self.tabela_frame.grid_columnconfigure(0, weight=1)
        self.tabela_frame.grid_rowconfigure(1, weight=1)
        configurar_tabela(self.tabela_frame)
        filtros = ctk.CTkFrame(self.tabela_frame, fg_color="transparent")
        filtros.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        filtros.grid_columnconfigure(0, weight=1)
        self.campo_busca = ctk.CTkEntry(
            filtros,
            placeholder_text="Buscar fornecedor, bobina ou romaneio...", height=34,
            fg_color=CORES["fundo"], border_color=CORES["borda"],
            text_color=CORES["texto"], placeholder_text_color=CORES["discreto"])
        self.campo_busca.grid(row=0, column=0, sticky="ew")
        self.filtro_romaneio = menu(filtros, [TODOS_ROMANEIOS, SEM_ROMANEIO],
            lambda valor: self._recarregar(), width=175)
        self.filtro_romaneio.grid(row=0, column=1, padx=(10, 0))
        self.campo_busca.bind(
            "<KeyRelease>", lambda evento: self.busca.set(self.campo_busca.get()))
        self.tabela = ttk.Treeview(
            self.tabela_frame, columns=("romaneio", "fornecedor", "numero"),
            show="headings", style="Bobinas.Treeview", selectmode="browse")
        self.tabela.heading("fornecedor", text="Fornecedor")
        self.tabela.heading("numero", text="Bobina")
        self.tabela.heading("romaneio", text="Romaneio")
        self.tabela.column("romaneio", width=150, minwidth=100, anchor="w")
        self.tabela.column("fornecedor", width=190, minwidth=110, anchor="w")
        self.tabela.column("numero", width=220, minwidth=120, anchor="w")
        self.tabela.grid(row=1, column=0, sticky="nsew")
        barra = ctk.CTkScrollbar(self.tabela_frame, command=self.tabela.yview,
            fg_color=CORES["cartao"], button_color=CORES["borda"],
            button_hover_color=CORES["discreto"], width=10)
        barra.grid(row=1, column=1, sticky="ns")
        self.tabela.configure(yscrollcommand=barra.set)
        self.tabela.bind("<<TreeviewSelect>>", self._selecionar)

        texto(self, "Registros antigos podem aparecer sem fornecedor ou sem romaneio.",
              11, "muted").grid(row=3, column=0, sticky="w", padx=22, pady=(7, 3))
        self.aviso_efeitos = texto(self,
              "Adicionar marca apenas o controle local; não cadastra a bobina no EGS. "
              "Excluir remove a prevenção local e pode permitir recadastro.",
              11, "alerta", wraplength=max(300, largura - 44), justify="left")
        self.aviso_efeitos.grid(row=4, column=0, sticky="ew", padx=22, pady=(0, 12))

        formulario = ctk.CTkFrame(self, fg_color=CORES["cartao"],
                                   border_color=CORES["borda"], border_width=1,
                                   corner_radius=9)
        formulario.grid(row=5, column=0, sticky="ew", padx=22)
        formulario.grid_columnconfigure((0, 1, 2), weight=1)
        texto(formulario, "Fornecedor", 11, "muted").grid(
            row=0, column=0, sticky="w", padx=(14, 8), pady=(12, 4))
        texto(formulario, "Número da bobina", 11, "muted").grid(
            row=0, column=1, sticky="w", padx=8, pady=(12, 4))
        texto(formulario, "Nº do romaneio", 11, "muted").grid(
            row=0, column=2, sticky="w", padx=8, pady=(12, 4))
        self.fornecedor = ctk.CTkEntry(
            formulario, placeholder_text="Ex.: ADF",
            fg_color=CORES["fundo"], border_color=CORES["borda"],
            text_color=CORES["texto"], height=34)
        self.fornecedor.grid(row=1, column=0, sticky="ew", padx=(14, 8), pady=(0, 12))
        self.numero = ctk.CTkEntry(
            formulario, placeholder_text="Número mantido como texto",
            fg_color=CORES["fundo"], border_color=CORES["borda"],
            text_color=CORES["texto"], height=34)
        self.numero.grid(row=1, column=1, sticky="ew", padx=8, pady=(0, 12))
        self.romaneio = ctk.CTkEntry(
            formulario, placeholder_text="Número do romaneio", width=140,
            fg_color=CORES["fundo"], border_color=CORES["borda"],
            text_color=CORES["texto"], height=34)
        self.romaneio.grid(row=1, column=2, sticky="ew", padx=(8, 14), pady=(0, 12))
        self.mensagem = texto(self, "", 11, "erro", wraplength=700, justify="left")
        self.mensagem.grid(row=6, column=0, sticky="w", padx=22, pady=(5, 0))

        acoes = ctk.CTkFrame(self, fg_color="transparent")
        acoes.grid(row=7, column=0, sticky="ew", padx=22, pady=(8, 18))
        acoes.grid_columnconfigure(0, weight=1)
        self.botao_adicionar = botao(acoes, "Adicionar manualmente",
                                      self._confirmar_adicao, "primario", width=190)
        self.botao_adicionar.grid(row=0, column=0, sticky="w")
        self.botao_editar = botao(acoes, "Editar", self._confirmar_edicao, width=90,
                                  state="disabled")
        self.botao_editar.grid(row=0, column=1, padx=(8, 0))
        self.botao_excluir = botao(acoes, "Excluir", self._confirmar_exclusao,
            "perigo", width=90, state="disabled")
        self.botao_excluir.grid(row=0, column=2, padx=(8, 0))
        botao(acoes, "Fechar", self.fechar, width=90).grid(
            row=0, column=3, padx=(8, 0))

        self._recarregar()
        self.busca.trace_add("write", lambda *_: self._recarregar())
        self.bind("<Configure>", self._ajustar_aviso)
        self.deiconify()
        self.lift()
        self.grab_set()
        self._timer_foco = self.after(100, self.focus_set)

    def _recarregar(self, selecionar=None):
        consulta_texto = self.busca.get()
        if self.campo_busca.get() != consulta_texto:
            self.campo_busca.delete(0, "end")
            if consulta_texto:
                self.campo_busca.insert(0, consulta_texto)
        self.tabela.delete(*self.tabela.get_children())
        self._limpar_selecao()
        try:
            registros = listar_registros(self.caminho)
        except HistoricoInvalido as erro:
            self._erro(str(erro))
            return
        consulta = self.busca.get().strip().casefold()
        romaneios = sorted({r["romaneio"] for r in registros if r["romaneio"]})
        opcoes = [TODOS_ROMANEIOS, SEM_ROMANEIO] + romaneios
        self.filtro_romaneio.configure(values=opcoes)
        if self.filtro_romaneio.get() not in opcoes:
            self.filtro_romaneio.set(TODOS_ROMANEIOS)
        filtro = self.filtro_romaneio.get()
        for registro in registros:
            chave = registro["chave"]
            fornecedor = registro["fornecedor"] or "Sem fornecedor (legado)"
            romaneio = registro["romaneio"] or SEM_ROMANEIO
            if filtro == SEM_ROMANEIO and registro["romaneio"]:
                continue
            if filtro not in (TODOS_ROMANEIOS, SEM_ROMANEIO) and registro["romaneio"] != filtro:
                continue
            if consulta and not any(consulta in valor.casefold()
                    for valor in (fornecedor, registro["numero"], romaneio)):
                continue
            self.tabela.insert("", "end", iid=chave,
                               values=(romaneio, fornecedor, registro["numero"]))
        if selecionar in self.tabela.get_children():
            self.tabela.selection_set(selecionar)
            self.tabela.see(selecionar)
            self._selecionar()
        else:
            self._limpar_selecao()

    def _ajustar_aviso(self, evento):
        if evento.widget is not self or not getattr(self, "aviso_efeitos", None):
            return
        escala = self._get_window_scaling()
        self.aviso_efeitos.configure(
            wraplength=max(300, round(evento.width / escala) - 44))

    def _limpar_selecao(self):
        self._chave_selecionada = None
        self.botao_editar.configure(state="disabled")
        self.botao_excluir.configure(state="disabled")

    def _selecionar(self, evento=None):
        selecao = self.tabela.selection()
        if not selecao:
            self._limpar_selecao()
            return
        chave = selecao[0]
        try:
            registro = next((item for item in listar_registros(self.caminho)
                             if item["chave"] == chave), None)
        except HistoricoInvalido as erro:
            self._erro(str(erro))
            return
        if registro is None:
            self._limpar_selecao()
            return
        self._chave_selecionada = chave
        self._definir_campo(self.fornecedor, registro["fornecedor"])
        self._definir_campo(self.numero, registro["numero"])
        self._definir_campo(self.romaneio, registro["romaneio"])
        self.botao_editar.configure(state="normal")
        self.botao_excluir.configure(state="normal")
        self._erro("")

    @staticmethod
    def _definir_campo(campo, valor):
        campo.delete(0, "end")
        campo.insert(0, valor)

    def _erro(self, mensagem):
        self.mensagem.configure(text=mensagem)

    def _restaurar_grab(self):
        if not self._fechada and self.winfo_exists():
            self.grab_set()

    def _confirmar_adicao(self):
        fornecedor, numero = self.fornecedor.get(), self.numero.get()
        romaneio = self.romaneio.get().strip()
        self._erro("")
        if not fornecedor.strip() or not numero.strip():
            self._erro("Informe fornecedor e número da bobina.")
            return
        if not romaneio:
            self._erro("Informe o número do romaneio para adicionar ao histórico.")
            return
        texto_confirmacao = (
            f"Marcar {fornecedor.strip()} | {numero} (romaneio {romaneio}) "
            "como já cadastrada no controle local?\n\n"
            "Isso não envia nem cadastra a bobina no EGS. A prevenção de recadastro "
            "passará a ignorá-la nas próximas execuções com histórico habilitado.")
        self._dialogo = Dialogo(self, "Adicionar ao histórico local", texto_confirmacao,
                confirmar=lambda resposta="": self._adicionar(fornecedor, numero, romaneio),
                cancelar=self._restaurar_grab, acao="Marcar localmente", tom="alerta",
                texto_cancelar="Cancelar")

    def _adicionar(self, fornecedor, numero, romaneio):
        try:
            adicionar_cadastrada(numero, fornecedor, self.caminho, romaneio=romaneio)
        except (HistoricoInvalido, ValueError) as erro:
            self._erro(str(erro))
        else:
            self._erro("Marcada somente no histórico local; nenhuma ação foi feita no EGS.")
            self._definir_campo(self.fornecedor, "")
            self._definir_campo(self.numero, "")
            self._definir_campo(self.romaneio, "")
            self._recarregar()
        self._restaurar_grab()

    def _confirmar_edicao(self):
        if not self._chave_selecionada:
            return
        fornecedor, numero = self.fornecedor.get(), self.numero.get()
        romaneio = self.romaneio.get().strip()
        self._erro("")
        if not fornecedor.strip() or not numero.strip():
            self._erro("Informe fornecedor e número da bobina.")
            return
        nova = f"{fornecedor.strip()} | {numero}"
        nova_chave = f"{fornecedor.strip().upper()}|{numero.strip()}"
        efeito = ("A chave anterior deixará de impedir recadastro; a nova chave passará "
                  "a ser reconhecida nas próximas execuções com histórico habilitado."
                  if nova_chave != self._chave_selecionada else
                  "O romaneio será usado na busca e no filtro do histórico. "
                  "A prevenção de recadastro continua vinculada ao fornecedor e à bobina.")
        self._dialogo = Dialogo(self, "Confirmar alteração", 
            f"Salvar {nova} com romaneio {romaneio or SEM_ROMANEIO}?\n\n"
            + efeito,
            confirmar=lambda resposta="": self._editar(fornecedor, numero, romaneio),
            cancelar=self._restaurar_grab, acao="Salvar alteração", tom="alerta",
            texto_cancelar="Cancelar")

    def _editar(self, fornecedor, numero, romaneio):
        chave = self._chave_selecionada
        try:
            editar_registro(chave, numero, fornecedor, self.caminho, romaneio=romaneio)
        except (HistoricoInvalido, ValueError) as erro:
            self._erro(str(erro))
        else:
            nova = f"{fornecedor.strip().upper()}|{numero.strip()}"
            self._recarregar(nova)
            self._erro("Registro local atualizado.")
        self._restaurar_grab()

    def _confirmar_exclusao(self):
        if not self._chave_selecionada:
            return
        self._erro("")
        chave = self._chave_selecionada
        self._dialogo = Dialogo(self, "Excluir do histórico local",
            f"Remover {chave} do controle local?\n\n"
            "A ausência dessa chave pode permitir que a bobina seja enviada para "
            "cadastro novamente. Esta ação não remove nada do EGS.",
            confirmar=lambda resposta="": self._excluir(chave),
            cancelar=self._restaurar_grab, acao="Excluir do histórico", tom="erro",
            texto_cancelar="Cancelar")

    def _excluir(self, chave):
        try:
            excluir_registro(chave, self.caminho)
        except (HistoricoInvalido, ValueError) as erro:
            self._erro(str(erro))
        else:
            self._erro("Registro removido do histórico local; ele poderá ser recadastrado.")
            self._definir_campo(self.fornecedor, "")
            self._definir_campo(self.numero, "")
            self._definir_campo(self.romaneio, "")
            self._recarregar()
        self._restaurar_grab()

    def bloquear(self):
        """Fecha antes de uma execução, protegendo leituras/gravações do worker."""
        self.fechar()

    def fechar(self):
        if self._fechada:
            return
        self._fechada = True
        timer = getattr(self, "_timer_foco", None)
        if timer:
            try:
                self.after_cancel(timer)
            except Exception:
                pass
            self._timer_foco = None
        dialogo, self._dialogo = self._dialogo, None
        try:
            if dialogo and dialogo.winfo_exists():
                dialogo.fechar()
        except Exception:
            pass
        try:
            self.grab_release()
        except Exception:
            pass
        if self._ao_fechar:
            callback, self._ao_fechar = self._ao_fechar, None
            callback(self)
        self.destroy()
