# Ambiente de teste manual com simulador local

## Objetivo
Exercitar leitura de PDF e automação contra HTML local, sem cadastro no EGS.

## Status atual
Implementado no commit inicial; não executado nesta tarefa. A suíte unitária
usa mocks Python e não depende deste HTML.

## Fluxo de funcionamento
Servidor http.server na raiz fornece HTML. Script escolhe PDF por argumento ou
diálogo, detecta/solicita fornecedor, atribui fornecedor às bobinas e inicia
CadastroBobinas com URL local e `usar_historico=False`. HTML simula login, Novo,
aviso de peso, cálculo após blur, Salvar/Sair e atualização de saldo/tabela.

## Regras de negócio
Reutiliza regras de extração/cadastro; mock apenas aceita peso não zero para salvar.
Não representa restrições oficiais do EGS. [RN-17](../BUSINESS_RULES.md) permite
desabilitar histórico; saldo inicial do mock é 25000 kg.

## Arquivos relacionados
[teste_ambiente.py](../../teste_ambiente.py),
[mock_sistema.html](../../mock/mock_sistema.html),
[cadastro.py](../../app/cadastro.py), [navegador.py](../../app/navegador.py).

## Funções e classes principais
`escolher_arquivo`, `escolher_fornecedor_manualmente`, `URL_TESTE`;
JavaScript `abrirModal`, `mostrarPopupPeso`, `atualizarSaldo`, `SALDO_INICIAL`.

## Entradas e saídas
PDF local e confirmações CLI → tabela/saldo no DOM e saída terminal/log.
URL: `http://localhost:8000/mock/mock_sistema.html`.

## Persistência de dados
Não lê/grava histórico pelo fluxo. Dados simulados somem ao recarregar HTML;
logs locais ainda podem ser gerados pelo logger.

## Integrações
http.server da biblioteca padrão e Chromium/Playwright. `fazer_login` ainda
preenche valores de config no HTML: use configuração de desenvolvimento sem
segredos. Comandos e preparação estão no [guia](../DEVELOPMENT_GUIDE.md).

## Validações e exceções
Sem arquivo ou sem bobinas reconhecidas, script encerra. Fornecedor desconhecido
oferece menu manual. Mock aceita qualquer login, calcula valores fictícios após
400 ms e não valida permissões nem nota real.

## Interface do usuário
Diálogo inicial opcional, confirmações por terminal e página local simplificada.
Não usa a janela App de produção durante cadastro.

## Testes relacionados
É ferramenta de teste manual, não teste automatizado. Não executar
`teste_cadastro.py` como alternativa: contrato antigo incompatível ([KI-06](../KNOWN_ISSUES.md#ki-06--script-manual-incompativel)).
`teste_bobina.py` aponta ao destino de config e só preenche, sem salvar.

## Limitações conhecidas
Sem backend/persistência/permissões reais, dinâmica e fórmulas não homologadas;
[KI-09](../KNOWN_ISSUES.md#ki-09--cobertura-de-testes-e-simulador).
Não prova funcionamento de produção nem qualidade de todos os PDFs.

## Melhorias planejadas
Nenhuma aprovada identificada. Cenários de integração/fixtures sanitizadas
dependem de definição no [ROADMAP](../ROADMAP.md).
