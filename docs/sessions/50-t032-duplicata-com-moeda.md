 ▐▛███▛█   Claude Code v2.1.287
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~/repo/sdd-desafio

  Get to finished work sooner with Opus 5.5. Switch anytime with /model.

❯ /clear                                                                        

❯ pode fazer a proxima task                                                     

⏺ Skill(task)
  ⎿  Successfully loaded skill

  Searched for 1 pattern, ran 1 shell command (ctrl+o to expand)

⏺ The next task is T-032 (its dependency, T-031, is done). Reading the spec.

  Ran 6 shell commands (ctrl+o to expand)

⏺ Moving to T-032 — I've confirmed _separar_duplicatas isn't grouping by moeda
  yet, so I'll check the RN-011 status rule before writing tests.

  Searched for 1 pattern (ctrl+o to expand)

⏺ Writing the tests now.

⏺ Bash(cat >> tests/test_rn007_duplicatas.py <<'EOF'…)
  ⎿  E
     E         At index 1 diff: 'duplicata' != 'limite_diario_excedido'
     E         Use -v to get more diff
     … +7 lines (ctrl+o to expand)
  ⎿  Updated tests/test_rn007_duplicatas.py (+75 -0)
      236          "valor_reembolsado": Decimal("54.90"),
      237          "valor_glosado": Decimal("54.90"),
      238      }
      239 +                                                              
      240 +                                                              
      241 +# --- moeda (v4, AMB-028): câmbio do envelope, EUR 5,93 e USD 
          +5,44 em 14/07 ---                                             
      242 +                                                              
      243 +                                                              
      244 +def test_rn007_mesmo_valor_em_moedas_diferentes_nao_e_duplicat
          +a(avaliar, despesa):                                          
      245 +    """RN-007 / AMB-028: 22,00 EUR e 22,00 USD, demais campos 
          +iguais → moedas                                               
      246 +    diferentes, as duas avaliadas (chegam ao limite diário).""
          +"                                                             
      247 +    campos = dict(data="2026-07-14", valor=Decimal("22.00"))  
      248 +    saida = avaliar(                                          
      249 +        despesa(id="eur", moeda="EUR", **campos),             
      250 +        despesa(id="usd", moeda="USD", **campos),             
      251 +    )                                                         
      252 +    eur, usd = saida["itens"]                                 
      253 +                                                              
      254 +    # EUR: 22,00 × 5,93 = 130,46; min(130,46; 60,00) = 60,00 →
          + parcial                                                      
      255 +    assert (eur["valor_considerado"], eur["valor_reembolsado"]
          +, eur["status"]) == (                                         
      256 +        Decimal("130.46"), Decimal("60.00"), "parcial",       
      257 +    )                                                         
      258 +    # USD: 22,00 × 5,44 = 119,68; saldo do dia 60,00 − 60,00 =
          + 0 → recusado                                                 
      259 +    # pelo limite (etapa 9), não por duplicata                
      260 +    assert usd["valor_considerado"] == Decimal("119.68")      
      261 +    assert (usd["status"], usd["motivo"]) == ("recusado", "lim
          +ite_diario_excedido")                                         
      262 +    assert usd["limite_diario"] == Decimal("60.00")           
      263 +                                                              
      264 +                                                              
      265 +def test_rn007_valor_comparado_arredondado_na_moeda_da_despesa
          +(avaliar, despesa):                                           
      266 +    """RN-007 / RN-003 / AMB-028: 22.001 EUR e 22.00 EUR → 22,
          +00 EUR nos dois                                               
      267 +    (arredondado na moeda da despesa) → a segunda `duplicata`.
          +"""                                                           
      268 +    campos = dict(data="2026-07-14", moeda="EUR")             
      269 +    saida = avaliar(                                          
      270 +        despesa(id="a", valor=Decimal("22.001"), **campos),   
      271 +        despesa(id="b", valor=Decimal("22.00"), **campos),    
      272 +    )                                                         
      273 +    a, b = saida["itens"]                                     
      274 +                                                              
      275 +    # a: 22,001 × 5,93 = 130,46593 → 130,47; min(130,47; 60,00
          +) = 60,00                                                     
     … 38 more lines (ctrl+o to expand)

⏺ Only the EUR×USD test fails as expected, since the second item is wrongly
  marked duplicata; the other three already pass and stay in as regression
  guards. Next, I'll tackle the two section-7 edge cases and the traceability
  check.

  Ran 1 shell command (ctrl+o to expand)

⏺ Bash(python3 - <<'EOF'
      from pathlib import Path…)
  ⎿  tests/test_casos_de_borda.py:1149: AssertionError
     =========================== short test summary info ==================
     ==========
     … +3 lines (ctrl+o to expand)
  ⎿  Updated tests/test_casos_de_borda.py (+35 -0)
      1140  
      1141  _SO_13_07 = {"2026-07-13": {"USD": Decimal("5.42")}}
      1142  
      1143 +def _caso_duplicata_em_moedas_diferentes(saida):             
      1144 +    # RN-007 / AMB-028: moedas diferentes → as duas chegam ao
           + limite (etapa 9):                                           
      1145 +    # 22,00 × 5,93 = 130,46 → min(130,46; 60,00) = 60,00, par
           +cial;                                                        
      1146 +    # 22,00 × 5,44 = 119,68 → saldo 0, recusado pelo limite  
      1147 +    eur, usd = saida["itens"]                                
      1148 +    assert (eur["status"], eur["valor_reembolsado"]) == ("par
           +cial", Decimal("60.00"))                                     
      1149 +    assert (usd["status"], usd["motivo"]) == ("recusado", "li
           +mite_diario_excedido")                                       
      1150 +                                                             
      1151 +                                                             
      1152 +def _caso_duplicata_em_moeda_estrangeira(saida):             
      1153 +    # RN-007: 22.001 e 22.00 EUR → 22,00 EUR arredondado na m
           +oeda da despesa →                                            
      1154 +    # a segunda `duplicata`; a primeira 22,001 × 5,93 = 130,4
           +6593 → 130,47,                                               
      1155 +    # min(130,47; 60,00) = 60,00 → parcial                   
      1156 +    a, b = saida["itens"]                                    
      1157 +    assert (a["status"], a["valor_reembolsado"]) == ("parcial
           +", Decimal("60.00"))                                         
      1158 +    assert (b["status"], b["motivo"]) == ("recusado", "duplic
           +ata")                                                        
      1159 +    assert (b["em_viagem"], b["limite_diario"]) == (None, Non
           +e)                                                           
      1160 +                                                             
      1161 +                                                             
      1162  CASOS_DE_CAMBIO = [
      1163      # (texto da entrada, documento do câmbio ou None para o d
            o envelope, verificação)
      1164      pytest.param(
     ...
      1236          }),
      1237          _caso_data_intermediaria_sem_a_moeda, id="Data interm
            ediária sem a moeda",
      1238      ),
      1239 +    pytest.param(                                            
      1240 +        _json(despesa(id="eur", data="2026-07-14", valor=Deci
           +mal("22.00"),                                                
      1241 +                      moeda="EUR"),                          
      1242 +              despesa(id="usd", data="2026-07-14", valor=Deci
           +mal("22.00"),                                                
      1243 +                      moeda="USD")),                         
      1244 +        None, _caso_duplicata_em_moedas_diferentes,          
      1245 +        id="Duplicata em moedas diferentes",                 
      1246 +    ),                                                       
      1247 +    pytest.param(                                            
      1248 +        _json(despesa(id="a", data="2026-07-14", valor=Decima
           +l("22.001"),                                                 
      1249 +                      moeda="EUR"),                          
      1250 +              despesa(id="b", data="2026-07-14", valor=Decima
           +l("22.00"),                                                  
     … 7 more lines (ctrl+o to expand)
  ⎿  Updated tests/test_rastreabilidade.py (+1 -4)
      17  SPEC = TESTES.parent / "specs" / "001-motor-reembolso" / "spec.
          md"
      18  TASKS = SPEC.with_name("tasks.md")
      19  
      20 -PENDENTES = {  # some quando a Fase 5 terminar (DT-016)        
      21 -    "Duplicata em moedas diferentes": "T-032",                 
      22 -    "Duplicata em moeda estrangeira": "T-032",                 
      23 -}                                                              
      20 +PENDENTES: dict[str, str] = {}  # some na T-034 (DT-016)       
      21  PRIMEIRA_TASK_DA_FASE_5, ULTIMA_TASK_DA_FASE_5 = 22, 34
      22  
      23  

⏺ Same expected failure. Now the implementation: adding moeda to the grouping
  key.

⏺ Bash(sed -i '' 's/^PENDENTES: dict\[str, str\] = {}  # some na T-034
      (DT-016)$/PENDENTES: dict[str, str] = {}  # some quando a Fase 5 terminar
      (DT-016)/' tests/test_…)
  ⎿  ...................................
        [100%]
     971 passed in 0.72s
     … +5 lines (ctrl+o to expand)
  ⎿  Updated src/reembolso/motor.py (+6 -4)
      163  def _separar_duplicatas(
      164      despesas: list[Despesa],
      165  ) -> tuple[list[Despesa], list[Despesa]]:
      166 -    """Etapa 7 (RN-007, AMB-010): agrupa por (data, categoria,
          - fornecedor,                                                  
      167 -    `valor_considerado`); a original é a primeira com nota fis
          -cal, ou a primeira                                            
      168 -    na ordem da entrada. Devolve (originais, duplicatas)."""  
      169 -    grupos: dict[tuple[date, str, str, Decimal], list[Despesa]
          -] = {}                                                        
      166 +    """Etapa 7 (RN-007, AMB-010, AMB-028): agrupa por (data, c
          +ategoria,                                                     
      167 +    fornecedor, moeda, `valor` arredondado na moeda da despesa
          +); a original é a                                             
      168 +    primeira com nota fiscal, ou a primeira na ordem da entrad
          +a. Devolve                                                    
      169 +    (originais, duplicatas)."""                               
      170 +    grupos: dict[tuple[date, str, str, str, Decimal], list[Des
          +pesa]] = {}                                                   
      171      for despesa in sorted(despesas, key=lambda d: d.posicao):
      172          chave = (
      173              despesa.data,
      174              despesa.categoria,
      175              despesa.fornecedor,
      176 +            despesa.moeda,                                    
      177              arredondar(despesa.valor_informado),
      178          )
      179          grupos.setdefault(chave, []).append(despesa)
  ⎿  Updated tests/test_rastreabilidade.py (+1 -1)
      17  SPEC = TESTES.parent / "specs" / "001-motor-reembolso" / "spec.
          md"
      18  TASKS = SPEC.with_name("tasks.md")
      19  
      20 -PENDENTES: dict[str, str] = {}  # some na T-034 (DT-016)       
      20 +PENDENTES: dict[str, str] = {}  # some quando a Fase 5 terminar
         + (DT-016)                                                      
      21  PRIMEIRA_TASK_DA_FASE_5, ULTIMA_TASK_DA_FASE_5 = 22, 34
      22  
      23  

⏺ Tests and lint pass: 971 passed, ruff clean. This is a business-rule task, so
  next is the independent review.

⏺ revisor-de-task(Revisão independente T-032)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ T-032 is implemented: 971 tests pass and ruff is clean. I'm now waiting on the
  independent revisor-de-task review before I can write the summary for your
  approval.

✻ Crunched for 1m 24s · done 3:45 PM

› Message from revisor-de-task
  # Revisão T-032 — Duplicata com moeda: etapa 7 agrupa por (data, categoria,
  fornecedor, moeda, `valor` arredondado na moeda da despesa)

  - **Data:** 2026-10-04
  - **Regras conferidas:** RN-007, RN-003 (exceção da duplicata), RN-015 (moeda
  ausente vale BRL), AMB-010, AMB-028, seção 7 ("Duplicata em moedas
  diferentes", "Duplicata em moeda estrangeira"), seção 8 (etapa 7), seção 10
  (risco do mesmo gasto lançado em moedas diferentes)
  - **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 971 passed, 0
  failed (evidência, não veredito)

  ### Resultado
  **APROVADO** — todos os critérios de aceite foram atendidos. A chave da etapa
  7 segue a RN-007 como está escrita e cada valor esperado confere com a conta
  feita à mão.

  ### Critérios de aceite
  | # | Critério | Status | Evidência |
  |---|---|---|---|
  | 1 | 22,00 EUR e 22,00 USD, demais campos iguais → as duas avaliadas |
  atendido | `tests/test_rn007_duplicatas.py::test_rn007_mesmo_valor_em_moedas_d
  iferentes_nao_e_duplicata`. Conta: EUR 22,00 × 5,93 = 130,46, min(130,46;
  60,00) = 60,00, `parcial`; USD 22,00 × 5,44 = 119,68, saldo 0,
  `recusado`/`limite_diario_excedido` (RN-009, spec linha 236), e não
  `duplicata`. Com a chave anterior, sem a moeda, o teste falharia. |
  | 2 | 22.001 EUR e 22.00 EUR → a segunda `duplicata` | atendido |
  `test_rn007_valor_comparado_arredondado_na_moeda_da_despesa`. Conta: 22,001 →
  22,00 EUR nas duas; a primeira dá 22,001 × 5,93 = 130,46593 → 130,47, limitado
  a 60,00 (`parcial`); a segunda é `duplicata` com `valor_considerado` 130,46.
  |
  | 3 | 10,00 EUR e 59,30 BRL do mesmo gasto → as duas avaliadas | atendido |
  `test_rn007_mesmo_gasto_em_eur_e_brl_nao_e_duplicata`. Conta: EUR 10,00 × 5,93
  = 59,30, `aprovado`; BRL 59,30 com saldo 0,70 → `parcial` 0,70. Uma
  implementação que comparasse o valor em reais falharia neste teste. |
  | 4 | Moeda ausente e `"BRL"`, demais campos iguais → a segunda `duplicata` |
  atendido | `test_rn007_moeda_ausente_e_brl_sao_a_mesma`, testado nas duas
  ordens. Na entrada, `moeda` ausente ou nula já vira `MOEDA_BASE`
  (`src/reembolso/entrada.py:139-141`). |
  | 5 | Os testes da 1.x da RN-007 continuam passando | atendido | Os testes
  anteriores de `tests/test_rn007_duplicatas.py` não mudaram e a suíte passa
  inteira. |
  | 6 | Casos de borda da seção 7 ("Duplicata em moedas diferentes" e "Duplicata
  em moeda estrangeira") | atendido | `tests/test_casos_de_borda.py`: os dois
  `pytest.param` têm o nome do caso como `id` e usam alimentação, com nota,
  mesmo fornecedor, em 14/07, como pede a spec (linhas 691-692). As duas
  entradas saíram de `PENDENTES` em `tests/test_rastreabilidade.py`. |

  ### Problemas encontrados
  Nenhum problema encontrado.

  Observações que não pedem correção:
  - **Chave da etapa 7:** `src/reembolso/motor.py:171-178` passou a usar (data,
  categoria normalizada, fornecedor normalizado, moeda,
  `arredondar(valor_informado)`). Isso corresponde à RN-007 (spec linha 211) e à
  exceção da RN-003 (spec linha 187).
  - **Moeda comparada como veio:** a moeda entra na chave sem normalização, o
  que está de acordo com a AMB-025. Um código fora do formato, como `"brl"`, já
  é recusado na etapa 1 e não chega à etapa 7.
  - **Testes que passariam com o código antigo:** os critérios 3 e 4 também
  passariam com a chave anterior. Mesmo assim, servem como guarda contra duas
  implementações erradas plausíveis: comparar em reais e comparar a moeda crua
  (`None` ≠ `"BRL"`).
  - **`PENDENTES` vazio:** o dicionário em `tests/test_rastreabilidade.py` ficou
  vazio. Apagá-lo é tarefa da T-034, então isso está dentro do escopo.

  ### Cobertura
  - **Regras testadas:**
    - RN-007 e AMB-028: os quatro testes novos em `test_rn007_duplicatas.py` e
  os dois casos novos em `test_casos_de_borda.py`.
    - RN-003 (valor da duplicata arredondado na moeda da despesa):
  `test_rn007_valor_comparado_arredondado_na_moeda_da_despesa`.
    - RN-015 (moeda ausente vale BRL):
  `test_rn007_moeda_ausente_e_brl_sao_a_mesma`.
  - **Casos de borda cobertos:**
    - Duplicata em moedas diferentes.
    - Duplicata em moeda estrangeira (arredondamento antes de comparar).
    - Mesmo gasto lançado em EUR e em BRL (risco da seção 10).
    - Moeda ausente e `"BRL"`, nas duas ordens.
  - **Casos que parecem faltar:** nenhum exigido pela task nem pela spec.

  ### Decisões necessárias
  Nenhuma.

  ### Antes de concluir a task
  Nada — pode seguir para o commit.

  Arquivos revisados:
  - /Users/rafaeltxm/repo/sdd-desafio/src/reembolso/motor.py
  - /Users/rafaeltxm/repo/sdd-desafio/tests/test_rn007_duplicatas.py
  - /Users/rafaeltxm/repo/sdd-desafio/tests/test_casos_de_borda.py
  - /Users/rafaeltxm/repo/sdd-desafio/tests/test_rastreabilidade.py

⏺ Saving the report unedited.

⏺ Bash(ls docs/reviews/T-032.md 2>/dev/null; cat > docs/reviews/T-032.md <<'EOF'
      # Revisão T-032 — Duplicata com moeda: etapa 7 agrupa por (data,
      categoria, fornecedor…)
  ⎿  Created docs/reviews/T-032.md (+51 -0)
       1 +# Revisão T-032 — Duplicata com moeda: etapa 7 agrupa por (data
         +, categoria, fornecedor, moeda, `valor` arredondado na moeda da
         + despesa)                                                      
       2 +                                                               
       3 +- **Data:** 2026-10-04                                         
       4 +- **Regras conferidas:** RN-007, RN-003 (exceção da duplicata),
         + RN-015 (moeda ausente vale BRL), AMB-010, AMB-028, seção 7 ("D
         +uplicata em moedas diferentes", "Duplicata em moeda estrangeira
         +"), seção 8 (etapa 7), seção 10 (risco do mesmo gasto lançado e
         +m moedas diferentes)                                           
       5 +- **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 
         +971 passed, 0 failed (evidência, não veredito)                 
       6 +                                                               
       7 +### Resultado                                                  
       8 +**APROVADO** — todos os critérios de aceite foram atendidos. A 
         +chave da etapa 7 segue a RN-007 como está escrita e cada valor 
         +esperado confere com a conta feita à mão.                      
       9 +                                                               
      10 +### Critérios de aceite                                        
      11 +| # | Critério | Status | Evidência |                          
      12 +|---|---|---|---|                                              
      13 +| 1 | 22,00 EUR e 22,00 USD, demais campos iguais → as duas ava
         +liadas | atendido | `tests/test_rn007_duplicatas.py::test_rn007
         +_mesmo_valor_em_moedas_diferentes_nao_e_duplicata`. Conta: EUR 
         +22,00 × 5,93 = 130,46, min(130,46; 60,00) = 60,00, `parcial`; U
         +SD 22,00 × 5,44 = 119,68, saldo 0, `recusado`/`limite_diario_ex
         +cedido` (RN-009, spec linha 236), e não `duplicata`. Com a chav
         +e anterior, sem a moeda, o teste falharia. |                   
      14 +| 2 | 22.001 EUR e 22.00 EUR → a segunda `duplicata` | atendido
         + | `test_rn007_valor_comparado_arredondado_na_moeda_da_despesa`
         +. Conta: 22,001 → 22,00 EUR nas duas; a primeira dá 22,001 × 5,
         +93 = 130,46593 → 130,47, limitado a 60,00 (`parcial`); a segund
         +a é `duplicata` com `valor_considerado` 130,46. |              
      15 +| 3 | 10,00 EUR e 59,30 BRL do mesmo gasto → as duas avaliadas 
         +| atendido | `test_rn007_mesmo_gasto_em_eur_e_brl_nao_e_duplica
         +ta`. Conta: EUR 10,00 × 5,93 = 59,30, `aprovado`; BRL 59,30 com
         + saldo 0,70 → `parcial` 0,70. Uma implementação que comparasse 
         +o valor em reais falharia neste teste. |                       
      16 +| 4 | Moeda ausente e `"BRL"`, demais campos iguais → a segunda
         + `duplicata` | atendido | `test_rn007_moeda_ausente_e_brl_sao_a
         +_mesma`, testado nas duas ordens. Na entrada, `moeda` ausente o
         +u nula já vira `MOEDA_BASE` (`src/reembolso/entrada.py:139-141`
         +). |                                                           
      17 +| 5 | Os testes da 1.x da RN-007 continuam passando | atendido 
         +| Os testes anteriores de `tests/test_rn007_duplicatas.py` não 
         +mudaram e a suíte passa inteira. |                             
      18 +| 6 | Casos de borda da seção 7 ("Duplicata em moedas diferente
         +s" e "Duplicata em moeda estrangeira") | atendido | `tests/test
         +_casos_de_borda.py`: os dois `pytest.param` têm o nome do caso 
         +como `id` e usam alimentação, com nota, mesmo fornecedor, em 14
         +/07, como pede a spec (linhas 691-692). As duas entradas saíram
         + de `PENDENTES` em `tests/test_rastreabilidade.py`. |          
      19 +                                                               
      20 +### Problemas encontrados                                      
      21 +Nenhum problema encontrado.                                    
      22 +                                                               
      23 +Observações que não pedem correção:                            
      24 +- **Chave da etapa 7:** `src/reembolso/motor.py:171-178` passou
         + a usar (data, categoria normalizada, fornecedor normalizado, m
         +oeda, `arredondar(valor_informado)`). Isso corresponde à RN-007
         + (spec linha 211) e à exceção da RN-003 (spec linha 187).      
      25 +- **Moeda comparada como veio:** a moeda entra na chave sem nor
         +malização, o que está de acordo com a AMB-025. Um código fora d
         +o formato, como `"brl"`, já é recusado na etapa 1 e não chega à
         + etapa 7.                                                      
      26 +- **Testes que passariam com o código antigo:** os critérios 3 
         +e 4 também passariam com a chave anterior. Mesmo assim, servem 
         +como guarda contra duas implementações erradas plausíveis: comp
         +arar em reais e comparar a moeda crua (`None` ≠ `"BRL"`).      
      27 +- **`PENDENTES` vazio:** o dicionário em `tests/test_rastreabil
         +idade.py` ficou vazio. Apagá-lo é tarefa da T-034, então isso e
         +stá dentro do escopo.                                          
      28 +                                                               
      29 +### Cobertura                                                  
      30 +- **Regras testadas:**                                         
      31 +  - RN-007 e AMB-028: os quatro testes novos em `test_rn007_dup
         +licatas.py` e os dois casos novos em `test_casos_de_borda.py`. 
      32 +  - RN-003 (valor da duplicata arredondado na moeda da despesa)
         +: `test_rn007_valor_comparado_arredondado_na_moeda_da_despesa`.
      33 +  - RN-015 (moeda ausente vale BRL): `test_rn007_moeda_ausente_
         +e_brl_sao_a_mesma`.                                            
      34 +- **Casos de borda cobertos:**                                 
      35 +  - Duplicata em moedas diferentes.                            
      36 +  - Duplicata em moeda estrangeira (arredondamento antes de com
         +parar).                                                        
      37 +  - Mesmo gasto lançado em EUR e em BRL (risco da seção 10).   
      38 +  - Moeda ausente e `"BRL"`, nas duas ordens.                  
      39 +- **Casos que parecem faltar:** nenhum exigido pela task nem pe
         +la spec.                                                       
      40 +                                                               
     … 11 more lines (ctrl+o to expand)

⏺ Agent "Revisão independente T-032" finished · 48s

⏺ Resumo — T-032: Duplicata com moeda

  A etapa 7 agora só trata duas despesas como duplicatas quando têm a mesma
  moeda. O revisor independente deu APROVADO; o commit aguarda sua autorização.

  Arquivos alterados:
  - src/reembolso/motor.py (modificado): a chave de agrupamento de
    _separar_duplicatas passou a incluir moeda.
  - tests/test_rn007_duplicatas.py (modificado): 4 testes novos.
  - tests/test_casos_de_borda.py (modificado): 2 casos novos em CASOS_DE_CAMBIO.
  - tests/test_rastreabilidade.py (modificado): PENDENTES ficou vazio. Apagar o
    dicionário fica para a T-034.
  - docs/reviews/T-032.md (novo): parecer do revisor, salvo sem edição.

  Testes criados/alterados:
  - test_rn007_mesmo_valor_em_moedas_diferentes_nao_e_duplicata → RN-007 /
    AMB-028
  - test_rn007_valor_comparado_arredondado_na_moeda_da_despesa → RN-007 / RN-003
    / AMB-028
  - test_rn007_mesmo_gasto_em_eur_e_brl_nao_e_duplicata → RN-007 / AMB-028 /
    seção 10
  - test_rn007_moeda_ausente_e_brl_sao_a_mesma (testado nas duas ordens) →
    RN-007 / RN-015
  - Casos de borda "Duplicata em moedas diferentes" e "Duplicata em moeda
    estrangeira" → seção 7

  Testes executados antes da implementação:
  - Só os dois testes de EUR × USD falharam, e pelo motivo certo: o código
    antigo marcava a segunda despesa como duplicata.
  - Os outros três (22.001 × 22.00 EUR, EUR × BRL, ausente × "BRL") já passavam,
    porque o comportamento antigo coincide com a spec nesses casos. Ficam como
    proteção contra dois erros plausíveis: comparar em reais e comparar a moeda
    crua (None ≠ "BRL").

  Testes executados depois: uv run pytest -q e uv run ruff check .

  pytest: 971 passed, 0 failed

  ruff: limpo

  Revisão independente: APROVADO, sem problemas e sem decisões necessárias
  (docs/reviews/T-032.md).

  Decisões ou interpretações realizadas: nenhuma.

  Lacunas ou dúvidas: nenhuma.

  Commit proposto: feat(T-032): duplicata agrupa também pela moeda (AMB-028)

  Posso commitar? Depois do commit vou pedir o /export da sessão para fechar o
  bloco com docs(tasks): conclui T-032.

✻ Sautéed for 2m 37s · done 3:46 PM

❯ pode commitar                                                                 

  Ran 1 shell command (ctrl+o to expand)

⏺ Bash(python3 - <<'EOF'
      from pathlib import Path…)
  ⎿   specs/001-motor-reembolso/tasks.md | 4 ++--
      1 file changed, 2 insertions(+), 2 deletions(-)
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+2 -2)
      363    - **Casos de borda:** Moeda nula · Moeda estrangeira com cot
           ação · Moeda estrangeira em sábado · Cotação exatamente 3 dias
            antes · Cotação 4 dias antes · Moeda sem cotação no arquivo ·
            Sem cotação e fora do período · Conversão arredondada uma vez
            · Nota fiscal comparada em reais · Valor estrangeiro minúscul
           o · Teto na moeda original · Moeda estrangeira não comprova vi
           agem · Hospedagem em moeda estrangeira · Data intermediária se
           m a moeda
      364    - **Commit:** a56b1cd
      365  
      366 -- [ ] **T-032** — Duplicata com moeda: etapa 7 agrupa por (dat
          -a, categoria, fornecedor, moeda, `valor` arredondado na moeda 
          -da despesa).                                                  
      366 +- [x] **T-032** — Duplicata com moeda: etapa 7 agrupa por (dat
          +a, categoria, fornecedor, moeda, `valor` arredondado na moeda 
          +da despesa).                                                  
      367    - **Tipo:** regra
      368    - **Atende:** RN-007, AMB-028
      369    - **Substitui:** T-017 (duplicata com moeda)
     ...
      375      - ausente e `"BRL"` com os demais campos iguais → a segund
           a `duplicata`, porque as duas valem `BRL`.
      376      Os testes da 1.x da RN-007 continuam passando.
      377    - **Casos de borda:** Duplicata em moedas diferentes · Dupli
           cata em moeda estrangeira
      378 -  - **Commit:** —                                             
      378 +  - **Commit:** cfe843d                                       
      379  
      380  - [ ] **T-033** — Aceite com os arquivos do envelope: `exemplo
           s/envelope/despesas-envelope.json` e `despesas-envelope-cc-des
           conhecido.json` pela CLI, com `politica-v4.json` e `cambio.jso
           n`, contra a segunda e a terceira tabelas da seção 9 da spec, 
           **transcritas à mão** no teste.
      381    - **Tipo:** regra

⏺ I committed T-032 as cfe843d; the pre-commit hook passed (ruff clean, 971
  tests passing). I also marked T-032 as [x] in tasks.md and filled in that
  hash.

  To close the block I need the session export before the docs(tasks): conclui 
  T-032 commit. Please run:

  /export docs/sessions/50-t032-duplicata-com-moeda.md

  Let me know when it's done and I'll commit tasks.md and the export together.

✻ Brewed for 10s · done 3:47 PM