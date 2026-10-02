 ▐▛███▛█   Claude Code v2.1.287
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~/repo/sdd-desafio

  Opus 5.5 is now your default model and it draws down usage faster than Sonnet 5. Switch anytime with /model.

❯ /clear                                                                        

❯ /task T-003                                                                   

  Searched for 2 patterns, listed 1 directory, ran 1 shell command (ctrl+o to expand)

⏺ Spec (seção 5), AMB-011 e DT-004 são consistentes e determinam todos os casos
  do Aceite. Dependência T-001 está [x]. Escrevendo os testes primeiro.

⏺ Write(tests/test_normalizacao.py)
  ⎿  Wrote 92 lines to tests/test_normalizacao.py
       1 import pytest
       2 
       3 from reembolso.normalizacao import normalizar_texto
       4 
       5 
       7     "texto",
       8     ["Transporte Urbano", "transporte-urbano", " TRANSPORTE__urb
         ano "],
       9 )
      10 def test_secao5_exemplos_transporte_urbano(texto):
     … +98 lines (ctrl+o to expand)

  Ran 1 shell command (ctrl+o to expand)

⏺ Falha esperada por import (função ainda não existe). Para confirmar que os
  testes falham pelo motivo certo, rodo contra um stub identidade temporário:

⏺ Bash(printf '"""normalizar_texto(): os 4 passos da seção 5 da
      spec."""\n\n\ndef normalizar_texto(texto: str) -> str:\n    return
      texto\n' > src/reembolso/normalizaca…)
  ⎿  FAILED tests/test_normalizacao.py::test_secao5_mistura_de_separadores_
     internos_vira_um_sublinhado[transporte---urbano]
     FAILED tests/test_normalizacao.py::test_secao5_sequencias_internas_sep
     … +2 lines (ctrl+o to expand)
  ⎿  Updated src/reembolso/normalizacao.py (+4 -0)
      1  """normalizar_texto(): os 4 passos da seção 5 da spec."""
      2 +                                                                
      3 +                                                                
      4 +def normalizar_texto(texto: str) -> str:                        
      5 +    return texto                                                

⏺ 25 testes falham por asserção, e o único que passa é o de idempotência, como
  esperado. Agora vou implementar conforme DT-004.

⏺ Write(src/reembolso/normalizacao.py)
  ⎿  Added 12 lines, removed 1 line
       1  """normalizar_texto(): os 4 passos da seção 5 da spec."""
       2  
       3 +import re                                                      
       4 +import unicodedata                                             
       5  
       6 +_SEPARADORES = re.compile(r"[\s\-_]+")                         
       7 +                                                               
       8 +                                                               
       9  def normalizar_texto(texto: str) -> str:
       5 -    return texto                                               
      10 +    """Normaliza categoria ou fornecedor conforme a seção 5 da 
         +spec (DT-004)."""                                              
      11 +    texto = texto.strip()                                      
      12 +    texto = texto.casefold()                                   
      13 +    texto = "".join(                                           
      14 +        c for c in unicodedata.normalize("NFD", texto) if unico
         +dedata.category(c) != "Mn"                                     
      15 +    )                                                          
      16 +    return _SEPARADORES.sub("_", texto)                        

  Ran 1 shell command (ctrl+o to expand)

⏺ Bash(python3 - <<'EOF'
      import pathlib…)
  ⎿  36 passed in 0.02s
     All checks passed!
      M src/reembolso/normalizacao.py
     … +26 lines (ctrl+o to expand)
  ⎿  Updated src/reembolso/normalizacao.py (+3 -1)
      11      texto = texto.strip()
      12      texto = texto.casefold()
      13      texto = "".join(
      14 -        c for c in unicodedata.normalize("NFD", texto) if unico
         -dedata.category(c) != "Mn"                                     
      14 +        c                                                      
      15 +        for c in unicodedata.normalize("NFD", texto)           
      16 +        if unicodedata.category(c) != "Mn"                     
      17      )
      18      return _SEPARADORES.sub("_", texto)
  ⎿  Updated tests/test_normalizacao.py (+2 -1)
      43      ],
      44  )
      45  def test_secao5_diacriticos_da_spec_viram_letra_base(texto, esp
          erado):
      46 -    """Seção 5 passo 3: `á`→`a`, `ç`→`c`, `ô`→`o`, `ü`→`u`, `ñ`
         -→`n` (e caixa, passo 2)."""                                    
      46 +    """Seção 5 passo 3: `á`→`a`, `ç`→`c`, `ô`→`o`, `ü`→`u`, `ñ`
         +→`n`                                                           
      47 +    (e caixa, passo 2)."""                                     
      48      assert normalizar_texto(texto) == esperado
      49  
      50  

⏺ Diff limpo, só os arquivos esperados. Task de tipo regra: invocando o revisor
  independente só com o ID.

⏺ revisor-de-task(Revisar task T-003)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ Implementação feita e testes verdes. O revisor independente (revisor-de-task)
  da T-003 ainda está rodando. Quando terminar, salvo o relatório em
  docs/reviews/T-003.md e trago o resumo final para você aprovar o commit.

✻ Baked for 53s · done 10:43 PM

› Message from revisor-de-task
  # Revisão T-003 — Normalização de texto: `normalizar_texto()` com os 4 passos
  da seção 5 da spec (DT-004)

  - **Data:** 2026-10-01
  - **Regras conferidas:** seção 5 (normalização, passos 1 a 4 e exemplos),
  AMB-011, RN-006 e RN-007 (só os trechos que usam a normalização), DT-004
  (plan.md), DECISIONS.md (linhas 75 e 109)
  - **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 36 passed, 0
  failed (evidência, não veredito)

  ### Resultado
  **BLOQUEADO**: o código troca por `_` também os hífens e sublinhados das
  pontas. O passo 4 da spec só fala de sequências **internas**. Ninguém decidiu
  o que fazer com separadores nas pontas, e a resposta muda a comparação de
  fornecedor na RN-007.

  ### Critérios de aceite
  | # | Critério | Status | Evidência |
  |---|---|---|---|
  | 1 | `"Transporte Urbano"`, `"transporte-urbano"`, `" TRANSPORTE__urbano "` →
  `transporte_urbano` | atendido |
  `tests/test_normalizacao.py::test_secao5_exemplos_transporte_urbano` |
  | 2 | `"Pão  Quente"`, `"pao-quente"` → `pao_quente` | atendido |
  `tests/test_normalizacao.py::test_secao5_exemplos_pao_quente` |
  | 3 | Acento pré-composto e combinante dão o mesmo resultado | atendido |
  `test_secao5_acento_precomposto_e_combinante_dao_o_mesmo_resultado`. Conferi
  que o arquivo contém mesmo U+0327 e U+0303, e o teste confirma que as duas
  strings são diferentes (`precomposto != combinante`) |
  | 4 | `ç`, `ô`, `ü`, `ñ` | atendido |
  `test_secao5_diacriticos_da_spec_viram_letra_base`, que também cobre `á`, `Ç`
  e `Bistrô` |
  | 5 | Tabulação, quebra de linha e espaço não separável nas pontas | atendido
  | `test_secao5_espaco_em_branco_de_qualquer_tipo_nas_pontas`. Conferi que
  U+00A0 está no arquivo |
  | 6 | Mistura interna de espaço, hífen e sublinhado vira um `_` | atendido |
  `test_secao5_mistura_de_separadores_internos_vira_um_sublinhado`,
  `test_secao5_sequencias_internas_separadas_viram_um_sublinhado_cada` |

  Recalculei à mão, pela seção 5, o esperado de cada teste. Todos batem com a
  spec.

  ### Problemas encontrados
  #### 1. Hífen e sublinhado nas pontas viram `_`, mas a spec só manda trocar
  sequências internas (severidade ALTA)
  - **Regra afetada:** seção 5, passo 4; RN-007 (fornecedor normalizado);
  AMB-011
  - **Evidência:** `src/reembolso/normalizacao.py:6` (`_SEPARADORES =
  re.compile(r"[\s\-_]+")`) e `:18` (`_SEPARADORES.sub("_", texto)`) aplicam a
  troca à string inteira. A spec diz: passo 1 "remover todo espaço em branco do
  início e do fim" (só espaço em branco); passo 4 "toda sequência **interna** de
  espaços em branco, hífens (`-`) e sublinhados (`_`) vale como um único `_`".
  Ela não diz o que fazer com hífen ou sublinhado no início ou no fim. Na
  leitura literal, eles ficam como estão. O DT-004 do plan.md descreve a mesma
  regex sem restringir às sequências internas, então plano e spec divergem nesse
  ponto.
  - **Impacto:** saídas que observei:
    - `"-Bistro"` → `_bistro`
    - `"_Bistro"` → `_bistro`
    - `"Bistro-"` → `bistro_`
    - `"Bistro _"` → `bistro_`

    Pelo texto literal da spec, `"-Bistro"` e `"_Bistro"` são fornecedores
  diferentes. O código os considera iguais e pode recusar uma delas como
  `duplicata` (RN-007). Na categoria o resultado não muda: nenhuma dessas formas
  bate com as três categorias reconhecidas.
  - **Recomendação:** depende de decisão (ver "Decisões necessárias"). Depois de
  decidir, registrar na spec e no `DECISIONS.md`, alinhar o DT-004 e escrever o
  teste correspondente.

  #### 2. Faltam testes para separadores nas pontas (severidade MÉDIA)
  - **Regra afetada:** seção 5, passo 4 ("interna")
  - **Evidência:** nenhum teste em `tests/test_normalizacao.py` usa hífen ou
  sublinhado no início ou no fim do texto. A suíte passaria tanto com a regex
  atual quanto com uma que tratasse só as sequências internas.
  - **Impacto:** a fronteira "interna × ponta" da regra não é verificada.
  - **Recomendação:** depois da decisão do problema 1, acrescentar casos como
  `"-alimentacao"`, `"alimentacao_"` e `" -alimentacao"` (espaço e depois hífen
  na ponta), com o esperado que a spec passar a definir.

  #### 3. Letras com sinal que o NFD não decompõe continuam iguais (severidade
  BAIXA, depende de decisão)
  - **Regra afetada:** seção 5, passo 3 ("toda letra com acento ou sinal
  diacrítico é comparada como a letra base")
  - **Evidência:** `normalizacao.py:13-17` usa NFD e remove os caracteres `Mn`.
  `ø`, `ł` e `đ` não se decompõem: a saída que observei foi
  `normalizar_texto("ø") == "ø"`. A spec só dá exemplos que o NFD resolve (`á ç
  ô ü ñ`).
  - **Impacto:** um fornecedor `"Smørrebrød"` e outro `"Smorrebrod"` não seriam
  considerados o mesmo na RN-007. É improvável em dados em português.
  - **Recomendação:** confirmar com o humano se esses sinais (barra, traço)
  contam como "sinal diacrítico" para o passo 3.

  ### Cobertura
  - **Regras testadas:** seção 5, passos 1 a 4 e os dois exemplos →
  `tests/test_normalizacao.py` (7 testes, 27 casos parametrizados no total);
  AMB-011 → mesmo arquivo. RN-006 e RN-007 só serão testadas nas próprias tasks
  (T-015 etc.).
  - **Casos de borda cobertos:**
    - `\t`, `\n`, `\r\n` e NBSP nas pontas;
    - acento pré-composto × combinante;
    - maiúscula com acento (`Ç`);
    - várias sequências internas independentes;
    - mistura interna de espaço, tab, hífen e `_`;
    - texto já normalizado fica igual.
  - **Casos que parecem faltar:**
    - hífen ou sublinhado nas pontas, inclusive depois de espaço em branco
  (seção 5, passo 4, "interna");
    - letra com diacrítico que o NFD não decompõe (seção 5, passo 3), dependendo
  da decisão;
    - opcional: espaço em branco Unicode interno que não seja ASCII, como NBSP
  no meio (passo 4, "espaços em branco"). O código já trata, mas não há teste.

  ### Decisões necessárias
  1. **Separadores nas pontas:** depois do passo 1, o que fazer com hífens ou
  sublinhados no início ou no fim do texto? Podem (a) ficar como estão, (b)
  virar `_` (o que o código faz hoje) ou (c) ser removidos. Exemplo em que a
  resposta muda o resultado: duas despesas com mesma data, categoria e valor, e
  fornecedores `"-Bistro"` e `"_Bistro"`. Com (b) ou (c), a segunda é
  `duplicata`. Com (a), as duas são avaliadas. Outro exemplo: `"alimentacao-"`.
  Com (c), é reconhecida como `alimentacao`. Com (a) ou (b), dá
  `categoria_fora_da_politica`.
  2. **Sinais que não são marcas combinantes:** a letra com barra ou traço (`ø`,
  `ł`, `đ`) conta como "letra com sinal diacrítico" no passo 3? Exemplo:
  fornecedores `"Smørrebrød"` e `"Smorrebrod"` na mesma data, com mesma
  categoria e valor. Se contar, a segunda é `duplicata`. Se não contar, as duas
  seguem.

  ### Antes de concluir a task
  - O humano decide a questão 1 (e a 2, se quiser fechá-la agora). A resposta
  vai para a seção 5 da spec e para o `specs/001-motor-reembolso/DECISIONS.md`,
  e o DT-004 do `plan.md` é alinhado.
  - Ajustar `src/reembolso/normalizacao.py` se a decisão for diferente da (b).
  - Acrescentar em `tests/test_normalizacao.py` os casos de separador nas pontas
  (e os de `ø`/`ł`, se decidido), com o esperado calculado pela spec já
  atualizada.
  - Rodar o revisor de novo.

⏺ Write(docs/reviews/T-003.md)
  ⎿  Wrote 69 lines to docs/reviews/T-003.md
      1 # Revisão T-003 — Normalização de texto: `normalizar_texto()` com
      2 
      3 - **Data:** 2026-10-01
        emplos), AMB-011, RN-006 e RN-007 (só os trechos que usam a norma
        lização), DT-004 (plan.md), DECISIONS.md (linhas 75 e 109)
         passed, 0 failed (evidência, não veredito)
      6 
      8 **BLOQUEADO**: o código troca por `_` também os hífens e sublinha
        dos das pontas. O passo 4 da spec só fala de sequências **interna
        resposta muda a comparação de fornecedor na RN-007.
     … +134 lines (ctrl+o to expand)

⏺ Agent "Revisar task T-003" finished · 1m 7s

⏺ Resumo — T-003: Normalização de texto

  Arquivos alterados:
  - src/reembolso/normalizacao.py (modificado): normalizar_texto() conforme o
    DT-004
  - tests/test_normalizacao.py (novo)
  - docs/reviews/T-003.md (novo): relatório do revisor, salvo sem edição

  Testes criados (todos verificam a seção 5 e a AMB-011):
  - test_secao5_exemplos_transporte_urbano: os 3 exemplos da spec
  - test_secao5_exemplos_pao_quente: os 2 exemplos da spec
  - test_secao5_acento_precomposto_e_combinante_dao_o_mesmo_resultado: passo 3
  - test_secao5_diacriticos_da_spec_viram_letra_base: ç ô ü ñ á, Ç, Bistrô
    (passos 2 e 3)
  - test_secao5_espaco_em_branco_de_qualquer_tipo_nas_pontas: tab, \n, \r\n,
    espaço não separável (passo 1)
  - test_secao5_mistura_de_separadores_internos_vira_um_sublinhado e
    ..._sequencias_internas_separadas_...: passo 4
  - test_secao5_texto_ja_normalizado_fica_igual: as 3 categorias da política não
    mudam

  Testes executados antes da implementação: primeiro deu erro de import, como
  esperado. Contra uma versão temporária que devolvia o texto sem mudança, 25
  testes falharam na asserção. O único que passou foi o de texto já normalizado,
  o que é esperado, porque ele só confere que a função não estraga o que já
  está certo.

  Testes executados depois: uv run pytest -q tests/test_normalizacao.py e a
  suíte inteira.
  pytest: 36 passed, 0 failed
  ruff: limpo

  Revisão independente: BLOQUEADO (docs/reviews/T-003.md)
  - ALTA: o passo 4 da spec fala só de sequências internas, mas o código (fiel à
    regex do DT-004) troca por _ também o hífen ou sublinhado nas pontas.
    Exemplo: "-Bistro" vira _bistro.
  - MÉDIA: não há teste de separador nas pontas. Depende da decisão abaixo.
  - BAIXA: ø, ł e đ não se decompõem no NFD e ficam como estão.

  Decisões ou interpretações realizadas: nenhuma intencional. Segui o DT-004 ao
  pé da letra, mas o revisor mostrou que nesse ponto o DT-004 diverge da spec.

  Lacunas ou dúvidas: a spec precisa ser atualizada antes do commit:
  1. Hífen ou sublinhado nas pontas, depois do passo 1: (a) ficam como estão,
     (b) viram _ (é o que o código faz hoje), ou (c) são removidos.
     - Isso muda resultados. Com fornecedores "-Bistro" e "_Bistro", em (b) ou
       (c) a segunda despesa é duplicata; em (a), as duas são avaliadas.
     - Com a categoria "alimentacao-", só em (c) ela é reconhecida.
     - Recomendo (c): remover espaço, hífen e sublinhado nas pontas, pela mesma
       lógica da AMB-011 (diferença de grafia não muda o significado).
  2. ø, ł, đ contam como letra com sinal no passo 3? É improvável em dados em
     português. Recomendo deixar como está e registrar como risco aceito, para
     não manter uma tabela manual (o DT-004 descartou essa opção).

  Commit proposto: feat(T-003): normalização de texto da seção 5, só depois de:
  - atualizar a spec (docs(spec)) e o DECISIONS.md;
  - alinhar o DT-004 no plano;
  - ajustar o código e os testes;
  - rodar o revisor de novo.

  Como você decide os itens 1 e 2?

✻ Worked for 2m 39s · done 10:45 PM

❯ 1- pode ser removido                                                          
  2- pode seguir o recomendado                                                  

  Ran 2 shell commands (ctrl+o to expand)

⏺ Aplicando as decisões na spec (1.6 → 1.7), no DECISIONS.md (D-005) e no DT-004
  do plano.

⏺ Bash(python3 - <<'EOF'
      import pathlib…)
  ⎿   specs/001-motor-reembolso/DECISIONS.md | 21 +++++++++++++++++++++
      specs/001-motor-reembolso/plan.md      |  4 ++--
      specs/001-motor-reembolso/spec.md      |  9 +++++----
     … +3 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/DECISIONS.md (+21 -0)
      10  
      11  ---
      12  
      13 +## D-005 — Pontas e letras sem decomposição na normalização: sp
         +ec 1.6 → 1.7 · `2026-10-01`                                    
      14 +                                                               
      15 +**Gatilho:** revisão independente da T-003 (`docs/reviews/T-003
         +.md`, resultado BLOQUEADO). O passo 4 da seção 5 só tratava seq
         +uências **internas** de separadores, e o passo 1 só removia esp
         +aço em branco das pontas: hífen ou sublinhado no início ou no f
         +im não tinham resultado definido (`"-Bistro"` × `"_Bistro"` mud
         +am a RN-007). O passo 3 não dizia se letras como `ø`, `ł`, `đ` 
         +contam como letra com sinal. O responsável decidiu os dois pont
         +os (sessão `docs/sessions/13-*`).                              
      16 +                                                               
      17 +**O que mudou na spec:**                                       
      18 +                                                               
      19 +| # | Ponto | De (1.6) | Para (1.7) | Onde |                   
      20 +|---|---|---|---|---|                                          
      21 +| 1 | Hífen e sublinhado nas pontas | indefinido (o passo 1 rem
         +ovia só espaço em branco; o passo 4 tratava só sequências inter
         +nas) | **removidos**, junto com o espaço em branco, em qualquer
         + mistura (`" -_Bistro"` → `bistro`) | seção 5 (passo 1 e exempl
         +os) |                                                          
      22 +| 2 | Letras sem decomposição canônica (`ø`, `ł`, `đ`) | indefi
         +nido | **ficam como estão**; letra base é a da decomposição can
         +ônica do Unicode; registrado como risco aceito | seção 5 (passo
         + 3 e exemplos), seção 10 |                                     
      23 +                                                               
      24 +**Por quê:** o ponto 1 segue a lógica da AMB-011: separador nas
         + pontas é diferença de grafia, não de significado (`"alimentaca
         +o-"` passa a ser reconhecida). O ponto 2 evita uma tabela manua
         +l de equivalências, incompleta por construção (alternativa já d
         +escartada no DT-004); o caso é raro em dados em português.     
      25 +                                                               
      26 +**O que isso invalidou:** o DT-004 do `plan.md` aplicava o pass
         +o 4 ao texto inteiro (pontas viravam `_`); alinhado na versão 1
         +.1 do plano. Código da T-003 ainda não commitado, ajustado ante
         +s do commit. Nenhum valor do exemplo (seção 9) mudou.          
      27 +                                                               
      28 +**Tasks afetadas:** T-003 (aceite passa a incluir separadores n
         +as pontas e letra sem decomposição).                           
      29 +                                                               
      30 +**Custo:** 4 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`, `t
         +asks.md`); 2 pontos decididos na mesma sessão.                 
      31 +                                                               
      32 +---                                                            
      33 +                                                               
      34  ## D-004 — Valor gigante e chave repetida: spec 1.3 → 1.6 · `20
          26-10-01`
      35  
      36  **Gatilho:** escrita do `plan.md` 1.0. Ao verificar como o códi
          go leria o arquivo, apareceram duas entradas válidas no formato
           cujo resultado a spec não definia. O responsável decidiu as du
          as (versão 1.4, não commitada). A rodada do `spec-adversary` so
          bre a 1.4 apontou 4 problemas (1 bloqueante) nas próprias decis
          ões; o responsável aceitou as 4 recomendações, aplicadas na 1.5
           (pontos 3 a 6). A rodada sobre a 1.5 apontou 4 problemas, nenh
          um bloqueante; o responsável aceitou as 4 recomendações, aplica
          das na 1.6 (pontos 7 a 10). Sessão `docs/sessions/07-*`.
  ⎿  Updated specs/001-motor-reembolso/plan.md (+2 -2)
      1  # Plano Técnico — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.0 · **Baseado na spec:** 1.6                      
      3 +**Versão:** 1.1 · **Baseado na spec:** 1.7                      
      4  
      5  > Aqui mora o COMO. Este arquivo pode e deve falar de linguagem,
          biblioteca e
      6  > arquitetura. O que ele **não** pode é introduzir regra de negó
         cio nova — se
     ...
      139  ### DT-004 — Normalização de texto com `unicodedata`
      140  
      141  **Contexto:** seção 5 da spec, 4 passos, "qualquer que seja a 
           forma como o caractere foi codificado".
      142 -**Decisão:** `strip()` → `casefold()` → `unicodedata.normalize
          -("NFD")` e remoção dos caracteres de categoria `Mn` (marcas co
          -mbinantes) → `re.sub(r"[\s\-_]+", "_", ...)`. O NFD decompõe t
          -anto `á` pré-composto (U+00E1) quanto `a` + acento combinante 
          -(U+0301) para a mesma sequência, cobrindo as duas codificações
          -.                                                             
      142 +**Decisão:** `re.sub(r"\A[\s\-_]+|[\s\-_]+\Z", "", ...)` (pont
          +as: espaço em branco, hífen e sublinhado) → `casefold()` → `un
          +icodedata.normalize("NFD")` e remoção dos caracteres de catego
          +ria `Mn` (marcas combinantes) → `re.sub(r"[\s\-_]+", "_", ...)
          +` (sequências internas). Letras sem decomposição canônica (`ø`
          +, `ł`) ficam como estão, como a spec define. O NFD decompõe ta
          +nto `á` pré-composto (U+00E1) quanto `a` + acento combinante (
          +U+0301) para a mesma sequência, cobrindo as duas codificações.
      143  **Alternativa descartada:** tabela manual de acentos (`á→a`, .
           ..): incompleta por construção; `NFKD`: também desfaz compatib
           ilidades (ligaduras, larguras) que a spec não pede.
      144  **Consequência:** uma função pura, usada por RN-006 e RN-007, 
           testada com os exemplos da seção 5 e os casos de borda de cate
           goria e fornecedor.
      145  
  ⎿  Updated specs/001-motor-reembolso/spec.md (+5 -4)
      1  # Spec — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.6 · **Status:** aprovada para planejamento · **Últ
        -ima alteração:** 2026-10-01 (ver `DECISIONS.md` D-001 a D-004)  
      3 +**Versão:** 1.7 · **Status:** aprovada para planejamento · **Últ
        +ima alteração:** 2026-10-01 (ver `DECISIONS.md` D-001 a D-005)  
      4  
      5  > **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ
         . Nenhuma linha
      6  > aqui pode citar linguagem, biblioteca, classe, função ou estru
         tura de pasta.
     ...
      138  
      139  **Normalização de texto** (usada em RN-006 e RN-007), aplicada
            nesta ordem:
      140  
      141 -1. remover todo espaço em branco do início e do fim (espaço co
          -mum, tabulação, quebra de linha, espaço não separável e demais
          - caracteres de espaço em branco);                             
      141 +1. remover do início e do fim toda sequência de espaços em bra
          +nco (espaço comum, tabulação, quebra de linha, espaço não sepa
          +rável e demais caracteres de espaço em branco), hífens (`-`) e
          + sublinhados (`_`), em qualquer mistura;                      
      142  2. ignorar maiúsculas/minúsculas;
      143 -3. toda letra com acento ou sinal diacrítico é comparada como 
          -a letra base, qualquer que seja a forma como o caractere foi c
          -odificado no arquivo (`á`→`a`, `ç`→`c`, `ô`→`o`, `ü`→`u`, `ñ`→
          -`n`);                                                         
      143 +3. toda letra com acento ou sinal diacrítico é comparada como 
          +a letra base, qualquer que seja a forma como o caractere foi c
          +odificado no arquivo (`á`→`a`, `ç`→`c`, `ô`→`o`, `ü`→`u`, `ñ`→
          +`n`). A letra base é a que resta ao separar os sinais pela dec
          +omposição canônica do Unicode; letras sem essa decomposição, c
          +ujo traço faz parte da própria letra (`ø`, `ł`, `đ`), ficam co
          +mo estão;                                                     
      144  4. toda sequência interna de espaços em branco, hífens (`-`) e
            sublinhados (`_`) vale como um único `_`.
      145  
      146 -Exemplos: `"Transporte Urbano"`, `"transporte-urbano"` e `" TR
          -ANSPORTE__urbano "` → `transporte_urbano`; `"Pão  Quente"` e `
          -"pao-quente"` → `pao_quente`.                                 
      146 +Exemplos: `"Transporte Urbano"`, `"transporte-urbano"` e `" TR
          +ANSPORTE__urbano "` → `transporte_urbano`; `"Pão  Quente"` e `
          +"pao-quente"` → `pao_quente`; `"-Bistro"`, `"_Bistro"`, `"Bist
          +ro -"` e `" -_Bistro"` → `bistro`; `"Smørrebrød"` → `smørrebrø
          +d` (diferente de `smorrebrod`).                               
      147  
      148  ### RN-001 — Um resultado por despesa
      149  
     ...
      543  - **Fracionamento para escapar da nota fiscal** (AMB-008): trê
           s hospedagens sem nota de 100,00 + 99,99 + 50,01 na mesma data
            recebem 250,00, enquanto uma de 250,00 sem nota recebe 0. O g
           anho é limitado aos casos em que o limite diário passa de 100,
           00 (hospedagem e transporte em viagem). Aceito para não recusa
           r despesas pequenas legítimas sem nota.
      544  - **Viagem por hospedagem irrisória com nota declarada** (AMB-
           004): uma hospedagem de 0,01 com `tem_nota_fiscal` verdadeiro 
           põe D e D+1 em viagem e amplia os limites de alimentação e tra
           nsporte em até 70,00 por dia (140,00 nos dois dias). Aceito po
           rque o sistema não verifica notas (seção 3) e qualquer valor m
           ínimo seria regra inventada; a saída expõe `em_viagem` por ite
           m para a conferência humana. Mitigação definitiva: indicação e
           xplícita de viagem na entrada (evolução, seção 3).
      545  - **Caminho ambíguo no aviso de chave repetida** (RN-013): cha
           ves com `.`, `[` ou `]`, vazias ou com quebra de linha aparece
           m no caminho sem escape. Dois caminhos diferentes podem gerar 
           o mesmo texto (`"a.b"` e `a` → `b`), e um campo extra pode ger
           ar aviso idêntico ao de um campo da seção 4 que entra no cálcu
           lo (chave extra `"periodo.inicio"` repetida na raiz produz o m
           esmo aviso que o `periodo.inicio` verdadeiro repetido) ou um t
           exto que imita outro aviso. Nenhum valor muda: o aviso só pode
            enganar o conferente sobre qual chave foi descartada. Aceito 
           para manter o aviso legível; na dúvida, o conferente consulta 
           o arquivo de entrada.
      546 +- **Letra com traço próprio não vira letra base** (seção 5, pa
          +sso 3): `ø`, `ł`, `đ` e semelhantes não têm decomposição canôn
          +ica e ficam como estão, então `"Smørrebrød"` e `"Smorrebrod"` 
          +são fornecedores diferentes na RN-007. Aceito porque são raras
          + em dados em português e uma tabela própria de equivalências s
          +eria incompleta por construção.                               
      547  - **Quase-duplicatas** (AMB-010): o mesmo gasto relançado com 
           data vizinha, valor diferente em um centavo ou fornecedor com 
           outra grafia (além do que a normalização da seção 5 cobre) não
            é detectado. Aceito porque qualquer critério aproximado seria
            regra inventada e poderia recusar gastos legítimos repetidos.
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+2 -2)
      1  # Tasks — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.0 · **Baseado em:** spec 1.6, plan 1.0            
      3 +**Versão:** 1.1 · **Baseado em:** spec 1.7, plan 1.1            
      4  
      5  > Cada task é pequena o bastante para virar **um commit**. Se vo
         cê não consegue
      6  > descrever o critério de aceite como "o teste X passa", a task 
         está grande demais.
     ...
      42    - **Tipo:** regra
      43    - **Atende:** seção 5 da spec (normalização), AMB-011; usada 
          por RN-006 e RN-007
      44    - **Depende de:** T-001
      45 -  - **Aceite:** `tests/test_normalizacao.py` passa: exemplos da
         - seção 5 (`"Transporte Urbano"`, `"transporte-urbano"`, `" TRAN
         -SPORTE__urbano "` → `transporte_urbano`; `"Pão  Quente"`, `"pao
         --quente"` → `pao_quente`); acento pré-composto e combinante dão
         - o mesmo resultado; `ç`, `ô`, `ü`, `ñ`; tabulação, quebra de li
         -nha e espaço não separável nas pontas; mistura de espaço, hífen
         - e sublinhado internos vira um `_`.                            
      45 +  - **Aceite:** `tests/test_normalizacao.py` passa: exemplos da
         + seção 5 (`"Transporte Urbano"`, `"transporte-urbano"`, `" TRAN
         +SPORTE__urbano "` → `transporte_urbano`; `"Pão  Quente"`, `"pao
         +-quente"` → `pao_quente`); acento pré-composto e combinante dão
         + o mesmo resultado; `ç`, `ô`, `ü`, `ñ`; tabulação, quebra de li
         +nha e espaço não separável nas pontas; mistura de espaço, hífen
         + e sublinhado internos vira um `_`; hífen e sublinhado nas pont
         +as, misturados ou não com espaço em branco, são removidos (`"-B
         +istro"`, `"_Bistro"`, `" -_Bistro"` → `bistro`; `"alimentacao-"
         +` → `alimentacao`); `ø`, `ł`, `đ` ficam como estão (spec 1.7, D
         +-005).                                                         
      46    - **Commit:**
      47  
      48  - [ ] **T-004** — Justificativa: `justificativa.py` gera a fras
          e em português de um item já decidido, para cada status e motiv
          o, com formatação própria `1.234,56` e `DD/MM` sem `locale` (DT
          -009).

⏺ Agora os testes novos, com o esperado calculado pela spec 1.7, e eles devem
  falhar antes do ajuste no código:

⏺ Bash(cat >> tests/test_normalizacao.py <<'EOF'…)
  ⎿  tests/test_normalizacao.py:108: AssertionError
     =========================== short test summary info ==================
     ==========
     … +15 lines (ctrl+o to expand)
  ⎿  Updated tests/test_normalizacao.py (+31 -0)
       91      """Seção 5: as categorias da política já estão na forma no
           rmalizada."""
       92      for texto in ("alimentacao", "transporte_urbano", "hospeda
           gem"):
       93          assert normalizar_texto(texto) == texto
       94 +                                                              
       95 +                                                              
       96 +@pytest.mark.parametrize(                                     
       97 +    "texto",                                                  
       98 +    ["-Bistro", "_Bistro", "Bistro -", "Bistro_", " -_Bistro",
          + "\t-Bistro- "],                                              
       99 +)                                                             
      100 +def test_secao5_hifen_e_sublinhado_nas_pontas_sao_removidos(te
          +xto):                                                         
      101 +    """Seção 5 passo 1 (spec 1.7, D-005): espaço em branco, hí
          +fen e sublinhado                                              
      102 +    nas pontas, em qualquer mistura, são removidos (não viram 
          +`_`)."""                                                      
      103 +    assert normalizar_texto(texto) == "bistro"                
      104 +                                                              
      105 +                                                              
      106 +def test_secao5_categoria_com_hifen_no_fim_e_reconhecivel():  
      107 +    """Seção 5 passo 1 (D-005) / AMB-011: `"alimentacao-"` → `
          +alimentacao`."""                                              
      108 +    assert normalizar_texto("alimentacao-") == "alimentacao"  
      109 +                                                              
      110 +                                                              
      111 +def test_secao5_nbsp_interno_vira_sublinhado():               
      112 +    """Seção 5 passo 4: espaço não separável interno é espaço 
          +em branco → `_`."""                                           
      113 +    assert normalizar_texto("transporte urbano") == "transport
          +e_urbano"                                                     
      114 +                                                              
      115 +                                                              
      116 +@pytest.mark.parametrize(                                     
      117 +    ("texto", "esperado"),                                    
      118 +    [("ø", "ø"), ("ł", "ł"), ("đ", "đ"), ("Smørrebrød", "smørr
          +ebrød")],                                                     
      119 +)                                                             
      120 +def test_secao5_letra_sem_decomposicao_canonica_fica_como_esta
          +(texto, esperado):                                            
      121 +    """Seção 5 passo 3 (spec 1.7, D-005): letra cujo traço faz
          + parte dela, sem                                              
      122 +    decomposição canônica, fica como está (só a caixa muda, pa
          +sso 2)."""                                                    
      123 +    assert normalizar_texto(texto) == esperado                
      124 +    assert normalizar_texto("Smørrebrød") != normalizar_texto(
          +"Smorrebrod")                                                 

⏺ Os 7 testes de ponta falham por asserção, como esperado, enquanto os de ø/ł/đ
  e do espaço não separável interno já passam. Agora vou ajustar o código.

⏺ Bash(cat > src/reembolso/normalizacao.py <<'EOF'
      """normalizar_texto(): os 4 passos da seção 5 da spec."""…)  ⎿  48 passed in 0.03s
     All checks passed!
      M specs/001-motor-reembolso/DECISIONS.md
     … +6 lines (ctrl+o to expand)
  ⎿  Updated src/reembolso/normalizacao.py (+2 -1)
       3  import re
       4  import unicodedata
       5  
       6 +_PONTAS = re.compile(r"\A[\s\-_]+|[\s\-_]+\Z")                 
       7  _SEPARADORES = re.compile(r"[\s\-_]+")
       8  
       9  
      10  def normalizar_texto(texto: str) -> str:
      11      """Normaliza categoria ou fornecedor conforme a seção 5 da 
          spec (DT-004)."""
      11 -    texto = texto.strip()                                      
      12 +    texto = _PONTAS.sub("", texto)                             
      13      texto = texto.casefold()
      14      texto = "".join(
      15          c

⏺ Suíte verde. A CLAUDE.md pede o spec-adversary depois de mudança relevante na
  spec, e a skill pede o revisor de novo. Os dois só leem os arquivos, então
  rodo em paralelo:

⏺ 2 background agents launched (↓ to manage)
   ├ spec-adversary (Revisão adversarial spec 1.7)
   └ revisor-de-task (Revisar task T-003 (revisão 2))

⏺ Apliquei as duas decisões e a suíte está verde. Ainda não fiz nenhum commit: o
  spec-adversary e a segunda rodada do revisor da T-003 estão rodando em
  segundo plano.

  O que mudou:
  - Spec 1.6 → 1.7:
    - No passo 1, hífen e sublinhado nas pontas agora são removidos junto com o
      espaço em branco, em qualquer mistura.
    - No passo 3, a letra base passa a ser a da decomposição canônica do
      Unicode. ø, ł e đ ficam como estão.
    - Acrescentei esses exemplos à seção 5 e registrei o caso do ø como risco
      aceito na seção 10.
  - DECISIONS.md: nova entrada D-005, com o gatilho na revisão da T-003.
  - plan.md 1.1: o DT-004 agora remove os separadores das pontas antes de trocar
    os internos por _.
  - tasks.md 1.1: o aceite da T-003 inclui os casos novos.
  - Código: normalizacao.py remove espaço, hífen e sublinhado das pontas antes
    de seguir os outros passos.
  - Testes: 12 casos novos. Os 7 de pontas falharam por asserção antes do
    ajuste. Os 5 de ø/ł/đ e do espaço não separável no meio do texto já
    passavam, porque o código já se comportava assim e a spec só passou a
    definir isso. Agora são 48 testes passando e o ruff está limpo.

  Um caso estranho que ainda não está coberto: um sinal de acento solto logo
  depois de um espaço no fim do texto, como "Bistro \u0301". Hoje ele vira
  bistro_: a remoção das pontas acontece antes de tirar o acento, e o espaço que
  sobra no fim é trocado por _. A spec não diz o que fazer aqui. Na prática é
  muito improvável, mas vou ver se os revisores apontam isso.

  Quando os dois relatórios chegarem, salvo o do revisor como "Revisão 2" em
  docs/reviews/T-003.md. Depois trago o resumo final e os commits propostos para
  você aprovar:
  - docs(spec) com a spec e o DECISIONS.md
  - docs(plan)
  - docs(tasks)
  - feat(T-003)

✻ Churned for 1m 21s · done 10:48 PM

› Message from revisor-de-task
  # Revisão T-003 — Normalização de texto: `normalizar_texto()` com os 4 passos
  da seção 5 da spec (DT-004)

  - **Data:** 2026-10-01
  - **Regras conferidas:** seção 5 da spec 1.7 (passos 1 a 4 e exemplos),
  AMB-011, RN-006 e RN-007 (só os trechos que usam a normalização), seção 10
  (risco aceito "Letra com traço próprio"), DT-004 do plan 1.1, D-005 no
  DECISIONS.md
  - **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 48 passed, 0
  failed (evidência, não veredito)

  ### Resultado
  **APROVADO COM RESSALVAS**: todos os critérios de aceite estão atendidos e o
  código segue a spec 1.7. A D-005 está refletida na spec, no plano e em
  tasks.md. Ficam só observações BAIXA sobre entradas raras que a spec não
  detalha.

  ### Critérios de aceite
  | # | Critério | Status | Evidência |
  |---|---|---|---|
  | 1 | `"Transporte Urbano"`, `"transporte-urbano"`, `" TRANSPORTE__urbano "` →
  `transporte_urbano` | atendido |
  `tests/test_normalizacao.py::test_secao5_exemplos_transporte_urbano` |
  | 2 | `"Pão  Quente"`, `"pao-quente"` → `pao_quente` | atendido |
  `tests/test_normalizacao.py::test_secao5_exemplos_pao_quente` |
  | 3 | Acento pré-composto e combinante dão o mesmo resultado | atendido |
  `test_secao5_acento_precomposto_e_combinante_dao_o_mesmo_resultado`. Conferi
  que o arquivo contém U+0327 e U+0303 e que o teste confirma `precomposto !=
  combinante` |
  | 4 | `ç`, `ô`, `ü`, `ñ` | atendido |
  `test_secao5_diacriticos_da_spec_viram_letra_base`, que também cobre `á`, `Ç`
  e `Bistrô` |
  | 5 | Tabulação, quebra de linha e espaço não separável nas pontas | atendido
  | `test_secao5_espaco_em_branco_de_qualquer_tipo_nas_pontas`. Conferi que há
  U+00A0 no arquivo |
  | 6 | Mistura interna de espaço, hífen e sublinhado vira um `_` | atendido |
  `test_secao5_mistura_de_separadores_internos_vira_um_sublinhado`,
  `test_secao5_sequencias_internas_separadas_viram_um_sublinhado_cada`,
  `test_secao5_nbsp_interno_vira_sublinhado` |
  | 7 | Hífen e sublinhado nas pontas, com ou sem espaço em branco, são
  removidos (`"-Bistro"`, `"_Bistro"`, `" -_Bistro"` → `bistro`;
  `"alimentacao-"` → `alimentacao`) | atendido |
  `test_secao5_hifen_e_sublinhado_nas_pontas_sao_removidos` (inclui também
  `"Bistro -"`, que é exemplo da spec, `"Bistro_"` e `"\t-Bistro- "`) e
  `test_secao5_categoria_com_hifen_no_fim_e_reconhecivel`. No código:
  `src/reembolso/normalizacao.py:6` e `:12` |
  | 8 | `ø`, `ł`, `đ` ficam como estão (spec 1.7, D-005) | atendido |
  `test_secao5_letra_sem_decomposicao_canonica_fica_como_esta`, que inclui
  `"Smørrebrød"` → `smørrebrød`, diferente de `smorrebrod`, como no exemplo da
  spec |

  Recalculei à mão, pela seção 5 da spec 1.7, o esperado de cada teste. Todos
  batem. Nenhum teste é tautológico: os esperados são literais tirados da spec.
  Os casos de ponta e de `ø` falhariam com a versão anterior do código, que
  trocava as pontas por `_`.

  **Consistência:** a spec 1.7 (seção 5, passos 1 e 3, exemplos e seção 10), o
  DT-004 do plan 1.1, a D-005 e o aceite da T-003 em tasks.md dizem a mesma
  coisa que o código. As alterações do diff fora do código são todas da D-005,
  que a revisão anterior mandou registrar. Não encontrei mudança fora do escopo.

  ### Problemas encontrados
  #### 1. `casefold()` faz mais do que trocar maiúsculas por minúsculas —
  severidade BAIXA
  - **Regra afetada:** seção 5, passo 2 ("ignorar maiúsculas/minúsculas")
  - **Evidência:** `src/reembolso/normalizacao.py:13`. Observei
  `normalizar_texto("Straße") == "strasse"`.
  - **Impacto:** os fornecedores `"Straße"` e `"Strasse"` contam como o mesmo na
  RN-007. Isso segue a comparação sem caixa padrão do Unicode, em que a
  maiúscula de `ß` é `SS`. A spec não fala desse caso. É improvável em dados em
  português.
  - **Recomendação:** nenhuma mudança obrigatória. Se o responsável quiser,
  deixar o caso explícito na spec ou no DT-004.

  #### 2. O que o código conta como "espaço em branco" vai um pouco além do
  Unicode — severidade BAIXA
  - **Regra afetada:** seção 5, passos 1 e 4 ("demais caracteres de espaço em
  branco")
  - **Evidência:** `normalizacao.py:6-7` usa `\s` do Python, que inclui os
  separadores de controle U+001C a U+001F. Esses quatro não são espaço em branco
  no Unicode. Observei `normalizar_texto("\x1cBistro") == "bistro"`. Já U+200B,
  o espaço de largura zero, não é tratado como espaço: `"ab"` fica como está.
  - **Impacto:** só aparece com caracteres de controle no texto. Nenhum dado
  realista é afetado.
  - **Recomendação:** nenhuma mudança obrigatória. Opcional: citar no DT-004
  qual definição de espaço em branco o código usa.

  #### 3. A remoção de marcas `Mn` pega mais do que acentos de letras —
  severidade BAIXA
  - **Regra afetada:** seção 5, passo 3
  - **Evidência:** `normalizacao.py:14-18` remove todo caractere de categoria
  `Mn`. Isso inclui:
    - marcas que não são diacríticos de letra latina, como os sinais de vogal de
  escritas indianas;
    - marcas presas a um separador. Observei `"Bistro -́"` → `bistro_`. Na
  leitura literal da ordem da spec, o passo 1 não removeria `" -"`, porque o
  último caractere é a marca, e o passo 4 não trataria esse trecho, porque ele
  não é interno.
  - **Impacto:** só com entradas patológicas ou escritas não latinas. Nenhum
  dado do domínio é afetado.
  - **Recomendação:** nenhuma mudança obrigatória. Registrar como observação.

  ### Cobertura
  - **Regras testadas:**
    - seção 5, passos 1 a 4 e todos os exemplos da 1.7:
  `tests/test_normalizacao.py`;
    - AMB-011: mesmo arquivo;
    - D-005, pontos 1 e 2:
  `test_secao5_hifen_e_sublinhado_nas_pontas_sao_removidos`,
  `test_secao5_categoria_com_hifen_no_fim_e_reconhecivel`,
  `test_secao5_letra_sem_decomposicao_canonica_fica_como_esta`.
  - **Casos de borda cobertos:**
    - nas pontas: `\t`, `\n`, `\r\n`, NBSP e mistura de espaço com hífen e
  sublinhado;
    - NBSP interno;
    - acento pré-composto e combinante;
    - maiúscula com acento;
    - várias sequências internas independentes;
    - texto que já está normalizado;
    - `ø`, `ł`, `đ`.
  - **Casos que parecem faltar:** nenhum que a spec exija. Opcionalmente, o
  texto que só tem separadores (`"---"`, `"  "`), que hoje dá `""`. A spec não
  define o resultado da normalização nesse caso. A validação de texto vazio é
  das tasks de entrada (T-009 e seguintes).

  ### Decisões necessárias
  Nenhuma.

  ### Antes de concluir a task
  Nada — pode seguir para o commit.

⏺ Bash(cat >> docs/reviews/T-003.md <<'EOF'…)
  ⎿  ok
  ⎿  Updated docs/reviews/T-003.md (+71 -0)
       67  - Ajustar `src/reembolso/normalizacao.py` se a decisão for dif
           erente da (b).
       68  - Acrescentar em `tests/test_normalizacao.py` os casos de sepa
           rador nas pontas (e os de `ø`/`ł`, se decidido), com o esperad
           o calculado pela spec já atualizada.
       69  - Rodar o revisor de novo.
       70 +                                                              
       71 +---                                                           
       72 +                                                              
       73 +## Revisão 2                                                  
       74 +                                                              
       75 +# Revisão T-003 — Normalização de texto: `normalizar_texto()` 
          +com os 4 passos da seção 5 da spec (DT-004)                   
       76 +                                                              
       77 +- **Data:** 2026-10-01                                        
       78 +- **Regras conferidas:** seção 5 da spec 1.7 (passos 1 a 4 e e
          +xemplos), AMB-011, RN-006 e RN-007 (só os trechos que usam a n
          +ormalização), seção 10 (risco aceito "Letra com traço próprio"
          +), DT-004 do plan 1.1, D-005 no DECISIONS.md                  
       79 +- **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` →
          + 48 passed, 0 failed (evidência, não veredito)                
       80 +                                                              
       81 +### Resultado                                                 
       82 +**APROVADO COM RESSALVAS**: todos os critérios de aceite estão
          + atendidos e o código segue a spec 1.7. A D-005 está refletida
          + na spec, no plano e em tasks.md. Ficam só observações BAIXA s
          +obre entradas raras que a spec não detalha.                   
       83 +                                                              
       84 +### Critérios de aceite                                       
       85 +| # | Critério | Status | Evidência |                         
       86 +|---|---|---|---|                                             
       87 +| 1 | `"Transporte Urbano"`, `"transporte-urbano"`, `" TRANSPO
          +RTE__urbano "` → `transporte_urbano` | atendido | `tests/test_
          +normalizacao.py::test_secao5_exemplos_transporte_urbano` |    
       88 +| 2 | `"Pão  Quente"`, `"pao-quente"` → `pao_quente` | atendid
          +o | `tests/test_normalizacao.py::test_secao5_exemplos_pao_quen
          +te` |                                                         
       89 +| 3 | Acento pré-composto e combinante dão o mesmo resultado |
          + atendido | `test_secao5_acento_precomposto_e_combinante_dao_o
          +_mesmo_resultado`. Conferi que o arquivo contém U+0327 e U+030
          +3 e que o teste confirma `precomposto != combinante` |        
       90 +| 4 | `ç`, `ô`, `ü`, `ñ` | atendido | `test_secao5_diacriticos
          +_da_spec_viram_letra_base`, que também cobre `á`, `Ç` e `Bistr
          +ô` |                                                          
       91 +| 5 | Tabulação, quebra de linha e espaço não separável nas po
          +ntas | atendido | `test_secao5_espaco_em_branco_de_qualquer_ti
          +po_nas_pontas`. Conferi que há U+00A0 no arquivo |            
       92 +| 6 | Mistura interna de espaço, hífen e sublinhado vira um `_
          +` | atendido | `test_secao5_mistura_de_separadores_internos_vi
          +ra_um_sublinhado`, `test_secao5_sequencias_internas_separadas_
          +viram_um_sublinhado_cada`, `test_secao5_nbsp_interno_vira_subl
          +inhado` |                                                     
       93 +| 7 | Hífen e sublinhado nas pontas, com ou sem espaço em bran
          +co, são removidos (`"-Bistro"`, `"_Bistro"`, `" -_Bistro"` → `
          +bistro`; `"alimentacao-"` → `alimentacao`) | atendido | `test_
          +secao5_hifen_e_sublinhado_nas_pontas_sao_removidos` (inclui ta
          +mbém `"Bistro -"`, que é exemplo da spec, `"Bistro_"` e `"\t-B
          +istro- "`) e `test_secao5_categoria_com_hifen_no_fim_e_reconhe
          +civel`. No código: `src/reembolso/normalizacao.py:6` e `:12` |
       94 +| 8 | `ø`, `ł`, `đ` ficam como estão (spec 1.7, D-005) | atend
          +ido | `test_secao5_letra_sem_decomposicao_canonica_fica_como_e
          +sta`, que inclui `"Smørrebrød"` → `smørrebrød`, diferente de `
          +smorrebrod`, como no exemplo da spec |                        
       95 +                                                              
       96 +Recalculei à mão, pela seção 5 da spec 1.7, o esperado de cada
          + teste. Todos batem. Nenhum teste é tautológico: os esperados 
          +são literais tirados da spec. Os casos de ponta e de `ø` falha
          +riam com a versão anterior do código, que trocava as pontas po
          +r `_`.                                                        
       97 +                                                              
       98 +**Consistência:** a spec 1.7 (seção 5, passos 1 e 3, exemplos 
          +e seção 10), o DT-004 do plan 1.1, a D-005 e o aceite da T-003
          + em tasks.md dizem a mesma coisa que o código. As alterações d
          +o diff fora do código são todas da D-005, que a revisão anteri
          +or mandou registrar. Não encontrei mudança fora do escopo.    
       99 +                                                              
      100 +### Problemas encontrados                                     
      101 +#### 1. `casefold()` faz mais do que trocar maiúsculas por min
          +úsculas — severidade BAIXA                                    
      102 +- **Regra afetada:** seção 5, passo 2 ("ignorar maiúsculas/min
          +úsculas")                                                     
      103 +- **Evidência:** `src/reembolso/normalizacao.py:13`. Observei 
          +`normalizar_texto("Straße") == "strasse"`.                    
      104 +- **Impacto:** os fornecedores `"Straße"` e `"Strasse"` contam
          + como o mesmo na RN-007. Isso segue a comparação sem caixa pad
          +rão do Unicode, em que a maiúscula de `ß` é `SS`. A spec não f
          +ala desse caso. É improvável em dados em português.           
      105 +- **Recomendação:** nenhuma mudança obrigatória. Se o responsá
          +vel quiser, deixar o caso explícito na spec ou no DT-004.     
      106 +                                                              
     … 34 more lines (ctrl+o to expand)

⏺ Agent "Revisar task T-003 (revisão 2)" finished · 1m 2s

⏺ A segunda revisão da T-003 voltou APROVADO COM RESSALVAS, sem nenhuma decisão
  pendente. Salvei o relatório sem edição como "Revisão 2" em
  docs/reviews/T-003.md.

  As 3 ressalvas são de severidade baixa e tratam só de entradas improváveis em
  dados em português. Nenhuma exige mudança no código:
  - Caixa: "Straße" e "Strasse" dão o mesmo resultado, porque a comparação sem
    caixa do Unicode trata ß como ss.
  - Espaço em branco: o código conta como espaço quatro caracteres de controle
    (U+001C a U+001F) e não conta o espaço de largura zero (U+200B).
  - Acentos soltos: a remoção de acentos também apaga outros sinais. Isso inclui
    o caso que eu já tinha mencionado: "Bistro -́" (com um acento solto no fim)
    vira bistro_.

  O spec-adversary ainda está revisando a spec 1.7. Quando o resultado chegar,
  trago o resumo final e os commits para você aprovar.

✻ Cooked for 27s · done 10:49 PM

› Message from spec-adversary
  5 problemas, 1 bloqueante.

  Não consegui rodar `git diff`: não tenho shell neste ambiente. Comparei o
  texto atual de
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md` (seção
  5, passos 1 a 4 e exemplos; seção 10) com a tabela "De/Para" da D-005 em
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md`. A
  spec traz os dois pontos da D-005: o passo 1 com os separadores nas pontas, o
  passo 3 com as letras sem decomposição, os exemplos, o risco aceito na seção
  10 e o cabeçalho na versão 1.7.

  ### 1. O conjunto de "hífens" e de "espaços em branco" não está fechado —
  BLOQUEANTE — ambiguidade

  - **Regras afetadas:** seção 5, passos 1 e 4; RN-006; RN-007; AMB-011; RN-002
  (o critério "só com espaços em branco").
  - **Cenários de entrada:**
    - (a) Alimentação em 03/07, `categoria` `"Transporte – Urbano"` (com o
  travessão curto U+2013 que o Word/Outlook coloca sozinho), 50,00, com nota.
    - (b) Mesma data, `categoria` `"transporte‐urbano"` (U+2010 HYPHEN) ou
  `"transporte−urbano"` (U+2212, sinal de menos).
    - (c) `categoria` `"alimentacao"` (BOM no início, comum em texto colado de
  planilha) ou `"alimentacao"` (espaço de largura zero).
    - (d) Duas alimentações em 03/07, 40,00, com nota, fornecedores `"Bistro -
  Centro"` e `"Bistro – Centro"`.
    - (e) `fornecedor` `""`.
  - **Comportamento pela interpretação atual:** indefinido.
    - Os passos 1 e 4 dizem "hífens (`-`)". Dá para ler "só U+002D", que é o
  caractere entre crases, ou "qualquer caractere de hífen/traço", que é o
  sentido da palavra no plural.
    - "Demais caracteres de espaço em branco" não diz qual lista vale. U+200B e
  U+FEFF não são espaço em branco pela propriedade Unicode White_Space, mas
  aparecem como "espaço" em muitas definições. U+001C a U+001F entram em algumas
  listas e não em outras.
    - Por isso, (a), (b) e (c) dão `transporte_urbano`/`alimentacao` reconhecida
  (reembolsada) numa leitura e `categoria_fora_da_politica` (0,00) na outra. Em
  (d), as despesas são ou não `duplicata`. Em (e), o item é ou não
  `entrada_invalida`.
  - **Por que é um problema:** a justificativa da AMB-011 e da D-005 é que
  separador "é diferença de grafia, não de significado". O travessão automático
  do editor é justamente uma diferença de grafia, e o resultado em reais muda
  com a leitura. O código teria que escolher a lista de caracteres.
  - **Pergunta para decisão:** quais caracteres, exatamente, contam como "hífen"
  e como "espaço em branco" nos passos 1 e 4 e no critério "só com espaços em
  branco" da RN-002? Isso inclui U+2010 a U+2015, U+2212, U+200B, U+FEFF e
  U+001C a U+001F.

  ### 2. Sinais diacríticos sem letra base e marcas que não são acento — PODE
  ESPERAR — lacuna

  - **Regra afetada:** seção 5, passo 3, e a ordem entre os passos 1, 3 e 4.
  - **Cenários de entrada:**
    - (a) `categoria` `"alimentacao-́"`: hífen seguido de acento agudo
  combinante, que fica "sobre" o hífen.
    - (b) `categoria` `"́alimentacao"`: sinal solto no início.
    - (c) Fornecedores `"Bistro Centro"` e `"Bistro Centro️"` (seletor de
  variação), mesma data e valor.
    - (d) Fornecedores `"Smørrebrød"` (ø pré-composto, que fica como está) e
  `"Smo̸rrebrød"` (o + U+0338, traço combinante), visualmente iguais.
  - **Comportamento pela interpretação atual:** indefinido.
    - O passo 3 só fala de "letra com acento ou sinal diacrítico". Não diz o que
  acontece com um sinal combinante sobre algo que não é letra (hífen, espaço,
  início do texto), nem com marcas combinantes que não são acento (U+0338,
  U+20DD, seletores de variação).
    - Em (a), o passo 1 roda antes do passo 3 e não remove o hífen, porque o
  último caractere é o sinal. Se o passo 3 remove o sinal, sobra `alimentacao-`
  com hífen final, que o passo 4 (só sequências internas) não trata. Se não
  remove, sobra o sinal. As duas leituras recusam a despesa, mas por caminhos
  diferentes, e uma terceira leitura (passo 1 reaplicado) reconheceria a
  categoria.
    - Em (d), uma leitura dá `smorrebrød` × `smørrebrød` (diferentes) e outra
  deixa as duas com o traço (iguais ou não, conforme o caso).
  - **Por que é um problema:** o resultado de duplicata e de categoria depende
  de como o código separa e descarta as marcas. A D-005 tratou separadores nas
  pontas, mas não separadores que só viram ponta depois do passo 3.
  - **Pergunta para decisão:** o passo 3 remove todo caractere combinante, ou só
  os sinais que acompanham uma letra? E os passos 1 e 4 valem para separadores
  que só ficam na ponta ou adjacentes depois do passo 3?

  ### 3. Fornecedor só de separadores normaliza para texto vazio e passa na
  validação — PODE ESPERAR — brecha (incoerência com RN-002)

  - **Regras afetadas:** RN-002 (texto vazio ou só com espaços →
  `entrada_invalida`), seção 5 (passo 1, novo), RN-007.
  - **Cenário de entrada:** em 03/07, dois táxis de `transporte_urbano`, 25,00
  cada, sem nota, com `fornecedor` `"-"` e `"_"` (ou `"--"`, `" - "`). É
  plausível: o campo é obrigatório e o colaborador põe um traço quando não sabe
  o fornecedor.
  - **Comportamento pela interpretação atual:**
    - Pela RN-002, `"-"` não é texto vazio nem só espaço, então a despesa é
  válida.
    - Pela 1.7, o passo 1 reduz `"-"`, `"_"` e `" - "` ao texto vazio. Os dois
  táxis viram duplicatas: o segundo sai `duplicata`, com 0,00.
    - Na 1.6, o resultado de `"-"` × `"_"` era indefinido (o problema que a
  D-005 fechou). Agora está definido, mas um fornecedor "sem conteúdo" é aceito
  e se iguala a qualquer outro fornecedor "sem conteúdo".
    - O mesmo vale para `categoria` `"-"`: normaliza para vazio e sai
  `categoria_fora_da_politica` (não `entrada_invalida`), com a categoria "como
  veio".
  - **Por que é um problema:** a RN-002 recusa `"   "` como fornecedor
  inexistente, mas aceita `"-"`, que depois da normalização é igualmente vazio.
  Isso funde fornecedores desconhecidos distintos na detecção de duplicatas.
  - **Pergunta para decisão:** um `fornecedor` ou `categoria` cujo texto
  normalizado fica vazio deve ter o mesmo tratamento do texto "só com espaços em
  branco" da RN-002, ou segue como valor válido igual a qualquer outro texto
  que também normaliza para vazio?

  ### 4. "Ignorar maiúsculas/minúsculas" não diz qual equivalência de caixa —
  PODE ESPERAR — ambiguidade

  - **Regras afetadas:** seção 5, passo 2; RN-007.
  - **Cenário de entrada:** duas alimentações em 03/07, 40,00, com nota,
  fornecedores `"STRASSE CAFE"` e `"Straße Cafe"`. Variante: `"ẞ"` maiúsculo
  (U+1E9E).
  - **Comportamento pela interpretação atual:** indefinido. Se "ignorar caixa"
  for só converter para minúsculas, `ß` ≠ `ss` e as duas são avaliadas, com
  80,00 → 60,00 pelo limite. Se for a equivalência completa de caixa do Unicode,
  `ß` = `ss` e a segunda é `duplicata`, com 40,00 → 40,00 sem o corte.
  - **Por que é um problema:** o passo 3 agora fixa a referência no Unicode
  (decomposição canônica), mas o passo 2 não diz qual mapeamento de caixa usa. O
  caso é raro em dados em português.
  - **Pergunta para decisão:** a equivalência de maiúsculas/minúsculas do passo
  2 inclui mapeamentos que mudam o número de letras (`ß` ↔ `ss`), ou só a
  correspondência letra a letra?

  ### 5. Os comportamentos novos da 1.7 não estão em casos de borda nem em
  aceite da spec — PODE ESPERAR — lacuna (rastreabilidade)

  - **Regras afetadas:** seção 5 (passos 1 e 3), RN-006 (aceite), RN-007
  (aceite), seção 7, seção 9 ("cada caso de borda da seção 7 tem um teste").
  - **Cenário de entrada:** `categoria` `"alimentacao-"`; fornecedores
  `"-Bistro"` × `"_Bistro"`; fornecedores `"Smørrebrød"` × `"Smorrebrod"`.
  - **Comportamento pela interpretação atual:** a seção 5 define o resultado só
  por exemplos de normalização. Nenhuma linha da seção 7 e nenhum aceite da
  RN-006/RN-007 traz esses casos. Diferente da D-002 a D-004, a D-005 não lista
  "casos de borda novos". Segundo a própria D-005, o aceite novo está só na
  T-003, no `tasks.md`.
  - **Por que é um problema:** pelo critério da seção 9, o teste do sistema
  pronto não exige cobrir o comportamento decidido na 1.7, que a justificativa
  da D-005 cita como motivo da mudança (`"alimentacao-"` reconhecida). Só a task
  cobre esses casos, e a spec não.
  - **Pergunta para decisão:** os comportamentos decididos na D-005 (separador
  nas pontas e letra sem decomposição) devem constar da seção 7 e dos aceites da
  RN-006/RN-007, ou basta o aceite da T-003?

  **Decidir antes da implementação:** 1.

  **Pode ser decidido depois:** 2, 3, 4, 5.

⏺ O spec-adversary encontrou 5 problemas na spec 1.7, e um deles bloqueia o 
  commit. Ainda não fiz nenhum commit.

  Bloqueante: quais caracteres contam como hífen e como espaço em branco

  Os passos 1 e 4 da seção 5 falam em "hífens (-)" e em "demais caracteres de
  espaço em branco", mas não dizem quais caracteres entram nessas listas.
  Exemplos em que a resposta muda o valor reembolsado:

  - Travessão curto: o Word costuma trocar o hífen por – (U+2013) sozinho. Com
    isso, "Transporte – Urbano" pode ser reconhecida (transporte_urbano) ou
    recusada (categoria_fora_da_politica, com reembolso 0).
  - Fornecedor: "Bistro - Centro" e "Bistro – Centro" podem ou não ser tratadas
    como duplicata.
  - Caracteres invisíveis: "alimentacao", com um espaço de largura zero (U+200B)
    ou um BOM (U+FEFF), pode ou não ser reconhecida.

  Hoje o código usa a definição de espaço em branco do Python. Ela inclui quatro
  caracteres de controle (U+001C a U+001F) que o Unicode não considera espaço,
  e só trata como hífen o - comum (U+002D).

  Minha recomendação:
  - Espaço em branco: os caracteres que o próprio Unicode classifica como espaço
    em branco. O espaço de largura zero e o BOM ficam fora e vão para os riscos
    aceitos.
  - Hífen: qualquer traço, ou seja, o - comum, o hífen tipográfico e os
    travessões (o Unicode agrupa todos numa mesma categoria). O sinal de menos
    (U+2212) fica fora.

  Isso segue a lógica da AMB-011 e da D-005: o travessão que o editor coloca
  sozinho é só uma diferença de grafia. Com essa opção, ajusto a spec para 1.8
  (entrada D-005 ampliada), o DT-004, o código e os testes, e rodo os dois
  revisores de novo.

  Problemas que podem esperar

  2. Acento solto sobre um traço ou no início do texto. Exemplo: "alimentacao-́",
     com um acento sobre o hífen. Só acontece com entradas patológicas.
     Recomendo registrar como risco aceito.
  3. Fornecedor só de traços. Fornecedores "-" e "_" ficam vazios depois da
     normalização. Por isso duas despesas desse tipo viram duplicata uma da
     outra, enquanto um fornecedor "   " (só espaços) já é entrada_invalida pela
     RN-002. Esse é o mais relevante dos quatro, porque pôr um traço no campo
     quando não se sabe o fornecedor é plausível. Só que ele mexe na RN-002, que
     é escopo da T-009. Recomendo decidir antes da T-009 se texto que fica
     vazio depois da normalização é entrada_invalida.
  4. ß e ss. Hoje "Straße" e "Strasse" contam como o mesmo fornecedor. Recomendo
     manter assim e registrar na spec.
  5. Casos novos fora da seção 7. Os comportamentos decididos na D-005 aparecem
     só no aceite da T-003, não na seção 7 da spec. Recomendo deixar para a
     T-021: incluí-los agora mexe na contagem de 63 casos e na distribuição
     deles entre as tasks.

  Como você decide o bloqueante (1)? E o 3: decidimos agora ou deixamos para
  antes da T-009?

✻ Churned for 18s · done 10:50 PM

⏺ Agent "Revisão adversarial spec 1.7" finished · 1m 53s

❯ não tem como limpar tudo que entre de caracteres especial?                    

  Searched for 1 pattern (ctrl+o to expand)

⏺ Dá, sim. E é mais simples que a minha recomendação. A regra ficaria assim:
  depois de tirar caixa e acentos, só letras e dígitos importam. Qualquer 
  sequência de outros caracteres vira um _ quando está no meio do texto e é 
  removida quando está nas pontas. "Outros caracteres" inclui espaço de qualquer
  tipo, hífen, travessão, ponto, &, parênteses, emoji e caracteres invisíveis.

  O que isso resolve:
  - Problema 1 (o bloqueante): fecha por inteiro. Não precisa mais de uma lista
    de quais caracteres são hífen ou espaço, porque tudo que não é letra nem
    dígito recebe o mesmo tratamento. "Transporte – Urbano", "alimentacao" e
    "alimentacao\x1c" são reconhecidas.
  - Problema 2: quase todo. "alimentacao-́" vira alimentacao, desde que o acento
    seja removido antes de cortar as pontas (inverto a ordem dos passos).
  - Exemplo do desafio (seção 9): nada muda. Conferi: nenhuma categoria ou
    fornecedor do arquivo tem caractere especial.

  O que muda, e você precisa aceitar:
  - Mais fornecedores contam como iguais. "Padaria (Centro)" = "Padaria Centro"
    e "Loja 1" = "Loja-1". Isso tende a ser o certo, mas aumenta a chance de uma
    despesa sair como duplicata. Ainda ficam diferentes os casos em que a
    pontuação está colada dentro da palavra: "McDonald's" vira mcdonald_s,
    diferente de "McDonalds".
  - Caractere invisível no meio da palavra vira separador. "alimentacao" vira
    ali_mentacao e é recusada. Dá para remover esses invisíveis em vez de
    trocá-los por _, mas isso volta a exigir uma lista. Sugiro aceitar como
    risco.
  - O problema 3 piora. Fornecedores "-", "?", "***" e "N/A"… quase: "N/A" vira
    n_a. Mas qualquer fornecedor só de símbolos fica vazio, e todos esses passam
    a contar como o mesmo fornecedor na busca de duplicatas. Com essa regra, eu
    decidiria agora que texto que fica vazio depois da normalização é 
    entrada_invalida, igual ao texto só com espaços que a RN-002 já recusa. A
    implementação disso fica na T-009, mas a decisão entra na spec agora.

  Se você aprovar, faço assim:
  - Spec 1.8: os passos da seção 5 reescritos nessa forma, os riscos aceitos
    atualizados e a regra do texto vazio na RN-002.
  - DECISIONS.md: uma entrada D-006.
  - Plano e tasks: DT-004 alinhado e aceite da T-003 atualizado.
  - Código e testes da T-003, com os casos novos falhando antes do ajuste.
  - Os dois revisores rodam de novo.

  Aprova essa regra e o texto vazio como entrada_invalida?

✻ Cooked for 6m 5s · done 10:53 PM

❯ qual opcao melhor?                                                            

⏺ Recomendo a segunda opção, "só letras e dígitos importam", junto com a regra
  de que texto vazio depois da normalização é entrada_invalida.

  Por que ela é melhor:
  - Fecha o problema de vez. A primeira opção troca uma lista indefinida por
    outra mais longa: categorias de traço do Unicode, propriedade de espaço em
    branco, exceções para U+2212, U+200B e BOM. Cada caractere que ficasse de
    fora daria um novo achado do spec-adversary. Na segunda não existe lista.
  - Qualquer pessoa consegue conferir. "Só letras e dígitos contam" dá para
    checar lendo a spec, sem consultar tabela do Unicode. É o teste de aceitação
    da própria spec, no topo do arquivo.
  - O efeito colateral é pequeno. Juntar mais fornecedores só pesa na busca de
    duplicatas, e lá eles também precisam ter a mesma data, a mesma categoria e
    o mesmo valor ao centavo. Duas despesas reais com tudo isso igual e
    fornecedor diferente só na pontuação, como "Padaria (Centro)" e "Padaria 
    Centro", quase certamente são a mesma despesa.
  - Segue a lógica que você já aprovou. É a mesma da AMB-011 e da D-005:
    diferença de grafia não muda o significado.

  O texto vazio como entrada_invalida vem junto, não é opcional. Sem essa regra,
  "-", "?" e "***" viram o mesmo fornecedor e se anulam como duplicatas. A
  RN-002 já recusa um fornecedor só com espaços; isso só estende a mesma ideia.

  O único custo real: um caractere invisível no meio da palavra ("alimentacao")
  vira separador e a despesa é recusada. É raro e fica registrado como risco
  aceito.

  Posso seguir com essa opção?

✻ Churned for 14s · done 10:55 PM

❯ pode seguir                                                                   

  Ran 1 shell command (ctrl+o to expand)

⏺ Aplicando a regra na spec 1.8. Sigo o precedente da D-004: a rodada sobre a
  1.7, que nunca foi commitada, entra na mesma entrada D-005, em vez de abrir
  uma D-006.

  Ran 2 shell commands (ctrl+o to expand)

⏺ Bash(python3 - <<'PYEOF'
      import pathlib, re…)
  ⎿   specs/001-motor-reembolso/DECISIONS.md | 26 +++++++++++++++++++++++++
     +
      specs/001-motor-reembolso/plan.md      | 12 ++++++------
     … +5 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/DECISIONS.md (+14 -9)
      10  
      11  ---
      12  
      13 -## D-005 — Pontas e letras sem decomposição na normalização: sp
         -ec 1.6 → 1.7 · `2026-10-01`                                    
      13 +## D-005 — Normalização: só letras e algarismos contam: spec 1.
         +6 → 1.8 · `2026-10-01`                                         
      14  
      15 -**Gatilho:** revisão independente da T-003 (`docs/reviews/T-003
         -.md`, resultado BLOQUEADO). O passo 4 da seção 5 só tratava seq
         -uências **internas** de separadores, e o passo 1 só removia esp
         -aço em branco das pontas: hífen ou sublinhado no início ou no f
         -im não tinham resultado definido (`"-Bistro"` × `"_Bistro"` mud
         -am a RN-007). O passo 3 não dizia se letras como `ø`, `ł`, `đ` 
         -contam como letra com sinal. O responsável decidiu os dois pont
         -os (sessão `docs/sessions/13-*`).                              
      15 +**Gatilho:** revisão independente da T-003 (`docs/reviews/T-003
         +.md`, revisão 1, BLOQUEADO). O passo 4 da seção 5 só tratava se
         +quências **internas** de separadores e o passo 1 só removia esp
         +aço em branco das pontas: hífen ou sublinhado no início ou no f
         +im não tinham resultado definido (`"-Bistro"` × `"_Bistro"` mud
         +am a RN-007). O passo 3 não dizia se `ø`, `ł`, `đ` contam como 
         +letra com sinal. O responsável decidiu os dois pontos (versão 1
         +.7, não commitada). A rodada do `spec-adversary` sobre a 1.7 ap
         +ontou 5 problemas (1 bloqueante): o conjunto de "hífens" e de "
         +espaços em branco" não estava fechado (travessão U+2013 colocad
         +o pelo editor, espaço de largura zero, BOM, caracteres de contr
         +ole). O responsável optou por trocar as listas por uma regra ún
         +ica, "só letras e algarismos contam" (versão 1.8). Sessão `docs
         +/sessions/13-*`.                                               
      16  
      17  **O que mudou na spec:**
      18  
      19 -| # | Ponto | De (1.6) | Para (1.7) | Onde |                   
      19 +| # | Ponto | De (1.6) | Para (1.8) | Onde |                   
      20  |---|---|---|---|---|
      21 -| 1 | Hífen e sublinhado nas pontas | indefinido (o passo 1 rem
         -ovia só espaço em branco; o passo 4 tratava só sequências inter
         -nas) | **removidos**, junto com o espaço em branco, em qualquer
         - mistura (`" -_Bistro"` → `bistro`) | seção 5 (passo 1 e exempl
         -os) |                                                          
      22 -| 2 | Letras sem decomposição canônica (`ø`, `ł`, `đ`) | indefi
         -nido | **ficam como estão**; letra base é a da decomposição can
         -ônica do Unicode; registrado como risco aceito | seção 5 (passo
         - 3 e exemplos), seção 10 |                                     
      21 +| 1 | Separadores | espaço em branco, hífen (`-`) e sublinhado;
         + nas pontas, só espaço em branco removido; hífen e sublinhado n
         +as pontas indefinidos | todo caractere que não é letra nem alga
         +rismo decimal é separador (inclui travessão, pontuação, símbolo
         +, emoji, invisível, controle); nas pontas, removido; no meio, c
         +ada sequência vale um `_` | seção 5 (passo 3 e exemplos), AMB-0
         +11 |                                                           
      22 +| 2 | Letras sem decomposição canônica (`ø`, `ł`, `đ`) | indefi
         +nido | **ficam como estão**; letra base é a da decomposição can
         +ônica do Unicode; risco aceito | seção 5 (passo 2), seção 10 | 
      23 +| 3 | Sinal combinante sem letra (sobre hífen, no início, U+033
         +8, seletor de variação) | indefinido | todo sinal combinante é 
         +descartado, acompanhe ele uma letra ou não; descartado antes de
         + separar, então `"alimentacao-́"` → `alimentacao` | seção 5 (pas
         +so 2) |                                                        
      24 +| 4 | Ordem dos passos | pontas → caixa → acentos → separadores
         + internos | caixa → acentos → separadores (pontas e meio juntos
         +) | seção 5 |                                                  
      25 +| 5 | Equivalência de caixa | "ignorar maiúsculas/minúsculas", 
         +sem dizer qual | equivalência completa de caixa do Unicode (`ß`
         + = `ss`) | seção 5 (passo 1) |                                 
      26 +| 6 | `categoria` ou `fornecedor` só de separadores (`"-"`, `"*
         +**"`) | válido; normalizava para vazio e todos os fornecedores 
         +"vazios" eram iguais na RN-007 | `entrada_invalida`, como o tex
         +to só com espaços | RN-002 (regra e aceite), seção 5, seção 7 (
         +linha "Texto vazio em campo obrigatório") |                    
      27 +| 7 | Caractere invisível no meio da palavra | — | é separador 
         +(`ali_mentacao`); risco aceito | seção 10 |                    
      28  
      24 -**Por quê:** o ponto 1 segue a lógica da AMB-011: separador nas
         - pontas é diferença de grafia, não de significado (`"alimentaca
         -o-"` passa a ser reconhecida). O ponto 2 evita uma tabela manua
         -l de equivalências, incompleta por construção (alternativa já d
         -escartada no DT-004); o caso é raro em dados em português.     
      29 +**Por quê:** os pontos 1 e 3 seguem a lógica da AMB-011: separa
         +dor e sinal solto são diferença de grafia, não de significado (
         +`"alimentacao-"` e `"Transporte – Urbano"` passam a ser reconhe
         +cidas). Uma regra única ("só letras e algarismos") fecha o conj
         +unto sem lista de caracteres, que seria incompleta por construç
         +ão, e qualquer pessoa consegue conferir. O efeito colateral (ma
         +is fornecedores iguais, como `"Padaria (Centro)"` = `"Padaria C
         +entro"`) só pesa na RN-007, que também exige mesma data, catego
         +ria e valor ao centavo. O ponto 6 vem junto: sem ele, `"-"` e `
         +"?"` viram o mesmo fornecedor e se anulam como duplicatas, enqu
         +anto `"   "` já era recusado. O ponto 2 evita tabela manual (al
         +ternativa já descartada no DT-004). O ponto 5 registra o compor
         +tamento escolhido; raro em dados em português.                 
      30  
      26 -**O que isso invalidou:** o DT-004 do `plan.md` aplicava o pass
         -o 4 ao texto inteiro (pontas viravam `_`); alinhado na versão 1
         -.1 do plano. Código da T-003 ainda não commitado, ajustado ante
         -s do commit. Nenhum valor do exemplo (seção 9) mudou.          
      31 +**O que isso invalidou:** o DT-004 do `plan.md` (lista fixa de 
         +separadores, só `Mn` removido); alinhado na versão 1.1 do plano
         +. Código da T-003 ainda não commitado, ajustado antes do commit
         +. Aceite da T-009 ganha o texto que normaliza para vazio. Nenhu
         +m valor do exemplo (seção 9) mudou: nenhuma categoria ou fornec
         +edor do arquivo tem caractere fora de letras, algarismos e espa
         +ço simples.                                                    
      32  
      28 -**Tasks afetadas:** T-003 (aceite passa a incluir separadores n
         -as pontas e letra sem decomposição).                           
      33 +**Tasks afetadas:** T-003 (aceite com separadores de qualquer t
         +ipo, sinal solto, `ø`, `ß`), T-009 (aceite com texto normalizad
         +o vazio).                                                      
      34  
      30 -**Custo:** 4 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`, `t
         -asks.md`); 2 pontos decididos na mesma sessão.                 
      35 +**Custo:** 4 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`, `t
         +asks.md`); 7 pontos decididos na mesma sessão. Uma rodada do `s
         +pec-adversary` (sobre a 1.7); rodada sobre a 1.8 antes do commi
         +t.                                                             
      36  
      37  ---
      38  
  ⎿  Updated specs/001-motor-reembolso/plan.md (+6 -6)
      1  # Plano Técnico — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.1 · **Baseado na spec:** 1.7                      
      3 +**Versão:** 1.1 · **Baseado na spec:** 1.8                      
      4  
      5  > Aqui mora o COMO. Este arquivo pode e deve falar de linguagem,
          biblioteca e
      6  > arquitetura. O que ele **não** pode é introduzir regra de negó
         cio nova — se
     ...
      33  |---|---|---|
      34  | `cli.py` | `argparse`, lê bytes do arquivo, chama o pipeline,
           grava a saída de forma atômica, mapeia erros para mensagem + c
          ódigo de saída | sim |
      35  | `entrada.py` | bytes → JSON (`Decimal`) → `Entrada`. Resolve 
          chaves repetidas e gera os avisos (RN-013); erros de arquivo da
           RN-002 viram `ErroDeArquivo`; despesa inválida vira `DespesaIn
          valida` (etapa 1 da seção 8) | não |
      36 -| `normalizacao.py` | `normalizar_texto()` — os 4 passos da seç
         -ão 5 da spec | não |                                           
      36 +| `normalizacao.py` | `normalizar_texto()` — os passos da seção
         + 5 da spec | não |                                             
      37  | `politica.py` | constantes da política (seção 4 deste plano) 
          | não |
      38  | `motor.py` | etapas 2 a 9 da seção 8; recebe `Entrada`, devol
          ve `Resultado` | não |
      39  | `justificativa.py` | frase em português para cada item (texto
           não contratual) | não |
     ...
      138  
      139  ### DT-004 — Normalização de texto com `unicodedata`
      140  
      141 -**Contexto:** seção 5 da spec, 4 passos, "qualquer que seja a 
          -forma como o caractere foi codificado".                       
      142 -**Decisão:** `re.sub(r"\A[\s\-_]+|[\s\-_]+\Z", "", ...)` (pont
          -as: espaço em branco, hífen e sublinhado) → `casefold()` → `un
          -icodedata.normalize("NFD")` e remoção dos caracteres de catego
          -ria `Mn` (marcas combinantes) → `re.sub(r"[\s\-_]+", "_", ...)
          -` (sequências internas). Letras sem decomposição canônica (`ø`
          -, `ł`) ficam como estão, como a spec define. O NFD decompõe ta
          -nto `á` pré-composto (U+00E1) quanto `a` + acento combinante (
          -U+0301) para a mesma sequência, cobrindo as duas codificações.
      143 -**Alternativa descartada:** tabela manual de acentos (`á→a`, .
          -..): incompleta por construção; `NFKD`: também desfaz compatib
          -ilidades (ligaduras, larguras) que a spec não pede.           
      144 -**Consequência:** uma função pura, usada por RN-006 e RN-007, 
          -testada com os exemplos da seção 5 e os casos de borda de cate
          -goria e fornecedor.                                           
      141 +**Contexto:** seção 5 da spec, 3 passos (caixa, acentos, só le
          +tras e algarismos), "qualquer que seja a forma como o caracter
          +e foi codificado".                                            
      142 +**Decisão:** `casefold()` (equivalência completa de caixa, `ß`
          + → `ss`) → `unicodedata.normalize("NFD")` e remoção de todo ca
          +ractere de categoria `M*` (sinais combinantes, com ou sem letr
          +a) → todo caractere que não é de categoria `L*` (letra) nem `N
          +d` (algarismo decimal) vira espaço → `"_".join(texto.split())`
          + (pontas somem, sequências internas viram um `_`). O NFD decom
          +põe tanto `á` pré-composto (U+00E1) quanto `a` + acento combin
          +ante (U+0301) para a mesma sequência, cobrindo as duas codific
          +ações; letras sem decomposição canônica (`ø`, `ł`) ficam como 
          +estão, como a spec define. Texto que resulta vazio é tratado p
          +ela validação (`entrada.py`, RN-002).                         
      143 +**Alternativa descartada:** tabela manual de acentos (`á→a`, .
          +..): incompleta por construção; `NFKD`: também desfaz compatib
          +ilidades (ligaduras, larguras) que a spec não pede; lista de s
          +eparadores (`[\s\-_]`): deixa travessões, invisíveis e pontuaç
          +ão sem resultado definido (D-005).                            
      144 +**Consequência:** uma função pura, usada por RN-006, RN-007 e 
          +pela validação da RN-002, testada com os exemplos da seção 5 e
          + os casos de borda de categoria e fornecedor.                 
      145  
      146  ### DT-005 — Pipeline em duas fases, espelhando a seção 8
      147  
  ⎿  Updated specs/001-motor-reembolso/spec.md (+15 -13)
      1  # Spec — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.7 · **Status:** aprovada para planejamento · **Últ
        -ima alteração:** 2026-10-01 (ver `DECISIONS.md` D-001 a D-005)  
      3 +**Versão:** 1.8 · **Status:** aprovada para planejamento · **Últ
        +ima alteração:** 2026-10-01 (ver `DECISIONS.md` D-001 a D-005)  
      4  
      5  > **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ
         . Nenhuma linha
      6  > aqui pode citar linguagem, biblioteca, classe, função ou estru
         tura de pasta.
     ...
      136  
      137  As regras são aplicadas a cada despesa na ordem da seção 8. A 
           primeira regra que recusa uma despesa encerra a avaliação dela
           : cada despesa recusada tem exatamente um motivo.
      138  
      139 -**Normalização de texto** (usada em RN-006 e RN-007), aplicada
          - nesta ordem:                                                 
      139 +**Normalização de texto** (usada em RN-006, RN-007 e na valida
          +ção de `categoria` e `fornecedor` da RN-002), aplicada nesta o
          +rdem:                                                         
      140  
      141 -1. remover do início e do fim toda sequência de espaços em bra
          -nco (espaço comum, tabulação, quebra de linha, espaço não sepa
          -rável e demais caracteres de espaço em branco), hífens (`-`) e
          - sublinhados (`_`), em qualquer mistura;                      
      142 -2. ignorar maiúsculas/minúsculas;                             
      143 -3. toda letra com acento ou sinal diacrítico é comparada como 
          -a letra base, qualquer que seja a forma como o caractere foi c
          -odificado no arquivo (`á`→`a`, `ç`→`c`, `ô`→`o`, `ü`→`u`, `ñ`→
          -`n`). A letra base é a que resta ao separar os sinais pela dec
          -omposição canônica do Unicode; letras sem essa decomposição, c
          -ujo traço faz parte da própria letra (`ø`, `ł`, `đ`), ficam co
          -mo estão;                                                     
      144 -4. toda sequência interna de espaços em branco, hífens (`-`) e
          - sublinhados (`_`) vale como um único `_`.                    
      141 +1. ignorar maiúsculas/minúsculas, pela equivalência completa d
          +e caixa do Unicode (inclui `ß` = `ss`);                       
      142 +2. toda letra com acento ou sinal diacrítico é comparada como 
          +a letra base, qualquer que seja a forma como o caractere foi c
          +odificado no arquivo (`á`→`a`, `ç`→`c`, `ô`→`o`, `ü`→`u`, `ñ`→
          +`n`). Os sinais são separados pela decomposição canônica do Un
          +icode e todo sinal combinante é descartado, acompanhe ele uma 
          +letra ou não; letras sem essa decomposição, cujo traço faz par
          +te da própria letra (`ø`, `ł`, `đ`), ficam como estão;        
      143 +3. só letras (de qualquer alfabeto) e algarismos decimais cont
          +am. Todo outro caractere é separador: espaço em branco de qual
          +quer tipo, hífen, travessão, sublinhado, pontuação, símbolo, e
          +moji, caractere invisível ou de controle. Toda sequência de se
          +paradores no início ou no fim é removida, e toda sequência int
          +erna vale como um único `_`.                                  
      144  
      146 -Exemplos: `"Transporte Urbano"`, `"transporte-urbano"` e `" TR
          -ANSPORTE__urbano "` → `transporte_urbano`; `"Pão  Quente"` e `
          -"pao-quente"` → `pao_quente`; `"-Bistro"`, `"_Bistro"`, `"Bist
          -ro -"` e `" -_Bistro"` → `bistro`; `"Smørrebrød"` → `smørrebrø
          -d` (diferente de `smorrebrod`).                               
      145 +Texto cujo resultado fica vazio (só separadores, como `"-"` ou
          + `"***"`) não identifica categoria nem fornecedor: a despesa é
          + inválida (RN-002).                                           
      146 +                                                              
      147 +Exemplos: `"Transporte Urbano"`, `"transporte-urbano"`, `" TRA
          +NSPORTE__urbano "` e `"Transporte – Urbano"` (travessão) → `tr
          +ansporte_urbano`; `"Pão  Quente"` e `"pao-quente"` → `pao_quen
          +te`; `"-Bistro"`, `"_Bistro"`, `"Bistro -"` e `" -_Bistro"` → 
          +`bistro`; `"Padaria (Centro)"` → `padaria_centro`; `"McDonald'
          +s"` → `mcdonald_s` (diferente de `mcdonalds`); `"Straße"` → `s
          +trasse`; `"Smørrebrød"` → `smørrebrød` (diferente de `smorrebr
          +od`); `"-"` → vazio.                                          
      148  
      149  ### RN-001 — Um resultado por despesa
      150  
     ...
      156  
      157  **Regra:**
      158  - **Erro de arquivo** (o arquivo de saída não é criado nem alt
           erado): arquivo de entrada ausente ou que não é JSON válido; t
           exto, em chave ou valor, com escape que não forma caractere Un
           icode válido (seção 4); `colaborador` ausente ou sem `id`/`nom
           e` em texto, ou com `id`/`nome` vazio ou só com espaços em bra
           nco; `periodo.inicio`, `periodo.fim` ou `despesas` ausentes; `
           inicio` ou `fim` que não são datas válidas `AAAA-MM-DD`; `inic
           io` posterior a `fim`; `despesas` que não é lista; arquivo de 
           saída que não pode ser gravado. `periodo.competencia` nunca ca
           usa erro: se não for texto, sai nula.
      158 -- **Despesa inválida** (vira item `recusado` com motivo `entra
          -da_invalida`; as demais despesas seguem): elemento de `despesa
          -s` que não é um objeto; falta `id`, `data`, `categoria`, `forn
          -ecedor`, `valor` ou `tem_nota_fiscal`; `data` não é data válid
          -a `AAAA-MM-DD`; `valor` não é número; `tem_nota_fiscal` não é 
          -booleano; `id`, `categoria` ou `fornecedor` não são texto, ou 
          -são texto vazio ou só com espaços em branco; `valor` com valor
          - absoluto maior ou igual a 1.000.000.000,00 (um bilhão), compa
          -rado com o número recebido, antes do arredondamento (AMB-018).
      159 +- **Despesa inválida** (vira item `recusado` com motivo `entra
          +da_invalida`; as demais despesas seguem): elemento de `despesa
          +s` que não é um objeto; falta `id`, `data`, `categoria`, `forn
          +ecedor`, `valor` ou `tem_nota_fiscal`; `data` não é data válid
          +a `AAAA-MM-DD`; `valor` não é número; `tem_nota_fiscal` não é 
          +booleano; `id`, `categoria` ou `fornecedor` não são texto, ou 
          +são texto vazio ou só com espaços em branco; `categoria` ou `f
          +ornecedor` cujo texto normalizado (seção 5) fica vazio, como `
          +"-"` ou `"***"`; `valor` com valor absoluto maior ou igual a 1
          +.000.000.000,00 (um bilhão), comparado com o número recebido, 
          +antes do arredondamento (AMB-018).                            
      160  - Na saída de uma despesa inválida, `id`, `data` e `categoria`
            são copiados se forem texto e saem nulos caso contrário (tipo
            errado, ausente ou elemento que não é objeto); a `categoria`,
            se reconhecida, sai normalizada, como em qualquer item (seção
            4).
      161  - Uma despesa recusada por `entrada_invalida` tem `valor_consi
           derado` nulo, `em_viagem` e `limite_diario` nulos, e não entra
            nos totais.
      162  - Campos extras, no arquivo ou nas despesas, são ignorados.
      162 -**Origem:** necessidade operacional (a política não trata entr
          -ada malformada); pontos 7 e 9 de D-001; AMB-018.              
      163 -**Aceite:** despesa sem `tem_nota_fiscal` com `valor` 33.333 →
          - `recusado`, `entrada_invalida`, `valor_informado` 33.333, `va
          -lor_considerado` nulo, fora de `valor_solicitado`; as demais d
          -espesas são processadas normalmente. Elemento `null` em `despe
          -sas` → item com `id` e `data` nulos, `entrada_invalida`. Arqui
          -vo sem `colaborador` → nenhuma saída, código diferente de 0. H
          -ospedagem com campo extra `"noites": 2` → avaliada como uma di
          -ária (RN-012). Despesa com `"id": 17` → `entrada_invalida`, `i
          -d` nulo na saída. Despesa com `fornecedor` `"   "` → `entrada_
          -invalida`. `competencia` 202607 (número) → processamento norma
          -l, `competencia` nula na saída. Caminho de saída em pasta inex
          -istente → nenhuma saída, código diferente de 0. Despesa `"cate
          -goria": "ALIMENTACAO"` sem `tem_nota_fiscal` → `entrada_invali
          -da`, `categoria` `alimentacao` na saída. `colaborador.nome` `"
          -  "` → erro de arquivo. Erro de arquivo com arquivo de saída p
          -reexistente → o arquivo continua com o conteúdo anterior. Cham
          -ada sem `--output` → código diferente de 0. `valor` 1000000000
          - → `entrada_invalida`, `valor_informado` 1000000000, fora dos 
          -totais. `valor` -1e12 → `entrada_invalida` (não `valor_invalid
          -o`). `valor` 999999999.995 → segue, com `valor_considerado` 10
          -00000000.00 (o teto vale para o número recebido).             
      163 +**Origem:** necessidade operacional (a política não trata entr
          +ada malformada); pontos 7 e 9 de D-001; AMB-018; D-005.       
      164 +**Aceite:** despesa sem `tem_nota_fiscal` com `valor` 33.333 →
          + `recusado`, `entrada_invalida`, `valor_informado` 33.333, `va
          +lor_considerado` nulo, fora de `valor_solicitado`; as demais d
          +espesas são processadas normalmente. Elemento `null` em `despe
          +sas` → item com `id` e `data` nulos, `entrada_invalida`. Arqui
          +vo sem `colaborador` → nenhuma saída, código diferente de 0. H
          +ospedagem com campo extra `"noites": 2` → avaliada como uma di
          +ária (RN-012). Despesa com `"id": 17` → `entrada_invalida`, `i
          +d` nulo na saída. Despesa com `fornecedor` `"   "` → `entrada_
          +invalida`. Despesa com `fornecedor` `"-"` → `entrada_invalida`
          +. `competencia` 202607 (número) → processamento normal, `compe
          +tencia` nula na saída. Caminho de saída em pasta inexistente →
          + nenhuma saída, código diferente de 0. Despesa `"categoria": "
          +ALIMENTACAO"` sem `tem_nota_fiscal` → `entrada_invalida`, `cat
          +egoria` `alimentacao` na saída. `colaborador.nome` `"  "` → er
          +ro de arquivo. Erro de arquivo com arquivo de saída preexisten
          +te → o arquivo continua com o conteúdo anterior. Chamada sem `
          +--output` → código diferente de 0. `valor` 1000000000 → `entra
          +da_invalida`, `valor_informado` 1000000000, fora dos totais. `
          +valor` -1e12 → `entrada_invalida` (não `valor_invalido`). `val
          +or` 999999999.995 → segue, com `valor_considerado` 1000000000.
          +00 (o teto vale para o número recebido).                      
     … 26 more lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+5 -5)
      1  # Tasks — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.1 · **Baseado em:** spec 1.7, plan 1.1            
      3 +**Versão:** 1.1 · **Baseado em:** spec 1.8, plan 1.1            
      4  
      5  > Cada task é pequena o bastante para virar **um commit**. Se vo
         cê não consegue
      6  > descrever o critério de aceite como "o teste X passa", a task 
         está grande demais.
     ...
      38    - **Aceite:** `tests/test_politica.py` passa: `test_rn009_lim
          ites_conferem_tabela_da_spec` (60/90, 80/120, 250/250), `test_r
          n006_tres_categorias_reconhecidas`, `test_rn008_valor_de_nota_e
          _100`, `test_rn002_teto_de_um_bilhao`, `test_rn010_viagem_cobre
          _d_e_d_mais_1`, `test_motivos_na_ordem_da_secao_8`; todas as co
          nstantes monetárias são `Decimal`.
      39    - **Commit:** 6e1f498
      40  
      41 -- [ ] **T-003** — Normalização de texto: `normalizar_texto()` c
         -om os 4 passos da seção 5 da spec (DT-004).                    
      41 +- [ ] **T-003** — Normalização de texto: `normalizar_texto()` c
         +om os passos da seção 5 da spec (DT-004).                      
      42    - **Tipo:** regra
      43 -  - **Atende:** seção 5 da spec (normalização), AMB-011; usada 
         -por RN-006 e RN-007                                            
      43 +  - **Atende:** seção 5 da spec (normalização), AMB-011, D-005;
         + usada por RN-002, RN-006 e RN-007                             
      44    - **Depende de:** T-001
      45 -  - **Aceite:** `tests/test_normalizacao.py` passa: exemplos da
         - seção 5 (`"Transporte Urbano"`, `"transporte-urbano"`, `" TRAN
         -SPORTE__urbano "` → `transporte_urbano`; `"Pão  Quente"`, `"pao
         --quente"` → `pao_quente`); acento pré-composto e combinante dão
         - o mesmo resultado; `ç`, `ô`, `ü`, `ñ`; tabulação, quebra de li
         -nha e espaço não separável nas pontas; mistura de espaço, hífen
         - e sublinhado internos vira um `_`; hífen e sublinhado nas pont
         -as, misturados ou não com espaço em branco, são removidos (`"-B
         -istro"`, `"_Bistro"`, `" -_Bistro"` → `bistro`; `"alimentacao-"
         -` → `alimentacao`); `ø`, `ł`, `đ` ficam como estão (spec 1.7, D
         --005).                                                         
      45 +  - **Aceite:** `tests/test_normalizacao.py` passa: exemplos da
         + seção 5 (`"Transporte Urbano"`, `"transporte-urbano"`, `" TRAN
         +SPORTE__urbano "`, `"Transporte – Urbano"` → `transporte_urbano
         +`; `"Pão  Quente"`, `"pao-quente"` → `pao_quente`; `"-Bistro"`,
         + `"_Bistro"`, `"Bistro -"`, `" -_Bistro"` → `bistro`; `"Padaria
         + (Centro)"` → `padaria_centro`; `"McDonald's"` → `mcdonald_s`; 
         +`"Straße"` → `strasse`; `"Smørrebrød"` → `smørrebrød`; `"-"` → 
         +vazio); acento pré-composto e combinante dão o mesmo resultado;
         + `ç`, `ô`, `ü`, `ñ`; sinal combinante solto (no início, sobre h
         +ífen no fim) é descartado; tabulação, quebra de linha, espaço n
         +ão separável, espaço de largura zero e caractere de controle na
         +s pontas; mistura de separadores internos de qualquer tipo vira
         + um `_`; algarismos são mantidos.                              
      46    - **Commit:**
      47  
      48  - [ ] **T-004** — Justificativa: `justificativa.py` gera a fras
          e em português de um item já decidido, para cada status e motiv
          o, com formatação própria `1.234,56` e `DD/MM` sem `locale` (DT
          -009).
     ...
      86    - **Tipo:** regra
      87    - **Atende:** RN-002 (despesa inválida), AMB-018, DT-003
      88    - **Depende de:** T-003, T-007, T-008
      89 -  - **Aceite:** `tests/test_rn002_validacao_da_entrada.py` pass
         -a os testes de despesa: elemento que não é objeto (`null`, núme
         -ro, lista) → inválida com `id`/`data` nulos; cada campo obrigat
         -ório ausente; `data` em formato errado (mesmos casos da T-008);
         - `valor` não número (`"10"`, `true`, `null`); `tem_nota_fiscal`
         - não booleano (`1`, `"sim"`); `id`/`categoria`/`fornecedor` não
         - texto, vazio ou só espaços; `abs(valor) >= 1000000000` (inclus
         -ive `-1e12` e `1e999999`) → inválida; `999999999.995` e `999999
         -999.99999999999` → válidas; `"id": 17` → `id` nulo; `"ALIMENTAC
         -AO"` em despesa inválida → `categoria_saida` `alimentacao`; cat
         -egoria não reconhecida em despesa inválida → como veio; campo e
         -xtra ignorado; `valor_informado` guardado quando é número.     
      89 +  - **Aceite:** `tests/test_rn002_validacao_da_entrada.py` pass
         +a os testes de despesa: elemento que não é objeto (`null`, núme
         +ro, lista) → inválida com `id`/`data` nulos; cada campo obrigat
         +ório ausente; `data` em formato errado (mesmos casos da T-008);
         + `valor` não número (`"10"`, `true`, `null`); `tem_nota_fiscal`
         + não booleano (`1`, `"sim"`); `id`/`categoria`/`fornecedor` não
         + texto, vazio ou só espaços; `categoria`/`fornecedor` cujo text
         +o normalizado fica vazio (`"-"`, `"***"`); `abs(valor) >= 10000
         +00000` (inclusive `-1e12` e `1e999999`) → inválida; `999999999.
         +995` e `999999999.99999999999` → válidas; `"id": 17` → `id` nul
         +o; `"ALIMENTACAO"` em despesa inválida → `categoria_saida` `ali
         +mentacao`; categoria não reconhecida em despesa inválida → como
         + veio; campo extra ignorado; `valor_informado` guardado quando 
         +é número.                                                      
      90    - **Commit:**
      91  
      92  ## Fase 3 — Regras de negócio (motor)

⏺ Agora os testes, reescritos para a nova numeração dos passos e com os casos
  novos:

⏺ Write(tests/test_normalizacao.py)
  ⎿  Error writing file

  Read 1 file, ran 2 shell commands (ctrl+o to expand)

⏺ O arquivo no disco é a versão anterior. O aviso de "modificado" veio do meu
  próprio cat >> de antes. Gravando de novo:

⏺ Bash(cat > tests/test_normalizacao.py <<'EOF'
      import pytest…)
  ⎿  Updated tests/test_normalizacao.py (+94 -43)
       5  
       6  @pytest.mark.parametrize(
       7      "texto",
       8 -    ["Transporte Urbano", "transporte-urbano", " TRANSPORTE__ur
         -bano "],                                                       
       8 +    [                                                          
       9 +        "Transporte Urbano",                                   
      10 +        "transporte-urbano",                                   
      11 +        " TRANSPORTE__urbano ",                                
      12 +        "Transporte – Urbano",  # travessão (U+2013)           
      13 +    ],                                                         
      14  )
      15  def test_secao5_exemplos_transporte_urbano(texto):
      16      """Seção 5 / AMB-011: exemplos da spec que viram `transport
          e_urbano`."""
      12 -    # passos 1 (pontas), 2 (caixa) e 4 (espaço, hífen, `__` → u
         -m `_`)                                                         
      17 +    # passo 1 (caixa) e passo 3 (pontas somem; espaço, hífen, `
         +__`, " – " → um `_`)                                           
      18      assert normalizar_texto(texto) == "transporte_urbano"
      19  
      20  
      21  @pytest.mark.parametrize("texto", ["Pão  Quente", "pao-quente"]
          )
      22  def test_secao5_exemplos_pao_quente(texto):
      23      """Seção 5 / AMB-011: exemplos da spec que viram `pao_quent
          e`."""
      19 -    # passo 3 (`ã` → `a`) e passo 4 (dois espaços ou hífen → um
         - `_`)                                                          
      24 +    # passo 2 (`ã` → `a`) e passo 3 (dois espaços ou hífen → um
         + `_`)                                                          
      25      assert normalizar_texto(texto) == "pao_quente"
      26  
      27  
      28 +@pytest.mark.parametrize(                                      
      29 +    ("texto", "esperado"),                                     
      30 +    [                                                          
      31 +        ("Padaria (Centro)", "padaria_centro"),  # " (" → `_`; 
         +")" na ponta some                                              
      32 +        ("McDonald's", "mcdonald_s"),  # "'" interno → `_`     
      33 +        ("Straße", "strasse"),  # passo 1: equivalência complet
         +a de caixa                                                     
      34 +        ("Smørrebrød", "smørrebrød"),  # passo 2: ø sem decompo
         +sição canônica                                                 
      35 +        ("-", ""),  # só separadores → vazio                   
      36 +    ],                                                         
      37 +)                                                              
      38 +def test_secao5_demais_exemplos_da_spec(texto, esperado):      
      39 +    """Seção 5 (spec 1.8, D-005): exemplos de pontuação, `ß`, `
         +ø` e texto vazio."""                                           
      40 +    assert normalizar_texto(texto) == esperado                 
      41 +                                                               
     … 153 more lines (ctrl+o to expand)

  Ran 2 shell commands (ctrl+o to expand)

⏺ 11 testes falham na asserção como esperado — travessão, pontuação, caracteres
  invisíveis/de controle e sinal solto sobre hífen — enquanto os demais já
  passavam com o código anterior. Agora vou implementar conforme o DT-004 da
  1.1.

⏺ Bash(cat > src/reembolso/normalizacao.py <<'EOF'
      """normalizar_texto(): os passos da seção 5 da spec."""…)
  ⎿  70 passed in 0.04s
     All checks passed!
      M specs/001-motor-reembolso/DECISIONS.md
     … +6 lines (ctrl+o to expand)
  ⎿  Updated src/reembolso/normalizacao.py (+10 -12)
       1 -"""normalizar_texto(): os 4 passos da seção 5 da spec."""      
       1 +"""normalizar_texto(): os passos da seção 5 da spec."""        
       2  
       3 -import re                                                      
       3  import unicodedata
       4  
       6 -_PONTAS = re.compile(r"\A[\s\-_]+|[\s\-_]+\Z")                 
       7 -_SEPARADORES = re.compile(r"[\s\-_]+")                         
       5 +                                                               
       6 +def _conta(caractere: str) -> bool:                            
       7 +    """Letra (categoria `L*`) ou algarismo decimal (`Nd`); o re
         +sto é separador."""                                            
       8 +    categoria = unicodedata.category(caractere)                
       9 +    return categoria.startswith("L") or categoria == "Nd"      
      10  
      11  
      12  def normalizar_texto(texto: str) -> str:
      13      """Normaliza categoria ou fornecedor conforme a seção 5 da 
          spec (DT-004)."""
      12 -    texto = _PONTAS.sub("", texto)                             
      13 -    texto = texto.casefold()                                   
      14 -    texto = "".join(                                           
      15 -        c                                                      
      16 -        for c in unicodedata.normalize("NFD", texto)           
      17 -        if unicodedata.category(c) != "Mn"                     
      18 -    )                                                          
      19 -    return _SEPARADORES.sub("_", texto)                        
      14 +    texto = unicodedata.normalize("NFD", texto.casefold())     
      15 +    texto = "".join(c for c in texto if not unicodedata.categor
         +y(c).startswith("M"))                                          
      16 +    texto = "".join(c if _conta(c) else " " for c in texto)    
      17 +    return "_".join(texto.split())                             

⏺ Os 70 testes passam e o ruff está limpo. Rodando de novo o spec-adversary,
  agora sobre a 1.8, e o revisor da T-003 (revisão 3):
⏺ 2 background agents launched (↓ to manage)
   ├ spec-adversary (Revisão adversarial spec 1.8)
   └ revisor-de-task (Revisar task T-003 (revisão 3))

⏺ Apliquei a regra "só letras e algarismos contam". Os 70 testes passam e o ruff
  está limpo. Ainda não fiz nenhum commit.

  Spec 1.8:
  - Seção 5 agora tem 3 passos:
    a. Ignorar maiúsculas e minúsculas. ß passa a valer ss.
    b. Descartar todo acento ou sinal, mesmo solto. ø, ł e đ ficam como estão.
    c. Só letras e algarismos contam. Qualquer outro caractere é removido nas
       pontas e, no meio, cada sequência vira um _.
  - RN-002: categoria ou fornecedor que fica vazio depois da normalização ("-",
    "***") é entrada_invalida. Acrescentei o caso ao aceite e à linha "Texto
    vazio em campo obrigatório" da seção 7, então a contagem de 63 casos
    continua a mesma.
  - Seção 10: novo risco aceito para o caractere invisível no meio da palavra.
  - DECISIONS.md: a D-005 cobre as versões 1.6 → 1.8. Segui o precedente da
    D-004 em vez de abrir uma D-006, porque a 1.7 nunca foi commitada.

  O que mais mudou:
  - plan.md: o DT-004 foi reescrito para a regra nova.
  - tasks.md: o aceite da T-003 foi atualizado. O da T-009 ganhou o caso de
    texto vazio depois da normalização. A implementação dessa recusa fica na
    T-009; a T-003 só garante que a normalização devolve texto vazio.
  - Código: normalizacao.py aplica caixa, depois descarta os sinais e por fim
    mantém só letras e algarismos. Ficou mais simples, sem nenhuma expressão
    regular.
  - Testes: 60 casos, dos quais 11 falharam na asserção antes do ajuste no
    código.

  O spec-adversary sobre a 1.8 e o revisor da T-003 (revisão 3) estão rodando em
  segundo plano. Quando os dois terminarem, trago o resumo final e os commits
  propostos.

✻ Worked for 2m 55s · done 10:58 PM

› Message from revisor-de-task
  # Revisão T-003 — Normalização de texto: `normalizar_texto()` com os passos da
  seção 5 da spec (DT-004)

  - **Data:** 2026-10-01
  - **Regras conferidas:** seção 5 da spec (normalização, passos 1 a 3,
  parágrafo do texto vazio e exemplos), AMB-011, D-005 (DECISIONS.md), DT-004
  (plan.md). RN-002, RN-006 e RN-007 só nos trechos que usam a normalização.
  - **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 70 passed, 0
  failed (evidência, não veredito)

  ### Resultado
  **APROVADO COM RESSALVAS**: todos os critérios de aceite estão atendidos, e o
  código segue a seção 5 da versão 1.8 e a D-005. Faltam testes para dois
  trechos explícitos do passo 3: "letras de qualquer alfabeto" e "algarismos
  **decimais**".

  ### Critérios de aceite
  | # | Critério | Status | Evidência |
  |---|---|---|---|
  | 1 | `"Transporte Urbano"`, `"transporte-urbano"`, `" TRANSPORTE__urbano "`,
  `"Transporte – Urbano"` → `transporte_urbano` | atendido |
  `tests/test_normalizacao.py::test_secao5_exemplos_transporte_urbano`. Conferi
  que U+2013 está no arquivo. |
  | 2 | `"Pão  Quente"`, `"pao-quente"` → `pao_quente` | atendido |
  `test_secao5_exemplos_pao_quente` |
  | 3 | `"-Bistro"`, `"_Bistro"`, `"Bistro -"`, `" -_Bistro"` → `bistro` |
  atendido | `test_secao5_hifen_e_sublinhado_nas_pontas_sao_removidos` |
  | 4 | `"Padaria (Centro)"` → `padaria_centro`; `"McDonald's"` → `mcdonald_s`;
  `"Straße"` → `strasse`; `"Smørrebrød"` → `smørrebrød`; `"-"` → vazio |
  atendido | `test_secao5_demais_exemplos_da_spec`,
  `test_secao5_pontuacao_interna_distingue_mcdonalds`,
  `test_secao5_letra_sem_decomposicao_canonica_fica_como_esta` |
  | 5 | Acento pré-composto e combinante dão o mesmo resultado | atendido |
  `test_secao5_acento_precomposto_e_combinante_dao_o_mesmo_resultado`. Conferi
  que U+0327 e U+0303 estão no arquivo, e o teste confirma que as duas strings
  de entrada são diferentes. |
  | 6 | `ç`, `ô`, `ü`, `ñ` | atendido |
  `test_secao5_diacriticos_da_spec_viram_letra_base` |
  | 7 | Sinal combinante solto (no início, sobre hífen no fim) é descartado |
  atendido | `test_secao5_sinal_combinante_solto_e_descartado`. Conferi U+0301 e
  U+FE0F no arquivo. |
  | 8 | Tabulação, quebra de linha, espaço não separável, espaço de largura zero
  e caractere de controle nas pontas | atendido |
  `test_secao5_separador_de_qualquer_tipo_nas_pontas_e_removido`. Conferi
  U+00A0, U+200B, U+FEFF, `\x1c` e `\x00`. |
  | 9 | Mistura de separadores internos de qualquer tipo vira um `_` | atendido
  | `test_secao5_mistura_de_separadores_internos_vira_um_sublinhado`,
  `test_secao5_sequencias_internas_separadas_viram_um_sublinhado_cada` |
  | 10 | Algarismos são mantidos | atendido |
  `test_secao5_algarismos_sao_mantidos` |

  Recalculei à mão, a partir da seção 5, o esperado de cada teste. Todos batem
  com a spec. Também conferi o código contra cada passo, em
  `/Users/rafaeltxm/repo/sdd-desafio/src/reembolso/normalizacao.py`:
  - **Passo 1:** `casefold()`, a equivalência completa de caixa.
  - **Passo 2:** `NFD` e descarte de toda categoria `M*`, tenha a marca uma
  letra ou não.
  - **Passo 3:** o que não é `L*` nem `Nd` vira separador, e `"_".join(split())`
  remove as pontas e transforma cada sequência interna em um `_`.

  A ordem dos passos é a da spec. Não encontrei constante, filtro ou
  comportamento sem base na spec ou na D-005. As alterações não commitadas em
  `spec.md`, `plan.md`, `tasks.md` e `DECISIONS.md` correspondem à D-005, que
  esta task motivou: estão no escopo.

  ### Problemas encontrados
  #### 1. Faltam testes para "letras de qualquer alfabeto" e "algarismos
  decimais" — severidade MÉDIA
  - **Regra afetada:** seção 5, passo 3 ("só letras (de qualquer alfabeto) e
  algarismos decimais contam")
  - **Evidência:** todos os testes de `tests/test_normalizacao.py` usam letras
  latinas e algarismos ASCII. Nenhum teste usa uma letra de outro alfabeto (por
  exemplo grego ou cirílico), que precisa ser mantida. Nenhum usa um caractere
  numérico que não é algarismo decimal (`²`, `½`, `Ⅻ`), que pela spec é
  separador. Nenhum usa um algarismo decimal não ASCII (`٣`), que pela spec é
  mantido.
  - **Impacto:** a suíte atual não distingue o código de uma implementação
  errada. Uma versão com `str.isalnum()` manteria `²` e `½`, que a spec manda
  tratar como separador, e passaria em todos os testes. Uma versão restrita a
  `[a-z0-9]` descartaria letras não latinas, e só seria pega pelos casos
  `ø`/`ł`/`đ`.
  - **Recomendação:** acrescentar casos com o resultado tirado direto do passo
  3:
    - uma letra não latina é mantida;
    - `"Loja²"` e `"Loja½"` tratam `²` e `½` como separador nas pontas, e o
  resultado é `loja`;
    - um algarismo decimal não ASCII é mantido.

  #### 2. Teste que passaria com a função identidade — severidade BAIXA
  - **Regra afetada:** seção 5
  - **Evidência:** `test_secao5_texto_ja_normalizado_fica_igual` e o primeiro
  `assert` de `test_secao5_letra_sem_decomposicao_canonica_fica_como_esta`
  (`"ø"` → `"ø"`) passariam com `normalizar_texto = lambda t: t`.
  - **Impacto:** nenhum, porque outros testes do arquivo pegam essa
  implementação errada. Isoladamente, porém, esses dois testes não verificam
  nada.
  - **Recomendação:** opcional. O segundo `assert` do teste de `ø`
  (`"Smørrebrød"` ≠ `"Smorrebrod"`) já dá a esse teste um valor real.

  ### Cobertura
  - **Regras testadas:**
    - Seção 5, passo 1: `Straße`, maiúsculas nos exemplos.
    - Seção 5, passo 2: diacríticos, pré-composto × combinante, sinal solto,
  letras sem decomposição.
    - Seção 5, passo 3: pontas, separadores internos, pontuação, algarismos
  ASCII.
    - Texto vazio: `test_secao5_texto_so_de_separadores_fica_vazio`. A recusa
  por `entrada_invalida` é da T-009, como deve ser.
    - AMB-011: os exemplos de categoria.
  - **Casos de borda cobertos:** todos os exemplos literais da seção 5; `""` e o
  sinal combinante sozinho → vazio; seletor de variação; BOM; `\x00`; `\r\n`;
  travessões U+2013 e U+2014; NBSP interno. A T-003 não tem linhas próprias na
  tabela da seção 7.
  - **Casos que parecem faltar:**
    - letra de alfabeto não latino é mantida (seção 5, passo 3, "de qualquer
  alfabeto");
    - caractere numérico que não é decimal (`²`, `½`) é separador (seção 5,
  passo 3, "algarismos decimais");
    - algarismo decimal não ASCII é mantido (seção 5, passo 3).

  ### Decisões necessárias
  Nenhuma.

  ### Antes de concluir a task
  Nenhum item bloqueia o commit. É recomendável acrescentar os casos de teste do
  problema 1 antes, para cobrir o passo 3 por completo.

⏺ Bash(cat >> docs/reviews/T-003.md <<'EOF'…)
  ⎿  77 passed in 0.04s
     All checks passed!
  ⎿  Updated docs/reviews/T-003.md (+69 -0)
      138  
      139  ### Antes de concluir a task
      140  Nada — pode seguir para o commit.
      141 +                                                              
      142 +---                                                           
      143 +                                                              
      144 +## Revisão 3                                                  
      145 +                                                              
      146 +# Revisão T-003 — Normalização de texto: `normalizar_texto()` 
          +com os passos da seção 5 da spec (DT-004)                     
      147 +                                                              
      148 +- **Data:** 2026-10-01                                        
      149 +- **Regras conferidas:** seção 5 da spec (normalização, passos
          + 1 a 3, parágrafo do texto vazio e exemplos), AMB-011, D-005 (
          +DECISIONS.md), DT-004 (plan.md). RN-002, RN-006 e RN-007 só no
          +s trechos que usam a normalização.                            
      150 +- **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` →
          + 70 passed, 0 failed (evidência, não veredito)                
      151 +                                                              
      152 +### Resultado                                                 
      153 +**APROVADO COM RESSALVAS**: todos os critérios de aceite estão
          + atendidos, e o código segue a seção 5 da versão 1.8 e a D-005
          +. Faltam testes para dois trechos explícitos do passo 3: "letr
          +as de qualquer alfabeto" e "algarismos **decimais**".         
      154 +                                                              
      155 +### Critérios de aceite                                       
      156 +| # | Critério | Status | Evidência |                         
      157 +|---|---|---|---|                                             
      158 +| 1 | `"Transporte Urbano"`, `"transporte-urbano"`, `" TRANSPO
          +RTE__urbano "`, `"Transporte – Urbano"` → `transporte_urbano` 
          +| atendido | `tests/test_normalizacao.py::test_secao5_exemplos
          +_transporte_urbano`. Conferi que U+2013 está no arquivo. |    
      159 +| 2 | `"Pão  Quente"`, `"pao-quente"` → `pao_quente` | atendid
          +o | `test_secao5_exemplos_pao_quente` |                       
      160 +| 3 | `"-Bistro"`, `"_Bistro"`, `"Bistro -"`, `" -_Bistro"` → 
          +`bistro` | atendido | `test_secao5_hifen_e_sublinhado_nas_pont
          +as_sao_removidos` |                                           
      161 +| 4 | `"Padaria (Centro)"` → `padaria_centro`; `"McDonald's"` 
          +→ `mcdonald_s`; `"Straße"` → `strasse`; `"Smørrebrød"` → `smør
          +rebrød`; `"-"` → vazio | atendido | `test_secao5_demais_exempl
          +os_da_spec`, `test_secao5_pontuacao_interna_distingue_mcdonald
          +s`, `test_secao5_letra_sem_decomposicao_canonica_fica_como_est
          +a` |                                                          
      162 +| 5 | Acento pré-composto e combinante dão o mesmo resultado |
          + atendido | `test_secao5_acento_precomposto_e_combinante_dao_o
          +_mesmo_resultado`. Conferi que U+0327 e U+0303 estão no arquiv
          +o, e o teste confirma que as duas strings de entrada são difer
          +entes. |                                                      
      163 +| 6 | `ç`, `ô`, `ü`, `ñ` | atendido | `test_secao5_diacriticos
          +_da_spec_viram_letra_base` |                                  
      164 +| 7 | Sinal combinante solto (no início, sobre hífen no fim) é
          + descartado | atendido | `test_secao5_sinal_combinante_solto_e
          +_descartado`. Conferi U+0301 e U+FE0F no arquivo. |           
      165 +| 8 | Tabulação, quebra de linha, espaço não separável, espaço
          + de largura zero e caractere de controle nas pontas | atendido
          + | `test_secao5_separador_de_qualquer_tipo_nas_pontas_e_removi
          +do`. Conferi U+00A0, U+200B, U+FEFF, `\x1c` e `\x00`. |       
      166 +| 9 | Mistura de separadores internos de qualquer tipo vira um
          + `_` | atendido | `test_secao5_mistura_de_separadores_internos
          +_vira_um_sublinhado`, `test_secao5_sequencias_internas_separad
          +as_viram_um_sublinhado_cada` |                                
      167 +| 10 | Algarismos são mantidos | atendido | `test_secao5_algar
          +ismos_sao_mantidos` |                                         
      168 +                                                              
      169 +Recalculei à mão, a partir da seção 5, o esperado de cada test
          +e. Todos batem com a spec. Também conferi o código contra cada
          + passo, em `/Users/rafaeltxm/repo/sdd-desafio/src/reembolso/no
          +rmalizacao.py`:                                               
      170 +- **Passo 1:** `casefold()`, a equivalência completa de caixa.
      171 +- **Passo 2:** `NFD` e descarte de toda categoria `M*`, tenha 
          +a marca uma letra ou não.                                     
      172 +- **Passo 3:** o que não é `L*` nem `Nd` vira separador, e `"_
          +".join(split())` remove as pontas e transforma cada sequência 
          +interna em um `_`.                                            
      173 +                                                              
      174 +A ordem dos passos é a da spec. Não encontrei constante, filtr
          +o ou comportamento sem base na spec ou na D-005. As alterações
          + não commitadas em `spec.md`, `plan.md`, `tasks.md` e `DECISIO
          +NS.md` correspondem à D-005, que esta task motivou: estão no e
          +scopo.                                                        
      175 +                                                              
      176 +### Problemas encontrados                                     
      177 +#### 1. Faltam testes para "letras de qualquer alfabeto" e "al
          +garismos decimais" — severidade MÉDIA                         
     … 32 more lines (ctrl+o to expand)
  ⎿  Updated tests/test_normalizacao.py (+23 -0)
      162      assert normalizar_texto("Loja 1") == "loja_1"
      163  
      164  
      165 +@pytest.mark.parametrize(                                     
      166 +    ("texto", "esperado"),                                    
      167 +    [                                                         
      168 +        ("Café Ωμέγα", "cafe_ωμεγα"),  # grego: caixa e acento
          + tirados, letras ficam                                        
      169 +        ("Кафе Москва", "кафе_москва"),  # cirílico           
      170 +        ("Loja ٣", "loja_٣"),  # ٣: algarismo decimal árabe-ín
          +dico                                                          
      171 +    ],                                                        
      172 +)                                                             
      173 +def test_secao5_letras_de_qualquer_alfabeto_e_algarismos_decim
          +ais_contam(                                                   
      174 +    texto, esperado                                           
      175 +):                                                            
      176 +    """Seção 5 passo 3: "só letras (de qualquer alfabeto) e al
          +garismos decimais                                             
      177 +    contam" — letra não latina e algarismo decimal não ASCII s
          +ão mantidos."""                                               
      178 +    assert normalizar_texto(texto) == esperado                
      179 +                                                              
      180 +                                                              
      181 +@pytest.mark.parametrize("texto", ["Loja²", "Loja½", "Loja Ⅻ",
          + "² Loja"])                                                   
      182 +def test_secao5_numero_que_nao_e_algarismo_decimal_e_separador
          +(texto):                                                      
      183 +    """Seção 5 passo 3: `²`, `½` e `Ⅻ` não são algarismos deci
          +mais → separadores                                            
      184 +    (nas pontas, removidos)."""                               
      185 +    assert normalizar_texto(texto) == "loja"                  
      186 +                                                              
      187 +                                                              
      188  @pytest.mark.parametrize("texto", ["-", "***", " - ", "_", "",
            "́"])
      189  def test_secao5_texto_so_de_separadores_fica_vazio(texto):
      190      """Seção 5 (D-005): texto só de separadores normaliza para
            vazio (a recusa como

⏺ Agent "Revisar task T-003 (revisão 3)" finished · 1m 17s

⏺ A revisão 3 da T-003 voltou APROVADO COM RESSALVAS, sem nenhuma decisão
  pendente. Salvei o relatório sem edição em docs/reviews/T-003.md.

  A ressalva média era a falta de testes para duas partes do passo 3: "letras de
  qualquer alfabeto" e "algarismos decimais". Acrescentei 7 casos:
  - grego e cirílico mantidos;
  - ٣ (algarismo árabe-índico) mantido;
  - ², ½ e Ⅻ tratados como separadores.

  Eles passaram de primeira, porque o código já fazia o certo. O valor deles é
  pegar uma implementação errada: uma versão com str.isalnum() manteria ² e ½, e
  o teste falharia. A suíte tem 77 testes passando e o ruff está limpo.

  Ainda não fiz nenhum commit. Falta a rodada do spec-adversary sobre a 1.8, que
  continua rodando em segundo plano.

✻ Brewed for 32s · done 10:59 PM

› Message from spec-adversary
  Resumo: 5 problemas, 2 bloqueantes.

  Arquivos lidos:
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md` (1.8),
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md`
  (D-005), `/Users/rafaeltxm/repo/sdd-desafio/exemplos/despesas-exemplo.json`.
  Não li `src/` nem `tests/`.

  ### 1. O que conta como "letra", "algarismo decimal" e "sinal combinante" não
  está definido — BLOQUEANTE — ambiguidade

  - **Regra afetada:** seção 5, passos 2 e 3; RN-002 (texto normalizado vazio);
  RN-006; RN-007; AMB-011.
  - **Cenário de entrada:** duas alimentações em 03/07, 40,00, com nota, uma com
  fornecedor `"Padaria Nº 1"` (U+00BA, indicador ordinal) e outra com `"Padaria
  N° 1"` (U+00B0, sinal de grau). As duas aparecem iguais em teclado de
  celular.
  - **Comportamento pela interpretação atual:** indefinido. Se `º` conta como
  letra (no Unicode ele é classificado como "outra letra"), o resultado é
  `padaria_nº_1` × `padaria_n_1`: não são duplicatas, as duas são pagas e o
  limite fica com 60,00 (40,00 + 20,00). Se `º` é símbolo (como um leitor em
  português o veria), as duas viram `padaria_n_1`: a segunda é `duplicata` e o
  dia paga só 40,00. O mesmo vale para `ª` (`"Lanchonete 1ª"`) e para a letra
  modificadora `ʼ` (U+02BC) × o apóstrofo `’` (U+2019) em `"McDonaldʼs"`.
  Variações do mesmo ponto:
    - "Algarismo decimal": não se sabe se `١` (arábico) e `１` (largura total)
  contam e, se contam, se valem `1`. Também não se sabe se `²` é algarismo:
  `"Loja²"` daria `loja` ou `loja2`.
    - "Sinal combinante": não se sabe se são só os sinais sem espaço próprio ou
  também os de espaço próprio e os envolventes. Ex.: U+20E3 no emoji de tecla
  `1️⃣`; sinais vocálicos de escritas indianas. Pela primeira leitura, os outros
  sinais não são letra e viram separador; pela segunda, são descartados. Muda
  `"loja_1_centro"` × `"loja_1centro"` em `"Loja 1⃣Centro"`.
    - U+0345 (subscrito grego): a equivalência de caixa do passo 1 o transforma
  na letra `ι` antes do passo 2, mas o passo 2 diz que "todo sinal combinante é
  descartado". Raro, mas são duas leituras.
  - **Por que é uma brecha/problema:** "só letras e algarismos contam" virou a
  regra central da normalização. A D-005 diz que "qualquer pessoa consegue
  conferir", mas sem saber quais caracteres entram em cada conjunto ninguém
  consegue conferir os casos acima, e o teste da T-003 teria de escolher uma das
  leituras. É o mesmo tipo de conjunto aberto que bloqueou a 1.7, agora em
  outros termos.
  - **Pergunta para decisão:** quais caracteres são "letra", quais são
  "algarismo decimal" e quais são "sinal combinante" para a seção 5? Em
  particular, como ficam `º`/`ª`, letras modificadoras, algarismos de outras
  escritas, sobrescritos e sinais com espaço próprio ou envolventes? E a ordem
  caixa → acentos vale também para U+0345?

  ### 2. "Espaço em branco" continua sem definição para `id` e
  `colaborador.id`/`nome` — BLOQUEANTE — lacuna

  - **Regra afetada:** RN-002 (despesa inválida: `id` "vazio ou só com espaços
  em branco"; erro de arquivo: `colaborador.id`/`nome` idem); seção 7, linha
  "Colaborador com texto vazio".
  - **Cenário de entrada:** (a) alimentação válida de 40,00 com `"id": ""`
  (espaço de largura zero); (b) `"colaborador": {"id": "c-1", "nome": "\u001f"}`
  ou `""` (BOM).
  - **Comportamento pela interpretação atual:** indefinido. Em (a), a despesa é
  `entrada_invalida` (0,00 e fora dos totais) ou é aprovada com 40,00. Em (b),
  há erro de arquivo (sem saída, código diferente de 0) ou processamento normal.
  Pela propriedade de espaço em branco do Unicode, U+200B, U+FEFF e U+001F não
  são espaço; por outras definitions usuais, U+001C a U+001F são.
  - **Por que é uma brecha/problema:** a 1.8 fechou o conjunto para `categoria`
  e `fornecedor`, que agora usam o texto normalizado vazio, mas `id` e
  `colaborador` continuam com a expressão "só com espaços em branco". Essa
  expressão era justamente o conjunto aberto apontado como bloqueante na 1.7. O
  resultado (recusar, ou erro de arquivo, contra processar normalmente) depende
  de qual conjunto o código escolher. Há também uma assimetria nova: `id` `"-"`
  é válido, enquanto `fornecedor` `"-"` é inválido. Pode ser intencional, mas a
  spec não diz.
  - **Pergunta para decisão:** para `despesas[].id`, `colaborador.id` e
  `colaborador.nome`, quais caracteres contam como "espaço em branco"
  (invisíveis, BOM, caracteres de controle)? O critério deve ou não ser o mesmo
  da seção 5 usado para `categoria`/`fornecedor`?

  ### 3. Fornecedor visualmente idêntico escapa da RN-007, e o risco aceito não
  descreve esse caso — PODE ESPERAR — brecha

  - **Regra afetada:** RN-007; seção 5, passos 2 e 3; seção 10 (riscos
  "Caractere invisível no meio da palavra" e "Quase-duplicatas").
  - **Cenário de entrada:** duas alimentações em 09/07, 54,90, com nota.
  Fornecedores `"Bistro Central"` e `"Bistro Central"` (hífen suave, comum em
  texto copiado de PDF ou da web), ou `"Bistro Central"`, ou `"Bistrо Central"`
  com `о` cirílico.
  - **Comportamento pela interpretação atual:** definido. O caractere invisível
  é separador (`bistro_cen_tral`) e o `о` cirílico é letra distinta, então não
  são duplicatas. As duas despesas passam e o dia paga 60,00 em vez de 54,90.
  Num dia em viagem, pagaria 90,00 em vez de 54,90.
  - **Por que é uma brecha/problema:** a seção 10 aceita o risco do invisível só
  para a categoria, com a justificativa de que "o conferente vê a categoria
  como veio". Para o fornecedor essa mitigação não existe: `fornecedor` nem
  aparece na saída (seção 4). A duplicata visualmente idêntica passa sem nenhum
  sinal para o conferente. O risco "Quase-duplicatas" fala de "outra grafia",
  não de texto que parece idêntico. É o mesmo tipo de justificativa incompleta
  corrigido no ponto 2 da D-002.
  - **Pergunta para decisão:** o risco de duplicatas com fornecedor visualmente
  idêntico (caractere invisível ou letra de outro alfabeto parecida) está
  aceito? Se sim, a descrição da seção 10 deve cobrir o fornecedor, que não
  aparece na saída?

  ### 4. Formas de compatibilidade tratadas de modo desigual — PODE ESPERAR —
  ambiguidade

  - **Regra afetada:** seção 5, passos 1 e 2; RN-006.
  - **Cenário de entrada:** alimentação válida com `"categoria":
  "ＡＬＩＭＥＮＴＡＣＡＯ"` (largura total, comum em entrada de teclado
  asiático), e fornecedores `"ﬁlial"` (ligadura U+FB01) × `"filial"`.
  - **Comportamento pela interpretação atual:** lido ao pé da letra, a
  equivalência completa de caixa transforma `ﬁ` em `fi`, então `"ﬁlial"` =
  `"filial"`. Já `Ａ` só tem decomposição de compatibilidade, que o passo 2 não
  aplica: fica como letra distinta, e a categoria em largura total sai
  `categoria_fora_da_politica`. Uma leitura menos literal de "qualquer que seja
  a forma como o caractere foi codificado" (passo 2) aceitaria as duas.
  - **Por que é uma brecha/problema:** a frase do passo 2 sugere que a
  codificação não importa, mas a regra só cobre a decomposição canônica. Uma
  categoria que qualquer pessoa reconheceria é recusada, e a seção 10 não
  registra isso como risco (só registra `ø`/`ł`/`đ`). Afeta casos improváveis em
  dados em português.
  - **Pergunta para decisão:** letras e algarismos em formas de compatibilidade
  (largura total, sobrescritos, ligaduras não cobertas pela caixa) devem
  continuar distintos da forma comum? Se sim, isso entra como risco aceito na
  seção 10?

  ### 5. Comportamentos novos fora da seção 7 e afirmação imprecisa na D-005 —
  PODE ESPERAR — lacuna

  - **Regra afetada:** seção 7; seção 9 ("cada caso de borda da seção 7 tem um
  teste"); RN-006 (aceite); D-005 ("O que isso invalidou").
  - **Cenário de entrada:** `"-Bistro"` × `"_Bistro"` (o gatilho da D-005);
  `"Transporte – Urbano"` (travessão); `"Padaria (Centro)"` × `"Padaria
  Centro"`; `"Straße"`; `"Smørrebrød"` × `"Smorrebrod"`; `"alimentacao-́"` (sinal
  solto); `"alimentacao"`; `categoria` `"-"`.
  - **Comportamento pela interpretação atual:** esses resultados aparecem só nos
  exemplos da seção 5 e nos riscos da seção 10. A seção 7 não tem linha para
  eles: a linha "Categoria com separador diferente" só cobre espaço e hífen, e a
  linha "Texto vazio" só cobre `fornecedor`. Pelo critério da seção 9, nenhum
  deles precisa de teste. Além disso, a D-005 afirma que "nenhuma categoria ou
  fornecedor do arquivo tem caractere fora de letras, algarismos e espaço
  simples", mas `"transporte_urbano"` (d-003, d-004, d-009) tem sublinhado. O
  valor não muda, porque o sublinhado interno vira `_`, mas a afirmação está
  errada.
  - **Por que é uma brecha/problema:** os casos que motivaram a mudança podem
  ficar sem teste obrigatório, e o registro da decisão traz uma justificativa
  factualmente errada. Não muda valores.
  - **Pergunta para decisão:** os comportamentos novos da seção 5 devem virar
  linhas da seção 7, entrando assim no critério de aceite da seção 9? E a frase
  da D-005 sobre o exemplo deve ser corrigida?

  ---

  1. **Decidir antes da implementação:** 1, 2.
  2. **Pode ser decidido depois:** 3, 4, 5.

⏺ O spec-adversary encontrou 5 problemas na spec 1.8, e 2 bloqueiam o commit.
  Ainda não fiz nenhum commit. A revisão 3 da T-003 tinha aprovado com ressalvas
  e eu já acrescentei os testes que ela pediu: são 77 passando e o ruff está
  limpo.

  Cada rodada encontra um canto novo do Unicode. Para encerrar, a saída é
  definir os conjuntos pela classificação oficial do Unicode, que cobre todos os
  caracteres e não deixa sobra. É o que o código já faz.

  Bloqueantes

  1. O que conta como "letra", "algarismo" e "sinal". O exemplo do revisor:
  "Padaria Nº 1" (com º) e "Padaria N° 1" (com o sinal de grau °) são iguais ou
  não?

  Recomendo escrever na seção 5 as categorias do Unicode:
  - Letra é qualquer caractere da categoria "letra". Isso inclui º, ª e ʼ, então
    nº ≠ n°.
  - Algarismo decimal é a categoria "dígito decimal", mantido como está. ١
    continua ١ e não vira 1. ² não é algarismo decimal.
  - Sinal combinante é qualquer caractere da categoria "marca": com ou sem
    espaço próprio, e os envolventes.
  - A ordem caixa → acentos vale para tudo, inclusive o U+0345.

  O código e os testes atuais já seguem essas definições. A spec só passa a
  dizer isso explicitamente.

  2. "Espaço em branco" no id e no colaborador. Isso é escopo da T-008 e da
  T-009, mas a definição entra na spec agora. Recomendo:
  - "Espaço em branco" vale pela propriedade White_Space do Unicode. O espaço de
    largura zero, o BOM e os caracteres de controle não contam como espaço,
    então "id": "" é um id válido.
  - id "-" continua válido. O id só é repetido na saída, nunca comparado, então
    não precisa da normalização.

  Problemas que podem esperar

  3. Fornecedor visualmente idêntico (com hífen suave, caractere invisível ou о
     cirílico) escapa da detecção de duplicata. Recomendo aceitar e corrigir a
     descrição do risco na seção 10: hoje ela fala só da categoria, e o
     fornecedor nem aparece na saída.
  4. Largura total (ＡＬＩＭ…) e sobrescritos continuam diferentes da forma 
     comum. Recomendo registrar como risco aceito.
  5. Afirmação errada na D-005 e casos fora da seção 7.
     - A D-005 diz que nenhum dado do exemplo tem caractere fora de letras,
       algarismos e espaço, mas transporte_urbano tem sublinhado. O valor não
       muda. Recomendo corrigir a frase.
     - Recomendo não criar linhas novas na seção 7. Os exemplos da seção 5 já
       têm teste na T-003, e mexer na contagem de 63 casos afeta a distribuição
       entre as tasks.

  Se você aprovar o pacote, aplico tudo na própria 1.8, que ainda não foi
  commitada. Depois rodo o spec-adversary uma última vez, só para confirmar que
  os bloqueantes fecharam. Se ele trouxer outro canto do Unicode que não muda
  nenhum valor em dados realistas, proponho registrar como risco e encerrar.

  Aprova?

✻ Cooked for 19s · done 11:01 PM

⏺ Agent "Revisão adversarial spec 1.8" finished · 2m 37s

❯ pode seguir                                                                   

  Searched for 1 pattern (ctrl+o to expand)

⏺ Bash(python3 - <<'PYEOF'
      import pathlib…)
  ⎿  15:**Gatilho:** revisão independente da T-003 (`docs/reviews/T-003.md`
     , revisão 1, BLOQUEADO). O passo 4 da seção 5 só tratava sequências **
     internas** de separadores e o passo 1 só removia espaço em branco das
     … +14 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/DECISIONS.md (+9 -4)
      12  
      13  ## D-005 — Normalização: só letras e algarismos contam: spec 1.
          6 → 1.8 · `2026-10-01`
      14  
      15 -**Gatilho:** revisão independente da T-003 (`docs/reviews/T-003
         -.md`, revisão 1, BLOQUEADO). O passo 4 da seção 5 só tratava se
         -quências **internas** de separadores e o passo 1 só removia esp
         -aço em branco das pontas: hífen ou sublinhado no início ou no f
         -im não tinham resultado definido (`"-Bistro"` × `"_Bistro"` mud
         -am a RN-007). O passo 3 não dizia se `ø`, `ł`, `đ` contam como 
         -letra com sinal. O responsável decidiu os dois pontos (versão 1
         -.7, não commitada). A rodada do `spec-adversary` sobre a 1.7 ap
         -ontou 5 problemas (1 bloqueante): o conjunto de "hífens" e de "
         -espaços em branco" não estava fechado (travessão U+2013 colocad
         -o pelo editor, espaço de largura zero, BOM, caracteres de contr
         -ole). O responsável optou por trocar as listas por uma regra ún
         -ica, "só letras e algarismos contam" (versão 1.8). Sessão `docs
         -/sessions/13-*`.                                               
      15 +**Gatilho:** revisão independente da T-003 (`docs/reviews/T-003
         +.md`, revisão 1, BLOQUEADO). O passo 4 da seção 5 só tratava se
         +quências **internas** de separadores e o passo 1 só removia esp
         +aço em branco das pontas: hífen ou sublinhado no início ou no f
         +im não tinham resultado definido (`"-Bistro"` × `"_Bistro"` mud
         +am a RN-007). O passo 3 não dizia se `ø`, `ł`, `đ` contam como 
         +letra com sinal. O responsável decidiu os dois pontos (versão 1
         +.7, não commitada). A rodada do `spec-adversary` sobre a 1.7 ap
         +ontou 5 problemas (1 bloqueante): o conjunto de "hífens" e de "
         +espaços em branco" não estava fechado (travessão U+2013 colocad
         +o pelo editor, espaço de largura zero, BOM, caracteres de contr
         +ole). O responsável optou por trocar as listas por uma regra ún
         +ica, "só letras e algarismos contam". A rodada do `spec-adversa
         +ry` sobre essa versão apontou 5 problemas (2 bloqueantes): "let
         +ra", "algarismo decimal" e "sinal combinante" sem conjunto defi
         +nido (`Nº` × `N°`), e "espaço em branco" ainda aberto para `id`
         + e `colaborador`. O responsável aceitou as 5 recomendações (pon
         +tos 8 a 12), aplicadas na mesma versão 1.8. Sessão `docs/sessio
         +ns/13-*`.                                                      
      16  
      17  **O que mudou na spec:**
      18  
     ...
      25  | 5 | Equivalência de caixa | "ignorar maiúsculas/minúsculas", 
          sem dizer qual | equivalência completa de caixa do Unicode (`ß`
           = `ss`) | seção 5 (passo 1) |
      26  | 6 | `categoria` ou `fornecedor` só de separadores (`"-"`, `"*
          **"`) | válido; normalizava para vazio e todos os fornecedores 
          "vazios" eram iguais na RN-007 | `entrada_invalida`, como o tex
          to só com espaços | RN-002 (regra e aceite), seção 5, seção 7 (
          linha "Texto vazio em campo obrigatório") |
      27  | 7 | Caractere invisível no meio da palavra | — | é separador 
          (`ali_mentacao`); risco aceito | seção 10 |
      28 +| 8 | Conjuntos de "letra", "algarismo decimal" e "sinal combin
         +ante" | indefinidos (`Nº` × `N°`, `²`, `١`, sinais com espaço p
         +róprio) | categorias Unicode "letra" (inclui `º`, `ª`, `ʼ`), "d
         +ígito decimal" (mantido como está) e "marca" (todas as três sub
         +categorias); o passo 2 trata o resultado do passo 1 | seção 5 |
      29 +| 9 | "Espaço em branco" em `id`, `colaborador.id` e `nome` | i
         +ndefinido (BOM, espaço de largura zero, U+001C a U+001F) | prop
         +riedade White_Space do Unicode; os demais não são espaço; `id` 
         +e `nome` não são normalizados (`id` `"-"` é válido) | RN-002 | 
      30 +| 10 | Fornecedor visualmente idêntico (invisível, letra de out
         +ro alfabeto) | risco descrito só para a categoria | risco aceit
         +o descrito também para o fornecedor, que não aparece na saída |
         + seção 10 |                                                    
      31 +| 11 | Formas de compatibilidade (largura total, sobrescritos) 
         +| indefinido | distintas da forma comum; risco aceito | seção 1
         +0 |                                                            
      32 +| 12 | Comportamentos novos fora da seção 7 | — | **mantido**: 
         +exemplos da seção 5 testados na T-003; seção 7 não muda (contag
         +em de 63 casos preservada) | — |                               
      33  
      34  **Por quê:** os pontos 1 e 3 seguem a lógica da AMB-011: separa
          dor e sinal solto são diferença de grafia, não de significado (
          `"alimentacao-"` e `"Transporte – Urbano"` passam a ser reconhe
          cidas). Uma regra única ("só letras e algarismos") fecha o conj
          unto sem lista de caracteres, que seria incompleta por construç
          ão, e qualquer pessoa consegue conferir. O efeito colateral (ma
          is fornecedores iguais, como `"Padaria (Centro)"` = `"Padaria C
          entro"`) só pesa na RN-007, que também exige mesma data, catego
          ria e valor ao centavo. O ponto 6 vem junto: sem ele, `"-"` e `
          "?"` viram o mesmo fornecedor e se anulam como duplicatas, enqu
          anto `"   "` já era recusado. O ponto 2 evita tabela manual (al
          ternativa já descartada no DT-004). O ponto 5 registra o compor
          tamento escolhido; raro em dados em português.
      35  
      31 -**O que isso invalidou:** o DT-004 do `plan.md` (lista fixa de 
         -separadores, só `Mn` removido); alinhado na versão 1.1 do plano
         -. Código da T-003 ainda não commitado, ajustado antes do commit
         -. Aceite da T-009 ganha o texto que normaliza para vazio. Nenhu
         -m valor do exemplo (seção 9) mudou: nenhuma categoria ou fornec
         -edor do arquivo tem caractere fora de letras, algarismos e espa
         -ço simples.                                                    
      36 +**O que isso invalidou:** o DT-004 do `plan.md` (lista fixa de 
         +separadores, só `Mn` removido); alinhado na versão 1.1 do plano
         +. Código da T-003 ainda não commitado, ajustado antes do commit
         +. Aceite da T-009 ganha o texto que normaliza para vazio. Nenhu
         +m valor do exemplo (seção 9) mudou: as categorias e fornecedore
         +s do arquivo só têm letras ASCII, espaço simples e, em `transpo
         +rte_urbano`, sublinhado interno, que continua valendo `_`.     
      37  
      33 -**Tasks afetadas:** T-003 (aceite com separadores de qualquer t
         -ipo, sinal solto, `ø`, `ß`), T-009 (aceite com texto normalizad
         -o vazio).                                                      
      38 +**Tasks afetadas:** T-003 (aceite com separadores de qualquer t
         +ipo, sinal solto, `ø`, `ß`, `º`, `²`), T-008 e T-009 (espaço em
         + branco pela propriedade White_Space; texto normalizado vazio).
      39  
      35 -**Custo:** 4 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`, `t
         -asks.md`); 7 pontos decididos na mesma sessão. Uma rodada do `s
         -pec-adversary` (sobre a 1.7); rodada sobre a 1.8 antes do commi
         -t.                                                             
      40 +**Custo:** 4 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`, `t
         +asks.md`); 12 pontos decididos na mesma sessão. Três rodadas do
         + `spec-adversary` (sobre a 1.7, sobre a primeira redação da 1.8
         + e de confirmação sobre a 1.8 final).                          
      41  
      42  ---
      43  
  ⎿  Updated specs/001-motor-reembolso/plan.md (+3 -3)
      132  - número = `Decimal` ou `int`, **e não** `bool`;
      133  - booleano = `type(x) is bool`;
      134  - data = casa `^[0-9]{4}-[0-9]{2}-[0-9]{2}$` **e** `date.fromi
           soformat` aceita (rejeita 2026-02-30);
      135 -- texto obrigatório = `str` com `strip()` não vazio (o `strip(
          -)` sem argumento remove todo espaço em branco Unicode, inclusi
          -ve o não separável).                                          
      135 +- texto obrigatório = `str` com algum caractere fora do espaço
          + em branco da RN-002 (propriedade White_Space do Unicode). **N
          +ão** usar `strip()`/`isspace()` puros: eles também tratam U+00
          +1C a U+001F como espaço, e a spec diz que não são; usar `c.iss
          +pace() and c not in "\x1c\x1d\x1e\x1f"`.                      
      136  **Alternativa descartada:** `isinstance(x, (int, float))` e `f
           romisoformat` sozinho — aceitariam `"valor": true` e `"data": 
           "20260703"`.
      137  **Consequência:** cada armadilha vira um caso de teste de `ent
           rada.py`.
      138  
      139  ### DT-004 — Normalização de texto com `unicodedata`
      140  
      141  **Contexto:** seção 5 da spec, 3 passos (caixa, acentos, só le
           tras e algarismos), "qualquer que seja a forma como o caracter
           e foi codificado".
      142 -**Decisão:** `casefold()` (equivalência completa de caixa, `ß`
          - → `ss`) → `unicodedata.normalize("NFD")` e remoção de todo ca
          -ractere de categoria `M*` (sinais combinantes, com ou sem letr
          -a) → todo caractere que não é de categoria `L*` (letra) nem `N
          -d` (algarismo decimal) vira espaço → `"_".join(texto.split())`
          - (pontas somem, sequências internas viram um `_`). O NFD decom
          -põe tanto `á` pré-composto (U+00E1) quanto `a` + acento combin
          -ante (U+0301) para a mesma sequência, cobrindo as duas codific
          -ações; letras sem decomposição canônica (`ø`, `ł`) ficam como 
          -estão, como a spec define. Texto que resulta vazio é tratado p
          -ela validação (`entrada.py`, RN-002).                         
      143 -**Alternativa descartada:** tabela manual de acentos (`á→a`, .
          -..): incompleta por construção; `NFKD`: também desfaz compatib
          -ilidades (ligaduras, larguras) que a spec não pede; lista de s
          -eparadores (`[\s\-_]`): deixa travessões, invisíveis e pontuaç
          -ão sem resultado definido (D-005).                            
      142 +**Decisão:** `casefold()` (equivalência completa de caixa, `ß`
          + → `ss`) → `unicodedata.normalize("NFD")` e remoção de todo ca
          +ractere de categoria `M*` (sinais combinantes, com ou sem letr
          +a) → todo caractere que não é de categoria `L*` (letra, inclui
          + `Lm`/`Lo` como `º` e `ʼ`) nem `Nd` (algarismo decimal, sem co
          +nversão para ASCII) vira espaço → `"_".join(texto.split())` (p
          +ontas somem, sequências internas viram um `_`). O NFD decompõe
          + tanto `á` pré-composto (U+00E1) quanto `a` + acento combinant
          +e (U+0301) para a mesma sequência, cobrindo as duas codificaçõ
          +es; letras sem decomposição canônica (`ø`, `ł`) ficam como est
          +ão, como a spec define. Texto que resulta vazio é tratado pela
          + validação (`entrada.py`, RN-002).                            
      143 +**Alternativa descartada:** tabela manual de acentos (`á→a`, .
          +..): incompleta por construção; `NFKD`: também desfaz compatib
          +ilidades (ligaduras, larguras, `²` → `2`) que a spec não pede 
          +(seção 10); lista de separadores (`[\s\-_]`): deixa travessões
          +, invisíveis e pontuação sem resultado definido (D-005).      
      144  **Consequência:** uma função pura, usada por RN-006, RN-007 e 
           pela validação da RN-002, testada com os exemplos da seção 5 e
            os casos de borda de categoria e fornecedor.
      145  
      146  ### DT-005 — Pipeline em duas fases, espelhando a seção 8
  ⎿  Updated specs/001-motor-reembolso/spec.md (+8 -5)
      138  
      139  **Normalização de texto** (usada em RN-006, RN-007 e na valida
           ção de `categoria` e `fornecedor` da RN-002), aplicada nesta o
           rdem:
      140  
      141 -1. ignorar maiúsculas/minúsculas, pela equivalência completa d
          -e caixa do Unicode (inclui `ß` = `ss`);                       
      142 -2. toda letra com acento ou sinal diacrítico é comparada como 
          -a letra base, qualquer que seja a forma como o caractere foi c
          -odificado no arquivo (`á`→`a`, `ç`→`c`, `ô`→`o`, `ü`→`u`, `ñ`→
          -`n`). Os sinais são separados pela decomposição canônica do Un
          -icode e todo sinal combinante é descartado, acompanhe ele uma 
          -letra ou não; letras sem essa decomposição, cujo traço faz par
          -te da própria letra (`ø`, `ł`, `đ`), ficam como estão;        
      143 -3. só letras (de qualquer alfabeto) e algarismos decimais cont
          -am. Todo outro caractere é separador: espaço em branco de qual
          -quer tipo, hífen, travessão, sublinhado, pontuação, símbolo, e
          -moji, caractere invisível ou de controle. Toda sequência de se
          -paradores no início ou no fim é removida, e toda sequência int
          -erna vale como um único `_`.                                  
      141 +1. ignorar maiúsculas/minúsculas, pela equivalência completa d
          +e caixa do Unicode (inclui `ß` = `ss`); o resultado deste pass
          +o é o que os passos seguintes tratam;                         
      142 +2. toda letra com acento ou sinal diacrítico é comparada como 
          +a letra base, qualquer que seja a forma como o caractere foi c
          +odificado no arquivo (`á`→`a`, `ç`→`c`, `ô`→`o`, `ü`→`u`, `ñ`→
          +`n`). Os sinais são separados pela decomposição canônica do Un
          +icode e todo sinal combinante (caractere da categoria Unicode 
          +"marca": sem espaço próprio, com espaço próprio ou envolvente)
          + é descartado, acompanhe ele uma letra ou não; letras sem essa
          + decomposição, cujo traço faz parte da própria letra (`ø`, `ł`
          +, `đ`), ficam como estão;                                     
      143 +3. só letras e algarismos decimais contam. Letra é todo caract
          +ere da categoria Unicode "letra", de qualquer alfabeto, inclus
          +ive `º`, `ª` e letras modificadoras como `ʼ`; algarismo decima
          +l é todo caractere da categoria Unicode "dígito decimal", de q
          +ualquer escrita, mantido como está (`١` não vira `1`). Todo ou
          +tro caractere é separador: espaço em branco de qualquer tipo, 
          +hífen, travessão, sublinhado, pontuação, símbolo (inclusive `°
          +`), número que não é dígito decimal (`²`, `½`), emoji, caracte
          +re invisível ou de controle. Toda sequência de separadores no 
          +início ou no fim é removida, e toda sequência interna vale com
          +o um único `_`.                                               
      144  
      145  Texto cujo resultado fica vazio (só separadores, como `"-"` ou
            `"***"`) não identifica categoria nem fornecedor: a despesa é
            inválida (RN-002).
      146  
      147 -Exemplos: `"Transporte Urbano"`, `"transporte-urbano"`, `" TRA
          -NSPORTE__urbano "` e `"Transporte – Urbano"` (travessão) → `tr
          -ansporte_urbano`; `"Pão  Quente"` e `"pao-quente"` → `pao_quen
          -te`; `"-Bistro"`, `"_Bistro"`, `"Bistro -"` e `" -_Bistro"` → 
          -`bistro`; `"Padaria (Centro)"` → `padaria_centro`; `"McDonald'
          -s"` → `mcdonald_s` (diferente de `mcdonalds`); `"Straße"` → `s
          -trasse`; `"Smørrebrød"` → `smørrebrød` (diferente de `smorrebr
          -od`); `"-"` → vazio.                                          
      147 +Exemplos: `"Transporte Urbano"`, `"transporte-urbano"`, `" TRA
          +NSPORTE__urbano "` e `"Transporte – Urbano"` (travessão) → `tr
          +ansporte_urbano`; `"Pão  Quente"` e `"pao-quente"` → `pao_quen
          +te`; `"-Bistro"`, `"_Bistro"`, `"Bistro -"` e `" -_Bistro"` → 
          +`bistro`; `"Padaria (Centro)"` → `padaria_centro`; `"McDonald'
          +s"` → `mcdonald_s` (diferente de `mcdonalds`); `"Straße"` → `s
          +trasse`; `"Padaria Nº 1"` → `padaria_nº_1` (diferente de `"Pad
          +aria N° 1"` → `padaria_n_1`); `"Loja²"` → `loja`; `"Smørrebrød
          +"` → `smørrebrød` (diferente de `smorrebrod`); `"-"` → vazio. 
      148  
      149  ### RN-001 — Um resultado por despesa
      150  
     ...
      159  - **Despesa inválida** (vira item `recusado` com motivo `entra
           da_invalida`; as demais despesas seguem): elemento de `despesa
           s` que não é um objeto; falta `id`, `data`, `categoria`, `forn
           ecedor`, `valor` ou `tem_nota_fiscal`; `data` não é data válid
           a `AAAA-MM-DD`; `valor` não é número; `tem_nota_fiscal` não é 
           booleano; `id`, `categoria` ou `fornecedor` não são texto, ou 
           são texto vazio ou só com espaços em branco; `categoria` ou `f
           ornecedor` cujo texto normalizado (seção 5) fica vazio, como `
           "-"` ou `"***"`; `valor` com valor absoluto maior ou igual a 1
           .000.000.000,00 (um bilhão), comparado com o número recebido, 
           antes do arredondamento (AMB-018).
      160  - Na saída de uma despesa inválida, `id`, `data` e `categoria`
            são copiados se forem texto e saem nulos caso contrário (tipo
            errado, ausente ou elemento que não é objeto); a `categoria`,
            se reconhecida, sai normalizada, como em qualquer item (seção
            4).
      161  - Uma despesa recusada por `entrada_invalida` tem `valor_consi
           derado` nulo, `em_viagem` e `limite_diario` nulos, e não entra
            nos totais.
      162 +- Espaço em branco, nesta regra e em toda a spec, é o caracter
          +e com a propriedade White_Space do Unicode (espaço comum, tabu
          +lação, quebra de linha, espaço não separável e semelhantes). E
          +spaço de largura zero, BOM e caracteres de controle (como U+00
          +1C a U+001F) não são espaço em branco: um `id` ou `nome` feito
          + só deles é texto válido.                                     
      163 +- `id` (da despesa e do colaborador) e `nome` não passam pela 
          +normalização da seção 5: só são repetidos, nunca comparados. U
          +m `id` `"-"` é válido.                                        
      164  - Campos extras, no arquivo ou nas despesas, são ignorados.
      165  **Origem:** necessidade operacional (a política não trata entr
           ada malformada); pontos 7 e 9 de D-001; AMB-018; D-005.
      166  **Aceite:** despesa sem `tem_nota_fiscal` com `valor` 33.333 →
            `recusado`, `entrada_invalida`, `valor_informado` 33.333, `va
           lor_considerado` nulo, fora de `valor_solicitado`; as demais d
           espesas são processadas normalmente. Elemento `null` em `despe
           sas` → item com `id` e `data` nulos, `entrada_invalida`. Arqui
           vo sem `colaborador` → nenhuma saída, código diferente de 0. H
           ospedagem com campo extra `"noites": 2` → avaliada como uma di
           ária (RN-012). Despesa com `"id": 17` → `entrada_invalida`, `i
           d` nulo na saída. Despesa com `fornecedor` `"   "` → `entrada_
           invalida`. Despesa com `fornecedor` `"-"` → `entrada_invalida`
           . `competencia` 202607 (número) → processamento normal, `compe
           tencia` nula na saída. Caminho de saída em pasta inexistente →
            nenhuma saída, código diferente de 0. Despesa `"categoria": "
           ALIMENTACAO"` sem `tem_nota_fiscal` → `entrada_invalida`, `cat
           egoria` `alimentacao` na saída. `colaborador.nome` `"  "` → er
           ro de arquivo. Erro de arquivo com arquivo de saída preexisten
           te → o arquivo continua com o conteúdo anterior. Chamada sem `
           --output` → código diferente de 0. `valor` 1000000000 → `entra
           da_invalida`, `valor_informado` 1000000000, fora dos totais. `
           valor` -1e12 → `entrada_invalida` (não `valor_invalido`). `val
           or` 999999999.995 → segue, com `valor_considerado` 1000000000.
           00 (o teto vale para o número recebido).
     ...
      547  - **Viagem por hospedagem irrisória com nota declarada** (AMB-
           004): uma hospedagem de 0,01 com `tem_nota_fiscal` verdadeiro 
           põe D e D+1 em viagem e amplia os limites de alimentação e tra
           nsporte em até 70,00 por dia (140,00 nos dois dias). Aceito po
           rque o sistema não verifica notas (seção 3) e qualquer valor m
           ínimo seria regra inventada; a saída expõe `em_viagem` por ite
           m para a conferência humana. Mitigação definitiva: indicação e
           xplícita de viagem na entrada (evolução, seção 3).
      548  - **Caminho ambíguo no aviso de chave repetida** (RN-013): cha
           ves com `.`, `[` ou `]`, vazias ou com quebra de linha aparece
           m no caminho sem escape. Dois caminhos diferentes podem gerar 
           o mesmo texto (`"a.b"` e `a` → `b`), e um campo extra pode ger
           ar aviso idêntico ao de um campo da seção 4 que entra no cálcu
           lo (chave extra `"periodo.inicio"` repetida na raiz produz o m
           esmo aviso que o `periodo.inicio` verdadeiro repetido) ou um t
           exto que imita outro aviso. Nenhum valor muda: o aviso só pode
            enganar o conferente sobre qual chave foi descartada. Aceito 
           para manter o aviso legível; na dúvida, o conferente consulta 
           o arquivo de entrada.
      549  - **Letra com traço próprio não vira letra base** (seção 5, pa
           sso 2): `ø`, `ł`, `đ` e semelhantes não têm decomposição canôn
           ica e ficam como estão, então `"Smørrebrød"` e `"Smorrebrod"` 
           são fornecedores diferentes na RN-007. Aceito porque são raras
            em dados em português e uma tabela própria de equivalências s
           eria incompleta por construção.
      548 -- **Caractere invisível no meio da palavra** (seção 5, passo 3
          -): um espaço de largura zero dentro de `"ali\u200bmentacao"` é
          - separador, a categoria vira `ali_mentacao` e a despesa sai `c
          -ategoria_fora_da_politica`. Aceito porque tratar invisíveis de
          - outro jeito exigiria uma lista própria de caracteres, incompl
          -eta por construção; o caractere vem de colagem acidental e o c
          -onferente vê a categoria como veio.                           
      550 +- **Caractere invisível ou letra parecida de outro alfabeto** 
          +(seção 5, passo 3): um espaço de largura zero ou um hífen suav
          +e dentro da palavra é separador, e uma letra de outro alfabeto
          + parecida com a latina (`о` cirílico) é letra distinta. Na cat
          +egoria, `"ali\u200bmentacao"` vira `ali_mentacao` e sai `categ
          +oria_fora_da_politica`; o conferente vê a categoria como veio.
          + No fornecedor, `"Bistro Cen\u00adtral"` ou `"Bistrо Central"`
          + (com `о` cirílico) não é duplicata de `"Bistro Central"`, e a
          +s duas despesas são pagas até o limite do dia, **sem sinal na 
          +saída** (o fornecedor não aparece nela). Aceito porque tratar 
          +esses caracteres exigiria uma lista própria de equivalências, 
          +incompleta por construção; o caso vem de colagem acidental ou 
          +de fraude deliberada, que a conferência humana das notas cobre
          +.                                                             
      551 +- **Formas de compatibilidade distintas da forma comum** (seçã
          +o 5, passo 2): letras e algarismos em largura total (`ＡＬＩＭ
          +ＥＮＴＡＣＡＯ`), sobrescritos e ligaduras que a equivalência 
          +de caixa não desfaz continuam diferentes da forma comum; uma c
          +ategoria em largura total sai `categoria_fora_da_politica`. Ac
          +eito por ser improvável em dados em português e porque desfaze
          +r compatibilidades mudaria também caracteres que a spec não pe
          +de (ex.: `²` viraria `2`).                                    
      552  - **Quase-duplicatas** (AMB-010): o mesmo gasto relançado com 
           data vizinha, valor diferente em um centavo ou fornecedor com 
           outra grafia (além do que a normalização da seção 5 cobre) não
            é detectado. Aceito porque qualquer critério aproximado seria
            regra inventada e poderia recusar gastos legítimos repetidos.
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+3 -3)
      42    - **Tipo:** regra
      43    - **Atende:** seção 5 da spec (normalização), AMB-011, D-005;
           usada por RN-002, RN-006 e RN-007
      44    - **Depende de:** T-001
      45 -  - **Aceite:** `tests/test_normalizacao.py` passa: exemplos da
         - seção 5 (`"Transporte Urbano"`, `"transporte-urbano"`, `" TRAN
         -SPORTE__urbano "`, `"Transporte – Urbano"` → `transporte_urbano
         -`; `"Pão  Quente"`, `"pao-quente"` → `pao_quente`; `"-Bistro"`,
         - `"_Bistro"`, `"Bistro -"`, `" -_Bistro"` → `bistro`; `"Padaria
         - (Centro)"` → `padaria_centro`; `"McDonald's"` → `mcdonald_s`; 
         -`"Straße"` → `strasse`; `"Smørrebrød"` → `smørrebrød`; `"-"` → 
         -vazio); acento pré-composto e combinante dão o mesmo resultado;
         - `ç`, `ô`, `ü`, `ñ`; sinal combinante solto (no início, sobre h
         -ífen no fim) é descartado; tabulação, quebra de linha, espaço n
         -ão separável, espaço de largura zero e caractere de controle na
         -s pontas; mistura de separadores internos de qualquer tipo vira
         - um `_`; algarismos são mantidos.                              
      45 +  - **Aceite:** `tests/test_normalizacao.py` passa: exemplos da
         + seção 5 (`"Transporte Urbano"`, `"transporte-urbano"`, `" TRAN
         +SPORTE__urbano "`, `"Transporte – Urbano"` → `transporte_urbano
         +`; `"Pão  Quente"`, `"pao-quente"` → `pao_quente`; `"-Bistro"`,
         + `"_Bistro"`, `"Bistro -"`, `" -_Bistro"` → `bistro`; `"Padaria
         + (Centro)"` → `padaria_centro`; `"McDonald's"` → `mcdonald_s`; 
         +`"Straße"` → `strasse`; `"Padaria Nº 1"` → `padaria_nº_1` e `"P
         +adaria N° 1"` → `padaria_n_1`; `"Loja²"` → `loja`; `"Smørrebrød
         +"` → `smørrebrød`; `"-"` → vazio); acento pré-composto e combin
         +ante dão o mesmo resultado; `ç`, `ô`, `ü`, `ñ`; sinal combinant
         +e solto (no início, sobre hífen no fim) é descartado; tabulação
         +, quebra de linha, espaço não separável, espaço de largura zero
         + e caractere de controle nas pontas; mistura de separadores int
         +ernos de qualquer tipo vira um `_`; letras de qualquer alfabeto
         + e algarismos decimais de qualquer escrita são mantidos como es
         +tão; número que não é dígito decimal (`²`, `½`) é separador.   
      46    - **Commit:**
      47  
      48  - [ ] **T-004** — Justificativa: `justificativa.py` gera a fras
          e em português de um item já decidido, para cada status e motiv
          o, com formatação própria `1.234,56` e `DD/MM` sem `locale` (DT
          -009).
     ...
      79    - **Tipo:** regra
      80    - **Atende:** RN-002 (erro de arquivo), seção 4 da spec (Entr
          ada), DT-003
      81    - **Depende de:** T-006
      82 -  - **Aceite:** `tests/test_rn002_validacao_da_entrada.py` pass
         -a os testes de cabeçalho: `colaborador` ausente; `id`/`nome` au
         -sentes, não texto, vazios ou só com espaços em branco (inclusiv
         -e espaço não separável); `periodo.inicio`, `periodo.fim` ou `de
         -spesas` ausentes; `inicio`/`fim` que não são `AAAA-MM-DD` válid
         -as (`2026-7-1`, `20260701`, `2026-02-30`, dígitos não ASCII); `
         -inicio` posterior a `fim` → `ErroDeArquivo`. `inicio` igual a `
         -fim` → válido. `despesas: []` → válido. `competencia` `202607` 
         -→ nula, sem erro; `competencia` `"julho"` → copiada. `centro_cu
         -sto` ausente → válido.                                         
      82 +  - **Aceite:** `tests/test_rn002_validacao_da_entrada.py` pass
         +a os testes de cabeçalho: `colaborador` ausente; `id`/`nome` au
         +sentes, não texto, vazios ou só com espaços em branco (inclusiv
         +e espaço não separável); `nome` só de U+200B, BOM ou U+001F → v
         +álido (não é espaço em branco, RN-002); `periodo.inicio`, `peri
         +odo.fim` ou `despesas` ausentes; `inicio`/`fim` que não são `AA
         +AA-MM-DD` válidas (`2026-7-1`, `20260701`, `2026-02-30`, dígito
         +s não ASCII); `inicio` posterior a `fim` → `ErroDeArquivo`. `in
         +icio` igual a `fim` → válido. `despesas: []` → válido. `compete
         +ncia` `202607` → nula, sem erro; `competencia` `"julho"` → copi
         +ada. `centro_custo` ausente → válido.                          
      83    - **Commit:**
      84  
      85  - [ ] **T-009** — Validação da despesa: cada elemento de `despe
          sas` vira `Despesa` (válida) ou `DespesaInvalida` (etapa 1 da s
          eção 8), com `categoria_saida` normalizada se reconhecida e os 
          avisos da T-007 anexados.
      86    - **Tipo:** regra
      87    - **Atende:** RN-002 (despesa inválida), AMB-018, DT-003
      88    - **Depende de:** T-003, T-007, T-008
      89 -  - **Aceite:** `tests/test_rn002_validacao_da_entrada.py` pass
         -a os testes de despesa: elemento que não é objeto (`null`, núme
         -ro, lista) → inválida com `id`/`data` nulos; cada campo obrigat
         -ório ausente; `data` em formato errado (mesmos casos da T-008);
         - `valor` não número (`"10"`, `true`, `null`); `tem_nota_fiscal`
         - não booleano (`1`, `"sim"`); `id`/`categoria`/`fornecedor` não
         - texto, vazio ou só espaços; `categoria`/`fornecedor` cujo text
         -o normalizado fica vazio (`"-"`, `"***"`); `abs(valor) >= 10000
         -00000` (inclusive `-1e12` e `1e999999`) → inválida; `999999999.
         -995` e `999999999.99999999999` → válidas; `"id": 17` → `id` nul
         -o; `"ALIMENTACAO"` em despesa inválida → `categoria_saida` `ali
         -mentacao`; categoria não reconhecida em despesa inválida → como
         - veio; campo extra ignorado; `valor_informado` guardado quando 
         -é número.                                                      
      89 +  - **Aceite:** `tests/test_rn002_validacao_da_entrada.py` pass
         +a os testes de despesa: elemento que não é objeto (`null`, núme
         +ro, lista) → inválida com `id`/`data` nulos; cada campo obrigat
         +ório ausente; `data` em formato errado (mesmos casos da T-008);
         + `valor` não número (`"10"`, `true`, `null`); `tem_nota_fiscal`
         + não booleano (`1`, `"sim"`); `id`/`categoria`/`fornecedor` não
         + texto, vazio ou só espaços; `id` `"-"` ou só de U+200B → válid
         +o; `categoria`/`fornecedor` cujo texto normalizado fica vazio (
         +`"-"`, `"***"`); `abs(valor) >= 1000000000` (inclusive `-1e12` 
         +e `1e999999`) → inválida; `999999999.995` e `999999999.99999999
         +999` → válidas; `"id": 17` → `id` nulo; `"ALIMENTACAO"` em desp
         +esa inválida → `categoria_saida` `alimentacao`; categoria não r
         +econhecida em despesa inválida → como veio; campo extra ignorad
         +o; `valor_informado` guardado quando é número.                 
      90    - **Commit:**
      91  
      92  ## Fase 3 — Regras de negócio (motor)

