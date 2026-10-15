# Parser de romaneios ADF

## Objetivo
Extrair os dados das bobinas do layout ADF reconhecido no texto do PDF.

## Status atual
Implementado e presente no commit inicial; sem teste automatizado específico.

## Fluxo de funcionamento
Concatena texto das páginas, percorre linhas, aplica regex e converte grupos
em Bobina. Linhas vazias/fora do padrão são descartadas.

## Regras de negócio
[RN-05](../BUSINESS_RULES.md). Detecção do fornecedor está em RN-01;
atribuição do fornecedor/rua em RN-03/RN-04.

## Arquivos relacionados
[parsers.py](../../app/parsers.py), [modelos.py](../../app/modelos.py),
[leitor_pdf.py](../../app/leitor_pdf.py).

## Funções e classes principais
`extrair_bobinas_adf`, `_extrair_texto`, `Bobina`.

## Entradas e saídas
Caminho PDF → `(bobinas, 0)`. Captura número, token de produto, gramatura,
formato, diâmetro e peso; remove pontos do peso antes de converter para int.

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
Não identificado teste específico nem fixture PDF versionada.

## Limitações conhecidas
Sem contador de descartes, OCR ou checagem independente do total oficial;
[KI-05](../KNOWN_ISSUES.md#ki-05--parsers-dependem-de-layout-e-formato-numerico).

## Melhorias planejadas
Nenhuma aprovada identificada; cobertura por layouts depende de definição no [ROADMAP](../ROADMAP.md).
