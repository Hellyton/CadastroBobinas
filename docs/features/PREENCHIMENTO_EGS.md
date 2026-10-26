# Preenchimento, validação e confirmação no EGS

## Objetivo
Preencher bobina e só liberar sucesso quando os campos e o saldo sustentarem a gravação.

## Status atual
Implementado. Saldo confirmado desde `3dbea63`; preenchimento verifica campos e
confirma o fechamento do aviso de peso antes de continuar.

## Fluxo de funcionamento
Abre Chromium visível e login com config. Novo aguarda Rua visível (10 s).
Preenche Rua/Diâmetro/Formato, trata aviso ao focar Peso, preenche Peso e recupera
campos iniciais alterados. Preenche Gramatura, dispara Tab, aguarda calculados,
preenche Observação e verifica todos os campos. Salvar repete conferência de
campos e aguarda remoção do botão e saldo esperado (10 s).
O operador confirmou que o aviso surge em cada classificação ao clicar em Peso;
o tratamento é repetido por bobina e aguarda o fechamento antes de preencher Peso.

## Regras de negócio
[RN-20 a RN-25](../BUSINESS_RULES.md). `_fill_verificado` tenta Rua até 4 vezes,
com 50 ms apenas após divergência. `preencher_bobina` tenta ciclo até 3 vezes;
calculados têm espera de 8 s e uma repetição de blur/8 s por tentativa.

## Arquivos relacionados
[navegador.py](../../app/navegador.py), [config.example.py](../../config.example.py),
[cadastro.py](../../app/cadastro.py).

## Funções e classes principais
`Navegador`, `SalvamentoNaoConfirmado`, constantes `SEL_*`, `clicar_novo`,
`preencher_bobina`, `_preencher_campos`, `_campos_divergentes`, `_fill_verificado`,
`_aguardar_campos_calculados`, `_esperar_calculo`, `_fechar_popup_peso`, `salvar`.

## Entradas e saídas
Bobina → campos EGS. Saldo/quantidade lidos retornam float ou None. `_parse_numero`
remove pontos de milhar e troca vírgula por ponto. `salvar(peso, saldo_antes)`
conclui sem objeto retornado ou lança exceção. Número textual é Observação;
produto/nota não são selecionados automaticamente.

## Persistência de dados
Gravação ocorre no EGS. Classe não escreve JSON; orquestrador marca histórico
após retorno confirmado. Sem ID remoto retornado/reconciliação automática.

## Integrações
Playwright sync API, Chromium, config local e DOM EGS. [API_INTEGRATIONS](../API_INTEGRATIONS.md).

## Validações e exceções
Campos numéricos comparados após parse pt-BR; observação por igualdade textual.
Aviso de peso zero tem espera de aparição delimitada e botão OK localizado pelo
contexto da mensagem, sem exigir somente as classes do modal antigo. Ausência é
opcional; falha no clique ou no fechamento de um aviso identificado gera erro.
Calculados devem ser
não vazios; fórmulas não são validadas. Salvar exige peso/saldo finitos, positivos,
peso ≤ saldo e redução com diferença < 0,01 kg. Timeout vira SalvamentoNaoConfirmado.

## Interface do usuário
Operador prepara lista e nota no navegador; automação atua no modal. Não existe
tela de edição de seletores ou credenciais no aplicativo.

## Testes relacionados
[test_preenchimento.py](../../tests/test_preenchimento.py): campos apagados por
aviso/cálculo, tentativas, caminho sem pausa fixa, popup e bloqueio antes de salvar.
[test_popup_peso.py](../../tests/test_popup_peso.py): Chromium local sem rede,
aparição atrasada, isolamento de outros avisos e sequência de preenchimento.
[test_saldo_classificacao.py](../../tests/test_saldo_classificacao.py): confirmação
incerta/zero final. Mock de wait_for_function não executa o predicado JavaScript.

## Limitações conhecidas
Seletores posicionais sensíveis ao DOM, config parcialmente inativa, campos
calculados sem validação de fórmula e nota escolhida pelo operador.
[KI-07 a KI-09](../KNOWN_ISSUES.md). Constante antiga `SEL_OK_POPUP_PESO` permanece,
mas fechamento atual usa mensagem/botão OK; anotações em botoes.txt não prevalecem.

## Melhorias planejadas
Nenhuma aprovada identificada; identidade de observação e homologação de integração
pendentes no [ROADMAP](../ROADMAP.md).
