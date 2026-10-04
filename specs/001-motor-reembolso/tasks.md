# Tasks — Motor de Cálculo de Reembolso

**Versão:** 2.0 · **Baseado em:** spec 2.0, plan 2.0

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
- **Casos de borda:** linhas da tabela da seção 7 da spec que a task cobre, cada uma um caso de `tests/test_casos_de_borda.py` com `id` igual ao texto da coluna "Caso". As 100 linhas (63 da 1.x e 37 da 2.0) estão distribuídas entre as tasks; nenhuma fica sem dono.

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

- [x] **T-017** — Duplicatas: etapa 7, agrupa as despesas que passaram pelas etapas 1 a 6 por (data, categoria normalizada, fornecedor normalizado, `valor_considerado`); a original é a primeira com nota, ou a primeira na ordem; as demais → `duplicata`.
  - **Tipo:** regra
  - **Atende:** RN-007, AMB-010, AMB-016
  - **Depende de:** T-016
  - **Aceite:** `tests/test_rn007_duplicatas.py` passa: d-006/d-007 (54,90, ambas com nota) → primeira avaliada, segunda `duplicata`; `id`, `descricao` e `tem_nota_fiscal` diferentes não impedem a duplicata; sem nota antes e com nota depois (valor ≤ 100) → a com nota é a original, a sem nota `duplicata`, nas duas ordens; táxi 110,00 sem nota + o mesmo com nota → `nota_fiscal_ausente` e o outro avaliado, nas duas ordens; nenhuma com nota → a primeira é a original; duplicata não consome limite (alimentação 54,90 + duplicata 54,90 → a original `aprovado` com 54,90); três cópias → uma original e duas `duplicata`; "Bistro Central" e "Bistrô Central" → mesmo fornecedor.
  - **Casos de borda:** Duplicata exata · Fornecedor com acento · Fornecedor com espaços internos · Quase duplicata · Cópias idênticas sem nota acima de 100 · Relançamento com nota
  - **Commit:** `555a85e`

- [x] **T-018** — Viagem: etapa 8, antes do limite, `dias_em_viagem` = {D, D+1} de cada hospedagem com nota que passou pelas etapas 1 a 7; nessas datas, limites de alimentação e transporte em viagem; `em_viagem` verdadeiro no item.
  - **Tipo:** regra
  - **Atende:** RN-010, RN-012 (parte de viagem), AMB-004, AMB-005, AMB-006
  - **Depende de:** T-017
  - **Aceite:** `tests/test_rn010_viagem.py` passa: hospedagem com nota em 14/07 → 14/07 e 15/07 em viagem; alimentação 80,00 em 15/07 → limite 90,00, `aprovado`; alimentação 80,00 em 16/07 → limite 60,00, `parcial` com 60,00; transporte em viagem → limite 120,00; hospedagem em viagem continua com limite 250,00; hospedagem 80,00 sem nota → reembolsada, mas data não fica em viagem; hospedagem com nota recusada nas etapas 1 a 7 (fora do período, duplicata) não comprova viagem; hospedagem com nota que recebe 0 no limite (terceira do dia) comprova viagem; alimentação antes da hospedagem na entrada → em viagem; hospedagem em 31/07 põe 01/08 em viagem sem efeito (fora do período). `test_rn012_hospedagem_uma_diaria.py`: 480,00 com nota em 14/07 → 14/07 e 15/07 em viagem, não 16/07.
  - **Casos de borda:** Limite de nota em viagem · Duplicata de hospedagem só uma com nota · Hospedagem com várias diárias na descrição · Dia seguinte à diária · Dois dias depois da diária · Hospedagem sem nota até 100 · Hospedagem sem nota acima de 100 · Hospedagem fora do período · Alimentação antes da hospedagem na entrada, mesma data
  - **Commit:** b1cb651

## Fase 4 — Saída e CLI

