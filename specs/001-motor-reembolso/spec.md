# Spec — Motor de Cálculo de Reembolso

**Versão:** 1.3 · **Status:** aprovada para planejamento · **Última alteração:** 2026-10-01 (ver `DECISIONS.md` D-001 a D-003)

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
- Não lê nem interpreta o texto livre de `descricao` (nem para contar diárias, AMB-005, nem para identificar refeição com cliente, AMB-017).
- Não converte moedas: todos os valores são em reais.
- Não guarda histórico entre execuções: duplicatas só são detectadas dentro da mesma entrada.
- Não usa campos além dos previstos na seção 4; campos extras são ignorados (RN-002). Em particular, não usa datas de entrada e saída de hospedagem: seriam a solução ideal para AMB-005, mas o formato de entrada é fixo. Fica registrado como evolução recomendada.
- Não tem categoria nem limite de representação (refeição com cliente): fica registrado como evolução recomendada (AMB-017).
- Não recebe indicação explícita de viagem na entrada (ex.: um indicador `em_viagem` ou um código de viagem aprovada): a viagem é inferida da hospedagem (RN-010). Uma indicação explícita eliminaria a inferência e o risco registrado na seção 10; fica registrada como evolução recomendada, pois exige mudar o formato fixo.
- Não trata feriados nem fins de semana de forma especial (AMB-015).

## 4. Entrada e saída

### Interface

`<comando> calcular --input <arquivo de entrada> --output <arquivo de saída>`

- Sucesso: grava o arquivo de saída e termina com código 0.
- Erro de arquivo (RN-002), inclusive quando o arquivo de saída não pode ser gravado: não cria nem altera o arquivo de saída (se já existia, permanece como estava), escreve uma mensagem de erro e termina com código diferente de 0.
- Erro de uso (subcomando diferente de `calcular`, `--input` ou `--output` ausentes): mesmo comportamento do erro de arquivo.

### Entrada

Formato fixo, conforme `exemplos/despesas-exemplo.json`.

| Campo | Tipo | Significado | Obrigatório |
|---|---|---|---|
| `colaborador.id` | texto | identificador do colaborador | sim (erro de arquivo) |
| `colaborador.nome` | texto | nome | sim (erro de arquivo) |
| `colaborador.centro_custo` | texto | centro de custo | não |
| `periodo.competencia` | texto `AAAA-MM` | rótulo do mês de competência; repetido na saída, não usado em cálculo | não |
| `periodo.inicio` | data `AAAA-MM-DD` | primeiro dia do período (inclusive) | sim (erro de arquivo) |
| `periodo.fim` | data `AAAA-MM-DD` | último dia do período (inclusive) | sim (erro de arquivo) |
| `despesas` | lista | despesas a avaliar (pode ser vazia) | sim (erro de arquivo) |
| `despesas[].id` | texto | identificador da despesa | sim (`entrada_invalida`) |
| `despesas[].data` | data `AAAA-MM-DD` | data em que a despesa ocorreu | sim (`entrada_invalida`) |
| `despesas[].categoria` | texto | categoria da despesa | sim (`entrada_invalida`) |
| `despesas[].descricao` | texto | descrição livre; não usada em regras | não |
| `despesas[].fornecedor` | texto | estabelecimento; usado na detecção de duplicatas | sim (`entrada_invalida`) |
| `despesas[].valor` | número | valor em reais | sim (`entrada_invalida`) |
| `despesas[].tem_nota_fiscal` | booleano | se há nota fiscal | sim (`entrada_invalida`) |

Campos não listados acima são ignorados.

### Saída

| Campo | Tipo | Significado |
|---|---|---|
| `colaborador` | objeto | `id` e `nome`, copiados da entrada |
| `periodo` | objeto | `inicio` e `fim`, copiados da entrada; `competencia` copiada se for texto (em qualquer formato), nula se ausente ou não for texto |
| `itens` | lista | um item por elemento de `despesas`, **na mesma ordem** |
| `itens[].id` | texto ou nulo | id da despesa como veio, se for texto; nulo se ausente, se não for texto ou se o elemento não é um objeto |
| `itens[].data` | texto ou nulo | data da despesa como veio, se for texto; nulo se ausente, se não for texto ou se o elemento não é um objeto |
| `itens[].categoria` | texto ou nulo | categoria normalizada (RN-006) se reconhecida, qualquer que seja o status ou o motivo do item (inclusive `entrada_invalida`); senão, como veio, se for texto; nulo se ausente ou não for texto |
| `itens[].valor_informado` | número ou nulo | o número recebido em `valor`, sem arredondamento; nulo se ausente ou não numérico |
| `itens[].valor_considerado` | número ou nulo | valor arredondado ao centavo (RN-003); **nulo se a despesa foi recusada por `entrada_invalida`** |
| `itens[].valor_reembolsado` | número | quanto será reembolsado (0 se recusado) |
| `itens[].status` | texto | `aprovado`, `parcial` ou `recusado` (RN-011) |
| `itens[].motivo` | texto ou nulo | código do motivo (tabela abaixo); nulo quando `aprovado` |
| `itens[].em_viagem` | booleano ou nulo | se a data estava em viagem (RN-010); nulo se o item foi recusado antes do limite diário |
| `itens[].limite_diario` | número ou nulo | limite diário aplicado à categoria naquela data; nulo se o item foi recusado antes do limite diário |
| `itens[].justificativa` | texto | frase em português explicando a decisão. Texto livre: **não é contratual**; os campos acima são |
| `totais.valor_solicitado` | número | soma de `valor_considerado` dos itens **não recusados por `entrada_invalida` e com `valor_considerado` maior que zero** |
| `totais.valor_reembolsado` | número | soma de `valor_reembolsado` |
| `totais.valor_glosado` | número | `valor_solicitado − valor_reembolsado` |

