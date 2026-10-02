# Plano Técnico — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Baseado na spec:** 1.6

> Aqui mora o COMO. Este arquivo pode e deve falar de linguagem, biblioteca e
> arquitetura. O que ele **não** pode é introduzir regra de negócio nova — se
> apareceu uma, ela pertence à `spec.md`.

---

## 1. Stack

| Escolha | O quê | Por quê | O que descartei e por quê |
|---|---|---|---|
| Linguagem | Python ≥ 3.12, projeto gerenciado com `uv` (`pyproject.toml` + `uv.lock`) | `Decimal` e `datetime.date` na biblioteca padrão cobrem dinheiro e datas sem dependência; `uv` fixa a versão do Python (o do sistema é 3.9) e já é o que os hooks de `.githooks/` usam | Node/TypeScript: sem tipo decimal nativo, teria que trazer biblioteca para o ponto mais sensível do projeto |
| Testes | `pytest` | Testes como funções simples, `parametrize` para tabelas de casos (seção 7 da spec), `tmp_path` para a CLI | `unittest`: mais cerimônia por teste, sem ganho |
| Lint | `ruff` (regras `E`, `F`, `I`, `B`, `UP`) | Já exigido pelo `pre-commit`; um só binário para lint e ordenação de imports | `flake8` + `isort`: duas ferramentas para o mesmo papel |
| Parsing/validação | `simplejson` com `use_decimal=True` (leitura e escrita), `object_pairs_hook` para chaves repetidas (DT-010) + validação manual campo a campo | Lê `33.333` direto como `Decimal("33.333")`, sem passar por `float`, e escreve `Decimal` como número JSON exato; o hook entrega os pares de cada objeto na ordem do arquivo, inclusive os repetidos. A validação precisa produzir **item `entrada_invalida`** por despesa, não exceção — regra fina demais para um validador de schema | `json` da biblioteca padrão: lê com `parse_float=Decimal`, mas não escreve `Decimal` como número — teria que converter para `float` na saída e `valor_informado` perderia dígitos além do 17º. `pydantic`/`jsonschema`: rejeitam o documento inteiro ou exigem contornos para "erro vira item" e para copiar campos de tipo errado como nulo |
| Aritmética monetária | `decimal.Decimal`, `quantize(Decimal("0.01"), ROUND_HALF_UP)` | Exato ao centavo; `ROUND_HALF_UP` do Python arredonda a metade **afastando do zero** (-0,005 → -0,01), exatamente a RN-003 | `float`: `1.005` é guardado como `1.00499…` e `round(1.005, 2)` dá 1,00 (a RN-003 exige 1,01); `round(0.125, 2)` dá 0,12, porque `round` arredonda a metade para o par. Centavos em `int`: exige arredondar na conversão de qualquer forma, e o número informado (33,333) não cabe em centavos |
| CLI | `argparse` (biblioteca padrão) | Um subcomando, duas opções obrigatórias; erro de uso já sai com código 2 e mensagem em stderr | `click`/`typer`: dependência a mais para uma interface fixa e mínima |

## 2. Arquitetura

```
arquivo JSON ─▶ cli ─▶ entrada ─▶ motor ─▶ saida ─▶ cli ─▶ arquivo JSON
               (I/O)  (parse +    (regras,  (monta     (gravação
                       validação)  puro)     dicionário) atômica)
                         │           │
                         └── normalizacao, politica, justificativa ──┘
```

| Módulo (`src/reembolso/`) | Responsabilidade | Faz I/O? |
|---|---|---|
| `cli.py` | `argparse`, lê bytes do arquivo, chama o pipeline, grava a saída de forma atômica, mapeia erros para mensagem + código de saída | sim |
| `entrada.py` | bytes → JSON (`Decimal`) → `Entrada`. Resolve chaves repetidas e gera os avisos (RN-013); erros de arquivo da RN-002 viram `ErroDeArquivo`; despesa inválida vira `DespesaInvalida` (etapa 1 da seção 8) | não |
| `normalizacao.py` | `normalizar_texto()` — os 4 passos da seção 5 da spec | não |
| `politica.py` | constantes da política (seção 4 deste plano) | não |
| `motor.py` | etapas 2 a 9 da seção 8; recebe `Entrada`, devolve `Resultado` | não |
| `justificativa.py` | frase em português para cada item (texto não contratual) | não |
| `saida.py` | `Resultado` → dicionário na ordem de campos da seção 4 da spec → texto JSON | não |
| `modelo.py` | dataclasses e enums compartilhados (seção 3) | não |

