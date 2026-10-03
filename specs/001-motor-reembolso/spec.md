# Spec — Motor de Cálculo de Reembolso

**Versão:** 2.0 · **Status:** aprovada para planejamento (Política v4) · **Última alteração:** 2026-10-02 (ver `DECISIONS.md` D-001 a D-007)

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

A partir da Política v4 (D-007), os limites não são mais fixos: vêm de um **arquivo de política** mantido pelo financeiro, com uma tabela por centro de custo e uma tabela padrão. Despesas podem vir em moeda estrangeira e são convertidas para reais pelas taxas de um **arquivo de câmbio**. Os dois arquivos são recebidos a cada execução (seção 4).

## 3. Fora de escopo

- Não aprova, paga nem integra com sistemas de pagamento ou folha: só calcula e justifica.
- Não processa mais de um colaborador ou mais de um período por execução.
- Não verifica a autenticidade da nota fiscal; confia no indicador `tem_nota_fiscal`.
- Não lê nem interpreta o texto livre de `descricao` (nem para contar diárias, AMB-005, nem para identificar refeição com cliente, AMB-017).
- Não consulta câmbio externo: converte moedas só com as taxas do arquivo de câmbio recebido (RN-015).
- Não verifica o centro de custo contra um cadastro de colaboradores: usa o `centro_custo` declarado na entrada (AMB-020, risco na seção 10).
- Não tem fila de aprovação manual (item C da Política v4, opcional): todo item sai com o status da RN-011, sem estado de pendência (AMB-030).
- Não guarda histórico entre execuções: duplicatas só são detectadas dentro da mesma entrada.
- Não usa campos além dos previstos na seção 4; campos extras são ignorados (RN-002). Em particular, não usa datas de entrada e saída de hospedagem: seriam a solução ideal para AMB-005, mas o formato de entrada é fixo. Fica registrado como evolução recomendada.
- Não identifica refeição com cliente pela descrição: uma despesa lançada como `alimentacao` é alimentação do colaborador; `representacao` só existe onde a tabela aplicada a define (AMB-017, RN-014).
- Não recebe indicação explícita de viagem na entrada (ex.: um indicador `em_viagem` ou um código de viagem aprovada): a viagem é inferida da hospedagem (RN-010), nem mesmo da moeda estrangeira (AMB-023). Uma indicação explícita eliminaria a inferência e os riscos registrados na seção 10; fica registrada como evolução recomendada, pois exige mudar o formato fixo.
- Não trata feriados nem fins de semana de forma especial no reembolso (AMB-015); eles só afetam qual cotação de câmbio é usada (AMB-024).

## 4. Entrada e saída

### Interface

`<comando> calcular --input <arquivo de entrada> --politica <arquivo de política> --cambio <arquivo de câmbio> --output <arquivo de saída>`

- Sucesso: grava o arquivo de saída e termina com código 0.
- Erro de arquivo (RN-002 para a entrada, RN-016 para a política e o câmbio), inclusive quando o arquivo de saída não pode ser gravado: não cria nem altera o arquivo de saída (se já existia, permanece como estava), escreve uma mensagem de erro e termina com código diferente de 0.
- Erro de uso (subcomando diferente de `calcular`, `--input`, `--politica`, `--cambio` ou `--output` ausentes): mesmo comportamento do erro de arquivo. Os cinco argumentos são sempre obrigatórios, inclusive quando todas as despesas são em reais (AMB-031).

### Entrada

Formato fixo, conforme `exemplos/despesas-exemplo.json`.

| Campo | Tipo | Significado | Obrigatório |
|---|---|---|---|
| `colaborador.id` | texto | identificador do colaborador | sim (erro de arquivo) |
| `colaborador.nome` | texto | nome | sim (erro de arquivo) |
| `colaborador.centro_custo` | texto ou nulo | centro de custo; escolhe a tabela de limites (RN-014) | não; ausente, nulo, texto vazio ou só com espaços em branco → tabela padrão; qualquer outro tipo → erro de arquivo |
| `periodo.competencia` | texto `AAAA-MM` | rótulo do mês de competência; repetido na saída, não usado em cálculo | não |
| `periodo.inicio` | data `AAAA-MM-DD` | primeiro dia do período (inclusive) | sim (erro de arquivo) |
| `periodo.fim` | data `AAAA-MM-DD` | último dia do período (inclusive) | sim (erro de arquivo) |
| `despesas` | lista | despesas a avaliar (pode ser vazia) | sim (erro de arquivo) |
| `despesas[].id` | texto | identificador da despesa | sim (`entrada_invalida`) |
| `despesas[].data` | data `AAAA-MM-DD` | data em que a despesa ocorreu | sim (`entrada_invalida`) |
| `despesas[].categoria` | texto | categoria da despesa | sim (`entrada_invalida`) |
| `despesas[].descricao` | texto | descrição livre; não usada em regras | não |
| `despesas[].fornecedor` | texto | estabelecimento; usado na detecção de duplicatas | sim (`entrada_invalida`) |
| `despesas[].valor` | número | valor na moeda da despesa | sim (`entrada_invalida`) |
| `despesas[].moeda` | texto ou nulo | código ISO 4217 da moeda do `valor`: exatamente 3 letras maiúsculas de `A` a `Z` (RN-015) | não; ausente ou nulo → `BRL`; outro tipo ou outro formato → `entrada_invalida` |
| `despesas[].tem_nota_fiscal` | booleano | se há nota fiscal | sim (`entrada_invalida`) |

Campos não listados acima são ignorados.

Se um mesmo objeto do arquivo traz a mesma chave mais de uma vez, vale a última ocorrência, e a saída avisa que as anteriores foram descartadas (RN-013).

O arquivo de entrada é lido em UTF-8; uma única marca BOM no início do arquivo é ignorada (uma segunda marca logo em seguida não é ignorada e torna o arquivo JSON inválido). Um byte ou sequência de bytes que não forma UTF-8 válido, em qualquer lugar do arquivo (inclusive um caractere de `U+D800` a `U+DFFF` gravado diretamente em bytes, ou um arquivo em outra codificação, como Latin-1), é erro de arquivo (RN-002).

"JSON válido" é o formato definido na RFC 8259, sem extensões. Em particular, são erro de arquivo (RN-002): caractere de controle (U+0000 a U+001F, como tabulação ou quebra de linha) gravado diretamente dentro de um texto, em vez de escrito como escape (`\t`, `\n`, `\u0000`); `NaN`, `Infinity` e `-Infinity`; número com zero à esquerda (`01.5`), sem dígito antes ou depois do ponto (`.5`, `1.`) ou com sinal `+` (`+1`).

Todo texto da entrada, chave ou valor, vale pelo seu conteúdo **depois de decodificados os escapes** do arquivo (`"2026\u002d07\u002d03"` é a data `2026-07-03`), e "caractere" é o caractere Unicode (um emoji escrito como par de escapes é igual ao mesmo emoji escrito diretamente). Um escape que não forma caractere Unicode válido, em qualquer chave ou valor, é erro de arquivo (RN-002), em qualquer profundidade, inclusive dentro de uma ocorrência descartada por chave repetida (RN-013). Os únicos escapes que não formam caractere válido são os de `\uD800` a `\uDFFF` sem o par correspondente. Par correspondente é exatamente um escape de `\uD800` a `\uDBFF` seguido imediatamente de um escape de `\uDC00` a `\uDFFF`; qualquer outra combinação (ordem invertida, um deles sozinho, um deles seguido de outro caractere) é escape que não forma caractere válido; qualquer outro escape, inclusive de caractere de controle (`\u0000`) ou de não caractere do Unicode (`\uFFFF`), forma um caractere válido.

### Saída

| Campo | Tipo | Significado |
|---|---|---|
| `colaborador` | objeto | `id` e `nome`, copiados da entrada; `centro_custo` copiado se for texto (inclusive só com espaços), nulo se ausente ou nulo |
| `periodo` | objeto | `inicio` e `fim`, copiados da entrada; `competencia` copiada se for texto (em qualquer formato), nula se ausente ou não for texto |
| `politica` | objeto | `versao` e `vigencia`, copiadas do arquivo de política (nulas se ausentes); `tabela_aplicada`: o centro de custo cuja tabela foi usada, como escrito no arquivo de política, ou `padrao` (RN-014) |
| `itens` | lista | um item por elemento de `despesas`, **na mesma ordem** |
| `itens[].id` | texto ou nulo | id da despesa como veio, se for texto; nulo se ausente, se não for texto ou se o elemento não é um objeto |
| `itens[].data` | texto ou nulo | data da despesa como veio, se for texto; nulo se ausente, se não for texto ou se o elemento não é um objeto |
| `itens[].categoria` | texto ou nulo | categoria normalizada (RN-006) se presente na tabela aplicada (inclusive com limite 0), qualquer que seja o status ou o motivo do item (inclusive `entrada_invalida`); senão, como veio, se for texto; nulo se ausente ou não for texto |
| `itens[].valor_informado` | número ou nulo | o número recebido em `valor`, **na moeda da despesa**, sem arredondamento nem conversão; nulo se ausente ou não numérico |
| `itens[].moeda` | texto ou nulo | `BRL` se `moeda` ausente ou nula; como veio, se for texto (mesmo fora do formato); nulo se não for texto nem nula, ou se o elemento não é um objeto |
| `itens[].taxa_cambio` | número ou nulo | taxa usada na conversão (RN-015): 1 para `BRL`; o número do arquivo de câmbio para as demais; **nula se a despesa foi recusada por `entrada_invalida` ou `cambio_indisponivel`** |
| `itens[].data_cotacao` | texto ou nulo | data `AAAA-MM-DD` da cotação usada (pode ser anterior à data da despesa, AMB-024); nula para `BRL` e sempre que `taxa_cambio` é nula |
| `itens[].valor_considerado` | número ou nulo | valor **em reais**: `valor` × `taxa_cambio`, arredondado ao centavo (RN-003, RN-015); **nulo se a despesa foi recusada por `entrada_invalida` ou `cambio_indisponivel`** |
| `itens[].valor_reembolsado` | número | quanto será reembolsado (0 se recusado) |
| `itens[].status` | texto | `aprovado`, `parcial` ou `recusado` (RN-011) |
| `itens[].motivo` | texto ou nulo | código do motivo (tabela abaixo); nulo quando `aprovado` |
| `itens[].em_viagem` | booleano ou nulo | se a data estava em viagem (RN-010); nulo se o item foi recusado antes do limite diário |
| `itens[].limite_diario` | número ou nulo | limite diário aplicado à categoria naquela data; nulo se o item foi recusado antes do limite diário |
| `itens[].justificativa` | texto | frase em português explicando a decisão. Texto livre: **não é contratual**; os demais campos são |
| `itens[].avisos` | lista de textos | avisos de chave repetida dentro da despesa (RN-013); lista vazia se não houver |
| `totais.valor_solicitado` | número | soma de `valor_considerado` dos itens com `valor_considerado` **não nulo e maior que zero** (ficam fora os recusados por `entrada_invalida` ou `cambio_indisponivel`) |
| `totais.valor_reembolsado` | número | soma de `valor_reembolsado` |
| `totais.valor_glosado` | número | `valor_solicitado − valor_reembolsado` |
| `avisos` | lista de textos | avisos de chave repetida fora das despesas (RN-013); lista vazia se não houver |

Todos os valores monetários **calculados** da saída (`valor_considerado`, `valor_reembolsado`, `limite_diario` e totais) são em reais, com no máximo 2 casas decimais e exatos ao centavo. `valor_informado` é a única exceção: é a cópia do número recebido, na moeda da despesa (ex.: 33.333). `taxa_cambio` não é valor monetário: é a cópia do número do arquivo de câmbio, com o valor decimal exato. O arquivo de saída é gravado em UTF-8, com os escapes que o formato exige (uma quebra de linha dentro de um texto sai como `\n`).

Todo número da entrada vale pelo seu **valor decimal exato, como escrito no arquivo**, com qualquer quantidade de dígitos e qualquer expoente, nunca por uma aproximação: é sobre esse valor que se aplicam o teto (RN-002), o arredondamento (RN-003) e a cópia em `valor_informado`. "Como veio" se refere ao valor numérico, não à forma escrita (72.50 e 72.5 são o mesmo valor; 1e999999 pode sair escrito como 1E+999999).