Todos os valores monetários **calculados** da saída (`valor_considerado`, `valor_reembolsado`, `limite_diario` e totais) são em reais, com no máximo 2 casas decimais e exatos ao centavo. `valor_informado` é a única exceção: é a cópia do número recebido (ex.: 33.333). Como a entrada é um número, "como veio" se refere ao valor numérico, não à forma escrita (72.50 e 72.5 são o mesmo valor).

**Códigos de motivo** (na ordem das etapas da seção 8):

| Código | Quando | Status resultante |
|---|---|---|
| `entrada_invalida` | elemento que não é objeto, ou campo obrigatório ausente ou com tipo/formato errado (RN-002) | `recusado` |
| `valor_invalido` | valor considerado menor ou igual a zero (RN-004) | `recusado` |
| `fora_do_periodo` | data fora de `[inicio, fim]` (RN-005) | `recusado` |
| `categoria_fora_da_politica` | categoria não reconhecida (RN-006) | `recusado` |
| `nota_fiscal_ausente` | valor acima de 100,00 sem nota (RN-008) | `recusado` |
| `duplicata` | repete uma despesa anterior (RN-007) | `recusado` |
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

**Normalização de texto** (usada em RN-006 e RN-007), aplicada nesta ordem:

1. remover todo espaço em branco do início e do fim (espaço comum, tabulação, quebra de linha, espaço não separável e demais caracteres de espaço em branco);
2. ignorar maiúsculas/minúsculas;
3. toda letra com acento ou sinal diacrítico é comparada como a letra base, qualquer que seja a forma como o caractere foi codificado no arquivo (`á`→`a`, `ç`→`c`, `ô`→`o`, `ü`→`u`, `ñ`→`n`);
4. toda sequência interna de espaços em branco, hífens (`-`) e sublinhados (`_`) vale como um único `_`.

Exemplos: `"Transporte Urbano"`, `"transporte-urbano"` e `" TRANSPORTE__urbano "` → `transporte_urbano`; `"Pão  Quente"` e `"pao-quente"` → `pao_quente`.

### RN-001 — Um resultado por despesa

**Regra:** a saída tem exatamente um item para cada elemento de `despesas`, na mesma ordem, inclusive os recusados. Os totais seguem as fórmulas da seção 4.
**Origem:** objetivo do sistema ("justifica cada decisão").
**Aceite:** entrada com 14 despesas gera 14 itens, na mesma ordem de ids; `valor_glosado = valor_solicitado − valor_reembolsado`.

### RN-002 — Validação da entrada

