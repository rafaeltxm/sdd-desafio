# Spec — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Status:** rascunho para revisão · **Última alteração:** 2026-10-01

> **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ. Nenhuma linha
> aqui pode citar linguagem, biblioteca, classe, função ou estrutura de pasta.
> Se apareceu solução, o lugar dela é o `plan.md`.
>
> **Teste de aceitação da própria spec:** uma pessoa que nunca viu o projeto
> consegue, lendo só este arquivo, verificar se o sistema está correto?

---

## 1. Problema

Hoje o financeiro confere manualmente, item por item, as despesas de cada colaborador contra a política de reembolso do RH. O processo é lento, e como a política é ambígua, cada pessoa a interpreta de um jeito: o mesmo conjunto de despesas pode gerar valores diferentes dependendo de quem confere.

## 2. Objetivo

Dado o conjunto de despesas de um colaborador num período, calcular de forma determinística quanto é reembolsável e justificar a decisão sobre cada despesa, aplicando uma interpretação única e documentada da política.

## 3. Fora de escopo

- Não aprova, paga nem integra com sistemas de pagamento ou folha: só calcula e justifica.
- Não processa mais de um colaborador ou mais de um período por execução.
- Não verifica a autenticidade da nota fiscal; confia no indicador `tem_nota_fiscal`.
- Não lê nem interpreta o texto livre de `descricao` (nem para contar diárias, ver AMB-005).
- Não converte moedas: todos os valores são em reais.
- Não guarda histórico entre execuções: duplicatas só são detectadas dentro da mesma entrada.
- Não aceita campos adicionais na entrada para datas de entrada/saída de hospedagem. Seria a solução ideal para AMB-005, mas o formato de entrada é fixo; fica registrado como evolução recomendada.
- Não trata feriados nem fins de semana de forma especial (AMB-015).

## 4. Entrada e saída

### Interface

`<comando> calcular --input <arquivo de entrada> --output <arquivo de saída>`

- Sucesso: grava o arquivo de saída e termina com código 0.
- Erro de arquivo (RN-002): não grava o arquivo de saída, escreve uma mensagem de erro e termina com código diferente de 0.

### Entrada

Formato fixo, conforme `exemplos/despesas-exemplo.json`.

| Campo | Tipo | Significado | Obrigatório |
|---|---|---|---|
| `colaborador.id` | texto | identificador do colaborador | sim |
| `colaborador.nome` | texto | nome | sim |
| `colaborador.centro_custo` | texto | centro de custo | não |
| `periodo.competencia` | texto `AAAA-MM` | rótulo do mês de competência; repetido na saída, não usado em cálculo | não |
| `periodo.inicio` | data `AAAA-MM-DD` | primeiro dia do período (inclusive) | sim |
| `periodo.fim` | data `AAAA-MM-DD` | último dia do período (inclusive) | sim |
| `despesas` | lista | despesas a avaliar (pode ser vazia) | sim |
| `despesas[].id` | texto | identificador da despesa | sim |
| `despesas[].data` | data `AAAA-MM-DD` | data em que a despesa ocorreu | sim |
| `despesas[].categoria` | texto | categoria da despesa | sim |
| `despesas[].descricao` | texto | descrição livre; não usada em regras | não |
| `despesas[].fornecedor` | texto | estabelecimento; usado na detecção de duplicatas | sim |
| `despesas[].valor` | número | valor em reais | sim |
| `despesas[].tem_nota_fiscal` | booleano | se há nota fiscal | sim |

### Saída

