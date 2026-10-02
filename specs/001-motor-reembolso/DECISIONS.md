# Log de Decisões e Mudanças de Spec

> Uma entrada **toda vez** que a spec mudar. Este arquivo é a prova de que a spec
> foi tratada como artefato vivo e não como cerimônia de abertura.
>
> Spec que não muda em dois dias é spec que ninguém consultou. Mudança não é
> demérito — mudança não registrada é.

Ordem cronológica inversa: a mais recente primeiro.

---

## D-004 — Valor gigante e chave repetida: spec 1.3 → 1.6 · `2026-10-01`

**Gatilho:** escrita do `plan.md` 1.0. Ao verificar como o código leria o arquivo, apareceram duas entradas válidas no formato cujo resultado a spec não definia. O responsável decidiu as duas (versão 1.4, não commitada). A rodada do `spec-adversary` sobre a 1.4 apontou 4 problemas (1 bloqueante) nas próprias decisões; o responsável aceitou as 4 recomendações, aplicadas na 1.5 (pontos 3 a 6). A rodada sobre a 1.5 apontou 4 problemas, nenhum bloqueante; o responsável aceitou as 4 recomendações, aplicadas na 1.6 (pontos 7 a 10). Sessão `docs/sessions/07-*`.

**O que mudou na spec:**

| # | Ponto | De (1.3) | Para (1.6) | Onde |
|---|---|---|---|---|
| 1 | `valor` sem limite superior (ex.: 1e999999) | indefinido; o cálculo exato ao centavo não é possível para qualquer número, e a execução seria interrompida | valor absoluto a partir de 1.000.000.000,00, comparado com o número recebido → `entrada_invalida` (também se negativo, antes de `valor_invalido`) | RN-002, seção 4 (motivos), AMB-018, seção 7 |
| 2 | Chave repetida num objeto (ex.: dois `valor`) | indefinido; a leitura ficaria com uma delas em silêncio | vale a última ocorrência; cada chave repetida gera aviso com texto fixo em `itens[].avisos` (dentro da despesa) ou `avisos` do topo (fora) | RN-013 (nova), seção 4 (entrada e saída), seção 8, AMB-019, seção 7 |
| 3 | Precisão do "número recebido" (**bloqueante** na 1.4) | indefinida: lido aproximado, 999999999.995 arredondava para 999999999,99, contra o aceite da própria RN-002 (e 10.005 contra a RN-003); `valor_informado` de 1e999999 sem esperado | todo número vale pelo valor decimal exato escrito no arquivo, com quaisquer dígitos e expoente; teto, arredondamento e `valor_informado` usam esse valor | seção 4, RN-003, seção 7 |
| 4 | Ordem e contagem de aviso de chave aninhada que também aparece em valor descartado | indefinidas | contam só as ocorrências dentro do valor que valeu | RN-013, seção 7 |
| 5 | Caminho do aviso | sem regra para elemento de `despesas` que é lista; chaves com `.`, `[`, `]` ou vazias geram caminhos ambíguos | lista começa pela posição (`[0].a`); chaves sem escape, ambiguidade registrada como risco aceito | RN-013, seção 10, seção 7 |
| 6 | Igualdade de chaves | "caractere a caractere" sem dizer se antes ou depois dos escapes (`"\u0076alor"`) | depois de decodificar os escapes, sem normalização Unicode; caminho usa o texto decodificado | RN-013, seção 7 |
| 7 | Escape sem caractere válido (`\ud800` sem par) | indefinido; aceito pelo parser, a gravação da saída falharia | erro de arquivo, em chave ou valor; "caractere" é o caractere Unicode | seção 4, RN-002, seção 7 |
| 8 | Escapes nos valores de texto | o ponto 6 falava só de chaves | todo texto da entrada, chave ou valor, vale depois de decodificados os escapes | seção 4, seção 7 |
| 9 | Texto exato do aviso | lista dentro de lista, `<n>` ≥ 1000 e "sem escape" indefinidos | colchetes encadeados (`m[0][0].x`); `<n>` sem separador de milhar; "sem escape" vale só para o caminho; saída em UTF-8 com os escapes do formato | RN-013, seção 4, seção 7 |
| 10 | Descrição do risco "caminho ambíguo" | dizia que a ambiguidade só afeta campos extras — **justificativa incompleta da 1.5** | inclui aviso de campo extra idêntico ao de campo da seção 4 e chave que imita outro aviso | seção 10 |

