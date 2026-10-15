# Conferência de bobinas e resumo por produto

## Objetivo
Permitir conferir lista extraída, quantidade/peso total e participação de cada produto.

## Status atual
Tabela/total implementados no histórico Git; resumo por produto e ajustes de
layout são alterações locais preexistentes, sem data de implementação identificada.

## Fluxo de funcionamento
Após processar PDF, limpa tabela e insere bobinas; calcula total geral e chama
`atualizar_resumo_produtos`, que limpa/recria linhas com contagem e peso por produto.
Trocar fornecedor executa novamente o mesmo fluxo.

## Regras de negócio
[RN-13](../BUSINESS_RULES.md): igualdade de produto determina grupo, sem subdividir
gramatura/formato/diâmetro. Total geral inclui ajuste; totais por produto não.

## Arquivos relacionados
[interface.py](../../app/interface.py), [README.md](../../README.md).

## Funções e classes principais
`App.processar_pdf`, `App.atualizar_resumo_produtos`, widgets `tabela`,
`resumo_produtos`, `total`, `nota_resumo`.

## Entradas e saídas
`self.bobinas` e `self.ajuste_peso` → linhas de conferência, quantidade,
pesos em kg formatados com pontos de milhar e nota sobre ajustes.

## Persistência de dados
Nenhuma; valores derivam da lista em memória, sem buscar EGS/histórico.

## Integrações
ttk.Treeview e widgets CustomTkinter; nenhum serviço externo.

## Validações e exceções
Lista vazia exibe nenhum produto; cadastrar/exportar ficam desabilitados.
Não há validação independente do total oficial do PDF ou edição dos registros.

## Interface do usuário
“Peso por produto” acima da tabela; barras de rolagem, total geral e nota de ajuste.
Controles inferiores têm espaço reservado. Geometria inicial 1000×780, mínima 900×700.

## Testes relacionados
Sem teste automatizado específico de resumo/UI. Nenhuma validação visual foi
executada nesta tarefa; evidência é código e diff local.

## Limitações conhecidas
Resumo inclui bobinas já cadastradas e não acompanha progresso. Não aparece na
planilha; tabela não é editável. [KI-11](../KNOWN_ISSUES.md#ki-11--leitura-e-exportacao-na-interface).

## Melhorias planejadas
Nenhuma aprovada identificada. Estado/revisão do diff local permanece pendente
de confirmação em [CURRENT_STATE](../CURRENT_STATE.md).
