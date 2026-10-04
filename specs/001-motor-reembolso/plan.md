# Plano Técnico — Motor de Cálculo de Reembolso

**Versão:** 2.0 · **Baseado na spec:** 2.0 (Política v4, D-007)

> Aqui mora o COMO. Este arquivo pode e deve falar de linguagem, biblioteca e
> arquitetura. O que ele **não** pode é introduzir regra de negócio nova — se
> apareceu uma, ela pertence à `spec.md`.

**O que mudou da 1.2 para a 2.0:** a política deixa de ser constante no código e passa a ser um arquivo lido a cada execução, com uma tabela por centro de custo, e as despesas podem vir em moeda estrangeira, convertidas por um arquivo de câmbio (spec 2.0, RN-014 a RN-016). No plano, isso muda o seguinte:
- a arquitetura ganha `leitura.py` (forma comum aos três arquivos), `cambio.py` e `dinheiro.py` (aritmética exata);
- `politica.py` passa de constantes a leitor e validador do arquivo de política;
- o modelo ganha `Politica`, `Cambio` e os campos novos da saída;
- o motor recebe a tabela aplicada e o câmbio;
- a CLI recebe `--politica` e `--cambio`.

Ficam iguais a stack, a gravação atômica e a serialização determinística. As decisões novas são DT-011 a DT-016. DT-001, DT-002, DT-005, DT-007 e DT-009 foram atualizadas.

---

## 1. Stack

Nenhuma dependência nova na 2.0: política e câmbio são JSON, lidos pelo mesmo `simplejson` estrito da entrada.

| Escolha | O quê | Por quê | O que descartei e por quê |
|---|---|---|---|
| Linguagem | Python ≥ 3.12, projeto gerenciado com `uv` (`pyproject.toml` + `uv.lock`) | `Decimal` e `datetime.date` na biblioteca padrão cobrem dinheiro e datas sem dependência; `uv` fixa a versão do Python (o do sistema é 3.9) e já é o que os hooks de `.githooks/` usam | Node/TypeScript: sem tipo decimal nativo, teria que trazer biblioteca para o ponto mais sensível do projeto |
| Testes | `pytest` | Testes como funções simples, `parametrize` para tabelas de casos (seção 7 da spec), `tmp_path` para a CLI | `unittest`: mais cerimônia por teste, sem ganho |
| Lint | `ruff` (regras `E`, `F`, `I`, `B`, `UP`) | Já exigido pelo `pre-commit`; um só binário para lint e ordenação de imports | `flake8` + `isort`: duas ferramentas para o mesmo papel |
| Parsing/validação | `simplejson` com `use_decimal=True` (leitura e escrita), `object_pairs_hook` para chaves repetidas (DT-010) + validação manual campo a campo, para os três arquivos | Lê `33.333` direto como `Decimal("33.333")`, sem passar por `float`, e escreve `Decimal` como número JSON exato; o hook entrega os pares de cada objeto na ordem do arquivo, inclusive os repetidos (aviso na entrada, erro na política e no câmbio). A validação da entrada precisa produzir **item `entrada_invalida`** por despesa, não exceção — regra fina demais para um validador de schema | `json` da biblioteca padrão: lê com `parse_float=Decimal`, mas não escreve `Decimal` como número — teria que converter para `float` na saída e `valor_informado` perderia dígitos além do 17º. `pydantic`/`jsonschema`: rejeitam o documento inteiro ou exigem contornos para "erro vira item" e para copiar campos de tipo errado como nulo; para política e câmbio, um schema não expressa "casas decimais pelo valor exato", "nomes de categoria distintos depois de normalizar" nem chave repetida |
| Aritmética monetária | `decimal.Decimal`; arredondamento com `quantize(Decimal("0.01"), ROUND_HALF_UP)`; toda conta em contexto exato (DT-012); limite em viagem com `ROUND_DOWN` (DT-013) | Exato ao centavo; `ROUND_HALF_UP` do Python arredonda a metade **afastando do zero** (-0,005 → -0,01), exatamente a RN-003 | `float`: `1.005` é guardado como `1.00499…` e `round(1.005, 2)` dá 1,00 (a RN-003 exige 1,01); `round(0.125, 2)` dá 0,12, porque `round` arredonda a metade para o par. Centavos em `int`: exige arredondar na conversão de qualquer forma, e o número informado (33,333) não cabe em centavos |
| CLI | `argparse` (biblioteca padrão) | Um subcomando, quatro opções obrigatórias; erro de uso já sai com código 2 e mensagem em stderr | `click`/`typer`: dependência a mais para uma interface fixa e mínima |

## 2. Arquitetura

```
entrada  ─┐
política ─┼─▶ cli ─▶ entrada / politica / cambio ─▶ motor ─▶ saida ─▶ cli ─▶ arquivo JSON
câmbio   ─┘  (I/O)   (forma: leitura; conteúdo:     (regras,  (monta     (gravação
                      RN-002/013, RN-016)            puro)     dicionário) atômica)
                                  │                    │
                                  └── normalizacao, politica, cambio, justificativa ──┘
```

| Módulo (`src/reembolso/`) | Responsabilidade | Faz I/O? |
|---|---|---|
| `cli.py` | `argparse`, lê os bytes dos três arquivos, chama o pipeline, grava a saída de forma atômica, mapeia erros para mensagem + código de saída | sim |
| `leitura.py` | **novo.** Forma comum aos três arquivos (seção 4 da spec, RN-016): bytes → JSON estrito com `Decimal` e `ObjetoJson` (DT-002, DT-010), `ErroDeArquivo`, verificação de escapes e os testes de tipo da DT-003 (`e_numero`, `e_data`, `tem_texto`). Sai de `entrada.py`, sem mudar o comportamento (DT-011) | não |
| `entrada.py` | documento → `Entrada`. Resolve chaves repetidas e gera os avisos (RN-013); erros de cabeçalho da RN-002 (inclusive `centro_custo` de tipo errado) viram `ErroDeArquivo`; despesa inválida (inclusive `moeda` mal formada) vira `DespesaInvalida` (etapa 1 da seção 8). **Não conhece a política:** guarda a categoria como veio, e quem decide se ela é reconhecida é o motor (seção 3) | não |
| `politica.py` | documento → `Politica` (RN-016, parte da política); escolha da tabela aplicada (RN-014); limite diário normal e em viagem (RN-009, DT-013); as constantes de interpretação que a spec fixa e o arquivo não traz (seção 4 deste plano) | não |
| `cambio.py` | **novo.** Documento → `Cambio` (RN-016, parte do câmbio); busca da cotação de D a D-3 (RN-015, DT-014) | não |
| `normalizacao.py` | `normalizar_texto()` — os passos da seção 5 da spec | não |
| `dinheiro.py` | **novo.** `contexto_exato()` (DT-012), `arredondar` (RN-003) e `truncar` (RN-009, DT-013): a aritmética de `Decimal` usada pelo motor e pela política, sem regra de negócio além do modo de arredondamento | não |
| `motor.py` | etapas 2 a 9 da seção 8; recebe `Entrada`, `Politica` e `Cambio` e devolve `Resultado` | não |
| `justificativa.py` | frase em português para cada item (texto não contratual) | não |
| `saida.py` | `Resultado` → dicionário na ordem de campos da seção 4 da spec → texto JSON | não |
| `modelo.py` | dataclasses e enums compartilhados (seção 3) | não |

