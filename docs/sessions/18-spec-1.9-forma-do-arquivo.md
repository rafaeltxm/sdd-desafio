 ▐▛███▛█   Claude Code v2.1.287
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~/repo/sdd-desafio

  Opus 5.5 is now your default model and it draws down usage faster than Sonnet 5. Switch anytime with /model.

❯ /clear                                                                        

❯ /task T-007                                                                   

  Searched for 2 patterns, ran 3 shell commands (ctrl+o to expand)

⏺ Li a T-007, a RN-013, a AMB-019 e a DT-010. Agora escrevo os testes da leitura
  e depois o ObjetoJson com o percurso que gera os avisos.

⏺ Write(tests/test_rn013_chave_repetida.py)
  ⎿  Wrote 192 lines to tests/test_rn013_chave_repetida.py
       1 """Chave repetida no arquivo de entrada: RN-013, AMB-019, DT-010
          (nível da leitura)."""
       2 
       4 from decimal import Decimal
       5 
       6 from reembolso.entrada import avisos_de_chave_repetida, ler_json
       7 
       9 def _aviso(caminho, n):
      10     return f"chave repetida: {caminho} ({n} ocorrências; valeu a
          última)"
     … +229 lines (ctrl+o to expand)

  Ran 1 shell command (ctrl+o to expand)

⏺ Falha por import (esperado). Para ver a falha pelo motivo certo, coloco um
  stub que não detecta nada e rodo de novo.

