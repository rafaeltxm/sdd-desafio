 ▐▛███▛█   Claude Code v2.1.287
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~/repo/sdd-desafio

  Get to finished work sooner with Opus 5.5. Switch anytime with /model.

❯ /clear                                                                        

❯ pode fazer a proxima task                                                     

⏺ Skill(task)
  ⎿  Successfully loaded skill

  Searched for 1 pattern, ran 1 shell command (ctrl+o to expand)

⏺ Próxima task: T-031 — Conversão de moeda (dependências T-024, T-026, T-030
  concluídas). Vou ler a spec.

  Read 2 files, listed 1 directory, ran 2 shell commands (ctrl+o to expand)

⏺ Agora o código atual.

  Searched for 2 patterns, read 2 files, ran 2 shell commands (ctrl+o to expand)

⏺ Lendo a T-031 e os testes existentes; em seguida escrevo os testes de
  conversão de moeda antes da implementação.

  Ran 4 shell commands (ctrl+o to expand)

⏺ Contexto lido. Começo pelos testes: conftest.avaliar ganha cambio, depois os
  testes por regra.

⏺ Bash(python3 - <<'EOF'
      p='tests/conftest.py'…)
  ⎿  170:def avaliar(*despesas, politica=None, cambio=None, **cabecalho) ->
      dict:
  ⎿  Updated tests/conftest.py (+4 -3)
      167      )
      168  
      169  
      170 -def avaliar(*despesas, politica=None, **cabecalho) -> dict:   
      170 +def avaliar(*despesas, politica=None, cambio=None, **cabecalho
          +) -> dict:                                                    
      171      """Despesas (dicionários) numa entrada mínima válida → saí
           da de `processar`.
      172  
      173 -    `politica` é um documento (`construir_politica`); sem ela,
          - a v4 transcrita.                                             
      173 +    `politica` e `cambio` são documentos (`construir_politica`
          +,                                                             
      174 +    `construir_cambio`); sem eles, a v4 e o câmbio do envelope
          + transcritos.                                                 
      175      """
      176      documento = construir_entrada(despesas, **cabecalho)
      176 -    return processar(simplejson.dumps(documento, use_decimal=T
          -rue), politica)                                               
      177 +    return processar(simplejson.dumps(documento, use_decimal=T
          +rue), politica, cambio)                                       
      178  
      179  
      180  @pytest.fixture(name="processar")