- [x] **T-019** — CLI: `reembolso calcular --input X --output Y` com `argparse`, leitura de bytes, pipeline em memória, gravação atômica (temporário no mesmo diretório + `os.replace`), códigos 0 / 1 / 2 e mensagem `erro: ...` em stderr, sem stack trace em erro previsto (DT-006, DT-007).
  - **Tipo:** estrutura (CLI)
  - **Atende:** seção 4 da spec (Interface), RN-002 (erro de arquivo, saída não gravável), DT-006, DT-007
  - **Depende de:** T-018
  - **Aceite:** `tests/test_cli.py` passa: sucesso → código 0 e arquivo de saída igual a `processar()` da mesma entrada; arquivo de entrada ausente → código 1, sem saída; erro de arquivo com saída preexistente → arquivo intacto byte a byte; pasta de saída inexistente → código 1; sem `--input`, sem `--output` ou subcomando diferente de `calcular` → código 2, sem saída; nenhum temporário sobra no diretório em erro; stderr sem `Traceback`.
  - **Casos de borda:** Saída não gravável · Colaborador ausente · Colaborador com texto vazio · Saída preexistente com erro · Escape sem caractere válido · Erro de uso
  - **Commit:** 00cf730

- [x] **T-020** — Aceite com o arquivo de exemplo: `exemplos/despesas-exemplo.json` pela CLI contra a tabela da seção 9 da spec, **transcrita à mão** no teste.
  - **Tipo:** regra
  - **Atende:** seção 9 da spec (critérios de aceite), RN-001 a RN-012
  - **Depende de:** T-019
  - **Aceite:** `tests/test_exemplo.py` passa: as 14 linhas da tabela da seção 9 (considerado, em viagem, limite, reembolsado, status, motivo), totais 1.861,84 / 585,43 / 1.276,41, `avisos` vazios no topo e em todos os itens; `test_determinismo_byte_a_byte` (duas execuções → arquivos idênticos); `test_nenhum_valor_monetario_e_float` (propriedade da DT-001 sobre a saída lida com `Decimal`).
  - **Commit:** `45f014f`

- [x] **T-021** — Rastreabilidade automática: `tests/test_rastreabilidade.py` lê a `spec.md`, extrai todos os `RN-NNN` e todos os valores da coluna "Caso" da seção 7, e falha se algum não tiver teste (RN no nome ou docstring; caso como `id` em `test_casos_de_borda.py`). Preenche a tabela de Cobertura abaixo.
  - **Tipo:** estrutura
  - **Atende:** seção 9 da spec (cada caso de borda e cada RN com teste), plan seção 6
  - **Depende de:** T-020
  - **Aceite:** `tests/test_rastreabilidade.py` passa com a suíte completa; remover qualquer teste de RN ou caso de borda o faz falhar (verificado à mão uma vez e registrado no resumo da task); tabela de Cobertura sem célula vazia.
  - **Commit:** 672cc34

---

## Fase 5 — Envelope: Política v4 (spec 2.0, D-007)

Tasks da mudança de requisito do Dia 2 (D-007, plan 2.0). As tasks da 1.x **não são desmarcadas**: as que o D-007 lista como afetadas são substituídas pelas tasks abaixo, e cada uma diz o que substitui. A ordem mantém a suíte verde em todo commit:
1. **Fundação:** pendências da rastreabilidade (DT-016), `leitura.py` e `dinheiro.py`.
2. **Peças puras:** leitores de política e câmbio, seleção da tabela e limite.
3. **Ligação:** a CLI recebe os dois arquivos, e depois o motor passa a usá-los.
4. **Moeda:** validação, depois conversão, depois duplicata.
5. **Fechamento:** aceite com os três arquivos e fim das pendências.

Cada task que escreve o teste de uma regra ou de um caso pendente tira a pendência de `PENDENTES` no mesmo commit (DT-016). O dono de cada pendência é a task que lista o caso em **Casos de borda**, ou a regra em **Remove pendência**.

