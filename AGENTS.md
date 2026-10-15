# Contexto permanente — Classificação de Bobinas

Aplicação desktop Windows em Python: importa romaneios PDF, confere bobinas,
exporta XLSX e automatiza a classificação no EGS. Stack: CustomTkinter/Tkinter,
pdfplumber, Playwright síncrono/Chromium, openpyxl e Loguru. Histórico local JSON.
O código é a referência do comportamento; documentação é contexto verificável.

## Antes de implementar

1. Leia este arquivo e identifique a funcionalidade em [docs/features/README.md](docs/features/README.md).
2. Consulte somente documentos pertinentes, seguindo o roteador abaixo.
3. Localize arquivos/símbolos em [FILE_MAP](docs/FILE_MAP.md); confirme no código.
4. Confira regras e decisões relacionadas; preserve funcionalidades e compatibilidade.

| Necessidade | Consultar |
| --- | --- |
| Retomar trabalho | [CURRENT_STATE](docs/CURRENT_STATE.md) |
| Índice completo e política de evidências | [docs/README](docs/README.md) |
| Entender escopo e componentes | [PROJECT_OVERVIEW](docs/PROJECT_OVERVIEW.md), [ARCHITECTURE](docs/ARCHITECTURE.md) |
| Alterar comportamento | [BUSINESS_RULES](docs/BUSINESS_RULES.md), documento da funcionalidade |
| Persistência ou integração | [DATABASE](docs/DATABASE.md), [API_INTEGRATIONS](docs/API_INTEGRATIONS.md) |
| Preparar ambiente e testar | [DEVELOPMENT_GUIDE](docs/DEVELOPMENT_GUIDE.md) |
| Decisões e evolução | [DECISIONS](docs/DECISIONS.md), [CHANGELOG](docs/CHANGELOG.md) |
| Pendências e termos | [KNOWN_ISSUES](docs/KNOWN_ISSUES.md), [ROADMAP](docs/ROADMAP.md), [GLOSSARY](docs/GLOSSARY.md) |

## Durante a implementação

- Siga as convenções Python existentes; mantenha nomes operacionais em português.
- Restrinja alterações ao escopo; reutilize funções/componentes e não recrie funcionalidades.
- Não altere regras de negócio sem autorização. Preserve os contratos de retorno,
  números de bobina como texto, pesos em kg e leitura das chaves antigas do histórico.
- Widgets ficam na thread principal; Playwright nasce, trabalha e fecha na mesma thread.
- Preserve a validação de saldo e a confirmação do salvamento antes do histórico.
- Não registre segredos nem dados operacionais reais em documentação/fixtures.
  `config.py`, histórico, logs, PDFs e planilhas são locais e ignorados pelo Git.
- Execute testes apropriados quando possível. Suíte: `venv\Scripts\python.exe -m unittest discover -s tests -v`.
  Não trate scripts `teste_*.py` como testes unitários; verifique seus efeitos no guia.
- Preserve alterações locais preexistentes; não crie commits automaticamente.

## Após a implementação

1. Atualize apenas o documento da funcionalidade afetada.
2. Atualize FILE_MAP se a estrutura mudar e BUSINESS_RULES se regras mudarem.
3. Registre decisões arquiteturais relevantes em DECISIONS e mudanças em CHANGELOG.
4. Atualize CURRENT_STATE para mudanças relevantes ou trabalho incompleto,
   registrando estado e próximo passo verificável; ajuste ROADMAP conforme o avanço.
5. Preserve IDs e links; diferencie implementado, proposto e pendente de confirmação.
6. Nas respostas, informe objetivamente realizado, arquivos alterados, testes e pendências.

## Recuperação econômica de contexto

Comece pelo índice; abra uma funcionalidade e os trechos de código necessários.
Use `rg` por caminhos/símbolos. Não carregue toda a documentação, releia o repositório
inteiro ou reescreva documentos não afetados. Prefira referências relativas e símbolos
a cópias de código. Não dependa exclusivamente do histórico de conversa.