**Códigos de motivo** (na ordem das etapas da seção 8):

| Código | Quando | Status resultante |
|---|---|---|
| `entrada_invalida` | elemento que não é objeto; campo obrigatório ausente ou com tipo/formato errado; `moeda` fora do formato; ou `valor` com valor absoluto a partir de 1.000.000.000,00 (RN-002) | `recusado` |
| `cambio_indisponivel` | moeda diferente de `BRL` sem cotação no arquivo de câmbio na data da despesa nem nos 3 dias anteriores (RN-015) | `recusado` |
| `valor_invalido` | valor considerado menor ou igual a zero (RN-004) | `recusado` |
| `fora_do_periodo` | data fora de `[inicio, fim]` (RN-005) | `recusado` |
| `categoria_fora_da_politica` | categoria ausente da tabela aplicada ou com limite 0 nela (RN-006, RN-014) | `recusado` |
| `nota_fiscal_ausente` | valor em reais acima do mínimo da política (100,00 na v4) sem nota (RN-008) | `recusado` |
| `duplicata` | repete uma despesa anterior (RN-007) | `recusado` |
| `limite_diario_excedido` | o limite diário cortou parte ou todo o valor (RN-009) | `parcial`, ou `recusado` se nada restou |

**Exemplo** (entrada sem centro de custo, com a política `politica-v4.json`, e duas despesas de alimentação em reais no mesmo dia, fora de viagem):

```json
{
  "colaborador": { "id": "c-1", "nome": "Ana", "centro_custo": null },
  "periodo": { "competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31" },
  "politica": { "versao": "v4", "vigencia": "2026-07-01", "tabela_aplicada": "padrao" },
  "itens": [
    { "id": "d-1", "data": "2026-07-03", "categoria": "alimentacao",
      "valor_informado": 45.0, "moeda": "BRL", "taxa_cambio": 1, "data_cotacao": null,
      "valor_considerado": 45.0, "valor_reembolsado": 45.0,
      "status": "aprovado", "motivo": null, "em_viagem": false, "limite_diario": 60.0,
      "justificativa": "Aprovado integralmente: 45,00 dentro do limite diário de 60,00.",
      "avisos": [] },
    { "id": "d-2", "data": "2026-07-03", "categoria": "alimentacao",
      "valor_informado": 30.0, "moeda": "BRL", "taxa_cambio": 1, "data_cotacao": null,
      "valor_considerado": 30.0, "valor_reembolsado": 15.0,
      "status": "parcial", "motivo": "limite_diario_excedido", "em_viagem": false, "limite_diario": 60.0,
      "justificativa": "Parcial: restavam 15,00 do limite diário de 60,00 de alimentação em 03/07.",
      "avisos": [] }
  ],
  "totais": { "valor_solicitado": 75.0, "valor_reembolsado": 60.0, "valor_glosado": 15.0 },
  "avisos": []
}
```

## 5. Regras de negócio

As regras são aplicadas a cada despesa na ordem da seção 8. A primeira regra que recusa uma despesa encerra a avaliação dela: cada despesa recusada tem exatamente um motivo.

**Normalização de texto** (usada em RN-006, RN-007 e na validação de `categoria` e `fornecedor` da RN-002), aplicada nesta ordem:

1. ignorar maiúsculas/minúsculas, pela equivalência completa de caixa do Unicode (inclui `ß` = `ss`); o resultado deste passo é o que os passos seguintes tratam;
2. toda letra com acento ou sinal diacrítico é comparada como a letra base, qualquer que seja a forma como o caractere foi codificado no arquivo (`á`→`a`, `ç`→`c`, `ô`→`o`, `ü`→`u`, `ñ`→`n`). Os sinais são separados pela decomposição canônica do Unicode e todo sinal combinante (caractere da categoria Unicode "marca": sem espaço próprio, com espaço próprio ou envolvente) é descartado, acompanhe ele uma letra ou não; letras sem essa decomposição, cujo traço faz parte da própria letra (`ø`, `ł`, `đ`), ficam como estão;
3. só letras e algarismos decimais contam. Letra é todo caractere da categoria Unicode "letra", de qualquer alfabeto, inclusive `º`, `ª` e letras modificadoras como `ʼ`; algarismo decimal é todo caractere da categoria Unicode "dígito decimal", de qualquer escrita, mantido como está (`١` não vira `1`). Todo outro caractere é separador: espaço em branco de qualquer tipo, hífen, travessão, sublinhado, pontuação, símbolo (inclusive `°`), número que não é dígito decimal (`²`, `½`), emoji, caractere invisível ou de controle. Toda sequência de separadores no início ou no fim é removida, e toda sequência interna vale como um único `_`.

Texto cujo resultado fica vazio (só separadores, como `"-"` ou `"***"`) não identifica categoria nem fornecedor: a despesa é inválida (RN-002).

Exemplos: `"Transporte Urbano"`, `"transporte-urbano"`, `" TRANSPORTE__urbano "` e `"Transporte – Urbano"` (travessão) → `transporte_urbano`; `"Pão  Quente"` e `"pao-quente"` → `pao_quente`; `"-Bistro"`, `"_Bistro"`, `"Bistro -"` e `" -_Bistro"` → `bistro`; `"Padaria (Centro)"` → `padaria_centro`; `"McDonald's"` → `mcdonald_s` (diferente de `mcdonalds`); `"Straße"` → `strasse`; `"Padaria Nº 1"` → `padaria_nº_1` (diferente de `"Padaria N° 1"` → `padaria_n_1`); `"Loja²"` → `loja`; `"Smørrebrød"` → `smørrebrød` (diferente de `smorrebrod`); `"-"` → vazio.

### RN-001 — Um resultado por despesa

**Regra:** a saída tem exatamente um item para cada elemento de `despesas`, na mesma ordem, inclusive os recusados. Os totais seguem as fórmulas da seção 4.
**Origem:** objetivo do sistema ("justifica cada decisão").
**Aceite:** entrada com 14 despesas gera 14 itens, na mesma ordem de ids; `valor_glosado = valor_solicitado − valor_reembolsado`.

### RN-002 — Validação da entrada

**Regra:**
- **Erro de arquivo** (o arquivo de saída não é criado nem alterado): arquivo de entrada ausente, que não está em UTF-8 válido ou que não é JSON válido (seção 4); texto, em chave ou valor, com escape que não forma caractere Unicode válido (seção 4), em qualquer profundidade, inclusive dentro de ocorrência descartada por chave repetida (RN-013); `colaborador` ausente ou sem `id`/`nome` em texto, ou com `id`/`nome` vazio ou só com espaços em branco; `periodo.inicio`, `periodo.fim` ou `despesas` ausentes; `inicio` ou `fim` que não são datas válidas `AAAA-MM-DD`; `inicio` posterior a `fim`; `despesas` que não é lista; `colaborador.centro_custo` presente que não é texto nem nulo (número, booleano, lista, objeto); arquivo de saída que não pode ser gravado. `periodo.competencia` nunca causa erro: se não for texto, sai nula. Erros nos arquivos de política e de câmbio estão na RN-016.
- **Despesa inválida** (vira item `recusado` com motivo `entrada_invalida`; as demais despesas seguem): elemento de `despesas` que não é um objeto; falta `id`, `data`, `categoria`, `fornecedor`, `valor` ou `tem_nota_fiscal`; `data` não é data válida `AAAA-MM-DD`; `valor` não é número; `tem_nota_fiscal` não é booleano; `id`, `categoria` ou `fornecedor` não são texto, ou são texto vazio ou só com espaços em branco; `categoria` ou `fornecedor` cujo texto normalizado (seção 5) fica vazio, como `"-"` ou `"***"`; `moeda` presente e não nula que não é texto de exatamente 3 letras maiúsculas de `A` a `Z`, comparado como veio, sem normalização (`"eur"`, `" EUR"`, `"R$"`, `""`, `978` → inválida; AMB-025); `valor` com valor absoluto maior ou igual a 1.000.000.000,00 (um bilhão), comparado com o número recebido, na moeda da despesa, antes do arredondamento e da conversão (AMB-018, AMB-026).
- Na saída de uma despesa inválida, `id`, `data` e `categoria` são copiados se forem texto e saem nulos caso contrário (tipo errado, ausente ou elemento que não é objeto); a `categoria`, se reconhecida, sai normalizada, como em qualquer item (seção 4).
- Uma despesa recusada por `entrada_invalida` tem `valor_considerado`, `taxa_cambio`, `data_cotacao`, `em_viagem` e `limite_diario` nulos, e não entra nos totais.
- Espaço em branco, nesta regra e em toda a spec, é o caractere com a propriedade White_Space do Unicode (espaço comum, tabulação, quebra de linha, espaço não separável e semelhantes). Tabulação, quebra de linha (LF, CR) e NEL têm essa propriedade e são espaço em branco. Espaço de largura zero, BOM e caracteres de controle sem essa propriedade (como U+001C a U+001F) não são espaço em branco: um `id` ou `nome` feito só deles é texto válido.
- `id` (da despesa e do colaborador) e `nome` não passam pela normalização da seção 5: só são repetidos, nunca comparados. Um `id` `"-"` é válido.
- Campos extras, no arquivo ou nas despesas, são ignorados.
**Origem:** necessidade operacional (a política não trata entrada malformada); pontos 7 e 9 de D-001; AMB-018; D-005; AMB-020 e AMB-025 (D-007).
**Aceite:** despesa sem `tem_nota_fiscal` com `valor` 33.333 → `recusado`, `entrada_invalida`, `valor_informado` 33.333, `valor_considerado` nulo, fora de `valor_solicitado`; as demais despesas são processadas normalmente. Elemento `null` em `despesas` → item com `id` e `data` nulos, `entrada_invalida`. Arquivo sem `colaborador` → nenhuma saída, código diferente de 0. Hospedagem com campo extra `"noites": 2` → avaliada como uma diária (RN-012). Despesa com `"id": 17` → `entrada_invalida`, `id` nulo na saída. Despesa com `fornecedor` `"   "` → `entrada_invalida`. Despesa com `fornecedor` `"-"` → `entrada_invalida`. `competencia` 202607 (número) → processamento normal, `competencia` nula na saída. Caminho de saída em pasta inexistente → nenhuma saída, código diferente de 0. Despesa `"categoria": "ALIMENTACAO"` sem `tem_nota_fiscal` → `entrada_invalida`, `categoria` `alimentacao` na saída. `colaborador.nome` `"  "` → erro de arquivo. Erro de arquivo com arquivo de saída preexistente → o arquivo continua com o conteúdo anterior. Chamada sem `--output` → código diferente de 0. `valor` 1000000000 → `entrada_invalida`, `valor_informado` 1000000000, fora dos totais. `valor` -1e12 → `entrada_invalida` (não `valor_invalido`). `valor` 999999999.995 → segue, com `valor_considerado` 1000000000.00 (o teto vale para o número recebido). `"moeda": "eur"` → `entrada_invalida`, `moeda` `eur` na saída. `"moeda": 978` → `entrada_invalida`, `moeda` nula na saída. `"centro_custo": 17` → erro de arquivo.

### RN-003 — Arredondamento ao centavo

**Regra:** antes de qualquer outra regra de valor, `valor` (pelo seu valor decimal exato, seção 4) é multiplicado pela taxa de câmbio (RN-015; 1 para `BRL`) e o produto exato é arredondado **uma única vez** para 2 casas decimais, com a metade arredondada afastando do zero (0,005 → 0,01; -0,005 → -0,01). O resultado é o `valor_considerado`, em reais. Todas as regras de valor usam o `valor_considerado`, e todos os cálculos são exatos ao centavo. A única exceção é a comparação de duplicatas (RN-007), que usa o `valor` arredondado ao centavo pela mesma regra **na moeda da despesa**, sem conversão.
**Origem:** AMB-014; AMB-026.
**Aceite:** `valor` 33.333 → `valor_considerado` 33.33; `valor` 10.005 → 10.01; `valor` 10.004 → 10.00. 16,8649 EUR com taxa 5,93 → 100,008857 → 100,01 (não 16,86 × 5,93 = 99,98). 0,001 EUR com taxa 5,93 → 0,00593 → 0,01.

### RN-004 — Valor deve ser positivo

