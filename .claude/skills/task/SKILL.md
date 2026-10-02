---
name: task
description: Executa uma task do tasks.md seguindo o fluxo padronizado do projeto — testes derivados da spec primeiro, implementação só no escopo da task, pytest + ruff, revisão independente, resumo para aprovação humana e só então commit e marcação da task. Use quando o usuário pedir para executar/implementar uma task (ex. "/task T-004", "faz a próxima task").
argument-hint: "[T-NNN]"
---

# Executar uma task

Task solicitada: `$ARGUMENTS`

Arquivos de referência:
- Tasks: `specs/001-motor-reembolso/tasks.md`
- Spec: `specs/001-motor-reembolso/spec.md`
- Decisões: `specs/001-motor-reembolso/DECISIONS.md`
- Plano (stack, estrutura, estratégia de testes): `specs/001-motor-reembolso/plan.md`

## Regras que valem durante toda a execução

- **Não alterar a spec** (`spec.md`, `DECISIONS.md`) durante a task. Mudança de spec é um passo separado, feito com o humano, com commit `docs(spec)` próprio.
- **Decisão ausente ou ambígua na spec → parar e perguntar.** Não escolher uma interpretação "razoável" e seguir. Descreva a lacuna, o cenário concreto em que ela muda o resultado e as leituras possíveis, e aguarde.
- **Não inventar requisitos.** Toda condição, constante, limite, arredondamento, ordenação, filtro ou mensagem no código precisa de um trecho da spec que a determine.
- **Escopo fechado.** Implementar só o que a task descreve. Se notar algo necessário fora dela, registre como lacuna no resumo — não implemente.
- **Testes vêm da spec, não do código.** O valor esperado de cada teste é calculado à mão a partir da spec e dos critérios de aceite, nunca copiado da saída do programa.
- **"Todos os testes passaram" não prova correção.** Prova apenas que o código concorda com os testes. A correção vem de os testes representarem a spec — por isso os passos 4, 5 e 9 existem.

## Fluxo

### 1. Selecionar e ler a task
- Se `$ARGUMENTS` trouxer um ID, use-o. Se vier vazio, identifique a primeira task não marcada (`- [ ]`) em `tasks.md`, mostre-a ao usuário e **confirme antes de seguir**.
- Leia o item completo: o que faz, `Atende:` (RN-/AMB-), `Aceite:`.
- Verifique dependências: tasks anteriores de que ela depende estão concluídas? Se não, pare e avise.
- Se a task já estiver marcada `[x]`, pare e avise.

### 2. Ler as regras da spec relacionadas
- Leia cada `RN-`/`AMB-` citado, a seção de **ordem de aplicação das regras**, os **casos de borda** e o **schema de saída** quando a task os tocar.
- Leia as entradas do `DECISIONS.md` que afetam essas regras e confirme que a spec já as reflete.
- Se a task cita uma regra que não existe na spec, ou a regra não determina o resultado de algum caso que a task precisa tratar → **pare e pergunte**.

### 3. Identificar os critérios de aceite
- Liste, em itens verificáveis, o que precisa ser verdade ao final: o `Aceite:` da task + os casos de borda da spec ligados às regras citadas (fronteira exata, fronteira ± 0,01, valor inválido etc.).
- Se o `Aceite:` for vago ("funciona corretamente"), pare e pergunte como verificá-lo.

### 4. Escrever ou revisar os testes primeiro
- Um teste por comportamento da spec. Nome e docstring citam a regra: ex. `test_rn003_limite_diario_alimentacao_corta_excedente`, docstring `"""RN-003 / AMB-002: ..."""`.
- Em cada teste, deixe o cálculo do esperado visível (comentário curto com a conta feita a partir da spec).
- Cubra as fronteiras listadas no passo 3, não só o caminho feliz.
- Se já existirem testes para essas regras, revise se ainda batem com a spec atual.

### 5. Executar os testes antes de implementar (quando aplicável)
- Rode só os testes novos: `uv run pytest -q <arquivo>::<teste>`.
- Esperado: **falhar pelo motivo certo** (asserção sobre o comportamento ausente). Falha por erro de import/nome de algo que a task vai criar é aceitável; anote.
- Se um teste novo **passar antes da implementação**: ou o comportamento já existe (confira se a task está redundante) ou o teste é fraco. Investigue e corrija antes de seguir.
- Não aplicável a tasks puramente estruturais (setup, scaffolding) — diga isso no resumo.

