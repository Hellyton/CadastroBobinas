# Cadastro Automático de Bobinas

Aplicativo para Windows que lê romaneios em PDF, permite conferir as bobinas
em uma tabela, exporta os dados para Excel e automatiza a classificação no EGS.

Reconhece layouts dos fornecedores ADF, HP, Novakraft e Cocelpa.

## Preparação

1. Instale Python com suporte a Tkinter e disponibilize o comando `python`.
2. Copie `config.example.py` para `config.py` e preencha usuário, senha e chave
   de acesso. O arquivo `config.py` é local e não entra no Git.
3. Execute `instalar.bat` na pasta do projeto para criar o ambiente e instalar
   as dependências e o navegador.
4. Abra o programa com `executar.bat`.

Se o ambiente `venv` veio de outra máquina ou aponta para uma instalação de
Python ausente, recrie-o usando a instalação de Python disponível.

## Uso

Selecione o romaneio, confira o fornecedor e os dados, e clique em
**Iniciar Cadastro**. Quando solicitado pela janela, abra a classificação no
navegador, selecione a nota correspondente e clique em **Continuar**.

A seção **Peso por produto** mostra a quantidade de bobinas e o peso total
em kg de cada produto (por exemplo, RECICLADO e MIOLO), somando todas as
suas bobinas, independentemente de gramatura ou formato.
Os ajustes do romaneio aparecem no total geral, sem serem atribuídos a um
produto específico.

O cadastro executa em segundo plano, com progresso e controles de pausa,
continuação e interrupção. A pausa e a interrupção aguardam a operação da
bobina atual terminar. Em romaneios com vários produtos, a janela solicita
a escolha do próximo produto e a confirmação da nota.

Antes de cada bobina, o programa verifica se o saldo da nota comporta o peso.
Saldo zerado, insuficiente ou ilegível para o lote e mantém as bobinas restantes
pendentes. O sucesso só é registrado quando o formulário fecha e o saldo diminui
pelo peso da bobina. Se essa confirmação falhar, confira o cadastro no EGS antes
de tentar novamente; a bobina não entra automaticamente no histórico local.

O histórico local ajuda a evitar recadastros por fornecedor e número da
bobina. Confira o sistema antes de retomar um cadastro que apresentou erro.

## Testes

Com as dependências instaladas, execute:

```powershell
python -m unittest discover -s tests -v
```

Esses testes simulam o navegador e verificam pausa, interrupção, progresso
e encerramento. Não realizam cadastros no EGS.

Para teste manual com um PDF e o sistema simulado local, inicie:

```powershell
python -m http.server 8000 --bind 127.0.0.1
```

Em outro terminal na pasta do projeto, execute `python teste_ambiente.py`.
Esse teste usa `mock/mock_sistema.html` e não grava no histórico real.

## Arquivos locais

Credenciais, histórico, logs, ambientes Python, PDFs e planilhas estão
excluídos do Git. Preserve os dados operacionais separadamente ao transferir
o programa para outro computador.
