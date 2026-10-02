# Roteiro do Desafio — passo a passo

Checklist pessoal para organizar os 2 dias. Marque `[x]` conforme avança.

**Prazos:** envelope com mudança de requisito no **Dia 2 ~10h** · entrega no **Dia 2, 18h**.

**Regras que valem o tempo todo:**
- Todo commit referencia task: `feat(T-00N): ...`, `test(T-00N): ...` · docs usam `docs(spec)`, `docs(plan)`, `docs(tasks)`.
- Regra/decisão explicada no chat e ausente da spec = bug de spec → corrigir spec + registrar no `DECISIONS.md` antes de seguir.
- `/export docs/sessions/NN-descricao.md` ao fim de **cada** sessão, e commitar.
- Anotar durante o trabalho (para o relatório): erros do Claude que você pegou, o que verificou, o que delegou.

---

## Fase 0 — Preparação

- [x] Fork público + clone
- [x] Copiar `template/` → `CLAUDE.md`, `specs/`, `docs/` e commitar
- [x] Testar `/export` (`docs/sessions/01-setup.md`) e push
- [x] Ler `DESAFIO.md` e percorrer `exemplos/despesas-exemplo.json`
- [x] Ler `RUBRICA.md` e `FAQ.md`
- [x] Confirmar que o fork está público

### O que a rubrica/FAQ deixam claro (lembretes)
- Ambiguidades de 3 tipos: **unidade de aplicação**, **fronteira**, **dado ausente**. Mínimo 8; mais que 8 conta a favor.
- Não existe interpretação certa: decisão escrita + justificada + código fiel a ela = pontuação integral.
- Caso presente no exemplo e ausente da spec = buraco (mesmo que seja para declarar fora de escopo).
- Produto é conferido **contra a minha spec**, inclusive em casos ocultos → spec precisa ser precisa.
- Penalidades: regra só no chat (−5 cada), sem `DECISIONS.md` (−5), sem `CLAUDE.md` (−3), README que não roda (−3).
- Rastreabilidade: datas dos commits na ordem spec → plan → tasks → código; marcar tasks concluídas **ao longo** do caminho; testes nomeados pelos requisitos.
- Envelope: ordem spec → `DECISIONS.md` → tasks → código. Bônus por medir em números o quanto foi reexecução de tasks vs. edição manual.
- Commit errado? Não reescrever histórico; registrar no relatório.
- Fechar a spec até ~meio-dia do Dia 1, mesmo imperfeita.

## Fase 1 — Dia 1, manhã: especificar (sem código)

### 1.1 `spec.md` — o QUÊ e o PORQUÊ
- [x] Decidir cada ambiguidade (A1–A15 + ordem de aplicação das regras) — 19 na spec 1.6: AMB-001…AMB-019, ordem em AMB-016 e seção 8
- [x] Escrever na spec: ambiguidade → decisão → justificativa de 1 linha — spec seção 6
- [x] Requisitos funcionais numerados (RF-01, RF-02, ...) — numerados como regras de negócio RN-001…RN-013 (spec seção 5)
- [x] Schema de saída (JSON) documentado — spec seção 4
- [x] Casos de borda + critérios de aceite verificáveis sem ler código — seção 7 (63 casos), seção 9 e **Aceite** de cada RN
- [x] Fora de escopo explícito — spec seção 3
- [x] Revisar: nada de biblioteca, classe, pasta ou linguagem na spec
- [x] Commit `docs(spec): ...` — `c8bcad9` (1.0) → `d35f68d` (1.1, D-001) → `bdb1eec` (1.2, D-002) → `b253498` (1.3, D-003) → `1eb808c` (1.6, D-004)
- [x] Revisões adversariais com `spec-adversary`, decisões registradas em `DECISIONS.md` (D-001 a D-004)

### 1.2 `plan.md` — o COMO
- [x] Stack e por quê — plan seção 1
- [x] Arquitetura em blocos e modelo de dados — plan seções 2 e 3
- [x] Decisões técnicas com alternativa descartada e motivo — DT-001 a DT-010 (plan seção 5)
- [x] Estratégia de testes (incluindo o exemplo como teste de ponta a ponta) — plan seção 6
- [x] Commit `docs(plan): ...` — `bf1df44` (plan 1.0 sobre spec 1.6)

### 1.3 `tasks.md` — a fatia executável
- [x] T-001..T-0NN, cada uma: o que faz, RFs atendidos, critério de aceite (teste X passa) — T-001…T-021, com Tipo, Atende, Depende de, Aceite e Casos de borda
- [x] Cada task pequena o bastante para 1 commit
- [x] Commit `docs(tasks): ...` — `70b9d31` (tasks 1.0)

### 1.4 `CLAUDE.md`
- [x] Convenções do projeto (stack, como rodar testes, padrão de commit, "spec é a fonte da verdade")
- [x] Commit — `b8efb2b docs(claude)`
- [ ] **Pendente:** "Convenções de código" e "Fora de escopo" ainda com `<...>` do template (dinheiro em `Decimal` → DT-001; fora de escopo → spec seção 3) — commit `docs(claude)`

- [x] `/export` da sessão + commit — sessões 05 a 09 (`docs/sessions/`)

## Fase 2 — Dia 1, tarde: implementar guiado pelas tasks