**Regra:**
- **Erro de arquivo** (o arquivo de saída não é criado nem alterado): arquivo de entrada ausente ou que não é JSON válido; `colaborador` ausente ou sem `id`/`nome` em texto, ou com `id`/`nome` vazio ou só com espaços em branco; `periodo.inicio`, `periodo.fim` ou `despesas` ausentes; `inicio` ou `fim` que não são datas válidas `AAAA-MM-DD`; `inicio` posterior a `fim`; `despesas` que não é lista; arquivo de saída que não pode ser gravado. `periodo.competencia` nunca causa erro: se não for texto, sai nula.
- **Despesa inválida** (vira item `recusado` com motivo `entrada_invalida`; as demais despesas seguem): elemento de `despesas` que não é um objeto; falta `id`, `data`, `categoria`, `fornecedor`, `valor` ou `tem_nota_fiscal`; `data` não é data válida `AAAA-MM-DD`; `valor` não é número; `tem_nota_fiscal` não é booleano; `id`, `categoria` ou `fornecedor` não são texto, ou são texto vazio ou só com espaços em branco.
- Na saída de uma despesa inválida, `id`, `data` e `categoria` são copiados se forem texto e saem nulos caso contrário (tipo errado, ausente ou elemento que não é objeto); a `categoria`, se reconhecida, sai normalizada, como em qualquer item (seção 4).
- Uma despesa recusada por `entrada_invalida` tem `valor_considerado` nulo, `em_viagem` e `limite_diario` nulos, e não entra nos totais.
- Campos extras, no arquivo ou nas despesas, são ignorados.
**Origem:** necessidade operacional (a política não trata entrada malformada); pontos 7 e 9 de D-001.
**Aceite:** despesa sem `tem_nota_fiscal` com `valor` 33.333 → `recusado`, `entrada_invalida`, `valor_informado` 33.333, `valor_considerado` nulo, fora de `valor_solicitado`; as demais despesas são processadas normalmente. Elemento `null` em `despesas` → item com `id` e `data` nulos, `entrada_invalida`. Arquivo sem `colaborador` → nenhuma saída, código diferente de 0. Hospedagem com campo extra `"noites": 2` → avaliada como uma diária (RN-012). Despesa com `"id": 17` → `entrada_invalida`, `id` nulo na saída. Despesa com `fornecedor` `"   "` → `entrada_invalida`. `competencia` 202607 (número) → processamento normal, `competencia` nula na saída. Caminho de saída em pasta inexistente → nenhuma saída, código diferente de 0. Despesa `"categoria": "ALIMENTACAO"` sem `tem_nota_fiscal` → `entrada_invalida`, `categoria` `alimentacao` na saída. `colaborador.nome` `"  "` → erro de arquivo. Erro de arquivo com arquivo de saída preexistente → o arquivo continua com o conteúdo anterior. Chamada sem `--output` → código diferente de 0.

### RN-003 — Arredondamento ao centavo

**Regra:** antes de qualquer outra regra de valor, `valor` é arredondado para 2 casas decimais, com a metade arredondada afastando do zero (0,005 → 0,01; -0,005 → -0,01). Todas as regras usam o valor arredondado (`valor_considerado`), e todos os cálculos são exatos ao centavo.
**Origem:** AMB-014.
**Aceite:** `valor` 33.333 → `valor_considerado` 33.33; `valor` 10.005 → 10.01; `valor` 10.004 → 10.00.

### RN-004 — Valor deve ser positivo

**Regra:** despesa com `valor_considerado` menor ou igual a zero é `recusado` com motivo `valor_invalido`. Ela não abate, não soma nos totais e não consome limite de nenhuma outra despesa.
**Origem:** AMB-013.
**Aceite:** `valor` -45.00 → `recusado`, `valor_invalido`, `valor_reembolsado` 0; demais despesas do mesmo dia não mudam. `valor` 0 → `valor_invalido`. `valor` 0.004 (arredonda para 0,00) → `valor_invalido`.

### RN-005 — Período de competência

**Regra:** a `data` da despesa precisa estar entre `periodo.inicio` e `periodo.fim`, incluindo os dois extremos. Fora disso: `recusado`, motivo `fora_do_periodo`.
**Origem:** política do RH, item 7; AMB-009.
**Aceite:** período 2026-07-01 a 2026-07-31: data 2026-04-15 → `fora_do_periodo`; datas 2026-07-01 e 2026-07-31 → seguem para as próximas regras.

### RN-006 — Categorias da política

**Regra:** a categoria é comparada depois da normalização de texto (seção 5). Só três categorias são reconhecidas: `alimentacao`, `transporte_urbano` e `hospedagem`. Na saída, categorias reconhecidas aparecem nessa forma normalizada. Qualquer outra → `recusado`, motivo `categoria_fora_da_politica`.
**Origem:** política do RH, item 9; AMB-011; AMB-012.
**Aceite:** `ALIMENTACAO`, `" Alimentacao "`, `"alimentacao\t"` e `alimentação` → tratadas como `alimentacao`; `"Transporte Urbano"` e `"transporte-urbano"` → `transporte_urbano`; `coworking` → `categoria_fora_da_politica`.

### RN-007 — Duplicatas

**Regra:** duas despesas são duplicatas quando têm a mesma `data`, a mesma categoria normalizada, o mesmo `fornecedor` normalizado (seção 5) e o mesmo `valor_considerado`. `id`, `descricao` e `tem_nota_fiscal` não entram na comparação. Só participam da comparação despesas que passaram pelas etapas 1 a 6 da seção 8 (inclusive a nota fiscal): uma despesa recusada antes disso não é "original" de ninguém. Dentro de cada grupo de despesas duplicatas entre si, segue avaliada uma só, a **original**: a primeira na ordem da entrada que tem `tem_nota_fiscal` verdadeiro; se nenhuma do grupo tem, a primeira na ordem da entrada. Todas as outras do grupo são `recusado`, motivo `duplicata`, e não consomem limite nem comprovam viagem. Assim, qual cópia sobrevive não depende da ordem quando só uma delas tem nota. A comparação é exata: datas, valores ou fornecedores diferentes após a normalização não são duplicatas (risco aceito, seção 10).
**Origem:** política do RH, item 8; AMB-010.
**Aceite:** d-006 e d-007 (mesmos data, categoria, fornecedor e valor 54,90, ambas com nota) → d-006 avaliada normalmente, d-007 `duplicata`. Táxi de 110,00 sem nota seguido do mesmo táxi com nota → o primeiro `nota_fiscal_ausente`, o segundo segue avaliado (não é duplicata), em qualquer ordem. Hospedagem de 90,00 sem nota e a mesma com nota, em qualquer ordem → a com nota é a original (comprova viagem, RN-010), a sem nota é `duplicata`. "Bistro Central" e "Bistrô Central" → mesmo fornecedor.

