# Parser Novakraft: romaneio e laudo técnico

## Objetivo
Extrair lote/peso e dimensões nominais em dois layouts Novakraft.

## Status atual
Ambos os layouts estão implementados no commit inicial; sem testes próprios.

## Fluxo de funcionamento
Extrai texto. Título exato `Laudo Técnico da Qualidade` seleciona ramo de laudo;
caso contrário usa romaneio. O código nominal define produto/dimensões para os
lotes seguintes. Tenta interpretar código diretamente e depois desduplicar pares.
Romaneio percorre tokens sem depender das quebras de linha; o pedido do cliente é
usado como referência do romaneio quando não existe número próprio. Laudo percorre
linhas e aceita colunas de ensaio ignoradas na saída.

## Regras de negócio
[RN-07 a RN-09](../BUSINESS_RULES.md). NEBX → MIOLO; prefixo diferente permanece.
Código: letras + gramatura (3) + diâmetro (4) + formato (4).

## Arquivos relacionados
[parsers.py](../../app/parsers.py), [modelos.py](../../app/modelos.py),
[leitor_pdf.py](../../app/leitor_pdf.py).

## Funções e classes principais
`extrair_bobinas_novakraft`, `_extrair_bobinas_novakraft_romaneio`,
`_extrair_bobinas_novakraft_laudo`, `_interpretar_codigo_produto`,
`_desduplicar_codigo`, `TOKEN_NOVAKRAFT`, `PADRAO_LINHA_LAUDO_NOVAKRAFT`.

## Entradas e saídas
Caminho PDF → `(bobinas, 0)`. Número recebe lote; testes de qualidade não são
persistidos. No romaneio, peso pt-BR remove pontos de milhar e troca vírgula por
ponto antes de `float/round`; também aceita `/ /` quando data e turno ainda não
foram preenchidos. O laudo mantém sua conversão própria.

## Persistência de dados
Nenhuma; contexto de produto é mantido durante análise do texto.

## Integrações
pdfplumber para extração de texto; não há OCR.

## Validações e exceções
Sem código válido anterior, linha de lote é pulada. No romaneio, código inválido
zera produto; no laudo, uma linha de código inválida não limpa o contexto anterior.
Separadores numéricos não previstos podem gerar ValueError.

## Interface do usuário
Novakraft no menu; escolha de laudo/romaneio é interna, sem opção separada.

## Testes relacionados
O romaneio V26654 foi validado localmente, incluindo código duplicado, peso pt-BR
e a ausência de data/turno. Não há fixture operacional versionada.

## Limitações conhecidas
Conversões numéricas divergentes, dependência de texto e contexto do produto;
[KI-05](../KNOWN_ISSUES.md#ki-05--parsers-dependem-de-layout-e-formato-numerico).

## Melhorias planejadas
Nenhuma aprovada identificada; confirmar convenções de peso com documentos
sanitizados antes de propor mudança. [ROADMAP](../ROADMAP.md).
