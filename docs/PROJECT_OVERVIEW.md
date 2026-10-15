# Visão geral

O projeto chama-se **Classificação de Bobinas** nesta memória; a janela e o
[README operacional](../README.md) usam **Cadastro Automático de Bobinas**.
É uma aplicação desktop para reduzir a digitação de dados de romaneios no EGS.

## Objetivos e usuários

O operador seleciona o PDF, confere os dados extraídos, escolhe a nota/produto
no navegador e acompanha o cadastro. A aplicação extrai e preenche os campos;
a escolha da empresa, da nota e da tela correta depende do operador.
O desenvolvedor mantém parsers, seletores, interface e testes. Perfis formais,
responsável de homologação e permissões por cargo: **Não identificado**.

## Escopo implementado

- Detecção automática ou escolha manual de ADF, HP, Novakraft e Cocelpa.
- Extração dos layouts de romaneio; Novakraft também aceita laudo técnico.
- Tabela de conferência, total geral e resumo de quantidade/peso por produto.
- Exportação das bobinas extraídas para XLSX.
- Login no EGS e cadastro sequencial, agrupado por produto, com intervenção humana.
- Verificação de saldo, de campos preenchidos e de evidência de salvamento.
- Histórico local, progresso, pausa, continuação, interrupção e logs.
- Testes unitários simulados e ambiente HTML para teste manual.

O índice detalhado está em [features/README.md](features/README.md).

## Fluxo de utilização

1. Preparar ambiente e configuração local conforme [guia](DEVELOPMENT_GUIDE.md).
2. Abrir `main.py` por `executar.bat` e selecionar um romaneio PDF.
3. Conferir fornecedor, bobinas e totais; trocar fornecedor para reprocessar se necessário.
4. Exportar a lista para Excel, se desejado, ou iniciar cadastro.
5. Após o login automatizado, abrir a classificação, selecionar a nota e confirmar na janela.
6. Em vários produtos, escolher o próximo e confirmar o registro correto.
7. Acompanhar progresso; se houver parada ou falha, conferir o EGS antes de retomar.

## Limites

Não há backend próprio, API pública, banco relacional, OCR, edição de células da
tabela, seleção parcial de bobinas ou seleção automática de nota identificados.
O lote recebe toda a lista extraída; o histórico filtra registros já conhecidos.
O resumo representa o PDF carregado, não o progresso nem o estoque no EGS.
O aplicativo não valida por identificador se a nota selecionada pertence ao
romaneio. Campos calculados são responsabilidade do EGS; suas fórmulas reais
não foram recuperadas. A estrutura interna e o banco do EGS são externos.

Funcionamento em produção e layouts reais não foram homologados nesta tarefa.
Consulte [estado atual](CURRENT_STATE.md) e [limitações](KNOWN_ISSUES.md).
