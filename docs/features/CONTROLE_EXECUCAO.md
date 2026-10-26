# Controle de execução, progresso e encerramento

## Objetivo
Manter janela responsiva durante cadastro e permitir confirmar, pausar e interromper.

## Status atual
Implementado no commit inicial; testes simulados de controle passaram.

## Fluxo de funcionamento
`iniciar_cadastro` impede execução dupla, desativa seleção e cria thread não daemon.
Worker publica eventos; janela consome Queue a cada 100 ms. Confirmação usa Event
e resposta da janela. Controle libera/bloqueia pontos de verificação. Ao fechar
janela durante cadastro, solicita interrupção e espera thread antes de destroy.

## Regras de negócio
[RN-26, RN-27 e RN-29](../BUSINESS_RULES.md); [ARCHITECTURE](../ARCHITECTURE.md)
descreve responsabilidade de threads. Progresso inclui falhas genéricas processadas.

## Arquivos relacionados
[controle.py](../../app/controle.py), [interface.py](../../app/interface.py),
[cadastro.py](../../app/cadastro.py).

## Funções e classes principais
`ControleCadastro`, `CadastroInterrompido`, `App.iniciar_cadastro`,
`executar_cadastro`, `processar_eventos`, `confirmar_etapa`, `alternar_pausa`,
`interromper_cadastro`, `encerrar_cadastro`, `fechar_janela`.

## Entradas e saídas
Cliques e sinais Event → bloqueio/liberação/interrupção. Mensagens de fila:
`status` e `progresso` trazem texto/contagens; `confirmacao` traz pedido com Event;
`finalizado` traz resultado; `erro` traz texto da exceção.

## Persistência de dados
Estado do controle, fila e pedido são transitórios; não há checkpoint de sessão.
Histórico de bobinas permite filtro em nova execução, com seus limites.

## Integrações
threading, queue e loop Tkinter; Playwright permanece na thread de trabalho.

## Validações e exceções
Pausa/interrupção não aborta chamada em andamento. Interromper libera Event de
pausa; verificar lança CadastroInterrompido. Worker captura demais exceções e
publica erro; UI mostra diálogo e reativa controles ao encerrar.

## Interface do usuário
Iniciar Cadastro, Pausar/Continuar, Interromper, barra com percentual e status visual.
Confirmações aparecem em diálogo escuro rolável, com seleção do grupo quando
aplicável. “Interromper cadastro”, Escape ou fechar esse diálogo interrompem o lote
pelos pontos cooperativos existentes. Exportação permanece disponível.

## Testes relacionados
[test_controle_cadastro.py](../../tests/test_controle_cadastro.py), 7 testes:
pausa, desbloqueio, interrupção após salvar, fechamento em login falho, contagem,
pausa durante salvamento e interrupção enquanto aguarda confirmação.
[test_interface.py](../../tests/test_interface.py) também verifica entrega da
escolha, interrupção do diálogo e percentual de resultado parcial.

## Limitações conhecidas
Encerramento aguarda chamadas/timeouts; não há retomada de checkpoint. PDF ainda
é processado na thread principal. Parada antecipada pode deixar barra sem último
incremento, embora resultado conte falhas. [RN-27](../BUSINESS_RULES.md), [KI-11](../KNOWN_ISSUES.md#ki-11--leitura-e-exportacao-na-interface).

## Melhorias planejadas
Nenhuma aprovada identificada; não alterar sem preservar afinidade de thread e
limite de interrupção entre operações.
