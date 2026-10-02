# Tasks — Motor de Cálculo de Reembolso

**Versão:** 1.2 · **Baseado em:** spec 1.9, plan 1.2

> Cada task é pequena o bastante para virar **um commit**. Se você não consegue
> descrever o critério de aceite como "o teste X passa", a task está grande demais.
>
> Marque `[x]` conforme conclui — ao longo do caminho, não tudo no fim. O histórico
> de quando cada task foi marcada é lido na correção.

**Formato do commit:** `feat(T-003): <descrição>` · `test(T-003): <descrição>` · `chore(T-001): <descrição>`

**Como ler cada task:**

- **Tipo:** `regra` (regra de negócio: passa pelo `revisor-de-task` antes do commit, parecer em `docs/reviews/T-NNN.md`) ou `estrutura` (setup, leitura/escrita de JSON, CLI: dispensa a revisão).
- **Atende:** as `RN-`/`AMB-` da spec (e as `DT-` do plano) que a task implementa.
- **Depende de:** tasks que precisam estar `[x]` antes.
- **Aceite:** os testes que precisam passar. Arquivos em `tests/`; nomes conforme `plan.md` seção 6.
- **Casos de borda:** linhas da tabela da seção 7 da spec que a task cobre, cada uma um caso de `tests/test_casos_de_borda.py` com `id` igual ao texto da coluna "Caso". As 63 linhas estão distribuídas entre as tasks; nenhuma fica sem dono.

O esperado de todo teste é calculado à mão a partir da spec, nunca copiado da saída do programa.

---

## Fase 1 — Fundação

- [x] **T-001** — Setup do projeto: `pyproject.toml` com `uv` (Python ≥ 3.12, `simplejson` ≥ 4, `pytest`, `ruff` com regras `E`, `F`, `I`, `B`, `UP`), pacote `src/reembolso/` com os módulos vazios da seção 2 do plano, entry point `reembolso = "reembolso.cli:main"` e `tests/conftest.py` com os construtores `entrada(...)` e `despesa(**campos)` (entrada mínima válida).
  - **Tipo:** estrutura
  - **Atende:** plan seções 1, 2 e 6 (fixtures)
  - **Depende de:** —
  - **Aceite:** `uv run pytest -q` e `uv run ruff check .` verdes; `tests/test_setup.py::test_fixture_entrada_minima_e_json_valido` passa (a entrada do construtor é um documento com `colaborador`, `periodo` e `despesas` conforme a seção 4 da spec).
  - **Commit:** 805aee5

- [x] **T-002** — Modelo de dados e política: `modelo.py` (dataclasses e enums da seção 3 do plano, com `Motivo` na ordem da seção 8 da spec) e `politica.py` (constantes literais da seção 4 do plano).
  - **Tipo:** regra
  - **Atende:** RN-006 (categorias), RN-008 (100,00), RN-009 (tabela de limites), RN-010 (D e D+1), RN-002 (teto de 1.000.000.000,00), AMB-006, AMB-018
  - **Depende de:** T-001
  - **Aceite:** `tests/test_politica.py` passa: `test_rn009_limites_conferem_tabela_da_spec` (60/90, 80/120, 250/250), `test_rn006_tres_categorias_reconhecidas`, `test_rn008_valor_de_nota_e_100`, `test_rn002_teto_de_um_bilhao`, `test_rn010_viagem_cobre_d_e_d_mais_1`, `test_motivos_na_ordem_da_secao_8`; todas as constantes monetárias são `Decimal`.
  - **Commit:** 6e1f498