**Fronteiras:** só `cli.py` toca disco, `sys.argv`, `stderr` e código de saída. Todo o resto é função pura de dados para dados, testável sem arquivo. A regra de negócio fica concentrada em `motor.py`, `politica.py`, `cambio.py` e `normalizacao.py`. `entrada.py` só aplica a RN-002 e a RN-013, e `leitura.py` só a forma do arquivo.

Impacto de cada tipo de mudança:
- **Valor da política** (limite, mínimo da nota, percentual, nova categoria ou centro de custo): muda só o arquivo de política, sem código.
- **Interpretação da política** (quais categorias ampliam em viagem, a janela da cotação): muda `politica.py` ou `cambio.py`.
- **Regra:** muda `motor.py`.
- **Formato de entrada ou saída:** muda `entrada.py` ou `saida.py`.

**Ordem de leitura e erros:** a CLI lê os bytes dos três arquivos e valida a política, depois o câmbio e depois a entrada, tudo antes de calcular. Política e câmbio vêm antes porque a seção 8 da spec os valida "antes de qualquer despesa", e `entrada.py` já valida as despesas (etapa 1). A diferença não é observável, já que todo erro encerra a execução sem saída, mas o código fica na ordem da spec. O primeiro erro encerra a execução, com uma mensagem que nomeia o arquivo (DT-007). A spec não fixa qual erro aparece quando há mais de um. Basta que nenhum gere saída.

Comando final: `uv run reembolso calcular --input <entrada> --politica <política> --cambio <câmbio> --output <saída>` (entry point `reembolso = "reembolso.cli:main"` no `pyproject.toml`).

## 3. Modelo de dados

Todas as estruturas são `@dataclass(frozen=True)`; valores monetários e taxas são sempre `Decimal`. Mapeamentos dentro das dataclasses (tabelas, taxas) são montados uma vez na leitura e nunca alterados depois.

```python
class Status(StrEnum):   APROVADO, PARCIAL, RECUSADO
class Motivo(StrEnum):   # na ordem das etapas da seção 8 da spec
    ENTRADA_INVALIDA, CAMBIO_INDISPONIVEL, VALOR_INVALIDO, FORA_DO_PERIODO,
    CATEGORIA_FORA_DA_POLITICA, NOTA_FISCAL_AUSENTE, DUPLICATA, LIMITE_DIARIO_EXCEDIDO

# --- entrada ---
Colaborador(id: str, nome: str, centro_custo: str | None)   # texto como veio, ou None se ausente/nulo
Periodo(inicio: date, fim: date, inicio_texto: str, fim_texto: str, competencia: str | None)

Despesa(                       # passou pela etapa 1 (validação)
    posicao: int,              # índice em `despesas` — ordem da entrada
    id: str, data: date, data_texto: str,
    categoria_texto: str,      # como veio
    categoria: str,            # normalizada (seção 5 da spec)
    fornecedor: str,           # normalizado
    valor_informado: Decimal,  # na moeda da despesa
    moeda: str,                # "BRL" se ausente ou nula; senão 3 letras A–Z
    tem_nota_fiscal: bool,
    avisos: tuple[str, ...],   # RN-013
)
DespesaInvalida(               # recusada na etapa 1
    posicao: int,
    id: str | None, data_texto: str | None,
    categoria_texto: str | None,   # como veio, se texto; o motor decide se sai normalizada
    valor_informado: Decimal | None,
    moeda_saida: str | None,       # "BRL" se ausente/nula; como veio, se texto; senão None
    avisos: tuple[str, ...],
)
Entrada(colaborador, periodo, despesas: list[Despesa | DespesaInvalida],
        avisos: tuple[str, ...])      # chaves repetidas fora das despesas

# --- política e câmbio (RN-014 a RN-016) ---
Tabela = Mapping[str, Decimal]        # categoria normalizada → limite diário normal
Politica(versao: str | None, vigencia: str | None,
         padrao: Tabela, centros_custo: Mapping[str, Tabela],   # chave como escrita no arquivo
         nota_fiscal_acima_de: Decimal, acrescimo_em_viagem_percentual: Decimal)
TabelaAplicada(nome: str, limites: Tabela)   # nome: chave de `centros_custo` ou "padrao"
Cambio(taxas: Mapping[date, Mapping[str, Decimal]])   # sem a entrada "BRL" (ignorada, RN-016)
Cotacao(taxa: Decimal, data: date | None)            # data None para BRL

# --- saída ---
ItemResultado(                 # espelha `itens[]` da seção 4 da spec, campo a campo
    id, data, categoria, valor_informado, moeda, taxa_cambio, data_cotacao,
    valor_considerado, valor_reembolsado,
    status: Status, motivo: Motivo | None, em_viagem: bool | None,
    limite_diario: Decimal | None, justificativa: str, avisos: tuple[str, ...],
)
Totais(valor_solicitado, valor_reembolsado, valor_glosado)
PoliticaAplicada(versao: str | None, vigencia: str | None, tabela_aplicada: str)
Resultado(colaborador, periodo, politica: PoliticaAplicada, itens: list[ItemResultado],
          totais, avisos: tuple[str, ...])
```

A justificativa é gerada a partir dos campos contratuais do item já decidido (status, motivo, valores, limite, data, moeda, taxa), nunca o contrário: nenhuma decisão depende do texto.

**A categoria de saída é decidida no motor, não na entrada.** Na 1.x, `entrada.py` normalizava a categoria de uma despesa inválida comparando com uma lista fixa. Desde a 2.0, "reconhecida" significa "presente na tabela aplicada, inclusive com limite 0" (seção 4 da spec), e a tabela depende do `centro_custo` e do arquivo de política. Por isso `entrada.py` guarda só o texto como veio, e o motor aplica a mesma função (`categoria_de_saida(texto, tabela)`) a todo item, válido ou não. Assim a entrada não depende da política, e a regra da seção 4 fica num lugar só.