### 6. Implementar somente o escopo da task
- Siga a arquitetura e as convenções do `plan.md` e do `CLAUDE.md`.
- Não altere comportamento de regras de outras tasks. Refatoração fora do escopo: registre como sugestão, não faça.

### 7. Executar a suíte relevante
- Rode os testes da task e os testes das regras vizinhas que podem ter sido afetadas. Corrija até passarem — corrigindo o **código**, não o esperado do teste (a menos que o esperado esteja provadamente errado em relação à spec; nesse caso, explique no resumo).

### 8. Executar pytest e ruff completos
- `uv run pytest -q` (suíte inteira) e `uv run ruff check .`.
- Ambos precisam estar verdes. Guarde a saída resumida para o relatório.

### 9. Verificar o diff
- `git status` e `git diff` (inclua arquivos novos não rastreados).
- Confira: só arquivos esperados foram tocados; nenhuma alteração em `spec.md`/`DECISIONS.md`; nenhuma regra sem trecho correspondente na spec; nada de código morto, prints de debug ou TODO solto.
- **Task de regra de negócio:** invoque o subagente `revisor-de-task` passando **apenas o ID da task** (sem explicar a implementação). Ele é somente leitura e devolve um relatório; **salve-o sem editar** em `docs/reviews/T-NNN.md` (se já existir, acrescente ao final como "Revisão N").
  - **BLOQUEADO** por problema de código/teste → corrija e volte ao passo 7; rode o revisor de novo.
  - **BLOQUEADO** por item em "Decisões necessárias" → **pare**: isso exige decisão humana e mudança de spec fora da task. Leve ao resumo.
  - **APROVADO COM RESSALVAS** → corrija o que for do escopo da task; o que não for, leve ao resumo para o humano decidir.
  - Tasks estruturais (setup, CLI, leitura/escrita de JSON) dispensam o revisor; diga no resumo.

### 10. Resumir para revisão humana — e parar
Apresente exatamente estas seções e **aguarde autorização explícita** antes do commit:

```
## Resumo — T-NNN: <título>

**Arquivos alterados:** <lista, com novo/modificado>
**Testes criados/alterados:** <nome do teste → regra RN-/AMB- que verifica>
**Testes executados antes da implementação:** <quais, e se falharam pelo motivo certo | não aplicável: motivo>
**Testes executados depois:** <comandos>
**pytest:** <N passed, M failed — resumo>
**ruff:** <limpo | problemas>
**Revisão independente:** <APROVADO / APROVADO COM RESSALVAS / BLOQUEADO, problemas por severidade, decisões necessárias, docs/reviews/T-NNN.md | dispensada: motivo>
**Decisões ou interpretações realizadas:** <toda escolha que não estava literal na spec — idealmente "nenhuma"; qualquer item aqui é candidato a bug de spec>
**Lacunas ou dúvidas:** <o que a spec não cobre, o que ficou fora do escopo, riscos>
**Commit proposto:** `<tipo>(T-NNN): <descrição>`
```

Se houver qualquer item em "Decisões ou interpretações" ou em "Decisões necessárias" do revisor, destaque que a spec precisa ser atualizada **antes** do commit.

### 11. Commit (só após a autorização)
- `git add` apenas os arquivos da task (+ `docs/reviews/T-NNN.md`, se existir).
- Mensagem no padrão do projeto: `feat|test|fix|refactor(T-NNN): <descrição>`. O hook `commit-msg` valida o formato e se a task existe; o `pre-commit` roda ruff + pytest.
- Se um hook bloquear: corrija a causa. **Nunca** use `--no-verify`.

### 12. Marcar a task como concluída e fechar o bloco (só após o commit)
- Em `tasks.md`: troque `- [ ]` por `- [x]` na task e preencha `**Commit:**` com o hash curto do passo 11.
- **Antes do commit, pare e peça o export da sessão** com o comando pronto:
  `/export docs/sessions/NN-<descricao-curta>.md` (NN = último número em `docs/sessions/` + 1).
  Aguarde o usuário confirmar que exportou; não commite antes disso.
- Commit único com `tasks.md` + o export: `docs(tasks): conclui T-NNN`. O hook `commit-msg`
  bloqueia commit de fim de bloco sem um `docs/sessions/NN-*.md` novo staged.
- **Não inicie a próxima task** sem novo pedido.
