# Parser de romaneios HP

## Objetivo
Extrair bobinas do layout com Papel, pedidos e Cod. Bobinas.

## Status atual
Implementado no commit inicial; homologação de layouts reais não recuperada.

## Fluxo de funcionamento
Extrai texto, percorre linhas e reconhece linha completa. Deriva produto e
gramatura de Papel; código da bobina permanece textual. Converte largura,
diâmetro e peso removendo pontos.

## Regras de negócio
[RN-06](../BUSINESS_RULES.md): M → MIOLO, outra letra preservada; largura vira
formato. RN-01/RN-03/RN-04 regem detecção e contrato.

## Arquivos relacionados
[parsers.py](../../app/parsers.py), [modelos.py](../../app/modelos.py),
[leitor_pdf.py](../../app/leitor_pdf.py).

## Funções e classes principais
`extrair_bobinas_hp`, `MAPA_PRODUTO_HP`, `_extrair_texto`, `Bobina`.

## Entradas e saídas
Caminho PDF → `(bobinas, 0)`. Papel tem uma letra maiúscula e 3 dígitos de
gramatura; pedidos e tubete não são preservados no modelo.

## Persistência de dados
Nenhuma neste parser.

## Integrações
pdfplumber para texto; sem serviço do fornecedor ou EGS.

## Validações e exceções
Linha precisa corresponder ao regex até o fim. Formatações não previstas são
ignoradas; erros ao abrir PDF propagam.

## Interface do usuário
HP no menu ou detecção automática; tabela/resumo comuns.

## Testes relacionados
Não identificado teste direto ou fixture de fornecedor versionada.

## Limitações conhecidas
Mapa tem somente M; não há descrição de negócio de outras letras nem garantia
para vírgulas decimais. [KI-05](../KNOWN_ISSUES.md#ki-05--parsers-dependem-de-layout-e-formato-numerico).

## Melhorias planejadas
Nenhuma aprovada identificada. Novos códigos exigem evidência de layout e
regra confirmada, conforme [ROADMAP](../ROADMAP.md).