- [x] **T-022** — Pendências da rastreabilidade: `PENDENTES` em `tests/test_rastreabilidade.py`, com RN-014, RN-015, RN-016 e os 37 casos novos da seção 7, cada um com a task dona (DT-016); arquivos de `exemplos/envelope/` versionados.
  - **Tipo:** estrutura
  - **Atende:** DT-016, seção 9 da spec (rastreabilidade)
  - **Depende de:** T-021
  - **Aceite:** `uv run pytest -q` verde. `tests/test_rastreabilidade.py` passa e ganha:
    - `test_pendencia_com_teste_falha`: uma pendência que já tem teste faz a verificação falhar;
    - `test_pendencia_fora_da_spec_falha`: uma pendência que não está na spec faz a verificação falhar;
    - `test_dono_da_pendencia_e_task_da_fase_5`: todo dono é uma task `T-022` a `T-034` existente em `tasks.md`.
    As três verificações são testadas sobre conjuntos montados no teste, sem editar a spec. Os 37 casos e os donos são os desta fase.
  - **Commit:** 91a0f33

- [x] **T-023** — `leitura.py`: mover de `entrada.py` a forma do arquivo (`ler_json`, `ObjetoJson`, `ErroDeArquivo`, verificação de escapes) e os testes de tipo da DT-003 (`e_numero`, `e_data`, `tem_texto`), sem mudar comportamento; acrescentar `e_codigo_de_moeda`, `tem_ate_2_casas` e `rejeitar_chaves_repetidas` (DT-010, DT-011).
  - **Tipo:** estrutura (leitura de JSON; commit `refactor(T-023)`)
  - **Atende:** DT-002, DT-003, DT-010, DT-011; prepara RN-016 (mesma forma para os três arquivos)
  - **Depende de:** T-022
  - **Aceite:**
    - `tests/test_leitura_json.py` passa importando de `reembolso.leitura`, sem nenhum outro teste alterado além dos imports.
    - `tests/test_leitura.py` (novo) passa:
      - `e_codigo_de_moeda`: `EUR` → sim; `eur`, `" EUR"`, `"EUR\n"`, `"EURO"`, `"R$"`, `""`, `978`, `"ÉUR"` → não;
      - `tem_ate_2_casas`: `60.000`, `6E1` e `0` → sim; `60.005` e `1E-999999` → não;
      - `rejeitar_chaves_repetidas`: chave repetida no topo, em objeto aninhado e dentro de lista → `ErroDeArquivo` com o caminho na mensagem; documento sem repetição → sem erro.
    - `entrada.py` não define mais nenhuma dessas funções.
  - **Commit:** b9f728e

- [x] **T-024** — `dinheiro.py`: `contexto_exato()`, `arredondar` (movido de `motor.py`) e `truncar` (DT-012, DT-013).
  - **Tipo:** regra
  - **Atende:** RN-003 (produto exato arredondado uma vez), RN-009 (limite em viagem truncado), AMB-022, AMB-026, DT-012, DT-013
  - **Depende de:** T-023
  - **Aceite:** `tests/test_dinheiro.py` passa:
    - `test_rn003_produto_exato_arredondado_uma_vez`: `16.8649 × 5.93` → 100,01 (não 99,98); `0.001 × 5.93` → 0,01;
    - `test_produto_com_mais_de_28_digitos_e_exato`: `999999999.99999999999 × 5.123456789123456789`, conferido contra a conta à mão;
    - `test_soma_com_mais_de_28_casas_e_exata`: `100 + 0.000…01` (41 casas);
    - `test_produto_com_expoente_minimo`: `1E-999999 × 5.93` → `5.93E-999999`, sem subnormal;
    - `test_rn009_truncar`: `49.995` → 49,99; `90.00` → 90,00;
    - `test_conta_inexata_levanta_erro`: uma divisão inexata dentro de `contexto_exato()` levanta exceção.
    `motor.py` importa `arredondar` de `dinheiro.py`, e a suíte da 1.x passa sem mudança.
  - **Commit:** beba6b8