| Campo | Tipo | Significado |
|---|---|---|
| `colaborador` | objeto | `id` e `nome`, copiados da entrada |
| `periodo` | objeto | `competencia`, `inicio` e `fim`, copiados da entrada |
| `itens` | lista | um item por despesa da entrada, **na mesma ordem** |
| `itens[].id` | texto | id da despesa |
| `itens[].data` | texto | data da despesa como veio na entrada |
| `itens[].categoria` | texto | categoria normalizada (RN-006) ou como veio, se não reconhecida |
| `itens[].valor_informado` | número ou nulo | valor exatamente como veio na entrada (nulo se ausente ou não numérico) |
| `itens[].valor_considerado` | número ou nulo | valor arredondado ao centavo (RN-003); nulo se ausente ou não numérico |
| `itens[].valor_reembolsado` | número | quanto será reembolsado (0 se recusado) |
| `itens[].status` | texto | `aprovado`, `parcial` ou `recusado` (RN-011) |
| `itens[].motivo` | texto ou nulo | código do motivo (tabela abaixo); nulo quando `aprovado` |
| `itens[].em_viagem` | booleano ou nulo | se a data estava em viagem (RN-010); nulo se o item foi recusado antes do limite diário |
| `itens[].limite_diario` | número ou nulo | limite diário aplicado à categoria naquela data; nulo se o item foi recusado antes do limite diário |
| `itens[].justificativa` | texto | frase em português explicando a decisão. Texto livre: não é contratual, os campos acima são |
| `totais.valor_solicitado` | número | soma de `valor_considerado` dos itens com valor válido (maior que zero) |
| `totais.valor_reembolsado` | número | soma de `valor_reembolsado` |
| `totais.valor_glosado` | número | `valor_solicitado − valor_reembolsado` |

Todos os valores monetários da saída são em reais, com no máximo 2 casas decimais e exatos ao centavo.

**Códigos de motivo:**

| Código | Quando | Status resultante |
|---|---|---|
| `entrada_invalida` | campo obrigatório ausente ou com tipo/formato errado (RN-002) | `recusado` |
| `valor_invalido` | valor considerado menor ou igual a zero (RN-004) | `recusado` |
| `fora_do_periodo` | data fora de `[inicio, fim]` (RN-005) | `recusado` |
| `categoria_fora_da_politica` | categoria não reconhecida (RN-006) | `recusado` |
| `duplicata` | repete uma despesa anterior (RN-007) | `recusado` |
| `nota_fiscal_ausente` | valor acima de 100,00 sem nota (RN-008) | `recusado` |
| `limite_diario_excedido` | o limite diário cortou parte ou todo o valor (RN-009) | `parcial`, ou `recusado` se nada restou |

**Exemplo** (entrada com duas despesas de alimentação no mesmo dia, fora de viagem):

```json
{
  "colaborador": { "id": "c-1", "nome": "Ana" },
  "periodo": { "competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31" },
  "itens": [
    { "id": "d-1", "data": "2026-07-03", "categoria": "alimentacao",
      "valor_informado": 45.0, "valor_considerado": 45.0, "valor_reembolsado": 45.0,
      "status": "aprovado", "motivo": null, "em_viagem": false, "limite_diario": 60.0,
      "justificativa": "Aprovado integralmente: 45,00 dentro do limite diário de 60,00." },
    { "id": "d-2", "data": "2026-07-03", "categoria": "alimentacao",
      "valor_informado": 30.0, "valor_considerado": 30.0, "valor_reembolsado": 15.0,
      "status": "parcial", "motivo": "limite_diario_excedido", "em_viagem": false, "limite_diario": 60.0,
      "justificativa": "Parcial: restavam 15,00 do limite diário de 60,00 de alimentação em 03/07." }
  ],
  "totais": { "valor_solicitado": 75.0, "valor_reembolsado": 60.0, "valor_glosado": 15.0 }
}
```

## 5. Regras de negócio

As regras são aplicadas a cada despesa na ordem da seção 8. A primeira regra que recusa uma despesa encerra a avaliação dela: cada despesa recusada tem exatamente um motivo.

### RN-001 — Um resultado por despesa

**Regra:** a saída tem exatamente um item para cada despesa da entrada, na mesma ordem, inclusive as recusadas. Os totais seguem as fórmulas da seção 4.
**Origem:** objetivo do sistema ("justifica cada decisão").
**Aceite:** entrada com 14 despesas gera 14 itens, na mesma ordem de ids; `valor_glosado = valor_solicitado − valor_reembolsado`.

