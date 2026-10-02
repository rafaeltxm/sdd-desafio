 ▐▛███▛█   Claude Code v2.1.287
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~/repo/sdd-desafio

  Opus 5.5 is now your default model and it draws down usage faster than Sonnet 5. Switch anytime with /model.

❯ /clear                                                                        

❯ segue o task.md                                                               

  Read 2 files, listed 4 directories, ran 1 shell command (ctrl+o to expand)

⏺ Já revisei a spec 1.6, o plan 1.0 e o fluxo da skill /task. Agora vou gerar o
  tasks.md, dividindo o plano em tasks de um commit cada, vinculando-as às
  RN/AMB e distribuindo as 63 linhas da seção 7 entre elas.

⏺ Write(specs/001-motor-reembolso/tasks.md)
  ⎿  Added 200 lines, removed 20 lines
        1  # Tasks — Motor de Cálculo de Reembolso
        2  
        3 +**Versão:** 1.0 · **Baseado em:** spec 1.6, plan 1.0          
        4 +                                                              
        5  > Cada task é pequena o bastante para virar **um commit**. Se 
           você não consegue
        6  > descrever o critério de aceite como "o teste X passa", a tas
           k está grande demais.
        7  >
        8  > Marque `[x]` conforme conclui — ao longo do caminho, não tud
           o no fim. O histórico
        9  > de quando cada task foi marcada é lido na correção.
       10  
        9 -**Formato do commit:** `feat(T-003): <descrição>` · `test(T-00
          -3): <descrição>`                                              
       11 +**Formato do commit:** `feat(T-003): <descrição>` · `test(T-00
          +3): <descrição>` · `chore(T-001): <descrição>`                
       12  
       13 +**Como ler cada task:**                                       
       14 +                                                              
       15 +- **Tipo:** `regra` (regra de negócio: passa pelo `revisor-de-
          +task` antes do commit, parecer em `docs/reviews/T-NNN.md`) ou 
          +`estrutura` (setup, leitura/escrita de JSON, CLI: dispensa a r
          +evisão).                                                      
       16 +- **Atende:** as `RN-`/`AMB-` da spec (e as `DT-` do plano) qu
          +e a task implementa.                                          
       17 +- **Depende de:** tasks que precisam estar `[x]` antes.       
       18 +- **Aceite:** os testes que precisam passar. Arquivos em `test
          +s/`; nomes conforme `plan.md` seção 6.                        
       19 +- **Casos de borda:** linhas da tabela da seção 7 da spec que 
          +a task cobre, cada uma um caso de `tests/test_casos_de_borda.p
          +y` com `id` igual ao texto da coluna "Caso". As 63 linhas estã
          +o distribuídas entre as tasks; nenhuma fica sem dono.         
       20 +                                                              
       21 +O esperado de todo teste é calculado à mão a partir da spec, n
          +unca copiado da saída do programa.                            
       22 +                                                              
       23  ---
       24  
       25  ## Fase 1 — Fundação
       26  
       15 -- [ ] **T-001** — <o que faz>                                 
       16 -  - **Atende:** RN-001                                        
       17 -  - **Aceite:** <o teste que precisa passar>                  
       18 -  - **Commit:** `<hash preenchido depois>`                    
       27 +- [ ] **T-001** — Setup do projeto: `pyproject.toml` com `uv` 
          +(Python ≥ 3.12, `simplejson` ≥ 4, `pytest`, `ruff` com regras 
          +`E`, `F`, `I`, `B`, `UP`), pacote `src/reembolso/` com os módu
          +los vazios da seção 2 do plano, entry point `reembolso = "reem
          +bolso.cli:main"` e `tests/conftest.py` com os construtores `en
          +trada(...)` e `despesa(**campos)` (entrada mínima válida).    
       28 +  - **Tipo:** estrutura                                       
       29 +  - **Atende:** plan seções 1, 2 e 6 (fixtures)               
       30 +  - **Depende de:** —                                         
       31 +  - **Aceite:** `uv run pytest -q` e `uv run ruff check .` ver
          +des; `tests/test_setup.py::test_fixture_entrada_minima_e_json_
          +valido` passa (a entrada do construtor é um documento com `col
          +aborador`, `periodo` e `despesas` conforme a seção 4 da spec).
       32 +  - **Commit:**                                               
       33  
       20 -- [ ] **T-002** — <...>                                       
       21 -  - **Atende:**                                               
       22 -  - **Aceite:**                                               
       34 +- [ ] **T-002** — Modelo de dados e política: `modelo.py` (dat
          +aclasses e enums da seção 3 do plano, com `Motivo` na ordem da
          + seção 8 da spec) e `politica.py` (constantes literais da seçã
          +o 4 do plano).                                                
       35 +  - **Tipo:** regra                                           
       36 +  - **Atende:** RN-006 (categorias), RN-008 (100,00), RN-009 (
          +tabela de limites), RN-010 (D e D+1), RN-002 (teto de 1.000.00
          +0.000,00), AMB-006, AMB-018                                   
       37 +  - **Depende de:** T-001                                     
       38 +  - **Aceite:** `tests/test_politica.py` passa: `test_rn009_li
          +mites_conferem_tabela_da_spec` (60/90, 80/120, 250/250), `test
          +_rn006_tres_categorias_reconhecidas`, `test_rn008_valor_de_not
          +a_e_100`, `test_rn002_teto_de_um_bilhao`, `test_rn010_viagem_c
          +obre_d_e_d_mais_1`, `test_motivos_na_ordem_da_secao_8`; todas 
          +as constantes monetárias são `Decimal`.                       
       39    - **Commit:**
       40  
       25 -## Fase 2 — Regras de negócio                                 
       41 +- [ ] **T-003** — Normalização de texto: `normalizar_texto()` 
          +com os 4 passos da seção 5 da spec (DT-004).                  
       42 +  - **Tipo:** regra                                           
       43 +  - **Atende:** seção 5 da spec (normalização), AMB-011; usada
          + por RN-006 e RN-007                                          
       44 +  - **Depende de:** T-001                                     
       45 +  - **Aceite:** `tests/test_normalizacao.py` passa: exemplos d
          +a seção 5 (`"Transporte Urbano"`, `"transporte-urbano"`, `" TR
          +ANSPORTE__urbano "` → `transporte_urbano`; `"Pão  Quente"`, `"
          +pao-quente"` → `pao_quente`); acento pré-composto e combinante
          + dão o mesmo resultado; `ç`, `ô`, `ü`, `ñ`; tabulação, quebra 
          +de linha e espaço não separável nas pontas; mistura de espaço,
          + hífen e sublinhado internos vira um `_`.                     
       46 +  - **Commit:**                                               
       47  
       27 -- [ ] **T-00N** — <...>                                       
       28 -  - **Atende:** RN-00X, AMB-00Y                               
       29 -  - **Aceite:**                                               
       48 +- [ ] **T-004** — Justificativa: `justificativa.py` gera a fra
          +se em português de um item já decidido, para cada status e mot
          +ivo, com formatação própria `1.234,56` e `DD/MM` sem `locale` 
          +(DT-009).                                                     
       49 +  - **Tipo:** estrutura (texto não contratual)                
       50 +  - **Atende:** RN-011 (todo item tem justificativa), DT-009  
       51 +  - **Depende de:** T-002                                     
       52 +  - **Aceite:** `tests/test_justificativa.py` passa: `test_rn0
          +11_justificativa_nao_vazia_para_todo_status_e_motivo` (todas a
          +s combinações de status × motivo da seção 4); `test_formata_de
          +cimal_em_reais` (`Decimal("1234.5")` → `1.234,50`); `test_form
          +ata_data_dd_mm`. O texto exato da frase não é testado.        
       53    - **Commit:**
       54  
       32 -## Fase 3 — Casos de borda                                    
       55 +- [ ] **T-005** — Serialização da saída: `saida.py` converte `
          +Resultado` em dicionário com os campos na ordem da tabela de s
          +aída da seção 4 e em texto JSON (`use_decimal`, `ensure_ascii=
          +False`, `indent=2`, quebra de linha final) (DT-001, DT-008).  
       56 +  - **Tipo:** estrutura (escrita de JSON)                     
       57 +  - **Atende:** seção 4 da spec (Saída), DT-001, DT-008       
       58 +  - **Depende de:** T-002                                     
       59 +  - **Aceite:** `tests/test_saida.py` passa: ordem dos campos 
          +do topo e de `itens[]` igual à tabela da spec; `Decimal` sai c
          +omo número JSON exato, nunca `float` (`Decimal("33.333")` → `3
          +3.333`; `Decimal("1E+999999")` sai como número); campos nulos 
          +saem `null`; `avisos` sai lista vazia quando não há aviso; tex
          +to com quebra de linha sai com `\n`; caractere não ASCII sai e
          +m UTF-8 sem escape; mesma entrada → mesmo texto byte a byte.  
       60 +  - **Commit:**                                               
       61  
       34 -- [ ] **T-00N** — <...>                                       
       62 +## Fase 2 — Entrada (RN-002, RN-013)                          
       63  
       64 +- [ ] **T-006** — Leitura do JSON estrito: bytes → documento, 
          +com `utf-8-sig`, `simplejson` (`use_decimal=True`, `parse_int=
          +Decimal`) e verificação de caractere substituto isolado em cha
          +ves e textos; qualquer falha vira `ErroDeArquivo` (DT-001, DT-
          +002).                                                         
       65 +  - **Tipo:** estrutura (leitura de JSON)                     
       66 +  - **Atende:** RN-002 (arquivo que não é JSON válido; escape 
          +que não forma caractere válido), seção 4 da spec (número pelo 
          +valor decimal exato; texto depois de decodificados os escapes)
          +, DT-001, DT-002                                              
       67 +  - **Depende de:** T-001                                     
       68 +  - **Aceite:** `tests/test_leitura_json.py` passa: `test_rn00
          +2_nan_e_erro_de_arquivo` (`NaN`, `Infinity`, `-Infinity`); `te
          +st_rn002_json_malformado_e_erro_de_arquivo`; `test_rn002_utf8_
          +invalido_e_erro_de_arquivo`; `test_rn002_escape_sem_par_em_val
          +or_e_erro_de_arquivo` e `..._em_chave_...` (`\ud800`); `test_b
          +om_e_aceito`; `test_numero_lido_pelo_valor_exato` (`33.333`, `
          +999999999.99999999999`, `1e999999`, `1e-999999` e inteiro de 5
          +.000 dígitos lidos como `Decimal` exato, sem erro); `test_esca
          +pes_validos_decodificados` (`"2026-07-03"` → `2026-07-03`; emo
          +ji em par de escapes igual ao emoji direto).                  
       69 +  - **Commit:**                                               
       70 +                                                              
       71 +- [ ] **T-007** — Chaves repetidas: `ObjetoJson` via `object_p
          +airs_hook` (vale a última ocorrência) e percurso que gera os a
          +visos do topo e de cada elemento de `despesas`, com texto, cam
          +inho, contagem e ordem da RN-013 (DT-010).                    
       72 +  - **Tipo:** regra                                           
       73 +  - **Atende:** RN-013, AMB-019, DT-010                       
       74 +  - **Depende de:** T-006                                     
       75 +  - **Aceite:** `tests/test_rn013_chave_repetida.py` passa, co
          +brindo o **Aceite** da RN-013 no nível da leitura: `valor` dua
          +s vezes → vale a última, aviso `chave repetida: valor (2 ocorr
          +ências; valeu a última)` no elemento; `colaborador.nome` → avi
          +so no topo com caminho da raiz; `valor` três vezes → um aviso 
          +com `3 ocorrências`; `despesas` repetida → só a última lista, 
          +um aviso `despesas`, chaves repetidas da lista descartada sem 
          +aviso; `extra`/`obs`/`extra.x` na ordem `extra`, `obs`, `extra
          +.x`, cada um com 2; `"valor"` igual a `valor`; forma composta 
          +e decomposta de letra acentuada são chaves diferentes; `m[0][0
          +].x`; elemento-lista `[0].a`; `obs` 1000 vezes → `1000 ocorrên
          +cias`; objeto sem repetição → nenhum aviso.                   
       76 +  - **Commit:**                                               
       77 +                                                              
       78 +- [ ] **T-008** — Validação do cabeçalho: `colaborador`, `peri
          +odo` e `despesas` conforme o primeiro item da RN-002; erro → `
          +ErroDeArquivo`. `competencia` copiada se texto, senão nula.   
       79 +  - **Tipo:** regra                                           
       80 +  - **Atende:** RN-002 (erro de arquivo), seção 4 da spec (Ent
          +rada), DT-003                                                 
       81 +  - **Depende de:** T-006                                     
       82 +  - **Aceite:** `tests/test_rn002_validacao_da_entrada.py` pas
          +sa os testes de cabeçalho: `colaborador` ausente; `id`/`nome` 
          +ausentes, não texto, vazios ou só com espaços em branco (inclu
          +sive espaço não separável); `periodo.inicio`, `periodo.fim` ou
          + `despesas` ausentes; `inicio`/`fim` que não são `AAAA-MM-DD` 
          +válidas (`2026-7-1`, `20260701`, `2026-02-30`, dígitos não ASC
          +II); `inicio` posterior a `fim` → `ErroDeArquivo`. `inicio` ig
          +ual a `fim` → válido. `despesas: []` → válido. `competencia` `
          +202607` → nula, sem erro; `competencia` `"julho"` → copiada. `
          +centro_custo` ausente → válido.                               
       83 +  - **Commit:**                                               
       84 +                                                              
       85 +- [ ] **T-009** — Validação da despesa: cada elemento de `desp
          +esas` vira `Despesa` (válida) ou `DespesaInvalida` (etapa 1 da
          + seção 8), com `categoria_saida` normalizada se reconhecida e 
          +os avisos da T-007 anexados.                                  
       86 +  - **Tipo:** regra                                           
       87 +  - **Atende:** RN-002 (despesa inválida), AMB-018, DT-003    
       88 +  - **Depende de:** T-003, T-007, T-008                       
       89 +  - **Aceite:** `tests/test_rn002_validacao_da_entrada.py` pas
          +sa os testes de despesa: elemento que não é objeto (`null`, nú
          +mero, lista) → inválida com `id`/`data` nulos; cada campo obri
          +gatório ausente; `data` em formato errado (mesmos casos da T-0
          +08); `valor` não número (`"10"`, `true`, `null`); `tem_nota_fi
          +scal` não booleano (`1`, `"sim"`); `id`/`categoria`/`fornecedo
          +r` não texto, vazio ou só espaços; `abs(valor) >= 1000000000` 
          +(inclusive `-1e12` e `1e999999`) → inválida; `999999999.995` e
          + `999999999.99999999999` → válidas; `"id": 17` → `id` nulo; `"
          +ALIMENTACAO"` em despesa inválida → `categoria_saida` `aliment
          +acao`; categoria não reconhecida em despesa inválida → como ve
          +io; campo extra ignorado; `valor_informado` guardado quando é 
          +número.                                                       
       90 +  - **Commit:**                                               
       91 +                                                              
       92 +## Fase 3 — Regras de negócio (motor)                         
       93 +                                                              
       94 +O motor segue o DT-005: fase individual (lista ordenada de ver
          +ificações, etapas 2 a 6), duplicatas (etapa 7), viagem (etapa 
          +8), limite (etapa 9). As tasks abaixo constroem primeiro o cam
          +inho de uma despesa válida até o limite e depois inserem cada 
          +recusa na sua posição da lista. Até a T-015, testes do motor u
          +sam só categorias reconhecidas.                               
       95 +                                                              
       96 +- [ ] **T-010** — Núcleo do motor: um item por despesa na orde
          +m da entrada, arredondamento, limite diário por data e categor
          +ia consumido na ordem da entrada (fora de viagem), status, tot
          +ais; função auxiliar de teste `processar(texto_json) -> dict` 
          +(entrada → motor → saída).                                    
       97 +  - **Tipo:** regra                                           
       98 +  - **Atende:** RN-001, RN-003, RN-009, RN-011, RN-012, AMB-00
          +1, AMB-002, AMB-003, AMB-006, AMB-014, AMB-015, AMB-017       
       99 +  - **Depende de:** T-004, T-005, T-009                       
      100 +  - **Aceite:** passam `test_rn001_um_resultado_por_despesa.py
          +` (N despesas → N itens, mesma ordem de ids; `valor_glosado = 
          +valor_solicitado − valor_reembolsado`), `test_rn003_arredondam
          +ento.py` (33.333 → 33.33; 10.005 → 10.01; 10.004 → 10.00), `te
          +st_rn009_limite_diario.py` (72,50 + 38,00 → 60,00 `parcial` e 
          +0 `recusado`; ordem invertida → 38,00 `aprovado` e 22,00 `parc
          +ial`; limites de transporte 80,00 e hospedagem 250,00; categor
          +ias diferentes na mesma data não dividem limite), `test_rn011_
          +status.py` (status compatível com os valores em todos os itens
          +; `motivo` nulo só em `aprovado`), `test_rn012_hospedagem_uma_
          +diaria.py` (480,00 com nota → `parcial` com 250,00; duas hospe
          +dagens na mesma data dividem 250,00). Item válido sai com `em_
          +viagem` falso e `limite_diario` preenchido.                   
      101 +  - **Casos de borda:** Duas alimentações no mesmo dia somando
          + mais que o limite · Valor exatamente no limite diário · Um ce
          +ntavo acima do limite diário · Duas hospedagens na mesma data 
          +· Três casas decimais · Arredondamento da metade · Lista de de
          +spesas vazia · Despesa em sábado                              
      102 +  - **Commit:**                                               
      103 +                                                              
      104 +- [ ] **T-011** — Despesa inválida na saída: `DespesaInvalida`
          + vira item `recusado` / `entrada_invalida`, com `valor_conside
          +rado`, `em_viagem` e `limite_diario` nulos, fora de `valor_sol
          +icitado`, sem afetar as demais.                               
      105 +  - **Tipo:** regra                                           
      106 +  - **Atende:** RN-002 (saída de despesa inválida), RN-001 (to
          +tais), seção 4 da spec (`itens[].id`, `data`, `categoria`, `va
          +lor_informado`), AMB-018                                      
      107 +  - **Depende de:** T-010                                     
      108 +  - **Aceite:** `tests/test_rn002_validacao_da_entrada.py` pas
          +sa os testes de saída: o **Aceite** da RN-002 inteiro, exceto 
          +os itens de erro de arquivo e CLI (cobertos na T-008 e na T-01
          +9) — despesa sem `tem_nota_fiscal` com 33.333 → `valor_informa
          +do` 33.333, `valor_considerado` nulo, fora de `valor_solicitad
          +o`, demais processadas; `null` em `despesas`; `"id": 17`; `for
          +necedor` `"   "`; `competencia` 202607; `"ALIMENTACAO"` sem `t
          +em_nota_fiscal`; `"noites": 2`; `valor` 1000000000; `-1e12` → 
          +`entrada_invalida`, não `valor_invalido`; `999999999.995` → `v
          +alor_considerado` 1000000000.00.                              
      109 +  - **Casos de borda:** Campo obrigatório ausente · Elemento q
          +ue não é objeto · Campo extra · Campo com tipo errado · Texto 
          +vazio em campo obrigatório · Competência não textual · Texto c
          +om escapes válidos · Categoria reconhecível em despesa inválid
          +a · Valor a partir de um bilhão · Valor logo abaixo de um bilh
          +ão · Valor negativo gigante · Valor com expoente enorme · Muit
          +as casas logo abaixo do teto                                  
      110 +  - **Commit:**                                               
      111 +                                                              
      112 +- [ ] **T-012** — Avisos de chave repetida na saída: avisos da
          + T-007 chegam a `itens[].avisos` e a `avisos` do topo, sem mud
          +ar status, motivo nem valores, inclusive em item recusado.    
      113 +  - **Tipo:** regra                                           
      114 +  - **Atende:** RN-013, AMB-019                               
      115 +  - **Depende de:** T-011                                     
      116 +  - **Aceite:** `tests/test_rn013_chave_repetida.py` passa os 
          +testes de ponta a ponta: o **Aceite** da RN-013 verificado na 
          +saída (despesa avaliada com 50,00 e aviso no item; `colaborado
          +r.nome` no topo com itens de `avisos` vazio; `tem_nota_fiscal`
          + `true` e depois `"sim"` → `entrada_invalida` com aviso; `"val
          +or"` 90,00 → `parcial` com 60,00 e aviso).                    
      117 +  - **Casos de borda:** Chave repetida na despesa · Chave repe
          +tida fora das despesas · Chave repetida dentro de valor descar
          +tado · Mesma chave aninhada no valor descartado e no que valeu
          + · Chave repetida escrita com escape · Lista dentro de lista n
          +o caminho · Chave repetida mil vezes · Chave repetida em eleme
          +nto que é lista                                               
      118 +  - **Commit:**                                               
      119 +                                                              
      120 +- [ ] **T-013** — Valor positivo: etapa 3, `valor_invalido` pa
          +ra `valor_considerado` ≤ 0.                                   
      121 +  - **Tipo:** regra                                           
      122 +  - **Atende:** RN-004, AMB-013                               
      123 +  - **Depende de:** T-010                                     
      124 +  - **Aceite:** `tests/test_rn004_valor_positivo.py` passa: -4
          +5,00 → `recusado`, `valor_invalido`, reembolsado 0, e as demai
          +s despesas do mesmo dia têm o mesmo resultado que teriam sem e
          +la; 0 → `valor_invalido`; 0.004 → `valor_invalido`; item recus
          +ado aqui tem `em_viagem` e `limite_diario` nulos e fica fora d
          +e `valor_solicitado`.                                         
      125 +  - **Casos de borda:** Estorno · Valor zero · Arredondamento 
          +da metade negativa · Valor minúsculo                          
      126 +  - **Commit:**                                               
      127 +                                                              
      128 +- [ ] **T-014** — Período: etapa 4, `fora_do_periodo` para dat
          +a fora de `[inicio, fim]`.                                    
      129 +  - **Tipo:** regra                                           
      130 +  - **Atende:** RN-005, AMB-009                               
      131 +  - **Depende de:** T-013                                     
      132 +  - **Aceite:** `tests/test_rn005_periodo.py` passa: período 2
          +026-07-01 a 2026-07-31 — 2026-04-15 → `fora_do_periodo`; 2026-
          +07-01 e 2026-07-31 → seguem; 2026-06-30 e 2026-08-01 → `fora_d
          +o_periodo`; despesa com valor ≤ 0 fora do período → `valor_inv
          +alido` (etapa 3 vem antes).                                   
      133 +  - **Casos de borda:** Primeiro e último dia do período · Um 
          +dia fora do período · Despesa antiga lançada no período       
      134 +  - **Commit:**                                               
      135 +                                                              
      136 +- [ ] **T-015** — Categoria: etapa 5, `categoria_fora_da_polit
          +ica` para categoria normalizada fora das três reconhecidas; ca
          +tegoria reconhecida sai normalizada.                          
      137 +  - **Tipo:** regra                                           
      138 +  - **Atende:** RN-006, AMB-011, AMB-012                      
      139 +  - **Depende de:** T-014                                     
      140 +  - **Aceite:** `tests/test_rn006_categorias.py` passa: `ALIME
          +NTACAO`, `" Alimentacao "`, `"alimentacao\t"`, `alimentação` →
          + `alimentacao` na saída e limite de alimentação; `"Transporte 
          +Urbano"`, `"transporte-urbano"` → `transporte_urbano`; `cowork
          +ing` → `categoria_fora_da_politica`, `categoria` `coworking` n
          +a saída, item presente (não omitido); despesa fora do período 
          +com categoria desconhecida → `fora_do_periodo` (etapa 4 vem an
          +tes).                                                         
      141 +  - **Casos de borda:** Categoria em maiúsculas · Categoria co
          +m acento · Categoria com separador diferente · Categoria com t
          +abulação no fim                                               
      142 +  - **Commit:**                                               
      143 +                                                              
      144 +- [ ] **T-016** — Nota fiscal: etapa 6, `nota_fiscal_ausente` 
          +para `valor_considerado` > 100,00 sem nota, comparando o valor
          + individual antes do limite.                                  
      145 +  - **Tipo:** regra                                           
      146 +  - **Atende:** RN-008, AMB-007, AMB-008                      
      147 +  - **Depende de:** T-015                                     
      148 +  - **Aceite:** `tests/test_rn008_nota_fiscal.py` passa: 100,0
          +0 sem nota → segue (transporte: `parcial` com 80,00); 100,01 s
          +em nota → `nota_fiscal_ausente`; 100,01 com nota → segue; 100.
          +004 sem nota (considerado 100,00) → segue; 100.005 sem nota (c
          +onsiderado 100,01) → `nota_fiscal_ausente`; despesa recusada a
          +qui não consome limite (alimentação de 150,00 sem nota seguida
          + de 50,00 no mesmo dia → a segunda `aprovado` com 50,00); cate
          +goria desconhecida acima de 100,00 sem nota → `categoria_fora_
          +da_politica` (etapa 5 vem antes).                             
      149 +  - **Casos de borda:** Valor exatamente no limite de nota · U
          +m centavo acima do limite de nota                             
      150 +  - **Commit:**                                               
      151 +                                                              
      152 +- [ ] **T-017** — Duplicatas: etapa 7, agrupa as despesas que 
          +passaram pelas etapas 1 a 6 por (data, categoria normalizada, 
          +fornecedor normalizado, `valor_considerado`); a original é a p
          +rimeira com nota, ou a primeira na ordem; as demais → `duplica
          +ta`.                                                          
      153 +  - **Tipo:** regra                                           
      154 +  - **Atende:** RN-007, AMB-010, AMB-016                      
      155 +  - **Depende de:** T-016                                     
      156 +  - **Aceite:** `tests/test_rn007_duplicatas.py` passa: d-006/
          +d-007 (54,90, ambas com nota) → primeira avaliada, segunda `du
          +plicata`; `id`, `descricao` e `tem_nota_fiscal` diferentes não
          + impedem a duplicata; sem nota antes e com nota depois (valor 
          +≤ 100) → a com nota é a original, a sem nota `duplicata`, nas 
          +duas ordens; táxi 110,00 sem nota + o mesmo com nota → `nota_f
          +iscal_ausente` e o outro avaliado, nas duas ordens; nenhuma co
          +m nota → a primeira é a original; duplicata não consome limite
          + (alimentação 54,90 + duplicata 54,90 → a original `aprovado` 
          +com 54,90); três cópias → uma original e duas `duplicata`; "Bi
          +stro Central" e "Bistrô Central" → mesmo fornecedor.          
      157 +  - **Casos de borda:** Duplicata exata · Fornecedor com acent
          +o · Fornecedor com espaços internos · Quase duplicata · Cópias
          + idênticas sem nota acima de 100 · Relançamento com nota      
      158 +  - **Commit:**                                               
      159 +                                                              
      160 +- [ ] **T-018** — Viagem: etapa 8, antes do limite, `dias_em_v
          +iagem` = {D, D+1} de cada hospedagem com nota que passou pelas
          + etapas 1 a 7; nessas datas, limites de alimentação e transpor
          +te em viagem; `em_viagem` verdadeiro no item.                 
      161 +  - **Tipo:** regra                                           
      162 +  - **Atende:** RN-010, RN-012 (parte de viagem), AMB-004, AMB
          +-005, AMB-006                                                 
      163 +  - **Depende de:** T-017                                     
      164 +  - **Aceite:** `tests/test_rn010_viagem.py` passa: hospedagem
          + com nota em 14/07 → 14/07 e 15/07 em viagem; alimentação 80,0
          +0 em 15/07 → limite 90,00, `aprovado`; alimentação 80,00 em 16
          +/07 → limite 60,00, `parcial` com 60,00; transporte em viagem 
          +→ limite 120,00; hospedagem em viagem continua com limite 250,
          +00; hospedagem 80,00 sem nota → reembolsada, mas data não fica
          + em viagem; hospedagem com nota recusada nas etapas 1 a 7 (for
          +a do período, duplicata) não comprova viagem; hospedagem com n
          +ota que recebe 0 no limite (terceira do dia) comprova viagem; 
          +alimentação antes da hospedagem na entrada → em viagem; hosped
          +agem em 31/07 põe 01/08 em viagem sem efeito (fora do período)
          +. `test_rn012_hospedagem_uma_diaria.py`: 480,00 com nota em 14
          +/07 → 14/07 e 15/07 em viagem, não 16/07.                     
      165 +  - **Casos de borda:** Limite de nota em viagem · Duplicata d
          +e hospedagem só uma com nota · Hospedagem com várias diárias n
          +a descrição · Dia seguinte à diária · Dois dias depois da diár
          +ia · Hospedagem sem nota até 100 · Hospedagem sem nota acima d
          +e 100 · Hospedagem fora do período · Alimentação antes da hosp
          +edagem na entrada, mesma data                                 
      166 +  - **Commit:**                                               
      167 +                                                              
      168  ## Fase 4 — Saída e CLI
      169  
       38 -- [ ] **T-00N** — <...>                                       
      170 +- [ ] **T-019** — CLI: `reembolso calcular --input X --output 
          +Y` com `argparse`, leitura de bytes, pipeline em memória, grav
          +ação atômica (temporário no mesmo diretório + `os.replace`), c
          +ódigos 0 / 1 / 2 e mensagem `erro: ...` em stderr, sem stack t
          +race em erro previsto (DT-006, DT-007).                       
      171 +  - **Tipo:** estrutura (CLI)                                 
      172 +  - **Atende:** seção 4 da spec (Interface), RN-002 (erro de a
          +rquivo, saída não gravável), DT-006, DT-007                   
      173 +  - **Depende de:** T-018                                     
      174 +  - **Aceite:** `tests/test_cli.py` passa: sucesso → código 0 
          +e arquivo de saída igual a `processar()` da mesma entrada; arq
          +uivo de entrada ausente → código 1, sem saída; erro de arquivo
          + com saída preexistente → arquivo intacto byte a byte; pasta d
          +e saída inexistente → código 1; sem `--input`, sem `--output` 
          +ou subcomando diferente de `calcular` → código 2, sem saída; n
          +enhum temporário sobra no diretório em erro; stderr sem `Trace
          +back`.                                                        
      175 +  - **Casos de borda:** Saída não gravável · Colaborador ausen
          +te · Colaborador com texto vazio · Saída preexistente com erro
          + · Escape sem caractere válido · Erro de uso                  
      176 +  - **Commit:**                                               
      177  
      178 +- [ ] **T-020** — Aceite com o arquivo de exemplo: `exemplos/d
          +espesas-exemplo.json` pela CLI contra a tabela da seção 9 da s
          +pec, **transcrita à mão** no teste.                           
      179 +  - **Tipo:** regra                                           
      180 +  - **Atende:** seção 9 da spec (critérios de aceite), RN-001 
          +a RN-012                                                      
      181 +  - **Depende de:** T-019                                     
      182 +  - **Aceite:** `tests/test_exemplo.py` passa: as 14 linhas da
          + tabela da seção 9 (considerado, em viagem, limite, reembolsad
          +o, status, motivo), totais 1.861,84 / 585,43 / 1.276,41, `avis
          +os` vazios no topo e em todos os itens; `test_determinismo_byt
          +e_a_byte` (duas execuções → arquivos idênticos); `test_nenhum_
          +valor_monetario_e_float` (propriedade da DT-001 sobre a saída 
          +lida com `Decimal`).                                          
      183 +  - **Commit:**                                               
      184 +                                                              
      185 +- [ ] **T-021** — Rastreabilidade automática: `tests/test_rast
          +reabilidade.py` lê a `spec.md`, extrai todos os `RN-NNN` e tod
          +os os valores da coluna "Caso" da seção 7, e falha se algum nã
          +o tiver teste (RN no nome ou docstring; caso como `id` em `tes
          +t_casos_de_borda.py`). Preenche a tabela de Cobertura abaixo. 
      186 +  - **Tipo:** estrutura                                       
      187 +  - **Atende:** seção 9 da spec (cada caso de borda e cada RN 
          +com teste), plan seção 6                                      
      188 +  - **Depende de:** T-020                                     
      189 +  - **Aceite:** `tests/test_rastreabilidade.py` passa com a su
          +íte completa; remover qualquer teste de RN ou caso de borda o 
          +faz falhar (verificado à mão uma vez e registrado no resumo da
          + task); tabela de Cobertura sem célula vazia.                 
      190 +  - **Commit:**                                               
      191 +                                                              
      192  ---
      193  
      194  ## Fase 5 — Envelope (criar no Dia 2)
     ...
      200  
      201  ## Cobertura
      202  
       51 -Preencha ao fechar cada fase. É a sua própria checagem de rast
          -reabilidade — e é                                             
       52 -exatamente a matriz que a correção vai montar.                
      203 +Preenchida ao fechar cada fase (a T-021 confere que não falta 
          +nada).                                                        
      204  
      205  | Regra da spec | Task | Teste |
      206  |---|---|---|
       56 -| RN-001 | T-00X | `<nome do teste>` |                        
       57 -| RN-002 | | |                                                
       58 -| AMB-001 | | |                                               
      207 +| RN-001 | T-010, T-011 | `test_rn001_um_resultado_por_despesa
          +.py` |                                                        
      208 +| RN-002 | T-006, T-008, T-009, T-011, T-019 | `test_leitura_j
          +son.py`, `test_rn002_validacao_da_entrada.py`, `test_cli.py` |
      209 +| RN-003 | T-010 | `test_rn003_arredondamento.py` |           
      210 +| RN-004 | T-013 | `test_rn004_valor_positivo.py` |           
      211 +| RN-005 | T-014 | `test_rn005_periodo.py` |                  
      212 +| RN-006 | T-002, T-015 | `test_politica.py`, `test_rn006_cate
          +gorias.py` |                                                  
      213 +| RN-007 | T-017 | `test_rn007_duplicatas.py` |               
      214 +| RN-008 | T-002, T-016 | `test_politica.py`, `test_rn008_nota
          +_fiscal.py` |                                                 
      215 +| RN-009 | T-002, T-010 | `test_politica.py`, `test_rn009_limi
          +te_diario.py` |                                               
      216 +| RN-010 | T-002, T-018 | `test_politica.py`, `test_rn010_viag
          +em.py` |                                                      
      217 +| RN-011 | T-004, T-010 | `test_justificativa.py`, `test_rn011
          +_status.py` |                                                 
      218 +| RN-012 | T-010, T-018 | `test_rn012_hospedagem_uma_diaria.py
          +` |                                                           
      219 +| RN-013 | T-007, T-012 | `test_rn013_chave_repetida.py` |    
      220 +| Seção 5 (normalização) | T-003 | `test_normalizacao.py` |   
      221 +| Seção 7 (63 casos) | T-010 a T-019 | `test_casos_de_borda.py
          +` |                                                           
      222 +| Seção 9 (exemplo) | T-020 | `test_exemplo.py` |             
      223 +| AMB-001, AMB-002, AMB-003 | T-010 | `test_rn009_limite_diari
          +o.py` |                                                       
      224 +| AMB-004 | T-018 | `test_rn010_viagem.py` |                  
      225 +| AMB-005 | T-010, T-018 | `test_rn012_hospedagem_uma_diaria.p
          +y` |                                                          
      226 +| AMB-006 | T-002, T-010, T-018 | `test_politica.py`, `test_rn
          +010_viagem.py` |                                              
      227 +| AMB-007, AMB-008 | T-016 | `test_rn008_nota_fiscal.py` |    
      228 +| AMB-009 | T-014 | `test_rn005_periodo.py` |                 
      229 +| AMB-010 | T-017 | `test_rn007_duplicatas.py` |              
      230 +| AMB-011 | T-003, T-015 | `test_normalizacao.py`, `test_rn006
          +_categorias.py` |                                             
      231 +| AMB-012 | T-015 | `test_rn006_categorias.py` |              
      232 +| AMB-013 | T-013 | `test_rn004_valor_positivo.py` |          
      233 +| AMB-014 | T-010 | `test_rn003_arredondamento.py` |          
      234 +| AMB-015 | T-010 | `test_casos_de_borda.py` (Despesa em sábad
          +o) |                                                          
      235 +| AMB-016 | T-013 a T-018 | testes de ordem entre etapas em ca
          +da `test_rnNNN_*.py` |                                        
      236 +| AMB-017 | T-010 | `test_rn009_limite_diario.py` |           
      237 +| AMB-018 | T-002, T-009, T-011 | `test_rn002_validacao_da_ent
          +rada.py` |                                                    
      238 +| AMB-019 | T-007, T-012 | `test_rn013_chave_repetida.py` |   

