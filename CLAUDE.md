# CLAUDE.md

> Este arquivo é lido pelo Claude Code no início de toda sessão. É onde moram as
> convenções que você não quer repetir em todo prompt.
> Substitua os `<...>` e apague o que não usar. Mantenha curto — CLAUDE.md longo
> é CLAUDE.md ignorado.

## O projeto

Motor de cálculo de reembolso de despesas corporativas. CLI que lê um JSON de
despesas e emite um JSON com o valor reembolsável e a justificativa de cada item.

## Fonte da verdade

`specs/001-motor-reembolso/spec.md` define **o que** o sistema faz.
`specs/001-motor-reembolso/plan.md` define **como**.
`specs/001-motor-reembolso/tasks.md` define **em que ordem**.

Quando o código e a spec discordarem, a spec está certa e o código é o bug —
a menos que a spec esteja errada, e nesse caso corrigimos a spec primeiro e
registramos em `DECISIONS.md`.

**Antes de implementar qualquer coisa, leia a task correspondente em `tasks.md`.**
Se o que eu pedi não está coberto por nenhuma task, me avise em vez de implementar.

## Regras de trabalho

- Toda regra de negócio vive na spec, não no chat e não em comentário de código.
- Se eu te explicar uma regra que não está na spec, **pare e me diga isso** antes
  de escrever código. Isso é um bug de spec.
- Todo commit referencia uma task: `feat(T-003): <descrição>` (formatos completos abaixo).
  Mudanças de documentação: `docs(spec):`, `docs(plan):`, `docs(tasks):`.
- Nenhuma regra de negócio entra sem teste.

## Revisão adversarial da spec

Antes de começar a implementação, e depois de qualquer mudança relevante na spec
(inclusive a do envelope), invocar o subagente `spec-adversary`. Ele só lê e
devolve problemas numerados com perguntas; **as decisões são do humano**. Cada
pergunta BLOQUEANTE vira decisão na spec + entrada no `DECISIONS.md` antes do código.

## Fluxo por task e ferramentas de qualidade

Toda task é executada pela skill `/task T-NNN` (`.claude/skills/task/SKILL.md`),
que detalha o fluxo abaixo e para para aprovação humana antes do commit.

1. Ler a task em `tasks.md` e as `RN-`/`AMB-` que ela cita na spec.
2. Implementar código + teste; `uv run pytest -q` e `uv run ruff check .` verdes.
3. **Task de regra de negócio:** antes do commit, invocar o subagente
   `revisor-de-task` passando **só o ID da task** (sem explicar a implementação).
   Ele é somente leitura; o relatório que devolve é salvo sem edição em
   `docs/reviews/T-NNN.md`. Resultado BLOQUEADO impede o commit: corrigir o
   código/teste, ou — se houver "Decisões necessárias" — parar para decisão
   humana (spec + `DECISIONS.md` antes). Tasks de estrutura (CLI, leitura de
   JSON, setup) dispensam a revisão.
4. Commit com o parecer junto; marcar `[x]` e o hash na task.

Git hooks em `.githooks/` (ativar uma vez por clone: `git config core.hooksPath .githooks`):
- `pre-commit` — `ruff check` + `pytest`; bloqueia se falhar.
- `commit-msg` — valida o padrão de mensagem e que o `T-NNN` existe em `tasks.md`.
- `post-commit` — no fim de um bloco (qualquer commit exceto `feat|test|fix|refactor(T-NNN)`
  e `docs(sessions)`), lembra de exportar a sessão para `docs/sessions/NN-*.md`. O hook
  `.claude/hooks/lembrete-export.sh` (em `.claude/settings.json`) mostra o mesmo lembrete
  ao usuário quando o commit é feito pelo Claude. Ao vê-lo, não iniciar o próximo bloco
  sem o usuário.

Formatos de commit aceitos: `feat|test|fix|refactor(T-NNN):`,
`docs(spec|plan|tasks|decisions|readme|relatorio|sessions|claude):`,
`chore(tooling|setup|T-NNN):`.

## Stack e comandos

Detalhes e justificativas em `plan.md` seção 1.

- Linguagem: Python ≥ 3.12 gerenciado com `uv` (`pyproject.toml` + `uv.lock`);
  o Python do sistema é 3.9, então sempre via `uv run`. Dependência de runtime
  só `simplejson` ≥ 4; o resto é biblioteca padrão (`decimal`, `argparse`, `unicodedata`).
- Rodar: `uv run reembolso calcular --input <entrada> --output <saída>`
- Testes: `uv run pytest -q`
- Lint: `uv run ruff check .` (regras `E`, `F`, `I`, `B`, `UP`)
- Pacote em `src/reembolso/`, testes em `tests/` (módulos e fronteiras: `plan.md` seção 2).

## Convenções de código

- `<nomenclatura, estrutura de pastas, tratamento de erro, o que for relevante>`
- Valores monetários: `<como são representados — decimal, centavos em inteiro, etc.>`

## Fora de escopo

- `<o que este projeto explicitamente não faz — evita que o agente invente feature>`