### RN-002 — Validação da entrada

**Regra:**
- **Erro de arquivo** (nenhuma saída é gerada): arquivo ausente ou que não é JSON válido; `periodo.inicio`, `periodo.fim` ou `despesas` ausentes; `inicio` ou `fim` que não são datas válidas `AAAA-MM-DD`; `inicio` posterior a `fim`; `despesas` que não é lista.
- **Despesa inválida** (vira item `recusado` com motivo `entrada_invalida`): falta `id`, `data`, `categoria`, `fornecedor`, `valor` ou `tem_nota_fiscal`; `data` não é data válida `AAAA-MM-DD`; `valor` não é número; `tem_nota_fiscal` não é booleano; `categoria` ou `fornecedor` não são texto.
**Origem:** necessidade operacional (a política não trata entrada malformada).
**Aceite:** despesa sem `tem_nota_fiscal` → `recusado`, `entrada_invalida`, e as demais despesas são processadas normalmente. Arquivo com `inicio` = `2026-07-31` e `fim` = `2026-07-01` → nenhuma saída, código de saída diferente de 0.

### RN-003 — Arredondamento ao centavo

**Regra:** antes de qualquer outra regra de valor, `valor` é arredondado para 2 casas decimais, com a metade arredondada para cima (0,005 → 0,01). Todas as regras usam o valor arredondado (`valor_considerado`), e todos os cálculos são exatos ao centavo.
**Origem:** AMB-014.
**Aceite:** `valor` 33.333 → `valor_considerado` 33.33; `valor` 10.005 → 10.01; `valor` 10.004 → 10.00.

### RN-004 — Valor deve ser positivo

**Regra:** despesa com `valor_considerado` menor ou igual a zero é `recusado` com motivo `valor_invalido`. Ela não abate, não soma e não consome limite de nenhuma outra despesa.
**Origem:** AMB-013.
**Aceite:** `valor` -45.00 → `recusado`, `valor_invalido`, `valor_reembolsado` 0; demais despesas do mesmo dia não mudam. `valor` 0.004 (arredonda para 0,00) → `valor_invalido`.

### RN-005 — Período de competência

**Regra:** a `data` da despesa precisa estar entre `periodo.inicio` e `periodo.fim`, incluindo os dois extremos. Fora disso: `recusado`, motivo `fora_do_periodo`.
**Origem:** política do RH, item 7; AMB-009.
**Aceite:** período 2026-07-01 a 2026-07-31: data 2026-04-15 → `fora_do_periodo`; datas 2026-07-01 e 2026-07-31 → seguem para as próximas regras.

### RN-006 — Categorias da política

**Regra:** a categoria é comparada depois de remover espaços no início e no fim e ignorando maiúsculas/minúsculas. Só três categorias são reconhecidas: `alimentacao`, `transporte_urbano` e `hospedagem`. Na saída, categorias reconhecidas aparecem nessa forma normalizada. Qualquer outra (incluindo variações com acento, como `alimentação`) → `recusado`, motivo `categoria_fora_da_politica`.
**Origem:** política do RH, item 9; AMB-011; AMB-012.
**Aceite:** `ALIMENTACAO` e `" Alimentacao "` → tratadas como `alimentacao`; `coworking` → `categoria_fora_da_politica`.

### RN-007 — Duplicatas

**Regra:** duas despesas são duplicatas quando têm a mesma `data`, a mesma categoria normalizada, o mesmo `fornecedor` (comparado sem espaços nas pontas e ignorando maiúsculas/minúsculas) e o mesmo `valor_considerado`. `id` e `descricao` não entram na comparação. Entre despesas duplicatas, só a primeira na ordem da entrada segue avaliada; as seguintes são `recusado`, motivo `duplicata`. Só despesas que passaram por RN-002 a RN-006 participam da comparação. Uma duplicata recusada não consome limite.
**Origem:** política do RH, item 8; AMB-010.
**Aceite:** d-006 e d-007 (mesmos data, categoria, fornecedor e valor 54,90) → d-006 avaliada normalmente, d-007 `recusado`, `duplicata`. Mesmos dados com fornecedor diferente → não são duplicatas.

