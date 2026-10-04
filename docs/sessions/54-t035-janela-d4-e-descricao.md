 ▐▛███▛█   Claude Code v2.1.287
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~/repo/sdd-desafio

  Get to finished work sooner with Opus 5.5. Switch anytime with /model.

❯ /clear                                                                        

❯ pode continuar                                                                

  Ran 1 shell command (ctrl+o to expand)

⏺ Próxima pendente é a T-035. Seguindo o fluxo, executo pela skill /task.

⏺ Skill(task)
  ⎿  Successfully loaded skill

  Listed 1 directory, ran 4 shell commands (ctrl+o to expand)

⏺ Retomando a T-035 (janela da cotação até D-4 e descricao de qualquer tipo).
  Antes de escrever os testes, estou lendo o que já existe para a RN-015, a
  RN-002 e os casos de borda.

  Searched for 1 pattern, ran 5 shell commands (ctrl+o to expand)

⏺ Já li o contexto. Agora vou escrever os testes: primeiro mudo os da janela da
  cotação de D-3/D-4 para D-4/D-5.

⏺ Bash(python3 - <<'EOF'
      from pathlib import Path…)
  ⎿  Updated tests/test_rn015_moeda_e_cambio.py (+46 -19)
      35      )
      36  
      37  
      38 -def test_rn015_cotacao_ate_3_dias_antes():                     
      39 -    """RN-015 / AMB-024: câmbio só com 13/07; USD em 16/07 usa 
         -13/07 (D-3)."""                                                
      38 +def test_rn015_cotacao_ate_4_dias_antes():                     
      39 +    """RN-015 / AMB-024: câmbio só com 13/07; USD em 17/07 usa 
         +13/07 (D-4)."""                                                
      40      cambio = _cambio(taxas={"2026-07-13": {"USD": Decimal("5.42
          ")}})
      41 -    # 16/07 - 3 dias = 13/07: ainda dentro da janela           
      42 -    assert cotacao(cambio, "USD", date(2026, 7, 16)) == Cotacao
         -(                                                              
      41 +    # 17/07 - 4 dias = 13/07: ainda dentro da janela D a D-4   
      42 +    assert cotacao(cambio, "USD", date(2026, 7, 17)) == Cotacao
         +(                                                              
      43          Decimal("5.42"), date(2026, 7, 13)
      44      )
      45  
      46  
      47 -def test_rn015_cotacao_4_dias_antes_nao_serve():               
      48 -    """RN-015 / AMB-024: câmbio só com 13/07; USD em 17/07 → se
         -m cotação (D-4)."""                                            
      47 +def test_rn015_cotacao_5_dias_antes_nao_serve():               
      48 +    """RN-015 / AMB-024: câmbio só com 13/07; USD em 18/07 → se
         +m cotação (D-5)."""                                            
      49      cambio = _cambio(taxas={"2026-07-13": {"USD": Decimal("5.42
          ")}})
      50 -    # 17/07 - 4 dias = 13/07: fora da janela D a D-3           
      51 -    assert cotacao(cambio, "USD", date(2026, 7, 17)) is None   
      50 +    # 18/07 - 5 dias = 13/07: fora da janela D a D-4           
      51 +    assert cotacao(cambio, "USD", date(2026, 7, 18)) is None   
      52 +                                                               
      53 +                                                               
      54 +def test_rn015_terca_de_carnaval_usa_a_sexta():                
      55 +    """RN-015 / AMB-024: câmbio só com 05/02/2027 (sexta); EUR 
         +em 09/02/2027                                                  
      56 +    (terça de Carnaval) usa 05/02 (D-4)."""                    
      57 +    cambio = _cambio(taxas={"2027-02-05": {"EUR": Decimal("6.00
         +")}})                                                          
      58 +    # 09/02 - 4 dias = 05/02; 06/02 a 08/02 sem cotação        
      59 +    assert cotacao(cambio, "EUR", date(2027, 2, 9)) == Cotacao(
      60 +        Decimal("6.00"), date(2027, 2, 5)                      
      61 +    )                                                          
      62  
      63  
      64  def test_rn015_nunca_usa_cotacao_posterior():
     ...
      103  
      104  
     … 61 more lines (ctrl+o to expand)

  Ran 1 shell command (ctrl+o to expand)
  ⎿  You've hit your session limit · resets 7:20pm (America/Sao_Paulo)
     /upgrade or /usage-credits to finish what you’re working on.

⏺ Usage limit reached · continuing automatically at 7:20pm · esc to 
  cancel

✻ Brewed for 1m 11s · done 5:25 PM

⏺ Usage limit reset · continuing automatically

⏺ Testes da RN-015 atualizados. Agora os da descricao na RN-002.

⏺ Update(tests/test_rn002_validacao_da_entrada.py)
  ⎿  Added 38 lines
      695      assert com_extra == sem_extra
      696  
      697  
      698 +@pytest.mark.parametrize(                                     
      699 +    "descricao", [None, 17, True, [], {}, "Almoço"],          
      700 +    ids=["nula", "numero", "booleano", "lista", "objeto", "tex
          +to"],                                                         
      701 +)                                                             
      702 +def test_rn002_descricao_de_qualquer_tipo_nao_invalida(entrada
          +, despesa, descricao):                                        
      703 +    """RN-002 / D-008: `descricao` nula ou de qualquer tipo → 
          +a despesa segue,                                              
      704 +    igual à mesma despesa sem `descricao`."""                 
      705 +    com_descricao = _uma(entrada, despesa(descricao=descricao)
          +)                                                             
      706 +    sem_descricao = _uma(entrada, despesa())                  
      707 +    assert isinstance(com_descricao, Despesa)                 
      708 +    assert com_descricao == sem_descricao                     
      709 +                                                              
      710 +                                                              
      711 +def test_rn002_descricao_com_surrogate_isolado_e_erro_de_arqui
          +vo(entrada, despesa):                                         
      712 +    """RN-002 / D-008: a `descricao` segue sujeita aos erros d
          +e forma:                                                      
      713 +    `"Almoço \\uD800"` (surrogate isolado) → erro de arquivo."
          +""                                                            
      714 +    texto = simplejson.dumps(                                 
      715 +        entrada(despesas=[despesa(descricao="DESCRICAO")]),   
      716 +        use_decimal=True, ensure_ascii=False,                 
      717 +    ).replace('"DESCRICAO"', r'"Almoço \uD800"')              
      718 +    with pytest.raises(ErroDeArquivo):                        
      719 +        ler_entrada(texto.encode())                           
      720 +                                                              
      721 +                                                              
      722 +@pytest.mark.parametrize("descricao", [None, 17, True, [], {}]
          +)                                                             
      723 +def test_rn002_descricao_de_outro_tipo_segue_no_motor(avaliar,
          + despesa, descricao):                                         
      724 +    """RN-002 / D-008: alimentação 45,00 sem nota com `descric
          +ao` não textual →                                             
      725 +    `aprovado` com 45,00."""                                  
      726 +    documento = despesa(valor=Decimal("45.00"), descricao=desc
          +ricao)                                                        
      727 +    del documento["tem_nota_fiscal"]                          
      728 +    documento["tem_nota_fiscal"] = False                      
      729 +    (item,) = avaliar(documento)["itens"]                     
      730 +                                                              
      731 +    # 45,00 ≤ 100,00 (mínimo da nota) e ≤ 60,00 (alimentação, 
          +padrao) → aprovado                                            
      732 +    assert (item["status"], item["valor_reembolsado"]) == ("ap
          +rovado",                                                      
      733 +                                                          Deci
          +mal("45.00"))                                                 
      734 +                                                              
      735 +                                                              
      736  def test_rn002_despesas_mantem_posicao_e_ordem(entrada, despes
           a):
      737      """RN-001 / RN-002: uma despesa inválida não afeta as dema
           is; ordem mantida."""
      738      resultado = _despesas(

⏺ Update(tests/test_rn002_validacao_da_entrada.py)
  ⎿  Added 3 lines, removed 4 lines
      723  def test_rn002_descricao_de_outro_tipo_segue_no_motor(avaliar,
            despesa, descricao):
      724      """RN-002 / D-008: alimentação 45,00 sem nota com `descric
           ao` não textual →
      725      `aprovado` com 45,00."""
      726 -    documento = despesa(valor=Decimal("45.00"), descricao=desc
          -ricao)                                                        
      727 -    del documento["tem_nota_fiscal"]                          
      728 -    documento["tem_nota_fiscal"] = False                      
      729 -    (item,) = avaliar(documento)["itens"]                     
      726 +    (item,) = avaliar(                                        
      727 +        despesa(valor=Decimal("45.00"), tem_nota_fiscal=False,
          + descricao=descricao)                                         
      728 +    )["itens"]                                                
      729  
      730      # 45,00 ≤ 100,00 (mínimo da nota) e ≤ 60,00 (alimentação, 
           padrao) → aprovado
      731      assert (item["status"], item["valor_reembolsado"]) == ("ap
           rovado",

  Ran 1 shell command (ctrl+o to expand)

⏺ Agora os casos de borda da seção 7 em test_casos_de_borda.py.

⏺ Bash(python3 - <<'EOF'
      from pathlib import Path…)
  ⎿                                      Decimal("60.00"))
     E       AssertionError: assert ('EUR', None, None, None) == ('EUR', De
     cim...imal('60.00'))
     … +18 lines (ctrl+o to expand)
  ⎿  Updated tests/test_casos_de_borda.py (+46 -7)
      836      verificar(processar(texto))
      837  
      838  
      839 +def _descricao(descricao):                                    
      840 +    return _json(despesa(valor=Decimal("45.00"), tem_nota_fisc
          +al=False,                                                     
      841 +                         descricao=descricao))                
      842 +                                                              
      843 +                                                              
      844 +@pytest.mark.parametrize(                                     
      845 +    "textos",                                                 
      846 +    [                                                         
      847 +        pytest.param(                                         
      848 +            (_descricao(None), _descricao(17), _descricao({}))
          +,                                                             
      849 +            id="Descrição nula ou de outro tipo",             
      850 +        ),                                                    
      851 +    ],                                                        
      852 +)                                                             
      853 +def test_caso_de_borda_com_varios_arquivos(processar, textos):
      854 +    """Seção 7 da spec: casos com uma entrada por arquivo (RN-
          +002)."""                                                      
      855 +    for texto in textos:                                      
      856 +        (item,) = processar(texto)["itens"]                   
      857 +        # 45,00 ≤ 100,00 (sem nota) e ≤ 60,00 (alimentação) → 
          +aprovado                                                      
      858 +        assert (item["status"], item["valor_reembolsado"]) == 
          +("aprovado",                                                  
      859 +                                                              
          +Decimal("45.00"))                                             
      860 +                                                              
      861 +                                                              
      862  # --- tabela aplicada por centro de custo e política (RN-014, 
           RN-006, RN-016) ---
      863  
      864  
     ...
      1075                                  Decimal("178.80"))
      1076  
      1077  
      1055 -def _caso_cotacao_3_dias_antes(saida):                       
      1056 -    # 16/07 - 3 = 13/07: 10,00 × 5,42 = 54,20                
      1078 +def _caso_cotacao_4_dias_antes(saida):                       
      1079 +    # 17/07 - 4 = 13/07: 10,00 × 5,42 = 54,20                
      1080      (item,) = saida["itens"]
      1081      assert _conversao(item) == ("USD", Decimal("5.42"), "2026
            -07-13",
      1082                                  Decimal("54.20"))
      1083  
     … 39 more lines (ctrl+o to expand)
  ⎿  Updated tests/test_rastreabilidade.py (+0 -4)
      18  TASKS = SPEC.with_name("tasks.md")
      19  
      20  PENDENTES: dict[str, str] = {  # some quando a Fase 6 terminar 
          (DT-016, D-008)
      21 -    "Cotação exatamente 4 dias antes": "T-035",                
      22 -    "Cotação 5 dias antes": "T-035",                           
      23 -    "Terça de Carnaval": "T-035",                              
      24 -    "Descrição nula ou de outro tipo": "T-035",                
      21      "Argumento repetido": "T-036",
      22      "Argumento desconhecido": "T-036",
      23      "Argumento sobrando": "T-036",

⏺ Antes da implementação, os 6 testes de D-4 e terça de Carnaval falham
  corretamente por falta de cotação, enquanto os testes de descricao já passam,
  confirmando a D-008. Agora vou implementar a solução.

⏺ Bash(sed -i '' 's/^DIAS_ANTERIORES_ACEITOS_NA_COTACAO = 3  # RN-015, AMB-024:
      D-1 a D-3/DIAS_ANTERIORES_ACEITOS_NA_COTACAO = 4  # RN-015, AMB-024: D-1 a
      D-4/; s/na a…)
  ⎿  18:DIAS_ANTERIORES_ACEITOS_NA_COTACAO = 4  # RN-015, AMB-024: D-1 a D-
     4
     70:    """Cotação da `moeda` na `data`, ou na anterior mais próxima at
     é D-4 (DT-014)."""
  ⎿  Updated src/reembolso/cambio.py (+2 -2)
      15  from reembolso.modelo import Cambio, Cotacao
      16  from reembolso.politica import MOEDA_BASE, VALOR_ABSOLUTO_MAXIM
          O
      17  
      18 -DIAS_ANTERIORES_ACEITOS_NA_COTACAO = 3  # RN-015, AMB-024: D-1 
         -a D-3                                                          
      18 +DIAS_ANTERIORES_ACEITOS_NA_COTACAO = 4  # RN-015, AMB-024: D-1 
         +a D-4                                                          
      19  
      20  
      21  def _taxa(valor, caminho: str) -> Decimal:
     ...
      67  
      68  
      69  def cotacao(cambio: Cambio, moeda: str, data: date) -> Cotacao 
          | None:
      70 -    """Cotação da `moeda` na `data`, ou na anterior mais próxim
         -a até D-3 (DT-014)."""                                         
      70 +    """Cotação da `moeda` na `data`, ou na anterior mais próxim
         +a até D-4 (DT-014)."""                                         
      71      if moeda == MOEDA_BASE:
      72          return Cotacao(Decimal(1), None)
      73      for dias in range(DIAS_ANTERIORES_ACEITOS_NA_COTACAO + 1):

⏺ Agora o plan.md: seção 4, DT-014 e a nota de que a DT-016 foi reaberta.

⏺ Bash(f=specs/001-motor-reembolso/plan.md && python3 - <<'EOF'
      from pathlib import Path…)
  ⎿  - **Uma única task com toda a v4:** um commit gigante, sem revisão por
      regra.
     … +4 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/plan.md (+6 -6)
      47  | `leitura.py` | **novo.** Forma comum aos três arquivos (seção
           4 da spec, RN-016): bytes → JSON estrito com `Decimal` e `Obje
          toJson` (DT-002, DT-010), `ErroDeArquivo`, verificação de escap
          es e os testes de tipo da DT-003 (`e_numero`, `e_data`, `tem_te
          xto`). Sai de `entrada.py`, sem mudar o comportamento (DT-011) 
          | não |
      48  | `entrada.py` | documento → `Entrada`. Resolve chaves repetida
          s e gera os avisos (RN-013); erros de cabeçalho da RN-002 (incl
          usive `centro_custo` de tipo errado) viram `ErroDeArquivo`; des
          pesa inválida (inclusive `moeda` mal formada) vira `DespesaInva
          lida` (etapa 1 da seção 8). **Não conhece a política:** guarda 
          a categoria como veio, e quem decide se ela é reconhecida é o m
          otor (seção 3) | não |
      49  | `politica.py` | documento → `Politica` (RN-016, parte da polí
          tica); escolha da tabela aplicada (RN-014); limite diário norma
          l e em viagem (RN-009, DT-013); as constantes de interpretação 
          que a spec fixa e o arquivo não traz (seção 4 deste plano) | nã
          o |
      50 -| `cambio.py` | **novo.** Documento → `Cambio` (RN-016, parte d
         -o câmbio); busca da cotação de D a D-3 (RN-015, DT-014) | não |
      50 +| `cambio.py` | **novo.** Documento → `Cambio` (RN-016, parte d
         +o câmbio); busca da cotação de D a D-4 (RN-015, DT-014) | não |
      51  | `normalizacao.py` | `normalizar_texto()` — os passos da seção
           5 da spec | não |
      52  | `dinheiro.py` | **novo.** `contexto_exato()` (DT-012), `arred
          ondar` (RN-003) e `truncar` (RN-009, DT-013): a aritmética de `
          Decimal` usada pelo motor e pela política, sem regra de negócio
           além do modo de arredondamento | não |
      53  | `motor.py` | etapas 2 a 9 da seção 8; recebe `Entrada`, `Poli
          tica` e `Cambio` e devolve `Resultado` | não |
     ...
      148  E em `cambio.py`:
      149  
      150  ```python
      151 -DIAS_ANTERIORES_ACEITOS_NA_COTACAO = 3                        
          -# RN-015, AMB-024: D-1 a D-3                                  
      151 +DIAS_ANTERIORES_ACEITOS_NA_COTACAO = 4                        
          +# RN-015, AMB-024: D-1 a D-4                                  
      152  ```
      153  
      154  **Funções** (todas puras):
     ...
      290  **Alternativa descartada:** `ROUND_FLOOR`: igual para não nega
           tivos, mas esconde a intenção. Escrever 90,00 e 120,00 por ext
           enso, como na 1.2: os valores agora vêm do arquivo.
      291  **Consequência:** 33,33 com 50% dá 49,99, e 60,00 com 50% dá 9
           0,00, iguais à tabela da RN-009. Os testes de limite da 1.x co
           ntinuam valendo com a tabela `padrao` da v4.
      292  
      293 -### DT-014 — Busca da cotação de D a D-3                      
      293 +### DT-014 — Busca da cotação de D a D-4                      
      294  
      295 -**Contexto:** RN-015 e AMB-024: a cotação é a da moeda na data
          - da despesa. Se essa data não tem cotação **dessa moeda**, usa
          --se a data anterior mais próxima que a tenha, até D-3, nunca u
          -ma data posterior. `BRL` tem taxa 1 sem consultar o arquivo.  
      295 +**Contexto:** RN-015 e AMB-024: a cotação é a da moeda na data
          + da despesa. Se essa data não tem cotação **dessa moeda**, usa
          +-se a data anterior mais próxima que a tenha, até D-4, nunca u
          +ma data posterior. `BRL` tem taxa 1 sem consultar o arquivo.  
      296  **Decisão:** `cotacao(cambio, moeda, data)` em `cambio.py`:
      297  - se `moeda == MOEDA_BASE`, devolve `Cotacao(Decimal(1), None)
           `;
      298  - senão, para `dias` de 0 a `DIAS_ANTERIORES_ACEITOS_NA_COTACA
           O`, calcula `d = data - timedelta(days=dias)` e devolve `Cotac
           ao(taxas[d][moeda], d)` na primeira data em que existe `taxas[
           d][moeda]`;
      299 -- devolve `None` se nenhuma das quatro datas tem a moeda;     
      299 +- devolve `None` se nenhuma das cinco datas tem a moeda;      
      300  - se `data - timedelta` sair do calendário (antes de 0001-01-0
           1), para a busca ali: nenhuma data anterior existe.
      301  
      302 -**Alternativa descartada:** ordenar as datas do arquivo e proc
          -urar a anterior mais próxima com busca binária: mais código pa
          -ra o mesmo resultado com, no máximo, 4 consultas a dicionário.
          - E a janela fixa deixa explícito o "até 3 dias".              
      302 +**Alternativa descartada:** ordenar as datas do arquivo e proc
          +urar a anterior mais próxima com busca binária: mais código pa
          +ra o mesmo resultado com, no máximo, 5 consultas a dicionário.
          + E a janela fixa deixa explícito o "até 4 dias".              
      303  **Consequência:** uma data intermediária que só cota outras mo
           edas é pulada naturalmente (caso de borda "Data intermediária 
           sem a moeda"). `data_cotacao` sai de `Cotacao.data.isoformat()
           `, que é igual ao texto do arquivo, porque a chave foi validad
           a como `AAAA-MM-DD` com dígitos ASCII (DT-003).
      304  
      305  ### DT-015 — Validação dos arquivos de política e câmbio

⏺ Update(specs/001-motor-reembolso/plan.md)
  ⎿  Added 2 lines
      344  
      345  **Consequência:** a suíte fica verde em todo commit da Fase 5.
            O dono de cada pendência fica visível no código, e uma pendên
           cia esquecida ou já resolvida quebra a suíte. A tabela de Cobe
           rtura do `tasks.md` é preenchida pela mesma lista.
      346  
      347 +**Reaberta na Fase 6 (D-008):** a spec 2.1 trouxe 7 casos novo
          +s ou renomeados na seção 7. Eles voltam a `PENDENTES`, com don
          +os T-035 e T-036, pelo mesmo mecanismo. A T-036, última da fas
          +e, apaga `PENDENTES` de novo.                                 
      348 +                                                              
      349  ## 6. Estratégia de testes
      350  
      351  - **Nível e proporção:**

  Ran 1 shell command (ctrl+o to expand)

⏺ Suíte verde (1013 testes), ruff limpo, test_exemplo.py sem alteração. É task
  de regra, então chamo o revisor independente só com o ID.

⏺ revisor-de-task(Revisão independente T-035)  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ A implementação da T-035 está pronta e o revisor independente
  (revisor-de-task) está rodando. Quando ele terminar, salvo o relatório em
  docs/reviews/T-035.md e te mostro o resumo completo para aprovar o commit.

✻ Sautéed for 57s · done 7:21 PM

› Message from revisor-de-task
  # Revisão T-035 — Janela da cotação D-1 a D-4 e `descricao` de qualquer tipo

  - **Data:** 2026-10-04
  - **Regras conferidas:** RN-015, AMB-024, RN-002 (`descricao`), D-008 (pontos
  2, 3, R2-3, R2-4); DT-014 e DT-016 do plan
  - **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 1013 passed, 0
  failed (evidência, não veredito)

  ### Resultado
  **APROVADO COM RESSALVAS** — todos os critérios de aceite estão atendidos e os
  esperados conferem com a spec recalculada à mão. Ficam duas pendências de
  rastreabilidade e documentação, ambas BAIXA.

  ### Critérios de aceite
  | # | Critério | Status | Evidência |
  |---|---|---|---|
  | 1 | Câmbio só com 13/07: USD em 17/07 usa 13/07 (D-4) | atendido |
  `tests/test_rn015_moeda_e_cambio.py::test_rn015_cotacao_ate_4_dias_antes`,
  `::test_rn015_cotacao_d4_e_d5_no_motor` (10,00 × 5,42 = 54,20 confere) |
  | 2 | USD em 18/07 → `cambio_indisponivel` (D-5) | atendido |
  `::test_rn015_cotacao_5_dias_antes_nao_serve`,
  `::test_rn015_cotacao_d4_e_d5_no_motor` |
  | 3 | Câmbio só com 05/02/2027 (EUR 6,00), 10,00 EUR em 09/02/2027 →
  `data_cotacao` 2027-02-05, `valor_considerado` 60,00 | atendido |
  `::test_rn015_terca_de_carnaval_usa_a_sexta`,
  `::test_rn015_terca_de_carnaval_no_motor`. Conferi o calendário: 05/02/2027 é
  sexta e 09/02/2027 é a terça de Carnaval (Páscoa em 28/03/2027 − 47 dias). O
  período usado é fevereiro de 2027, como pede a seção 7. |
  | 4 | Testes de D-3/D-4 da 2.0 passam a D-4/D-5 | atendido | diff de
  `test_rn015_moeda_e_cambio.py`: os testes foram renomeados e as datas
  deslocadas em +1. A docstring de
  `test_rn015_usd_sem_cotacao_nos_4_dias_anteriores` agora cita de 08/07 a
  12/07, como no aceite da RN-015. |
  | 5 | `descricao` ausente, `null`, `17`, `true`, `[]` e `{}` → a despesa segue
  normalmente | atendido | `tests/test_rn002_validacao_da_entrada.py::test_rn00
  2_descricao_de_qualquer_tipo_nao_invalida` compara cada caso com a mesma
  despesa sem `descricao`, que cobre o "ausente".
  `::test_rn002_descricao_de_outro_tipo_segue_no_motor` cobre o motor: 45,00 sem
  nota fica `aprovado` com 45,00. |
  | 6 | `"descricao": "Almoço \uD800"` → erro de arquivo | atendido |
  `::test_rn002_descricao_com_surrogate_isolado_e_erro_de_arquivo`
  (`ErroDeArquivo` em `ler_entrada`) |
  | 7 | Nenhum valor da seção 9 muda (`test_exemplo.py` sem alteração) |
  atendido | `git diff` não toca `tests/test_exemplo.py`, e a suíte passa |
  | 8 | Constante de 3 para 4 em `cambio.py` | atendido |
  `src/reembolso/cambio.py:18` `DIAS_ANTERIORES_ACEITOS_NA_COTACAO = 4`; o laço
  `range(N + 1)` consulta de D a D-4 |
  | 9 | `plan.md` com "D-4" na seção 4, na DT-014 e na DT-016 reaberta |
  atendido | diff do `plan.md`: tabela de módulos, bloco da seção 4 e DT-014
  ("cinco datas", "5 consultas") atualizados; a DT-016 ganhou o parágrafo
  "Reaberta na Fase 6 (D-008)" |
  | 10 | Casos de borda: "Cotação exatamente 4 dias antes", "Cotação 5 dias
  antes", "Terça de Carnaval", "Descrição nula ou de outro tipo"; os `id`
  antigos saem | atendido | `tests/test_casos_de_borda.py`: os ids antigos foram
  renomeados; "Terça de Carnaval" está em `CASOS_DE_CAMBIO` e também verifica
  `aprovado` com 60,00 (60,00 ≤ 60,00 da alimentação na tabela `padrao`).
  "Descrição nula ou de outro tipo" está em
  `test_caso_de_borda_com_varios_arquivos` com `null`, `17` e `{}`, uma entrada
  por vez. As 4 pendências da T-035 saíram de `PENDENTES` em
  `tests/test_rastreabilidade.py`. |

  ### Problemas encontrados
  #### 1. Cabeçalho do `plan.md` continua em "Versão 2.0 · Baseado na spec 2.0"
  — severidade BAIXA
  - **Regra afetada:** nenhuma regra de negócio. É uma inconsistência entre
  documentos.
  - **Evidência:** `specs/001-motor-reembolso/tasks.md:3` diz "plan 2.0 (a T-035
  leva o plan a 2.1)". O `specs/001-motor-reembolso/plan.md:3` continua com
  `**Versão:** 2.0 · **Baseado na spec:** 2.0 (Política v4, D-007)`, embora o
  conteúdo já reflita a spec 2.1 (D-4, D-008).
  - **Impacto:** nenhum no resultado. A versão declarada do plan não bate com o
  `tasks.md` nem com o conteúdo do próprio plan.
  - **Recomendação:** subir o cabeçalho do plan para 2.1, baseado na spec 2.1 e
  na D-008, como o `tasks.md` anuncia.

  #### 2. Aviso de chave repetida dentro da `descricao` (RN-013) sem teste —
  severidade BAIXA
  - **Regra afetada:** RN-002 / RN-013 (D-008 R2-3)
  - **Evidência:** `spec.md:183`: "e ao aviso de chave repetida (RN-013: `{"x":
  1, "x": 2}` gera o aviso de `descricao.x`)". Nenhum teste em `tests/` usa
  `descricao` com chave repetida.
  - **Impacto:** se o tratamento de objetos aninhados ignorasse a `descricao`,
  nenhum teste perceberia. O critério não está no `Aceite:` da T-035; a D-008
  diz que o R2-3 não muda código.
  - **Recomendação:** acrescentar um teste em que `"descricao": {"x": 1, "x":
  2}` gera o aviso `descricao.x` e a despesa segue. Pode ficar nesta task ou em
  outra; é escolha de quem conduz.

  ### Cobertura
  - **Regras testadas:**
    - RN-015 / AMB-024 (janela D-4) → `test_rn015_cotacao_ate_4_dias_antes`,
  `test_rn015_cotacao_5_dias_antes_nao_serve`,
  `test_rn015_terca_de_carnaval_usa_a_sexta`,
  `test_rn015_cotacao_d4_e_d5_no_motor`,
  `test_rn015_terca_de_carnaval_no_motor`,
  `test_rn015_usd_sem_cotacao_nos_4_dias_anteriores`,
  `test_rn015_busca_no_inicio_do_calendario_nao_falha`, mais os casos de borda.
    - RN-002 (`descricao`) →
  `test_rn002_descricao_de_qualquer_tipo_nao_invalida`,
  `test_rn002_descricao_com_surrogate_isolado_e_erro_de_arquivo`,
  `test_rn002_descricao_de_outro_tipo_segue_no_motor`, mais o caso de borda.
  - **Casos de borda cobertos:**
    - fronteira exata D-4 (incluída) e D-5 (excluída);
    - D-1 a D-3 sem cotação até chegar a D-4 (Carnaval);
    - início do calendário (0001-01-02);
    - cotação posterior nunca usada (teste existente);
    - data intermediária que só cota outra moeda (caso existente);
    - `descricao` nula, número, booleano, lista, objeto, texto e ausente;
    - surrogate isolado na `descricao`.
  - **Casos que parecem faltar:** aviso de chave repetida dentro de `descricao`
  (`spec.md:183`, RN-013), descrito no problema 2.

  ### Decisões necessárias
  Nenhuma.

  ### Antes de concluir a task
  Nada bloqueia o commit. Recomendado, mas não obrigatório:
  1. Subir o cabeçalho de
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/plan.md` para
  2.1, baseado na spec 2.1 (problema 1).
  2. Opcionalmente, acrescentar o teste do aviso `descricao.x` (problema 2).

⏺ Resultado do revisor: APROVADO COM RESSALVAS, as duas de severidade BAIXA.
  Salvo o relatório sem edição e corrijo as duas, que cabem no escopo da task: o
  tasks.md diz que a T-035 leva o plan a 2.1, e a descricao da RN-002 está no
  Atende:.

⏺ Bash(cat > docs/reviews/T-035.md <<'EOF'
      # Revisão T-035 — Janela da cotação D-1 a D-4 e `descricao` de qualquer
      tipo…)
  ⎿  # Plano Técnico — Motor de Cálculo de Reembolso

     **Versão:** 2.0 · **Baseado na spec:** 2.0 (Política v4, D-007)
     … +61 lines (ctrl+o to expand)
  ⎿  Created docs/reviews/T-035.md (+57 -0)
       1 +# Revisão T-035 — Janela da cotação D-1 a D-4 e `descricao` de 
         +qualquer tipo                                                  
       2 +                                                               
       3 +- **Data:** 2026-10-04                                         
       4 +- **Regras conferidas:** RN-015, AMB-024, RN-002 (`descricao`),
         + D-008 (pontos 2, 3, R2-3, R2-4); DT-014 e DT-016 do plan      
       5 +- **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 
         +1013 passed, 0 failed (evidência, não veredito)                
       6 +                                                               
       7 +### Resultado                                                  
       8 +**APROVADO COM RESSALVAS** — todos os critérios de aceite estão
         + atendidos e os esperados conferem com a spec recalculada à mão
         +. Ficam duas pendências de rastreabilidade e documentação, amba
         +s BAIXA.                                                       
       9 +                                                               
      10 +### Critérios de aceite                                        
      11 +| # | Critério | Status | Evidência |                          
      12 +|---|---|---|---|                                              
      13 +| 1 | Câmbio só com 13/07: USD em 17/07 usa 13/07 (D-4) | atend
         +ido | `tests/test_rn015_moeda_e_cambio.py::test_rn015_cotacao_a
         +te_4_dias_antes`, `::test_rn015_cotacao_d4_e_d5_no_motor` (10,0
         +0 × 5,42 = 54,20 confere) |                                    
      14 +| 2 | USD em 18/07 → `cambio_indisponivel` (D-5) | atendido | `
         +::test_rn015_cotacao_5_dias_antes_nao_serve`, `::test_rn015_cot
         +acao_d4_e_d5_no_motor` |                                       
      15 +| 3 | Câmbio só com 05/02/2027 (EUR 6,00), 10,00 EUR em 09/02/2
         +027 → `data_cotacao` 2027-02-05, `valor_considerado` 60,00 | at
         +endido | `::test_rn015_terca_de_carnaval_usa_a_sexta`, `::test_
         +rn015_terca_de_carnaval_no_motor`. Conferi o calendário: 05/02/
         +2027 é sexta e 09/02/2027 é a terça de Carnaval (Páscoa em 28/0
         +3/2027 − 47 dias). O período usado é fevereiro de 2027, como pe
         +de a seção 7. |                                                
      16 +| 4 | Testes de D-3/D-4 da 2.0 passam a D-4/D-5 | atendido | di
         +ff de `test_rn015_moeda_e_cambio.py`: os testes foram renomeado
         +s e as datas deslocadas em +1. A docstring de `test_rn015_usd_s
         +em_cotacao_nos_4_dias_anteriores` agora cita de 08/07 a 12/07, 
         +como no aceite da RN-015. |                                    
      17 +| 5 | `descricao` ausente, `null`, `17`, `true`, `[]` e `{}` → 
         +a despesa segue normalmente | atendido | `tests/test_rn002_vali
         +dacao_da_entrada.py::test_rn002_descricao_de_qualquer_tipo_nao_
         +invalida` compara cada caso com a mesma despesa sem `descricao`
         +, que cobre o "ausente". `::test_rn002_descricao_de_outro_tipo_
         +segue_no_motor` cobre o motor: 45,00 sem nota fica `aprovado` c
         +om 45,00. |                                                    
      18 +| 6 | `"descricao": "Almoço \uD800"` → erro de arquivo | atendi
         +do | `::test_rn002_descricao_com_surrogate_isolado_e_erro_de_ar
         +quivo` (`ErroDeArquivo` em `ler_entrada`) |                    
      19 +| 7 | Nenhum valor da seção 9 muda (`test_exemplo.py` sem alter
         +ação) | atendido | `git diff` não toca `tests/test_exemplo.py`,
         + e a suíte passa |                                             
      20 +| 8 | Constante de 3 para 4 em `cambio.py` | atendido | `src/re
         +embolso/cambio.py:18` `DIAS_ANTERIORES_ACEITOS_NA_COTACAO = 4`;
         + o laço `range(N + 1)` consulta de D a D-4 |                   
      21 +| 9 | `plan.md` com "D-4" na seção 4, na DT-014 e na DT-016 rea
         +berta | atendido | diff do `plan.md`: tabela de módulos, bloco 
         +da seção 4 e DT-014 ("cinco datas", "5 consultas") atualizados;
         + a DT-016 ganhou o parágrafo "Reaberta na Fase 6 (D-008)" |    
      22 +| 10 | Casos de borda: "Cotação exatamente 4 dias antes", "Cota
         +ção 5 dias antes", "Terça de Carnaval", "Descrição nula ou de o
         +utro tipo"; os `id` antigos saem | atendido | `tests/test_casos
         +_de_borda.py`: os ids antigos foram renomeados; "Terça de Carna
         +val" está em `CASOS_DE_CAMBIO` e também verifica `aprovado` com
         + 60,00 (60,00 ≤ 60,00 da alimentação na tabela `padrao`). "Desc
         +rição nula ou de outro tipo" está em `test_caso_de_borda_com_va
         +rios_arquivos` com `null`, `17` e `{}`, uma entrada por vez. As
         + 4 pendências da T-035 saíram de `PENDENTES` em `tests/test_ras
         +treabilidade.py`. |                                            
      23 +                                                               
      24 +### Problemas encontrados                                      
      25 +#### 1. Cabeçalho do `plan.md` continua em "Versão 2.0 · Basead
         +o na spec 2.0" — severidade BAIXA                              
      26 +- **Regra afetada:** nenhuma regra de negócio. É uma inconsistê
         +ncia entre documentos.                                         
      27 +- **Evidência:** `specs/001-motor-reembolso/tasks.md:3` diz "pl
         +an 2.0 (a T-035 leva o plan a 2.1)". O `specs/001-motor-reembol
         +so/plan.md:3` continua com `**Versão:** 2.0 · **Baseado na spec
         +:** 2.0 (Política v4, D-007)`, embora o conteúdo já reflita a s
         +pec 2.1 (D-4, D-008).                                          
      28 +- **Impacto:** nenhum no resultado. A versão declarada do plan 
         +não bate com o `tasks.md` nem com o conteúdo do próprio plan.  
      29 +- **Recomendação:** subir o cabeçalho do plan para 2.1, baseado
         + na spec 2.1 e na D-008, como o `tasks.md` anuncia.            
      30 +                                                               
      31 +#### 2. Aviso de chave repetida dentro da `descricao` (RN-013) 
         +sem teste — severidade BAIXA                                   
      32 +- **Regra afetada:** RN-002 / RN-013 (D-008 R2-3)              
      33 +- **Evidência:** `spec.md:183`: "e ao aviso de chave repetida (
         +RN-013: `{"x": 1, "x": 2}` gera o aviso de `descricao.x`)". Nen
         +hum teste em `tests/` usa `descricao` com chave repetida.      
      34 +- **Impacto:** se o tratamento de objetos aninhados ignorasse a
         + `descricao`, nenhum teste perceberia. O critério não está no `
         +Aceite:` da T-035; a D-008 diz que o R2-3 não muda código.     
      35 +- **Recomendação:** acrescentar um teste em que `"descricao": {
         +"x": 1, "x": 2}` gera o aviso `descricao.x` e a despesa segue. 
         +Pode ficar nesta task ou em outra; é escolha de quem conduz.   
      36 +                                                               
      37 +### Cobertura                                                  
      38 +- **Regras testadas:**                                         
      39 +  - RN-015 / AMB-024 (janela D-4) → `test_rn015_cotacao_ate_4_d
         +ias_antes`, `test_rn015_cotacao_5_dias_antes_nao_serve`, `test_
         +rn015_terca_de_carnaval_usa_a_sexta`, `test_rn015_cotacao_d4_e_
         +d5_no_motor`, `test_rn015_terca_de_carnaval_no_motor`, `test_rn
         +015_usd_sem_cotacao_nos_4_dias_anteriores`, `test_rn015_busca_n
         +o_inicio_do_calendario_nao_falha`, mais os casos de borda.     
      40 +  - RN-002 (`descricao`) → `test_rn002_descricao_de_qualquer_ti
         +po_nao_invalida`, `test_rn002_descricao_com_surrogate_isolado_e
         +_erro_de_arquivo`, `test_rn002_descricao_de_outro_tipo_segue_no
         +_motor`, mais o caso de borda.                                 
     … 17 more lines (ctrl+o to expand)

⏺ Agent "Revisão independente T-035" finished · 59s

⏺ Relatório salvo. Agora corrijo as duas ressalvas: o cabeçalho do plan e o
  teste do aviso descricao.x.

  Ran 1 shell command (ctrl+o to expand)

⏺ Update(tests/test_rn002_validacao_da_entrada.py)
  ⎿  Added 13 lines
      719          ler_entrada(texto.encode())
      720  
      721  
      722 +def test_rn002_descricao_com_chave_repetida_gera_aviso_e_segue
          +(entrada, despesa):                                           
      723 +    """RN-002 / RN-013 / D-008: `"descricao": {"x": 1, "x": 2}
          +` → aviso de                                                  
      724 +    `descricao.x`, e a despesa segue válida."""               
      725 +    texto = simplejson.dumps(                                 
      726 +        entrada(despesas=[despesa(descricao="DESCRICAO")]), us
          +e_decimal=True,                                               
      727 +    ).replace('"DESCRICAO"', '{"x": 1, "x": 2}')              
      728 +    (resultado,) = ler_entrada(texto.encode()).despesas       
      729 +    assert isinstance(resultado, Despesa)                     
      730 +    assert resultado.avisos == (                              
      731 +        "chave repetida: descricao.x (2 ocorrências; valeu a ú
          +ltima)",                                                      
      732 +    )                                                         
      733 +                                                              
      734 +                                                              
      735  @pytest.mark.parametrize("descricao", [None, 17, True, [], {}]
           )
      736  def test_rn002_descricao_de_outro_tipo_segue_no_motor(avaliar,
            despesa, descricao):
      737      """RN-002 / D-008: alimentação 45,00 sem nota com `descric
           ao` não textual →

⏺ Bash(python3 - <<'EOF'
      from pathlib import Path…)
  ⎿  ......
        [100%]
     1014 passed in 0.73s
     … +8 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/plan.md (+3 -1)
      1  # Plano Técnico — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 2.0 · **Baseado na spec:** 2.0 (Política v4, D-007) 
      3 +**Versão:** 2.1 · **Baseado na spec:** 2.1 (Política v4, D-007; 
        +revisão adversarial, D-008)                                     
      4  
      5  > Aqui mora o COMO. Este arquivo pode e deve falar de linguagem,
          biblioteca e
      6  > arquitetura. O que ele **não** pode é introduzir regra de negó
         cio nova — se
     ...
      15  
      16  Ficam iguais a stack, a gravação atômica e a serialização deter
          minística. As decisões novas são DT-011 a DT-016. DT-001, DT-00
          2, DT-005, DT-007 e DT-009 foram atualizadas.
      17  
      18 +**O que mudou da 2.0 para a 2.1** (spec 2.1, D-008): a busca da
         + cotação vai até D-4 (`DIAS_ANTERIORES_ACEITOS_NA_COTACAO`, seç
         +ão 4 e DT-014), e a DT-016 foi reaberta para a Fase 6.         
      19 +                                                               
      20  ---
      21  
      22  ## 1. Stack

⏺ Resumo — T-035: Janela da cotação D-1 a D-4 e descricao de qualquer tipo

  A T-035 está implementada e testada, mas ainda sem commit: falta a sua
  autorização.

  Arquivos alterados:
  - src/reembolso/cambio.py (modificado): DIAS_ANTERIORES_ACEITOS_NA_COTACAO
    passou de 3 para 4; a docstring de cotacao agora diz D-4.
  - specs/001-motor-reembolso/plan.md (modificado):
    - a tabela de módulos, a seção 4 e a DT-014 dizem D-4 ("cinco datas", "5
      consultas");
    - a DT-016 ganhou o parágrafo "Reaberta na Fase 6 (D-008)";
    - o cabeçalho subiu para a versão 2.1, baseada na spec 2.1, com o bloco "O
      que mudou da 2.0 para a 2.1".
  - tests/test_rn015_moeda_e_cambio.py,
    tests/test_rn002_validacao_da_entrada.py, tests/test_casos_de_borda.py,
    tests/test_rastreabilidade.py (modificados).
  - docs/reviews/T-035.md (novo).

  Testes criados/alterados:
  - RN-015 / AMB-024:
    - test_rn015_cotacao_ate_4_dias_antes e
      test_rn015_cotacao_5_dias_antes_nao_serve substituem os testes de D-3/D-4.
    - test_rn015_terca_de_carnaval_usa_a_sexta e
      test_rn015_terca_de_carnaval_no_motor: 10,00 × 6,00 = 60,00, aprovado.
    - test_rn015_cotacao_d4_e_d5_no_motor (antes d3_e_d4).
    - test_rn015_usd_sem_cotacao_nos_4_dias_anteriores: só o nome e a docstring
      mudaram, agora "de 08/07 a 12/07".
    - A docstring de test_rn015_busca_no_inicio_do_calendario_nao_falha foi
      ajustada.
  - RN-002 (descricao):
    - test_rn002_descricao_de_qualquer_tipo_nao_invalida: null, 17, true, [], {}
      e texto dão o mesmo resultado que a despesa sem descricao.
    - test_rn002_descricao_com_surrogate_isolado_e_erro_de_arquivo.
    - test_rn002_descricao_de_outro_tipo_segue_no_motor: 45,00 sem nota fica
      aprovado.
    - test_rn002_descricao_com_chave_repetida_gera_aviso_e_segue: cobre a RN-013
      e veio de uma ressalva do revisor.
  - Seção 7:
    - "Cotação exatamente 4 dias antes", "Cotação 5 dias antes" e "Terça de
      Carnaval" entram em CASOS_DE_CAMBIO.
    - "Descrição nula ou de outro tipo" ficou num teste novo,
      test_caso_de_borda_com_varios_arquivos, porque o caso pede um arquivo por
      entrada.
    - As 4 pendências da T-035 saíram de PENDENTES.

  Testes executados antes da implementação:
  - Os 6 testes de D-4 e de Carnaval falharam pelo motivo certo: a taxa saía
    nula porque a janela ia só até D-3.
  - Os testes de descricao já passavam. Era esperado: segundo a D-008, o ponto 3
    só registra a leitura que o código já seguia.

  Testes executados depois: uv run pytest -q e uv run ruff check .
  pytest: 1014 passed. test_exemplo.py não foi alterado, então nenhum valor da
  seção 9 mudou.
  ruff: limpo.

  Revisão independente: APROVADO COM RESSALVAS, com dois problemas de severidade
  BAIXA, já corrigidos:
  1. O cabeçalho do plan continuava 2.0.
  2. Faltava o teste do aviso descricao.x.

  Não houve decisões necessárias. O relatório está em docs/reviews/T-035.md.

  Decisões ou interpretações realizadas:
  - No plan.md, o "DT-016 reaberto" da task virou um parágrafo novo no fim da
    DT-016. O texto antigo da Fase 5 não mudou.

  Lacunas ou dúvidas: nenhuma. As 3 pendências de CLI continuam com a T-036.

  Commit proposto: feat(T-035): janela da cotação até D-4 e descricao de 
  qualquer tipo

  Posso commitar?

✻ Worked for 2m 49s · done 7:23 PM

※ recap: Estamos na T-035, que leva a janela da cotação a D-4 e aceita `descricao` de qualquer tipo; ela está pronta, com 1014 testes passando e o revisor aprovando com ressalvas, já corrigidas. Falta você autorizar o commit. (disable recaps in /config)

❯ pode commitar                                                                 

  Ran 1 shell command (ctrl+o to expand)

⏺ Bash(f=specs/001-motor-reembolso/tasks.md && sed -i '' 's/^- \[ \]
      \*\*T-035\*\*/- [x] **T-035**/' $f && awk '/\*\*T-035\*\*/{p=1}
      p&&/Commit|^- \[/{print NR": "$0}…)
  ⎿  404: - [x] **T-035** — Janela da cotação D-1 a D-4 e `descricao` de qu
     alquer tipo: `DIAS_ANTERIORES_ACEITOS_NA_COTACAO` de 3 para 4 em `camb
     io.py`; `plan.md` (seção 4, DT-014, DT-016 reaberto) com "D-4"; testes
     … +7 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+1 -1)
      401  
      402  Tasks das decisões da D-008 que mudam código ou exigem teste n
           ovo. Os demais pontos da D-008 só mudaram texto da spec. Os 7 
           casos novos ou renomeados da seção 7 ficam em `PENDENTES` de `
           tests/test_rastreabilidade.py` (DT-016, reaberto para esta fas
           e, donos T-035 e T-036). Cada task tira as suas pendências no 
           mesmo commit, e a última apaga o `PENDENTES` de novo.
      403  
      404 -- [ ] **T-035** — Janela da cotação D-1 a D-4 e `descricao` de
          - qualquer tipo: `DIAS_ANTERIORES_ACEITOS_NA_COTACAO` de 3 para
          - 4 em `cambio.py`; `plan.md` (seção 4, DT-014, DT-016 reaberto
          -) com "D-4"; testes da janela e da `descricao`.               
      404 +- [x] **T-035** — Janela da cotação D-1 a D-4 e `descricao` de
          + qualquer tipo: `DIAS_ANTERIORES_ACEITOS_NA_COTACAO` de 3 para
          + 4 em `cambio.py`; `plan.md` (seção 4, DT-014, DT-016 reaberto
          +) com "D-4"; testes da janela e da `descricao`.               
      405    - **Tipo:** regra
      406    - **Atende:** RN-015, AMB-024, RN-002 (`descricao`), D-008 (
           pontos 2 e 3)
      407    - **Depende de:** T-034

  Ran 1 shell command (ctrl+o to expand)

⏺ Bash(f=specs/001-motor-reembolso/tasks.md && python3 - <<'EOF'
      from pathlib import Path…)
  ⎿   specs/001-motor-reembolso/tasks.md | 5 +++--
      1 file changed, 3 insertions(+), 2 deletions(-)
     53-revisao-adversarial-spec-final.md
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+2 -1)
      1  # Tasks — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 2.1 · **Baseado em:** spec 2.1, plan 2.0 (a T-035 le
        -va o plan a 2.1)                                                
      3 +**Versão:** 2.1 · **Baseado em:** spec 2.1, plan 2.1            
      4  
      5  > Cada task é pequena o bastante para virar **um commit**. Se vo
         cê não consegue
      6  > descrever o critério de aceite como "o teste X passa", a task 
         está grande demais.
     ...
      410      - `tests/test_rn002_validacao_da_entrada.py`: `descricao` 
           ausente, `null`, `17`, `true`, `[]` e `{}` → a despesa segue n
           ormalmente; `"descricao": "Almoço \uD800"` → erro de arquivo.
      411      - Nenhum valor da seção 9 muda (`test_exemplo.py` passa se
           m alteração).
      412    - **Casos de borda:** Cotação exatamente 4 dias antes · Cota
           ção 5 dias antes · Terça de Carnaval · Descrição nula ou de ou
           tro tipo (substituem "Cotação exatamente 3 dias antes" e "Cota
           ção 4 dias antes", cujos `id` saem de `test_casos_de_borda.py`
           )
      413 +  - **Commit:** 436d6c7                                       
      414  
      415  - [ ] **T-036** — CLI: argumento repetido e prefixo abreviado 
           são erro de uso; fim das pendências da Fase 6. `cli.py` com `a
           llow_abbrev=False` e recusa da segunda ocorrência de `--input`
           , `--politica`, `--cambio` ou `--output`, inclusive na forma `
           --opção=valor`; `PENDENTES` e o código que o lê apagados de `t
           est_rastreabilidade.py`; tabela de Cobertura com 105 casos.
      416    - **Tipo:** estrutura

⏺ O commit 436d6c7 da T-035 entrou; o hook rodou ruff e pytest (1014 testes
  passando).

  No tasks.md, marquei a T-035 como [x], preenchi o hash e mudei o cabeçalho
  para "plan 2.1", já que o plan agora está nessa versão.

  Para fechar o bloco, falta o export da sessão. Rode:

  /export docs/sessions/54-t035-janela-d4-e-descricao.md

  Quando confirmar, faço um único commit docs(tasks): conclui T-035 com o
  tasks.md e o export. A T-036 só começa quando você pedir.

✻ Crunched for 20s · done 7:42 PM