### RN-008 — Nota fiscal obrigatória acima de R$ 100

**Regra:** despesa com `valor_considerado` estritamente maior que 100,00 e `tem_nota_fiscal` falso → `recusado`, motivo `nota_fiscal_ausente`. A comparação usa o valor da despesa individual, antes de qualquer limite. O valor de 100,00 é fixo: não é ampliado em viagem. A despesa recusada não consome limite, não caracteriza viagem e não participa da comparação de duplicatas.
**Origem:** política do RH, item 5; AMB-007; AMB-008.
**Aceite:** 100,00 sem nota → segue; 100,01 sem nota → `nota_fiscal_ausente`; 100,01 com nota → segue; transporte de 110,00 sem nota em data em viagem → `nota_fiscal_ausente`.

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

**Regra:** uma despesa de `hospedagem` **comprova viagem** quando tem `tem_nota_fiscal` verdadeiro e passou pelas etapas 1 a 7 da seção 8. Uma hospedagem que comprova viagem na data D coloca em viagem as datas **D e D+1** (a noite da diária e o dia seguinte). Em datas em viagem, os limites de `alimentacao` e `transporte_urbano` são ampliados em 50% (tabela da RN-009). A condição de viagem vale para todas as despesas da data, independentemente da ordem em que aparecem na entrada.
**Origem:** política do RH, item 6; AMB-004.
**Aceite:** hospedagem com nota em 14/07 → 14/07 e 15/07 em viagem; alimentação de 80,00 em 15/07 → limite 90,00, `aprovado` com 80,00; alimentação de 80,00 em 16/07 → limite 60,00, `parcial` com 60,00. Hospedagem de 80,00 **sem** nota em 03/07 → reembolsada pelas regras normais, mas 03/07 e 04/07 **não** ficam em viagem. Hospedagem com nota em 30/06, fora de um período que começa em 01/07 → recusada por `fora_do_periodo`, e 01/07 não fica em viagem.

### RN-011 — Status e justificativa

**Regra:** `aprovado` quando `valor_reembolsado = valor_considerado`; `parcial` quando `0 < valor_reembolsado < valor_considerado`; `recusado` quando `valor_reembolsado = 0`. Todo item `parcial` ou `recusado` tem um `motivo` da tabela da seção 4; todo item tem uma `justificativa` em texto.
**Origem:** objetivo do sistema.
**Aceite:** nenhum item da saída tem status incompatível com os seus valores.

### RN-012 — Hospedagem: um lançamento é uma diária

**Regra:** cada despesa de `hospedagem` é tratada como uma diária na sua `data`, qualquer que seja o valor, a descrição ou campos extras. Várias hospedagens na mesma data dividem o mesmo limite diário de 250,00 (RN-009).
**Origem:** política do RH, item 3; AMB-005.
**Aceite:** hospedagem de 480,00 com nota em 14/07 ("2 diarias" na descrição) → `parcial` com 250,00; 14/07 e 15/07 em viagem (RN-010).

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
**Decisão:** as despesas consomem o limite na ordem em que aparecem na entrada; o corte cai nas últimas. Se o saldo acabou, a despesa é `recusado` com `limite_diario_excedido`.
**Justificativa:** é o único critério determinístico disponível nos dados e reproduz a conferência item a item feita hoje.
**Regra afetada:** RN-009

### AMB-004 — O que caracteriza "em viagem"? (D)

**Texto original do RH:** "Colaborador em viagem tem limites ampliados em 50%."
**O que não está claro:** a entrada não tem campo de viagem. Também não está claro se uma hospedagem barata e sem nota basta como prova, e se o dia seguinte ao pernoite conta (d-011, café no hotel em 15/07, depois da diária de 14/07).
**Decisão:** uma hospedagem **com nota fiscal** que não foi recusada antes do limite comprova viagem na data dela e no dia seguinte.
**Justificativa:** hospedagem é a única evidência objetiva de viagem nos dados, e exigir a nota a torna verificável na conferência humana; uma diária é uma noite, então o colaborador acorda em viagem no dia seguinte. A exigência **não** elimina o abuso: o sistema confia no `tem_nota_fiscal` declarado (seção 3), então uma hospedagem irrisória com nota declarada ainda amplia os limites de D e D+1 (risco aceito, seção 10).
**Regra afetada:** RN-010

