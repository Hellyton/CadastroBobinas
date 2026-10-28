# Conferência opcional de nota fiscal

## Objetivo
Comparar uma NF em PDF com os grupos de bobinas do romaneio e oferecer
associações sugeridas, mantendo a decisão de classificação sob revisão humana.

## Status atual
Importação opcional implementada na interface para o layout textual DANFE ADF.
A interface apresenta associações, pendências e alertas para confirmação; isso
não altera dados da classificação nem executa ações no EGS.

## Fluxo de funcionamento
Lê número da NF, referência do romaneio e itens na ordem da tabela impressa.
Compara cada grupo original com itens da NF por produto compatível e peso exato.
Devolve associações propostas, pendências e alertas para revisão. Cada linha NF
permanece independente, mesmo quando código e descrição se repetem.

## Regras de negócio
Uma associação é sugerida apenas quando produto e peso em kg coincidem e a
correspondência é única, respeitando um item por grupo e um grupo por item.
Pesos repetidos/ambíguos não recebem associação arbitrária. Largura divergente
gera alerta, mas mantém sugestão única para avaliação humana. Referência de
romaneio divergente bloqueia associações; referência ausente gera alerta.
Exceção de item único: se a NF tem um só item e o peso total do romaneio é
igual ao peso desse item, a NF define a divisão. Todos os grupos são associados
ao item (`item_unico=True`) e o cadastro roda em uma única etapa. Produto ou
largura divergente gera alerta, sem bloquear; peso total diferente segue a regra
geral e referência divergente continua bloqueando.

## Arquivos relacionados
[nota_fiscal.py](../../app/nota_fiscal.py), [agrupamento.py](../../app/agrupamento.py),
[modelos.py](../../app/modelos.py), [leitor_pdf.py](../../app/leitor_pdf.py),
[CADASTRO_LOTES](CADASTRO_LOTES.md).

## Funções e classes principais
`ler_nota_fiscal`, `ler_numero_romaneio`, `conferir_nota`, `NotaFiscal`,
`ItemNotaFiscal`, `ConferenciaNota`.

## Entradas e saídas
`ler_nota_fiscal(caminho)` retorna `NotaFiscal(numero, romaneio, itens)`.
`ItemNotaFiscal.numero` é a sequência/linha do item na tabela da NF, não o código
do produto. `conferir_nota(nota, bobinas, numero_romaneio=None)` retorna
associações por grupo, pendências, alertas, indicador de referência compatível
e `item_unico`.
Peso é Decimal em kg; largura fica ausente quando não está explicitamente
identificada no documento.

## Persistência de dados
Nenhuma. Leitura e comparação ocorrem em memória; não grava NF, grupos ou
associações no histórico local.

## Integrações
Usa extração textual de PDF com pdfplumber e os grupos produzidos por
`agrupamento.py`. Não acessa EGS nem serviços externos.

## Validações e exceções
O parser exige layout reconhecido e unidade KG. Item incompleto ou linha não
reconhecida nos campos necessários causa erro claro em vez de aceitar importação
parcial. A leitura identifica NCM, situação tributária, CFOP, unidade e quantidade;
não depende da separação das colunas monetárias, que podem sair concatenadas na
extração do PDF. A quantidade deve ser um token numérico brasileiro completo e é
convertida para Decimal. Não infere gramatura nem largura ausentes.

## Interface do usuário
O botão **Importar NF** permite selecionar PDF depois do romaneio. A interface
apresenta propostas por item, alertas e pendências para confirmação. Ao aceitar,
os rótulos sugeridos aparecem nos cartões, filtro e escolha do cadastro; o
operador ainda confere e seleciona manualmente a aba/item no EGS. Importar um
novo romaneio limpa a NF e suas associações anteriores.
Com NF de item único confirmada, a interface envia `grupo_unico` ao cadastro:
todas as bobinas pendentes formam uma etapa rotulada `NF <n> · item <i> · <descrição>`,
sem escolha de próximo produto. O operador seleciona essa nota no EGS antes de iniciar.
Corrigir o campo Nº do romaneio também limpa a conferência anterior; a próxima
comparação usa o número informado na interface como referência.

## Testes relacionados
`tests/test_nota_fiscal.py` cobre parsing sanitizado, unidade, peso, referência,
correspondência exata, duplicatas e linhas inválidas. Os testes não usam PDFs
operacionais.
Regressões cobrem valores monetários concatenados e recusa de quantidades malformadas.
Item único é coberto em `test_nota_fiscal.py`, `test_agrupamento.py` (cadastro em
uma etapa) e `test_interface.py` (envio de `grupo_unico` e rótulos sem colisão).

## Limitações conhecidas
Parser direcionado ao layout textual DANFE ADF; não lê XML nem executa OCR.
Peso exato compatível não comprova sozinho que a classificação está correta.
Diferença de largura é aviso de revisão, não critério de bloqueio quando a
associação por produto/peso é única.

## Melhorias planejadas
Nenhuma melhoria aprovada identificada; ampliação para outros layouts depende de
especificação e exemplos sanitizados.
