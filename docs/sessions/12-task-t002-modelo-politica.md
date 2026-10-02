 ▐▛███▛█   Claude Code v2.1.287
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~/repo/sdd-desafio

  Opus 5.5 is now your default model and it draws down usage faster than Sonnet 5. Switch anytime with /model.

❯ /clear                                                                        

❯ /task T-002                                                                   

  Searched for 2 patterns, ran 3 shell commands (ctrl+o to expand)

⏺ Já li o contexto da task T-002 (seções 3–4 do plano, regras
  RN-002/006/008/009/010, AMB-006/018 e seção 8). Agora vou escrever
  tests/test_politica.py, transcrevendo manualmente os valores esperados da
  spec.

⏺ Write(tests/test_politica.py)
  ⎿  Wrote 74 lines to tests/test_politica.py
       1 from decimal import Decimal
       2 
       3 from reembolso import politica
       4 from reembolso.modelo import Motivo, Status
       5 
       7 def test_rn009_limites_conferem_tabela_da_spec():
       8     """RN-009 / AMB-006: limite diário normal e em viagem por ca
         tegoria; a hospedagem
       9     não amplia em viagem."""
      10     # Tabela da RN-009, transcrita: (normal, em viagem)
     … +76 lines (ctrl+o to expand)

  Ran 1 shell command (ctrl+o to expand)

⏺ Falha esperada (import do que a task cria). Implementando modelo.py e
  politica.py.

⏺ Write(src/reembolso/modelo.py)
  ⎿  Added 109 lines
        1  """Dataclasses e enums compartilhados (plan seção 3)."""
        2 +                                                              
        3 +from dataclasses import dataclass                             
        4 +from datetime import date                                     
        5 +from decimal import Decimal                                   
        6 +from enum import StrEnum                                      
        7 +                                                              
        8 +                                                              
        9 +class Status(StrEnum):                                        
       10 +    APROVADO = "aprovado"                                     
       11 +    PARCIAL = "parcial"                                       
       12 +    RECUSADO = "recusado"                                     
       13 +                                                              
       14 +                                                              
       15 +class Motivo(StrEnum):                                        
       16 +    """Na ordem das etapas da seção 8 da spec."""             
       17 +                                                              
       18 +    ENTRADA_INVALIDA = "entrada_invalida"                     
       19 +    VALOR_INVALIDO = "valor_invalido"                         
       20 +    FORA_DO_PERIODO = "fora_do_periodo"                       
       21 +    CATEGORIA_FORA_DA_POLITICA = "categoria_fora_da_politica" 
       22 +    NOTA_FISCAL_AUSENTE = "nota_fiscal_ausente"               
       23 +    DUPLICATA = "duplicata"                                   
       24 +    LIMITE_DIARIO_EXCEDIDO = "limite_diario_excedido"         
       25 +                                                              
       26 +                                                              
       27 +@dataclass(frozen=True)                                       
       28 +class Colaborador:                                            
       29 +    id: str                                                   
       30 +    nome: str                                                 
       31 +                                                              
       32 +                                                              
       33 +@dataclass(frozen=True)                                       
       34 +class Periodo:                                                
       35 +    inicio: date                                              
       36 +    fim: date                                                 
       37 +    inicio_texto: str                                         
       38 +    fim_texto: str                                            
       39 +    competencia: str | None                                   
       40 +                                                              
       41 +                                                              
       42 +@dataclass(frozen=True)                                       
       43 +class Despesa:                                                
       44 +    """Despesa que passou pela etapa 1 (validação)."""        
       45 +                                                              
       46 +    posicao: int  # índice em `despesas` — ordem da entrada   
       47 +    id: str                                                   
       48 +    data: date                                                
       49 +    data_texto: str                                           
       50 +    categoria_texto: str  # como veio                         
       51 +    categoria: str  # normalizada (seção 5 da spec)           
       52 +    fornecedor: str  # normalizado                            
       53 +    valor_informado: Decimal                                  
       54 +    tem_nota_fiscal: bool                                     
       55 +    avisos: tuple[str, ...]  # RN-013                         
       56 +                                                              
       57 +                                                              
       58 +@dataclass(frozen=True)                                       
       59 +class DespesaInvalida:                                        
       60 +    """Despesa recusada na etapa 1."""                        
       61 +                                                              
       62 +    posicao: int                                              
       63 +    id: str | None                                            
       64 +    data_texto: str | None                                    
       65 +    # normalizada se reconhecida; senão texto como veio; senão
          + None                                                         
       66 +    categoria_saida: str | None                               
       67 +    valor_informado: Decimal | None                           
       68 +    avisos: tuple[str, ...]                                   
       69 +                                                              
       70 +                                                              
       71 +@dataclass(frozen=True)                                       
       72 +class Entrada:                                                
       73 +    colaborador: Colaborador                                  
       74 +    periodo: Periodo                                          
       75 +    despesas: list[Despesa | DespesaInvalida]                 
       76 +    avisos: tuple[str, ...]  # chaves repetidas fora das despe
          +sas                                                           
       77 +                                                              
       78 +                                                              
       79 +@dataclass(frozen=True)                                       
       80 +class ItemResultado:                                          
       81 +    """Espelha `itens[]` da seção 4 da spec, campo a campo."""
       82 +                                                              
       83 +    id: str | None                                            
       84 +    data: str | None                                          
       85 +    categoria: str | None                                     
       86 +    valor_informado: Decimal | None                           
       87 +    valor_considerado: Decimal | None                         
       88 +    valor_reembolsado: Decimal                                
       89 +    status: Status                                            
       90 +    motivo: Motivo | None                                     
       91 +    em_viagem: bool | None                                    
       92 +    limite_diario: Decimal | None                             
       93 +    justificativa: str                                        
       94 +    avisos: tuple[str, ...]                                   
       95 +                                                              
       96 +                                                              
       97 +@dataclass(frozen=True)                                       
       98 +class Totais:                                                 
       99 +    valor_solicitado: Decimal                                 
      100 +    valor_reembolsado: Decimal                                
      101 +    valor_glosado: Decimal                                    
      102 +                                                              
      103 +                                                              
      104 +@dataclass(frozen=True)                                       
      105 +class Resultado:                                              
      106 +    colaborador: Colaborador                                  
      107 +    periodo: Periodo                                          
      108 +    itens: list[ItemResultado]                                
      109 +    totais: Totais                                            
      110 +    avisos: tuple[str, ...]                                   