- [x] **T-003** — Normalização de texto: `normalizar_texto()` com os passos da seção 5 da spec (DT-004).
  - **Tipo:** regra
  - **Atende:** seção 5 da spec (normalização), AMB-011, D-005; usada por RN-002, RN-006 e RN-007
  - **Depende de:** T-001
  - **Aceite:** `tests/test_normalizacao.py` passa: exemplos da seção 5 (`"Transporte Urbano"`, `"transporte-urbano"`, `" TRANSPORTE__urbano "`, `"Transporte – Urbano"` → `transporte_urbano`; `"Pão  Quente"`, `"pao-quente"` → `pao_quente`; `"-Bistro"`, `"_Bistro"`, `"Bistro -"`, `" -_Bistro"` → `bistro`; `"Padaria (Centro)"` → `padaria_centro`; `"McDonald's"` → `mcdonald_s`; `"Straße"` → `strasse`; `"Padaria Nº 1"` → `padaria_nº_1` e `"Padaria N° 1"` → `padaria_n_1`; `"Loja²"` → `loja`; `"Smørrebrød"` → `smørrebrød`; `"-"` → vazio); acento pré-composto e combinante dão o mesmo resultado; `ç`, `ô`, `ü`, `ñ`; sinal combinante solto (no início, sobre hífen no fim) é descartado; tabulação, quebra de linha, espaço não separável, espaço de largura zero e caractere de controle nas pontas; mistura de separadores internos de qualquer tipo vira um `_`; letras de qualquer alfabeto e algarismos decimais de qualquer escrita são mantidos como estão; número que não é dígito decimal (`²`, `½`) é separador.
  - **Commit:** aaf201a

- [x] **T-004** — Justificativa: `justificativa.py` gera a frase em português de um item já decidido, para cada status e motivo, com formatação própria `1.234,56` e `DD/MM` sem `locale` (DT-009).
  - **Tipo:** estrutura (texto não contratual)
  - **Atende:** RN-011 (todo item tem justificativa), DT-009
  - **Depende de:** T-002
  - **Aceite:** `tests/test_justificativa.py` passa: `test_rn011_justificativa_nao_vazia_para_todo_status_e_motivo` (todas as combinações de status × motivo da seção 4); `test_formata_decimal_em_reais` (`Decimal("1234.5")` → `1.234,50`); `test_formata_data_dd_mm`. O texto exato da frase não é testado.
  - **Commit:** 18a8117

- [x] **T-005** — Serialização da saída: `saida.py` converte `Resultado` em dicionário com os campos na ordem da tabela de saída da seção 4 e em texto JSON (`use_decimal`, `ensure_ascii=False`, `indent=2`, quebra de linha final) (DT-001, DT-008).
  - **Tipo:** estrutura (escrita de JSON)
  - **Atende:** seção 4 da spec (Saída), DT-001, DT-008
  - **Depende de:** T-002
  - **Aceite:** `tests/test_saida.py` passa: ordem dos campos do topo e de `itens[]` igual à tabela da spec; `Decimal` sai como número JSON exato, nunca `float` (`Decimal("33.333")` → `33.333`; `Decimal("1E+999999")` sai como número); campos nulos saem `null`; `avisos` sai lista vazia quando não há aviso; texto com quebra de linha sai com `\n`; caractere não ASCII sai em UTF-8 sem escape; mesma entrada → mesmo texto byte a byte.
  - **Commit:** dea6ff9

## Fase 2 — Entrada (RN-002, RN-013)