**Regra:** despesa com `valor_considerado` (em reais, RN-003) menor ou igual a zero é `recusado` com motivo `valor_invalido`. Ela não abate, não soma nos totais e não consome limite de nenhuma outra despesa.
**Origem:** AMB-013; AMB-026.
**Aceite:** `valor` -45.00 → `recusado`, `valor_invalido`, `valor_reembolsado` 0; demais despesas do mesmo dia não mudam. `valor` 0 → `valor_invalido`. `valor` 0.004 em reais (arredonda para 0,00) → `valor_invalido`. 0,001 EUR com taxa 5,93 → `valor_considerado` 0,01 → não é `valor_invalido`.

### RN-005 — Período de competência

**Regra:** a `data` da despesa precisa estar entre `periodo.inicio` e `periodo.fim`, incluindo os dois extremos. Fora disso: `recusado`, motivo `fora_do_periodo`.
**Origem:** política do RH, item 7; AMB-009.
**Aceite:** período 2026-07-01 a 2026-07-31: data 2026-04-15 → `fora_do_periodo`; datas 2026-07-01 e 2026-07-31 → seguem para as próximas regras.

### RN-006 — Categorias da política

**Regra:** a categoria é comparada depois da normalização de texto (seção 5) com as categorias da **tabela aplicada** ao colaborador (RN-014), também normalizadas. São reconhecidas só as categorias dessa tabela; não há lista fixa. Na saída, categorias reconhecidas aparecem na forma normalizada. Categoria ausente da tabela aplicada → `recusado`, motivo `categoria_fora_da_politica`, mesmo que exista em outra tabela do arquivo ou no `padrao`. Categoria presente na tabela aplicada com limite 0 também → `categoria_fora_da_politica`: a política declara que ela não é reembolsável (AMB-021).
**Origem:** política do RH, item 9; AMB-011; AMB-012; AMB-020 e AMB-021 (D-007).
**Aceite:** com a tabela `padrao` da v4: `ALIMENTACAO`, `" Alimentacao "`, `"alimentacao\t"` e `alimentação` → tratadas como `alimentacao`; `"Transporte Urbano"` e `"transporte-urbano"` → `transporte_urbano`; `coworking` → `categoria_fora_da_politica`; `representacao` → `categoria_fora_da_politica`. Com `CC-COMERCIAL`: `representacao` → reconhecida. Com `CC-ADM`: `hospedagem` → `categoria_fora_da_politica`. Com `CC-ENG-PLATAFORMA`: `hospedagem` (limite 0) → `categoria_fora_da_politica`.

### RN-007 — Duplicatas

**Regra:** duas despesas são duplicatas quando têm a mesma `data`, a mesma categoria normalizada, o mesmo `fornecedor` normalizado (seção 5), a mesma moeda (`BRL` quando ausente ou nula) e o mesmo `valor` arredondado ao centavo **na moeda da despesa** (RN-003; para `BRL`, é o próprio `valor_considerado`). A taxa de câmbio e o valor em reais não entram na comparação: `22,00 EUR` e `22,00 USD` não são duplicatas, e o mesmo gasto lançado uma vez em EUR e outra em BRL também não (AMB-028, risco na seção 10). `id`, `descricao` e `tem_nota_fiscal` não entram na comparação. Só participam da comparação despesas que passaram pelas etapas 1 a 6 da seção 8 (inclusive a nota fiscal): uma despesa recusada antes disso não é "original" de ninguém. Dentro de cada grupo de despesas duplicatas entre si, segue avaliada uma só, a **original**: a primeira na ordem da entrada que tem `tem_nota_fiscal` verdadeiro; se nenhuma do grupo tem, a primeira na ordem da entrada. Todas as outras do grupo são `recusado`, motivo `duplicata`, e não consomem limite nem comprovam viagem. Assim, qual cópia sobrevive não depende da ordem quando só uma delas tem nota. A comparação é exata: datas, valores ou fornecedores diferentes após a normalização não são duplicatas (risco aceito, seção 10).
**Origem:** política do RH, item 8; AMB-010; AMB-028.
**Aceite:** d-006 e d-007 (mesmos data, categoria, fornecedor e valor 54,90, ambas com nota) → d-006 avaliada normalmente, d-007 `duplicata`. 22,00 EUR e 22,00 USD, demais campos iguais → as duas avaliadas. 22.001 EUR e 22.00 EUR, demais campos iguais → a segunda `duplicata`. Táxi de 110,00 sem nota seguido do mesmo táxi com nota → o primeiro `nota_fiscal_ausente`, o segundo segue avaliado (não é duplicata), em qualquer ordem. Hospedagem de 90,00 sem nota e a mesma com nota, em qualquer ordem → a com nota é a original (comprova viagem, RN-010), a sem nota é `duplicata`. "Bistro Central" e "Bistrô Central" → mesmo fornecedor.

### RN-008 — Nota fiscal obrigatória acima do mínimo da política

**Regra:** despesa com `valor_considerado` (em reais) estritamente maior que o mínimo `nota_fiscal_obrigatoria_acima_de` do arquivo de política (100,00 na v4) e `tem_nota_fiscal` falso → `recusado`, motivo `nota_fiscal_ausente`. O mínimo é um só para todos os centros de custo. A comparação usa o valor da despesa individual, convertido em reais, antes de qualquer limite. O mínimo não é ampliado em viagem. A despesa recusada não consome limite, não caracteriza viagem e não participa da comparação de duplicatas.
**Origem:** política do RH, item 5; AMB-007; AMB-008; AMB-027 (D-007).
**Aceite** (mínimo 100,00): 100,00 sem nota → segue; 100,01 sem nota → `nota_fiscal_ausente`; 100,01 com nota → segue; transporte de 110,00 sem nota em data em viagem → `nota_fiscal_ausente`; 40,00 USD sem nota com taxa 5,50 → 220,00 → `nota_fiscal_ausente`.

### RN-009 — Limite diário por categoria

**Regra:** para cada combinação de data e categoria, a soma reembolsada das despesas que chegaram a esta regra não pode passar do limite diário, que vem da **tabela aplicada** ao colaborador (RN-014):

- **Limite normal:** o `limite` da categoria na tabela aplicada.
- **Limite em viagem** (RN-010): só para `alimentacao` e `transporte_urbano`, o limite normal × (1 + `acrescimo_em_viagem_percentual` / 100), **truncado** ao centavo (as casas além da segunda são descartadas, nunca arredondadas para cima: o limite é um teto). Para qualquer outra categoria, inclusive `hospedagem` (AMB-006) e `representacao` (AMB-022), o limite em viagem é igual ao normal.

Com a v4 (acréscimo de 50%), a tabela `padrao` dá:

| Categoria | Limite diário normal | Limite diário em viagem |
|---|---|---|
| `alimentacao` | 60,00 | 90,00 |
| `transporte_urbano` | 80,00 | 120,00 |
| `hospedagem` | 250,00 | 250,00 (não amplia) |

O limite é consumido pelas despesas na ordem da entrada: cada despesa recebe `mínimo(valor_considerado, saldo restante do limite)`. Se recebe o valor inteiro → `aprovado`; se recebe parte → `parcial`, motivo `limite_diario_excedido`; se o saldo já era zero → `recusado`, motivo `limite_diario_excedido`.
**Origem:** política do RH, itens 1, 2, 3 e 4; AMB-001; AMB-002; AMB-003; Política v4, item A; AMB-022 (D-007).
**Aceite** (tabela `padrao` da v4): alimentação, mesmo dia, fora de viagem: 72,50 e depois 38,00 → primeira `parcial` com 60,00, segunda `recusado` com 0. Ordem invertida (38,00 e depois 72,50) → primeira `aprovado` com 38,00, segunda `parcial` com 22,00. `CC-COMERCIAL`: alimentação em viagem → limite 135,00; `representacao` em viagem → limite 300,00. Política com alimentação 33,33 e acréscimo de 50% → limite em viagem 49,99 (49,995 truncado).

### RN-010 — Colaborador em viagem

**Regra:** uma despesa de `hospedagem` **comprova viagem** quando tem `tem_nota_fiscal` verdadeiro e passou pelas etapas 1 a 7 da seção 8. Uma hospedagem que comprova viagem na data D coloca em viagem as datas **D e D+1** (a noite da diária e o dia seguinte). Em datas em viagem, os limites de `alimentacao` e `transporte_urbano` são ampliados pelo percentual da política (RN-009). A condição de viagem vale para todas as despesas da data, independentemente da ordem em que aparecem na entrada. Hospedagem recusada por `categoria_fora_da_politica` (inclusive por limite 0, AMB-021) não comprova viagem. A moeda não importa para a comprovação: uma hospedagem com nota em moeda estrangeira comprova viagem como qualquer outra, e nenhuma outra despesa comprova viagem por estar em moeda estrangeira (AMB-023).
**Origem:** política do RH, item 6; AMB-004; AMB-021 e AMB-023 (D-007).
**Aceite** (tabela `padrao` da v4): hospedagem com nota em 14/07 → 14/07 e 15/07 em viagem; alimentação de 80,00 em 15/07 → limite 90,00, `aprovado` com 80,00; alimentação de 80,00 em 16/07 → limite 60,00, `parcial` com 60,00. Hospedagem de 80,00 **sem** nota em 03/07 → reembolsada pelas regras normais, mas 03/07 e 04/07 **não** ficam em viagem. Hospedagem com nota em 30/06, fora de um período que começa em 01/07 → recusada por `fora_do_periodo`, e 01/07 não fica em viagem. `CC-ENG-PLATAFORMA`: hospedagem com nota em 14/07 → `categoria_fora_da_politica`; alimentação de 100,00 com nota em 15/07 → limite 75,00, `parcial` com 75,00. Alimentação de 22,00 EUR com nota em 14/07, sem hospedagem → 14/07 não fica em viagem.

### RN-011 — Status e justificativa

**Regra:** `aprovado` quando `valor_reembolsado = valor_considerado`; `parcial` quando `0 < valor_reembolsado < valor_considerado`; `recusado` quando `valor_reembolsado = 0`. Todo item `parcial` ou `recusado` tem um `motivo` da tabela da seção 4; todo item tem uma `justificativa` em texto.
**Origem:** objetivo do sistema.
**Aceite:** nenhum item da saída tem status incompatível com os seus valores.

### RN-012 — Hospedagem: um lançamento é uma diária

**Regra:** cada despesa de `hospedagem` é tratada como uma diária na sua `data`, qualquer que seja o valor, a descrição ou campos extras. Várias hospedagens na mesma data dividem o mesmo limite diário da tabela aplicada (RN-009). A `periodicidade` do arquivo de política (`dia` ou `diaria`) não muda o cálculo: as duas significam limite por data (RN-016).
**Origem:** política do RH, item 3; AMB-005.
**Aceite** (tabela `padrao` da v4): hospedagem de 480,00 com nota em 14/07 ("2 diarias" na descrição) → `parcial` com 250,00; 14/07 e 15/07 em viagem (RN-010). `CC-COMERCIAL`: hospedagem de 1.200,00 com nota ("3 noites") → `parcial` com 400,00.

### RN-013 — Chave repetida no arquivo de entrada

**Regra:** quando um objeto do arquivo de entrada traz a mesma chave (igual caractere a caractere) mais de uma vez, vale a **última** ocorrência: as anteriores são descartadas e nenhuma regra as considera. Cada chave repetida gera **um** aviso, qualquer que seja o número de repetições, com o texto exato:

`chave repetida: <caminho> (<n> ocorrências; valeu a última)`