⏺ Vou conferir se os 63 nomes de casos de borda batem exatamente com a seção 7 e
  se cada um aparece uma única vez.

  Ran 1 shell command (ctrl+o to expand)

⏺ Escrevi o specs/001-motor-reembolso/tasks.md (v1.0, baseado na spec 1.6 e no
  plan 1.0) com 21 tasks. Ainda não fiz o commit.

  As 21 tasks, por fase

  - Fundação (T-001 a T-005): setup do projeto com uv, pytest, ruff e as
    fixtures; modelo de dados e política; normalização de texto; justificativa;
    serialização da saída.
  - Entrada (T-006 a T-009): leitura estrita do JSON; chaves repetidas (RN-013);
    validação do cabeçalho; validação de cada despesa (RN-002).
  - Motor (T-010 a T-018):
    - A T-010 constrói o caminho de uma despesa válida: um item por despesa,
      arredondamento, limite diário, status e hospedagem como uma diária
      (RN-001, RN-003, RN-009, RN-011, RN-012).
    - A T-011 trata despesa inválida na saída e a T-012 leva os avisos de chave
      repetida até a saída.
    - Da T-013 à T-018 entra uma regra por task, cada uma na sua posição da
      seção 8: RN-004, RN-005, RN-006, RN-008, RN-007 e RN-010.
  - CLI e aceite (T-019 a T-021): a CLI com gravação atômica; o teste com o
    arquivo de exemplo contra a tabela da seção 9, transcrita à mão; um teste
    que falha se alguma RN ou caso de borda ficar sem teste.

  Formato de cada task
  - Cada task tem Tipo, que indica se precisa do revisor-de-task ou dispensa por
    ser estrutura, e Depende de, que a skill /task confere no passo 1.
  - O Aceite lista os testes concretos com os valores esperados tirados da spec.
  - As 63 linhas da seção 7 estão distribuídas entre a T-010 e a T-019. Um
    script confirmou que todas aparecem, cada uma uma vez só, e com o texto
    exato da coluna "Caso".
  - A tabela de Cobertura já está preenchida com RN/AMB → task → arquivo de
    teste.

  Duas escolhas que valem sua revisão
  1. Ordem de construção diferente da ordem de aplicação: primeiro sai o caminho
     de uma despesa válida até o limite (T-010), e só depois cada recusa é
     inserida na sua posição. O motivo é que todo item precisa de um status, e
     isso só existe quando o limite está pronto. A ordem da seção 8 continua no
     código. Por isso, até a T-015, os testes do motor usam só categorias
     reconhecidas.
  2. Testes extras de interação entre etapas: acrescentei ao aceite das tasks
     alguns testes que não estão literalmente na spec, mas saem direto da
     seção 8. Exemplos: "despesa fora do período e com valor ≤ 0 →
     valor_invalido" e "terceira hospedagem do dia, que recebe 0 no limite,
     ainda comprova viagem". Nenhum deles cria regra nova.

  Fora do tasks.md: a seção "Stack e comandos" do CLAUDE.md ainda está com os
  <...> do template. Posso preencher com o que o plan define (Python 3.12/uv, uv
  run reembolso calcular ..., uv run pytest -q, uv run ruff check ., valores em
  Decimal) num commit separado, docs(claude): ....

  Commit proposto: docs(tasks): tasks 1.0 sobre spec 1.6 e plan 1.0. Posso
  commitar?

✻ Cogitated for 3m 54s · done 10:26 PM

❯ pode commitar                                                                 

  Ran 1 shell command (ctrl+o to expand)
  ⎿  PostToolUse:Bash says: 📝 Fim do bloco de trabalho ("docs(tasks): tasks 1.0
     sobre spec 1.6 e plan 1.0"). Exporte a sessão antes de continuar:
        /export docs/sessions/08-<descricao-curta>.md
        e commite com: docs(sessions): export da sessão 08

⏺ Commitei o tasks.md como 70b9d31 docs(tasks): tasks 1.0 sobre spec 1.6 e plan 
  1.0, e o diretório está limpo. Como o commit só mexeu em documentação, o hook
  não rodou ruff nem pytest.

  Isso fecha um bloco de trabalho, então antes de seguir exporte a sessão:

  /export docs/sessions/08-tasks.md

  Depois eu commito com docs(sessions): export da sessão 08.

  Para depois do export:
  - CLAUDE.md: a seção "Stack e comandos" ainda está com os <...> do modelo.
    Posso preencher com o que o plan define, num commit docs(claude).
  - Implementação: começa com /task T-001 (setup do projeto). Não vou começar
    sem você pedir.

✻ Crunched for 11s · done 10:27 PM