⏺ Bash(cat >> src/reembolso/entrada.py <<'EOF'…)
  ⎿  FAILED tests/test_rn013_chave_repetida.py::test_rn013_valor_duas_vezes
     _vale_a_ultima_com_aviso_no_elemento
     FAILED tests/test_rn013_chave_repetida.py::test_rn013_colaborador_nome
     … +17 lines (ctrl+o to expand)
  ⎿  Updated src/reembolso/entrada.py (+5 -0)
      40          raise ErroDeArquivo(f"arquivo não é JSON válido: {erro}
          ") from erro
      41      _verificar_textos(documento)
      42      return documento
      43 +                                                               
      44 +                                                               
      45 +def avisos_de_chave_repetida(documento):                       
      46 +    despesas = documento.get("despesas") if isinstance(document
         +o, dict) else None                                             
      47 +    return (), tuple(() for _ in despesas) if isinstance(despes
         +as, list) else ()                                              

⏺ 13 falham pela asserção (aviso ausente). Os 2 que passam são negativos (sem
  repetição; composta ≠ decomposta), e é esperado que um stub sem detecção passe
  neles. Agora a implementação:

  Ran 1 shell command (ctrl+o to expand)

⏺ Bash(python3 - <<'EOF'
      p = "tests/test_rn013_chave_repetida.py"…)
  ⎿  All checks passed!
     162 passed in 0.06s
      M src/reembolso/entrada.py
     … +89 lines (ctrl+o to expand)
  ⎿  Updated tests/test_rn013_chave_repetida.py (+3 -3)
      86  
      87  
      88  def test_rn013_aninhada_no_descartado_e_no_que_valeu_ordem_da_p
          rimeira_ocorrencia():
      89 -    """RN-013: ordem da primeira ocorrência; descartado não ent
         -ra no <n> nem na ordem."""                                     
      89 +    """RN-013: ordem da 1ª ocorrência; descartado não entra no 
         +<n> nem na ordem."""                                           
      90      campos = (
      91          '"valor": 10, "extra": {"x": 1, "x": 2}, "obs": "a", "o
          bs": "b", '
      92          '"extra": {"x": 3, "x": 4}'
      93      )
      94      documento, _, por_despesa = _ler(_documento("[" + _despesa(
          campos) + "]"))
      95 -    # extra (1ª ocorrência antes de obs), obs, extra.x (no valo
         -r que valeu, depois de obs)                                    
      95 +    # extra (1ª ocorrência antes de obs), obs, extra.x (no valo
         +r que valeu)                                                   
      96      assert por_despesa == (
      97          (_aviso("extra", 2), _aviso("obs", 2), _aviso("extra.x"
          , 2)),
      98      )
     ...
      100  
      101  
      102  def test_rn013_chave_com_escape_e_a_mesma_chave_decodificada()
           :
      103 -    """RN-013: igualdade depois de decodificados os escapes (`
          -\\u0076alor` = `valor`)."""                                   
      103 +    """RN-013: igualdade depois de decodificar escapes (`\\u00
          +76alor` = `valor`)."""                                        
      104      texto = _documento("[" + _despesa('"valor": 30.00, "\\u007
           6alor": 90.00') + "]")
      105      documento, _, por_despesa = _ler(texto)
      106      assert documento["despesas"][0]["valor"] == Decimal("90.00
           ")

⏺ Funciona; dois ajustes de limpeza: linha em branco extra e trocar a contagem
  manual por Counter.

⏺ Bash(python3 - <<'EOF'
      p = "src/reembolso/entrada.py"…)
  ⎿  All checks passed!
     162 passed in 0.06s
      src/reembolso/entrada.py | 67 +++++++++++++++++++++++++++++++++++++++
     … +4 lines (ctrl+o to expand)
  ⎿  Updated src/reembolso/entrada.py (+4 -6)
      1  """bytes → JSON → Entrada; erros de arquivo e despesas inválidas
          (RN-002, RN-013)."""
      2  
      3 +from collections import Counter                                 
      4  from decimal import Decimal
      5  
      6  import simplejson
     ...
      56      return documento
      57  
      58  
      58 -                                                               
      59  def _aviso(caminho: str, n: int) -> str:
      60      return f"chave repetida: {caminho} ({n} ocorrências; valeu 
          a última)"
      61  
     ...
      71      última, na posição dela; valores descartados nunca são visi
          tados.
      72      """
      73      if isinstance(valor, ObjetoJson):
      74 -        ocorrencias: dict[str, int] = {}                       
      75 -        for chave, _ in valor.pares:                           
      76 -            ocorrencias[chave] = ocorrencias.get(chave, 0) + 1 
      77 -        vistas: dict[str, int] = {}                            
      74 +        ocorrencias = Counter(chave for chave, _ in valor.pares
         +)                                                              
      75 +        vistas: Counter[str] = Counter()                       
      76          for chave, _ in valor.pares:
      79 -            vistas[chave] = vistas.get(chave, 0) + 1           
      77 +            vistas[chave] += 1                                 
      78              if vistas[chave] == 1 and ocorrencias[chave] > 1:
      79                  avisos.append(_aviso(_filho(caminho, chave), oc
          orrencias[chave]))
      80              if vistas[chave] == ocorrencias[chave]:

⏺ Suíte e ruff verdes. Agora a revisão independente.

⏺ revisor-de-task(Revisão independente T-007)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ O revisor-de-task está analisando a T-007. Assim que ele terminar, salvo o
  relatório em docs/reviews/T-007.md e apresento o resumo.

✻ Cogitated for 1m 53s · done 11:19 PM

› Message from revisor-de-task
  # Revisão T-007 — Chaves repetidas: `ObjetoJson` e avisos da RN-013 no nível
  da leitura

  - **Data:** 2026-10-01
  - **Regras conferidas:** RN-013, AMB-019, DT-010 (plan.md), D-004
  (DECISIONS.md), seção 4 (escapes), seção 7 (casos de borda da RN-013), seção
  10 (caminho ambíguo)
  - **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 162 passed, 0
  failed. Isso só mostra que código e testes concordam entre si.

  ### Resultado
  **BLOQUEADO**: quando o caminho passa por uma chave vazia (`""`), o ponto
  separador some e o texto do aviso fica diferente do formato de caminho da
  RN-013.

  ### Critérios de aceite
  | # | Critério | Status | Evidência |
  |---|---|---|---|
  | 1 | `valor` duas vezes → vale a última; aviso `chave repetida: valor (2
  ocorrências; valeu a última)` no elemento | atendido | `tests/test_rn013_chave
  _repetida.py::test_rn013_valor_duas_vezes_vale_a_ultima_com_aviso_no_elemento`
  |
  | 2 | `colaborador.nome` → aviso no topo com caminho a partir da raiz |
  atendido |
  `::test_rn013_colaborador_nome_repetido_avisa_no_topo_com_caminho_da_raiz` |
  | 3 | `valor` três vezes → um aviso com `3 ocorrências` | atendido |
  `::test_rn013_valor_tres_vezes_gera_um_aviso_com_3_ocorrencias` |
  | 4 | `despesas` repetida → só a última lista; um aviso `despesas`; chaves
  repetidas da lista descartada não geram aviso | atendido |
  `::test_rn013_despesas_repetida_so_ultima_lista_e_um_aviso_no_topo` |
  | 5 | `extra`/`obs`/`extra.x` na ordem `extra`, `obs`, `extra.x`, cada um com
  2 | atendido | `::test_rn013_aninhada_no_descartado_e_no_que_valeu_ordem_da_pr
  imeira_ocorrencia` (ordem refeita à mão: `extra` aparece pela primeira vez
  antes de `obs`; `extra.x` só sai ao descer no último `extra`, com 2
  ocorrências) |
  | 6 | `"valor"` igual a `valor` | atendido |
  `::test_rn013_chave_com_escape_e_a_mesma_chave_decodificada` |
  | 7 | Forma composta e forma decomposta são chaves diferentes | atendido |
  `::test_rn013_forma_composta_e_decomposta_sao_chaves_diferentes` (conferi os
  bytes: as linhas 115 e 116 usam U+00E9 e `e`+U+0301) |
  | 8 | `m[0][0].x` | atendido | `::test_rn013_lista_dentro_de_lista_no_caminho`
  |
  | 9 | Elemento que é lista → `[0].a` | atendido |
  `::test_rn013_elemento_de_despesas_que_e_lista_comeca_pela_posicao` e
  `::test_rn013_lista_dentro_de_elemento_lista_encadeia_colchetes` (`[0][0].a`)
  |
  | 10 | `obs` 1000 vezes → `1000 ocorrências` | atendido |
  `::test_rn013_obs_mil_vezes_sem_separador_de_milhar` |
  | 11 | Objeto sem repetição → nenhum aviso | atendido |
  `::test_rn013_objeto_sem_repeticao_nenhum_aviso` |

  ### Problemas encontrados
  #### 1. Chave vazia no caminho perde o ponto separador — severidade ALTA
  - **Regra afetada:** RN-013 (formato do caminho)
  - **Evidência:** `src/reembolso/entrada.py`, função `_filho`:
    ```python
    def _filho(caminho: str, chave: str) -> str:
        return f"{caminho}.{chave}" if caminho else chave
    ```
    O código usa a string vazia ao mesmo tempo como marca de "início do caminho"
  e como caminho legítimo de uma chave `""`. A spec diz: "Caminho: chaves
  separadas por ponto". A seção 10 e a D-004 item 5 tratam chaves vazias como
  possíveis e dizem que elas "aparecem no caminho sem escape".
  - **Impacto:** numa despesa com `"": {"x": 1, "x": 2}`, a sequência de chaves
  é `""`, `x`, e o caminho pela spec é `.x`. O código emite `chave repetida: x
  (2 ocorrências; valeu a última)`. Esse texto é idêntico ao aviso de uma chave
  `x` repetida no primeiro nível, um caso diferente que a seção 10 não lista
  como ambiguidade aceita. O mesmo acontece na raiz (`"": {"nome": 1, "nome":
  2}` sai como `nome` em vez de `.nome`). Status e valores não mudam, mas o
  texto de saída fica diferente do especificado.
  - **Recomendação:** separar "estou no início do caminho" de "o caminho é a
  string vazia". Por exemplo, a raiz e o início de cada despesa podem ser
  marcados com `None` ou com uma lista de segmentos. Acrescentar um teste com a
  chave vazia aninhada.

  #### 2. Repetição dentro da última lista de `despesas` repetida não é testada
  — severidade MÉDIA
  - **Regra afetada:** RN-013 ("chaves repetidas dentro de um valor descartado
  não geram aviso" e, por contraste, as do valor que valeu geram aviso no item)
  - **Evidência:** em
  `::test_rn013_despesas_repetida_so_ultima_lista_e_um_aviso_no_topo`, a última
  lista não tem nenhuma chave repetida (`por_despesa == ((), ())`). Uma
  implementação que deixasse de percorrer os elementos quando `despesas` está
  repetida também passaria nesse teste.
  - **Impacto:** fica sem verificação que, com `despesas` repetida, os avisos
  dos elementos da última lista ainda vão para cada item.
  - **Recomendação:** pôr uma chave repetida num elemento da última lista e
  conferir que o aviso aparece em `por_despesa`.

  #### 3. `despesas` aninhada fora da raiz não é testada — severidade BAIXA
  - **Regra afetada:** RN-013 (aviso no item só "dentro de um elemento de
  `despesas`"; os demais vão para o topo com caminho a partir da raiz)
  - **Evidência:** o código separa as despesas apenas na raiz (`ao_descer` só é
  passado na chamada da raiz), o que está correto. Mas nenhum teste cobre uma
  chave `despesas` aninhada (ex.: `colaborador.despesas[0].a` repetida), cujo
  aviso deve ir para o topo.
  - **Impacto:** não muda o resultado hoje; é proteção contra regressão.
  - **Recomendação:** um teste curto opcional.

  ### Cobertura
  - **Regras testadas:** RN-013 / AMB-019 / DT-010 → todos os 15 testes de
  `tests/test_rn013_chave_repetida.py` (todos citam RN-013 na docstring).
  - **Casos de borda cobertos:** última ocorrência vale; um aviso por chave;
  `<n>` = 3 e 1000; caminho a partir da raiz no topo; caminho relativo na
  despesa; valor descartado não visitado (`despesas` e `extra`); ordem pela
  primeira ocorrência; igualdade depois de decodificar o escape; sem
  normalização Unicode; `m[0][0].x`; `[0].a`; `[0][0].a`; `extra.lista[1].x`;
  elemento `null` gera tupla vazia na posição certa; ordem dos avisos do topo;
  ausência de avisos. Recalculei à mão todos os valores esperados a partir da
  spec e todos batem.
  - **Casos que parecem faltar:**
    - chave vazia no caminho (RN-013, seção 10; ver problema 1);
    - chave repetida dentro da última lista quando `despesas` está repetida
  (RN-013; ver problema 2);
    - `despesas` aninhada fora da raiz (RN-013; ver problema 3).
    - Os casos que dependem do motor (`tem_nota_fiscal` `true` e depois `"sim"`
  → `entrada_invalida`; `"valor"` 90,00 → `parcial` 60,00) são da T-012, não
  desta task.

  ### Decisões necessárias
  1. **Escape inválido dentro de um valor descartado.** A seção 4 diz que um
  escape que não forma caractere válido, "em qualquer chave ou valor", é erro de
  arquivo. A RN-013 diz que as ocorrências anteriores "são descartadas e
  nenhuma regra as considera". Hoje `_verificar_textos` percorre `dict.items()`,
  ou seja, só os valores que valeram. Cenário: despesa com `"obs": "\uD800",
  "obs": "ok"`. Pela seção 4 seria erro de arquivo, sem saída. Pela leitura
  atual do código, a despesa é processada com aviso de `obs`. Qual das duas
  vale? Esse comportamento vem da T-006 e não depende da mudança desta task,
  então **não bloqueia a T-007**. Mas fica exposto agora que o descarte é
  explícito.

  ### Antes de concluir a task
  - Corrigir `_filho` / `_percorrer` para que uma chave vazia apareça no caminho
  com o ponto separador (ex.: `.x`), conforme "chaves separadas por ponto" da
  RN-013. Acrescentar o teste correspondente.
  - Recomendado: reforçar o teste de `despesas` repetida com uma chave repetida
  num elemento da última lista (problema 2).
  - Opcional: teste de `despesas` aninhada fora da raiz (problema 3).
  - Registrar, para o humano, a pergunta sobre escape inválido em valor
  descartado (não bloqueia esta task).

  Arquivos revisados:
  `/Users/rafaeltxm/repo/sdd-desafio/src/reembolso/entrada.py`,
  `/Users/rafaeltxm/repo/sdd-desafio/tests/test_rn013_chave_repetida.py`,
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md`,
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/plan.md`,
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md`,
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/tasks.md`.

⏺ O revisor apontou um bug real (chave vazia no caminho perde o ponto). Salvo o
  relatório sem edição e depois corrijo.

⏺ Write(docs/reviews/T-007.md)
  ⎿  Wrote 67 lines to docs/reviews/T-007.md
       1 # Revisão T-007 — Chaves repetidas: `ObjetoJson` e avisos da RN-
       2 
       4 - **Regras conferidas:** RN-013, AMB-019, DT-010 (plan.md), D-00
         4 (DECISIONS.md), seção 4 (escapes), seção 7 (casos de borda da 
       5 - **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 1
         m entre si.
       7 ### Resultado
       8 **BLOQUEADO**: quando o caminho passa por uma chave vazia (`""`)
         rmato de caminho da RN-013.
      10 ### Critérios de aceite
     … +148 lines (ctrl+o to expand)

  Read 1 file (ctrl+o to expand)

⏺ Agent "Revisão independente T-007" finished · 1m 28s

⏺ Agora corrijo o caminho (None marca o início; "" passa a ser uma chave
  legítima) e acrescento os três testes que o revisor pediu.

⏺ Bash(python3 - <<'EOF'
      p = "src/reembolso/entrada.py"…)
  ⎿  All checks passed!
     164 passed in 0.07s
     (sem correção:)
  ⎿  Updated src/reembolso/entrada.py (+1 -66)
      1  """bytes → JSON → Entrada; erros de arquivo e despesas inválidas
          (RN-002, RN-013)."""
      2  
      3 -from collections import Counter                                 
      3  from decimal import Decimal
      4  
      5  import simplejson
     ...
       9      """Erro de arquivo da RN-002: nenhuma saída é gravada."""
      10  
      11  
      13 -class ObjetoJson(dict):                                        
      14 -    """Objeto JSON: vale a última ocorrência de cada chave; gua
         -rda os pares (DT-010)."""                                      
      15 -                                                               
      16 -    def __init__(self, pares):                                 
      17 -        super().__init__(pares)                                
      18 -        self.pares = tuple(pares)                              
      19 -                                                               
      20 -                                                               
      12  def _tem_substituto_isolado(texto: str) -> bool:
      13      """Caractere entre U+D800 e U+DFFF: escape sem caractere vá
          lido (seção 4)."""
      14      return any("\ud800" <= c <= "\udfff" for c in texto)
     ...
       35      except UnicodeDecodeError as erro:
       36          raise ErroDeArquivo("arquivo não está em UTF-8 válido"
           ) from erro
       37      try:
       47 -        documento = simplejson.loads(                         
       48 -            texto,                                            
       49 -            use_decimal=True,                                 
       50 -            parse_int=Decimal,                                
       51 -            object_pairs_hook=ObjetoJson,                     
       52 -        )                                                     
       38 +        documento = simplejson.loads(texto, use_decimal=True, 
          +parse_int=Decimal)                                            
       39      except simplejson.JSONDecodeError as erro:
       40          raise ErroDeArquivo(f"arquivo não é JSON válido: {erro
           }") from erro
       41      _verificar_textos(documento)
       42      return documento
       57 -                                                              
       58 -                                                              
       59 -def _aviso(caminho: str, n: int) -> str:                      
       60 -    return f"chave repetida: {caminho} ({n} ocorrências; valeu
          - a última)"                                                   
       61 -                                                              
       62 -                                                              
     … 45 more lines (ctrl+o to expand)
  ⎿  Updated tests/test_rn013_chave_repetida.py (+32 -5)
      70  def test_rn013_despesas_repetida_so_ultima_lista_e_um_aviso_no_
          topo():
      71      """RN-013: chaves repetidas dentro de valor descartado não 
          geram aviso."""
      72      primeira = "[" + _despesa('"valor": 1, "valor": 2') + "]"
      73 -    ultima = "[" + _despesa('"valor": 5') + ", " + _despesa('"v
         -alor": 6') + "]"                                               
      73 +    ultima = (                                                 
      74 +        "[" + _despesa('"valor": 5') + ", " + _despesa('"valor"
         +: 6, "valor": 7') + "]"                                        
      75 +    )                                                          
      76      texto = (
      77          '{"colaborador": {"id": "c-1", "nome": "Ana"}, '
      78          '"periodo": {"inicio": "2026-07-01", "fim": "2026-07-31
          "}, '
     ...
      80          '"despesas": ' + ultima + "}"
      81      )
      82      documento, topo, por_despesa = _ler(texto)
      81 -    # só a última lista (2 despesas: 5 e 6) é avaliada         
      82 -    assert [d["valor"] for d in documento["despesas"]] == [Deci
         -mal(5), Decimal(6)]                                            
      83 -    # o `valor` repetido da primeira lista não gera aviso      
      83 +    # só a última lista (2 despesas: 5 e 7) é avaliada         
      84 +    assert [d["valor"] for d in documento["despesas"]] == [Deci
         +mal(5), Decimal(7)]                                            
      85 +    # o `valor` repetido da primeira lista não gera aviso; o da
         + última vai ao item                                            
      86      assert topo == (_aviso("despesas", 2),)
      85 -    assert por_despesa == ((), ())                             
      87 +    assert por_despesa == ((), (_aviso("valor", 2),))          
      88  
      89  
      90  def test_rn013_aninhada_no_descartado_e_no_que_valeu_ordem_da_p
          rimeira_ocorrencia():
     ...
      147      assert por_despesa == ((_aviso("extra.lista[1].x", 2),),)
      148  
      149  
      150 +def test_rn013_chave_vazia_aparece_no_caminho_com_o_ponto():  
      151 +    """RN-013: chaves separadas por ponto, sem escape — a chav
          +e `""` também conta."""                                       
      152 +    campos = '"valor": 10, "": {"x": 1, "x": 2}'              
      153 +    texto = _documento(                                       
      154 +        "[" + _despesa(campos) + "]",                         
      155 +        colaborador='{"id": "c-1", "nome": "Ana", "": {"n": 1,
          + "n": 2}}',                                                   
      156 +    )                                                         
      157 +    _, topo, por_despesa = _ler(texto)                        
      158 +    # despesa: "" + "." + "x" → ".x"; raiz: "colaborador" + ".
          +" + "" + "." + "n"                                            
      159 +    assert por_despesa == ((_aviso(".x", 2),),)               
      160 +    assert topo == (_aviso("colaborador..n", 2),)             
      161 +                                                              
     … 16 more lines (ctrl+o to expand)

⏺ Esse stash reverteu a implementação inteira da T-007, não só a correção.
  Restauro antes de seguir:

⏺ Bash(git stash pop -q && git stash list && grep -c "caminho is None"
      src/reembolso/entrada.py && uv run pytest -q 2>&1 | tail -1)
  ⎿  1
     164 passed in 0.06s
  ⎿  Updated src/reembolso/entrada.py (+67 -1)
      1  """bytes → JSON → Entrada; erros de arquivo e despesas inválidas
          (RN-002, RN-013)."""
      2  
      3 +from collections import Counter                                 
      4  from decimal import Decimal
      5  
      6  import simplejson
     ...
      10      """Erro de arquivo da RN-002: nenhuma saída é gravada."""
      11  
      12  
      13 +class ObjetoJson(dict):                                        
      14 +    """Objeto JSON: vale a última ocorrência de cada chave; gua
         +rda os pares (DT-010)."""                                      
      15 +                                                               
      16 +    def __init__(self, pares):                                 
      17 +        super().__init__(pares)                                
      18 +        self.pares = tuple(pares)                              
      19 +                                                               
      20 +                                                               
      21  def _tem_substituto_isolado(texto: str) -> bool:
      22      """Caractere entre U+D800 e U+DFFF: escape sem caractere vá
          lido (seção 4)."""
      23      return any("\ud800" <= c <= "\udfff" for c in texto)
     ...
       44      except UnicodeDecodeError as erro:
       45          raise ErroDeArquivo("arquivo não está em UTF-8 válido"
           ) from erro
       46      try:
       38 -        documento = simplejson.loads(texto, use_decimal=True, 
          -parse_int=Decimal)                                            
       47 +        documento = simplejson.loads(                         
       48 +            texto,                                            
       49 +            use_decimal=True,                                 
       50 +            parse_int=Decimal,                                
       51 +            object_pairs_hook=ObjetoJson,                     
       52 +        )                                                     
       53      except simplejson.JSONDecodeError as erro:
       54          raise ErroDeArquivo(f"arquivo não é JSON válido: {erro
           }") from erro
       55      _verificar_textos(documento)
       56      return documento
       57 +                                                              
       58 +                                                              
       59 +def _aviso(caminho: str, n: int) -> str:                      
       60 +    return f"chave repetida: {caminho} ({n} ocorrências; valeu
          + a última)"                                                   
       61 +                                                              
       62 +                                                              
     … 46 more lines (ctrl+o to expand)

⏺ Restaurado. Agora confiro que o teste da chave vazia falha com o _filho antigo
  (monkeypatch numa execução avulsa, sem tocar no arquivo):

  Ran 1 shell command (ctrl+o to expand)

⏺ Falha pelo motivo certo com o código antigo, e passa com a correção. Rodo o
  revisor de novo.
⏺ revisor-de-task(Revisão independente T-007 (2))
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ O bug da chave vazia está corrigido e coberto por teste: 164 testes passam e o
  ruff está limpo. A segunda rodada do revisor-de-task está em andamento;
  quando terminar, acrescento o relatório como "Revisão 2" em
  docs/reviews/T-007.md e apresento o resumo.

  Um aviso sobre o que aconteceu no meio do caminho: para ver o teste falhar sem
  a correção, rodei um git stash que reverteu a implementação inteira da T-007,
  não só a correção. Restaurei logo em seguida com stash pop. A pilha de stash
  ficou vazia, a correção está no arquivo e a suíte continua verde. Depois
  disso, conferi o teste contra o código antigo trocando a função só durante uma
  execução avulsa, sem mexer no arquivo.

✻ Brewed for 1m 3s · done 11:21 PM

› Message from revisor-de-task
  # Revisão T-007 — Chaves repetidas: `ObjetoJson` e avisos da RN-013 no nível
  da leitura

  - **Data:** 2026-10-01
  - **Regras conferidas:** RN-013, AMB-019, DT-010 (plan.md), D-004 itens 2, 4–9
  (DECISIONS.md), seção 4 (escapes), seção 7 (casos de borda da RN-013), seção
  10 (caminho ambíguo)
  - **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 164 passed, 0
  failed (evidência, não veredito). `uv run --frozen ruff check .` → sem erros.

  ### Resultado
  **APROVADO COM RESSALVAS** — todos os critérios de aceite estão atendidos e os
  problemas da revisão anterior foram corrigidos. Sobram uma observação BAIXA e
  uma decisão em aberto que vem da T-006 e não bloqueia esta task.

  ### Critérios de aceite
  | # | Critério | Status | Evidência |
  |---|---|---|---|
  | 1 | `valor` duas vezes → vale a última; aviso `chave repetida: valor (2
  ocorrências; valeu a última)` no elemento | atendido | `tests/test_rn013_chave
  _repetida.py::test_rn013_valor_duas_vezes_vale_a_ultima_com_aviso_no_elemento`
  |
  | 2 | `colaborador.nome` → aviso no topo com caminho a partir da raiz |
  atendido |
  `::test_rn013_colaborador_nome_repetido_avisa_no_topo_com_caminho_da_raiz`,
  `::test_rn013_topo_com_caminho_aninhado_e_ordem_do_arquivo` |
  | 3 | `valor` três vezes → um aviso com `3 ocorrências` | atendido |
  `::test_rn013_valor_tres_vezes_gera_um_aviso_com_3_ocorrencias` |
  | 4 | `despesas` repetida → só a última lista; um aviso `despesas`; chaves
  repetidas da lista descartada sem aviso | atendido |
  `::test_rn013_despesas_repetida_so_ultima_lista_e_um_aviso_no_topo`. A lista
  descartada tem `valor` repetido e não gera aviso. A última lista tem `valor`
  repetido no 2º elemento e o aviso vai para esse item (`((), (aviso valor
  2,))`). |
  | 5 | `extra`/`obs`/`extra.x` na ordem `extra`, `obs`, `extra.x`, cada um com
  2 | atendido | `::test_rn013_aninhada_no_descartado_e_no_que_valeu_ordem_da_pr
  imeira_ocorrencia`. Refeito à mão: a 1ª ocorrência de `extra` vem antes de
  `obs`; `extra.x` só aparece no `extra` que valeu, depois de `obs`, com 2
  ocorrências (o descartado não conta). |
  | 6 | `"valor"` igual a `valor` | atendido |
  `::test_rn013_chave_com_escape_e_a_mesma_chave_decodificada` |
  | 7 | Forma composta e forma decomposta são chaves diferentes | atendido |
  `::test_rn013_forma_composta_e_decomposta_sao_chaves_diferentes`. Pelos bytes,
  as linhas 117–118 usam U+00E9 e `e`+U+0301, respectivamente. |
  | 8 | `m[0][0].x` | atendido | `::test_rn013_lista_dentro_de_lista_no_caminho`
  |
  | 9 | Elemento-lista `[0].a` | atendido |
  `::test_rn013_elemento_de_despesas_que_e_lista_comeca_pela_posicao` (também
  `[0][0].a` em
  `::test_rn013_lista_dentro_de_elemento_lista_encadeia_colchetes`) |
  | 10 | `obs` 1000 vezes → `1000 ocorrências` | atendido |
  `::test_rn013_obs_mil_vezes_sem_separador_de_milhar` (confere também que o
  valor que vale é `"999"`) |
  | 11 | Objeto sem repetição → nenhum aviso | atendido |
  `::test_rn013_objeto_sem_repeticao_nenhum_aviso` |

  ### Problemas encontrados
  #### 1. Asserção final de `test_rn013_objeto_sem_repeticao_nenhum_aviso` não
  verifica regra — severidade BAIXA
  - **Regra afetada:** nenhuma regra determina isto
  - **Evidência:** a última linha do teste, `json.loads(json.dumps(documento,
  default=str))["despesas"][0]["id"] == "d-1"`, só confirma que `ObjetoJson`
  serializa como `dict`. Não verifica nenhum comportamento da RN-013.
  - **Impacto:** nenhum no resultado. As asserções de RN-013 do mesmo teste
  (`topo == ()`, `por_despesa == ((),)`) estão corretas.
  - **Recomendação:** opcional. Pode ficar como teste de integridade estrutural.

  Os três problemas da revisão anterior (`docs/reviews/T-007.md`, ainda não
  rastreado) foram resolvidos:
  - **Chave vazia no caminho:** `_filho` agora usa `None` como início do caminho
  (`src/reembolso/entrada.py`, `_filho`/`_percorrer`). O teste
  `::test_rn013_chave_vazia_aparece_no_caminho_com_o_ponto` espera `.x` e
  `colaborador..n`, que é o que dá "chaves separadas por ponto" aplicado à
  sequência `""`,`x` e `colaborador`,`""`,`n`.
  - **Repetição na última lista de `despesas`:** agora testada.
  - **`despesas` aninhada fora da raiz:** agora testada em
  `::test_rn013_despesas_fora_da_raiz_avisa_no_topo`, que espera o caminho
  `colaborador.despesas[0].a` no topo.

  ### Cobertura
  - **Regras testadas:** RN-013 / AMB-019 / DT-010 → os 17 testes de
  `tests/test_rn013_chave_repetida.py`. Todos citam RN-013 na docstring.
  - **Casos de borda cobertos:**
    - vale a última ocorrência; um aviso por chave; `<n>` = 2, 3 e 1000, sem
  separador;
    - caminho a partir da raiz no topo e relativo na despesa;
    - valor descartado não é visitado (`despesas` e `extra`); ordem pela
  primeira ocorrência, no topo e no item;
    - igualdade depois de decodificar o escape; sem normalização Unicode;
    - caminhos `m[0][0].x`, `[0].a`, `[0][0].a`, `extra.lista[1].x`, `.x`,
  `colaborador..n`;
    - elemento `null` em `despesas` gera tupla vazia na posição certa;
  `despesas` aninhada vai para o topo; ausência de avisos.
    - Recalculei à mão, a partir da spec, todos os valores esperados, e todos
  batem.
  - **Casos que parecem faltar:**
    - Os casos que dependem do motor ficam para a T-012, fora do escopo desta
  task:
      - `tem_nota_fiscal` `true` e depois `"sim"` → `entrada_invalida` com
  aviso;
      - `"valor"` 90,00 → `parcial` 60,00.
    - Escape inválido dentro de um valor descartado: depende de decisão
  (abaixo).

  ### Decisões necessárias
  1. **Escape inválido dentro de um valor descartado** (pendente desde a revisão
  anterior, comportamento vindo da T-006). A seção 4 diz que um escape que não
  forma caractere válido "em qualquer chave ou valor" é erro de arquivo
  (RN-002). A RN-013 diz que as ocorrências anteriores "são descartadas e
  nenhuma regra as considera". Hoje `_verificar_textos` percorre `dict.items()`,
  ou seja, só os valores que valeram.
     - **Cenário:** despesa com `"obs": "\uD800", "obs": "ok"`.
     - **Pela leitura literal da seção 4:** erro de arquivo, sem saída.
     - **Pelo código atual:** a despesa é processada com o aviso `chave
  repetida: obs (2 ocorrências; valeu a última)`.
     - Qual das duas vale? Isso não depende das linhas alteradas nesta task,
  então não bloqueia a T-007. Precisa de resposta antes da T-012/T-019, que
  tratam a saída e o erro de arquivo de ponta a ponta.

  ### Antes de concluir a task
  Nada bloqueia o commit. Pendências:
  - Encaminhar ao humano a Decisão necessária 1. Se ela mudar o comportamento,
  registrar em spec + `DECISIONS.md` e ajustar `_verificar_textos` na task
  correspondente.
  - Opcional: problema 1 (BAIXA).
  - Esta revisão deve substituir o `docs/reviews/T-007.md` não rastreado, que é
  da rodada anterior (BLOQUEADO).

  Arquivos revisados:
  - `/Users/rafaeltxm/repo/sdd-desafio/src/reembolso/entrada.py`
  - `/Users/rafaeltxm/repo/sdd-desafio/tests/test_rn013_chave_repetida.py`
  - `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md`
  - `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/plan.md`
  - `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md`
  - `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/tasks.md`
  - `/Users/rafaeltxm/repo/sdd-desafio/docs/reviews/T-007.md`

⏺ O revisor aprovou com ressalvas. Acrescento o relatório como "Revisão 2" (a
  skill manda acrescentar, não substituir) e removo a asserção sem regra que ele
  apontou como BAIXA.

⏺ Bash(cat >> docs/reviews/T-007.md <<'EOF'…)
  ⎿  All checks passed!
     164 passed in 0.07s
      M src/reembolso/entrada.py
     … +5 lines (ctrl+o to expand)
  ⎿  Updated docs/reviews/T-007.md (+78 -0)
       65  - Registrar, para o humano, a pergunta sobre escape inválido e
           m valor descartado (não bloqueia esta task).
       66  
       67  Arquivos revisados: `/Users/rafaeltxm/repo/sdd-desafio/src/ree
           mbolso/entrada.py`, `/Users/rafaeltxm/repo/sdd-desafio/tests/t
           est_rn013_chave_repetida.py`, `/Users/rafaeltxm/repo/sdd-desaf
           io/specs/001-motor-reembolso/spec.md`, `/Users/rafaeltxm/repo/
           sdd-desafio/specs/001-motor-reembolso/plan.md`, `/Users/rafael
           txm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md`, 
           `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/t
           asks.md`.
       68 +                                                              
       69 +---                                                           
       70 +                                                              
       71 +## Revisão 2                                                  
       72 +                                                              
       73 +# Revisão T-007 — Chaves repetidas: `ObjetoJson` e avisos da R
          +N-013 no nível da leitura                                     
       74 +                                                              
       75 +- **Data:** 2026-10-01                                        
       76 +- **Regras conferidas:** RN-013, AMB-019, DT-010 (plan.md), D-
          +004 itens 2, 4–9 (DECISIONS.md), seção 4 (escapes), seção 7 (c
          +asos de borda da RN-013), seção 10 (caminho ambíguo)          
       77 +- **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` →
          + 164 passed, 0 failed (evidência, não veredito). `uv run --fro
          +zen ruff check .` → sem erros.                                
       78 +                                                              
       79 +### Resultado                                                 
       80 +**APROVADO COM RESSALVAS** — todos os critérios de aceite estã
          +o atendidos e os problemas da revisão anterior foram corrigido
          +s. Sobram uma observação BAIXA e uma decisão em aberto que vem
          + da T-006 e não bloqueia esta task.                           
       81 +                                                              
       82 +### Critérios de aceite                                       
       83 +| # | Critério | Status | Evidência |                         
       84 +|---|---|---|---|                                             
       85 +| 1 | `valor` duas vezes → vale a última; aviso `chave repetid
          +a: valor (2 ocorrências; valeu a última)` no elemento | atendi
          +do | `tests/test_rn013_chave_repetida.py::test_rn013_valor_dua
          +s_vezes_vale_a_ultima_com_aviso_no_elemento` |                
       86 +| 2 | `colaborador.nome` → aviso no topo com caminho a partir 
          +da raiz | atendido | `::test_rn013_colaborador_nome_repetido_a
          +visa_no_topo_com_caminho_da_raiz`, `::test_rn013_topo_com_cami
          +nho_aninhado_e_ordem_do_arquivo` |                            
       87 +| 3 | `valor` três vezes → um aviso com `3 ocorrências` | aten
          +dido | `::test_rn013_valor_tres_vezes_gera_um_aviso_com_3_ocor
          +rencias` |                                                    
       88 +| 4 | `despesas` repetida → só a última lista; um aviso `despe
          +sas`; chaves repetidas da lista descartada sem aviso | atendid
          +o | `::test_rn013_despesas_repetida_so_ultima_lista_e_um_aviso
          +_no_topo`. A lista descartada tem `valor` repetido e não gera 
          +aviso. A última lista tem `valor` repetido no 2º elemento e o 
          +aviso vai para esse item (`((), (aviso valor 2,))`). |        
       89 +| 5 | `extra`/`obs`/`extra.x` na ordem `extra`, `obs`, `extra.
          +x`, cada um com 2 | atendido | `::test_rn013_aninhada_no_desca
          +rtado_e_no_que_valeu_ordem_da_primeira_ocorrencia`. Refeito à 
          +mão: a 1ª ocorrência de `extra` vem antes de `obs`; `extra.x` 
          +só aparece no `extra` que valeu, depois de `obs`, com 2 ocorrê
          +ncias (o descartado não conta). |                             
       90 +| 6 | `"valor"` igual a `valor` | atendido | `::test_rn013_cha
          +ve_com_escape_e_a_mesma_chave_decodificada` |                 
       91 +| 7 | Forma composta e forma decomposta são chaves diferentes 
          +| atendido | `::test_rn013_forma_composta_e_decomposta_sao_cha
          +ves_diferentes`. Pelos bytes, as linhas 117–118 usam U+00E9 e 
          +`e`+U+0301, respectivamente. |                                
       92 +| 8 | `m[0][0].x` | atendido | `::test_rn013_lista_dentro_de_l
          +ista_no_caminho` |                                            
       93 +| 9 | Elemento-lista `[0].a` | atendido | `::test_rn013_elemen
          +to_de_despesas_que_e_lista_comeca_pela_posicao` (também `[0][0
          +].a` em `::test_rn013_lista_dentro_de_elemento_lista_encadeia_
          +colchetes`) |                                                 
       94 +| 10 | `obs` 1000 vezes → `1000 ocorrências` | atendido | `::t
          +est_rn013_obs_mil_vezes_sem_separador_de_milhar` (confere tamb
          +ém que o valor que vale é `"999"`) |                          
       95 +| 11 | Objeto sem repetição → nenhum aviso | atendido | `::tes
          +t_rn013_objeto_sem_repeticao_nenhum_aviso` |                  
       96 +                                                              
       97 +### Problemas encontrados                                     
       98 +#### 1. Asserção final de `test_rn013_objeto_sem_repeticao_nen
          +hum_aviso` não verifica regra — severidade BAIXA              
       99 +- **Regra afetada:** nenhuma regra determina isto             
      100 +- **Evidência:** a última linha do teste, `json.loads(json.dum
          +ps(documento, default=str))["despesas"][0]["id"] == "d-1"`, só
          + confirma que `ObjetoJson` serializa como `dict`. Não verifica
          + nenhum comportamento da RN-013.                              
      101 +- **Impacto:** nenhum no resultado. As asserções de RN-013 do 
          +mesmo teste (`topo == ()`, `por_despesa == ((),)`) estão corre
          +tas.                                                          
      102 +- **Recomendação:** opcional. Pode ficar como teste de integri
          +dade estrutural.                                              
      103 +                                                              
      104 +Os três problemas da revisão anterior (`docs/reviews/T-007.md`
          +, ainda não rastreado) foram resolvidos:                      
     … 41 more lines (ctrl+o to expand)
  ⎿  Updated tests/test_rn013_chave_repetida.py (+1 -4)
      1  """Chave repetida no arquivo de entrada: RN-013, AMB-019, DT-010
          (nível da leitura)."""
      2  
      3 -import json                                                     
      3  from decimal import Decimal
      4  
      5  from reembolso.entrada import avisos_de_chave_repetida, ler_json
     ...
      209  
      210  def test_rn013_objeto_sem_repeticao_nenhum_aviso():
      211      """RN-013: sem chave repetida, nenhum aviso no topo nem no
           s itens."""
      213 -    documento, topo, por_despesa = _ler(                      
      212 +    _, topo, por_despesa = _ler(                              
      213          _documento("[" + _despesa('"valor": 10, "extra": {"a":
            [1, {"b": 2}]}') + "]")
      214      )
      215      assert topo == ()
      216      assert por_despesa == ((),)
      218 -    # o documento continua se comportando como dict comum     
      219 -    assert json.loads(json.dumps(documento, default=str))["des
          -pesas"][0]["id"] == "d-1"                                     

⏺ Agent "Revisão independente T-007 (2)" finished · 1m 8s

⏺ Resumo — T-007: chaves repetidas (ObjetoJson e avisos da RN-013)

  A T-007 está pronta e aprovada com ressalvas na segunda revisão. Fica uma
  pergunta de spec para você responder, vinda da T-006; ela não bloqueia este
  commit.

  Arquivos alterados:
  - src/reembolso/entrada.py (modificado):
    - ObjetoJson (subclasse de dict em que vale a última ocorrência e que guarda
      os pares originais) ligado ao object_pairs_hook;
    - avisos_de_chave_repetida(documento), que devolve (avisos do topo, avisos 
      de cada elemento de despesas).
  - tests/test_rn013_chave_repetida.py (novo).
  - docs/reviews/T-007.md (novo; Revisão 1 e Revisão 2, sem edição).

  Testes criados (17, todos para RN-013 / AMB-019 / DT-010):
  - Aceite da task:
    - valor duas vezes vale a última, com aviso no item;
    - colaborador.nome com aviso no topo;
    - valor três vezes gera 3 ocorrências;
    - despesas repetida: só a última lista vale e a lista descartada não gera
      aviso;
    - ordem extra, obs, extra.x;
    - chave escrita com escape (\u0076alor) é a mesma chave valor;
    - forma composta e decomposta de letra acentuada são chaves diferentes;
    - caminhos m[0][0].x, [0].a e [0][0].a;
    - obs 1000 vezes gera 1000 ocorrências;
    - objeto sem repetição não gera aviso.
  - Extras:
    - extra.lista[1].x;
    - elemento null em despesas fica com lista de avisos vazia na posição certa;
    - ordem dos avisos do topo;
    - chave vazia no caminho (.x, colaborador..n);
    - despesas aninhada fora da raiz avisa no topo.

  Testes antes da implementação:
  - Primeiro falharam por erro de import, o que era esperado.
  - Com um stub que não detectava nada, 13 falharam na asserção, pelo motivo
    certo. Os 2 que passaram são os negativos (sem repetição; composta ≠
    decomposta), o que é esperado para um stub vazio.
  - O teste da chave vazia falha com o código antigo e passa com a correção.

  Testes depois: uv run pytest -q e uv run ruff check .
  pytest: 164 passed, 0 failed
  ruff: limpo

  Revisão independente:
  - Revisão 1: BLOQUEADO. A chave "" perdia o ponto no caminho. Corrigi usando
    None como marca de início do caminho e acrescentei os testes de chave vazia,
    de repetição dentro da última lista de despesas e de despesas aninhada.
  - Revisão 2: APROVADO COM RESSALVAS. A única ressalva de código foi uma
    asserção que não testava regra nenhuma (BAIXA); já removi.

  Decisões ou interpretações realizadas:
  - Chave vazia no caminho: apliquei "chaves separadas por ponto" ao pé da
    letra, então "" e depois x vira .x. A spec não traz exemplo desse caso, mas
    a seção 10 já aceita que chaves vazias aparecem no caminho sem escape.

  Lacunas ou dúvidas — precisam de decisão sua:
  1. Escape inválido dentro de um valor descartado.
     - Exemplo: "obs": "\uD800", "obs": "ok".
     - A seção 4 diz que escape inválido "em qualquer chave ou valor" é erro de
       arquivo. A RN-013 diz que as ocorrências descartadas "nenhuma regra as
       considera".
     - Hoje o código só verifica os valores que valeram, então essa despesa é
       processada com aviso de obs.
     - O comportamento vem da T-006 e não bloqueia a T-007, mas a resposta
       precisa entrar na spec e no DECISIONS.md antes da T-012/T-019.
  2. Os casos do Aceite da RN-013 que dependem do motor (tem_nota_fiscal true e
     depois "sim"; "valor" 90,00 dando parcial com 60,00) ficaram para a T-012,
     como o tasks.md prevê.

  Commit proposto: feat(T-007): chaves repetidas com última ocorrência e avisos 
  da RN-013

  Posso fazer o commit?

✻ Baked for 6m 10s · done 11:23 PM

❯ pode fazer o commit                                                           

  Ran 1 shell command (ctrl+o to expand)

⏺ Bash(python3 - <<'EOF'
      p = "specs/001-motor-reembolso/tasks.md"…)
  ⎿   specs/001-motor-reembolso/tasks.md | 4 ++--
      1 file changed, 2 insertions(+), 2 deletions(-)
     pre-commit: commit sem código Python/testes/exemplos — ruff e pytest n
     … +10 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+2 -2)
      68    - **Aceite:** `tests/test_leitura_json.py` passa: `test_rn002
          _nan_e_erro_de_arquivo` (`NaN`, `Infinity`, `-Infinity`); `test
          _rn002_json_malformado_e_erro_de_arquivo`; `test_rn002_utf8_inv
          alido_e_erro_de_arquivo`; `test_rn002_escape_sem_par_em_valor_e
          _erro_de_arquivo` e `..._em_chave_...` (`\ud800`); `test_bom_e_
          aceito`; `test_numero_lido_pelo_valor_exato` (`33.333`, `999999
          999.99999999999`, `1e999999`, `1e-999999` e inteiro de 5.000 dí
          gitos lidos como `Decimal` exato, sem erro); `test_escapes_vali
          dos_decodificados` (`"2026-07-03"` → `2026-07-03`; emoji em par
           de escapes igual ao emoji direto).
      69    - **Commit:** e84693c
      70  
      71 -- [ ] **T-007** — Chaves repetidas: `ObjetoJson` via `object_pa
         -irs_hook` (vale a última ocorrência) e percurso que gera os avi
         -sos do topo e de cada elemento de `despesas`, com texto, caminh
         -o, contagem e ordem da RN-013 (DT-010).                        
      71 +- [x] **T-007** — Chaves repetidas: `ObjetoJson` via `object_pa
         +irs_hook` (vale a última ocorrência) e percurso que gera os avi
         +sos do topo e de cada elemento de `despesas`, com texto, caminh
         +o, contagem e ordem da RN-013 (DT-010).                        
      72    - **Tipo:** regra
      73    - **Atende:** RN-013, AMB-019, DT-010
      74    - **Depende de:** T-006
      75    - **Aceite:** `tests/test_rn013_chave_repetida.py` passa, cob
          rindo o **Aceite** da RN-013 no nível da leitura: `valor` duas 
          vezes → vale a última, aviso `chave repetida: valor (2 ocorrênc
          ias; valeu a última)` no elemento; `colaborador.nome` → aviso n
          o topo com caminho da raiz; `valor` três vezes → um aviso com `
          3 ocorrências`; `despesas` repetida → só a última lista, um avi
          so `despesas`, chaves repetidas da lista descartada sem aviso; 
          `extra`/`obs`/`extra.x` na ordem `extra`, `obs`, `extra.x`, cad
          a um com 2; `"valor"` igual a `valor`; forma composta e decompo
          sta de letra acentuada são chaves diferentes; `m[0][0].x`; elem
          ento-lista `[0].a`; `obs` 1000 vezes → `1000 ocorrências`; obje
          to sem repetição → nenhum aviso.
      76 -  - **Commit:**                                                
      76 +  - **Commit:** ae9e75b                                        
      77  
      78  - [ ] **T-008** — Validação do cabeçalho: `colaborador`, `perio
          do` e `despesas` conforme o primeiro item da RN-002; erro → `Er
          roDeArquivo`. `competencia` copiada se texto, senão nula.
      79    - **Tipo:** regra
  ⎿  PostToolUse:Bash says: 📝 Fim do bloco de trabalho ("docs(tasks): conclui 
     T-007"). Exporte a sessão antes de continuar:
        /export docs/sessions/17-<descricao-curta>.md
        e commite com: docs(sessions): export da sessão 17

⏺ A T-007 está commitada e marcada como concluída:
  - ae9e75b feat(T-007): chaves repetidas com última ocorrência e avisos da 
    RN-013 (os hooks rodaram ruff e pytest antes do commit: 164 passed)
  - 4ac5f08 docs(tasks): conclui T-007

  📝 Fim do bloco: exporte a sessão antes de continuar:
  /export docs/sessions/17-<descricao-curta>.md
  e commite com docs(sessions): export da sessão 17.

  Ainda falta você decidir o caso do escape inválido dentro de um valor
  descartado ("obs": "\uD800", "obs": "ok"). Hoje o código processa essa despesa
  e só avisa a chave obs repetida. Se a seção 4 prevalecer, isso passa a ser
  erro de arquivo. A resposta precisa entrar na spec e no DECISIONS.md antes da
  T-012 e da T-019.

  Não vou começar a próxima task sem um novo pedido seu.

✻ Worked for 11s · done 11:24 PM

❯ me ajudar na descricao do documento para export                               

  Listed 1 directory (ctrl+o to expand)

⏺ Pelos nomes das exportações anteriores, sugiro:

  /export docs/sessions/17-task-t007-chaves-repetidas.md

  Segue o padrão das sessões 12 e 13 (NN-task-tNNN-<tema>), que são mais fáceis
  de achar depois. Se preferir o formato curto das 15 e 16, use 17-task-t007.md.

  Depois de exportar, o commit fica assim:
  docs(sessions): export da sessão 17 — task T-007

✻ Brewed for 5s · done 11:24 PM

❯ /export docs/sessions/17-task-t007-chaves-repetidas.md                        
  ⎿  Conversation exported to: /Users/rafaeltxm/repo/sdd-desafio/docs/sessions/1
     7-task-t007-chaves-repetidas.md

❯ fiz o export                                                                  

⏺ Export salvo em docs/sessions/17-task-t007-chaves-repetidas.md. Ainda não
  commitei. Quer que eu faça o commit com esta mensagem?

  docs(sessions): export da sessão 17 — task T-007

✻ Cogitated for 3s · done 11:25 PM

❯ pode commitar                                                                 

  Ran 1 shell command (ctrl+o to expand)

⏺ Commitei o export: ee2404a docs(sessions): export da sessão 17 — task T-007.
  Não ficou nada pendente no repositório.

  Antes da T-012 e da T-019, falta você decidir o caso do escape inválido dentro
  de um valor descartado ("obs": "\uD800", "obs": "ok"). Hoje o código processa
  essa despesa e só avisa a chave obs repetida. Se valer a seção 4, isso passa
  a ser erro de arquivo. A resposta vai para a spec e para o DECISIONS.md.

  A próxima task na ordem é a T-008 (validação do cabeçalho); só começo quando
  você pedir.

✻ Baked for 6s · done 11:25 PM

❯ nao entendi essa questao que precisamos decidir, me explique de outra forma   

⏺ O ponto é este: quando o texto quebrado aparece só na parte que a regra de
  chave repetida manda ignorar, a spec não diz claramente qual das duas regras
  ganha.

  O texto quebrado

  No JSON, alguns caracteres (como emojis) podem ser escritos como dois códigos
  de escape que só funcionam juntos, por exemplo \uD83D\uDE00 para 😀. Se
  aparece só uma das metades, como \uD800 sozinho, o texto fica com um caractere
  quebrado, que nem pode ser gravado no arquivo de saída.

  As duas regras da spec

  1. Seção 4: caractere quebrado em qualquer lugar do arquivo é erro de arquivo.
     A execução para e nenhuma saída é gerada.
  2. RN-013: se uma chave aparece duas vezes no mesmo objeto, vale a última, e
     as anteriores são descartadas e "nenhuma regra as considera".

  Onde elas batem de frente

  { "id": "d-1", "valor": 50.00, ...,
    "obs": "\uD800",
    "obs": "ok" }

  O caractere quebrado está só no primeiro obs, que a RN-013 manda descartar.

  - Pela regra 1: o arquivo tem um caractere quebrado, então é erro de arquivo e
    nenhuma despesa é processada.
  - Pela regra 2: esse obs foi descartado e nenhuma regra olha para ele. Vale
    "ok", a despesa é processada normalmente e sai o aviso chave repetida: obs 
    (2 ocorrências; valeu a última).

  Hoje o código faz a segunda opção. Isso não foi uma decisão: aconteceu porque
  a verificação de caractere quebrado só olha os valores que sobraram.

  As opções

  - A — o arquivo inteiro é rejeitado. Segue a seção 4 ao pé da letra: arquivo
    com caractere quebrado está corrompido, não importa onde. A regra fica
    simples e sem exceção.
  - B — o valor descartado é ignorado e a despesa é processada. Segue a RN-013:
    o que foi descartado não conta para nada. O caractere quebrado nunca chega à
    saída, então não há problema técnico. Mas a seção 4 ganha uma exceção.

  Minha recomendação: A. Um caractere quebrado indica arquivo corrompido ou
  gerado com defeito, e é melhor recusar do que processar um arquivo suspeito. O
  texto da seção 4 já diz isso, então bastaria uma frase de esclarecimento e a
  entrada no DECISIONS.md. No código, a verificação passaria a olhar também os
  valores descartados, como correção da T-006.

  Na prática quase nunca acontece, mas a escolha muda se o colaborador recebe
  saída ou não. Qual opção você prefere?

✻ Sautéed for 16s · done 11:26 PM

❯ existem possibilidades de emoji? pra mim isso nao tinha que existir           

⏺ Sim, emoji pode aparecer: descricao, fornecedor e nome são texto livre, e o
  JSON aceita qualquer caractere neles. Alguém pode escrever "descricao": 
  "Almoço com cliente 🍝", ou o sistema que gera o arquivo pode copiar um nome
  de restaurante com emoji. A spec já trata isso: um emoji válido é aceito como
  texto comum, e a T-006 tem teste para isso.

  Mas a decisão pendente não é sobre emoji. Usei o emoji só para explicar de
  onde vem o \uD800. O problema é um código quebrado, que não forma caractere
  nenhum e só aparece em arquivo gerado com defeito. Um emoji válido nunca cai
  nesse caso.

  Se você quisesse proibir emoji, eu desaconselho:
  - Seria uma regra nova, que a política do RH não pede.
  - Rejeitaria arquivos com JSON válido e despesas legítimas só por causa de um
    caractere na descrição.
  - Esses campos nem entram no cálculo: descricao é ignorada, e fornecedor só
    serve para achar duplicatas, depois de normalizado.
  - Pela seção 4, o formato de entrada é fixo, e qualquer texto é válido nele.

  O que continua em aberto é só o caso raro do código quebrado dentro de uma
  chave repetida, entre as opções A e B. Minha recomendação continua sendo A:
  arquivo com código quebrado é rejeitado inteiro, esteja onde estiver.

✻ Brewed for 8s · done 11:27 PM

❯ certo, pode seguir a recomencaçào A                                           

  Ran 1 shell command (ctrl+o to expand)

⏺ Vou registrar a decisão na spec (versão 1.9, entrada D-006 no DECISIONS.md) e
  alinhar o plano e as tasks. A correção no código vem depois, num commit
  fix(T-006) separado.
  Ran 1 shell command (ctrl+o to expand)

⏺ Bash(python3 - <<'EOF'
      def edit(p, pairs):…)
  ⎿   specs/001-motor-reembolso/plan.md  | 4 ++--
      specs/001-motor-reembolso/spec.md  | 7 ++++---
      specs/001-motor-reembolso/tasks.md | 4 ++--
      3 files changed, 8 insertions(+), 7 deletions(-)
  ⎿  Updated specs/001-motor-reembolso/plan.md (+2 -2)
      1  # Plano Técnico — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.1 · **Baseado na spec:** 1.8                      
      3 +**Versão:** 1.2 · **Baseado na spec:** 1.9                      
      4  
      5  > Aqui mora o COMO. Este arquivo pode e deve falar de linguagem,
          biblioteca e
      6  > arquitetura. O que ele **não** pode é introduzir regra de negó
         cio nova — se
     ...
      121  ### DT-002 — Rejeitar o que não é JSON estrito
      122  
      123  **Contexto:** RN-002: arquivo que não é JSON válido é erro de 
           arquivo. O `json` da biblioteca padrão aceita `NaN`, `Infinity
           ` e `-Infinity`, que não são JSON.
      124 -**Decisão:** `simplejson` ≥ 4 já os rejeita na leitura por pad
          -rão (`allow_nan=False`); a versão mínima fica fixada no `pypro
          -ject.toml` e um teste garante que `"valor": NaN` é erro de arq
          -uivo, para a proteção não sumir numa troca de versão. Erro de 
          -parse → `ErroDeArquivo`. Bytes decodificados como UTF-8 estrit
          -o (`utf-8-sig`, aceitando BOM, que a RFC 8259 permite ignorar)
          -; falha de decodificação → `ErroDeArquivo`. O parser aceita em
          - silêncio um escape `\ud800` sem par (vira um caractere substi
          -tuto isolado na `str`, que a gravação em UTF-8 recusaria depoi
          -s); por isso, depois do parse, `entrada.py` percorre todas as 
          -chaves e textos e levanta `ErroDeArquivo` se algum contiver ca
          -ractere entre U+D800 e U+DFFF (seção 4 da spec). Pares de esca
          -pes válidos já chegam combinados num único caractere.         
      124 +**Decisão:** `simplejson` ≥ 4 já os rejeita na leitura por pad
          +rão (`allow_nan=False`); a versão mínima fica fixada no `pypro
          +ject.toml` e um teste garante que `"valor": NaN` é erro de arq
          +uivo, para a proteção não sumir numa troca de versão. Erro de 
          +parse → `ErroDeArquivo`. Bytes decodificados como UTF-8 estrit
          +o (`utf-8-sig`, aceitando BOM, que a RFC 8259 permite ignorar)
          +; falha de decodificação → `ErroDeArquivo`. O parser aceita em
          + silêncio um escape `\ud800` sem par (vira um caractere substi
          +tuto isolado na `str`, que a gravação em UTF-8 recusaria depoi
          +s); por isso, depois do parse, `entrada.py` percorre todas as 
          +chaves e textos — inclusive os das ocorrências descartadas por
          + chave repetida, pelos pares guardados no `ObjetoJson` (DT-010
          +; spec 1.9, D-006) — e levanta `ErroDeArquivo` se algum contiv
          +er caractere entre U+D800 e U+DFFF (seção 4 da spec). Pares de
          + escapes válidos já chegam combinados num único caractere.    
      125  **Alternativa descartada:** aceitar `NaN` e tratar como "valor
            não é número" na despesa: transformaria arquivo inválido em p
           rocessamento normal.
      126  **Consequência:** `"valor": NaN` encerra a execução sem saída,
            como qualquer JSON inválido.
      127  
  ⎿  Updated specs/001-motor-reembolso/spec.md (+4 -3)
      1  # Spec — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.8 · **Status:** aprovada para planejamento · **Últ
        -ima alteração:** 2026-10-01 (ver `DECISIONS.md` D-001 a D-005)  
      3 +**Versão:** 1.9 · **Status:** aprovada para planejamento · **Últ
        +ima alteração:** 2026-10-01 (ver `DECISIONS.md` D-001 a D-006)  
      4  
      5  > **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ
         . Nenhuma linha
      6  > aqui pode citar linguagem, biblioteca, classe, função ou estru
         tura de pasta.
     ...
      67  
      68  Se um mesmo objeto do arquivo traz a mesma chave mais de uma ve
          z, vale a última ocorrência, e a saída avisa que as anteriores 
          foram descartadas (RN-013).
      69  
      70 -Todo texto da entrada, chave ou valor, vale pelo seu conteúdo *
         -*depois de decodificados os escapes** do arquivo (`"2026\u002d0
         -7\u002d03"` é a data `2026-07-03`), e "caractere" é o caractere
         - Unicode (um emoji escrito como par de escapes é igual ao mesmo
         - emoji escrito diretamente). Um escape que não forma caractere 
         -Unicode válido (`\uD800` a `\uDFFF` sem o par correspondente), 
         -em qualquer chave ou valor, é erro de arquivo (RN-002).        
      70 +Todo texto da entrada, chave ou valor, vale pelo seu conteúdo *
         +*depois de decodificados os escapes** do arquivo (`"2026\u002d0
         +7\u002d03"` é a data `2026-07-03`), e "caractere" é o caractere
         + Unicode (um emoji escrito como par de escapes é igual ao mesmo
         + emoji escrito diretamente). Um escape que não forma caractere 
         +Unicode válido (`\uD800` a `\uDFFF` sem o par correspondente), 
         +em qualquer chave ou valor, é erro de arquivo (RN-002), inclusi
         +ve numa ocorrência descartada por chave repetida (RN-013).     
      71  
      72  ### Saída
      73  
     ...
      247  - Ordem dos avisos de cada lista: a ordem em que a primeira oc
           orrência de cada chave repetida aparece no arquivo.
      248  - Só geram aviso os objetos que continuam no arquivo depois de
            aplicada a última ocorrência: chaves repetidas dentro de um v
           alor descartado não geram aviso, nem entram no `<n>` nem na or
           dem de avisos de chaves com o mesmo caminho no valor que valeu
           .
      249  - O aviso não muda status, motivo nem valores, e aparece em qu
           alquer item, inclusive recusado. Em erro de arquivo não há saí
           da, logo não há aviso.
      250 +- O descarte vale para as regras de negócio, não para a valida
          +de do arquivo: uma ocorrência descartada que traz escape sem c
          +aractere válido torna o arquivo inteiro erro de arquivo (seção
          + 4, RN-002).                                                  
      251  
      252  **Origem:** necessidade operacional (a política não trata o fo
           rmato do arquivo); AMB-019.
      252 -**Aceite:** despesa com `"valor": 30.00` e depois `"valor": 50
          -.00` → avaliada com 50,00; `itens[].avisos` = [`chave repetida
          -: valor (2 ocorrências; valeu a última)`]. `colaborador.nome` 
          -repetido → `avisos` do topo = [`chave repetida: colaborador.no
          -me (2 ocorrências; valeu a última)`]; itens sem chave repetida
          - têm `avisos` vazio. Despesa com `"tem_nota_fiscal": true` e d
          -epois `"tem_nota_fiscal": "sim"` → `entrada_invalida`, com o a
          -viso de `tem_nota_fiscal`. `despesas` repetida na raiz → só a 
          -última lista é avaliada; um aviso `chave repetida: despesas (2
          - ocorrências; valeu a última)` no topo; chaves repetidas dentr
          -o da primeira lista não geram aviso. Chave `valor` três vezes 
          -→ um aviso, com `3 ocorrências`. Despesa com `"extra": {"x": 1
          -, "x": 2}, "obs": "a", "obs": "b", "extra": {"x": 3, "x": 4}` 
          -→ avisos, nesta ordem: `extra` (2), `obs` (2), `extra.x` (2). 
          -Alimentação fora de viagem com `"valor": 30.00` e depois `"\u0
          -076alor": 90.00` → vale 90,00, `parcial` com 60,00, aviso de `
          -valor`.                                                       
      253 +**Aceite:** despesa com `"valor": 30.00` e depois `"valor": 50
          +.00` → avaliada com 50,00; `itens[].avisos` = [`chave repetida
          +: valor (2 ocorrências; valeu a última)`]. `colaborador.nome` 
          +repetido → `avisos` do topo = [`chave repetida: colaborador.no
          +me (2 ocorrências; valeu a última)`]; itens sem chave repetida
          + têm `avisos` vazio. Despesa com `"tem_nota_fiscal": true` e d
          +epois `"tem_nota_fiscal": "sim"` → `entrada_invalida`, com o a
          +viso de `tem_nota_fiscal`. `despesas` repetida na raiz → só a 
          +última lista é avaliada; um aviso `chave repetida: despesas (2
          + ocorrências; valeu a última)` no topo; chaves repetidas dentr
          +o da primeira lista não geram aviso. Chave `valor` três vezes 
          +→ um aviso, com `3 ocorrências`. Despesa com `"extra": {"x": 1
          +, "x": 2}, "obs": "a", "obs": "b", "extra": {"x": 3, "x": 4}` 
          +→ avisos, nesta ordem: `extra` (2), `obs` (2), `extra.x` (2). 
          +Alimentação fora de viagem com `"valor": 30.00` e depois `"\u0
          +076alor": 90.00` → vale 90,00, `parcial` com 60,00, aviso de `
          +valor`. Despesa com `"obs": "\uD800"` e depois `"obs": "ok"` →
          + erro de arquivo, sem saída.                                  
      254  
      255  ---
      256  
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+2 -2)
      1  # Tasks — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.1 · **Baseado em:** spec 1.8, plan 1.1            
      3 +**Versão:** 1.2 · **Baseado em:** spec 1.9, plan 1.2            
      4  
      5  > Cada task é pequena o bastante para virar **um commit**. Se vo
         cê não consegue
      6  > descrever o critério de aceite como "o teste X passa", a task 
         está grande demais.
     ...
      65    - **Tipo:** estrutura (leitura de JSON)
      66    - **Atende:** RN-002 (arquivo que não é JSON válido; escape q
          ue não forma caractere válido), seção 4 da spec (número pelo va
          lor decimal exato; texto depois de decodificados os escapes), D
          T-001, DT-002
      67    - **Depende de:** T-001
      68 -  - **Aceite:** `tests/test_leitura_json.py` passa: `test_rn002
         -_nan_e_erro_de_arquivo` (`NaN`, `Infinity`, `-Infinity`); `test
         -_rn002_json_malformado_e_erro_de_arquivo`; `test_rn002_utf8_inv
         -alido_e_erro_de_arquivo`; `test_rn002_escape_sem_par_em_valor_e
         -_erro_de_arquivo` e `..._em_chave_...` (`\ud800`); `test_bom_e_
         -aceito`; `test_numero_lido_pelo_valor_exato` (`33.333`, `999999
         -999.99999999999`, `1e999999`, `1e-999999` e inteiro de 5.000 dí
         -gitos lidos como `Decimal` exato, sem erro); `test_escapes_vali
         -dos_decodificados` (`"2026-07-03"` → `2026-07-03`; emoji em par
         - de escapes igual ao emoji direto).                            
      68 +  - **Aceite:** `tests/test_leitura_json.py` passa: `test_rn002
         +_nan_e_erro_de_arquivo` (`NaN`, `Infinity`, `-Infinity`); `test
         +_rn002_json_malformado_e_erro_de_arquivo`; `test_rn002_utf8_inv
         +alido_e_erro_de_arquivo`; `test_rn002_escape_sem_par_em_valor_e
         +_erro_de_arquivo` e `..._em_chave_...` (`\ud800`); `test_rn002_
         +escape_sem_par_em_ocorrencia_descartada_e_erro_de_arquivo` (`"o
         +bs": "\ud800", "obs": "ok"`, em valor e em objeto aninhado desc
         +artado; D-006); `test_bom_e_aceito`; `test_numero_lido_pelo_val
         +or_exato` (`33.333`, `999999999.99999999999`, `1e999999`, `1e-9
         +99999` e inteiro de 5.000 dígitos lidos como `Decimal` exato, s
         +em erro); `test_escapes_validos_decodificados` (`"2026-07-03"` 
         +→ `2026-07-03`; emoji em par de escapes igual ao emoji direto).
      69    - **Commit:** e84693c
      70  
      71  - [x] **T-007** — Chaves repetidas: `ObjetoJson` via `object_pa
          irs_hook` (vale a última ocorrência) e percurso que gera os avi
          sos do topo e de cada elemento de `despesas`, com texto, caminh
          o, contagem e ordem da RN-013 (DT-010).

⏺ Agora a entrada D-006 no DECISIONS.md:

⏺ Update(specs/001-motor-reembolso/DECISIONS.md)
  ⎿  Added 20 lines
      10  
      11  ---
      12  
      13 +## D-006 — Escape inválido em ocorrência descartada: spec 1.8 →
         + 1.9 · `2026-10-01`                                            
      14 +                                                               
      15 +**Gatilho:** revisão independente da T-007 (`docs/reviews/T-007
         +.md`, revisões 1 e 2, "Decisões necessárias" 1). A seção 4 dizi
         +a que escape sem caractere válido "em qualquer chave ou valor" 
         +é erro de arquivo; a RN-013 dizia que as ocorrências descartada
         +s por chave repetida "nenhuma regra as considera". Para `"obs":
         + "\uD800", "obs": "ok"` as duas leituras davam resultados opost
         +os (erro de arquivo × despesa processada com aviso). O código d
         +a T-006 seguia a segunda sem decisão explícita: só verificava o
         +s valores que valeram. Decidido pelo responsável na sessão `doc
         +s/sessions/18-*`.                                              
      16 +                                                               
      17 +**O que mudou na spec:**                                       
      18 +                                                               
      19 +| # | Ponto | De (1.8) | Para (1.9) | Onde |                   
      20 +|---|---|---|---|---|                                          
      21 +| 1 | Escape sem caractere válido numa ocorrência descartada po
         +r chave repetida | contraditório entre seção 4 e RN-013 | **err
         +o de arquivo**, como em qualquer outra chave ou valor; o descar
         +te da RN-013 vale para as regras de negócio, não para a validad
         +e do arquivo | seção 4, RN-013 (regra e aceite) |              
      22 +                                                               
      23 +**Por quê:** escape sem par só aparece em arquivo corrompido ou
         + gerado com defeito; o lugar onde ele está (valor que valeu ou 
         +descartado) não muda isso. Recusar o arquivo mantém a regra da 
         +seção 4 sem exceção e evita processar um arquivo suspeito. Emoj
         +i válido (par completo ou caractere direto) continua aceito em 
         +qualquer texto.                                                
      24 +                                                               
      25 +**O que isso invalidou:** o código da T-006 (`_verificar_textos
         +` percorria só os valores que valeram); corrigido em commit `fi
         +x(T-006)`. DT-002 do `plan.md` alinhado na versão 1.2. Nenhum v
         +alor do exemplo (seção 9) mudou; seção 7 não muda (contagem de 
         +63 casos preservada).                                          
      26 +                                                               
      27 +**Tasks afetadas:** T-006 (aceite ganha o teste de ocorrência d
         +escartada).                                                    
      28 +                                                               
      29 +**Custo:** 4 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`, `t
         +asks.md`) + correção de uma função e um teste.                 
      30 +                                                               
      31 +---                                                            
      32 +                                                               
      33  ## D-005 — Normalização: só letras e algarismos contam: spec 1.
          6 → 1.8 · `2026-10-01`
      34  
      35  **Gatilho:** revisão independente da T-003 (`docs/reviews/T-003
          .md`, revisão 1, BLOQUEADO). O passo 4 da seção 5 só tratava se
          quências **internas** de separadores e o passo 1 só removia esp
          aço em branco das pontas: hífen ou sublinhado no início ou no f
          im não tinham resultado definido (`"-Bistro"` × `"_Bistro"` mud
          am a RN-007). O passo 3 não dizia se `ø`, `ł`, `đ` contam como 
          letra com sinal. O responsável decidiu os dois pontos (versão 1
          .7, não commitada). A rodada do `spec-adversary` sobre a 1.7 ap
          ontou 5 problemas (1 bloqueante): o conjunto de "hífens" e de "
          espaços em branco" não estava fechado (travessão U+2013 colocad
          o pelo editor, espaço de largura zero, BOM, caracteres de contr
          ole). O responsável optou por trocar as listas por uma regra ún
          ica, "só letras e algarismos contam". A rodada do `spec-adversa
          ry` sobre essa versão apontou 5 problemas (2 bloqueantes): "let
          ra", "algarismo decimal" e "sinal combinante" sem conjunto defi
          nido (`Nº` × `N°`), e "espaço em branco" ainda aberto para `id`
           e `colaborador`. O responsável aceitou as 5 recomendações (pon
          tos 8 a 12), aplicadas na mesma versão 1.8. A rodada de confirm
          ação não apontou bloqueante; os 4 achados (uma contradição de r
          edação e três cantos do Unicode sem efeito em dados realistas) 
          foram registrados no ponto 13, como combinado com o responsável
          . Sessão `docs/sessions/13-*`.

⏺ Agora o teste da correção, escrito antes do código:

⏺ Bash(python3 - <<'EOF'
      p = "tests/test_leitura_json.py"…)
  ⎿  FAILED tests/test_leitura_json.py::test_rn002_escape_sem_par_em_ocorre
     ncia_descartada_e_erro_de_arquivo[{"extra": {"\udc00": 1}, "extra": {}
     }]
     3 failed, 26 deselected in 0.02s
  ⎿  Updated tests/test_leitura_json.py (+14 -0)
      73          ler_json(texto)
      74  
      75  
      76 +@pytest.mark.parametrize(                                      
      77 +    "texto",                                                   
      78 +    [                                                          
      79 +        rb'{"obs": "\ud800", "obs": "ok"}',                    
      80 +        rb'{"despesas": [{"obs": {"x": "\ud800"}, "obs": "ok"}]
         +}',                                                            
      81 +        rb'{"extra": {"\udc00": 1}, "extra": {}}',             
      82 +    ],                                                         
      83 +)                                                              
      84 +def test_rn002_escape_sem_par_em_ocorrencia_descartada_e_erro_d
         +e_arquivo(texto):                                              
      85 +    """RN-002 / RN-013 / D-006: escape inválido em ocorrência d
         +escartada → erro."""                                           
      86 +    with pytest.raises(ErroDeArquivo):                         
      87 +        ler_json(texto)                                        
      88 +                                                               
      89 +                                                               
      90  def test_bom_e_aceito():
      91      """DT-002: BOM UTF-8 no início é ignorado (RFC 8259)."""
      92      documento = ler_json(b'\xef\xbb\xbf{"nome": "Jo\xc3\xa3o"}'
          )

⏺ Os 3 casos falham pelo motivo certo (nenhum erro é levantado). Agora a
  correção: a verificação passa a percorrer os pares guardados, não só os
  valores que valeram.

⏺ Bash(python3 - <<'EOF'
      p = "src/reembolso/entrada.py"…)
  ⎿  All checks passed!
     167 passed in 0.06s
     diff --git a/src/reembolso/entrada.py b/src/reembolso/entrada.py
     … +20 lines (ctrl+o to expand)
  ⎿  Updated src/reembolso/entrada.py (+3 -3)
      24  
      25  
      26  def _verificar_textos(valor) -> None:
      27 -    """Percorre chaves e textos do documento (DT-002)."""      
      27 +    """Percorre chaves e textos do documento, inclusive descart
         +ados (DT-002, D-006)."""                                       
      28      if isinstance(valor, str):
      29          if _tem_substituto_isolado(valor):
      30              raise ErroDeArquivo("texto com escape que não forma
           caractere válido")
      31 -    elif isinstance(valor, dict):                              
      32 -        for chave, item in valor.items():                      
      31 +    elif isinstance(valor, ObjetoJson):                        
      32 +        for chave, item in valor.pares:                        
      33              _verificar_textos(chave)
      34              _verificar_textos(item)
      35      elif isinstance(valor, list):

⏺ A opção A ficou registrada na spec e o código já segue a decisão: um código
  quebrado numa chave repetida descartada agora faz o arquivo inteiro ser
  recusado. Nada foi commitado ainda. Os 167 testes passam e o ruff está limpo.

  O que mudou na documentação:
  - spec.md (versão 1.9):
    - a seção 4 passa a dizer "inclusive numa ocorrência descartada por chave
      repetida";
    - a RN-013 ganha um item dizendo que o descarte vale para as regras de
      negócio, não para a validade do arquivo;
    - o Aceite da RN-013 ganha o exemplo "obs": "\uD800", "obs": "ok", que dá
      erro de arquivo, sem saída.
    - A seção 7 não muda: continuam 63 casos.
  - DECISIONS.md: nova entrada D-006 com o motivo, as duas leituras que
    conflitavam e o que a decisão invalidou.
  - plan.md (1.2): a DT-002 diz que a verificação inclui as ocorrências
    descartadas.
  - tasks.md (1.2): o Aceite da T-006 ganha o teste novo.

  Código:
  - entrada.py: a verificação de código quebrado percorre todos os pares de cada
    objeto, inclusive os descartados, e não só os valores que valeram.
  - Teste novo
    test_rn002_escape_sem_par_em_ocorrencia_descartada_e_erro_de_arquivo com 3
    casos: valor descartado, objeto aninhado descartado e chave dentro de um
    valor descartado. Os 3 falharam antes da correção, sem erro levantado, e
    passam depois.

  Na D-006 citei a sessão como docs/sessions/18-*, porque o export 17 já foi
  feito.

  Commits propostos, separados como nas versões anteriores:
  1. docs(spec): v1.9 escape inválido em ocorrência descartada é erro de arquivo
     (D-006), com spec.md e DECISIONS.md
  2. docs(plan): v1.2 alinha DT-002 à spec 1.9
  3. docs(tasks): v1.2 atualiza aceite da T-006
  4. fix(T-006): verifica escape inválido também nas ocorrências descartadas

  O CLAUDE.md pede uma rodada do spec-adversary depois de mudança relevante na
  spec. Esta mudança é pequena: só resolve a contradição, sem regra nova. Posso
  rodar a revisão antes dos commits, ou seguir direto. Como prefere?

✻ Churned for 58s · done 11:29 PM

❯ pode rodar a revisao antes do commit                                          

⏺ spec-adversary(Revisão adversarial spec 1.9)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ Iniciei a revisão do spec-adversary sobre a spec 1.9. Quando terminar, trago
  os problemas que ele apontar para você decidir. Só depois disso faço os
  commits.

✻ Churned for 6s · done 11:30 PM

› Message from spec-adversary
  Encontrei 3 problemas, 1 deles bloqueante. A mudança 1.8 → 1.9 resolve a
  contradição que a D-006 aponta. Não achei contradição nova com RN-002, seção
  7, seção 8 ou seção 10. Também não achei brecha que aumente o reembolso: a
  regra nova só pode levar a erro de arquivo, sem saída, e isso não dá ganho a
  ninguém. Os problemas estão na fronteira de "texto inválido" que a decisão
  traça.

  Conferências feitas sem achado:
  - Versão e cabeçalho da spec citam D-001 a D-006.
  - A seção 7 continua com 63 linhas (419–481).
  - A seção 8 não contradiz a mudança: o erro de arquivo acontece na leitura,
  fora das etapas, e as etapas continuam vendo só o valor que valeu.
  - A RN-013 já dizia "em erro de arquivo não há aviso", o que segue coerente.

  ### 1. "Arquivo corrompido" só é definido para escape; o mesmo defeito sem
  escape não tem resultado — BLOQUEANTE — lacuna

  - **Regra afetada:** seção 4 (parágrafo de escapes), RN-002 (erro de arquivo:
  "não é JSON válido"), RN-013 (último item).
  - **Cenário de entrada:**
    - (a) Arquivo UTF-8 com BOM (EF BB BF) antes do `{`, gerado por ferramenta
  Windows, e conteúdo igual ao do exemplo.
    - (b) Despesa com `"obs": "<bytes ED A0 80>", "obs": "ok"`: é o mesmo
  `\uD800` da D-006, só que gravado como bytes crus (WTF-8/CESU-8) em vez de
  escape.
    - (c) Arquivo inteiro em Latin-1 com `"fornecedor": "Bistrô Central"`.
  - **Comportamento pela interpretação atual:** indefinido. A spec não diz em
  que codificação o arquivo de entrada está; só fala da saída em UTF-8. A RFC do
  JSON proíbe o BOM, mas deixa o leitor ignorá-lo, então tanto "não é JSON
  válido" (erro de arquivo) quanto "processa normalmente" cabem no texto. Em
  (b), a D-006 justifica a regra com "escape sem par só aparece em arquivo
  corrompido; o lugar onde ele está não muda isso", mas a regra escrita cobre só
  o escape. O mesmo caractere sem par gravado cru pode virar erro de arquivo,
  caractere de substituição (U+FFFD) ou outra coisa. Em (c), "Bistrô" pode ser
  lido como outro texto e mudar a comparação de fornecedor da RN-007.
  - **Por que é um problema:** o motivo da decisão (rejeitar arquivo defeituoso,
  qualquer que seja o lugar do defeito) não chega a defeitos equivalentes que
  não usam escape. No cenário (a), que é plausível, o mesmo arquivo pode ser
  processado por inteiro ou rejeitado por inteiro conforme a leitura. Em (b),
  uma ocorrência descartada pode tornar o arquivo inválido ou não, dependendo só
  de como o caractere foi escrito, o que contraria o motivo da D-006.
  - **Perguntas para decisão:** Em que codificação o arquivo de entrada deve
  estar, e o que acontece com BOM no início? Bytes que não formam UTF-8 válido,
  inclusive um caractere sem par gravado cru, numa ocorrência que valeu ou numa
  descartada, dão o mesmo resultado que o escape sem par, ou outro?

  ### 2. O parêntese "(`\uD800` a `\uDFFF` sem o par correspondente)" é a lista
  completa ou um exemplo? — PODE ESPERAR — ambiguidade

  - **Regra afetada:** seção 4 (parágrafo de escapes), RN-002, RN-013 (último
  item).
  - **Cenário de entrada:** despesa válida com `"obs": "￿", "obs": "ok"`, ou com
  `"obs": "\u0000"`.
  - **Comportamento pela interpretação atual:** indefinido. Se o parêntese for a
  definição completa, U+FFFF (um "não caractere" do Unicode) e U+0000 são
  válidos e a despesa é processada com aviso de `obs`. Se o parêntese for só um
  exemplo de "escape que não forma caractere Unicode válido", U+FFFF pode ser
  lido como inválido e o arquivo vira erro. Com a 1.9, a diferença passa a valer
  também para ocorrências descartadas: o arquivo é processado inteiro ou
  rejeitado inteiro.
  - **Por que é um problema:** "caractere Unicode válido" não tem definição
  fechada. O parêntese pode ser lido como o conjunto inteiro ou como um caso
  dele. Isso é pouco provável em dados reais, por isso não é bloqueante.
  - **Pergunta para decisão:** Os escapes de não caracteres (U+FFFE, U+FFFF,
  U+FDD0 a U+FDEF etc.) e de caracteres de controle como U+0000 são válidos, ou
  "não forma caractere Unicode válido" inclui mais que os substitutos
  (surrogates) sem par?

  ### 3. Até onde vai a "ocorrência descartada", e onde a regra está escrita —
  PODE ESPERAR — ambiguidade (redação)

  - **Regra afetada:** RN-013 (último item e Aceite), RN-002 (lista de erros de
  arquivo), seção 7, seção 8.
  - **Cenário de entrada:**
    - (a) Na raiz, `"despesas": [{"id": "d-1", "obs": "\uD800"}], "despesas": [
  ... válidas ... ]`. O texto inválido está numa chave não repetida (`obs`)
  dentro de um valor descartado por inteiro.
    - (b) Na despesa, `"extra": {"y": "\uDC00"}, "extra": {}`.
  - **Comportamento pela interpretação atual:** a seção 4 ("em qualquer chave ou
  valor, inclusive numa ocorrência descartada") leva a erro de arquivo nos dois
  casos. Mas o item da RN-013 diz "uma ocorrência descartada que **traz**
  escape", e o único exemplo do Aceite tem o escape direto no valor de primeiro
  nível (`"obs": "\uD800"`). Quem ler só a RN-013 pode entender que o teste vale
  só para o valor imediato da chave repetida, e não para o que vem dentro dele.
  Isso fica mais provável porque o item anterior da mesma regra trata o que
  está "dentro de um valor descartado" de outro jeito: ali as chaves repetidas
  não geram aviso nem entram na contagem.
  - **Pontos de redação ligados ao mesmo tema:**
    - O item de erro de arquivo da RN-002 remete à seção 4, mas não repete
  "inclusive em ocorrência descartada".
    - A seção 8 diz que "todas as etapas veem só o valor que valeu" e não
  menciona que a validade dos escapes é verificada no arquivo inteiro antes
  disso.
    - A seção 7 não tem linha para o caso novo (a D-006 manteve 63 casos de
  propósito). O critério da seção 9 fica atendido pelo teste da RN-013, mas o
  caso aninhado (a)/(b) não aparece em nenhum aceite.
    - Nada disso muda valores se lido junto com a seção 4.
  - **Por que é um problema:** há duas leituras possíveis para o alcance do item
  novo da RN-013 quando o texto inválido está aninhado. O resultado vai de
  "processa com um aviso de `despesas`" até "erro de arquivo".
  - **Pergunta para decisão:** Texto com escape inválido em qualquer
  profundidade dentro de um valor descartado, inclusive em chave que não se
  repete, também é erro de arquivo? A RN-002, a seção 8 ou a seção 7 devem dizer
  isso explicitamente, ou basta a seção 4?

  ---

  1. **Decidir antes da implementação:** 1
  2. **Pode ser decidido depois:** 2, 3

  Arquivos lidos:
  /Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md e
  /Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md
  (entrada D-006).

⏺ Antes de levar os pontos a você, confiro se a spec já cobre a codificação de
  entrada que o problema 1 diz faltar:

  Ran 1 shell command (ctrl+o to expand)

⏺ Agent "Revisão adversarial spec 1.9" finished · 1m 26s

⏺ O spec-adversary apontou 3 problemas, 1 deles bloqueante. Não encontrou
  contradição nova nem brecha que aumente o reembolso: a regra nova só pode
  levar a erro de arquivo, sem saída.

  Conferi os três na spec e no código. Nos três casos o código já faz uma 
  escolha, que está no plan.md (DT-002) e tem teste, mas a spec não diz nada.
  Por isso proponho só escrever na spec o que o código já faz, sem mudar código.
  Preciso do seu sim ou não em cada um.

  1. Codificação do arquivo de entrada (BLOQUEANTE)

  A spec diz que a saída é UTF-8, mas não diz como a entrada deve estar
  codificada. Hoje o código:
  - aceita BOM no início (marca invisível que o Windows costuma colocar), que é
    ignorado;
  - trata como erro de arquivo qualquer byte que não seja UTF-8 válido, em
    qualquer lugar. Isso inclui arquivo em Latin-1 e o mesmo caractere quebrado
    da D-006 gravado como bytes crus, em vez de escape.

  Isso segue a mesma lógica da opção A: arquivo defeituoso é recusado, onde quer
  que esteja o defeito. O problema 1 é anterior à 1.9; a revisão só o deixou
  visível.

  → Proposta: escrever na seção 4 e na RN-002 que a entrada é UTF-8, que o BOM
  no início é ignorado e que byte fora do UTF-8, em qualquer lugar, é erro de
  arquivo.

  2. O que conta como "caractere inválido" (pode esperar)

  O parêntese (\uD800 a \uDFFF sem o par) é a lista completa ou só um exemplo?
  Hoje o código trata como lista completa. Caracteres estranhos mas existentes,
  como \u0000 e \uFFFF, são aceitos.

  → Proposta: deixar explícito que a lista é completa e que os demais caracteres
  são válidos.

  3. Profundidade do valor descartado (pode esperar)

  Se o caractere quebrado estiver dentro de um valor descartado, por exemplo em
  "extra": {"y": "\uDC00"}, "extra": {}, a RN-013 nova pode ser lida como se
  valesse só para o primeiro nível. Hoje o código recusa em qualquer
  profundidade, e o teste novo já cobre esse caso.

  → Proposta: escrever "em qualquer profundidade" na RN-013 e na RN-002, e uma
  frase na seção 8 dizendo que a validade dos textos é verificada no arquivo
  inteiro, antes das etapas.

  Se você concordar com as três, ajusto a spec e a D-006 (que passa a registrar
  os 4 pontos) e rodo o spec-adversary de novo para confirmar. Só depois disso
  faço os commits. Prefiro resolver o 2 e o 3 agora, junto com o 1, porque são
  só redação. Concorda?

✻ Cogitated for 1m 50s · done 11:32 PM

❯ concordo com os tres                                                          

⏺ Bash(python3 - <<'EOF'
      def edit(p, pairs):…)
  ⎿   specs/001-motor-reembolso/DECISIONS.md | 23 +++++++++++++++++++++++
      specs/001-motor-reembolso/plan.md      |  4 ++--
      specs/001-motor-reembolso/spec.md      | 13 ++++++++-----
     … +4 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/DECISIONS.md (+8 -5)
      10  
      11  ---
      12  
      13 -## D-006 — Escape inválido em ocorrência descartada: spec 1.8 →
         - 1.9 · `2026-10-01`                                            
      13 +## D-006 — Arquivo defeituoso: escape inválido em ocorrência de
         +scartada e codificação da entrada: spec 1.8 → 1.9 · `2026-10-01
         +`                                                              
      14  
      15 -**Gatilho:** revisão independente da T-007 (`docs/reviews/T-007
         -.md`, revisões 1 e 2, "Decisões necessárias" 1). A seção 4 dizi
         -a que escape sem caractere válido "em qualquer chave ou valor" 
         -é erro de arquivo; a RN-013 dizia que as ocorrências descartada
         -s por chave repetida "nenhuma regra as considera". Para `"obs":
         - "\uD800", "obs": "ok"` as duas leituras davam resultados opost
         -os (erro de arquivo × despesa processada com aviso). O código d
         -a T-006 seguia a segunda sem decisão explícita: só verificava o
         -s valores que valeram. Decidido pelo responsável na sessão `doc
         -s/sessions/18-*`.                                              
      15 +**Gatilho:** revisão independente da T-007 (`docs/reviews/T-007
         +.md`, revisões 1 e 2, "Decisões necessárias" 1). A seção 4 dizi
         +a que escape sem caractere válido "em qualquer chave ou valor" 
         +é erro de arquivo; a RN-013 dizia que as ocorrências descartada
         +s por chave repetida "nenhuma regra as considera". Para `"obs":
         + "\uD800", "obs": "ok"` as duas leituras davam resultados opost
         +os (erro de arquivo × despesa processada com aviso). O código d
         +a T-006 seguia a segunda sem decisão explícita: só verificava o
         +s valores que valeram. Decidido pelo responsável (ponto 1). A r
         +odada do `spec-adversary` sobre a primeira redação da 1.9 apont
         +ou 3 problemas (1 bloqueante): a codificação da entrada não est
         +ava na spec (só no DT-002 do plano), o parêntese `\uD800` a `\u
         +DFFF` podia ser lido como exemplo e não como lista, e o alcance
         + do descarte em profundidade era ambíguo na RN-013. O responsáv
         +el aceitou as 3 recomendações (pontos 2 a 4), que registram na 
         +spec o que o plano e o código já faziam. Sessão `docs/sessions/
         +18-*`.                                                         
      16  
      17  **O que mudou na spec:**
      18  
      19  | # | Ponto | De (1.8) | Para (1.9) | Onde |
      20  |---|---|---|---|---|
      21  | 1 | Escape sem caractere válido numa ocorrência descartada po
          r chave repetida | contraditório entre seção 4 e RN-013 | **err
          o de arquivo**, como em qualquer outra chave ou valor; o descar
          te da RN-013 vale para as regras de negócio, não para a validad
          e do arquivo | seção 4, RN-013 (regra e aceite) |
      22 +| 2 | Codificação da entrada (**bloqueante** na revisão) | inde
         +finida na spec (BOM, Latin-1, substituto gravado em bytes crus)
         + | UTF-8; BOM no início ignorado; byte fora do UTF-8 em qualque
         +r lugar → erro de arquivo | seção 4, RN-002 |                  
      23 +| 3 | Conjunto de escapes inválidos | parêntese `\uD800` a `\uD
         +FFF` lido como lista ou exemplo | lista completa; `\u0000`, `\u
         +FFFF` e demais formam caractere válido | seção 4 |             
      24 +| 4 | Profundidade do descarte | RN-013 podia ser lida como só 
         +o primeiro nível | em qualquer profundidade; explicitado na RN-
         +002, na RN-013 (regra e aceite) e na seção 8 | RN-002, RN-013, 
         +seção 8 |                                                      
      25  
      23 -**Por quê:** escape sem par só aparece em arquivo corrompido ou
         - gerado com defeito; o lugar onde ele está (valor que valeu ou 
         -descartado) não muda isso. Recusar o arquivo mantém a regra da 
         -seção 4 sem exceção e evita processar um arquivo suspeito. Emoj
         -i válido (par completo ou caractere direto) continua aceito em 
         -qualquer texto.                                                
      26 +**Por quê:** escape sem par só aparece em arquivo corrompido ou
         + gerado com defeito; o lugar onde ele está (valor que valeu ou 
         +descartado, em qualquer profundidade) não muda isso. Recusar o 
         +arquivo mantém a regra da seção 4 sem exceção e evita processar
         + um arquivo suspeito. O ponto 2 aplica o mesmo motivo ao defeit
         +o gravado sem escape: byte fora do UTF-8 é recusado onde quer q
         +ue esteja; o BOM é aceito porque ferramentas comuns o gravam em
         + arquivos corretos. O ponto 3 fecha o conjunto: caracteres de c
         +ontrole e não caracteres existem no Unicode e podem ser gravado
         +s em UTF-8, então não são defeito. Emoji válido (par completo o
         +u caractere direto) continua aceito em qualquer texto.         
      27  
      25 -**O que isso invalidou:** o código da T-006 (`_verificar_textos
         -` percorria só os valores que valeram); corrigido em commit `fi
         -x(T-006)`. DT-002 do `plan.md` alinhado na versão 1.2. Nenhum v
         -alor do exemplo (seção 9) mudou; seção 7 não muda (contagem de 
         -63 casos preservada).                                          
      28 +**O que isso invalidou:** o código da T-006 (`_verificar_textos
         +` percorria só os valores que valeram); corrigido em commit `fi
         +x(T-006)`. Os pontos 2 a 4 não mudam código: o DT-002 já lia `u
         +tf-8-sig` estrito e verificava só U+D800 a U+DFFF, com testes n
         +a T-006 (`test_bom_e_aceito`, `test_rn002_utf8_invalido_e_erro_
         +de_arquivo`, inclusive substituto em bytes crus). DT-002 do `pl
         +an.md` alinhado na versão 1.2. Nenhum valor do exemplo (seção 9
         +) mudou; seção 7 não muda (contagem de 63 casos preservada).   
      29  
      30  **Tasks afetadas:** T-006 (aceite ganha o teste de ocorrência d
          escartada).
      31  
      29 -**Custo:** 4 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`, `t
         -asks.md`) + correção de uma função e um teste.                 
      32 +**Custo:** 4 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`, `t
         +asks.md`) + correção de uma função e um teste. Duas rodadas do 
         +`spec-adversary` (sobre a primeira redação da 1.9 e de confirma
         +ção).                                                          
      33  
      34  ---
      35  
  ⎿  Updated specs/001-motor-reembolso/spec.md (+7 -5)
      67  
      68  Se um mesmo objeto do arquivo traz a mesma chave mais de uma ve
          z, vale a última ocorrência, e a saída avisa que as anteriores 
          foram descartadas (RN-013).
      69  
      70 -Todo texto da entrada, chave ou valor, vale pelo seu conteúdo *
         -*depois de decodificados os escapes** do arquivo (`"2026\u002d0
         -7\u002d03"` é a data `2026-07-03`), e "caractere" é o caractere
         - Unicode (um emoji escrito como par de escapes é igual ao mesmo
         - emoji escrito diretamente). Um escape que não forma caractere 
         -Unicode válido (`\uD800` a `\uDFFF` sem o par correspondente), 
         -em qualquer chave ou valor, é erro de arquivo (RN-002), inclusi
         -ve numa ocorrência descartada por chave repetida (RN-013).     
      70 +O arquivo de entrada é lido em UTF-8; uma marca BOM no início d
         +o arquivo é ignorada. Um byte ou sequência de bytes que não for
         +ma UTF-8 válido, em qualquer lugar do arquivo (inclusive um car
         +actere de `U+D800` a `U+DFFF` gravado diretamente em bytes, ou 
         +um arquivo em outra codificação, como Latin-1), é erro de arqui
         +vo (RN-002).                                                   
      71 +                                                               
      72 +Todo texto da entrada, chave ou valor, vale pelo seu conteúdo *
         +*depois de decodificados os escapes** do arquivo (`"2026\u002d0
         +7\u002d03"` é a data `2026-07-03`), e "caractere" é o caractere
         + Unicode (um emoji escrito como par de escapes é igual ao mesmo
         + emoji escrito diretamente). Um escape que não forma caractere 
         +Unicode válido, em qualquer chave ou valor, é erro de arquivo (
         +RN-002), em qualquer profundidade, inclusive dentro de uma ocor
         +rência descartada por chave repetida (RN-013). Os únicos escape
         +s que não formam caractere válido são os de `\uD800` a `\uDFFF`
         + sem o par correspondente; qualquer outro escape, inclusive de 
         +caractere de controle (`\u0000`) ou de não caractere do Unicode
         + (`\uFFFF`), forma um caractere válido.                        
      73  
      74  ### Saída
      75  
     ...
      157  ### RN-002 — Validação da entrada
      158  
      159  **Regra:**
      158 -- **Erro de arquivo** (o arquivo de saída não é criado nem alt
          -erado): arquivo de entrada ausente ou que não é JSON válido; t
          -exto, em chave ou valor, com escape que não forma caractere Un
          -icode válido (seção 4); `colaborador` ausente ou sem `id`/`nom
          -e` em texto, ou com `id`/`nome` vazio ou só com espaços em bra
          -nco; `periodo.inicio`, `periodo.fim` ou `despesas` ausentes; `
          -inicio` ou `fim` que não são datas válidas `AAAA-MM-DD`; `inic
          -io` posterior a `fim`; `despesas` que não é lista; arquivo de 
          -saída que não pode ser gravado. `periodo.competencia` nunca ca
          -usa erro: se não for texto, sai nula.                         
      160 +- **Erro de arquivo** (o arquivo de saída não é criado nem alt
          +erado): arquivo de entrada ausente, que não está em UTF-8 váli
          +do ou que não é JSON válido (seção 4); texto, em chave ou valo
          +r, com escape que não forma caractere Unicode válido (seção 4)
          +, em qualquer profundidade, inclusive dentro de ocorrência des
          +cartada por chave repetida (RN-013); `colaborador` ausente ou 
          +sem `id`/`nome` em texto, ou com `id`/`nome` vazio ou só com e
          +spaços em branco; `periodo.inicio`, `periodo.fim` ou `despesas
          +` ausentes; `inicio` ou `fim` que não são datas válidas `AAAA-
          +MM-DD`; `inicio` posterior a `fim`; `despesas` que não é lista
          +; arquivo de saída que não pode ser gravado. `periodo.competen
          +cia` nunca causa erro: se não for texto, sai nula.            
      161  - **Despesa inválida** (vira item `recusado` com motivo `entra
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
      162  - Na saída de uma despesa inválida, `id`, `data` e `categoria`
            são copiados se forem texto e saem nulos caso contrário (tipo
            errado, ausente ou elemento que não é objeto); a `categoria`,
            se reconhecida, sai normalizada, como em qualquer item (seção
            4).
      163  - Uma despesa recusada por `entrada_invalida` tem `valor_consi
           derado` nulo, `em_viagem` e `limite_diario` nulos, e não entra
            nos totais.
     ...
      249  - Ordem dos avisos de cada lista: a ordem em que a primeira oc
           orrência de cada chave repetida aparece no arquivo.
      250  - Só geram aviso os objetos que continuam no arquivo depois de
            aplicada a última ocorrência: chaves repetidas dentro de um v
           alor descartado não geram aviso, nem entram no `<n>` nem na or
           dem de avisos de chaves com o mesmo caminho no valor que valeu
           .
      251  - O aviso não muda status, motivo nem valores, e aparece em qu
           alquer item, inclusive recusado. Em erro de arquivo não há saí
           da, logo não há aviso.
      250 -- O descarte vale para as regras de negócio, não para a valida
          -de do arquivo: uma ocorrência descartada que traz escape sem c
          -aractere válido torna o arquivo inteiro erro de arquivo (seção
          - 4, RN-002).                                                  
      252 +- O descarte vale para as regras de negócio, não para a valida
          +de do arquivo: escape sem caractere válido em qualquer ponto d
          +e uma ocorrência descartada, no valor dela ou em qualquer prof
          +undidade dentro dele, torna o arquivo inteiro erro de arquivo 
          +(seção 4, RN-002).                                            
      253  
      254  **Origem:** necessidade operacional (a política não trata o fo
           rmato do arquivo); AMB-019.
      253 -**Aceite:** despesa com `"valor": 30.00` e depois `"valor": 50
          -.00` → avaliada com 50,00; `itens[].avisos` = [`chave repetida
          -: valor (2 ocorrências; valeu a última)`]. `colaborador.nome` 
          -repetido → `avisos` do topo = [`chave repetida: colaborador.no
          -me (2 ocorrências; valeu a última)`]; itens sem chave repetida
          - têm `avisos` vazio. Despesa com `"tem_nota_fiscal": true` e d
          -epois `"tem_nota_fiscal": "sim"` → `entrada_invalida`, com o a
          -viso de `tem_nota_fiscal`. `despesas` repetida na raiz → só a 
          -última lista é avaliada; um aviso `chave repetida: despesas (2
          - ocorrências; valeu a última)` no topo; chaves repetidas dentr
          -o da primeira lista não geram aviso. Chave `valor` três vezes 
          -→ um aviso, com `3 ocorrências`. Despesa com `"extra": {"x": 1
          -, "x": 2}, "obs": "a", "obs": "b", "extra": {"x": 3, "x": 4}` 
          -→ avisos, nesta ordem: `extra` (2), `obs` (2), `extra.x` (2). 
          -Alimentação fora de viagem com `"valor": 30.00` e depois `"\u0
          -076alor": 90.00` → vale 90,00, `parcial` com 60,00, aviso de `
          -valor`. Despesa com `"obs": "\uD800"` e depois `"obs": "ok"` →
          - erro de arquivo, sem saída.                                  
      255 +**Aceite:** despesa com `"valor": 30.00` e depois `"valor": 50
          +.00` → avaliada com 50,00; `itens[].avisos` = [`chave repetida
          +: valor (2 ocorrências; valeu a última)`]. `colaborador.nome` 
          +repetido → `avisos` do topo = [`chave repetida: colaborador.no
          +me (2 ocorrências; valeu a última)`]; itens sem chave repetida
          + têm `avisos` vazio. Despesa com `"tem_nota_fiscal": true` e d
          +epois `"tem_nota_fiscal": "sim"` → `entrada_invalida`, com o a
          +viso de `tem_nota_fiscal`. `despesas` repetida na raiz → só a 
          +última lista é avaliada; um aviso `chave repetida: despesas (2
          + ocorrências; valeu a última)` no topo; chaves repetidas dentr
          +o da primeira lista não geram aviso. Chave `valor` três vezes 
          +→ um aviso, com `3 ocorrências`. Despesa com `"extra": {"x": 1
          +, "x": 2}, "obs": "a", "obs": "b", "extra": {"x": 3, "x": 4}` 
          +→ avisos, nesta ordem: `extra` (2), `obs` (2), `extra.x` (2). 
          +Alimentação fora de viagem com `"valor": 30.00` e depois `"\u0
          +076alor": 90.00` → vale 90,00, `parcial` com 60,00, aviso de `
          +valor`. Despesa com `"obs": "\uD800"` e depois `"obs": "ok"` →
          + erro de arquivo, sem saída; o mesmo com `"extra": {"y": "\uDC
          +00"}` e depois `"extra": {}`.                                 
      256  
      257  ---
      258  
     ...
      484  
      485  ## 8. Ordem de aplicação das regras
      486  
      485 -Antes das etapas, a leitura do arquivo resolve chaves repetida
          -s pela última ocorrência (RN-013): todas as etapas veem só o v
          -alor que valeu.                                               
      487 +Antes das etapas, a leitura verifica o arquivo inteiro, inclus
          +ive as ocorrências descartadas (UTF-8 e escapes, seção 4; erro
          + de arquivo, RN-002), e resolve chaves repetidas pela última o
          +corrência (RN-013): todas as etapas veem só o valor que valeu.
      488  
      489  Cada despesa passa pelas etapas abaixo, nesta ordem. A primeir
           a etapa que a recusa encerra a avaliação dela.
      490  

⏺ A spec agora diz que \u0000 e \uFFFF são válidos, mas nenhum teste cobre isso.
  Acrescento o teste na correção da T-006 e no aceite dela:

⏺ Bash(python3 - <<'EOF'
      def edit(p, pairs):…)
  ⎿  1
     All checks passed!
     170 passed in 0.07s
  ⎿  Updated specs/001-motor-reembolso/DECISIONS.md (+1 -1)
      25  
      26  **Por quê:** escape sem par só aparece em arquivo corrompido ou
           gerado com defeito; o lugar onde ele está (valor que valeu ou 
          descartado, em qualquer profundidade) não muda isso. Recusar o 
          arquivo mantém a regra da seção 4 sem exceção e evita processar
           um arquivo suspeito. O ponto 2 aplica o mesmo motivo ao defeit
          o gravado sem escape: byte fora do UTF-8 é recusado onde quer q
          ue esteja; o BOM é aceito porque ferramentas comuns o gravam em
           arquivos corretos. O ponto 3 fecha o conjunto: caracteres de c
          ontrole e não caracteres existem no Unicode e podem ser gravado
          s em UTF-8, então não são defeito. Emoji válido (par completo o
          u caractere direto) continua aceito em qualquer texto.
      27  
      28 -**O que isso invalidou:** o código da T-006 (`_verificar_textos
         -` percorria só os valores que valeram); corrigido em commit `fi
         -x(T-006)`. Os pontos 2 a 4 não mudam código: o DT-002 já lia `u
         -tf-8-sig` estrito e verificava só U+D800 a U+DFFF, com testes n
         -a T-006 (`test_bom_e_aceito`, `test_rn002_utf8_invalido_e_erro_
         -de_arquivo`, inclusive substituto em bytes crus). DT-002 do `pl
         -an.md` alinhado na versão 1.2. Nenhum valor do exemplo (seção 9
         -) mudou; seção 7 não muda (contagem de 63 casos preservada).   
      28 +**O que isso invalidou:** o código da T-006 (`_verificar_textos
         +` percorria só os valores que valeram); corrigido em commit `fi
         +x(T-006)`. Os pontos 2 a 4 não mudam código: o DT-002 já lia `u
         +tf-8-sig` estrito e verificava só U+D800 a U+DFFF, com testes n
         +a T-006 (`test_bom_e_aceito`, `test_rn002_utf8_invalido_e_erro_
         +de_arquivo`, inclusive substituto em bytes crus); o ponto 3 gan
         +ha `test_escape_fora_dos_substitutos_forma_caractere_valido`. D
         +T-002 do `plan.md` alinhado na versão 1.2. Nenhum valor do exem
         +plo (seção 9) mudou; seção 7 não muda (contagem de 63 casos pre
         +servada).                                                      
      29  
      30  **Tasks afetadas:** T-006 (aceite ganha o teste de ocorrência d
          escartada).
      31  
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+1 -1)
      65    - **Tipo:** estrutura (leitura de JSON)
      66    - **Atende:** RN-002 (arquivo que não é JSON válido; escape q
          ue não forma caractere válido), seção 4 da spec (número pelo va
          lor decimal exato; texto depois de decodificados os escapes), D
          T-001, DT-002
      67    - **Depende de:** T-001
      68 -  - **Aceite:** `tests/test_leitura_json.py` passa: `test_rn002
         -_nan_e_erro_de_arquivo` (`NaN`, `Infinity`, `-Infinity`); `test
         -_rn002_json_malformado_e_erro_de_arquivo`; `test_rn002_utf8_inv
         -alido_e_erro_de_arquivo`; `test_rn002_escape_sem_par_em_valor_e
         -_erro_de_arquivo` e `..._em_chave_...` (`\ud800`); `test_rn002_
         -escape_sem_par_em_ocorrencia_descartada_e_erro_de_arquivo` (`"o
         -bs": "\ud800", "obs": "ok"`, em valor e em objeto aninhado desc
         -artado; D-006); `test_bom_e_aceito`; `test_numero_lido_pelo_val
         -or_exato` (`33.333`, `999999999.99999999999`, `1e999999`, `1e-9
         -99999` e inteiro de 5.000 dígitos lidos como `Decimal` exato, s
         -em erro); `test_escapes_validos_decodificados` (`"2026-07-03"` 
         -→ `2026-07-03`; emoji em par de escapes igual ao emoji direto).
      68 +  - **Aceite:** `tests/test_leitura_json.py` passa: `test_rn002
         +_nan_e_erro_de_arquivo` (`NaN`, `Infinity`, `-Infinity`); `test
         +_rn002_json_malformado_e_erro_de_arquivo`; `test_rn002_utf8_inv
         +alido_e_erro_de_arquivo`; `test_rn002_escape_sem_par_em_valor_e
         +_erro_de_arquivo` e `..._em_chave_...` (`\ud800`); `test_rn002_
         +escape_sem_par_em_ocorrencia_descartada_e_erro_de_arquivo` (`"o
         +bs": "\ud800", "obs": "ok"`, em valor e em objeto aninhado desc
         +artado; D-006); `test_escape_fora_dos_substitutos_forma_caracte
         +re_valido` (`\u0000`, `\uffff`, `\ufdd0` lidos como caractere, 
         +sem erro; D-006); `test_bom_e_aceito`; `test_numero_lido_pelo_v
         +alor_exato` (`33.333`, `999999999.99999999999`, `1e999999`, `1e
         +-999999` e inteiro de 5.000 dígitos lidos como `Decimal` exato,
         + sem erro); `test_escapes_validos_decodificados` (`"2026-07-03"
         +` → `2026-07-03`; emoji em par de escapes igual ao emoji direto
         +).                                                             
      69    - **Commit:** e84693c
      70  
      71  - [x] **T-007** — Chaves repetidas: `ObjetoJson` via `object_pa
          irs_hook` (vale a última ocorrência) e percurso que gera os avi
          sos do topo e de cada elemento de `despesas`, com texto, caminh
          o, contagem e ordem da RN-013 (DT-010).
  ⎿  Updated tests/test_leitura_json.py (+10 -0)
       87          ler_json(texto)
       88  
       89  
       90 +@pytest.mark.parametrize(                                     
       91 +    "escape, caractere",                                      
       92 +    [(r"\u0000", "\x00"), (r"\uffff", "\uffff"), (r"\ufdd0", "
          +\ufdd0")],                                                    
       93 +)                                                             
       94 +def test_escape_fora_dos_substitutos_forma_caractere_valido(es
          +cape, caractere):                                             
       95 +    """Seção 4 / D-006: só U+D800 a U+DFFF sem par são inválid
          +os; o resto é válido."""                                      
       96 +    documento = ler_json(f'{{"obs": "{escape}"}}'.encode())   
       97 +    assert documento["obs"] == caractere                      
       98 +                                                              
       99 +                                                              
      100  def test_bom_e_aceito():
      101      """DT-002: BOM UTF-8 no início é ignorado (RFC 8259)."""
      102      documento = ler_json(b'\xef\xbb\xbf{"nome": "Jo\xc3\xa3o"}
           ')

⏺ Agora a rodada de confirmação do spec-adversary:

⏺ spec-adversary(Confirmação adversarial spec 1.9)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ Coloquei na spec as três decisões que você aprovou:
  - Seção 4:
    - a entrada é UTF-8 e o BOM no início é ignorado;
    - byte fora do UTF-8, em qualquer lugar, é erro de arquivo;
    - os únicos escapes inválidos são os de \uD800 a \uDFFF sem par;
    - a verificação vale em qualquer profundidade, inclusive dentro de valor
      descartado.
  - RN-002, RN-013 e seção 8: mesma coisa dita explicitamente. A RN-013 ganhou
    também o exemplo aninhado no Aceite.
  - D-006: passa a registrar os 4 pontos.

  Além do combinado, acrescentei um teste: a spec agora diz que \u0000, \uFFFF e
  \uFDD0 são válidos, e nada verificava isso. O teste confirma que o código já
  os aceita, então não houve mudança de código por causa dele. O teste também
  entrou no aceite da T-006 e na D-006. A suíte está com 170 testes passando e o
  ruff limpo.

  A rodada de confirmação do spec-adversary está em andamento. Quando terminar,
  trago o resultado e, se não houver bloqueante, faço os 4 commits.

✻ Churned for 46s · done 11:33 PM

› Message from spec-adversary
  Encontrei 4 problemas na spec 1.9, 2 deles bloqueantes.

  As três decisões estão na spec sem contradição direta com o resto:
  - **UTF-8 e BOM:** seção 4, linha 70, e RN-002.
  - **Escapes inválidos só de `\uD800` a `\uDFFF` sem par:** seção 4, linha 72.
  - **Escape inválido em ocorrência descartada, em qualquer profundidade:**
  seção 4, RN-002, RN-013 (linha 252 e aceite) e seção 8, linha 487.

  A D-006 descreve o que está no texto. A seção 7 continua com 63 linhas, como a
  D-006 afirma. Os problemas abaixo vêm de redação nova da 1.9 ou de pontos ao
  lado dela que continuam sem resposta.

  ### 1. Quais erros de arquivo valem para a ocorrência descartada —
  [BLOQUEANTE] — ambiguidade

  - **Regra afetada:** RN-013 (linha 252), seção 8 (linha 487), RN-002 (lista de
  erro de arquivo).
  - **Cenário de entrada:**
    - Na raiz: `"colaborador": {"id": "c-1", "nome": ""}, "colaborador": {"id":
  "c-1", "nome": "Ana"}` e uma alimentação válida de 30,00 em 2026-07-03, com
  nota.
    - Variações:
      - `"periodo": {"inicio": "2026-07-32", "fim": "2026-07-31"}` seguido de um
  `periodo` válido;
      - `"despesas": "x", "despesas": [...]`;
      - dentro de `colaborador`: `"nome": "  ", "nome": "Ana"`.
  - **Comportamento pela interpretação atual:** indefinido.
    - A RN-013 diz que "o descarte vale para as regras de negócio, não para a
  validade do arquivo".
    - A seção 8 diz que a leitura verifica "o arquivo inteiro, inclusive as
  ocorrências descartadas (UTF-8 e escapes, seção 4; **erro de arquivo,
  RN-002**)".
    - Leitura A: só a codificação, os escapes e a sintaxe atingem a ocorrência
  descartada. Aí vale o `nome` "Ana", sai a saída completa e o aviso `chave
  repetida: colaborador (2 ocorrências; valeu a última)`.
    - Leitura B: "validade do arquivo" e "erro de arquivo, RN-002" incluem todas
  as condições de erro de arquivo da RN-002, como `nome` vazio, data inválida
  em `inicio` ou `despesas` que não é lista. Aí não há saída e o código de saída
  é diferente de 0.
    - A lista da RN-002 cita "inclusive dentro de ocorrência descartada" só no
  item do escape, o que puxa para A. O parêntese da seção 8 puxa para B.
  - **Por que é um problema:** o cenário é exatamente o que a AMB-019 usa como
  justificativa: uma "correção feita ao final do registro". Conforme a leitura,
  o mesmo arquivo gera a saída inteira ou nenhuma saída. A mesma dúvida vale, de
  forma mais fraca, para a despesa: `"tem_nota_fiscal": "sim"` seguido de
  `"tem_nota_fiscal": true`. O aceite só cobre a ordem inversa.
  - **Pergunta para decisão:** além de UTF-8, escapes e sintaxe, alguma outra
  condição de erro de arquivo da RN-002 é verificada numa ocorrência descartada
  por chave repetida? Se nenhuma, o parêntese "erro de arquivo, RN-002" da seção
  8 continua dizendo o que se pretende?

  ### 2. "JSON válido" não tem definição: caracteres crus e números fora do
  padrão — [BLOQUEANTE] — lacuna

  - **Regra afetada:** RN-002 ("que não é JSON válido (seção 4)") e seção 4,
  linhas 70 e 72.
  - **Cenário de entrada:**
    - (a) Uma despesa com `"categoria": "alimentacao<TAB>"`, onde `<TAB>` é o
  byte 0x09 gravado cru dentro do texto, sem escape. O resto da despesa é
  válido: 30,00, com nota, em 2026-07-03.
    - (b) O mesmo com um byte 0x00 cru dentro de `descricao`.
    - (c) `"valor": NaN`, `"valor": Infinity`, `"valor": 01.5` ou `"valor": .5`.
  - **Comportamento pela interpretação atual:** indefinido.
    - A seção 4 diz que só os bytes fora do UTF-8 são erro "em qualquer lugar".
  0x09 e 0x00 são UTF-8 válido.
    - A 1.9 diz que `\u0000` e caracteres de controle formam caractere válido
  quando vêm como escape. Um leitor pode concluir que a forma crua também vale.
  Nesse caso, (a) dá `alimentacao` aprovada com 30,00.
    - Pela gramática estrita do formato, o caractere de controle cru dentro de
  texto torna o arquivo inválido: erro de arquivo, sem saída.
    - No caso (c), o resultado pode ser erro de arquivo, `entrada_invalida`
  (valor que não é número) ou um número aceito.
    - A seção 4, citada pela RN-002, não diz qual gramática define "JSON
  válido".
  - **Por que é um problema:** a 1.9 fechou com precisão o que é byte válido e
  escape válido, mas não o que é JSON válido. O mesmo arquivo dá a saída
  completa ou nenhuma saída conforme a gramática adotada. Um tab colado de
  planilha dentro de um texto é um caso plausível em arquivo montado à mão.
  - **Pergunta para decisão:** qual é a definição de "JSON válido" na RN-002? Em
  particular:
    - um caractere de controle gravado cru dentro de um texto é erro de arquivo?
    - `NaN`, `Infinity` e números com zero à esquerda ou sem dígito antes do
  ponto são erro de arquivo, `entrada_invalida` ou outra coisa?

  ### 3. "Sem o par correspondente": a ordem dos substitutos não está fixada —
  [PODE ESPERAR] — ambiguidade

  - **Regra afetada:** seção 4, linha 72.
  - **Cenário de entrada:** `"obs": "\uDC00\uD800"` (o baixo antes do alto, os
  dois adjacentes) e `"obs": "\uD800😀"` (um alto solto seguido de um par
  completo).
  - **Comportamento pela interpretação atual:** a spec não define o que é "par
  correspondente".
    - Se o par é só alto seguido imediatamente de baixo, o primeiro cenário é
  erro de arquivo.
    - Se basta existirem os dois, o primeiro cenário passaria, mas sem nenhum
  caractere resultante definido.
    - O segundo cenário depende de como o alto solto é pareado.
  - **Por que é um problema:** só aparece em arquivo corrompido, mas a frase "os
  únicos escapes que não formam caractere válido" virou uma lista fechada, e o
  critério do par faz parte dela.
  - **Pergunta para decisão:** "par correspondente" quer dizer exatamente um
  escape de `\uD800`–`\uDBFF` seguido imediatamente de um escape de
  `\uDC00`–`\uDFFF`, com qualquer outra combinação sendo escape inválido?

  ### 4. BOM: só um, ou também repetido no início — [PODE ESPERAR] — lacuna

  - **Regra afetada:** seção 4, linha 70 ("uma marca BOM no início do arquivo é
  ignorada").
  - **Cenário de entrada:** o arquivo começa com `EF BB BF EF BB BF {` e o JSON
  é válido em seguida. Isso acontece, por exemplo, quando uma ferramenta
  acrescenta um BOM a um arquivo que já tinha um.
  - **Comportamento pela interpretação atual:** indefinido.
    - Lendo "uma" como "exatamente uma", o segundo U+FEFF fica fora de qualquer
  texto e o arquivo não é JSON válido: erro de arquivo.
    - Lendo "uma" como "a marca", que pode se repetir, os dois são ignorados e o
  arquivo é processado.
  - **Por que é um problema:** o mesmo arquivo dá a saída completa ou nenhuma
  saída. O caso é raro.
  - **Pergunta para decisão:** só um BOM no início é ignorado, ou qualquer
  sequência de BOMs no início?

  ---

  1. **Decidir antes da implementação:** 1, 2.
  2. **Pode ser decidido depois:** 3, 4.

  Arquivos lidos:
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md` e
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md`.

⏺ Antes de levar os 4 pontos a você, confiro o que o código faz hoje em cada
  cenário:

  Ran 1 shell command (ctrl+o to expand)

⏺ Agent "Confirmação adversarial spec 1.9" finished · 1m 47s
⏺ A rodada de confirmação encontrou 4 problemas, 2 bloqueantes. Testei no código
  o que acontece hoje em cada cenário. Em três deles o código já faz algo
  coerente e só falta escrever na spec. No quarto, o do BOM, o código tem um
  comportamento acidental.

  1. Quais erros valem para a parte descartada? (BLOQUEANTE, falha da minha 
  redação)

  Exemplo: "colaborador": {"nome": ""} seguido de "colaborador": {"nome": 
  "Ana"}.

  Na seção 8 eu escrevi "verifica o arquivo inteiro, inclusive as ocorrências
  descartadas (... erro de arquivo, RN-002)". Isso pode ser lido como se todas
  as validações da RN-002 (nome vazio, data inválida etc.) valessem também para
  a parte descartada. Nesse caso esse arquivo seria recusado, quando a ideia da
  chave repetida é justamente aceitar a correção feita no fim.

  → Proposta: na parte descartada, só se verifica se o arquivo está bem formado
  (UTF-8, escapes, sintaxe JSON). As validações de conteúdo olham só o que
  valeu, então esse exemplo é processado com nome "Ana" e um aviso. Corrijo a
  frase da seção 8 e a da RN-013.

  2. O que é "JSON válido"? (BLOQUEANTE)

  A spec não define. Testei o código, e ele recusa como erro de arquivo:
  - tab ou caractere nulo gravados crus dentro de um texto;
  - NaN;
  - números como 01.5, .5, 1. e +1.

  Isso é exatamente o padrão oficial do JSON (RFC 8259).

  → Proposta: a spec passa a dizer "JSON válido conforme a RFC 8259", com esses
  exemplos. Um tab colado dentro de um texto vira erro de arquivo; quem gera o
  arquivo precisa escrever \t.

  3. O que é "par correspondente"? (pode esperar)

  Hoje o código só aceita a metade alta (\uD800–\uDBFF) seguida imediatamente da
  metade baixa (\uDC00–\uDFFF). A ordem invertida e a metade solta antes de um
  emoji são recusadas.

  → Proposta: escrever essa definição na spec. O código não muda.

  4. BOM repetido (pode esperar, mas o código está estranho)

  Hoje o código aceita dois BOMs seguidos no início. Isso não foi decidido: cada
  etapa da leitura remove um BOM por conta própria.

  → Proposta: só um BOM no início é ignorado. Um segundo BOM é erro de arquivo,
  como qualquer outro defeito de formato. Isso exige um ajuste pequeno no
  código, com teste, dentro do mesmo fix(T-006).

  Se concordar com as quatro propostas, aplico, rodo mais uma confirmação do
  spec-adversary e então faço os commits.

✻ Baked for 2m 53s · done 11:36 PM

❯ concordo                                                                      

  Ran 1 shell command (ctrl+o to expand)

⏺ Bash(python3 - <<'EOF'
      def edit(p, pairs):…)
  ⎿   specs/001-motor-reembolso/DECISIONS.md | 27 +++++++++++++++++++++++++
     ++
      specs/001-motor-reembolso/plan.md      |  4 ++--
     … +3 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/DECISIONS.md (+8 -4)
      12  
      13  ## D-006 — Arquivo defeituoso: escape inválido em ocorrência de
          scartada e codificação da entrada: spec 1.8 → 1.9 · `2026-10-01
          `
      14  
      15 -**Gatilho:** revisão independente da T-007 (`docs/reviews/T-007
         -.md`, revisões 1 e 2, "Decisões necessárias" 1). A seção 4 dizi
         -a que escape sem caractere válido "em qualquer chave ou valor" 
         -é erro de arquivo; a RN-013 dizia que as ocorrências descartada
         -s por chave repetida "nenhuma regra as considera". Para `"obs":
         - "\uD800", "obs": "ok"` as duas leituras davam resultados opost
         -os (erro de arquivo × despesa processada com aviso). O código d
         -a T-006 seguia a segunda sem decisão explícita: só verificava o
         -s valores que valeram. Decidido pelo responsável (ponto 1). A r
         -odada do `spec-adversary` sobre a primeira redação da 1.9 apont
         -ou 3 problemas (1 bloqueante): a codificação da entrada não est
         -ava na spec (só no DT-002 do plano), o parêntese `\uD800` a `\u
         -DFFF` podia ser lido como exemplo e não como lista, e o alcance
         - do descarte em profundidade era ambíguo na RN-013. O responsáv
         -el aceitou as 3 recomendações (pontos 2 a 4), que registram na 
         -spec o que o plano e o código já faziam. Sessão `docs/sessions/
         -18-*`.                                                         
      15 +**Gatilho:** revisão independente da T-007 (`docs/reviews/T-007
         +.md`, revisões 1 e 2, "Decisões necessárias" 1). A seção 4 dizi
         +a que escape sem caractere válido "em qualquer chave ou valor" 
         +é erro de arquivo; a RN-013 dizia que as ocorrências descartada
         +s por chave repetida "nenhuma regra as considera". Para `"obs":
         + "\uD800", "obs": "ok"` as duas leituras davam resultados opost
         +os (erro de arquivo × despesa processada com aviso). O código d
         +a T-006 seguia a segunda sem decisão explícita: só verificava o
         +s valores que valeram. Decidido pelo responsável (ponto 1). A r
         +odada do `spec-adversary` sobre a primeira redação da 1.9 apont
         +ou 3 problemas (1 bloqueante): a codificação da entrada não est
         +ava na spec (só no DT-002 do plano), o parêntese `\uD800` a `\u
         +DFFF` podia ser lido como exemplo e não como lista, e o alcance
         + do descarte em profundidade era ambíguo na RN-013. O responsáv
         +el aceitou as 3 recomendações (pontos 2 a 4), que registram na 
         +spec o que o plano e o código já faziam. A rodada de confirmaçã
         +o apontou 4 problemas (2 bloqueantes): a seção 8 podia ser lida
         + como se todo erro de arquivo da RN-002 valesse para a ocorrênc
         +ia descartada; "JSON válido" não tinha definição (caractere de 
         +controle cru, `NaN`, `01.5`); "par correspondente" e BOM repeti
         +do sem resultado. O responsável aceitou as 4 recomendações (pon
         +tos 5 a 8). Sessão `docs/sessions/18-*`.                       
      16  
      17  **O que mudou na spec:**
      18  
     ...
      22  | 2 | Codificação da entrada (**bloqueante** na revisão) | inde
          finida na spec (BOM, Latin-1, substituto gravado em bytes crus)
           | UTF-8; BOM no início ignorado; byte fora do UTF-8 em qualque
          r lugar → erro de arquivo | seção 4, RN-002 |
      23  | 3 | Conjunto de escapes inválidos | parêntese `\uD800` a `\uD
          FFF` lido como lista ou exemplo | lista completa; `\u0000`, `\u
          FFFF` e demais formam caractere válido | seção 4 |
      24  | 4 | Profundidade do descarte | RN-013 podia ser lida como só 
          o primeiro nível | em qualquer profundidade; explicitado na RN-
          002, na RN-013 (regra e aceite) e na seção 8 | RN-002, RN-013, 
          seção 8 |
      25 +| 5 | Quais erros atingem a ocorrência descartada (**bloqueante
         +** na confirmação) | seção 8 citava "erro de arquivo, RN-002" s
         +em restrição | só a forma do arquivo (UTF-8, JSON válido, escap
         +es); campos ausentes, vazios, de tipo errado ou datas inválidas
         + valem só para o valor que valeu (`nome` `""` corrigido por `no
         +me` `"Ana"` é processado) | RN-013, seção 8 |                  
      26 +| 6 | Definição de "JSON válido" (**bloqueante** na confirmação
         +) | indefinida | RFC 8259 sem extensões: caractere de controle 
         +cru em texto, `NaN`/`Infinity`, `01.5`, `.5`, `1.`, `+1` → erro
         + de arquivo | seção 4 |                                        
      27 +| 7 | Par correspondente | indefinido | escape `\uD800`–`\uDBFF
         +` seguido imediatamente de `\uDC00`–`\uDFFF`; qualquer outra co
         +mbinação é inválida | seção 4 |                                
      28 +| 8 | BOM repetido no início | indefinido (código aceitava dois
         +, por efeito de duas camadas de leitura) | só um BOM é ignorado
         +; o segundo torna o arquivo JSON inválido | seção 4 |          
      29  
      26 -**Por quê:** escape sem par só aparece em arquivo corrompido ou
         - gerado com defeito; o lugar onde ele está (valor que valeu ou 
         -descartado, em qualquer profundidade) não muda isso. Recusar o 
         -arquivo mantém a regra da seção 4 sem exceção e evita processar
         - um arquivo suspeito. O ponto 2 aplica o mesmo motivo ao defeit
         -o gravado sem escape: byte fora do UTF-8 é recusado onde quer q
         -ue esteja; o BOM é aceito porque ferramentas comuns o gravam em
         - arquivos corretos. O ponto 3 fecha o conjunto: caracteres de c
         -ontrole e não caracteres existem no Unicode e podem ser gravado
         -s em UTF-8, então não são defeito. Emoji válido (par completo o
         -u caractere direto) continua aceito em qualquer texto.         
      30 +**Por quê:** escape sem par só aparece em arquivo corrompido ou
         + gerado com defeito; o lugar onde ele está (valor que valeu ou 
         +descartado, em qualquer profundidade) não muda isso. Recusar o 
         +arquivo mantém a regra da seção 4 sem exceção e evita processar
         + um arquivo suspeito. O ponto 2 aplica o mesmo motivo ao defeit
         +o gravado sem escape: byte fora do UTF-8 é recusado onde quer q
         +ue esteja; o BOM é aceito porque ferramentas comuns o gravam em
         + arquivos corretos. O ponto 3 fecha o conjunto: caracteres de c
         +ontrole e não caracteres existem no Unicode e podem ser gravado
         +s em UTF-8, então não são defeito. O ponto 5 preserva o motivo 
         +da AMB-019: a chave repetida existe para aceitar a correção fei
         +ta ao final do registro, e recusar o arquivo pelo conteúdo do v
         +alor corrigido anularia isso; só a forma do arquivo, que indica
         + defeito na geração, é verificada por inteiro. Os pontos 6 e 7 
         +adotam o padrão do formato, que qualquer ferramenta consegue co
         +nferir. O ponto 8 mantém a regra estrita: um BOM é prática comu
         +m de ferramentas, dois é defeito. Emoji válido (par completo ou
         + caractere direto) continua aceito em qualquer texto.          
      31  
      28 -**O que isso invalidou:** o código da T-006 (`_verificar_textos
         -` percorria só os valores que valeram); corrigido em commit `fi
         -x(T-006)`. Os pontos 2 a 4 não mudam código: o DT-002 já lia `u
         -tf-8-sig` estrito e verificava só U+D800 a U+DFFF, com testes n
         -a T-006 (`test_bom_e_aceito`, `test_rn002_utf8_invalido_e_erro_
         -de_arquivo`, inclusive substituto em bytes crus); o ponto 3 gan
         -ha `test_escape_fora_dos_substitutos_forma_caractere_valido`. D
         -T-002 do `plan.md` alinhado na versão 1.2. Nenhum valor do exem
         -plo (seção 9) mudou; seção 7 não muda (contagem de 63 casos pre
         -servada).                                                      
      32 +**O que isso invalidou:** o código da T-006 (`_verificar_textos
         +` percorria só os valores que valeram); corrigido em commit `fi
         +x(T-006)`. Os pontos 2 a 4 não mudam código: o DT-002 já lia `u
         +tf-8-sig` estrito e verificava só U+D800 a U+DFFF, com testes n
         +a T-006 (`test_bom_e_aceito`, `test_rn002_utf8_invalido_e_erro_
         +de_arquivo`, inclusive substituto em bytes crus); o ponto 3 gan
         +ha `test_escape_fora_dos_substitutos_forma_caractere_valido`. O
         +s pontos 5 a 7 também refletem o comportamento já existente (po
         +ntos 6 e 7 ganham casos em `test_rn002_json_malformado_e_erro_d
         +e_arquivo` e `test_rn002_escape_sem_par_em_valor_e_erro_de_arqu
         +ivo`; o ponto 5 é coberto na T-008, que valida o cabeçalho sobr
         +e o valor que valeu). O ponto 8 muda código: o segundo BOM era 
         +aceito; corrigido no mesmo `fix(T-006)`, com `test_segundo_bom_
         +e_erro_de_arquivo`. DT-002 do `plan.md` alinhado na versão 1.2.
         + Nenhum valor do exemplo (seção 9) mudou; seção 7 não muda (con
         +tagem de 63 casos preservada).                                 
      33  
      34  **Tasks afetadas:** T-006 (aceite ganha o teste de ocorrência d
          escartada).
      35  
      32 -**Custo:** 4 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`, `t
         -asks.md`) + correção de uma função e um teste. Duas rodadas do 
         -`spec-adversary` (sobre a primeira redação da 1.9 e de confirma
         -ção).                                                          
      36 +**Custo:** 4 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`, `t
         +asks.md`) + correção de uma função e um teste. Três rodadas do 
         +`spec-adversary` (sobre a primeira redação da 1.9, confirmação 
         +com 4 achados e confirmação final).                            
      37  
      38  ---
      39  
  ⎿  Updated specs/001-motor-reembolso/spec.md (+6 -4)
      67  
      68  Se um mesmo objeto do arquivo traz a mesma chave mais de uma ve
          z, vale a última ocorrência, e a saída avisa que as anteriores 
          foram descartadas (RN-013).
      69  
      70 -O arquivo de entrada é lido em UTF-8; uma marca BOM no início d
         -o arquivo é ignorada. Um byte ou sequência de bytes que não for
         -ma UTF-8 válido, em qualquer lugar do arquivo (inclusive um car
         -actere de `U+D800` a `U+DFFF` gravado diretamente em bytes, ou 
         -um arquivo em outra codificação, como Latin-1), é erro de arqui
         -vo (RN-002).                                                   
      70 +O arquivo de entrada é lido em UTF-8; uma única marca BOM no in
         +ício do arquivo é ignorada (uma segunda marca logo em seguida n
         +ão é ignorada e torna o arquivo JSON inválido). Um byte ou sequ
         +ência de bytes que não forma UTF-8 válido, em qualquer lugar do
         + arquivo (inclusive um caractere de `U+D800` a `U+DFFF` gravado
         + diretamente em bytes, ou um arquivo em outra codificação, como
         + Latin-1), é erro de arquivo (RN-002).                         
      71  
      72 -Todo texto da entrada, chave ou valor, vale pelo seu conteúdo *
         -*depois de decodificados os escapes** do arquivo (`"2026\u002d0
         -7\u002d03"` é a data `2026-07-03`), e "caractere" é o caractere
         - Unicode (um emoji escrito como par de escapes é igual ao mesmo
         - emoji escrito diretamente). Um escape que não forma caractere 
         -Unicode válido, em qualquer chave ou valor, é erro de arquivo (
         -RN-002), em qualquer profundidade, inclusive dentro de uma ocor
         -rência descartada por chave repetida (RN-013). Os únicos escape
         -s que não formam caractere válido são os de `\uD800` a `\uDFFF`
         - sem o par correspondente; qualquer outro escape, inclusive de 
         -caractere de controle (`\u0000`) ou de não caractere do Unicode
         - (`\uFFFF`), forma um caractere válido.                        
      72 +"JSON válido" é o formato definido na RFC 8259, sem extensões. 
         +Em particular, são erro de arquivo (RN-002): caractere de contr
         +ole (U+0000 a U+001F, como tabulação ou quebra de linha) gravad
         +o diretamente dentro de um texto, em vez de escrito como escape
         + (`\t`, `\n`, `\u0000`); `NaN`, `Infinity` e `-Infinity`; númer
         +o com zero à esquerda (`01.5`), sem dígito antes ou depois do p
         +onto (`.5`, `1.`) ou com sinal `+` (`+1`).                     
      73 +                                                               
      74 +Todo texto da entrada, chave ou valor, vale pelo seu conteúdo *
         +*depois de decodificados os escapes** do arquivo (`"2026\u002d0
         +7\u002d03"` é a data `2026-07-03`), e "caractere" é o caractere
         + Unicode (um emoji escrito como par de escapes é igual ao mesmo
         + emoji escrito diretamente). Um escape que não forma caractere 
         +Unicode válido, em qualquer chave ou valor, é erro de arquivo (
         +RN-002), em qualquer profundidade, inclusive dentro de uma ocor
         +rência descartada por chave repetida (RN-013). Os únicos escape
         +s que não formam caractere válido são os de `\uD800` a `\uDFFF`
         + sem o par correspondente. Par correspondente é exatamente um e
         +scape de `\uD800` a `\uDBFF` seguido imediatamente de um escape
         + de `\uDC00` a `\uDFFF`; qualquer outra combinação (ordem inver
         +tida, um deles sozinho, um deles seguido de outro caractere) é 
         +escape que não forma caractere válido; qualquer outro escape, i
         +nclusive de caractere de controle (`\u0000`) ou de não caracter
         +e do Unicode (`\uFFFF`), forma um caractere válido.            
      75  
      76  ### Saída
      77  
     ...
      251  - Ordem dos avisos de cada lista: a ordem em que a primeira oc
           orrência de cada chave repetida aparece no arquivo.
      252  - Só geram aviso os objetos que continuam no arquivo depois de
            aplicada a última ocorrência: chaves repetidas dentro de um v
           alor descartado não geram aviso, nem entram no `<n>` nem na or
           dem de avisos de chaves com o mesmo caminho no valor que valeu
           .
      253  - O aviso não muda status, motivo nem valores, e aparece em qu
           alquer item, inclusive recusado. Em erro de arquivo não há saí
           da, logo não há aviso.
      252 -- O descarte vale para as regras de negócio, não para a valida
          -de do arquivo: escape sem caractere válido em qualquer ponto d
          -e uma ocorrência descartada, no valor dela ou em qualquer prof
          -undidade dentro dele, torna o arquivo inteiro erro de arquivo 
          -(seção 4, RN-002).                                            
      254 +- O descarte vale para as regras de negócio, não para a forma 
          +do arquivo: escape sem caractere válido, byte fora do UTF-8 ou
          + sintaxe que não é JSON válido em qualquer ponto de uma ocorrê
          +ncia descartada, no valor dela ou em qualquer profundidade den
          +tro dele, torna o arquivo inteiro erro de arquivo (seção 4, RN
          +-002). As demais condições da RN-002 (campos ausentes, de tipo
          + errado, vazios, datas inválidas etc.) valem só para o valor q
          +ue valeu: `"colaborador": {"id": "c-1", "nome": ""}` seguido d
          +e `"colaborador": {"id": "c-1", "nome": "Ana"}` é processado n
          +ormalmente, com `nome` `Ana` e o aviso de `colaborador`.      
      255  
      256  **Origem:** necessidade operacional (a política não trata o fo
           rmato do arquivo); AMB-019.
      257  **Aceite:** despesa com `"valor": 30.00` e depois `"valor": 50
           .00` → avaliada com 50,00; `itens[].avisos` = [`chave repetida
           : valor (2 ocorrências; valeu a última)`]. `colaborador.nome` 
           repetido → `avisos` do topo = [`chave repetida: colaborador.no
           me (2 ocorrências; valeu a última)`]; itens sem chave repetida
            têm `avisos` vazio. Despesa com `"tem_nota_fiscal": true` e d
           epois `"tem_nota_fiscal": "sim"` → `entrada_invalida`, com o a
           viso de `tem_nota_fiscal`. `despesas` repetida na raiz → só a 
           última lista é avaliada; um aviso `chave repetida: despesas (2
            ocorrências; valeu a última)` no topo; chaves repetidas dentr
           o da primeira lista não geram aviso. Chave `valor` três vezes 
           → um aviso, com `3 ocorrências`. Despesa com `"extra": {"x": 1
           , "x": 2}, "obs": "a", "obs": "b", "extra": {"x": 3, "x": 4}` 
           → avisos, nesta ordem: `extra` (2), `obs` (2), `extra.x` (2). 
           Alimentação fora de viagem com `"valor": 30.00` e depois `"\u0
           076alor": 90.00` → vale 90,00, `parcial` com 60,00, aviso de `
           valor`. Despesa com `"obs": "\uD800"` e depois `"obs": "ok"` →
            erro de arquivo, sem saída; o mesmo com `"extra": {"y": "\uDC
           00"}` e depois `"extra": {}`.
     ...
      486  
      487  ## 8. Ordem de aplicação das regras
      488  
      487 -Antes das etapas, a leitura verifica o arquivo inteiro, inclus
          -ive as ocorrências descartadas (UTF-8 e escapes, seção 4; erro
          - de arquivo, RN-002), e resolve chaves repetidas pela última o
          -corrência (RN-013): todas as etapas veem só o valor que valeu.
      489 +Antes das etapas, a leitura verifica a forma do arquivo inteir
          +o, inclusive das ocorrências descartadas (UTF-8, JSON válido e
          + escapes, seção 4), e resolve chaves repetidas pela última oco
          +rrência (RN-013): as demais validações da RN-002 e todas as et
          +apas veem só o valor que valeu.                               
      490  
      491  Cada despesa passa pelas etapas abaixo, nesta ordem. A primeir
           a etapa que a recusa encerra a avaliação dela.
      492  

⏺ Agora os testes. Primeiro os casos novos, antes de mexer no código:

⏺ Bash(python3 - <<'EOF'
      def edit(p, pairs):…)
  ⎿  FAILED tests/test_leitura_json.py::test_segundo_bom_e_erro_de_arquivo
     - Faile...
     1 failed, 41 passed in 0.03s
  ⎿  Updated tests/test_leitura_json.py (+16 -1)
      23          b"{'valor': 10}",
      24          b'{"valor": 10} {}',
      25          b'{"valor": 010}',
      26 +        b'{"valor": 01.5}',                                    
      27 +        b'{"valor": .5}',                                      
      28 +        b'{"valor": 1.}',                                      
      29 +        b'{"valor": +1}',                                      
      30 +        b'{"obs": "a\tb"}',  # tabulação crua dentro do texto  
      31 +        b'{"obs": "a\nb"}',  # quebra de linha crua dentro do t
         +exto                                                           
      32 +        b'{"obs": "a\x00b"}',  # U+0000 cru dentro do texto    
      33      ],
      34  )
      35  def test_rn002_json_malformado_e_erro_de_arquivo(texto):
      29 -    """RN-002: arquivo que não é JSON válido → erro de arquivo.
         -"""                                                            
      36 +    """RN-002 / D-006: não é JSON válido pela RFC 8259 → erro d
         +e arquivo."""                                                  
      37      with pytest.raises(ErroDeArquivo):
      38          ler_json(texto)
      39  
     ...
      59          rb'{"nome": "a\udc00b"}',
      60          rb'{"despesas": [{"id": "x\ud800"}]}',
      61          rb'{"lista": [["\udfff"]]}',
      62 +        rb'{"nome": "\udc00\ud800"}',  # par em ordem invertida
      63 +        b'{"nome": "\\ud800\xf0\x9f\x98\x80"}',  # alto solto a
         +ntes de emoji cru                                              
      64      ],
      65  )
      66  def test_rn002_escape_sem_par_em_valor_e_erro_de_arquivo(texto)
          :
     ...
      106      assert documento["obs"] == caractere
      107  
      108  
      109 +def test_segundo_bom_e_erro_de_arquivo():                     
      110 +    """Seção 4 / D-006: só um BOM no início é ignorado; o segu
          +ndo é erro."""                                                
      111 +    with pytest.raises(ErroDeArquivo):                        
      112 +        ler_json(b'\xef\xbb\xbf\xef\xbb\xbf{"a": 1}')         
      113 +                                                              
      114 +                                                              
      115  def test_bom_e_aceito():
      116      """DT-002: BOM UTF-8 no início é ignorado (RFC 8259)."""
      117      documento = ler_json(b'\xef\xbb\xbf{"nome": "Jo\xc3\xa3o"}
           ')

⏺ Só o teste do segundo BOM falha, como esperado. Os demais casos documentam
  comportamento que o código já tinha. Agora a correção:

⏺ Bash(python3 - <<'EOF'
      def edit(p, pairs):…)
  ⎿  All checks passed!
     180 passed in 0.07s
      specs/001-motor-reembolso/DECISIONS.md | 27 ++++++++++++++++++++++
     … +7 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/plan.md (+1 -1)
      121  ### DT-002 — Rejeitar o que não é JSON estrito
      122  
      123  **Contexto:** RN-002: arquivo que não é JSON válido é erro de 
           arquivo. O `json` da biblioteca padrão aceita `NaN`, `Infinity
           ` e `-Infinity`, que não são JSON.
      124 -**Decisão:** `simplejson` ≥ 4 já os rejeita na leitura por pad
          -rão (`allow_nan=False`); a versão mínima fica fixada no `pypro
          -ject.toml` e um teste garante que `"valor": NaN` é erro de arq
          -uivo, para a proteção não sumir numa troca de versão. Erro de 
          -parse → `ErroDeArquivo`. Bytes decodificados como UTF-8 estrit
          -o (`utf-8-sig`, aceitando BOM, que a RFC 8259 permite ignorar)
          -; falha de decodificação → `ErroDeArquivo`. O parser aceita em
          - silêncio um escape `\ud800` sem par (vira um caractere substi
          -tuto isolado na `str`, que a gravação em UTF-8 recusaria depoi
          -s); por isso, depois do parse, `entrada.py` percorre todas as 
          -chaves e textos — inclusive os das ocorrências descartadas por
          - chave repetida, pelos pares guardados no `ObjetoJson` (DT-010
          -; spec 1.9, D-006) — e levanta `ErroDeArquivo` se algum contiv
          -er caractere entre U+D800 e U+DFFF (seção 4 da spec). Pares de
          - escapes válidos já chegam combinados num único caractere.    
      124 +**Decisão:** `simplejson` ≥ 4 já os rejeita na leitura por pad
          +rão (`allow_nan=False`); a versão mínima fica fixada no `pypro
          +ject.toml` e um teste garante que `"valor": NaN` é erro de arq
          +uivo, para a proteção não sumir numa troca de versão. Erro de 
          +parse → `ErroDeArquivo`. Bytes decodificados como UTF-8 estrit
          +o (`utf-8-sig`, aceitando um BOM, que a RFC 8259 permite ignor
          +ar); falha de decodificação → `ErroDeArquivo`. O `simplejson` 
          +também descarta um U+FEFF inicial por conta própria, o que far
          +ia dois BOMs passarem; por isso um U+FEFF que sobra depois do 
          +`utf-8-sig` → `ErroDeArquivo` (spec 1.9, D-006). Caractere de 
          +controle cru em texto e números fora da gramática (`01.5`, `.5
          +`, `1.`, `+1`) já são rejeitados pelo parser estrito (`strict=
          +True`, padrão). O parser aceita em silêncio um escape `\ud800`
          + sem par (vira um caractere substituto isolado na `str`, que a
          + gravação em UTF-8 recusaria depois); por isso, depois do pars
          +e, `entrada.py` percorre todas as chaves e textos — inclusive 
          +os das ocorrências descartadas por chave repetida, pelos pares
          + guardados no `ObjetoJson` (DT-010; spec 1.9, D-006) — e levan
          +ta `ErroDeArquivo` se algum contiver caractere entre U+D800 e 
          +U+DFFF (seção 4 da spec). Pares de escapes válidos já chegam c
          +ombinados num único caractere.                                
      125  **Alternativa descartada:** aceitar `NaN` e tratar como "valor
            não é número" na despesa: transformaria arquivo inválido em p
           rocessamento normal.
      126  **Consequência:** `"valor": NaN` encerra a execução sem saída,
            como qualquer JSON inválido.
      127  
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+2 -2)
      65    - **Tipo:** estrutura (leitura de JSON)
      66    - **Atende:** RN-002 (arquivo que não é JSON válido; escape q
          ue não forma caractere válido), seção 4 da spec (número pelo va
          lor decimal exato; texto depois de decodificados os escapes), D
          T-001, DT-002
      67    - **Depende de:** T-001
      68 -  - **Aceite:** `tests/test_leitura_json.py` passa: `test_rn002
         -_nan_e_erro_de_arquivo` (`NaN`, `Infinity`, `-Infinity`); `test
         -_rn002_json_malformado_e_erro_de_arquivo`; `test_rn002_utf8_inv
         -alido_e_erro_de_arquivo`; `test_rn002_escape_sem_par_em_valor_e
         -_erro_de_arquivo` e `..._em_chave_...` (`\ud800`); `test_rn002_
         -escape_sem_par_em_ocorrencia_descartada_e_erro_de_arquivo` (`"o
         -bs": "\ud800", "obs": "ok"`, em valor e em objeto aninhado desc
         -artado; D-006); `test_escape_fora_dos_substitutos_forma_caracte
         -re_valido` (`\u0000`, `\uffff`, `\ufdd0` lidos como caractere, 
         -sem erro; D-006); `test_bom_e_aceito`; `test_numero_lido_pelo_v
         -alor_exato` (`33.333`, `999999999.99999999999`, `1e999999`, `1e
         --999999` e inteiro de 5.000 dígitos lidos como `Decimal` exato,
         - sem erro); `test_escapes_validos_decodificados` (`"2026-07-03"
         -` → `2026-07-03`; emoji em par de escapes igual ao emoji direto
         -).                                                             
      68 +  - **Aceite:** `tests/test_leitura_json.py` passa: `test_rn002
         +_nan_e_erro_de_arquivo` (`NaN`, `Infinity`, `-Infinity`); `test
         +_rn002_json_malformado_e_erro_de_arquivo`; `test_rn002_utf8_inv
         +alido_e_erro_de_arquivo`; `test_rn002_escape_sem_par_em_valor_e
         +_erro_de_arquivo` e `..._em_chave_...` (`\ud800`); `test_rn002_
         +escape_sem_par_em_ocorrencia_descartada_e_erro_de_arquivo` (`"o
         +bs": "\ud800", "obs": "ok"`, em valor e em objeto aninhado desc
         +artado; D-006); `test_escape_fora_dos_substitutos_forma_caracte
         +re_valido` (`\u0000`, `\uffff`, `\ufdd0` lidos como caractere, 
         +sem erro; D-006); `test_bom_e_aceito`; `test_segundo_bom_e_erro
         +_de_arquivo` (D-006); `test_rn002_json_malformado_e_erro_de_arq
         +uivo` inclui `01.5`, `.5`, `1.`, `+1` e tabulação, quebra de li
         +nha e U+0000 crus em texto; `test_rn002_escape_sem_par_em_valor
         +_e_erro_de_arquivo` inclui par invertido e alto solto antes de 
         +emoji (D-006); `test_numero_lido_pelo_valor_exato` (`33.333`, `
         +999999999.99999999999`, `1e999999`, `1e-999999` e inteiro de 5.
         +000 dígitos lidos como `Decimal` exato, sem erro); `test_escape
         +s_validos_decodificados` (`"2026-07-03"` → `2026-07-03`; emoji 
         +em par de escapes igual ao emoji direto).                      
      69    - **Commit:** e84693c
      70  
      71  - [x] **T-007** — Chaves repetidas: `ObjetoJson` via `object_pa
          irs_hook` (vale a última ocorrência) e percurso que gera os avi
          sos do topo e de cada elemento de `despesas`, com texto, caminh
          o, contagem e ordem da RN-013 (DT-010).
     ...
      79    - **Tipo:** regra
      80    - **Atende:** RN-002 (erro de arquivo), seção 4 da spec (Entr
          ada), DT-003
      81    - **Depende de:** T-006
      82 -  - **Aceite:** `tests/test_rn002_validacao_da_entrada.py` pass
         -a os testes de cabeçalho: `colaborador` ausente; `id`/`nome` au
         -sentes, não texto, vazios ou só com espaços em branco (inclusiv
         -e espaço não separável); `nome` só de U+200B, BOM ou U+001F → v
         -álido (não é espaço em branco, RN-002); `periodo.inicio`, `peri
         -odo.fim` ou `despesas` ausentes; `inicio`/`fim` que não são `AA
         -AA-MM-DD` válidas (`2026-7-1`, `20260701`, `2026-02-30`, dígito
         -s não ASCII); `inicio` posterior a `fim` → `ErroDeArquivo`. `in
         -icio` igual a `fim` → válido. `despesas: []` → válido. `compete
         -ncia` `202607` → nula, sem erro; `competencia` `"julho"` → copi
         -ada. `centro_custo` ausente → válido.                          
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
         +ada. `centro_custo` ausente → válido. `colaborador` com `nome` 
         +`""` seguido de `colaborador` com `nome` `"Ana"` → válido, `nom
         +e` `Ana` (só o valor que valeu é validado; RN-013, D-006).     
      83    - **Commit:**
      84  
      85  - [ ] **T-009** — Validação da despesa: cada elemento de `despe
          sas` vira `Despesa` (válida) ou `DespesaInvalida` (etapa 1 da s
          eção 8), com `categoria_saida` normalizada se reconhecida e os 
          avisos da T-007 anexados.
  ⎿  Updated src/reembolso/entrada.py (+3 -0)
      43          texto = conteudo.decode("utf-8-sig")
      44      except UnicodeDecodeError as erro:
      45          raise ErroDeArquivo("arquivo não está em UTF-8 válido")
           from erro
      46 +    if texto.startswith("\ufeff"):                             
      47 +        # `utf-8-sig` removeu o único BOM ignorado; um segundo 
         +é JSON inválido (D-006)                                        
      48 +        raise ErroDeArquivo("arquivo não é JSON válido: BOM rep
         +etido no início")                                              
      49      try:
      50          documento = simplejson.loads(
      51              texto,

⏺ Bash(python3 - <<'EOF'
      p = "specs/001-motor-reembolso/DECISIONS.md"…)
  ⎿  ok
  ⎿  Updated specs/001-motor-reembolso/DECISIONS.md (+1 -1)
      31  
      32  **O que isso invalidou:** o código da T-006 (`_verificar_textos
          ` percorria só os valores que valeram); corrigido em commit `fi
          x(T-006)`. Os pontos 2 a 4 não mudam código: o DT-002 já lia `u
          tf-8-sig` estrito e verificava só U+D800 a U+DFFF, com testes n
          a T-006 (`test_bom_e_aceito`, `test_rn002_utf8_invalido_e_erro_
          de_arquivo`, inclusive substituto em bytes crus); o ponto 3 gan
          ha `test_escape_fora_dos_substitutos_forma_caractere_valido`. O
          s pontos 5 a 7 também refletem o comportamento já existente (po
          ntos 6 e 7 ganham casos em `test_rn002_json_malformado_e_erro_d
          e_arquivo` e `test_rn002_escape_sem_par_em_valor_e_erro_de_arqu
          ivo`; o ponto 5 é coberto na T-008, que valida o cabeçalho sobr
          e o valor que valeu). O ponto 8 muda código: o segundo BOM era 
          aceito; corrigido no mesmo `fix(T-006)`, com `test_segundo_bom_
          e_erro_de_arquivo`. DT-002 do `plan.md` alinhado na versão 1.2.
           Nenhum valor do exemplo (seção 9) mudou; seção 7 não muda (con
          tagem de 63 casos preservada).
      33  
      34 -**Tasks afetadas:** T-006 (aceite ganha o teste de ocorrência d
         -escartada).                                                    
      34 +**Tasks afetadas:** T-006 (aceite ganha os testes de ocorrência
         + descartada, escapes válidos, JSON inválido pela RFC 8259, par 
         +correspondente e segundo BOM); T-008 (aceite ganha `colaborador
         +` corrigido por chave repetida, ponto 5).                      
      35  
      36  **Custo:** 4 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`, `t
          asks.md`) + correção de uma função e um teste. Três rodadas do 
          `spec-adversary` (sobre a primeira redação da 1.9, confirmação 
          com 4 achados e confirmação final).
      37  

⏺ spec-adversary(Confirmação final spec 1.9)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ Apliquei as 4 decisões:

  - Spec:
    - a seção 4 define "JSON válido" pela RFC 8259, define "par correspondente"
      e diz que só um BOM no início é ignorado;
    - a RN-013 e a seção 8 deixam claro que, na parte descartada, só se verifica
      a forma do arquivo, com o exemplo do colaborador corrigido.
  - D-006: agora registra os pontos 1 a 8.
  - Plano: a DT-002 explica o tratamento do BOM.
  - Tasks: os aceites da T-006 e da T-008 incluem os casos novos.
  - Código: a única mudança é recusar o segundo BOM. O teste desse caso falhou
    antes da correção e passa depois. Os outros casos novos (01.5, .5, 1., +1,
    tab, quebra de linha e nulo crus, par invertido) só registram o que o código
    já fazia.
  - Suíte: 180 testes passando, ruff limpo.

  Pedi ao spec-adversary que não reabra pontos já decididos. Ele está fazendo a
  confirmação final; quando terminar, trago o resultado.

✻ Churned for 1m 8s · done 11:37 PM

› Message from spec-adversary
  Resumo: 1 problema, nenhum bloqueante. A spec 1.9 reflete os pontos 5 a 8 da
  D-006 sem contradição.

  Arquivo revisado:
  /Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md (seções 4,
  5/RN-002, RN-013, 7, 8), conferido contra
  /Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md
  (D-006).

  **O que confere com a D-006:**
  - **Ponto 5:** o último item da RN-013 e o parágrafo de abertura da seção 8
  limitam o que se verifica na ocorrência descartada à forma do arquivo (UTF-8,
  JSON válido, escapes). As demais condições da RN-002 valem só para o valor que
  valeu, e o exemplo `nome ""` → `"Ana"` está na regra. A RN-002 não diz o
  contrário: o primeiro item dela só estende à ocorrência descartada a
  verificação de escapes. A frase "nenhuma regra as considera" da RN-013 fica
  qualificada por "o descarte vale para as regras de negócio".
  - **Ponto 6:** a seção 4 diz "RFC 8259 sem extensões" e dá os exemplos
  (controle cru U+0000–U+001F, `NaN`/`Infinity`, `01.5`, `.5`, `1.`, `+1`). Isso
  não contradiz o resto da spec:
    - chaves repetidas são permitidas pela RFC, então a RN-013 continua
  aplicável;
    - `1e999999` é número válido pela gramática, o que bate com a seção 7;
    - `\u0000` como escape e NEL/U+007F crus continuam válidos, o que bate com o
  White_Space da RN-002;
    - os exemplos `"alimentacao\t"` da RN-006 e da seção 7 estão em notação JSON
  (escape), não em tabulação crua.
  - **Ponto 7:** a definição de par correspondente não deixa dupla leitura. Cada
  alto só pode formar par com o escape imediatamente seguinte, e cada baixo só
  com o imediatamente anterior, então em `\uD800𐀀` ou `𐀀\uDC00` o resultado
  (erro de arquivo) não depende de como se agrupa. A seção 7 usa hexadecimal
  minúsculo (`\ud800`), o que é compatível.
  - **Ponto 8:** só um BOM no início é ignorado. Qualquer outro U+FEFF fora de
  texto (o segundo, ou um depois de espaço inicial) cai na regra geral de JSON
  inválido, e U+FEFF dentro de texto continua sendo caractere válido. A RFC 8259
  (seção 8.1) permite ignorar o BOM, então não há conflito com o ponto 6.

  ### 1. Limites de implementação permitidos pela RFC 8259 — [PODE ESPERAR] —
  ambiguidade

  - **Regra afetada:** seção 4 ("JSON válido" = RFC 8259 sem extensões), RN-002
  (erro de arquivo).
  - **Cenário de entrada:** um arquivo correto, com uma despesa válida
  (alimentação, 2026-07-03, 45,00, `tem_nota_fiscal` true) e um campo extra
  `"extra"` com 100.000 níveis de listas aninhadas (`[[[[...]]]]`). Variação: um
  campo extra de texto com centenas de megabytes.
  - **Comportamento pela interpretação atual:** indefinido. A gramática da RFC
  8259 não tem limite de profundidade nem de tamanho, então o arquivo é JSON
  válido: o campo extra é ignorado e a despesa sai `aprovado` com 45,00. Mas a
  seção 9 da mesma RFC permite que a implementação limite profundidade, tamanho
  do texto e tamanho dos textos internos. Pela leitura "RFC 8259 sem extensões",
  rejeitar por esses limites pode ser conforme ou não. O resultado pode ser
  processamento normal ou erro de arquivo, e uma terceira possibilidade é a
  execução cair sem respeitar a garantia da seção 4 de não criar nem alterar a
  saída. A faixa de números não entra nessa dúvida, porque a seção 4 já fixa
  "qualquer quantidade de dígitos e qualquer expoente".
  - **Por que é um problema:** ao adotar a RFC como definição, a 1.9 trouxe
  junto a liberdade que ela dá às implementações, e a spec não diz se essa
  liberdade vale. Fora de entrada maliciosa ou corrompida o cenário é improvável
  e não muda valores de despesas reais.
  - **Pergunta para decisão:** um arquivo que segue a gramática da RFC 8259 mas
  excede um limite de profundidade de aninhamento ou de tamanho deve ser
  processado normalmente, ser erro de arquivo, ou ficar registrado como fora de
  escopo ou risco aceito?

  Não encontrei nenhum outro caso sem resultado definido nem brecha nova
  introduzida pelas mudanças da 1.9.

  **Decidir antes da implementação:** nenhum.

  **Pode ser decidido depois:** 1.

⏺ Antes de trazer o resultado, testei o caso que sobrou no código atual:

  Ran 1 shell command (ctrl+o to expand)

⏺ Agent "Confirmação final spec 1.9" finished · 1m 22s

⏺ A confirmação final não encontrou nenhum bloqueante, e os pontos 5 a 8
  entraram na spec sem contradição. Sobrou 1 ponto que pode esperar, mas ao
  testá-lo achei um problema real no código.

  O ponto que sobrou: arquivo com aninhamento exagerado

  Exemplo: uma despesa válida com um campo extra que tem milhares de listas uma
  dentro da outra ([[[[...]]]]). A RFC permite que o programa imponha um limite
  de profundidade, mas a spec não diz o que acontece nesse caso.

  O que o código faz hoje

  - Com 500 níveis, o arquivo é aceito.
  - Com 5.000 níveis, o programa quebra com um erro interno do Python. Isso
    viola a regra de não mostrar stack trace em erro previsto e não segue o
    tratamento de erro de arquivo.

  Esse caso só aparece em arquivo malicioso ou corrompido, nunca em dados reais
  de despesas.

  Recomendação:
  - Código: capturar esse erro e transformá-lo em erro de arquivo, sem saída e
    sem stack trace. É uma linha a mais no mesmo fix(T-006), com teste.
  - Spec: registrar na seção 10 um risco aceito, sem fixar número: "um arquivo
    com aninhamento muito profundo (milhares de níveis) ou de tamanho exagerado
    pode ser recusado como erro de arquivo; o limite exato não é fixado, porque
    nenhum arquivo real de despesas chega perto dele".

  A alternativa seria fixar um limite, por exemplo 100 níveis. Seria uma regra
  nova, com número inventado, e eu evitaria.

  Se concordar, aplico isso, registro como ponto 9 da D-006 e já faço os 4
  commits, sem nova rodada do spec-adversary, porque o item vai para a seção 10
  como risco aceito e não muda regra nenhuma.

✻ Churned for 2m 40s · done 11:39 PM

❯ seguir a recomendaçào                                                         

  Searched for 1 pattern, ran 2 shell commands (ctrl+o to expand)

⏺ Primeiro o teste, que deve falhar com RecursionError:

⏺ Bash(python3 - <<'EOF'
      p = "tests/test_leitura_json.py"…)
  ⎿  E       RecursionError: maximum recursion depth exceeded while decodin
     g a JSON array from a string
     .venv/lib/python3.12/site-packages/simplejson/decoder.py:428: Recursio
     … +2 lines (ctrl+o to expand)
  ⎿  Updated tests/test_leitura_json.py (+8 -0)
      112          ler_json(b'\xef\xbb\xbf\xef\xbb\xbf{"a": 1}')
      113  
      114  
      115 +@pytest.mark.parametrize("niveis", [5_000, 100_000])          
      116 +def test_aninhamento_exagerado_e_erro_de_arquivo(niveis):     
      117 +    """Seção 10 / D-006: aninhamento de milhares de níveis → e
          +rro de arquivo."""                                            
      118 +    texto = b'{"extra": ' + b"[" * niveis + b"]" * niveis + b"
          +}"                                                            
      119 +    with pytest.raises(ErroDeArquivo):                        
      120 +        ler_json(texto)                                       
      121 +                                                              
      122 +                                                              
      123  def test_bom_e_aceito():
      124      """DT-002: BOM UTF-8 no início é ignorado (RFC 8259)."""
      125      documento = ler_json(b'\xef\xbb\xbf{"nome": "Jo\xc3\xa3o"}
           ')

⏺ Falha pelo motivo certo, mas levou 27 s, lento demais para o pre-commit. Faço
  a correção e meço cada caso:

⏺ Bash(python3 - <<'EOF'
      p = "src/reembolso/entrada.py"…)
  ⎿  def ler_json(conteudo: bytes):
         """Bytes → documento JSON estrito, números em `Decimal` (DT-001, D
     T-002)."""
     … +25 lines (ctrl+o to expand)
  ⎿  Updated src/reembolso/entrada.py (+4 -1)
      53              parse_int=Decimal,
      54              object_pairs_hook=ObjetoJson,
      55          )
      56 +        _verificar_textos(documento)                           
      57      except simplejson.JSONDecodeError as erro:
      58          raise ErroDeArquivo(f"arquivo não é JSON válido: {erro}
          ") from erro
      58 -    _verificar_textos(documento)                               
      59 +    except RecursionError as erro:                             
      60 +        # limite de aninhamento não fixado pela spec (seção 10,
         + D-006)                                                        
      61 +        raise ErroDeArquivo("arquivo com aninhamento profundo d
         +emais") from erro                                              
      62      return documento
      63  
      64  

⏺ Rápido agora: a lentidão vinha da formatação do traceback pelo pytest. Confiro
  também se o percurso de avisos da T-007 aguenta a maior profundidade que a
  leitura aceita:

  Ran 2 shell commands (ctrl+o to expand)

⏺ Agora a spec (seção 10), a D-006 (ponto 9), o plano e as tasks:

⏺ Bash(python3 - <<'EOF'
      def edit(p, pairs):…)
  ⎿  All checks passed!
     182 passed in 0.07s
      M specs/001-motor-reembolso/DECISIONS.md
     … +5 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/DECISIONS.md (+5 -4)
      12  
      13  ## D-006 — Arquivo defeituoso: escape inválido em ocorrência de
          scartada e codificação da entrada: spec 1.8 → 1.9 · `2026-10-01
          `
      14  
      15 -**Gatilho:** revisão independente da T-007 (`docs/reviews/T-007
         -.md`, revisões 1 e 2, "Decisões necessárias" 1). A seção 4 dizi
         -a que escape sem caractere válido "em qualquer chave ou valor" 
         -é erro de arquivo; a RN-013 dizia que as ocorrências descartada
         -s por chave repetida "nenhuma regra as considera". Para `"obs":
         - "\uD800", "obs": "ok"` as duas leituras davam resultados opost
         -os (erro de arquivo × despesa processada com aviso). O código d
         -a T-006 seguia a segunda sem decisão explícita: só verificava o
         -s valores que valeram. Decidido pelo responsável (ponto 1). A r
         -odada do `spec-adversary` sobre a primeira redação da 1.9 apont
         -ou 3 problemas (1 bloqueante): a codificação da entrada não est
         -ava na spec (só no DT-002 do plano), o parêntese `\uD800` a `\u
         -DFFF` podia ser lido como exemplo e não como lista, e o alcance
         - do descarte em profundidade era ambíguo na RN-013. O responsáv
         -el aceitou as 3 recomendações (pontos 2 a 4), que registram na 
         -spec o que o plano e o código já faziam. A rodada de confirmaçã
         -o apontou 4 problemas (2 bloqueantes): a seção 8 podia ser lida
         - como se todo erro de arquivo da RN-002 valesse para a ocorrênc
         -ia descartada; "JSON válido" não tinha definição (caractere de 
         -controle cru, `NaN`, `01.5`); "par correspondente" e BOM repeti
         -do sem resultado. O responsável aceitou as 4 recomendações (pon
         -tos 5 a 8). Sessão `docs/sessions/18-*`.                       
      15 +**Gatilho:** revisão independente da T-007 (`docs/reviews/T-007
         +.md`, revisões 1 e 2, "Decisões necessárias" 1). A seção 4 dizi
         +a que escape sem caractere válido "em qualquer chave ou valor" 
         +é erro de arquivo; a RN-013 dizia que as ocorrências descartada
         +s por chave repetida "nenhuma regra as considera". Para `"obs":
         + "\uD800", "obs": "ok"` as duas leituras davam resultados opost
         +os (erro de arquivo × despesa processada com aviso). O código d
         +a T-006 seguia a segunda sem decisão explícita: só verificava o
         +s valores que valeram. Decidido pelo responsável (ponto 1). A r
         +odada do `spec-adversary` sobre a primeira redação da 1.9 apont
         +ou 3 problemas (1 bloqueante): a codificação da entrada não est
         +ava na spec (só no DT-002 do plano), o parêntese `\uD800` a `\u
         +DFFF` podia ser lido como exemplo e não como lista, e o alcance
         + do descarte em profundidade era ambíguo na RN-013. O responsáv
         +el aceitou as 3 recomendações (pontos 2 a 4), que registram na 
         +spec o que o plano e o código já faziam. A rodada de confirmaçã
         +o apontou 4 problemas (2 bloqueantes): a seção 8 podia ser lida
         + como se todo erro de arquivo da RN-002 valesse para a ocorrênc
         +ia descartada; "JSON válido" não tinha definição (caractere de 
         +controle cru, `NaN`, `01.5`); "par correspondente" e BOM repeti
         +do sem resultado. O responsável aceitou as 4 recomendações (pon
         +tos 5 a 8). A confirmação final não apontou bloqueante; o único
         + achado (limites de profundidade e tamanho que a RFC 8259 deixa
         + à implementação) virou risco aceito (ponto 9), depois de o tes
         +te mostrar que a leitura quebrava com erro interno a partir de 
         +alguns milhares de níveis. Sessão `docs/sessions/18-*`.        
      16  
      17  **O que mudou na spec:**
      18  
     ...
      26  | 6 | Definição de "JSON válido" (**bloqueante** na confirmação
          ) | indefinida | RFC 8259 sem extensões: caractere de controle 
          cru em texto, `NaN`/`Infinity`, `01.5`, `.5`, `1.`, `+1` → erro
           de arquivo | seção 4 |
      27  | 7 | Par correspondente | indefinido | escape `\uD800`–`\uDBFF
          ` seguido imediatamente de `\uDC00`–`\uDFFF`; qualquer outra co
          mbinação é inválida | seção 4 |
      28  | 8 | BOM repetido no início | indefinido (código aceitava dois
          , por efeito de duas camadas de leitura) | só um BOM é ignorado
          ; o segundo torna o arquivo JSON inválido | seção 4 |
      29 +| 9 | Limites de aninhamento e tamanho (RFC 8259, seção 9) | in
         +definidos; o código quebrava com erro interno a partir de ~1.00
         +0 níveis | risco aceito: aninhamento muito profundo ou tamanho 
         +exagerado pode ser erro de arquivo; limite não fixado | seção 1
         +0 |                                                            
      30  
      30 -**Por quê:** escape sem par só aparece em arquivo corrompido ou
         - gerado com defeito; o lugar onde ele está (valor que valeu ou 
         -descartado, em qualquer profundidade) não muda isso. Recusar o 
         -arquivo mantém a regra da seção 4 sem exceção e evita processar
         - um arquivo suspeito. O ponto 2 aplica o mesmo motivo ao defeit
         -o gravado sem escape: byte fora do UTF-8 é recusado onde quer q
         -ue esteja; o BOM é aceito porque ferramentas comuns o gravam em
         - arquivos corretos. O ponto 3 fecha o conjunto: caracteres de c
         -ontrole e não caracteres existem no Unicode e podem ser gravado
         -s em UTF-8, então não são defeito. O ponto 5 preserva o motivo 
         -da AMB-019: a chave repetida existe para aceitar a correção fei
         -ta ao final do registro, e recusar o arquivo pelo conteúdo do v
         -alor corrigido anularia isso; só a forma do arquivo, que indica
         - defeito na geração, é verificada por inteiro. Os pontos 6 e 7 
         -adotam o padrão do formato, que qualquer ferramenta consegue co
         -nferir. O ponto 8 mantém a regra estrita: um BOM é prática comu
         -m de ferramentas, dois é defeito. Emoji válido (par completo ou
         - caractere direto) continua aceito em qualquer texto.          
      31 +**Por quê:** escape sem par só aparece em arquivo corrompido ou
         + gerado com defeito; o lugar onde ele está (valor que valeu ou 
         +descartado, em qualquer profundidade) não muda isso. Recusar o 
         +arquivo mantém a regra da seção 4 sem exceção e evita processar
         + um arquivo suspeito. O ponto 2 aplica o mesmo motivo ao defeit
         +o gravado sem escape: byte fora do UTF-8 é recusado onde quer q
         +ue esteja; o BOM é aceito porque ferramentas comuns o gravam em
         + arquivos corretos. O ponto 3 fecha o conjunto: caracteres de c
         +ontrole e não caracteres existem no Unicode e podem ser gravado
         +s em UTF-8, então não são defeito. O ponto 5 preserva o motivo 
         +da AMB-019: a chave repetida existe para aceitar a correção fei
         +ta ao final do registro, e recusar o arquivo pelo conteúdo do v
         +alor corrigido anularia isso; só a forma do arquivo, que indica
         + defeito na geração, é verificada por inteiro. Os pontos 6 e 7 
         +adotam o padrão do formato, que qualquer ferramenta consegue co
         +nferir. O ponto 8 mantém a regra estrita: um BOM é prática comu
         +m de ferramentas, dois é defeito. O ponto 9 não fixa número por
         +que nenhum limite tem origem na política; o que importa é que o
         + arquivo absurdo termine como erro de arquivo, sem saída e sem 
         +erro interno. Emoji válido (par completo ou caractere direto) c
         +ontinua aceito em qualquer texto.                              
      32  
      32 -**O que isso invalidou:** o código da T-006 (`_verificar_textos
         -` percorria só os valores que valeram); corrigido em commit `fi
         -x(T-006)`. Os pontos 2 a 4 não mudam código: o DT-002 já lia `u
         -tf-8-sig` estrito e verificava só U+D800 a U+DFFF, com testes n
         -a T-006 (`test_bom_e_aceito`, `test_rn002_utf8_invalido_e_erro_
         -de_arquivo`, inclusive substituto em bytes crus); o ponto 3 gan
         -ha `test_escape_fora_dos_substitutos_forma_caractere_valido`. O
         -s pontos 5 a 7 também refletem o comportamento já existente (po
         -ntos 6 e 7 ganham casos em `test_rn002_json_malformado_e_erro_d
         -e_arquivo` e `test_rn002_escape_sem_par_em_valor_e_erro_de_arqu
         -ivo`; o ponto 5 é coberto na T-008, que valida o cabeçalho sobr
         -e o valor que valeu). O ponto 8 muda código: o segundo BOM era 
         -aceito; corrigido no mesmo `fix(T-006)`, com `test_segundo_bom_
         -e_erro_de_arquivo`. DT-002 do `plan.md` alinhado na versão 1.2.
         - Nenhum valor do exemplo (seção 9) mudou; seção 7 não muda (con
         -tagem de 63 casos preservada).                                 
      33 +**O que isso invalidou:** o código da T-006 (`_verificar_textos
         +` percorria só os valores que valeram); corrigido em commit `fi
         +x(T-006)`. Os pontos 2 a 4 não mudam código: o DT-002 já lia `u
         +tf-8-sig` estrito e verificava só U+D800 a U+DFFF, com testes n
         +a T-006 (`test_bom_e_aceito`, `test_rn002_utf8_invalido_e_erro_
         +de_arquivo`, inclusive substituto em bytes crus); o ponto 3 gan
         +ha `test_escape_fora_dos_substitutos_forma_caractere_valido`. O
         +s pontos 5 a 7 também refletem o comportamento já existente (po
         +ntos 6 e 7 ganham casos em `test_rn002_json_malformado_e_erro_d
         +e_arquivo` e `test_rn002_escape_sem_par_em_valor_e_erro_de_arqu
         +ivo`; o ponto 5 é coberto na T-008, que valida o cabeçalho sobr
         +e o valor que valeu). O ponto 8 muda código: o segundo BOM era 
         +aceito; corrigido no mesmo `fix(T-006)`, com `test_segundo_bom_
         +e_erro_de_arquivo`. O ponto 9 também: o estouro de recursão da 
         +leitura vira `ErroDeArquivo`, com `test_aninhamento_exagerado_e
         +_erro_de_arquivo` (5.000 e 100.000 níveis). DT-002 do `plan.md`
         + alinhado na versão 1.2. Nenhum valor do exemplo (seção 9) mudo
         +u; seção 7 não muda (contagem de 63 casos preservada).         
      34  
      34 -**Tasks afetadas:** T-006 (aceite ganha os testes de ocorrência
         - descartada, escapes válidos, JSON inválido pela RFC 8259, par 
         -correspondente e segundo BOM); T-008 (aceite ganha `colaborador
         -` corrigido por chave repetida, ponto 5).                      
      35 +**Tasks afetadas:** T-006 (aceite ganha os testes de ocorrência
         + descartada, escapes válidos, JSON inválido pela RFC 8259, par 
         +correspondente, segundo BOM e aninhamento exagerado); T-008 (ac
         +eite ganha `colaborador` corrigido por chave repetida, ponto 5)
         +.                                                              
      36  
      37  **Custo:** 4 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`, `t
          asks.md`) + correção de uma função e um teste. Três rodadas do 
          `spec-adversary` (sobre a primeira redação da 1.9, confirmação 
          com 4 achados e confirmação final).
      38  
  ⎿  Updated specs/001-motor-reembolso/plan.md (+1 -1)
      121  ### DT-002 — Rejeitar o que não é JSON estrito
      122  
      123  **Contexto:** RN-002: arquivo que não é JSON válido é erro de 
           arquivo. O `json` da biblioteca padrão aceita `NaN`, `Infinity
           ` e `-Infinity`, que não são JSON.
      124 -**Decisão:** `simplejson` ≥ 4 já os rejeita na leitura por pad
          -rão (`allow_nan=False`); a versão mínima fica fixada no `pypro
          -ject.toml` e um teste garante que `"valor": NaN` é erro de arq
          -uivo, para a proteção não sumir numa troca de versão. Erro de 
          -parse → `ErroDeArquivo`. Bytes decodificados como UTF-8 estrit
          -o (`utf-8-sig`, aceitando um BOM, que a RFC 8259 permite ignor
          -ar); falha de decodificação → `ErroDeArquivo`. O `simplejson` 
          -também descarta um U+FEFF inicial por conta própria, o que far
          -ia dois BOMs passarem; por isso um U+FEFF que sobra depois do 
          -`utf-8-sig` → `ErroDeArquivo` (spec 1.9, D-006). Caractere de 
          -controle cru em texto e números fora da gramática (`01.5`, `.5
          -`, `1.`, `+1`) já são rejeitados pelo parser estrito (`strict=
          -True`, padrão). O parser aceita em silêncio um escape `\ud800`
          - sem par (vira um caractere substituto isolado na `str`, que a
          - gravação em UTF-8 recusaria depois); por isso, depois do pars
          -e, `entrada.py` percorre todas as chaves e textos — inclusive 
          -os das ocorrências descartadas por chave repetida, pelos pares
          - guardados no `ObjetoJson` (DT-010; spec 1.9, D-006) — e levan
          -ta `ErroDeArquivo` se algum contiver caractere entre U+D800 e 
          -U+DFFF (seção 4 da spec). Pares de escapes válidos já chegam c
          -ombinados num único caractere.                                
      124 +**Decisão:** `simplejson` ≥ 4 já os rejeita na leitura por pad
          +rão (`allow_nan=False`); a versão mínima fica fixada no `pypro
          +ject.toml` e um teste garante que `"valor": NaN` é erro de arq
          +uivo, para a proteção não sumir numa troca de versão. Erro de 
          +parse → `ErroDeArquivo`. Bytes decodificados como UTF-8 estrit
          +o (`utf-8-sig`, aceitando um BOM, que a RFC 8259 permite ignor
          +ar); falha de decodificação → `ErroDeArquivo`. O `simplejson` 
          +também descarta um U+FEFF inicial por conta própria, o que far
          +ia dois BOMs passarem; por isso um U+FEFF que sobra depois do 
          +`utf-8-sig` → `ErroDeArquivo` (spec 1.9, D-006). Caractere de 
          +controle cru em texto e números fora da gramática (`01.5`, `.5
          +`, `1.`, `+1`) já são rejeitados pelo parser estrito (`strict=
          +True`, padrão). O parser e o percurso de `entrada.py` são recu
          +rsivos: aninhamento além do limite de recursão do Python (~1.0
          +00 níveis) levanta `RecursionError`, convertido em `ErroDeArqu
          +ivo` (risco aceito na seção 10 da spec, D-006). O parser aceit
          +a em silêncio um escape `\ud800` sem par (vira um caractere su
          +bstituto isolado na `str`, que a gravação em UTF-8 recusaria d
          +epois); por isso, depois do parse, `entrada.py` percorre todas
          + as chaves e textos — inclusive os das ocorrências descartadas
          + por chave repetida, pelos pares guardados no `ObjetoJson` (DT
          +-010; spec 1.9, D-006) — e levanta `ErroDeArquivo` se algum co
          +ntiver caractere entre U+D800 e U+DFFF (seção 4 da spec). Pare
          +s de escapes válidos já chegam combinados num único caractere.
      125  **Alternativa descartada:** aceitar `NaN` e tratar como "valor
            não é número" na despesa: transformaria arquivo inválido em p
           rocessamento normal.
      126  **Consequência:** `"valor": NaN` encerra a execução sem saída,
            como qualquer JSON inválido.
      127  
  ⎿  Updated specs/001-motor-reembolso/spec.md (+1 -0)
      550  
      551  - **Fracionamento para escapar da nota fiscal** (AMB-008): trê
           s hospedagens sem nota de 100,00 + 99,99 + 50,01 na mesma data
            recebem 250,00, enquanto uma de 250,00 sem nota recebe 0. O g
           anho é limitado aos casos em que o limite diário passa de 100,
           00 (hospedagem e transporte em viagem). Aceito para não recusa
           r despesas pequenas legítimas sem nota.
      552  - **Viagem por hospedagem irrisória com nota declarada** (AMB-
           004): uma hospedagem de 0,01 com `tem_nota_fiscal` verdadeiro 
           põe D e D+1 em viagem e amplia os limites de alimentação e tra
           nsporte em até 70,00 por dia (140,00 nos dois dias). Aceito po
           rque o sistema não verifica notas (seção 3) e qualquer valor m
           ínimo seria regra inventada; a saída expõe `em_viagem` por ite
           m para a conferência humana. Mitigação definitiva: indicação e
           xplícita de viagem na entrada (evolução, seção 3).
      553 +- **Limites de aninhamento e de tamanho do arquivo** (seção 4,
          + RN-002): a RFC 8259 permite que a leitura limite a profundida
          +de de aninhamento e o tamanho do arquivo e dos textos. A spec 
          +não fixa esses limites: um arquivo com aninhamento muito profu
          +ndo (milhares de níveis) ou de tamanho exagerado pode ser recu
          +sado como erro de arquivo, sem saída, mesmo seguindo a gramáti
          +ca. Aceito porque nenhum arquivo real de despesas chega perto 
          +desses limites, e um número fixo seria regra sem origem na pol
          +ítica.                                                        
      554  - **Caminho ambíguo no aviso de chave repetida** (RN-013): cha
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
      555  - **Letra com traço próprio não vira letra base** (seção 5, pa
           sso 2): `ø`, `ł`, `đ` e semelhantes não têm decomposição canôn
           ica e ficam como estão, então `"Smørrebrød"` e `"Smorrebrod"` 
           são fornecedores diferentes na RN-007. Aceito porque são raras
            em dados em português e uma tabela própria de equivalências s
           eria incompleta por construção.
      556  - **Caractere invisível ou letra parecida de outro alfabeto** 
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
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+1 -1)
      65    - **Tipo:** estrutura (leitura de JSON)
      66    - **Atende:** RN-002 (arquivo que não é JSON válido; escape q
          ue não forma caractere válido), seção 4 da spec (número pelo va
          lor decimal exato; texto depois de decodificados os escapes), D
          T-001, DT-002
      67    - **Depende de:** T-001
      68 -  - **Aceite:** `tests/test_leitura_json.py` passa: `test_rn002
         -_nan_e_erro_de_arquivo` (`NaN`, `Infinity`, `-Infinity`); `test
         -_rn002_json_malformado_e_erro_de_arquivo`; `test_rn002_utf8_inv
         -alido_e_erro_de_arquivo`; `test_rn002_escape_sem_par_em_valor_e
         -_erro_de_arquivo` e `..._em_chave_...` (`\ud800`); `test_rn002_
         -escape_sem_par_em_ocorrencia_descartada_e_erro_de_arquivo` (`"o
         -bs": "\ud800", "obs": "ok"`, em valor e em objeto aninhado desc
         -artado; D-006); `test_escape_fora_dos_substitutos_forma_caracte
         -re_valido` (`\u0000`, `\uffff`, `\ufdd0` lidos como caractere, 
         -sem erro; D-006); `test_bom_e_aceito`; `test_segundo_bom_e_erro
         -_de_arquivo` (D-006); `test_rn002_json_malformado_e_erro_de_arq
         -uivo` inclui `01.5`, `.5`, `1.`, `+1` e tabulação, quebra de li
         -nha e U+0000 crus em texto; `test_rn002_escape_sem_par_em_valor
         -_e_erro_de_arquivo` inclui par invertido e alto solto antes de 
         -emoji (D-006); `test_numero_lido_pelo_valor_exato` (`33.333`, `
         -999999999.99999999999`, `1e999999`, `1e-999999` e inteiro de 5.
         -000 dígitos lidos como `Decimal` exato, sem erro); `test_escape
         -s_validos_decodificados` (`"2026-07-03"` → `2026-07-03`; emoji 
         -em par de escapes igual ao emoji direto).                      
      68 +  - **Aceite:** `tests/test_leitura_json.py` passa: `test_rn002
         +_nan_e_erro_de_arquivo` (`NaN`, `Infinity`, `-Infinity`); `test
         +_rn002_json_malformado_e_erro_de_arquivo`; `test_rn002_utf8_inv
         +alido_e_erro_de_arquivo`; `test_rn002_escape_sem_par_em_valor_e
         +_erro_de_arquivo` e `..._em_chave_...` (`\ud800`); `test_rn002_
         +escape_sem_par_em_ocorrencia_descartada_e_erro_de_arquivo` (`"o
         +bs": "\ud800", "obs": "ok"`, em valor e em objeto aninhado desc
         +artado; D-006); `test_escape_fora_dos_substitutos_forma_caracte
         +re_valido` (`\u0000`, `\uffff`, `\ufdd0` lidos como caractere, 
         +sem erro; D-006); `test_bom_e_aceito`; `test_segundo_bom_e_erro
         +_de_arquivo` (D-006); `test_aninhamento_exagerado_e_erro_de_arq
         +uivo` (5.000 e 100.000 níveis → `ErroDeArquivo`, não erro inter
         +no; D-006); `test_rn002_json_malformado_e_erro_de_arquivo` incl
         +ui `01.5`, `.5`, `1.`, `+1` e tabulação, quebra de linha e U+00
         +00 crus em texto; `test_rn002_escape_sem_par_em_valor_e_erro_de
         +_arquivo` inclui par invertido e alto solto antes de emoji (D-0
         +06); `test_numero_lido_pelo_valor_exato` (`33.333`, `999999999.
         +99999999999`, `1e999999`, `1e-999999` e inteiro de 5.000 dígito
         +s lidos como `Decimal` exato, sem erro); `test_escapes_validos_
         +decodificados` (`"2026-07-03"` → `2026-07-03`; emoji em par de 
         +escapes igual ao emoji direto).                                
      69    - **Commit:** e84693c
      70  
      71  - [x] **T-007** — Chaves repetidas: `ObjetoJson` via `object_pa
          irs_hook` (vale a última ocorrência) e percurso que gera os avi
          sos do topo e de cada elemento de `despesas`, com texto, caminh
          o, contagem e ordem da RN-013 (DT-010).

⏺ Uma conferência rápida no diff da spec e depois os commits:

  Ran 2 shell commands (ctrl+o to expand)

⏺ O aninhamento exagerado agora vira erro de arquivo, sem quebrar o programa, e
  os 4 commits estão feitos:

  - cdebcde docs(spec): v1.9 forma do arquivo de entrada e escape em ocorrência 
    descartada (D-006)
  - 9276b99 docs(plan): v1.2 alinha DT-002 à spec 1.9
  - 6226809 docs(tasks): v1.2 atualiza aceites de T-006 e T-008
  - afe14cc fix(T-006): forma do arquivo verificada também em ocorrências 
    descartadas, BOM único e aninhamento exagerado

  Antes do commit, o pre-commit rodou ruff e pytest com 182 testes passando. Não
  ficou nada pendente no repositório.

  Último ajuste:
  - Código: a leitura recusava com erro interno o arquivo com milhares de níveis
    de aninhamento; agora recusa como erro de arquivo. A leitura aceita até
    cerca de 990 níveis, e conferi que o percurso de avisos da T-007 funciona
    nessa profundidade máxima.
  - Teste: cobre 5.000 e 100.000 níveis. Ele falhou antes da correção e passa
    depois.
  - Spec e D-006: risco aceito novo na seção 10, sem fixar número, registrado
    como ponto 9 da D-006.

  📝 Fim do bloco: exporte a sessão antes de continuar. Sugiro:
  /export docs/sessions/18-spec-1.9-forma-do-arquivo.md
  e depois o commit docs(sessions): export da sessão 18 — spec 1.9 (D-006).

  A próxima task é a T-008 (validação do cabeçalho); só começo quando você
  pedir.
✻ Churned for 1m 35s · done 11:41 PM