- Chave repetida dentro de um elemento de `despesas`, em qualquer profundidade → aviso em `itens[].avisos` daquele item, com o caminho a partir da despesa (ex.: `valor`, `extra.obs`).
- Qualquer outra → aviso em `avisos` do topo da saída, com o caminho a partir da raiz (ex.: `colaborador.nome`, `periodo.inicio`, `despesas`).
- Caminho: chaves separadas por ponto; elemento de lista indicado pela posição, a partir de 0, entre colchetes (ex.: `extra.lista[0].x`). Se o elemento de `despesas` é uma lista, o caminho começa pela posição (ex.: `[0].a`). Lista dentro de lista: colchetes encadeados, sem ponto entre eles (ex.: `m[0][0].x`, `[0][0].a`). As chaves aparecem no caminho como texto, sem aspas nem escape (risco aceito, seção 10); a gravação do aviso no arquivo de saída segue a seção 4.
- `<n>`: em algarismos, sem separador de milhar (ex.: `1000 ocorrências`).
- Igualdade de chaves: compara o texto **depois** de decodificados os escapes do arquivo (`"\u0076alor"` é a chave `valor`), caractere a caractere, sem normalização Unicode (a forma composta e a decomposta de uma letra acentuada são chaves diferentes). O caminho usa o texto decodificado.
- Ordem dos avisos de cada lista: a ordem em que a primeira ocorrência de cada chave repetida aparece no arquivo.
- Só geram aviso os objetos que continuam no arquivo depois de aplicada a última ocorrência: chaves repetidas dentro de um valor descartado não geram aviso, nem entram no `<n>` nem na ordem de avisos de chaves com o mesmo caminho no valor que valeu.
- O aviso não muda status, motivo nem valores, e aparece em qualquer item, inclusive recusado. Em erro de arquivo não há saída, logo não há aviso.
- O descarte vale para as regras de negócio, não para a forma do arquivo: escape sem caractere válido, byte fora do UTF-8 ou sintaxe que não é JSON válido em qualquer ponto de uma ocorrência descartada, no valor dela ou em qualquer profundidade dentro dele, torna o arquivo inteiro erro de arquivo (seção 4, RN-002). As demais condições da RN-002 (campos ausentes, de tipo errado, vazios, datas inválidas etc.) valem só para o valor que valeu: `"colaborador": {"id": "c-1", "nome": ""}` seguido de `"colaborador": {"id": "c-1", "nome": "Ana"}` é processado normalmente, com `nome` `Ana` e o aviso de `colaborador`.

**Origem:** necessidade operacional (a política não trata o formato do arquivo); AMB-019.
**Aceite:** despesa com `"valor": 30.00` e depois `"valor": 50.00` → avaliada com 50,00; `itens[].avisos` = [`chave repetida: valor (2 ocorrências; valeu a última)`]. `colaborador.nome` repetido → `avisos` do topo = [`chave repetida: colaborador.nome (2 ocorrências; valeu a última)`]; itens sem chave repetida têm `avisos` vazio. Despesa com `"tem_nota_fiscal": true` e depois `"tem_nota_fiscal": "sim"` → `entrada_invalida`, com o aviso de `tem_nota_fiscal`. `despesas` repetida na raiz → só a última lista é avaliada; um aviso `chave repetida: despesas (2 ocorrências; valeu a última)` no topo; chaves repetidas dentro da primeira lista não geram aviso. Chave `valor` três vezes → um aviso, com `3 ocorrências`. Despesa com `"extra": {"x": 1, "x": 2}, "obs": "a", "obs": "b", "extra": {"x": 3, "x": 4}` → avisos, nesta ordem: `extra` (2), `obs` (2), `extra.x` (2). Alimentação fora de viagem com `"valor": 30.00` e depois `"\u0076alor": 90.00` → vale 90,00, `parcial` com 60,00, aviso de `valor`. Despesa com `"obs": "\uD800"` e depois `"obs": "ok"` → erro de arquivo, sem saída; o mesmo com `"extra": {"y": "\uDC00"}` e depois `"extra": {}`.

### RN-014 — Tabela aplicada por centro de custo

**Regra:** cada execução aplica **uma** tabela de limites a todas as despesas, escolhida pelo `colaborador.centro_custo`:
- se o texto de `centro_custo` (informado, ver abaixo) é **igual, caractere a caractere**, a uma chave de `centros_custo` do arquivo de política, aplica-se a tabela desse centro de custo. A comparação é exata: sem normalização, sem ignorar maiúsculas nem espaços (`"cc-adm"` e `"CC-ADM "` não são `CC-ADM`);
- `centro_custo` ausente, nulo, vazio ou só com espaços em branco é "não informado": aplica-se a tabela `padrao`, sem consultar `centros_custo`;
- centro de custo informado que não é chave de `centros_custo` (ou arquivo sem `centros_custo`) → tabela `padrao`.

A tabela aplicada é **fechada**: suas categorias são as únicas reconhecidas (RN-006), seus limites são os únicos usados (RN-009). Uma categoria que falta na tabela de um centro de custo **não** é completada pelo `padrao`. A saída informa a tabela aplicada em `politica.tabela_aplicada` (seção 4).
**Origem:** Política v4, item A ("aplica-se a política padrão"); AMB-020 (D-007).
**Aceite** (`politica-v4.json`): `"CC-COMERCIAL"` → tabela `CC-COMERCIAL`, alimentação 85,00 → limite 90,00, `aprovado`. `"CC-SUPORTE-N2"` → `padrao`, alimentação 65,00 → limite 60,00, `parcial` com 60,00. Sem `centro_custo` → `padrao`. `"cc-adm"` → `padrao` (alimentação 50,00 → limite 60,00, `aprovado`). `"CC-ADM"` com hospedagem de 300,00 com nota → `categoria_fora_da_politica` (não 250,00 do `padrao`).

### RN-015 — Moeda e conversão para reais

**Regra:**
- A moeda da despesa é o campo `moeda`; ausente ou nulo vale `BRL`. Formato inválido é `entrada_invalida` (RN-002).
- `BRL` tem taxa 1, sem consultar o arquivo de câmbio (uma entrada `BRL` no arquivo é ignorada).
- Para outra moeda, a taxa é a do arquivo de câmbio para essa moeda **na data da despesa**. Se essa data não tem cotação para a moeda, usa-se a cotação **dessa moeda** na data anterior mais próxima que a tenha, **até 3 dias corridos antes** (D-1, D-2 ou D-3); uma data intermediária que só cota outras moedas é ignorada: um sábado ou domingo usa a sexta-feira; uma segunda-feira de feriado usa a sexta-feira. Sem cotação de D a D-3 → `recusado`, motivo `cambio_indisponivel`. Cotação posterior à data da despesa nunca é usada.
- Moeda bem formada que não aparece no arquivo de câmbio (inclusive código que não existe na ISO 4217, como `XYZ`) → `cambio_indisponivel`. Não há lista própria de códigos ISO.
- Taxa é "reais por uma unidade da moeda": `valor_considerado` = `valor` × taxa, arredondado uma vez (RN-003).
- Uma despesa recusada por `cambio_indisponivel` tem `valor_considerado`, `taxa_cambio`, `data_cotacao`, `em_viagem` e `limite_diario` nulos, e não entra nos totais.
- A moeda não muda nenhuma outra regra: por si só não caracteriza viagem, nem impede que uma hospedagem com nota a comprove (AMB-023); todos os limites e o mínimo da nota são comparados em reais.

**Origem:** Política v4, item B; AMB-024, AMB-025, AMB-026 (D-007).
**Aceite** (`cambio.json` do envelope): 22,00 EUR em 14/07 → taxa 5,93, `data_cotacao` 2026-07-14, `valor_considerado` 130,46. 30,00 EUR em 18/07 (sábado) → taxa 5,96 de 17/07, `valor_considerado` 178,80. Sem `moeda` → `BRL`, taxa 1, `data_cotacao` nula. `"moeda": null` → `BRL`. 55,00 GBP em 21/07 → `cambio_indisponivel`, `valor_considerado` nulo, fora de `valor_solicitado`. USD em 2026-07-12 (nenhuma cotação de 09/07 a 12/07) → `cambio_indisponivel`. Câmbio só com 13/07: USD em 16/07 → usa 13/07 (D-3); USD em 17/07 → `cambio_indisponivel` (D-4).

### RN-016 — Arquivos de política e de câmbio

**Regra:** os dois arquivos seguem as mesmas regras de forma do arquivo de entrada (seção 4: UTF-8, JSON válido, escapes). Qualquer defeito em qualquer um deles é **erro de arquivo** (sem saída, código diferente de 0), porque nenhum cálculo é confiável com a política ou o câmbio defeituosos. É erro de arquivo:

- arquivo ausente, fora do UTF-8, que não é JSON válido ou com escape sem caractere válido;
- chave repetida em qualquer objeto (a RN-013 vale só para o arquivo de entrada);
- **política:**
  - raiz que não é objeto;
  - `versao` presente que não é texto com algum caractere fora do espaço em branco (só espaços é erro; ausente é válida: sai nula);
  - `vigencia` presente que não é data válida `AAAA-MM-DD` (ausente é válida: sai nula);
  - `moeda_base` presente e diferente de `"BRL"` (ausente vale `BRL`);
  - `padrao` ausente ou que não é tabela;
  - `centros_custo` presente que não é objeto cujos valores são tabelas (ausente: nenhum centro de custo, todos usam o `padrao`); chave de `centros_custo` igual a `"padrao"`, vazia ou só com espaços em branco (nome reservado ou "não informado", RN-014);
  - `nota_fiscal_obrigatoria_acima_de` ausente, que não é número, negativo ou com mais de 2 casas decimais;
  - `acrescimo_em_viagem_percentual` ausente, que não é número ou negativo;
- **tabela** (o `padrao` e cada valor de `centros_custo`): objeto de categoria → regra. É erro de arquivo:
  - nome de categoria cujo texto normalizado (seção 5) fica vazio;
  - duas categorias da mesma tabela com o mesmo texto normalizado;
  - regra que não é objeto;
  - `limite` ausente, que não é número, negativo ou com mais de 2 casas decimais;
  - `periodicidade` ausente ou diferente de `"dia"` e `"diaria"`, que significam a mesma coisa: limite por data;
- **câmbio:**
  - raiz que não é objeto;
  - `moeda_base` presente e diferente de `"BRL"` (ausente vale `BRL`);
  - `taxas` ausente ou que não é objeto;
  - chave de `taxas` que não é data válida `AAAA-MM-DD`;
  - valor de `taxas` que não é objeto;
  - código de moeda que não tem exatamente 3 letras maiúsculas de `A` a `Z`;
  - taxa que não é número ou que é menor ou igual a zero.
- limite, mínimo da nota, percentual ou taxa com valor absoluto a partir de 1.000.000.000 — o mesmo teto da AMB-018.

Nos campos opcionais (`versao`, `vigencia`, `moeda_base`, `centros_custo`), `null` vale como ausente, como `centro_custo` e `moeda` na entrada. A validação vale para todos os campos listados acima, inclusive taxas de moedas que nenhuma despesa usa; a entrada `BRL` do câmbio (RN-015) e os campos não listados são ignorados sem nenhuma validação (`"BRL": 0` ou `"observacao": 1e999999` não são erro).

"Casas decimais" e o teto se medem pelo **valor exato** do número, como na seção 4, não pela forma escrita: `60.000` e `6E1` são 60,00 e valem; `60.005` tem 3 casas e é erro de arquivo.

Campos não listados (`observacao`, `fonte` e outros) são ignorados. Uma tabela vazia é válida: nenhuma categoria é reconhecida para quem a usa. `versao` e `vigencia` não mudam o cálculo: são copiadas para a saída, nulas se ausentes (AMB-029).
**Origem:** Política v4, itens A e B; AMB-029, AMB-031 (D-007).
**Aceite:** política sem `padrao` → erro de arquivo. Limite `"60"` (texto), `-10` ou `60.005` → erro de arquivo; `60.000` → 60,00, válido. Taxa `1e999999` → erro de arquivo. Política sem `versao`, `vigencia`, `moeda_base` e `centros_custo` → válida, todos no `padrao`. `periodicidade` `"mes"` → erro de arquivo. Câmbio com taxa 0 → erro de arquivo. Câmbio com data `"2026-07-32"` → erro de arquivo. Chave `alimentacao` duas vezes na mesma tabela → erro de arquivo. Arquivo de câmbio ausente com todas as despesas em BRL → erro de arquivo. Política com `observacao` numa regra → ignorada.

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
**Decisão:** não; a hospedagem tem sempre o limite da tabela aplicada, sem acréscimo (na v4: 250,00 no `padrao`, 400,00 no `CC-COMERCIAL`).
**Justificativa:** toda hospedagem já é viagem; ampliar o limite dela tornaria o valor da política inalcançável na prática. Mantida na v4 (D-007), que traz o percentual sem dizer a quais categorias se aplica (AMB-022).
**Regra afetada:** RN-009

### AMB-007 — "Acima de R$ 100": exatamente 100,00 exige nota? (F)