## 4. Como a política é representada

Desde a 2.0 (AMB-031), **os números da política vêm do arquivo `--politica`**. `politica.py` não tem mais limites, mínimo da nota nem percentual: lê o arquivo, valida pela RN-016 e devolve uma `Politica` (seção 3). As tabelas são indexadas pela categoria **normalizada**, porque a comparação com a despesa é sempre feita depois da normalização (RN-006). Dois nomes que normalizam igual na mesma tabela são erro de arquivo, então a indexação nunca perde uma regra. Os centros de custo são indexados pela chave **como escrita**, porque a comparação com o `centro_custo` é exata (RN-014).

Ficam em `politica.py` só as constantes de **interpretação**, que a spec fixa e o arquivo não traz:

```python
CATEGORIAS_AMPLIADAS_EM_VIAGEM = frozenset({"alimentacao", "transporte_urbano"})  # RN-009, AMB-006, AMB-022
CATEGORIA_QUE_COMPROVA_VIAGEM = "hospedagem"                  # RN-010
DIAS_EM_VIAGEM_APOS_HOSPEDAGEM = 1                            # RN-010: D e D+1
VALOR_ABSOLUTO_MAXIMO = Decimal("1000000000")                 # RN-002, RN-016, AMB-018 (a partir dele: inválido)
NOME_DA_TABELA_PADRAO = "padrao"                              # RN-014, RN-016
PERIODICIDADES = frozenset({"dia", "diaria"})                 # RN-012, RN-016: as duas = limite por data
MOEDA_BASE = "BRL"                                            # RN-015, RN-016
```

E em `cambio.py`:

```python
DIAS_ANTERIORES_ACEITOS_NA_COTACAO = 3                        # RN-015, AMB-024: D-1 a D-3
```

**Funções** (todas puras):
- `ler_politica(conteudo: bytes) -> Politica`: aplica a parte da RN-016 sobre a política (DT-015).
- `tabela_aplicada(politica, centro_custo) -> TabelaAplicada`: aplica a RN-014. Se `centro_custo` tem texto fora do espaço em branco e é chave exata de `centros_custo`, usa essa tabela; em qualquer outro caso, usa o `padrao`.
- `limite_diario(tabela_aplicada, categoria, em_viagem, percentual) -> Decimal`: aplica a RN-009 com a DT-013.
- `categoria_de_saida(texto, tabela) -> str | None`: aplica a seção 4. Devolve a forma normalizada se ela está na tabela, senão o texto como veio, e `None` se não é texto.
- `ler_cambio(conteudo: bytes) -> Cambio` e `cotacao(cambio, moeda, data) -> Cotacao | None` (em `cambio.py`): aplicam a RN-016 e a RN-015 (DT-014).

**Descartado:**
- **Manter constantes como "padrão de fábrica" e o arquivo como sobrescrita.** Seriam duas fontes da verdade, e a AMB-020 decide que o padrão é o bloco `padrao` do arquivo. Um limite esquecido no código mudaria o resultado sem nada visível mudar (AMB-031).
- **Indexar as tabelas pelo nome como escrito no arquivo.** Obrigaria a normalizar a cada consulta, e dois nomes equivalentes passariam pela validação.
- **Ler a política dentro de `motor.py`.** Misturaria validação de arquivo com regra de reembolso, e o motor deixaria de ser testável com uma `Politica` construída à mão.

## 5. Decisões técnicas

### DT-001 — Dinheiro em `Decimal` lido direto do texto JSON

**Contexto:** RN-003 exige arredondar a metade afastando do zero e cálculos exatos ao centavo; `valor_informado` é o número recebido (33.333), na moeda da despesa.
**Decisão:** os três arquivos são lidos com `simplejson.loads(..., use_decimal=True)`, então todo número com parte decimal chega como `Decimal` construído do texto, ou seja, com o valor decimal exato escrito no arquivo (seção 4 da spec); inteiros também, via `parse_int=Decimal` (evita o limite de 4.300 dígitos na conversão de texto para `int` do Python). `valor` com `abs(valor) >= VALOR_ABSOLUTO_MAXIMO` é `entrada_invalida` (RN-002), e limite, mínimo, percentual ou taxa a partir do mesmo teto é erro de arquivo (RN-016) — comparação exata entre `Decimal`, válida para qualquer expoente. `valor_considerado` = `arredondar(valor_informado × taxa)`, com o produto calculado no contexto exato (DT-012) e `quantize(Decimal("0.01"), ROUND_HALF_UP)`. Toda conta posterior (saldo do limite, totais) também roda no contexto exato. A saída escreve `Decimal` como número JSON (`use_decimal=True`); `taxa_cambio` sai como o `Decimal` lido do câmbio, com o valor exato.
**Alternativa descartada:** `float` com arredondamento no fim (`round(1.005, 2) == 1.0`), e `json` padrão com conversão para `float` só na saída (perde dígitos de `valor_informado`).
**Consequência:** com o teto da RN-002 e da RN-016, todo `valor_considerado` fica abaixo de 10^18 (um bilhão vezes uma taxa abaixo de um bilhão), com até 20 dígitos depois de quantizado. Somas e subtrações rodam no contexto exato da DT-012, então nenhuma conta depende da precisão padrão do `Decimal` (28 dígitos), qualquer que seja o número de despesas. Exige cuidado para nunca misturar `float` (proibido em `motor.py`; um teste de propriedade verifica que nenhum campo monetário da saída é `float`). A forma escrita na saída pode diferir da entrada (`72.50` → `72.5`, ou `45.00` → `45.00`), o que a spec permite (seção 4: "como veio" é o valor numérico).

### DT-002 — Rejeitar o que não é JSON estrito