- [x] **T-006** — Leitura do JSON estrito: bytes → documento, com `utf-8-sig`, `simplejson` (`use_decimal=True`, `parse_int=Decimal`) e verificação de caractere substituto isolado em chaves e textos; qualquer falha vira `ErroDeArquivo` (DT-001, DT-002).
  - **Tipo:** estrutura (leitura de JSON)
  - **Atende:** RN-002 (arquivo que não é JSON válido; escape que não forma caractere válido), seção 4 da spec (número pelo valor decimal exato; texto depois de decodificados os escapes), DT-001, DT-002
  - **Depende de:** T-001
  - **Aceite:** `tests/test_leitura_json.py` passa: `test_rn002_nan_e_erro_de_arquivo` (`NaN`, `Infinity`, `-Infinity`); `test_rn002_json_malformado_e_erro_de_arquivo`; `test_rn002_utf8_invalido_e_erro_de_arquivo`; `test_rn002_escape_sem_par_em_valor_e_erro_de_arquivo` e `..._em_chave_...` (`\ud800`); `test_rn002_escape_sem_par_em_ocorrencia_descartada_e_erro_de_arquivo` (`"obs": "\ud800", "obs": "ok"`, em valor e em objeto aninhado descartado; D-006); `test_escape_fora_dos_substitutos_forma_caractere_valido` (`\u0000`, `\uffff`, `\ufdd0` lidos como caractere, sem erro; D-006); `test_bom_e_aceito`; `test_segundo_bom_e_erro_de_arquivo` (D-006); `test_aninhamento_exagerado_e_erro_de_arquivo` (5.000 e 100.000 níveis → `ErroDeArquivo`, não erro interno; D-006); `test_rn002_json_malformado_e_erro_de_arquivo` inclui `01.5`, `.5`, `1.`, `+1` e tabulação, quebra de linha e U+0000 crus em texto; `test_rn002_escape_sem_par_em_valor_e_erro_de_arquivo` inclui par invertido e alto solto antes de emoji (D-006); `test_numero_lido_pelo_valor_exato` (`33.333`, `999999999.99999999999`, `1e999999`, `1e-999999` e inteiro de 5.000 dígitos lidos como `Decimal` exato, sem erro); `test_escapes_validos_decodificados` (`"2026-07-03"` → `2026-07-03`; emoji em par de escapes igual ao emoji direto).
  - **Commit:** e84693c

- [x] **T-007** — Chaves repetidas: `ObjetoJson` via `object_pairs_hook` (vale a última ocorrência) e percurso que gera os avisos do topo e de cada elemento de `despesas`, com texto, caminho, contagem e ordem da RN-013 (DT-010).
  - **Tipo:** regra
  - **Atende:** RN-013, AMB-019, DT-010
  - **Depende de:** T-006
  - **Aceite:** `tests/test_rn013_chave_repetida.py` passa, cobrindo o **Aceite** da RN-013 no nível da leitura: `valor` duas vezes → vale a última, aviso `chave repetida: valor (2 ocorrências; valeu a última)` no elemento; `colaborador.nome` → aviso no topo com caminho da raiz; `valor` três vezes → um aviso com `3 ocorrências`; `despesas` repetida → só a última lista, um aviso `despesas`, chaves repetidas da lista descartada sem aviso; `extra`/`obs`/`extra.x` na ordem `extra`, `obs`, `extra.x`, cada um com 2; `"valor"` igual a `valor`; forma composta e decomposta de letra acentuada são chaves diferentes; `m[0][0].x`; elemento-lista `[0].a`; `obs` 1000 vezes → `1000 ocorrências`; objeto sem repetição → nenhum aviso.
  - **Commit:** ae9e75b

- [x] **T-008** — Validação do cabeçalho: `colaborador`, `periodo` e `despesas` conforme o primeiro item da RN-002; erro → `ErroDeArquivo`. `competencia` copiada se texto, senão nula.
  - **Tipo:** regra
  - **Atende:** RN-002 (erro de arquivo), seção 4 da spec (Entrada), DT-003
  - **Depende de:** T-006
  - **Aceite:** `tests/test_rn002_validacao_da_entrada.py` passa os testes de cabeçalho: `colaborador` ausente; `id`/`nome` ausentes, não texto, vazios ou só com espaços em branco (inclusive espaço não separável); `nome` só de U+200B, BOM ou U+001F → válido (não é espaço em branco, RN-002); `periodo.inicio`, `periodo.fim` ou `despesas` ausentes; `inicio`/`fim` que não são `AAAA-MM-DD` válidas (`2026-7-1`, `20260701`, `2026-02-30`, dígitos não ASCII); `inicio` posterior a `fim` → `ErroDeArquivo`. `inicio` igual a `fim` → válido. `despesas: []` → válido. `competencia` `202607` → nula, sem erro; `competencia` `"julho"` → copiada. `centro_custo` ausente → válido. `colaborador` com `nome` `""` seguido de `colaborador` com `nome` `"Ana"` → válido, `nome` `Ana` (só o valor que valeu é validado; RN-013, D-006).
  - **Commit:** 8efe738