⏺ Bash(python3 - <<'EOF'
      p='tests/test_rn015_moeda_e_cambio.py'…)
  ⎿  Updated tests/test_rn015_moeda_e_cambio.py (+198 -2)
      1 -"""Busca da cotação: RN-015, AMB-024, AMB-025, DT-014.          
      1 +"""Moeda e conversão: RN-015, AMB-024, AMB-025, DT-014; etapa 2 
        +da seção 8.                                                     
      2  
      3  Salvo indicação, o câmbio é o `cambio.json` do envelope (`constr
         uir_cambio`),
      4 -com cotações de USD e EUR só em dias úteis, de 13/07 (segunda) a
        - 28/07.                                                         
      4 +com cotações de USD e EUR só em dias úteis, de 13/07 (segunda) a
        + 28/07, e a                                                     
      5 +política é a v4 com a tabela `padrao` (alimentação 60,00).      
      6  """
      7  
      8  from datetime import date
     ...
       99          Decimal("5.42"), date(1, 1, 1)
      100      )
      101      assert cotacao(cambio, "EUR", date(1, 1, 2)) is None
      102 +                                                              
      103 +                                                              
      104 +# --- ponta a ponta: etapa 2 da seção 8 (motor) ---           
      105 +                                                              
      106 +                                                              
      107 +def _conversao(item):                                         
      108 +    return (                                                  
      109 +        item["moeda"], item["taxa_cambio"], item["data_cotacao
          +"],                                                           
      110 +        item["valor_considerado"],                            
      111 +    )                                                         
      112 +                                                              
      113 +                                                              
      114 +def _recusado_cambio_indisponivel(item):                      
      115 +    # RN-015: recusado na etapa 2; sem valor em reais nem taxa
          + (seção 4)                                                    
      116 +    assert (item["status"], item["motivo"]) == ("recusado", "c
          +ambio_indisponivel")                                          
      117 +    assert item["valor_reembolsado"] == 0                     
      118 +    for campo in (                                            
      119 +        "valor_considerado", "taxa_cambio", "data_cotacao", "e
          +m_viagem",                                                    
      120 +        "limite_diario",                                      
      121 +    ):                                                        
      122 +        assert item[campo] is None, campo                     
      123 +                                                              
      124 +                                                              
      125 +def test_rn015_eur_na_propria_data_convertido(avaliar, despesa
          +):                                                            
      126 +    """RN-015 (aceite): 22,00 EUR em 14/07 → taxa 5,93, `data_
          +cotacao`                                                      
      127 +    2026-07-14, `valor_considerado` 130,46."""                
      128 +    (item,) = avaliar(                                        
     … 168 more lines (ctrl+o to expand)

  Searched for 1 pattern (ctrl+o to expand)

⏺ Bash(cat >> tests/test_rn003_arredondamento.py <<'EOF'…)
  ⎿  def _resumo(item):
         return (item["valor_reembolsado"], item["status"], item["motivo"])
     … +3 lines (ctrl+o to expand)
  ⎿  Updated tests/test_rn003_arredondamento.py (+42 -0)
      45      assert item["valor_considerado"] == Decimal("60.01")
      46      assert item["valor_reembolsado"] == Decimal("60.00")
      47      assert item["status"] == "parcial"
      48 +                                                               
      49 +                                                               
      50 +@pytest.mark.parametrize(                                      
      51 +    ("valor", "considerado"),                                  
      52 +    [                                                          
      53 +        # RN-003 Aceite: 16,8649 × 5,93 = 100,008857 → 100,01  
      54 +        # (arredondar antes daria 16,86 × 5,93 = 99,98)        
      55 +        (Decimal("16.8649"), Decimal("100.01")),               
      56 +        # RN-003 Aceite: 0,001 × 5,93 = 0,00593 → 0,01         
      57 +        (Decimal("0.001"), Decimal("0.01")),                   
      58 +    ],                                                         
      59 +)                                                              
      60 +def test_rn003_conversao_arredondada_uma_vez_em_reais(         
      61 +    avaliar, despesa, valor, considerado                       
      62 +):                                                             
      63 +    """RN-003 / AMB-026: o valor exato em EUR é multiplicado pe
         +la taxa (5,93 em                                               
      64 +    14/07) e o produto é arredondado uma única vez, em reais.""
         +"                                                              
      65 +    (item,) = avaliar(                                         
      66 +        despesa(data="2026-07-14", valor=valor, moeda="EUR")   
      67 +    )["itens"]                                                 
      68 +                                                               
      69 +    assert item["valor_considerado"] == considerado            
      70 +    assert item["valor_informado"] == valor                    
      71 +                                                               
      72 +                                                               
      73 +def test_rn003_produto_com_mais_de_28_digitos_e_exato(avaliar, 
         +despesa, ):                                                    
      74 +    """RN-003 / DT-012: o produto é exato, sem a precisão padrã
         +o de 28 dígitos.                                               
      75 +                                                               
      76 +    Câmbio com USD 2 em 14/07; 50,00249999999999999999999999999
         +9 USD sem nota."""                                             
      77 +    from conftest import construir_cambio                      
      78 +                                                               
      79 +    cambio = construir_cambio(taxas={"2026-07-14": {"USD": Deci
         +mal("2")}})                                                    
      80 +    (item,) = avaliar(                                         
      81 +        despesa(data="2026-07-14", valor=Decimal("50.0024999999
         +99999999999999999999"),                                        
      82 +                moeda="USD", tem_nota_fiscal=False),           
      83 +        cambio=cambio,                                         
      84 +    )["itens"]                                                 
     … 5 more lines (ctrl+o to expand)
  ⎿  Updated tests/test_rn004_valor_positivo.py (+27 -0)
      112  
      113      assert item["valor_considerado"] == Decimal("0.01")
      114      assert (item["status"], item["valor_reembolsado"]) == ("ap
           rovado", Decimal("0.01"))
      115 +                                                              
      116 +                                                              
      117 +def test_rn004_valor_estrangeiro_minusculo_nao_e_invalido(aval
          +iar, despesa):                                                
      118 +    """RN-004 / AMB-026 (aceite): 0,001 EUR com taxa 5,93 (14/
          +07) →                                                         
      119 +    `valor_considerado` 0,01 → não é `valor_invalido`."""     
      120 +    (item,) = avaliar(                                        
      121 +        despesa(data="2026-07-14", valor=Decimal("0.001"), moe
          +da="EUR")                                                     
      122 +    )["itens"]                                                
      123 +                                                              
      124 +    # 0,001 × 5,93 = 0,00593 → 0,01 > 0; 0,01 ≤ 60,00 → aprova
          +do                                                            
      125 +    assert item["valor_considerado"] == Decimal("0.01")       
      126 +    assert (item["status"], item["valor_reembolsado"]) == ("ap
          +rovado",                                                      
      127 +                                                          Deci
          +mal("0.01"))                                                  
      128 +                                                              
      129 +                                                              
      130 +def test_rn004_valor_estrangeiro_que_arredonda_a_zero_e_invali
          +do(                                                           
      131 +    avaliar, despesa                                          
      132 +):                                                            
      133 +    """RN-004 / AMB-026: 1e-999999 EUR com taxa 5,93 → 0,00 em
          + reais →                                                      
      134 +    `valor_invalido`."""                                      
      135 +    (item,) = avaliar(                                        
      136 +        despesa(data="2026-07-14", valor=Decimal("1e-999999"),
          + moeda="EUR")                                                 
      137 +    )["itens"]                                                
      138 +                                                              
      139 +    # 5,93 × 10^-999999 → 0,00 ≤ 0                            
      140 +    assert item["valor_considerado"] == Decimal("0.00")       
      141 +    _recusado_valor_invalido(item)                            
  ⎿  Updated tests/test_rn008_nota_fiscal.py (+13 -0)
      170      )["itens"]
      171  
      172      assert (item["status"], item["valor_reembolsado"]) == ("ap
           rovado", Decimal("50.00"))
      173 +                                                              
      174 +                                                              
      175 +def test_rn008_minimo_comparado_em_reais(avaliar, despesa):   
      176 +    """RN-008 / AMB-027 (aceite): 40,00 USD sem nota em 20/07,
          + taxa 5,50 →                                                  
      177 +    220,00 → `nota_fiscal_ausente` (40,00 na moeda original nã
          +o passaria)."""                                               
      178 +    (item,) = avaliar(                                        
      179 +        despesa(data="2026-07-20", categoria="transporte_urban
          +o",                                                           
      180 +                valor=Decimal("40.00"), moeda="USD", tem_nota_
          +fiscal=False)                                                 
      181 +    )["itens"]                                                
      182 +                                                              
      183 +    # 40,00 × 5,50 = 220,00 > 100,00 sem nota                 
      184 +    assert item["valor_considerado"] == Decimal("220.00")     
      185 +    _recusado_nota_fiscal_ausente(item)                       
  ⎿  Updated tests/test_rn010_viagem.py (+12 -0)
      349      assert _resumo(alimentacao) == (
      350          Decimal("135.00"), "parcial", "limite_diario_excedido"
           ,
      351      )
      352 +                                                              
      353 +                                                              
      354 +def test_rn010_moeda_estrangeira_nao_comprova_viagem(avaliar, 
          +despesa):                                                     
      355 +    """RN-010 / AMB-023 (aceite): alimentação de 22,00 EUR com
          + nota em 14/07,                                               
      356 +    sem hospedagem → 14/07 não fica em viagem."""             
      357 +    (item,) = avaliar(                                        
      358 +        despesa(data="2026-07-14", valor=Decimal("22.00"), moe
          +da="EUR")                                                     
      359 +    )["itens"]                                                
      360 +                                                              
      361 +    # 22,00 × 5,93 = 130,46; fora de viagem: limite 60,00 → pa
          +rcial com 60,00                                               
      362 +    assert (item["em_viagem"], item["limite_diario"]) == (Fals
          +e, Decimal("60.00"))                                          
      363 +    assert _resumo(item) == (Decimal("60.00"), "parcial", "lim
          +ite_diario_excedido")                                         

⏺ Ajusto o import local no teste de RN-003 para o topo, e sigo para saída e
  justificativa.

⏺ Bash(python3 - <<'EOF'
      p='tests/test_rn003_arredondamento.py'…)
  ⎿  29:        dict(data=date(2026, 7, 21), categoria="alimentacao", moeda
     ="GBP",
     78:        dict(data=date(2026, 7, 14), categoria="alimentacao", moeda
     ="EUR",
  ⎿  Updated tests/test_justificativa.py (+15 -0)
      24               valor_reembolsado=Decimal("0"), limite_diario=None
          ),
      25          id="recusado-entrada_invalida",
      26      ),
      27 +    pytest.param(                                              
      28 +        Status.RECUSADO, Motivo.CAMBIO_INDISPONIVEL,           
      29 +        dict(data=date(2026, 7, 21), categoria="alimentacao", m
         +oeda="GBP",                                                    
      30 +             valor_considerado=None, valor_reembolsado=Decimal(
         +"0"),                                                          
      31 +             limite_diario=None),                              
      32 +        id="recusado-cambio_indisponivel",                     
      33 +    ),                                                         
      34      pytest.param(
      35          Status.RECUSADO, Motivo.VALOR_INVALIDO,
      36          dict(data=date(2026, 7, 3), categoria="alimentacao",
     ...
      73               limite_diario=Decimal("60.00")),
      74          id="parcial-limite_diario_excedido",
      75      ),
      76 +    pytest.param(                                              
      77 +        Status.PARCIAL, Motivo.LIMITE_DIARIO_EXCEDIDO,         
      78 +        dict(data=date(2026, 7, 14), categoria="alimentacao", m
         +oeda="EUR",                                                    
      79 +             taxa_cambio=Decimal("5.93"), data_cotacao=date(202
         +6, 7, 14),                                                     
      80 +             valor_considerado=Decimal("130.46"),              
      81 +             valor_reembolsado=Decimal("60.00"), limite_diario=
         +Decimal("60.00")),                                             
      82 +        id="parcial-convertido-de-eur",                        
      83 +    ),                                                         
      84      pytest.param(
      85          Status.RECUSADO, Motivo.LIMITE_DIARIO_EXCEDIDO,
      86          dict(data=date(2026, 7, 3), categoria="alimentacao",
  ⎿  Updated tests/test_rn003_arredondamento.py (+3 -3)
       4  
       5  import pytest
       6  
       7 +from conftest import construir_cambio                          
       8 +                                                               
       9  
      10  @pytest.mark.parametrize(
      11      ("valor", "considerado"),
     ...
      72      assert item["valor_informado"] == valor
      73  
      74  
      73 -def test_rn003_produto_com_mais_de_28_digitos_e_exato(avaliar, 
         -despesa, ):                                                    
      75 +def test_rn003_produto_com_mais_de_28_digitos_e_exato(avaliar, 
         +despesa):                                                      
      76      """RN-003 / DT-012: o produto é exato, sem a precisão padrã
          o de 28 dígitos.
      77  
      78      Câmbio com USD 2 em 14/07; 50,00249999999999999999999999999
          9 USD sem nota."""
      77 -    from conftest import construir_cambio                      
      78 -                                                               
      79      cambio = construir_cambio(taxas={"2026-07-14": {"USD": Deci
          mal("2")}})
      80      (item,) = avaliar(
      81          despesa(data="2026-07-14", valor=Decimal("50.0024999999
          99999999999999999999"),
  ⎿  Updated tests/test_saida.py (+21 -1)
      27      "categoria",
      28      "valor_informado",
      29      "moeda",
      30 +    "taxa_cambio",                                             
      31 +    "data_cotacao",                                            
      32      "valor_considerado",
      33      "valor_reembolsado",
      34      "status",
     ...
      48          categoria="alimentacao",
      49          valor_informado=Decimal("45.00"),
      50          moeda="BRL",
      51 +        taxa_cambio=Decimal(1),                                
      52 +        data_cotacao=None,                                     
      53          valor_considerado=Decimal("45.00"),
      54          valor_reembolsado=Decimal("45.00"),
      55          status=Status.APROVADO,
     ...
      70          categoria=None,
      71          valor_informado=None,
      72          moeda=None,
      73 +        taxa_cambio=None,                                      
      74 +        data_cotacao=None,                                     
      75          valor_considerado=None,
      76          valor_reembolsado=Decimal("0"),
      77          status=Status.RECUSADO,
     ...
      193  
      194  
      195  def test_nenhum_valor_monetario_e_float():
      190 -    """DT-001: nenhum campo monetário do dicionário de saída é
          - `float`."""                                                  
      196 +    """DT-001: nenhum campo monetário do dicionário de saída, 
          +nem a                                                         
      197 +    `taxa_cambio`, é `float`."""                              
      198      dicionario = para_dicionario(resultado(itens=[item()]))
      199      monetarios = [
      200          dicionario["itens"][0][campo]
      201          for campo in (
      202              "valor_informado",
      203 +            "taxa_cambio",                                    
      204              "valor_considerado",
      205              "valor_reembolsado",
      206              "limite_diario",
     ...
      225          "categoria",
     … 23 more lines (ctrl+o to expand)

  Ran 1 shell command (ctrl+o to expand)

⏺ Insiro os 14 casos de borda de câmbio logo após os de tabela aplicada.

⏺ Bash(python3 - <<'EOF'
      p='tests/test_casos_de_borda.py'…)
  ⎿  266:def _hospedagem(**campos):
     267-    padrao = dict(id="h", categoria="hospedagem", fornecedor="Hote
     l",
     … +11 lines (ctrl+o to expand)
  ⎿  Updated tests/test_casos_de_borda.py (+217 -0)
      1010      verificar(processar(texto, politica))
      1011  
      1012  
      1013 +def _conversao(item):                                        
      1014 +    return (                                                 
      1015 +        item["moeda"], item["taxa_cambio"], item["data_cotaca
           +o"],                                                         
      1016 +        item["valor_considerado"],                           
      1017 +    )                                                        
      1018 +                                                             
      1019 +                                                             
      1020 +def _recusado_cambio_indisponivel(item):                     
      1021 +    # RN-015: recusado na etapa 2; sem valor em reais nem tax
           +a (seção 4)                                                  
      1022 +    assert (item["status"], item["motivo"]) == ("recusado", "
           +cambio_indisponivel")                                        
      1023 +    assert item["valor_reembolsado"] == 0                    
      1024 +    for campo in (                                           
      1025 +        "valor_considerado", "taxa_cambio", "data_cotacao", "
           +em_viagem",                                                  
      1026 +        "limite_diario",                                     
      1027 +    ):                                                       
      1028 +        assert item[campo] is None, campo                    
      1029 +                                                             
      1030 +                                                             
      1031 +def _caso_moeda_nula(saida):                                 
      1032 +    # null = BRL: taxa 1, sem data de cotação; 45,00 ≤ 60,00 
           +→ aprovado                                                   
      1033 +    (item,) = saida["itens"]                                 
      1034 +    assert _conversao(item) == ("BRL", 1, None, Decimal("45.0
           +0"))                                                         
      1035 +    assert (item["valor_reembolsado"], item["status"]) == (De
           +cimal("45.00"),                                              
      1036 +                                                          "ap
           +rovado")                                                     
      1037 +                                                             
      1038 +                                                             
      1039 +def _caso_moeda_estrangeira_com_cotacao(saida):              
      1040 +    # 22,00 × 5,93 = 130,46; min(130,46; 60,00) = 60,00 → par
           +cial                                                         
      1041 +    (item,) = saida["itens"]                                 
      1042 +    assert _conversao(item) == ("EUR", Decimal("5.93"), "2026
           +-07-14",                                                     
      1043 +                                Decimal("130.46"))           
      1044 +    assert (item["valor_reembolsado"], item["status"]) == (De
           +cimal("60.00"),                                              
      1045 +                                                          "pa
           +rcial")                                                      
      1046 +                                                             
      1047 +                                                             
      1048 +def _caso_moeda_estrangeira_em_sabado(saida):                
      1049 +    # 18/07 sem cotação → 17/07 (D-1): 30,00 × 5,96 = 178,80 
     … 183 more lines (ctrl+o to expand)
  ⎿  Updated tests/test_rastreabilidade.py (+0 -14)
      18  TASKS = SPEC.with_name("tasks.md")
      19  
      20  PENDENTES = {  # some quando a Fase 5 terminar (DT-016)
      21 -    "Moeda nula": "T-031",                                     
      22 -    "Moeda estrangeira com cotação": "T-031",                  
      23 -    "Moeda estrangeira em sábado": "T-031",                    
      24 -    "Cotação exatamente 3 dias antes": "T-031",                
      25 -    "Cotação 4 dias antes": "T-031",                           
      26 -    "Moeda sem cotação no arquivo": "T-031",                   
      27 -    "Sem cotação e fora do período": "T-031",                  
      28 -    "Conversão arredondada uma vez": "T-031",                  
      29 -    "Nota fiscal comparada em reais": "T-031",                 
      30 -    "Valor estrangeiro minúsculo": "T-031",                    
      31 -    "Teto na moeda original": "T-031",                         
      32 -    "Moeda estrangeira não comprova viagem": "T-031",          
      33 -    "Hospedagem em moeda estrangeira": "T-031",                
      34 -    "Data intermediária sem a moeda": "T-031",                 
      21      "Duplicata em moedas diferentes": "T-032",
      22      "Duplicata em moeda estrangeira": "T-032",
      23  }

⏺ Testes escritos. Rodo os novos antes da implementação (devem falhar pelo
  motivo certo).

  Ran 2 shell commands (ctrl+o to expand)

⏺ Erro de coleta em test_justificativa.py esperado (Motivo.CAMBIO_INDISPONIVEL
  ainda não existe). O resto:

  Ran 1 shell command (ctrl+o to expand)

⏺ As falhas identificadas se devem a campos/comportamentos ausentes, enquanto
  dois testes novos já passam e servirão como proteção contra regressão. Agora
  vou partir para a implementação.

⏺ Bash(python3 - <<'EOF'
      p='src/reembolso/modelo.py'…)
  ⎿  Updated src/reembolso/modelo.py (+3 -0)
      17      """Na ordem das etapas da seção 8 da spec."""
      18  
      19      ENTRADA_INVALIDA = "entrada_invalida"
      20 +    CAMBIO_INDISPONIVEL = "cambio_indisponivel"                
      21      VALOR_INVALIDO = "valor_invalido"
      22      FORA_DO_PERIODO = "fora_do_periodo"
      23      CATEGORIA_FORA_DA_POLITICA = "categoria_fora_da_politica"
     ...
      127      categoria: str | None
      128      valor_informado: Decimal | None
      129      moeda: str | None
      130 +    taxa_cambio: Decimal | None                               
      131 +    data_cotacao: str | None  # AAAA-MM-DD                    
      132      valor_considerado: Decimal | None
      133      valor_reembolsado: Decimal
      134      status: Status
  ⎿  Updated src/reembolso/saida.py (+2 -0)
      13          "categoria": item.categoria,
      14          "valor_informado": item.valor_informado,
      15          "moeda": item.moeda,
      16 +        "taxa_cambio": item.taxa_cambio,                       
      17 +        "data_cotacao": item.data_cotacao,                     
      18          "valor_considerado": item.valor_considerado,
      19          "valor_reembolsado": item.valor_reembolsado,
      20          "status": item.status.value,

⏺ Bash(python3 - <<'EOF'
      p='src/reembolso/justificativa.py'…)
  ⎿  Updated src/reembolso/justificativa.py (+48 -2)
      16      return f"{data.day:02d}/{data.month:02d}"
      17  
      18  
      19 +def formatar_taxa(taxa: Decimal) -> str:                       
      20 +    """Taxa com as casas que tiver, sem arredondar (DT-009): `5
         +,93`."""                                                       
      21 +    return str(taxa).replace(".", ",")                         
      22 +                                                               
      23 +                                                               
      24  def justificar(
      25      status: Status,
      26      motivo: Motivo | None,
     ...
      31      valor_reembolsado: Decimal,
      32      limite_diario: Decimal | None,
      33      nota_fiscal_acima_de: Decimal,
      34 +    moeda: str | None = None,                                  
      35 +    taxa_cambio: Decimal | None = None,                        
      36 +    data_cotacao: date | None = None,                          
      37  ) -> str:
      38      """Frase de um item já decidido, a partir dos seus campos c
          ontratuais.
      39  
      32 -    `nota_fiscal_acima_de` é o mínimo da nota da política (DT-0
         -09). Nenhuma                                                   
      33 -    decisão depende deste texto (plan seção 3).                
      40 +    `nota_fiscal_acima_de` é o mínimo da nota da política (DT-0
         +09). Com                                                       
      41 +    `data_cotacao` (moeda diferente de `BRL`), a frase começa p
         +ela conversão.                                                 
      42 +    Nenhuma decisão depende deste texto (plan seção 3).        
      43      """
      44 +    frase = _frase(                                            
      45 +        status,                                                
      46 +        motivo,                                                
      47 +        data=data,                                             
      48 +        categoria=categoria,                                   
      49 +        valor_considerado=valor_considerado,                   
      50 +        valor_reembolsado=valor_reembolsado,                   
      51 +        limite_diario=limite_diario,                           
      52 +        nota_fiscal_acima_de=nota_fiscal_acima_de,             
      53 +        moeda=moeda,                                           
      54 +    )                                                          
      55 +    if data_cotacao is None:                                   
      56 +        return frase                                           
      57 +    return (                                                   
     … 32 more lines (ctrl+o to expand)

⏺ Bash(python3 - <<'EOF'
      p='src/reembolso/motor.py'…)
  ⎿          """RN-002 / seção 4: despesa válida recusada numa etapa poster
     ior à 1
             (fora do período, RN-005) → `moeda` como na validação."""
     … +19 lines (ctrl+o to expand)
  ⎿  Updated src/reembolso/motor.py (+59 -17)
       3  from datetime import date, timedelta
       4  from decimal import Decimal
       5  
       6 -from reembolso.dinheiro import arredondar                      
       6 +from reembolso.cambio import cotacao                           
       7 +from reembolso.dinheiro import arredondar, contexto_exato      
       8  from reembolso.justificativa import justificar
       9  from reembolso.modelo import (
      10      Cambio,
      11 +    Cotacao,                                                   
      12      Despesa,
      13      DespesaInvalida,
      14      Entrada,
     ...
      33  ZERO = Decimal("0.00")
      34  
      35  
      36 +def _converter(valor: Decimal, taxa: Decimal) -> Decimal:      
      37 +    """Etapa 2 (RN-003, RN-015, AMB-026): `valor` × taxa, produ
         +to exato (DT-012),                                             
      38 +    arredondado ao centavo uma única vez, em reais."""         
      39 +    with contexto_exato():                                     
      40 +        return arredondar(valor * taxa)                        
      41 +                                                               
      42 +                                                               
      43 +def _taxa_e_data(cotacao_usada: Cotacao | None) -> tuple[Decima
         +l | None, str | None]:                                         
      44 +    """`taxa_cambio` e `data_cotacao` da saída (seção 4); nulas
         + sem cotação."""                                               
      45 +    if cotacao_usada is None:                                  
      46 +        return None, None                                      
      47 +    data = cotacao_usada.data                                  
      48 +    return cotacao_usada.taxa, data.isoformat() if data is not 
         +None else None                                                 
      49 +                                                               
      50 +                                                               
      51  def _status(
      52      considerado: Decimal, reembolsado: Decimal
      53  ) -> tuple[Status, Motivo | None]:
     ...
      71          categoria=categoria,
      72          valor_informado=despesa.valor_informado,
      73          moeda=despesa.moeda_saida,
      74 +        taxa_cambio=None,                                      
      75 +        data_cotacao=None,                                     
      76          valor_considerado=None,
     … 140 more lines (ctrl+o to expand)
  Ran 1 shell command (ctrl+o to expand)

⏺ Encontrei duas falhas em testes antigos ligadas à T-031: a lista de Motivo com
  comentário pendente e um teste da T-030 usando data sem cotação, que pela
  spec deveria falhar antes por cambio_indisponivel. Vou corrigir o teste
  mantendo a intenção original (recusa na etapa 4), ajustando para período até
  20/07 e data 21/07, que tem cotação disponível.

⏺ Bash(python3 - <<'EOF'
      p='tests/test_modelo.py'…)
  ⎿  ......................................................................
     .. [ 97%]
     .........................
     … +3 lines (ctrl+o to expand)
  ⎿  Updated tests/test_modelo.py (+2 -2)
       5  
       6  def test_motivos_na_ordem_da_secao_8():
       7      """Seção 4 (códigos de motivo) / seção 8: códigos na ordem 
          das etapas."""
       8 -    # Tabela "Códigos de motivo" da seção 4, na ordem das etapa
         -s 1, 3, 4, 5, 6, 7, 9                                          
       9 -    # (`cambio_indisponivel`, da etapa 2, entra na T-031)      
       8 +    # Tabela "Códigos de motivo" da seção 4, na ordem das etapa
         +s 1 a 7 e 9                                                    
       9      assert [m.value for m in Motivo] == [
      10          "entrada_invalida",
      11 +        "cambio_indisponivel",                                 
      12          "valor_invalido",
      13          "fora_do_periodo",
      14          "categoria_fora_da_politica",
  ⎿  Updated tests/test_rn002_validacao_da_entrada.py (+6 -2)
      1036  ):
      1037      """RN-002 / seção 4: despesa válida recusada numa etapa p
            osterior à 1
      1038      (fora do período, RN-005) → `moeda` como na validação."""
      1039 -    (item,) = avaliar(despesa(data="2026-08-01", **documento)
           -)["itens"]                                                   
      1040 -    # período de 01/07 a 31/07: 01/08 → `fora_do_periodo` (et
           -apa 4)                                                       
      1039 +    (item,) = avaliar(                                       
      1040 +        despesa(data="2026-07-21", **documento),             
      1041 +        periodo={"inicio": "2026-07-01", "fim": "2026-07-20"}
           +,                                                            
      1042 +    )["itens"]                                               
      1043 +    # 21/07 tem cotação de USD (etapa 2 passa); período até 2
           +0/07 →                                                       
      1044 +    # `fora_do_periodo` (etapa 4)                            
      1045      assert item["motivo"] == "fora_do_periodo"
      1046      assert item["moeda"] == esperada

⏺ Suíte verde (961 testes) e ruff limpo. Agora confiro o diff, rodo a CLI no
  envelope como sanidade e chamo o revisor independente.

  Ran 1 shell command (ctrl+o to expand)

⏺ A saída do envelope já bate com a segunda tabela da seção 9 (formalização fica
  para a T-033). Chamo o revisor.

⏺ revisor-de-task(Revisão independente T-031)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ O revisor independente da T-031 está rodando em segundo plano. Quando o
  parecer chegar, salvo em docs/reviews/T-031.md e apresento o resumo para sua
  aprovação antes do commit.

✻ Crunched for 6m 4s · done 3:39 PM

› Message from revisor-de-task
  # Revisão T-031 — Conversão: etapa 2 da seção 8 (cotação, `valor_considerado`
  convertido, `cambio_indisponivel`, `taxa_cambio`/`data_cotacao`)

  - **Data:** 2026-10-04
  - **Regras conferidas:** RN-002 (nulos em `entrada_invalida`), RN-003, RN-004,
  RN-008, RN-010, RN-015, AMB-023, AMB-024, AMB-025, AMB-026, AMB-027, seção 4
  (`taxa_cambio`, `data_cotacao`, `valor_considerado`,
  `totais.valor_solicitado`), seção 7 (14 casos de câmbio), seção 8 (etapa 2),
  DT-001, DT-009, DT-012, D-007 (itens 6, 7 e 14)
  - **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 961 passed, 0
  failed (evidência, não veredito)

  ### Resultado
  **APROVADO COM RESSALVAS**: todos os critérios de aceite têm evidência e os
  esperados conferem com a spec quando recalculados à mão. Ficam um teste de
  propriedade fraco para `taxa_cambio` e duas observações de baixa severidade.

  ### Critérios de aceite
  | # | Critério | Status | Evidência |
  |---|---|---|---|
  | 1 | 22,00 EUR em 14/07 → 5,93, `2026-07-14`, 130,46 | atendido | `tests/test
  _rn015_moeda_e_cambio.py::test_rn015_eur_na_propria_data_convertido` (22 ×
  5,93 = 130,46 ✔) |
  | 2 | 30,00 EUR em 18/07 → 5,96 de 17/07, 178,80 | atendido |
  `test_rn015_eur_no_sabado_usa_a_cotacao_de_sexta` (30 × 5,96 = 178,80 ✔) |
  | 3 | Sem `moeda` → `BRL`, taxa 1, `data_cotacao` nula | atendido |
  `test_rn015_brl_tem_taxa_1_e_data_cotacao_nula[ausente/nula/BRL]`;
  `test_rn015_brl_ignora_o_arquivo_de_cambio` |
  | 4 | 55,00 GBP em 21/07 → `cambio_indisponivel`, cinco campos nulos, fora de
  `valor_solicitado` | atendido |
  `test_rn015_gbp_sem_cotacao_e_cambio_indisponivel` +
  `_recusado_cambio_indisponivel` (confere os 5 campos e os totais zerados) |
  | 5 | USD em 12/07 → `cambio_indisponivel` | atendido |
  `test_rn015_usd_sem_cotacao_nos_3_dias_anteriores` (o câmbio começa em 13/07
  ✔) |
  | 6 | RN-003: 16,8649 EUR × 5,93 → 100,01; 0,001 EUR → 0,01 | atendido |
  `tests/test_rn003_arredondamento.py::test_rn003_conversao_arredondada_uma_vez_
  em_reais` (100,008857 → 100,01; 0,00593 → 0,01 ✔) |
  | 7 | RN-004: 0,001 EUR não é `valor_invalido`; `1e-999999` EUR é
  `valor_invalido` | atendido | `tests/test_rn004_valor_positivo.py::test_rn004_
  valor_estrangeiro_minusculo_nao_e_invalido`,
  `::test_rn004_valor_estrangeiro_que_arredonda_a_zero_e_invalido` |
  | 8 | RN-008: 40,00 USD sem nota a 5,50 → 220,00, `nota_fiscal_ausente` |
  atendido |
  `tests/test_rn008_nota_fiscal.py::test_rn008_minimo_comparado_em_reais` (20/07
  USD 5,50 ✔) |
  | 9 | RN-010: alimentação de 22,00 EUR com nota em 14/07, sem hospedagem →
  fora de viagem | atendido |
  `tests/test_rn010_viagem.py::test_rn010_moeda_estrangeira_nao_comprova_viagem`
  (limite 60,00, parcial 60,00 ✔) |
  | 10 | `test_justificativa.py` cobre `cambio_indisponivel` | atendido |
  `tests/test_justificativa.py` param `recusado-cambio_indisponivel`; frase em
  `src/reembolso/justificativa.py` (ramo `CAMBIO_INDISPONIVEL`) |
  | 11 | Ordem das etapas: sem cotação + fora do período; sem cotação + valor
  negativo → `cambio_indisponivel`; inválida em EUR → `entrada_invalida` com
  `taxa_cambio` nula | atendido |
  `test_rn015_sem_cotacao_e_fora_do_periodo_e_cambio_indisponivel`,
  `test_rn015_sem_cotacao_e_valor_negativo_e_cambio_indisponivel`,
  `test_rn015_despesa_invalida_em_eur_tem_taxa_nula`; código em
  `src/reembolso/motor.py` (`calcular`: busca a cotação antes de
  `_motivo_de_recusa`) |
  | 12 | O teste de propriedade da DT-001 cobre `taxa_cambio` | atendido (fraco,
  ver problema 1) | `tests/test_saida.py::test_nenhum_valor_monetario_e_float`
  passou a incluir `taxa_cambio` |
  | 13 | Casos de borda da seção 7 (14 casos) | atendido |
  `tests/test_casos_de_borda.py::test_caso_de_borda_de_cambio`, com `id` igual
  ao nome de cada caso; as entradas de T-031 saíram de `PENDENTES` em
  `tests/test_rastreabilidade.py` |

  ### Problemas encontrados
  #### 1. Teste de propriedade da DT-001 para `taxa_cambio` não pegaria um
  `float` vindo do motor — severidade MÉDIA
  - **Regra afetada:** DT-001 (seção 4: "`taxa_cambio` ... é a cópia do número
  do arquivo de câmbio, com o valor decimal exato")
  - **Evidência:** `tests/test_saida.py::test_nenhum_valor_monetario_e_float`
  monta o item à mão com `taxa_cambio=Decimal(1)` e só confere que
  `para_dicionario` não o transforma em `float`. O teste de ponta a ponta
  `tests/test_exemplo.py::test_nenhum_valor_monetario_e_float` não ganhou
  `taxa_cambio` e só roda o exemplo todo em BRL.
  - **Impacto:** se o motor ou `cambio.cotacao` passassem a devolver a taxa como
  `float` (ou `Decimal(1)` virasse `1.0`), nenhum teste de propriedade
  falharia. Os testes de igualdade com `Decimal("5.93")` também não pegam,
  porque um `float` 5.93 pode ser igual ao `Decimal` em igualdade frouxa.
  - **Recomendação:** exercitar a propriedade sobre a saída real do motor com
  moeda estrangeira, conferindo `type(item["taxa_cambio"]) is Decimal` (ou que
  não é `float`). Pode entrar aqui ou ficar explícito para a T-033, que roda os
  arquivos do envelope.

  #### 2. Saldo do limite e totais fora do contexto exato (anterior à task) —
  severidade BAIXA
  - **Regra afetada:** DT-012 / DT-001 do plan ("Toda conta posterior (saldo do
  limite, totais) também roda no contexto exato"), RN-003 ("todos os cálculos
  são exatos ao centavo")
  - **Evidência:** `src/reembolso/motor.py`, `_aplicar_limite` (`saldos[chave] =
  saldo - reembolsado`) e `_totais` (`sum(...)`, `solicitado - reembolsado`)
  rodam no contexto padrão de 28 dígitos. A T-031 só pôs a multiplicação em
  `contexto_exato()` (`_converter`).
  - **Impacto:** com a conversão, `valor_considerado` pode chegar a cerca de
  10^18 (20 dígitos). Para estourar 28 dígitos seriam precisos uns 10^8 itens
  desse tamanho. Nenhum resultado realista muda, mas o código não segue a DT-012
  escrita.
  - **Recomendação:** registrar ou corrigir fora desta task (é anterior a ela).
  Não bloqueia.

  #### 3. Hospedagem com nota recusada por `cambio_indisponivel` sem teste de
  que não comprova viagem — severidade BAIXA
  - **Regra afetada:** RN-010 ("comprova viagem quando ... passou pelas etapas 1
  a 7"), seção 8 (Consequências)
  - **Evidência:** o código está certo: `src/reembolso/motor.py` faz `continue`
  antes de `seguem`, então o item não chega a `_dias_em_viagem`. Mas nenhum
  teste usa hospedagem com nota em GBP seguida de alimentação em D+1.
  - **Impacto:** se a etapa 2 mudar, a regressão passa sem teste. Hoje não há
  resultado errado.
  - **Recomendação:** opcional. A spec não lista esse caso de borda.

  ### Cobertura
  - **Regras testadas:**
    - RN-015: 13 testes de ponta a ponta em `tests/test_rn015_moeda_e_cambio.py`
  (EUR na data, sábado, BRL ausente/nulo/explícito, BRL do arquivo ignorado,
  GBP, USD em 12/07, `XYZ`, D-3/D-4, não consome limite, ordem das etapas,
  inválida em EUR, hospedagem em EUR).
    - RN-003: conversão arredondada uma vez, mais um produto com mais de 28
  dígitos (50,0024999… × 2 → 100,00; conferido à mão).
    - RN-004: 0,001 EUR e 1e-999999 EUR.
    - RN-008: 40 USD → 220,00.
    - RN-010 / AMB-023: EUR não comprova viagem; hospedagem em EUR comprova.
    - Justificativa: `cambio_indisponivel` e a frase com a conversão.
    - Seção 4: `taxa_cambio` e `data_cotacao` na ordem dos campos e exatas
  (`test_saida.py`); `test_modelo.py` com `Motivo` na ordem da seção 8.
  - **Casos de borda cobertos:** os 14 da T-031 na seção 7, com os esperados
  recalculados à mão: 45,00 BRL; 130,46 / 60,00; 178,80; 54,20; D-4 nulo; GBP
  nulo e fora dos totais; 15/04 USD; 100,01 com nota ausente; 220,00; 0,01
  aprovado; 1.088.000.000,00 / parcial 60,00; 14/07 fora de viagem com limite
  60,00; 297,50 → 250,00 e 23/07 com limite 90,00 aprovado em 80,00; data
  intermediária → 5,91 de 13/07, 118,20, parcial 60,00.
  - **Casos que parecem faltar:**
    - Hospedagem com nota em moeda sem cotação não comprova viagem (RN-010,
  seção 8). Opcional.
    - Despesa em moeda estrangeira com cotação e valor negativo →
  `valor_invalido` com `taxa_cambio` preenchida (seção 4: a taxa só é nula em
  `entrada_invalida`/`cambio_indisponivel`). Opcional.
    - Duplicata em moeda estrangeira com `taxa_cambio` preenchida no item
  `duplicata`. O código faz isso (`_item_recusado(despesa, *conversoes[...],
  ...)`), mas sem teste; pode ficar com a T-032.

  Observação de escopo, sem problema: `_separar_duplicatas` ainda agrupa sem a
  moeda. Hoje 22,00 EUR e 22,00 USD com os demais campos iguais dão `duplicata`,
  o que é a T-032 (RN-007 / AMB-028), ainda pendente em `PENDENTES`. Não é
  falha desta task.

  ### Decisões necessárias
  Nenhuma.

  ### Antes de concluir a task
  Nada bloqueia: pode seguir para o commit. Fica recomendado (MÉDIA) reforçar o
  teste de propriedade da DT-001 para `taxa_cambio` sobre a saída real do motor
  com moeda estrangeira, aqui ou registrado explicitamente para a T-033.

⏺ Revisor: APROVADO COM RESSALVAS, nenhuma decisão necessária. Salvo o parecer
  sem edição e corrijo o que é do escopo (problemas 1 e 3).

⏺ Write(docs/reviews/T-031.md)
  ⎿  Wrote 67 lines to docs/reviews/T-031.md
      1 # Revisão T-031 — Conversão: etapa 2 da seção 8 (cotação, `valor_
        ta_cotacao`)
      2 
      4 - **Regras conferidas:** RN-002 (nulos em `entrada_invalida`), RN
        AMB-026, AMB-027, seção 4 (`taxa_cambio`, `data_cotacao`, `valor_
        considerado`, `totais.valor_solicitado`), seção 7 (14 casos de câ
         7 e 14)
      5 - **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 96
      6 
      8 **APROVADO COM RESSALVAS**: todos os critérios de aceite têm evi
     … +154 lines (ctrl+o to expand)

⏺ Bash(cat >> tests/test_rn015_moeda_e_cambio.py <<'EOF'…)
  ⎿  ............................
        [100%]
     964 passed in 0.63s
     All checks passed!
  ⎿  Updated tests/test_rn015_moeda_e_cambio.py (+46 -0)
      294          True, Decimal("90.00"),
      295      )
      296      assert alimentacao["status"] == "aprovado"
      297 +                                                              
      298 +                                                              
      299 +def test_rn015_taxa_e_valores_da_saida_do_motor_sao_decimal(av
          +aliar, despesa):                                              
      300 +    """RN-015 / DT-001: na saída real do motor, `taxa_cambio` 
          +(EUR e BRL) e os                                              
      301 +    valores monetários convertidos são `Decimal`, nunca `float
          +`."""                                                         
      302 +    saida = avaliar(                                          
      303 +        despesa(id="e", data="2026-07-14", valor=Decimal("22.0
          +0"), moeda="EUR"),                                            
      304 +        despesa(id="b", data="2026-07-14", valor=Decimal("10.0
          +0"), fornecedor="B"),                                         
      305 +    )                                                         
      306 +                                                              
      307 +    for item in saida["itens"]:                               
      308 +        for campo in ("taxa_cambio", "valor_considerado", "val
          +or_reembolsado",                                              
      309 +                      "limite_diario"):                       
      310 +            assert type(item[campo]) is Decimal, campo        
      311 +    assert all(type(v) is Decimal for v in saida["totais"].val
          +ues())                                                        
      312 +                                                              
      313 +                                                              
      314 +@pytest.mark.parametrize(                                     
      315 +    ("campos", "motivo"),                                     
      316 +    [                                                         
      317 +        # 22,00 GBP sem cotação → etapa 2                     
      318 +        ({"moeda": "GBP"}, "cambio_indisponivel"),            
      319 +        # -10,00 EUR × 5,95 = -59,50 ≤ 0 → etapa 3, com a taxa
          + preenchida                                                   
      320 +        ({"moeda": "EUR", "valor": Decimal("-10.00")}, "valor_
          +invalido"),                                                   
      321 +    ],                                                        
      322 +)                                                             
      323 +def test_rn015_hospedagem_recusada_antes_do_limite_nao_comprov
          +a_viagem(                                                     
      324 +    avaliar, despesa, campos, motivo                          
      325 +):                                                            
      326 +    """RN-015 / RN-010 / seção 8: hospedagem com nota recusada
          + na etapa 2 ou 3                                              
      327 +    não comprova viagem; a recusada na etapa 3 sai com a taxa 
          +(seção 4)."""                                                 
      328 +    hospedagem, alimentacao = avaliar(                        
      329 +        despesa(**{"id": "h", "data": "2026-07-22", "categoria
          +": "hospedagem",                                              
      330 +                   "valor": Decimal("22.00"), **campos}),     
      331 +        despesa(id="a", data="2026-07-23", valor=Decimal("80.0
          +0")),                                                         
      332 +    )["itens"]                                                
      333 +                                                              
     … 9 more lines (ctrl+o to expand)

⏺ Agent "Revisão independente T-031" finished · 2m 31s

⏺ Resumo — T-031: Conversão de moeda (etapa 2 da seção 8)

  A T-031 está implementada e testada, sem commit. Falta a sua autorização.

  Arquivos alterados:
  - src/reembolso/modelo.py (modificado): novo motivo CAMBIO_INDISPONIVEL, na
    ordem da seção 8. ItemResultado ganha taxa_cambio e data_cotacao.
  - src/reembolso/motor.py (modificado): a etapa 2 busca a cotação. Sem cotação,
    a despesa sai cambio_indisponivel antes das etapas 3 a 6. Com cotação,
    valor_considerado = arredondar(valor × taxa), com o produto calculado em
    contexto_exato(). As etapas seguintes usam o valor convertido. O total
    valor_solicitado agora deixa de fora todo valor_considerado nulo.
  - src/reembolso/saida.py (modificado): taxa_cambio e data_cotacao saem na
    posição da seção 4.
  - src/reembolso/justificativa.py (modificado): frase para cambio_indisponivel
    e prefixo com a conversão ("Convertido de EUR pela taxa 5,93 de 14/07:
    130,46."). A taxa sai com as casas que tiver, como pede a DT-009.
  - docs/reviews/T-031.md (novo): parecer do revisor, sem edição.
  - Testes (modificados): conftest.py (avaliar aceita cambio=), test_rn015,
    test_rn003, test_rn004, test_rn008, test_rn010, test_casos_de_borda,
    test_justificativa, test_saida, test_modelo, test_rn002 e
    test_rastreabilidade (as 14 pendências da T-031 saíram de PENDENTES).

  Testes criados/alterados:
  - test_rn015_* (17 testes de ponta a ponta) → RN-015, AMB-024, AMB-025,
    seção 8. Cobrem:
    - EUR na própria data e no sábado;
    - BRL ausente, nulo ou explícito, e a entrada BRL do arquivo de câmbio
      ignorada;
    - GBP sem cotação, USD em 12/07 e XYZ;
    - cotação de D-3 aceita e de D-4 recusada;
    - despesa sem cotação não consome limite nem entra nos totais;
    - ordem das etapas e despesa inválida em EUR;
    - hospedagem em EUR comprova viagem; hospedagem recusada na etapa 2 ou 3 não
      comprova;
    - taxa_cambio é Decimal na saída real do motor.
  - test_rn003_conversao_arredondada_uma_vez_em_reais (16,8649 → 100,01 e 0,001
    → 0,01) e test_rn003_produto_com_mais_de_28_digitos_e_exato → RN-003,
    AMB-026, DT-012.
  - test_rn004_valor_estrangeiro_* (0,001 EUR e 1e-999999 EUR) → RN-004.
  - test_rn008_minimo_comparado_em_reais (40 USD → 220,00) → RN-008, AMB-027.
  - test_rn010_moeda_estrangeira_nao_comprova_viagem → RN-010, AMB-023.
  - test_caso_de_borda_de_cambio: os 14 casos de borda da seção 7.
  - test_justificativa: casos novos cambio_indisponivel e convertido de EUR.
  - test_saida: ordem dos campos, taxa_cambio e data_cotacao exatas, nulos,
    DT-001.

  Testes executados antes da implementação: 46 falharam pelo motivo certo: campo
  ausente, ItemResultado sem os campos novos, nenhuma conversão.
  test_justificativa.py falhou na importação porque Motivo.CAMBIO_INDISPONIVEL
  ainda não existia, o que é aceitável. Dois testes novos já passavam: "Moeda
  estrangeira não comprova viagem" e "1e-999999 EUR → valor_invalido". Esse
  comportamento já valia por construção (o motor tratava EUR como BRL), então
  eles ficam como proteção contra regressão.

  Testes executados depois: uv run pytest -q e uv run ruff check .. Também rodei
  a CLI no despesas-envelope.json: as 10 linhas e os totais (2.457,52 /
  1.148,26 / 1.309,26) batem com a seção 9. O teste formal disso é da T-033.

  pytest: 964 passed, 0 failed
  ruff: limpo

  Revisão independente: APROVADO COM RESSALVAS, sem decisões necessárias
  (docs/reviews/T-031.md).
  - Ressalva MÉDIA, corrigida: o teste da DT-001 para taxa_cambio não pegaria um
    float vindo do motor. Agora há um teste de ponta a ponta que confere
    type(...) is Decimal.
  - Ressalva BAIXA, corrigida: faltava teste de que uma hospedagem recusada por
    cambio_indisponivel não comprova viagem. Agora há, junto com o caso
    valor_invalido em EUR, que sai com a taxa preenchida.
  - Ressalva BAIXA, não corrigida: o saldo do limite e os totais rodam fora do
    contexto_exato(), ao contrário do que a DT-012 manda. Isso vem de antes
    desta task e não muda nenhum resultado realista. Fica para você decidir se
    vira task.

  Decisões ou interpretações realizadas:
  - Mudei o esperado de um teste da T-030
    (test_rn002_moeda_sai_em_item_recusado_depois_da_etapa_1[USD]). Ele usava
    USD em 01/08, data sem cotação, e esperava fora_do_periodo. Pela seção 8, o
    câmbio é verificado antes do período, então o certo é cambio_indisponivel.
    Para manter o que o teste queria verificar, ele agora usa um período até
    20/07 e a data 21/07, que tem cotação.
  - O texto da justificativa é escolha minha, mas não é contratual (DT-009).
  - Nenhuma decisão de regra fora da spec.

  Lacunas ou dúvidas:
  - A detecção de duplicatas ainda não considera a moeda: hoje 22,00 EUR e 22,00
    USD com os demais campos iguais saem como duplicata. Isso é a T-032, que
    segue pendente em PENDENTES.
  - A DT-012 no saldo e nos totais, como acima.

  Commit proposto: feat(T-031): conversão de moeda na etapa 2 com 
  cambio_indisponivel

  Posso commitar? Depois do commit, para fechar o bloco, vou te pedir /export 
  docs/sessions/49-t031-conversao-moeda.md.

✻ Cogitated for 9m 39s · done 3:43 PM

❯ pode commitar                                                                 

  Ran 1 shell command (ctrl+o to expand)

⏺ Agora marco a task no tasks.md com o hash.

⏺ Bash(python3 - <<'EOF'
      p='specs/001-motor-reembolso/tasks.md'…)
  ⎿   specs/001-motor-reembolso/tasks.md | 4 ++--
      1 file changed, 2 insertions(+), 2 deletions(-)
     48-t030-moeda-na-entrada.md
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+2 -2)
      342    - **Casos de borda:** Moeda em minúsculas · Moeda de tipo er
           rado
      343    - **Commit:** d63fa0e
      344  
      345 -- [ ] **T-031** — Conversão: etapa 2 da seção 8, com `cotacao`
          - (T-026), `valor_considerado = arredondar(valor × taxa)` no co
          -ntexto exato (DT-012) e `cambio_indisponivel` (novo `Motivo`, 
          -na ordem da seção 8); `taxa_cambio` e `data_cotacao` na saída;
          - nulos e fora de `valor_solicitado` em `entrada_invalida` e `c
          -ambio_indisponivel`; justificativa para `cambio_indisponivel` 
          -e para a conversão (DT-009).                                  
      345 +- [x] **T-031** — Conversão: etapa 2 da seção 8, com `cotacao`
          + (T-026), `valor_considerado = arredondar(valor × taxa)` no co
          +ntexto exato (DT-012) e `cambio_indisponivel` (novo `Motivo`, 
          +na ordem da seção 8); `taxa_cambio` e `data_cotacao` na saída;
          + nulos e fora de `valor_solicitado` em `entrada_invalida` e `c
          +ambio_indisponivel`; justificativa para `cambio_indisponivel` 
          +e para a conversão (DT-009).                                  
      346    - **Tipo:** regra
      347    - **Atende:** RN-003 (conversão arredondada uma vez), RN-004
            (valor positivo em reais), RN-008 (mínimo comparado em reais)
           , RN-010 (moeda não comprova viagem; hospedagem estrangeira co
           mprova), RN-015, AMB-023, AMB-024, AMB-026, AMB-027, seção 4 d
           a spec (`taxa_cambio`, `data_cotacao`, `valor_considerado`, `t
           otais.valor_solicitado`), seção 8 (etapa 2)
      348    - **Depende de:** T-024, T-026, T-030
     ...
      361      - Ordem das etapas: sem cotação e fora do período → `cambi
           o_indisponivel`; sem cotação e valor negativo → `cambio_indisp
           onivel`; despesa inválida em EUR → `entrada_invalida` com `tax
           a_cambio` nula.
      362      - O teste de propriedade da DT-001 cobre `taxa_cambio`.
      363    - **Casos de borda:** Moeda nula · Moeda estrangeira com cot
           ação · Moeda estrangeira em sábado · Cotação exatamente 3 dias
            antes · Cotação 4 dias antes · Moeda sem cotação no arquivo ·
            Sem cotação e fora do período · Conversão arredondada uma vez
            · Nota fiscal comparada em reais · Valor estrangeiro minúscul
           o · Teto na moeda original · Moeda estrangeira não comprova vi
           agem · Hospedagem em moeda estrangeira · Data intermediária se
           m a moeda
      364 -  - **Commit:** —                                             
      364 +  - **Commit:** a56b1cd                                       
      365  
      366  - [ ] **T-032** — Duplicata com moeda: etapa 7 agrupa por (dat
           a, categoria, fornecedor, moeda, `valor` arredondado na moeda 
           da despesa).
      367    - **Tipo:** regra

⏺ A T-031 está commitada em a56b1cd; os hooks de pre-commit passaram (ruff
  limpo, 964 testes). No tasks.md, ela já está marcada [x] com o hash, mas essa
  alteração ainda não foi commitada.

  Para fechar o bloco, rode:

  /export docs/sessions/49-t031-conversao-moeda.md

  Quando me confirmar que exportou, faço um commit único docs(tasks): conclui 
  T-031 com o tasks.md e o export. Depois disso não começo a T-032 sem você
  pedir.

✻ Cogitated for 14s · done 3:43 PM