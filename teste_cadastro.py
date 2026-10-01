from app.leitor_pdf import ler_romaneio
from app.cadastro import CadastroBobinas
from tkinter import filedialog, Tk


def main():

    # Abre um seletor de arquivo simples, só pra escolher o PDF do romaneio
    root = Tk()
    root.withdraw()

    caminho = filedialog.askopenfilename(
        title="Selecione o Romaneio",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )

    if not caminho:
        print("Nenhum arquivo selecionado.")
        return

    bobinas = ler_romaneio(caminho)

    if not bobinas:
        print("Nenhuma bobina encontrada no PDF.")
        return

    print(f"{len(bobinas)} bobinas encontradas. Testando só a primeira:")
    print(bobinas[0])

    cadastro = CadastroBobinas()
    cadastro.iniciar(bobinas[:1])


if __name__ == "__main__":
    main()