- [x] **T-009** — Validação da despesa: cada elemento de `despesas` vira `Despesa` (válida) ou `DespesaInvalida` (etapa 1 da seção 8), com `categoria_saida` normalizada se reconhecida e os avisos da T-007 anexados.
  - **Tipo:** regra
  - **Atende:** RN-002 (despesa inválida), AMB-018, DT-003
  - **Depende de:** T-003, T-007, T-008
  - **Aceite:** `tests/test_rn002_validacao_da_entrada.py` passa os testes de despesa: elemento que não é objeto (`null`, número, lista) → inválida com `id`/`data` nulos; cada campo obrigatório ausente; `data` em formato errado (mesmos casos da T-008); `valor` não número (`"10"`, `true`, `null`); `tem_nota_fiscal` não booleano (`1`, `"sim"`); `id`/`categoria`/`fornecedor` não texto, vazio ou só espaços; `id` `"-"` ou só de U+200B → válido; `categoria`/`fornecedor` cujo texto normalizado fica vazio (`"-"`, `"***"`); `abs(valor) >= 1000000000` (inclusive `-1e12` e `1e999999`) → inválida; `999999999.995` e `999999999.99999999999` → válidas; `"id": 17` → `id` nulo; `"ALIMENTACAO"` em despesa inválida → `categoria_saida` `alimentacao`; categoria não reconhecida em despesa inválida → como veio; campo extra ignorado; `valor_informado` guardado quando é número.
  - **Commit:** 117814a

## Fase 3 — Regras de negócio (motor)

O motor segue o DT-005: fase individual (lista ordenada de verificações, etapas 2 a 6), duplicatas (etapa 7), viagem (etapa 8), limite (etapa 9). As tasks abaixo constroem primeiro o caminho de uma despesa válida até o limite e depois inserem cada recusa na sua posição da lista. Até a T-015, testes do motor usam só categorias reconhecidas.

- [x] **T-010** — Núcleo do motor: um item por despesa na ordem da entrada, arredondamento, limite diário por data e categoria consumido na ordem da entrada (fora de viagem), status, totais; função auxiliar de teste `processar(texto_json) -> dict` (entrada → motor → saída).
  - **Tipo:** regra
  - **Atende:** RN-001, RN-003, RN-009, RN-011, RN-012, AMB-001, AMB-002, AMB-003, AMB-006, AMB-014, AMB-015, AMB-017
  - **Depende de:** T-004, T-005, T-009
  - **Aceite:** passam `test_rn001_um_resultado_por_despesa.py` (N despesas → N itens, mesma ordem de ids; `valor_glosado = valor_solicitado − valor_reembolsado`), `test_rn003_arredondamento.py` (33.333 → 33.33; 10.005 → 10.01; 10.004 → 10.00), `test_rn009_limite_diario.py` (72,50 + 38,00 → 60,00 `parcial` e 0 `recusado`; ordem invertida → 38,00 `aprovado` e 22,00 `parcial`; limites de transporte 80,00 e hospedagem 250,00; categorias diferentes na mesma data não dividem limite), `test_rn011_status.py` (status compatível com os valores em todos os itens; `motivo` nulo só em `aprovado`), `test_rn012_hospedagem_uma_diaria.py` (480,00 com nota → `parcial` com 250,00; duas hospedagens na mesma data dividem 250,00). Item válido sai com `em_viagem` falso e `limite_diario` preenchido.
  - **Casos de borda:** Duas alimentações no mesmo dia somando mais que o limite · Valor exatamente no limite diário · Um centavo acima do limite diário · Duas hospedagens na mesma data · Três casas decimais · Arredondamento da metade · Lista de despesas vazia · Despesa em sábado
  - **Commit:** b50dbfa