**Fronteiras:** só `cli.py` toca disco, `sys.argv`, `stderr` e código de saída. Todo o resto é função pura de dados para dados, testável sem arquivo. A regra de negócio fica concentrada em `motor.py` + `politica.py` + `normalizacao.py`; `entrada.py` só aplica a RN-002 (forma da entrada). Uma mudança de política mexe em `politica.py`; uma mudança de regra mexe em `motor.py`; uma mudança de formato de entrada mexe em `entrada.py`; uma mudança de formato de saída mexe em `saida.py`.

Comando final: `uv run reembolso calcular --input <entrada> --output <saída>` (entry point `reembolso = "reembolso.cli:main"` no `pyproject.toml`).

## 3. Modelo de dados

Todas as estruturas são `@dataclass(frozen=True)`; valores monetários são sempre `Decimal`.

```python
class Status(StrEnum):   APROVADO, PARCIAL, RECUSADO
class Motivo(StrEnum):   # na ordem das etapas da seção 8 da spec
    ENTRADA_INVALIDA, VALOR_INVALIDO, FORA_DO_PERIODO, CATEGORIA_FORA_DA_POLITICA,
    NOTA_FISCAL_AUSENTE, DUPLICATA, LIMITE_DIARIO_EXCEDIDO

Colaborador(id: str, nome: str)
Periodo(inicio: date, fim: date, inicio_texto: str, fim_texto: str, competencia: str | None)

Despesa(                       # passou pela etapa 1 (validação)
    posicao: int,              # índice em `despesas` — ordem da entrada
    id: str, data: date, data_texto: str,
    categoria_texto: str,      # como veio
    categoria: str,            # normalizada (seção 5 da spec)
    fornecedor: str,           # normalizado
    valor_informado: Decimal,
    tem_nota_fiscal: bool,
    avisos: tuple[str, ...],   # RN-013
)
DespesaInvalida(               # recusada na etapa 1
    posicao: int,
    id: str | None, data_texto: str | None,
    categoria_saida: str | None,   # normalizada se reconhecida; senão texto como veio; senão None
    valor_informado: Decimal | None,
    avisos: tuple[str, ...],
)
Entrada(colaborador, periodo, despesas: list[Despesa | DespesaInvalida],
        avisos: tuple[str, ...])      # chaves repetidas fora das despesas

ItemResultado(                 # espelha `itens[]` da seção 4 da spec, campo a campo
    id, data, categoria, valor_informado, valor_considerado, valor_reembolsado,
    status: Status, motivo: Motivo | None, em_viagem: bool | None,
    limite_diario: Decimal | None, justificativa: str, avisos: tuple[str, ...],
)
Totais(valor_solicitado, valor_reembolsado, valor_glosado)
Resultado(colaborador, periodo, itens: list[ItemResultado], totais, avisos: tuple[str, ...])
```

A justificativa é gerada a partir dos campos contratuais do item já decidido (status, motivo, valores, limite, data), nunca o contrário: nenhuma decisão depende do texto.

## 4. Como a política é representada

Constantes em `politica.py`, um único módulo, com os valores **literais** da spec:

