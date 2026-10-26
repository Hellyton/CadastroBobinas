# Banco de dados e persistência

## Tecnologia e fronteira

Não há banco de dados próprio, SQL, ORM, tabelas, migrações ou API de persistência
identificados. A persistência local é um arquivo JSON e logs; XLSX é uma exportação.
O banco, as tabelas e a transação interna do EGS: **Não identificado**.

## Modelo em memória

Fonte: [modelos.Bobina](../app/modelos.py). As anotações da dataclass não fazem
validação de tipo/intervalo em tempo de execução.

| Campo | Tipo declarado | Origem / significado verificável |
| --- | --- | --- |
| `numero` | str | Identificador extraído; preservado no campo Observação do EGS |
| `produto` | str | Texto do PDF ou mapeamento do parser |
| `gramatura` | int | Valor nominal extraído para preencher o EGS |
| `formato` | int | Dimensão extraída; HP usa Largura |
| `diametro` | int | Dimensão extraída |
| `peso` | int | Peso em kg; conversão/arredondamento depende do parser |
| `rua` | int, padrão 1 | Enviado ao EGS e à planilha; config.RUA_PADRAO não é consultado |
| `fornecedor` | str, padrão vazio | Atribuído por App.processar_pdf e teste_ambiente; leitor retorna separadamente |

Não há PK/FK, índices, restrições declarativas ou relacionamentos persistidos
entre bobina, nota e produto. O agrupamento por produto é transitório.

## Histórico JSON

Fonte: [historico.py](../app/historico.py). `CAMINHO_HISTORICO` aponta para
`historico_cadastro.json`, relativo ao diretório de execução.
Contrato lógico: objeto com propriedade `cadastradas`, lista de strings, e mapa
opcional `romaneios`, de chave de histórico para número do romaneio. Arquivos
antigos sem esse mapa continuam válidos e seus registros são tratados como sem
romaneio; nenhum número é inferido retroativamente.
Chave nova: `FORNECEDOR_NORMALIZADO|numero`; fornecedor usa `strip().upper()`.
Sem fornecedor, usa `str(numero)`. A marca automática preserva a representação
textual recebida; inclusão/edição manual removem somente espaços externos do
número, preservando zeros, letras e espaços internos, e rejeitam `|` no fornecedor.
O número do romaneio é metadado para consulta/filtro, não parte da identidade.
Não há registro de nota fiscal, peso, horário, tentativa ou status de falha.

| Operação | Comportamento |
| --- | --- |
| `carregar_historico` | Mantém retorno `set`; inexistência, JSON/schema inválido ou OSError retornam set vazio por compatibilidade |
| `bobina_ja_cadastrada` | Busca chave composta e, depois, número puro para reconhecer legado |
| `marcar_cadastrada(numero, fornecedor=None, romaneio=None)` | Recarrega estritamente, adiciona chave e, se informado, guarda o romaneio; ordena chaves e grava JSON UTF-8 por arquivo temporário e `os.replace` |
| `listar_registros` | Retorna registros com chave, fornecedor, número e `romaneio`; chave antiga sem metadado aparece sem romaneio |
| Gestão manual | Lista, adiciona, edita e exclui chaves e metadados; `adicionar_cadastrada`/`editar_registro` aceitam `caminho=None, romaneio=None`; `None` preserva o valor existente e string vazia limpa. JSON inválido ou schema inesperado gera erro e não é substituído |
| `CadastroBobinas._executar` | Lê histórico uma vez para filtrar o lote; marca cada sucesso confirmado |
| `usar_historico=False` | Não lê/grava histórico no fluxo de cadastro; usado no simulador |

Compatibilidade com entradas antigas é uma consulta alternativa, não uma
migração executada. Não existe versão de schema nem ferramenta de migração.
O leitor estrito usado por marcação/gestão exige objeto com `cadastradas` como
lista de strings não vazias e valida o mapa opcional `romaneios`; a API pública de carregamento conserva o retorno
`set` em erro para não alterar o contrato do filtro de cadastro.

## Integridade e recuperação

- A marca local ocorre depois da confirmação de saldo do EGS; falha de disco
  nesse intervalo pode deixar cadastro remoto sem marca local.
- Arquivo temporário no mesmo diretório e `os.replace` evitam truncamento no meio
  da gravação. Não há lock/transação entre instâncias: atualizações simultâneas
  ainda podem se sobrescrever. Deduplicação não é garantia remota.
- O filtro continua recebendo set vazio quando o carregamento encontra arquivo
  inválido/ilegível; ausência de chave local não prova ausência de cadastro no
  EGS. Escritas estritas falham sem sobrescrever o arquivo inválido. Entrada
  legada sem fornecedor vale para todos.
- Duplicatas dentro do PDF não são removidas após o filtro inicial.
- O romaneio informado é capturado antes do worker e só é associado à chave após
  salvamento confirmado. No cadastro manual, a interface exige o número do
  romaneio; inclusão/edição podem revisar ou limpar esse metadado. Filtros por
  romaneio não mudam a chave nem o conjunto usado para prevenção de recadastro.
- Preserve o histórico operacional ao transferir máquinas; não o versione nem
  o edite para presumir sucesso. Após falha, confronte a situação no EGS.

Riscos com evidências: [KI-01 a KI-03 e KI-12](KNOWN_ISSUES.md).
Regras: [RN-15 a RN-17](BUSINESS_RULES.md). Nenhum dado operacional real foi
copiado para esta documentação e nenhuma migração foi executada.

## Outros arquivos

`logs/cadastro.log` é adicionado na importação de `app.logger`, com rotação de
1 MB e UTF-8. Não há retenção máxima configurada. XLSX é criado no caminho
escolhido, com uma aba de bobinas; não é utilizado como entrada nem histórico.
Backups automáticos e política institucional de retenção: **Não identificado**.