**Por quê:** o ponto 1 deixaria uma despesa derrubar a execução inteira, contra o tratamento por item da RN-002; recusar como `entrada_invalida` preserva as demais. O ponto 3 fecha o que o ponto 1 deixou aberto: o teto limita a magnitude, e a leitura exata garante que o valor aceito é o escrito. O ponto 2 muda o reembolso conforme a ocorrência escolhida; a última ocorrência foi a escolhida, e o descarte fica visível ao conferente em campo contratual, em vez de texto livre na justificativa ou no terminal. Os pontos 4 a 6 tornam o texto e a ordem dos avisos determinísticos, já que são contratuais; escapar caracteres no caminho foi descartado para manter o aviso legível. Os pontos 7 a 9 fecham entradas válidas pela sintaxe sem resultado definido; o 10 corrige a descrição de um risco aceito, como o ponto 2 da D-002.

**O que isso invalidou:** nenhum código ou teste (ainda não existem). Formato de saída: dois campos novos (`itens[].avisos`, `avisos`), sempre presentes. Nenhum valor do resultado esperado do exemplo mudou (seção 9; `avisos` vazios). Casos de borda novos: 16 linhas na seção 7. Risco aceito novo na seção 10 (caminho ambíguo). Critério de aceite da seção 9 passa a citar RN-001 a RN-013. `plan.md` passa a se basear na 1.6.

**Tasks afetadas:** nenhuma (o `tasks.md` ainda não foi escrito).