```python
LIMITES_DIARIOS = {          # RN-009: (normal, em viagem)
    "alimentacao":       LimiteDiario(normal=Decimal("60.00"),  viagem=Decimal("90.00")),
    "transporte_urbano": LimiteDiario(normal=Decimal("80.00"),  viagem=Decimal("120.00")),
    "hospedagem":        LimiteDiario(normal=Decimal("250.00"), viagem=Decimal("250.00")),
}
CATEGORIAS_RECONHECIDAS = frozenset(LIMITES_DIARIOS)          # RN-006
VALOR_ACIMA_DO_QUAL_EXIGE_NOTA = Decimal("100.00")            # RN-008 (estritamente maior)
CATEGORIA_QUE_COMPROVA_VIAGEM = "hospedagem"                  # RN-010
DIAS_EM_VIAGEM_APOS_HOSPEDAGEM = 1                            # RN-010: D e D+1
VALOR_ABSOLUTO_MAXIMO = Decimal("1000000000")                 # RN-002 / AMB-018 (a partir dele: entrada_invalida)
```

Os limites em viagem ficam escritos por extenso (90,00 / 120,00 / 250,00), e não calculados como `normal × 1,5`: a tabela da RN-009 é a fonte, e a hospedagem não amplia (AMB-006). Um teste confere `politica.py` contra a tabela da spec.

**Descartado:** arquivo de configuração (YAML/JSON) com a política. Não há requisito de trocar a política sem novo deploy; exigiria validar o próprio arquivo de política e testar combinações inválidas. Como a política já está isolada num módulo sem lógica, migrar para configuração depois custa um leitor e um teste.

## 5. Decisões técnicas

### DT-001 — Dinheiro em `Decimal` lido direto do texto JSON

**Contexto:** RN-003 exige arredondar a metade afastando do zero e cálculos exatos ao centavo; `valor_informado` é o número recebido (33.333).
**Decisão:** o JSON é lido com `simplejson.loads(..., use_decimal=True)`, então todo número com parte decimal chega como `Decimal` construído do texto, ou seja, com o valor decimal exato escrito no arquivo (seção 4 da spec); inteiros também, via `parse_int=Decimal` (evita o limite de 4.300 dígitos na conversão de texto para `int` do Python). `valor` com `abs(valor) >= VALOR_ABSOLUTO_MAXIMO` é `entrada_invalida` (RN-002) — comparação exata entre `Decimal`, válida para qualquer expoente. `valor_considerado = valor_informado.quantize(Decimal("0.01"), ROUND_HALF_UP)`. Toda conta (saldo do limite, totais) é feita entre `Decimal` já quantizados, então soma e subtração são exatas. A saída escreve `Decimal` como número JSON (`use_decimal=True`).
**Alternativa descartada:** `float` com arredondamento no fim (`round(1.005, 2) == 1.0`), e `json` padrão com conversão para `float` só na saída (perde dígitos de `valor_informado`).
**Consequência:** fácil garantir a RN-003 e os totais da seção 9 ao centavo. Com o teto da RN-002, todo valor aceito tem no máximo 12 dígitos depois de quantizado, e as somas cabem com folga na precisão padrão do `Decimal` (28 dígitos): nenhuma conta arredonda em silêncio nem levanta `InvalidOperation`. Exige cuidado para nunca misturar `float` (proibido em `motor.py`; um teste de propriedade verifica que nenhum campo monetário da saída é `float`). A forma escrita na saída pode diferir da entrada (`72.50` → `72.5`, ou `45.00` → `45.00`), o que a spec permite (seção 4: "como veio" é o valor numérico).

### DT-002 — Rejeitar o que não é JSON estrito

