# Importação de romaneios e seleção de fornecedor

## Objetivo
Transformar um PDF local em bobinas e ajuste usando o parser do fornecedor.

## Status atual
Implementada. Detecção automática e seleção manual disponíveis para quatro fornecedores.

## Fluxo de funcionamento
`abrir_pdf` escolhe arquivo e reinicia seleção automática. `ler_romaneio` extrai
texto para detectar fornecedor quando ausente; despacha parser pelo caminho do PDF.
`processar_pdf` atribui fornecedor aos objetos, atualiza tabela/totais e habilita
cadastro/exportação apenas quando lista não vazia. Mudar fornecedor reprocessa o mesmo PDF.

## Regras de negócio
[RN-01 a RN-04](../BUSINESS_RULES.md): precedência de marcadores, chave manual,
tripla de retorno e contrato Bobina. Parsers: [ADF](PARSER_ADF.md), [HP](PARSER_HP.md),
[Novakraft](PARSER_NOVAKRAFT.md), [Cocelpa](PARSER_COCELPA.md).

## Arquivos relacionados
[leitor_pdf.py](../../app/leitor_pdf.py), [parsers.py](../../app/parsers.py),
[interface.py](../../app/interface.py), [modelos.py](../../app/modelos.py).

## Funções e classes principais
`ler_romaneio`, `detectar_fornecedor`, `FORNECEDORES`, `App.abrir_pdf`,
`fornecedor_alterado`, `processar_pdf`.

## Entradas e saídas
Caminho PDF e fornecedor opcional → `(list[Bobina], fornecedor_usado, ajuste_peso)`.
Fornecedor não encontrado produz lista vazia e ajuste zero.

## Persistência de dados
Lista e caminho ficam em memória; não há cópia/importação para banco ou histórico.

## Integrações
pdfplumber lê arquivo local; [API_INTEGRATIONS](../API_INTEGRATIONS.md).
Detecção e parser podem abrir/extrair o PDF em etapas separadas.

## Validações e exceções
Cancelar diálogo retorna sem ação. Fornecedor não detectado exibe aviso; pode
ser escolhido manualmente. Falhas de PDF não têm tratamento abrangente na UI.

## Interface do usuário
Selecionar Romaneio, nome do arquivo, menu de fornecedor, tabela e totais.
Interface é de conferência, sem edição de registros.

## Testes relacionados
Não há teste unitário direto do leitor/detecção. `teste_ambiente.py` usa PDF
manual contra mock; não foi executado nesta tarefa.

## Limitações conhecidas
Sem OCR, formatos específicos, descarte de linhas e extração na thread da janela;
[KI-05 e KI-11](../KNOWN_ISSUES.md).

## Melhorias planejadas
Nenhuma aprovada identificada. Exemplos sanitizados/critério de validação estão
pendentes de definição no [ROADMAP](../ROADMAP.md).