Avaliação em 2026-10-02 09:50 (antes do envelope): T-001…T-021 concluídas, 649 testes passando, ruff limpo.

- [x] Esqueleto da CLI: `uv run reembolso calcular --input X --output Y` — T-019 `00cf730`; exemplo roda com exit 0
- [x] Executar task por task (teste + código + commit com `T-00N`) — 21 tasks, cada uma com commit `feat|test|chore(T-NNN)` + `docs(tasks): conclui` + hash preenchido em `tasks.md`
- [x] Ler o diff de cada entrega do Claude antes de aceitar; rodar testes — skill `/task` + `revisor-de-task` em 15 tasks de regra (`docs/reviews/`); hooks `pre-commit`/`commit-msg` ativos
- [x] Ao descobrir lacuna na spec: parar → corrigir spec → `DECISIONS.md` → seguir — spec 1.8 (D-005, durante T-003) e 1.9 (D-006, durante T-006/T-008), sempre spec → plan → tasks → código
- [x] Teste de ponta a ponta com `exemplos/despesas-exemplo.json` — T-020 `45f014f` (tabela da seção 9 transcrita à mão + determinismo)
- [x] Rastreabilidade automática RN/casos de borda → testes — T-021 `672cc34`; tabela de Cobertura preenchida
- [ ] **`README.md` do projeto (como rodar, como testar) substituindo o atual** — ainda é o README do desafio (risco de −3). Não é task de código: commit `docs(readme)`
- [x] Sistema base funcionando e testado **antes do Dia 2**
- [ ] **Push** — `main` está 80 commits à frente de `origin/main`; nada do trabalho está no fork público ainda
- [ ] `/export` da sessão desta avaliação (sessão 33) + commit + push

### Anotações para o relatório (coletadas até aqui)
- Revisões BLOQUEADAS pelo `revisor-de-task`: T-003 (2×) e T-007 (2×) — candidatas a **Discernimento** (o que o Claude entregou, o que o revisor pegou, o que foi corrigido); ver `docs/reviews/T-003.md`, `docs/reviews/T-007.md` e sessões 13 e 17.
- Mudanças de spec durante a implementação: D-005 (normalização) e D-006 (forma do arquivo) — candidatas a **Descrição**/Diligência.
- Commits sem task a explicar: `994a491 chore:` (estrutura inicial) e `683f161 docs:` (export da sessão 01), anteriores ao hook `commit-msg`.
- Versões da spec puladas (1.4, 1.5, 1.7): explicar no relatório que foram intermediárias dentro de D-004/D-005, ou citar isso no próprio `DECISIONS.md`.
- Tasks estruturais sem revisão (T-001, T-004, T-005, T-006, T-019, T-021) — dispensa prevista no `CLAUDE.md`.
- Ressalvas dos revisores marcadas como opcionais e não aplicadas: levantar uma vez para o relatório (Diligência: "o que aceitei sem verificar").
- Sessão 33: `/task T-022` pedida sem a task existir — o fluxo parou em vez de inventar (exemplo de guarda-corpo funcionando).

## Fase 3 — Dia 2, ~10h: o envelope (20 pts)

- [ ] Anotar hora de início e o hash de partida (`git rev-parse --short HEAD`) para o `git diff --stat` do relatório
- [ ] Ler a mudança e mapear o impacto: quais RN-/AMB-, casos de borda (seção 7), tabela da seção 9, tasks e testes ela toca
- [ ] Atualizar `spec.md` primeiro
- [ ] Entrada no `DECISIONS.md` (D-007): o que mudou, por quê, o que quebrou, tasks afetadas
- [ ] Rodar `spec-adversary` na spec nova; decisões BLOQUEANTES → spec + `DECISIONS.md` antes do código
- [ ] Atualizar `plan.md` se a arquitetura/DT mudar (`docs(plan)`)
- [ ] Novas tasks a partir de **T-022** na Fase 5 do `tasks.md` (+ tasks antigas reabertas, se houver); `docs(tasks)`
- [ ] Executar cada uma com `/task T-NNN`; contar quantas foram reexecução de task vs. edição manual (bônus da rubrica)
- [ ] Implementar com commits rastreáveis; todos os testes verdes
- [ ] Anotar hora de fim e nº de arquivos tocados na mão
- [ ] `/export` da sessão + commit

## Fase 4 — Dia 2, tarde: fechamento

### `docs/RELATORIO.md` (4 Ds + envelope, com evidências)
- [ ] **Delegação** — o que você fez vs. o Claude, e por quê
- [ ] **Descrição** — 1 requisito: primeira versão vs. final na spec (citar commits)
- [ ] **Discernimento** — ≥1 erro concreto do Claude que você pegou, com link para a sessão exportada (sem isso = zero)
- [ ] **Diligência** — o que verificou, o que aceitou sem verificar e o custo
- [ ] **Envelope** — arquivos tocados, tempo, o que a spec facilitou/atrapalhou
- [ ] Explicar os 2 commits iniciais sem task (setup e export)

### Checagem final
- [ ] `git log` legível: todo commit com task ou `docs(...)`
- [ ] Rastreabilidade fecha: RF → task → commit → teste
- [ ] Testes passando a partir de um clone limpo, seguindo o README
- [ ] `docs/sessions/` com um export por sessão
- [ ] `/export` final + commit + push
- [ ] Enviar link do fork no formulário **até 18h**
