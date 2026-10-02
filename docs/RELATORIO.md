# Relatório — Desafio SDD

**Aluno:** Rafael Teixeira Martins · **Repositório:** https://github.com/rafaeltxm/sdd-desafio · **Data:** 2026-10-02

> **RASCUNHO.** Os fatos (hashes, arquivos, linhas de sessão) foram levantados
> do repositório. Os trechos marcados com ✍️ são julgamento e precisam ser
> escritos por mim. Sessões citadas como `docs/sessions/<arquivo>`, linha N.

---

## Delegação

**A divisão:**

| Atividade | Quem | Evidência |
|---|---|---|
| Identificar ambiguidades | Claude levantou a lista a partir da política × `despesas-exemplo.json`; o `spec-adversary` achou as que sobraram a cada versão | `05-spec-e-revisoes-adversariais.md` l. 1005–1417; D-001 a D-006 |
| Decidir as ambiguidades | Eu, uma a uma, entre opções com exemplo concreto | `05-…` l. 1460–2034 (respostas "A, recusar pela data da despesa", "2a exigir nota, 2b diária e dia seguinte"…) |
| Escrever a spec | Claude redigiu; eu decidi e revisei | `c8bcad9` → `cdebcde` (spec 1.0 → 1.9) |
| Desenhar a arquitetura | Claude propôs (`plan.md`); eu aprovei | `bf1df44`; `07-plan-e-spec-v1.6.md` l. 9–640 |
| Implementar | Claude, pela skill `/task`, uma task por sessão | T-001…T-021, sessões 11–32 |
| Escrever testes | Claude, com o esperado calculado à mão a partir da spec (regra da skill `/task`); conferidos pelo `revisor-de-task` | `docs/reviews/`; `tests/test_exemplo.py` (seção 9 transcrita à mão) |
| Absorver o envelope | ✍️ (Dia 2) | |

**Usei subagentes / skills / MCP / hooks?** Sim:
- **Subagente `spec-adversary`** (`.claude/agents/spec-adversary.md`, `42f9336`): só leitura, devolve problemas numerados com perguntas; as decisões ficam comigo. Rodou sobre cada versão da spec (sessões 05, 06, 07, 13, 18). Achou o erro da seção 9 (Discernimento, caso 1) e 2 bloqueantes da 1.9 (D-006).
- **Subagente `revisor-de-task`** (`.claude/agents/revisor-de-task.md`, `56018a0`): recebe só o ID da task, sem explicação da implementação. Rodou nas 15 tasks de regra: resultado final 13 APROVADO COM RESSALVAS e 2 APROVADO; 2 delas (T-003, T-007) foram BLOQUEADAS na primeira rodada e só passaram depois de correção. Pareceres em `docs/reviews/`.
- **Skill `/task`** (`.claude/skills/task/SKILL.md`, `86eee2b`): fluxo fixo teste-primeiro → implementação → pytest/ruff → revisor → resumo → **para** para aprovação antes do commit.
- **Git hooks** (`.githooks/`, `f717aed`, `3c82fc1`): `pre-commit` (ruff + pytest), `commit-msg` (formato + T-NNN existente em `tasks.md`), `post-commit` (lembrete de export). Hook do Claude Code `.claude/hooks/lembrete-export.sh` (`fc9c429`).
- **Memória do Claude Code:** "sinalizar decisões que quebram o formato de entrada fixo", criada a meu pedido (`05-…` l. 170).

✍️ **Onde deleguei e me arrependi:**

✍️ **Onde não deleguei e deveria ter delegado:**

✍️ **Valeu a pena?** (pistas: o revisor pegou 2 bloqueios reais; a spec teve 7 versões commitadas (1.0, 1.1, 1.2, 1.3, 1.6, 1.8, 1.9) — custo vs. ganho)

---

## Descrição

**Requisito escolhido:** política item 6, "Colaborador em viagem tem limites ampliados em 50%" (AMB-004 / RN-010).

**Versão 1 (spec 1.0, `c8bcad9`):**
> **Decisão:** uma data está em viagem se há na entrada uma hospedagem válida (não recusada antes do limite) nessa data.
> **Justificativa:** hospedagem é a única evidência objetiva de viagem nos dados; uma hospedagem recusada não comprova a viagem.

