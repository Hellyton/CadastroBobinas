# Cadastro sequencial de lotes por produto e ponta

## Objetivo
Conduzir cadastro das bobinas pendentes na nota selecionada, com saldo e resultados.

## Status atual
Implementado; proteção de saldo/confirmar sucesso adicionada em `3dbea63`.
Suíte simulada passou; operação real não foi executada nesta tarefa.

## Fluxo de funcionamento
Cria navegador, abre destino, faz login e pede preparação da lista pelo operador.
Preserva a descrição original ADF e identifica variantes antes de filtrar o
histórico. Produtos com descrições originais distintas formam grupos por
descrição completa, independentemente da largura. Sem variantes de descrição,
formato abaixo de 1000 agrupa por produto e largura (ponta); formato igual ou
acima de 1000 permanece agrupado somente por produto. Cada grupo mostra seu
próprio peso. A importação de NF é opcional e gera sugestões para revisão
humana; a seleção da aba/nota correspondente continua manual no EGS. Para cada bobina, verifica
controle/saldo, abre Novo, preenche, salva e marca histórico; registra
sucesso/falha e progresso. No final faz conferência global; sempre tenta fechar
navegador no finally.

## Regras de negócio
[RN-16 a RN-20, RN-24 a RN-29](../BUSINESS_RULES.md). Leia a regra específica
antes de modificar saldo, histórico, contadores ou seleção de produtos.

## Arquivos relacionados
[cadastro.py](../../app/cadastro.py), [agrupamento.py](../../app/agrupamento.py),
[nota_fiscal.py](../../app/nota_fiscal.py), [modelos.py](../../app/modelos.py),
[navegador.py](../../app/navegador.py),
[historico.py](../../app/historico.py), [controle.py](../../app/controle.py),
[interface.py](../../app/interface.py).

## Funções e classes principais
`CadastroBobinas.iniciar`, `_executar`, `_escolher_proximo_produto`, `_confirmar`,
`_parar_por_saldo`, `_resultado`.

## Entradas e saídas
`iniciar(bobinas, ajuste_peso=0, url=None, usar_historico=True, controle=None,
evento=None, solicitar=None, rotulos_grupos=None)` → dicionário com contagens `sucessos`, `falhas`,
`total`, `ignoradas`, booleano `interrompido` e texto `motivo_parada`.
`total` é redefinido para pendentes após filtro. Eventos transportam status/progresso.
`rotulos_grupos` permite exibir nomes sugeridos pela conferência opcional de NF
sem alterar produto, peso ou ordem. O número do item NF é a sequência/linha na
tabela do PDF, não o código do produto.

## Persistência de dados
Sucessos confirmados gravam histórico quando habilitado; falhas/pendências não
têm registro persistente próprio. [DATABASE](../DATABASE.md).

## Integrações
[Preenchimento EGS](PREENCHIMENTO_EGS.md), [histórico](HISTORICO_CADASTRO.md),
[controle de execução](CONTROLE_EXECUCAO.md); CLI usa input quando não há callback.

## Validações e exceções
Saldo ilegível/finito inválido/insuficiente ou peso não positivo para o lote.
SalvamentoNaoConfirmado conta falha e encerra. Erro genérico conta falha e tenta
fechar modal; se persistir, pede intervenção. Login/erro fora do laço propaga.

## Interface do usuário
App inicia worker, apresenta seleção de produto e confirmação da nota. CLI
oferece escolha por índice e ENTER como primeiro produto; pode esperar ENTER ao final.
`CadastroBobinas.iniciar` aceita `numero_romaneio` opcional no fim da assinatura;
a interface exige e captura esse número antes da thread. Cada sucesso confirmado
o envia à marcação do histórico, sem alterar a identidade fornecedor/bobina.

## Testes relacionados
[test_agrupamento.py](../../tests/test_agrupamento.py): limite 999/1000,
variantes de descrição, filtro de histórico e execução simulada de grupos.
[test_nota_fiscal.py](../../tests/test_nota_fiscal.py): comparação opcional,
associações únicas e ambiguidades com dados sintéticos.
[test_controle_cadastro.py](../../tests/test_controle_cadastro.py) e
[test_saldo_classificacao.py](../../tests/test_saldo_classificacao.py): interrupção,
progresso, fechamento, saldo inválido/insuficiente/zerado e confirmação incerta.

## Limitações conhecidas
Duplicatas no lote, escolha humana de nota, histórico não transacional e
conferência global entre notas; [KI-01 a KI-04 e KI-08](../KNOWN_ISSUES.md).

## Melhorias planejadas
Nenhuma aprovada identificada; definição de reconciliação por nota/ajuste e
critérios de identidade estão no [ROADMAP](../ROADMAP.md).
