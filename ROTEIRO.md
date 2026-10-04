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
- [x] "Convenções de código" e "Fora de escopo" preenchidos a partir do plan (DT-001…DT-009) e da spec seção 3 — `30dd977 docs(claude)`

- [x] `/export` da sessão + commit — sessões 05 a 09 (`docs/sessions/`)

## Fase 2 — Dia 1, tarde: implementar guiado pelas tasks

Avaliação em 2026-10-02 09:50 (antes do envelope): T-001…T-021 concluídas, 649 testes passando, ruff limpo.

- [x] Esqueleto da CLI: `uv run reembolso calcular --input X --output Y` — T-019 `00cf730`; exemplo roda com exit 0
- [x] Executar task por task (teste + código + commit com `T-00N`) — 21 tasks, cada uma com commit `feat|test|chore(T-NNN)` + `docs(tasks): conclui` + hash preenchido em `tasks.md`
- [x] Ler o diff de cada entrega do Claude antes de aceitar; rodar testes — skill `/task` + `revisor-de-task` em 15 tasks de regra (`docs/reviews/`); hooks `pre-commit`/`commit-msg` ativos
- [x] Ao descobrir lacuna na spec: parar → corrigir spec → `DECISIONS.md` → seguir — spec 1.8 (D-005, durante T-003) e 1.9 (D-006, durante T-006/T-008), sempre spec → plan → tasks → código
- [x] Teste de ponta a ponta com `exemplos/despesas-exemplo.json` — T-020 `45f014f` (tabela da seção 9 transcrita à mão + determinismo)
- [x] Rastreabilidade automática RN/casos de borda → testes — T-021 `672cc34`; tabela de Cobertura preenchida
- [x] `README.md` do projeto (como rodar, como testar) substituindo o atual — `66362be docs(readme)`; comandos conferidos num clone limpo (exemplo exit 0, JSON inválido exit 1, uso exit 2, 649 testes)
- [x] Sistema base funcionando e testado **antes do Dia 2**
- [x] Push de todo o trabalho até aqui para o fork público (`origin/main`)
- [x] `/export` da sessão desta avaliação (sessão 33) + commit — `2a9ee34`

### Anotações para o relatório (coletadas até aqui)
- Revisões BLOQUEADAS pelo `revisor-de-task`: T-003 e T-007 (1× cada, na primeira rodada) — candidatas a **Discernimento** (o que o Claude entregou, o que o revisor pegou, o que foi corrigido); ver `docs/reviews/T-003.md`, `docs/reviews/T-007.md` e sessões 13 e 17.
- Mudanças de spec durante a implementação: D-005 (normalização) e D-006 (forma do arquivo) — candidatas a **Descrição**/Diligência.
- Commits sem task a explicar: `994a491 chore:` (estrutura inicial) e `683f161 docs:` (export da sessão 01), anteriores ao hook `commit-msg`.
- Versões da spec puladas (1.4, 1.5, 1.7): explicar no relatório que foram intermediárias dentro de D-004/D-005, ou citar isso no próprio `DECISIONS.md`.
- Tasks estruturais sem revisão (T-001, T-004, T-005, T-006, T-019, T-021) — dispensa prevista no `CLAUDE.md`.
- Ressalvas dos revisores marcadas como opcionais e não aplicadas: levantar uma vez para o relatório (Diligência: "o que aceitei sem verificar").
- Sessão 33: `/task T-022` pedida sem a task existir — o fluxo parou em vez de inventar (exemplo de guarda-corpo funcionando).

## Fase 3 — Dia 2, ~10h: o envelope (20 pts)

Aberto em 02/10 às 19:51 (não às ~10h previstas); planejamento retomado só em 04/10, depois de interrupção por falta de acesso à assinatura (sessão 38).