### AMB-005 — Uma despesa de hospedagem com várias diárias (D, U)

**Texto original do RH:** "Hospedagem tem limite de R$ 250 por diária."
**O que não está claro:** a entrada não informa quantas diárias uma despesa representa; essa informação só aparece em texto livre (d-010 "2 diarias", d-013 "3 noites").
**Decisão:** cada lançamento de hospedagem é uma diária, na data da despesa. A descrição e campos extras não são interpretados.
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
**Decisão:** só exige nota quando o valor é estritamente maior que 100,00. O valor de 100,00 não é ampliado em viagem.
**Justificativa:** leitura literal de "acima de"; a ampliação da política (item 6) fala de limites de reembolso, não da exigência de nota.
**Regra afetada:** RN-008

### AMB-008 — O que acontece sem a nota obrigatória, e sobre qual valor se compara? (F, U)

**Texto original do RH:** "Nota fiscal é obrigatória acima de R$ 100."
**O que não está claro:** se a despesa sem nota é recusada inteira ou paga até 100,00; e se o 100,00 se compara ao valor da despesa, ao valor já limitado ou à soma do dia.
**Decisão:** recusa a despesa inteira; compara com o valor individual da despesa (arredondado), antes de qualquer limite.
**Justificativa:** "obrigatória" é condição para reembolsar; comparar antes do limite impede que o corte do limite "esconda" a falta de nota; comparar pela soma do dia recusaria despesas pequenas legítimas sem nota (duas corridas de 60,00). A brecha do fracionamento é aceita conscientemente (seção 10).
**Regra afetada:** RN-008

### AMB-009 — "Lançadas dentro do período de competência" (D, F)

**Texto original do RH:** "Despesas devem ser lançadas dentro do período de competência."
**O que não está claro:** a entrada não tem data de lançamento, só a data da despesa (d-008: "Almoco de abril lancado com atraso", data 15/04 num relatório de julho); e se os extremos do período estão incluídos.
**Decisão:** a data da despesa precisa estar entre `inicio` e `fim`, ambos inclusive.
**Justificativa:** toda despesa da entrada já está "lançada" no relatório do período; se "lançada" significasse só isso, a regra nunca recusaria nada e despesas de qualquer mês antigo entrariam. A data da despesa é o único dado que dá sentido à regra.
**Regra afetada:** RN-005

### AMB-010 — O que é duplicata e como tratá-la? (U)

**Texto original do RH:** "Duplicatas devem ser tratadas."
**O que não está claro:** quais campos definem uma duplicata (d-006 e d-007 só diferem no id), o que fazer com ela, e se uma despesa relançada com a nota fiscal que faltava é duplicata da original.
**Decisão:** mesma data, categoria, fornecedor e valor (texto normalizado, comparação exata); a nota fiscal é verificada antes, e só despesas que passaram por ela são comparadas; a original é a primeira com nota fiscal (ou, se nenhuma tem, a primeira na ordem da entrada), e as demais são recusadas com motivo `duplicata`.
**Justificativa:** o id é gerado no lançamento e não identifica o gasto; verificar a nota antes e preferir a cópia com nota tornam o resultado independente da ordem e permitem corrigir uma nota faltante, inclusive abaixo de 100,00, onde a nota importa para comprovar viagem; recusar com motivo explícito deixa visível um eventual gasto legítimo repetido, para o colaborador contestar.
**Regra afetada:** RN-007

### AMB-011 — Categoria com grafia diferente (F)

**Texto original do RH:** (não tratado)
**O que não está claro:** se `ALIMENTACAO` (d-014) é a mesma categoria que `alimentacao`; e uma grafia com acento (`alimentação`).
**Decisão:** normalização completa da seção 5: espaços em branco nas pontas, maiúsculas/minúsculas, qualquer acento ou sinal diacrítico, e separadores internos (espaço, hífen, sublinhado) equivalentes. A mesma normalização vale para o fornecedor.
**Justificativa:** são variações de escrita da mesma palavra; recusar `alimentação` puniria quem escreve corretamente em português, e recusar `Transporte Urbano` recusaria a grafia que o próprio RH usou na política.
**Regra afetada:** RN-006, RN-007

### AMB-012 — Categoria fora da política: recusar ou omitir? (U)

**Texto original do RH:** "Categorias fora da política não são reembolsáveis."
**O que não está claro:** se a despesa some do resultado ou aparece recusada.
**Decisão:** aparece na saída como `recusado`, motivo `categoria_fora_da_politica`.
**Justificativa:** o objetivo é justificar cada decisão; omitir esconderia a despesa do colaborador.
**Regra afetada:** RN-006, RN-001

### AMB-013 — Valor negativo (estorno) ou zero (D)