### RN-008 — Nota fiscal obrigatória acima de R$ 100

**Regra:** despesa com `valor_considerado` estritamente maior que 100,00 e `tem_nota_fiscal` falso → `recusado`, motivo `nota_fiscal_ausente`. A comparação usa o valor da despesa individual, antes de qualquer limite. A despesa recusada não consome limite nem caracteriza viagem.
**Origem:** política do RH, item 5; AMB-007; AMB-008.
**Aceite:** 100,00 sem nota → segue para o limite diário; 100,01 sem nota → `nota_fiscal_ausente`; 100,01 com nota → segue.

### RN-009 — Limite diário por categoria

**Regra:** para cada combinação de data e categoria, a soma reembolsada das despesas que chegaram a esta regra não pode passar do limite diário:

| Categoria | Limite diário normal | Limite diário em viagem (RN-010) |
|---|---|---|
| `alimentacao` | 60,00 | 90,00 |
| `transporte_urbano` | 80,00 | 120,00 |
| `hospedagem` | 250,00 | 250,00 (não amplia, AMB-006) |

O limite é consumido pelas despesas na ordem da entrada: cada despesa recebe `mínimo(valor_considerado, saldo restante do limite)`. Se recebe o valor inteiro → `aprovado`; se recebe parte → `parcial`, motivo `limite_diario_excedido`; se o saldo já era zero → `recusado`, motivo `limite_diario_excedido`.
**Origem:** política do RH, itens 1, 2, 3 e 4; AMB-001; AMB-002; AMB-003.
**Aceite:** alimentação, mesmo dia, fora de viagem: 72,50 e depois 38,00 → primeira `parcial` com 60,00, segunda `recusado` com 0. Ordem invertida (38,00 e depois 72,50) → primeira `aprovado` com 38,00, segunda `parcial` com 22,00.

### RN-010 — Colaborador em viagem

**Regra:** uma data está "em viagem" quando existe na entrada uma despesa de `hospedagem` nessa mesma data que chegou ao limite diário (não foi recusada por RN-002 a RN-008). Em datas em viagem, os limites de `alimentacao` e `transporte_urbano` são ampliados em 50% (tabela da RN-009). Cada despesa de hospedagem cobre apenas a sua própria data (RN-012). A condição de viagem vale para todas as despesas da data, independentemente da ordem em que aparecem na entrada.
**Origem:** política do RH, item 6; AMB-004.
**Aceite:** hospedagem válida em 14/07 + alimentação de 80,00 em 14/07 → limite 90,00, alimentação `aprovado` com 80,00. Alimentação de 80,00 em 15/07 sem hospedagem em 15/07 → limite 60,00, `parcial` com 60,00. Hospedagem de 14/07 recusada por nota fiscal → 14/07 não está em viagem.

### RN-011 — Status e justificativa

**Regra:** `aprovado` quando `valor_reembolsado = valor_considerado`; `parcial` quando `0 < valor_reembolsado < valor_considerado`; `recusado` quando `valor_reembolsado = 0`. Todo item `parcial` ou `recusado` tem um `motivo` da tabela da seção 4; todo item tem uma `justificativa` em texto.
**Origem:** objetivo do sistema.
**Aceite:** nenhum item da saída tem status incompatível com os seus valores.

### RN-012 — Hospedagem: um lançamento é uma diária

**Regra:** cada despesa de `hospedagem` é tratada como uma diária na sua `data`, qualquer que seja o valor ou a descrição. Várias hospedagens na mesma data dividem o mesmo limite diário de 250,00 (RN-009).
**Origem:** política do RH, item 3; AMB-005.
**Aceite:** hospedagem de 480,00 com nota ("2 diarias" na descrição) → `parcial` com 250,00; data em viagem só no dia da despesa.

---

