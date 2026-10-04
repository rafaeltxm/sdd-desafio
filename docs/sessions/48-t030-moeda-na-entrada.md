 ▐▛███▛█   Claude Code v2.1.287
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~/repo/sdd-desafio

  Get to finished work sooner with Opus 5.5. Switch anytime with /model.

❯ /clear                                                                        

❯ pode fazer a proxima task                                                     

⏺ Skill(task)
  ⎿  Successfully loaded skill

  Searched for 1 pattern, ran 1 shell command (ctrl+o to expand)

⏺ A próxima é a T-030 — Moeda na entrada (depende da T-029, que já está
  concluída). Vou começar por ela.

  Searched for 1 pattern, read 1 file, ran 5 shell commands (ctrl+o to expand)

⏺ Estou na T-030: já li a spec e o código atual, e agora vou escrever os testes
  de moeda antes de implementar.

  Searched for 1 pattern, ran 5 shell commands (ctrl+o to expand)

⏺ Agora vou ajustar os testes que já existem para o campo novo moeda, depois
  escrever os testes novos.

⏺ Bash(python3 - <<'EOF'
      import re…)
  ⎿  435:        # `moeda` ausente → BRL (RN-002, seção 4)
     436:        moeda="BRL",
     464:        moeda_saida=None,
     … +3 lines (ctrl+o to expand)
  ⎿  Updated tests/test_rn002_validacao_da_entrada.py (+6 -0)
      432          fornecedor="padaria_centro",
      433          # sem arredondamento: valor recebido (seção 4, `valor_
           informado`)
      434          valor_informado=Decimal("33.333"),
      435 +        # `moeda` ausente → BRL (RN-002, seção 4)             
      436 +        moeda="BRL",                                          
      437          tem_nota_fiscal=False,
      438          avisos=(),
      439      )
     ...
      461          data_texto=None,
      462          categoria_texto=None,
      463          valor_informado=None,
      464 +        moeda_saida=None,                                     
      465          avisos=(),
      466      )
      467  
     ...
      624          data_texto="2026-07-03",
      625          categoria_texto="alimentacao",
      626          valor_informado=Decimal("10.00"),
      627 +        moeda_saida="BRL",                                    
      628          avisos=(),
      629      )
      630  
     ...
      664          data_texto="2026-07-05",
      665          categoria_texto="alimentacao",
      666          valor_informado=Decimal("33.333"),
      667 +        moeda_saida="BRL",                                    
      668          avisos=(),
      669      )
      670  
     ...
      678              data_texto=None,
      679              categoria_texto=None,
      680              valor_informado=None,
      681 +            moeda_saida="BRL",                                
      682              avisos=(),
      683          )
      684      )

⏺ Bash(cat >> tests/test_rn002_validacao_da_entrada.py <<'EOF'…)
  ⎿  Updated tests/test_rn002_validacao_da_entrada.py (+102 -0)
       924      # limite 60,00: a recebe 40,00; c recebe min(30,00; 60,00
             − 40,00) = 20,00
       925      assert (a["status"], a["valor_reembolsado"]) == ("aprovad
            o", Decimal("40.00"))
       926      assert (c["status"], c["valor_reembolsado"]) == ("parcial
            ", Decimal("20.00"))
       927 +                                                             
       928 +                                                             
       929 +# --- moeda (T-030) ---                                      
       930 +                                                             
       931 +# Fora do formato "3 letras maiúsculas de A a Z", comparado c
           +omo veio (AMB-025)                                           
       932 +_MOEDAS_TEXTO_INVALIDAS = [                                  
       933 +    "eur", " EUR", "EUR ", "R$", "", "EURO", "EUR\n", "Eur", 
           +"EU", "ÉUR", "ＥＵＲ",                                       
       934 +]                                                            
       935 +                                                             
       936 +                                                             
       937 +@pytest.mark.parametrize("moeda", _MOEDAS_TEXTO_INVALIDAS)   
       938 +def test_rn002_moeda_texto_fora_do_formato_e_invalida_e_guard
           +ada_como_veio(                                               
       939 +    entrada, despesa, moeda                                  
       940 +):                                                           
       941 +    """RN-002 / AMB-025: `moeda` texto fora do formato, sem n
           +ormalização →                                                
       942 +    inválida; a saída copia o texto como veio (seção 4)."""  
       943 +    resultado = _uma(entrada, despesa(moeda=moeda))          
       944 +    assert isinstance(resultado, DespesaInvalida)            
       945 +    assert resultado.moeda_saida == moeda                    
       946 +                                                             
       947 +                                                             
       948 +@pytest.mark.parametrize("moeda", [978, True, ["EUR"], {"codi
           +go": "EUR"}])                                                
       949 +def test_rn002_moeda_nao_texto_e_invalida_e_sai_nula(entrada,
           + despesa, moeda):                                            
       950 +    """RN-002 / AMB-025: `moeda` que não é texto nem nula → i
           +nválida, nula na                                             
       951 +    saída (seção 4)."""                                      
       952 +    resultado = _uma(entrada, despesa(moeda=moeda))          
       953 +    assert isinstance(resultado, DespesaInvalida)            
       954 +    assert resultado.moeda_saida is None                     
       955 +                                                             
       956 +                                                             
       957 +def test_rn002_moeda_ausente_ou_nula_vale_brl(entrada, despes
           +a):                                                          
       958 +    """RN-002 / AMB-025: `moeda` ausente ou `null` → válida, 
           +`BRL`."""                                                    
       959 +    ausente = _uma(entrada, despesa())                       
       960 +    nula = _uma(entrada, despesa(moeda=None))                
       961 +    assert isinstance(ausente, Despesa) and isinstance(nula, 
           +Despesa)                                                     
       962 +    assert (ausente.moeda, nula.moeda) == ("BRL", "BRL")     
       963 +                                                             
     … 65 more lines (ctrl+o to expand)

⏺ Bash(python3 - <<'EOF'
      p='tests/test_saida.py'…)
  ⎿              fornecedor="padaria_centro",
                 # sem arredondamento: valor recebido (seção 4, `valor_info
     rmado`)
     … +17 lines (ctrl+o to expand)
  ⎿  Updated tests/test_casos_de_borda.py (+24 -0)
      203      _recusado_valor_invalido(item)
      204  
      205  
      206 +def _caso_moeda_em_minusculas(saida):                         
      207 +    # RN-002 / AMB-025: comparado como veio, sem normalização 
          +→ inválida                                                    
      208 +    (item,) = saida["itens"]                                  
      209 +    _recusado_entrada_invalida(item)                          
      210 +    assert item["moeda"] == "eur"                             
      211 +                                                              
      212 +                                                              
      213 +def _caso_moeda_de_tipo_errado(saida):                        
      214 +    # RN-002: não é texto nem nula → inválida, `moeda` nula na
          + saída                                                        
      215 +    (item,) = saida["itens"]                                  
      216 +    _recusado_entrada_invalida(item)                          
      217 +    assert item["moeda"] is None                              
      218 +                                                              
      219 +                                                              
      220  def _recusado_fora_do_periodo(item):
      221      # RN-005: recusado, `fora_do_periodo`, sem reembolso, nulo
           s de antes do limite
      222      assert (item["status"], item["motivo"]) == ("recusado", "f
           ora_do_periodo")
     ...
      817          _caso_alimentacao_antes_da_hospedagem,
      818          id="Alimentação antes da hospedagem na entrada, mesma 
           data",
      819      ),
      820 +    pytest.param(                                             
      821 +        _json(despesa(moeda="eur")),                          
      822 +        _caso_moeda_em_minusculas,                            
      823 +        id="Moeda em minúsculas",                             
      824 +    ),                                                        
      825 +    pytest.param(                                             
      826 +        _json(despesa(moeda=978)),                            
      827 +        _caso_moeda_de_tipo_errado,                           
      828 +        id="Moeda de tipo errado",                            
      829 +    ),                                                        
      830  ]
      831  
      832  
  ⎿  Updated tests/test_rastreabilidade.py (+0 -2)
      18  TASKS = SPEC.with_name("tasks.md")
      19  
      20  PENDENTES = {  # some quando a Fase 5 terminar (DT-016)
      21 -    "Moeda em minúsculas": "T-030",                            
      22 -    "Moeda de tipo errado": "T-030",                           
      21      "Moeda nula": "T-031",
      22      "Moeda estrangeira com cotação": "T-031",
      23      "Moeda estrangeira em sábado": "T-031",
  ⎿  Updated tests/test_saida.py (+4 -0)
      26      "data",
      27      "categoria",
      28      "valor_informado",
      29 +    "moeda",                                                   
      30      "valor_considerado",
      31      "valor_reembolsado",
      32      "status",
     ...
      45          data="2026-07-03",
      46          categoria="alimentacao",
      47          valor_informado=Decimal("45.00"),
      48 +        moeda="BRL",                                           
      49          valor_considerado=Decimal("45.00"),
      50          valor_reembolsado=Decimal("45.00"),
      51          status=Status.APROVADO,
     ...
      65          data=None,
      66          categoria=None,
      67          valor_informado=None,
      68 +        moeda=None,                                            
      69          valor_considerado=None,
      70          valor_reembolsado=Decimal("0"),
      71          status=Status.RECUSADO,
     ...
      216          "data",
      217          "categoria",
      218          "valor_informado",
      219 +        "moeda",                                              
      220          "valor_considerado",
      221          "em_viagem",
      222          "limite_diario",

  Ran 1 shell command (ctrl+o to expand)

⏺ Os testes novos falham pelo motivo certo (moeda ignorada, Despesa sem o
  campo). Agora a implementação.

⏺ Bash(python3 - <<'EOF'
      p='src/reembolso/modelo.py'…)
  ⎿  3
     ......................................................................
     .. [ 94%]
     … +4 lines (ctrl+o to expand)
  ⎿  Updated src/reembolso/entrada.py (+12 -3)
       6  from reembolso.leitura import (
       7      ErroDeArquivo,
       8      ObjetoJson,
       9 +    e_codigo_de_moeda,                                         
      10      e_data,
      11      e_numero,
      12      ler_json,
     ...
      14  )
      15  from reembolso.modelo import Colaborador, Despesa, DespesaInval
          ida, Entrada, Periodo
      16  from reembolso.normalizacao import normalizar_texto
      16 -from reembolso.politica import VALOR_ABSOLUTO_MAXIMO           
      17 +from reembolso.politica import MOEDA_BASE, VALOR_ABSOLUTO_MAXIM
         +O                                                              
      18  
      19  
      20  def _aviso(caminho: str, n: int) -> str:
     ...
      123  ) -> Despesa | DespesaInvalida:
      124      """Etapa 1 da seção 8: elemento de `despesas` → `Despesa` 
           ou `DespesaInvalida`.
      125  
      125 -    Aplica a RN-002 (despesa inválida) e o teto da AMB-018 ao 
          -número recebido.                                              
      126 +    Aplica a RN-002 (despesa inválida), o teto da AMB-018 ao n
          +úmero recebido e                                              
      127 +    o formato da `moeda` (AMB-025).                           
      128      """
      129      if not isinstance(elemento, dict):
      128 -        return DespesaInvalida(posicao, None, None, None, None
          -, avisos)                                                     
      130 +        return DespesaInvalida(posicao, None, None, None, None
          +, None, avisos)                                               
      131  
      132      id_ = elemento.get("id")
      133      data_texto = elemento.get("data")
     ...
      135      fornecedor = elemento.get("fornecedor")
      136      valor = elemento.get("valor")
      137      tem_nota_fiscal = elemento.get("tem_nota_fiscal")
      138 +    # ausente ou nula → BRL; senão comparada como veio, sem no
          +rmalização (AMB-025)                                          
      139 +    moeda = elemento.get("moeda")                             
      140 +    if moeda is None:                                         
      141 +        moeda = MOEDA_BASE                                    
      142  
      143      data = e_data(data_texto)
      144      valida = (
     ...
      152          # `copy_abs` é exato, sem o arredondamento do contexto
            decimal
      153          and Decimal(valor).copy_abs() < VALOR_ABSOLUTO_MAXIMO
     … 19 more lines (ctrl+o to expand)
  ⎿  Updated src/reembolso/modelo.py (+4 -1)
      52      categoria_texto: str  # como veio
      53      categoria: str  # normalizada (seção 5 da spec)
      54      fornecedor: str  # normalizado
      55 -    valor_informado: Decimal                                   
      55 +    valor_informado: Decimal  # na moeda da despesa            
      56 +    moeda: str  # "BRL" se ausente ou nula; senão 3 letras A–Z 
      57      tem_nota_fiscal: bool
      58      avisos: tuple[str, ...]  # RN-013
      59  
     ...
      67      data_texto: str | None
      68      categoria_texto: str | None  # como veio, se texto; o motor
           decide a saída
      69      valor_informado: Decimal | None
      70 +    moeda_saida: str | None  # "BRL" se ausente/nula; como veio
         +, se texto; senão None                                         
      71      avisos: tuple[str, ...]
      72  
      73  
     ...
      125      data: str | None
      126      categoria: str | None
      127      valor_informado: Decimal | None
      128 +    moeda: str | None                                         
      129      valor_considerado: Decimal | None
      130      valor_reembolsado: Decimal
      131      status: Status
  ⎿  Updated src/reembolso/motor.py (+3 -0)
      53          data=despesa.data_texto,
      54          categoria=categoria,
      55          valor_informado=despesa.valor_informado,
      56 +        moeda=despesa.moeda_saida,                             
      57          valor_considerado=None,
      58          valor_reembolsado=ZERO,
      59          status=status,
     ...
      89          data=despesa.data_texto,
      90          categoria=categoria,
      91          valor_informado=despesa.valor_informado,
      92 +        moeda=despesa.moeda,                                   
      93          valor_considerado=considerado,
      94          valor_reembolsado=ZERO,
      95          status=status,
     ...
      200              data=despesa.data_texto,
      201              categoria=despesa.categoria,
      202              valor_informado=despesa.valor_informado,
      203 +            moeda=despesa.moeda,                              
      204              valor_considerado=considerado,
      205              valor_reembolsado=reembolsado,
      206              status=status,
  ⎿  Updated src/reembolso/saida.py (+1 -0)
      12          "data": item.data,
      13          "categoria": item.categoria,
      14          "valor_informado": item.valor_informado,
      15 +        "moeda": item.moeda,                                   
      16          "valor_considerado": item.valor_considerado,
      17          "valor_reembolsado": item.valor_reembolsado,
      18          "status": item.status.value,

⏺ Suíte verde (919 passed) e ruff limpo. Vou conferir o diff e chamar o revisor
  independente.

  Ran 1 shell command (ctrl+o to expand)

⏺ revisor-de-task(Revisão da T-030)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ A implementação da T-030 está pronta: 919 testes passando e ruff limpo. O
  revisor independente (revisor-de-task) está rodando agora. Quando ele
  terminar, salvo o parecer em docs/reviews/T-030.md e te trago o resumo para
  aprovação antes do commit.

✻ Sautéed for 2m 15s · done 3:31 PM

› Message from revisor-de-task
  # Revisão T-030 — Moeda na entrada: validação na etapa 1 e `itens[].moeda` na
  saída

  - **Data:** 2026-10-04
  - **Regras conferidas:** RN-002 (`moeda`), RN-015 (1º item: ausente/nulo =
  BRL, formato inválido = `entrada_invalida`), AMB-025, seção 4
  (`despesas[].moeda`, `itens[].moeda`, ordem dos campos), seção 7 ("Moeda em
  minúsculas", "Moeda de tipo errado")
  - **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 919 passed, 0
  failed (evidência, não veredito)

  ### Resultado
  **APROVADO COM RESSALVAS** — todos os critérios de aceite foram atendidos e o
  comportamento bate com a spec. As ressalvas são de cobertura e
  rastreabilidade, nenhuma bloqueia.

  ### Critérios de aceite
  | # | Critério | Status | Evidência |
  |---|---|---|---|
  | 1 | `"eur"`, `" EUR"`, `"EUR "`, `"R$"`, `""`, `"EURO"` →
  `entrada_invalida`, `moeda` como veio | atendido | `tests/test_rn002_validacao
  _da_entrada.py::test_rn002_moeda_fora_do_formato_sai_entrada_invalida` (passa
  pela saída, com `_invalido` e `valor_solicitado` 0) e
  `::test_rn002_moeda_texto_fora_do_formato_e_invalida_e_guardada_como_veio`
  (também `"EUR\n"`, `"Eur"`, `"EU"`, `"ÉUR"` e `"ＥＵＲ"` de largura cheia);
  `src/reembolso/leitura.py:90` usa `[A-Z]{3}` com `fullmatch`, sem normalização
  |
  | 2 | `978`, `true`, lista → `entrada_invalida`, `moeda` nula | atendido |
  `::test_rn002_moeda_fora_do_formato_sai_entrada_invalida` (978, True,
  `["EUR"]` → None); `::test_rn002_moeda_nao_texto_e_invalida_e_sai_nula`
  (também dict); `src/reembolso/entrada.py` `moeda_saida=moeda if
  isinstance(moeda, str) else None` |
  | 3 | ausente e `null` → válida, `moeda` `BRL` | atendido |
  `::test_rn002_moeda_ausente_ou_nula_vale_brl`,
  `::test_rn002_moeda_valida_sai_na_saida`; `entrada.py:139-141` |
  | 4 | `"USD"` → válida, `moeda` `USD` | atendido |
  `::test_rn002_moeda_valida_sai_na_saida`,
  `::test_rn002_moeda_com_3_letras_maiusculas_e_valida` (inclui `XYZ`, válida na
  etapa 1 conforme RN-015 "Não há lista própria de códigos ISO") |
  | 5 | elemento que não é objeto → `moeda` nula | atendido |
  `::test_rn002_elemento_que_nao_e_objeto_sai_com_moeda_nula` (`null` e
  `"EUR"`); `entrada.py` retorna `DespesaInvalida(..., None, ...)` |
  | 6 | inválida por outro campo com `"moeda": "EUR"` → `moeda` `EUR` | atendido
  | `::test_rn002_invalida_por_outro_campo_sai_com_a_moeda`,
  `::test_rn002_despesa_invalida_por_outro_campo_guarda_a_moeda` (também sem
  `moeda` → `BRL`, como diz a seção 4) |
  | 7 | `tests/test_saida.py` passa com `moeda` na posição da seção 4 | atendido
  | `tests/test_saida.py` `CAMPOS_DO_ITEM` tem `moeda` logo depois de
  `valor_informado`; `src/reembolso/saida.py` usa a mesma ordem. `taxa_cambio` e
  `data_cotacao`, que na seção 4 vêm entre `moeda` e `valor_considerado`, são
  da T-031 |
  | 8 | Casos de borda "Moeda em minúsculas" e "Moeda de tipo errado" | atendido
  | `tests/test_casos_de_borda.py` (ids com o nome exato dos casos; o esperado
  bate com a seção 7, linhas 684-685); retirados de `PENDENTES` em
  `tests/test_rastreabilidade.py` |

  Recalculei à mão, a partir da seção 4 e da RN-002, o esperado de cada
  parâmetro dos testes novos. Todos batem: texto vale como veio, não-texto sai
  nulo, ausente/nulo sai `BRL` e inválido sai fora de `valor_solicitado`.

  ### Problemas encontrados
  #### 1. `moeda` de despesa válida que depois é recusada (caminho
  `_item_recusado`) não tem teste — severidade MÉDIA
  - **Regra afetada:** seção 4 (`itens[].moeda`: "como veio, se for texto"),
  RN-015
  - **Evidência:** `src/reembolso/motor.py` (`_item_recusado`,
  `moeda=despesa.moeda`). Os testes de saída novos só passam por
  `_item_invalido` (inválidas) e por `_aplicar_limite`
  (`test_rn002_moeda_valida_sai_na_saida`, item avaliado). Nenhum teste confere
  `moeda` num item recusado por `fora_do_periodo`, `valor_invalido`,
  `nota_fiscal_ausente`, `categoria_fora_da_politica` ou `duplicata`.
  - **Impacto:** se esse caminho omitir ou trocar a moeda, a suíte não percebe.
  Hoje o código está correto.
  - **Recomendação:** acrescentar um teste com despesa válida em `"USD"` (ou
  `null`) recusada por uma regra anterior ao limite, verificando `moeda` `USD`
  (ou `BRL`) na saída.

  #### 2. Moeda estrangeira válida é processada como reais até a T-031 —
  severidade BAIXA
  - **Regra afetada:** RN-015, RN-003 (conversão)
  - **Evidência:** com esta task, `"moeda": "USD"` passa na etapa 1 e o motor
  usa `valor_informado` sem conversão (taxa implícita 1). A etapa 2 (conversão e
  `cambio_indisponivel`) é da T-031, que depende desta.
  - **Impacto:** é um estado intermediário, previsto pela ordem das tasks: entre
  a T-030 e a T-031 o resultado para moeda estrangeira está errado. Não é
  desvio desta task.
  - **Recomendação:** nada a corrigir aqui. Só registro para que a T-031 não
  seja esquecida antes de qualquer uso real.

  #### 3. Rastreabilidade em uma docstring — severidade BAIXA
  - **Regra afetada:** convenção de testes (docstring `"""RN-NNN / AMB-NNN:
  ..."""`)
  - **Evidência:** `tests/test_rn002_validacao_da_entrada.py::test_rn002_element
  o_que_nao_e_objeto_sai_com_moeda_nula` tem docstring `"Seção 4: ..."`, sem
  RN-002.
  - **Impacto:** nenhum no resultado.
  - **Recomendação:** começar a docstring por `RN-002 / seção 4:`.

  ### Cobertura
  - **Regras testadas:**
    - RN-002 (`moeda`) / AMB-025 →
  `test_rn002_moeda_texto_fora_do_formato_e_invalida_e_guardada_como_veio`,
  `test_rn002_moeda_nao_texto_e_invalida_e_sai_nula`,
  `test_rn002_moeda_ausente_ou_nula_vale_brl`,
  `test_rn002_moeda_com_3_letras_maiusculas_e_valida`,
  `test_rn002_despesa_invalida_por_outro_campo_guarda_a_moeda`,
  `test_rn002_moeda_fora_do_formato_sai_entrada_invalida`
    - Seção 4 (`itens[].moeda`) → `test_rn002_moeda_valida_sai_na_saida`,
  `test_rn002_elemento_que_nao_e_objeto_sai_com_moeda_nula`,
  `test_rn002_invalida_por_outro_campo_sai_com_a_moeda`, `tests/test_saida.py`
  (ordem e nulos)
  - **Casos de borda cobertos:** minúsculas, espaço antes/depois, `\n` no fim,
  `R$`, vazio, 4 letras, 2 letras, acento, letras de largura cheia, número,
  booleano, lista, objeto, ausente, `null`, código inexistente (`XYZ`) válido na
  etapa 1, elemento não-objeto, inválida por outro campo (com e sem `moeda`);
  "Moeda em minúsculas" e "Moeda de tipo errado" em `test_casos_de_borda.py`.
  - **Casos que parecem faltar:** `moeda` na saída de despesa válida recusada
  por regra anterior ao limite (seção 4; problema 1).

  ### Decisões necessárias
  Nenhuma.

  ### Antes de concluir a task
  Nenhum item bloqueia: pode seguir para o commit. Antes dele, recomendo:
  - o teste de `moeda` num item recusado por regra posterior à etapa 1 (problema
  1);
  - RN-002 na docstring de
  `test_rn002_elemento_que_nao_e_objeto_sai_com_moeda_nula` (problema 3).

  Arquivos conferidos:
  /Users/rafaeltxm/repo/sdd-desafio/src/reembolso/entrada.py,
  /Users/rafaeltxm/repo/sdd-desafio/src/reembolso/modelo.py,
  /Users/rafaeltxm/repo/sdd-desafio/src/reembolso/motor.py,
  /Users/rafaeltxm/repo/sdd-desafio/src/reembolso/saida.py,
  /Users/rafaeltxm/repo/sdd-desafio/src/reembolso/leitura.py,
  /Users/rafaeltxm/repo/sdd-desafio/tests/test_rn002_validacao_da_entrada.py,
  /Users/rafaeltxm/repo/sdd-desafio/tests/test_casos_de_borda.py,
  /Users/rafaeltxm/repo/sdd-desafio/tests/test_saida.py,
  /Users/rafaeltxm/repo/sdd-desafio/tests/test_rastreabilidade.py,
  /Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md,
  /Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md,
  /Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/tasks.md

⏺ Write(docs/reviews/T-030.md)
  ⎿  Wrote 58 lines to docs/reviews/T-030.md
       1 # Revisão T-030 — Moeda na entrada: validação na etapa 1 e `iten
       2 
       4 - **Regras conferidas:** RN-002 (`moeda`), RN-015 (1º item: ause
         nte/nulo = BRL, formato inválido = `entrada_invalida`), AMB-025,
         , seção 7 ("Moeda em minúsculas", "Moeda de tipo errado")
         19 passed, 0 failed (evidência, não veredito)
       7 ### Resultado
       8 **APROVADO COM RESSALVAS** — todos os critérios de aceite foram 
          cobertura e rastreabilidade, nenhuma bloqueia.
      10 ### Critérios de aceite
     … +134 lines (ctrl+o to expand)

