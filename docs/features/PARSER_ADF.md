# Parser de romaneios ADF

## Objetivo
Extrair os dados das bobinas do layout ADF reconhecido no texto do PDF,
preservando a descrição original completa do produto.

## Status atual
Implementado. O parser preserva a descrição completa e mantém `produto` como
token-base para compatibilidade com o cadastro existente.

## Fluxo de funcionamento
Concatena texto das páginas, percorre linhas, aplica regex e converte grupos
em Bobina. A descrição original é capturada separadamente do produto-base.
Linhas vazias/fora do padrão são descartadas.

## Regras de negócio
[RN-05](../BUSINESS_RULES.md) e regras de agrupamento em [RN-13 e RN-19](../BUSINESS_RULES.md).
Descrições distintas do mesmo produto-base podem formar grupos separados;
detalhes em [Cadastro por lotes](CADASTRO_LOTES.md). Detecção do fornecedor está em RN-01;
atribuição do fornecedor/rua em RN-03/RN-04.

## Arquivos relacionados
[parsers.py](../../app/parsers.py), [modelos.py](../../app/modelos.py),
[leitor_pdf.py](../../app/leitor_pdf.py).

## Funções e classes principais
`extrair_bobinas_adf`, `_extrair_texto`, `Bobina.descricao_original`.

## Entradas e saídas
Caminho PDF → `(bobinas, 0)`. Captura número, produto-base, descrição original,
gramatura, formato, diâmetro e peso; remove pontos do peso antes de converter
para int. O novo campo opcional é acrescentado ao fim do modelo para preservar
construtores posicionais existentes.

## Persistência de dados
Nenhuma; lista em memória. Histórico pertence ao cadastro posterior.

## Integrações
pdfplumber, sem comunicação com EGS nesta etapa.

## Validações e exceções
Regex exige a estrutura de colunas incluindo quantidade ML e unidade; conversão
ValueError/AttributeError descarta linha. Abertura inválida de PDF pode propagar erro.

## Interface do usuário
Selecionado automaticamente ou por ADF no menu; resultados na tabela comum.

## Testes relacionados
`tests/test_parsers_adf.py` usa entradas sintéticas para validar descrição
original e compatibilidade do produto-base; não há PDF operacional versionado.

## Limitações conhecidas
Sem contador de descartes, OCR ou checagem independente do total oficial; a
descrição capturada depende das colunas textuais do layout, sem inferir família
ou gramatura a partir dela;
[KI-05](../KNOWN_ISSUES.md#ki-05--parsers-dependem-de-layout-e-formato-numerico).

## Melhorias planejadas
Nenhuma aprovada identificada; cobertura por layouts depende de definição no [ROADMAP](../ROADMAP.md).