## 6. Ambiguidades identificadas e decisões

Tipo: **U** = unidade de aplicação · **F** = fronteira · **D** = dado ausente.

### AMB-001 — Limite "por dia" é por despesa ou pela soma do dia? (U)

**Texto original do RH:** "Alimentação tem limite de R$ 60 por dia." (idem itens 2 e 3)
**O que não está claro:** se cada despesa pode ir até 60,00, ou se a soma das despesas do dia é que não pode passar de 60,00 (d-001 + d-002 no mesmo dia: 72,50 + 38,00).
**Decisão:** o limite vale para a soma de todas as despesas da mesma categoria na mesma data.
**Justificativa:** "por dia" descreve um teto diário; aplicar por despesa permitiria contornar o limite fracionando a despesa.
**Regra afetada:** RN-009

### AMB-002 — "Reembolsadas parcialmente" = paga até o limite ou recusa? (F)

**Texto original do RH:** "Despesas acima do limite são reembolsadas parcialmente."
**O que não está claro:** se paga o valor do limite e corta o excedente, ou se recusa a despesa inteira.
**Decisão:** paga até o limite e corta só o excedente.
**Justificativa:** "parcialmente" significa que parte é paga; recusar tudo contradiria o texto.
**Regra afetada:** RN-009

### AMB-003 — Como dividir o limite entre várias despesas do mesmo dia? (U)

**Texto original do RH:** (não tratado)
**O que não está claro:** quando a soma do dia passa do limite, de qual despesa sai o corte. A entrada não tem horário.
**Decisão:** as despesas consomem o limite na ordem em que aparecem na entrada; o corte cai nas últimas.
**Justificativa:** é o único critério determinístico disponível nos dados e reproduz a conferência item a item feita hoje.
**Regra afetada:** RN-009

### AMB-004 — O que caracteriza "em viagem"? (D)

**Texto original do RH:** "Colaborador em viagem tem limites ampliados em 50%."
**O que não está claro:** a entrada não tem campo de viagem.
**Decisão:** uma data está em viagem se há na entrada uma hospedagem válida (não recusada antes do limite) nessa data.
**Justificativa:** hospedagem é a única evidência objetiva de viagem nos dados; uma hospedagem recusada não comprova a viagem.
**Regra afetada:** RN-010

### AMB-005 — Uma despesa de hospedagem com várias diárias (D, U)

**Texto original do RH:** "Hospedagem tem limite de R$ 250 por diária."
**O que não está claro:** a entrada não informa quantas diárias uma despesa representa; essa informação só aparece em texto livre (d-010 "2 diarias", d-013 "3 noites").
**Decisão:** cada lançamento de hospedagem é uma diária, na data da despesa. A descrição não é interpretada.
**Justificativa:** sem campo estruturado, contar diárias a partir de texto livre seria adivinhar; a solução correta (datas de entrada e saída) exige mudar o formato de entrada, que é fixo (seção 3).
**Regra afetada:** RN-012, RN-010

### AMB-006 — O acréscimo de 50% vale para a hospedagem? (U)

**Texto original do RH:** "Colaborador em viagem tem limites ampliados em 50%."
**O que não está claro:** se "limites" inclui o de hospedagem, que já pressupõe viagem.
**Decisão:** não; a hospedagem tem sempre limite de 250,00 por diária.
**Justificativa:** toda hospedagem já é viagem; ampliar o limite dela tornaria o valor de 250,00 da política inalcançável na prática.
**Regra afetada:** RN-009

### AMB-007 — "Acima de R$ 100": exatamente 100,00 exige nota? (F)

**Texto original do RH:** "Nota fiscal é obrigatória acima de R$ 100."
**O que não está claro:** se 100,00 está incluído (d-003 = 100,00 e d-004 = 100,01, ambos sem nota).
**Decisão:** só exige nota quando o valor é estritamente maior que 100,00.
**Justificativa:** leitura literal de "acima de".
**Regra afetada:** RN-008