- [x] **T-011** — Despesa inválida na saída: `DespesaInvalida` vira item `recusado` / `entrada_invalida`, com `valor_considerado`, `em_viagem` e `limite_diario` nulos, fora de `valor_solicitado`, sem afetar as demais.
  - **Tipo:** regra
  - **Atende:** RN-002 (saída de despesa inválida), RN-001 (totais), seção 4 da spec (`itens[].id`, `data`, `categoria`, `valor_informado`), AMB-018
  - **Depende de:** T-010
  - **Aceite:** `tests/test_rn002_validacao_da_entrada.py` passa os testes de saída: o **Aceite** da RN-002 inteiro, exceto os itens de erro de arquivo e CLI (cobertos na T-008 e na T-019) — despesa sem `tem_nota_fiscal` com 33.333 → `valor_informado` 33.333, `valor_considerado` nulo, fora de `valor_solicitado`, demais processadas; `null` em `despesas`; `"id": 17`; `fornecedor` `"   "`; `competencia` 202607; `"ALIMENTACAO"` sem `tem_nota_fiscal`; `"noites": 2`; `valor` 1000000000; `-1e12` → `entrada_invalida`, não `valor_invalido`; `999999999.995` → `valor_considerado` 1000000000.00.
  - **Casos de borda:** Campo obrigatório ausente · Elemento que não é objeto · Campo extra · Campo com tipo errado · Texto vazio em campo obrigatório · Competência não textual · Texto com escapes válidos · Categoria reconhecível em despesa inválida · Valor a partir de um bilhão · Valor logo abaixo de um bilhão · Valor negativo gigante · Valor com expoente enorme · Muitas casas logo abaixo do teto
  - **Commit:** c576a24

- [x] **T-012** — Avisos de chave repetida na saída: avisos da T-007 chegam a `itens[].avisos` e a `avisos` do topo, sem mudar status, motivo nem valores, inclusive em item recusado.
  - **Tipo:** regra
  - **Atende:** RN-013, AMB-019
  - **Depende de:** T-011
  - **Aceite:** `tests/test_rn013_chave_repetida.py` passa os testes de ponta a ponta: o **Aceite** da RN-013 verificado na saída (despesa avaliada com 50,00 e aviso no item; `colaborador.nome` no topo com itens de `avisos` vazio; `tem_nota_fiscal` `true` e depois `"sim"` → `entrada_invalida` com aviso; `"valor"` 90,00 → `parcial` com 60,00 e aviso).
  - **Casos de borda:** Chave repetida na despesa · Chave repetida fora das despesas · Chave repetida dentro de valor descartado · Mesma chave aninhada no valor descartado e no que valeu · Chave repetida escrita com escape · Lista dentro de lista no caminho · Chave repetida mil vezes · Chave repetida em elemento que é lista
  - **Commit:** b787957

- [x] **T-013** — Valor positivo: etapa 3, `valor_invalido` para `valor_considerado` ≤ 0.
  - **Tipo:** regra
  - **Atende:** RN-004, AMB-013
  - **Depende de:** T-010
  - **Aceite:** `tests/test_rn004_valor_positivo.py` passa: -45,00 → `recusado`, `valor_invalido`, reembolsado 0, e as demais despesas do mesmo dia têm o mesmo resultado que teriam sem ela; 0 → `valor_invalido`; 0.004 → `valor_invalido`; item recusado aqui tem `em_viagem` e `limite_diario` nulos e fica fora de `valor_solicitado`.
  - **Casos de borda:** Estorno · Valor zero · Arredondamento da metade negativa · Valor minúsculo
  - **Commit:** `3c6131a`

- [x] **T-014** — Período: etapa 4, `fora_do_periodo` para data fora de `[inicio, fim]`.
  - **Tipo:** regra
  - **Atende:** RN-005, AMB-009
  - **Depende de:** T-013
  - **Aceite:** `tests/test_rn005_periodo.py` passa: período 2026-07-01 a 2026-07-31 — 2026-04-15 → `fora_do_periodo`; 2026-07-01 e 2026-07-31 → seguem; 2026-06-30 e 2026-08-01 → `fora_do_periodo`; despesa com valor ≤ 0 fora do período → `valor_invalido` (etapa 3 vem antes).
  - **Casos de borda:** Primeiro e último dia do período · Um dia fora do período · Despesa antiga lançada no período
  - **Commit:** `0f4805d`

