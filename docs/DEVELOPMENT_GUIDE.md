# Guia de desenvolvimento

## Ambiente

O alvo operacional documentado é Windows com Python e Tkinter. Ambiente local
verificado em 2026-10-15: Python **3.10.9** no `venv`. Versão mínima oficialmente
suportada: **Não identificado**. `requirements.txt` não fixa versões.

| Dependência direta | Uso | Versão instalada observada |
| --- | --- | --- |
| customtkinter | Janela desktop | 6.0.0 |
| playwright | Automação web síncrona | 1.61.0 |
| pdfplumber | Extração de texto/palavras do PDF | 0.11.10 |
| loguru | Logs e rotação | 0.7.3 |
| openpyxl | Escrita XLSX | 3.1.5 |

Essas versões descrevem a máquina analisada; não constituem lockfile ou matriz
de compatibilidade. Tkinter, dataclasses, threading, queue, json e unittest
vêm da biblioteca padrão. Chromium é instalado separadamente pelo Playwright.

## Preparação e execução

Na raiz do projeto, copie `config.example.py` para `config.py` apenas se ainda
não existir, e configure localmente `USUARIO`, `SENHA`, `CHAVE_ACESSO` e `URL`.
Não sobrescreva configuração operacional. `RUA_PADRAO`, `TIMEOUT` e `HEADLESS`
existem no exemplo, mas não controlam o comportamento atual ([KI-07](KNOWN_ISSUES.md#ki-07--configuracao-parcialmente-inativa)).

`instalar.bat` cria/ativa `venv`, atualiza pip, instala requirements e Chromium.
Execute-o a partir da raiz: ele não muda de diretório nem valida todas as falhas.
Equivalente explícito para preparar uma instalação nova:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m playwright install chromium
```

Se um venv copiado aponta para Python ausente, preserve os arquivos operacionais
e prepare um ambiente compatível; não suponha que um venv é transportável.
Nesta tarefa não foram instaladas dependências nem recriado o ambiente.

Use `executar.bat`, que muda para a raiz, ativa venv e executa `main.py`, ou:

```powershell
.\venv\Scripts\python.exe main.py
```

Execute com diretório de trabalho na raiz: histórico e logs têm caminhos relativos.
`config.py` precisa existir também para importar módulos usados por vários testes.

## Testes e alcance

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

São 23 testes: 7 de controle, 8 de saldo e 8 de preenchimento. Em 2026-10-15,
todos passaram usando o venv existente, navegador simulado e diretório temporário
para não escrever logs operacionais; bytecode foi desabilitado com `-B`.
A tentativa com Python global não importou Playwright, portanto não executou
casos funcionais. Isso não é falha do código: use o interpretador do venv.

A suíte não valida JavaScript no navegador real: `wait_for_function` é simulado.
Não cobre diretamente parsers, JSON real, resumo, exportação ou seleção de várias
notas. Não há CI, lint, typecheck, cobertura mínima ou pipeline identificados.

| Script manual | Efeito e cuidado |
| --- | --- |
| `teste_ambiente.py` | PDF + HTML local; `usar_historico=False`; exige confirmação por terminal |
| `teste_bobina.py` | Abre destino de config e preenche uma bobina; não chama salvar, mas exige login/manual |
| `teste_cadastro.py` | Contrato antigo incompatível; não usar como validação ([KI-06](KNOWN_ISSUES.md#ki-06--script-manual-incompativel)) |

Para o simulador, use configuração de desenvolvimento sem segredos e inicie
na raiz em um terminal:

```powershell
.\venv\Scripts\python.exe -m http.server 8000 --bind 127.0.0.1
```

Em outro terminal: `.\venv\Scripts\python.exe teste_ambiente.py caminho-do-romaneio.pdf`.
Sem argumento, abre seletor de PDF. [SIMULADOR_LOCAL](features/SIMULADOR_LOCAL.md)
descreve limites; ele não foi executado nesta tarefa.

## Depuração localizada

1. PDF vazio/incorreto: confirmar fornecedor, marcadores e parser; não presumir OCR.
2. Campos apagados: verificar `_campos_divergentes`, esperas de cálculo e seletores `SEL_*`.
3. Saldo ou salvamento incerto: conferir primeiro a nota e o registro no EGS;
   não marcar histórico como sucesso para contornar a falha.
4. Janela/pausa: verificar fila, `Event`, thread e pontos `verificar`, sem manipular
   widgets da thread de trabalho.
5. Consultar logs locais com cuidado: podem conter dados operacionais.

## Convenções e versionamento

Preserve nomes e contratos existentes, pesos inteiros em kg, número como texto,
compatibilidade do histórico e responsabilidade de cada thread. Não há formatter,
padrão formal de branch/release ou política de revisão identificados. Antes de
editar, consulte `git status --short` para preservar mudanças locais; para novas
branches use `codex/` salvo orientação do usuário. Não crie commits automaticamente.
Atualize a documentação incrementalmente conforme [AGENTS](../AGENTS.md), com
evidência e sem inventar motivação histórica. Nunca versione credenciais, PDFs,
planilhas, logs ou histórico operacional.
