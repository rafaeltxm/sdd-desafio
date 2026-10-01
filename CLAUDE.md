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

1. Ler a task em `tasks.md` e as `RN-`/`AMB-` que ela cita na spec.
2. Implementar código + teste; `uv run pytest -q` e `uv run ruff check .` verdes.
3. **Task de regra de negócio:** antes do commit, invocar o subagente
   `task-reviewer` passando **só o ID da task** (sem explicar a implementação).
   Ele salva o parecer em `docs/reviews/T-NNN.md`. Tratar todo achado
   CORRIGIR CÓDIGO / CORRIGIR SPEC antes do commit (CORRIGIR SPEC → atualizar
   spec + `DECISIONS.md`). Tasks de estrutura (CLI, leitura de JSON, setup)
   dispensam a revisão.
4. Commit com o parecer junto; marcar `[x]` e o hash na task.

Git hooks em `.githooks/` (ativar uma vez por clone: `git config core.hooksPath .githooks`):
- `pre-commit` — `ruff check` + `pytest`; bloqueia se falhar.
- `commit-msg` — valida o padrão de mensagem e que o `T-NNN` existe em `tasks.md`.
- `post-commit` — lembra de exportar a sessão para `docs/sessions/NN-*.md`.

Formatos de commit aceitos: `feat|test|fix|refactor(T-NNN):`,
`docs(spec|plan|tasks|decisions|readme|relatorio|sessions|claude):`,
`chore(tooling|setup|T-NNN):`.

## Stack e comandos

- Linguagem: `<...>`
- Rodar: `<comando>`
- Testes: `<comando>`
- Lint/format: `<comando>`

## Convenções de código

- `<nomenclatura, estrutura de pastas, tratamento de erro, o que for relevante>`
- Valores monetários: `<como são representados — decimal, centavos em inteiro, etc.>`

## Fora de escopo

- `<o que este projeto explicitamente não faz — evita que o agente invente feature>`