**Contexto:** RN-002 e RN-016: arquivo que não é JSON válido é erro de arquivo, e os três arquivos seguem as mesmas regras de forma. O `json` da biblioteca padrão aceita `NaN`, `Infinity` e `-Infinity`, que não são JSON.
**Decisão:** vale igual para entrada, política e câmbio, todos lidos pela mesma função de `leitura.py` (DT-011).
- **Valores não JSON:** o `simplejson` ≥ 4 já rejeita `NaN` e `Infinity` na leitura por padrão (`allow_nan=False`). A versão mínima fica fixada no `pyproject.toml`, e um teste garante que `"valor": NaN` é erro de arquivo, para a proteção não sumir numa troca de versão. Erro de parse → `ErroDeArquivo`.
- **Codificação e BOM:** os bytes são decodificados como UTF-8 estrito (`utf-8-sig`, aceitando um BOM, que a RFC 8259 permite ignorar). Falha de decodificação → `ErroDeArquivo`. O `simplejson` também descarta um U+FEFF inicial por conta própria, o que faria dois BOMs passarem; por isso um U+FEFF que sobra depois do `utf-8-sig` → `ErroDeArquivo` (spec 1.9, D-006).
- **Gramática:** caractere de controle cru em texto e números fora da gramática (`01.5`, `.5`, `1.`, `+1`) já são rejeitados pelo parser estrito (`strict=True`, padrão).
- **Aninhamento:** o parser e os percursos são recursivos. Aninhamento além do limite de recursão do Python (~1.000 níveis) levanta `RecursionError`, convertido em `ErroDeArquivo` (risco aceito na seção 10 da spec, D-006).
- **Escapes sem par:** o parser aceita em silêncio um escape `\ud800` sem par, que vira um caractere substituto isolado na `str` e seria recusado depois, na gravação em UTF-8. Por isso, depois do parse, a leitura percorre todas as chaves e textos, inclusive os das ocorrências descartadas por chave repetida (pelos pares guardados no `ObjetoJson`, DT-010; spec 1.9, D-006). Se algum contiver caractere entre U+D800 e U+DFFF, levanta `ErroDeArquivo` (seção 4 da spec). Pares de escapes válidos já chegam combinados num único caractere.

**Alternativa descartada:** aceitar `NaN` e tratar como "valor não é número" na despesa: transformaria arquivo inválido em processamento normal.
**Consequência:** `"valor": NaN` encerra a execução sem saída, como qualquer JSON inválido. O mesmo vale para `"limite": NaN` ou uma taxa `Infinity`.

### DT-003 — Validação de tipo sem as armadilhas do Python

**Contexto:** RN-002 exige `valor` número e `tem_nota_fiscal` booleano; RN-016 exige limite, mínimo, percentual e taxa números e `vigencia` e chaves de `taxas` datas. Em Python, `True` é `int`; `date.fromisoformat` (3.11+) aceita `20260701` e outros formatos ISO; `strptime("%Y-%m-%d")` aceita `2026-7-1`; `\d` casa dígitos não ASCII; `str.isupper()` aceita letras acentuadas.
**Decisão:** os testes de tipo ficam em `leitura.py` e valem para os três arquivos:
- número = `Decimal` ou `int`, **e não** `bool`;
- booleano = `type(x) is bool`;
- data = casa `^[0-9]{4}-[0-9]{2}-[0-9]{2}$` **e** `date.fromisoformat` aceita (rejeita 2026-02-30 e 2026-07-32);
- texto obrigatório = `str` com algum caractere fora do espaço em branco da RN-002 (propriedade White_Space do Unicode). **Não** usar `strip()`/`isspace()` puros: eles também tratam U+001C a U+001F como espaço, e a spec diz que não são; usar `c.isspace() and c not in "\x1c\x1d\x1e\x1f"`;
- código de moeda (`moeda` na entrada, códigos em `taxas`) = `str` que casa `[A-Z]{3}` com `re.fullmatch` (classe com intervalo ASCII explícito; `"EUR\n"` não casa com `fullmatch`, ao contrário de `$`), sem normalização (AMB-025);
- "no máximo 2 casas decimais" (RN-016) = `x == x.quantize(Decimal("0.01"))`, testado **depois** do teto, que garante que o `quantize` cabe na precisão. É comparação pelo valor exato: `60.000` e `6E1` passam, `60.005` e `1E-999999` não.

**Alternativa descartada:** `isinstance(x, (int, float))` e `fromisoformat` sozinho — aceitariam `"valor": true` e `"data": "20260703"`. Contar casas pelo expoente (`as_tuple().exponent >= -2`) recusaria `60.000`, que a spec aceita.
**Consequência:** cada armadilha vira um caso de teste, em `entrada.py` ou nos leitores de política e câmbio.

### DT-004 — Normalização de texto com `unicodedata`

**Contexto:** seção 5 da spec, 3 passos (caixa, acentos, só letras e algarismos), "qualquer que seja a forma como o caractere foi codificado".
**Decisão:** `casefold()` (equivalência completa de caixa, `ß` → `ss`) → `unicodedata.normalize("NFD")` e remoção de todo caractere de categoria `M*` (sinais combinantes, com ou sem letra) → todo caractere que não é de categoria `L*` (letra, inclui `Lm`/`Lo` como `º` e `ʼ`) nem `Nd` (algarismo decimal, sem conversão para ASCII) vira espaço → `"_".join(texto.split())` (pontas somem, sequências internas viram um `_`). O NFD decompõe tanto `á` pré-composto (U+00E1) quanto `a` + acento combinante (U+0301) para a mesma sequência, cobrindo as duas codificações; letras sem decomposição canônica (`ø`, `ł`) ficam como estão, como a spec define. Texto que resulta vazio é tratado pela validação (`entrada.py`, RN-002; `politica.py`, RN-016).
**Alternativa descartada:** tabela manual de acentos (`á→a`, ...): incompleta por construção; `NFKD`: também desfaz compatibilidades (ligaduras, larguras, `²` → `2`) que a spec não pede (seção 10); lista de separadores (`[\s\-_]`): deixa travessões, invisíveis e pontuação sem resultado definido (D-005).
**Consequência:** uma função pura, usada por RN-006, RN-007, pela validação da RN-002 e pela indexação das tabelas da RN-016, testada com os exemplos da seção 5 e os casos de borda de categoria e fornecedor.

### DT-005 — Pipeline em duas fases, espelhando a seção 8

**Contexto:** as etapas 1 a 6 decidem cada despesa isoladamente; as etapas 7 a 9 dependem do conjunto (duplicatas, viagem, saldo do dia). Desde a 2.0, a etapa 2 converte a moeda, e as etapas 5, 6 e 9 consultam a tabela aplicada.
**Decisão:** antes das etapas, o motor escolhe a tabela aplicada uma vez (`tabela_aplicada(politica, colaborador.centro_custo)`, RN-014). Depois:
1. **Fase individual:** para cada despesa, na ordem:
   - **Conversão (etapa 2):** `cotacao(cambio, moeda, data)`. Se não há cotação, recusa com `cambio_indisponivel`. Se há, calcula `valor_considerado = arredondar(valor_informado * taxa)`, com o produto no contexto exato (DT-012).
   - **Verificações (etapas 3 a 6):** aplica uma lista ordenada de verificações (`valor_invalido`, `fora_do_periodo`, `categoria_fora_da_politica`, `nota_fiscal_ausente`), e a primeira recusa encerra. A ordem da lista é a ordem da seção 8. A categoria é recusada se não está na tabela aplicada **ou** se o limite dela é 0 (AMB-021). A nota compara com `politica.nota_fiscal_acima_de`.