**Texto original do RH:** "Nota fiscal é obrigatória acima de R$ 100."
**O que não está claro:** se 100,00 está incluído (d-003 = 100,00 e d-004 = 100,01, ambos sem nota).
**Decisão:** só exige nota quando o valor é estritamente maior que o mínimo. O mínimo não é ampliado em viagem. Na v4, o mínimo vem do arquivo de política (`nota_fiscal_obrigatoria_acima_de`, 100,00) e é comparado em reais (AMB-027).
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
**Decisão:** mesma data, categoria, fornecedor, moeda e valor na moeda da despesa (texto normalizado, comparação exata; moeda desde a v4, AMB-028); a nota fiscal é verificada antes, e só despesas que passaram por ela são comparadas; a original é a primeira com nota fiscal (ou, se nenhuma tem, a primeira na ordem da entrada), e as demais são recusadas com motivo `duplicata`.
**Justificativa:** o id é gerado no lançamento e não identifica o gasto; verificar a nota antes e preferir a cópia com nota tornam o resultado independente da ordem e permitem corrigir uma nota faltante, inclusive abaixo de 100,00, onde a nota importa para comprovar viagem; recusar com motivo explícito deixa visível um eventual gasto legítimo repetido, para o colaborador contestar.
**Regra afetada:** RN-007

### AMB-011 — Categoria com grafia diferente (F)

**Texto original do RH:** (não tratado)
**O que não está claro:** se `ALIMENTACAO` (d-014) é a mesma categoria que `alimentacao`; e uma grafia com acento (`alimentação`).
**Decisão:** normalização completa da seção 5: maiúsculas/minúsculas, qualquer acento ou sinal diacrítico, e só letras e algarismos contam; qualquer outro caractere é separador (removido nas pontas; no meio, cada sequência vale um `_`). A mesma normalização vale para o fornecedor.
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
**Decisão:** arredonda para o centavo, metade afastando do zero, antes de qualquer regra. A saída mostra o número recebido (`valor_informado`) e o arredondado (`valor_considerado`); desde a v4, o arredondado é o valor convertido em reais (AMB-026).
**Justificativa:** reembolso é pago em centavos; arredondar no início garante que todas as regras usem o mesmo valor.
**Regra afetada:** RN-003

### AMB-015 — Despesa em fim de semana (D)

**Texto original do RH:** (não tratado)
**O que não está claro:** d-012 é um almoço de sábado ("plantão"); a política não diz se despesas em fim de semana são aceitas.
**Decisão:** dia da semana não afeta o reembolso. Desde a v4, afeta só qual cotação de câmbio é usada para despesa em moeda estrangeira, porque não há cotação em fim de semana (AMB-024).
**Justificativa:** a política não restringe; criar a restrição seria inventar regra.
**Regra afetada:** nenhuma no reembolso (registrado em Fora de escopo); RN-015 na cotação

### AMB-016 — Em que ordem as regras se aplicam? (U)

**Texto original do RH:** (não tratado)
**O que não está claro:** quando várias regras incidem na mesma despesa, a ordem muda o resultado (ex.: se uma duplicata ou uma despesa sem nota consome o limite do dia, ou se uma despesa sem nota impede o relançamento com nota).
**Decisão:** ordem da seção 8; a primeira recusa encerra a avaliação da despesa; só despesas que chegam ao limite diário o consomem.
**Justificativa:** despesa recusada não é reembolsável e, portanto, não deve tirar limite de uma despesa válida nem bloquear uma correção.
**Regra afetada:** todas

### AMB-017 — Refeição com cliente (U)

**Texto original do RH:** (não tratado)
**O que não está claro:** d-001 é "Almoco com cliente" (72,50): pode incluir a refeição de outra pessoa; a política não prevê representação nem limite por pessoa.
**Decisão:** é alimentação do colaborador, com o limite diário normal. Desde a v4, quem quiser o limite de representação lança a despesa na categoria `representacao`, que só existe onde a tabela aplicada a define (na v4, só no `CC-COMERCIAL`); a descrição continua não sendo lida.
**Justificativa:** a entrada não informa número de pessoas; identificar a refeição com cliente pela descrição seria adivinhar. A categoria explícita da v4 resolve o caso sem interpretar texto livre.
**Regra afetada:** RN-009, RN-006

### AMB-018 — Valor grande demais para ser despesa (F)

**Texto original do RH:** (não tratado)
**O que não está claro:** a entrada não tem limite superior para `valor`; um número como 1e999999 é válido no formato, mas não é uma despesa possível e não pode ser calculado com exatidão ao centavo.
**Decisão:** `valor` com valor absoluto a partir de 1.000.000.000,00, comparado com o número recebido, é `entrada_invalida`, inclusive se negativo.
**Justificativa:** nenhuma despesa corporativa real chega perto de um bilhão, e o teto, junto com o mesmo teto nos números dos arquivos de política e câmbio (RN-016), garante que todo valor aceito é calculado exatamente; recusar com motivo explícito, em vez de interromper a execução, preserva a avaliação das demais despesas.
**Regra afetada:** RN-002

### AMB-019 — Chave repetida num objeto do arquivo (D)

**Texto original do RH:** (não tratado)
**O que não está claro:** o formato de entrada não proíbe que um objeto traga a mesma chave duas vezes (ex.: dois `valor` na mesma despesa); qual delas vale muda o resultado.
**Decisão:** vale a última ocorrência; cada chave repetida gera um aviso na saída (`itens[].avisos` ou `avisos` do topo).
**Justificativa:** a última ocorrência é a leitura mais comum desse tipo de arquivo e corresponde a uma correção feita ao final do registro; descartar em silêncio esconderia do conferente um valor que pode ter mudado o reembolso, por isso o descarte é avisado.
**Regra afetada:** RN-013

**Política v4 (D-007).** As ambiguidades abaixo vêm do comunicado da Política v4 e dos arquivos `politica-v4.json` e `cambio.json` (em `exemplos/envelope/`).

### AMB-020 — "Aplica-se a política padrão": quando, e qual é o padrão? (D, U)

**Texto original do RH:** "Alguns centros de custo não têm entrada na tabela. Nesse caso, aplica-se a política padrão."
**O que não está claro:** se o padrão também completa a categoria que falta num centro de custo que está na tabela (`CC-ADM` não tem `hospedagem`); se uma categoria de outro centro de custo vale para quem caiu no padrão (`representacao` no f-003); se "padrão" é o bloco `padrao` do arquivo ou a política anterior; como comparar o `centro_custo` da entrada com a tabela (`"cc-adm"`); e o que fazer com `centro_custo` ausente, nulo, vazio ou de outro tipo. O campo é declarado pelo próprio colaborador.
**Decisão:** o padrão é o bloco `padrao` do arquivo e vale só quando o centro de custo não está na tabela, inclusive quando `centro_custo` está ausente, nulo ou só com espaços. A tabela aplicada é fechada: categoria que falta nela é `categoria_fora_da_politica`, sem completar pelo padrão. A comparação do centro de custo é exata. `centro_custo` de outro tipo é erro de arquivo. O centro de custo declarado não é verificado (risco na seção 10).
**Justificativa:** o comunicado só manda aplicar o padrão ao centro de custo que "não tem entrada"; o próprio arquivo mostra que o financeiro monta tabelas diferentes de propósito (`CC-ENG-PLATAFORMA` veda hospedagem), então completar com o padrão daria ao `CC-ADM` uma hospedagem que ninguém autorizou. O padrão vem do arquivo para que nenhum limite fique no código. O centro de custo é código de cadastro, não texto livre; um erro de grafia aparece na saída (`politica.tabela_aplicada`) para a conferência. Tipo errado num campo do cabeçalho é arquivo malformado, como em `colaborador.id`.
**Regra afetada:** RN-014, RN-006, RN-002

### AMB-021 — Categoria "não reembolsável de forma alguma" (limite 0) (U)

**Texto original do RH:** "`CC-ENG-PLATAFORMA` não reembolsa `hospedagem` de forma alguma." No arquivo: `"limite": 0.00`, `"observacao": "nao reembolsavel"`.
**O que não está claro:** se é um limite diário 0 (motivo `limite_diario_excedido`, etapa 9) ou uma categoria vedada (`categoria_fora_da_politica`, etapa 5); e, por consequência, se essa hospedagem com nota ainda comprova viagem (RN-010).
**Decisão:** categoria com limite 0 na tabela aplicada é tratada como fora da política: `categoria_fora_da_politica`, na etapa 5. Por isso não comprova viagem.
**Justificativa:** "não reembolsa de forma alguma" é vedar a categoria, não um teto que se esgota; o motivo `limite_diario_excedido` diria ao colaborador que houve excesso. Tratar como limite 0 deixaria uma hospedagem de 0,01 com nota declarada ampliar os limites de dois dias numa categoria que a política proíbe.
**Regra afetada:** RN-006, RN-010

### AMB-022 — O acréscimo em viagem vem do arquivo e vale para quais categorias? (U, F)

**Texto original do RH:** "Colaborador em viagem tem limites ampliados em 50%." No arquivo v4: `"acrescimo_em_viagem_percentual": 50`, sem lista de categorias.
**O que não está claro:** se o percentual do arquivo substitui os valores em viagem escritos na spec; se vale para `representacao` e para categorias que o financeiro venha a criar; e como tratar um limite ampliado que não fecha no centavo (33,33 × 1,5 = 49,995).
**Decisão:** o percentual vem do arquivo; vale só para `alimentacao` e `transporte_urbano`; o limite ampliado é truncado ao centavo.
**Justificativa:** o acréscimo compensa comer e se deslocar fora de casa, que era o sentido da política original; representação já tem limite próprio para um contexto especial, como a hospedagem (AMB-006); estender a ampliação a qualquer categoria nova seria regra que ninguém escreveu. O limite é um teto: truncar garante que o reembolso nunca passa de limite × (1 + percentual), enquanto arredondar poderia pagar meio centavo acima. O truncamento não interfere na nota fiscal, que compara o valor da despesa antes de qualquer limite (AMB-008).
**Regra afetada:** RN-009, RN-010

### AMB-023 — Despesa em moeda estrangeira põe o colaborador em viagem? (D)

**Texto original do RH:** "Colaboradores em viagem internacional lançam despesas em moeda estrangeira."
**O que não está claro:** se a moeda estrangeira é evidência de viagem, como a hospedagem (e-002 a e-005, em Lisboa, não têm hospedagem).
**Decisão:** não; a viagem continua comprovada só por hospedagem com nota (RN-010), em qualquer moeda: uma hospedagem com nota paga em EUR comprova viagem como uma paga em reais.
**Justificativa:** a frase descreve quem lança em moeda estrangeira, não cria regra de viagem. A moeda é declarada pelo colaborador: se ela comprovasse viagem, um almoço de 1 USD ampliaria os limites do dia sem nem exigir nota, brecha maior que a da hospedagem irrisória. Viagem internacional sem hospedagem lançada fica sem ampliação (risco na seção 10).
**Regra afetada:** RN-010

### AMB-024 — "A taxa da data da despesa" quando não há taxa nessa data (D)

**Texto original do RH:** "A conversão usa a taxa da data da despesa, não a taxa de hoje." No arquivo: "Cotações publicadas apenas em dias úteis bancários", de 13/07 a 28/07.
**O que não está claro:** que taxa usar num fim de semana ou feriado (e-004, sábado 18/07), e numa data sem nenhuma cotação próxima no arquivo. A escolha muda a aprovação, não só o valor: 16,70 EUR sem nota num sábado dá 99,53 com a taxa de sexta (não exige nota) e 100,37 com a de segunda (`nota_fiscal_ausente`).
**Decisão:** usa a cotação da moeda na data; sem ela, a da mesma moeda na data anterior mais próxima que a tenha, até 3 dias corridos antes; sem nenhuma, `cambio_indisponivel`. Nunca uma cotação posterior.
**Justificativa:** é a prática da PTAX: a cotação vigente num sábado é a de sexta. A cotação posterior ainda não existia na data da despesa. O limite de 3 dias cobre fim de semana e feriado de segunda ou sexta adjacente; sem limite, uma lacuna de semanas no arquivo passaria em silêncio com uma taxa velha.
**Regra afetada:** RN-015

### AMB-025 — Moeda sem cotação, mal escrita ou nula (D, F)