- [x] **T-025** — Leitor do arquivo de política: `ler_politica(bytes) -> Politica`, com a parte da RN-016 sobre a política (DT-015); `Politica` em `modelo.py`; construtor `construir_politica(**sobrescritas)` em `tests/conftest.py`, com a v4 transcrita (plan seção 6).
  - **Tipo:** regra
  - **Atende:** RN-016 (política), AMB-029 (`versao` e `vigencia` opcionais), AMB-031, DT-015
  - **Substitui:** T-002 (política como dados, não constantes; as constantes da 1.x continuam até a T-029)
  - **Depende de:** T-023
  - **Remove pendência:** RN-016
  - **Aceite:** `tests/test_rn016_arquivos_de_politica_e_cambio.py` passa os testes da política, cada um com `ErroDeArquivo` e o campo na mensagem:
    - **Forma:** UTF-8 inválido, JSON inválido, escape sem par, chave repetida em qualquer objeto (`alimentacao` duas vezes na mesma tabela; `versao` duas vezes na raiz).
    - **Raiz:** raiz que não é objeto; `versao` só com espaços ou não texto; `vigencia` `"2026-7-1"` ou `2026`; `moeda_base` `"brl"` ou `1`.
    - **Tabelas:** `padrao` ausente ou lista; `centros_custo` lista ou com valor que não é tabela; chave de `centros_custo` `"padrao"`, `""` ou `"  "`.
    - **Números:** `nota_fiscal_obrigatoria_acima_de` ausente, `"100"`, `-1` ou `100.001`; `acrescimo_em_viagem_percentual` ausente, texto ou `-1`.
    - **Regras de categoria:** nome que normaliza vazio (`"-"`); `"Alimentação"` e `"alimentacao"` na mesma tabela; regra que não é objeto; `limite` ausente, `"60"`, `-10`, `60.005`; `periodicidade` ausente ou `"mes"`.
    - **Teto:** `limite`, mínimo ou percentual `1000000000` ou `1e999999`.
    - **Válidos:** `politica-v4` transcrita → `Politica` com as quatro tabelas indexadas pela categoria normalizada e os centros de custo pela chave como escrita; sem `versao`, `vigencia`, `moeda_base` e `centros_custo` (ou com `null`) → válida, `versao` e `vigencia` `None`; `60.000` → 60,00; `periodicidade` `"diaria"` em qualquer categoria; tabela vazia; `observacao` numa regra e campo desconhecido na raiz ignorados; limite `-0` → 0.
  - **Commit:** 4c93a08

- [x] **T-026** — Leitor do câmbio e busca da cotação: `ler_cambio(bytes) -> Cambio` (RN-016, parte do câmbio) e `cotacao(cambio, moeda, data) -> Cotacao | None` (RN-015, DT-014); `Cambio` e `Cotacao` em `modelo.py`; construtor `construir_cambio(taxas=...)` em `tests/conftest.py`, com o `cambio.json` do envelope transcrito.
  - **Tipo:** regra
  - **Atende:** RN-015 (taxa da data, D-1 a D-3, só a mesma moeda, nunca posterior, `BRL` taxa 1), RN-016 (câmbio), AMB-024, AMB-025 (`BRL` fora do arquivo; código sem cotação), DT-014, DT-015
  - **Depende de:** T-023
  - **Remove pendência:** RN-015
  - **Aceite:**
    - `tests/test_rn015_moeda_e_cambio.py` passa os testes da busca, com o câmbio do envelope salvo indicação:
      - EUR em 14/07 → 5,93 de 14/07; EUR em 18/07 (sábado) → 5,96 de 17/07;
      - câmbio só com 13/07: USD em 16/07 → 13/07 (D-3) e USD em 17/07 → `None` (D-4);
      - USD em 12/07 → `None` (nunca a cotação posterior de 13/07); GBP e `XYZ` → `None`;
      - câmbio com 13/07 (USD, EUR) e 14/07 (só USD): EUR em 15/07 → 5,91 de 13/07;
      - `BRL` → taxa 1, data `None`, mesmo com câmbio vazio ou com `"BRL": 7` no arquivo;
      - data em 0001-01-02 → busca sem erro.
    - `tests/test_rn016_arquivos_de_politica_e_cambio.py` passa os testes do câmbio, cada um com `ErroDeArquivo`: raiz que não é objeto; `moeda_base` diferente de `"BRL"`; `taxas` ausente ou lista; data `"2026-07-32"` ou `"2026-7-13"`; valor de data que não é objeto; código `"usd"` ou `"US"`; taxa `0`, `-5.4`, `"5.4"` ou `1e999999`; chave repetida (mesma data duas vezes; mesma moeda duas vezes na data).
    - Câmbio com `"BRL": 0` ou `"BRL": "x"` numa data e com `fonte` e `observacao` na raiz → válido.
  - **Commit:** b3fd107

