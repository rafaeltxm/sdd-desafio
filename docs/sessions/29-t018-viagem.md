 ▐▛███▛█   Claude Code v2.1.287
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~/repo/sdd-desafio

  Opus 5.5 is now your default model and it draws down usage faster than Sonnet 5. Switch anytime with /model.

❯ /clear                                                                        

❯ /task T-018                                                                   

  Searched for 1 pattern, read 1 file, listed 1 directory, ran 1 shell command (ctrl+o to expand)

⏺ Now the code.

  Searched for 2 patterns, ran 4 shell commands (ctrl+o to expand)

⏺ Lidas a task, a spec (RN-010, RN-012, AMB-004/005/006, seção 8) e o código
  atual. Agora escrevo os testes de T-018 antes da implementação.

⏺ Write(tests/test_rn010_viagem.py)
  ⎿  Wrote 309 lines to tests/test_rn010_viagem.py
      1 """Colaborador em viagem: RN-010 / AMB-004 / AMB-006 / AMB-016 (e
        tapa 8 da seção 8).
      2 
      3 Período padrão do `conftest`: 2026-07-01 a 2026-07-31.
      4 """
      5 
      6 from decimal import Decimal
      7 
      8 import pytest
      9 
     … +388 lines (ctrl+o to expand)

⏺ Limpo dois testes que ficaram confusos.