⏺ Write(src/reembolso/politica.py)
  ⎿  Added 23 lines
       1  """Constantes da política (plan seção 4)."""
       2 +                                                               
       3 +from dataclasses import dataclass                              
       4 +from decimal import Decimal                                    
       5 +                                                               
       6 +                                                               
       7 +@dataclass(frozen=True)                                        
       8 +class LimiteDiario:                                            
       9 +    normal: Decimal                                            
      10 +    viagem: Decimal                                            
      11 +                                                               
      12 +                                                               
      13 +# RN-009: (normal, em viagem). Valores em viagem escritos por e
         +xtenso, como na                                                
      14 +# tabela da spec; a hospedagem não amplia (AMB-006).           
      15 +LIMITES_DIARIOS = {                                            
      16 +    "alimentacao": LimiteDiario(normal=Decimal("60.00"), viagem
         +=Decimal("90.00")),                                            
      17 +    "transporte_urbano": LimiteDiario(normal=Decimal("80.00"), 
         +viagem=Decimal("120.00")),                                     
      18 +    "hospedagem": LimiteDiario(normal=Decimal("250.00"), viagem
         +=Decimal("250.00")),                                           
      19 +}                                                              
      20 +CATEGORIAS_RECONHECIDAS = frozenset(LIMITES_DIARIOS)  # RN-006 
      21 +VALOR_ACIMA_DO_QUAL_EXIGE_NOTA = Decimal("100.00")  # RN-008 (e
         +stritamente maior)                                             
      22 +CATEGORIA_QUE_COMPROVA_VIAGEM = "hospedagem"  # RN-010         
      23 +DIAS_EM_VIAGEM_APOS_HOSPEDAGEM = 1  # RN-010: D e D+1          
      24 +VALOR_ABSOLUTO_MAXIMO = Decimal("1000000000")  # RN-002 / AMB-0
         +18 (a partir dele: entrada_invalida)                           

  Ran 1 shell command (ctrl+o to expand)

⏺ Fix line lengths.