- [x] **T-027** — Tabela aplicada e limite: `tabela_aplicada(politica, centro_custo)` (RN-014), `limite_diario(tabela, categoria, em_viagem, percentual)` com truncamento (RN-009, DT-013) e `categoria_de_saida(texto, tabela)` (seção 4 da spec), em `politica.py`, com as constantes de interpretação da seção 4 do plano.
  - **Tipo:** regra
  - **Atende:** RN-014, RN-009 (limite normal e em viagem do arquivo), RN-006 (categorias da tabela aplicada), AMB-006, AMB-020, AMB-022, seção 4 da spec (`itens[].categoria`)
  - **Depende de:** T-024, T-025
  - **Remove pendência:** RN-014
  - **Aceite:**
    - `tests/test_rn014_tabela_aplicada.py` passa, com a v4 transcrita:
      - `"CC-COMERCIAL"` → tabela `CC-COMERCIAL`;
      - `"CC-SUPORTE-N2"`, `"cc-adm"`, `"CC-ADM "`, `None`, `""` e `"  "` → `padrao`;
      - política sem `centros_custo` → `padrao` para qualquer centro de custo;
      - `CC-ADM` não tem `hospedagem`, mesmo existindo no `padrao`, porque a tabela é fechada (AMB-020).
    - `tests/test_rn009_limite_diario.py` ganha os testes de `limite_diario`:
      - `padrao` em viagem dá 90,00, 120,00 e 250,00 (hospedagem não amplia);
      - `CC-COMERCIAL` em viagem dá alimentação 135,00 e representação 300,00 (não amplia, AMB-022);
      - alimentação 33,33 com 50% → 49,99;
      - percentual 0 → limite normal;
      - percentual com mais de 28 casas → conferido à mão.
    - `categoria_de_saida`: `"ALIMENTACAO"` → `alimentacao`; `"hospedagem"` com `CC-ENG-PLATAFORMA` (limite 0) → `hospedagem`; `"representacao"` com `padrao` → `representacao` como veio; `"Coworking"` → `Coworking`; não texto → `None`.
  - **Commit:** 4bbfdaf

- [x] **T-028** — CLI com política e câmbio: `--politica` e `--cambio` obrigatórios; leitura dos três arquivos, validação na ordem política → câmbio → entrada; mensagem `erro: <arquivo>: ...` (DT-007); `calcular(entrada, politica, cambio)` recebe os dois, mas o motor só os usa a partir da T-029; `processar()` do `conftest.py` passa a v4 e o câmbio transcritos quando o teste não informa outros.
  - **Tipo:** estrutura (CLI)
  - **Atende:** seção 4 da spec (Interface), RN-016 (erro de arquivo na política e no câmbio), AMB-031, DT-006, DT-007
  - **Substitui:** T-019 (CLI com quatro argumentos)
  - **Depende de:** T-025, T-026
  - **Aceite:** `tests/test_cli.py` passa, com todas as chamadas de `main` (inclusive em `test_exemplo.py` e `test_casos_de_borda.py`) atualizadas para os quatro argumentos:
    - **Sucesso:** código 0.
    - **Erro de uso:** sem `--politica` ou sem `--cambio` → código 2, sem saída.
    - **Arquivos:** política ausente, câmbio ausente (com todas as despesas em BRL) ou política inválida → código 1, sem saída. Com saída preexistente, o arquivo continua intacto byte a byte em erro de qualquer um dos três arquivos.
    - **Mensagem:** stderr começa com `erro: política:`, `erro: câmbio:` ou `erro: entrada:`, sem `Traceback`.
    - **Ordem:** política inválida e entrada inválida juntas → a mensagem é da política.
    - **Exemplo:** `test_exemplo.py` continua com a tabela da 1.9 (o motor ainda não lê a política), agora chamado com `exemplos/envelope/politica-v4.json` e `cambio.json`.
  - **Casos de borda:** Centro de custo reservado no arquivo · Política sem tabela padrão · Limite inválido na política · Periodicidade desconhecida · Taxa de câmbio não positiva · Chave repetida na política · Câmbio ausente com despesas em reais · Sem argumento de política
  - **Commit:** 0c4311b