### AMB-008 — O que acontece sem a nota obrigatória, e sobre qual valor se compara? (F, U)

**Texto original do RH:** "Nota fiscal é obrigatória acima de R$ 100."
**O que não está claro:** se a despesa sem nota é recusada inteira ou paga até 100,00; e se o 100,00 se compara ao valor da despesa, ao valor já limitado ou à soma do dia.
**Decisão:** recusa a despesa inteira; compara com o valor individual da despesa (arredondado), antes de qualquer limite.
**Justificativa:** "obrigatória" é condição para reembolsar; comparar antes do limite impede que o corte do limite "esconda" a falta de nota.
**Regra afetada:** RN-008

### AMB-009 — "Lançadas dentro do período de competência" (D, F)

**Texto original do RH:** "Despesas devem ser lançadas dentro do período de competência."
**O que não está claro:** a entrada não tem data de lançamento, só a data da despesa; e se os extremos do período estão incluídos.
**Decisão:** a data da despesa precisa estar entre `inicio` e `fim`, ambos inclusive.
**Justificativa:** a data da despesa é o único dado disponível; o período informado é fechado nos dois extremos.
**Regra afetada:** RN-005

### AMB-010 — O que é duplicata e como tratá-la? (U)

**Texto original do RH:** "Duplicatas devem ser tratadas."
**O que não está claro:** quais campos definem uma duplicata (d-006 e d-007 só diferem no id) e o que fazer com ela.
**Decisão:** mesma data, categoria, fornecedor e valor; a primeira na ordem da entrada é avaliada, as demais são recusadas com motivo `duplicata`.
**Justificativa:** o id é gerado no lançamento e não identifica o gasto; recusar com motivo explícito deixa visível um eventual gasto legítimo repetido, para o colaborador contestar.
**Regra afetada:** RN-007

### AMB-011 — Categoria com grafia diferente (F)

**Texto original do RH:** (não tratado)
**O que não está claro:** se `ALIMENTACAO` (d-014) é a mesma categoria que `alimentacao`.
**Decisão:** ignora maiúsculas/minúsculas e espaços nas pontas; não ignora acentos.
**Justificativa:** diferença de caixa é erro de digitação inequívoco; acentos e outras variações não são presumidos.
**Regra afetada:** RN-006

### AMB-012 — Categoria fora da política: recusar ou omitir? (U)

**Texto original do RH:** "Categorias fora da política não são reembolsáveis."
**O que não está claro:** se a despesa some do resultado ou aparece recusada.
**Decisão:** aparece na saída como `recusado`, motivo `categoria_fora_da_politica`.
**Justificativa:** o objetivo é justificar cada decisão; omitir esconderia a despesa do colaborador.
**Regra afetada:** RN-006, RN-001

### AMB-013 — Valor negativo (estorno) (D)

**Texto original do RH:** (não tratado)
**O que não está claro:** d-009 tem valor -45,00 ("estorno"): se abate do dia, se é ignorado ou se é erro.
**Decisão:** valor menor ou igual a zero é recusado com motivo `valor_invalido` e não afeta nenhuma outra despesa.
**Justificativa:** o sistema calcula reembolso de despesas; estorno não é despesa e não há como saber a qual despesa ele se refere.
**Regra afetada:** RN-004

### AMB-014 — Valor com mais de 2 casas decimais (F)

**Texto original do RH:** (não tratado)
**O que não está claro:** d-011 tem 33,333: arredondar, truncar ou recusar, e quando.
**Decisão:** arredonda para o centavo, metade para cima, antes de qualquer regra.
**Justificativa:** reembolso é pago em centavos; arredondar no início garante que todas as regras usem o mesmo valor.
**Regra afetada:** RN-003

### AMB-015 — Despesa em fim de semana (D)

**Texto original do RH:** (não tratado)
**O que não está claro:** d-012 é um almoço de sábado ("plantão"); a política não diz se despesas em fim de semana são aceitas.
**Decisão:** dia da semana não afeta o reembolso.
**Justificativa:** a política não restringe; criar a restrição seria inventar regra.
**Regra afetada:** nenhuma (registrado em Fora de escopo)