- [x] **T-015** — Categoria: etapa 5, `categoria_fora_da_politica` para categoria normalizada fora das três reconhecidas; categoria reconhecida sai normalizada.
  - **Tipo:** regra
  - **Atende:** RN-006, AMB-011, AMB-012
  - **Depende de:** T-014
  - **Aceite:** `tests/test_rn006_categorias.py` passa: `ALIMENTACAO`, `" Alimentacao "`, `"alimentacao\t"`, `alimentação` → `alimentacao` na saída e limite de alimentação; `"Transporte Urbano"`, `"transporte-urbano"` → `transporte_urbano`; `coworking` → `categoria_fora_da_politica`, `categoria` `coworking` na saída, item presente (não omitido); despesa fora do período com categoria desconhecida → `fora_do_periodo` (etapa 4 vem antes).
  - **Casos de borda:** Categoria em maiúsculas · Categoria com acento · Categoria com separador diferente · Categoria com tabulação no fim
  - **Commit:** `154c679`

- [x] **T-016** — Nota fiscal: etapa 6, `nota_fiscal_ausente` para `valor_considerado` > 100,00 sem nota, comparando o valor individual antes do limite.
  - **Tipo:** regra
  - **Atende:** RN-008, AMB-007, AMB-008
  - **Depende de:** T-015
  - **Aceite:** `tests/test_rn008_nota_fiscal.py` passa: 100,00 sem nota → segue (transporte: `parcial` com 80,00); 100,01 sem nota → `nota_fiscal_ausente`; 100,01 com nota → segue; 100.004 sem nota (considerado 100,00) → segue; 100.005 sem nota (considerado 100,01) → `nota_fiscal_ausente`; despesa recusada aqui não consome limite (alimentação de 150,00 sem nota seguida de 50,00 no mesmo dia → a segunda `aprovado` com 50,00); categoria desconhecida acima de 100,00 sem nota → `categoria_fora_da_politica` (etapa 5 vem antes).
  - **Casos de borda:** Valor exatamente no limite de nota · Um centavo acima do limite de nota
  - **Commit:** `09573f7`

- [ ] **T-017** — Duplicatas: etapa 7, agrupa as despesas que passaram pelas etapas 1 a 6 por (data, categoria normalizada, fornecedor normalizado, `valor_considerado`); a original é a primeira com nota, ou a primeira na ordem; as demais → `duplicata`.
  - **Tipo:** regra
  - **Atende:** RN-007, AMB-010, AMB-016
  - **Depende de:** T-016
  - **Aceite:** `tests/test_rn007_duplicatas.py` passa: d-006/d-007 (54,90, ambas com nota) → primeira avaliada, segunda `duplicata`; `id`, `descricao` e `tem_nota_fiscal` diferentes não impedem a duplicata; sem nota antes e com nota depois (valor ≤ 100) → a com nota é a original, a sem nota `duplicata`, nas duas ordens; táxi 110,00 sem nota + o mesmo com nota → `nota_fiscal_ausente` e o outro avaliado, nas duas ordens; nenhuma com nota → a primeira é a original; duplicata não consome limite (alimentação 54,90 + duplicata 54,90 → a original `aprovado` com 54,90); três cópias → uma original e duas `duplicata`; "Bistro Central" e "Bistrô Central" → mesmo fornecedor.
  - **Casos de borda:** Duplicata exata · Fornecedor com acento · Fornecedor com espaços internos · Quase duplicata · Cópias idênticas sem nota acima de 100 · Relançamento com nota
  - **Commit:**

