"""Componentes visuais compartilhados do tema escuro desktop."""

import customtkinter as ctk
from tkinter import ttk


CORES = {
    "fundo": "#09090B", "cartao": "#111114", "superficie": "#18181B",
    "borda": "#29292E", "texto": "#FAFAFA", "muted": "#A1A1AA",
    "discreto": "#71717A", "hover": "#27272A", "primario": "#F4F4F5",
    "sucesso": "#6EE7B7", "alerta": "#FBBF24", "erro": "#FCA5A5",
}
FONTE = "Segoe UI"


def texto(master, conteudo, tamanho=13, cor="texto", negrito=False, **kwargs):
    kwargs.setdefault("height", 0)
    return ctk.CTkLabel(
        master, text=conteudo, font=(FONTE, tamanho, "bold" if negrito else "normal"),
        text_color=CORES.get(cor, cor), **kwargs
    )


def cartao(master, **kwargs):
    return ctk.CTkFrame(
        master, fg_color=CORES["cartao"], border_color=CORES["borda"],
        border_width=1, corner_radius=10, **kwargs
    )


def botao(master, conteudo, comando, variante="secundario", **kwargs):
    principal = variante == "primario"
    widget = ctk.CTkButton(
        master, text=conteudo, command=comando, height=36, corner_radius=7,
        font=(FONTE, 13, "bold"), border_width=0 if principal else 1,
        border_color=CORES["borda"],
        fg_color=CORES["primario"] if principal else CORES["superficie"],
        hover_color="#D4D4D8" if principal else CORES["hover"],
        text_color=CORES["fundo"] if principal else (
            CORES["erro"] if variante == "perigo" else CORES["texto"]),
        text_color_disabled=CORES["discreto"], **kwargs
    )
    widget.bind("<Return>", lambda event: widget.invoke())
    return widget


def menu(master, valores, comando=None, **kwargs):
    return ctk.CTkOptionMenu(
        master, values=valores, command=comando, height=36, corner_radius=7,
        fg_color=CORES["superficie"], button_color=CORES["superficie"],
        button_hover_color=CORES["hover"], text_color=CORES["texto"],
        text_color_disabled=CORES["discreto"], dropdown_fg_color=CORES["superficie"],
        dropdown_hover_color=CORES["hover"], dropdown_text_color=CORES["texto"],
        font=(FONTE, 12), dropdown_font=(FONTE, 12), **kwargs
    )


def configurar_tabela(master):
    estilo = ttk.Style(master)
    estilo.theme_use("clam")
    estilo.configure(
        "Bobinas.Treeview", background=CORES["cartao"],
        fieldbackground=CORES["cartao"], foreground=CORES["texto"],
        borderwidth=0, relief="flat", font=(FONTE, 10),
        rowheight=round(33 * master._get_widget_scaling())
    )
    estilo.configure(
        "Bobinas.Treeview.Heading", background=CORES["superficie"],
        foreground=CORES["muted"], font=(FONTE, 10), relief="flat",
        borderwidth=0, padding=(10, 10)
    )
    estilo.map("Bobinas.Treeview", background=[("selected", "#303036")],
               foreground=[("selected", CORES["texto"])])
    estilo.map("Bobinas.Treeview.Heading", background=[("active", CORES["hover"])])
    estilo.layout("Bobinas.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
    return estilo


def numero(valor):
    return f"{valor:,}".replace(",", ".")
