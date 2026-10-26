# Conferência de bobinas e resumo por produto

## Objetivo
Permitir conferir lista extraída, quantidade/peso total e participação de cada produto.

## Status atual
Implementada. Interface escura redesenhada em 2026-10-15, com indicadores,
busca, filtro e cartões de peso por grupo de classificação.

## Fluxo de funcionamento
Após processar PDF, limpa tabela e insere bobinas; calcula total geral e chama
`atualizar_resumo_produtos`, que recria cartões com contagem e peso por grupo.
Busca e filtro alteram somente a tabela; indicadores, resumo e exportação continuam
usando toda a lista. Trocar fornecedor executa novamente o fluxo de importação.

## Regras de negócio
[RN-13](../BUSINESS_RULES.md): quando existem descrições ADF distintas para o
mesmo produto-base, cada descrição completa forma um grupo independentemente da
largura. Sem variantes, produtos com largura >= 1000 são agrupados pelo produto;
pontas (< 1000) são separadas por produto e largura. Gramatura/diâmetro não
dividem grupos. Total geral inclui ajuste; pesos dos grupos não. A importação
opcional de NF e suas sugestões estão em [CONFERENCIA_NF](CONFERENCIA_NF.md).

## Arquivos relacionados
[interface.py](../../app/interface.py), [tema.py](../../app/tema.py),
[componentes.py](../../app/componentes.py), [agrupamento.py](../../app/agrupamento.py).

## Funções e classes principais
`App.processar_pdf`, `_atualizar_romaneio`, `atualizar_resumo_produtos`,
`filtrar_bobinas`, `agrupar_bobinas`, `Indicador`; `tabela`, `resumo_produtos`,
`totais_produtos` e `nota_resumo`.

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
Tema grafite inspirado no shadcn/ui, com tabela escura e três indicadores.
“Peso por grupo” fica ao lado da tabela; cartões identificam ponta/largura ou a
descrição original preservada. NF opcional pode fornecer rótulos de grupo após
confirmação humana; ver [CONFERENCIA_NF](CONFERENCIA_NF.md).
Busca por número/produto/especificação e filtro por grupo; Ctrl+O importa, Ctrl+F
foca busca e Escape limpa busca. Barras horizontal/vertical mantêm a tabela acessível.
Janela até 1180×800, limitada à tela disponível; mínimo até 940×680, também limitado.
Em telas baixas, reduz margens e legendas dos indicadores para ampliar a tabela.

## Testes relacionados
[test_interface.py](../../tests/test_interface.py): totais/ajustes, filtros sem
alterar exportação, falha de leitura, confirmação/interrupção, resultado parcial
e fluxo opcional de conferência NF.
[test_agrupamento.py](../../tests/test_agrupamento.py): limite, produtos distintos,
variantes, peso por grupo e integração com cadastro. A suíte atual de 60 testes
passou com dados sintéticos e navegador simulado.
PDF fornecido foi lido sem cadastro. Conferência visual concluída no Windows com
dados fictícios: tela carregada/vazia, largura mínima, filtros, rolagem e diálogo.

## Limitações conhecidas
Resumo inclui bobinas já cadastradas e não acompanha progresso. Não aparece na
planilha; tabela não é editável. [KI-11](../KNOWN_ISSUES.md#ki-11--leitura-e-exportacao-na-interface).

## Melhorias planejadas
Redesenho, separação de pontas e conferência visual concluídos; estado em
[CURRENT_STATE](../CURRENT_STATE.md).
