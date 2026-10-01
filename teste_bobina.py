from app.navegador import Navegador
from app.modelos import Bobina
import config


def main():

    navegador = Navegador()
    navegador.abrir()
    navegador.acessar(config.URL)

    input(
        "Faça login, escolha a empresa, abra Classificação de Bobinas, "
        "selecione a nota e clique em Classificar.\n"
        "Deixe a tela na LISTA de bobinas.\n"
        "Pressione ENTER aqui para testar o preenchimento..."
    )

    bobina_teste = Bobina(
        numero=999999,
        produto="TESTE",
        gramatura=90,
        formato=1130,
        diametro=1200,
        peso=800,
        rua=1
    )

    navegador.clicar_novo()
    navegador.preencher_bobina(bobina_teste)

    print("Formulário preenchido. NÃO foi salvo.")
    input(
        "Confira os campos na tela. Quando terminar, pressione ENTER "
        "para fechar o navegador (o formulário será descartado)..."
    )

    navegador.fechar()


if __name__ == "__main__":
    main()