⏺ Agora os testes dos exemplos novos da seção 5. Também confiro a afirmação que
  pus no plano, de que isspace() só difere do White_Space em U+001C a U+001F:

⏺ Bash(python3 - <<'PYEOF'
      import pathlib…)
  ⎿  82 passed in 0.05s
     All checks passed!
     so no python: ['0x1c', '0x1d', '0x1e', '0x1f'] so no unicode: []
  ⎿  Updated tests/test_normalizacao.py (+15 -0)
      31          ("Padaria (Centro)", "padaria_centro"),  # " (" → `_`; 
          ")" na ponta some
      32          ("McDonald's", "mcdonald_s"),  # "'" interno → `_`
      33          ("Straße", "strasse"),  # passo 1: equivalência complet
          a de caixa
      34 +        ("Padaria Nº 1", "padaria_nº_1"),  # º é letra (categor
         +ia Unicode "letra")                                            
      35 +        ("Padaria N° 1", "padaria_n_1"),  # ° é símbolo → separ
         +ador                                                           
      36 +        ("Loja²", "loja"),  # ² não é dígito decimal → separado
         +r na ponta                                                     
      37          ("Smørrebrød", "smørrebrød"),  # passo 2: ø sem decompo
          sição canônica
      38          ("-", ""),  # só separadores → vazio
      39      ],
     ...
      199      """Seção 5: as categorias da política já estão na forma no
           rmalizada."""
      200      for texto in ("alimentacao", "transporte_urbano", "hospeda
           gem"):
      201          assert normalizar_texto(texto) == texto
      202 +                                                              
      203 +                                                              
      204 +def test_secao5_ordinal_e_letra_e_grau_e_separador():         
      205 +    """Seção 5 passo 3 (D-005 ponto 8): `"Padaria Nº 1"` ≠ `"P
          +adaria N° 1"`."""                                             
      206 +    assert normalizar_texto("Padaria Nº 1") != normalizar_text
          +o("Padaria N° 1")                                             
      207 +                                                              
      208 +                                                              
      209 +def test_secao5_letra_modificadora_e_letra_e_apostrofo_e_separ
          +ador():                                                       
      210 +    """Seção 5 passo 3 (D-005 ponto 8): `ʼ` (U+02BC) é letra; 
          +`’` (U+2019) é                                                
      211 +    pontuação → separador."""                                 
      212 +    assert normalizar_texto("McDonald\u02bcs") == "mcdonald\u0
          +2bcs"                                                         
      213 +    assert normalizar_texto("McDonald\u2019s") == "mcdonald_s"

⏺ Confirmado: a única diferença entre isspace() do Python e White_Space do
  Unicode fica nos caracteres U+001C–U+001F; os 82 testes passam e o ruff está
  limpo, incluindo os novos casos de Nº/N° e ʼ. Agora vou rodar a rodada de
  confirmação do spec-adversary e a revisão 4 da T-003.

⏺ 2 background agents launched (↓ to manage)
   ├ spec-adversary (Confirmação adversarial spec 1.8)
   └ revisor-de-task (Revisar task T-003 (revisão 4))

⏺ Apliquei o pacote que você aprovou na spec 1.8, que ainda não foi commitada.
  Ainda não fiz nenhum commit.

  O que mudou:
  - Seção 5:
    - "Letra", "algarismo decimal" e "sinal combinante" agora são definidos
      pelas categorias do Unicode. º, ª e ʼ contam como letra; °, ² e ½ são
      separadores; algarismos de outras escritas ficam como estão.
    - Novos exemplos: Nº ≠ N° e "Loja²" → loja.
  - RN-002:
    - "Espaço em branco" segue a classificação do Unicode. Espaço de largura
      zero, BOM e os caracteres de controle U+001C a U+001F não contam como
      espaço.
    - id e nome não passam pela normalização, então "-" é um id válido.
  - Seção 10:
    - O risco do caractere invisível agora cobre também o fornecedor, que não
      aparece na saída.
    - Novo risco aceito para letras e algarismos em largura total e
      sobrescritos, que continuam diferentes da forma comum.
  - D-005:
    - Pontos 8 a 12 acrescentados.
    - Frase errada sobre o exemplo corrigida: transporte_urbano tem sublinhado.
    - As três rodadas do spec-adversary ficaram registradas.
  - plan.md: o DT-003 avisa que, para validar id e nome, não basta usar
    strip()/isspace() do Python, porque eles tratam U+001C a U+001F como espaço.
    Conferi por script que essa é a única diferença em relação ao Unicode.
  - tasks.md: os aceites da T-003, T-008 e T-009 foram atualizados.
  - Testes: acrescentei os casos de Nº/N°, ʼ/’ e ². Eles passaram de primeira,
    porque o código já seguia essas regras. Agora são 82 testes passando e o
    ruff está limpo.

  A rodada de confirmação do spec-adversary e a revisão 4 da T-003 estão rodando
  em segundo plano. Pedi ao spec-adversary que só marque como bloqueante o que
  muda valor, status ou motivo em entrada plausível.

✻ Churned for 1m 17s · done 11:05 PM

› Message from revisor-de-task
  # Revisão T-003 — Normalização de texto: `normalizar_texto()` com os passos da
  seção 5 da spec (DT-004)

  - **Data:** 2026-10-01
  - **Regras conferidas:** seção 5 da spec 1.8 (passos 1 a 3, o parágrafo sobre
  texto vazio e os exemplos), AMB-011, D-005 (pontos 1 a 12),
  RN-002/RN-006/RN-007 (apenas os trechos que usam a normalização), seção 10
  (riscos sobre `ø`, invisíveis e compatibilidade), DT-004 (plan 1.1)
  - **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 82 passed, 0
  failed (evidência, não veredito)

  ### Resultado
  **APROVADO COM RESSALVAS** — A implementação segue literalmente os 3 passos da
  seção 5 e cumpre todos os itens do Aceite. Faltam testes para dois
  comportamentos que a spec cita de forma explícita: marcas `Mc`/`Me` e
  separador invisível no meio da palavra.

  ### Critérios de aceite
  | # | Critério | Status | Evidência |
  |---|---|---|---|
  | 1 | `"Transporte Urbano"`, `"transporte-urbano"`, `" TRANSPORTE__urbano "`,
  `"Transporte – Urbano"` → `transporte_urbano` | atendido |
  `tests/test_normalizacao.py::test_secao5_exemplos_transporte_urbano`. O
  travessão é U+2013, conferido nos bytes do arquivo |
  | 2 | `"Pão  Quente"`, `"pao-quente"` → `pao_quente` | atendido |
  `test_secao5_exemplos_pao_quente` |
  | 3 | `"-Bistro"`, `"_Bistro"`, `"Bistro -"`, `" -_Bistro"` → `bistro` |
  atendido | `test_secao5_hifen_e_sublinhado_nas_pontas_sao_removidos` |
  | 4 | `"Padaria (Centro)"` → `padaria_centro`; `"McDonald's"` → `mcdonald_s` |
  atendido | `test_secao5_demais_exemplos_da_spec`,
  `test_secao5_pontuacao_interna_distingue_mcdonalds` |
  | 5 | `"Straße"` → `strasse` | atendido |
  `test_secao5_demais_exemplos_da_spec` |
  | 6 | `"Padaria Nº 1"` → `padaria_nº_1`; `"Padaria N° 1"` → `padaria_n_1` |
  atendido | `test_secao5_demais_exemplos_da_spec`,
  `test_secao5_ordinal_e_letra_e_grau_e_separador`. Bytes conferidos: `º` =
  U+00BA (Lo) e `°` = U+00B0 (So) |
  | 7 | `"Loja²"` → `loja`; `"Smørrebrød"` → `smørrebrød`; `"-"` → vazio |
  atendido | `test_secao5_demais_exemplos_da_spec`,
  `test_secao5_texto_so_de_separadores_fica_vazio` |
  | 8 | Acento pré-composto e combinante dão o mesmo resultado | atendido |
  `test_secao5_acento_precomposto_e_combinante_dao_o_mesmo_resultado`. O arquivo
  contém U+0327 e U+0303, e o teste afirma que as duas strings de entrada são
  diferentes |
  | 9 | `ç`, `ô`, `ü`, `ñ` | atendido |
  `test_secao5_diacriticos_da_spec_viram_letra_base` |
  | 10 | Sinal combinante solto (no início, sobre hífen no fim) é descartado |
  atendido | `test_secao5_sinal_combinante_solto_e_descartado`, com U+0301 no
  início, `-` + U+0301 no fim e o seletor U+FE0F |
  | 11 | Tabulação, quebra de linha, espaço não separável, espaço de largura
  zero e caractere de controle nas pontas | atendido |
  `test_secao5_separador_de_qualquer_tipo_nas_pontas_e_removido`, com U+00A0,
  U+200B, U+FEFF, `\x1c` e `\x00` |
  | 12 | Mistura de separadores internos de qualquer tipo vira um `_` | atendido
  | `test_secao5_mistura_de_separadores_internos_vira_um_sublinhado`,
  `test_secao5_sequencias_internas_separadas_viram_um_sublinhado_cada` |
  | 13 | Letras de qualquer alfabeto e algarismos decimais de qualquer escrita
  ficam como estão | atendido |
  `test_secao5_letras_de_qualquer_alfabeto_e_algarismos_decimais_contam` (grego,
  cirílico, `٣` U+0663) e
  `test_secao5_letra_modificadora_e_letra_e_apostrofo_e_separador` (`ʼ` U+02BC)
  |
  | 14 | Número que não é dígito decimal (`²`, `½`) é separador | atendido |
  `test_secao5_numero_que_nao_e_algarismo_decimal_e_separador` (`²`, `½`, `Ⅻ`) |

  Recalculei à mão, pela seção 5, o esperado de cada teste, e todos batem com a
  spec. Exemplo: `"Café Ωμέγα"` passa por casefold e vira `"café ωμέγα"`. O NFD
  separa `é` em `e` + U+0301 e `έ` em `ε` + U+0301; as marcas são descartadas,
  resultando em `"cafe ωμεγα"`, e o espaço vira `_`: `cafe_ωμεγα`. Nenhum
  esperado parece copiado da saída do programa.

  Implementação
  (`/Users/rafaeltxm/repo/sdd-desafio/src/reembolso/normalizacao.py`):
  - A ordem casefold → NFD → descarte de `M*` → troca de tudo que não é
  `L*`/`Nd` por espaço → `"_".join(split())` corresponde aos passos 1, 2 e 3 da
  spec e ao DT-004.
  - `split()` só recebe espaços ASCII, porque os demais separadores já foram
  trocados no passo anterior. Assim, a divergência de `isspace()` com U+001C a
  U+001F não afeta este módulo.
  - Não encontrei constante, filtro ou condição sem base na spec.

  ### Problemas encontrados

  #### 1. Descarte de marcas `Mc` e `Me` sem teste — severidade MÉDIA
  - **Regra afetada:** seção 5, passo 2; D-005, ponto 8.
  - **Evidência:** a spec diz: "todo sinal combinante (caractere da categoria
  Unicode "marca": sem espaço próprio, com espaço próprio ou envolvente) é
  descartado". Os testes em `tests/test_normalizacao.py` só usam marcas `Mn`
  (U+0301, U+0303, U+0327, U+FE0F). O código (`normalizacao.py:15`,
  `startswith("M")`) está certo: verifiquei manualmente que `'alimentacao⃝'` vira
  `alimentacao` e `'aःb'` vira `ab`.
  - **Impacto:** uma implementação que descarte só `Mn` passaria em todos os
  testes. O antigo DT-004 era exatamente assim e foi invalidado pela D-005. Uma
  regressão nesse ponto não seria detectada.
  - **Recomendação:** acrescentar um caso com marca `Mc` (como U+0903) e outro
  com marca `Me` (como U+20DD), com o esperado tirado do passo 2.

  #### 2. Separador invisível no meio da palavra sem teste — severidade MÉDIA
  - **Regra afetada:** seção 5, passo 3; seção 10 ("Caractere invisível ou letra
  parecida de outro alfabeto"); D-005, ponto 7.
  - **Evidência:** a seção 10 dá exemplos explícitos: `"alimentacao"` vira
  `ali_mentacao`, e `"Bistro Central"` não é duplicata de `"Bistro Central"`. Os
  testes usam U+200B, BOM e caracteres de controle apenas nas pontas. O código
  está de acordo: verifiquei manualmente `ali_mentacao` e `bistro_cen_tral`.
  - **Impacto:** uma implementação que simplesmente removesse os invisíveis (em
  vez de tratá-los como separador) passaria nos testes. Isso mudaria a RN-006: a
  categoria passaria a ser reconhecida como `alimentacao`, quando a spec manda
  `categoria_fora_da_politica`.
  - **Recomendação:** testar os dois exemplos da seção 10 (U+200B e U+00AD no
  meio da palavra). Opcionalmente, testar também `о` cirílico como letra
  distinta.

  #### 3. Diff mistura a mudança de spec da D-005 com o código da task —
  severidade BAIXA
  - **Regra afetada:** nenhuma regra de negócio. É convenção de commits do
  CLAUDE.md (`docs(spec|plan|tasks|decisions):`).
  - **Evidência:** `git diff --stat` mostra `spec.md`, `plan.md`, `tasks.md` e
  `DECISIONS.md` alterados junto com `normalizacao.py`. Esse diff também inclui
  mudanças no Aceite da T-008 e da T-009.
  - **Impacto:** nenhum resultado muda. As mudanças de documentação são
  coerentes entre si: a spec 1.8 reflete os pontos 1 a 12 da D-005, e o DT-004
  está alinhado. Só a rastreabilidade fica prejudicada se tudo entrar em um
  único `feat(T-003)`.
  - **Recomendação:** commitar a spec, o plano, as tasks e as decisões em
  commits `docs(...)` separados do `feat(T-003)`.

  #### 4. Histórico da revisão anterior — severidade BAIXA
  - **Regra afetada:** nenhuma. É questão de rastreabilidade.
  - **Evidência:** o `DECISIONS.md` (D-005, "Gatilho") cita
  "`docs/reviews/T-003.md`, revisão 1, BLOQUEADO". O arquivo ainda não rastreado
  `docs/reviews/T-003.md` contém essa revisão 1.
  - **Impacto:** se este relatório substituir o arquivo, a referência da D-005
  aponta para um conteúdo que deixou de existir.
  - **Recomendação:** cabe ao humano decidir como preservar a revisão 1, por
  exemplo anexando esta revisão ao mesmo arquivo em vez de sobrescrevê-lo.

  ### Cobertura
  - **Regras testadas:**
    - Seção 5, passo 1 (casefold, `ß`): `test_secao5_demais_exemplos_da_spec`,
  testes de caixa.
    - Seção 5, passo 2 (NFD, marcas, `ø`/`ł`/`đ`):
  `test_secao5_acento_precomposto_e_combinante_dao_o_mesmo_resultado`,
  `test_secao5_diacriticos_da_spec_viram_letra_base`,
  `test_secao5_sinal_combinante_solto_e_descartado`,
  `test_secao5_letra_sem_decomposicao_canonica_fica_como_esta`.
    - Seção 5, passo 3 (letras, dígitos, separadores, pontas e meio):
  `test_secao5_separador_de_qualquer_tipo_nas_pontas_e_removido`,
  `test_secao5_hifen_e_sublinhado_nas_pontas_sao_removidos`,
  `test_secao5_mistura_de_separadores_internos_vira_um_sublinhado`,
  `test_secao5_letras_de_qualquer_alfabeto_e_algarismos_decimais_contam`,
  `test_secao5_numero_que_nao_e_algarismo_decimal_e_separador`,
  `test_secao5_ordinal_e_letra_e_grau_e_separador`,
  `test_secao5_letra_modificadora_e_letra_e_apostrofo_e_separador`.
    - Texto vazio: `test_secao5_texto_so_de_separadores_fica_vazio`. A recusa
  por `entrada_invalida` é da T-009, corretamente fora do escopo.
    - AMB-011: os exemplos de categoria (`transporte_urbano`, `alimentação`,
  tabulação no fim) e `test_secao5_texto_ja_normalizado_fica_igual`.
  - **Casos de borda cobertos:** todos os exemplos da seção 5; acento
  pré-composto e combinante; sinal combinante solto no início e sobre hífen no
  fim; seletor de variação; White_Space, invisíveis e controle nas pontas;
  separadores mistos no meio; texto só com separadores, incluindo `""` e uma
  marca sozinha; `º` × `°`; `ʼ` × `’`; `²`, `½`, `Ⅻ`; dígito não ASCII. A seção
  7 não atribui linhas à T-003; as linhas de categoria e fornecedor pertencem a
  T-009, T-015 e T-016.
  - **Casos que parecem faltar:**
    - Marcas `Mc` e `Me` (seção 5, passo 2: "com espaço próprio ou envolvente").
    - Invisível no meio da palavra: `"alimentacao"` → `ali_mentacao` e hífen
  suave U+00AD (seção 10).
    - Opcionais, sem mudança de resultado no código atual: forma de largura
  total diferente da forma comum (seção 10, "Formas de compatibilidade") e `ª`
  (passo 3).

  ### Decisões necessárias
  Nenhuma.

  ### Antes de concluir a task
  - Acrescentar os testes de marca `Mc`/`Me` (problema 1) e de invisível no meio
  da palavra (problema 2). Estes problemas são recomendados, não bloqueantes.
  - Separar os commits de documentação da D-005 (spec, plano, tasks, decisões)
  do commit `feat(T-003)`, e decidir como preservar a revisão 1 citada na D-005
  (problemas 3 e 4).
  - Com isso, pode seguir para o commit.

  Arquivos relevantes:
  `/Users/rafaeltxm/repo/sdd-desafio/src/reembolso/normalizacao.py`,
  `/Users/rafaeltxm/repo/sdd-desafio/tests/test_normalizacao.py`,
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md` (seção
  5, linhas 139-147; seção 10),
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md`
  (D-005), `/Users/rafaeltxm/repo/sdd-desafio/docs/reviews/T-003.md` (revisão 1,
  existente).

⏺ Bash(cat >> docs/reviews/T-003.md <<'EOF'…)
  ⎿  87 passed in 0.05s
     All checks passed!
  ⎿  Updated docs/reviews/T-003.md (+87 -0)
      207  
      208  ### Antes de concluir a task
      209  Nenhum item bloqueia o commit. É recomendável acrescentar os c
           asos de teste do problema 1 antes, para cobrir o passo 3 por c
           ompleto.
      210 +                                                              
      211 +---                                                           
      212 +                                                              
      213 +## Revisão 4                                                  
      214 +                                                              
      215 +# Revisão T-003 — Normalização de texto: `normalizar_texto()` 
          +com os passos da seção 5 da spec (DT-004)                     
      216 +                                                              
      217 +- **Data:** 2026-10-01                                        
      218 +- **Regras conferidas:** seção 5 da spec 1.8 (passos 1 a 3, o 
          +parágrafo sobre texto vazio e os exemplos), AMB-011, D-005 (po
          +ntos 1 a 12), RN-002/RN-006/RN-007 (apenas os trechos que usam
          + a normalização), seção 10 (riscos sobre `ø`, invisíveis e com
          +patibilidade), DT-004 (plan 1.1)                              
      219 +- **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` →
          + 82 passed, 0 failed (evidência, não veredito)                
      220 +                                                              
      221 +### Resultado                                                 
      222 +**APROVADO COM RESSALVAS** — A implementação segue literalment
          +e os 3 passos da seção 5 e cumpre todos os itens do Aceite. Fa
          +ltam testes para dois comportamentos que a spec cita de forma 
          +explícita: marcas `Mc`/`Me` e separador invisível no meio da p
          +alavra.                                                       
      223 +                                                              
      224 +### Critérios de aceite                                       
      225 +| # | Critério | Status | Evidência |                         
      226 +|---|---|---|---|                                             
      227 +| 1 | `"Transporte Urbano"`, `"transporte-urbano"`, `" TRANSPO
          +RTE__urbano "`, `"Transporte – Urbano"` → `transporte_urbano` 
          +| atendido | `tests/test_normalizacao.py::test_secao5_exemplos
          +_transporte_urbano`. O travessão é U+2013, conferido nos bytes
          + do arquivo |                                                 
      228 +| 2 | `"Pão  Quente"`, `"pao-quente"` → `pao_quente` | atendid
          +o | `test_secao5_exemplos_pao_quente` |                       
      229 +| 3 | `"-Bistro"`, `"_Bistro"`, `"Bistro -"`, `" -_Bistro"` → 
          +`bistro` | atendido | `test_secao5_hifen_e_sublinhado_nas_pont
          +as_sao_removidos` |                                           
      230 +| 4 | `"Padaria (Centro)"` → `padaria_centro`; `"McDonald's"` 
          +→ `mcdonald_s` | atendido | `test_secao5_demais_exemplos_da_sp
          +ec`, `test_secao5_pontuacao_interna_distingue_mcdonalds` |    
      231 +| 5 | `"Straße"` → `strasse` | atendido | `test_secao5_demais_
          +exemplos_da_spec` |                                           
      232 +| 6 | `"Padaria Nº 1"` → `padaria_nº_1`; `"Padaria N° 1"` → `p
          +adaria_n_1` | atendido | `test_secao5_demais_exemplos_da_spec`
          +, `test_secao5_ordinal_e_letra_e_grau_e_separador`. Bytes conf
          +eridos: `º` = U+00BA (Lo) e `°` = U+00B0 (So) |               
      233 +| 7 | `"Loja²"` → `loja`; `"Smørrebrød"` → `smørrebrød`; `"-"`
          + → vazio | atendido | `test_secao5_demais_exemplos_da_spec`, `
          +test_secao5_texto_so_de_separadores_fica_vazio` |             
      234 +| 8 | Acento pré-composto e combinante dão o mesmo resultado |
          + atendido | `test_secao5_acento_precomposto_e_combinante_dao_o
          +_mesmo_resultado`. O arquivo contém U+0327 e U+0303, e o teste
          + afirma que as duas strings de entrada são diferentes |       
      235 +| 9 | `ç`, `ô`, `ü`, `ñ` | atendido | `test_secao5_diacriticos
          +_da_spec_viram_letra_base` |                                  
      236 +| 10 | Sinal combinante solto (no início, sobre hífen no fim) 
          +é descartado | atendido | `test_secao5_sinal_combinante_solto_
          +e_descartado`, com U+0301 no início, `-` + U+0301 no fim e o s
          +eletor U+FE0F |                                               
      237 +| 11 | Tabulação, quebra de linha, espaço não separável, espaç
          +o de largura zero e caractere de controle nas pontas | atendid
          +o | `test_secao5_separador_de_qualquer_tipo_nas_pontas_e_remov
          +ido`, com U+00A0, U+200B, U+FEFF, `\x1c` e `\x00` |           
      238 +| 12 | Mistura de separadores internos de qualquer tipo vira u
          +m `_` | atendido | `test_secao5_mistura_de_separadores_interno
          +s_vira_um_sublinhado`, `test_secao5_sequencias_internas_separa
          +das_viram_um_sublinhado_cada` |                               
      239 +| 13 | Letras de qualquer alfabeto e algarismos decimais de qu
          +alquer escrita ficam como estão | atendido | `test_secao5_letr
          +as_de_qualquer_alfabeto_e_algarismos_decimais_contam` (grego, 
          +cirílico, `٣` U+0663) e `test_secao5_letra_modificadora_e_letr
          +a_e_apostrofo_e_separador` (`ʼ` U+02BC) |                     
      240 +| 14 | Número que não é dígito decimal (`²`, `½`) é separador 
          +| atendido | `test_secao5_numero_que_nao_e_algarismo_decimal_e
          +_separador` (`²`, `½`, `Ⅻ`) |                                 
      241 +                                                              
      242 +Recalculei à mão, pela seção 5, o esperado de cada teste, e to
          +dos batem com a spec. Exemplo: `"Café Ωμέγα"` passa por casefo
          +ld e vira `"café ωμέγα"`. O NFD separa `é` em `e` + U+0301 e `
          +έ` em `ε` + U+0301; as marcas são descartadas, resultando em `
          +"cafe ωμεγα"`, e o espaço vira `_`: `cafe_ωμεγα`. Nenhum esper
          +ado parece copiado da saída do programa.                      
      243 +                                                              
      244 +Implementação (`/Users/rafaeltxm/repo/sdd-desafio/src/reembols
          +o/normalizacao.py`):                                          
      245 +- A ordem casefold → NFD → descarte de `M*` → troca de tudo qu
          +e não é `L*`/`Nd` por espaço → `"_".join(split())` corresponde
          + aos passos 1, 2 e 3 da spec e ao DT-004.                     
      246 +- `split()` só recebe espaços ASCII, porque os demais separado
          +res já foram trocados no passo anterior. Assim, a divergência 
          +de `isspace()` com U+001C a U+001F não afeta este módulo.     
     … 50 more lines (ctrl+o to expand)
  ⎿  Updated tests/test_normalizacao.py (+30 -0)
      211      pontuação → separador."""
      212      assert normalizar_texto("McDonald\u02bcs") == "mcdonald\u0
           2bcs"
      213      assert normalizar_texto("McDonald\u2019s") == "mcdonald_s"
      214 +                                                              
      215 +                                                              
      216 +@pytest.mark.parametrize(                                     
      217 +    "texto",                                                  
      218 +    [                                                         
      219 +        "alimentaःcao",  # Mc: marca com espaço próprio (devan
          +ágari)                                                        
      220 +        "alimentacao⃝",  # Me: marca envolvente                
      221 +    ],                                                        
      222 +)                                                             
      223 +def test_secao5_marcas_com_espaco_proprio_e_envolventes_sao_de
          +scartadas(texto):                                             
      224 +    """Seção 5 passo 2 (D-005 ponto 8): todo sinal combinante 
          +da categoria                                                  
      225 +    "marca" — sem espaço próprio, com espaço próprio ou envolv
          +ente — é descartado."""                                       
      226 +    assert normalizar_texto(texto) == "alimentacao"           
      227 +                                                              
      228 +                                                              
      229 +@pytest.mark.parametrize(                                     
      230 +    ("texto", "esperado"),                                    
      231 +    [                                                         
      232 +        ("alimentacao", "ali_mentacao"),  # espaço de largura 
          +zero                                                          
      233 +        ("Bistro Central", "bistro_cen_tral"),  # hífen suave 
      234 +        ("Bistrо Central", "bistrо_central"),  # о cirílico é 
          +outra letra                                                   
      235 +    ],                                                        
      236 +)                                                             
      237 +def test_secao5_invisivel_no_meio_e_separador_e_letra_parecida
          +_e_distinta(                                                  
      238 +    texto, esperado                                           
      239 +):                                                            
      240 +    """Seção 5 passo 3 / seção 10 (risco aceito): invisível no
          + meio da palavra é                                            
      241 +    separador (não é removido); `о` cirílico é letra distinta 
          +de `o`."""                                                    
      242 +    assert normalizar_texto(texto) == esperado                
      243 +    assert normalizar_texto(texto) != normalizar_texto("Bistro
          + Central")                                                    

⏺ Agent "Revisar task T-003 (revisão 4)" finished · 1m 41s

⏺ A revisão 4 da T-003 voltou APROVADO COM RESSALVAS, sem nenhuma decisão
  pendente. Salvei o relatório sem edição como "Revisão 4" em
  docs/reviews/T-003.md.

  Ela apontou duas ressalvas médias, ambas sobre testes que faltavam.
  Acrescentei os dois:
  - Sinais combinantes de outros tipos: um caso com sinal que ocupa espaço
    próprio e outro com sinal envolvente. Os dois são descartados.
  - Caractere invisível no meio da palavra: é tratado como separador.
    "alimentacao" vira ali_mentacao, e o mesmo vale para o hífen suave. O о
    cirílico conta como letra diferente do o latino.

  Os 5 casos passaram de primeira, porque o código já fazia isso. O ganho é que
  agora um erro nesses pontos seria detectado. São 87 testes passando e o ruff
  está limpo.

  As duas ressalvas baixas já estavam no plano:
  - Commits separados: a documentação (spec, plano, tasks e decisões) vai em
    commits docs(...) separados do feat(T-003).
  - Revisão 1 preservada: as revisões estão sendo anexadas ao mesmo arquivo,
    então a revisão 1, citada na D-005, continua lá.

  Ainda não fiz nenhum commit. Falta a rodada de confirmação do spec-adversary
  sobre a 1.8, que continua rodando em segundo plano.

✻ Churned for 46s · done 11:07 PM

› Message from spec-adversary
  Resumo: 4 problemas, nenhum bloqueante. Os dois bloqueantes da rodada anterior
  estão resolvidos na spec 1.8. Uma das correções trouxe uma contradição de
  texto nova (item 1), que só aparece em entradas improváveis.

  **Os dois bloqueantes anteriores**
  - **(1) Conjuntos de letra, algarismo e sinal: resolvido.** O passo 3 da seção
  5 define "letra" como a categoria Unicode L\* (com `º`, `ª` e `ʼ`) e
  "algarismo decimal" como Nd, mantido como está. O passo 2 define "sinal
  combinante" como a categoria M (Mn, Mc e Me). Também diz que o passo 2 trata o
  resultado do passo 1. Conferi um a um os exemplos da seção 5 (`Nº`/`N°`, `²`,
  `ß`, `ø`, `McDonald's`, travessão, `"-"`): todos batem com a regra.
  - **(2) "Espaço em branco": resolvido.** A RN-002 usa a propriedade
  White_Space do Unicode e vale para a spec inteira. ZWSP e BOM ficam excluídos
  de forma explícita, e `id` e `nome` não passam pela normalização. A seção 10 e
  a D-005 (pontos 8 a 11) refletem isso.
  - **Seção 7, RN-006 e RN-007:** não encontrei contradição nova com as
  correções.

  ### 1. "Caracteres de controle não são espaço em branco" contradiz a tabulação
  e a quebra de linha — [PODE ESPERAR] — contradição

  - **Regra afetada:** RN-002 (parágrafo "Espaço em branco...").
  - **Cenário de entrada:** uma despesa com `"id": "\t"`, ou com `"id":
  "\u0085"` (NEL), e o resto válido (data 2026-07-03, alimentacao, 30.00,
  `tem_nota_fiscal` true). Outra variação: `colaborador.nome` igual a `"\n"`.
  - **Comportamento pela interpretação atual:** indefinido. A primeira frase diz
  que tabulação e quebra de linha são White_Space. Então `"\t"` é "só espaço em
  branco": a despesa sai `entrada_invalida` e o `nome` dá erro de arquivo. A
  frase seguinte diz que "caracteres de controle (como U+001C a U+001F) não são
  espaço em branco". Tabulação, LF, CR e NEL são caracteres de controle (Cc).
  Lida como regra geral com exemplos, essa frase torna `"\t"` um texto válido.
  - **Por que é um problema:** as duas frases da mesma correção dão status
  opostos para o mesmo `id`. Isso só não é bloqueante porque um `id` ou `nome`
  feito só de tabulação ou quebra de linha é improvável.
  - **Pergunta para decisão:** a exclusão vale só para os caracteres de controle
  sem a propriedade White_Space (como U+001C a U+001F) ou para todo caractere
  de controle? Nos dois casos, o texto precisa deixar isso explícito para
  tabulação, LF, CR e NEL?

  ### 2. Letras invisíveis ou que parecem pontuação contam como letra — [PODE
  ESPERAR] — brecha

  - **Regra afetada:** seção 5, passo 3; RN-002 (normalizado vazio); RN-007;
  risco "Caractere invisível" da seção 10.
  - **Cenário de entrada:**
    - (a) Duas alimentações em 03/07, valor 40,00, com nota. Fornecedores
  `"Bistro Central"` e `"BistroㅤCentral"`. U+3164 é o preenchimento Hangul:
  invisível e da categoria Lo.
    - (b) Uma despesa com `"fornecedor": "ㅤ"`.
    - (c) As categorias `"alimentacaoㅤ"` e `"alimentacao"`.
    - (d) Os fornecedores `"Padaria Nº 1"` e `"Padaria N° 1"`. A troca de `º`
  por `°` é comum em dados brasileiros. O mesmo vale para `ʼ` (U+02BC) ou `ˊ`
  (U+02CA, Lm) no lugar de `'` ou `´`.
  - **Comportamento pela interpretação atual:**
    - (a) Não é duplicata: `bistroㅤcentral` ≠ `bistro_central`.
    - (b) O fornecedor é válido: não é White_Space e o normalizado não fica
  vazio. Todos os fornecedores feitos só desse caractere ficam iguais entre si.
    - (c) A primeira categoria sai `categoria_fora_da_politica`, porque uma
  letra na ponta não é removida. A segunda é reconhecida, porque o separador na
  ponta é removido.
    - (d) Não é duplicata. Esse resultado é decidido de forma explícita pelos
  exemplos da seção 5.
  - **Por que é um problema:** o resultado está definido, mas a seção 10
  descreve o caractere invisível só como separador. A variante "letra invisível"
  fica fora do risco registrado. Com ela, um fornecedor que parece vazio passa
  na validação da RN-002 (cenário b). O caso `º`/`°` é o mais plausível e só
  está coberto de forma genérica pelo risco "Quase-duplicatas".
  - **Pergunta para decisão:** esses casos (letra invisível Lo, letras
  modificadoras Lm parecidas com pontuação, `º` × `°`) estão cobertos pelos
  riscos aceitos atuais, ou precisam de registro próprio na seção 10?

  ### 3. Versão do Unicode não fixada — [PODE ESPERAR] — lacuna

  - **Regra afetada:** seção 5 (passos 1 a 3), RN-002 (White_Space), seção 9 ("a
  mesma entrada sempre produz a mesma saída").
  - **Cenário de entrada:** um fornecedor ou categoria com um code point hoje
  não atribuído (Cn, ou seja, separador), que uma versão futura do Unicode
  classifique como letra. Vale o mesmo para mudanças de categoria, de case
  folding ou de decomposição entre versões.
  - **Comportamento pela interpretação atual:** indefinido. A saída pode mudar
  (duplicata ou não, categoria reconhecida ou não) só por trocar a versão das
  tabelas Unicode, com a mesma entrada.
  - **Por que é um problema:** a spec exige determinismo, mas o resultado
  depende de tabelas cuja versão ela não fixa. Em dados realistas em português o
  efeito é nulo.
  - **Pergunta para decisão:** a spec deve fixar a versão do Unicode ou
  registrar essa dependência como risco aceito?

  ### 4. U+0345 deixa de ser sinal combinante no passo 1 e sobrevive como letra
  — [PODE ESPERAR] — contradição de redação

  - **Regra afetada:** seção 5, passos 1 e 2; D-005, ponto 3.
  - **Cenário de entrada:** `"categoria": "alimentacaoͅ"`. U+0345 é a
  ypogegrammeni grega, da categoria Mn.
  - **Comportamento pela interpretação atual:** o passo 1 (case folding
  completo) transforma U+0345 em `ι` (U+03B9, uma letra). O passo 2 então não a
  descarta, e o resultado é `alimentacaoι`, que sai
  `categoria_fora_da_politica`. Um outro sinal no mesmo lugar, como U+0301,
  seria descartado e a categoria seria reconhecida.
  - **Por que é um problema:** a leitura literal da ordem dos passos é
  inequívoca. Mesmo assim, ela contradiz a frase "todo sinal combinante é
  descartado, acompanhe ele uma letra ou não" e o texto da D-005, ponto 3. Não
  muda nada em dados realistas.
  - **Pergunta para decisão:** essa exceção é aceita como consequência da ordem
  caixa → acentos, ou o texto deve mencioná-la?

  **1. Decidir antes da implementação:** nenhum.

  **2. Pode ser decidido depois:** 1, 2, 3, 4.

  Arquivos lidos:
  - /Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md (seção
  5, RN-002, RN-006, RN-007, seções 7 e 10)
  - /Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md
  (D-005)

⏺ A rodada de confirmação não encontrou nenhum bloqueante, e os dois bloqueantes
  anteriores estão resolvidos. O item 1 é uma contradição de redação que eu
  introduzi: a regra pretendida era "espaço em branco = propriedade White_Space
  do Unicode", que você já aprovou. Os itens 2 a 4 são cantos do Unicode que não
  mudam nada em dados realistas e, como combinado, vão para os riscos aceitos.

⏺ Bash(python3 - <<'PYEOF'
      import pathlib…)
  ⎿  32:| 12 | Comportamentos novos fora da seção 7 | — | **manti
     33:| 13 | Redação e cantos do Unicode (rodada de confirmação
     148:| 12 | Registro desta revisão | — | commit da 1.0 (`c8bc
     … +10 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/DECISIONS.md (+3 -2)
      12  
      13  ## D-005 — Normalização: só letras e algarismos contam: spec 1.
          6 → 1.8 · `2026-10-01`
      14  
      15 -**Gatilho:** revisão independente da T-003 (`docs/reviews/T-003
         -.md`, revisão 1, BLOQUEADO). O passo 4 da seção 5 só tratava se
         -quências **internas** de separadores e o passo 1 só removia esp
         -aço em branco das pontas: hífen ou sublinhado no início ou no f
         -im não tinham resultado definido (`"-Bistro"` × `"_Bistro"` mud
         -am a RN-007). O passo 3 não dizia se `ø`, `ł`, `đ` contam como 
         -letra com sinal. O responsável decidiu os dois pontos (versão 1
         -.7, não commitada). A rodada do `spec-adversary` sobre a 1.7 ap
         -ontou 5 problemas (1 bloqueante): o conjunto de "hífens" e de "
         -espaços em branco" não estava fechado (travessão U+2013 colocad
         -o pelo editor, espaço de largura zero, BOM, caracteres de contr
         -ole). O responsável optou por trocar as listas por uma regra ún
         -ica, "só letras e algarismos contam". A rodada do `spec-adversa
         -ry` sobre essa versão apontou 5 problemas (2 bloqueantes): "let
         -ra", "algarismo decimal" e "sinal combinante" sem conjunto defi
         -nido (`Nº` × `N°`), e "espaço em branco" ainda aberto para `id`
         - e `colaborador`. O responsável aceitou as 5 recomendações (pon
         -tos 8 a 12), aplicadas na mesma versão 1.8. Sessão `docs/sessio
         -ns/13-*`.                                                      
      15 +**Gatilho:** revisão independente da T-003 (`docs/reviews/T-003
         +.md`, revisão 1, BLOQUEADO). O passo 4 da seção 5 só tratava se
         +quências **internas** de separadores e o passo 1 só removia esp
         +aço em branco das pontas: hífen ou sublinhado no início ou no f
         +im não tinham resultado definido (`"-Bistro"` × `"_Bistro"` mud
         +am a RN-007). O passo 3 não dizia se `ø`, `ł`, `đ` contam como 
         +letra com sinal. O responsável decidiu os dois pontos (versão 1
         +.7, não commitada). A rodada do `spec-adversary` sobre a 1.7 ap
         +ontou 5 problemas (1 bloqueante): o conjunto de "hífens" e de "
         +espaços em branco" não estava fechado (travessão U+2013 colocad
         +o pelo editor, espaço de largura zero, BOM, caracteres de contr
         +ole). O responsável optou por trocar as listas por uma regra ún
         +ica, "só letras e algarismos contam". A rodada do `spec-adversa
         +ry` sobre essa versão apontou 5 problemas (2 bloqueantes): "let
         +ra", "algarismo decimal" e "sinal combinante" sem conjunto defi
         +nido (`Nº` × `N°`), e "espaço em branco" ainda aberto para `id`
         + e `colaborador`. O responsável aceitou as 5 recomendações (pon
         +tos 8 a 12), aplicadas na mesma versão 1.8. A rodada de confirm
         +ação não apontou bloqueante; os 4 achados (uma contradição de r
         +edação e três cantos do Unicode sem efeito em dados realistas) 
         +foram registrados no ponto 13, como combinado com o responsável
         +. Sessão `docs/sessions/13-*`.                                 
      16  
      17  **O que mudou na spec:**
      18  
     ...
      30  | 10 | Fornecedor visualmente idêntico (invisível, letra de out
          ro alfabeto) | risco descrito só para a categoria | risco aceit
          o descrito também para o fornecedor, que não aparece na saída |
           seção 10 |
      31  | 11 | Formas de compatibilidade (largura total, sobrescritos) 
          | indefinido | distintas da forma comum; risco aceito | seção 1
          0 |
      32  | 12 | Comportamentos novos fora da seção 7 | — | **mantido**: 
          exemplos da seção 5 testados na T-003; seção 7 não muda (contag
          em de 63 casos preservada) | — |
      33 +| 13 | Redação e cantos do Unicode (rodada de confirmação) | "c
         +aracteres de controle não são espaço" contradizia tabulação e q
         +uebra de linha; letra invisível (U+3164), `º` × `°`, U+0345 e v
         +ersão do Unicode sem registro | exclusão vale só para controle 
         +sem White_Space (tabulação, LF, CR, NEL são espaço); demais cas
         +os num risco aceito único | RN-002, seção 10 |                 
      34  
      35  **Por quê:** os pontos 1 e 3 seguem a lógica da AMB-011: separa
          dor e sinal solto são diferença de grafia, não de significado (
          `"alimentacao-"` e `"Transporte – Urbano"` passam a ser reconhe
          cidas). Uma regra única ("só letras e algarismos") fecha o conj
          unto sem lista de caracteres, que seria incompleta por construç
          ão, e qualquer pessoa consegue conferir. O efeito colateral (ma
          is fornecedores iguais, como `"Padaria (Centro)"` = `"Padaria C
          entro"`) só pesa na RN-007, que também exige mesma data, catego
          ria e valor ao centavo. O ponto 6 vem junto: sem ele, `"-"` e `
          "?"` viram o mesmo fornecedor e se anulam como duplicatas, enqu
          anto `"   "` já era recusado. O ponto 2 evita tabela manual (al
          ternativa já descartada no DT-004). O ponto 5 registra o compor
          tamento escolhido; raro em dados em português.
      36  
     ...
      38  
      39  **Tasks afetadas:** T-003 (aceite com separadores de qualquer t
          ipo, sinal solto, `ø`, `ß`, `º`, `²`), T-008 e T-009 (espaço em
           branco pela propriedade White_Space; texto normalizado vazio).
      40  
      40 -**Custo:** 4 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`, `t
         -asks.md`); 12 pontos decididos na mesma sessão. Três rodadas do
         - `spec-adversary` (sobre a 1.7, sobre a primeira redação da 1.8
         - e de confirmação sobre a 1.8 final).                          
      41 +**Custo:** 4 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`, `t
         +asks.md`); 13 pontos decididos na mesma sessão. Três rodadas do
         + `spec-adversary` (sobre a 1.7, sobre a primeira redação da 1.8
         + e de confirmação sobre a 1.8 final).                          
      42  
      43  ---
      44  
  ⎿  Updated specs/001-motor-reembolso/spec.md (+2 -1)
      159  - **Despesa inválida** (vira item `recusado` com motivo `entra
           da_invalida`; as demais despesas seguem): elemento de `despesa
           s` que não é um objeto; falta `id`, `data`, `categoria`, `forn
           ecedor`, `valor` ou `tem_nota_fiscal`; `data` não é data válid
           a `AAAA-MM-DD`; `valor` não é número; `tem_nota_fiscal` não é 
           booleano; `id`, `categoria` ou `fornecedor` não são texto, ou 
           são texto vazio ou só com espaços em branco; `categoria` ou `f
           ornecedor` cujo texto normalizado (seção 5) fica vazio, como `
           "-"` ou `"***"`; `valor` com valor absoluto maior ou igual a 1
           .000.000.000,00 (um bilhão), comparado com o número recebido, 
           antes do arredondamento (AMB-018).
      160  - Na saída de uma despesa inválida, `id`, `data` e `categoria`
            são copiados se forem texto e saem nulos caso contrário (tipo
            errado, ausente ou elemento que não é objeto); a `categoria`,
            se reconhecida, sai normalizada, como em qualquer item (seção
            4).
      161  - Uma despesa recusada por `entrada_invalida` tem `valor_consi
           derado` nulo, `em_viagem` e `limite_diario` nulos, e não entra
            nos totais.
      162 -- Espaço em branco, nesta regra e em toda a spec, é o caracter
          -e com a propriedade White_Space do Unicode (espaço comum, tabu
          -lação, quebra de linha, espaço não separável e semelhantes). E
          -spaço de largura zero, BOM e caracteres de controle (como U+00
          -1C a U+001F) não são espaço em branco: um `id` ou `nome` feito
          - só deles é texto válido.                                     
      162 +- Espaço em branco, nesta regra e em toda a spec, é o caracter
          +e com a propriedade White_Space do Unicode (espaço comum, tabu
          +lação, quebra de linha, espaço não separável e semelhantes). T
          +abulação, quebra de linha (LF, CR) e NEL têm essa propriedade 
          +e são espaço em branco. Espaço de largura zero, BOM e caracter
          +es de controle sem essa propriedade (como U+001C a U+001F) não
          + são espaço em branco: um `id` ou `nome` feito só deles é text
          +o válido.                                                     
      163  - `id` (da despesa e do colaborador) e `nome` não passam pela 
           normalização da seção 5: só são repetidos, nunca comparados. U
           m `id` `"-"` é válido.
      164  - Campos extras, no arquivo ou nas despesas, são ignorados.
      165  **Origem:** necessidade operacional (a política não trata entr
           ada malformada); pontos 7 e 9 de D-001; AMB-018; D-005.
     ...
      548  - **Caminho ambíguo no aviso de chave repetida** (RN-013): cha
           ves com `.`, `[` ou `]`, vazias ou com quebra de linha aparece
           m no caminho sem escape. Dois caminhos diferentes podem gerar 
           o mesmo texto (`"a.b"` e `a` → `b`), e um campo extra pode ger
           ar aviso idêntico ao de um campo da seção 4 que entra no cálcu
           lo (chave extra `"periodo.inicio"` repetida na raiz produz o m
           esmo aviso que o `periodo.inicio` verdadeiro repetido) ou um t
           exto que imita outro aviso. Nenhum valor muda: o aviso só pode
            enganar o conferente sobre qual chave foi descartada. Aceito 
           para manter o aviso legível; na dúvida, o conferente consulta 
           o arquivo de entrada.
      549  - **Letra com traço próprio não vira letra base** (seção 5, pa
           sso 2): `ø`, `ł`, `đ` e semelhantes não têm decomposição canôn
           ica e ficam como estão, então `"Smørrebrød"` e `"Smorrebrod"` 
           são fornecedores diferentes na RN-007. Aceito porque são raras
            em dados em português e uma tabela própria de equivalências s
           eria incompleta por construção.
      550  - **Caractere invisível ou letra parecida de outro alfabeto** 
           (seção 5, passo 3): um espaço de largura zero ou um hífen suav
           e dentro da palavra é separador, e uma letra de outro alfabeto
            parecida com a latina (`о` cirílico) é letra distinta. Na cat
           egoria, `"ali\u200bmentacao"` vira `ali_mentacao` e sai `categ
           oria_fora_da_politica`; o conferente vê a categoria como veio.
            No fornecedor, `"Bistro Cen\u00adtral"` ou `"Bistrо Central"`
            (com `о` cirílico) não é duplicata de `"Bistro Central"`, e a
           s duas despesas são pagas até o limite do dia, **sem sinal na 
           saída** (o fornecedor não aparece nela). Aceito porque tratar 
           esses caracteres exigiria uma lista própria de equivalências, 
           incompleta por construção; o caso vem de colagem acidental ou 
           de fraude deliberada, que a conferência humana das notas cobre
           .
      551 +- **Classificação do Unicode decide os cantos** (seção 5, RN-0
          +02): o resultado segue as categorias e propriedades do Unicode
          + mesmo quando a aparência engana. Uma letra invisível (`ㅤ`, U
          ++3164) conta como letra: `"BistroㅤCentral"` não é duplicata d
          +e `"Bistro Central"` e um fornecedor só desse caractere é váli
          +do. `º` × `°` e letras modificadoras parecidas com pontuação (
          +`ʼ`, `ˊ`) dão fornecedores diferentes. U+0345 vira `ι` no pass
          +o 1 (caixa) e por isso não é descartado no passo 2. Uma versão
          + futura do Unicode pode reclassificar caracteres hoje não atri
          +buídos. Aceito porque nenhum desses casos muda resultado em da
          +dos realistas em português, e qualquer exceção exigiria lista 
          +própria, incompleta por construção.                           
      552  - **Formas de compatibilidade distintas da forma comum** (seçã
           o 5, passo 2): letras e algarismos em largura total (`ＡＬＩＭ
           ＥＮＴＡＣＡＯ`), sobrescritos e ligaduras que a equivalência 
           de caixa não desfaz continuam diferentes da forma comum; uma c
           ategoria em largura total sai `categoria_fora_da_politica`. Ac
           eito por ser improvável em dados em português e porque desfaze
           r compatibilidades mudaria também caracteres que a spec não pe
           de (ex.: `²` viraria `2`).
      553  - **Quase-duplicatas** (AMB-010): o mesmo gasto relançado com 
           data vizinha, valor diferente em um centavo ou fornecedor com 
           outra grafia (além do que a normalização da seção 5 cobre) não
            é detectado. Aceito porque qualquer critério aproximado seria
            regra inventada e poderia recusar gastos legítimos repetidos.

⏺ Agent "Confirmação adversarial spec 1.8" finished · 2m 40s

⏺ Resumo — T-003: Normalização de texto

  A T-003 está pronta para commit, mas no caminho a spec mudou bastante: seção 5
  reescrita, RN-002 e seção 10 ampliadas, de 1.6 para 1.8. Por isso proponho 4
  commits e preciso da sua aprovação.

  Arquivos alterados:
  - src/reembolso/normalizacao.py (modificado)
  - tests/test_normalizacao.py (novo)
  - docs/reviews/T-003.md (novo, com as revisões 1 a 4)
  - spec.md (1.6 → 1.8) e DECISIONS.md (D-005, 13 pontos), modificados
  - plan.md (1.1: DT-003 e DT-004) e tasks.md (1.1: aceites de T-003, T-008 e
    T-009), modificados

  Testes criados: 22 funções e 87 casos ao todo. Cada um cita o passo da seção 5
  ou o ponto da D-005 que verifica. Cobrem:
  - os exemplos da seção 5;
  - acento pré-composto e combinante;
  - sinais combinantes de qualquer tipo;
  - ø, ł, đ, ß, º/°, ʼ/’;
  - separadores de qualquer tipo nas pontas e no meio, incluindo invisíveis;
  - letras de outros alfabetos e algarismos de outras escritas;
  - ², ½, Ⅻ;
  - texto só de separadores, que fica vazio.

  Testes executados antes da implementação: a cada mudança de regra, os testes
  novos falharam pelo motivo certo, na asserção: primeiro 25, depois 7 e depois
  11. Os testes que entraram por pedido do revisor passaram de primeira, porque
  o código já cumpria aquela parte; servem para pegar implementações erradas.

  pytest: 87 passed. ruff: limpo.

  Revisão independente: APROVADO COM RESSALVAS na revisão 4, sem nenhuma decisão
  pendente.
  - As ressalvas médias eram testes faltando, e já estão acrescentados.
  - As baixas eram separar os commits de documentação e preservar a revisão 1;
    as duas estão atendidas.
  - Relatório em docs/reviews/T-003.md.

  Spec-adversary: três rodadas, de 1 bloqueante, 2 bloqueantes e 0 bloqueantes.
  Os achados da rodada de confirmação foram registrados assim:
  - Contradição de redação na RN-002: era minha e foi corrigida. A tabulação e a
    quebra de linha agora são explicitamente espaço em branco.
  - Três cantos do Unicode sem efeito em dados realistas: registrados como um
    único risco aceito na seção 10.

  Esses ajustes não mudam regra, então não rodei o adversário de novo, como na
  D-004.

  Decisões ou interpretações realizadas: nenhuma fora das que você tomou. Elas
  estão na D-005: pontas, ø, "só letras e algarismos", texto vazio vira
  entrada_invalida, White_Space e riscos aceitos.

  Lacunas:
  - A recusa de categoria/fornecedor cujo texto fica vazio depois da
    normalização é implementada na T-009, e o aceite dela já inclui isso.
  - Na T-008 e na T-009, validar id/nome exige não usar strip() puro, porque ele
    trata U+001C a U+001F como espaço. Isso está registrado no DT-003.
  - Nenhum valor do exemplo da seção 9 mudou.

  Commits propostos, nesta ordem:
  1. docs(spec): v1.8 normalização só letras e algarismos (D-005), com spec.md e
     DECISIONS.md
  2. docs(plan): v1.1 alinha DT-003 e DT-004 à spec 1.8
  3. docs(tasks): v1.1 atualiza aceites de T-003, T-008 e T-009
  4. feat(T-003): normalização de texto da seção 5, com o código, o teste e
     docs/reviews/T-003.md

  Depois disso vem docs(tasks): conclui T-003, que marca o [x] com o hash.

  Posso commitar?

✻ Cogitated for 13m 20s · done 11:08 PM

❯ pode commitar                                                                 

  Ran 1 shell command (ctrl+o to expand)

⏺ Agora marco a T-003 como concluída, com o hash do commit:
⏺ Bash(python3 - <<'PYEOF'
      import pathlib…)
  ⎿  pre-commit: commit sem código Python/testes/exemplos — ruff e pytest n
     ão se aplicam.
     … +6 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+2 -2)
      38    - **Aceite:** `tests/test_politica.py` passa: `test_rn009_lim
          ites_conferem_tabela_da_spec` (60/90, 80/120, 250/250), `test_r
          n006_tres_categorias_reconhecidas`, `test_rn008_valor_de_nota_e
          _100`, `test_rn002_teto_de_um_bilhao`, `test_rn010_viagem_cobre
          _d_e_d_mais_1`, `test_motivos_na_ordem_da_secao_8`; todas as co
          nstantes monetárias são `Decimal`.
      39    - **Commit:** 6e1f498
      40  
      41 -- [ ] **T-003** — Normalização de texto: `normalizar_texto()` c
         -om os passos da seção 5 da spec (DT-004).                      
      41 +- [x] **T-003** — Normalização de texto: `normalizar_texto()` c
         +om os passos da seção 5 da spec (DT-004).                      
      42    - **Tipo:** regra
      43    - **Atende:** seção 5 da spec (normalização), AMB-011, D-005;
           usada por RN-002, RN-006 e RN-007
      44    - **Depende de:** T-001
      45    - **Aceite:** `tests/test_normalizacao.py` passa: exemplos da
           seção 5 (`"Transporte Urbano"`, `"transporte-urbano"`, `" TRAN
          SPORTE__urbano "`, `"Transporte – Urbano"` → `transporte_urbano
          `; `"Pão  Quente"`, `"pao-quente"` → `pao_quente`; `"-Bistro"`,
           `"_Bistro"`, `"Bistro -"`, `" -_Bistro"` → `bistro`; `"Padaria
           (Centro)"` → `padaria_centro`; `"McDonald's"` → `mcdonald_s`; 
          `"Straße"` → `strasse`; `"Padaria Nº 1"` → `padaria_nº_1` e `"P
          adaria N° 1"` → `padaria_n_1`; `"Loja²"` → `loja`; `"Smørrebrød
          "` → `smørrebrød`; `"-"` → vazio); acento pré-composto e combin
          ante dão o mesmo resultado; `ç`, `ô`, `ü`, `ñ`; sinal combinant
          e solto (no início, sobre hífen no fim) é descartado; tabulação
          , quebra de linha, espaço não separável, espaço de largura zero
           e caractere de controle nas pontas; mistura de separadores int
          ernos de qualquer tipo vira um `_`; letras de qualquer alfabeto
           e algarismos decimais de qualquer escrita são mantidos como es
          tão; número que não é dígito decimal (`²`, `½`) é separador.
      46 -  - **Commit:**                                                
      46 +  - **Commit:** aaf201a                                        
      47  
      48  - [ ] **T-004** — Justificativa: `justificativa.py` gera a fras
          e em português de um item já decidido, para cada status e motiv
          o, com formatação própria `1.234,56` e `DD/MM` sem `locale` (DT
          -009).
      49    - **Tipo:** estrutura (texto não contratual)
  ⎿  PostToolUse:Bash says: 📝 Fim do bloco de trabalho ("docs(tasks): conclui 
     T-003"). Exporte a sessão antes de continuar:
        /export docs/sessions/13-<descricao-curta>.md
        e commite com: docs(sessions): export da sessão 13

⏺ A T-003 está concluída e commitada. Os hooks passaram em todos os commits: 87
  testes verdes e ruff limpo. O working tree está limpo.

  ┌─────────┬──────────────────────────────────────────────────────┐
  │ Commit  │                        O quê                         │
  ├─────────┼──────────────────────────────────────────────────────┤
  │ 6cc8554 │ docs(spec): spec 1.8 e entrada D-005 no DECISIONS.md │
  ├─────────┼──────────────────────────────────────────────────────┤
  │ d1671b0 │ docs(plan): plano 1.1 (DT-003 e DT-004)              │
  ├─────────┼──────────────────────────────────────────────────────┤
  │ 7b1e760 │ docs(tasks): aceites da T-003, T-008 e T-009         │
  ├─────────┼──────────────────────────────────────────────────────┤
  │ aaf201a │ feat(T-003): código, testes e docs/reviews/T-003.md  │
  ├─────────┼──────────────────────────────────────────────────────┤
  │ 8c5ca4b │ docs(tasks): T-003 marcada [x] com o hash aaf201a    │
  └─────────┴──────────────────────────────────────────────────────┘

  Para a próxima task: a T-008 e a T-009 já trazem no aceite as duas regras
  novas da RN-002. Uma é que texto que fica vazio depois da normalização é
  entrada_invalida. A outra é que "espaço em branco" segue o Unicode, e por isso
  a validação não pode usar o strip() puro do Python.

  📝 Fim do bloco de trabalho. Antes de continuar, exporte a sessão:
  /export docs/sessions/13-task-t003-normalizacao.md
  Depois é só commitar com docs(sessions): export da sessão 13 — task T-003. Não
  começo a próxima task sem você pedir.

✻ Crunched for 19s · done 11:09 PM