- [ ] **T-018** — Viagem: etapa 8, antes do limite, `dias_em_viagem` = {D, D+1} de cada hospedagem com nota que passou pelas etapas 1 a 7; nessas datas, limites de alimentação e transporte em viagem; `em_viagem` verdadeiro no item.
  - **Tipo:** regra
  - **Atende:** RN-010, RN-012 (parte de viagem), AMB-004, AMB-005, AMB-006
  - **Depende de:** T-017
  - **Aceite:** `tests/test_rn010_viagem.py` passa: hospedagem com nota em 14/07 → 14/07 e 15/07 em viagem; alimentação 80,00 em 15/07 → limite 90,00, `aprovado`; alimentação 80,00 em 16/07 → limite 60,00, `parcial` com 60,00; transporte em viagem → limite 120,00; hospedagem em viagem continua com limite 250,00; hospedagem 80,00 sem nota → reembolsada, mas data não fica em viagem; hospedagem com nota recusada nas etapas 1 a 7 (fora do período, duplicata) não comprova viagem; hospedagem com nota que recebe 0 no limite (terceira do dia) comprova viagem; alimentação antes da hospedagem na entrada → em viagem; hospedagem em 31/07 põe 01/08 em viagem sem efeito (fora do período). `test_rn012_hospedagem_uma_diaria.py`: 480,00 com nota em 14/07 → 14/07 e 15/07 em viagem, não 16/07.
  - **Casos de borda:** Limite de nota em viagem · Duplicata de hospedagem só uma com nota · Hospedagem com várias diárias na descrição · Dia seguinte à diária · Dois dias depois da diária · Hospedagem sem nota até 100 · Hospedagem sem nota acima de 100 · Hospedagem fora do período · Alimentação antes da hospedagem na entrada, mesma data
  - **Commit:**

## Fase 4 — Saída e CLI

- [ ] **T-019** — CLI: `reembolso calcular --input X --output Y` com `argparse`, leitura de bytes, pipeline em memória, gravação atômica (temporário no mesmo diretório + `os.replace`), códigos 0 / 1 / 2 e mensagem `erro: ...` em stderr, sem stack trace em erro previsto (DT-006, DT-007).
  - **Tipo:** estrutura (CLI)
  - **Atende:** seção 4 da spec (Interface), RN-002 (erro de arquivo, saída não gravável), DT-006, DT-007
  - **Depende de:** T-018
  - **Aceite:** `tests/test_cli.py` passa: sucesso → código 0 e arquivo de saída igual a `processar()` da mesma entrada; arquivo de entrada ausente → código 1, sem saída; erro de arquivo com saída preexistente → arquivo intacto byte a byte; pasta de saída inexistente → código 1; sem `--input`, sem `--output` ou subcomando diferente de `calcular` → código 2, sem saída; nenhum temporário sobra no diretório em erro; stderr sem `Traceback`.
  - **Casos de borda:** Saída não gravável · Colaborador ausente · Colaborador com texto vazio · Saída preexistente com erro · Escape sem caractere válido · Erro de uso
  - **Commit:**

- [ ] **T-020** — Aceite com o arquivo de exemplo: `exemplos/despesas-exemplo.json` pela CLI contra a tabela da seção 9 da spec, **transcrita à mão** no teste.
  - **Tipo:** regra
  - **Atende:** seção 9 da spec (critérios de aceite), RN-001 a RN-012
  - **Depende de:** T-019
  - **Aceite:** `tests/test_exemplo.py` passa: as 14 linhas da tabela da seção 9 (considerado, em viagem, limite, reembolsado, status, motivo), totais 1.861,84 / 585,43 / 1.276,41, `avisos` vazios no topo e em todos os itens; `test_determinismo_byte_a_byte` (duas execuções → arquivos idênticos); `test_nenhum_valor_monetario_e_float` (propriedade da DT-001 sobre a saída lida com `Decimal`).
  - **Commit:**