⏺ Update(tests/test_rn010_viagem.py)
  ⎿  Added 1 line, removed 14 lines
      216  ):
      217      """RN-010 / AMB-016: a terceira hospedagem do dia, com not
           a, recebe 0 no limite
      218      (etapa 9), mas passou pelas etapas 1 a 7 → comprova viagem
            (D+1 em viagem)."""
      219 -    h1, h2, h3, alimentacao = avaliar(                        
      220 -        despesa(**_hospedagem(id="h1", data="2026-07-13", forn
          -ecedor="Hotel A",                                             
      221 -                              valor=Decimal("200.00"))),      
      222 -        despesa(**_hospedagem(id="h2", data="2026-07-13", forn
          -ecedor="Hotel B",                                             
      223 -                              valor=Decimal("50.00"))),       
      224 -        despesa(**_hospedagem(id="h3", data="2026-07-14", forn
          -ecedor="Hotel C",                                             
      225 -                              valor=Decimal("40.00"))),       
      226 -        despesa(id="a", data="2026-07-15", valor=Decimal("80.0
          -0")),                                                         
      227 -    )["itens"]                                                
      228 -    # h1 e h2 esgotam 250,00 em 13/07; h3 em 14/07 tem o própr
          -io limite → reescrito                                         
      229 -    # abaixo com as três na mesma data                        
      230 -    del h1, h2, h3, alimentacao                               
      231 -                                                              
      232 -    h1, h2, h3, alimentacao = avaliar(                        
      219 +    _, _, h3, alimentacao = avaliar(                          
      220          despesa(**_hospedagem(id="h1", data="2026-07-14", forn
           ecedor="Hotel A",
      221                                valor=Decimal("200.00"))),
      222          despesa(**_hospedagem(id="h2", data="2026-07-14", forn
           ecedor="Hotel B",

⏺ Update(tests/test_rn010_viagem.py)
  ⎿  Added 3 lines, removed 4 lines
      150      assert _resumo(alimentacao) == (Decimal("80.00"), "aprovad
           o", None)
      151  
      152  
      153 -def test_rn010_duplicata_com_nota_de_original_sem_nota_nao_com
          -prova_viagem(                                                 
      153 +def test_rn010_duplicatas_de_hospedagem_sem_nota_nao_comprovam
          +_viagem(                                                      
      154      avaliar, despesa
      155  ):
      156 -    """RN-010 / RN-007 / AMB-016: grupo em que nenhuma tem not
          -a... não se aplica;                                           
      157 -    aqui duas cópias sem nota ≤ 100,00: a original segue, mas 
          -sem nota não comprova                                         
      158 -    viagem, e a `duplicata` não comprova viagem."""           
      156 +    """RN-010 / RN-007: duas cópias de hospedagem de 90,00 sem
          + nota → a original                                            
      157 +    segue, mas sem nota não comprova viagem; a outra é `duplic
          +ata`."""                                                      
      158      original, copia, alimentacao = avaliar(
      159          despesa(**_hospedagem(id="h1", data="2026-07-14", valo
           r=Decimal("90.00"),
      160                                tem_nota_fiscal=False)),

⏺ Update(tests/test_rn010_viagem.py)
  ⎿  Added 1 line, removed 1 line
      194      assert _resumo(itens["a"]) == (Decimal("80.00"), "aprovado
           ", None)
      195  
      196  
      197 -def test_rn010_hospedagem_com_nota_acima_de_100_sem_nota_nao_c
          -omprova_viagem(                                               
      197 +def test_rn010_hospedagem_acima_de_100_sem_nota_nao_comprova_v
          +iagem(                                                        
      198      avaliar, despesa
      199  ):
      200      """RN-010 / RN-008: hospedagem de 690,00 sem nota → `nota_
           fiscal_ausente`; a

⏺ Now RN-012's viagem part and the edge cases.

⏺ Bash(python3 - <<'EOF'
      p='tests/test_rn012_hospedagem_uma_diaria.py'…)
  ⎿  386:        id="Duas hospedagens na mesma data",
     416:        id="Campo extra",
         # min(60,01; 60,00) = 60,00 → parcial
     … +24 lines (ctrl+o to expand)
  ⎿  Updated tests/test_rn012_hospedagem_uma_diaria.py (+17 -4)
      1 -"""Hospedagem: um lançamento é uma diária — RN-012, AMB-005.    
      2 -                                                                
      3 -A parte de viagem da RN-012 (14/07 e 15/07 em viagem) é da T-018
        -.                                                               
      4 -"""                                                             
      1 +"""Hospedagem: um lançamento é uma diária — RN-012, AMB-005.""" 
      2  
      3  from decimal import Decimal
      4  
     ...
      45      assert segunda["valor_reembolsado"] == Decimal("50.00")
      46      assert segunda["status"] == "parcial"
      47      assert segunda["motivo"] == "limite_diario_excedido"
      48 +                                                               
      49 +                                                               
      50 +def test_rn012_hospedagem_de_480_poe_em_viagem_so_d_e_d_mais_1(
         +avaliar, despesa):                                             
      51 +    """RN-012 / RN-010 / AMB-005 (aceite): 480,00 com nota em 1
         +4/07, "2 diarias" →                                            
      52 +    uma diária: 14/07 e 15/07 em viagem, 16/07 não."""         
      53 +    hospedagem, a15, a16 = avaliar(                            
      54 +        despesa(id="h", categoria="hospedagem", data="2026-07-1
         +4",                                                            
      55 +                valor=Decimal("480.00"), descricao="2 diarias",
         + tem_nota_fiscal=True),                                        
      56 +        despesa(id="a15", data="2026-07-15", valor=Decimal("10.
         +00")),                                                         
      57 +        despesa(id="a16", data="2026-07-16", valor=Decimal("10.
         +00")),                                                         
      58 +    )["itens"]                                                 
      59 +                                                               
      60 +    # uma diária em D = 14/07 → {14/07, 15/07}; a descrição não
         + estende a 16/07                                               
      61 +    assert hospedagem["em_viagem"] is True                     
      62 +    assert a15["em_viagem"] is True                            
      63 +    assert a16["em_viagem"] is False                           

⏺ Adding the 9 viagem edge cases to test_casos_de_borda.py.

⏺ Bash(python3 - <<'EOF'
      p='tests/test_casos_de_borda.py'…)
  ⎿      def test_caso_de_borda(processar, texto, verificar):
             """Seção 7 da spec: comportamento esperado de cada caso."""
     >       verificar(processar(texto))
     … +37 lines (ctrl+o to expand)
  ⎿  Updated tests/test_casos_de_borda.py (+174 -0)
      248      assert (item["em_viagem"], item["limite_diario"]) == (None
           , None)
      249  
      250  
      251 +def _hospedagem(**campos):                                    
      252 +    padrao = dict(id="h", categoria="hospedagem", fornecedor="
          +Hotel",                                                       
      253 +                  valor=Decimal("200.00"), tem_nota_fiscal=Tru
          +e)                                                            
      254 +    padrao.update(campos)                                     
      255 +    return despesa(**padrao)                                  
      256 +                                                              
      257 +                                                              
      258 +def _em_viagem(item, limite):                                 
      259 +    assert (item["em_viagem"], item["limite_diario"]) == (True
          +, limite)                                                     
      260 +                                                              
      261 +                                                              
      262 +def _caso_limite_de_nota_em_viagem(saida):                    
      263 +    # RN-008: 110,00 > 100,00 sem nota, mesmo em viagem → recu
          +sado antes do limite                                          
      264 +    _, transporte = saida["itens"]                            
      265 +    assert (transporte["status"], transporte["motivo"]) == (  
      266 +        "recusado", "nota_fiscal_ausente",                    
      267 +    )                                                         
      268 +    assert (transporte["em_viagem"], transporte["limite_diario
          +"]) == (None, None)                                           
      269 +                                                              
      270 +                                                              
      271 +def _caso_hospedagem_duplicata_so_uma_com_nota(saida):        
      272 +    # RN-007: a com nota é a original; RN-010: comprova 14/07 
          +e 15/07;                                                      
      273 +    # alimentação 80,00 em 15/07 ≤ 90,00 → aprovado           
      274 +    itens = {item["id"]: item for item in saida["itens"]}     
      275 +    assert itens["sem"]["motivo"] == "duplicata"              
      276 +    _em_viagem(itens["com"], Decimal("250.00"))               
      277 +    _em_viagem(itens["a"], Decimal("90.00"))                  
      278 +    assert itens["a"]["status"] == "aprovado"                 
      279 +                                                              
      280 +                                                              
      281 +def _caso_hospedagem_varias_diarias(saida):                   
      282 +    # RN-012: uma diária, min(480,00; 250,00) = 250,00 → parci
          +al; RN-010: 14 e 15/07                                        
      283 +    hospedagem, a15, a16 = saida["itens"]                     
      284 +    assert (hospedagem["valor_reembolsado"], hospedagem["statu
          +s"]) == (                                                     
      285 +        Decimal("250.00"), "parcial",                         
      286 +    )                                                         
      287 +    _em_viagem(hospedagem, Decimal("250.00"))                 
     … 146 more lines (ctrl+o to expand)

⏺ Falharam pelo motivo certo (em_viagem falso, limite normal). Os que passaram
  são os negativos (não fica em viagem), esperado sem a etapa 8. Implementando.

  Ran 1 shell command (ctrl+o to expand)

⏺ Suite verde; um E501 a corrigir. Verifico também um caso extremo: hospedagem
  em 9999-12-31 (D+1 não é representável).

⏺ Bash(sed -i '' 's/    assert (hospedagem\["status"\], hospedagem\["motivo"\])
      == ("recusado", "fora_do_periodo")/    assert (hospedagem["status"],
      hospedagem["motivo…)
  ⎿               ~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     OverflowError: date value out of range
     All checks passed!
  ⎿  Updated tests/test_rn010_viagem.py (+3 -1)
      125      )["itens"]
      126  
      127      # recusada na etapa 4 → não comprova viagem; min(80,00; 60
           ,00) = 60,00
      128 -    assert (hospedagem["status"], hospedagem["motivo"]) == ("r
          -ecusado", "fora_do_periodo")                                  
      128 +    assert (hospedagem["status"], hospedagem["motivo"]) == (  
      129 +        "recusado", "fora_do_periodo",                        
      130 +    )                                                         
      131      assert (hospedagem["em_viagem"], hospedagem["limite_diario
           "]) == (None, None)
      132      assert alimentacao["em_viagem"] is False
      133      assert _resumo(alimentacao) == (

⏺ Crash confirmado (OverflowError). O resultado é determinado pela spec (nenhuma
  despesa pode ter data 10000-01-01, então D+1 inexistente não muda nada);
  corrijo o crash e adiciono teste.

⏺ Bash(python3 - <<'EOF'
      p='src/reembolso/motor.py'…)
  ⎿  """Limite diário por categoria: RN-009, AMB-001, AMB-002, AMB-003, AMB
     -006, AMB-017.
     … +3 lines (ctrl+o to expand)
  ⎿  Updated src/reembolso/motor.py (+3 -1)
      154              and despesa.tem_nota_fiscal
      155          ):
      156              for dias_depois in range(DIAS_EM_VIAGEM_APOS_HOSPE
           DAGEM + 1):
      157 -                dias.add(despesa.data + timedelta(days=dias_de
          -pois))                                                        
      157 +                # D+1 depois de 9999-12-31 não existe: nenhuma
          + despesa cai nele                                             
      158 +                if despesa.data <= date.max - timedelta(days=d
          +ias_depois):                                                  
      159 +                    dias.add(despesa.data + timedelta(days=dia
          +s_depois))                                                    
      160      return dias
      161  
      162  
  ⎿  Updated tests/test_rn009_limite_diario.py (+0 -2)
      1  """Limite diário por categoria: RN-009, AMB-001, AMB-002, AMB-00
         3, AMB-006, AMB-017.
      2  
      3 -Até a T-018 não há viagem: os casos usam datas sem hospedagem co
        -m nota, ou não                                                  
      4 -conferem `em_viagem`/limite de alimentação e transporte nessas d
        -atas.                                                           
      3  """
      4  
      5  from decimal import Decimal
  ⎿  Updated tests/test_rn010_viagem.py (+13 -0)
      295      )["itens"]
      296  
      297      assert [item["em_viagem"] for item in itens] == [True, Tru
           e, True, False]
      298 +                                                              
      299 +                                                              
      300 +def test_rn010_hospedagem_no_ultimo_dia_representavel(avaliar,
          + despesa):                                                    
      301 +    """RN-010: hospedagem com nota em 9999-12-31 (período até 
          +essa data) → a data                                           
      302 +    fica em viagem; o D+1 não existe e não interrompe o proces
          +samento."""                                                   
      303 +    (hospedagem,) = avaliar(                                  
      304 +        despesa(**_hospedagem(data="9999-12-31", valor=Decimal
          +("50.00"))),                                                  
      305 +        periodo={"inicio": "9999-12-01", "fim": "9999-12-31"},
      306 +    )["itens"]                                                
      307 +                                                              
      308 +    # 50,00 ≤ 250,00 → aprovado; D em viagem                  
      309 +    assert hospedagem["em_viagem"] is True                    
      310 +    assert _resumo(hospedagem) == (Decimal("50.00"), "aprovado
          +", None)                                                      

  Ran 1 shell command (ctrl+o to expand)

⏺ Bash(python3 - <<'EOF'
      p='tests/test_rn009_limite_diario.py'…)
  ⎿  ............................
        [100%]
     604 passed in 0.24s
     … +6 lines (ctrl+o to expand)
  ⎿  Updated tests/test_rn009_limite_diario.py (+2 -0)
      1  """Limite diário por categoria: RN-009, AMB-001, AMB-002, AMB-00
         3, AMB-006, AMB-017.
      2  
      3 +Os casos de alimentação e transporte usam datas sem hospedagem c
        +om nota (fora de                                                
      4 +viagem); os limites em viagem estão em `test_rn010_viagem.py`.  
      5  """
      6  
      7  from decimal import Decimal

⏺ Verde. Rodo o revisor independente (task de regra de negócio).

⏺ revisor-de-task(Revisar T-018)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ Implementação e testes estão prontos (604 testes passando, ruff limpo). O
  revisor independente da T-018 ainda está rodando; quando ele terminar, eu
  salvo o relatório em docs/reviews/T-018.md e mando o resumo completo para você
  aprovar.

✻ Brewed for 2m 54s · done 9:29 AM
› Message from revisor-de-task
  # Revisão T-018 — Viagem: etapa 8, dias em viagem {D, D+1} e limites em viagem

  - **Data:** 2026-10-02
  - **Regras conferidas:** RN-010, RN-012 (parte de viagem), RN-009 (tabela de
  viagem), RN-008/RN-007/RN-005 (interação), AMB-004, AMB-005, AMB-006, AMB-016
  (ordem das etapas, seção 8)
  - **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 604 passed, 0
  failed (evidência, não veredito)

  ### Resultado
  **APROVADO COM RESSALVAS** — todos os critérios de aceite foram atendidos e
  conferidos à mão contra a spec. Ficam só observações BAIXA: uma guarda de data
  máxima que a spec não prevê, mas que não muda resultado, e um teste de
  duplicata que não tem como isolar o efeito pretendido.

  ### Critérios de aceite
  | # | Critério | Status | Evidência |
  |---|---|---|---|
  | 1 | Hospedagem com nota em 14/07 → 14/07 e 15/07 em viagem | atendido |
  `tests/test_rn010_viagem.py::test_rn010_hospedagem_com_nota_poe_d_e_d_mais_1_e
  m_viagem` (13/07 e 16/07 ficam False); `motor.py` `_dias_em_viagem` |
  | 2 | Alimentação 80,00 em 15/07 → limite 90,00, `aprovado` | atendido |
  `test_rn010_alimentacao_no_dia_seguinte_tem_limite_de_viagem` (80 ≤ 90 →
  aprovado 80,00, conferido) |
  | 3 | Alimentação 80,00 em 16/07 → limite 60,00, `parcial` com 60,00 |
  atendido | `test_rn010_alimentacao_dois_dias_depois_tem_limite_normal` |
  | 4 | Transporte em viagem → limite 120,00 | atendido |
  `test_rn010_transporte_em_viagem_tem_limite_120` (130 → 120 parcial,
  conferido) |
  | 5 | Hospedagem em viagem continua com limite 250,00 | atendido |
  `test_rn010_hospedagem_em_viagem_continua_com_limite_250`; `politica.py`
  hospedagem viagem=250,00 |
  | 6 | Hospedagem 80,00 sem nota → reembolsada, data não fica em viagem |
  atendido |
  `test_rn010_hospedagem_sem_nota_e_reembolsada_mas_nao_comprova_viagem` (03/07
  e 04/07 com limite 60,00) |
  | 7 | Hospedagem com nota recusada nas etapas 1 a 7 (fora do período,
  duplicata) não comprova viagem | atendido |
  `test_rn010_hospedagem_fora_do_periodo_nao_comprova_viagem`,
  `test_rn010_hospedagem_duplicata_nao_comprova_viagem`,
  `test_rn010_duplicatas_de_hospedagem_sem_nota_nao_comprovam_viagem`;
  `motor.py` chama `_dias_em_viagem(originais)`, só sobre as que passaram pelas
  etapas 1 a 7 |
  | 8 | Hospedagem com nota que recebe 0 no limite (terceira do dia) comprova
  viagem | atendido |
  `test_rn010_hospedagem_que_recebe_zero_no_limite_comprova_viagem` (200+50 =
  250 → h3 recebe 0; 15/07 em viagem) |
  | 9 | Alimentação antes da hospedagem na entrada → em viagem | atendido |
  `test_rn010_alimentacao_antes_da_hospedagem_na_entrada_esta_em_viagem`; a
  etapa 8 roda antes da 9 em `calcular` |
  | 10 | Hospedagem em 31/07 põe 01/08 em viagem sem efeito (fora do período) |
  atendido |
  `test_rn010_hospedagem_no_ultimo_dia_poe_dia_seguinte_fora_do_periodo`
  (`em_viagem`/`limite_diario` nulos em 01/08, como manda a seção 4) |
  | 11 | `test_rn012`: 480,00 com nota em 14/07 → 14/07 e 15/07 em viagem, não
  16/07 | atendido | `tests/test_rn012_hospedagem_uma_diaria.py::test_rn012_hosp
  edagem_de_480_poe_em_viagem_so_d_e_d_mais_1` |
  | 12 | Casos de borda da task na seção 7 | atendido | Os 9 ids foram
  adicionados em `tests/test_casos_de_borda.py`, e "Duplicata de hospedagem só
  uma com nota" é testado nas duas ordens. Os esperados batem com as linhas 426
  e 439 a 454 da spec |

  Verificação extra: rodei o motor em memória sobre
  `exemplos/despesas-exemplo.json`. As 14 linhas e os totais (1.861,84 / 585,43
  / 1.276,41) batem com a tabela da seção 9, inclusive d-010 e d-011 em viagem e
  d-011 com limite 90,00.

  ### Problemas encontrados
  #### 1. Guarda de `date.max` em `_dias_em_viagem` — severidade BAIXA
  - **Regra afetada:** nenhuma regra determina isto
  - **Evidência:** `src/reembolso/motor.py`, em `_dias_em_viagem`: `if
  despesa.data <= date.max - timedelta(days=dias_depois)`. A spec não trata
  hospedagem em 9999-12-31; existe o teste
  `test_rn010_hospedagem_no_ultimo_dia_representavel`.
  - **Impacto:** nenhum no resultado. Nenhuma despesa pode ter a data
  10000-01-01, então omitir esse D+1 não muda o valor de nenhum item. A guarda
  só evita que o processamento seja interrompido.
  - **Recomendação:** nada a mudar no resultado. Opcionalmente, registrar como
  caso técnico (plan/DECISIONS) para que fique rastreável.

  #### 2. O teste "duplicata não comprova viagem" não isola o efeito —
  severidade BAIXA
  - **Regra afetada:** RN-010 / RN-007
  - **Evidência:** `test_rn010_hospedagem_duplicata_nao_comprova_viagem`. A
  original e a cópia têm a mesma data, então a viagem que se observa vem da
  original. O teste passaria mesmo que a duplicata contasse como prova.
  - **Impacto:** nenhum observável. Pela RN-007, se uma cópia tem nota, a
  original também tem, e a data é a mesma. Por isso uma duplicata com nota nunca
  acrescenta dias, e não existe entrada capaz de distinguir as duas
  implementações. A garantia vem da estrutura do código
  (`_dias_em_viagem(originais)`).
  - **Recomendação:** nenhuma ação obrigatória.

  #### 3. Hospedagem "em viagem continua com 250" não distingue limite normal de
  limite de viagem — severidade BAIXA
  - **Regra afetada:** AMB-006
  - **Evidência:** `politica.py` usa normal = viagem = 250,00 para hospedagem.
  Pela AMB-006 os dois valores são iguais, então nenhum teste consegue
  distinguir qual dos dois campos foi lido.
  - **Impacto:** nenhum.
  - **Recomendação:** nenhuma.

  ### Cobertura
  - **Regras testadas:** RN-010 / AMB-004 → `tests/test_rn010_viagem.py` (17
  testes) e 9 casos em `tests/test_casos_de_borda.py`. RN-012 / AMB-005 →
  `test_rn012_hospedagem_de_480_poe_em_viagem_so_d_e_d_mais_1` e "Hospedagem com
  várias diárias na descrição". AMB-006 →
  `test_rn010_hospedagem_em_viagem_continua_com_limite_250`. AMB-016 (etapa 8
  antes da 9, recusadas nas etapas 1 a 7 não comprovam) → testes de fora do
  período, nota ausente, duplicata e alimentação antes da hospedagem.
  - **Casos de borda cobertos:** Limite de nota em viagem; Duplicata de
  hospedagem só uma com nota (duas ordens); Hospedagem com várias diárias na
  descrição; Dia seguinte à diária; Dois dias depois da diária; Hospedagem sem
  nota até 100; Hospedagem sem nota acima de 100; Hospedagem fora do período;
  Alimentação antes da hospedagem na entrada, mesma data. Também: D-1 fora de
  viagem, união de hospedagens em dias seguidos, hospedagem que recebe 0 no
  limite e D+1 fora do período.
  - **Casos que parecem faltar:** nenhum que a spec exija para esta task.

  ### Decisões necessárias
  Nenhuma.

  ### Antes de concluir a task
  Nada — pode seguir para o commit. O item 1 dos problemas pode, opcionalmente,
  ser registrado no plan/DECISIONS para rastreabilidade.

  Arquivos revisados:
  `/Users/rafaeltxm/repo/sdd-desafio/src/reembolso/motor.py`,
  `/Users/rafaeltxm/repo/sdd-desafio/src/reembolso/politica.py`,
  `/Users/rafaeltxm/repo/sdd-desafio/tests/test_rn010_viagem.py`,
  `/Users/rafaeltxm/repo/sdd-desafio/tests/test_rn012_hospedagem_uma_diaria.py`,
  `/Users/rafaeltxm/repo/sdd-desafio/tests/test_casos_de_borda.py`,
  `/Users/rafaeltxm/repo/sdd-desafio/tests/test_rn009_limite_diario.py` (só a
  docstring mudou).

  Listed 1 directory (ctrl+o to expand)

⏺ Agent "Revisar T-018" finished · 1m 3s

⏺ Write(docs/reviews/T-018.md)
  ⎿  Wrote 58 lines to docs/reviews/T-018.md
      1 # Revisão T-018 — Viagem: etapa 8, dias em viagem {D, D+1} e limi
      2 
      3 - **Data:** 2026-10-02
         (tabela de viagem), RN-008/RN-007/RN-005 (interação), AMB-004, A
      5 - **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 60
        4 passed, 0 failed (evidência, não veredito)
      7 ### Resultado
      8 **APROVADO COM RESSALVAS** — todos os critérios de aceite foram a
        AIXA: uma guarda de data máxima que a spec não prevê, mas que não
        o efeito pretendido
     … +129 lines (ctrl+o to expand)

⏺ Update(docs/reviews/T-018.md)
  ⎿  Added 1 line, removed 1 line
      55  ### Antes de concluir a task
      56  Nada — pode seguir para o commit. O item 1 dos problemas pode, 
          opcionalmente, ser registrado no plan/DECISIONS para rastreabil
          idade.
      57  
      58 -Arquivos revisados: `/Users/rafaeltxm/repo/sdd-desafio/src/reem
         -bolso/motor.py`, `/Users/rafaeltxm/repo/sdd-desafio/tests/test_
         -rn010_viagem.py`, `/Users/rafaeltxm/repo/sdd-desafio/tests/test
         -_rn012_hospedagem_uma_diaria.py`, `/Users/rafaeltxm/repo/sdd-de
         -safio/tests/test_casos_de_borda.py`, `/Users/rafaeltxm/repo/sdd
         --desafio/tests/test_rn009_limite_diario.py` (só a docstring mud
         -ou), `/Users/rafaeltxm/repo/sdd-desafio/src/reembolso/politica.
         -py`.                                                           
      58 +Arquivos revisados: `/Users/rafaeltxm/repo/sdd-desafio/src/reem
         +bolso/motor.py`, `/Users/rafaeltxm/repo/sdd-desafio/src/reembol
         +so/politica.py`, `/Users/rafaeltxm/repo/sdd-desafio/tests/test_
         +rn010_viagem.py`, `/Users/rafaeltxm/repo/sdd-desafio/tests/test
         +_rn012_hospedagem_uma_diaria.py`, `/Users/rafaeltxm/repo/sdd-de
         +safio/tests/test_casos_de_borda.py`, `/Users/rafaeltxm/repo/sdd
         +-desafio/tests/test_rn009_limite_diario.py` (só a docstring mud
         +ou).                                                           

⏺ Resumo — T-018: Viagem (etapa 8), {D, D+1} e limites em viagem

  A etapa 8 está implementada: 604 testes passando, ruff limpo e o revisor
  independente deu APROVADO COM RESSALVAS. Há uma interpretação que a spec não
  cobre (item 1 de "Decisões"); você decide se ela entra na spec antes do
  commit.

  Arquivos alterados:
  - src/reembolso/motor.py (modificado): nova função _dias_em_viagem (etapa 8).
    _aplicar_limite passa a receber as datas em viagem e usa o limite de viagem
    nessas datas, preenchendo em_viagem.
  - tests/test_rn010_viagem.py (novo).
  - tests/test_rn012_hospedagem_uma_diaria.py (modificado): teste da parte de
    viagem; tirei a nota "é da T-018".
  - tests/test_casos_de_borda.py (modificado): 9 casos de viagem da seção 7, com
    "Duplicata de hospedagem só uma com nota" testado nas duas ordens.
  - tests/test_rn009_limite_diario.py (modificado, só a docstring): a frase "Até
    a T-018 não há viagem" ficou desatualizada e foi reescrita.
  - docs/reviews/T-018.md (novo).

  Testes criados/alterados:
  - test_rn010_hospedagem_com_nota_poe_d_e_d_mais_1_em_viagem → RN-010 / AMB-004
  - test_rn010_alimentacao_no_dia_seguinte_tem_limite_de_viagem e
    test_rn010_alimentacao_dois_dias_depois_tem_limite_normal → RN-010
  - test_rn010_transporte_em_viagem_tem_limite_120 → RN-010 / RN-009
  - test_rn010_hospedagem_em_viagem_continua_com_limite_250 → AMB-006
  - test_rn010_hospedagem_sem_nota_e_reembolsada_mas_nao_comprova_viagem →
    RN-010 / AMB-004
  - test_rn010_hospedagem_fora_do_periodo_nao_comprova_viagem → RN-010 / RN-005
  - test_rn010_hospedagem_duplicata_nao_comprova_viagem,
    test_rn010_duplicatas_de_hospedagem_sem_nota_nao_comprovam_viagem e
    test_rn010_duplicata_de_hospedagem_so_uma_com_nota_comprova_viagem[2 ordens]
    → RN-010 / RN-007
  - test_rn010_hospedagem_acima_de_100_sem_nota_nao_comprova_viagem → RN-010 /
    RN-008
  - test_rn010_hospedagem_que_recebe_zero_no_limite_comprova_viagem → AMB-016
  - test_rn010_alimentacao_antes_da_hospedagem_na_entrada_esta_em_viagem →
    AMB-016 (etapa 8 antes da 9)
  - test_rn010_hospedagem_no_ultimo_dia_poe_dia_seguinte_fora_do_periodo →
    RN-010 / RN-005
  - test_rn010_limite_de_nota_nao_amplia_em_viagem → RN-008 / AMB-007
  - test_rn010_duas_hospedagens_em_datas_seguidas_cobrem_tres_dias → RN-010
  - test_rn010_hospedagem_no_ultimo_dia_representavel → RN-010 (ver Decisões)
  - test_rn012_hospedagem_de_480_poe_em_viagem_so_d_e_d_mais_1 → RN-012 /
    AMB-005
  - Casos de borda: Limite de nota em viagem · Duplicata de hospedagem só uma
    com nota (+ ordem inversa) · Hospedagem com várias diárias na descrição ·
    Dia seguinte à diária · Dois dias depois da diária · Hospedagem sem nota até
    100 · Hospedagem sem nota acima de 100 · Hospedagem fora do período ·
    Alimentação antes da hospedagem na entrada, mesma data

  Testes executados antes da implementação: os 3 arquivos acima. 17 falharam
  pelo motivo certo (em_viagem falso, limite 60,00 em vez de 90,00). Os que
  passaram são os casos em que a data não deve ficar em viagem: sem nota, fora
  do período, nota ausente, D+2. Eles já passavam porque não existia viagem;
  servem para impedir que a implementação marque viagem demais.

  Testes executados depois: uv run pytest -q e uv run ruff check .

  pytest: 604 passed, 0 failed

  ruff: limpo

  Revisão independente: APROVADO COM RESSALVAS, sem decisões necessárias, salva
  em docs/reviews/T-018.md. Há 3 ressalvas de severidade BAIXA:
  1. A proteção contra 9999-12-31 não vem da spec; não muda nenhum resultado.
  2. O teste "duplicata não comprova viagem" não isola o efeito. Pela RN-007, a
     original tem a mesma data e também tem nota, então nenhuma entrada consegue
     distinguir as duas implementações.
  3. O limite de hospedagem normal e em viagem é 250,00 nos dois casos, então
     nenhum teste distingue qual dos dois foi usado.

  As ressalvas 2 e 3 não pedem ação.

  Decisões ou interpretações realizadas:
  1. Hospedagem com nota em 9999-12-31. Sem proteção, o cálculo de D+1 estoura
     (OverflowError, eu reproduzi) e o programa termina com um traceback, ou
     seja, quebra. Passei a ignorar o D+1 quando a data não existe. O resultado
     não muda: nenhuma despesa pode ter data 10000-01-01. Mesmo assim, a spec
     não trata esse caso. Se você quiser rastreabilidade, isso vira uma linha no
     plan.md (caso técnico) ou no DECISIONS.md antes do commit; o revisor
     marcou como opcional.

  Lacunas ou dúvidas: a justificativa (texto não contratual) não cita a viagem.
  Ela mostra o limite aplicado, mas não diz que foi ampliado. Não alterei porque
  está fora do escopo da task.

  Commit proposto: feat(T-018): etapa 8 marca D e D+1 de cada hospedagem com 
  nota como em viagem e aplica limites de viagem

  Posso fazer o commit? E quer registrar o caso de 9999-12-31 no plan/DECISIONS
  antes?

✻ Worked for 4m 48s · done 9:31 AM

❯ Faz sentido registrar?                                                        

⏺ Não recomendo registrar. Eu faria o commit como está.

  Por que não entra na spec nem no DECISIONS.md: a proteção não é uma regra de
  negócio. A spec já define o resultado: a RN-010 põe D+1 em viagem, e uma data
  10000-01-01 não existe. Então nenhuma despesa pode cair nela, e ignorar esse
  D+1 dá exatamente a saída que a spec manda. A proteção só evita que o programa
  quebre. O DECISIONS.md registra mudanças de interpretação da política, e aqui
  nada mudou.

  Por que também não no plan.md: o plano registra escolhas de arquitetura e de
  biblioteca, como Decimal, gravação atômica e a ordem das etapas. Uma proteção
  de uma linha contra o limite de date está no nível de detalhe do código. Ela
  já fica rastreável por dois caminhos:
  - o comentário em _dias_em_viagem, que explica por que a proteção existe (é um
    porquê técnico, não uma regra escondida em comentário);
  - o teste test_rn010_hospedagem_no_ultimo_dia_representavel, que quebra se
    alguém tirar a proteção.

  Quando passaria a fazer sentido registrar: se o limite de datas virasse uma
  questão de entrada. Por exemplo, se a gente decidisse que datas absurdas como
  9999-12-31 devem ser entrada_invalida. Isso seria regra nova e iria para a
  spec, mas a spec atual não pede isso e não estou propondo.

  Se concordar, faço o commit com a mensagem proposta e depois marco a task.

✻ Sautéed for 9s · done 9:33 AM

❯ pode commitar                                                                 

  Ran 1 shell command (ctrl+o to expand)

⏺ Bash(python3 - <<'EOF'
      p='specs/001-motor-reembolso/tasks.md'…)
  ⎿   specs/001-motor-reembolso/tasks.md | 4 ++--
      1 file changed, 2 insertions(+), 2 deletions(-)
     -- [ ] **T-018** — Viagem: etapa 8, antes do limite, `dias_em_viagem`
     … +11 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+2 -2)
      157    - **Casos de borda:** Duplicata exata · Fornecedor com acent
           o · Fornecedor com espaços internos · Quase duplicata · Cópias
            idênticas sem nota acima de 100 · Relançamento com nota
      158    - **Commit:** `555a85e`
      159  
      160 -- [ ] **T-018** — Viagem: etapa 8, antes do limite, `dias_em_v
          -iagem` = {D, D+1} de cada hospedagem com nota que passou pelas
          - etapas 1 a 7; nessas datas, limites de alimentação e transpor
          -te em viagem; `em_viagem` verdadeiro no item.                 
      160 +- [x] **T-018** — Viagem: etapa 8, antes do limite, `dias_em_v
          +iagem` = {D, D+1} de cada hospedagem com nota que passou pelas
          + etapas 1 a 7; nessas datas, limites de alimentação e transpor
          +te em viagem; `em_viagem` verdadeiro no item.                 
      161    - **Tipo:** regra
      162    - **Atende:** RN-010, RN-012 (parte de viagem), AMB-004, AMB
           -005, AMB-006
      163    - **Depende de:** T-017
      164    - **Aceite:** `tests/test_rn010_viagem.py` passa: hospedagem
            com nota em 14/07 → 14/07 e 15/07 em viagem; alimentação 80,0
           0 em 15/07 → limite 90,00, `aprovado`; alimentação 80,00 em 16
           /07 → limite 60,00, `parcial` com 60,00; transporte em viagem 
           → limite 120,00; hospedagem em viagem continua com limite 250,
           00; hospedagem 80,00 sem nota → reembolsada, mas data não fica
            em viagem; hospedagem com nota recusada nas etapas 1 a 7 (for
           a do período, duplicata) não comprova viagem; hospedagem com n
           ota que recebe 0 no limite (terceira do dia) comprova viagem; 
           alimentação antes da hospedagem na entrada → em viagem; hosped
           agem em 31/07 põe 01/08 em viagem sem efeito (fora do período)
           . `test_rn012_hospedagem_uma_diaria.py`: 480,00 com nota em 14
           /07 → 14/07 e 15/07 em viagem, não 16/07.
      165    - **Casos de borda:** Limite de nota em viagem · Duplicata d
           e hospedagem só uma com nota · Hospedagem com várias diárias n
           a descrição · Dia seguinte à diária · Dois dias depois da diár
           ia · Hospedagem sem nota até 100 · Hospedagem sem nota acima d
           e 100 · Hospedagem fora do período · Alimentação antes da hosp
           edagem na entrada, mesma data
      166 -  - **Commit:**                                               
      166 +  - **Commit:** b1cb651                                       
      167  
      168  ## Fase 4 — Saída e CLI
      169  
  ⎿  PostToolUse:Bash says: 📝 Fim do bloco de trabalho ("docs(tasks): conclui 
     T-018"). Exporte a sessão antes de continuar:
        /export docs/sessions/29-<descricao-curta>.md
        e commite com: docs(sessions): export da sessão 29

⏺ A T-018 está concluída e commitada. Os hooks passaram (ruff + pytest, 604
  testes).

  - b1cb651 feat(T-018): etapa 8 marca D e D+1 de cada hospedagem com nota como 
    em viagem e aplica limites de viagem, com a revisão em docs/reviews/T-018.md
  - 2ecd18a docs(tasks): conclui T-018: a task está marcada [x] com o hash do
    commit

  📝 Fim do bloco: exporte a sessão antes de continuar:
  /export docs/sessions/29-<descricao-curta>.md
  e faça o commit com docs(sessions): export da sessão 29.

  Não vou começar a T-019 (CLI) sem você pedir.

✻ Cogitated for 12s · done 9:33 AM