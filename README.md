# Motor de Cálculo de Reembolso

CLI que lê um JSON com as despesas de um colaborador num período e grava um JSON
com, para cada despesa, o valor reembolsável, o status (`aprovado`, `parcial`,
`recusado`), o motivo e uma justificativa em português, além dos totais.

Desenvolvido com Spec Driven Development para o desafio descrito em
[`DESAFIO.md`](DESAFIO.md). As regras de negócio, incluindo as 19 ambiguidades da
política de RH e a decisão tomada em cada uma, estão na spec, não no código.

## Requisitos

- [`uv`](https://docs.astral.sh/uv/getting-started/installation/), que baixa o
  Python ≥ 3.12 sozinho se a máquina não tiver.

## Como rodar

```bash
git clone https://github.com/rafaeltxm/sdd-desafio.git
cd sdd-desafio
uv sync
uv run reembolso calcular --input exemplos/despesas-exemplo.json --output resultado.json
```

- **Entrada:** o formato de [`exemplos/despesas-exemplo.json`](exemplos/despesas-exemplo.json)
  (spec, seção 4).
- **Saída:** o schema está na spec, seção 4. O resultado esperado do exemplo está
  na tabela da seção 9: solicitado R$ 1.861,84, reembolsado R$ 585,43, glosado
  R$ 1.276,41.
- **Códigos de saída:**
  - `0`: sucesso.
  - `1`: erro de arquivo (JSON inválido, cabeçalho inválido, saída que não pode
    ser gravada), com a mensagem `erro: ...` em stderr.
  - `2`: erro de uso.

  Em caso de erro, o arquivo de saída não é criado nem alterado.

## Como testar

```bash
uv run pytest -q        # suíte completa (regras, casos de borda, exemplo, CLI, rastreabilidade)
uv run ruff check .     # lint
```

Os testes que garantem a ligação entre spec e código:

- `tests/test_rnNNN_*.py`: um arquivo por regra de negócio (RN-001 a RN-013).
- `tests/test_casos_de_borda.py`: um teste por linha da seção 7 da spec, com o
  nome do caso como `id`.
- `tests/test_exemplo.py`: o arquivo de exemplo pela CLI, conferido contra a
  tabela da seção 9 transcrita à mão.
- `tests/test_rastreabilidade.py`: lê a spec e falha se alguma RN ou algum caso
  de borda ficar sem teste.

## Onde está cada coisa

| Arquivo | O quê |
|---|---|
| [`specs/001-motor-reembolso/spec.md`](specs/001-motor-reembolso/spec.md) | O quê e o porquê: regras RN-001 a RN-013, ambiguidades AMB-001 a AMB-019, casos de borda, critérios de aceite, fora de escopo |
| [`specs/001-motor-reembolso/plan.md`](specs/001-motor-reembolso/plan.md) | O como: stack, arquitetura, modelo de dados, decisões técnicas DT-001 a DT-010, estratégia de testes |
| [`specs/001-motor-reembolso/tasks.md`](specs/001-motor-reembolso/tasks.md) | Tasks T-001 em diante, com o commit de cada uma e a tabela de cobertura regra → task → teste |
| [`specs/001-motor-reembolso/DECISIONS.md`](specs/001-motor-reembolso/DECISIONS.md) | Log de mudanças da spec |
| [`src/reembolso/`](src/reembolso/) | Código: `cli` → `entrada` → `motor` → `saida` (plan, seção 2) |
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
