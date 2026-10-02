# Log de Decisões e Mudanças de Spec

> Uma entrada **toda vez** que a spec mudar. Este arquivo é a prova de que a spec
> foi tratada como artefato vivo e não como cerimônia de abertura.
>
> Spec que não muda em dois dias é spec que ninguém consultou. Mudança não é
> demérito — mudança não registrada é.

Ordem cronológica inversa: a mais recente primeiro.

---

## D-006 — Arquivo defeituoso: escape inválido em ocorrência descartada e codificação da entrada: spec 1.8 → 1.9 · `2026-10-01`

**Gatilho:** revisão independente da T-007 (`docs/reviews/T-007.md`, revisões 1 e 2, "Decisões necessárias" 1). A seção 4 dizia que escape sem caractere válido "em qualquer chave ou valor" é erro de arquivo; a RN-013 dizia que as ocorrências descartadas por chave repetida "nenhuma regra as considera". Para `"obs": "\uD800", "obs": "ok"` as duas leituras davam resultados opostos (erro de arquivo × despesa processada com aviso). O código da T-006 seguia a segunda sem decisão explícita: só verificava os valores que valeram. Decidido pelo responsável (ponto 1). A rodada do `spec-adversary` sobre a primeira redação da 1.9 apontou 3 problemas (1 bloqueante): a codificação da entrada não estava na spec (só no DT-002 do plano), o parêntese `\uD800` a `\uDFFF` podia ser lido como exemplo e não como lista, e o alcance do descarte em profundidade era ambíguo na RN-013. O responsável aceitou as 3 recomendações (pontos 2 a 4), que registram na spec o que o plano e o código já faziam. A rodada de confirmação apontou 4 problemas (2 bloqueantes): a seção 8 podia ser lida como se todo erro de arquivo da RN-002 valesse para a ocorrência descartada; "JSON válido" não tinha definição (caractere de controle cru, `NaN`, `01.5`); "par correspondente" e BOM repetido sem resultado. O responsável aceitou as 4 recomendações (pontos 5 a 8). A confirmação final não apontou bloqueante; o único achado (limites de profundidade e tamanho que a RFC 8259 deixa à implementação) virou risco aceito (ponto 9), depois de o teste mostrar que a leitura quebrava com erro interno a partir de alguns milhares de níveis. Sessão `docs/sessions/18-*`.

**O que mudou na spec:**

| # | Ponto | De (1.8) | Para (1.9) | Onde |
|---|---|---|---|---|
| 1 | Escape sem caractere válido numa ocorrência descartada por chave repetida | contraditório entre seção 4 e RN-013 | **erro de arquivo**, como em qualquer outra chave ou valor; o descarte da RN-013 vale para as regras de negócio, não para a validade do arquivo | seção 4, RN-013 (regra e aceite) |
| 2 | Codificação da entrada (**bloqueante** na revisão) | indefinida na spec (BOM, Latin-1, substituto gravado em bytes crus) | UTF-8; BOM no início ignorado; byte fora do UTF-8 em qualquer lugar → erro de arquivo | seção 4, RN-002 |
| 3 | Conjunto de escapes inválidos | parêntese `\uD800` a `\uDFFF` lido como lista ou exemplo | lista completa; `\u0000`, `\uFFFF` e demais formam caractere válido | seção 4 |
| 4 | Profundidade do descarte | RN-013 podia ser lida como só o primeiro nível | em qualquer profundidade; explicitado na RN-002, na RN-013 (regra e aceite) e na seção 8 | RN-002, RN-013, seção 8 |
| 5 | Quais erros atingem a ocorrência descartada (**bloqueante** na confirmação) | seção 8 citava "erro de arquivo, RN-002" sem restrição | só a forma do arquivo (UTF-8, JSON válido, escapes); campos ausentes, vazios, de tipo errado ou datas inválidas valem só para o valor que valeu (`nome` `""` corrigido por `nome` `"Ana"` é processado) | RN-013, seção 8 |
| 6 | Definição de "JSON válido" (**bloqueante** na confirmação) | indefinida | RFC 8259 sem extensões: caractere de controle cru em texto, `NaN`/`Infinity`, `01.5`, `.5`, `1.`, `+1` → erro de arquivo | seção 4 |
| 7 | Par correspondente | indefinido | escape `\uD800`–`\uDBFF` seguido imediatamente de `\uDC00`–`\uDFFF`; qualquer outra combinação é inválida | seção 4 |
| 8 | BOM repetido no início | indefinido (código aceitava dois, por efeito de duas camadas de leitura) | só um BOM é ignorado; o segundo torna o arquivo JSON inválido | seção 4 |
| 9 | Limites de aninhamento e tamanho (RFC 8259, seção 9) | indefinidos; o código quebrava com erro interno a partir de ~1.000 níveis | risco aceito: aninhamento muito profundo ou tamanho exagerado pode ser erro de arquivo; limite não fixado | seção 10 |