**Versão final (spec 1.9):**
> **Decisão:** uma hospedagem **com nota fiscal** que não foi recusada antes do limite comprova viagem na data dela e no dia seguinte.
> **Justificativa:** hospedagem é a única evidência objetiva de viagem nos dados, e exigir a nota a torna verificável na conferência humana; uma diária é uma noite, então o colaborador acorda em viagem no dia seguinte. A exigência **não** elimina o abuso: o sistema confia no `tem_nota_fiscal` declarado (seção 3), então uma hospedagem irrisória com nota declarada ainda amplia os limites de D e D+1 (risco aceito, seção 10).

**O que estava ambíguo / como mudou:**
- **1.0 → 1.1 (D-001, `d35f68d`), itens 2a e 2b:** qualquer hospedagem → só **com nota**; só a data da diária → **D e D+1**. Gatilho: o d-011 do exemplo (café no hotel em 15/07, depois da diária de 14/07) não ficava em viagem.
- **1.1 → 1.2 (D-002, `bdb1eec`), item 2:** a justificativa da 1.1 dizia que exigir nota fechava a brecha da hospedagem irrisória — errado, a nota é só declarada. Regra mantida, justificativa corrigida, risco aceito.
- Na mesma rodada perguntei se uma flag `em_viagem` na entrada resolveria; não, porque o formato de entrada é fixo e os casos ocultos não a trazem. Ficou como evolução recomendada (spec seção 3). `05-…` l. 3422–3454.
- **1.1 → 1.2 (D-002), item 1:** duplicata de hospedagem em que só uma cópia tem nota fazia a viagem depender da ordem do arquivo → a original passou a ser a primeira **com nota**.

✍️ **Como percebi:** (minha versão; pistas: o 2a/2b veio da análise dos dados do exemplo; o abuso e a duplicata vieram do `spec-adversary`)

**Commits da mudança:** `c8bcad9` → `d35f68d` → `bdb1eec`; implementado em `b1cb651` (T-018), testes em `tests/test_rn010_viagem.py`.

---

## Discernimento

### Caso 1 — Seção 9 dizia que nenhuma data do exemplo ficava em viagem

**O que ele propôs:** na spec 1.0 (`c8bcad9`, seção 9), o Claude escreveu "Resultado esperado para `exemplos/despesas-exemplo.json` (nenhuma data do exemplo fica em viagem)".
**Por que estava errado:** pela própria RN-010 da mesma versão, a hospedagem d-010 de 14/07 coloca 14/07 em viagem. A tabela de aceite contradizia a regra.
**Como foi detectado:** a primeira rodada do `spec-adversary` sobre a 1.0 (`05-…` l. 1227). O Claude admitiu o erro (`05-…` l. 1302–1305).
**O que eu fiz:** corrigido na 1.1 (D-001, item 11): 14/07 e 15/07 em viagem, d-011 com limite 90,00; valores e totais inalterados.
**Evidência:** `docs/sessions/05-spec-e-revisoes-adversariais.md` l. 1227 e 1302; `DECISIONS.md` D-001 item 11.
✍️ Observação honesta: quem pegou foi o subagente que eu configurei, não eu lendo a tabela.

### Caso 2 — Solução desnecessariamente complexa na normalização (D-005)

**O que ele propôs:** com a spec 1.7 bloqueada (quais caracteres contam como hífen e espaço), o Claude recomendou definir listas por categoria Unicode: traços da categoria Pd, espaço pela propriedade White_Space, exceções para U+2212, U+200B e BOM (`13-task-t003-normalizacao.md` l. 1104–1135).
**Por que estava errado:** trocava uma lista indefinida por outra mais longa; cada caractere esquecido viraria um novo achado e a regra não era verificável sem tabela Unicode.
**Como foi detectado:** eu perguntei "não tem como limpar tudo que entre de caracteres especial?" (l. 1163). O Claude respondeu "Dá, sim. E é mais simples que a minha recomendação" (l. 1165).
**O que eu fiz:** adotei "só letras e algarismos contam" + texto vazio após normalização é `entrada_invalida`; spec 1.8 (`6cc8554`, D-005), plan 1.1, tasks 1.1, T-003 (`aaf201a`).
**Evidência:** `docs/sessions/13-task-t003-normalizacao.md` l. 1104–1250.

### Caso 3 — Teste errado / fraco escrito pelo próprio agente