**Contexto:** RN-002: arquivo que não é JSON válido é erro de arquivo. O `json` da biblioteca padrão aceita `NaN`, `Infinity` e `-Infinity`, que não são JSON.
**Decisão:** `simplejson` ≥ 4 já os rejeita na leitura por padrão (`allow_nan=False`); a versão mínima fica fixada no `pyproject.toml` e um teste garante que `"valor": NaN` é erro de arquivo, para a proteção não sumir numa troca de versão. Erro de parse → `ErroDeArquivo`. Bytes decodificados como UTF-8 estrito (`utf-8-sig`, aceitando BOM, que a RFC 8259 permite ignorar); falha de decodificação → `ErroDeArquivo`. O parser aceita em silêncio um escape `\ud800` sem par (vira um caractere substituto isolado na `str`, que a gravação em UTF-8 recusaria depois); por isso, depois do parse, `entrada.py` percorre todas as chaves e textos e levanta `ErroDeArquivo` se algum contiver caractere entre U+D800 e U+DFFF (seção 4 da spec). Pares de escapes válidos já chegam combinados num único caractere.
**Alternativa descartada:** aceitar `NaN` e tratar como "valor não é número" na despesa: transformaria arquivo inválido em processamento normal.
**Consequência:** `"valor": NaN` encerra a execução sem saída, como qualquer JSON inválido.

### DT-003 — Validação de tipo sem as armadilhas do Python

**Contexto:** RN-002 exige `valor` número e `tem_nota_fiscal` booleano. Em Python, `True` é `int`; `date.fromisoformat` (3.11+) aceita `20260701` e outros formatos ISO; `strptime("%Y-%m-%d")` aceita `2026-7-1`; `\d` casa dígitos não ASCII.
**Decisão:**
- número = `Decimal` ou `int`, **e não** `bool`;
- booleano = `type(x) is bool`;
- data = casa `^[0-9]{4}-[0-9]{2}-[0-9]{2}$` **e** `date.fromisoformat` aceita (rejeita 2026-02-30);
- texto obrigatório = `str` com `strip()` não vazio (o `strip()` sem argumento remove todo espaço em branco Unicode, inclusive o não separável).
**Alternativa descartada:** `isinstance(x, (int, float))` e `fromisoformat` sozinho — aceitariam `"valor": true` e `"data": "20260703"`.
**Consequência:** cada armadilha vira um caso de teste de `entrada.py`.

### DT-004 — Normalização de texto com `unicodedata`

**Contexto:** seção 5 da spec, 4 passos, "qualquer que seja a forma como o caractere foi codificado".
**Decisão:** `strip()` → `casefold()` → `unicodedata.normalize("NFD")` e remoção dos caracteres de categoria `Mn` (marcas combinantes) → `re.sub(r"[\s\-_]+", "_", ...)`. O NFD decompõe tanto `á` pré-composto (U+00E1) quanto `a` + acento combinante (U+0301) para a mesma sequência, cobrindo as duas codificações.
**Alternativa descartada:** tabela manual de acentos (`á→a`, ...): incompleta por construção; `NFKD`: também desfaz compatibilidades (ligaduras, larguras) que a spec não pede.
**Consequência:** uma função pura, usada por RN-006 e RN-007, testada com os exemplos da seção 5 e os casos de borda de categoria e fornecedor.

### DT-005 — Pipeline em duas fases, espelhando a seção 8

**Contexto:** as etapas 1 a 6 decidem cada despesa isoladamente; as etapas 7 a 9 dependem do conjunto (duplicatas, viagem, saldo do dia).
**Decisão:**
1. **Fase individual:** para cada despesa, na ordem, aplica uma lista ordenada de verificações (`valor_invalido`, `fora_do_periodo`, `categoria_fora_da_politica`, `nota_fiscal_ausente`); a primeira recusa encerra. A ordem da lista é a ordem da seção 8.
2. **Duplicatas:** agrupa as sobreviventes por `(data, categoria, fornecedor, valor_considerado)`; em cada grupo, a original é a primeira com `tem_nota_fiscal`, ou a primeira por `posicao`; as demais recebem `duplicata`.
3. **Viagem:** `dias_em_viagem` = `{D, D+1}` para cada hospedagem sobrevivente com nota. Calculado **antes** de qualquer limite, então independe da ordem na entrada.
4. **Limite:** percorre as sobreviventes por `posicao`, com saldo por `(data, categoria)`; reembolsado = `min(valor_considerado, saldo)`; status pela RN-011.
**Alternativa descartada:** uma passada única despesa a despesa: a viagem de uma hospedagem que aparece depois da alimentação do mesmo dia não seria vista (caso de borda "Alimentação antes da hospedagem").
**Consequência:** reordenar ou inserir uma etapa individual é mexer numa lista; cada fase é testável isoladamente.