- [x] Anotar hora de início e o hash de partida — `edeeb2d`, 02/10 19:51 (registrado na D-007)
- [x] Ler a mudança e mapear o impacto — sessão 37; arquivos do envelope em `exemplos/envelope/`
- [x] Atualizar `spec.md` primeiro — spec 2.0 `9f993c5` (RN-014 a RN-016, AMB-020 a AMB-031, seção 7 com 100 casos, seção 9 com três arquivos)
- [x] Entrada no `DECISIONS.md` (D-007) — o que mudou, o que invalidou, 9 tasks antigas afetadas
- [x] `spec-adversary` na spec nova — 3 rodadas (17 + 10 + 3 pontos, 30 decisões) antes do código
- [x] `plan.md` 2.0 (DT-011 a DT-016) e tasks da Fase 5 — `eb47e11`; correção da DT-012 em `7535999`
- [x] Tasks novas T-022…T-034 (antigas substituídas por tasks novas, não reabertas)
- [x] Executar cada uma com `/task T-NNN` — 13 tasks, 10 revisões (1 APROVADO, 9 COM RESSALVAS, 0 BLOQUEADO); aceite com os três arquivos na T-033 `b1f1708`; pendências zeradas na T-034 `e0d9bfa`
- [x] Contagem reexecução vs. edição manual — 0 arquivos editados na mão; todo código dentro de task (RELATORIO, "O envelope")
- [x] Hora de fim — envelope absorvido em 04/10 16:02 (~3h20 de trabalho efetivo)
- [x] `/export` de cada sessão no commit de fim de bloco — sessões 37 a 52

### Fase 6 — Revisão adversarial da spec final (não prevista no roteiro original)
- [x] `spec-adversary` na spec 2.0 implementada → spec 2.1 + D-008 — `d725054` (7 + 4 pontos)
- [x] T-035 — janela da cotação até D-4 e `descricao` de qualquer tipo — `436d6c7`
- [x] T-036 — CLI recusa argumento repetido e prefixo abreviado; `PENDENTES` apagado (105 casos cobertos) — `2594725`
- [x] README com `--politica`/`--cambio` e totais dos três exemplos — `5f429a6`
- [x] Sessões 53 a 56 exportadas

### Fase 7 — Correção vinda do levantamento do relatório
- [x] Divergência DT-012 × código (saldo do limite e totais fora do `contexto_exato()`) achada no levantamento → decisão registrada no RELATORIO — `8674de6`
- [x] T-037 — saldo do limite e totais no contexto exato — `80639e1`, revisão em `docs/reviews/T-037.md`, sessão 58 exportada em `80dc88b`

**Estado em 2026-10-04 20:06 (`80dc88b`):** T-001…T-037 concluídas, 1043 testes passando, ruff limpo, spec 2.1, D-001…D-008, 58 sessões, 26 pareceres em `docs/reviews/`, 38 commits `T-NNN`. **`main` está 38 commits à frente de `origin/main`** (último push: `9f993c5`).

## Fase 4 — Dia 2, tarde: fechamento

### `docs/RELATORIO.md` (4 Ds + envelope, com evidências)
- [x] Levantamento de evidências do Dia 1 no rascunho — `112d565`
- [x] **Delegação** — tabela do que fiz vs. o Claude — `76fb384`
- [x] **Descrição** — requisito da viagem (RN-010), `c8bcad9` → `d35f68d` → `bdb1eec`, implementado na T-018
- [x] **Discernimento** — 4 casos (seção 9 em viagem, normalização D-005, teste fraco da T-014, número errado no README) com links para as sessões
- [x] **Diligência** — procedimento, números, o que aceitei sem verificar
- [x] **Envelope** — hash de partida, 0 arquivos na mão, tempos, diff de absorção, o que absorveu/resistiu — `8674de6`
- [x] Explicar os 2 commits iniciais sem task (setup e export) — seção Fechamento
- [x] Atualizar números que ficaram para trás com a T-037 (Diligência: 37 tasks, 38 commits `T-NNN`, 1043 testes, 26 revisões, 60 sessões)
- [x] Fechar o "Ponto em aberto" do envelope: registrar que a T-037 foi feita (`80639e1`) e o resultado da revisão
- [x] Releitura final do relatório inteiro (coerência dos números entre seções)

### Checagem final
- [x] `git log` legível: todo commit com task ou `docs(...)` — conferido em 04/10: só `994a491` e `683f161` fora do padrão, já explicados
- [x] Rastreabilidade fecha: RN → task → commit → teste (`test_rastreabilidade.py` verde, tabela de Cobertura em `tasks.md`)
- [x] Testes passando a partir de um clone limpo, seguindo o README (os três exemplos com `--politica`/`--cambio`)
- [x] `docs/sessions/` com um export por sessão (01 a 61, sem lacuna)
- [x] `/export` final (sessão 60) + commit de fim de bloco
- [x] **Push** do commit final (`9ee57e7`)
- [x] Confirmar no GitHub que o fork público mostra o último commit (conferido pela API: público, `main` em `9ee57e7`)
- [x] Enviar link do fork no formulário (2026-10-04)