2. **Duplicatas:** agrupa as sobreviventes por `(data, categoria, fornecedor, moeda, arredondar(valor_informado))`. O valor é arredondado **na moeda da despesa**, sem a taxa (RN-007, AMB-028). Em cada grupo, a original é a primeira com `tem_nota_fiscal`, ou a primeira por `posicao`; as demais recebem `duplicata`.
3. **Viagem:** `dias_em_viagem` = `{D, D+1}` para cada hospedagem sobrevivente com nota, em qualquer moeda. É calculado **antes** de qualquer limite, então independe da ordem na entrada. A hospedagem vedada ou ausente da tabela já saiu na etapa 5, então não comprova viagem.
4. **Limite:** percorre as sobreviventes por `posicao`, com saldo por `(data, categoria)`. O limite vem de `limite_diario(tabela, categoria, em_viagem, percentual)` (DT-013). Reembolsado = `min(valor_considerado, saldo)`, e o status sai pela RN-011.

Todo item, inclusive o inválido, recebe a categoria de saída de `categoria_de_saida(texto, tabela)` (seção 3). Os totais somam `valor_considerado` só dos itens em que ele não é nulo e é maior que zero. Os nulos são os itens recusados por `entrada_invalida` e por `cambio_indisponivel` (seção 4).

**Alternativa descartada:** uma passada única despesa a despesa: a viagem de uma hospedagem que aparece depois da alimentação do mesmo dia não seria vista (caso de borda "Alimentação antes da hospedagem"). Converter na etapa 1 (`entrada.py`): a entrada passaria a depender do câmbio, e a falta de cotação viraria `entrada_invalida`, que é outro motivo.
**Consequência:** reordenar ou inserir uma etapa individual continua sendo mexer numa lista; a 2.0 insere a conversão na frente dela sem mexer nas demais.

### DT-006 — Gravação atômica da saída

**Contexto:** em erro de arquivo, a saída não pode ser criada nem alterada, inclusive se a falha for na gravação (RN-002, seção 4).
**Decisão:** os três arquivos são lidos e todo o processamento e a serialização acontecem em memória antes de tocar o disco. A gravação escreve num arquivo temporário no **mesmo diretório** da saída e faz `os.replace` para o nome final; em qualquer falha, remove o temporário. Pasta inexistente ou sem permissão falha na criação do temporário, antes de qualquer alteração.
**Alternativa descartada:** `open(output, "w")` direto: trunca o arquivo existente antes de escrever; uma falha no meio deixa arquivo parcial.
**Consequência:** o arquivo de saída ou fica como estava, ou é substituído inteiro.

### DT-007 — Códigos de saída e mensagens

**Contexto:** a spec exige só "código diferente de 0" e "mensagem de erro".
**Decisão:**
- **Códigos:** `0` sucesso; `1` erro de arquivo, em qualquer um dos três arquivos de leitura ou na gravação; `2` erro de uso, inclusive falta de `--politica` ou `--cambio` (padrão do `argparse`).
- **Mensagem:** `erro: <arquivo>: <descrição>` em stderr, onde `<arquivo>` é `entrada`, `política`, `câmbio` ou `saída`, e a descrição diz o campo quando houver (ex.: `erro: política: centros_custo.CC-ADM.alimentacao.limite com mais de 2 casas decimais`). Os leitores levantam `ErroDeArquivo` com a descrição, e a CLI acrescenta o nome do arquivo.
- **Sem stack trace:** nenhuma exceção não tratada chega ao usuário como stack trace por um erro previsto na RN-002 ou na RN-016.

**Alternativa descartada:** um único código para tudo: perderia a distinção útil para scripts, sem custo para cumpri-la. Um código por arquivo: a spec não pede, e scripts que já tratam `1` quebrariam.
**Consequência:** os testes de CLI conferem `!= 0` (contrato) e o código exato (este plano). O texto da mensagem não é testado além do prefixo `erro:` e do nome do arquivo.

### DT-008 — Serialização determinística

**Contexto:** critério de aceite "a mesma entrada, com a mesma política e o mesmo câmbio, sempre produz a mesma saída".
**Decisão:** itens na ordem de `posicao`; campos de cada objeto na ordem da tabela da seção 4 da spec (topo: `colaborador`, `periodo`, `politica`, `itens`, `totais`, `avisos`; item: `id`, `data`, `categoria`, `valor_informado`, `moeda`, `taxa_cambio`, `data_cotacao`, `valor_considerado`, `valor_reembolsado`, `status`, `motivo`, `em_viagem`, `limite_diario`, `justificativa`, `avisos`); `ensure_ascii=False`, UTF-8, `indent=2`, quebra de linha final. Nenhuma decisão depende de ordem de iteração de `set`; agrupamentos usam `dict` (ordem de inserção). A busca da cotação percorre datas por aritmética (`data - timedelta(dias)`), não por iteração sobre as chaves do câmbio.
**Consequência:** saída idêntica byte a byte entre execuções; testável comparando duas execuções.

### DT-009 — Formatação de valores na justificativa

**Contexto:** a justificativa é em português e não contratual (seção 4), mas o exemplo da spec usa `45,00` e `03/07`.
**Decisão:** função própria em `justificativa.py` formata `Decimal` como `1.234,56` e datas como `DD/MM`, sem depender de `locale` do sistema (que mudaria a saída entre máquinas e quebraria a DT-008). Desde a 2.0, `justificar` não importa nada de `politica.py`: o mínimo da nota chega como argumento, vindo da `Politica`. Para despesa em moeda estrangeira, a frase pode citar a conversão (`22,00 EUR × 5,93 = 130,46`). A taxa é formatada com as casas que tiver, sem arredondar, porque não é valor monetário (seção 4).
**Consequência:** os testes conferem que toda justificativa é texto não vazio; o conteúdo exato não é testado, para não transformar texto livre em contrato.

### DT-010 — Chaves repetidas pelo `object_pairs_hook`