- [x] **T-029** — Motor com a tabela aplicada: `centro_custo` validado na entrada (RN-002) e copiado na saída; tabela escolhida uma vez (RN-014); categorias, mínimo da nota, percentual e limites vindos da `Politica` (etapas 5, 6 e 9); categoria com limite 0 recusada na etapa 5 (AMB-021); categoria de saída decidida no motor para todo item, e `DespesaInvalida` passa a guardar `categoria_texto`; `politica` (`versao`, `vigencia`, `tabela_aplicada`) e `colaborador.centro_custo` na saída; mínimo da nota passado à justificativa (DT-009). Remove de `politica.py` os limites, o mínimo e as categorias fixas da 1.x; `tests/test_politica.py` sai, e os testes de `Motivo` e `Status` vão para `tests/test_modelo.py`.
  - **Tipo:** regra
  - **Atende:** RN-002 (`centro_custo`), RN-006, RN-008 (mínimo do arquivo), RN-009, RN-010 (limite 0 não comprova viagem), RN-014, AMB-017, AMB-020, AMB-021, AMB-022, AMB-027 (origem do mínimo), AMB-029, seção 4 da spec (`colaborador`, `politica`, `itens[].categoria`)
  - **Substitui:** T-009 (categoria dependente da tabela), T-010, T-015, T-016 (mínimo do arquivo), T-018 (percentual, truncamento e limite 0), T-020 (primeira tabela da seção 9)
  - **Depende de:** T-027, T-028
  - **Aceite:**
    - `tests/test_rn014_tabela_aplicada.py` ganha os testes de ponta a ponta do **Aceite** da RN-014: `CC-COMERCIAL` com alimentação 85,00 → limite 90,00, `aprovado`; `CC-SUPORTE-N2` com 65,00 → `parcial` com 60,00; sem `centro_custo` → `padrao`; `"cc-adm"` com 50,00 → `aprovado`; `CC-ADM` com hospedagem de 300,00 com nota → `categoria_fora_da_politica`.
    - `tests/test_rn006_categorias.py` ganha os testes do **Aceite** da RN-006 por tabela (`representacao` no `padrao` e no `CC-COMERCIAL`; `hospedagem` no `CC-ADM` e no `CC-ENG-PLATAFORMA`). Também ganha a categoria de saída de despesa inválida com `CC-COMERCIAL` e `"Representacao"` sem `tem_nota_fiscal` → `representacao`.
    - `tests/test_rn010_viagem.py` ganha: `CC-ENG-PLATAFORMA`, hospedagem com nota em 14/07 → `categoria_fora_da_politica`, e alimentação de 100,00 com nota em 15/07 → limite 75,00, `parcial` com 75,00.
    - `tests/test_rn012_hospedagem_uma_diaria.py` ganha: `CC-COMERCIAL`, hospedagem de 1.200,00 com nota → `parcial` com 400,00.
    - `tests/test_rn008_nota_fiscal.py` ganha: política com mínimo 50,00 → 50,01 sem nota é `nota_fiscal_ausente`.
    - `tests/test_rn002_validacao_da_entrada.py` ganha os testes de `centro_custo`: `17`, `true`, lista e objeto → `ErroDeArquivo`; ausente, `null`, `""` e `"  "` → válidos. Na saída, `centro_custo` é copiado se texto (inclusive `"  "`) e sai nulo se ausente ou nulo.
    - `tests/test_saida.py` passa com a ordem nova do topo e de `colaborador` e `politica`.
    - `tests/test_exemplo.py` passa com a **primeira tabela da seção 9 da spec 2.0**, transcrita à mão: `CC-ENG-PLATAFORMA`, 14 linhas, totais 1.861,84 / 351,43 / 1.510,41, `politica` = `v4` / `2026-07-01` / `CC-ENG-PLATAFORMA`.
    - A suíte da 1.x continua passando com a tabela `padrao` da v4.
  - **Casos de borda:** Centro de custo da tabela · Centro de custo fora da tabela · Centro de custo com grafia diferente · Centro de custo só com espaços · Centro de custo de tipo errado · Categoria ausente da tabela do centro de custo · Categoria com limite zero · Representação fora do centro de custo que a define · Representação não amplia em viagem · Limite em viagem truncado · Política sem versão nem vigência
  - **Commit:** 7e38a46