⏺ Bash(python3 - <<'EOF'
      import re…)
  ⎿  ..........
        [100%]
     10 passed in 0.02s
     … +4 lines (ctrl+o to expand)
  ⎿  Updated src/reembolso/politica.py (+5 -2)
      14  # tabela da spec; a hospedagem não amplia (AMB-006).
      15  LIMITES_DIARIOS = {
      16      "alimentacao": LimiteDiario(normal=Decimal("60.00"), viagem
          =Decimal("90.00")),
      17 -    "transporte_urbano": LimiteDiario(normal=Decimal("80.00"), 
         -viagem=Decimal("120.00")),                                     
      17 +    "transporte_urbano": LimiteDiario(                         
      18 +        normal=Decimal("80.00"), viagem=Decimal("120.00")      
      19 +    ),                                                         
      20      "hospedagem": LimiteDiario(normal=Decimal("250.00"), viagem
          =Decimal("250.00")),
      21  }
      22  CATEGORIAS_RECONHECIDAS = frozenset(LIMITES_DIARIOS)  # RN-006
      23  VALOR_ACIMA_DO_QUAL_EXIGE_NOTA = Decimal("100.00")  # RN-008 (e
          stritamente maior)
      24  CATEGORIA_QUE_COMPROVA_VIAGEM = "hospedagem"  # RN-010
      25  DIAS_EM_VIAGEM_APOS_HOSPEDAGEM = 1  # RN-010: D e D+1
      24 -VALOR_ABSOLUTO_MAXIMO = Decimal("1000000000")  # RN-002 / AMB-0
         -18 (a partir dele: entrada_invalida)                           
      26 +# RN-002 / AMB-018: valor absoluto a partir dele é entrada_inva
         +lida                                                           
      27 +VALOR_ABSOLUTO_MAXIMO = Decimal("1000000000")                  
  ⎿  Updated tests/test_politica.py (+8 -3)
      31  
      32  
      33  def test_rn008_valor_de_nota_e_100():
      34 -    """RN-008 / AMB-007: nota obrigatória acima de 100,00 (fixo
         -, não amplia em viagem)."""                                    
      34 +    """RN-008 / AMB-007: nota obrigatória acima de 100,00 (fixo
         +, não amplia                                                   
      35 +    em viagem)."""                                             
      36      assert politica.VALOR_ACIMA_DO_QUAL_EXIGE_NOTA == Decimal("
          100.00")
      37  
      38  
      39  def test_rn002_teto_de_um_bilhao():
      39 -    """RN-002 / AMB-018: valor absoluto a partir de 1.000.000.0
         -00,00 é entrada_invalida."""                                   
      40 +    """RN-002 / AMB-018: valor absoluto a partir de 1.000.000.0
         +00,00 é                                                        
      41 +    entrada_invalida."""                                       
      42      assert politica.VALOR_ABSOLUTO_MAXIMO == Decimal("100000000
          0.00")
      43  
      44  
     ...
      70  
      71  def test_constantes_monetarias_sao_decimal():
      72      """RN-003 / DT-001: toda constante monetária da política é 
          Decimal, nunca float."""
      71 -    monetarias = [politica.VALOR_ACIMA_DO_QUAL_EXIGE_NOTA, poli
         -tica.VALOR_ABSOLUTO_MAXIMO]                                    
      73 +    monetarias = [                                             
      74 +        politica.VALOR_ACIMA_DO_QUAL_EXIGE_NOTA,               
      75 +        politica.VALOR_ABSOLUTO_MAXIMO,                        
      76 +    ]                                                          
      77      for limite in politica.LIMITES_DIARIOS.values():
      78          monetarias += [limite.normal, limite.viagem]
      79      assert all(type(v) is Decimal for v in monetarias)

⏺ Verde. Invocando o revisor independente só com o ID.

⏺ revisor-de-task(Revisar T-002)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ A implementação e os testes de T-002 estão prontos e verdes. Falta o parecer
  do revisor-de-task, que ainda está rodando. Quando ele terminar, salvo o
  relatório em docs/reviews/T-002.md e apresento o resumo completo para você
  autorizar o commit.

✻ Cogitated for 1m 4s · done 10:40 PM

› Message from revisor-de-task
  # Revisão T-002 — Modelo de dados e política

  - **Data:** 2026-10-01
  - **Regras conferidas:** RN-002 (teto), RN-006, RN-008, RN-009, RN-010,
  AMB-006, AMB-018; seção 4 (códigos de motivo, schema de `itens[]`), seção 8
  (ordem das etapas); plan seções 3 e 4; DECISIONS D-002 ponto 1, D-00x ponto 3b
  - **Suíte:** `uv run --frozen pytest -q -p no:cacheprovider` → 10 passed, 0
  failed; `ruff check` → All checks passed (evidência, não veredito)

  ### Resultado
  **APROVADO COM RESSALVAS** — todos os critérios de aceite foram atendidos e as
  constantes conferem com a spec. Restam só observações de severidade BAIXA
  sobre testes que conferem constantes, não comportamento.

  ### Critérios de aceite
  | # | Critério | Status | Evidência |
  |---|---|---|---|
  | 1 | `test_rn009_limites_conferem_tabela_da_spec` (60/90, 80/120, 250/250) |
  atendido |
  `tests/test_politica.py::test_rn009_limites_conferem_tabela_da_spec`. Compara
  o dicionário inteiro, então uma categoria a mais também falharia. Conferi à
  mão contra a tabela da RN-009: 60,00/90,00, 80,00/120,00, 250,00/250,00
  (AMB-006: a hospedagem não amplia). Em `src/reembolso/politica.py` os limites
  em viagem estão escritos por extenso, como pede o plano na seção 4. |
  | 2 | `test_rn006_tres_categorias_reconhecidas` | atendido |
  `tests/test_politica.py::test_rn006_tres_categorias_reconhecidas`;
  `CATEGORIAS_RECONHECIDAS = frozenset(LIMITES_DIARIOS)` dá exatamente
  `alimentacao`, `transporte_urbano` e `hospedagem`, como na RN-006 |
  | 3 | `test_rn008_valor_de_nota_e_100` | atendido |
  `tests/test_politica.py::test_rn008_valor_de_nota_e_100`;
  `VALOR_ACIMA_DO_QUAL_EXIGE_NOTA = Decimal("100.00")` |
  | 4 | `test_rn002_teto_de_um_bilhao` | atendido |
  `tests/test_politica.py::test_rn002_teto_de_um_bilhao`; `VALOR_ABSOLUTO_MAXIMO
  = Decimal("1000000000")`, igual em valor a 1.000.000.000,00 (RN-002/AMB-018)
  |
  | 5 | `test_rn010_viagem_cobre_d_e_d_mais_1` | atendido |
  `tests/test_politica.py::test_rn010_viagem_cobre_d_e_d_mais_1`;
  `CATEGORIA_QUE_COMPROVA_VIAGEM = "hospedagem"` e
  `DIAS_EM_VIAGEM_APOS_HOSPEDAGEM = 1` |
  | 6 | `test_motivos_na_ordem_da_secao_8` | atendido |
  `tests/test_politica.py::test_motivos_na_ordem_da_secao_8`. A ordem em
  `src/reembolso/modelo.py` (`Motivo`) é a mesma da tabela "Códigos de motivo"
  da seção 4: entrada_invalida, valor_invalido, fora_do_periodo,
  categoria_fora_da_politica, nota_fiscal_ausente, duplicata,
  limite_diario_excedido. Isso corresponde às etapas 1, 3, 4, 5, 6, 7 e 9 da
  seção 8 (nota antes de duplicata, conforme a decisão 4a do DECISIONS). |
  | 7 | Todas as constantes monetárias são `Decimal` | atendido |
  `tests/test_politica.py::test_constantes_monetarias_sao_decimal` (usa `type(v)
  is Decimal`) cobre os 6 limites, a nota e o teto |

  ### Problemas encontrados
  #### 1. O sentido das comparações (`>` na nota, `>=` no teto) só aparece em
  comentário — severidade BAIXA
  - **Regra afetada:** RN-008 / AMB-007 ("estritamente maior que 100,00");
  RN-002 / AMB-018 ("maior ou igual a 1.000.000.000,00")
  - **Evidência:** em `src/reembolso/politica.py`, `# RN-008 (estritamente
  maior)` e `# RN-002 / AMB-018: valor absoluto a partir dele é
  entrada_invalida`. Os testes conferem só o valor da constante.
  - **Impacto:** nesta task não muda nenhum resultado. Mas os testes da T-002
  não protegem a fronteira 100,00/100,01 nem 999999999,99/1000000000.
  - **Recomendação:** confirmar que as fronteiras entram como testes nas tasks
  que aplicam as regras: T-009 para o teto (o Aceite já cita `999999999.995` e
  `1e999999`) e a task da RN-008 para 100,00 e 100,01.

  #### 2. O teste da RN-010 confere um número, não o comportamento D e D+1 —
  severidade BAIXA
  - **Regra afetada:** RN-010
  - **Evidência:**
  `tests/test_politica.py::test_rn010_viagem_cobre_d_e_d_mais_1` faz `assert ...
  == 1`
  - **Impacto:** passaria mesmo se o código que aplica viagem usasse a constante
  de forma errada (por exemplo, só D+1, ou D-1).
  - **Recomendação:** o comportamento (14/07 e 15/07 em viagem, 16/07 não)
  precisa ser testado na task da etapa 8/RN-010.

  ### Cobertura
  - **Regras testadas:**
    - RN-009/AMB-006 → `test_rn009_limites_conferem_tabela_da_spec`
    - RN-006 → `test_rn006_tres_categorias_reconhecidas`
    - RN-008/AMB-007 → `test_rn008_valor_de_nota_e_100`
    - RN-002/AMB-018 → `test_rn002_teto_de_um_bilhao`
    - RN-010 → `test_rn010_viagem_cobre_d_e_d_mais_1`
    - Seção 4/8 → `test_motivos_na_ordem_da_secao_8`
    - RN-011 → `test_rn011_status_da_saida`
    - DT-001 → `test_constantes_monetarias_sao_decimal`
  - **Casos de borda cobertos:** a hospedagem não amplia em viagem (250/250);
  não existe uma quarta categoria; constantes monetárias não são `float`.
  - **Casos que parecem faltar (fora do escopo desta task, ficam para as tasks
  de comportamento):**
    - fronteira 100,00 / 100,01 (RN-008)
    - fronteira 999999999,995 / 1000000000 / -1e12 (RN-002)
    - D, D+1 e D+2 (RN-010)

  O modelo em `src/reembolso/modelo.py` replica campo a campo a seção 3 do
  plano. `ItemResultado` tem os 12 campos de `itens[]` da seção 4, na mesma
  ordem. Não encontrei constante, limite ou regra sem base na spec ou no plano.
  O diff toca só `src/reembolso/modelo.py`, `src/reembolso/politica.py` e
  `tests/test_politica.py`, todos dentro do escopo.

  ### Decisões necessárias
  Nenhuma.

  ### Antes de concluir a task
  Nada — pode seguir para o commit. As ressalvas 1 e 2 ficam como lembrete para
  as tasks que aplicam RN-002, RN-008 e RN-010.

  Listed 1 directory (ctrl+o to expand)

⏺ Agent "Revisar T-002" finished · 41s

⏺ Write(docs/reviews/T-002.md)
  ⎿  Wrote 56 lines to docs/reviews/T-002.md
       1 # Revisão T-002 — Modelo de dados e política
       3 - **Data:** 2026-10-01
         RN-010, AMB-006, AMB-018; seção 4 (códigos de motivo, schema de 
         IONS D-002 ponto 1, D-00x ponto 3b
         0 passed, 0 failed; `ruff check` → All checks passed (evidência,
          não veredito)
       7 ### Resultado
         atendidos e as constantes conferem com a spec. Restam só observa
         ão comportamento.
      10 ### Critérios de aceite
     … +101 lines (ctrl+o to expand)

⏺ Resumo — T-002: Modelo de dados e política

  Arquivos alterados:
  - src/reembolso/modelo.py (modificado): enums Status e Motivo, mais as
    dataclasses da seção 3 do plano.
  - src/reembolso/politica.py (modificado): as constantes da seção 4 do plano.
  - tests/test_politica.py (novo)
  - docs/reviews/T-002.md (novo): o parecer do revisor, salvo sem edição.

  Testes criados/alterados:
  - test_rn009_limites_conferem_tabela_da_spec → RN-009 e AMB-006 (60/90,
    80/120, 250/250)
  - test_rn006_tres_categorias_reconhecidas → RN-006
  - test_rn008_valor_de_nota_e_100 → RN-008 e AMB-007
  - test_rn002_teto_de_um_bilhao → RN-002 e AMB-018
  - test_rn010_viagem_cobre_d_e_d_mais_1 → RN-010
  - test_motivos_na_ordem_da_secao_8 → tabela de motivos da seção 4 e seção 8
  - test_rn011_status_da_saida → RN-011 (valores do enum Status)
  - test_constantes_monetarias_sao_decimal → DT-001 e a exigência do Aceite de
    que toda constante monetária seja Decimal

  Testes executados antes da implementação: uv run pytest -q 
  tests/test_politica.py. A coleta falhou com ImportError: cannot import name 
  'Motivo', que é o que a task vai criar. É uma falha aceitável pelo passo 5.
  Não houve falha de asserção porque o código ainda não existia.

  Testes executados depois: uv run pytest -q (suíte inteira) e uv run ruff check
  .

  pytest: 10 passed, 0 failed

  ruff: limpo

  Revisão independente: APROVADO COM RESSALVAS, sem decisões necessárias.
  Parecer em docs/reviews/T-002.md. As duas ressalvas são de severidade baixa e
  ficam fora do escopo desta task:
  1. Os testes conferem só o valor das constantes, não o sentido das comparações
     (maior que 100,00 na nota; a partir de 1 bilhão no teto). Esses limites já
     estão no Aceite da T-009 (999999999.995, 1e999999) e da T-016 (100,00 e
     100,01).
  2. O teste da RN-010 confere o número 1, não o comportamento de colocar D e
     D+1 em viagem. Isso já está no Aceite da T-018 (14/07 e 15/07 em viagem,
     16/07 não).

  Decisões ou interpretações realizadas:
  - LimiteDiario aparece na seção 4 do plano mas não está definido na seção 3.
    Defini como uma dataclass congelada (normal, viagem) dentro de politica.py.
    É um detalhe de implementação, não regra de negócio.
  - Incluí test_rn011_status_da_saida, que o Aceite não pede, para conferir os
    valores do enum Status.

  Lacunas ou dúvidas: nenhuma na spec.

  Commit proposto: feat(T-002): modelo de dados e constantes da política

  Posso fazer o commit?

✻ Brewed for 2m 16s · done 10:41 PM

❯ pode commitar                                                                 

  Ran 1 shell command (ctrl+o to expand)

⏺ Bash(python3 - <<'EOF'
      p='specs/001-motor-reembolso/tasks.md'; s=open(p).read()…)
  ⎿   specs/001-motor-reembolso/tasks.md | 4 ++--
      1 file changed, 2 insertions(+), 2 deletions(-)
     pre-commit: commit sem código Python/testes/exemplos — ruff e pytest n
     … +9 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+2 -2)
      31    - **Aceite:** `uv run pytest -q` e `uv run ruff check .` verd
          es; `tests/test_setup.py::test_fixture_entrada_minima_e_json_va
          lido` passa (a entrada do construtor é um documento com `colabo
          rador`, `periodo` e `despesas` conforme a seção 4 da spec).
      32    - **Commit:** 805aee5
      33  
      34 -- [ ] **T-002** — Modelo de dados e política: `modelo.py` (data
         -classes e enums da seção 3 do plano, com `Motivo` na ordem da s
         -eção 8 da spec) e `politica.py` (constantes literais da seção 4
         - do plano).                                                    
      34 +- [x] **T-002** — Modelo de dados e política: `modelo.py` (data
         +classes e enums da seção 3 do plano, com `Motivo` na ordem da s
         +eção 8 da spec) e `politica.py` (constantes literais da seção 4
         + do plano).                                                    
      35    - **Tipo:** regra
      36    - **Atende:** RN-006 (categorias), RN-008 (100,00), RN-009 (t
          abela de limites), RN-010 (D e D+1), RN-002 (teto de 1.000.000.
          000,00), AMB-006, AMB-018
      37    - **Depende de:** T-001
      38    - **Aceite:** `tests/test_politica.py` passa: `test_rn009_lim
          ites_conferem_tabela_da_spec` (60/90, 80/120, 250/250), `test_r
          n006_tres_categorias_reconhecidas`, `test_rn008_valor_de_nota_e
          _100`, `test_rn002_teto_de_um_bilhao`, `test_rn010_viagem_cobre
          _d_e_d_mais_1`, `test_motivos_na_ordem_da_secao_8`; todas as co
          nstantes monetárias são `Decimal`.
      39 -  - **Commit:**                                                
      39 +  - **Commit:** 6e1f498                                        
      40  
      41  - [ ] **T-003** — Normalização de texto: `normalizar_texto()` c
          om os 4 passos da seção 5 da spec (DT-004).
      42    - **Tipo:** regra
  ⎿  PostToolUse:Bash says: 📝 Fim do bloco de trabalho ("docs(tasks): conclui 
     T-002"). Exporte a sessão antes de continuar:
        /export docs/sessions/12-<descricao-curta>.md
        e commite com: docs(sessions): export da sessão 12

⏺ T-002 está commitada e marcada como concluída. Os hooks rodaram ruff e pytest
  antes do commit, e os 10 testes passaram.

  - 6e1f498 feat(T-002): modelo de dados e constantes da política
  - 83e9bd0 docs(tasks): conclui T-002 — a task está marcada [x] com o hash
    6e1f498 em tasks.md.

  📝 Fim do bloco: exporte a sessão antes de continuar:
  /export docs/sessions/12-<descricao-curta>.md
  e commite com docs(sessions): export da sessão 12.

  Não vou começar a próxima task até você pedir.

✻ Cooked for 18s · done 10:41 PM