**Texto original do RH:** "A entrada agora pode trazer um campo `moeda` (ISO 4217). Quando ausente, assume-se BRL."
**O que não está claro:** moeda válida sem taxa no arquivo (e-006, GBP); grafia fora do padrão (`"eur"`, `" EUR "`, `"R$"`, `978`); `"moeda": null`; `BRL`, que não está no arquivo de câmbio.
**Decisão:** 3 letras maiúsculas de `A` a `Z`, comparadas como vieram, ou `entrada_invalida`; nulo vale como ausente (`BRL`); `BRL` tem taxa 1; código bem formado sem cotação → `cambio_indisponivel`, sem verificar a lista ISO.
**Justificativa:** ISO 4217 é sempre 3 letras maiúsculas e o código é comparado exatamente, como o centro de custo (AMB-020). Ao contrário do centro de custo, não há moeda segura para supor quando a grafia está errada, por isso recusa em vez de assumir BRL. Nulo é a forma comum de "não informado". Embutir a lista ISO exigiria mantê-la; o motivo `cambio_indisponivel` é verdadeiro para qualquer código sem taxa.
**Regra afetada:** RN-002, RN-015

### AMB-026 — Arredondar antes ou depois de converter; teto e valor positivo em qual moeda (F)

**Texto original do RH:** "Uma despesa em EUR é convertida antes de ser comparada ao limite." A RN-003 arredondava `valor` "antes de qualquer outra regra".
**O que não está claro:** se o arredondamento acontece na moeda original, em reais, ou nos dois; e se o teto de um bilhão (AMB-018) e o valor positivo (RN-004) usam o número recebido ou o convertido. 16,8649 EUR com taxa 5,93: arredondar antes dá 99,98 (não exige nota); converter antes dá 100,01 (exige).
**Decisão:** converte o valor exato e arredonda uma vez, em reais. O teto compara só o número recebido, na moeda original (etapa 1). O valor positivo usa o valor em reais.
**Justificativa:** todas as regras de valor trabalham em reais; arredondar na moeda original cria um erro que a taxa multiplica. O teto existe para garantir cálculo exato e leitura segura, uma questão da forma do número recebido; um valor convertido acima de um bilhão continua exato e é cortado pelo limite. Para despesa em BRL, nada muda (taxa 1).
**Regra afetada:** RN-003, RN-004, RN-002

### AMB-027 — Mínimo da nota fiscal: de onde vem e em qual moeda se compara (F)

**Texto original do RH:** "Os limites da política são sempre em BRL." No arquivo v4: `"nota_fiscal_obrigatoria_acima_de": 100.00`, no nível de cima.
**O que não está claro:** se o mínimo de 100,00 compara o valor convertido ou o número na moeda original (e-005: 40 USD sem nota = 220,00 BRL); se o mínimo passa a vir do arquivo.
**Decisão:** compara o `valor_considerado` em reais; o mínimo vem do arquivo e é um só para todos os centros de custo.
**Justificativa:** comparar na moeda original faria 99 USD (cerca de 545 BRL) passar sem nota e 101 BRL exigir; o mínimo deixaria de significar a mesma coisa para todos. O valor está no arquivo da política, que é a fonte dos números da política desde a v4.
**Regra afetada:** RN-008

### AMB-028 — Duplicata entre moedas (U)

**Texto original do RH:** "Duplicatas devem ser tratadas." (inalterado na v4)
**O que não está claro:** se a RN-007 compara o valor convertido em reais ou o valor recebido junto com a moeda (22,00 EUR × 22,00 USD; 10,00 EUR × 59,30 BRL do mesmo gasto).
**Decisão:** compara o valor recebido arredondado ao centavo, na moeda da despesa, junto com a moeda.
**Justificativa:** um lançamento repetido repete os números como foram digitados; comparar em reais acoplaria a duplicata ao arquivo de câmbio e poderia recusar gasto legítimo por coincidência de conversão. O mesmo gasto lançado em moedas diferentes não é detectado (risco na seção 10).
**Regra afetada:** RN-007

### AMB-029 — Vigência da política (D)

**Texto original do RH:** "Vigência imediata, retroativa à competência atual." No arquivo: `"vigencia": "2026-07-01"`.
**O que não está claro:** se despesas anteriores à vigência são recusadas, avaliadas por outra política ou avaliadas pela v4; o que é "competência atual".
**Decisão:** a vigência é informativa: copiada para a saída, sem efeito no cálculo; pode faltar no arquivo (sai nula), como a `versao`.
**Justificativa:** cada execução recebe explicitamente o arquivo de política (AMB-031): escolher a política certa para o período é um ato visível de quem executa, registrado na saída. O sistema só conhece uma política por execução; recusar uma despesa anterior à vigência a deixaria sem caminho de reembolso. Aplicar a política fora da vigência é risco aceito (seção 10).
**Regra afetada:** RN-016

### AMB-030 — Fila de aprovação manual (item C, opcional) (U)

**Texto original do RH:** "Itens cujo valor reembolsável passe de R$ 500 não são mais aprovados automaticamente. [...] cada item passa a ter um estado."
**O que não está claro:** a unidade (reembolso do item, valor considerado, dia, período), se o estado é um status novo ou um campo separado, e como entra nos totais.
**Decisão:** não implementado nesta versão (seção 3).
**Justificativa:** o item é opcional no comunicado; com a v4, o maior reembolso possível de um item é 400,00 (hospedagem do `CC-COMERCIAL`, que não amplia em viagem), então a leitura literal nunca dispara; as demais leituras reinterpretam "valor reembolsável". Fica registrado para decisão futura.
**Regra afetada:** nenhuma

### AMB-031 — Como a política e o câmbio chegam à execução (D)

**Texto original do RH:** "O motor precisa ler a política de fora, não de dentro do código." / "As taxas estão em `cambio.json`."
**O que não está claro:** se os arquivos são argumentos, caminhos fixos ou parte da entrada; se o câmbio é exigido quando todas as despesas são em reais; o que fazer com um arquivo defeituoso.
**Decisão:** dois argumentos obrigatórios, `--politica` e `--cambio`, sempre; qualquer defeito em um deles é erro de arquivo (RN-016).
**Justificativa:** tudo o que entra no cálculo aparece na linha de comando, e a mesma linha de comando dá sempre o mesmo resultado (seção 9). Um caminho implícito faria o resultado mudar sem nada visível mudar. Com política ou câmbio defeituosos nenhum cálculo é confiável; recusar despesa por despesa esconderia o defeito atrás de recusas.
**Regra afetada:** seção 4, RN-016

---

## 7. Casos de borda

Salvo indicação na linha, cada caso usa a política `politica-v4.json` e o câmbio `cambio.json` de `exemplos/envelope/`, um colaborador sem `centro_custo` (tabela `padrao`: alimentação 60,00, transporte 80,00, hospedagem 250,00; acréscimo em viagem de 50%) e despesas sem `moeda` (em reais).

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
| Texto vazio em campo obrigatório | `fornecedor` `""`, `"   "` ou `"-"` | `entrada_invalida` | RN-002 |
| Competência não textual | `competencia` 202607 | processamento normal; `competencia` nula na saída | RN-002 |
| Saída não gravável | caminho de saída em pasta inexistente | erro de arquivo: código diferente de 0 | RN-002 |
| Colaborador ausente | arquivo sem `colaborador` | erro de arquivo: sem saída, código diferente de 0 | RN-002 |
| Colaborador com texto vazio | `colaborador.id` `""` ou `nome` `"  "` | erro de arquivo | RN-002 |
| Saída preexistente com erro | arquivo de saída já existe; entrada sem `colaborador` | erro de arquivo; o arquivo existente não é alterado | RN-002 |
| Escape sem caractere válido | `"fornecedor": "X\ud800"` (ou chave `"\ud800"`) | erro de arquivo: sem saída, código diferente de 0 | RN-002 |
| Texto com escapes válidos | `"data": "2026\u002d07\u002d03"` | data `2026-07-03`, válida; avaliada normalmente | RN-002 |
| Erro de uso | chamada sem `--input` ou sem `--output`, ou subcomando diferente de `calcular` | mensagem de erro, código diferente de 0, nenhuma saída | seção 4 |
| Categoria reconhecível em despesa inválida | `"ALIMENTACAO"` sem `tem_nota_fiscal` | `entrada_invalida`; `categoria` `alimentacao` na saída | RN-002, RN-006 |
| Lista de despesas vazia | `despesas: []` | `itens` vazio, totais 0 | RN-001 |
| Valor a partir de um bilhão | `valor` 1000000000 | `entrada_invalida`; `valor_informado` 1000000000; fora dos totais | RN-002 |
| Valor logo abaixo de um bilhão | hospedagem com nota, `valor` 999999999.995 | segue; `valor_considerado` 1000000000.00; `parcial` com 250,00 | RN-002, RN-003 |
| Valor negativo gigante | `valor` -1e12 | `entrada_invalida` (não `valor_invalido`) | RN-002 |
| Valor com expoente enorme | `valor` 1e999999 | `entrada_invalida`; `valor_informado` igual a 10^999999 (pode sair escrito `1E+999999`) | RN-002 |
| Valor minúsculo | `valor` 1e-999999 | `valor_considerado` 0,00; `valor_invalido`; `valor_informado` igual a 10^-999999 | RN-003, RN-004 |
| Muitas casas logo abaixo do teto | hospedagem com nota, `valor` 999999999.99999999999 | abaixo do teto: segue; `valor_considerado` 1000000000.00; `parcial` com 250,00 | RN-002, RN-003 |
| Chave repetida na despesa | `"valor": 30.00` e depois `"valor": 50.00` | avaliada com 50,00; aviso em `itens[].avisos` | RN-013 |
| Chave repetida fora das despesas | `colaborador.nome` duas vezes | vale a última; aviso em `avisos` do topo | RN-013 |
| Chave repetida dentro de valor descartado | `despesas` repetida na raiz | só a última lista é avaliada; um único aviso, `despesas` | RN-013 |
| Mesma chave aninhada no valor descartado e no que valeu | `"extra": {"x":1,"x":2}, "obs":"a", "obs":"b", "extra": {"x":3,"x":4}` | avisos `extra` (2), `obs` (2), `extra.x` (2), nesta ordem | RN-013 |
| Chave repetida escrita com escape | `"valor": 30.00` e `"\u0076alor": 90.00`, alimentação fora de viagem | mesma chave: vale 90,00; `parcial` com 60,00; aviso de `valor` | RN-013, RN-009 |
| Lista dentro de lista no caminho | despesa com `"m": [[{"x": 1, "x": 2}]]` | aviso `chave repetida: m[0][0].x (2 ocorrências; valeu a última)` | RN-013 |
| Chave repetida mil vezes | `obs` 1000 vezes na mesma despesa | um aviso, `chave repetida: obs (1000 ocorrências; valeu a última)` | RN-013 |
| Chave repetida em elemento que é lista | `[{"a": 1, "a": 2}]` como elemento de `despesas` | `entrada_invalida`; aviso `chave repetida: [0].a (2 ocorrências; valeu a última)` | RN-013, RN-002 |
| Despesa em sábado | 18/07 (sábado) | avaliada normalmente | AMB-015 |
| Centro de custo da tabela | `CC-COMERCIAL`, alimentação 85,00 com nota | `tabela_aplicada` `CC-COMERCIAL`; limite 90,00; `aprovado` com 85,00 | RN-014 |
| Centro de custo fora da tabela | `CC-SUPORTE-N2`, alimentação 65,00 | `tabela_aplicada` `padrao`; limite 60,00; `parcial` com 60,00 | RN-014 |
| Centro de custo com grafia diferente | `"cc-adm"`, alimentação 50,00 | não é `CC-ADM`: `padrao`, limite 60,00, `aprovado` com 50,00 | RN-014 |
| Centro de custo só com espaços | `"centro_custo": "  "` | `padrao`; `colaborador.centro_custo` `"  "` na saída | RN-014 |
| Centro de custo de tipo errado | `"centro_custo": 17` | erro de arquivo | RN-002 |
| Categoria ausente da tabela do centro de custo | `CC-ADM`, hospedagem 300,00 com nota em 14/07; alimentação 70,00 em 15/07 | hospedagem `categoria_fora_da_politica`; 15/07 não fica em viagem; alimentação limite 45,00, `parcial` com 45,00 | RN-014, RN-006, RN-010 |
| Categoria com limite zero | `CC-ENG-PLATAFORMA`, hospedagem 480,00 com nota em 14/07; alimentação 100,00 com nota em 15/07 | hospedagem `categoria_fora_da_politica`; 15/07 não fica em viagem; alimentação limite 75,00, `parcial` com 75,00 | RN-006, RN-010 |
| Representação fora do centro de custo que a define | `CC-SUPORTE-N2`, representação 190,00 com nota | `categoria_fora_da_politica` | RN-006, RN-014 |
| Representação não amplia em viagem | `CC-COMERCIAL`, hospedagem com nota em 22/07; representação 400,00 com nota em 23/07 | 23/07 em viagem; representação limite 300,00, `parcial` com 300,00 | RN-009 |
| Limite em viagem truncado | política cujo `padrao` tem alimentação 33,33 e hospedagem 250,00, acréscimo 50; hospedagem com nota em 14/07; alimentação 60,00 em 15/07 | limite 49,99 (49,995 truncado); `parcial` com 49,99 | RN-009 |
| Moeda nula | `"moeda": null`, alimentação 45,00 | como `BRL`: `moeda` `BRL`, `taxa_cambio` 1, `data_cotacao` nula, `aprovado` com 45,00 | RN-015 |
| Moeda estrangeira com cotação | 22,00 EUR em 14/07, alimentação com nota | taxa 5,93, `data_cotacao` 2026-07-14; `valor_considerado` 130,46; `parcial` com 60,00 | RN-015, RN-003 |
| Moeda estrangeira em sábado | 30,00 EUR em 18/07 (sábado), alimentação com nota | taxa 5,96 de 17/07; `data_cotacao` 2026-07-17; `valor_considerado` 178,80 | RN-015 |
| Cotação exatamente 3 dias antes | câmbio só com 13/07 (USD 5,42); 10,00 USD em 16/07 | usa 13/07; `valor_considerado` 54,20 | RN-015 |
| Cotação 4 dias antes | câmbio só com 13/07; 10,00 USD em 17/07 | `cambio_indisponivel`; `valor_considerado` nulo; fora dos totais | RN-015 |
| Moeda sem cotação no arquivo | 55,00 GBP em 21/07 | `cambio_indisponivel`; `moeda` `GBP`; `taxa_cambio` e `valor_considerado` nulos; fora de `valor_solicitado` | RN-015 |
| Moeda em minúsculas | `"moeda": "eur"` | `entrada_invalida`; `moeda` `eur` na saída | RN-002 |
| Moeda de tipo errado | `"moeda": 978` | `entrada_invalida`; `moeda` nula na saída | RN-002 |
| Sem cotação e fora do período | 10,00 USD em 15/04, período de julho | `cambio_indisponivel` (etapa 2 antes da 4) | RN-015 |
| Conversão arredondada uma vez | 16,8649 EUR em 14/07, alimentação sem nota | 100,008857 → `valor_considerado` 100,01 → `nota_fiscal_ausente` | RN-003, RN-008 |
| Nota fiscal comparada em reais | 40,00 USD em 20/07, transporte sem nota | 220,00 → `nota_fiscal_ausente` | RN-008 |
| Valor estrangeiro minúsculo | 0,001 EUR em 14/07, alimentação | `valor_considerado` 0,01; `aprovado` com 0,01 | RN-003, RN-004 |
| Teto na moeda original | 200000000 USD em 14/07, alimentação com nota | abaixo do teto: segue; `valor_considerado` 1088000000,00; `parcial` com 60,00 | RN-002, RN-003 |
| Duplicata em moedas diferentes | 22,00 EUR e 22,00 USD, alimentação com nota, mesmo fornecedor, em 14/07 | as duas avaliadas | RN-007 |
| Duplicata em moeda estrangeira | 22.001 EUR e 22.00 EUR, alimentação com nota, mesmo fornecedor, em 14/07 | segunda `duplicata` | RN-007 |
| Moeda estrangeira não comprova viagem | transporte de 22,00 EUR com nota em 14/07; alimentação 80,00 em BRL em 14/07 | 14/07 fora de viagem; alimentação limite 60,00, `parcial` com 60,00 | RN-010 |
| Hospedagem em moeda estrangeira | hospedagem de 50,00 EUR com nota em 22/07; alimentação 80,00 em BRL em 23/07 | hospedagem 297,50, `parcial` com 250,00; 22/07 e 23/07 em viagem; alimentação limite 90,00, `aprovado` com 80,00 | RN-010, RN-015 |
| Data intermediária sem a moeda | câmbio só com 13/07 (USD 5,42, EUR 5,91) e 14/07 (só USD 5,44); alimentação de 20,00 EUR com nota em 15/07 | usa 13/07: `valor_considerado` 118,20, `data_cotacao` 2026-07-13; `parcial` com 60,00 | RN-015 |
| Centro de custo reservado no arquivo | política com chave `"padrao"` em `centros_custo` | erro de arquivo | RN-016 |
| Política sem versão nem vigência | arquivo de política sem `versao` e sem `vigencia` | processamento normal; `politica.versao` e `politica.vigencia` nulas | RN-016 |
| Política sem tabela padrão | arquivo de política sem `padrao` | erro de arquivo | RN-016 |
| Limite inválido na política | `"limite": -10`, `"60"` ou `60.005` | erro de arquivo | RN-016 |
| Periodicidade desconhecida | `"periodicidade": "mes"` | erro de arquivo | RN-016 |
| Taxa de câmbio não positiva | taxa 0 no arquivo de câmbio | erro de arquivo | RN-016 |
| Chave repetida na política | `alimentacao` duas vezes na mesma tabela | erro de arquivo | RN-016 |
| Câmbio ausente com despesas em reais | `--cambio` aponta arquivo inexistente; todas as despesas em BRL | erro de arquivo | RN-016 |
| Sem argumento de política | chamada sem `--politica` | erro de uso: código diferente de 0, nenhuma saída | seção 4 |