**Texto original do RH:** (não tratado)
**O que não está claro:** d-009 tem valor -45,00 ("estorno"): se abate do dia, se é ignorado ou se é erro. Também não está claro o que fazer com valor zero.
**Decisão:** valor menor ou igual a zero é recusado com motivo `valor_invalido` e não afeta nenhuma outra despesa nem os totais.
**Justificativa:** o sistema calcula reembolso de despesas; estorno não é despesa e não há como saber a qual despesa ele se refere; valor zero não é despesa e provavelmente é erro de lançamento.
**Regra afetada:** RN-004

### AMB-014 — Valor com mais de 2 casas decimais (F)

**Texto original do RH:** (não tratado)
**O que não está claro:** d-011 tem 33,333: arredondar, truncar ou recusar, e quando.
**Decisão:** arredonda para o centavo, metade afastando do zero, antes de qualquer regra. A saída mostra o número recebido (`valor_informado`) e o arredondado (`valor_considerado`).
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
**O que não está claro:** quando várias regras incidem na mesma despesa, a ordem muda o resultado (ex.: se uma duplicata ou uma despesa sem nota consome o limite do dia, ou se uma despesa sem nota impede o relançamento com nota).
**Decisão:** ordem da seção 8; a primeira recusa encerra a avaliação da despesa; só despesas que chegam ao limite diário o consomem.
**Justificativa:** despesa recusada não é reembolsável e, portanto, não deve tirar limite de uma despesa válida nem bloquear uma correção.
**Regra afetada:** todas

### AMB-017 — Refeição com cliente (U)

**Texto original do RH:** (não tratado)
**O que não está claro:** d-001 é "Almoco com cliente" (72,50): pode incluir a refeição de outra pessoa; a política não prevê representação nem limite por pessoa.
**Decisão:** é alimentação do colaborador, com o limite diário normal.
**Justificativa:** a entrada não informa número de pessoas nem uma categoria de representação; identificá-las exigiria interpretar a descrição. Fica registrado como evolução recomendada (seção 3).
**Regra afetada:** RN-009

---

## 7. Casos de borda