⏺ Agent "Revisão da T-030" finished · 55s

⏺ Parecer salvo. Agora corrijo as ressalvas 1 e 3, que são do escopo da task.

⏺ Bash(python3 - <<'EOF'
      p='tests/test_rn002_validacao_da_entrada.py'…)
  ⎿  922 passed in 0.61s
     All checks passed!
  ⎿  Updated tests/test_rn002_validacao_da_entrada.py (+15 -1)
      1011  
      1012  
      1013  def test_rn002_elemento_que_nao_e_objeto_sai_com_moeda_nula(p
            rocessar):
      1014 -    """Seção 4: elemento que não é objeto → `moeda` nula.""" 
      1014 +    """RN-002 / seção 4: elemento que não é objeto → `moeda` 
           +nula."""                                                     
      1015      saida = processar(
      1016          '{"colaborador": {"id": "c-1", "nome": "Ana"}, '
      1017          '"periodo": {"inicio": "2026-07-01", "fim": "2026-07-
            31"}, '
     ...
      1026      (item,) = avaliar(_sem_nota(moeda="EUR"))["itens"]
      1027      _invalido(item)
      1028      assert item["moeda"] == "EUR"
      1029 +                                                             
      1030 +                                                             
      1031 +@pytest.mark.parametrize(("documento", "esperada"), [        
      1032 +    ({"moeda": "USD"}, "USD"), ({"moeda": None}, "BRL"), ({},
           + "BRL"),                                                     
      1033 +])                                                           
      1034 +def test_rn002_moeda_sai_em_item_recusado_depois_da_etapa_1( 
      1035 +    avaliar, despesa, documento, esperada                    
      1036 +):                                                           
      1037 +    """RN-002 / seção 4: despesa válida recusada numa etapa p
           +osterior à 1                                                 
      1038 +    (fora do período, RN-005) → `moeda` como na validação."""
      1039 +    (item,) = avaliar(despesa(data="2026-08-01", **documento)
           +)["itens"]                                                   
      1040 +    # período de 01/07 a 31/07: 01/08 → `fora_do_periodo` (et
           +apa 4)                                                       
      1041 +    assert item["motivo"] == "fora_do_periodo"               
      1042 +    assert item["moeda"] == esperada                         