## 8. Ordem de aplicação das regras

Antes das etapas, a leitura verifica a forma do arquivo inteiro, inclusive das ocorrências descartadas (UTF-8, JSON válido e escapes, seção 4), e resolve chaves repetidas pela última ocorrência (RN-013): as demais validações da RN-002 e todas as etapas veem só o valor que valeu.

Os arquivos de política e de câmbio são lidos e validados por inteiro antes de qualquer despesa (RN-016), e a tabela aplicada ao colaborador é escolhida uma vez pelo `centro_custo` (RN-014). Essa tabela decide quais categorias são reconhecidas, inclusive para a saída de uma despesa inválida (seção 4), e os limites da etapa 9.

Cada despesa passa pelas etapas abaixo, nesta ordem. A primeira etapa que a recusa encerra a avaliação dela.

1. **Validação da despesa** — RN-002 (`entrada_invalida`).
2. **Conversão e arredondamento** — RN-015 e RN-003: obtém a taxa (`cambio_indisponivel` se não houver) e calcula o `valor_considerado` em reais.
3. **Valor positivo** — RN-004 (`valor_invalido`).
4. **Período** — RN-005 (`fora_do_periodo`).
5. **Categoria** — RN-006 (`categoria_fora_da_politica`).
6. **Nota fiscal** — RN-008 (`nota_fiscal_ausente`).
7. **Duplicata** — RN-007 (`duplicata`), comparando só despesas que passaram pelas etapas 1 a 6; em cada grupo de duplicatas, a original é a primeira com nota fiscal (ou a primeira na ordem, se nenhuma tem).
8. **Viagem** — RN-010: com todas as despesas já avaliadas pelas etapas 1 a 7, marca as datas em viagem.
9. **Limite diário** — RN-009, por data e categoria, consumindo o limite na ordem da entrada.

Consequências: despesas recusadas nas etapas 1 a 7 não consomem limite; uma despesa sem cotação é recusada na etapa 2, antes de valor positivo, período e categoria, porque sem valor em reais nenhuma regra de valor pode ser avaliada; uma despesa sem nota recusada na etapa 6 não impede que o relançamento com nota seja avaliado; uma hospedagem recusada nas etapas 1 a 7, ou sem nota, não caracteriza viagem; a viagem é determinada antes de qualquer limite ser aplicado.

## 9. Critérios de aceite

O sistema está pronto quando:

- [ ] Processa `exemplos/despesas-exemplo.json` e os dois arquivos de despesas de `exemplos/envelope/`, com `exemplos/envelope/politica-v4.json` e `exemplos/envelope/cambio.json`, e produz exatamente os resultados das tabelas abaixo.
- [ ] Cada caso de borda da seção 7 tem um teste automatizado que passa.
- [ ] Cada regra RN-001 a RN-016 tem pelo menos um teste automatizado que a referencia.
- [ ] A mesma entrada, com a mesma política e o mesmo câmbio, sempre produz a mesma saída.
- [ ] Entradas com erro de arquivo (RN-002, RN-016) e chamadas com erro de uso (seção 4) terminam com código diferente de 0 e não criam nem alteram o arquivo de saída.

Nas tabelas, "—" = nulo: nas colunas de viagem e limite, o item foi recusado antes do limite diário; nas colunas de taxa e data da cotação, o item é em `BRL` (sem data de cotação) ou foi recusado por `cambio_indisponivel`. Itens sem `moeda` saem com `moeda` `BRL`, `taxa_cambio` 1 e `data_cotacao` nula. Nenhum dos três arquivos tem chave repetida: `avisos` vazio em todos os itens e no topo.

### Exemplo: `exemplos/despesas-exemplo.json`

`centro_custo` `CC-ENG-PLATAFORMA` → `tabela_aplicada` `CC-ENG-PLATAFORMA` (alimentação 75,00, em viagem 112,50; transporte 80,00, em viagem 120,00; hospedagem com limite 0, vedada pela AMB-021). Nenhuma data em viagem: a única hospedagem com nota (d-010) é recusada na etapa 5 e não comprova viagem. Todas as despesas em reais.

| id | considerado | em viagem | limite | reembolsado | status | motivo |
|---|---|---|---|---|---|---|
| d-001 | 72,50 | não | 75,00 | 72,50 | aprovado | — |
| d-002 | 38,00 | não | 75,00 | 2,50 | parcial | limite_diario_excedido |
| d-003 | 100,00 | não | 80,00 | 80,00 | parcial | limite_diario_excedido |
| d-004 | 100,01 | — | — | 0,00 | recusado | nota_fiscal_ausente |
| d-005 | 89,00 | — | — | 0,00 | recusado | categoria_fora_da_politica |
| d-006 | 54,90 | não | 75,00 | 54,90 | aprovado | — |
| d-007 | 54,90 | — | — | 0,00 | recusado | duplicata |
| d-008 | 41,00 | — | — | 0,00 | recusado | fora_do_periodo |
| d-009 | -45,00 | — | — | 0,00 | recusado | valor_invalido |
| d-010 | 480,00 | — | — | 0,00 | recusado | categoria_fora_da_politica |
| d-011 | 33,33 | não | 75,00 | 33,33 | aprovado | — |
| d-012 | 47,20 | não | 75,00 | 47,20 | aprovado | — |
| d-013 | 690,00 | — | — | 0,00 | recusado | categoria_fora_da_politica |
| d-014 | 61,00 | não | 75,00 | 61,00 | aprovado | — |

Contas: d-001 + d-002 em 03/07 = 72,50 + 38,00 contra 75,00 → 72,50 e 2,50. d-013 é recusada na etapa 5 (hospedagem vedada) antes da nota (etapa 6).

Totais: `valor_solicitado` = 1.861,84 · `valor_reembolsado` = 351,43 · `valor_glosado` = 1.510,41.

### Envelope: `exemplos/envelope/despesas-envelope.json`

`centro_custo` `CC-COMERCIAL` → `tabela_aplicada` `CC-COMERCIAL` (alimentação 90,00, em viagem 135,00; transporte 150,00, em viagem 225,00; hospedagem 400,00; representação 300,00; as duas últimas não ampliam). Datas em viagem: 22/07 e 23/07, pela hospedagem e-007 com nota.