### DT-006 — Gravação atômica da saída

**Contexto:** em erro de arquivo, a saída não pode ser criada nem alterada, inclusive se a falha for na gravação (RN-002, seção 4).
**Decisão:** todo o processamento e a serialização acontecem em memória antes de tocar o disco. A gravação escreve num arquivo temporário no **mesmo diretório** da saída e faz `os.replace` para o nome final; em qualquer falha, remove o temporário. Pasta inexistente ou sem permissão falha na criação do temporário, antes de qualquer alteração.
**Alternativa descartada:** `open(output, "w")` direto: trunca o arquivo existente antes de escrever; uma falha no meio deixa arquivo parcial.
**Consequência:** o arquivo de saída ou fica como estava, ou é substituído inteiro.

### DT-007 — Códigos de saída e mensagens

**Contexto:** a spec exige só "código diferente de 0" e "mensagem de erro".
**Decisão:** `0` sucesso; `1` erro de arquivo (mensagem `erro: <descrição>` em stderr); `2` erro de uso (padrão do `argparse`). Nenhuma exceção não tratada chega ao usuário como stack trace por um erro previsto na RN-002.
**Alternativa descartada:** um único código para tudo: perderia a distinção útil para scripts, sem custo para cumpri-la.
**Consequência:** os testes de CLI conferem `!= 0` (contrato) e o código exato (este plano).

### DT-008 — Serialização determinística

**Contexto:** critério de aceite "a mesma entrada sempre produz a mesma saída".
**Decisão:** itens na ordem de `posicao`; campos de cada objeto na ordem da tabela da seção 4 da spec; `ensure_ascii=False`, UTF-8, `indent=2`, quebra de linha final. Nenhuma decisão depende de ordem de iteração de `set`; agrupamentos usam `dict` (ordem de inserção).
**Consequência:** saída idêntica byte a byte entre execuções; testável comparando duas execuções.

### DT-009 — Formatação de valores na justificativa

**Contexto:** a justificativa é em português e não contratual (seção 4), mas o exemplo da spec usa `45,00` e `03/07`.
**Decisão:** função própria em `justificativa.py` formata `Decimal` como `1.234,56` e datas como `DD/MM`, sem depender de `locale` do sistema (que mudaria a saída entre máquinas e quebraria a DT-008).
**Consequência:** os testes conferem que toda justificativa é texto não vazio; o conteúdo exato não é testado, para não transformar texto livre em contrato.

### DT-010 — Chaves repetidas pelo `object_pairs_hook`

**Contexto:** RN-013: vale a última ocorrência de uma chave repetida, com aviso de texto fixo, caminho e ordem definidos. Um `dict` comum descarta as ocorrências anteriores sem deixar rastro.
**Decisão:** o `object_pairs_hook` monta cada objeto como `ObjetoJson` (subclasse de `dict`, preenchido pela última ocorrência), que guarda também a lista original de pares. Depois do parse, `entrada.py` percorre o documento seguindo essa lista: ao passar pela **primeira** ocorrência de uma chave repetida, emite o aviso; desce só no valor da ocorrência que valeu. Assim os avisos saem na ordem do arquivo, e valores descartados nunca são visitados. O percurso começa em cada elemento de `despesas` com caminho relativo (avisos do item; elemento que é lista começa por `[i]`; listas encadeadas viram `[i][j]`) e no restante com caminho a partir da raiz (avisos do topo). As chaves comparadas são as `str` já decodificadas pelo parser, sem `unicodedata.normalize` (RN-013); como o percurso só desce no valor que valeu, ocorrências dentro de valores descartados não entram no `<n>` nem na ordem.
**Alternativa descartada:** detectar repetição no texto bruto com expressão regular ou um tokenizador próprio — reescreveria o parser; e `parse` padrão + segunda leitura: duas fontes da verdade para o mesmo arquivo.
**Consequência:** o resto do código vê `dict` comum; a RN-013 fica inteira em `entrada.py`, testável com strings JSON curtas.

