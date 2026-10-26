# Exportação de bobinas para Excel

## Objetivo
Gerar planilha XLSX com os registros extraídos para conferência externa.

## Status atual
Implementada no commit inicial; não depende de cadastrar no EGS.

## Fluxo de funcionamento
Com bobinas carregadas, abre diálogo de destino, cria Workbook, nomeia aba
Bobinas, escreve cabeçalho/linhas e salva. Ao concluir mostra caminho ao operador.

## Regras de negócio
[RN-14](../BUSINESS_RULES.md). Exporta toda lista em memória e rua; não aplica
filtro do histórico nem cria resumo/ajuste/status.

## Arquivos relacionados
[interface.py](../../app/interface.py), [requirements.txt](../../requirements.txt).

## Funções e classes principais
`App.exportar_excel`, `openpyxl.Workbook`, `filedialog.asksaveasfilename`.

## Entradas e saídas
Lista Bobina e caminho escolhido → XLSX com Bobina, Produto, Gramatura,
Formato, Diâmetro, Peso e Rua, nessa ordem.

## Persistência de dados
Arquivo XLSX local. Não atualiza histórico e não há importação de volta.

## Integrações
openpyxl; não requer controlar Microsoft Excel nem autenticação externa.

## Validações e exceções
Sem bobinas ou com diálogo cancelado, retorna. OSError ao salvar exibe mensagem
escura orientando conferir arquivo/pasta. Código não configura estilo da planilha.

## Interface do usuário
Botão Exportar Excel habilitado após extração não vazia; diálogo de salvar e aviso
de conclusão com tema escuro. Botão permanece disponível durante cadastro.
Busca e filtro da tabela não restringem os registros exportados.

## Testes relacionados
`test_interface.py` simula Workbook e verifica exportação integral, números como
texto e pesos numéricos mesmo com filtro ativo. Não valida arquivo XLSX real.

## Limitações conhecidas
Fornecedor e ajuste não exportados, sem resumo por produto e sem classificação
de sucesso/falha. [KI-11](../KNOWN_ISSUES.md#ki-11--leitura-e-exportacao-na-interface).

## Melhorias planejadas
Nenhuma aprovada identificada; alteração de colunas exigirá confirmar compatibilidade.
