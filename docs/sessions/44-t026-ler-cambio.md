 ▐▛███▛█   Claude Code v2.1.287
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~/repo/sdd-desafio

  Get to finished work sooner with Opus 5.5. Switch anytime with /model.

❯ /clear                                                                        

❯ pode fazer a proxima task T-026                                               

⏺ Skill(task)
  ⎿  Successfully loaded skill

  Searched for 1 pattern, ran 1 shell command (ctrl+o to expand)

⏺ Now the spec rules.

  Ran 3 shell commands (ctrl+o to expand)

⏺ Now the existing code: politica.py, modelo.py, leitura.py, conftest, the rn016
  tests and the envelope câmbio.

  Ran 3 shell commands (ctrl+o to expand)

⏺ Tenho o contexto. T-026 depende só da T-023 (concluída). Vou escrever os
  testes primeiro.

  Ran 1 shell command (ctrl+o to expand)

⏺ Agora o construtor no conftest e os testes.

⏺ Update(tests/conftest.py)
  ⎿  Added 33 lines
       89      return documento
       90  
       91  
       92 +def construir_cambio(**sobrescritas):                         
       93 +    """`exemplos/envelope/cambio.json` transcrito (plan seção 
          +6).                                                           
       94 +                                                              
       95 +    Os campos passados sobrescrevem os da raiz (ex. `taxas=...
          +`); cada chamada                                              
       96 +    devolve um documento novo, que o teste pode alterar.      
       97 +    """                                                       
       98 +    cotacoes = {                                              
       99 +        "2026-07-13": ("5.42", "5.91"),                       
      100 +        "2026-07-14": ("5.44", "5.93"),                       
      101 +        "2026-07-15": ("5.39", "5.88"),                       
      102 +        "2026-07-16": ("5.41", "5.90"),                       
      103 +        "2026-07-17": ("5.47", "5.96"),                       
      104 +        "2026-07-20": ("5.50", "6.01"),                       
      105 +        "2026-07-21": ("5.48", "5.99"),                       
      106 +        "2026-07-22": ("5.45", "5.95"),                       
      107 +        "2026-07-23": ("5.44", "5.94"),                       
      108 +        "2026-07-24": ("5.46", "5.97"),                       
      109 +        "2026-07-27": ("5.52", "6.03"),                       
      110 +        "2026-07-28": ("5.51", "6.02"),                       
      111 +    }                                                         
      112 +    documento = {                                             
      113 +        "moeda_base": "BRL",                                  
      114 +        "fonte": "Banco Central - PTAX de fechamento",        
      115 +        "observacao": "Cotacoes publicadas apenas em dias utei
          +s bancarios.",                                                
      116 +        "taxas": {                                            
      117 +            data: {"USD": Decimal(usd), "EUR": Decimal(eur)}  
      118 +            for data, (usd, eur) in cotacoes.items()          
      119 +        },                                                    
      120 +    }                                                         
      121 +    documento.update(sobrescritas)                            
      122 +    return documento                                          
      123 +                                                              
      124 +                                                              
      125  @pytest.fixture
      126  def despesa():
      127      return construir_despesa

⏺ Write(tests/test_rn015_moeda_e_cambio.py)
  ⎿  Wrote 100 lines to tests/test_rn015_moeda_e_cambio.py
       1 """Busca da cotação: RN-015, AMB-024, AMB-025, DT-014.
       2 
       3 Salvo indicação, o câmbio é o `cambio.json` do envelope (`constr
       4 com cotações de USD e EUR só em dias úteis, de 13/07 (segunda) a
          28/07.
       5 """
       6 
       8 from decimal import Decimal
       9 
      10 import pytest
     … +105 lines (ctrl+o to expand)

⏺ Agora os testes do câmbio na RN-016.

