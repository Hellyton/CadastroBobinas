# Planejamento e pendências

Este arquivo distingue entregas observáveis de sugestões. Não foi identificado
backlog formal, prazo, responsável ou priorização aprovada. Status em 2026-10-15.

## Concluídas

- No código: importação dos quatro fornecedores, conferência, XLSX, agrupamento
  por produto, automação EGS, histórico e controle de execução.
- No commit `3dbea63`: prevenção por saldo e confirmação de salvamento.
- Nesta tarefa: memória modular, AGENTS e validação documental; 23 testes aprovados.

“Concluído” aqui significa implementado/documentado, não homologado no ambiente EGS.
Os detalhes e cobertura estão no [índice de funcionalidades](features/README.md).

## Em andamento

Há alterações locais preexistentes de resumo por produto/preenchimento e seu
teste. Elas estão implementadas no checkout; não foi possível determinar se
estão em revisão, concluídas sem commit ou em desenvolvimento. Não atribuir
status de entrega por inferência. Veja [CURRENT_STATE](CURRENT_STATE.md).

## Planejadas

Manutenção incremental da memória após futuras alterações, conforme
[AGENTS](../AGENTS.md). Nenhuma nova funcionalidade com plano aprovado foi identificada.

## Bloqueadas

Nenhuma tarefa formalmente bloqueada foi identificada. A homologação do EGS e
dos PDFs exige ambiente/documentos e escopo de validação apropriados; não foi
autorizada como execução operacional nesta tarefa de documentação.

## Pendentes de definição

| Item | Evidência | Definição necessária |
| --- | --- | --- |
| Conteúdo do campo Observação para rastreio | `botoes.txt` deseja código de produto; código envia número da bobina ([KI-08](KNOWN_ISSUES.md#ki-08--escolha-de-nota-e-identificacao-dependem-do-operador)) | Identificador desejado, formato e compatibilidade; sem requisito aprovado identificado |
| Correção do script manual antigo | [KI-06](KNOWN_ISSUES.md#ki-06--script-manual-incompativel) | Prioridade e cenário de teste seguro |
| Integridade do histórico e duplicatas | KI-01, KI-02, KI-03, KI-12 em [KNOWN_ISSUES](KNOWN_ISSUES.md) | Critério de identidade, recuperação e concorrência |
| Conferência por nota e tratamento de ajustes | [KI-04](KNOWN_ISSUES.md#ki-04--conferencia-global-de-saldo) | Regra operacional para múltiplas notas e ajustes |
| Convenções numéricas e continuidade dos parsers | [KI-05](KNOWN_ISSUES.md#ki-05--parsers-dependem-de-layout-e-formato-numerico) | Exemplos sanitizados e pesos esperados de cada layout |
| Configuração, dependências e tratamento de erros | KI-07, KI-10, KI-11 em [KNOWN_ISSUES](KNOWN_ISSUES.md) | Suporte desejado, prioridades e compatibilidade |
| Ampliar cobertura e validar integração | [KI-09](KNOWN_ISSUES.md#ki-09--cobertura-de-testes-e-simulador) | Cenários/ambiente de homologação e critérios de aceite |

Esses itens são candidatos derivados da análise e de uma anotação existente;
não são requisitos aprovados, prazos prometidos ou trabalho iniciado nesta tarefa.