**Custo:** 3 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`); 10 pontos decididos na mesma sessão. Duas rodadas do `spec-adversary`: sobre a 1.4 (por mudar o formato de saída) e sobre a 1.5 (pontos 3 a 6). Sem rodada sobre a 1.6: os pontos 7 a 10 são ajustes de texto sem mudança de regra de cálculo, recomendados pela própria rodada da 1.5.

---

## D-003 — Validação final antes do plano: spec 1.2 → 1.3 · `2026-10-01`

**Gatilho:** conferência da spec 1.2 (commit `bdb1eec`) antes de iniciar o `plan.md`, pedida pelo responsável. Saíram uma contradição interna e três lacunas de contrato. As quatro recomendações foram aceitas pelo responsável (sessão `docs/sessions/06-*`).

**O que mudou na spec:**

| # | Ponto | De (1.2) | Para (1.3) | Onde |
|---|---|---|---|---|
| 1 | Categoria de despesa `entrada_invalida` (**contradição**) | seção 4: normalizada se reconhecida; RN-002: "como veio" | normalizada se reconhecida, em qualquer status ou motivo; senão, como veio | seção 4, RN-002 |
| 2 | Arquivo de saída preexistente em erro de arquivo | "não deixa arquivo de saída" (silencioso sobre arquivo já existente) | não cria nem altera o arquivo de saída; um arquivo preexistente permanece como estava | seção 4 (Interface), RN-002, seção 9 |
| 3 | Erro de uso da CLI | indefinido | subcomando diferente de `calcular` ou `--input`/`--output` ausentes: mensagem de erro, código diferente de 0, saída não criada nem alterada | seção 4 (Interface), seção 9 |
| 4 | `colaborador.id`/`nome` com texto vazio | aceito (só exigia texto) | erro de arquivo, coerente com o tratamento de texto vazio nas despesas (D-002, ponto 5) | RN-002 |

**Por quê:** o ponto 1 obrigaria o código a escolher entre duas seções; os pontos 2 a 4 deixavam comportamentos observáveis (código de saída, arquivo no disco) sem definição. Recomendações: regra única de categoria (mais simples e já válida para recusas nas etapas 3 e 4); não apagar arquivo do usuário; erro de uso com o mesmo contrato do erro de arquivo; mesmo critério de texto vazio em todo o arquivo.

**O que isso invalidou:** nenhum código ou teste (ainda não existem). Nenhum valor do resultado esperado do exemplo mudou (seção 9). Casos de borda novos: 4 linhas na seção 7.

**Tasks afetadas:** nenhuma (o `tasks.md` ainda não foi escrito).

**Custo:** 2 arquivos (`spec.md`, `DECISIONS.md`); 4 pontos decididos na mesma sessão. Sem nova rodada do `spec-adversary`: as mudanças fecham lacunas apontadas na conferência e não alteram regra de cálculo.

---

## D-002 — Segunda revisão adversarial: spec 1.1 → 1.2 · `2026-10-01`

**Gatilho:** nova rodada do `spec-adversary` sobre a 1.1 (commit `d35f68d`), focada no que a D-001 mudou: 6 problemas, 1 bloqueante. Decididos um a um pelo responsável (sessão `docs/sessions/05-*`).

**O que mudou na spec:**

| # | Ponto | De (1.1) | Para (1.2) | Onde |
|---|---|---|---|---|
| 1 | Duplicata de hospedagem ≤ 100,00 em que só uma cópia tem nota (**bloqueante**) | sobrevivia a primeira na ordem; com a cópia sem nota primeiro, a viagem sumia — contradizia a justificativa da D-001 (4a) de independência da ordem | a original é a **primeira com nota fiscal**; se nenhuma tem, a primeira na ordem | RN-007, seção 8 (etapa 7), AMB-010 |
| 2 | Hospedagem irrisória com nota declarada | AMB-004 afirmava que exigir nota fechava a brecha — **erro de justificativa da 1.1** (a nota é só declarada) | regra mantida; justificativa corrigida; registrado como risco aceito; indicação explícita de viagem na entrada registrada como evolução (o formato fixo não permite) | AMB-004, seção 3, seção 10 |
| 3 | Normalização de texto | só espaço comum nas pontas e 3 exemplos de acento; separadores internos preservados (`Transporte Urbano`, como o RH escreveu, era recusada) | regra completa em 4 passos: espaços em branco de qualquer tipo nas pontas, caixa, qualquer diacrítico (independentemente da codificação), espaço/hífen/sublinhado internos = um `_` | seção 5, RN-006, AMB-011 |
| 4a | Campo com tipo errado (`"id": 17`) | "como veio" × "texto ou nulo" | `entrada_invalida`; campo sai nulo se não for texto | RN-002, seção 4 |
| 4b | `competencia` não textual | indefinido | copiada se for texto; nula caso contrário; nunca é erro | RN-002, seção 4 |
| 4c | Arredondamento da metade negativa | "metade para cima" | "metade afastando do zero" (-0,005 → -0,01); positivos inalterados | RN-003, AMB-014 |
| 4d | Falha ao gravar a saída | não listada | erro de arquivo | RN-002, seção 4 (Interface) |
| 5 | Texto vazio em `id`/`categoria`/`fornecedor` | aceito como texto | `entrada_invalida` | RN-002 |
| 6 | D-001 sem o ponto 12 | tabela pulava do 11 ao 13 — **erro de registro** | linha 12 incluída na D-001 antes do commit da 1.1 | `DECISIONS.md` |

**Por quê:** o ponto 1 obrigaria o código a escolher entre a regra literal e a justificativa; os pontos 3, 4 e 5 deixavam saídas indefinidas ou não determinísticas; os pontos 2 e 6 eram erros de redação/registro da revisão anterior.

**O que isso invalidou:** nenhum código ou teste (ainda não existem). Nenhum valor do resultado esperado do exemplo mudou (seção 9). Casos de borda novos: 10 linhas na seção 7.

**Tasks afetadas:** nenhuma (o `tasks.md` ainda não foi escrito).

**Custo:** 2 arquivos (`spec.md`, `DECISIONS.md`); 6 pontos decididos na mesma sessão.

---

## D-001 — Revisão adversarial e análise dos dados: spec 1.0 → 1.1 · `2026-10-01`

**Gatilho:** revisão da spec 1.0 (commit `c8bcad9`) antes do plano, em duas frentes: o subagente `spec-adversary` (9 problemas, 2 bloqueantes) e uma nova análise item a item de `exemplos/despesas-exemplo.json`. Os 13 pontos resultantes foram decididos um a um pelo responsável (sessão `docs/sessions/05-*`).

**O que mudou na spec:**

| # | Ponto | De (1.0) | Para (1.1) | Onde |
|---|---|---|---|---|
| 1 | d-008 "lançado com atraso" | recusa pela data da despesa | **mantido**; justificativa reforçada (a regra seria letra morta na leitura literal) | AMB-009 |
| 2a | Prova de viagem | qualquer hospedagem válida | só hospedagem **com nota fiscal** | RN-010, AMB-004 |
| 2b | Dias em viagem | só a data da diária | data da diária **e o dia seguinte** | RN-010, RN-012, AMB-004 |
| 3 | Nota fiscal fracionada | por lançamento, sem menção ao risco | **mantido** por lançamento; brecha registrada como risco aceito | AMB-008, seção 10 |
| 3b | Valor de 100,00 em viagem | implícito | explícito: **não amplia** | RN-008, AMB-007 |
| 4a | Ordem nota × duplicata | duplicata (6) antes da nota (7) | **nota (6) antes da duplicata (7)**; despesa sem nota sai da comparação | RN-007, RN-008, seção 8, AMB-010, AMB-016 |
| 4b | Quase-duplicatas | não mencionado | comparação exata **mantida**; registrado como risco aceito | RN-007, seção 10 |
| 5a | Valor zero | `valor_invalido` (não aprovado explicitamente) | **confirmado** | RN-004, AMB-013 |
| 5b | Acentos | não ignorados (`alimentação` recusada) | **ignorados** na categoria e no fornecedor | seção 5 (normalização), RN-006, RN-007, AMB-011 |
| 6 | d-001 "Almoço com cliente" | não tratado | alimentação normal; representação como evolução | AMB-017 (nova), seção 3 |
| 7 | Campos de despesa `entrada_invalida` | indefinidos | `valor_considerado` nulo, categoria como veio, **fora dos totais** | RN-002, seção 4 |
| 8 | `valor_informado` × 2 casas | contraditórios | `valor_informado` isento; é o número recebido | seção 4 |
| 9 | Entrada malformada | lacunas | `colaborador` ausente = erro de arquivo; elemento não-objeto = `entrada_invalida`; `id`/`data` podem ser nulos; campos extras ignorados | RN-002, seção 4 |
| 10 | Formato de saída | proposto | **confirmado**; limite esgotado = `recusado`; justificativa não contratual | seção 4, RN-009 |
| 11 | Seção 9 (resultado do exemplo) | "nenhuma data em viagem" — **erro**: contradizia a RN-010 para d-010 | 14/07 e 15/07 em viagem; d-011 com limite 90,00. Valores e totais inalterados | seção 9 |
| 12 | Registro desta revisão | — | commit da 1.0 (`c8bcad9`) preservado como "antes"; mudanças registradas nesta entrada D-001 e aplicadas na 1.1 | `DECISIONS.md` |
| 13 | Pontos em aberto | — | ids repetidos e `competencia` inconsistente mantidos como decisões provisórias | seção 10 |

**Por quê:** os dois bloqueantes (7 e 8) obrigariam o código a inventar regra; as brechas 2a, 3 e 4 mudavam valores em cenários plausíveis; o item 11 era um erro de redação da 1.0 apontado pelo `spec-adversary`.

**O que isso invalidou:** nenhum código ou teste (ainda não existiam). Na spec: a etapa 6/7 da ordem de aplicação, a definição de viagem, o caso de borda "duplicata depois de despesa recusada por nota" (agora as duas cópias são `nota_fiscal_ausente`) e o caso "categoria com acento" (agora reconhecida).

**Tasks afetadas:** nenhuma (o `tasks.md` ainda não foi escrito).

**Custo:** 2 arquivos (`spec.md`, `DECISIONS.md`); revisão de 13 pontos numa sessão.