**Contexto:** RN-013: na entrada, vale a última ocorrência de uma chave repetida, com aviso de texto fixo, caminho e ordem definidos. RN-016: na política e no câmbio, chave repetida em qualquer objeto é erro de arquivo. Um `dict` comum descarta as ocorrências anteriores sem deixar rastro.
**Decisão:** o `object_pairs_hook` monta cada objeto como `ObjetoJson` (subclasse de `dict`, preenchido pela última ocorrência), que guarda também a lista original de pares.
- **Entrada:** depois do parse, `entrada.py` percorre o documento seguindo essa lista. Ao passar pela **primeira** ocorrência de uma chave repetida, emite o aviso, e desce só no valor da ocorrência que valeu. Assim os avisos saem na ordem do arquivo, e valores descartados nunca são visitados.
- **Caminhos:** o percurso começa em cada elemento de `despesas` com caminho relativo, para os avisos do item. Um elemento que é lista começa por `[i]`, e listas encadeadas viram `[i][j]`. No restante, o caminho parte da raiz, para os avisos do topo.
- **Comparação de chaves:** as chaves comparadas são as `str` já decodificadas pelo parser, sem `unicodedata.normalize` (RN-013). Como o percurso só desce no valor que valeu, ocorrências dentro de valores descartados não entram no `<n>` nem na ordem.
- **Política e câmbio:** `leitura.py` oferece `rejeitar_chaves_repetidas(documento)`, que percorre **todos** os `ObjetoJson` pelos pares e levanta `ErroDeArquivo` na primeira chave que aparece duas vezes no mesmo objeto, com o caminho na mensagem.

**Alternativa descartada:** detectar repetição no texto bruto com expressão regular ou um tokenizador próprio — reescreveria o parser; e `parse` padrão + segunda leitura: duas fontes da verdade para o mesmo arquivo.
**Consequência:** o resto do código vê `dict` comum. A RN-013 fica inteira em `entrada.py`, e a rejeição da RN-016 é uma função de 10 linhas sobre a mesma estrutura, todas testáveis com strings JSON curtas.

### DT-011 — Forma do arquivo num módulo comum (`leitura.py`)

**Contexto:** RN-016: política e câmbio "seguem as mesmas regras de forma do arquivo de entrada" (UTF-8, BOM, JSON estrito, escapes). Na 1.2, tudo isso está em `entrada.py` (`ler_json`, `ObjetoJson`, `ErroDeArquivo`, `_data`, `_tem_texto`, `_numero`), que o plano restringe à RN-002 e à RN-013.
**Decisão:** mover para `leitura.py`, **sem mudar comportamento**, `ler_json`, `ObjetoJson`, `ErroDeArquivo`, a verificação de escapes e os testes de tipo da DT-003 (públicos: `e_numero`, `e_data`, `tem_texto`, `e_codigo_de_moeda`, `tem_ate_2_casas`). `entrada.py`, `politica.py` e `cambio.py` importam de lá. Os testes da forma (`test_leitura_json.py`) passam a importar de `leitura.py`. A mudança é um `refactor` com a suíte verde antes e depois.
**Alternativa descartada:** `politica.py` e `cambio.py` importarem de `entrada.py`: criaria dependência da política para a entrada, e a regra "entrada.py só aplica RN-002 e RN-013" deixaria de ser verdadeira. Duplicar a leitura: três cópias de uma regra que a spec declara única.
**Consequência:** as três leituras ficam iguais por construção. Um único teste por armadilha de forma cobre os três arquivos, e cada leitor só precisa de um teste de integração que mostre que usa `ler_json`.

### DT-012 — Contas monetárias em contexto exato

**Contexto:** RN-003 e AMB-026: o `valor` é multiplicado pela taxa e o **produto exato** é arredondado uma única vez. A precisão padrão do `Decimal` é de 28 dígitos, e um produto com mais dígitos é arredondado **em silêncio**, pela regra do contexto (`ROUND_HALF_EVEN`), antes do `quantize`. Um exemplo verificado: `999999999.99999999999 × 5.123456789123456789` tem 39 dígitos e sai com 28. Um duplo arredondamento pode mudar o centavo. O mesmo vale para a soma: com um percentual de 41 casas, `100 + percentual` sai `100.0000000000000000000000000` (também verificado). E vale para o expoente: `1E-999999 × 5.93` passa do `Emin` padrão e vira subnormal.
**Decisão:** `dinheiro.py` define `contexto_exato()`, um `decimal.localcontext` com `prec = MAX_PREC`, `Emin = MIN_EMIN`, `Emax = MAX_EMAX` e `traps` em `Inexact`, `Rounded` e `InvalidOperation`. **Toda** conta com dinheiro, taxa ou percentual roda dentro dele: a conversão, o limite em viagem (DT-013), o saldo do limite e os totais. Soma, subtração e multiplicação são sempre exatas em decimal; com a precisão máxima, o contexto nunca precisa arredondar, e o `libmpdec` aloca pelo tamanho real do resultado, não pela precisão (os quatro casos acima rodaram em 0,05 ms). Divisão não é usada: dividir por 100 é `scaleb(-2)`. Se alguma conta não for exata, é defeito do código, e a exceção sobe sem ser tratada. `arredondar` e `truncar` fazem o `quantize` dentro do mesmo contexto. Para `BRL`, a taxa é `Decimal(1)`, pelo mesmo caminho, sem ramo especial.
**Alternativa descartada:** um contexto por operação com `prec` = soma dos dígitos dos fatores: resolve o produto, mas a soma precisa de outra conta (a distância entre os expoentes), e cada nova operação viraria um caso a acertar. Mudar o contexto global: afetaria código de terceiros no mesmo processo (testes, `simplejson`). Arredondar `valor` antes de multiplicar: contraria a AMB-026 (16,8649 EUR dá 99,98, não 100,01).
**Consequência:** a conversão é exata para qualquer número aceito. Testes: o caso 16,8649 × 5,93 → 100,01, o caso 0,001 × 5,93 → 0,01, o caso `1E-999999` em EUR → `valor_invalido`, um par de fatores com mais de 28 dígitos no produto e um percentual com mais de 28 casas, conferidos contra a conta feita à mão.

### DT-013 — Limite em viagem: produto exato e truncamento

**Contexto:** RN-009 e AMB-022: o limite em viagem é o limite normal × (1 + percentual / 100), **truncado** ao centavo, e só para `alimentacao` e `transporte_urbano`. O percentual pode ter qualquer número de casas (RN-016 só exige número não negativo abaixo do teto).
**Decisão:** em `politica.py`, `limite_diario` faz o seguinte:
- devolve o limite normal se `em_viagem` é falso ou se a categoria não está em `CATEGORIAS_AMPLIADAS_EM_VIAGEM`;
- senão, calcula `(limite * (100 + percentual)).scaleb(-2)` no contexto exato (DT-012); o `scaleb(-2)` divide por 100 só movendo o expoente;
- aplica `truncar` (`quantize(Decimal("0.01"), ROUND_DOWN)`). Como o limite e o percentual não são negativos, `ROUND_DOWN` (em direção ao zero) é o truncamento da spec.