| Caso | Entrada | Comportamento esperado | Regra |
|---|---|---|---|
| Duas alimentações no mesmo dia somando mais que o limite | 72,50 e 38,00 em 03/07, fora de viagem | 60,00 `parcial` e 0 `recusado` (`limite_diario_excedido`) | RN-009 |
| Valor exatamente no limite de nota | 100,00 sem nota, transporte | não exige nota; limite 80,00 → `parcial` com 80,00 | RN-008, RN-009 |
| Um centavo acima do limite de nota | 100,01 sem nota | `recusado`, `nota_fiscal_ausente` | RN-008 |
| Limite de nota em viagem | transporte 110,00 sem nota em data em viagem | `nota_fiscal_ausente` (o 100,00 não amplia) | RN-008 |
| Valor exatamente no limite diário | alimentação 60,00 | `aprovado` com 60,00 | RN-009 |
| Um centavo acima do limite diário | alimentação 60,01 | `parcial` com 60,00 | RN-009 |
| Primeiro e último dia do período | datas iguais a `inicio` e a `fim` | dentro do período | RN-005 |
| Um dia fora do período | `fim` + 1 dia | `fora_do_periodo` | RN-005 |
| Despesa antiga lançada no período | d-008, data 15/04 num período de julho | `fora_do_periodo` | RN-005 |
| Categoria em maiúsculas | `ALIMENTACAO` | tratada como `alimentacao` | RN-006 |
| Categoria com acento | `alimentação` | tratada como `alimentacao` | RN-006 |
| Categoria com separador diferente | `"Transporte Urbano"`, `"transporte-urbano"` | tratada como `transporte_urbano` | RN-006 |
| Categoria com tabulação no fim | `"alimentacao\t"` | tratada como `alimentacao` | RN-006 |
| Duplicata exata | mesmos data, categoria, fornecedor, valor (≤ 100) | segunda `duplicata` | RN-007 |
| Fornecedor com acento | "Bistro Central" e "Bistrô Central", demais campos iguais | segunda `duplicata` | RN-007 |
| Fornecedor com espaços internos | "Pão  Quente" e "Pao Quente", demais campos iguais | segunda `duplicata` | RN-007 |
| Duplicata de hospedagem só uma com nota | hospedagem 90,00 sem nota e a mesma com nota, mesma data, em qualquer ordem | a com nota é a original e comprova viagem; a sem nota é `duplicata` | RN-007, RN-010 |
| Quase duplicata | mesmo valor, data vizinha ou fornecedor diferente | as duas avaliadas | RN-007 |
| Cópias idênticas sem nota acima de 100 | duas despesas de 150,00 sem nota | as duas `nota_fiscal_ausente` | RN-008, RN-007 |
| Relançamento com nota | 110,00 sem nota e depois o mesmo com nota (ou ordem inversa) | sem nota `nota_fiscal_ausente`; com nota segue avaliada | RN-007, RN-008 |
| Estorno | -45,00 | `valor_invalido`; não altera o dia | RN-004 |
| Valor zero | 0,00 | `valor_invalido` | RN-004 |
| Três casas decimais | 33,333 | `valor_informado` 33.333, `valor_considerado` 33,33 | RN-003 |
| Arredondamento da metade | 10,005 | considerado 10,01 | RN-003 |
| Arredondamento da metade negativa | -0,005 | considerado -0,01; `valor_invalido` | RN-003, RN-004 |
| Hospedagem com várias diárias na descrição | 480,00 "2 diarias", com nota, em 14/07 | 1 diária: `parcial` com 250,00; 14/07 e 15/07 em viagem | RN-012, RN-010 |
| Dia seguinte à diária | hospedagem com nota em 14/07; alimentação 80,00 em 15/07 | 15/07 em viagem: limite 90,00, `aprovado` com 80,00 | RN-010 |
| Dois dias depois da diária | hospedagem com nota em 14/07; alimentação 80,00 em 16/07 | limite 60,00, `parcial` com 60,00 | RN-010 |
| Hospedagem sem nota até 100 | hospedagem 80,00 sem nota em 03/07; alimentação 90,00 em 03/07 | hospedagem `aprovado` com 80,00; 03/07 não fica em viagem; alimentação `parcial` com 60,00 | RN-010 |
| Hospedagem sem nota acima de 100 | 690,00 sem nota | `nota_fiscal_ausente`; data não fica em viagem | RN-008, RN-010 |
| Hospedagem fora do período | hospedagem com nota em 30/06, período desde 01/07 | `fora_do_periodo`; 01/07 não fica em viagem | RN-005, RN-010 |
| Alimentação antes da hospedagem na entrada, mesma data | alimentação 80,00 e depois hospedagem com nota, mesma data | data em viagem: alimentação `aprovado` com 80,00 (limite 90,00) | RN-010 |
| Duas hospedagens na mesma data | 200,00 e 100,00, com nota | 200,00 `aprovado`; 50,00 `parcial` | RN-012, RN-009 |
| Campo obrigatório ausente | despesa sem `tem_nota_fiscal` | `entrada_invalida`, `valor_considerado` nulo, fora dos totais; demais processadas | RN-002 |
| Elemento que não é objeto | `null` dentro de `despesas` | item com `id` e `data` nulos, `entrada_invalida` | RN-002 |
| Campo extra | hospedagem com `"noites": 2` | campo ignorado; uma diária | RN-002, RN-012 |
| Campo com tipo errado | `"id": 17` | `entrada_invalida`; `id` nulo na saída | RN-002 |
| Texto vazio em campo obrigatório | `fornecedor` `""` ou `"   "` | `entrada_invalida` | RN-002 |
| Competência não textual | `competencia` 202607 | processamento normal; `competencia` nula na saída | RN-002 |
| Saída não gravável | caminho de saída em pasta inexistente | erro de arquivo: código diferente de 0 | RN-002 |
| Colaborador ausente | arquivo sem `colaborador` | erro de arquivo: sem saída, código diferente de 0 | RN-002 |
| Colaborador com texto vazio | `colaborador.id` `""` ou `nome` `"  "` | erro de arquivo | RN-002 |
| Saída preexistente com erro | arquivo de saída já existe; entrada sem `colaborador` | erro de arquivo; o arquivo existente não é alterado | RN-002 |
| Erro de uso | chamada sem `--input` ou sem `--output`, ou subcomando diferente de `calcular` | mensagem de erro, código diferente de 0, nenhuma saída | seção 4 |
| Categoria reconhecível em despesa inválida | `"ALIMENTACAO"` sem `tem_nota_fiscal` | `entrada_invalida`; `categoria` `alimentacao` na saída | RN-002, RN-006 |
| Lista de despesas vazia | `despesas: []` | `itens` vazio, totais 0 | RN-001 |
| Despesa em sábado | 18/07 (sábado) | avaliada normalmente | AMB-015 |

## 8. Ordem de aplicação das regras

Cada despesa passa pelas etapas abaixo, nesta ordem. A primeira etapa que a recusa encerra a avaliação dela.

1. **Validação da despesa** — RN-002 (`entrada_invalida`).
2. **Arredondamento** — RN-003.
3. **Valor positivo** — RN-004 (`valor_invalido`).
4. **Período** — RN-005 (`fora_do_periodo`).
5. **Categoria** — RN-006 (`categoria_fora_da_politica`).
6. **Nota fiscal** — RN-008 (`nota_fiscal_ausente`).
7. **Duplicata** — RN-007 (`duplicata`), comparando só despesas que passaram pelas etapas 1 a 6; em cada grupo de duplicatas, a original é a primeira com nota fiscal (ou a primeira na ordem, se nenhuma tem).
8. **Viagem** — RN-010: com todas as despesas já avaliadas pelas etapas 1 a 7, marca as datas em viagem.
9. **Limite diário** — RN-009, por data e categoria, consumindo o limite na ordem da entrada.