⏺ Resumo — T-030: Moeda na entrada

  Arquivos alterados:
  - src/reembolso/modelo.py (modificado): Despesa.moeda,
    DespesaInvalida.moeda_saida, ItemResultado.moeda, com os nomes da seção 3 do
    plan
  - src/reembolso/entrada.py (modificado): validação de moeda na etapa 1 com
    e_codigo_de_moeda, que já existia
  - src/reembolso/motor.py (modificado): moeda repassada nos três tipos de item
  - src/reembolso/saida.py (modificado): moeda logo depois de valor_informado
  - tests/test_rn002_validacao_da_entrada.py, tests/test_saida.py,
    tests/test_casos_de_borda.py, tests/test_rastreabilidade.py (modificados)
  - docs/reviews/T-030.md (novo)

  Testes criados/alterados:
  - test_rn002_moeda_texto_fora_do_formato_e_invalida_e_guardada_como_veio →
    RN-002 / AMB-025
  - test_rn002_moeda_nao_texto_e_invalida_e_sai_nula → RN-002 / AMB-025
  - test_rn002_moeda_ausente_ou_nula_vale_brl → RN-002 / AMB-025
  - test_rn002_moeda_com_3_letras_maiusculas_e_valida → RN-002 (XYZ também passa
    na etapa 1; a falta de cotação fica para a etapa 2)
  - test_rn002_despesa_invalida_por_outro_campo_guarda_a_moeda e
    test_rn002_invalida_por_outro_campo_sai_com_a_moeda → RN-002 / seção 4
  - test_rn002_moeda_fora_do_formato_sai_entrada_invalida → RN-002, pela saída,
    fora dos totais
  - test_rn002_moeda_valida_sai_na_saida → seção 4
  - test_rn002_elemento_que_nao_e_objeto_sai_com_moeda_nula → seção 4
  - test_rn002_moeda_sai_em_item_recusado_depois_da_etapa_1 → seção 4 (pedido
    pelo revisor)
  - Casos de borda "Moeda em minúsculas" e "Moeda de tipo errado", que saíram de
    PENDENTES
  - Testes que já existiam com Despesa/DespesaInvalida/ItemResultado e a ordem
    dos campos em test_saida.py foram atualizados com moeda.

  Testes executados antes da implementação: os novos falharam pelo motivo certo:
  moeda era ignorada, a despesa passava como válida e Despesa ainda não tinha o
  atributo.

  Testes executados depois: uv run pytest -q, uv run ruff check .

  pytest: 922 passed, 0 failed

  ruff: limpo

  Revisão independente: APROVADO COM RESSALVAS, parecer em
  docs/reviews/T-030.md.
  - Ressalva MÉDIA: faltava teste de moeda em item recusado depois da etapa 1.
    Corrigido.
  - Ressalva BAIXA: faltava RN-002 numa docstring. Corrigido.
  - Ressalva BAIXA, fora do escopo: ver "Lacunas".
  - Decisões necessárias: nenhuma.
  - As correções vieram depois do parecer, e o revisor não rodou de novo.

  Decisões ou interpretações realizadas: nenhuma. Testei casos além do aceite
  ("EUR\n", "Eur", "EU", "ÉUR", "ＥＵＲ", objeto); todos saem direto da regra
  "exatamente 3 letras maiúsculas de A a Z, como veio" (RN-002 e DT-003 do
  plan).

  Lacunas ou dúvidas: até a T-031, uma despesa válida em moeda estrangeira (ex.:
  USD) é calculada como se fosse em reais, sem conversão e sem
  cambio_indisponivel. É o estado intermediário previsto pela ordem das tasks.
  taxa_cambio e data_cotacao também ficam para a T-031.

  Commit proposto: feat(T-030): moeda validada na entrada e copiada na saída

  Posso fazer o commit?