`contexto_exato`, `arredondar` (RN-003) e `truncar` ficam em `dinheiro.py` (seção 2), usado por `motor.py` e `politica.py`. Se ficassem em `motor.py`, `politica.py` teria de importá-lo, e `motor` já importa `politica`.
**Alternativa descartada:** `ROUND_FLOOR`: igual para não negativos, mas esconde a intenção. Escrever 90,00 e 120,00 por extenso, como na 1.2: os valores agora vêm do arquivo.
**Consequência:** 33,33 com 50% dá 49,99, e 60,00 com 50% dá 90,00, iguais à tabela da RN-009. Os testes de limite da 1.x continuam valendo com a tabela `padrao` da v4.

### DT-014 — Busca da cotação de D a D-3

**Contexto:** RN-015 e AMB-024: a cotação é a da moeda na data da despesa. Se essa data não tem cotação **dessa moeda**, usa-se a data anterior mais próxima que a tenha, até D-3, nunca uma data posterior. `BRL` tem taxa 1 sem consultar o arquivo.
**Decisão:** `cotacao(cambio, moeda, data)` em `cambio.py`:
- se `moeda == MOEDA_BASE`, devolve `Cotacao(Decimal(1), None)`;
- senão, para `dias` de 0 a `DIAS_ANTERIORES_ACEITOS_NA_COTACAO`, calcula `d = data - timedelta(days=dias)` e devolve `Cotacao(taxas[d][moeda], d)` na primeira data em que existe `taxas[d][moeda]`;
- devolve `None` se nenhuma das quatro datas tem a moeda;
- se `data - timedelta` sair do calendário (antes de 0001-01-01), para a busca ali: nenhuma data anterior existe.

**Alternativa descartada:** ordenar as datas do arquivo e procurar a anterior mais próxima com busca binária: mais código para o mesmo resultado com, no máximo, 4 consultas a dicionário. E a janela fixa deixa explícito o "até 3 dias".
**Consequência:** uma data intermediária que só cota outras moedas é pulada naturalmente (caso de borda "Data intermediária sem a moeda"). `data_cotacao` sai de `Cotacao.data.isoformat()`, que é igual ao texto do arquivo, porque a chave foi validada como `AAAA-MM-DD` com dígitos ASCII (DT-003).

### DT-015 — Validação dos arquivos de política e câmbio

**Contexto:** RN-016 lista os defeitos que são erro de arquivo. Qualquer um encerra a execução.
**Decisão:** `ler_politica` e `ler_cambio` recebem os bytes, como `ler_entrada`, passam por `leitura.ler_json` e chamam `rejeitar_chaves_repetidas` (DT-010). Depois validam campo a campo, **na ordem da lista da RN-016**, e levantam `ErroDeArquivo` no primeiro defeito, com o caminho do campo na mensagem (DT-007).

Regras de implementação que a RN-016 deixa implícitas:
- **Campos opcionais** (`versao`, `vigencia`, `moeda_base`, `centros_custo`): `raiz.get(campo) is None` cobre ausente e `null`, que valem a mesma coisa.
- **`moeda_base`:** presente tem de ser exatamente a `str` `"BRL"`. `"brl"` e `1` são erro.
- **Tabela:** é um objeto (`dict`). Cada nome de categoria é normalizado (`normalizar_texto`). Nome vazio depois da normalização, ou repetido entre nomes normalizados da mesma tabela, é erro. Cada regra é objeto com `limite` (número, ≥ 0, abaixo do teto, até 2 casas) e `periodicidade` em `PERIODICIDADES`. Os demais campos da regra são ignorados sem validação.
- **Chaves de `centros_custo`:** `"padrao"`, texto vazio ou só com espaço em branco (`not tem_texto(chave)`) são erro. Qualquer outro texto é aceito como está.
- **Números:** a ordem dos testes é tipo → sinal → teto → casas, para que o `quantize` do teste de casas só rode em número abaixo do teto (DT-003). O mínimo da nota tem o mesmo teste do limite. O percentual não tem limite de casas. A taxa precisa ser maior que 0.
- **Câmbio:** a chave `"BRL"` dentro de uma data é pulada **antes** de qualquer validação (`"BRL": 0` não é erro). As demais chaves precisam ser código de moeda (DT-003). Campos da raiz fora de `moeda_base` e `taxas` são ignorados.
- **`-0`:** como limite, mínimo ou percentual, vale 0, porque `Decimal("-0") < 0` é falso. Um limite `-0` é uma categoria vedada (AMB-021). A spec trata o número pelo valor, e o valor é zero.

**Alternativa descartada:** acumular todos os defeitos e listar de uma vez: a spec só exige que haja erro, e listar tudo exigiria decidir como continuar depois de um tipo errado.
**Consequência:** cada linha da RN-016 vira pelo menos um teste de `ErroDeArquivo`, em `tests/test_rn016_arquivos_de_politica_e_cambio.py`.

### DT-016 — Rastreabilidade com pendências durante a Fase 5

**Contexto:** desde a spec 2.0, `test_rastreabilidade.py` falha: a RN-014 a RN-016 e 37 casos da seção 7 ainda não têm teste (D-007). O `pre-commit` roda a suíte inteira, então **todo** commit `feat(T-NNN)` da Fase 5 seria bloqueado até a última task, e o fluxo de um commit por task deixaria de funcionar.
**Decisão:** a primeira task da Fase 5 cria em `test_rastreabilidade.py` um registro explícito e **estrito** de pendências:

```python
PENDENTES = {            # some quando a Fase 5 terminar (DT-016)
    "RN-014": "T-0NN",
    "Centro de custo da tabela": "T-0NN",
    ...
}
```

- Uma regra ou caso **sem** teste só é aceito se estiver em `PENDENTES`.
- Uma pendência que **já tem** teste faz a suíte falhar, como um `xfail(strict=True)`. Assim, a task que escreve o teste é obrigada a tirar a pendência no mesmo commit.
- Uma pendência que não está mais na spec também faz a suíte falhar.
- A última task da Fase 5 apaga `PENDENTES` e o código que o lê, e a rastreabilidade volta a ser a da 1.x.

**Alternativa descartada:**
- **`SEM_PYTEST` ou `--no-verify` nos commits:** perderia a proteção do hook justamente nas tasks que mudam regra.
- **Escrever de uma vez os testes dos 37 casos, marcados `xfail`:** os esperados seriam escritos antes do desenho de cada task, e a revisão por task perderia o foco.
- **Uma única task com toda a v4:** um commit gigante, sem revisão por regra.

**Consequência:** a suíte fica verde em todo commit da Fase 5. O dono de cada pendência fica visível no código, e uma pendência esquecida ou já resolvida quebra a suíte. A tabela de Cobertura do `tasks.md` é preenchida pela mesma lista.