| id | moeda | taxa | data cotação | considerado | em viagem | limite | reembolsado | status | motivo |
|---|---|---|---|---|---|---|---|---|---|
| e-001 | BRL | 1 | — | 340,00 | não | 300,00 | 300,00 | parcial | limite_diario_excedido |
| e-002 | EUR | 5,93 | 2026-07-14 | 130,46 | não | 90,00 | 90,00 | parcial | limite_diario_excedido |
| e-003 | EUR | 5,88 | 2026-07-15 | 85,26 | não | 90,00 | 85,26 | aprovado | — |
| e-004 | EUR | 5,96 | 2026-07-17 | 178,80 | não | 90,00 | 90,00 | parcial | limite_diario_excedido |
| e-005 | USD | 5,50 | 2026-07-20 | 220,00 | — | — | 0,00 | recusado | nota_fiscal_ausente |
| e-006 | GBP | — | — | — | — | — | 0,00 | recusado | cambio_indisponivel |
| e-007 | BRL | 1 | — | 1.200,00 | sim | 400,00 | 400,00 | parcial | limite_diario_excedido |
| e-008 | BRL | 1 | — | 95,00 | sim | 135,00 | 95,00 | aprovado | — |
| e-009 | BRL | 1 | — | 120,00 | — | — | 0,00 | recusado | categoria_fora_da_politica |
| e-010 | BRL | 1 | — | 88,00 | não | 90,00 | 88,00 | aprovado | — |

Contas: e-002 22,00 × 5,93 = 130,46; e-003 14,50 × 5,88 = 85,26; e-004 é sábado (18/07), sem cotação → 17/07: 30,00 × 5,96 = 178,80; e-005 40,00 × 5,50 = 220,00 > 100,00 sem nota; e-006 GBP não está no câmbio; e-010 não tem `moeda` → BRL.

Totais: `valor_solicitado` = 2.457,52 · `valor_reembolsado` = 1.148,26 · `valor_glosado` = 1.309,26. (`valor_solicitado` não inclui e-006, que não tem valor em reais.)

### Envelope: `exemplos/envelope/despesas-envelope-cc-desconhecido.json`

`centro_custo` `CC-SUPORTE-N2`, ausente da política → `tabela_aplicada` `padrao` (alimentação 60,00, em viagem 90,00; transporte 80,00, em viagem 120,00; hospedagem 250,00). Datas em viagem: 17/07 e 18/07, pela hospedagem f-002 com nota.

| id | moeda | taxa | data cotação | considerado | em viagem | limite | reembolsado | status | motivo |
|---|---|---|---|---|---|---|---|---|---|
| f-001 | BRL | 1 | — | 58,00 | não | 60,00 | 58,00 | aprovado | — |
| f-002 | BRL | 1 | — | 310,00 | sim | 250,00 | 250,00 | parcial | limite_diario_excedido |
| f-003 | BRL | 1 | — | 190,00 | — | — | 0,00 | recusado | categoria_fora_da_politica |
| f-004 | USD | 5,48 | 2026-07-21 | 65,76 | não | 80,00 | 65,76 | aprovado | — |

Contas: f-003 `representacao` não está no `padrao`; f-004 12,00 × 5,48 = 65,76.

Totais: `valor_solicitado` = 623,76 · `valor_reembolsado` = 373,76 · `valor_glosado` = 250,00.

## 10. O que fica em aberto

### Decisões provisórias

- **Datas de entrada e saída de hospedagem.** A solução correta para AMB-005 exige mudar o formato de entrada. Decisão provisória: um lançamento = uma diária. Consequência conhecida: uma hospedagem de 480,00 "2 diarias" recebe 250,00 no `padrao` mesmo se forem de fato duas diárias (no envelope, e-007 "3 noites" recebe 400,00 de 1.200,00).
- **Ids repetidos na entrada.** A política não trata. Decisão provisória: despesas com o mesmo `id` são avaliadas normalmente, cada uma pelo seu conteúdo; a saída repete o id.
- **`competencia` inconsistente com `inicio`/`fim`.** Decisão provisória: o período vale por `inicio` e `fim`; `competencia` só é repetida na saída.
- **Estorno vinculado a uma despesa.** Se o formato um dia trouxer referência à despesa original, AMB-013 deve ser revista.

### Riscos conhecidos e aceitos

- **Fracionamento para escapar da nota fiscal** (AMB-008): três hospedagens sem nota de 100,00 + 99,99 + 50,01 na mesma data recebem 250,00, enquanto uma de 250,00 sem nota recebe 0. O ganho existe em toda categoria cujo limite diário (normal ou em viagem) passa do mínimo da nota; com a v4, além da hospedagem e do transporte em viagem, inclui o transporte do `CC-COMERCIAL` (150,00), a alimentação do `CC-COMERCIAL` em viagem (135,00) e a representação (300,00). Aceito para não recusar despesas pequenas legítimas sem nota.
- **Viagem por hospedagem irrisória com nota declarada** (AMB-004): uma hospedagem de 0,01 com `tem_nota_fiscal` verdadeiro põe D e D+1 em viagem e amplia os limites de alimentação e transporte pelo percentual da política. O ganho depende da tabela aplicada: com a v4, 70,00 por dia no `padrao` e 120,00 por dia no `CC-COMERCIAL` (45,00 + 75,00), o dobro nos dois dias. Num centro de custo com hospedagem vedada, a hospedagem não comprova viagem (AMB-021). Aceito porque o sistema não verifica notas (seção 3) e qualquer valor mínimo seria regra inventada; a saída expõe `em_viagem` por item para a conferência humana. Mitigação definitiva: indicação explícita de viagem na entrada (evolução, seção 3).
- **Limites de aninhamento e de tamanho do arquivo** (seção 4, RN-002): a RFC 8259 permite que a leitura limite a profundidade de aninhamento e o tamanho do arquivo e dos textos. A spec não fixa esses limites: um arquivo com aninhamento muito profundo (milhares de níveis) ou de tamanho exagerado pode ser recusado como erro de arquivo, sem saída, mesmo seguindo a gramática. Aceito porque nenhum arquivo real de despesas chega perto desses limites, e um número fixo seria regra sem origem na política.
- **Caminho ambíguo no aviso de chave repetida** (RN-013): chaves com `.`, `[` ou `]`, vazias ou com quebra de linha aparecem no caminho sem escape. Dois caminhos diferentes podem gerar o mesmo texto (`"a.b"` e `a` → `b`), e um campo extra pode gerar aviso idêntico ao de um campo da seção 4 que entra no cálculo (chave extra `"periodo.inicio"` repetida na raiz produz o mesmo aviso que o `periodo.inicio` verdadeiro repetido) ou um texto que imita outro aviso. Nenhum valor muda: o aviso só pode enganar o conferente sobre qual chave foi descartada. Aceito para manter o aviso legível; na dúvida, o conferente consulta o arquivo de entrada.
- **Letra com traço próprio não vira letra base** (seção 5, passo 2): `ø`, `ł`, `đ` e semelhantes não têm decomposição canônica e ficam como estão, então `"Smørrebrød"` e `"Smorrebrod"` são fornecedores diferentes na RN-007. Aceito porque são raras em dados em português e uma tabela própria de equivalências seria incompleta por construção.
- **Caractere invisível ou letra parecida de outro alfabeto** (seção 5, passo 3): um espaço de largura zero ou um hífen suave dentro da palavra é separador, e uma letra de outro alfabeto parecida com a latina (`о` cirílico) é letra distinta. Na categoria, `"ali\u200bmentacao"` vira `ali_mentacao` e sai `categoria_fora_da_politica`; o conferente vê a categoria como veio. No fornecedor, `"Bistro Cen\u00adtral"` ou `"Bistrо Central"` (com `о` cirílico) não é duplicata de `"Bistro Central"`, e as duas despesas são pagas até o limite do dia, **sem sinal na saída** (o fornecedor não aparece nela). Aceito porque tratar esses caracteres exigiria uma lista própria de equivalências, incompleta por construção; o caso vem de colagem acidental ou de fraude deliberada, que a conferência humana das notas cobre.
- **Classificação do Unicode decide os cantos** (seção 5, RN-002): o resultado segue as categorias e propriedades do Unicode mesmo quando a aparência engana. Uma letra invisível (`ㅤ`, U+3164) conta como letra: `"BistroㅤCentral"` não é duplicata de `"Bistro Central"` e um fornecedor só desse caractere é válido. `º` × `°` e letras modificadoras parecidas com pontuação (`ʼ`, `ˊ`) dão fornecedores diferentes. U+0345 vira `ι` no passo 1 (caixa) e por isso não é descartado no passo 2. Uma versão futura do Unicode pode reclassificar caracteres hoje não atribuídos. Aceito porque nenhum desses casos muda resultado em dados realistas em português, e qualquer exceção exigiria lista própria, incompleta por construção.
- **Formas de compatibilidade distintas da forma comum** (seção 5, passo 2): letras e algarismos em largura total (`ＡＬＩＭＥＮＴＡＣＡＯ`), sobrescritos e ligaduras que a equivalência de caixa não desfaz continuam diferentes da forma comum; uma categoria em largura total sai `categoria_fora_da_politica`. Aceito por ser improvável em dados em português e porque desfazer compatibilidades mudaria também caracteres que a spec não pede (ex.: `²` viraria `2`).
- **Quase-duplicatas** (AMB-010): o mesmo gasto relançado com data vizinha, valor diferente em um centavo ou fornecedor com outra grafia (além do que a normalização da seção 5 cobre) não é detectado. Aceito porque qualquer critério aproximado seria regra inventada e poderia recusar gastos legítimos repetidos.
- **Centro de custo autodeclarado** (AMB-020): o `centro_custo` vem da mesma entrada que o colaborador produz; declarar `CC-COMERCIAL` dá alimentação 90,00, transporte 150,00 e hospedagem 400,00, e escrever `"cc-adm"` em vez de `CC-ADM` troca a tabela pelo `padrao` (mais generosa para o `CC-ADM`). Aceito pelo mesmo motivo do `tem_nota_fiscal`: o sistema não tem cadastro para conferir (seção 3); a saída expõe `colaborador.centro_custo` e `politica.tabela_aplicada` para a conferência humana.
- **Viagem internacional sem hospedagem lançada** (AMB-023): quem está no exterior sem hospedagem na entrada (hotel pago pela empresa por outro meio, por exemplo) não tem os limites ampliados; no envelope, o almoço de Lisboa e-002 recebe 90,00 de 130,46. Aceito porque a moeda é declarada e, como prova de viagem, abriria brecha maior; mitigação definitiva é a indicação explícita de viagem (seção 3).
- **Mesmo gasto lançado em moedas diferentes** (AMB-028): 10,00 EUR e 59,30 BRL do mesmo gasto não são duplicatas e as duas são pagas até o limite do dia. Aceito porque comparar em reais acoplaria a duplicata ao câmbio e só pegaria a conversão manual que batesse ao centavo.
- **Política aplicada fora da vigência** (AMB-029): a execução aplica o arquivo de política recebido a todas as despesas, mesmo às anteriores à `vigencia`. Aceito porque quem executa escolhe a política explicitamente (`--politica`) e a saída registra `politica.versao` e `politica.vigencia`.
- **Cotação de até 3 dias antes** (AMB-024): uma despesa em dia útil cuja cotação falta no arquivo (lacuna do arquivo, não fim de semana) usa a de até 3 dias antes sem aviso, exceto pela `data_cotacao` na saída. Aceito porque o arquivo declara publicar só em dias úteis e a diferença de taxa em 3 dias é pequena; lacunas maiores viram `cambio_indisponivel`.
- **Moeda autodeclarada como multiplicador** (AMB-025): a `moeda` vem da entrada; um gasto de 20,00 reais lançado como `"EUR"` vira 118,60 e recebe até o limite do dia (60,00 no `padrao`). Aceito pelo mesmo motivo do `tem_nota_fiscal` e do `centro_custo`: o sistema não verifica a nota nem lê a descrição (seção 3); a saída expõe `moeda`, `taxa_cambio` e `valor_informado` para a conferência humana comparar com a nota.
- **Categorias reconhecidas pelo nome** (RN-009, RN-010, AMB-022): a ampliação em viagem vale para `alimentacao` e `transporte_urbano`, e só `hospedagem` comprova viagem, pelo nome normalizado. Se o financeiro renomear uma dessas categorias no arquivo de política (ex.: `refeicao`), a ampliação ou a comprovação de viagem some sem aviso. Aceito porque a v4 não marca no arquivo quais categorias ampliam ou comprovam viagem, e inferir isso seria regra inventada; a saída mostra `em_viagem` e `limite_diario` por item.