- **T-014:** o Claude escreveu "fora do período não consome limite", que não podia falhar (data fora do período nunca divide saldo com uma de dentro) e o removeu antes do commit — `25-t014-periodo.md` l. 29 e 365.
- **T-011:** o revisor apontou que nenhum teste provava a posição de uma despesa inválida depois de uma válida (RN-001) — `docs/reviews/T-011.md`.
- **T-007:** código perdia o ponto separador quando o caminho tinha chave vazia `""` (aviso `x` em vez de `.x`), BLOQUEADO pelo revisor — `docs/reviews/T-007.md` revisão 1, problema 1.

### Caso 4 — Erro numérico no README (sessão 33)
O Claude escreveu "total reembolsado R$ 1.276,41" (é o glosado; reembolsado é 585,43). Pego pelo próprio Claude ao conferir a saída num clone limpo, antes do commit — `33-avaliacao-fase-2-readme-claude.md` l. 439.

✍️ **Padrão que eu notei:** (pistas: os erros se concentraram em afirmações sobre o exemplo — seção 9, README — e em justificativas que prometiam mais do que a regra entregava — D-002 item 2; quem pegou foi quase sempre um verificador separado do autor)

---

## Diligência

**Procedimento (o que o fluxo impunha):** cada task pela skill `/task`: testes primeiro, falhando pelo motivo certo; pytest + ruff completos; `revisor-de-task` nas tasks de regra; resumo com "Decisões ou interpretações realizadas"; commit só depois do meu "pode commitar". Hooks bloqueiam commit com teste vermelho ou mensagem fora do padrão.

**Números:** 21 tasks, 22 commits `T-NNN`, 649 testes, 15 revisões independentes, 33 sessões exportadas, 6 mudanças de spec registradas (D-001 a D-006).

**Exemplo de pergunta antes de aceitar:** T-018, proteção contra 9999-12-31 — perguntei "faz sentido registrar?" antes de commitar (`29-t018-viagem.md` l. 608).

**O que aceitei sem verificar direito, e o que me custou:**
- **T-006** (leitura de JSON) era "estrutura" e dispensou o revisor. A verificação de escape inválido só olhava os valores que valeram; o problema apareceu na revisão da **T-007** e virou spec 1.9 (D-006, 9 pontos) + `afe14cc fix(T-006)`. Custo registrado na D-006: 4 documentos, uma função, um teste, três rodadas do `spec-adversary`.
- Ressalvas BAIXA dos revisores marcadas como opcionais não foram aplicadas (ex.: `docs/reviews/T-007.md` revisão 2, problema 1).
- ✍️ **Li o diff inteiro em que porcentagem das entregas?** (honestidade: as respostas nas sessões 19–32 são quase todas "pode commitar")

✍️ **Testes: quem escreveu, e como você sabe que eles testam a coisa certa?** (pistas: o mesmo agente escreveu código e teste; contrapesos — esperado calculado à mão com a conta em comentário, revisor independente, `test_exemplo.py` com a seção 9 transcrita à mão, `test_rastreabilidade.py` falha se uma RN ou caso de borda ficar sem teste)

---

## O envelope

✍️ Dia 2. Hash de partida: `2a9ee34`.

**Quantos arquivos toquei na mão:**
**Quanto tempo levou:**
**Diff de absorção:** (`git diff 2a9ee34 HEAD --stat`)
**Reexecução de tasks vs. edição manual:**
**Absorveu de graça:**
**Resistiu:**
**Ordem em que fiz:**
**Se eu tivesse escrito a spec original sabendo desta mudança:**
**O que a spec me poupou, em concreto:**

---

## Fechamento

**Commits sem task:** `994a491 chore:` (estrutura inicial do template) e `683f161 docs:` (export da sessão 01), feitos antes de existir o hook `commit-msg` (`f717aed`). Não reescrevi o histórico.

**Versões da spec puladas (1.4, 1.5, 1.7):** foram rodadas intermediárias nunca commitadas, absorvidas na entrada seguinte do `DECISIONS.md` (1.4–1.5 na D-004, 1.7 na D-005; `13-…` l. 1250).

✍️ **Para qual tamanho de projeto isto valeu a pena?**
✍️ **Para qual não valeria?**
✍️ **O que eu faria diferente:**
✍️ **A coisa mais desconfortável que aprendi sobre como eu trabalho com IA:**