**Por quê:** escape sem par só aparece em arquivo corrompido ou gerado com defeito; o lugar onde ele está (valor que valeu ou descartado, em qualquer profundidade) não muda isso. Recusar o arquivo mantém a regra da seção 4 sem exceção e evita processar um arquivo suspeito. O ponto 2 aplica o mesmo motivo ao defeito gravado sem escape: byte fora do UTF-8 é recusado onde quer que esteja; o BOM é aceito porque ferramentas comuns o gravam em arquivos corretos. O ponto 3 fecha o conjunto: caracteres de controle e não caracteres existem no Unicode e podem ser gravados em UTF-8, então não são defeito. O ponto 5 preserva o motivo da AMB-019: a chave repetida existe para aceitar a correção feita ao final do registro, e recusar o arquivo pelo conteúdo do valor corrigido anularia isso; só a forma do arquivo, que indica defeito na geração, é verificada por inteiro. Os pontos 6 e 7 adotam o padrão do formato, que qualquer ferramenta consegue conferir. O ponto 8 mantém a regra estrita: um BOM é prática comum de ferramentas, dois é defeito. O ponto 9 não fixa número porque nenhum limite tem origem na política; o que importa é que o arquivo absurdo termine como erro de arquivo, sem saída e sem erro interno. Emoji válido (par completo ou caractere direto) continua aceito em qualquer texto.

**O que isso invalidou:** o código da T-006 (`_verificar_textos` percorria só os valores que valeram); corrigido em commit `fix(T-006)`. Os pontos 2 a 4 não mudam código: o DT-002 já lia `utf-8-sig` estrito e verificava só U+D800 a U+DFFF, com testes na T-006 (`test_bom_e_aceito`, `test_rn002_utf8_invalido_e_erro_de_arquivo`, inclusive substituto em bytes crus); o ponto 3 ganha `test_escape_fora_dos_substitutos_forma_caractere_valido`. Os pontos 5 a 7 também refletem o comportamento já existente (pontos 6 e 7 ganham casos em `test_rn002_json_malformado_e_erro_de_arquivo` e `test_rn002_escape_sem_par_em_valor_e_erro_de_arquivo`; o ponto 5 é coberto na T-008, que valida o cabeçalho sobre o valor que valeu). O ponto 8 muda código: o segundo BOM era aceito; corrigido no mesmo `fix(T-006)`, com `test_segundo_bom_e_erro_de_arquivo`. O ponto 9 também: o estouro de recursão da leitura vira `ErroDeArquivo`, com `test_aninhamento_exagerado_e_erro_de_arquivo` (5.000 e 100.000 níveis). DT-002 do `plan.md` alinhado na versão 1.2. Nenhum valor do exemplo (seção 9) mudou; seção 7 não muda (contagem de 63 casos preservada).

**Tasks afetadas:** T-006 (aceite ganha os testes de ocorrência descartada, escapes válidos, JSON inválido pela RFC 8259, par correspondente, segundo BOM e aninhamento exagerado); T-008 (aceite ganha `colaborador` corrigido por chave repetida, ponto 5).

