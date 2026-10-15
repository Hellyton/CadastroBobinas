# Cadastro sequencial de lotes por produto

## Objetivo
Conduzir cadastro das bobinas pendentes na nota selecionada, com saldo e resultados.

## Status atual
Implementado; proteção de saldo/confirmar sucesso adicionada em `3dbea63`.
Suíte simulada passou; operação real não foi executada nesta tarefa.

## Fluxo de funcionamento
Cria navegador, abre destino, faz login e pede preparação da lista pelo operador.
Filtra histórico, agrupa pendentes com OrderedDict, escolhe produto e confirma
nota quando lote tem vários produtos. Para cada bobina, verifica controle/saldo,
abre Novo, preenche, salva e marca histórico; registra sucesso/falha e progresso.
No final faz conferência global; sempre tenta fechar navegador no finally.

## Regras de negócio
[RN-16 a RN-20, RN-24 a RN-29](../BUSINESS_RULES.md). Leia a regra específica
antes de modificar saldo, histórico, contadores ou seleção de produtos.

## Arquivos relacionados
[cadastro.py](../../app/cadastro.py), [navegador.py](../../app/navegador.py),
[historico.py](../../app/historico.py), [controle.py](../../app/controle.py),
[interface.py](../../app/interface.py).

## Funções e classes principais
`CadastroBobinas.iniciar`, `_executar`, `_escolher_proximo_produto`, `_confirmar`,
`_parar_por_saldo`, `_resultado`.

## Entradas e saídas
`iniciar(bobinas, ajuste_peso=0, url=None, usar_historico=True, controle=None,
evento=None, solicitar=None)` → dicionário com contagens `sucessos`, `falhas`,
`total`, `ignoradas`, booleano `interrompido` e texto `motivo_parada`.
`total` é redefinido para pendentes após filtro. Eventos transportam status/progresso.

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

## Testes relacionados
[test_controle_cadastro.py](../../tests/test_controle_cadastro.py) e
[test_saldo_classificacao.py](../../tests/test_saldo_classificacao.py): interrupção,
progresso, fechamento, saldo inválido/insuficiente/zerado e confirmação incerta.

## Limitações conhecidas
Duplicatas no lote, escolha humana de nota, histórico não transacional e
conferência global entre notas; [KI-01 a KI-04 e KI-08](../KNOWN_ISSUES.md).

## Melhorias planejadas
Nenhuma aprovada identificada; definição de reconciliação por nota/ajuste e
critérios de identidade estão no [ROADMAP](../ROADMAP.md).