- [ ] **T-030** — Moeda na entrada: `moeda` validada na etapa 1 (`Despesa.moeda`, `BRL` se ausente ou nula; `entrada_invalida` fora do formato) e `itens[].moeda` na saída (`BRL`, como veio se texto, ou nula).
  - **Tipo:** regra
  - **Atende:** RN-002 (`moeda`), AMB-025, seção 4 da spec (`itens[].moeda`)
  - **Substitui:** T-009 (validação de `moeda`)
  - **Depende de:** T-029
  - **Aceite:** `tests/test_rn002_validacao_da_entrada.py` ganha os testes de `moeda`:
    - `"eur"`, `" EUR"`, `"EUR "`, `"R$"`, `""`, `"EURO"` → `entrada_invalida`, `moeda` como veio;
    - `978`, `true`, lista → `entrada_invalida`, `moeda` nula;
    - ausente e `null` → válida, `moeda` `BRL`;
    - `"USD"` → válida, `moeda` `USD`;
    - elemento que não é objeto → `moeda` nula;
    - despesa inválida por outro campo com `"moeda": "EUR"` → `moeda` `EUR`.
    `tests/test_saida.py` passa com `moeda` na posição da seção 4.
  - **Casos de borda:** Moeda em minúsculas · Moeda de tipo errado
  - **Commit:** —

- [ ] **T-031** — Conversão: etapa 2 da seção 8, com `cotacao` (T-026), `valor_considerado = arredondar(valor × taxa)` no contexto exato (DT-012) e `cambio_indisponivel` (novo `Motivo`, na ordem da seção 8); `taxa_cambio` e `data_cotacao` na saída; nulos e fora de `valor_solicitado` em `entrada_invalida` e `cambio_indisponivel`; justificativa para `cambio_indisponivel` e para a conversão (DT-009).
  - **Tipo:** regra
  - **Atende:** RN-003 (conversão arredondada uma vez), RN-004 (valor positivo em reais), RN-008 (mínimo comparado em reais), RN-010 (moeda não comprova viagem; hospedagem estrangeira comprova), RN-015, AMB-023, AMB-024, AMB-026, AMB-027, seção 4 da spec (`taxa_cambio`, `data_cotacao`, `valor_considerado`, `totais.valor_solicitado`), seção 8 (etapa 2)
  - **Depende de:** T-024, T-026, T-030
  - **Aceite:**
    - `tests/test_rn015_moeda_e_cambio.py` ganha os testes de ponta a ponta do **Aceite** da RN-015:
      - 22,00 EUR em 14/07 → 5,93, `2026-07-14`, 130,46;
      - 30,00 EUR em 18/07 → 5,96 de 17/07, 178,80;
      - sem `moeda` → `BRL`, taxa 1, `data_cotacao` nula;
      - 55,00 GBP em 21/07 → `cambio_indisponivel`, `valor_considerado`, `taxa_cambio`, `data_cotacao`, `em_viagem` e `limite_diario` nulos, fora de `valor_solicitado`;
      - USD em 12/07 → `cambio_indisponivel`.
    - `tests/test_rn003_arredondamento.py` ganha: 16,8649 EUR × 5,93 → 100,01; 0,001 EUR → 0,01.
    - `tests/test_rn004_valor_positivo.py` ganha: 0,001 EUR → não é `valor_invalido`; `1e-999999` EUR → `valor_invalido`.
    - `tests/test_rn008_nota_fiscal.py` ganha: 40,00 USD sem nota a 5,50 → 220,00, `nota_fiscal_ausente`.
    - `tests/test_rn010_viagem.py` ganha: alimentação de 22,00 EUR com nota em 14/07 sem hospedagem → 14/07 fora de viagem.
    - `tests/test_justificativa.py` cobre `cambio_indisponivel`.
    - Ordem das etapas: sem cotação e fora do período → `cambio_indisponivel`; sem cotação e valor negativo → `cambio_indisponivel`; despesa inválida em EUR → `entrada_invalida` com `taxa_cambio` nula.
    - O teste de propriedade da DT-001 cobre `taxa_cambio`.
  - **Casos de borda:** Moeda nula · Moeda estrangeira com cotação · Moeda estrangeira em sábado · Cotação exatamente 3 dias antes · Cotação 4 dias antes · Moeda sem cotação no arquivo · Sem cotação e fora do período · Conversão arredondada uma vez · Nota fiscal comparada em reais · Valor estrangeiro minúsculo · Teto na moeda original · Moeda estrangeira não comprova viagem · Hospedagem em moeda estrangeira · Data intermediária sem a moeda
  - **Commit:** —