✻ Baked for 3m 58s · done 3:32 PM

❯ pode commitar                                                                 

  Ran 1 shell command (ctrl+o to expand)
⏺ Bash(python3 - <<'EOF'
      p='specs/001-motor-reembolso/tasks.md'…)
  ⎿   specs/001-motor-reembolso/tasks.md | 4 ++--
      1 file changed, 2 insertions(+), 2 deletions(-)
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+2 -2)
      326    - **Casos de borda:** Centro de custo da tabela · Centro de 
           custo fora da tabela · Centro de custo com grafia diferente · 
           Centro de custo só com espaços · Centro de custo de tipo errad
           o · Categoria ausente da tabela do centro de custo · Categoria
            com limite zero · Representação fora do centro de custo que a
            define · Representação não amplia em viagem · Limite em viage
           m truncado · Política sem versão nem vigência
      327    - **Commit:** 7e38a46
      328  
      329 -- [ ] **T-030** — Moeda na entrada: `moeda` validada na etapa 
          -1 (`Despesa.moeda`, `BRL` se ausente ou nula; `entrada_invalid
          -a` fora do formato) e `itens[].moeda` na saída (`BRL`, como ve
          -io se texto, ou nula).                                        
      329 +- [x] **T-030** — Moeda na entrada: `moeda` validada na etapa 
          +1 (`Despesa.moeda`, `BRL` se ausente ou nula; `entrada_invalid
          +a` fora do formato) e `itens[].moeda` na saída (`BRL`, como ve
          +io se texto, ou nula).                                        
      330    - **Tipo:** regra
      331    - **Atende:** RN-002 (`moeda`), AMB-025, seção 4 da spec (`i
           tens[].moeda`)
      332    - **Substitui:** T-009 (validação de `moeda`)
     ...
      340      - despesa inválida por outro campo com `"moeda": "EUR"` → 
           `moeda` `EUR`.
      341      `tests/test_saida.py` passa com `moeda` na posição da seçã
           o 4.
      342    - **Casos de borda:** Moeda em minúsculas · Moeda de tipo er
           rado
      343 -  - **Commit:** —                                             
      343 +  - **Commit:** d63fa0e                                       
      344  
      345  - [ ] **T-031** — Conversão: etapa 2 da seção 8, com `cotacao`
            (T-026), `valor_considerado = arredondar(valor × taxa)` no co
           ntexto exato (DT-012) e `cambio_indisponivel` (novo `Motivo`, 
           na ordem da seção 8); `taxa_cambio` e `data_cotacao` na saída;
            nulos e fora de `valor_solicitado` em `entrada_invalida` e `c
           ambio_indisponivel`; justificativa para `cambio_indisponivel` 
           e para a conversão (DT-009).
      346    - **Tipo:** regra

⏺ A T-030 está commitada como d63fa0e. Os hooks rodaram ruff e pytest antes do
  commit, e os 922 testes passaram. Também já marquei a task como [x] no
  tasks.md, com o hash.

  Para fechar o bloco, preciso que você exporte a sessão:

  /export docs/sessions/48-t030-moeda-na-entrada.md

  Quando confirmar que exportou, faço o commit docs(tasks): conclui T-030 junto
  com o export.

✻ Baked for 12s · done 3:33 PM