Consequências: despesas recusadas nas etapas 1 a 7 não consomem limite; uma despesa sem nota recusada na etapa 6 não impede que o relançamento com nota seja avaliado; uma hospedagem recusada nas etapas 1 a 7, ou sem nota, não caracteriza viagem; a viagem é determinada antes de qualquer limite ser aplicado.

## 9. Critérios de aceite

O sistema está pronto quando:

- [ ] Processa `exemplos/despesas-exemplo.json` e produz exatamente o resultado da tabela abaixo.
- [ ] Cada caso de borda da seção 7 tem um teste automatizado que passa.
- [ ] Cada regra RN-001 a RN-012 tem pelo menos um teste automatizado que a referencia.
- [ ] A mesma entrada sempre produz a mesma saída.
- [ ] Entradas com erro de arquivo (RN-002) e chamadas com erro de uso (seção 4) terminam com código diferente de 0 e não criam nem alteram o arquivo de saída.

**Resultado esperado para `exemplos/despesas-exemplo.json`** (datas em viagem: 14/07 e 15/07, pela hospedagem d-010 com nota):

| id | considerado | em viagem | limite | reembolsado | status | motivo |
|---|---|---|---|---|---|---|
| d-001 | 72,50 | não | 60,00 | 60,00 | parcial | limite_diario_excedido |
| d-002 | 38,00 | não | 60,00 | 0,00 | recusado | limite_diario_excedido |
| d-003 | 100,00 | não | 80,00 | 80,00 | parcial | limite_diario_excedido |
| d-004 | 100,01 | — | — | 0,00 | recusado | nota_fiscal_ausente |
| d-005 | 89,00 | — | — | 0,00 | recusado | categoria_fora_da_politica |
| d-006 | 54,90 | não | 60,00 | 54,90 | aprovado | — |
| d-007 | 54,90 | — | — | 0,00 | recusado | duplicata |
| d-008 | 41,00 | — | — | 0,00 | recusado | fora_do_periodo |
| d-009 | -45,00 | — | — | 0,00 | recusado | valor_invalido |
| d-010 | 480,00 | sim | 250,00 | 250,00 | parcial | limite_diario_excedido |
| d-011 | 33,33 | sim | 90,00 | 33,33 | aprovado | — |
| d-012 | 47,20 | não | 60,00 | 47,20 | aprovado | — |
| d-013 | 690,00 | — | — | 0,00 | recusado | nota_fiscal_ausente |
| d-014 | 61,00 | não | 60,00 | 60,00 | parcial | limite_diario_excedido |

("—" = nulo: o item foi recusado antes do limite diário.)

Totais: `valor_solicitado` = 1.861,84 · `valor_reembolsado` = 585,43 · `valor_glosado` = 1.276,41.

## 10. O que fica em aberto

### Decisões provisórias

- **Datas de entrada e saída de hospedagem.** A solução correta para AMB-005 exige mudar o formato de entrada. Decisão provisória: um lançamento = uma diária. Consequência conhecida: d-010 recebe 250,00 de 480,00 mesmo se forem de fato duas diárias.
- **Ids repetidos na entrada.** A política não trata. Decisão provisória: despesas com o mesmo `id` são avaliadas normalmente, cada uma pelo seu conteúdo; a saída repete o id.
- **`competencia` inconsistente com `inicio`/`fim`.** Decisão provisória: o período vale por `inicio` e `fim`; `competencia` só é repetida na saída.
- **Estorno vinculado a uma despesa.** Se o formato um dia trouxer referência à despesa original, AMB-013 deve ser revista.

### Riscos conhecidos e aceitos

- **Fracionamento para escapar da nota fiscal** (AMB-008): três hospedagens sem nota de 100,00 + 99,99 + 50,01 na mesma data recebem 250,00, enquanto uma de 250,00 sem nota recebe 0. O ganho é limitado aos casos em que o limite diário passa de 100,00 (hospedagem e transporte em viagem). Aceito para não recusar despesas pequenas legítimas sem nota.
- **Viagem por hospedagem irrisória com nota declarada** (AMB-004): uma hospedagem de 0,01 com `tem_nota_fiscal` verdadeiro põe D e D+1 em viagem e amplia os limites de alimentação e transporte em até 70,00 por dia (140,00 nos dois dias). Aceito porque o sistema não verifica notas (seção 3) e qualquer valor mínimo seria regra inventada; a saída expõe `em_viagem` por item para a conferência humana. Mitigação definitiva: indicação explícita de viagem na entrada (evolução, seção 3).
- **Quase-duplicatas** (AMB-010): o mesmo gasto relançado com data vizinha, valor diferente em um centavo ou fornecedor com outra grafia (além do que a normalização da seção 5 cobre) não é detectado. Aceito porque qualquer critério aproximado seria regra inventada e poderia recusar gastos legítimos repetidos.