## 6. Estratégia de testes

- **Nível e proporção:**
  - **Unitários (~70%)** — `normalizacao`, `entrada` (cada item da RN-002 e cada armadilha da DT-003), `motor` (uma regra por arquivo), sem disco.
  - **Integração (~20%)** — `entrada → motor → saida` com `exemplos/despesas-exemplo.json` contra a tabela da seção 9 da spec, transcrita à mão para o teste (nunca copiada da saída do programa), e totais 1.861,84 / 585,43 / 1.276,41.
  - **Ponta a ponta (~10%)** — `cli.main([...])` com `tmp_path`: código de saída, arquivo criado, arquivo preexistente intacto em erro, erro de uso, pasta inexistente, determinismo byte a byte.
- **Cada `RN-NNN` da spec tem teste?** Um arquivo por regra (`tests/test_rn001_um_resultado_por_despesa.py`, …, `test_rn013_chave_repetida.py`), cobrindo pelo menos o **Aceite** da regra. `tests/test_rastreabilidade.py` lê a `spec.md`, extrai todos os `RN-NNN` e falha se algum não aparecer no nome ou na docstring de pelo menos um teste.
- **Casos de borda da seção 7 da spec:** `tests/test_casos_de_borda.py`, um teste parametrizado por linha da tabela, com `id` igual ao texto da coluna "Caso". `test_rastreabilidade.py` também extrai a coluna "Caso" da seção 7 e falha se algum caso não tiver teste com esse `id` — caso novo na spec sem teste quebra a suíte.
- **Nomenclatura:** `test_rnNNN_<comportamento>` com docstring `"""RN-NNN / AMB-NNN: <o que a spec diz>"""`; o esperado de cada teste tem um comentário com a conta feita a partir da spec (ex.: `# 72,50 + 38,00 > 60,00 → 60,00 e 0`). O nome remete à regra; a docstring, à decisão.
- **Fixtures:** um construtor de entrada mínima válida em `tests/conftest.py` (`entrada(despesas=[...])`, `despesa(**campos)`), para cada teste declarar só o que importa ao caso.

## 7. Riscos

| Risco | Probabilidade | O que faço se acontecer |
|---|---|---|
| `float` entrar por acidente numa conta (ex.: literal `0.01`, `round()`) | média | Teste de propriedade sobre a saída (nenhum valor monetário é `float`); ruff + revisão no `revisor-de-task`; constantes só como `Decimal("…")` |
| Implementação divergir da ordem da seção 8 (ex.: duplicata antes da nota) | média | Casos de borda que só passam na ordem certa (relançamento com nota, duplicata de hospedagem com só uma nota, alimentação antes da hospedagem) |
| Valor gigante (`1e999999`, inteiro com milhares de dígitos) quebrar a leitura ou o cálculo | baixa | Resolvido na spec 1.4 (AMB-018, D-004): `entrada_invalida`. No código, `parse_int=Decimal` e o teto testado antes de qualquer `quantize`; casos de borda com `1e999999` e inteiro de 5.000 dígitos |
| Chave repetida passar sem aviso (ex.: uma troca de parser que não chame o `object_pairs_hook`) | baixa | Resolvido na spec 1.4 (RN-013, D-004); os testes da RN-013 quebram se o aviso sumir |
| Envelope do Dia 2 mudar política, regra ou formato | alta (é certo) | Fronteiras da seção 2: política em `politica.py`, regras em `motor.py` com etapas em lista ordenada, formato em `entrada.py`/`saida.py`; rastreabilidade automática (seção 6) aponta os testes afetados |
| Testes passarem por concordarem com o código, não com a spec | média | Esperados calculados à mão a partir da spec (skill `/task`, passo 4); `revisor-de-task` confere teste contra spec antes do commit |