⏺ Bash(python3 - <<'EOF'
      p='tests/test_rn016_arquivos_de_politica_e_cambio.py'…)
  ⎿  3:from decimal import Decimal
     5:import pytest
     6:import simplejson
     … +4 lines (ctrl+o to expand)
  ⎿  Updated tests/test_rn016_arquivos_de_politica_e_cambio.py (+163 -1)
       5  import pytest
       6  import simplejson
       7  
       8 -from conftest import construir_politica                        
       8 +from conftest import construir_cambio, construir_politica      
       9 +from reembolso.cambio import ler_cambio                        
      10  from reembolso.leitura import ErroDeArquivo
      11  from reembolso.politica import ler_politica
      12  
     ...
      389      """RN-016: a chave de `centros_custo` fica como veio (plan
            seção 4)."""
      390      documento = construir_politica(centros_custo={" cc-adm ": 
           {}})
      391      assert list(ler_politica(_bytes(documento)).centros_custo)
            == [" cc-adm "]
      392 +                                                              
      393 +                                                              
      394 +# --- câmbio -------------------------------------------------
          +------------------                                            
      395 +                                                              
      396 +                                                              
      397 +def _cambio_com(caminho, valor):                              
      398 +    """Câmbio do envelope com `valor` no `caminho` (tupla de c
          +haves) da raiz."""                                            
      399 +    documento = construir_cambio()                            
      400 +    alvo = documento                                          
      401 +    for chave in caminho[:-1]:                                
      402 +        alvo = alvo[chave]                                    
      403 +    alvo[caminho[-1]] = valor                                 
      404 +    return documento                                          
      405 +                                                              
      406 +                                                              
      407 +def _erro_no_cambio(conteudo: bytes) -> str:                  
      408 +    with pytest.raises(ErroDeArquivo) as erro:                
      409 +        ler_cambio(conteudo)                                  
      410 +    return str(erro.value)                                    
      411 +                                                              
      412 +                                                              
      413 +@pytest.mark.parametrize(                                     
      414 +    ("documento", "campo"),                                   
      415 +    [                                                         
      416 +        pytest.param([], "raiz", id="raiz_lista"),            
      417 +        pytest.param(construir_cambio(moeda_base="USD"), "moed
          +a_base", id="moeda_base_usd"),                                
      418 +        pytest.param(construir_cambio(moeda_base="brl"), "moed
          +a_base", id="moeda_base_minuscula"),                          
      419 +        pytest.param(construir_cambio(taxas=None), "taxas", id
          +="taxas_nulas"),                                              
     … 133 more lines (ctrl+o to expand)

⏺ Bash(sed -i '' 's/^from decimal import Decimal$/from datetime import
      date\nfrom decimal import Decimal/'
      tests/test_rn016_arquivos_de_politica_e_cambio.py && grep -n…)
  ⎿  422:            {"moeda_base": "BRL", "fonte": "PTAX"}, "taxas", id="t
     axas_ausentes"
     515:    texto = _bytes(construir_cambio()).replace(b"PTAX", b"PT\xe9X"
     … +8 lines (ctrl+o to expand)
  ⎿  Updated tests/test_rn016_arquivos_de_politica_e_cambio.py (+1 -0)
      1  """Arquivos de política e de câmbio: RN-016, AMB-029, AMB-031, D
         T-015."""
      2  
      3 +from datetime import date                                       
      4  from decimal import Decimal
      5  
      6  import pytest

  Ran 1 shell command (ctrl+o to expand)

⏺ Falham pelo motivo esperado (módulo cambio ainda não existe). Implementando.

⏺ Update(src/reembolso/modelo.py)
  ⎿  Added 15 lines
       93  
       94  
       95  @dataclass(frozen=True)
       96 +class Cambio:                                                 
       97 +    """Arquivo de câmbio validado (RN-016), sem a entrada `BRL
          +` (ignorada)."""                                              
       98 +                                                              
       99 +    taxas: Mapping[date, Mapping[str, Decimal]]               
      100 +                                                              
      101 +                                                              
      102 +@dataclass(frozen=True)                                       
      103 +class Cotacao:                                                
      104 +    """Taxa usada na conversão (RN-015); `data` é `None` para 
          +`BRL`."""                                                     
      105 +                                                              
      106 +    taxa: Decimal                                             
      107 +    data: date | None                                         
      108 +                                                              
      109 +                                                              
      110 +@dataclass(frozen=True)                                       
      111  class ItemResultado:
      112      """Espelha `itens[]` da seção 4 da spec, campo a campo."""
      113  

⏺ Write(src/reembolso/cambio.py)
  ⎿  Wrote 81 lines to src/reembolso/cambio.py
       1 """Leitura do arquivo de câmbio e busca da cotação (plan seção 4
         , DT-014, DT-015)."""
       2 
       3 from datetime import date, timedelta
       4 from decimal import Decimal
       6 
       7 from reembolso.leitura import (
       8     ErroDeArquivo,
       9     e_codigo_de_moeda,
      10     e_data,
     … +79 lines (ctrl+o to expand)

⏺ Bash(sed -i '' '/^    "RN-015": "T-026",$/d' tests/test_rastreabilidade.py &&
      uv run pytest -q tests/test_rn015_moeda_e_cambio.py
      tests/test_rn016_arquivos_de_politi…)
  ⎿  ......................................................................
     .. [ 75%]
     ........................
     … +49 lines (ctrl+o to expand)
  ⎿  Updated tests/test_rastreabilidade.py (+0 -1)
      19  
      20  PENDENTES = {  # some quando a Fase 5 terminar (DT-016)
      21      "RN-014": "T-027",
      22 -    "RN-015": "T-026",                                         
      22      "Centro de custo reservado no arquivo": "T-028",
      23      "Política sem tabela padrão": "T-028",
      24      "Limite inválido na política": "T-028",

⏺ Bash(python3 - <<'EOF'
      p='tests/test_rn015_moeda_e_cambio.py'…)
  ⎿  E501 Line too long (89 > 88)
       --> tests/test_rn015_moeda_e_cambio.py:88:89
     E501 Line too long (91 > 88)
     … +2 lines (ctrl+o to expand)
  ⎿  Updated tests/test_rn015_moeda_e_cambio.py (+1 -1)
      85      ],
      86  )
      87  def test_rn015_brl_tem_taxa_1_sem_consultar_o_arquivo(taxas):
      88 -    """RN-015 / AMB-025: BRL → taxa 1 e data nula; a entrada BR
         -L do arquivo é ignorada."""                                    
      88 +    """RN-015 / AMB-025: BRL → taxa 1, data nula; a entrada BRL
         + do arquivo é ignorada."""                                     
      89      assert cotacao(_cambio(taxas=taxas), "BRL", date(2026, 7, 1
          4)) == Cotacao(
      90          Decimal(1), None
      91      )
  ⎿  Updated tests/test_rn016_arquivos_de_politica_e_cambio.py (+7 -3)
      415      ("documento", "campo"),
      416      [
      417          pytest.param([], "raiz", id="raiz_lista"),
      418 -        pytest.param(construir_cambio(moeda_base="USD"), "moed
          -a_base", id="moeda_base_usd"),                                
      419 -        pytest.param(construir_cambio(moeda_base="brl"), "moed
          -a_base", id="moeda_base_minuscula"),                          
      418 +        pytest.param(                                         
      419 +            construir_cambio(moeda_base="USD"), "moeda_base", 
          +id="moeda_base_usd"                                           
      420 +        ),                                                    
      421 +        pytest.param(                                         
      422 +            construir_cambio(moeda_base="brl"), "moeda_base", 
          +id="moeda_base_minuscula"                                     
      423 +        ),                                                    
      424          pytest.param(construir_cambio(taxas=None), "taxas", id
           ="taxas_nulas"),
      425          pytest.param(
      426              {"moeda_base": "BRL", "fonte": "PTAX"}, "taxas", i
           d="taxas_ausentes"
     ...
      538      ],
      539  )
      540  def test_rn016_brl_e_campos_nao_listados_ignorados_sem_validac
           ao(brl):
      537 -    """RN-016 / RN-015: a entrada BRL de uma data e `fonte`/`o
          -bservacao` são ignoradas."""                                  
      541 +    """RN-016 / RN-015: a entrada BRL de uma data, `fonte` e `
          +observacao` são ignoradas."""                                 
      542      documento = construir_cambio(fonte=Decimal("1e999999"), ob
           servacao=[])
      543      documento["taxas"]["2026-07-13"]["BRL"] = brl
      544      cambio = ler_cambio(_bytes(documento))

⏺ Bash(python3 - <<'EOF'
      p='tests/test_rn015_moeda_e_cambio.py'…)
  ⎿  All checks passed!
     784 passed in 0.43s
      M src/reembolso/modelo.py
     … +5 lines (ctrl+o to expand)
  ⎿  Updated tests/test_rn015_moeda_e_cambio.py (+1 -1)
      85      ],
      86  )
      87  def test_rn015_brl_tem_taxa_1_sem_consultar_o_arquivo(taxas):
      88 -    """RN-015 / AMB-025: BRL → taxa 1, data nula; a entrada BRL
         - do arquivo é ignorada."""                                     
      88 +    """RN-015 / AMB-025: BRL → taxa 1, data nula; BRL no arquiv
         +o é ignorado."""                                               
      89      assert cotacao(_cambio(taxas=taxas), "BRL", date(2026, 7, 1
          4)) == Cotacao(
      90          Decimal(1), None
      91      )
  ⎿  Updated tests/test_rn016_arquivos_de_politica_e_cambio.py (+1 -1)
      538      ],
      539  )
      540  def test_rn016_brl_e_campos_nao_listados_ignorados_sem_validac
           ao(brl):
      541 -    """RN-016 / RN-015: a entrada BRL de uma data, `fonte` e `
          -observacao` são ignoradas."""                                 
      541 +    """RN-016 / RN-015: BRL numa data, `fonte` e `observacao` 
          +são ignorados."""                                             
      542      documento = construir_cambio(fonte=Decimal("1e999999"), ob
           servacao=[])
      543      documento["taxas"]["2026-07-13"]["BRL"] = brl
      544      cambio = ler_cambio(_bytes(documento))

⏺ Suíte verde e ruff limpo. Agora a revisão independente.

⏺ revisor-de-task(Revisar T-026)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ A implementação da T-026 está pronta, a suíte está verde e o revisor-de-task
  está rodando. Assim que ele devolver o parecer, salvo em docs/reviews/T-026.md
  e trago o resumo completo para você aprovar o commit.
✻ Crunched for 2m 12s · done 3:08 PM

› Message from revisor-de-task
  # Revisão T-026 — Leitor do câmbio e busca da cotação

  - **Data:** 2026-10-04
  - **Regras conferidas:** RN-015, RN-016 (parte do câmbio), AMB-024, AMB-025,
  DT-014, DT-015 (câmbio), DECISIONS.md linhas 6, R2-2, R2-4b, R2-6a, R2-6e,
  R3-2
  - **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 784 passed, 0
  failed (isso é evidência, não veredito)

  ### Resultado
  **APROVADO COM RESSALVAS** — todos os critérios de aceite estão atendidos e o
  código segue a RN-015, a RN-016 e a DT-014. Faltam só testes de fronteira que
  impediriam uma implementação errada de passar.

  ### Critérios de aceite
  | # | Critério | Status | Evidência |
  |---|---|---|---|
  | 1 | EUR em 14/07 → 5,93 de 14/07 | atendido |
  `tests/test_rn015_moeda_e_cambio.py::test_rn015_cotacao_da_propria_data`
  (confere com `exemplos/envelope/cambio.json`) |
  | 2 | EUR em 18/07 (sábado) → 5,96 de 17/07 | atendido |
  `test_rn015_sabado_usa_a_sexta` |
  | 3 | Câmbio só com 13/07: USD em 16/07 → 13/07 (D-3); USD em 17/07 → `None`
  (D-4) | atendido | `test_rn015_cotacao_ate_3_dias_antes`,
  `test_rn015_cotacao_4_dias_antes_nao_serve` |
  | 4 | USD em 12/07 → `None` (nunca a cotação posterior); GBP e `XYZ` → `None`
  | atendido | `test_rn015_nunca_usa_cotacao_posterior`,
  `test_rn015_moeda_fora_do_arquivo_nao_tem_cotacao[GBP/XYZ]` |
  | 5 | Câmbio com 13/07 (USD, EUR) e 14/07 (só USD): EUR em 15/07 → 5,91 de
  13/07 | atendido | `test_rn015_data_intermediaria_sem_a_moeda_e_pulada` |
  | 6 | `BRL` → taxa 1, data `None`, com câmbio vazio ou com `"BRL": 7` |
  atendido | `test_rn015_brl_tem_taxa_1_sem_consultar_o_arquivo[cambio_vazio/brl
  _no_arquivo]`; `src/reembolso/cambio.py:71-72` |
  | 7 | Data 0001-01-02 → busca sem erro | atendido |
  `test_rn015_busca_no_inicio_do_calendario_nao_falha` (com EUR chega ao D-2 e
  passa pelo `OverflowError` em `cambio.py:76-78`) |
  | 8 | RN-016 câmbio → `ErroDeArquivo`: raiz que não é objeto; `moeda_base` ≠
  `"BRL"`; `taxas` ausente ou lista; data `"2026-07-32"` / `"2026-7-13"`; valor
  de data que não é objeto; código `"usd"` / `"US"`; taxa `0`, `-5.4`, `"5.4"`,
  `1e999999`; chave repetida (data e moeda) | atendido |
  `tests/test_rn016_arquivos_de_politica_e_cambio.py::test_rn016_cambio_invalido
  _e_erro_de_arquivo_com_o_campo` (todos os ids) e
  `::test_rn016_cambio_com_chave_repetida_e_erro_de_arquivo` |
  | 9 | `"BRL": 0` ou `"BRL": "x"` numa data, com `fonte` e `observacao` na raiz
  → válido | atendido | `test_rn016_brl_e_campos_nao_listados_ignorados_sem_val
  idacao[brl_zero/brl_texto]` (com `fonte=1e999999` e `observacao=[]`) |
  | 10 | `Cambio`/`Cotacao` em `modelo.py`; `construir_cambio` em `conftest.py`
  com o envelope transcrito | atendido | `src/reembolso/modelo.py` (diff),
  conforme o plan seção 3, linhas 112-113; `tests/conftest.py::construir_cambio`
  (12 datas conferidas uma a uma com `exemplos/envelope/cambio.json`) |

  ### Problemas encontrados
  #### 1. Falta teste de fronteira do teto da taxa (logo abaixo do teto ainda é
  válido) — severidade MÉDIA
  - **Regra afetada:** RN-016 ("taxa com valor absoluto a partir de
  1.000.000.000"), DECISIONS R2-4b
  - **Evidência:** só há os casos de erro `taxa_no_teto` (1000000000) e
  `taxa_gigante`. Nenhum teste aceita 999999999,99. O código em
  `src/reembolso/cambio.py:28` usa `>=`, o que está correto.
  - **Impacto:** uma implementação com `>` trocado, ou com teto menor, passaria
  na suíte.
  - **Recomendação:** acrescentar um caso válido logo abaixo do teto (por
  exemplo 999999999.99 ou 999999999.999) ao lado de `taxa_no_teto`.

  #### 2. Falta teste mostrando que a taxa não tem limite de casas decimais —
  severidade MÉDIA
  - **Regra afetada:** RN-016. A regra de "mais de 2 casas decimais" vale só
  para limite e mínimo da nota; a taxa só precisa ser número, maior que 0 e
  abaixo do teto.
  - **Evidência:** todas as taxas testadas têm 2 casas. `cambio.py:_taxa` não
  aplica `tem_ate_2_casas`, o que está correto, mas nenhum teste trava esse
  comportamento.
  - **Impacto:** se alguém reaproveitar o validador de limite de `politica.py`,
  que testa casas, uma taxa como `5.4321` passaria a dar erro de arquivo sem
  nenhum teste falhar.
  - **Recomendação:** acrescentar um teste com uma taxa de mais de 2 casas sendo
  aceita, com o valor exato preservado em `Cambio.taxas`.

  #### 3. Ordem dos erros dentro de `taxas` intercalada por data — severidade
  BAIXA
  - **Regra afetada:** DT-015 ("validam campo a campo, na ordem da lista da
  RN-016").
  - **Evidência:** `cambio.py:49-64` valida, data por data, a chave, o objeto e
  depois as moedas. Uma data malformada que vem depois de uma moeda inválida em
  outra data é reportada depois desta.
  - **Impacto:** nenhum no resultado: o desfecho é o mesmo `ErroDeArquivo`, o
  código de saída é o mesmo e a mensagem não é contratual. Fica registrado só
  por rastreabilidade em relação à DT-015.
  - **Recomendação:** nenhuma ação obrigatória. Se quiser, deixar explícito na
  DT-015 que a ordem vale por data.

  ### Cobertura
  - **Regras testadas:**
    - RN-015, AMB-024, AMB-025, DT-014 → `tests/test_rn015_moeda_e_cambio.py` (9
  funções e parametrizações).
    - RN-016 câmbio, DT-015 →
  `tests/test_rn016_arquivos_de_politica_e_cambio.py`, seção "câmbio":
  inválidos, chaves repetidas, UTF-8, envelope válido, `BRL` e campos ignorados,
  `moeda_base` ausente ou nula.
    - Tirar RN-015 de `PENDENTES` em `tests/test_rastreabilidade.py` está
  correto. Os casos de borda de RN-015 da seção 7 continuam pendentes para a
  T-031, que é a dona deles.
  - **Casos de borda cobertos:**
    - janela D, D-1 (sábado), D-2 (data intermediária pulada) e D-3; D-4
  recusado;
    - cotação posterior não é usada; moeda bem formada ausente do arquivo;
    - `BRL` com câmbio vazio e com `BRL` no arquivo; início do calendário;
    - taxa `0`, `-0`, negativa, texto, booleana, no teto e gigante;
    - `moeda_base` `"USD"`, `"brl"`, ausente e `null`; `taxas` `null`, ausente e
  lista;
    - chave repetida na data e na moeda; arquivo fora do UTF-8.
  - **Casos que parecem faltar:**
    - taxa logo abaixo do teto aceita (RN-016, teto "a partir de");
    - taxa com mais de 2 casas aceita (RN-016 só limita casas de limite e
  mínimo);
    - raiz de outro tipo além de lista, como número ou texto (RN-016, "raiz que
  não é objeto"). É um caso fraco: a verificação é a mesma `isinstance`.

  ### Decisões necessárias
  Nenhuma.

  ### Antes de concluir a task
  Nada bloqueia o commit. Recomendo, sem obrigar, acrescentar os dois testes de
  fronteira dos problemas 1 e 2 em `/Users/rafaeltxm/repo/sdd-desafio/tests/test
  _rn016_arquivos_de_politica_e_cambio.py`.

  Read 1 file (ctrl+o to expand)

⏺ Agent "Revisar T-026" finished · 1m 9s

⏺ Write(docs/reviews/T-026.md)
  ⎿  Wrote 64 lines to docs/reviews/T-026.md
       1 # Revisão T-026 — Leitor do câmbio e busca da cotação
       3 - **Data:** 2026-10-04
       4 - **Regras conferidas:** RN-015, RN-016 (parte do câmbio), AMB-0
         2, R2-4b, R2-6a, R2-6e, R3-2
         84 passed, 0 failed (isso é evidência, não veredito)
       6 
       8 **APROVADO COM RESSALVAS** — todos os critérios de aceite estão 
         atendidos e o código segue a RN-015, a RN-016 e a DT-014. Faltam
         de passar.
      10 ### Critérios de aceite
     … +122 lines (ctrl+o to expand)

⏺ Os problemas 1 e 2 cabem no escopo da task, então acrescento os dois testes de
  fronteira.

⏺ Bash(cat >> tests/test_rn016_arquivos_de_politica_e_cambio.py <<'EOF'…)
  ⎿  786 passed in 0.44s
     All checks passed!
  ⎿  Updated tests/test_rn016_arquivos_de_politica_e_cambio.py (+14 -0)
      555      del documento["moeda_base"]
      556      assert ler_cambio(_bytes(documento)).taxas
      557      assert ler_cambio(_bytes(construir_cambio(moeda_base=None)
           )).taxas
      558 +                                                              
      559 +                                                              
      560 +@pytest.mark.parametrize(                                     
      561 +    "taxa",                                                   
      562 +    [                                                         
      563 +        pytest.param(Decimal("999999999.999"), id="logo_abaixo
          +_do_teto"),                                                   
      564 +        pytest.param(Decimal("5.4321987654321"), id="mais_de_2
          +_casas"),                                                     
      565 +    ],                                                        
      566 +)                                                             
      567 +def test_rn016_taxa_valida_pelo_valor_exato(taxa):            
      568 +    """RN-016: taxa abaixo do teto vale com qualquer número de
          + casas, sem arredondar."""                                    
      569 +    # o limite de 2 casas é só do limite e do mínimo da nota; 
          +a taxa sai exata                                              
      570 +    documento = _cambio_com(("taxas", "2026-07-13", "USD"), ta
          +xa)                                                           
      571 +    assert ler_cambio(_bytes(documento)).taxas[date(2026, 7, 1
          +3)]["USD"] == taxa                                            

⏺ Resumo — T-026: leitor do câmbio e busca da cotação

  A T-026 está implementada: 786 testes passam e o ruff está limpo. A revisão
  independente deu APROVADO COM RESSALVAS, sem nenhuma decisão de spec pendente.
  Falta só a sua autorização para o commit.

  Arquivos alterados:
  - src/reembolso/cambio.py (novo): ler_cambio, cotacao e a constante
    DIAS_ANTERIORES_ACEITOS_NA_COTACAO = 3. MOEDA_BASE e VALOR_ABSOLUTO_MAXIMO
    vêm de politica.py, como manda a seção 4 do plan.
  - src/reembolso/modelo.py (modificado): Cambio e Cotacao.
  - tests/conftest.py (modificado): construir_cambio(**sobrescritas), com o
    cambio.json do envelope transcrito.
  - tests/test_rn015_moeda_e_cambio.py (novo).
  - tests/test_rn016_arquivos_de_politica_e_cambio.py (modificado): ganhou a
    seção do câmbio.
  - tests/test_rastreabilidade.py (modificado): a RN-015 saiu de PENDENTES.
  - docs/reviews/T-026.md (novo).

  Testes criados:
  - Busca da cotação (RN-015, AMB-024, AMB-025, DT-014): a data da própria
    despesa, sábado que usa a sexta, D-3 aceito, D-4 recusado, nunca cotação
    posterior, GBP e XYZ sem cotação, data intermediária sem a moeda pulada, BRL
    com taxa 1 (câmbio vazio e "BRL": 7 no arquivo) e busca em 0001-01-02.
  - Câmbio inválido (RN-016, DT-015):
    - raiz, moeda_base e taxas com defeito;
    - datas 2026-07-32 e 2026-7-13, e valor de data que não é objeto;
    - códigos usd e US;
    - taxas 0, -0, -5.4, "5.4", true, no teto e 1e999999;
    - chave repetida na data e na moeda;
    - arquivo fora do UTF-8.
  - Câmbio válido (RN-016): o do envelope; "BRL": 0 e "BRL": "x" numa data, com
    fonte e observacao na raiz; moeda_base ausente ou nula; taxa logo abaixo do
    teto e taxa com mais de 2 casas, preservada sem arredondar.

  Testes antes da implementação: falharam pelo motivo esperado, porque o módulo
  reembolso.cambio ainda não existia.

  Testes depois: uv run pytest -q e uv run ruff check ..

  pytest: 786 passed, 0 failed.

  ruff: limpo.

  Revisão independente: APROVADO COM RESSALVAS, sem decisões necessárias. O
  relatório está salvo sem edição em docs/reviews/T-026.md.
  - MÉDIA 1 (corrigido): faltava um teste com taxa logo abaixo do teto sendo
    aceita.
  - MÉDIA 2 (corrigido): faltava um teste mostrando que a taxa aceita mais de 2
    casas decimais.
  - BAIXA 3 (não alterado): os erros dentro de taxas aparecem data por data, e
    não na ordem exata da lista da RN-016. Isso não muda o resultado nem o
    código de saída, e a mensagem não é contratual. Se quiser, a DT-015 pode
    dizer isso explicitamente, mas é mudança de plan, fora desta task.

  Decisões ou interpretações: nenhuma regra nova. Pela spec, a taxa precisa ser
  maior que zero, então -0, que vale zero, é erro de arquivo.

  Lacunas: os casos de borda de conversão da seção 7 continuam pendentes, como
  previsto. São da T-031, e os do arquivo de câmbio (por exemplo "Taxa de câmbio
  não positiva") são da T-028.

  Commit proposto: feat(T-026): ler_cambio e cotacao com a validação da RN-016 e
  a busca D a D-3

  Posso commitar?

✻ Crunched for 4m 4s · done 3:10 PM

❯ pode commitar                                                                 

  Ran 1 shell command (ctrl+o to expand)

⏺ Bash(python3 - <<'EOF'
      p='specs/001-motor-reembolso/tasks.md'…)
  ⎿   specs/001-motor-reembolso/tasks.md | 4 ++--
      1 file changed, 2 insertions(+), 2 deletions(-)
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+2 -2)
      256      - **Válidos:** `politica-v4` transcrita → `Politica` com a
           s quatro tabelas indexadas pela categoria normalizada e os cen
           tros de custo pela chave como escrita; sem `versao`, `vigencia
           `, `moeda_base` e `centros_custo` (ou com `null`) → válida, `v
           ersao` e `vigencia` `None`; `60.000` → 60,00; `periodicidade` 
           `"diaria"` em qualquer categoria; tabela vazia; `observacao` n
           uma regra e campo desconhecido na raiz ignorados; limite `-0` 
           → 0.
      257    - **Commit:** 4c93a08
      258  
      259 -- [ ] **T-026** — Leitor do câmbio e busca da cotação: `ler_ca
          -mbio(bytes) -> Cambio` (RN-016, parte do câmbio) e `cotacao(ca
          -mbio, moeda, data) -> Cotacao | None` (RN-015, DT-014); `Cambi
          -o` e `Cotacao` em `modelo.py`; construtor `construir_cambio(ta
          -xas=...)` em `tests/conftest.py`, com o `cambio.json` do envel
          -ope transcrito.                                               
      259 +- [x] **T-026** — Leitor do câmbio e busca da cotação: `ler_ca
          +mbio(bytes) -> Cambio` (RN-016, parte do câmbio) e `cotacao(ca
          +mbio, moeda, data) -> Cotacao | None` (RN-015, DT-014); `Cambi
          +o` e `Cotacao` em `modelo.py`; construtor `construir_cambio(ta
          +xas=...)` em `tests/conftest.py`, com o `cambio.json` do envel
          +ope transcrito.                                               
      260    - **Tipo:** regra
      261    - **Atende:** RN-015 (taxa da data, D-1 a D-3, só a mesma mo
           eda, nunca posterior, `BRL` taxa 1), RN-016 (câmbio), AMB-024,
            AMB-025 (`BRL` fora do arquivo; código sem cotação), DT-014, 
           DT-015
      262    - **Depende de:** T-023
     ...
      271        - data em 0001-01-02 → busca sem erro.
      272      - `tests/test_rn016_arquivos_de_politica_e_cambio.py` pass
           a os testes do câmbio, cada um com `ErroDeArquivo`: raiz que n
           ão é objeto; `moeda_base` diferente de `"BRL"`; `taxas` ausent
           e ou lista; data `"2026-07-32"` ou `"2026-7-13"`; valor de dat
           a que não é objeto; código `"usd"` ou `"US"`; taxa `0`, `-5.4`
           , `"5.4"` ou `1e999999`; chave repetida (mesma data duas vezes
           ; mesma moeda duas vezes na data).
      273      - Câmbio com `"BRL": 0` ou `"BRL": "x"` numa data e com `f
           onte` e `observacao` na raiz → válido.
      274 -  - **Commit:** —                                             
      274 +  - **Commit:** b3fd107                                       
      275  
      276  - [ ] **T-027** — Tabela aplicada e limite: `tabela_aplicada(p
           olitica, centro_custo)` (RN-014), `limite_diario(tabela, categ
           oria, em_viagem, percentual)` com truncamento (RN-009, DT-013)
            e `categoria_de_saida(texto, tabela)` (seção 4 da spec), em `
           politica.py`, com as constantes de interpretação da seção 4 do
            plano.
      277    - **Tipo:** regra

⏺ Fiz o commit da T-026 como b3fd107. O pre-commit passou: ruff limpo e 786
  testes ok.

  Já marquei a task como [x] em tasks.md, com o hash, mas ainda não commitei
  essa alteração. O hook exige o export da sessão no commit que fecha o bloco,
  então rode:

  /export docs/sessions/44-t026-ler-cambio.md

  Quando você me avisar que exportou, faço o commit docs(tasks): conclui T-026
  com tasks.md e o export.

✻ Crunched for 10s · done 3:10 PM