- [ ] **T-032** — Duplicata com moeda: etapa 7 agrupa por (data, categoria, fornecedor, moeda, `valor` arredondado na moeda da despesa).
  - **Tipo:** regra
  - **Atende:** RN-007, AMB-028
  - **Substitui:** T-017 (duplicata com moeda)
  - **Depende de:** T-031
  - **Aceite:** `tests/test_rn007_duplicatas.py` ganha:
    - 22,00 EUR e 22,00 USD com os demais campos iguais → as duas avaliadas;
    - 22.001 EUR e 22.00 EUR → a segunda `duplicata`;
    - 10,00 EUR e 59,30 BRL do mesmo gasto → as duas avaliadas (risco aceito, seção 10);
    - ausente e `"BRL"` com os demais campos iguais → a segunda `duplicata`, porque as duas valem `BRL`.
    Os testes da 1.x da RN-007 continuam passando.
  - **Casos de borda:** Duplicata em moedas diferentes · Duplicata em moeda estrangeira
  - **Commit:** —

- [ ] **T-033** — Aceite com os arquivos do envelope: `exemplos/envelope/despesas-envelope.json` e `despesas-envelope-cc-desconhecido.json` pela CLI, com `politica-v4.json` e `cambio.json`, contra a segunda e a terceira tabelas da seção 9 da spec, **transcritas à mão** no teste.
  - **Tipo:** regra
  - **Atende:** seção 9 da spec (critérios de aceite), RN-001 a RN-016
  - **Substitui:** T-020 (três tabelas da seção 9)
  - **Depende de:** T-032
  - **Aceite:** `tests/test_exemplo.py` passa:
    - **Envelope:** as 10 linhas de `despesas-envelope.json` (moeda, taxa, data da cotação, considerado, em viagem, limite, reembolsado, status, motivo); totais 2.457,52 / 1.148,26 / 1.309,26; `tabela_aplicada` `CC-COMERCIAL`.
    - **CC desconhecido:** as 4 linhas de `despesas-envelope-cc-desconhecido.json`; totais 623,76 / 373,76 / 250,00; `tabela_aplicada` `padrao`.
    - **Determinismo e propriedade:** `avisos` vazios no topo e nos itens dos três arquivos; determinismo byte a byte e nenhum valor monetário `float` também nos dois arquivos do envelope.
  - **Commit:** —

- [ ] **T-034** — Fim das pendências: apagar `PENDENTES` e o código que o lê em `tests/test_rastreabilidade.py` (DT-016); docstrings para "RN-001 a RN-016"; tabela de Cobertura atualizada com RN-014 a RN-016, AMB-020 a AMB-031, seção 7 (100 casos) e seção 9 (três arquivos).
  - **Tipo:** estrutura
  - **Atende:** seção 9 da spec (cada caso de borda e cada RN com teste), DT-016
  - **Depende de:** T-033
  - **Aceite:** `tests/test_rastreabilidade.py` passa sem nenhuma pendência; remover qualquer teste de RN-014 a RN-016 ou de um caso novo o faz falhar (verificado à mão uma vez e registrado no resumo da task); tabela de Cobertura sem célula vazia, e nenhum `test_politica.py` citado.
  - **Commit:** —

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