## 6. Estratégia de testes

- **Nível e proporção:**
  - **Unitários (~70%)** — `normalizacao`; `leitura` (cada armadilha de forma e de tipo, DT-002 e DT-003); `entrada` (cada item da RN-002, inclusive `moeda` e `centro_custo`); `politica` e `cambio` (cada linha da RN-016, escolha da tabela, limite em viagem, busca da cotação), com documentos JSON curtos e sem disco; `motor` (uma regra por arquivo), com `Politica` e `Cambio` construídos.
  - **Integração (~20%)** — `entrada → motor → saida` com os **três** arquivos da seção 9 da spec (`exemplos/despesas-exemplo.json`, `exemplos/envelope/despesas-envelope.json`, `exemplos/envelope/despesas-envelope-cc-desconhecido.json`), com `politica-v4.json` e `cambio.json`. As três tabelas da seção 9 e seus totais são transcritos à mão para o teste, nunca copiados da saída do programa.
  - **Ponta a ponta (~10%)** — `cli.main([...])` com `tmp_path`: código de saída, arquivo criado, arquivo preexistente intacto em erro de qualquer um dos três arquivos de leitura, erro de uso (inclusive sem `--politica` ou `--cambio`), pasta inexistente, determinismo byte a byte.
- **Cada `RN-NNN` da spec tem teste?** Um arquivo por regra (`tests/test_rn001_um_resultado_por_despesa.py`, …, `test_rn014_tabela_aplicada.py`, `test_rn015_moeda_e_cambio.py`, `test_rn016_arquivos_de_politica_e_cambio.py`), cobrindo pelo menos o **Aceite** da regra. `tests/test_rastreabilidade.py` lê a `spec.md`, extrai todos os `RN-NNN` e falha se algum não aparecer no nome ou na docstring de pelo menos um teste (com as pendências da DT-016 durante a Fase 5).
- **Casos de borda da seção 7 da spec:** `tests/test_casos_de_borda.py`, um teste parametrizado por linha da tabela, com `id` igual ao texto da coluna "Caso". `test_rastreabilidade.py` também extrai a coluna "Caso" da seção 7 e falha se algum caso não tiver teste com esse `id` — caso novo na spec sem teste quebra a suíte.
- **Nomenclatura:** `test_rnNNN_<comportamento>` com docstring `"""RN-NNN / AMB-NNN: <o que a spec diz>"""`; o esperado de cada teste tem um comentário com a conta feita a partir da spec (ex.: `# 22,00 × 5,93 = 130,46 > 60,00 → 60,00`). O nome remete à regra; a docstring, à decisão.
- **Fixtures** (`tests/conftest.py`):
  - **Entrada:** os construtores `entrada(...)` e `despesa(**campos)` continuam, e `entrada` ganha `centro_custo`.
  - **Política e câmbio:** construtores novos `construir_politica(**sobrescritas)` e `construir_cambio(taxas=...)` geram documentos válidos. O padrão de cada um é o conteúdo de `exemplos/envelope/politica-v4.json` e `cambio.json` **transcrito** no `conftest.py`, não lido do disco, para um teste de regra não mudar se alguém editar o exemplo.
  - **Pipeline:** `processar(texto_json, politica=None, cambio=None)` usa a v4 e o câmbio do envelope quando não recebe outros. Por isso os testes da 1.x, que não definem centro de custo nem moeda, continuam válidos sem mudança: a tabela `padrao` da v4 tem os mesmos valores da 1.9, e o mínimo da nota também (D-007).
- **Testes da 1.x afetados:**
  - `test_politica.py` (constantes) é substituído pelos testes da RN-014 e da RN-016.
  - `test_exemplo.py` é reescrito com as três tabelas da seção 9.
  - `test_cli.py` e os casos de borda que chamam `main` passam a incluir `--politica` e `--cambio`.
  - Os testes de saída ganham os campos novos.

## 7. Riscos

| Risco | Probabilidade | O que faço se acontecer |
|---|---|---|
| `float` entrar por acidente numa conta (ex.: literal `0.01`, `round()`) | média | Teste de propriedade sobre a saída (nenhum valor monetário é `float`); ruff + revisão no `revisor-de-task`; constantes só como `Decimal("…")` |
| Conta da conversão, do limite em viagem ou dos totais arredondada em silêncio pela precisão do contexto | média | DT-012: toda conta no contexto exato, com `Inexact` e `Rounded` como trap; testes com produto de mais de 28 dígitos e percentual com mais de 28 casas |
| Implementação divergir da ordem da seção 8 (ex.: duplicata antes da nota, câmbio depois do período) | média | Casos de borda que só passam na ordem certa (relançamento com nota, duplicata de hospedagem com só uma nota, alimentação antes da hospedagem, "Sem cotação e fora do período") |
| Categoria de saída de despesa inválida divergir da dos itens válidos (duas regras de "reconhecida") | média | Seção 3: uma só função `categoria_de_saida`, chamada pelo motor para todo item; caso "Categoria reconhecível em despesa inválida" com `CC-COMERCIAL` e `representacao` |
| Testes da 1.x passarem a depender do conteúdo de `exemplos/envelope/` e quebrarem se o exemplo mudar | baixa | Política e câmbio padrão transcritos no `conftest.py` (seção 6); só os testes de aceite da seção 9 leem os arquivos de exemplo |
| Suíte vermelha bloquear todo commit da Fase 5 | certa sem ação | DT-016: pendências explícitas e estritas, removidas na última task |
| Valor gigante (`1e999999`, inteiro com milhares de dígitos) quebrar a leitura ou o cálculo | baixa | Resolvido na spec 1.4 (AMB-018, D-004) e estendido aos números da política e do câmbio na 2.0 (RN-016); `parse_int=Decimal` e o teto testado antes de qualquer `quantize` |
| Chave repetida passar sem aviso na entrada, ou sem erro na política e no câmbio (ex.: uma troca de parser que não chame o `object_pairs_hook`) | baixa | Testes da RN-013 e da RN-016 quebram se o aviso ou o erro sumirem |
| Nova mudança de política (outro centro de custo, outra categoria, outro percentual) | alta | Absorvida sem código: só o arquivo muda. O que ainda exige código está listado na seção 4 (constantes de interpretação) e no risco "Categorias reconhecidas pelo nome" da seção 10 da spec |
| Testes passarem por concordarem com o código, não com a spec | média | Esperados calculados à mão a partir da spec (skill `/task`, passo 4); `revisor-de-task` confere teste contra spec antes do commit |
