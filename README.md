# Motor de Cálculo de Reembolso

CLI que lê um JSON com as despesas de um colaborador num período, um arquivo de
política (limites por centro de custo) e um arquivo de câmbio, e grava um JSON
com, para cada despesa, o valor reembolsável em reais, o status (`aprovado`,
`parcial`, `recusado`), o motivo e uma justificativa em português, além dos totais.

Desenvolvido com Spec Driven Development para o desafio descrito em
[`DESAFIO.md`](DESAFIO.md). As regras de negócio, incluindo as 31 ambiguidades da
política de RH (19 da política original e 12 da Política v4 do envelope) e a
decisão tomada em cada uma, estão na spec, não no código.

## Requisitos

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/), que baixa o
  Python ≥ 3.12 sozinho se a máquina não tiver.

## Como rodar

```bash
git clone https://github.com/rafaeltxm/sdd-desafio.git
cd sdd-desafio
uv sync
uv run reembolso calcular \
  --input exemplos/despesas-exemplo.json \
  --politica exemplos/envelope/politica-v4.json \
  --cambio exemplos/envelope/cambio.json \
  --output resultado.json
```

Os quatro argumentos são obrigatórios e cada um aparece uma vez só.

- **Entrada:** o formato de [`exemplos/despesas-exemplo.json`](exemplos/despesas-exemplo.json)
  e de [`exemplos/envelope/`](exemplos/envelope/) (spec, seção 4).
- **Política e câmbio:** os formatos de
  [`politica-v4.json`](exemplos/envelope/politica-v4.json) e
  [`cambio.json`](exemplos/envelope/cambio.json). Os limites, o mínimo da nota
  fiscal e o percentual vêm do arquivo de política, não do código.
- **Saída:** o schema está na spec, seção 4. Os resultados esperados dos três
  arquivos de exemplo estão nas tabelas da seção 9:

  | Entrada | Solicitado | Reembolsado | Glosado |
  |---|---:|---:|---:|
  | `exemplos/despesas-exemplo.json` | R$ 1.861,84 | R$ 351,43 | R$ 1.510,41 |
  | `exemplos/envelope/despesas-envelope.json` | R$ 2.457,52 | R$ 1.148,26 | R$ 1.309,26 |
  | `exemplos/envelope/despesas-envelope-cc-desconhecido.json` | R$ 623,76 | R$ 373,76 | R$ 250,00 |

- **Códigos de saída:**
  - `0`: sucesso.
  - `1`: erro de arquivo (JSON inválido, cabeçalho inválido, política ou câmbio
    inválidos, saída que não pode ser gravada), com a mensagem
    `erro: <arquivo>: ...` em stderr.
  - `2`: erro de uso (argumento faltando, repetido, abreviado ou desconhecido).

  Em caso de erro, o arquivo de saída não é criado nem alterado.

## Como testar

```bash
uv run pytest -q        # suíte completa (regras, casos de borda, exemplo, CLI, rastreabilidade)
uv run ruff check .     # lint
```

Os testes que garantem a ligação entre spec e código:

- `tests/test_rnNNN_*.py`: um arquivo por regra de negócio (RN-001 a RN-016).
- `tests/test_casos_de_borda.py`: um teste por linha da seção 7 da spec, com o
  nome do caso como `id`.
- `tests/test_exemplo.py`: os três arquivos de exemplo pela CLI, conferidos
  contra as tabelas da seção 9 transcritas à mão.
- `tests/test_rastreabilidade.py`: lê a spec e falha se alguma RN ou algum caso
  de borda ficar sem teste.

## Onde está cada coisa

| Arquivo | O quê |
|---|---|
| [`specs/001-motor-reembolso/spec.md`](specs/001-motor-reembolso/spec.md) | O quê e o porquê: regras RN-001 a RN-016, ambiguidades AMB-001 a AMB-031, casos de borda, critérios de aceite, fora de escopo |
| [`specs/001-motor-reembolso/plan.md`](specs/001-motor-reembolso/plan.md) | O como: stack, arquitetura, modelo de dados, decisões técnicas DT-001 a DT-016, estratégia de testes |
| [`specs/001-motor-reembolso/tasks.md`](specs/001-motor-reembolso/tasks.md) | Tasks T-001 em diante, com o commit de cada uma e a tabela de cobertura regra → task → teste |
| [`specs/001-motor-reembolso/DECISIONS.md`](specs/001-motor-reembolso/DECISIONS.md) | Log de mudanças da spec (D-001 a D-008) |
| [`src/reembolso/`](src/reembolso/) | Código: `cli` → `leitura` → `entrada` / `politica` / `cambio` → `motor` → `saida` (plan, seção 2) |
| [`tests/`](tests/) | Testes |
| [`docs/reviews/`](docs/reviews/) | Parecer do revisor independente de cada task de regra |
| [`docs/sessions/`](docs/sessions/) | Exports das sessões com o Claude Code |
| [`docs/RELATORIO.md`](docs/RELATORIO.md) | Relatório final |
| [`CLAUDE.md`](CLAUDE.md), [`.claude/`](.claude/), [`.githooks/`](.githooks/) | Convenções para o agente, skill `/task`, subagentes e hooks de commit |

## Para quem for contribuir

```bash
git config core.hooksPath .githooks   # uma vez por clone: ruff + pytest e padrão de mensagem de commit
```

Todo commit referencia uma task (`feat(T-NNN): ...`) ou é de documentação
(`docs(spec): ...`). Os formatos aceitos estão no [`CLAUDE.md`](CLAUDE.md).

O enunciado original do desafio está em [`DESAFIO.md`](DESAFIO.md), a rubrica em
[`RUBRICA.md`](RUBRICA.md) e o FAQ em [`FAQ.md`](FAQ.md).