### AMB-016 — Em que ordem as regras se aplicam? (U)

**Texto original do RH:** (não tratado)
**O que não está claro:** quando várias regras incidem na mesma despesa, a ordem muda o resultado (ex.: se uma duplicata ou uma despesa sem nota consome o limite do dia).
**Decisão:** ordem da seção 8; a primeira recusa encerra a avaliação da despesa; só despesas que chegam ao limite diário o consomem.
**Justificativa:** despesa recusada não é reembolsável e, portanto, não deve tirar limite de uma despesa válida.
**Regra afetada:** todas

---

## 7. Casos de borda

| Caso | Entrada | Comportamento esperado | Regra |
|---|---|---|---|
| Duas alimentações no mesmo dia somando mais que o limite | 72,50 e 38,00 em 03/07, fora de viagem | 60,00 `parcial` e 0 `recusado` (`limite_diario_excedido`) | RN-009 |
| Valor exatamente no limite de nota | 100,00 sem nota, transporte | não exige nota; limite 80,00 → `parcial` com 80,00 | RN-008, RN-009 |
| Um centavo acima do limite de nota | 100,01 sem nota | `recusado`, `nota_fiscal_ausente` | RN-008 |
| Valor exatamente no limite diário | alimentação 60,00 | `aprovado` com 60,00 | RN-009 |
| Um centavo acima do limite diário | alimentação 60,01 | `parcial` com 60,00 | RN-009 |
| Primeiro e último dia do período | datas iguais a `inicio` e a `fim` | dentro do período | RN-005 |
| Um dia fora do período | `fim` + 1 dia | `fora_do_periodo` | RN-005 |
| Categoria em maiúsculas | `ALIMENTACAO` | tratada como `alimentacao` | RN-006 |
| Categoria com acento | `alimentação` | `categoria_fora_da_politica` | RN-006 |
| Duplicata exata | mesmos data, categoria, fornecedor, valor | segunda `duplicata` | RN-007 |
| Quase duplicata | mesmo valor, fornecedor diferente | as duas avaliadas | RN-007 |
| Duplicata depois de despesa recusada por nota | 1ª: 150,00 sem nota; 2ª: idêntica | 1ª `nota_fiscal_ausente`; 2ª `duplicata` | RN-007, seção 8 |
| Estorno | -45,00 | `valor_invalido`; não altera o dia | RN-004 |
| Valor zero | 0,00 | `valor_invalido` | RN-004 |
| Três casas decimais | 33,333 | considerado 33,33 | RN-003 |
| Arredondamento da metade | 10,005 | considerado 10,01 | RN-003 |
| Hospedagem com várias diárias na descrição | 480,00 "2 diarias", com nota | 1 diária: `parcial` com 250,00 | RN-012 |
| Hospedagem sem nota acima de 100 | 690,00 sem nota | `nota_fiscal_ausente`; data não fica em viagem | RN-008, RN-010 |
| Alimentação antes da hospedagem na entrada, mesma data | alimentação 80,00 e depois hospedagem válida, mesma data | data em viagem: alimentação `aprovado` com 80,00 (limite 90,00) | RN-010 |
| Duas hospedagens na mesma data | 200,00 e 100,00, com nota | 200,00 `aprovado`; 50,00 `parcial` | RN-012, RN-009 |
| Campo obrigatório ausente | despesa sem `tem_nota_fiscal` | `entrada_invalida`; demais processadas | RN-002 |
| Lista de despesas vazia | `despesas: []` | `itens` vazio, totais 0 | RN-001 |
| Despesa em sábado | 18/07 (sábado) | avaliada normalmente | AMB-015 |

## 8. Ordem de aplicação das regras

Cada despesa passa pelas etapas abaixo, nesta ordem. A primeira etapa que a recusa encerra a avaliação dela.

