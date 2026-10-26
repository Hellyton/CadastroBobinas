# Problemas conhecidos

Registro de comportamentos observados no código e limitações da análise em
2026-10-15. Não são correções implementadas nem requisitos automaticamente aprovados.
Testes unitários não equivalem a reprodução no EGS. IDs permanecem estáveis.

## KI-01 — Historico nao transacional

**Risco de integridade.** [historico.marcar_cadastrada](../app/historico.py) grava
em arquivo temporário e usa `os.replace`, reduzindo risco de arquivo truncado por
interrupção durante a escrita. Não há lock/transação: instâncias concorrentes
ainda podem perder atualizações. EGS salva antes da escrita local; se esta falhar,
[CadastroBobinas._executar](../app/cadastro.py) pode registrar falha genérica embora
o cadastro remoto exista. Conferir EGS e preservar backup antes de uma retomada.

## KI-02 — Historico ausente, ilegivel ou legado

**Risco de recadastro/omissão.** `carregar_historico` retorna set vazio para arquivo
ausente, JSON inválido ou OSError, sem alertar. Chaves antigas só com número
ignoram fornecedor e podem pular bobina de outro fornecedor. A chave nova não
considera nota/peso. Fonte: [historico.py](../app/historico.py). Histórico local
não garante unicidade no EGS; conferir operação antes de repetir.

## KI-03 — Duplicatas dentro do lote

**Risco observado em fonte.** [CadastroBobinas._executar](../app/cadastro.py)
filtra contra um conjunto inicial; não atualiza esse conjunto após sucesso nem
deduplica a lista. Dois registros iguais no mesmo PDF podem ser tentados, se
saldo permitir. A conferência da lista é necessária; não há teste específico.

## KI-04 — Conferencia global de saldo

**Limitação funcional.** `_executar` lê saldo inicial antes de escolher grupos e
saldo final ao fim, mesmo se operador trocou de nota. A comparação global pode
confrontar notas distintas. Inclui `ajuste_peso` no esperado, mas não lança ajuste
no EGS. Alerta é só terminal/log e não integra resultado da UI. Também não detecta
necessariamente bobinas omitidas: redução e soma de sucessos podem concordar com
saldo residual. Fonte: [cadastro.py](../app/cadastro.py). Não há teste multiproduto.

## KI-05 — Parsers dependem de layout e formato numerico

**Limitações e riscos de extração.** [parsers.py](../app/parsers.py) não faz OCR;
linhas não reconhecidas podem ser descartadas silenciosamente. Novakraft romaneio
troca vírgula por ponto; laudo remove vírgulas. Portanto a mesma representação
decimal pode gerar pesos diferentes; formatos mistos podem levantar ValueError.
No laudo, código de produto inválido não limpa produto anterior. Cocelpa reinicia
grupos por coluna e página; continuação sem dimensões pode ser ignorada, e uma
linha com dimensões inválidas pode herdar grupo anterior. Detecção usa substrings
sensíveis a caixa e precedência fixa. Validar PDFs e convenções reais antes de corrigir.

## KI-06 — Script manual incompativel

**Bug verificável em fonte.** [teste_cadastro.main](../teste_cadastro.py) trata
`ler_romaneio` como lista, mas recebe tripla. `len` vira 3 e `bobinas[:1]` contém
uma lista, não Bobina. O fluxo pode abrir navegador antes de falhar; não executar
como teste seguro. Desempacotar retorno e definir fornecedor são candidatos a
correção futura, sem alterar nesta tarefa.

## KI-07 — Configuracao parcialmente inativa

**Inconsistência.** [config.example.py](../config.example.py) declara `RUA_PADRAO`,
`TIMEOUT`, `HEADLESS`; o fluxo não os consulta. Rua vem do modelo (1), Chromium
usa `headless=False` e esperas têm valores no código. Fontes:
[modelos.py](../app/modelos.py), [navegador.py](../app/navegador.py).

## KI-08 — Escolha de nota e identificacao dependem do operador

**Limitação operacional.** O cadastro solicita nota correta, mas não compara
identificador de nota/produto do EGS com PDF. Observação recebe número da bobina;
[botoes.txt](../botoes.txt) registra desejo de código do produto do fornecedor,
sem requisito fechado. Fontes: [cadastro.py](../app/cadastro.py): `_confirmar`;
[navegador.py](../app/navegador.py): `preencher_bobina`.

## KI-09 — Cobertura de testes e simulador

**Débito de validação.** A suíte tem 76 testes, incluindo gestão do histórico em
arquivos temporários e DOM/JavaScript do popup de peso em Chromium local. A
confirmação de saldo continua simulada; não cobre planilha real, múltiplas
notas ou todas as combinações de schema. HTML local não representa backend,
permissões, falhas de rede ou toda a dinâmica do EGS; aceita login livre e saldo
fica só em memória. Fontes: [tests](../tests), [mock](../mock/mock_sistema.html).
Não houve homologação no EGS.

## KI-10 — Ambiente e diagnostico

**Limitações operacionais.** Dependências não são fixadas; Python global analisado
não tem Playwright, enquanto venv tem a suíte completa. `instalar.bat` usa diretório
atual e não aborta explicitamente após cada erro. Histórico/logs são relativos ao
diretório de execução; importação do logger pode criar logs. Rotação de 1 MB não
limita retenção total e erros podem registrar dados de bobinas. Fontes:
[requirements](../requirements.txt), [instalador](../instalar.bat),
[logger](../app/logger.py). Execute da raiz com venv e preserve dados separadamente.

## KI-11 — Leitura e exportacao na interface

**Limitação/risco de usabilidade.** [App.processar_pdf](../app/interface.py) faz
extração síncrona; PDF grande pode bloquear a janela. A tabela do romaneio é de
conferência, sem edição ou filtro parcial do cadastro. O histórico tem janela
separada para busca e manutenção das chaves locais; isso não edita o EGS. A
exportação trata falha de escrita, mas a dataclass não valida dimensões/produto
nem formatos além dos parsers e do saldo.

## KI-12 — Schema JSON nao validado

**Risco residual de prevenção.** O leitor estrito em
[historico.py](../app/historico.py) valida raiz objeto, `cadastradas` como lista e
chaves como strings não vazias. JSON malformado ou schema inesperado continua
fazendo `carregar_historico` retornar set vazio por compatibilidade, o que pode
deixar de prevenir recadastro; marcação e gestão manual falham sem sobrescrever o
arquivo inválido. Testes com JSON sintaticamente válido e schema inválido cobrem
string, nulo, elemento não textual e raiz lista, preservando o original.

Prioridades, critérios de aceite e aprovação para resolver os riscos residuais:
[ROADMAP](ROADMAP.md). Gestão local não confirma situação no EGS.