**Custo:** 4 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`, `tasks.md`) + correção de uma função e um teste. Três rodadas do `spec-adversary` (sobre a primeira redação da 1.9, confirmação com 4 achados e confirmação final).

---

## D-005 — Normalização: só letras e algarismos contam: spec 1.6 → 1.8 · `2026-10-01`

**Gatilho:** revisão independente da T-003 (`docs/reviews/T-003.md`, revisão 1, BLOQUEADO). O passo 4 da seção 5 só tratava sequências **internas** de separadores e o passo 1 só removia espaço em branco das pontas: hífen ou sublinhado no início ou no fim não tinham resultado definido (`"-Bistro"` × `"_Bistro"` mudam a RN-007). O passo 3 não dizia se `ø`, `ł`, `đ` contam como letra com sinal. O responsável decidiu os dois pontos (versão 1.7, não commitada). A rodada do `spec-adversary` sobre a 1.7 apontou 5 problemas (1 bloqueante): o conjunto de "hífens" e de "espaços em branco" não estava fechado (travessão U+2013 colocado pelo editor, espaço de largura zero, BOM, caracteres de controle). O responsável optou por trocar as listas por uma regra única, "só letras e algarismos contam". A rodada do `spec-adversary` sobre essa versão apontou 5 problemas (2 bloqueantes): "letra", "algarismo decimal" e "sinal combinante" sem conjunto definido (`Nº` × `N°`), e "espaço em branco" ainda aberto para `id` e `colaborador`. O responsável aceitou as 5 recomendações (pontos 8 a 12), aplicadas na mesma versão 1.8. A rodada de confirmação não apontou bloqueante; os 4 achados (uma contradição de redação e três cantos do Unicode sem efeito em dados realistas) foram registrados no ponto 13, como combinado com o responsável. Sessão `docs/sessions/13-*`.

**O que mudou na spec:**

| # | Ponto | De (1.6) | Para (1.8) | Onde |
|---|---|---|---|---|
| 1 | Separadores | espaço em branco, hífen (`-`) e sublinhado; nas pontas, só espaço em branco removido; hífen e sublinhado nas pontas indefinidos | todo caractere que não é letra nem algarismo decimal é separador (inclui travessão, pontuação, símbolo, emoji, invisível, controle); nas pontas, removido; no meio, cada sequência vale um `_` | seção 5 (passo 3 e exemplos), AMB-011 |
| 2 | Letras sem decomposição canônica (`ø`, `ł`, `đ`) | indefinido | **ficam como estão**; letra base é a da decomposição canônica do Unicode; risco aceito | seção 5 (passo 2), seção 10 |
| 3 | Sinal combinante sem letra (sobre hífen, no início, U+0338, seletor de variação) | indefinido | todo sinal combinante é descartado, acompanhe ele uma letra ou não; descartado antes de separar, então `"alimentacao-́"` → `alimentacao` | seção 5 (passo 2) |
| 4 | Ordem dos passos | pontas → caixa → acentos → separadores internos | caixa → acentos → separadores (pontas e meio juntos) | seção 5 |
| 5 | Equivalência de caixa | "ignorar maiúsculas/minúsculas", sem dizer qual | equivalência completa de caixa do Unicode (`ß` = `ss`) | seção 5 (passo 1) |
| 6 | `categoria` ou `fornecedor` só de separadores (`"-"`, `"***"`) | válido; normalizava para vazio e todos os fornecedores "vazios" eram iguais na RN-007 | `entrada_invalida`, como o texto só com espaços | RN-002 (regra e aceite), seção 5, seção 7 (linha "Texto vazio em campo obrigatório") |
| 7 | Caractere invisível no meio da palavra | — | é separador (`ali_mentacao`); risco aceito | seção 10 |
| 8 | Conjuntos de "letra", "algarismo decimal" e "sinal combinante" | indefinidos (`Nº` × `N°`, `²`, `١`, sinais com espaço próprio) | categorias Unicode "letra" (inclui `º`, `ª`, `ʼ`), "dígito decimal" (mantido como está) e "marca" (todas as três subcategorias); o passo 2 trata o resultado do passo 1 | seção 5 |
| 9 | "Espaço em branco" em `id`, `colaborador.id` e `nome` | indefinido (BOM, espaço de largura zero, U+001C a U+001F) | propriedade White_Space do Unicode; os demais não são espaço; `id` e `nome` não são normalizados (`id` `"-"` é válido) | RN-002 |
| 10 | Fornecedor visualmente idêntico (invisível, letra de outro alfabeto) | risco descrito só para a categoria | risco aceito descrito também para o fornecedor, que não aparece na saída | seção 10 |
| 11 | Formas de compatibilidade (largura total, sobrescritos) | indefinido | distintas da forma comum; risco aceito | seção 10 |
| 12 | Comportamentos novos fora da seção 7 | — | **mantido**: exemplos da seção 5 testados na T-003; seção 7 não muda (contagem de 63 casos preservada) | — |
| 13 | Redação e cantos do Unicode (rodada de confirmação) | "caracteres de controle não são espaço" contradizia tabulação e quebra de linha; letra invisível (U+3164), `º` × `°`, U+0345 e versão do Unicode sem registro | exclusão vale só para controle sem White_Space (tabulação, LF, CR, NEL são espaço); demais casos num risco aceito único | RN-002, seção 10 |

**Por quê:** os pontos 1 e 3 seguem a lógica da AMB-011: separador e sinal solto são diferença de grafia, não de significado (`"alimentacao-"` e `"Transporte – Urbano"` passam a ser reconhecidas). Uma regra única ("só letras e algarismos") fecha o conjunto sem lista de caracteres, que seria incompleta por construção, e qualquer pessoa consegue conferir. O efeito colateral (mais fornecedores iguais, como `"Padaria (Centro)"` = `"Padaria Centro"`) só pesa na RN-007, que também exige mesma data, categoria e valor ao centavo. O ponto 6 vem junto: sem ele, `"-"` e `"?"` viram o mesmo fornecedor e se anulam como duplicatas, enquanto `"   "` já era recusado. O ponto 2 evita tabela manual (alternativa já descartada no DT-004). O ponto 5 registra o comportamento escolhido; raro em dados em português.

**O que isso invalidou:** o DT-004 do `plan.md` (lista fixa de separadores, só `Mn` removido); alinhado na versão 1.1 do plano. Código da T-003 ainda não commitado, ajustado antes do commit. Aceite da T-009 ganha o texto que normaliza para vazio. Nenhum valor do exemplo (seção 9) mudou: as categorias e fornecedores do arquivo só têm letras ASCII, espaço simples e, em `transporte_urbano`, sublinhado interno, que continua valendo `_`.

**Tasks afetadas:** T-003 (aceite com separadores de qualquer tipo, sinal solto, `ø`, `ß`, `º`, `²`), T-008 e T-009 (espaço em branco pela propriedade White_Space; texto normalizado vazio).

**Custo:** 4 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`, `tasks.md`); 13 pontos decididos na mesma sessão. Três rodadas do `spec-adversary` (sobre a 1.7, sobre a primeira redação da 1.8 e de confirmação sobre a 1.8 final).

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
