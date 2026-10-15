# Parser Cocelpa: colunas, grupos e ajustes

## Objetivo
Separar bobinas de duas colunas e recuperar produto, dimensões e ajustes do romaneio.

## Status atual
Implementado no commit inicial; sem teste direto dos grupos/coordenadas.

## Fluxo de funcionamento
Por página, extrai palavras com posição; agrupa por top (tolerância 2,5) e
divide colunas por x0 relativo à metade da largura. Processa cada coluna em
grupos, aplica marcador KE ao grupo todo e concatena esquerda antes de direita.
Acumula ajustes separados das bobinas.

## Regras de negócio
[RN-10 a RN-12](../BUSINESS_RULES.md): fabricação de 10 dígitos, dimensões
herdadas no grupo, MIOLO padrão e KE → KRAFT ECOLOGICO, toneladas → kg.

## Arquivos relacionados
[parsers.py](../../app/parsers.py), [modelos.py](../../app/modelos.py),
[leitor_pdf.py](../../app/leitor_pdf.py).

## Funções e classes principais
`extrair_bobinas_cocelpa`, `_agrupar_palavras_por_linha`,
`_processar_coluna_cocelpa`, `_tentar_valor_ajuste`, `PADRAO_FABRICACAO`.

## Entradas e saídas
Caminho PDF → `(bobinas, ajuste_peso)`. Peso/ajuste em toneladas multiplicado
por 1000 e arredondado para kg; ajuste pode ser negativo. Não gera bobina de ajuste.

## Persistência de dados
Nenhuma. Estado de grupo é local à coluna/página; não atravessa essas fronteiras.

## Integrações
pdfplumber `extract_words`, com `top`, `x0` e largura da página.

## Validações e exceções
Fabricação precisa ter 10 dígitos; pesos/dimensões devem converter. Dados sem
grupo válido são ignorados. Ajuste exige token único compatível com o padrão
numérico; linha não reconhecida é descartada silenciosamente.

## Interface do usuário
Cocelpa no menu; ajuste aparece no total geral e na nota do resumo, sem atribuição
por produto. A exportação lista somente bobinas.

## Testes relacionados
Não identificado teste unitário ou PDF versionado específico.

## Limitações conhecidas
Colunas/layout fixos; continuidade de grupo entre páginas não preservada;
dimensões inválidas podem herdar grupo anterior. [KI-05](../KNOWN_ISSUES.md#ki-05--parsers-dependem-de-layout-e-formato-numerico).

## Melhorias planejadas
Nenhuma aprovada identificada; exemplos sanitizados e critérios de ajustes
estão pendentes no [ROADMAP](../ROADMAP.md).
