# APIs e integrações

Não há endpoints próprios, cliente REST/SDK do EGS, webhooks ou contratos de
API identificados. A integração EGS usa sua interface web e seletores CSS.

## EGS Sistemas

- **Objetivo:** login e classificação de bobinas na nota selecionada pelo operador.
- **Arquivos:** [navegador.py](../app/navegador.py), [cadastro.py](../app/cadastro.py).
- **Destino:** `config.URL`; exemplo público em [config.example.py](../config.example.py):
  `https://app.egssistemas.com.br/login`. Caminhos internos de classificação: **Não identificado**.
- **Autenticação:** `USUARIO`, `SENHA`, `CHAVE_ACESSO` preenchidos no formulário;
  valores mantidos localmente, nunca reproduzidos aqui. Não há login no aplicativo desktop.
- **Operações:** navegar, preencher login, abrir Novo, ler saldo, preencher bobina,
  esperar cálculos, clicar Salvar, conferir saldo, tentar fechar modal após falha.
- **Entrada:** `Bobina`, peso e saldo anterior. Campos enviados: Rua, Diâmetro,
  Formato, Peso, Gramatura e Observação com número da bobina. Produto e nota são
  escolhidos na interface do EGS pelo operador; não são enviados em campo pelo robô.
- **Saída:** valores de saldo/quantidade classificada lidos como float ou None;
  conclusão de salvar ou `SalvamentoNaoConfirmado`. Métodos de interação em geral
  não retornam objeto remoto nem identificador de cadastro.
- **Erros:** login/navegação propagam exceções; leitura de saldo converte exceções
  em None; confirmação incerta interrompe lote; outras falhas são contabilizadas
  e disparam tentativa de fechar modal. Pela interface, o navegador fica aberto ao
  final e fecha quando o operador o fecha, outro cadastro começa ou o app fecha.
- **Limitações:** dependência do DOM, posições `nth-child`, formatação pt-BR,
  seleção humana e disponibilidade/rede. Sessão compartilhada com outras instâncias,
  limites oficiais, MFA e permissões por perfil: **Não identificado**.
- **Dependências:** Playwright síncrono, Chromium visível e configuração Python local.

Contrato de sucesso e tempos: [preenchimento EGS](features/PREENCHIMENTO_EGS.md).
Os seletores do código prevalecem sobre [botoes.txt](../botoes.txt).

## PDFs de fornecedores

- **Serviço/origem:** arquivos locais fornecidos pelo operador; não há download automatizado.
- **Arquivos:** [leitor_pdf.py](../app/leitor_pdf.py), [parsers.py](../app/parsers.py).
- **Entrada/saída:** caminho PDF e fornecedor opcional → `(list[Bobina], fornecedor, ajuste_peso)`.
- **Autenticação:** nenhuma implementada para arquivo; PDF protegido/corrompido pode falhar.
- **Erros:** fornecedor desconhecido retorna lista vazia; linhas fora do padrão
  podem ser ignoradas; erros de abertura/conversão não são todos capturados.
- **Limitações:** sem OCR e com layouts específicos; [importação](features/IMPORTACAO_ROMANEIOS.md)
  aponta aos quatro parsers e às diferenças de unidades/formatação.
- **Dependência:** pdfplumber; Cocelpa usa coordenadas de palavras, demais usam texto.

## Arquivos XLSX e JSON

Exportação local via openpyxl: [exportação Excel](features/EXPORTACAO_EXCEL.md).
Não há automação do Microsoft Excel, conexão com planilha online nem importação XLSX.
Persistência JSON usa biblioteca padrão, sem serviço externo ou autenticação;
contrato e falhas estão em [DATABASE](DATABASE.md).

## Simulador e logs

`teste_ambiente.URL_TESTE` acessa `http://localhost:8000/mock/mock_sistema.html`,
servido manualmente com `http.server`. HTML aceita qualquer login e mantém dados
apenas no DOM/memória JavaScript. O fluxo ainda preenche credenciais de config
no HTML local; para usá-lo, empregue configuração de desenvolvimento sem segredos.
Não existe validação do backend nem persistência remota no mock.

Loguru grava mensagens de status/erros em destino local relativo, com rotação.
Falhas podem incluir objetos Bobina; não copiar logs reais para a memória técnica.
Detalhes e limitações: [simulador](features/SIMULADOR_LOCAL.md), [KI-10](KNOWN_ISSUES.md#ki-10--ambiente-e-diagnostico).