- [ ] **T-021** — Rastreabilidade automática: `tests/test_rastreabilidade.py` lê a `spec.md`, extrai todos os `RN-NNN` e todos os valores da coluna "Caso" da seção 7, e falha se algum não tiver teste (RN no nome ou docstring; caso como `id` em `test_casos_de_borda.py`). Preenche a tabela de Cobertura abaixo.
  - **Tipo:** estrutura
  - **Atende:** seção 9 da spec (cada caso de borda e cada RN com teste), plan seção 6
  - **Depende de:** T-020
  - **Aceite:** `tests/test_rastreabilidade.py` passa com a suíte completa; remover qualquer teste de RN ou caso de borda o faz falhar (verificado à mão uma vez e registrado no resumo da task); tabela de Cobertura sem célula vazia.
  - **Commit:**

---

## Fase 5 — Envelope (criar no Dia 2)

<Novas tasks a partir da mudança de requisito. Numeração continua de onde parou —
não reinicie e não renumere as antigas: a numeração é o eixo da rastreabilidade.>

---

## Cobertura

Preenchida ao fechar cada fase (a T-021 confere que não falta nada).

| Regra da spec | Task | Teste |
|---|---|---|
| RN-001 | T-010, T-011 | `test_rn001_um_resultado_por_despesa.py` |
| RN-002 | T-006, T-008, T-009, T-011, T-019 | `test_leitura_json.py`, `test_rn002_validacao_da_entrada.py`, `test_cli.py` |
| RN-003 | T-010 | `test_rn003_arredondamento.py` |
| RN-004 | T-013 | `test_rn004_valor_positivo.py` |
| RN-005 | T-014 | `test_rn005_periodo.py` |
| RN-006 | T-002, T-015 | `test_politica.py`, `test_rn006_categorias.py` |
| RN-007 | T-017 | `test_rn007_duplicatas.py` |
| RN-008 | T-002, T-016 | `test_politica.py`, `test_rn008_nota_fiscal.py` |
| RN-009 | T-002, T-010 | `test_politica.py`, `test_rn009_limite_diario.py` |
| RN-010 | T-002, T-018 | `test_politica.py`, `test_rn010_viagem.py` |
| RN-011 | T-004, T-010 | `test_justificativa.py`, `test_rn011_status.py` |
| RN-012 | T-010, T-018 | `test_rn012_hospedagem_uma_diaria.py` |
| RN-013 | T-007, T-012 | `test_rn013_chave_repetida.py` |
| Seção 5 (normalização) | T-003 | `test_normalizacao.py` |
| Seção 7 (63 casos) | T-010 a T-019 | `test_casos_de_borda.py` |
| Seção 9 (exemplo) | T-020 | `test_exemplo.py` |
| AMB-001, AMB-002, AMB-003 | T-010 | `test_rn009_limite_diario.py` |
| AMB-004 | T-018 | `test_rn010_viagem.py` |
| AMB-005 | T-010, T-018 | `test_rn012_hospedagem_uma_diaria.py` |
| AMB-006 | T-002, T-010, T-018 | `test_politica.py`, `test_rn010_viagem.py` |
| AMB-007, AMB-008 | T-016 | `test_rn008_nota_fiscal.py` |
| AMB-009 | T-014 | `test_rn005_periodo.py` |
| AMB-010 | T-017 | `test_rn007_duplicatas.py` |
| AMB-011 | T-003, T-015 | `test_normalizacao.py`, `test_rn006_categorias.py` |
| AMB-012 | T-015 | `test_rn006_categorias.py` |
| AMB-013 | T-013 | `test_rn004_valor_positivo.py` |
| AMB-014 | T-010 | `test_rn003_arredondamento.py` |
| AMB-015 | T-010 | `test_casos_de_borda.py` (Despesa em sábado) |
| AMB-016 | T-013 a T-018 | testes de ordem entre etapas em cada `test_rnNNN_*.py` |
| AMB-017 | T-010 | `test_rn009_limite_diario.py` |
| AMB-018 | T-002, T-009, T-011 | `test_rn002_validacao_da_entrada.py` |
| AMB-019 | T-007, T-012 | `test_rn013_chave_repetida.py` |