1. **Validação da despesa** — RN-002 (`entrada_invalida`).
2. **Arredondamento** — RN-003.
3. **Valor positivo** — RN-004 (`valor_invalido`).
4. **Período** — RN-005 (`fora_do_periodo`).
5. **Categoria** — RN-006 (`categoria_fora_da_politica`).
6. **Duplicata** — RN-007 (`duplicata`), comparando só com despesas anteriores que passaram pelas etapas 1 a 5.
7. **Nota fiscal** — RN-008 (`nota_fiscal_ausente`).
8. **Viagem** — RN-010: com todas as despesas já avaliadas pelas etapas 1 a 7, marca as datas em viagem.
9. **Limite diário** — RN-009, por data e categoria, consumindo o limite na ordem da entrada.

Consequências: despesas recusadas nas etapas 1 a 7 não consomem limite; uma hospedagem recusada nas etapas 1 a 7 não caracteriza viagem; a viagem é determinada antes de qualquer limite ser aplicado.

## 9. Critérios de aceite

O sistema está pronto quando:

- [ ] Processa `exemplos/despesas-exemplo.json` e produz exatamente o resultado da tabela abaixo.
- [ ] Cada caso de borda da seção 7 tem um teste automatizado que passa.
- [ ] Cada regra RN-001 a RN-012 tem pelo menos um teste automatizado que a referencia.
- [ ] A mesma entrada sempre produz a mesma saída.
- [ ] Entradas com erro de arquivo (RN-002) terminam com código diferente de 0 e não geram arquivo de saída.

**Resultado esperado para `exemplos/despesas-exemplo.json`** (nenhuma data do exemplo fica em viagem):

| id | considerado | limite | reembolsado | status | motivo |
|---|---|---|---|---|---|
| d-001 | 72,50 | 60,00 | 60,00 | parcial | limite_diario_excedido |
| d-002 | 38,00 | 60,00 | 0,00 | recusado | limite_diario_excedido |
| d-003 | 100,00 | 80,00 | 80,00 | parcial | limite_diario_excedido |
| d-004 | 100,01 | — | 0,00 | recusado | nota_fiscal_ausente |
| d-005 | 89,00 | — | 0,00 | recusado | categoria_fora_da_politica |
| d-006 | 54,90 | 60,00 | 54,90 | aprovado | — |
| d-007 | 54,90 | — | 0,00 | recusado | duplicata |
| d-008 | 41,00 | — | 0,00 | recusado | fora_do_periodo |
| d-009 | -45,00 | — | 0,00 | recusado | valor_invalido |
| d-010 | 480,00 | 250,00 | 250,00 | parcial | limite_diario_excedido |
| d-011 | 33,33 | 60,00 | 33,33 | aprovado | — |
| d-012 | 47,20 | 60,00 | 47,20 | aprovado | — |
| d-013 | 690,00 | — | 0,00 | recusado | nota_fiscal_ausente |
| d-014 | 61,00 | 60,00 | 60,00 | parcial | limite_diario_excedido |

Totais: `valor_solicitado` = 1.861,84 · `valor_reembolsado` = 585,43 · `valor_glosado` = 1.276,41.

> d-011 (café no hotel em 15/07) não está em viagem: d-010 é uma diária só em 14/07 (AMB-005).

## 10. O que fica em aberto

- **Datas de entrada e saída de hospedagem.** A solução correta para AMB-005 exige mudar o formato de entrada. Decisão provisória: um lançamento = uma diária. Consequência conhecida: d-010 recebe 250,00 de 480,00 mesmo se forem de fato duas diárias.
- **Ids repetidos na entrada.** A política não trata. Decisão provisória: despesas com o mesmo `id` são avaliadas normalmente, cada uma pelo seu conteúdo; a saída repete o id.
- **`competencia` inconsistente com `inicio`/`fim`.** Decisão provisória: o período vale por `inicio` e `fim`; `competencia` só é repetida na saída.
- **Estorno vinculado a uma despesa.** Se o formato um dia trouxer referência à despesa original, AMB-013 deve ser revista.
