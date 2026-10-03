 ▐▛███▛█   Claude Code v2.1.287
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~/repo/sdd-desafio

  Opus 5.5 is now your default model and it draws down usage faster than Sonnet 5. Switch anytime with /model.

❯ durante o processo percebi que sempre após um commit eu gerava um export e    
  depois commitava novamente, gerando dois commits. tem como corrigir os hooks  
  e subagents pra só commitar após me solicitar o export, assim o commit é      
  sempre feito uma vez só com tudo                                              

  Ran 2 shell commands (ctrl+o to expand)

⏺ Update(.githooks/commit-msg)
  ⎿  Added 23 lines, removed 2 lines
      19      echo "commit-msg: ✗ $task não existe em $tasks_file. Crie a
           task antes do commit."
      20      exit 1
      21    fi
      22 -  exit 0                                                       
      22 +  [[ "$subject" =~ ^chore ]] || exit 0                         
      23  fi
      24  
      25 -if [[ "$subject" =~ $docs_re ]]; then exit 0; fi               
      25 +if [[ "$subject" =~ $docs_re ]] || [[ "$subject" =~ $chore_re ]
         +]; then                                                        
      26 +  # Fim de bloco = qualquer commit exceto feat|test|fix|refacto
         +r(T-NNN) (meio da task)                                        
      27 +  # e docs(sessions) (export avulso). O export da sessão vai no
         + mesmo commit que fecha o bloco.                               
      28 +  # Commit no meio de um bloco que não é de código: SEM_EXPORT=
         +1 git commit ...                                               
      29 +  if [[ "$subject" == docs\(sessions\):* ]] || [ "${SEM_EXPORT:
         +-}" = "1" ]; then exit 0; fi                                   
      30 +  if git diff --cached --name-only --diff-filter=A | grep -qE '
         +^docs/sessions/[0-9]{2}-.+\.md$'; then                         
      31 +    exit 0                                                     
      32 +  fi                                                           
      33 +  last=$(ls docs/sessions/ 2>/dev/null | grep -oE '^[0-9]{2}' |
         + sort -n | tail -1)                                            
      34 +  next=$(printf '%02d' $((10#${last:-0} + 1)))                 
      35 +  cat <<MSG                                                    
      36 +commit-msg: ✗ commit de fim de bloco sem o export da sessão:   
      37 +  "$subject"                                                   
      38  
      39 +Peça o export ao usuário e inclua-o neste mesmo commit:        
      40 +  /export docs/sessions/${next}-<descricao-curta>.md           
      41 +  git add docs/sessions/${next}-*.md                           
      42 +                                                               
      43 +Se este commit não fecha o bloco de trabalho: SEM_EXPORT=1 git 
         +commit ...                                                     
      44 +MSG                                                            
      45 +  exit 1                                                       
      46 +fi                                                             
      47 +                                                               
      48  cat <<MSG
      49  commit-msg: ✗ mensagem fora do padrão:
      50    "$subject"

  Ran 1 shell command (ctrl+o to expand)

⏺ Não tenho permissão para remover os hooks de lembrete (post-commit,
  .claude/hooks/lembrete-export.sh e .claude/settings.json), então isso fica por
  sua conta. Vou seguir com a skill, o CLAUDE.md e a memória.

⏺ Update(.claude/skills/task/SKILL.md)
  ⎿  Added 7 lines, removed 3 lines
       97  - Mensagem no padrão do projeto: `feat|test|fix|refactor(T-NNN
           ): <descrição>`. O hook `commit-msg` valida o formato e se a t
           ask existe; o `pre-commit` roda ruff + pytest.
       98  - Se um hook bloquear: corrija a causa. **Nunca** use `--no-ve
           rify`.
       99  
      100 -### 12. Marcar a task como concluída (só após o commit)       
      100 +### 12. Marcar a task como concluída e fechar o bloco (só após
          + o commit)                                                    
      101  - Em `tasks.md`: troque `- [ ]` por `- [x]` na task e preencha
            `**Commit:**` com o hash curto do passo 11.
      102 -- Commit separado: `docs(tasks): conclui T-NNN`.              
      103 -- Repasse ao usuário o lembrete de export do hook `post-commit
          -` e **não inicie a próxima task** sem novo pedido.            
      102 +- **Antes do commit, pare e peça o export da sessão** com o co
          +mando pronto:                                                 
      103 +  `/export docs/sessions/NN-<descricao-curta>.md` (NN = último
          + número em `docs/sessions/` + 1).                             
      104 +  Aguarde o usuário confirmar que exportou; não commite antes 
          +disso.                                                        
      105 +- Commit único com `tasks.md` + o export: `docs(tasks): conclu
          +i T-NNN`. O hook `commit-msg`                                 
      106 +  bloqueia commit de fim de bloco sem um `docs/sessions/NN-*.m
          +d` novo staged.                                               
      107 +- **Não inicie a próxima task** sem novo pedido.              

⏺ Update(CLAUDE.md)
  ⎿  Added 6 lines, removed 5 lines
      53  Git hooks em `.githooks/` (ativar uma vez por clone: `git confi
          g core.hooksPath .githooks`):
      54  - `pre-commit` — `ruff check` + `pytest`; bloqueia se falhar.
      55  - `commit-msg` — valida o padrão de mensagem e que o `T-NNN` ex
          iste em `tasks.md`.
      56 -- `post-commit` — no fim de um bloco (qualquer commit exceto `f
         -eat|test|fix|refactor(T-NNN)`                                  
      57 -  e `docs(sessions)`), lembra de exportar a sessão para `docs/s
         -essions/NN-*.md`. O hook                                       
      58 -  `.claude/hooks/lembrete-export.sh` (em `.claude/settings.json
         -`) mostra o mesmo lembrete                                     
      59 -  ao usuário quando o commit é feito pelo Claude. Ao vê-lo, não
         - iniciar o próximo bloco                                       
      60 -  sem o usuário.                                               
      56 +- `commit-msg` também exige o export da sessão no commit que fe
         +cha um bloco (qualquer commit                                  
      57 +  exceto `feat|test|fix|refactor(T-NNN)` e `docs(sessions)`): p
         +recisa haver um                                                
      58 +  `docs/sessions/NN-*.md` novo staged. Por isso, **antes** dess
         +e commit, parar e pedir ao                                     
      59 +  usuário `/export docs/sessions/NN-<descricao>.md` (NN = últim
         +o + 1), esperar, e commitar                                    
      60 +  tudo junto, num commit só. Commit que não fecha bloco: `SEM_E
         +XPORT=1 git commit ...`.                                       
      61 +  Depois do commit de fim de bloco, não iniciar o próximo bloco
         + sem o usuário.                                                
      62  
      63  Formatos de commit aceitos: `feat|test|fix|refactor(T-NNN):`,
      64  `docs(spec|plan|tasks|decisions|readme|relatorio|sessions|claud
          e):`,

  Wrote 1 memory (ctrl+o to expand)

⏺ Skill, CLAUDE.md e memória atualizados; agora testo o novo commit-msg com
  mensagens simuladas.

  Ran 1 shell command (ctrl+o to expand)

⏺ Agora o export da sessão vai no mesmo commit que fecha o bloco, em vez de
  gerar um segundo commit docs(sessions). Testei o novo commit-msg com mensagens
  simuladas e todos os casos se comportaram como esperado. Nada foi commitado
  ainda.

  Como fica o fluxo:
  1. feat|test|fix|refactor(T-NNN) continua sendo commitado direto (é o meio da
     task).
  2. No commit que fecha o bloco (ex.: docs(tasks): conclui T-NNN), eu paro e te
     peço /export docs/sessions/NN-<descricao>.md.
  3. Depois que você exportar, faço um commit só com tasks.md + o export.

  O que mudei:
  - .githooks/commit-msg: um commit de fim de bloco (qualquer um, exceto
    feat|test|fix|refactor(T-NNN) e docs(sessions)) agora é bloqueado se não
    houver um docs/sessions/NN-*.md novo staged. A mensagem de erro já traz o
    número da próxima sessão e o comando /export pronto.
    - Para um docs/chore que não fecha bloco, use SEM_EXPORT=1 git commit ....
    - docs(sessions): continua passando, para algum export avulso.
  - .claude/skills/task/SKILL.md, passo 12: marca a task, para e pede o export,
    espera sua confirmação e faz o commit único.
  - CLAUDE.md: a parte sobre o hook post-commit foi trocada pela descrição da
    nova regra.
  - Memória: atualizada para eu pedir o export antes do commit.

  Os subagentes (revisor-de-task e spec-adversary) não precisaram de mudança,
  porque não fazem commit nem falam de export.

  Falta você fazer: o modo automático não me deixou apagar os lembretes antigos,
  que agora ficaram errados (avisam depois do commit). Para removê-los:
  ! git rm .githooks/post-commit .claude/hooks/lembrete-export.sh 
  .claude/settings.json
  O .claude/settings.json só tem a configuração desse hook, então pode ir junto.

  Pela própria regra nova, o commit destas mudanças, por exemplo chore(tooling):
  export da sessão no mesmo commit de fim de bloco, vai precisar do export:
  rode /export docs/sessions/36-<descricao>.md e eu commito tudo junto.

✻ Crunched for 1m 24s · done 7:49 PM

!  git rm .githooks/post-commit .claude/hooks/lembrete-export.sh                
  .claude/settings.json                                                         
  ⎿  rm '.claude/hooks/lembrete-export.sh'
     rm '.claude/settings.json'
     rm '.githooks/post-commit'

⏺ Os três arquivos dos lembretes antigos foram removidos e estão staged. O que
  falta é o commit, que pela regra nova precisa do export junto:

  1. Rode /export docs/sessions/36-<descricao>.md, por exemplo
     36-export-no-commit-de-fim-de-bloco.md.
  2. Me avise e eu faço um commit só com tudo: chore(tooling): export da sessão 
     no mesmo commit de fim de bloco.

  O docs/RELATORIO.md (linha 28) ainda descreve o post-commit e o
  lembrete-export.sh. Como ele cita os commits em que esses hooks entraram,
  deixei como está. Se quiser registrar a mudança no relatório, posso incluir no
  mesmo commit.

✻ Crunched for 3s · done 7:50 PM

❯ /export docs/sessions/36-export-no-commit-de-fim-de-bloco.md                  
  ⎿  Conversation exported to: /Users/rafaeltxm/repo/sdd-desafio/docs/sessions/3
     6-export-no-commit-de-fim-de-bloco.md

❯ feito export                                                                  
  ⎿  1 skill available

  Ran 1 shell command (ctrl+o to expand)

⏺ Commitado como edeeb2d, com tudo em um commit só: o commit-msg novo, a skill
  /task, o CLAUDE.md, os três lembretes antigos removidos e o export da sessão
  36. O novo commit-msg aceitou porque o export estava staged junto, e o working
  tree ficou limpo.

  A partir de agora, no fim de cada bloco eu paro e peço o /export antes de
  commitar. O próximo export será o 37.

✻ Baked for 6s · done 7:50 PM

❯ faz o push                                                                    

  Pushed to main (ctrl+o to expand)

⏺ Push feito: o commit edeeb2d está no origin/main (de 37261f5 para edeeb2d). O
  main local está em dia com o remoto.

✻ Cogitated for 5s · done 7:50 PM

❯ coloquei na raiz do projeto o envelope do dia 2                               

  Ran 3 shell commands (ctrl+o to expand)

⏺ Li o envelope e os quatro arquivos de dados. Antes de mexer em qualquer coisa,
  os dados de partida para o git diff --stat do relatório:

  - Hash de partida: edeeb2d
  - Hora de início: 2026-10-02 19:51

  O que o comunicado pede (A, B e C):
  - A. Política por centro de custo: os limites passam a vir do
    politica-v4.json, com uma tabela por centro de custo e uma padrão. Inclui a
    categoria representacao, hospedagem com limite 0 em CC-ENG-PLATAFORMA e a
    tabela padrão para centro de custo ausente.
  - B. Moeda: campo moeda opcional (BRL quando ausente), convertido pela taxa do
    cambio.json na data da despesa antes de comparar com o limite.
  - C. (opcional) Aprovação manual: item com reembolsável acima de R$ 500 fica
    pendente de aprovação do gestor.

  O que isso quebra na spec atual: a seção 3 (fora de escopo) exclui hoje
  conversão de moeda, a categoria de representação e campos além dos da seção 4.
  Além disso, as constantes fixas em politica.py deixam de ser a fonte da
  política. Vai ser preciso um D-007 e uma nova versão da spec antes de qualquer
  código.

  Ambiguidades que já aparecem nos dados:
  1. Centro de custo ausente: não há regra para quando ele aparece, mas sem a
     categoria. CC-ADM não tem hospedagem e o padrao não tem representacao. Uma
     despesa assim cai na tabela padrão daquela categoria ou é recusada? O caso
     f-003 (representacao em CC-SUPORTE-N2) depende disso.
  2. Data sem taxa:
     - Fim de semana: e-004 é de 18/07, um sábado. Usa a taxa do dia útil
       anterior, do seguinte, ou recusa?
     - Moeda inexistente no cambio.json: e-006 está em GBP.
  3. Conversão: em que momento arredonda (converte e arredonda, ou só no final)?
     E a justificativa precisa mostrar o valor original?
  4. Campos do politica-v4.json que conflitam com a spec:
     - nota_fiscal_obrigatoria_acima_de: confere com a regra atual da spec?
     - acrescimo_em_viagem_percentual: indicação de viagem está fora de escopo
       hoje.
     - periodicidade dia vs diaria: há diferença?
     - vigencia contra a competência.
  5. Hospedagem com várias noites num item: e-007 diz "3 noites" mas tem um
     valor único, e a descricao não é lida.
  6. Categoria desconhecida: e-009 (coworking) deve continuar recusada como
     hoje? Isso precisa ser confirmado contra a spec.
  7. Item C: "acima de R$ 500" é estrito? Vale por item ou pelo total? E muda o
     schema de saída (novo campo de estado).

  O envelope também sugere guardar os quatro arquivos em exemplos/envelope/,
  commitados junto.

  Proposta de próximo passo, seguindo a Fase 3 do ROTEIRO.md:
  1. Mover os arquivos para exemplos/envelope/.
  2. Fazer um mapeamento de impacto, só leitura: quais RN, AMB, casos de borda,
     tabela da seção 9, tasks e testes são afetados.
  3. Te apresentar as decisões em aberto para você tomar.
  4. Depois disso, spec → DECISIONS.md (D-007) → spec-adversary → plan → tasks
     T-022 em diante → código.

  Sigo com os passos 1 e 2?

✻ Baked for 26s · done 7:51 PM

❯ sim, segue com os passos 1 e 2                                                

⏺ Bash(mkdir -p exemplos/envelope && mv 00-ENVELOPE-LACRADO.md cambio.json
      politica-v4.json despesas-envelope.json
      despesas-envelope-cc-desconhecido.json exemplos/enve…)
  ⎿  exemplos:
     despesas-exemplo.json
     envelope
     … +46 lines (ctrl+o to expand)
  ⎿  Deleted 00-ENVELOPE-LACRADO.md (+0 -72)
       1 -# 🔒 ENVELOPE LACRADO                                          
       2 -                                                               
       3 -**Não distribuir antes do Dia 2, 10h.**                        
       4 -Alunos: se você chegou aqui antes da hora, feche. Ler antes que
         -ima o exercício inteiro e você é a única pessoa prejudicada.   
       5 -                                                               
       6 ----                                                            
       7 -                                                               
       8 -## Mudança de requisito — Política de Reembolso v4             
       9 -                                                               
      10 -Bom dia. O RH revisou a política. Vigência imediata, retroativa
         - à competência atual.                                          
      11 -                                                               
      12 -> **Comunicado do RH — Política de Reembolso v4**              
      13 ->                                                              
      14 -> Após auditoria interna, a política deixa de ser única para to
         -da a empresa.                                                  
      15 ->                                                              
      16 -> **A. Limites passam a variar por centro de custo.**          
      17 -> Os limites não são mais constantes. Cada centro de custo tem 
         -a sua tabela, mantida pelo financeiro num arquivo à parte, e el
         -a muda sem aviso. O motor precisa ler a política de fora, não d
         -e dentro do código.                                            
      18 ->                                                              
      19 -> A tabela vigente está em `politica-v4.json`.                 
      20 ->                                                              
      21 -> Observações que o financeiro fez questão de incluir:         
      22 -> - `CC-COMERCIAL` tem uma categoria nova, `representacao`, que
         - não existia na v3 — limite de R$ 300 por dia.                 
      23 -> - `CC-ENG-PLATAFORMA` não reembolsa `hospedagem` de forma alg
         -uma.                                                           
      24 -> - Alguns centros de custo não têm entrada na tabela. Nesse ca
         -so, aplica-se a política padrão.                               
      25 ->                                                              
      26 -> **B. Despesas internacionais.**                              
      27 -> Colaboradores em viagem internacional lançam despesas em moed
         -a estrangeira. A entrada agora pode trazer um campo `moeda` (IS
         -O 4217). Quando ausente, assume-se `BRL`.                      
      28 ->                                                              
      29 -> A conversão usa a **taxa da data da despesa**, não a taxa de 
         -hoje. As taxas estão em `cambio.json`.                         
      30 ->                                                              
      31 -> Os limites da política são sempre em BRL. Uma despesa em EUR 
         -é convertida antes de ser comparada ao limite.                 
      32 ->                                                              
      33 -> **C. (Opcional — só se sobrar tempo) Fila de aprovação manual
         -.**                                                            
      34 -> Itens cujo valor reembolsável passe de R$ 500 não são mais ap
         -rovados automaticamente. Eles entram em estado de pendência agu
         -ardando aprovação do gestor. O resultado deixa de ser apenas um
         - valor: cada item passa a ter um estado.                       
      35 -                                                               
      36 ----                                                            
      37 -                                                               
      38 -## O que se espera de você agora                               
      39 -                                                               
      40 -Nada de heroísmo. O que se avalia é o **caminho**, não a veloci
         -dade:                                                          
     … 32 more lines (ctrl+o to expand)
  ⎿  Deleted cambio.json (+0 -19)
       1 -{                                                              
       2 -  "moeda_base": "BRL",                                         
       3 -  "fonte": "Banco Central - PTAX de fechamento",               
       4 -  "observacao": "Cotacoes publicadas apenas em dias uteis banca
         -rios.",                                                        
       5 -  "taxas": {                                                   
       6 -    "2026-07-13": { "USD": 5.42, "EUR": 5.91 },                
       7 -    "2026-07-14": { "USD": 5.44, "EUR": 5.93 },                
       8 -    "2026-07-15": { "USD": 5.39, "EUR": 5.88 },                
       9 -    "2026-07-16": { "USD": 5.41, "EUR": 5.90 },                
      10 -    "2026-07-17": { "USD": 5.47, "EUR": 5.96 },                
      11 -    "2026-07-20": { "USD": 5.50, "EUR": 6.01 },                
      12 -    "2026-07-21": { "USD": 5.48, "EUR": 5.99 },                
      13 -    "2026-07-22": { "USD": 5.45, "EUR": 5.95 },                
      14 -    "2026-07-23": { "USD": 5.44, "EUR": 5.94 },                
      15 -    "2026-07-24": { "USD": 5.46, "EUR": 5.97 },                
      16 -    "2026-07-27": { "USD": 5.52, "EUR": 6.03 },                
      17 -    "2026-07-28": { "USD": 5.51, "EUR": 6.02 }                 
      18 -  }                                                            
      19 -}                                                              
  ⎿  Deleted despesas-envelope-cc-desconhecido.json (+0 -52)
       1 -{                                                              
       2 -  "colaborador": {                                             
       3 -    "id": "c-1103",                                            
       4 -    "nome": "Dani Okonkwo",                                    
       5 -    "centro_custo": "CC-SUPORTE-N2"                            
       6 -  },                                                           
       7 -  "periodo": {                                                 
       8 -    "competencia": "2026-07",                                  
       9 -    "inicio": "2026-07-01",                                    
      10 -    "fim": "2026-07-31"                                        
      11 -  },                                                           
      12 -  "despesas": [                                                
      13 -    {                                                          
      14 -      "id": "f-001",                                           
      15 -      "data": "2026-07-16",                                    
      16 -      "categoria": "alimentacao",                              
      17 -      "descricao": "Almoco",                                   
      18 -      "fornecedor": "Padaria Uniao",                           
      19 -      "valor": 58.00,                                          
      20 -      "tem_nota_fiscal": true                                  
      21 -    },                                                         
      22 -    {                                                          
      23 -      "id": "f-002",                                           
      24 -      "data": "2026-07-17",                                    
      25 -      "categoria": "hospedagem",                               
      26 -      "descricao": "Pousada - 1 diaria",                       
      27 -      "fornecedor": "Pousada do Vale",                         
      28 -      "valor": 310.00,                                         
      29 -      "tem_nota_fiscal": true                                  
      30 -    },                                                         
      31 -    {                                                          
      32 -      "id": "f-003",                                           
      33 -      "data": "2026-07-17",                                    
      34 -      "categoria": "representacao",                            
      35 -      "descricao": "Jantar com fornecedor",                    
      36 -      "fornecedor": "Casa Trindade",                           
      37 -      "valor": 190.00,                                         
      38 -      "moeda": "BRL",                                          
      39 -      "tem_nota_fiscal": true                                  
      40 -    },                                                         
     … 12 more lines (ctrl+o to expand)
  ⎿  Deleted despesas-envelope.json (+0 -113)
        1 -{                                                             
        2 -  "colaborador": {                                            
        3 -    "id": "c-0912",                                           
        4 -    "nome": "Rafael Nkemelu",                                 
        5 -    "centro_custo": "CC-COMERCIAL"                            
        6 -  },                                                          
        7 -  "periodo": {                                                
        8 -    "competencia": "2026-07",                                 
        9 -    "inicio": "2026-07-01",                                   
       10 -    "fim": "2026-07-31"                                       
       11 -  },                                                          
       12 -  "despesas": [                                               
       13 -    {                                                         
       14 -      "id": "e-001",                                          
       15 -      "data": "2026-07-13",                                   
       16 -      "categoria": "representacao",                           
       17 -      "descricao": "Jantar com prospect - fechamento de contra
          -to",                                                          
       18 -      "fornecedor": "Casa Trindade",                          
       19 -      "valor": 340.00,                                        
       20 -      "moeda": "BRL",                                         
       21 -      "tem_nota_fiscal": true                                 
       22 -    },                                                        
       23 -    {                                                         
       24 -      "id": "e-002",                                          
       25 -      "data": "2026-07-14",                                   
       26 -      "categoria": "alimentacao",                             
       27 -      "descricao": "Almoco - Lisboa",                         
       28 -      "fornecedor": "Taberna do Chiado",                      
       29 -      "valor": 22.00,                                         
       30 -      "moeda": "EUR",                                         
       31 -      "tem_nota_fiscal": true                                 
       32 -    },                                                        
       33 -    {                                                         
       34 -      "id": "e-003",                                          
       35 -      "data": "2026-07-15",                                   
       36 -      "categoria": "alimentacao",                             
       37 -      "descricao": "Cafe e sanduiche",                        
       38 -      "fornecedor": "Padaria Lisboa",                         
       39 -      "valor": 14.50,                                         
       40 -      "moeda": "EUR",                                         
     … 73 more lines (ctrl+o to expand)
  ⎿  Created exemplos/envelope/00-ENVELOPE-LACRADO.md (+72 -0)
       1 +# 🔒 ENVELOPE LACRADO                                          
       2 +                                                               
       3 +**Não distribuir antes do Dia 2, 10h.**                        
       4 +Alunos: se você chegou aqui antes da hora, feche. Ler antes que
         +ima o exercício inteiro e você é a única pessoa prejudicada.   
       5 +                                                               
       6 +---                                                            
       7 +                                                               
       8 +## Mudança de requisito — Política de Reembolso v4             
       9 +                                                               
      10 +Bom dia. O RH revisou a política. Vigência imediata, retroativa
         + à competência atual.                                          
      11 +                                                               
      12 +> **Comunicado do RH — Política de Reembolso v4**              
      13 +>                                                              
      14 +> Após auditoria interna, a política deixa de ser única para to
         +da a empresa.                                                  
      15 +>                                                              
      16 +> **A. Limites passam a variar por centro de custo.**          
      17 +> Os limites não são mais constantes. Cada centro de custo tem 
         +a sua tabela, mantida pelo financeiro num arquivo à parte, e el
         +a muda sem aviso. O motor precisa ler a política de fora, não d
         +e dentro do código.                                            
      18 +>                                                              
      19 +> A tabela vigente está em `politica-v4.json`.                 
      20 +>                                                              
      21 +> Observações que o financeiro fez questão de incluir:         
      22 +> - `CC-COMERCIAL` tem uma categoria nova, `representacao`, que
         + não existia na v3 — limite de R$ 300 por dia.                 
      23 +> - `CC-ENG-PLATAFORMA` não reembolsa `hospedagem` de forma alg
         +uma.                                                           
      24 +> - Alguns centros de custo não têm entrada na tabela. Nesse ca
         +so, aplica-se a política padrão.                               
      25 +>                                                              
      26 +> **B. Despesas internacionais.**                              
      27 +> Colaboradores em viagem internacional lançam despesas em moed
         +a estrangeira. A entrada agora pode trazer um campo `moeda` (IS
         +O 4217). Quando ausente, assume-se `BRL`.                      
      28 +>                                                              
      29 +> A conversão usa a **taxa da data da despesa**, não a taxa de 
         +hoje. As taxas estão em `cambio.json`.                         
      30 +>                                                              
      31 +> Os limites da política são sempre em BRL. Uma despesa em EUR 
         +é convertida antes de ser comparada ao limite.                 
      32 +>                                                              
      33 +> **C. (Opcional — só se sobrar tempo) Fila de aprovação manual
         +.**                                                            
      34 +> Itens cujo valor reembolsável passe de R$ 500 não são mais ap
         +rovados automaticamente. Eles entram em estado de pendência agu
         +ardando aprovação do gestor. O resultado deixa de ser apenas um
         + valor: cada item passa a ter um estado.                       
      35 +                                                               
      36 +---                                                            
      37 +                                                               
      38 +## O que se espera de você agora                               
      39 +                                                               
      40 +Nada de heroísmo. O que se avalia é o **caminho**, não a veloci
         +dade:                                                          
     … 32 more lines (ctrl+o to expand)
  ⎿  … 5 more files changed

⏺ Arquivos movidos. Agora leio a spec inteira para o mapeamento.
  Read 1 file, ran 3 shell commands (ctrl+o to expand)

⏺ Terminei os passos 1 e 2: os cinco arquivos foram movidos para
  exemplos/envelope/ (ainda sem commit) e o mapeamento de impacto está abaixo.
  Nenhum arquivo do projeto foi alterado.

  Dois achados que mudam o tamanho do trabalho:
  - O exemplo antigo muda de resultado. O exemplos/despesas-exemplo.json é do
    CC-ENG-PLATAFORMA, e a política v4 vale retroativamente desde julho de 2026.
    Com ela, a tabela da seção 9 e os totais mudam quase inteiros: alimentação
    passa a ter limite 75,00 e hospedagem passa a ter limite 0. O d-010 (480,00)
    vira recusado e o d-014 (61,00) vira aprovado.
  - Os testes de regra quase não mudam. O construtor de entrada dos testes
    (conftest.py) não define centro de custo. Se "sem centro de custo na
    entrada" usar a tabela padrão (60/80/250, que é igual à v3), a maior parte
    dos 252 testes continua valendo como está.

  Impacto

  Spec:
  - Seção 3 (fora de escopo): caem três itens: "não converte moedas", "não tem
    categoria de representação" e "não usa campos além da seção 4".
  - Seção 4 (entrada e saída):
    - A interface precisa receber a política e o câmbio.
    - Entrada: centro_custo passa a ser usado e entra o campo moeda.
    - Saída: precisa mostrar a moeda e a taxa; na opção C, também o estado do
      item. Valem novos códigos de motivo.
  - Regras:
    - RN-002: validar moeda, politica-v4.json e cambio.json.
    - RN-003: em que momento a conversão entra no arredondamento.
    - RN-006: as categorias passam a depender do centro de custo.
    - RN-008: o valor 100,00 vem do arquivo e é comparado em reais.
    - RN-009: a tabela de limites sai da spec e vai para o arquivo.
    - RN-010: o percentual de 50% vem do arquivo.
    - RN-012: hospedagem com limite 0.
  - Ambiguidades revistas: AMB-006 (o acréscimo vale para hospedagem e
    representação?), AMB-015 (fim de semana agora importa para o câmbio) e
    AMB-017 (a categoria de representação passa a existir).
  - Seção 7: casos novos de centro de custo, moeda e câmbio.
  - Seção 8: entra uma etapa de conversão.
  - Seção 9: a tabela do exemplo é refeita, e entra uma tabela nova para os dois
    arquivos do envelope.

  Plan:
  - A seção 4 descartou de propósito ler a política de um arquivo, e isso agora
    se inverte.
  - Novos módulos de leitura da política e do câmbio. Pela fronteira atual, a
    leitura do disco fica no cli.py e o parse puro em módulos próprios.
  - Duas novas decisões técnicas: a política passa para o motor como parâmetro
    (hoje são constantes importadas) e a forma de calcular a conversão.

  Código:
  - politica.py deixa de ter constantes e passa a ter o modelo e a leitura da
    política.
  - motor.py usa as constantes nas linhas 20–23, 81, 116, 119 e 173.
  - entrada.py usa CATEGORIAS_RECONHECIDAS na linha 200. Isso passa a depender
    do centro de custo, então a normalização da categoria precisa sair da
    leitura da entrada.
  - justificativa.py usa a constante de nota fiscal.
  - cli.py e saida.py mudam (interface e campos novos).

  Testes:
  - test_politica.py é reescrito.
  - test_exemplo.py ganha uma tabela nova.
  - Novos test_rn014+.
  - O processar() dos testes passa a receber a política e o câmbio.

  Tasks reabertas: T-002, T-009, T-010, T-016, T-018, T-019 e T-020 (por
  substituição, sem renumerar).

  Decisões em aberto

  Para cada uma deixo a minha recomendação, mas as decisões são suas.

  A. Política por centro de custo
  1. Como a política e o câmbio chegam ao motor. Duas opções: --politica e
     --cambio obrigatórios na CLI, ou arquivos padrão. Recomendo opções 
     obrigatórias: nada fica escondido e a CLI continua determinística.
  2. Centro de custo fora da tabela. "Aplica-se a política padrão": a tabela
     padrão inteira. Recomendo: o mesmo vale para centro_custo ausente na
     entrada.
  3. Centro de custo na tabela, mas sem a categoria. Exemplos: CC-ADM não tem
     hospedagem e CC-ENG não tem representacao. Duas opções:
     - (a) a categoria cai na tabela padrão;
     - (b) categoria_fora_da_politica.
       Recomendo (b): a tabela do centro de custo é completa, e o envelope
       mostra que o financeiro omite categoria de propósito. A opção (a) daria
       hospedagem a 250,00 para o CC-ADM.
  4. representacao num centro de custo desconhecido (f-003): o padrão não tem
     essa categoria, então categoria_fora_da_politica. Isso decorre da
     decisão 2.
  5. Comparação do nome do centro de custo. Exata, ou normalizada como a
     categoria? Recomendo exata: é um código, não texto livre.
  6. Limite 0 (CC-ENG hospedagem).
     - Motivo: recomendo categoria_fora_da_politica, porque "não reembolsa de
       forma alguma" é ser categoria não reembolsável. A alternativa é
       limite_diario_excedido.
     - Viagem: essa hospedagem com nota ainda comprova viagem? Recomendo sim: a
       viagem é um fato, não um reembolso. Isso muda o d-011 do exemplo.
  7. Acréscimo em viagem (acrescimo_em_viagem_percentual). Vale para alimentação
     e transporte, como hoje. Para representacao, recomendo não: a categoria já
     é de contexto especial, assim como a hospedagem (AMB-006). Limite × 1,5
     arredondado ao centavo.
  8. Campos do arquivo de política.
     - periodicidade dia e diaria são equivalentes.
     - Os campos observacao e moeda_base (deve ser BRL) são ignorados.
     - Recomendo: vigencia posterior à data da despesa leva a recusar com motivo
       novo, ou ser ignorado. Ignorar é mais simples, mas na prática deixa a
       política retroativa sem limite.
  9. Arquivo de política inválido (ausente, limite negativo, sem padrao): erro
     de arquivo, como a RN-002.

  B. Moeda

  10. Data sem cotação. O e-004 é de sábado, 18/07. Além disso, o cambio.json só
      começa em 13/07, então do dia 1º ao dia 12 não há taxa nenhuma. Duas
      opções:
      - (a) usar a última cotação anterior (é a prática da PTAX);
      - (b) recusar com o motivo novo cambio_indisponivel.
        Recomendo (a), limitada a uma cotação anterior de no máximo X dias. Sem
        limite, uma despesa em 2026-07-01 não teria taxa.
  11. Moeda sem cotação (e-006 em GBP): recusar com cambio_indisponivel. É etapa
      nova da seção 8; sugiro antes da nota fiscal, porque a nota compara em
      reais.
  12. Validação de moeda. Tipo e formato ("eur" minúsculo, número):
      entrada_invalida ou normalizar? Recomendo: texto de 3 letras, comparado em
      maiúsculas.
  13. Ordem do arredondamento. Duas opções:
      - (a) arredondar o valor na moeda original, multiplicar pela taxa e
        arredondar de novo;
      - (b) multiplicar o valor exato pela taxa e arredondar uma vez.
        Recomendo (b): um arredondamento só e sem erro acumulado. O valor
        convertido passa a ser o valor_considerado em reais.
  14. Teto de um bilhão (AMB-018): continua valendo sobre o número recebido, na
      moeda original.
  15. Duplicatas: comparam o valor em reais, ou o valor e a moeda originais?
      Recomendo original + moeda: o mesmo gasto lançado duas vezes tem os mesmos
      números de origem.
  16. Campos novos na saída: moeda, taxa_cambio e valor_convertido (ou o próprio
      valor_considerado em reais). Define o contrato.

  C. Aprovação manual (opcional)

  17. Com os limites da v4, nenhum item passa de R$ 500 reembolsáveis. O maior
      limite é a hospedagem do CC-COMERCIAL, 400,00, que não é ampliada em
      viagem. Então o item C só aparece se a política mudar. Recomendo: decidir
      o C por último, ou não implementar e deixar registrado.

  O que cada caso do envelope exercita

  ┌────────────┬─────────────────────────────────────────────┬──────────────┐
  │    Item    │               O que exercita                │   Decisão    │
  ├────────────┼─────────────────────────────────────────────┼──────────────┤
  │ e-001      │ representação 340 contra limite 300         │ 3, 7         │
  ├────────────┼─────────────────────────────────────────────┼──────────────┤
  │ e-002,     │ EUR, conversão; 14/07 e 15/07               │ 13           │
  │ e-003      │                                             │              │
  ├────────────┼─────────────────────────────────────────────┼──────────────┤
  │ e-004      │ EUR no sábado                               │ 10           │
  ├────────────┼─────────────────────────────────────────────┼──────────────┤
  │ e-005      │ USD                                         │ 13           │
  ├────────────┼─────────────────────────────────────────────┼──────────────┤
  │ e-006      │ GBP sem taxa                                │ 11           │
  ├────────────┼─────────────────────────────────────────────┼──────────────┤
  │ e-007      │ hospedagem 1.200 ("3 noites") contra 400    │ RN-012       │
  │            │                                             │ continua     │
  ├────────────┼─────────────────────────────────────────────┼──────────────┤
  │ e-008      │ alimentação 95, limite 90 (135 em viagem?)  │ 6, 7         │
  ├────────────┼─────────────────────────────────────────────┼──────────────┤
  │ e-009      │ coworking                                   │ RN-006       │
  │            │                                             │ continua     │
  ├────────────┼─────────────────────────────────────────────┼──────────────┤
  │ e-010      │ sem moeda, assume BRL                       │ —            │
  ├────────────┼─────────────────────────────────────────────┼──────────────┤
  │ f-001 a    │ centro de custo desconhecido, padrão,       │ 2, 4         │
  │ f-004      │ representação, USD em 21/07                 │              │
  └────────────┴─────────────────────────────────────────────┴──────────────┘

  Quer decidir de 1 a 17 agora, um por um ou em bloco? Ou prefere que eu rode o
  spec-adversary primeiro sobre o envelope para levantar o que me escapou?

✻ Crunched for 1m 23s · done 7:53 PM

❯ roda o spec-adversary primeiro                                                

⏺ spec-adversary(Adversarial review of Day 2 envelope)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ O spec-adversary está rodando em segundo plano. Passei a ele o envelope, os
  quatro arquivos de dados, a spec 1.9, o DECISIONS.md e o exemplo da seção 9.

  Não passei a minha lista de 17 decisões, para que a revisão saia independente
  da minha. Quando ele terminar, junto as duas listas: aponto o que só ele
  achou, o que só eu achei e onde discordamos. Daí você decide.

✻ Crunched for 10s · done 7:53 PM

❯ ok, me avisa quando terminar                                                  

⏺ Combinado. Te aviso assim que ele terminar e já te mostro as duas listas
  juntas.

✻ Crunched for 2s · done 7:56 PM

› Message from spec-adversary
  Revisão adversarial da Política v4 contra a spec 1.9: 17 problemas, 10
  bloqueantes, 5 importantes e 2 menores.

  Não alterei nenhum arquivo. Não li `src/` nem `tests/`. Os cenários que usam
  itens do envelope citam o id do item. Todas as contas foram feitas à mão com
  as taxas de `cambio.json` e a tabela de `politica-v4.json`.

  ---

  ### 1. A v4 invalida a seção 9 e o critério de aceite: o exemplo é de
  CC-ENG-PLATAFORMA — BLOQUEANTE — contradição

  - **Onde:** seção 9, RN-009 (tabela), RN-010, seção 7.
  `exemplos/despesas-exemplo.json` traz `centro_custo: "CC-ENG-PLATAFORMA"` e
  período 2026-07, que fica dentro da vigência 2026-07-01 ("retroativa à
  competência atual").
  - **Cenário:** o exemplo da seção 9 com a tabela de CC-ENG-PLATAFORMA
  (alimentação 75, transporte 80, hospedagem 0):
    - d-001: 72,50 → `aprovado` (antes era `parcial` 60)
    - d-002: 38,00 → `parcial` 2,50 (antes era `recusado`)
    - d-010: hospedagem 480 → 0 (antes `parcial` 250; o motivo depende do achado
  2)
    - d-011: limite 112,50 ou 75,00, conforme o achado 2
    - d-014: 61,00 → `aprovado` (antes `parcial` 60)
    - Total reembolsado: 72,50 + 2,50 + 80 + 54,90 + 0 + 33,33 + 47,20 + 61 =
  **351,43**, contra 585,43 na spec. `valor_solicitado` continua 1.861,84 e o
  glosado vai para 1.510,41.
  - **Problema:** a tabela da seção 9 e o critério "produz exatamente o
  resultado da tabela" deixam de valer. Os casos da seção 7 fixam 60/80/250 sem
  dizer o centro de custo, e hoje só fecham se forem lidos como "política
  padrão".
  - **Pergunta:** o exemplo da seção 9 passa a ser calculado com a tabela de
  CC-ENG-PLATAFORMA (resultado novo) ou com outra política (v3 ou padrão)? E os
  casos da seção 7 passam a declarar o centro de custo, ou ficam implicitamente
  na "política padrão"?

  ### 2. CC-ENG-PLATAFORMA "não reembolsa hospedagem": limite 0 ou categoria
  fora da política? E a hospedagem ainda comprova viagem? — BLOQUEANTE —
  ambiguidade/brecha

  - **Onde:** RN-006, RN-009, RN-010, RN-011, códigos de motivo. Em
  `politica-v4.json` aparece `"hospedagem": { "limite": 0.00, ..., "observacao":
  "nao reembolsavel" }`.
  - **Leituras possíveis:**
    - (a) Limite diário 0 na etapa 9: `recusado` com `limite_diario_excedido`,
  `limite_diario` 0. A hospedagem passou pelas etapas 1 a 7, então pela RN-010
  **ainda comprova viagem** (D e D+1).
    - (b) Categoria não reconhecida para esse centro de custo:
  `categoria_fora_da_politica` na etapa 5. Não comprova viagem.
    - (c) Motivo novo.
  - **Cenário:** CC-ENG-PLATAFORMA, hospedagem de 0,01 com nota em 14/07 e
  alimentação de 100,00 com nota em 15/07.
    - Leitura (a): 15/07 fica em viagem, limite 112,50, alimentação `aprovado`
  com 100,00.
    - Leitura (b): limite 75, alimentação `parcial` com 75,00.
  - **Brecha na leitura (a):** uma hospedagem que a política declara não
  reembolsável amplia os limites. O motivo `limite_diario_excedido` também diz
  ao colaborador que houve "excesso", e não que a categoria é vedada.
  - **Pergunta:** para o centro de custo com hospedagem "não reembolsável", qual
  motivo a despesa recebe? Ela continua comprovando viagem?

  ### 3. "Aplica-se a política padrão": em que casos, e o que é o padrão? —
  BLOQUEANTE — ambiguidade

  - **Onde:** RN-006, RN-009, seção 4 (`centro_custo` é opcional e hoje não é
  usado).
  - **Casos:**
    - **(a) Centro de custo existente sem a categoria.** CC-ADM não tem
  `hospedagem`. Uma hospedagem de 300,00 com nota de um colaborador CC-ADM pode
  receber:
      - 250,00, se a categoria cai no padrão;
      - 0 com `categoria_fora_da_politica`, porque a tabela do CC é completa e a
  ausência significa "não coberto";
      - 0 por analogia com CC-ENG-PLATAFORMA.

      O comunicado só fala em "centros de custo que **não têm entrada**", ou
  seja, o CC inteiro.
    - **(b) Categoria que existe só em outro CC.** f-003 (CC-SUPORTE-N2,
  `representacao` 190,00 com nota): o padrão do arquivo não tem `representacao`.
  Pode sair `categoria_fora_da_politica` (0), ou a categoria pode ser
  considerada criada pela v4 para todos, com algum limite.
    - **(c) O que é "política padrão".** Pode ser o bloco `padrao` do arquivo,
  que "muda sem aviso", ou a política v3 / a RN-009 atual. Hoje os valores
  coincidem (60/80/250), mas divergem se o financeiro editar o bloco `padrao`.
  - **Pergunta:** a política padrão vale para o centro de custo ausente da
  tabela, para a categoria ausente num centro de custo existente, ou para ambos?
  "Padrão" é o bloco `padrao` do arquivo ou outra coisa? Quais categorias são
  reconhecidas para um colaborador: as da tabela do seu CC, as do padrão, ou a
  união?

  ### 4. Identificação do centro de custo: ausente, inválido, grafia diferente e
  autodeclarado — BLOQUEANTE — lacuna/brecha

  - **Onde:** seção 4 (entrada: `centro_custo` opcional, sem validação), RN-002,
  normalização da seção 5 (que só cobre categoria e fornecedor).
  - **Cenários:**
    - **Grafia diferente.** Um colaborador CC-ADM envia `"centro_custo":
  "cc-adm"` ou `"CC-ADM "`. Com comparação exata, ele cai no padrão: alimentação
  60 em vez de 45. Com normalização, fica em CC-ADM.
    - **Ausente ou inválido.** `centro_custo` ausente, `null`, `""` ou `17` pode
  ser tratado como padrão, como erro de arquivo, ou de outra forma.
    - **Autodeclarado.** O campo vem da mesma entrada que o colaborador produz.
  Declarar `CC-COMERCIAL` dá alimentação 90, transporte 150 e hospedagem 400, e
  a spec não tem como verificar.
  - **Brecha:** escapar de uma tabela mais restritiva errando a grafia ou
  omitindo o campo.
  - **Pergunta:** o centro de custo é comparado de forma exata ou normalizada?
  Ausente, não textual ou vazio vira padrão, `erro de arquivo` ou outra coisa? O
  risco de centro de custo autodeclarado é aceito (como o `tem_nota_fiscal`) ou
  tratado?

  ### 5. Limite de nota fiscal (100,00) comparado em BRL convertido ou na moeda
  original? — BLOQUEANTE — ambiguidade

  - **Onde:** RN-008, AMB-007, AMB-008 e o campo
  `nota_fiscal_obrigatoria_acima_de` do arquivo. O comunicado só diz que "os
  limites da política são em BRL" e que a despesa "é convertida antes de ser
  comparada **ao limite**".
  - **Cenário:** e-005, transporte de 40,00 USD sem nota em 20/07, taxa 5,50 →
  220,00 BRL.
    - Comparado em BRL: `nota_fiscal_ausente`, reembolso 0.
    - Comparado na moeda original (40 < 100): segue; o limite de CC-COMERCIAL é
  150 (sem viagem), então `parcial` com 150,00.
  - **Pergunta:** o valor mínimo para exigir nota fiscal se compara ao valor
  convertido em BRL ou ao valor na moeda da despesa? O valor desse mínimo passa
  a vir do arquivo (substituindo o "100,00 fixo" da RN-008), e pode variar por
  centro de custo?

  ### 6. "Taxa da data da despesa" quando não há taxa nessa data — BLOQUEANTE —
  lacuna, com inconsistência no próprio envelope

  - **Onde:** nenhuma regra cobre. `cambio.json` diz "Cotações publicadas apenas
  em dias úteis bancários" e só cobre de 13/07 a 28/07. Isso também entra em
  choque com a AMB-015, que diz que fim de semana não afeta nada.
  - **Cenários:**
    - **Fim de semana.** e-004: 30,00 EUR com nota em 18/07 (sábado), sem taxa.
      - Dia útil anterior (17/07, 5,96): 178,80.
      - Dia útil seguinte (20/07, 6,01): 180,30.
      - Ou recusa.

      O reembolso fica 90 (sem viagem) em qualquer conversão, mas
  `valor_considerado` e os totais mudam.
    - **A escolha muda a aprovação.** 16,70 EUR sem nota, alimentação, em 18/07:
      - Com 17/07: 99,53, não exige nota, `parcial` 90.
      - Com 20/07: 100,37, `nota_fiscal_ausente`, reembolso 0.
    - **Dia útil fora do arquivo.** Despesa em USD em 06/07 (segunda-feira,
  dentro do período): o arquivo não tem taxa. "Dia útil anterior" voltaria para
  antes de 13/07, que também não está no arquivo. A lacuna existe mesmo em dia
  útil.
  - **Pergunta:** sem taxa na data exata, usa-se o dia anterior com taxa, o
  seguinte, recusa-se a despesa (com qual motivo), ou é erro de arquivo? Há
  limite de quantos dias se pode voltar?

  ### 7. Moeda sem cotação ou inválida (GBP em e-006) — BLOQUEANTE — lacuna

  - **Onde:** RN-002 (hoje `moeda` é campo extra ignorado), códigos de motivo.
  - **Cenários:**
    - e-006: `representacao` de 55,00 GBP em 21/07. GBP não existe em
  `cambio.json`.
    - Variações de formato: `"moeda": "eur"`, `"moeda": "R$"`, `"moeda": ""`,
  `"moeda": null`, `"moeda": 978`.
    - O comunicado diz que `moeda` ausente é BRL; `null` não está coberto.
    - `"BRL"` explícito não está em `cambio.json`. Taxa 1 implícita?
  - **Leituras:** `entrada_invalida`, motivo novo (por exemplo "moeda sem
  cotação"), `erro de arquivo`, ou normalizar a caixa.
  - **Pergunta:** o que acontece com moeda sem taxa no arquivo, com código fora
  do padrão ISO 4217 ou com grafia diferente, e com `moeda: null`? Se houver
  motivo novo, em que etapa da seção 8 ele entra?

  ### 8. Arredondamento: antes ou depois da conversão, e sobre qual valor se
  aplicam o teto e o mínimo — BLOQUEANTE — ambiguidade

  - **Onde:** RN-003 ("antes de qualquer outra regra de valor, `valor` é
  arredondado"), RN-004, RN-002 (teto de 1 bilhão "comparado com o número
  recebido"), seção 4 (`valor_considerado` em reais).
  - **Cenário:** 16,8649 EUR sem nota, alimentação, em 14/07 (taxa 5,93).
    - Arredondar e depois converter: 16,86 × 5,93 = 99,9798 → 99,98. Não exige
  nota, `parcial` 90 em CC-COMERCIAL.
    - Converter e depois arredondar: 100,008857 → 100,01. `nota_fiscal_ausente`,
  reembolso 0.
  - **Variações:**
    - 0,004 EUR: arredondado primeiro fica 0,00, `valor_invalido`. Convertido
  primeiro fica 0,02, válido.
    - O teto de 1 bilhão compara o número em moeda estrangeira ou o valor
  convertido? 200.000.000 USD equivale a cerca de 1,1 bilhão BRL.
  - **Pergunta:** há um ou dois arredondamentos, e em que ordem em relação à
  conversão? O teto da RN-002 e a RN-004 se aplicam ao valor original ou ao
  convertido?

  ### 9. "Viagem internacional" põe o colaborador em viagem? — BLOQUEANTE —
  ambiguidade/contradição com RN-010/AMB-004

  - **Onde:** RN-010 e AMB-004 (viagem só pela hospedagem com nota). O
  comunicado diz "Colaboradores **em viagem internacional** lançam despesas em
  moeda estrangeira".
  - **Cenário:** e-002 a e-005 (Lisboa, 14/07 a 20/07) não têm hospedagem; a
  única é e-007, em 22/07.
    - Pela RN-010 atual:
      - e-002: 22 EUR × 5,93 = 130,46 → `parcial` 90
      - e-004: 178,80 (ou 180,30) → `parcial` 90
    - Se despesa em moeda estrangeira caracteriza viagem:
      - e-002 → `aprovado` 130,46 (limite 135)
      - e-004 → 135
      - e-005 (se passar na nota, achado 5) → limite 225, `aprovado` 220,00
  - **Pergunta:** despesa em moeda estrangeira caracteriza viagem nessa data (e
  em quais datas vizinhas), ou a viagem continua dependendo só de hospedagem com
  nota?

  ### 10. Acréscimo de viagem: vem do arquivo e vale para quais categorias? —
  BLOQUEANTE — ambiguidade

  - **Onde:** RN-009 (tabela fixa 90/120/250), RN-010, AMB-006. O arquivo traz
  `acrescimo_em_viagem_percentual: 50` global, sem lista de categorias.
  - **Cenários:**
    - CC-COMERCIAL, `representacao` de 400,00 com nota no dia seguinte a uma
  hospedagem com nota: o limite é 300 ou 450?
    - O percentual do arquivo se aplica também à hospedagem? A AMB-006 diz que
  não; o arquivo não restringe. Em CC-COMERCIAL seriam 400 ou 600.
    - Limite ampliado sem valor exato ao centavo, possível porque a tabela "muda
  sem aviso": 33,33 × 1,5 = 49,995. Arredondar ou truncar?
  - **Pergunta:** o acréscimo vale para quais categorias (as duas da RN-009
  atual, todas exceto hospedagem, ou todas)? O percentual passa a vir do
  arquivo? Como se arredonda um limite ampliado sem centavo exato?

  ### 11. Como a política e o câmbio entram na execução, e o que é erro nesses
  arquivos — BLOQUEANTE — lacuna

  - **Onde:** seção 4 (interface `calcular --input --output`), RN-002 (erro de
  arquivo), seção 9 ("mesma entrada, mesma saída").
  - **Cenários:**
    - Como os arquivos chegam: argumentos novos na linha de comando, caminho
  fixo, ou embutidos na entrada?
    - `cambio.json` é obrigatório quando todas as despesas são BRL?
    - `politica-v4.json`:
      - sem bloco `padrao`;
      - com `"limite": "60"` (texto), `-10` ou `60.005`;
      - com `periodicidade` diferente de `dia`/`diaria` (por exemplo `"mes"`);
      - com `moeda_base` diferente de BRL.
    - `cambio.json` com taxa 0, taxa negativa ou data inválida.
    - Diferença entre `dia` e `diaria`: tem efeito de cálculo ou é rótulo? A
  RN-012 já trata hospedagem como diária.
  - **Pergunta:** qual é a interface para fornecer política e câmbio? Que
  defeitos nesses arquivos são erro de arquivo (sem saída), quais são ignorados
  e quais viram recusa por item? O que `periodicidade` significa para o cálculo?

  ### 12. Ordem da conversão na seção 8 e qual motivo vence — IMPORTANTE —
  lacuna

  - **Onde:** seção 8, "cada despesa recusada tem exatamente um motivo".
  - **Cenários:**
    - Despesa em USD de 15/04 (fora do período e sem taxa): `fora_do_periodo` ou
  falta de cotação?
    - `coworking` em GBP: `categoria_fora_da_politica` ou moeda sem cotação?
    - Valor negativo em moeda sem taxa: `valor_invalido` ou falta de cotação?
  - **Pergunta:** em que posição entra a etapa de conversão (e a eventual recusa
  por falta de taxa), em relação às etapas 2 a 6?

  ### 13. Duplicata com moedas diferentes — IMPORTANTE — ambiguidade

  - **Onde:** RN-007 (compara `valor_considerado`, que passaria a ser BRL).
  - **Cenários:**
    - 10,00 EUR "Taberna do Chiado" com nota em 14/07, e o mesmo gasto relançado
  como 59,30 BRL. Comparando o valor convertido, é duplicata: recebe 59,30.
  Comparando o valor e a moeda originais, não é: 59,30 + 30,70 = 90,00 (limite).
    - Inverso: 22,00 EUR e 22,00 USD, mesmos fornecedor e data. Comparando o
  número recebido sem a moeda, seriam duplicatas.
  - **Pergunta:** a duplicata compara o valor convertido em BRL, ou o valor
  original junto com a moeda?

  ### 14. A saída não mostra moeda, taxa, centro de custo nem a política
  aplicada — IMPORTANTE — lacuna

  - **Onde:** seção 4 (saída). `colaborador` copia só `id`/`nome`.
  `valor_informado` é "o número recebido", em EUR, enquanto o texto diz "todos
  os valores monetários... em reais". `justificativa` não é contratual.
  - **Cenário:** e-002 sai `valor_informado` 22.0 e `valor_considerado` 130.46,
  e nenhum campo contratual mostra EUR nem 5,93. f-001 a f-004 caíram no padrão,
  mas a saída não diz isso. Como "a tabela muda sem aviso", não dá para
  reconstituir qual versão foi usada.
  - **Pergunta:** a saída passa a trazer moeda, taxa e data da taxa por item, e
  centro de custo, uso do padrão e versão/vigência da política no topo? Ou isso
  fica só na justificativa (não contratual)?

  ### 15. Vigência, "retroativa à competência atual" e o campo `vigencia` —
  IMPORTANTE — ambiguidade, com inconsistência no envelope

  - **Onde:** seção 4 (`competencia` não é usada em cálculo), seção 10. O
  arquivo diz `vigencia: "2026-07-01"`; os dados de entrada são de 2026-07; a
  data de hoje é 2026-10-02.
  - **Cenários:**
    - Período 2026-06-15 a 2026-07-15, com despesas de junho: usam a v4, a v3
  (que deixaria de estar em algum lugar), ou são recusadas?
    - Um arquivo de política com `vigencia` posterior ao `periodo.fim` deve ser
  aplicado?
    - "Competência atual" hoje seria 2026-10, não 2026-07.
  - **Pergunta:** o campo `vigencia` tem efeito no cálculo (por data da despesa,
  por `periodo`, por `competencia`) ou é informativo? O que acontece com
  despesas anteriores à vigência?

  ### 16. Item C (pendência acima de 500): unidade de aplicação e regra que
  nunca dispara com as tabelas atuais — IMPORTANTE (só se o item C for
  implementado) — ambiguidade

  - **Onde:** RN-011 (status `aprovado`/`parcial`/`recusado`), seção 4 (totais).
  - **Cenário:** com as tabelas v4, o maior reembolso possível de um único item
  é 400 (hospedagem CC-COMERCIAL), ou 450 se o achado 10 ampliar a
  representação. Então "valor reembolsável passe de R$ 500" por item **nunca
  dispara**. Ele dispara se a leitura for:
    - valor considerado (e-007: 1.200 → pendente);
    - soma do dia;
    - total do período (CC-COMERCIAL passa de 500 no envelope).

    Também não está definido:
    - se `pendente` combina com `parcial` (estado separado do status, ou valor
  novo de `status`);
    - se o valor pendente entra em `totais.valor_reembolsado`;
    - se o limite é `>` ou `>=` e se vem do arquivo de política.
  - **Pergunta:** o limite de 500 se aplica ao reembolso do item, ao valor
  considerado, ao dia ou ao período? Pendência é um campo novo ou um valor de
  `status`? Como ela entra nos totais?

  ### 17. Texto da spec que a v4 contradiz diretamente — MENOR (redação; os
  efeitos de cálculo estão nos itens acima) — contradição

  - **Seção 3:** "Não converte moedas"; "Não tem categoria nem limite de
  representação"; "Não usa campos além dos previstos na seção 4". A seção 4 diz
  `valor` "em reais" e RN-002 "campos extras ignorados". Pela 1.9 literal, e-002
  (22 EUR) é avaliada como 22,00 BRL.
  - **AMB-017:** "representação = evolução recomendada", e e-001
  (`representacao` 340, CC-COMERCIAL) seria `categoria_fora_da_politica` pela
  RN-006, contra 300 `parcial` pela v4.
  - **RN-008 e AMB-007:** "100,00 fixo".
  - **AMB-015:** fim de semana não afeta nada; agora afeta o câmbio (achado 6).
  - **Seção 10, riscos aceitos:**
    - O risco de fracionamento diz que o ganho só existe quando "o limite diário
  passa de 100,00 (hospedagem e transporte em viagem)". Agora transporte
  CC-COMERCIAL (150), alimentação CC-COMERCIAL em viagem (135) e representação
  (300) também passam de 100.
    - O risco de "hospedagem irrisória" fala em "até 70,00 por dia". Em
  CC-COMERCIAL seria 45 + 75 = 120 por dia.
  - **Pergunta:** quais desses trechos são revogados e quais são reescritos? As
  justificativas dos riscos aceitos continuam válidas com os novos valores?

  Uma observação sobre os dados do envelope, que nenhuma regra resolve (cabe no
  9 ou no 17): e-007 (hotel em Londres, de 22/07 a 24/07) e e-008 (almoço em BRL
  no "Restaurante Tavola" em 23/07) são geograficamente incoerentes, mas pela
  RN-010 o e-008 ganha o limite de viagem (135, `aprovado` 95).

  ---

  **Decidir antes da implementação (BLOQUEANTES):** 1, 2, 3, 4, 5, 6, 7, 8, 9,
  10, 11.

  Correção: são 11 bloqueantes, não 10 como diz o resumo inicial. A contagem
  certa é 17 problemas: 11 bloqueantes, 4 importantes e 2 menores. O achado 16
  está classificado como importante, mas é condicional ao item C; trato-o como o
  segundo menor da contagem.

  **Pode ser decidido depois:** 12, 13, 14, 15 (importantes); 16, 17 (16 vira
  bloqueante se o item C for implementado).

  Arquivos usados:
  - /Users/rafaeltxm/repo/sdd-desafio/exemplos/envelope/00-ENVELOPE-LACRADO.md
  - /Users/rafaeltxm/repo/sdd-desafio/exemplos/envelope/politica-v4.json
  - /Users/rafaeltxm/repo/sdd-desafio/exemplos/envelope/cambio.json
  - /Users/rafaeltxm/repo/sdd-desafio/exemplos/envelope/despesas-envelope.json
  - /Users/rafaeltxm/repo/sdd-desafio/exemplos/envelope/despesas-envelope-cc-des
  conhecido.json
  - /Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md
  - /Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md
  - /Users/rafaeltxm/repo/sdd-desafio/exemplos/despesas-exemplo.json

⏺ O spec-adversary terminou: 17 problemas, sendo 11 bloqueantes, 4 importantes e
  2 menores. Ele mesmo corrigiu a contagem do resumo dele. Conferi a conta
  principal: com a tabela do CC-ENG-PLATAFORMA, o exemplo da seção 9 passa a
  reembolsar 351,43 (hoje são 585,43), e o glosado vai para 1.510,41.

  Primeiro, um erro meu que a revisão expôs. Na decisão 6, recomendei duas
  coisas que não funcionam juntas: motivo categoria_fora_da_politica para a
  hospedagem com limite 0 e, ao mesmo tempo, que ela continuasse comprovando
  viagem. Pela seção 8, quem é recusado na etapa 5 (categoria) não passa pelas
  etapas 1 a 7 e, portanto, não comprova viagem. Então você precisa escolher um
  dos dois pares:
  - (a) limite_diario_excedido com limite 0, e a hospedagem comprova viagem.
    Brecha: uma hospedagem de 0,01 com nota amplia os limites dos dois dias,
    numa categoria que a política diz que não reembolsa.
  - (b) categoria_fora_da_politica, e a hospedagem não comprova viagem.

  O que só a revisão achou

  - Moeda estrangeira como prova de viagem (achado 9). O comunicado diz
    "colaboradores em viagem internacional lançam despesas em moeda
    estrangeira". Se isso caracteriza viagem, o e-002 passa de parcial 90 para
    aprovado 130,46. Eu não tinha visto esse caso.
  - Centro de custo autodeclarado (achado 4). O colaborador pode escrever
    CC-COMERCIAL e ganhar os limites maiores. Na mesma linha do tem_nota_fiscal,
    isso seria um risco aceito ou um caso tratado? Também falta decidir
    centro_custo null, "" ou 17.
  - Casos concretos onde a escolha vira o resultado.
    - Câmbio de fim de semana: com 16,70 EUR num sábado, usar a taxa da sexta dá
      99,53 (não exige nota). Usar a da segunda dá 100,37
      (nota_fiscal_ausente).
    - Ordem do arredondamento: com 16,8649 EUR, arredondar antes de converter dá
      99,98; converter antes dá 100,01, que exige nota.
  - O que é a "política padrão" (3c). Pode ser o bloco padrao do arquivo, que
    pode mudar sem aviso, ou a v3 fixa.
  - Rastro da política na saída (14). A saída não mostra centro de custo, se
    caiu no padrão, nem a versão ou vigência da política. Como a tabela muda sem
    aviso, não dá para reconstituir depois qual foi usada.
  - Vigência (15). "Competência atual" hoje seria 2026-10. Falta decidir o que
    fazer com despesas de antes da vigência.
  - Riscos aceitos da seção 10 desatualizados (17). Os números ("até 70,00 por
    dia", "limite passa de 100 só em hospedagem e transporte em viagem") não
    valem mais com os limites do CC-COMERCIAL.
  - Incoerência nos dados: o hotel em Londres (e-007) faz o almoço em BRL no dia
    seguinte (e-008) ganhar o limite de viagem.

  O que só eu tinha levantado é de implementação, não de spec: o entrada.py
  normaliza a categoria usando a lista fixa, e isso passa a depender do centro
  de custo.

  Lista para decidir

  Juntei as duas revisões. A numeração é a do adversário. Recomendações minhas,
  mas a decisão é sua.

  Bloqueantes:

  #: 11
  Decisão: Como política e câmbio entram na execução; defeitos nesses arquivos
  Minha recomendação: --politica e --cambio obrigatórios; arquivo defeituoso é
  erro de arquivo; dia e diaria são equivalentes
  ────────────────────────────────────────
  #: 1
  Decisão: Seção 9: o exemplo usa o CC-ENG (resultado novo)? Os casos da seção 7

  ficam no padrão?
  Minha recomendação: Sim aos dois; a tabela nova é calculada à mão
  ────────────────────────────────────────
  #: 3
  Decisão: Onde vale o padrão; o que é o padrão
  Minha recomendação: Bloco padrao do arquivo, só para centro de custo ausente
  da
  tabela; categoria ausente de um centro de custo existente vira
  categoria_fora_da_politica
  ────────────────────────────────────────
  #: 4
  Decisão: Comparação, validação e confiança no centro_custo
  Minha recomendação: Exata; ausente, nulo ou vazio usa o padrão; tipo errado é
  erro de arquivo; autodeclarado é risco aceito
  ────────────────────────────────────────
  #: 2
  Decisão: Hospedagem com limite 0
  Minha recomendação: (b), sem comprovar viagem: fecha a brecha
  ────────────────────────────────────────
  #: 10
  Decisão: Acréscimo de viagem
  Minha recomendação: Vem do arquivo; só para alimentação e transporte; limite
  arredondado ao centavo
  ────────────────────────────────────────
  #: 9
  Decisão: Moeda estrangeira caracteriza viagem?
  Minha recomendação: Não: a viagem continua sendo comprovada só pela
  hospedagem;
  risco registrado
  ────────────────────────────────────────
  #: 6
  Decisão: Data sem cotação
  Minha recomendação: Última cotação anterior, até 3 dias corridos (cobre o fim
  de semana); sem isso, motivo novo cambio_indisponivel
  ────────────────────────────────────────
  #: 7
  Decisão: Moeda sem cotação ou mal formada
  Minha recomendação: Sem cotação: cambio_indisponivel; fora do formato de 3
  letras maiúsculas: entrada_invalida; null é BRL; BRL tem taxa 1 implícita
  ────────────────────────────────────────
  #: 8
  Decisão: Arredondamento e teto
  Minha recomendação: Converter o valor exato e arredondar uma vez só; teto e
  RN-004 aplicados sobre o valor original e o convertido
  ────────────────────────────────────────
  #: 5
  Decisão: Nota fiscal em BRL ou na moeda original
  Minha recomendação: BRL convertido; o 100,00 vem do arquivo e é o mesmo para
  todos os centros de custo

  Importantes:

  ┌─────┬──────────────────┬────────────────────────────────────────────────┐
  │  #  │     Decisão      │               Minha recomendação               │
  ├─────┼──────────────────┼────────────────────────────────────────────────┤
  │     │ Etapa da         │ Nova etapa logo depois da categoria (5), antes │
  │ 12  │ conversão na     │  da nota (6)                                   │
  │     │ seção 8          │                                                │
  ├─────┼──────────────────┼────────────────────────────────────────────────┤
  │     │ Duplicata com    │                                                │
  │ 13  │ moedas           │ Valor original + moeda                         │
  │     │ diferentes       │                                                │
  ├─────┼──────────────────┼────────────────────────────────────────────────┤
  │     │ Campos novos na  │ Itens: moeda, taxa_cambio, data_taxa. Topo:    │
  │ 14  │ saída            │ centro_custo, politica_aplicada (CC ou         │
  │     │                  │ padrao), versão da política                    │
  ├─────┼──────────────────┼────────────────────────────────────────────────┤
  │ 15  │ Vigência         │ Despesa anterior à vigencia recusada com       │
  │     │                  │ motivo novo                                    │
  ├─────┼──────────────────┼────────────────────────────────────────────────┤
  │     │ Item C           │ Não implementar agora; registrar que, por      │
  │ 16  │ (pendência acima │ item, nunca dispara com a v4                   │
  │     │  de 500)         │                                                │
  ├─────┼──────────────────┼────────────────────────────────────────────────┤
  │     │ Texto da spec    │ Reescrever seção 3, AMB-015, AMB-017, RN-008 e │
  │ 17  │ revogado         │  riscos da seção 10 junto com as decisões      │
  │     │                  │ acima                                          │
  └─────┴──────────────────┴────────────────────────────────────────────────┘

  Quer decidir em bloco (aceitar as recomendações e apontar só onde discorda) ou
  que eu te pergunte uma por uma, começando pelas bloqueantes?

✻ Worked for 4m 13s · done 7:57 PM

⏺ Agent "Adversarial review of Day 2 envelope" finished · 3m 34s

❯ uma por uma                                                                   

⏺ User declined to answer questions
  ⎿  · Decisão 11 (bloqueante): como a política e o câmbio entram na execução? 
     (--politica e --cambio (Recomendado) / --cambio só se houver moeda 
     estrangeira / Caminhos padrão)

⏺ Você quis esclarecer algo antes de responder à decisão 11 (como a política e o
  câmbio entram na execução). O que ficou em dúvida: as opções, o impacto em
  outra parte do sistema, ou o enunciado do envelope?

✻ Brewed for 8s · done 8:10 PM

❯ me explica o primeiro no detalhe a minah decisao, ficou confuso pra mim       

⏺ A decisão 11 é: como o programa encontra os dois arquivos novos.

  O problema

  Hoje o programa roda assim:

  uv run reembolso calcular --input despesas.json --output saida.json

  Ele só recebe o arquivo de despesas. Os limites (60, 80, 250, a nota acima de
  100, os 50% de viagem) estão escritos dentro do código, em politica.py.

  O envelope muda isso de duas formas:
  - Item A: "O motor precisa ler a política de fora, não de dentro do código."
    Os limites passam a vir do politica-v4.json, que o financeiro altera sem
    avisar.
  - Item B: as taxas de câmbio vêm do cambio.json.

  O comunicado não diz como o programa acha esses arquivos. É isso que precisa
  ser decidido.

  As três opções

  1. Dois argumentos obrigatórios (minha recomendação)

  uv run reembolso calcular --input despesas.json \
      --politica politica-v4.json --cambio cambio.json --output saida.json

  - Quem roda diz explicitamente qual política e qual câmbio usar.
  - Se esquecer qualquer um deles, o programa para com erro de uso (código 2),
    como acontece hoje sem --output.
  - Vantagem: a linha de comando mostra tudo o que entrou no cálculo. Se o
    financeiro trocar a tabela amanhã, quem rodar vai apontar para o arquivo
    novo de forma consciente. Isso preserva o "mesma entrada, mesma saída" da
    seção 9.
  - Custo: a linha de comando fica mais longa, e é preciso passar o câmbio mesmo
    quando todas as despesas são em reais.

  2. --politica obrigatório e --cambio só quando precisar

  - Se todas as despesas forem em BRL, dá para omitir --cambio.
  - Custo: cria uma decisão a mais. Se alguma despesa vier em EUR e faltar o
    --cambio, o arquivo inteiro vira erro, ou só aquela despesa é recusada? É
    mais uma regra para especificar e testar.

  3. Caminho fixo

  - O programa procura politica.json e cambio.json num lugar combinado (por
    exemplo, a pasta atual) quando os argumentos não são passados.
  - Custo: o resultado passa a depender de um arquivo que não aparece na linha
    de comando. Rodar o mesmo comando em outra pasta, ou depois que o financeiro
    trocou o arquivo, dá outro resultado sem nada visível ter mudado. É o tipo
    de dependência escondida que a spec evitou até aqui.

  A segunda metade da decisão: arquivo de política ou câmbio com defeito

  O que fazer se o politica-v4.json ou o cambio.json vier quebrado? Por exemplo:
  - arquivo não existe, ou não é JSON válido;
  - limite escrito como texto ("60"), negativo (-10) ou com 3 casas (60.005);
  - falta o bloco padrao;
  - periodicidade com um valor desconhecido, como "mes";
  - taxa de câmbio zero ou negativa, ou data inválida no câmbio.

  Recomendação: tratar como erro de arquivo, igual a um despesas.json sem
  colaborador. O programa não gera saída, mostra erro: ... e termina com código
  1.

  O motivo: com uma política quebrada, nenhum cálculo é confiável. Recusar
  despesa por despesa esconderia o problema do arquivo atrás de dezenas de
  recusas.

  Detalhe da periodicidade: os valores dia e diaria seriam só rótulos com o
  mesmo significado, "limite por data". Hoje a RN-012 já trata cada lançamento
  de hospedagem como uma diária na sua data, então nada muda no cálculo.
  Qualquer outro valor seria erro de arquivo, porque o sistema não sabe aplicar,
  por exemplo, um limite mensal.

  Resumindo

  O que você decide aqui:
  1. Como os arquivos chegam: argumentos obrigatórios, câmbio opcional, ou
     caminho fixo.
  2. Se um defeito nesses arquivos é erro de arquivo (sem saída).

  Quer que eu repita a pergunta com essas opções?

✻ Cogitated for 14s · done 8:11 PM

❯ sim, repete a pergunta                                                        

⏺ User answered Claude's questions:
  ⎿  · Decisão 11, parte 1: como o programa encontra a política e o câmbio? → Os
     dois obrigatórios (Recomendado)
     · Decisão 11, parte 2: arquivo de política ou de câmbio com defeito 
     (ausente, JSON inválido, limite negativo/texto/3 casas, sem bloco padrao, 
     periodicidade desconhecida, taxa ≤ 0, data inválida)? → Erro de arquivo 
     (Recomendado)

  Made 1 scratchpad edit +4 (ctrl+o to expand)

⏺ Decisão 11 registrada: --politica e --cambio obrigatórios, e defeito em
  qualquer um dos dois arquivos é erro de arquivo.

  Decisão 1: o que acontece com o exemplo da seção 9 e com os casos da seção 7

  Seção 9. O arquivo exemplos/despesas-exemplo.json tem "centro_custo": 
  "CC-ENG-PLATAFORMA". Na v3 isso não importava, porque o campo era ignorado. Na
  v4 importa, e a política vale desde 01/07, então pega o período do exemplo.
  Com a tabela do CC-ENG (alimentação 75, transporte 80, hospedagem 0), o
  resultado muda:

  ┌──────────────────────────┬───────────────┬─────────────────────────────┐
  │            id            │   hoje (v3)   │       com CC-ENG (v4)       │
  ├──────────────────────────┼───────────────┼─────────────────────────────┤
  │ d-001 alimentação 72,50  │ parcial 60,00 │ aprovado 72,50              │
  ├──────────────────────────┼───────────────┼─────────────────────────────┤
  │ d-002 alimentação 38,00  │ recusado 0    │ parcial 2,50                │
  │ (mesmo dia)              │               │                             │
  ├──────────────────────────┼───────────────┼─────────────────────────────┤
  │ d-010 hospedagem 480,00  │ parcial       │ 0 (motivo depende da        │
  │                          │ 250,00        │ decisão 2)                  │
  ├──────────────────────────┼───────────────┼─────────────────────────────┤
  │ d-011 alimentação 33,33  │ limite 90     │ limite 112,50 ou 75         │
  │                          │ (viagem)      │ (depende da decisão 2)      │
  ├──────────────────────────┼───────────────┼─────────────────────────────┤
  │ d-014 alimentação 61,00  │ parcial 60,00 │ aprovado 61,00              │
  ├──────────────────────────┼───────────────┼─────────────────────────────┤
  │ Total reembolsado        │ 585,43        │ 351,43                      │
  └──────────────────────────┴───────────────┴─────────────────────────────┘

  Seção 7. Os mais de 60 casos de borda usam os valores 60, 80 e 250 sem dizer
  de qual centro de custo são. Hoje eles só fecham se forem lidos como "política
  padrão". Os testes também não definem centro de custo, então caem no padrão.

  As opções:
  - (a) Recalcular o exemplo com o CC-ENG e manter os casos da seção 7 no padrão
    (minha recomendação).
    - A tabela da seção 9 é refeita à mão com o resultado novo.
    - A seção 7 ganha uma frase: "salvo indicação, os casos usam um colaborador
      sem centro de custo, com a política padrão do politica-v4.json".
    - Os 63 casos e os testes deles continuam valendo.
    - É a leitura literal do envelope: política retroativa e exemplo de um
      centro de custo que está na tabela.
  - (b) Manter o resultado atual da seção 9, tirando o centro de custo do
    exemplo ou tratando o exemplo como da v3.
    - Exige alterar um arquivo de exemplo que é dado do desafio, ou manter duas
      políticas no sistema.
    - Sua regra de memória já alerta contra mexer nos dados fixos do desafio.
  - (c) Manter os dois: a tabela antiga com a política padrão e uma tabela nova
    com o CC-ENG.
    - Para a tabela antiga continuar valendo, seria preciso rodar o exemplo com
      outro centro de custo, o que não corresponde ao arquivo real.

⏺ User answered Claude's questions:
  ⎿  · Decisão 1: o exemplo da seção 9 (que é do CC-ENG-PLATAFORMA) e os casos 
     da seção 7? → Recalcular com CC-ENG (Recomendado)

  Made 1 scratchpad edit +3 -2 (ctrl+o to expand)

⏺ Decisão 1 registrada: o exemplo da seção 9 será recalculado com o CC-ENG, e os
  casos da seção 7 ficam na política padrão.

  Decisão 3: quando vale a "política padrão" e o que ela é

  O comunicado diz uma frase só: "Alguns centros de custo não têm entrada na 
  tabela. Nesse caso, aplica-se a política padrão." Ela deixa três perguntas.

  3a. Centro de custo que existe na tabela, mas sem a categoria.
  O CC-ADM só tem alimentação e transporte. Um colaborador do CC-ADM lança uma
  hospedagem de 300,00 com nota. Duas leituras:
  - "Completa com o padrão": a categoria que falta vem do bloco padrao, então a
    hospedagem tem limite 250,00 e é paga como parcial 250,00.
  - "A tabela do centro de custo é a lista fechada" (minha recomendação): se o
    financeiro não pôs hospedagem para o CC-ADM, ela não é coberta. Resultado:
    categoria_fora_da_politica, 0.
    - Por quê: o comunicado só manda usar o padrão quando o centro de custo
      inteiro não tem entrada.
    - O próprio arquivo mostra que o financeiro monta tabelas diferentes por
      centro de custo de propósito (o CC-ENG proíbe hospedagem). Completar com o
      padrão daria ao CC-ADM uma hospedagem que ninguém autorizou.
    - Risco: se a omissão foi um esquecimento do financeiro, o colaborador perde
      o reembolso. Mas o erro fica visível como recusa, não escondido.

  3b. Categoria que só existe em outro centro de custo.
  O caso f-003: um colaborador do CC-SUPORTE-N2 (fora da tabela, então usa o
  padrão) lança representacao de 190,00.
  - O bloco padrao não tem representação, então sai
    categoria_fora_da_politica, 0. Isso decorre da 3a: a lista de categorias
    reconhecidas é a da tabela aplicada ao colaborador.
  - A alternativa seria criar a representação para todos com algum limite, mas
    nenhum limite está escrito para isso. Seria inventar.

  3c. O que é o "padrão".
  - O bloco padrao do arquivo (minha recomendação). Ele muda junto com o resto
    quando o financeiro atualiza a tabela, e tudo vem do arquivo, como pede o
    item A.
  - A política v3 escrita na spec (60/80/250). Hoje os valores são iguais aos do
    bloco padrao, mas divergem se o financeiro editar o bloco. Manter os
    limites no código contraria "ler a política de fora".

  Consequência para a RN-006: ela deixa de ter as três categorias fixas. Passa a
  valer "categoria reconhecida é a que existe na tabela aplicada ao
  colaborador": a do centro de custo dele, ou o padrao se o centro de custo não
  está no arquivo.

⏺ User answered Claude's questions:
  ⎿  · Decisão 3a: centro de custo na tabela mas sem a categoria (ex.: CC-ADM + 
     hospedagem)? → Fora da política (Recomendado)
     · Decisão 3b: categoria que não está na tabela aplicada (ex.: f-003, 
     representacao num CC que caiu no padrão)? → Fora da política (Recomendado)
     · Decisão 3c: o que é a "política padrão"? → Bloco padrao do arquivo 
     (Recomendado)

  Made 1 scratchpad edit +3 -2 (ctrl+o to expand)

⏺ Decisão 3 registrada: o padrão é o bloco padrao do arquivo e vale só para
  centro de custo que não está no arquivo. Uma categoria que não existe na
  tabela aplicada ao colaborador sai categoria_fora_da_politica.

  Decisão 4: como o centro_custo da entrada é lido

  Hoje colaborador.centro_custo é opcional e não é usado. Agora ele escolhe a
  tabela de limites, então três perguntas.

  4a. Comparação com os nomes do arquivo
  - Exata (minha recomendação): "CC-ADM" só casa com CC-ADM.
    - "cc-adm" ou "CC-ADM " não estão na tabela e caem no padrão. O efeito pode
      ir para os dois lados: para o CC-ADM o padrão é mais generoso (alimentação
      60 contra 45), para o CC-COMERCIAL é menos (60 contra 90).
    - Por quê: é um código de cadastro, não texto livre digitado como a
      categoria.
    - Risco: errar a grafia muda a tabela sem nenhum alerta.
  - Normalizada como a categoria (seção 5: caixa, acento, separadores):
    "cc-adm", "CC ADM" e "CC_ADM" viram todos cc_adm e casam com CC-ADM.
    - Fecha a brecha da grafia, mas trata um código como texto livre.
    - Exige normalizar também os nomes do arquivo de política. Também é preciso
      decidir o que acontece se dois nomes do arquivo normalizarem igual: seria
      erro de arquivo.
  - Mitigação, qualquer que seja a escolha: a saída passa a mostrar qual tabela
    foi aplicada (decisão 14). O conferente vê "padrão" num colaborador que
    deveria ser CC-ADM.

  4b. Centro de custo ausente, nulo, vazio ou de tipo errado
  - Ausente, null ou texto vazio / só espaços → padrão (minha recomendação). É o
    mesmo caso de "centro de custo sem entrada na tabela", e mantém os testes e
    a seção 7 funcionando (decisão 1).
  - Tipo errado (17, true, objeto) → erro de arquivo. Faz parte do cabeçalho,
    como colaborador.id, e um tipo errado ali é arquivo malformado, não falta de
    informação.
    - Alternativa: tratar também o tipo errado como padrão. É mais tolerante,
      mas esconde o erro.

  4c. Centro de custo autodeclarado
  O colaborador pode escrever CC-COMERCIAL e ganhar alimentação 90, transporte
  150 e hospedagem 400. O sistema não tem cadastro para conferir.
  - Risco aceito, registrado na seção 10 (minha recomendação). É a mesma lógica
    do tem_nota_fiscal: o sistema confia no que vem na entrada, e a saída mostra
    o centro de custo e a tabela usada para a conferência humana.
  - Alternativa: exigir um cadastro de colaborador → centro de custo. Isso não
    existe nos dados e seria integração, que está fora de escopo.

⏺ User answered Claude's questions:
  ⎿  · Decisão 4a: como comparar o centro_custo da entrada com os nomes do 
     arquivo? → Exata (Recomendado)
     · Decisão 4b: centro_custo ausente, null, vazio ou de tipo errado? → 
     Ausente/vazio = padrão; tipo errado = erro (Recomendado)
     · Decisão 4c: o colaborador declara o próprio centro de custo; o sistema 
     não tem como conferir. → Risco aceito, seção 10 (Recomendado)

  Made 1 scratchpad edit +3 -2 (ctrl+o to expand)

⏺ Decisão 4 registrada: comparação exata; ausente ou vazio usa o padrão; tipo
  errado é erro de arquivo; centro de custo autodeclarado é risco aceito.

  Decisão 2: hospedagem "não reembolsável" no CC-ENG (limite 0)

  O arquivo traz "hospedagem": { "limite": 0.00, "observacao": "nao 
  reembolsavel" } para o CC-ENG-PLATAFORMA. Ou seja, a categoria está na tabela
  (então a decisão 3 não se aplica), mas com limite zero.

  Duas coisas dependem desta decisão:
  - O motivo da recusa. É o que o colaborador vê.
  - Se essa hospedagem comprova viagem. Isso amplia em 50% os limites de
    alimentação e transporte na data dela e no dia seguinte (RN-010).

  Pela seção 8, só comprova viagem a hospedagem com nota que passou pelas etapas
  1 a 7. O limite é a etapa 9; a categoria é a etapa 5. Então o motivo
  escolhido decide automaticamente a viagem.

  (a) Limite 0 aplicado na etapa 9 → limite_diario_excedido, e comprova viagem
  - Não exige regra nova: o limite 0 é só mais um número da tabela.
  - Exemplo da seção 9: d-010 (480,00) → recusado, limite_diario_excedido,
    limite_diario 0. A d-011 (33,33 em 15/07) fica em viagem com limite 112,50.
  - Brecha: uma hospedagem de 0,01 com nota declarada coloca dois dias em viagem
    e amplia alimentação de 75 para 112,50 e transporte de 80 para 120, numa
    categoria que a política diz que não reembolsa.
  - O motivo diz "excedeu o limite", quando na verdade a categoria é vedada.

  (b) Limite 0 tratado como categoria vedada na etapa 5 → 
  categoria_fora_da_politica, e não comprova viagem (minha recomendação)
  - Regra nova na RN-006: categoria com limite 0 na tabela aplicada é tratada
    como fora da política.
  - Exemplo da seção 9: d-010 → recusado, categoria_fora_da_politica,
    limite_diario nulo. A d-011 fica fora de viagem, com limite 75 (aprovado com
    33,33 de qualquer forma).
  - Fecha a brecha e o motivo diz a verdade ("não reembolsa de forma alguma").
  - Custo: um engenheiro em viagem real, com hotel pago pela empresa por outro
    meio, perde a ampliação dos limites. Mas para o CC-ENG a política só fala em
    hospedagem, não proíbe a viagem. Esse é um risco a aceitar.

  (c) Motivo novo, por exemplo categoria_nao_reembolsavel
  - Mesmo efeito de (b), com um motivo próprio que distingue "categoria
    inexistente" de "categoria vedada".
  - Custo: um código de motivo a mais no contrato de saída.

  Efeito no total do exemplo: nenhum. A d-011 é aprovada com 33,33 sob qualquer
  limite (75 ou 112,50), então o total continua 351,43.
⏺ User answered Claude's questions:
  ⎿  · Decisão 2: hospedagem com limite 0 no CC-ENG-PLATAFORMA ("nao 
     reembolsavel")? → categoria_fora_da_politica (Recomendado)

  Made 1 scratchpad edit +3 -2 (ctrl+o to expand)

⏺ Decisão 2 registrada: limite 0 é tratado como categoria vedada
  (categoria_fora_da_politica), e essa hospedagem não comprova viagem.

  Decisão 10: acréscimo de viagem

  Hoje a RN-009 tem a tabela fixa com os limites em viagem escritos por extenso
  (90 / 120 / 250), e a hospedagem não amplia (AMB-006). O arquivo traz um único
  "acrescimo_em_viagem_percentual": 50, sem dizer a quais categorias se aplica.

  10a. De onde vem o percentual
  - Do arquivo (minha recomendação): limite em viagem = limite normal × (1 +
    percentual/100). É coerente com "ler a política de fora".
  - A tabela da RN-009 com os valores escritos por extenso sai da spec.

  10b. A quais categorias se aplica

  ┌────────────────────┬─────────────────┬──────────────┬──────────────────┐
  │                    │    Leitura      │ Todas exceto │                  │
  │     Categoria      │   restritiva    │  hospedagem  │      Todas       │
  │                    │   (recomendo)   │              │                  │
  ├────────────────────┼─────────────────┼──────────────┼──────────────────┤
  │ alimentação        │ amplia          │ amplia       │ amplia           │
  ├────────────────────┼─────────────────┼──────────────┼──────────────────┤
  │ transporte urbano  │ amplia          │ amplia       │ amplia           │
  ├────────────────────┼─────────────────┼──────────────┼──────────────────┤
  │                    │                 │              │ amplia           │
  │ hospedagem         │ não (AMB-006)   │ não          │ (CC-COMERCIAL:   │
  │                    │                 │              │ 600)             │
  ├────────────────────┼─────────────────┼──────────────┼──────────────────┤
  │ representação      │ não             │ amplia (300  │ amplia           │
  │                    │                 │ → 450)       │                  │
  ├────────────────────┼─────────────────┼──────────────┼──────────────────┤
  │ categoria nova que │                 │              │                  │
  │  o financeiro      │ não             │ amplia       │ amplia           │
  │ criar              │                 │              │                  │
  └────────────────────┴─────────────────┴──────────────┴──────────────────┘

  - Restritiva: só alimentação e transporte, como hoje (minha recomendação).
    - Mantém o sentido original da política: o acréscimo compensa comer e se
      deslocar fora de casa.
    - Representação já é um gasto de contexto especial, com limite próprio e
      alto, como a hospedagem.
    - Custo: se o financeiro criar uma categoria nova (por exemplo
      "lavanderia"), ela não amplia até a spec mudar. A lista de categorias que
      ampliam fica na spec, não no arquivo.
  - Todas exceto hospedagem: qualquer categoria nova amplia automaticamente,
    inclusive representação. A tabela muda sozinha, mas a ampliação passa a
    valer para categorias que ninguém pensou.
  - Todas: contradiz a AMB-006, que hoje tem justificativa ("toda hospedagem já
    é viagem").

  10c. Arredondamento do limite ampliado
  Com os valores atuais o resultado é sempre exato: 75 × 1,5 = 112,50; 90 × 1,5
  = 135,00; 150 × 1,5 = 225,00. Mas a tabela muda sem aviso: 33,33 × 1,5 =
  49,995.
  - Arredondar ao centavo, metade afastando do zero (minha recomendação): mesma
    regra da RN-003, e 49,995 vira 50,00. Uma regra só de arredondamento em toda
    a spec.
  - Truncar: 49,99. Favorece a empresa, mas cria uma segunda regra de
    arredondamento.
  - Erro de arquivo se o limite ampliado não fechar ao centavo: é rígido, e o
    financeiro não tem como saber disso.

  Também: o próprio percentual precisa ser validado. Negativo, texto ou ausente
  seria erro de arquivo, pela decisão 11.

⏺ User declined to answer questions
  ⎿  · Decisão 10b: o acréscimo de viagem do arquivo vale para quais categorias?
     (Só alimentação e transporte (Recomendado) / Todas exceto hospedagem / 
     Todas)
     · Decisão 10c: limite ampliado que não fecha no centavo (ex.: 33,33 × 1,5 =
     49,995)? (Arredondar como RN-003 (Recomendado) / Truncar / Erro de 
     arquivo)

  Made 1 scratchpad edit +3 -2 (ctrl+o to expand)

⏺ Registrei a 10b: o acréscimo vale só para alimentação e transporte.

  Antes de seguir, você quis esclarecer algo na 10c (arredondamento do limite
  ampliado). O que ficou confuso: o próprio exemplo de 49,995, a diferença entre
  arredondar e truncar, ou se isso chega a acontecer na prática?

  Ainda está aberta também a 10a: o percentual vem do arquivo, em vez dos
  valores escritos na spec. Não fiz uma pergunta separada para ela; posso juntar
  com a 10c quando eu repetir.

✻ Baked for 1m 52s · done 8:27 PM

❯ arredondar nao daria margem de bater num limite de pedir nota fiscal? o       
  melhor nao seria truncar?                                                     

⏺ Não dá margem: o limite ampliado e a exigência de nota fiscal são verificações
  independentes.

  Por que não se cruzam:
  - A RN-008 (nota fiscal) compara o valor da própria despesa com 100,00, na
    etapa 6, antes de qualquer limite. A AMB-008 fixou isso de propósito:
    "compara com o valor individual, antes de qualquer limite".
  - O limite diário só entra na etapa 9 e só define quanto se paga de uma
    despesa que já passou pela nota.
  - Então uma despesa de 100,01 sem nota é recusada seja o limite 49,99, 50,00
    ou 500,00. E uma de 99,99 sem nota segue, e só depois é cortada pelo limite.

  O que muda de verdade entre arredondar e truncar: no máximo 1 centavo no teto
  pago por data e categoria, e só quando a tabela tiver um limite que não fecha
  no centavo depois de ampliado. Com a v4 de hoje isso não acontece: 75 →
  112,50, 90 → 135,00, 60 → 90,00, 80 → 120,00 e 150 → 225,00 são todos exatos.

  Ainda assim, truncar tem um argumento bom, diferente do que você levantou: um
  limite é um teto. "Ampliado em 50%" com 33,33 dá no máximo 49,995. Pagar 50,00
  passa do teto literal em meio centavo; truncar para 49,99 nunca passa.
  - Arredondar: uma regra só de arredondamento na spec inteira (a da RN-003).
    Pode pagar até meio centavo acima do teto literal.
  - Truncar: o teto nunca é ultrapassado. Custa uma segunda regra, que vale só
    para o limite ampliado.

  As duas são defensáveis. A sua leitura de teto é coerente com a ideia de
  limite, então o truncamento é uma boa escolha.

⏺ User answered Claude's questions:
  ⎿  · Decisão 10c: limite ampliado que não fecha no centavo (ex.: 33,33 × 1,5 =
     49,995)? → Truncar (teto nunca excedido)
     · Decisão 10a: o percentual de viagem passa a vir do arquivo 
     (acrescimo_em_viagem_percentual), substituindo a tabela 90/120/250 escrita 
     na RN-009? → Vem do arquivo (Recomendado)

  Made 1 scratchpad edit +4 -2 (ctrl+o to expand)

⏺ Decisão 10 registrada:
  - 10a: o percentual vem do arquivo.
  - 10b: o acréscimo vale só para alimentação e transporte.
  - 10c: o limite ampliado é truncado ao centavo, para nunca passar do teto.

  Decisão 9: despesa em moeda estrangeira caracteriza viagem?

  O comunicado diz: "Colaboradores em viagem internacional lançam despesas em 
  moeda estrangeira." Hoje, pela RN-010 e AMB-004, a viagem só é comprovada por
  hospedagem com nota (data D e D+1).

  No envelope, as despesas de Lisboa (e-002 a e-005, de 14/07 a 20/07) não têm 
  hospedagem; a única é a e-007, em Londres, em 22/07. O CC-COMERCIAL tem
  alimentação 90 e, em viagem, 135.

  ┌────────────────┬──────────┬─────────────────────────┬──────────────────┐
  │                │ valor em │  só hospedagem prova    │      moeda       │
  │      item      │    BRL   │         (hoje)          │   estrangeira    │
  │                │          │                         │      prova       │
  ├────────────────┼──────────┼─────────────────────────┼──────────────────┤
  │ e-002 22 EUR,  │ 130,46   │ parcial 90,00           │ aprovado 130,46  │
  │ 14/07          │          │                         │ (limite 135)     │
  ├────────────────┼──────────┼─────────────────────────┼──────────────────┤
  │ e-003 14,50    │ 85,26    │ aprovado 85,26          │ aprovado 85,26   │
  │ EUR, 15/07     │          │                         │                  │
  ├────────────────┼──────────┼─────────────────────────┼──────────────────┤
  │ e-004 30 EUR,  │ ~178,80  │ parcial 90,00           │ parcial 135,00   │
  │ sábado         │          │                         │                  │
  ├────────────────┼──────────┼─────────────────────────┼──────────────────┤
  │ e-005 40 USD,  │          │ (sem nota → recusado    │                  │
  │ transporte     │ 220,00   │ pela RN-008 se comparar │ idem             │
  │                │          │  em BRL)                │                  │
  └────────────────┴──────────┴─────────────────────────┴──────────────────┘

  (a) Não: a viagem continua sendo comprovada só pela hospedagem com nota (minha
  recomendação)
  - A frase do comunicado descreve quem lança em moeda estrangeira; não cria uma
    regra nova de viagem.
  - A moeda é declarada pelo colaborador, como o centro de custo. Se ela
    comprovasse viagem, bastaria lançar um almoço de 1 USD para ampliar os
    limites do dia, numa brecha maior que a da hospedagem de 0,01: nem nota
    exige.
  - Custo: quem está no exterior sem hospedagem lançada (hotel pago pela
    empresa, casa de amigos) não ganha a ampliação. O resultado do Lisboa fica
    "injusto" no envelope (e-002 parcial). Fica registrado como risco ou
    evolução.

  (b) Sim: despesa válida em moeda diferente de BRL comprova viagem na data dela
  - A saber: em quais datas (D? D e D+1?), se exige nota, e se uma despesa
    recusada por outra regra ainda comprova.
  - Abre a brecha do almoço de 1 USD.
  - Resultado mais "justo" para Lisboa.

  (c) Sim, mas exigindo nota fiscal, como a hospedagem: despesa em moeda
  estrangeira com nota que passou pelas etapas 1 a 7 comprova viagem na data
  dela.
  - Restringe a brecha ao mesmo nível da hospedagem irrisória com nota.
  - No envelope: e-002 (com nota) põe 14/07 em viagem → aprovado 130,46; e-003
    (sem nota) não prova nada; e-004 (com nota) amplia 18/07.

⏺ User answered Claude's questions:
  ⎿  · Decisão 9: despesa em moeda estrangeira caracteriza viagem? → Não, só 
     hospedagem (Recomendado)

  Made 1 scratchpad edit +3 -2 (ctrl+o to expand)

⏺ Decisão 9 registrada: moeda estrangeira não caracteriza viagem; a viagem
  continua sendo comprovada só pela hospedagem com nota.

  Decisão 6: data da despesa sem cotação no câmbio

  O comunicado manda usar "a taxa da data da despesa". O cambio.json avisa:
  "Cotações publicadas apenas em dias úteis bancários". E o arquivo só vai de
  13/07 a 28/07.

  Os buracos:
  - Fim de semana: e-004, 30 EUR em 18/07 (sábado).
  - Feriado bancário: mesmo caso (o arquivo não diz quais são).
  - Dia útil fora do arquivo: uma despesa em USD em 06/07 (segunda) não tem
    taxa, e não existe nenhuma cotação anterior no arquivo.

  A escolha muda a aprovação, não só o valor. 16,70 EUR de alimentação, sem
  nota, num sábado:
  - taxa da sexta (5,96) → 99,53: não exige nota, segue;
  - taxa da segunda (6,01) → 100,37: nota_fiscal_ausente, 0.

  (a) Última cotação anterior disponível, com limite de dias (minha 
  recomendação)
  - É a prática da PTAX: o câmbio de um sábado é o da sexta.
  - Sábado → sexta; domingo → sexta; feriado → dia útil anterior.
  - Limite proposto: até 3 dias corridos antes. Cobre fim de semana e um feriado
    prolongado (segunda de feriado → sexta). Sem limite, uma despesa de 06/07
    sem cotação no arquivo buscaria uma taxa inexistente; com limite, se não
    houver cotação nos 3 dias anteriores → recusa com motivo novo
    cambio_indisponivel.
  - O número 3 é uma escolha sua; 4 cobriria também feriado em sexta mais fim de
    semana.

  (b) Próxima cotação disponível (dia útil seguinte)
  - Menos usual. Num sábado, a cotação de segunda é publicada depois da despesa;
    dá para argumentar que é o câmbio da liquidação no cartão, mas não é "a
    taxa da data da despesa".

  (c) Recusar sempre que não houver taxa exata na data → cambio_indisponivel
  - Leitura literal. Toda despesa em moeda estrangeira de fim de semana é
    recusada; e-004 → 0.
  - Pune o colaborador por algo fora do controle dele, com dados que existem (a
    cotação de sexta).

  (d) Sem limite de dias, a última cotação anterior qualquer que seja.
  - Uma despesa de 06/07 ainda não teria taxa (nada antes de 13/07), então
    continua precisando do motivo cambio_indisponivel. E uma lacuna de semanas
    no arquivo passaria em silêncio.

  Também fica decidido: a saída mostra a data da cotação usada (decisão 14),
  para o conferente ver que o sábado usou a taxa de sexta.

⏺ User answered Claude's questions:
  ⎿  · Decisão 6: sem cotação na data da despesa (fim de semana, feriado, fora 
     do arquivo)? → Anterior, até 3 dias (Recomendado)

  Made 1 scratchpad edit +3 -2 (ctrl+o to expand)

⏺ Decisão 6 registrada: sem cotação na data, vale a última cotação dos 3 dias
  corridos anteriores. Se não houver nenhuma, a despesa é recusada com o motivo
  novo cambio_indisponivel.

  Decisão 7: moeda sem cotação ou mal formada

  Hoje moeda é um campo extra, ignorado. Agora ele decide a conversão. Os casos
  possíveis:

  ┌──────────────────────┬──────────────┬───────────────────────────────────┐
  │   moeda na despesa   │   Exemplo    │        Minha recomendação         │
  ├──────────────────────┼──────────────┼───────────────────────────────────┤
  │ ausente              │ e-010        │ BRL (o comunicado diz isso)       │
  ├──────────────────────┼──────────────┼───────────────────────────────────┤
  │                      │              │ BRL, igual a ausente (mesma       │
  │ null                 │ —            │ lógica do centro_custo, decisão   │
  │                      │              │ 4b)                               │
  ├──────────────────────┼──────────────┼───────────────────────────────────┤
  │                      │              │ taxa 1, sem consultar o câmbio (o │
  │ "BRL"                │ e-001        │  cambio.json não tem BRL, e não   │
  │                      │              │ precisa ter)                      │
  ├──────────────────────┼──────────────┼───────────────────────────────────┤
  │ código de 3 letras   │              │                                   │
  │ maiúsculas com       │ "EUR", "USD" │ converte (decisão 6)              │
  │ cotação              │              │                                   │
  ├──────────────────────┼──────────────┼───────────────────────────────────┤
  │ código de 3 letras   │              │                                   │
  │ maiúsculas sem       │ e-006 "GBP"  │ cambio_indisponivel               │
  │ cotação no arquivo   │              │                                   │
  ├──────────────────────┼──────────────┼───────────────────────────────────┤
  │ minúsculas ou com    │ "eur", " EUR │ entrada_invalida                  │
  │ espaço               │  "           │                                   │
  ├──────────────────────┼──────────────┼───────────────────────────────────┤
  │                      │ "R$",        │                                   │
  │ outro formato        │ "euro", "",  │ entrada_invalida                  │
  │                      │ 978, true    │                                   │
  └──────────────────────┴──────────────┴───────────────────────────────────┘

  Os dois pontos em disputa:

  7a. Grafia diferente ("eur", " EUR ")
  - entrada_invalida (minha recomendação): ISO 4217 é sempre 3 letras
    maiúsculas. É um código, como o centro de custo (decisão 4a, comparação
    exata).
  - Normalizar (maiúsculas, sem espaços): mais tolerante, mas incoerente com o
    centro de custo, e cria uma terceira forma de comparar texto na spec.
  - Ao contrário do centro de custo, aqui o erro não pode cair num "padrão": não
    há uma moeda segura para supor. Por isso recusa, em vez de assumir BRL.

  7b. Código válido sem cotação (GBP), e se é preciso validar contra a lista ISO
  4217
  - cambio_indisponivel para qualquer código de 3 letras maiúsculas sem cotação 
    (minha recomendação). Não verifica se o código existe de fato na ISO 4217:
    "XYZ" também sai cambio_indisponivel.
    - Evita embutir a lista ISO, que muda ao longo do tempo.
    - O motivo é verdadeiro: não há câmbio para converter.
  - Alternativa: verificar contra a lista ISO e dar entrada_invalida para "XYZ".
    Exige manter a lista; ganho pequeno.

  Também: um código igual a "BRL" no arquivo de câmbio (se o financeiro incluir)
  seria ignorado, porque BRL tem sempre taxa 1.

⏺ User answered Claude's questions:
  ⎿  · Decisão 7a: moeda escrita com grafia diferente ("eur", " EUR ")? → 
     entrada_invalida (Recomendado)
     · Decisão 7b: código de 3 letras maiúsculas sem cotação no arquivo (GBP no 
     e-006, ou "XYZ")? → cambio_indisponivel (Recomendado)
     · Decisão 7c: moeda null e moeda "BRL"? → null = BRL; BRL taxa 1 
     (Recomendado)

  Made 1 scratchpad edit +3 -2 (ctrl+o to expand)

⏺ Decisão 7 registrada:
  - 7a: moeda fora do formato de 3 letras maiúsculas é entrada_invalida.
  - 7b: código bem formado sem cotação (GBP, "XYZ") é cambio_indisponivel.
  - 7c: moeda ausente ou null é BRL, e BRL tem taxa 1.

  Decisão 8: arredondamento e conversão, e sobre qual valor valem o teto e o 
  "valor positivo"

  Hoje a RN-003 diz: antes de qualquer outra regra, valor é arredondado ao 
  centavo. Com moeda estrangeira, existem duas contas possíveis.

  (a) Arredondar na moeda original, converter e arredondar de novo (dois
  arredondamentos)
  (b) Converter o valor exato e arredondar uma vez só, em reais (minha 
  recomendação)

  Onde muda o resultado. 16,8649 EUR de alimentação, sem nota, em 14/07 (taxa
  5,93):
  - (a) 16,86 × 5,93 = 99,9798 → 99,98: não exige nota, segue.
  - (b) 16,8649 × 5,93 = 100,008857 → 100,01: nota_fiscal_ausente, 0.

  Por que (b):
  - O valor em reais é o que importa para todas as regras (limite, nota,
    totais). Arredondar antes de converter cria um erro que a taxa multiplica:
    um centavo em EUR vira até 6 centavos em BRL.
  - Um único arredondamento, com a mesma regra da RN-003 (metade afastando do
    zero).
  - Para despesa em BRL nada muda: taxa 1, resultado idêntico ao de hoje.
  - O exemplo acima é artificial (4 casas decimais em EUR); com valores reais de
    2 casas a diferença é rara, mas existe.

  8b. Teto de um bilhão (AMB-018, RN-002)
  Hoje: valor absoluto a partir de 1.000.000.000 → entrada_invalida, comparado
  com o número recebido. Com moeda: 200.000.000 USD ≈ 1,1 bilhão BRL.
  - Comparar só o número recebido, na moeda original (minha recomendação). O
    teto existe para garantir que o cálculo seja exato e que a leitura não
    quebre, e isso é uma questão da forma do número, não do valor econômico. É
    verificado na etapa 1, antes da conversão (que precisa do câmbio).
    - Consequência: um valor convertido pode passar de um bilhão. As contas
      continuam exatas (taxas de poucas casas × valor até 10^9 cabem com folga
      nos 28 dígitos de precisão) e qualquer limite diário corta o reembolso.
  - Alternativa: comparar também o convertido. Seria uma segunda verificação
    depois da conversão, com um motivo próprio. Ganho prático zero.

  8c. Valor positivo (RN-004, valor_invalido)
  - Aplicar ao valor convertido e arredondado em reais (minha recomendação): é o
    valor_considerado. 0,001 EUR → 0,00591 → 0,01 BRL: positivo, segue (e é
    reembolsado em 0,01).
  - Alternativa: aplicar à moeda original arredondada. 0,004 EUR → 0,00 →
    valor_invalido, mesmo valendo 0,02 em reais.

  Em resumo, (b) significa: valor_considerado = valor × taxa, arredondado uma
  vez ao centavo, e todas as regras de valor (positivo, nota, duplicata?,
  limite, totais) usam esse número em reais. A duplicata é a decisão 13,
  separada.

⏺ User answered Claude's questions:
  ⎿  · Decisão 8a: arredondamento com conversão? → Converte exato, arredonda 1x 
     (Recomendado)
     · Decisão 8b: teto de 1 bilhão (AMB-018)? → Só o número recebido 
     (Recomendado)
     · Decisão 8c: valor positivo (RN-004) se verifica sobre qual valor? → 
     Convertido em reais (Recomendado)

  Made 1 scratchpad edit +3 -2 (ctrl+o to expand)

⏺ Registrei a decisão 8 (conversão para reais, teto e checagem de valor
  positivo) e notei que isso exige mover a conversão antes da etapa 3, mudando
  minha recomendação anterior. Também analisei a decisão 5 (limite da nota
  fiscal), recomendando comparar em reais com o valor já convertido e trazer o
  limite de 100,00 do arquivo em vez de fixá-lo na spec — e pergunto se quer
  mais detalhes ou se sigo direto com as perguntas.

⏺ User answered Claude's questions:
  ⎿  · Decisão 5a: o limite da nota fiscal compara qual valor? → Convertido em 
     reais (Recomendado)
     · Decisão 5b: o valor mínimo da nota (100,00) vem do arquivo? → Vem do 
     arquivo (Recomendado)

  Made 1 scratchpad edit +3 -2 (ctrl+o to expand)

⏺ Todas as 11 bloqueantes estão decididas. Faltam as importantes (12 a 15) e as
  menores (16 e 17).

  Decisão 12: onde a conversão entra na ordem das etapas (seção 8)

  Ordem atual:

  1 validação → 2 arredondamento → 3 valor positivo → 4 período → 5 categoria → 
  6 nota → 7 duplicata → 8 viagem → 9 limite

  A decisão 8c (valor positivo verificado em reais) obriga a conversão a
  acontecer antes da etapa 3. A pergunta é o que fazer quando não há cotação
  (cambio_indisponivel), porque cada despesa recusada tem um motivo só, o da
  primeira etapa que a recusa.

  (a) Conversão junto com o arredondamento, na etapa 2 (minha recomendação)

  1 validação → 2 conversão + arredondamento (sem cotação: cambio_indisponivel) 
  → 3 positivo → 4 período → 5 categoria → ...

  - Sem valor em reais, nenhuma regra seguinte de valor consegue ser avaliada.
    Por isso recusa ali mesmo.
  - A ordem das etapas atuais não muda: para despesa em BRL o resultado é
    idêntico ao de hoje.
  - Custo: quando há dois problemas, o motivo mostrado é o câmbio.
    - Uma despesa em GBP de 15/04 sai cambio_indisponivel, não fora_do_periodo.
    - Um coworking em GBP sai cambio_indisponivel, não
      categoria_fora_da_politica.
    - O motivo é verdadeiro, mas menos útil para o colaborador.

  (b) Período e categoria antes da conversão

  1 validação → 2 período → 3 categoria → 4 conversão + arredondamento → 5 
  positivo → 6 nota → ...

  - Os motivos ficam mais informativos: coworking em GBP sai
    categoria_fora_da_politica.
  - Custo: muda a ordem atual entre valor positivo e período, e isso muda
    resultados que já existem. Um estorno (-45,00) de abril hoje sai
    valor_invalido e passaria a sair fora_do_periodo.
    - É uma mudança fora do que o envelope pede, e quebra testes de ordem da
      AMB-016 que já existem.

  Efeito nos dados do envelope: nenhum nas duas opções. O único item sem cotação
  é o e-006 (GBP), que está no período e cuja categoria (representacao) existe
  no CC-COMERCIAL. Ele sai cambio_indisponivel em qualquer ordem.

⏺ User answered Claude's questions:
  ⎿  · Decisão 12: onde entra a conversão (e a recusa cambio_indisponivel) na 
     seção 8? → Na etapa 2, com o arredondamento (Recomendado)

  Made 2 scratchpad edits +6 -4 (ctrl+o to expand)

⏺ Registro a decisão 13 sobre duplicatas entre moedas: recomendo comparar valor
  original junto com a moeda (arredondado ao centavo), em vez do valor
  convertido em reais, já que isso evita falsos positivos e desacopla a regra do
  câmbio — sem efeito nos dados atuais, pois não há duplicatas.
⏺ User answered Claude's questions:
  ⎿  · Decisão 13: duplicata compara qual valor? → Original + moeda 
     (Recomendado)

  Made 1 scratchpad edit +3 -2 (ctrl+o to expand)

⏺ Decisão 13 registrada: a duplicata compara o valor original arredondado mais a
  moeda.

  Decisão 14: campos novos na saída

  Hoje nenhum campo contratual da saída mostra moeda, taxa, centro de custo ou
  política aplicada. O conferente veria o e-002 com valor_informado 22.0 e
  valor_considerado 130.46 sem saber de onde veio a diferença. E como a tabela
  "muda sem aviso", não daria para reconstituir depois qual política foi usada.
  A justificativa poderia dizer isso, mas ela não é contratual: os testes não a
  fixam.

  Proposta completa (minha recomendação). São campos contratuais, testados.

  Por item, logo depois de valor_informado:

  ┌──────────────┬──────────┬────────────────────────────────────────────────┐
  │    Campo     │   Tipo   │                    Conteúdo                    │
  ├──────────────┼──────────┼────────────────────────────────────────────────┤
  │              │ texto ou │ código usado: "BRL" quando ausente ou null;    │
  │ moeda        │  nulo    │ como veio, se for texto; nulo se o item não é  │
  │              │          │ um objeto ou se moeda tem tipo errado          │
  ├──────────────┼──────────┼────────────────────────────────────────────────┤
  │ taxa_cambio  │ número   │ taxa usada (1 para BRL); nula se recusado na   │
  │              │ ou nulo  │ etapa 1 ou por cambio_indisponivel             │
  ├──────────────┼──────────┼────────────────────────────────────────────────┤
  │ data_cotacao │ texto ou │ data da cotação usada (sábado → a sexta); nula │
  │              │  nulo    │  para BRL e quando não houve conversão         │
  └──────────────┴──────────┴────────────────────────────────────────────────┘

  O significado de dois campos muda:
  - valor_informado passa a ser "o número recebido, na moeda da despesa".
  - valor_considerado passa a ser "convertido em reais e arredondado".

  No topo:

  ┌──────────────────────────┬───────────────────────────────────────────────┐
  │          Campo           │                   Conteúdo                    │
  ├──────────────────────────┼───────────────────────────────────────────────┤
  │ colaborador.centro_custo │ como veio, se texto; nulo se ausente ou null  │
  ├──────────────────────────┼───────────────────────────────────────────────┤
  │ politica.versao          │ o versao do arquivo ("v4")                    │
  ├──────────────────────────┼───────────────────────────────────────────────┤
  │ politica.vigencia        │ o vigencia do arquivo                         │
  ├──────────────────────────┼───────────────────────────────────────────────┤
  │ politica.tabela_aplicada │ o centro de custo usado ou "padrao" (é o que  │
  │                          │ expõe a brecha da grafia, decisões 4a e 4c)   │
  └──────────────────────────┴───────────────────────────────────────────────┘

  Exemplo de item (e-004, sábado):

  { "id": "e-004", "data": "2026-07-18", "categoria": "alimentacao",
    "valor_informado": 30.00, "moeda": "EUR", "taxa_cambio": 5.96,
  "data_cotacao": "2026-07-17",
    "valor_considerado": 178.80, "valor_reembolsado": 90.00, "status":
  "parcial", ... }

  Alternativas:
  - Mínima: só moeda e taxa_cambio por item, sem nada no topo. Não registra a
    política usada nem a tabela aplicada.
  - Só na justificativa: nenhum campo novo. O contrato não muda, mas nada disso
    é verificável por teste.

  Custo da proposta completa: muda o contrato de saída. saida.py ganha campos, e
  os testes que comparam a saída inteira precisam incluir os campos novos. Os
  testes que olham campo a campo não mudam.

⏺ User answered Claude's questions:
  ⎿  · Decisão 14: o que a saída passa a mostrar? → Completa (Recomendado)

  Made 1 scratchpad edit +3 -2 (ctrl+o to expand)

⏺ Decisão 14 registrada: saída completa. Por item: moeda, taxa_cambio e
  data_cotacao. No topo: colaborador.centro_custo e o bloco politica.

  Decisão 15: o campo vigencia do arquivo de política

  O arquivo diz "vigencia": "2026-07-01", e o comunicado diz "vigência imediata,
  retroativa à competência atual". Nos dados do envelope e no exemplo, todas as
  despesas são de julho de 2026, então nenhum resultado muda. A decisão só
  importa para casos fora disso: um período que começa em junho, ou um arquivo
  de política com vigência futura.

  Mudei minha recomendação aqui. Antes eu tinha sugerido recusar despesas
  anteriores à vigência. Revendo com a decisão 11 já tomada, prefiro outra
  opção, e explico o porquê.

  (a) Informativa: a vigência só é copiada para a saída (minha recomendação 
  agora)
  - Pela decisão 11, quem roda escolhe explicitamente qual política usar
    (--politica). Aplicar a política certa ao período é uma escolha visível na
    linha de comando, e a saída registra versão e vigência (decisão 14).
  - O sistema só conhece uma política por execução. Recusar uma despesa anterior
    à vigência a deixaria sem nenhum caminho de reembolso, porque não há uma v3
    para aplicar a ela.
  - Risco aceito: rodar despesas de junho com a v4 aplica a v4 sem aviso. Fica
    registrado na seção 10; o conferente vê a vigência na saída.

  (b) Despesa com data anterior à vigência → recusada com motivo novo 
  (fora_da_vigencia)
  - Impede aplicar uma política a despesas que ela não cobre.
  - Custo: a despesa fica sem reembolso possível nesta execução. Mais um motivo,
    mais uma etapa: provavelmente logo depois do período (etapa 4).

  (c) Vigência posterior ao fim do período → erro de arquivo
  - Pega o caso grosseiro: política que ainda nem começou a valer para o período
    inteiro. Não trata o caso de vigência no meio do período.
  - Pode ser combinada com (a).

  Detalhe: a vigência precisa ser uma data válida AAAA-MM-DD; senão, erro de
  arquivo (decisão 11), qualquer que seja a opção.

⏺ User answered Claude's questions:
  ⎿  · Decisão 15: o que a vigência do arquivo de política faz? → Informativa 
     (Recomendado)

  Made 1 scratchpad edit +3 -2 (ctrl+o to expand)

⏺ Decisão 15 registrada: a vigência é informativa, apenas copiada para a saída.

  Decisão 16: item C, aprovação manual acima de R$ 500 (opcional)

  O comunicado: "Itens cujo valor reembolsável passe de R$ 500 [...] entram em 
  estado de pendência aguardando aprovação do gestor. [...] cada item passa a 
  ter um estado." O próprio envelope diz que é opcional, que não implementar não
  perde ponto, e que deixar a spec inconsistente para chegar nele perde.

  O dado que pesa na decisão: com a v4, nenhum item tem reembolso acima de 500.
  O maior limite é a hospedagem do CC-COMERCIAL, 400, que não amplia (AMB-006).
  A representação é 300 e também não amplia (decisão 10b). Alimentação em viagem
  dá 135, transporte em viagem 225. Ou seja, lido literalmente ("valor
  reembolsável" do item), o item C nunca dispara com a tabela atual. Só
  dispararia se o financeiro subir algum limite acima de 500.

  (a) Não implementar agora; registrar na spec (minha recomendação)
  - A seção 3 ganha a linha "aprovação manual (item C da v4) não implementada",
    e o DECISIONS.md registra o motivo: opcional, e não dispara com a v4.
  - Se sobrar tempo depois de A e B, reabrimos a decisão e decidimos o resto (as
    perguntas abaixo).

  (b) Implementar com a leitura literal: reembolso do item > 500
  - Ainda é preciso decidir:
    - se pendente é um valor novo de status ou um campo separado (estado);
    - se combina com parcial (um item parcial de 520 fica pendente?);
    - se o valor pendente entra em totais.valor_reembolsado;
    - se o 500 vem do arquivo de política (hoje não está lá).
  - Código, testes e casos para uma regra que não dispara com nenhum dado do
    envelope; só seria testada com uma política inventada.

  (c) Implementar com outra leitura: valor considerado > 500, soma do dia, ou 
  total do período
  - Passaria a disparar (e-007, hotel de 1.200, ficaria pendente). Mas isso
    reinterpreta "valor reembolsável", que é o que sobra depois dos limites.
  - É exatamente o tipo de leitura forçada que o envelope avisa que custa ponto.

⏺ User answered Claude's questions:
  ⎿  · Decisão 16: item C (aprovação manual acima de R$ 500)? → Não implementar,
     registrar (Recomendado)

  Made 1 scratchpad edit +3 -2 (ctrl+o to expand)

⏺ Decisão 16 registrada: o item C não será implementado, e fica registrado na
  seção 3 e no DECISIONS.md.

  Decisão 17: textos da spec que a v4 contradiz

  Esta é de redação. Os efeitos de cálculo já saíram das decisões anteriores.
  Proponho o seguinte, trecho por trecho:

  Trecho: Seção 3: "Não converte moedas"
  O que fazer: Revogar. Entra: "não consulta câmbio externo; usa só o arquivo de

  câmbio recebido"
  ────────────────────────────────────────
  Trecho: Seção 3: "Não tem categoria de representação" (+ AMB-017)
  O que fazer: Reescrever: as categorias vêm da tabela aplicada. A AMB-017
  continua: refeição com cliente lançada como alimentacao é alimentação;
  representacao só existe onde a tabela a define
  ────────────────────────────────────────
  Trecho: Seção 3: "Não usa campos além da seção 4"
  O que fazer: Manter, porque a seção 4 passa a listar moeda e centro_custo
  ────────────────────────────────────────
  Trecho: Seção 3: novas linhas
  O que fazer: Item C não implementado (decisão 16); centro de custo não
  verificado contra cadastro (decisão 4c)
  ────────────────────────────────────────
  Trecho: Seção 4: valor "em reais"
  O que fazer: Reescrever: "na moeda da despesa"
  ────────────────────────────────────────
  Trecho: RN-006: três categorias fixas
  O que fazer: Reescrever com as decisões 2 e 3
  ────────────────────────────────────────
  Trecho: RN-008 e AMB-007: "100,00 fixo"
  O que fazer: Reescrever: valor do arquivo, comparado em reais; continua não
  ampliando em viagem
  ────────────────────────────────────────
  Trecho: RN-009: tabela 60/80/250 e 90/120/250
  O que fazer: Substituir pela regra "limite da tabela aplicada; em viagem, × (1

  + percentual), truncado"
  ────────────────────────────────────────
  Trecho: AMB-015: fim de semana não afeta nada
  O que fazer: Reescrever: não afeta o reembolso; afeta só qual cotação é usada
  (decisão 6)
  ────────────────────────────────────────
  Trecho: Seção 10: risco do fracionamento ("só quando o limite passa de 100:
  hospedagem e transporte em viagem")
  O que fazer: Reescrever sem lista fixa: o risco existe em toda categoria cujo
  limite passa do mínimo da nota (hoje inclui transporte do CC-COMERCIAL,
  representação e alimentação do CC-COMERCIAL em viagem)
  ────────────────────────────────────────
  Trecho: Seção 10: hospedagem irrisória ("até 70,00 por dia")
  O que fazer: Reescrever sem valor fixo: o ganho depende da tabela; com a v4,
  chega a 45 + 75 = 120 por dia no CC-COMERCIAL
  ────────────────────────────────────────
  Trecho: Seção 10: riscos novos
  O que fazer: Centro de custo autodeclarado (4c), viagem internacional sem
  hospedagem (9), mesmo gasto em moedas diferentes (13), política aplicada fora
   da vigência (15)

  O CLAUDE.md também tem uma lista "Fora de escopo" que copia a seção 3. Ele
  seria atualizado num docs(claude) separado.

⏺ User answered Claude's questions:
  ⎿  · Decisão 17: aplicar as reescritas da tabela acima na spec (e o Fora de 
     escopo do CLAUDE.md)? → Aplicar como proposto (Recomendado)

  Made 1 scratchpad edit +5 -2 (ctrl+o to expand)

⏺ Decisão 17 registrada. As 17 decisões estão tomadas; guardei o registro em um
  arquivo de rascunho para usar no DECISIONS.md.

  Resumo do que foi decidido:

  ┌─────┬────────────────────────────────────────────────────────────────────┐
  │  #  │                              Decisão                               │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │ 11  │ --politica e --cambio obrigatórios; defeito em qualquer um dos     │
  │     │ dois arquivos é erro de arquivo                                    │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │ 1   │ Seção 9 recalculada com o CC-ENG; casos da seção 7 sem centro de   │
  │     │ custo usam o padrão                                                │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │     │ O padrão é o bloco padrao do arquivo, só para centro de custo      │
  │ 3   │ ausente; categoria fora da tabela aplicada →                       │
  │     │ categoria_fora_da_politica                                         │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │ 4   │ centro_custo comparado exatamente; ausente ou vazio → padrão; tipo │
  │     │  errado → erro de arquivo; autodeclarado é risco aceito            │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │ 2   │ Limite 0 → categoria_fora_da_politica, e não comprova viagem       │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │ 10  │ Percentual de viagem vem do arquivo, só para alimentação e         │
  │     │ transporte, com o limite ampliado truncado                         │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │ 9   │ Moeda estrangeira não comprova viagem                              │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │ 6   │ Sem cotação na data: a anterior, até 3 dias antes; senão           │
  │     │ cambio_indisponivel                                                │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │ 7   │ moeda ausente ou null → BRL (taxa 1); 3 letras maiúsculas exatas,  │
  │     │ senão entrada_invalida; sem cotação → cambio_indisponivel          │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │ 8   │ Converte o valor exato e arredonda uma vez; teto sobre o número    │
  │     │ recebido; valor positivo sobre o valor em reais                    │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │ 5   │ Nota fiscal comparada em reais; o valor mínimo vem do arquivo      │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │ 12  │ Conversão na etapa 2; ordem das etapas mantida                     │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │ 13  │ Duplicata compara o valor original mais a moeda                    │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │ 14  │ Saída completa: moeda, taxa_cambio, data_cotacao por item; centro  │
  │     │ de custo e política no topo                                        │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │ 15  │ Vigência informativa                                               │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │ 16  │ Item C não implementado, registrado                                │
  ├─────┼────────────────────────────────────────────────────────────────────┤
  │ 17  │ Reescritas da seção 3, RN-006/008/009, AMB-007/015/017 e seção 10  │
  └─────┴────────────────────────────────────────────────────────────────────┘

  Próximos passos, seguindo o fluxo:
  1. Spec 2.0.
     - Aplicar as decisões: RN novas para centro de custo, moeda e câmbio, e
       arquivos de política e câmbio (RN-014 em diante).
     - Ambiguidades novas: AMB-020 em diante.
     - Casos novos na seção 7.
     - Seção 9 com duas tabelas calculadas à mão: o exemplo recalculado e os
       dois arquivos do envelope.
  2. DECISIONS.md (D-007): o que mudou, por quê, o que foi invalidado e quais
     tasks precisam ser refeitas.
  3. Rodar o spec-adversary de novo sobre a spec 2.0. Se aparecer algo
     bloqueante, voltamos a decidir antes de seguir.
  4. Depois: plan.md (leitura de política e câmbio, política passada como
     parâmetro) e as tasks T-022 em diante.

  Começo pelos passos 1 e 2? Ao terminar, te mostro as tabelas da seção 9 antes
  do adversário, porque elas são as contas mais fáceis de errar.

✻ Cogitated for 4m 13s · done 8:51 PM

❯ sim, segue com os passos 1 e 2                                                

  Ran 1 shell command (ctrl+o to expand)

⏺ Vou aplicar as decisões na spec, seção por seção. Começo pelo cabeçalho, pela
  seção 3 e pela seção 4.

  Ran 1 shell command (ctrl+o to expand)

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      1  # Spec — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.9 · **Status:** aprovada para planejamento · **Últ
        -ima alteração:** 2026-10-01 (ver `DECISIONS.md` D-001 a D-006)  
      3 +**Versão:** 2.0 · **Status:** em revisão (Política v4) · **Últim
        +a alteração:** 2026-10-02 (ver `DECISIONS.md` D-001 a D-007)    
      4  
      5  > **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ
         . Nenhuma linha
      6  > aqui pode citar linguagem, biblioteca, classe, função ou estru
         tura de pasta.

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 2 lines
      19  
      20  Dado o conjunto de despesas de um colaborador num período, calc
          ular de forma determinística quanto é reembolsável e justificar
           a decisão sobre cada despesa, aplicando uma interpretação únic
          a e documentada da política.
      21  
      22 +A partir da Política v4 (D-007), os limites não são mais fixos:
         + vêm de um **arquivo de política** mantido pelo financeiro, com
         + uma tabela por centro de custo e uma tabela padrão. Despesas p
         +odem vir em moeda estrangeira e são convertidas para reais pela
         +s taxas de um **arquivo de câmbio**. Os dois arquivos são receb
         +idos a cada execução (seção 4).                                
      23 +                                                               
      24  ## 3. Fora de escopo
      25  
      26  - Não aprova, paga nem integra com sistemas de pagamento ou fol
          ha: só calcula e justifica.

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 6 lines, removed 4 lines
      27  - Não processa mais de um colaborador ou mais de um período por
           execução.
      28  - Não verifica a autenticidade da nota fiscal; confia no indica
          dor `tem_nota_fiscal`.
      29  - Não lê nem interpreta o texto livre de `descricao` (nem para 
          contar diárias, AMB-005, nem para identificar refeição com clie
          nte, AMB-017).
      30 -- Não converte moedas: todos os valores são em reais.          
      30 +- Não consulta câmbio externo: converte moedas só com as taxas 
         +do arquivo de câmbio recebido (RN-015).                        
      31 +- Não verifica o centro de custo contra um cadastro de colabora
         +dores: usa o `centro_custo` declarado na entrada (AMB-020, risc
         +o na seção 10).                                                
      32 +- Não tem fila de aprovação manual (item C da Política v4, opci
         +onal): todo item sai com o status da RN-011, sem estado de pend
         +ência (AMB-030).                                               
      33  - Não guarda histórico entre execuções: duplicatas só são detec
          tadas dentro da mesma entrada.
      34  - Não usa campos além dos previstos na seção 4; campos extras s
          ão ignorados (RN-002). Em particular, não usa datas de entrada 
          e saída de hospedagem: seriam a solução ideal para AMB-005, mas
           o formato de entrada é fixo. Fica registrado como evolução rec
          omendada.
      33 -- Não tem categoria nem limite de representação (refeição com c
         -liente): fica registrado como evolução recomendada (AMB-017).  
      34 -- Não recebe indicação explícita de viagem na entrada (ex.: um 
         -indicador `em_viagem` ou um código de viagem aprovada): a viage
         -m é inferida da hospedagem (RN-010). Uma indicação explícita el
         -iminaria a inferência e o risco registrado na seção 10; fica re
         -gistrada como evolução recomendada, pois exige mudar o formato 
         -fixo.                                                          
      35 -- Não trata feriados nem fins de semana de forma especial (AMB-
         -015).                                                          
      35 +- Não identifica refeição com cliente pela descrição: uma despe
         +sa lançada como `alimentacao` é alimentação do colaborador; `re
         +presentacao` só existe onde a tabela aplicada a define (AMB-017
         +, RN-014).                                                     
      36 +- Não recebe indicação explícita de viagem na entrada (ex.: um 
         +indicador `em_viagem` ou um código de viagem aprovada): a viage
         +m é inferida da hospedagem (RN-010), nem mesmo da moeda estrang
         +eira (AMB-023). Uma indicação explícita eliminaria a inferência
         + e os riscos registrados na seção 10; fica registrada como evol
         +ução recomendada, pois exige mudar o formato fixo.             
      37 +- Não trata feriados nem fins de semana de forma especial no re
         +embolso (AMB-015); eles só afetam qual cotação de câmbio é usad
         +a (AMB-024).                                                   
      38  
      39  ## 4. Entrada e saída
      40  

⏺ Agora a seção 4: interface, entrada, saída, motivos e o exemplo.

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 3 lines, removed 3 lines
      40  
      41  ### Interface
      42  
      43 -`<comando> calcular --input <arquivo de entrada> --output <arqu
         -ivo de saída>`                                                 
      43 +`<comando> calcular --input <arquivo de entrada> --politica <ar
         +quivo de política> --cambio <arquivo de câmbio> --output <arqui
         +vo de saída>`                                                  
      44  
      45  - Sucesso: grava o arquivo de saída e termina com código 0.
      46 -- Erro de arquivo (RN-002), inclusive quando o arquivo de saída
         - não pode ser gravado: não cria nem altera o arquivo de saída (
         -se já existia, permanece como estava), escreve uma mensagem de 
         -erro e termina com código diferente de 0.                      
      47 -- Erro de uso (subcomando diferente de `calcular`, `--input` ou
         - `--output` ausentes): mesmo comportamento do erro de arquivo. 
      46 +- Erro de arquivo (RN-002 para a entrada, RN-016 para a polític
         +a e o câmbio), inclusive quando o arquivo de saída não pode ser
         + gravado: não cria nem altera o arquivo de saída (se já existia
         +, permanece como estava), escreve uma mensagem de erro e termin
         +a com código diferente de 0.                                   
      47 +- Erro de uso (subcomando diferente de `calcular`, `--input`, `
         +--politica`, `--cambio` ou `--output` ausentes): mesmo comporta
         +mento do erro de arquivo. Os cinco argumentos são sempre obriga
         +tórios, inclusive quando todas as despesas são em reais (AMB-03
         +1).                                                            
      48  
      49  ### Entrada
      50  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      54  |---|---|---|---|
      55  | `colaborador.id` | texto | identificador do colaborador | sim
           (erro de arquivo) |
      56  | `colaborador.nome` | texto | nome | sim (erro de arquivo) |
      57 -| `colaborador.centro_custo` | texto | centro de custo | não | 
      57 +| `colaborador.centro_custo` | texto ou nulo | centro de custo;
         + escolhe a tabela de limites (RN-014) | não; ausente, nulo ou t
         +exto só com espaços em branco → tabela padrão; qualquer outro t
         +ipo → erro de arquivo |                                        
      58  | `periodo.competencia` | texto `AAAA-MM` | rótulo do mês de co
          mpetência; repetido na saída, não usado em cálculo | não |
      59  | `periodo.inicio` | data `AAAA-MM-DD` | primeiro dia do períod
          o (inclusive) | sim (erro de arquivo) |
      60  | `periodo.fim` | data `AAAA-MM-DD` | último dia do período (in
          clusive) | sim (erro de arquivo) |

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 2 lines, removed 1 line
      64  | `despesas[].categoria` | texto | categoria da despesa | sim (
          `entrada_invalida`) |
      65  | `despesas[].descricao` | texto | descrição livre; não usada e
          m regras | não |
      66  | `despesas[].fornecedor` | texto | estabelecimento; usado na d
          etecção de duplicatas | sim (`entrada_invalida`) |
      67 -| `despesas[].valor` | número | valor em reais | sim (`entrada_
         -invalida`) |                                                   
      67 +| `despesas[].valor` | número | valor na moeda da despesa | sim
         + (`entrada_invalida`) |                                        
      68 +| `despesas[].moeda` | texto ou nulo | código ISO 4217 da moeda
         + do `valor`: exatamente 3 letras maiúsculas de `A` a `Z` (RN-01
         +5) | não; ausente ou nulo → `BRL`; outro tipo ou outro formato 
         +→ `entrada_invalida` |                                         
      69  | `despesas[].tem_nota_fiscal` | booleano | se há nota fiscal |
           sim (`entrada_invalida`) |
      70  
      71  Campos não listados acima são ignorados.

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 8 lines, removed 4 lines
      82  
      83  | Campo | Tipo | Significado |
      84  |---|---|---|
      85 -| `colaborador` | objeto | `id` e `nome`, copiados da entrada |
      85 +| `colaborador` | objeto | `id` e `nome`, copiados da entrada; 
         +`centro_custo` copiado se for texto (inclusive só com espaços),
         + nulo se ausente ou nulo |                                     
      86  | `periodo` | objeto | `inicio` e `fim`, copiados da entrada; `
          competencia` copiada se for texto (em qualquer formato), nula s
          e ausente ou não for texto |
      87 +| `politica` | objeto | `versao` e `vigencia`, copiadas do arqu
         +ivo de política; `tabela_aplicada`: o centro de custo cuja tabe
         +la foi usada, como escrito no arquivo de política, ou `padrao` 
         +(RN-014) |                                                     
      88  | `itens` | lista | um item por elemento de `despesas`, **na me
          sma ordem** |
      89  | `itens[].id` | texto ou nulo | id da despesa como veio, se fo
          r texto; nulo se ausente, se não for texto ou se o elemento não
           é um objeto |
      90  | `itens[].data` | texto ou nulo | data da despesa como veio, s
          e for texto; nulo se ausente, se não for texto ou se o elemento
           não é um objeto |
      90 -| `itens[].categoria` | texto ou nulo | categoria normalizada (
         -RN-006) se reconhecida, qualquer que seja o status ou o motivo 
         -do item (inclusive `entrada_invalida`); senão, como veio, se fo
         -r texto; nulo se ausente ou não for texto |                    
      91 -| `itens[].valor_informado` | número ou nulo | o número recebid
         -o em `valor`, sem arredondamento; nulo se ausente ou não numéri
         -co |                                                           
      92 -| `itens[].valor_considerado` | número ou nulo | valor arredond
         -ado ao centavo (RN-003); **nulo se a despesa foi recusada por `
         -entrada_invalida`** |                                          
      91 +| `itens[].categoria` | texto ou nulo | categoria normalizada (
         +RN-006) se reconhecida na tabela aplicada, qualquer que seja o 
         +status ou o motivo do item (inclusive `entrada_invalida`); senã
         +o, como veio, se for texto; nulo se ausente ou não for texto | 
      92 +| `itens[].valor_informado` | número ou nulo | o número recebid
         +o em `valor`, **na moeda da despesa**, sem arredondamento nem c
         +onversão; nulo se ausente ou não numérico |                    
      93 +| `itens[].moeda` | texto ou nulo | `BRL` se `moeda` ausente ou
         + nula; como veio, se for texto (mesmo fora do formato); nulo se
         + não for texto nem nula, ou se o elemento não é um objeto |    
      94 +| `itens[].taxa_cambio` | número ou nulo | taxa usada na conver
         +são (RN-015): 1 para `BRL`; o número do arquivo de câmbio para 
         +as demais; **nula se a despesa foi recusada por `entrada_invali
         +da` ou `cambio_indisponivel`** |                               
      95 +| `itens[].data_cotacao` | texto ou nulo | data `AAAA-MM-DD` da
         + cotação usada (pode ser anterior à data da despesa, AMB-024); 
         +nula para `BRL` e sempre que `taxa_cambio` é nula |            
      96 +| `itens[].valor_considerado` | número ou nulo | valor **em rea
         +is**: `valor` × `taxa_cambio`, arredondado ao centavo (RN-003, 
         +RN-015); **nulo se a despesa foi recusada por `entrada_invalida
         +` ou `cambio_indisponivel`** |                                 
      97  | `itens[].valor_reembolsado` | número | quanto será reembolsad
          o (0 se recusado) |
      98  | `itens[].status` | texto | `aprovado`, `parcial` ou `recusado
          ` (RN-011) |
      99  | `itens[].motivo` | texto ou nulo | código do motivo (tabela a
          baixo); nulo quando `aprovado` |

⏺ Update(specs/001-motor-reembolso/spec.md)  ⎿  Added 1 line, removed 1 line
      101  | `itens[].limite_diario` | número ou nulo | limite diário apl
           icado à categoria naquela data; nulo se o item foi recusado an
           tes do limite diário |
      102  | `itens[].justificativa` | texto | frase em português explica
           ndo a decisão. Texto livre: **não é contratual**; os demais ca
           mpos são |
      103  | `itens[].avisos` | lista de textos | avisos de chave repetid
           a dentro da despesa (RN-013); lista vazia se não houver |
      104 -| `totais.valor_solicitado` | número | soma de `valor_consider
          -ado` dos itens **não recusados por `entrada_invalida` e com `v
          -alor_considerado` maior que zero** |                          
      104 +| `totais.valor_solicitado` | número | soma de `valor_consider
          +ado` dos itens com `valor_considerado` **não nulo e maior que 
          +zero** (ficam fora os recusados por `entrada_invalida` ou `cam
          +bio_indisponivel`) |                                          
      105  | `totais.valor_reembolsado` | número | soma de `valor_reembol
           sado` |
      106  | `totais.valor_glosado` | número | `valor_solicitado − valor_
           reembolsado` |
      107  | `avisos` | lista de textos | avisos de chave repetida fora d
           as despesas (RN-013); lista vazia se não houver |

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      106  | `totais.valor_glosado` | número | `valor_solicitado − valor_
           reembolsado` |
      107  | `avisos` | lista de textos | avisos de chave repetida fora d
           as despesas (RN-013); lista vazia se não houver |
      108  
      109 -Todos os valores monetários **calculados** da saída (`valor_co
          -nsiderado`, `valor_reembolsado`, `limite_diario` e totais) são
          - em reais, com no máximo 2 casas decimais e exatos ao centavo.
          - `valor_informado` é a única exceção: é a cópia do número rece
          -bido (ex.: 33.333). O arquivo de saída é gravado em UTF-8, com
          - os escapes que o formato exige (uma quebra de linha dentro de
          - um texto sai como `\n`).                                     
      109 +Todos os valores monetários **calculados** da saída (`valor_co
          +nsiderado`, `valor_reembolsado`, `limite_diario` e totais) são
          + em reais, com no máximo 2 casas decimais e exatos ao centavo.
          + `valor_informado` é a única exceção: é a cópia do número rece
          +bido, na moeda da despesa (ex.: 33.333). `taxa_cambio` não é v
          +alor monetário: é a cópia do número do arquivo de câmbio, com 
          +o valor decimal exato. O arquivo de saída é gravado em UTF-8, 
          +com os escapes que o formato exige (uma quebra de linha dentro
          + de um texto sai como `\n`).                                  
      110  
      111  Todo número da entrada vale pelo seu **valor decimal exato, co
           mo escrito no arquivo**, com qualquer quantidade de dígitos e 
           qualquer expoente, nunca por uma aproximação: é sobre esse val
           or que se aplicam o teto (RN-002), o arredondamento (RN-003) e
            a cópia em `valor_informado`. "Como veio" se refere ao valor 
           numérico, não à forma escrita (72.50 e 72.5 são o mesmo valor;
            1e999999 pode sair escrito como 1E+999999).
      112  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 2 lines, removed 1 line
      114  
      115  | Código | Quando | Status resultante |
      116  |---|---|---|
      117 -| `entrada_invalida` | elemento que não é objeto; campo obriga
          -tório ausente ou com tipo/formato errado; ou `valor` com valor
          - absoluto a partir de 1.000.000.000,00 (RN-002) | `recusado` |
      117 +| `entrada_invalida` | elemento que não é objeto; campo obriga
          +tório ausente ou com tipo/formato errado; `moeda` fora do form
          +ato; ou `valor` com valor absoluto a partir de 1.000.000.000,0
          +0 (RN-002) | `recusado` |                                     
      118 +| `cambio_indisponivel` | moeda diferente de `BRL` sem cotação
          + no arquivo de câmbio na data da despesa nem nos 3 dias anteri
          +ores (RN-015) | `recusado` |                                  
      119  | `valor_invalido` | valor considerado menor ou igual a zero (
           RN-004) | `recusado` |
      120  | `fora_do_periodo` | data fora de `[inicio, fim]` (RN-005) | 
           `recusado` |
      121  | `categoria_fora_da_politica` | categoria não reconhecida (RN
           -006) | `recusado` |

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 2 lines, removed 2 lines
      118  | `cambio_indisponivel` | moeda diferente de `BRL` sem cotação
            no arquivo de câmbio na data da despesa nem nos 3 dias anteri
           ores (RN-015) | `recusado` |
      119  | `valor_invalido` | valor considerado menor ou igual a zero (
           RN-004) | `recusado` |
      120  | `fora_do_periodo` | data fora de `[inicio, fim]` (RN-005) | 
           `recusado` |
      121 -| `categoria_fora_da_politica` | categoria não reconhecida (RN
          --006) | `recusado` |                                          
      122 -| `nota_fiscal_ausente` | valor acima de 100,00 sem nota (RN-0
          -08) | `recusado` |                                            
      121 +| `categoria_fora_da_politica` | categoria ausente da tabela a
          +plicada ou com limite 0 nela (RN-006, RN-014) | `recusado` |  
      122 +| `nota_fiscal_ausente` | valor em reais acima do mínimo da po
          +lítica (100,00 na v4) sem nota (RN-008) | `recusado` |        
      123  | `duplicata` | repete uma despesa anterior (RN-007) | `recusa
           do` |
      124  | `limite_diario_excedido` | o limite diário cortou parte ou t
           odo o valor (RN-009) | `parcial`, ou `recusado` se nada restou
            |
      125  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 7 lines, removed 4 lines
      123  | `duplicata` | repete uma despesa anterior (RN-007) | `recusa
           do` |
      124  | `limite_diario_excedido` | o limite diário cortou parte ou t
           odo o valor (RN-009) | `parcial`, ou `recusado` se nada restou
            |
      125  
      126 -**Exemplo** (entrada com duas despesas de alimentação no mesmo
          - dia, fora de viagem):                                        
      126 +**Exemplo** (entrada sem centro de custo, com a política `poli
          +tica-v4.json`, e duas despesas de alimentação em reais no mesm
          +o dia, fora de viagem):                                       
      127  
      128  ```json
      129  {
      130 -  "colaborador": { "id": "c-1", "nome": "Ana" },              
      130 +  "colaborador": { "id": "c-1", "nome": "Ana", "centro_custo":
          + null },                                                      
      131    "periodo": { "competencia": "2026-07", "inicio": "2026-07-01
           ", "fim": "2026-07-31" },
      132 +  "politica": { "versao": "v4", "vigencia": "2026-07-01", "tab
          +ela_aplicada": "padrao" },                                    
      133    "itens": [
      134      { "id": "d-1", "data": "2026-07-03", "categoria": "aliment
           acao",
      134 -      "valor_informado": 45.0, "valor_considerado": 45.0, "val
          -or_reembolsado": 45.0,                                        
      135 +      "valor_informado": 45.0, "moeda": "BRL", "taxa_cambio": 
          +1, "data_cotacao": null,                                      
      136 +      "valor_considerado": 45.0, "valor_reembolsado": 45.0,   
      137        "status": "aprovado", "motivo": null, "em_viagem": false
           , "limite_diario": 60.0,
      138        "justificativa": "Aprovado integralmente: 45,00 dentro d
           o limite diário de 60,00.",
      139        "avisos": [] },
      140      { "id": "d-2", "data": "2026-07-03", "categoria": "aliment
           acao",
      139 -      "valor_informado": 30.0, "valor_considerado": 30.0, "val
          -or_reembolsado": 15.0,                                        
      141 +      "valor_informado": 30.0, "moeda": "BRL", "taxa_cambio": 
          +1, "data_cotacao": null,                                      
      142 +      "valor_considerado": 30.0, "valor_reembolsado": 15.0,   
      143        "status": "parcial", "motivo": "limite_diario_excedido",
            "em_viagem": false, "limite_diario": 60.0,
      144        "justificativa": "Parcial: restavam 15,00 do limite diár
           io de 60,00 de alimentação em 03/07.",
      145        "avisos": [] }

⏺ Agora as regras: RN-002, 003, 006, 007, 008, 009, 010 e 012.

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      172  ### RN-002 — Validação da entrada
      173  
      174  **Regra:**
      175 -- **Erro de arquivo** (o arquivo de saída não é criado nem alt
          -erado): arquivo de entrada ausente, que não está em UTF-8 váli
          -do ou que não é JSON válido (seção 4); texto, em chave ou valo
          -r, com escape que não forma caractere Unicode válido (seção 4)
          -, em qualquer profundidade, inclusive dentro de ocorrência des
          -cartada por chave repetida (RN-013); `colaborador` ausente ou 
          -sem `id`/`nome` em texto, ou com `id`/`nome` vazio ou só com e
          -spaços em branco; `periodo.inicio`, `periodo.fim` ou `despesas
          -` ausentes; `inicio` ou `fim` que não são datas válidas `AAAA-
          -MM-DD`; `inicio` posterior a `fim`; `despesas` que não é lista
          -; arquivo de saída que não pode ser gravado. `periodo.competen
          -cia` nunca causa erro: se não for texto, sai nula.            
      175 +- **Erro de arquivo** (o arquivo de saída não é criado nem alt
          +erado): arquivo de entrada ausente, que não está em UTF-8 váli
          +do ou que não é JSON válido (seção 4); texto, em chave ou valo
          +r, com escape que não forma caractere Unicode válido (seção 4)
          +, em qualquer profundidade, inclusive dentro de ocorrência des
          +cartada por chave repetida (RN-013); `colaborador` ausente ou 
          +sem `id`/`nome` em texto, ou com `id`/`nome` vazio ou só com e
          +spaços em branco; `periodo.inicio`, `periodo.fim` ou `despesas
          +` ausentes; `inicio` ou `fim` que não são datas válidas `AAAA-
          +MM-DD`; `inicio` posterior a `fim`; `despesas` que não é lista
          +; `colaborador.centro_custo` presente que não é texto nem nulo
          + (número, booleano, lista, objeto); arquivo de saída que não p
          +ode ser gravado. `periodo.competencia` nunca causa erro: se nã
          +o for texto, sai nula. Erros nos arquivos de política e de câm
          +bio estão na RN-016.                                          
      176  - **Despesa inválida** (vira item `recusado` com motivo `entra
           da_invalida`; as demais despesas seguem): elemento de `despesa
           s` que não é um objeto; falta `id`, `data`, `categoria`, `forn
           ecedor`, `valor` ou `tem_nota_fiscal`; `data` não é data válid
           a `AAAA-MM-DD`; `valor` não é número; `tem_nota_fiscal` não é 
           booleano; `id`, `categoria` ou `fornecedor` não são texto, ou 
           são texto vazio ou só com espaços em branco; `categoria` ou `f
           ornecedor` cujo texto normalizado (seção 5) fica vazio, como `
           "-"` ou `"***"`; `valor` com valor absoluto maior ou igual a 1
           .000.000.000,00 (um bilhão), comparado com o número recebido, 
           antes do arredondamento (AMB-018).
      177  - Na saída de uma despesa inválida, `id`, `data` e `categoria`
            são copiados se forem texto e saem nulos caso contrário (tipo
            errado, ausente ou elemento que não é objeto); a `categoria`,
            se reconhecida, sai normalizada, como em qualquer item (seção
            4).
      178  - Uma despesa recusada por `entrada_invalida` tem `valor_consi
           derado` nulo, `em_viagem` e `limite_diario` nulos, e não entra
            nos totais.

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      173  
      174  **Regra:**
      175  - **Erro de arquivo** (o arquivo de saída não é criado nem alt
           erado): arquivo de entrada ausente, que não está em UTF-8 váli
           do ou que não é JSON válido (seção 4); texto, em chave ou valo
           r, com escape que não forma caractere Unicode válido (seção 4)
           , em qualquer profundidade, inclusive dentro de ocorrência des
           cartada por chave repetida (RN-013); `colaborador` ausente ou 
           sem `id`/`nome` em texto, ou com `id`/`nome` vazio ou só com e
           spaços em branco; `periodo.inicio`, `periodo.fim` ou `despesas
           ` ausentes; `inicio` ou `fim` que não são datas válidas `AAAA-
           MM-DD`; `inicio` posterior a `fim`; `despesas` que não é lista
           ; `colaborador.centro_custo` presente que não é texto nem nulo
            (número, booleano, lista, objeto); arquivo de saída que não p
           ode ser gravado. `periodo.competencia` nunca causa erro: se nã
           o for texto, sai nula. Erros nos arquivos de política e de câm
           bio estão na RN-016.
      176 -- **Despesa inválida** (vira item `recusado` com motivo `entra
          -da_invalida`; as demais despesas seguem): elemento de `despesa
          -s` que não é um objeto; falta `id`, `data`, `categoria`, `forn
          -ecedor`, `valor` ou `tem_nota_fiscal`; `data` não é data válid
          -a `AAAA-MM-DD`; `valor` não é número; `tem_nota_fiscal` não é 
          -booleano; `id`, `categoria` ou `fornecedor` não são texto, ou 
          -são texto vazio ou só com espaços em branco; `categoria` ou `f
          -ornecedor` cujo texto normalizado (seção 5) fica vazio, como `
          -"-"` ou `"***"`; `valor` com valor absoluto maior ou igual a 1
          -.000.000.000,00 (um bilhão), comparado com o número recebido, 
          -antes do arredondamento (AMB-018).                            
      176 +- **Despesa inválida** (vira item `recusado` com motivo `entra
          +da_invalida`; as demais despesas seguem): elemento de `despesa
          +s` que não é um objeto; falta `id`, `data`, `categoria`, `forn
          +ecedor`, `valor` ou `tem_nota_fiscal`; `data` não é data válid
          +a `AAAA-MM-DD`; `valor` não é número; `tem_nota_fiscal` não é 
          +booleano; `id`, `categoria` ou `fornecedor` não são texto, ou 
          +são texto vazio ou só com espaços em branco; `categoria` ou `f
          +ornecedor` cujo texto normalizado (seção 5) fica vazio, como `
          +"-"` ou `"***"`; `moeda` presente e não nula que não é texto d
          +e exatamente 3 letras maiúsculas de `A` a `Z`, comparado como 
          +veio, sem normalização (`"eur"`, `" EUR"`, `"R$"`, `""`, `978`
          + → inválida; AMB-025); `valor` com valor absoluto maior ou igu
          +al a 1.000.000.000,00 (um bilhão), comparado com o número rece
          +bido, na moeda da despesa, antes do arredondamento e da conver
          +são (AMB-018, AMB-026).                                       
      177  - Na saída de uma despesa inválida, `id`, `data` e `categoria`
            são copiados se forem texto e saem nulos caso contrário (tipo
            errado, ausente ou elemento que não é objeto); a `categoria`,
            se reconhecida, sai normalizada, como em qualquer item (seção
            4).
      178  - Uma despesa recusada por `entrada_invalida` tem `valor_consi
           derado` nulo, `em_viagem` e `limite_diario` nulos, e não entra
            nos totais.
      179  - Espaço em branco, nesta regra e em toda a spec, é o caracter
           e com a propriedade White_Space do Unicode (espaço comum, tabu
           lação, quebra de linha, espaço não separável e semelhantes). T
           abulação, quebra de linha (LF, CR) e NEL têm essa propriedade 
           e são espaço em branco. Espaço de largura zero, BOM e caracter
           es de controle sem essa propriedade (como U+001C a U+001F) não
            são espaço em branco: um `id` ou `nome` feito só deles é text
           o válido.

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      175  - **Erro de arquivo** (o arquivo de saída não é criado nem alt
           erado): arquivo de entrada ausente, que não está em UTF-8 váli
           do ou que não é JSON válido (seção 4); texto, em chave ou valo
           r, com escape que não forma caractere Unicode válido (seção 4)
           , em qualquer profundidade, inclusive dentro de ocorrência des
           cartada por chave repetida (RN-013); `colaborador` ausente ou 
           sem `id`/`nome` em texto, ou com `id`/`nome` vazio ou só com e
           spaços em branco; `periodo.inicio`, `periodo.fim` ou `despesas
           ` ausentes; `inicio` ou `fim` que não são datas válidas `AAAA-
           MM-DD`; `inicio` posterior a `fim`; `despesas` que não é lista
           ; `colaborador.centro_custo` presente que não é texto nem nulo
            (número, booleano, lista, objeto); arquivo de saída que não p
           ode ser gravado. `periodo.competencia` nunca causa erro: se nã
           o for texto, sai nula. Erros nos arquivos de política e de câm
           bio estão na RN-016.
      176  - **Despesa inválida** (vira item `recusado` com motivo `entra
           da_invalida`; as demais despesas seguem): elemento de `despesa
           s` que não é um objeto; falta `id`, `data`, `categoria`, `forn
           ecedor`, `valor` ou `tem_nota_fiscal`; `data` não é data válid
           a `AAAA-MM-DD`; `valor` não é número; `tem_nota_fiscal` não é 
           booleano; `id`, `categoria` ou `fornecedor` não são texto, ou 
           são texto vazio ou só com espaços em branco; `categoria` ou `f
           ornecedor` cujo texto normalizado (seção 5) fica vazio, como `
           "-"` ou `"***"`; `moeda` presente e não nula que não é texto d
           e exatamente 3 letras maiúsculas de `A` a `Z`, comparado como 
           veio, sem normalização (`"eur"`, `" EUR"`, `"R$"`, `""`, `978`
            → inválida; AMB-025); `valor` com valor absoluto maior ou igu
           al a 1.000.000.000,00 (um bilhão), comparado com o número rece
           bido, na moeda da despesa, antes do arredondamento e da conver
           são (AMB-018, AMB-026).
      177  - Na saída de uma despesa inválida, `id`, `data` e `categoria`
            são copiados se forem texto e saem nulos caso contrário (tipo
            errado, ausente ou elemento que não é objeto); a `categoria`,
            se reconhecida, sai normalizada, como em qualquer item (seção
            4).
      178 -- Uma despesa recusada por `entrada_invalida` tem `valor_consi
          -derado` nulo, `em_viagem` e `limite_diario` nulos, e não entra
          - nos totais.                                                  
      178 +- Uma despesa recusada por `entrada_invalida` tem `valor_consi
          +derado`, `taxa_cambio`, `data_cotacao`, `em_viagem` e `limite_
          +diario` nulos, e não entra nos totais.                        
      179  - Espaço em branco, nesta regra e em toda a spec, é o caracter
           e com a propriedade White_Space do Unicode (espaço comum, tabu
           lação, quebra de linha, espaço não separável e semelhantes). T
           abulação, quebra de linha (LF, CR) e NEL têm essa propriedade 
           e são espaço em branco. Espaço de largura zero, BOM e caracter
           es de controle sem essa propriedade (como U+001C a U+001F) não
            são espaço em branco: um `id` ou `nome` feito só deles é text
           o válido.
      180  - `id` (da despesa e do colaborador) e `nome` não passam pela 
           normalização da seção 5: só são repetidos, nunca comparados. U
           m `id` `"-"` é válido.
      181  - Campos extras, no arquivo ou nas despesas, são ignorados.

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      179  - Espaço em branco, nesta regra e em toda a spec, é o caracter
           e com a propriedade White_Space do Unicode (espaço comum, tabu
           lação, quebra de linha, espaço não separável e semelhantes). T
           abulação, quebra de linha (LF, CR) e NEL têm essa propriedade 
           e são espaço em branco. Espaço de largura zero, BOM e caracter
           es de controle sem essa propriedade (como U+001C a U+001F) não
            são espaço em branco: um `id` ou `nome` feito só deles é text
           o válido.
      180  - `id` (da despesa e do colaborador) e `nome` não passam pela 
           normalização da seção 5: só são repetidos, nunca comparados. U
           m `id` `"-"` é válido.
      181  - Campos extras, no arquivo ou nas despesas, são ignorados.
      182 -**Origem:** necessidade operacional (a política não trata entr
          -ada malformada); pontos 7 e 9 de D-001; AMB-018; D-005.       
      182 +**Origem:** necessidade operacional (a política não trata entr
          +ada malformada); pontos 7 e 9 de D-001; AMB-018; D-005; AMB-02
          +0 e AMB-025 (D-007).                                          
      183  **Aceite:** despesa sem `tem_nota_fiscal` com `valor` 33.333 →
            `recusado`, `entrada_invalida`, `valor_informado` 33.333, `va
           lor_considerado` nulo, fora de `valor_solicitado`; as demais d
           espesas são processadas normalmente. Elemento `null` em `despe
           sas` → item com `id` e `data` nulos, `entrada_invalida`. Arqui
           vo sem `colaborador` → nenhuma saída, código diferente de 0. H
           ospedagem com campo extra `"noites": 2` → avaliada como uma di
           ária (RN-012). Despesa com `"id": 17` → `entrada_invalida`, `i
           d` nulo na saída. Despesa com `fornecedor` `"   "` → `entrada_
           invalida`. Despesa com `fornecedor` `"-"` → `entrada_invalida`
           . `competencia` 202607 (número) → processamento normal, `compe
           tencia` nula na saída. Caminho de saída em pasta inexistente →
            nenhuma saída, código diferente de 0. Despesa `"categoria": "
           ALIMENTACAO"` sem `tem_nota_fiscal` → `entrada_invalida`, `cat
           egoria` `alimentacao` na saída. `colaborador.nome` `"  "` → er
           ro de arquivo. Erro de arquivo com arquivo de saída preexisten
           te → o arquivo continua com o conteúdo anterior. Chamada sem `
           --output` → código diferente de 0. `valor` 1000000000 → `entra
           da_invalida`, `valor_informado` 1000000000, fora dos totais. `
           valor` -1e12 → `entrada_invalida` (não `valor_invalido`). `val
           or` 999999999.995 → segue, com `valor_considerado` 1000000000.
           00 (o teto vale para o número recebido).
      184  
      185  ### RN-003 — Arredondamento ao centavo

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      180  - `id` (da despesa e do colaborador) e `nome` não passam pela 
           normalização da seção 5: só são repetidos, nunca comparados. U
           m `id` `"-"` é válido.
      181  - Campos extras, no arquivo ou nas despesas, são ignorados.
      182  **Origem:** necessidade operacional (a política não trata entr
           ada malformada); pontos 7 e 9 de D-001; AMB-018; D-005; AMB-02
           0 e AMB-025 (D-007).
      183 -**Aceite:** despesa sem `tem_nota_fiscal` com `valor` 33.333 →
          - `recusado`, `entrada_invalida`, `valor_informado` 33.333, `va
          -lor_considerado` nulo, fora de `valor_solicitado`; as demais d
          -espesas são processadas normalmente. Elemento `null` em `despe
          -sas` → item com `id` e `data` nulos, `entrada_invalida`. Arqui
          -vo sem `colaborador` → nenhuma saída, código diferente de 0. H
          -ospedagem com campo extra `"noites": 2` → avaliada como uma di
          -ária (RN-012). Despesa com `"id": 17` → `entrada_invalida`, `i
          -d` nulo na saída. Despesa com `fornecedor` `"   "` → `entrada_
          -invalida`. Despesa com `fornecedor` `"-"` → `entrada_invalida`
          -. `competencia` 202607 (número) → processamento normal, `compe
          -tencia` nula na saída. Caminho de saída em pasta inexistente →
          - nenhuma saída, código diferente de 0. Despesa `"categoria": "
          -ALIMENTACAO"` sem `tem_nota_fiscal` → `entrada_invalida`, `cat
          -egoria` `alimentacao` na saída. `colaborador.nome` `"  "` → er
          -ro de arquivo. Erro de arquivo com arquivo de saída preexisten
          -te → o arquivo continua com o conteúdo anterior. Chamada sem `
          ---output` → código diferente de 0. `valor` 1000000000 → `entra
          -da_invalida`, `valor_informado` 1000000000, fora dos totais. `
          -valor` -1e12 → `entrada_invalida` (não `valor_invalido`). `val
          -or` 999999999.995 → segue, com `valor_considerado` 1000000000.
          -00 (o teto vale para o número recebido).                      
      183 +**Aceite:** despesa sem `tem_nota_fiscal` com `valor` 33.333 →
          + `recusado`, `entrada_invalida`, `valor_informado` 33.333, `va
          +lor_considerado` nulo, fora de `valor_solicitado`; as demais d
          +espesas são processadas normalmente. Elemento `null` em `despe
          +sas` → item com `id` e `data` nulos, `entrada_invalida`. Arqui
          +vo sem `colaborador` → nenhuma saída, código diferente de 0. H
          +ospedagem com campo extra `"noites": 2` → avaliada como uma di
          +ária (RN-012). Despesa com `"id": 17` → `entrada_invalida`, `i
          +d` nulo na saída. Despesa com `fornecedor` `"   "` → `entrada_
          +invalida`. Despesa com `fornecedor` `"-"` → `entrada_invalida`
          +. `competencia` 202607 (número) → processamento normal, `compe
          +tencia` nula na saída. Caminho de saída em pasta inexistente →
          + nenhuma saída, código diferente de 0. Despesa `"categoria": "
          +ALIMENTACAO"` sem `tem_nota_fiscal` → `entrada_invalida`, `cat
          +egoria` `alimentacao` na saída. `colaborador.nome` `"  "` → er
          +ro de arquivo. Erro de arquivo com arquivo de saída preexisten
          +te → o arquivo continua com o conteúdo anterior. Chamada sem `
          +--output` → código diferente de 0. `valor` 1000000000 → `entra
          +da_invalida`, `valor_informado` 1000000000, fora dos totais. `
          +valor` -1e12 → `entrada_invalida` (não `valor_invalido`). `val
          +or` 999999999.995 → segue, com `valor_considerado` 1000000000.
          +00 (o teto vale para o número recebido). `"moeda": "eur"` → `e
          +ntrada_invalida`, `moeda` `eur` na saída. `"moeda": 978` → `en
          +trada_invalida`, `moeda` nula na saída. `"centro_custo": 17` →
          + erro de arquivo.                                             
      184  
      185  ### RN-003 — Arredondamento ao centavo
      186  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 3 lines, removed 3 lines
      184  
      185  ### RN-003 — Arredondamento ao centavo
      186  
      187 -**Regra:** antes de qualquer outra regra de valor, `valor` (pe
          -lo seu valor decimal exato, seção 4) é arredondado para 2 casa
          -s decimais, com a metade arredondada afastando do zero (0,005 
          -→ 0,01; -0,005 → -0,01). Todas as regras usam o valor arredond
          -ado (`valor_considerado`), e todos os cálculos são exatos ao c
          -entavo.                                                       
      188 -**Origem:** AMB-014.                                          
      189 -**Aceite:** `valor` 33.333 → `valor_considerado` 33.33; `valor
          -` 10.005 → 10.01; `valor` 10.004 → 10.00.                     
      187 +**Regra:** antes de qualquer outra regra de valor, `valor` (pe
          +lo seu valor decimal exato, seção 4) é multiplicado pela taxa 
          +de câmbio (RN-015; 1 para `BRL`) e o produto exato é arredonda
          +do **uma única vez** para 2 casas decimais, com a metade arred
          +ondada afastando do zero (0,005 → 0,01; -0,005 → -0,01). O res
          +ultado é o `valor_considerado`, em reais. Todas as regras de v
          +alor usam o `valor_considerado`, e todos os cálculos são exato
          +s ao centavo. A única exceção é a comparação de duplicatas (RN
          +-007), que usa o `valor` arredondado ao centavo pela mesma reg
          +ra **na moeda da despesa**, sem conversão.                    
      188 +**Origem:** AMB-014; AMB-026.                                 
      189 +**Aceite:** `valor` 33.333 → `valor_considerado` 33.33; `valor
          +` 10.005 → 10.01; `valor` 10.004 → 10.00. 16,8649 EUR com taxa
          + 5,93 → 100,008857 → 100,01 (não 16,86 × 5,93 = 99,98). 0,001 
          +EUR com taxa 5,93 → 0,00593 → 0,01.                           
      190  
      191  ### RN-004 — Valor deve ser positivo
      192  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 3 lines, removed 3 lines
      190  
      191  ### RN-004 — Valor deve ser positivo
      192  
      193 -**Regra:** despesa com `valor_considerado` menor ou igual a ze
          -ro é `recusado` com motivo `valor_invalido`. Ela não abate, nã
          -o soma nos totais e não consome limite de nenhuma outra despes
          -a.                                                            
      194 -**Origem:** AMB-013.                                          
      195 -**Aceite:** `valor` -45.00 → `recusado`, `valor_invalido`, `va
          -lor_reembolsado` 0; demais despesas do mesmo dia não mudam. `v
          -alor` 0 → `valor_invalido`. `valor` 0.004 (arredonda para 0,00
          -) → `valor_invalido`.                                         
      193 +**Regra:** despesa com `valor_considerado` (em reais, RN-003) 
          +menor ou igual a zero é `recusado` com motivo `valor_invalido`
          +. Ela não abate, não soma nos totais e não consome limite de n
          +enhuma outra despesa.                                         
      194 +**Origem:** AMB-013; AMB-026.                                 
      195 +**Aceite:** `valor` -45.00 → `recusado`, `valor_invalido`, `va
          +lor_reembolsado` 0; demais despesas do mesmo dia não mudam. `v
          +alor` 0 → `valor_invalido`. `valor` 0.004 em reais (arredonda 
          +para 0,00) → `valor_invalido`. 0,001 EUR com taxa 5,93 → `valo
          +r_considerado` 0,01 → não é `valor_invalido`.                 
      196  
      197  ### RN-005 — Período de competência
      198  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 3 lines, removed 3 lines
      202  
      203  ### RN-006 — Categorias da política
      204  
      205 -**Regra:** a categoria é comparada depois da normalização de t
          -exto (seção 5). Só três categorias são reconhecidas: `alimenta
          -cao`, `transporte_urbano` e `hospedagem`. Na saída, categorias
          - reconhecidas aparecem nessa forma normalizada. Qualquer outra
          - → `recusado`, motivo `categoria_fora_da_politica`.           
      206 -**Origem:** política do RH, item 9; AMB-011; AMB-012.         
      207 -**Aceite:** `ALIMENTACAO`, `" Alimentacao "`, `"alimentacao\t"
          -` e `alimentação` → tratadas como `alimentacao`; `"Transporte 
          -Urbano"` e `"transporte-urbano"` → `transporte_urbano`; `cowor
          -king` → `categoria_fora_da_politica`.                         
      205 +**Regra:** a categoria é comparada depois da normalização de t
          +exto (seção 5) com as categorias da **tabela aplicada** ao col
          +aborador (RN-014), também normalizadas. São reconhecidas só as
          + categorias dessa tabela; não há lista fixa. Na saída, categor
          +ias reconhecidas aparecem na forma normalizada. Categoria ause
          +nte da tabela aplicada → `recusado`, motivo `categoria_fora_da
          +_politica`, mesmo que exista em outra tabela do arquivo ou no 
          +`padrao`. Categoria presente na tabela aplicada com limite 0 t
          +ambém → `categoria_fora_da_politica`: a política declara que e
          +la não é reembolsável (AMB-021).                              
      206 +**Origem:** política do RH, item 9; AMB-011; AMB-012; AMB-020 
          +e AMB-021 (D-007).                                            
      207 +**Aceite:** com a tabela `padrao` da v4: `ALIMENTACAO`, `" Ali
          +mentacao "`, `"alimentacao\t"` e `alimentação` → tratadas como
          + `alimentacao`; `"Transporte Urbano"` e `"transporte-urbano"` 
          +→ `transporte_urbano`; `coworking` → `categoria_fora_da_politi
          +ca`; `representacao` → `categoria_fora_da_politica`. Com `CC-C
          +OMERCIAL`: `representacao` → reconhecida. Com `CC-ADM`: `hospe
          +dagem` → `categoria_fora_da_politica`. Com `CC-ENG-PLATAFORMA`
          +: `hospedagem` (limite 0) → `categoria_fora_da_politica`.     
      208  
      209  ### RN-007 — Duplicatas
      210  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      208  
      209  ### RN-007 — Duplicatas
      210  
      211 -**Regra:** duas despesas são duplicatas quando têm a mesma `da
          -ta`, a mesma categoria normalizada, o mesmo `fornecedor` norma
          -lizado (seção 5) e o mesmo `valor_considerado`. `id`, `descric
          -ao` e `tem_nota_fiscal` não entram na comparação. Só participa
          -m da comparação despesas que passaram pelas etapas 1 a 6 da se
          -ção 8 (inclusive a nota fiscal): uma despesa recusada antes di
          -sso não é "original" de ninguém. Dentro de cada grupo de despe
          -sas duplicatas entre si, segue avaliada uma só, a **original**
          -: a primeira na ordem da entrada que tem `tem_nota_fiscal` ver
          -dadeiro; se nenhuma do grupo tem, a primeira na ordem da entra
          -da. Todas as outras do grupo são `recusado`, motivo `duplicata
          -`, e não consomem limite nem comprovam viagem. Assim, qual cóp
          -ia sobrevive não depende da ordem quando só uma delas tem nota
          -. A comparação é exata: datas, valores ou fornecedores diferen
          -tes após a normalização não são duplicatas (risco aceito, seçã
          -o 10).                                                        
      211 +**Regra:** duas despesas são duplicatas quando têm a mesma `da
          +ta`, a mesma categoria normalizada, o mesmo `fornecedor` norma
          +lizado (seção 5), a mesma moeda (`BRL` quando ausente ou nula)
          + e o mesmo `valor` arredondado ao centavo **na moeda da despes
          +a** (RN-003; para `BRL`, é o próprio `valor_considerado`). A t
          +axa de câmbio e o valor em reais não entram na comparação: `22
          +,00 EUR` e `22,00 USD` não são duplicatas, e o mesmo gasto lan
          +çado uma vez em EUR e outra em BRL também não (AMB-028, risco 
          +na seção 10). `id`, `descricao` e `tem_nota_fiscal` não entram
          + na comparação. Só participam da comparação despesas que passa
          +ram pelas etapas 1 a 6 da seção 8 (inclusive a nota fiscal): u
          +ma despesa recusada antes disso não é "original" de ninguém. D
          +entro de cada grupo de despesas duplicatas entre si, segue ava
          +liada uma só, a **original**: a primeira na ordem da entrada q
          +ue tem `tem_nota_fiscal` verdadeiro; se nenhuma do grupo tem, 
          +a primeira na ordem da entrada. Todas as outras do grupo são `
          +recusado`, motivo `duplicata`, e não consomem limite nem compr
          +ovam viagem. Assim, qual cópia sobrevive não depende da ordem 
          +quando só uma delas tem nota. A comparação é exata: datas, val
          +ores ou fornecedores diferentes após a normalização não são du
          +plicatas (risco aceito, seção 10).                            
      212  **Origem:** política do RH, item 8; AMB-010.
      213  **Aceite:** d-006 e d-007 (mesmos data, categoria, fornecedor 
           e valor 54,90, ambas com nota) → d-006 avaliada normalmente, d
           -007 `duplicata`. Táxi de 110,00 sem nota seguido do mesmo táx
           i com nota → o primeiro `nota_fiscal_ausente`, o segundo segue
            avaliado (não é duplicata), em qualquer ordem. Hospedagem de 
           90,00 sem nota e a mesma com nota, em qualquer ordem → a com n
           ota é a original (comprova viagem, RN-010), a sem nota é `dupl
           icata`. "Bistro Central" e "Bistrô Central" → mesmo fornecedor
           .
      214  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 2 lines, removed 2 lines
      209  ### RN-007 — Duplicatas
      210  
      211  **Regra:** duas despesas são duplicatas quando têm a mesma `da
           ta`, a mesma categoria normalizada, o mesmo `fornecedor` norma
           lizado (seção 5), a mesma moeda (`BRL` quando ausente ou nula)
            e o mesmo `valor` arredondado ao centavo **na moeda da despes
           a** (RN-003; para `BRL`, é o próprio `valor_considerado`). A t
           axa de câmbio e o valor em reais não entram na comparação: `22
           ,00 EUR` e `22,00 USD` não são duplicatas, e o mesmo gasto lan
           çado uma vez em EUR e outra em BRL também não (AMB-028, risco 
           na seção 10). `id`, `descricao` e `tem_nota_fiscal` não entram
            na comparação. Só participam da comparação despesas que passa
           ram pelas etapas 1 a 6 da seção 8 (inclusive a nota fiscal): u
           ma despesa recusada antes disso não é "original" de ninguém. D
           entro de cada grupo de despesas duplicatas entre si, segue ava
           liada uma só, a **original**: a primeira na ordem da entrada q
           ue tem `tem_nota_fiscal` verdadeiro; se nenhuma do grupo tem, 
           a primeira na ordem da entrada. Todas as outras do grupo são `
           recusado`, motivo `duplicata`, e não consomem limite nem compr
           ovam viagem. Assim, qual cópia sobrevive não depende da ordem 
           quando só uma delas tem nota. A comparação é exata: datas, val
           ores ou fornecedores diferentes após a normalização não são du
           plicatas (risco aceito, seção 10).
      212 -**Origem:** política do RH, item 8; AMB-010.                  
      213 -**Aceite:** d-006 e d-007 (mesmos data, categoria, fornecedor 
          -e valor 54,90, ambas com nota) → d-006 avaliada normalmente, d
          --007 `duplicata`. Táxi de 110,00 sem nota seguido do mesmo táx
          -i com nota → o primeiro `nota_fiscal_ausente`, o segundo segue
          - avaliado (não é duplicata), em qualquer ordem. Hospedagem de 
          -90,00 sem nota e a mesma com nota, em qualquer ordem → a com n
          -ota é a original (comprova viagem, RN-010), a sem nota é `dupl
          -icata`. "Bistro Central" e "Bistrô Central" → mesmo fornecedor
          -.                                                             
      212 +**Origem:** política do RH, item 8; AMB-010; AMB-028.         
      213 +**Aceite:** d-006 e d-007 (mesmos data, categoria, fornecedor 
          +e valor 54,90, ambas com nota) → d-006 avaliada normalmente, d
          +-007 `duplicata`. 22,00 EUR e 22,00 USD, demais campos iguais 
          +→ as duas avaliadas. 22.001 EUR e 22.00 EUR, demais campos igu
          +ais → a segunda `duplicata`. Táxi de 110,00 sem nota seguido d
          +o mesmo táxi com nota → o primeiro `nota_fiscal_ausente`, o se
          +gundo segue avaliado (não é duplicata), em qualquer ordem. Hos
          +pedagem de 90,00 sem nota e a mesma com nota, em qualquer orde
          +m → a com nota é a original (comprova viagem, RN-010), a sem n
          +ota é `duplicata`. "Bistro Central" e "Bistrô Central" → mesmo
          + fornecedor.                                                  
      214  
      215  ### RN-008 — Nota fiscal obrigatória acima de R$ 100
      216  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 4 lines, removed 4 lines
      212  **Origem:** política do RH, item 8; AMB-010; AMB-028.
      213  **Aceite:** d-006 e d-007 (mesmos data, categoria, fornecedor 
           e valor 54,90, ambas com nota) → d-006 avaliada normalmente, d
           -007 `duplicata`. 22,00 EUR e 22,00 USD, demais campos iguais 
           → as duas avaliadas. 22.001 EUR e 22.00 EUR, demais campos igu
           ais → a segunda `duplicata`. Táxi de 110,00 sem nota seguido d
           o mesmo táxi com nota → o primeiro `nota_fiscal_ausente`, o se
           gundo segue avaliado (não é duplicata), em qualquer ordem. Hos
           pedagem de 90,00 sem nota e a mesma com nota, em qualquer orde
           m → a com nota é a original (comprova viagem, RN-010), a sem n
           ota é `duplicata`. "Bistro Central" e "Bistrô Central" → mesmo
            fornecedor.
      214  
      215 -### RN-008 — Nota fiscal obrigatória acima de R$ 100          
      215 +### RN-008 — Nota fiscal obrigatória acima do mínimo da políti
          +ca                                                            
      216  
      217 -**Regra:** despesa com `valor_considerado` estritamente maior 
          -que 100,00 e `tem_nota_fiscal` falso → `recusado`, motivo `not
          -a_fiscal_ausente`. A comparação usa o valor da despesa individ
          -ual, antes de qualquer limite. O valor de 100,00 é fixo: não é
          - ampliado em viagem. A despesa recusada não consome limite, nã
          -o caracteriza viagem e não participa da comparação de duplicat
          -as.                                                           
      218 -**Origem:** política do RH, item 5; AMB-007; AMB-008.         
      219 -**Aceite:** 100,00 sem nota → segue; 100,01 sem nota → `nota_f
          -iscal_ausente`; 100,01 com nota → segue; transporte de 110,00 
          -sem nota em data em viagem → `nota_fiscal_ausente`.           
      217 +**Regra:** despesa com `valor_considerado` (em reais) estritam
          +ente maior que o mínimo `nota_fiscal_obrigatoria_acima_de` do 
          +arquivo de política (100,00 na v4) e `tem_nota_fiscal` falso →
          + `recusado`, motivo `nota_fiscal_ausente`. O mínimo é um só pa
          +ra todos os centros de custo. A comparação usa o valor da desp
          +esa individual, convertido em reais, antes de qualquer limite.
          + O mínimo não é ampliado em viagem. A despesa recusada não con
          +some limite, não caracteriza viagem e não participa da compara
          +ção de duplicatas.                                            
      218 +**Origem:** política do RH, item 5; AMB-007; AMB-008; AMB-027 
          +(D-007).                                                      
      219 +**Aceite** (mínimo 100,00): 100,00 sem nota → segue; 100,01 se
          +m nota → `nota_fiscal_ausente`; 100,01 com nota → segue; trans
          +porte de 110,00 sem nota em data em viagem → `nota_fiscal_ause
          +nte`; 40,00 USD sem nota com taxa 5,50 → 220,00 → `nota_fiscal
          +_ausente`.                                                    
      220  
      221  ### RN-009 — Limite diário por categoria
      222  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 8 lines, removed 3 lines
      220  
      221  ### RN-009 — Limite diário por categoria
      222  
      223 -**Regra:** para cada combinação de data e categoria, a soma re
          -embolsada das despesas que chegaram a esta regra não pode pass
          -ar do limite diário:                                          
      223 +**Regra:** para cada combinação de data e categoria, a soma re
          +embolsada das despesas que chegaram a esta regra não pode pass
          +ar do limite diário, que vem da **tabela aplicada** ao colabor
          +ador (RN-014):                                                
      224  
      225 -| Categoria | Limite diário normal | Limite diário em viagem (
          -RN-010) |                                                     
      225 +- **Limite normal:** o `limite` da categoria na tabela aplicad
          +a.                                                            
      226 +- **Limite em viagem** (RN-010): só para `alimentacao` e `tran
          +sporte_urbano`, o limite normal × (1 + `acrescimo_em_viagem_pe
          +rcentual` / 100), **truncado** ao centavo (as casas além da se
          +gunda são descartadas, nunca arredondadas para cima: o limite 
          +é um teto). Para qualquer outra categoria, inclusive `hospedag
          +em` (AMB-006) e `representacao` (AMB-022), o limite em viagem 
          +é igual ao normal.                                            
      227 +                                                              
      228 +Com a v4 (acréscimo de 50%), a tabela `padrao` dá:            
      229 +                                                              
      230 +| Categoria | Limite diário normal | Limite diário em viagem |
      231  |---|---|---|
      232  | `alimentacao` | 60,00 | 90,00 |
      233  | `transporte_urbano` | 80,00 | 120,00 |
      229 -| `hospedagem` | 250,00 | 250,00 (não amplia, AMB-006) |      
      234 +| `hospedagem` | 250,00 | 250,00 (não amplia) |               
      235  
      236  O limite é consumido pelas despesas na ordem da entrada: cada 
           despesa recebe `mínimo(valor_considerado, saldo restante do li
           mite)`. Se recebe o valor inteiro → `aprovado`; se recebe part
           e → `parcial`, motivo `limite_diario_excedido`; se o saldo já 
           era zero → `recusado`, motivo `limite_diario_excedido`.
      237  **Origem:** política do RH, itens 1, 2, 3 e 4; AMB-001; AMB-00
           2; AMB-003.

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 2 lines, removed 2 lines
      234  | `hospedagem` | 250,00 | 250,00 (não amplia) |
      235  
      236  O limite é consumido pelas despesas na ordem da entrada: cada 
           despesa recebe `mínimo(valor_considerado, saldo restante do li
           mite)`. Se recebe o valor inteiro → `aprovado`; se recebe part
           e → `parcial`, motivo `limite_diario_excedido`; se o saldo já 
           era zero → `recusado`, motivo `limite_diario_excedido`.
      237 -**Origem:** política do RH, itens 1, 2, 3 e 4; AMB-001; AMB-00
          -2; AMB-003.                                                   
      238 -**Aceite:** alimentação, mesmo dia, fora de viagem: 72,50 e de
          -pois 38,00 → primeira `parcial` com 60,00, segunda `recusado` 
          -com 0. Ordem invertida (38,00 e depois 72,50) → primeira `apro
          -vado` com 38,00, segunda `parcial` com 22,00.                 
      237 +**Origem:** política do RH, itens 1, 2, 3 e 4; AMB-001; AMB-00
          +2; AMB-003; Política v4, item A; AMB-022 (D-007).             
      238 +**Aceite** (tabela `padrao` da v4): alimentação, mesmo dia, fo
          +ra de viagem: 72,50 e depois 38,00 → primeira `parcial` com 60
          +,00, segunda `recusado` com 0. Ordem invertida (38,00 e depois
          + 72,50) → primeira `aprovado` com 38,00, segunda `parcial` com
          + 22,00. `CC-COMERCIAL`: alimentação em viagem → limite 135,00;
          + `representacao` em viagem → limite 300,00. Política com alime
          +ntação 33,33 e acréscimo de 50% → limite em viagem 49,99 (49,9
          +95 truncado).                                                 
      239  
      240  ### RN-010 — Colaborador em viagem
      241  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 2 lines, removed 2 lines
      239  
      240  ### RN-010 — Colaborador em viagem
      241  
      242 -**Regra:** uma despesa de `hospedagem` **comprova viagem** qua
          -ndo tem `tem_nota_fiscal` verdadeiro e passou pelas etapas 1 a
          - 7 da seção 8. Uma hospedagem que comprova viagem na data D co
          -loca em viagem as datas **D e D+1** (a noite da diária e o dia
          - seguinte). Em datas em viagem, os limites de `alimentacao` e 
          -`transporte_urbano` são ampliados em 50% (tabela da RN-009). A
          - condição de viagem vale para todas as despesas da data, indep
          -endentemente da ordem em que aparecem na entrada.             
      243 -**Origem:** política do RH, item 6; AMB-004.                  
      242 +**Regra:** uma despesa de `hospedagem` **comprova viagem** qua
          +ndo tem `tem_nota_fiscal` verdadeiro e passou pelas etapas 1 a
          + 7 da seção 8. Uma hospedagem que comprova viagem na data D co
          +loca em viagem as datas **D e D+1** (a noite da diária e o dia
          + seguinte). Em datas em viagem, os limites de `alimentacao` e 
          +`transporte_urbano` são ampliados pelo percentual da política 
          +(RN-009). A condição de viagem vale para todas as despesas da 
          +data, independentemente da ordem em que aparecem na entrada. H
          +ospedagem recusada por `categoria_fora_da_politica` (inclusive
          + por limite 0, AMB-021) não comprova viagem. Despesa em moeda 
          +estrangeira não comprova viagem (AMB-023).                    
      243 +**Origem:** política do RH, item 6; AMB-004; AMB-021 e AMB-023
          + (D-007).                                                     
      244  **Aceite:** hospedagem com nota em 14/07 → 14/07 e 15/07 em vi
           agem; alimentação de 80,00 em 15/07 → limite 90,00, `aprovado`
            com 80,00; alimentação de 80,00 em 16/07 → limite 60,00, `par
           cial` com 60,00. Hospedagem de 80,00 **sem** nota em 03/07 → r
           eembolsada pelas regras normais, mas 03/07 e 04/07 **não** fic
           am em viagem. Hospedagem com nota em 30/06, fora de um período
            que começa em 01/07 → recusada por `fora_do_periodo`, e 01/07
            não fica em viagem.
      245  
      246  ### RN-011 — Status e justificativa

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      241  
      242  **Regra:** uma despesa de `hospedagem` **comprova viagem** qua
           ndo tem `tem_nota_fiscal` verdadeiro e passou pelas etapas 1 a
            7 da seção 8. Uma hospedagem que comprova viagem na data D co
           loca em viagem as datas **D e D+1** (a noite da diária e o dia
            seguinte). Em datas em viagem, os limites de `alimentacao` e 
           `transporte_urbano` são ampliados pelo percentual da política 
           (RN-009). A condição de viagem vale para todas as despesas da 
           data, independentemente da ordem em que aparecem na entrada. H
           ospedagem recusada por `categoria_fora_da_politica` (inclusive
            por limite 0, AMB-021) não comprova viagem. Despesa em moeda 
           estrangeira não comprova viagem (AMB-023).
      243  **Origem:** política do RH, item 6; AMB-004; AMB-021 e AMB-023
            (D-007).
      244 -**Aceite:** hospedagem com nota em 14/07 → 14/07 e 15/07 em vi
          -agem; alimentação de 80,00 em 15/07 → limite 90,00, `aprovado`
          - com 80,00; alimentação de 80,00 em 16/07 → limite 60,00, `par
          -cial` com 60,00. Hospedagem de 80,00 **sem** nota em 03/07 → r
          -eembolsada pelas regras normais, mas 03/07 e 04/07 **não** fic
          -am em viagem. Hospedagem com nota em 30/06, fora de um período
          - que começa em 01/07 → recusada por `fora_do_periodo`, e 01/07
          - não fica em viagem.                                          
      244 +**Aceite:** hospedagem com nota em 14/07 → 14/07 e 15/07 em vi
          +agem; alimentação de 80,00 em 15/07 → limite 90,00, `aprovado`
          + com 80,00; alimentação de 80,00 em 16/07 → limite 60,00, `par
          +cial` com 60,00. Hospedagem de 80,00 **sem** nota em 03/07 → r
          +eembolsada pelas regras normais, mas 03/07 e 04/07 **não** fic
          +am em viagem. Hospedagem com nota em 30/06, fora de um período
          + que começa em 01/07 → recusada por `fora_do_periodo`, e 01/07
          + não fica em viagem. `CC-ENG-PLATAFORMA`: hospedagem com nota 
          +em 14/07 → `categoria_fora_da_politica`; alimentação de 100,00
          + com nota em 15/07 → limite 75,00, `parcial` com 75,00. Alimen
          +tação de 22,00 EUR com nota em 14/07, sem hospedagem → 14/07 n
          +ão fica em viagem.                                            
      245  
      246  ### RN-011 — Status e justificativa
      247  
⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 2 lines, removed 2 lines
      251  
      252  ### RN-012 — Hospedagem: um lançamento é uma diária
      253  
      254 -**Regra:** cada despesa de `hospedagem` é tratada como uma diá
          -ria na sua `data`, qualquer que seja o valor, a descrição ou c
          -ampos extras. Várias hospedagens na mesma data dividem o mesmo
          - limite diário de 250,00 (RN-009).                            
      254 +**Regra:** cada despesa de `hospedagem` é tratada como uma diá
          +ria na sua `data`, qualquer que seja o valor, a descrição ou c
          +ampos extras. Várias hospedagens na mesma data dividem o mesmo
          + limite diário da tabela aplicada (RN-009). A `periodicidade` 
          +do arquivo de política (`dia` ou `diaria`) não muda o cálculo:
          + as duas significam limite por data (RN-016).                 
      255  **Origem:** política do RH, item 3; AMB-005.
      256 -**Aceite:** hospedagem de 480,00 com nota em 14/07 ("2 diarias
          -" na descrição) → `parcial` com 250,00; 14/07 e 15/07 em viage
          -m (RN-010).                                                   
      256 +**Aceite** (tabela `padrao` da v4): hospedagem de 480,00 com n
          +ota em 14/07 ("2 diarias" na descrição) → `parcial` com 250,00
          +; 14/07 e 15/07 em viagem (RN-010). `CC-COMERCIAL`: hospedagem
          + de 1.200,00 com nota ("3 noites") → `parcial` com 400,00.    
      257  
      258  ### RN-013 — Chave repetida no arquivo de entrada
      259  

⏺ Agora as três regras novas (RN-014 a RN-016), logo depois da RN-013.

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 58 lines
      274  **Origem:** necessidade operacional (a política não trata o fo
           rmato do arquivo); AMB-019.
      275  **Aceite:** despesa com `"valor": 30.00` e depois `"valor": 50
           .00` → avaliada com 50,00; `itens[].avisos` = [`chave repetida
           : valor (2 ocorrências; valeu a última)`]. `colaborador.nome` 
           repetido → `avisos` do topo = [`chave repetida: colaborador.no
           me (2 ocorrências; valeu a última)`]; itens sem chave repetida
            têm `avisos` vazio. Despesa com `"tem_nota_fiscal": true` e d
           epois `"tem_nota_fiscal": "sim"` → `entrada_invalida`, com o a
           viso de `tem_nota_fiscal`. `despesas` repetida na raiz → só a 
           última lista é avaliada; um aviso `chave repetida: despesas (2
            ocorrências; valeu a última)` no topo; chaves repetidas dentr
           o da primeira lista não geram aviso. Chave `valor` três vezes 
           → um aviso, com `3 ocorrências`. Despesa com `"extra": {"x": 1
           , "x": 2}, "obs": "a", "obs": "b", "extra": {"x": 3, "x": 4}` 
           → avisos, nesta ordem: `extra` (2), `obs` (2), `extra.x` (2). 
           Alimentação fora de viagem com `"valor": 30.00` e depois `"\u0
           076alor": 90.00` → vale 90,00, `parcial` com 60,00, aviso de `
           valor`. Despesa com `"obs": "\uD800"` e depois `"obs": "ok"` →
            erro de arquivo, sem saída; o mesmo com `"extra": {"y": "\uDC
           00"}` e depois `"extra": {}`.
      276  
      277 +### RN-014 — Tabela aplicada por centro de custo              
      278 +                                                              
      279 +**Regra:** cada execução aplica **uma** tabela de limites a to
          +das as despesas, escolhida pelo `colaborador.centro_custo`:   
      280 +- se o texto de `centro_custo` é **igual, caractere a caracter
          +e**, a uma chave de `centros_custo` do arquivo de política, ap
          +lica-se a tabela desse centro de custo. A comparação é exata: 
          +sem normalização, sem ignorar maiúsculas nem espaços (`"cc-adm
          +"` e `"CC-ADM "` não são `CC-ADM`);                           
      281 +- em qualquer outro caso — centro de custo ausente da tabela, 
          +`centro_custo` ausente, nulo ou só com espaços em branco — apl
          +ica-se a tabela `padrao` do arquivo de política.              
      282 +                                                              
      283 +A tabela aplicada é **fechada**: suas categorias são as únicas
          + reconhecidas (RN-006), seus limites são os únicos usados (RN-
          +009). Uma categoria que falta na tabela de um centro de custo 
          +**não** é completada pelo `padrao`. A saída informa a tabela a
          +plicada em `politica.tabela_aplicada` (seção 4).              
      284 +**Origem:** Política v4, item A ("aplica-se a política padrão"
          +); AMB-020 (D-007).                                           
      285 +**Aceite** (`politica-v4.json`): `"CC-COMERCIAL"` → tabela `CC
          +-COMERCIAL`, alimentação 85,00 → limite 90,00, `aprovado`. `"C
          +C-SUPORTE-N2"` → `padrao`, alimentação 65,00 → limite 60,00, `
          +parcial` com 60,00. Sem `centro_custo` → `padrao`. `"cc-adm"` 
          +→ `padrao` (alimentação 50,00 → limite 60,00, `aprovado`). `"C
          +C-ADM"` com hospedagem de 300,00 com nota → `categoria_fora_da
          +_politica` (não 250,00 do `padrao`).                          
      286 +                                                              
      287 +### RN-015 — Moeda e conversão para reais                     
      288 +                                                              
      289 +**Regra:**                                                    
      290 +- A moeda da despesa é o campo `moeda`; ausente ou nulo vale `
          +BRL`. Formato inválido é `entrada_invalida` (RN-002).         
      291 +- `BRL` tem taxa 1, sem consultar o arquivo de câmbio (uma ent
          +rada `BRL` no arquivo é ignorada).                            
      292 +- Para outra moeda, a taxa é a do arquivo de câmbio para essa 
          +moeda **na data da despesa**. Se essa data não tem cotação par
          +a a moeda, usa-se a cotação da data anterior mais próxima **at
          +é 3 dias corridos antes** (D-1, D-2 ou D-3): um sábado ou domi
          +ngo usa a sexta-feira; uma segunda-feira de feriado usa a sext
          +a-feira. Sem cotação de D a D-3 → `recusado`, motivo `cambio_i
          +ndisponivel`. Cotação posterior à data da despesa nunca é usad
          +a.                                                            
      293 +- Moeda bem formada que não aparece no arquivo de câmbio (incl
          +usive código que não existe na ISO 4217, como `XYZ`) → `cambio
          +_indisponivel`. Não há lista própria de códigos ISO.          
      294 +- Taxa é "reais por uma unidade da moeda": `valor_considerado`
          + = `valor` × taxa, arredondado uma vez (RN-003).              
      295 +- Uma despesa recusada por `cambio_indisponivel` tem `valor_co
          +nsiderado`, `taxa_cambio`, `data_cotacao`, `em_viagem` e `limi
          +te_diario` nulos, e não entra nos totais.                     
      296 +- A moeda não muda nenhuma outra regra: não caracteriza viagem
          + (AMB-023) e todos os limites e o mínimo da nota são comparado
          +s em reais.                                                   
      297 +                                                              
      298 +**Origem:** Política v4, item B; AMB-024, AMB-025, AMB-026 (D-
          +007).                                                         
      299 +**Aceite** (`cambio.json` do envelope): 22,00 EUR em 14/07 → t
          +axa 5,93, `data_cotacao` 2026-07-14, `valor_considerado` 130,4
          +6. 30,00 EUR em 18/07 (sábado) → taxa 5,96 de 17/07, `valor_co
          +nsiderado` 178,80. Sem `moeda` → `BRL`, taxa 1, `data_cotacao`
          + nula. `"moeda": null` → `BRL`. 55,00 GBP em 21/07 → `cambio_i
          +ndisponivel`, `valor_considerado` nulo, fora de `valor_solicit
          +ado`. USD em 2026-07-12 (nenhuma cotação de 09/07 a 12/07) → `
          +cambio_indisponivel`. Câmbio só com 13/07: USD em 16/07 → usa 
          +13/07 (D-3); USD em 17/07 → `cambio_indisponivel` (D-4).      
      300 +                                                              
      301 +### RN-016 — Arquivos de política e de câmbio                 
      302 +                                                              
      303 +**Regra:** os dois arquivos seguem as mesmas regras de forma d
          +o arquivo de entrada (seção 4: UTF-8, JSON válido, escapes). Q
          +ualquer defeito em qualquer um deles é **erro de arquivo** (se
          +m saída, código diferente de 0), porque nenhum cálculo é confi
          +ável com a política ou o câmbio defeituosos. É erro de arquivo
          +:                                                             
      304 +                                                              
      305 +- arquivo ausente, fora do UTF-8, que não é JSON válido ou com
          + escape sem caractere válido;                                 
      306 +- chave repetida em qualquer objeto (a RN-013 vale só para o a
          +rquivo de entrada);                                           
      307 +- **política:**                                               
      308 +  - raiz que não é objeto;                                    
      309 +  - `versao` ausente ou que não é texto não vazio;            
      310 +  - `vigencia` ausente ou que não é data válida `AAAA-MM-DD`; 
      311 +  - `moeda_base` diferente de `"BRL"`;                        
      312 +  - `padrao` ausente ou que não é tabela;                     
      313 +  - `centros_custo` ausente ou que não é objeto cujos valores 
          +são tabelas;                                                  
      314 +  - `nota_fiscal_obrigatoria_acima_de` ausente, que não é núme
          +ro, negativo ou com mais de 2 casas decimais;                 
      315 +  - `acrescimo_em_viagem_percentual` ausente, que não é número
          + ou negativo;                                                 
      316 +- **tabela** (o `padrao` e cada valor de `centros_custo`): obj
          +eto de categoria → regra. É erro de arquivo:                  
      317 +  - nome de categoria cujo texto normalizado (seção 5) fica va
          +zio;                                                          
      318 +  - duas categorias da mesma tabela com o mesmo texto normaliz
          +ado;                                                          
      319 +  - regra que não é objeto;                                   
      320 +  - `limite` ausente, que não é número, negativo ou com mais d
          +e 2 casas decimais;                                           
      321 +  - `periodicidade` ausente ou diferente de `"dia"` e `"diaria
          +"`, que significam a mesma coisa: limite por data;            
      322 +- **câmbio:**                                                 
      323 +  - raiz que não é objeto;                                    
      324 +  - `moeda_base` diferente de `"BRL"`;                        
      325 +  - `taxas` ausente ou que não é objeto;                      
      326 +  - chave de `taxas` que não é data válida `AAAA-MM-DD`;      
      327 +  - valor de `taxas` que não é objeto;                        
      328 +  - código de moeda que não tem exatamente 3 letras maiúsculas
          + de `A` a `Z`;                                                
      329 +  - taxa que não é número ou que é menor ou igual a zero.     
      330 +                                                              
      331 +Campos não listados (`observacao`, `fonte` e outros) são ignor
          +ados. Uma tabela vazia é válida: nenhuma categoria é reconheci
          +da para quem a usa. `vigencia` não muda o cálculo: é copiada p
          +ara a saída (AMB-029).                                        
      332 +**Origem:** Política v4, itens A e B; AMB-029, AMB-031 (D-007)
          +.                                                             
      333 +**Aceite:** política sem `padrao` → erro de arquivo. Limite `"
          +60"` (texto), `-10` ou `60.005` → erro de arquivo. `periodicid
          +ade` `"mes"` → erro de arquivo. Câmbio com taxa 0 → erro de ar
          +quivo. Câmbio com data `"2026-07-32"` → erro de arquivo. Chave
          + `alimentacao` duas vezes na mesma tabela → erro de arquivo. A
          +rquivo de câmbio ausente com todas as despesas em BRL → erro d
          +e arquivo. Política com `observacao` numa regra → ignorada.   
      334 +                                                              
      335  ---
      336  
      337  ## 6. Ambiguidades identificadas e decisões

⏺ Agora a seção 6: ajustes nas AMB-006, 007, 015 e 017, e as novas AMB-020 a
  AMB-031.

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 2 lines, removed 2 lines
      382  
      383  **Texto original do RH:** "Colaborador em viagem tem limites a
           mpliados em 50%."
      384  **O que não está claro:** se "limites" inclui o de hospedagem,
            que já pressupõe viagem.
      385 -**Decisão:** não; a hospedagem tem sempre limite de 250,00 por
          - diária.                                                      
      386 -**Justificativa:** toda hospedagem já é viagem; ampliar o limi
          -te dela tornaria o valor de 250,00 da política inalcançável na
          - prática.                                                     
      385 +**Decisão:** não; a hospedagem tem sempre o limite da tabela a
          +plicada, sem acréscimo (na v4: 250,00 no `padrao`, 400,00 no `
          +CC-COMERCIAL`).                                               
      386 +**Justificativa:** toda hospedagem já é viagem; ampliar o limi
          +te dela tornaria o valor da política inalcançável na prática. 
          +Mantida na v4 (D-007), que traz o percentual sem dizer a quais
          + categorias se aplica (AMB-022).                              
      387  **Regra afetada:** RN-009
      388  
      389  ### AMB-007 — "Acima de R$ 100": exatamente 100,00 exige nota?
            (F)

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      390  
      391  **Texto original do RH:** "Nota fiscal é obrigatória acima de 
           R$ 100."
      392  **O que não está claro:** se 100,00 está incluído (d-003 = 100
           ,00 e d-004 = 100,01, ambos sem nota).
      393 -**Decisão:** só exige nota quando o valor é estritamente maior
          - que 100,00. O valor de 100,00 não é ampliado em viagem.      
      393 +**Decisão:** só exige nota quando o valor é estritamente maior
          + que o mínimo. O mínimo não é ampliado em viagem. Na v4, o mín
          +imo vem do arquivo de política (`nota_fiscal_obrigatoria_acima
          +_de`, 100,00) e é comparado em reais (AMB-027).               
      394  **Justificativa:** leitura literal de "acima de"; a ampliação 
           da política (item 6) fala de limites de reembolso, não da exig
           ência de nota.
      395  **Regra afetada:** RN-008
      396  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 2 lines, removed 2 lines
      454  
      455  **Texto original do RH:** (não tratado)
      456  **O que não está claro:** d-012 é um almoço de sábado ("plantã
           o"); a política não diz se despesas em fim de semana são aceit
           as.
      457 -**Decisão:** dia da semana não afeta o reembolso.             
      457 +**Decisão:** dia da semana não afeta o reembolso. Desde a v4, 
          +afeta só qual cotação de câmbio é usada para despesa em moeda 
          +estrangeira, porque não há cotação em fim de semana (AMB-024).
      458  **Justificativa:** a política não restringe; criar a restrição
            seria inventar regra.
      459 -**Regra afetada:** nenhuma (registrado em Fora de escopo)     
      459 +**Regra afetada:** nenhuma no reembolso (registrado em Fora de
          + escopo); RN-015 na cotação                                   
      460  
      461  ### AMB-016 — Em que ordem as regras se aplicam? (U)
      462  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 3 lines, removed 3 lines
      470  
      471  **Texto original do RH:** (não tratado)
      472  **O que não está claro:** d-001 é "Almoco com cliente" (72,50)
           : pode incluir a refeição de outra pessoa; a política não prev
           ê representação nem limite por pessoa.
      473 -**Decisão:** é alimentação do colaborador, com o limite diário
          - normal.                                                      
      474 -**Justificativa:** a entrada não informa número de pessoas nem
          - uma categoria de representação; identificá-las exigiria inter
          -pretar a descrição. Fica registrado como evolução recomendada 
          -(seção 3).                                                    
      475 -**Regra afetada:** RN-009                                     
      473 +**Decisão:** é alimentação do colaborador, com o limite diário
          + normal. Desde a v4, quem quiser o limite de representação lan
          +ça a despesa na categoria `representacao`, que só existe onde 
          +a tabela aplicada a define (na v4, só no `CC-COMERCIAL`); a de
          +scrição continua não sendo lida.                              
      474 +**Justificativa:** a entrada não informa número de pessoas; id
          +entificar a refeição com cliente pela descrição seria adivinha
          +r. A categoria explícita da v4 resolve o caso sem interpretar 
          +texto livre.                                                  
      475 +**Regra afetada:** RN-009, RN-006                             
      476  
      477  ### AMB-018 — Valor grande demais para ser despesa (F)
      478  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 100 lines
      490  **Justificativa:** a última ocorrência é a leitura mais comum 
           desse tipo de arquivo e corresponde a uma correção feita ao fi
           nal do registro; descartar em silêncio esconderia do conferent
           e um valor que pode ter mudado o reembolso, por isso o descart
           e é avisado.
      491  **Regra afetada:** RN-013
      492  
      493 +### Política v4 (D-007)                                       
      494 +                                                              
      495 +As ambiguidades abaixo vêm do comunicado da Política v4 e dos 
          +arquivos `politica-v4.json` e `cambio.json` (em `exemplos/enve
          +lope/`).                                                      
      496 +                                                              
      497 +### AMB-020 — "Aplica-se a política padrão": quando, e qual é 
          +o padrão? (D, U)                                              
      498 +                                                              
      499 +**Texto original do RH:** "Alguns centros de custo não têm ent
          +rada na tabela. Nesse caso, aplica-se a política padrão."     
      500 +**O que não está claro:** se o padrão também completa a catego
          +ria que falta num centro de custo que está na tabela (`CC-ADM`
          + não tem `hospedagem`); se uma categoria de outro centro de cu
          +sto vale para quem caiu no padrão (`representacao` no f-003); 
          +se "padrão" é o bloco `padrao` do arquivo ou a política anteri
          +or; como comparar o `centro_custo` da entrada com a tabela (`"
          +cc-adm"`); e o que fazer com `centro_custo` ausente, nulo, vaz
          +io ou de outro tipo. O campo é declarado pelo próprio colabora
          +dor.                                                          
      501 +**Decisão:** o padrão é o bloco `padrao` do arquivo e vale só 
          +quando o centro de custo não está na tabela, inclusive quando 
          +`centro_custo` está ausente, nulo ou só com espaços. A tabela 
          +aplicada é fechada: categoria que falta nela é `categoria_fora
          +_da_politica`, sem completar pelo padrão. A comparação do cent
          +ro de custo é exata. `centro_custo` de outro tipo é erro de ar
          +quivo. O centro de custo declarado não é verificado (risco na 
          +seção 10).                                                    
      502 +**Justificativa:** o comunicado só manda aplicar o padrão ao c
          +entro de custo que "não tem entrada"; o próprio arquivo mostra
          + que o financeiro monta tabelas diferentes de propósito (`CC-E
          +NG-PLATAFORMA` veda hospedagem), então completar com o padrão 
          +daria ao `CC-ADM` uma hospedagem que ninguém autorizou. O padr
          +ão vem do arquivo para que nenhum limite fique no código. O ce
          +ntro de custo é código de cadastro, não texto livre; um erro d
          +e grafia aparece na saída (`politica.tabela_aplicada`) para a 
          +conferência. Tipo errado num campo do cabeçalho é arquivo malf
          +ormado, como em `colaborador.id`.                             
      503 +**Regra afetada:** RN-014, RN-006, RN-002                     
      504 +                                                              
      505 +### AMB-021 — Categoria "não reembolsável de forma alguma" (li
          +mite 0) (U)                                                   
      506 +                                                              
      507 +**Texto original do RH:** "`CC-ENG-PLATAFORMA` não reembolsa `
          +hospedagem` de forma alguma." No arquivo: `"limite": 0.00`, `"
          +observacao": "nao reembolsavel"`.                             
      508 +**O que não está claro:** se é um limite diário 0 (motivo `lim
          +ite_diario_excedido`, etapa 9) ou uma categoria vedada (`categ
          +oria_fora_da_politica`, etapa 5); e, por consequência, se essa
          + hospedagem com nota ainda comprova viagem (RN-010).          
      509 +**Decisão:** categoria com limite 0 na tabela aplicada é trata
          +da como fora da política: `categoria_fora_da_politica`, na eta
          +pa 5. Por isso não comprova viagem.                           
      510 +**Justificativa:** "não reembolsa de forma alguma" é vedar a c
          +ategoria, não um teto que se esgota; o motivo `limite_diario_e
          +xcedido` diria ao colaborador que houve excesso. Tratar como l
          +imite 0 deixaria uma hospedagem de 0,01 com nota declarada amp
          +liar os limites de dois dias numa categoria que a política pro
          +íbe.                                                          
      511 +**Regra afetada:** RN-006, RN-010                             
      512 +                                                              
      513 +### AMB-022 — O acréscimo em viagem vem do arquivo e vale para
          + quais categorias? (U, F)                                     
      514 +                                                              
      515 +**Texto original do RH:** "Colaborador em viagem tem limites a
          +mpliados em 50%." No arquivo v4: `"acrescimo_em_viagem_percent
          +ual": 50`, sem lista de categorias.                           
      516 +**O que não está claro:** se o percentual do arquivo substitui
          + os valores em viagem escritos na spec; se vale para `represen
          +tacao` e para categorias que o financeiro venha a criar; e com
          +o tratar um limite ampliado que não fecha no centavo (33,33 × 
          +1,5 = 49,995).                                                
      517 +**Decisão:** o percentual vem do arquivo; vale só para `alimen
          +tacao` e `transporte_urbano`; o limite ampliado é truncado ao 
          +centavo.                                                      
      518 +**Justificativa:** o acréscimo compensa comer e se deslocar fo
          +ra de casa, que era o sentido da política original; representa
          +ção já tem limite próprio para um contexto especial, como a ho
          +spedagem (AMB-006); estender a ampliação a qualquer categoria 
          +nova seria regra que ninguém escreveu. O limite é um teto: tru
          +ncar garante que o reembolso nunca passa de limite × (1 + perc
          +entual), enquanto arredondar poderia pagar meio centavo acima.
          + O truncamento não interfere na nota fiscal, que compara o val
          +or da despesa antes de qualquer limite (AMB-008).             
      519 +**Regra afetada:** RN-009, RN-010                             
      520 +                                                              
      521 +### AMB-023 — Despesa em moeda estrangeira põe o colaborador e
          +m viagem? (D)                                                 
      522 +                                                              
      523 +**Texto original do RH:** "Colaboradores em viagem internacion
          +al lançam despesas em moeda estrangeira."                     
      524 +**O que não está claro:** se a moeda estrangeira é evidência d
          +e viagem, como a hospedagem (e-002 a e-005, em Lisboa, não têm
          + hospedagem).                                                 
      525 +**Decisão:** não; a viagem continua comprovada só por hospedag
          +em com nota (RN-010).                                         
      526 +**Justificativa:** a frase descreve quem lança em moeda estran
          +geira, não cria regra de viagem. A moeda é declarada pelo cola
          +borador: se ela comprovasse viagem, um almoço de 1 USD ampliar
          +ia os limites do dia sem nem exigir nota, brecha maior que a d
          +a hospedagem irrisória. Viagem internacional sem hospedagem la
          +nçada fica sem ampliação (risco na seção 10).                 
      527 +**Regra afetada:** RN-010                                     
      528 +                                                              
      529 +### AMB-024 — "A taxa da data da despesa" quando não há taxa n
          +essa data (D)                                                 
      530 +                                                              
      531 +**Texto original do RH:** "A conversão usa a taxa da data da d
          +espesa, não a taxa de hoje." No arquivo: "Cotações publicadas 
          +apenas em dias úteis bancários", de 13/07 a 28/07.            
      532 +**O que não está claro:** que taxa usar num fim de semana ou f
          +eriado (e-004, sábado 18/07), e numa data sem nenhuma cotação 
          +próxima no arquivo. A escolha muda a aprovação, não só o valor
          +: 16,70 EUR sem nota num sábado dá 99,53 com a taxa de sexta (
          +não exige nota) e 100,37 com a de segunda (`nota_fiscal_ausent
          +e`).                                                          
      533 +**Decisão:** usa a cotação da data; sem ela, a da data anterio
          +r mais próxima, até 3 dias corridos antes; sem nenhuma, `cambi
          +o_indisponivel`. Nunca uma cotação posterior.                 
      534 +**Justificativa:** é a prática da PTAX: a cotação vigente num 
          +sábado é a de sexta. A cotação posterior ainda não existia na 
          +data da despesa. O limite de 3 dias cobre fim de semana e feri
          +ado de segunda ou sexta adjacente; sem limite, uma lacuna de s
          +emanas no arquivo passaria em silêncio com uma taxa velha.    
      535 +**Regra afetada:** RN-015                                     
      536 +                                                              
      537 +### AMB-025 — Moeda sem cotação, mal escrita ou nula (D, F)   
      538 +                                                              
      539 +**Texto original do RH:** "A entrada agora pode trazer um camp
          +o `moeda` (ISO 4217). Quando ausente, assume-se BRL."         
      540 +**O que não está claro:** moeda válida sem taxa no arquivo (e-
          +006, GBP); grafia fora do padrão (`"eur"`, `" EUR "`, `"R$"`, 
          +`978`); `"moeda": null`; `BRL`, que não está no arquivo de câm
          +bio.                                                          
      541 +**Decisão:** 3 letras maiúsculas de `A` a `Z`, comparadas como
          + vieram, ou `entrada_invalida`; nulo vale como ausente (`BRL`)
          +; `BRL` tem taxa 1; código bem formado sem cotação → `cambio_i
          +ndisponivel`, sem verificar a lista ISO.                      
      542 +**Justificativa:** ISO 4217 é sempre 3 letras maiúsculas e o c
          +ódigo é comparado exatamente, como o centro de custo (AMB-020)
          +. Ao contrário do centro de custo, não há moeda segura para su
          +por quando a grafia está errada, por isso recusa em vez de ass
          +umir BRL. Nulo é a forma comum de "não informado". Embutir a l
          +ista ISO exigiria mantê-la; o motivo `cambio_indisponivel` é v
          +erdadeiro para qualquer código sem taxa.                      
      543 +**Regra afetada:** RN-002, RN-015                             
      544 +                                                              
      545 +### AMB-026 — Arredondar antes ou depois de converter; teto e 
          +valor positivo em qual moeda (F)                              
      546 +                                                              
      547 +**Texto original do RH:** "Uma despesa em EUR é convertida ant
          +es de ser comparada ao limite." A RN-003 arredondava `valor` "
          +antes de qualquer outra regra".                               
      548 +**O que não está claro:** se o arredondamento acontece na moed
          +a original, em reais, ou nos dois; e se o teto de um bilhão (A
          +MB-018) e o valor positivo (RN-004) usam o número recebido ou 
          +o convertido. 16,8649 EUR com taxa 5,93: arredondar antes dá 9
          +9,98 (não exige nota); converter antes dá 100,01 (exige).     
      549 +**Decisão:** converte o valor exato e arredonda uma vez, em re
          +ais. O teto compara só o número recebido, na moeda original (e
          +tapa 1). O valor positivo usa o valor em reais.               
      550 +**Justificativa:** todas as regras de valor trabalham em reais
          +; arredondar na moeda original cria um erro que a taxa multipl
          +ica. O teto existe para garantir cálculo exato e leitura segur
          +a, uma questão da forma do número recebido; um valor convertid
          +o acima de um bilhão continua exato e é cortado pelo limite. P
          +ara despesa em BRL, nada muda (taxa 1).                       
      551 +**Regra afetada:** RN-003, RN-004, RN-002                     
      552 +                                                              
      553 +### AMB-027 — Mínimo da nota fiscal: de onde vem e em qual moe
          +da se compara (F)                                             
      554 +                                                              
      555 +**Texto original do RH:** "Os limites da política são sempre e
          +m BRL." No arquivo v4: `"nota_fiscal_obrigatoria_acima_de": 10
          +0.00`, no nível de cima.                                      
      556 +**O que não está claro:** se o mínimo de 100,00 compara o valo
          +r convertido ou o número na moeda original (e-005: 40 USD sem 
          +nota = 220,00 BRL); se o mínimo passa a vir do arquivo.       
      557 +**Decisão:** compara o `valor_considerado` em reais; o mínimo 
          +vem do arquivo e é um só para todos os centros de custo.      
      558 +**Justificativa:** comparar na moeda original faria 99 USD (ce
          +rca de 545 BRL) passar sem nota e 101 BRL exigir; o mínimo dei
          +xaria de significar a mesma coisa para todos. O valor está no 
          +arquivo da política, que é a fonte dos números da política des
          +de a v4.                                                      
      559 +**Regra afetada:** RN-008                                     
      560 +                                                              
      561 +### AMB-028 — Duplicata entre moedas (U)                      
      562 +                                                              
      563 +**Texto original do RH:** "Duplicatas devem ser tratadas." (in
          +alterado na v4)                                               
      564 +**O que não está claro:** se a RN-007 compara o valor converti
          +do em reais ou o valor recebido junto com a moeda (22,00 EUR ×
          + 22,00 USD; 10,00 EUR × 59,30 BRL do mesmo gasto).            
      565 +**Decisão:** compara o valor recebido arredondado ao centavo, 
          +na moeda da despesa, junto com a moeda.                       
      566 +**Justificativa:** um lançamento repetido repete os números co
          +mo foram digitados; comparar em reais acoplaria a duplicata ao
          + arquivo de câmbio e poderia recusar gasto legítimo por coinci
          +dência de conversão. O mesmo gasto lançado em moedas diferente
          +s não é detectado (risco na seção 10).                        
      567 +**Regra afetada:** RN-007                                     
      568 +                                                              
      569 +### AMB-029 — Vigência da política (D)                        
      570 +                                                              
      571 +**Texto original do RH:** "Vigência imediata, retroativa à com
          +petência atual." No arquivo: `"vigencia": "2026-07-01"`.      
      572 +**O que não está claro:** se despesas anteriores à vigência sã
          +o recusadas, avaliadas por outra política ou avaliadas pela v4
          +; o que é "competência atual".                                
      573 +**Decisão:** a vigência é informativa: copiada para a saída, s
          +em efeito no cálculo.                                         
      574 +**Justificativa:** cada execução recebe explicitamente o arqui
          +vo de política (AMB-031): escolher a política certa para o per
          +íodo é um ato visível de quem executa, registrado na saída. O 
          +sistema só conhece uma política por execução; recusar uma desp
          +esa anterior à vigência a deixaria sem caminho de reembolso. A
          +plicar a política fora da vigência é risco aceito (seção 10). 
      575 +**Regra afetada:** RN-016                                     
      576 +                                                              
      577 +### AMB-030 — Fila de aprovação manual (item C, opcional) (U) 
      578 +                                                              
      579 +**Texto original do RH:** "Itens cujo valor reembolsável passe
          + de R$ 500 não são mais aprovados automaticamente. [...] cada 
          +item passa a ter um estado."                                  
      580 +**O que não está claro:** a unidade (reembolso do item, valor 
          +considerado, dia, período), se o estado é um status novo ou um
          + campo separado, e como entra nos totais.                     
      581 +**Decisão:** não implementado nesta versão (seção 3).         
      582 +**Justificativa:** o item é opcional no comunicado; com a v4, 
          +o maior reembolso possível de um item é 400,00 (hospedagem do 
          +`CC-COMERCIAL`, que não amplia em viagem), então a leitura lit
          +eral nunca dispara; as demais leituras reinterpretam "valor re
          +embolsável". Fica registrado para decisão futura.             
      583 +**Regra afetada:** nenhuma                                    
      584 +                                                              
      585 +### AMB-031 — Como a política e o câmbio chegam à execução (D)
      586 +                                                              
      587 +**Texto original do RH:** "O motor precisa ler a política de f
          +ora, não de dentro do código." / "As taxas estão em `cambio.js
          +on`."                                                         
      588 +**O que não está claro:** se os arquivos são argumentos, camin
          +hos fixos ou parte da entrada; se o câmbio é exigido quando to
          +das as despesas são em reais; o que fazer com um arquivo defei
          +tuoso.                                                        
      589 +**Decisão:** dois argumentos obrigatórios, `--politica` e `--c
          +ambio`, sempre; qualquer defeito em um deles é erro de arquivo
          + (RN-016).                                                    
      590 +**Justificativa:** tudo o que entra no cálculo aparece na linh
          +a de comando, e a mesma linha de comando dá sempre o mesmo res
          +ultado (seção 9). Um caminho implícito faria o resultado mudar
          + sem nada visível mudar. Com política ou câmbio defeituosos ne
          +nhum cálculo é confiável; recusar despesa por despesa esconder
          +ia o defeito atrás de recusas.                                
      591 +**Regra afetada:** seção 4, RN-016                            
      592 +                                                              
      593  ---
      594  
      595  ## 7. Casos de borda

  Ran 1 shell command (ctrl+o to expand)

⏺ Bash(python3 - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)
  ⎿  768
  ⎿  Updated specs/001-motor-reembolso/spec.md (+36 -3)
      490  **Justificativa:** a última ocorrência é a leitura mais comum 
           desse tipo de arquivo e corresponde a uma correção feita ao fi
           nal do registro; descartar em silêncio esconderia do conferent
           e um valor que pode ter mudado o reembolso, por isso o descart
           e é avisado.
      491  **Regra afetada:** RN-013
      492  
      493 -### Política v4 (D-007)                                       
      494 -                                                              
      495 -As ambiguidades abaixo vêm do comunicado da Política v4 e dos 
          -arquivos `politica-v4.json` e `cambio.json` (em `exemplos/enve
          -lope/`).                                                      
      493 +**Política v4 (D-007).** As ambiguidades abaixo vêm do comunic
          +ado da Política v4 e dos arquivos `politica-v4.json` e `cambio
          +.json` (em `exemplos/envelope/`).                             
      494  
      495  ### AMB-020 — "Aplica-se a política padrão": quando, e qual é 
           o padrão? (D, U)
      496  
     ...
      592  
      593  ## 7. Casos de borda
      594  
      595 +Salvo indicação na linha, cada caso usa a política `politica-v
          +4.json` e o câmbio `cambio.json` de `exemplos/envelope/`, um c
          +olaborador sem `centro_custo` (tabela `padrao`: alimentação 60
          +,00, transporte 80,00, hospedagem 250,00; acréscimo em viagem 
          +de 50%) e despesas sem `moeda` (em reais).                    
      596 +                                                              
      597  | Caso | Entrada | Comportamento esperado | Regra |
      598  |---|---|---|---|
      599  | Duas alimentações no mesmo dia somando mais que o limite | 7
           2,50 e 38,00 em 03/07, fora de viagem | 60,00 `parcial` e 0 `r
           ecusado` (`limite_diario_excedido`) | RN-009 |
     ...
      659  | Chave repetida mil vezes | `obs` 1000 vezes na mesma despesa
            | um aviso, `chave repetida: obs (1000 ocorrências; valeu a ú
           ltima)` | RN-013 |
      660  | Chave repetida em elemento que é lista | `[{"a": 1, "a": 2}]
           ` como elemento de `despesas` | `entrada_invalida`; aviso `cha
           ve repetida: [0].a (2 ocorrências; valeu a última)` | RN-013, 
           RN-002 |
      661  | Despesa em sábado | 18/07 (sábado) | avaliada normalmente | 
           AMB-015 |
      662 +| Centro de custo da tabela | `CC-COMERCIAL`, alimentação 85,0
          +0 com nota | `tabela_aplicada` `CC-COMERCIAL`; limite 90,00; `
          +aprovado` com 85,00 | RN-014 |                                
      663 +| Centro de custo fora da tabela | `CC-SUPORTE-N2`, alimentaçã
          +o 65,00 | `tabela_aplicada` `padrao`; limite 60,00; `parcial` 
          +com 60,00 | RN-014 |                                          
      664 +| Centro de custo com grafia diferente | `"cc-adm"`, alimentaç
          +ão 50,00 | não é `CC-ADM`: `padrao`, limite 60,00, `aprovado` 
          +com 50,00 | RN-014 |                                          
      665 +| Centro de custo só com espaços | `"centro_custo": "  "` | `p
          +adrao`; `colaborador.centro_custo` `"  "` na saída | RN-014 | 
      666 +| Centro de custo de tipo errado | `"centro_custo": 17` | erro
          + de arquivo | RN-002 |                                        
      667 +| Categoria ausente da tabela do centro de custo | `CC-ADM`, h
          +ospedagem 300,00 com nota em 14/07; alimentação 70,00 em 15/07
          + | hospedagem `categoria_fora_da_politica`; 15/07 não fica em 
          +viagem; alimentação limite 45,00, `parcial` com 45,00 | RN-014
          +, RN-006, RN-010 |                                            
      668 +| Categoria com limite zero | `CC-ENG-PLATAFORMA`, hospedagem 
          +480,00 com nota em 14/07; alimentação 100,00 com nota em 15/07
          + | hospedagem `categoria_fora_da_politica`; 15/07 não fica em 
          +viagem; alimentação limite 75,00, `parcial` com 75,00 | RN-006
          +, RN-010 |                                                    
      669 +| Representação fora do centro de custo que a define | `CC-SUP
          +ORTE-N2`, representação 190,00 com nota | `categoria_fora_da_p
          +olitica` | RN-006, RN-014 |                                   
      670 +| Representação não amplia em viagem | `CC-COMERCIAL`, hospeda
          +gem com nota em 22/07; representação 400,00 com nota em 23/07 
          +| 23/07 em viagem; representação limite 300,00, `parcial` com 
          +300,00 | RN-009 |                                             
      671 +| Limite em viagem truncado | política com alimentação 33,33 e
          + acréscimo 50; hospedagem com nota em 14/07; alimentação 60,00
          + em 15/07 | limite 49,99 (49,995 truncado); `parcial` com 49,9
          +9 | RN-009 |                                                  
      672 +| Moeda nula | `"moeda": null`, alimentação 45,00 | como `BRL`
          +: `moeda` `BRL`, `taxa_cambio` 1, `data_cotacao` nula, `aprova
          +do` com 45,00 | RN-015 |                                      
      673 +| Moeda estrangeira com cotação | 22,00 EUR em 14/07, alimenta
          +ção com nota | taxa 5,93, `data_cotacao` 2026-07-14; `valor_co
          +nsiderado` 130,46; `parcial` com 60,00 | RN-015, RN-003 |     
      674 +| Moeda estrangeira em sábado | 30,00 EUR em 18/07 (sábado), a
          +limentação com nota | taxa 5,96 de 17/07; `data_cotacao` 2026-
          +07-17; `valor_considerado` 178,80 | RN-015 |                  
      675 +| Cotação exatamente 3 dias antes | câmbio só com 13/07 (USD 5
          +,42); 10,00 USD em 16/07 | usa 13/07; `valor_considerado` 54,2
          +0 | RN-015 |                                                  
      676 +| Cotação 4 dias antes | câmbio só com 13/07; 10,00 USD em 17/
          +07 | `cambio_indisponivel`; `valor_considerado` nulo; fora dos
          + totais | RN-015 |                                            
      677 +| Moeda sem cotação no arquivo | 55,00 GBP em 21/07 | `cambio_
          +indisponivel`; `moeda` `GBP`; `taxa_cambio` e `valor_considera
          +do` nulos; fora de `valor_solicitado` | RN-015 |              
      678 +| Moeda em minúsculas | `"moeda": "eur"` | `entrada_invalida`;
          + `moeda` `eur` na saída | RN-002 |                            
      679 +| Moeda de tipo errado | `"moeda": 978` | `entrada_invalida`; 
          +`moeda` nula na saída | RN-002 |                              
      680 +| Sem cotação e fora do período | 10,00 USD em 15/04, período 
          +de julho | `cambio_indisponivel` (etapa 2 antes da 4) | RN-015
          + |                                                            
     … 17 more lines (ctrl+o to expand)

⏺ Bash(python3 - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)
  ⎿  696:## 8. Ordem de aplicação das regras
     697-
     698-Antes das etapas, a leitura verifica a forma do arquivo inteiro, i
     … +26 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/spec.md (+5 -3)
      668  | Categoria com limite zero | `CC-ENG-PLATAFORMA`, hospedagem 
           480,00 com nota em 14/07; alimentação 100,00 com nota em 15/07
            | hospedagem `categoria_fora_da_politica`; 15/07 não fica em 
           viagem; alimentação limite 75,00, `parcial` com 75,00 | RN-006
           , RN-010 |
      669  | Representação fora do centro de custo que a define | `CC-SUP
           ORTE-N2`, representação 190,00 com nota | `categoria_fora_da_p
           olitica` | RN-006, RN-014 |
      670  | Representação não amplia em viagem | `CC-COMERCIAL`, hospeda
           gem com nota em 22/07; representação 400,00 com nota em 23/07 
           | 23/07 em viagem; representação limite 300,00, `parcial` com 
           300,00 | RN-009 |
      671 -| Limite em viagem truncado | política com alimentação 33,33 e
          - acréscimo 50; hospedagem com nota em 14/07; alimentação 60,00
          - em 15/07 | limite 49,99 (49,995 truncado); `parcial` com 49,9
          -9 | RN-009 |                                                  
      671 +| Limite em viagem truncado | política cujo `padrao` tem alime
          +ntação 33,33 e hospedagem 250,00, acréscimo 50; hospedagem com
          + nota em 14/07; alimentação 60,00 em 15/07 | limite 49,99 (49,
          +995 truncado); `parcial` com 49,99 | RN-009 |                 
      672  | Moeda nula | `"moeda": null`, alimentação 45,00 | como `BRL`
           : `moeda` `BRL`, `taxa_cambio` 1, `data_cotacao` nula, `aprova
           do` com 45,00 | RN-015 |
      673  | Moeda estrangeira com cotação | 22,00 EUR em 14/07, alimenta
           ção com nota | taxa 5,93, `data_cotacao` 2026-07-14; `valor_co
           nsiderado` 130,46; `parcial` com 60,00 | RN-015, RN-003 |
      674  | Moeda estrangeira em sábado | 30,00 EUR em 18/07 (sábado), a
           limentação com nota | taxa 5,96 de 17/07; `data_cotacao` 2026-
           07-17; `valor_considerado` 178,80 | RN-015 |
     ...
      700  Cada despesa passa pelas etapas abaixo, nesta ordem. A primeir
           a etapa que a recusa encerra a avaliação dela.
      701  
      702  1. **Validação da despesa** — RN-002 (`entrada_invalida`).
      703 -2. **Arredondamento** — RN-003.                               
      703 +2. **Conversão e arredondamento** — RN-015 e RN-003: obtém a t
          +axa (`cambio_indisponivel` se não houver) e calcula o `valor_c
          +onsiderado` em reais.                                         
      704  3. **Valor positivo** — RN-004 (`valor_invalido`).
      705  4. **Período** — RN-005 (`fora_do_periodo`).
      706  5. **Categoria** — RN-006 (`categoria_fora_da_politica`).
     ...
      709  8. **Viagem** — RN-010: com todas as despesas já avaliadas pel
           as etapas 1 a 7, marca as datas em viagem.
      710  9. **Limite diário** — RN-009, por data e categoria, consumind
           o o limite na ordem da entrada.
      711  
      712 -Consequências: despesas recusadas nas etapas 1 a 7 não consome
          -m limite; uma despesa sem nota recusada na etapa 6 não impede 
          -que o relançamento com nota seja avaliado; uma hospedagem recu
          -sada nas etapas 1 a 7, ou sem nota, não caracteriza viagem; a 
          -viagem é determinada antes de qualquer limite ser aplicado.   
      712 +Antes das etapas, a tabela aplicada ao colaborador é escolhida
          + uma vez pelo `centro_custo` (RN-014); as etapas 5 e 9 usam es
          +sa tabela.                                                    
      713 +                                                              
      714 +Consequências: despesas recusadas nas etapas 1 a 7 não consome
          +m limite; uma despesa sem cotação é recusada na etapa 2, antes
          + de valor positivo, período e categoria, porque sem valor em r
          +eais nenhuma regra de valor pode ser avaliada; uma despesa sem
          + nota recusada na etapa 6 não impede que o relançamento com no
          +ta seja avaliado; uma hospedagem recusada nas etapas 1 a 7, ou
          + sem nota, não caracteriza viagem; a viagem é determinada ante
          +s de qualquer limite ser aplicado.                            
      715  
      716  ## 9. Critérios de aceite
      717  

⏺ Bash(python3 - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)
  ⎿  Updated specs/001-motor-reembolso/spec.md (+2 -2)
      697  
      698  Antes das etapas, a leitura verifica a forma do arquivo inteir
           o, inclusive das ocorrências descartadas (UTF-8, JSON válido e
            escapes, seção 4), e resolve chaves repetidas pela última oco
           rrência (RN-013): as demais validações da RN-002 e todas as et
           apas veem só o valor que valeu.
      699  
      700 +Os arquivos de política e de câmbio são lidos e validados por 
          +inteiro antes de qualquer despesa (RN-016), e a tabela aplicad
          +a ao colaborador é escolhida uma vez pelo `centro_custo` (RN-0
          +14). Essa tabela decide quais categorias são reconhecidas, inc
          +lusive para a saída de uma despesa inválida (seção 4), e os li
          +mites da etapa 9.                                             
      701 +                                                              
      702  Cada despesa passa pelas etapas abaixo, nesta ordem. A primeir
           a etapa que a recusa encerra a avaliação dela.
      703  
      704  1. **Validação da despesa** — RN-002 (`entrada_invalida`).
     ...
      711  8. **Viagem** — RN-010: com todas as despesas já avaliadas pel
           as etapas 1 a 7, marca as datas em viagem.
      712  9. **Limite diário** — RN-009, por data e categoria, consumind
           o o limite na ordem da entrada.
      713  
      712 -Antes das etapas, a tabela aplicada ao colaborador é escolhida
          - uma vez pelo `centro_custo` (RN-014); as etapas 5 e 9 usam es
          -sa tabela.                                                    
      713 -                                                              
      714  Consequências: despesas recusadas nas etapas 1 a 7 não consome
           m limite; uma despesa sem cotação é recusada na etapa 2, antes
            de valor positivo, período e categoria, porque sem valor em r
           eais nenhuma regra de valor pode ser avaliada; uma despesa sem
            nota recusada na etapa 6 não impede que o relançamento com no
           ta seja avaliado; uma hospedagem recusada nas etapas 1 a 7, ou
            sem nota, não caracteriza viagem; a viagem é determinada ante
           s de qualquer limite ser aplicado.
      715  
      716  ## 9. Critérios de aceite

⏺ Agora a seção 9, com as três tabelas calculadas à mão.

⏺ Bash(python3 - <<'EOF'
      import re…)
  ⎿  Updated specs/001-motor-reembolso/spec.md (+54 -16)
      717  
      718  O sistema está pronto quando:
      719  
      720 -- [ ] Processa `exemplos/despesas-exemplo.json` e produz exata
          -mente o resultado da tabela abaixo.                           
      720 +- [ ] Processa `exemplos/despesas-exemplo.json` e os dois arqu
          +ivos de despesas de `exemplos/envelope/`, com `exemplos/envelo
          +pe/politica-v4.json` e `exemplos/envelope/cambio.json`, e prod
          +uz exatamente os resultados das tabelas abaixo.               
      721  - [ ] Cada caso de borda da seção 7 tem um teste automatizado 
           que passa.
      722 -- [ ] Cada regra RN-001 a RN-013 tem pelo menos um teste autom
          -atizado que a referencia.                                     
      723 -- [ ] A mesma entrada sempre produz a mesma saída.            
      724 -- [ ] Entradas com erro de arquivo (RN-002) e chamadas com err
          -o de uso (seção 4) terminam com código diferente de 0 e não cr
          -iam nem alteram o arquivo de saída.                           
      722 +- [ ] Cada regra RN-001 a RN-016 tem pelo menos um teste autom
          +atizado que a referencia.                                     
      723 +- [ ] A mesma entrada, com a mesma política e o mesmo câmbio, 
          +sempre produz a mesma saída.                                  
      724 +- [ ] Entradas com erro de arquivo (RN-002, RN-016) e chamadas
          + com erro de uso (seção 4) terminam com código diferente de 0 
          +e não criam nem alteram o arquivo de saída.                   
      725  
      726 -**Resultado esperado para `exemplos/despesas-exemplo.json`** (
          -datas em viagem: 14/07 e 15/07, pela hospedagem d-010 com nota
          -):                                                            
      726 +Nas tabelas, "—" = nulo: o item foi recusado antes do limite d
          +iário. Itens sem `moeda` saem com `moeda` `BRL`, `taxa_cambio`
          + 1 e `data_cotacao` nula. Nenhum dos três arquivos tem chave r
          +epetida: `avisos` vazio em todos os itens e no topo.          
      727 +                                                              
      728 +### Exemplo: `exemplos/despesas-exemplo.json`                 
      729 +                                                              
      730 +`centro_custo` `CC-ENG-PLATAFORMA` → `tabela_aplicada` `CC-ENG
          +-PLATAFORMA` (alimentação 75,00, em viagem 112,50; transporte 
          +80,00, em viagem 120,00; hospedagem com limite 0, vedada pela 
          +AMB-021). Nenhuma data em viagem: a única hospedagem com nota 
          +(d-010) é recusada na etapa 5 e não comprova viagem. Todas as 
          +despesas em reais.                                            
      731  
      732  | id | considerado | em viagem | limite | reembolsado | status
            | motivo |
      733  |---|---|---|---|---|---|---|
      730 -| d-001 | 72,50 | não | 60,00 | 60,00 | parcial | limite_diari
          -o_excedido |                                                  
      731 -| d-002 | 38,00 | não | 60,00 | 0,00 | recusado | limite_diari
          -o_excedido |                                                  
      734 +| d-001 | 72,50 | não | 75,00 | 72,50 | aprovado | — |        
      735 +| d-002 | 38,00 | não | 75,00 | 2,50 | parcial | limite_diario
          +_excedido |                                                   
      736  | d-003 | 100,00 | não | 80,00 | 80,00 | parcial | limite_diar
           io_excedido |
      737  | d-004 | 100,01 | — | — | 0,00 | recusado | nota_fiscal_ausen
           te |
      738  | d-005 | 89,00 | — | — | 0,00 | recusado | categoria_fora_da_
           politica |
      735 -| d-006 | 54,90 | não | 60,00 | 54,90 | aprovado | — |        
      739 +| d-006 | 54,90 | não | 75,00 | 54,90 | aprovado | — |        
      740  | d-007 | 54,90 | — | — | 0,00 | recusado | duplicata |
      741  | d-008 | 41,00 | — | — | 0,00 | recusado | fora_do_periodo |
      742  | d-009 | -45,00 | — | — | 0,00 | recusado | valor_invalido |
      739 -| d-010 | 480,00 | sim | 250,00 | 250,00 | parcial | limite_di
          -ario_excedido |                                               
      740 -| d-011 | 33,33 | sim | 90,00 | 33,33 | aprovado | — |        
      741 -| d-012 | 47,20 | não | 60,00 | 47,20 | aprovado | — |        
      742 -| d-013 | 690,00 | — | — | 0,00 | recusado | nota_fiscal_ausen
          -te |                                                          
      743 -| d-014 | 61,00 | não | 60,00 | 60,00 | parcial | limite_diari
          -o_excedido |                                                  
      743 +| d-010 | 480,00 | — | — | 0,00 | recusado | categoria_fora_da
          +_politica |                                                   
     … 50 more lines (ctrl+o to expand)

⏺ Por último, a seção 10: os riscos reescritos e os novos.

⏺ Bash(python3 - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)
  ⎿  138:      "justificativa": "Aprovado integralmente: 45,00 dentro do li
     mite diário de 60,00.",
     144:      "justificativa": "Parcial: restavam 15,00 do limite diário d
     … +50 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/spec.md (+7 -2)
      797  
      798  ### Riscos conhecidos e aceitos
      799  
      800 -- **Fracionamento para escapar da nota fiscal** (AMB-008): trê
          -s hospedagens sem nota de 100,00 + 99,99 + 50,01 na mesma data
          - recebem 250,00, enquanto uma de 250,00 sem nota recebe 0. O g
          -anho é limitado aos casos em que o limite diário passa de 100,
          -00 (hospedagem e transporte em viagem). Aceito para não recusa
          -r despesas pequenas legítimas sem nota.                       
      801 -- **Viagem por hospedagem irrisória com nota declarada** (AMB-
          -004): uma hospedagem de 0,01 com `tem_nota_fiscal` verdadeiro 
          -põe D e D+1 em viagem e amplia os limites de alimentação e tra
          -nsporte em até 70,00 por dia (140,00 nos dois dias). Aceito po
          -rque o sistema não verifica notas (seção 3) e qualquer valor m
          -ínimo seria regra inventada; a saída expõe `em_viagem` por ite
          -m para a conferência humana. Mitigação definitiva: indicação e
          -xplícita de viagem na entrada (evolução, seção 3).            
      800 +- **Fracionamento para escapar da nota fiscal** (AMB-008): trê
          +s hospedagens sem nota de 100,00 + 99,99 + 50,01 na mesma data
          + recebem 250,00, enquanto uma de 250,00 sem nota recebe 0. O g
          +anho existe em toda categoria cujo limite diário (normal ou em
          + viagem) passa do mínimo da nota; com a v4, além da hospedagem
          + e do transporte em viagem, inclui o transporte do `CC-COMERCI
          +AL` (150,00), a alimentação do `CC-COMERCIAL` em viagem (135,0
          +0) e a representação (300,00). Aceito para não recusar despesa
          +s pequenas legítimas sem nota.                                
      801 +- **Viagem por hospedagem irrisória com nota declarada** (AMB-
          +004): uma hospedagem de 0,01 com `tem_nota_fiscal` verdadeiro 
          +põe D e D+1 em viagem e amplia os limites de alimentação e tra
          +nsporte pelo percentual da política. O ganho depende da tabela
          + aplicada: com a v4, 70,00 por dia no `padrao` e 120,00 por di
          +a no `CC-COMERCIAL` (45,00 + 75,00), o dobro nos dois dias. Nu
          +m centro de custo com hospedagem vedada, a hospedagem não comp
          +rova viagem (AMB-021). Aceito porque o sistema não verifica no
          +tas (seção 3) e qualquer valor mínimo seria regra inventada; a
          + saída expõe `em_viagem` por item para a conferência humana. M
          +itigação definitiva: indicação explícita de viagem na entrada 
          +(evolução, seção 3).                                          
      802  - **Limites de aninhamento e de tamanho do arquivo** (seção 4,
            RN-002): a RFC 8259 permite que a leitura limite a profundida
           de de aninhamento e o tamanho do arquivo e dos textos. A spec 
           não fixa esses limites: um arquivo com aninhamento muito profu
           ndo (milhares de níveis) ou de tamanho exagerado pode ser recu
           sado como erro de arquivo, sem saída, mesmo seguindo a gramáti
           ca. Aceito porque nenhum arquivo real de despesas chega perto 
           desses limites, e um número fixo seria regra sem origem na pol
           ítica.
      803  - **Caminho ambíguo no aviso de chave repetida** (RN-013): cha
           ves com `.`, `[` ou `]`, vazias ou com quebra de linha aparece
           m no caminho sem escape. Dois caminhos diferentes podem gerar 
           o mesmo texto (`"a.b"` e `a` → `b`), e um campo extra pode ger
           ar aviso idêntico ao de um campo da seção 4 que entra no cálcu
           lo (chave extra `"periodo.inicio"` repetida na raiz produz o m
           esmo aviso que o `periodo.inicio` verdadeiro repetido) ou um t
           exto que imita outro aviso. Nenhum valor muda: o aviso só pode
            enganar o conferente sobre qual chave foi descartada. Aceito 
           para manter o aviso legível; na dúvida, o conferente consulta 
           o arquivo de entrada.
      804  - **Letra com traço próprio não vira letra base** (seção 5, pa
           sso 2): `ø`, `ł`, `đ` e semelhantes não têm decomposição canôn
           ica e ficam como estão, então `"Smørrebrød"` e `"Smorrebrod"` 
           são fornecedores diferentes na RN-007. Aceito porque são raras
            em dados em português e uma tabela própria de equivalências s
           eria incompleta por construção.
     ...
      806  - **Classificação do Unicode decide os cantos** (seção 5, RN-0
           02): o resultado segue as categorias e propriedades do Unicode
            mesmo quando a aparência engana. Uma letra invisível (`ㅤ`, U
           +3164) conta como letra: `"BistroㅤCentral"` não é duplicata d
           e `"Bistro Central"` e um fornecedor só desse caractere é váli
           do. `º` × `°` e letras modificadoras parecidas com pontuação (
           `ʼ`, `ˊ`) dão fornecedores diferentes. U+0345 vira `ι` no pass
           o 1 (caixa) e por isso não é descartado no passo 2. Uma versão
            futura do Unicode pode reclassificar caracteres hoje não atri
           buídos. Aceito porque nenhum desses casos muda resultado em da
           dos realistas em português, e qualquer exceção exigiria lista 
           própria, incompleta por construção.
      807  - **Formas de compatibilidade distintas da forma comum** (seçã
           o 5, passo 2): letras e algarismos em largura total (`ＡＬＩＭ
           ＥＮＴＡＣＡＯ`), sobrescritos e ligaduras que a equivalência 
           de caixa não desfaz continuam diferentes da forma comum; uma c
           ategoria em largura total sai `categoria_fora_da_politica`. Ac
           eito por ser improvável em dados em português e porque desfaze
           r compatibilidades mudaria também caracteres que a spec não pe
           de (ex.: `²` viraria `2`).
      808  - **Quase-duplicatas** (AMB-010): o mesmo gasto relançado com 
           data vizinha, valor diferente em um centavo ou fornecedor com 
           outra grafia (além do que a normalização da seção 5 cobre) não
            é detectado. Aceito porque qualquer critério aproximado seria
            regra inventada e poderia recusar gastos legítimos repetidos.
      809 +- **Centro de custo autodeclarado** (AMB-020): o `centro_custo
          +` vem da mesma entrada que o colaborador produz; declarar `CC-
          +COMERCIAL` dá alimentação 90,00, transporte 150,00 e hospedage
          +m 400,00, e escrever `"cc-adm"` em vez de `CC-ADM` troca a tab
          +ela pelo `padrao` (mais generosa para o `CC-ADM`). Aceito pelo
          + mesmo motivo do `tem_nota_fiscal`: o sistema não tem cadastro
          + para conferir (seção 3); a saída expõe `colaborador.centro_cu
          +sto` e `politica.tabela_aplicada` para a conferência humana.  
      810 +- **Viagem internacional sem hospedagem lançada** (AMB-023): q
          +uem está no exterior sem hospedagem na entrada (hotel pago pel
          +a empresa por outro meio, por exemplo) não tem os limites ampl
          +iados; no envelope, o almoço de Lisboa e-002 recebe 90,00 de 1
          +30,46. Aceito porque a moeda é declarada e, como prova de viag
          +em, abriria brecha maior; mitigação definitiva é a indicação e
          +xplícita de viagem (seção 3).                                 
      811 +- **Mesmo gasto lançado em moedas diferentes** (AMB-028): 10,0
          +0 EUR e 59,30 BRL do mesmo gasto não são duplicatas e as duas 
          +são pagas até o limite do dia. Aceito porque comparar em reais
          + acoplaria a duplicata ao câmbio e só pegaria a conversão manu
          +al que batesse ao centavo.                                    
      812 +- **Política aplicada fora da vigência** (AMB-029): a execução
          + aplica o arquivo de política recebido a todas as despesas, me
          +smo às anteriores à `vigencia`. Aceito porque quem executa esc
          +olhe a política explicitamente (`--politica`) e a saída regist
          +ra `politica.versao` e `politica.vigencia`.                   
      813 +- **Cotação de até 3 dias antes** (AMB-024): uma despesa em di
          +a útil cuja cotação falta no arquivo (lacuna do arquivo, não f
          +im de semana) usa a de até 3 dias antes sem aviso, exceto pela
          + `data_cotacao` na saída. Aceito porque o arquivo declara publ
          +icar só em dias úteis e a diferença de taxa em 3 dias é pequen
          +a; lacunas maiores viram `cambio_indisponivel`.               

⏺ Bash(python3 - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)
  ⎿   specs/001-motor-reembolso/spec.md | 420 +++++++++++++++++++++++++++++
     +--------
      1 file changed, 337 insertions(+), 83 deletions(-)
  ⎿  Updated specs/001-motor-reembolso/spec.md (+2 -2)
      241  
      242  **Regra:** uma despesa de `hospedagem` **comprova viagem** qua
           ndo tem `tem_nota_fiscal` verdadeiro e passou pelas etapas 1 a
            7 da seção 8. Uma hospedagem que comprova viagem na data D co
           loca em viagem as datas **D e D+1** (a noite da diária e o dia
            seguinte). Em datas em viagem, os limites de `alimentacao` e 
           `transporte_urbano` são ampliados pelo percentual da política 
           (RN-009). A condição de viagem vale para todas as despesas da 
           data, independentemente da ordem em que aparecem na entrada. H
           ospedagem recusada por `categoria_fora_da_politica` (inclusive
            por limite 0, AMB-021) não comprova viagem. Despesa em moeda 
           estrangeira não comprova viagem (AMB-023).
      243  **Origem:** política do RH, item 6; AMB-004; AMB-021 e AMB-023
            (D-007).
      244 -**Aceite:** hospedagem com nota em 14/07 → 14/07 e 15/07 em vi
          -agem; alimentação de 80,00 em 15/07 → limite 90,00, `aprovado`
          - com 80,00; alimentação de 80,00 em 16/07 → limite 60,00, `par
          -cial` com 60,00. Hospedagem de 80,00 **sem** nota em 03/07 → r
          -eembolsada pelas regras normais, mas 03/07 e 04/07 **não** fic
          -am em viagem. Hospedagem com nota em 30/06, fora de um período
          - que começa em 01/07 → recusada por `fora_do_periodo`, e 01/07
          - não fica em viagem. `CC-ENG-PLATAFORMA`: hospedagem com nota 
          -em 14/07 → `categoria_fora_da_politica`; alimentação de 100,00
          - com nota em 15/07 → limite 75,00, `parcial` com 75,00. Alimen
          -tação de 22,00 EUR com nota em 14/07, sem hospedagem → 14/07 n
          -ão fica em viagem.                                            
      244 +**Aceite** (tabela `padrao` da v4): hospedagem com nota em 14/
          +07 → 14/07 e 15/07 em viagem; alimentação de 80,00 em 15/07 → 
          +limite 90,00, `aprovado` com 80,00; alimentação de 80,00 em 16
          +/07 → limite 60,00, `parcial` com 60,00. Hospedagem de 80,00 *
          +*sem** nota em 03/07 → reembolsada pelas regras normais, mas 0
          +3/07 e 04/07 **não** ficam em viagem. Hospedagem com nota em 3
          +0/06, fora de um período que começa em 01/07 → recusada por `f
          +ora_do_periodo`, e 01/07 não fica em viagem. `CC-ENG-PLATAFORM
          +A`: hospedagem com nota em 14/07 → `categoria_fora_da_politica
          +`; alimentação de 100,00 com nota em 15/07 → limite 75,00, `pa
          +rcial` com 75,00. Alimentação de 22,00 EUR com nota em 14/07, 
          +sem hospedagem → 14/07 não fica em viagem.                    
      245  
      246  ### RN-011 — Status e justificativa
      247  
     ...
      790  
      791  ### Decisões provisórias
      792  
      793 -- **Datas de entrada e saída de hospedagem.** A solução corret
          -a para AMB-005 exige mudar o formato de entrada. Decisão provi
          -sória: um lançamento = uma diária. Consequência conhecida: d-0
          -10 recebe 250,00 de 480,00 mesmo se forem de fato duas diárias
          -.                                                             
      793 +- **Datas de entrada e saída de hospedagem.** A solução corret
          +a para AMB-005 exige mudar o formato de entrada. Decisão provi
          +sória: um lançamento = uma diária. Consequência conhecida: uma
          + hospedagem de 480,00 "2 diarias" recebe 250,00 no `padrao` me
          +smo se forem de fato duas diárias (no envelope, e-007 "3 noite
          +s" recebe 400,00 de 1.200,00).                                
      794  - **Ids repetidos na entrada.** A política não trata. Decisão 
           provisória: despesas com o mesmo `id` são avaliadas normalment
           e, cada uma pelo seu conteúdo; a saída repete o id.
      795  - **`competencia` inconsistente com `inicio`/`fim`.** Decisão 
           provisória: o período vale por `inicio` e `fim`; `competencia`
            só é repetida na saída.
      796  - **Estorno vinculado a uma despesa.** Se o formato um dia tro
           uxer referência à despesa original, AMB-013 deve ser revista.

⏺ A spec 2.0 está escrita. Agora o D-007 no DECISIONS.md.

⏺ Update(specs/001-motor-reembolso/DECISIONS.md)
  ⎿  Added 76 lines
      10  
      11  ---
      12  
      13 +## D-007 — Política de Reembolso v4 (envelope do Dia 2): spec 1
         +.9 → 2.0 · `2026-10-02`                                        
      14 +                                                               
      15 +**Gatilho:** mudança de requisito do RH, "Política de Reembolso
         + v4" (`exemplos/envelope/00-ENVELOPE-LACRADO.md`), com os arqui
         +vos `politica-v4.json`, `cambio.json`, `despesas-envelope.json`
         + e `despesas-envelope-cc-desconhecido.json`. Três itens:       
      16 +- **A.** Limites por centro de custo, lidos de um arquivo, com 
         +tabela padrão.                                                 
      17 +- **B.** Despesas em moeda estrangeira, convertidas pela taxa d
         +a data.                                                        
      18 +- **C.** Opcional: fila de aprovação acima de R$ 500.          
      19 +                                                               
      20 +Ponto de partida: commit `edeeb2d`, 2026-10-02 19:51.          
      21 +                                                               
      22 +**Como foi decidido:** antes de editar a spec, foram feitos um 
         +mapeamento de impacto e uma rodada do `spec-adversary` sobre o 
         +envelope contra a spec 1.9. A revisão apontou 17 problemas: 11 
         +bloqueantes, 4 importantes e 2 menores. O mais grave foi que o 
         +exemplo da seção 9 é do `CC-ENG-PLATAFORMA`, e a v4 muda o seu 
         +resultado.                                                     
      23 +                                                               
      24 +O responsável decidiu os 17 pontos um a um. Dois pontos tiveram
         + ajuste durante a discussão:                                   
      25 +- **Limite 0 (ponto 2).** A recomendação inicial ("categoria ve
         +dada, mas comprova viagem") era incoerente com a seção 8. A rev
         +isão expôs o erro, e a decisão ficou "categoria vedada, não com
         +prova viagem".                                                 
      26 +- **Limite ampliado (ponto 10c).** O responsável perguntou se a
         +rredondar o limite poderia interagir com a nota fiscal. Não pod
         +e: a nota compara o valor da despesa, antes do limite, na AMB-0
         +08. Mesmo assim, o responsável escolheu truncar, pelo argumento
         + de que o limite é um teto.                                    
      27 +                                                               
      28 +A recomendação para a vigência (ponto 15) mudou de "recusar" pa
         +ra "informativa" depois que o ponto 11 tornou a política um arg
         +umento explícito. Sessão `docs/sessions/36-*`, continuada na `3
         +7-*`.                                                          
      29 +                                                               
      30 +**O que mudou na spec** (numeração dos pontos = numeração da re
         +visão adversarial):                                            
      31 +                                                               
      32 +| # | Ponto | De (1.9) | Para (2.0) | Onde |                   
      33 +|---|---|---|---|---|                                          
      34 +| 11 | Como política e câmbio entram na execução (**bloqueante*
         +*) | limites e nota fixos na spec; sem câmbio | `--politica` e 
         +`--cambio` obrigatórios; defeito em qualquer um dos dois arquiv
         +os é erro de arquivo; `dia` e `diaria` têm o mesmo significado 
         +| seção 4, RN-016, AMB-031 |                                   
      35 +| 1 | Exemplo da seção 9 é do `CC-ENG-PLATAFORMA` (**bloqueante
         +**) | 585,43 reembolsado (limites fixos) | recalculado com a ta
         +bela do `CC-ENG-PLATAFORMA`: 351,43. Seção 7 passa a declarar p
         +olítica v4, sem centro de custo (`padrao`) e em reais | seções 
         +7 e 9 |                                                        
      36 +| 3 | "Aplica-se a política padrão" (**bloqueante**) | não exis
         +tia | padrão = bloco `padrao` do arquivo, só para centro de cus
         +to fora da tabela; tabela aplicada fechada; categoria fora dela
         + → `categoria_fora_da_politica` | RN-014, RN-006, AMB-020 |    
      37 +| 4 | Identificação do centro de custo (**bloqueante**) | campo
         + opcional, ignorado | comparação exata; ausente, nulo ou só esp
         +aços → `padrao`; outro tipo → erro de arquivo; autodeclarado = 
         +risco aceito | seção 4, RN-002, RN-014, seção 10 |             
      38 +| 2 | Limite 0 ("não reembolsa de forma alguma") (**bloqueante*
         +*) | não existia | `categoria_fora_da_politica` (etapa 5); não 
         +comprova viagem | RN-006, RN-010, AMB-021 |                    
      39 +| 10 | Acréscimo de viagem (**bloqueante**) | tabela fixa 90 / 
         +120 / 250 | percentual do arquivo; só `alimentacao` e `transpor
         +te_urbano`; limite ampliado truncado ao centavo | RN-009, AMB-0
         +06, AMB-022 |                                                  
      40 +| 9 | Moeda estrangeira caracteriza viagem? (**bloqueante**) | 
         +não existia | não; só hospedagem com nota | RN-010, AMB-023, se
         +ção 3, seção 10 |                                              
      41 +| 6 | Data sem cotação (**bloqueante**) | não existia | cotação
         + anterior mais próxima, até D-3; sem ela → `cambio_indisponivel
         +`; nunca cotação posterior | RN-015, AMB-024, AMB-015 |        
      42 +| 7 | Moeda sem cotação, mal escrita ou nula (**bloqueante**) |
         + `moeda` era campo extra ignorado | 3 letras maiúsculas `A`–`Z`
         + exatas, senão `entrada_invalida`; nulo = `BRL`; `BRL` taxa 1; 
         +sem cotação → `cambio_indisponivel`; sem lista ISO | seção 4, R
         +N-002, RN-015, AMB-025 |                                       
      43 +| 8 | Arredondamento × conversão; teto; valor positivo (**bloqu
         +eante**) | arredonda `valor` em reais | converte o valor exato 
         +e arredonda uma vez, em reais; teto sobre o número recebido; va
         +lor positivo sobre o valor em reais | RN-002, RN-003, RN-004, A
         +MB-026 |                                                       
      44 +| 5 | Nota fiscal em qual moeda; origem do mínimo (**bloqueante
         +**) | 100,00 fixo | mínimo do arquivo, único para todos os cent
         +ros de custo, comparado em reais | RN-008, AMB-007, AMB-027 |  
      45 +| 12 | Etapa da conversão | — | etapa 2 (conversão + arredondam
         +ento); sem cotação recusa ali; ordem das demais etapas mantida 
         +| seção 8 |                                                    
      46 +| 13 | Duplicata entre moedas | compara `valor_considerado` | c
         +ompara o valor recebido arredondado na moeda original + a moeda
         + | RN-003, RN-007, AMB-028 |                                   
      47 +| 14 | Saída sem moeda, taxa e política | — | item: `moeda`, `t
         +axa_cambio`, `data_cotacao`; topo: `colaborador.centro_custo`, 
         +`politica` (`versao`, `vigencia`, `tabela_aplicada`) | seção 4 
         +|                                                              
      48 +| 15 | Vigência | — | informativa, copiada para a saída; aplica
         +r a política fora da vigência é risco aceito | RN-016, AMB-029,
         + seção 10 |                                                    
      49 +| 16 | Item C (aprovação manual) | — | não implementado; com a 
         +v4, nunca dispara por item (máximo de 400,00) | seção 3, AMB-03
         +0 |                                                            
      50 +| 17 | Textos que a v4 contradiz | "não converte moedas", "sem 
         +representação", "100,00 fixo", riscos com valores fixos | reesc
         +ritos: seção 3, AMB-006, AMB-007, AMB-015, AMB-017, riscos de f
         +racionamento e hospedagem irrisória sem valores fixos; 5 riscos
         + novos | seções 3, 6, 10 |                                     
      51 +                                                               
      52 +**Detalhes fixados na redação** (consequências das decisões aci
         +ma, a confirmar na próxima rodada do `spec-adversary`):        
      53 +- A despesa recusada por `cambio_indisponivel` tem `valor_consi
         +derado` nulo e fica fora de `valor_solicitado`, como `entrada_i
         +nvalida`. Sem cotação, não existe valor em reais.              
      54 +- Arquivos de política e câmbio:                               
      55 +  - chave repetida é erro de arquivo (a RN-013 vale só para a e
         +ntrada);                                                       
      56 +  - limites e mínimo da nota com no máximo 2 casas decimais;   
      57 +  - nomes de categoria do arquivo normalizados pela seção 5; do
         +is nomes iguais depois da normalização são erro de arquivo;    
      58 +  - `versao` texto não vazio e `vigencia` data válida obrigatór
         +ias;                                                           
      59 +  - campos não listados são ignorados; tabela vazia é válida.  
      60 +- `itens[].moeda` sai como veio quando é texto, mesmo fora do f
         +ormato (`eur`), e nula quando tem outro tipo.                  
      61 +                                                               
      62 +**Por quê:** o comunicado manda ler a política de fora do códig
         +o e converter pela taxa da data. As decisões seguem três princí
         +pios já usados na 1.x:                                         
      63 +- **Nada implícito.** Os arquivos chegam na linha de comando e 
         +a saída registra a tabela, a moeda, a taxa e a data da cotação 
         +usadas.                                                        
      64 +- **Não inventar regra.** A tabela do centro de custo é fechada
         +, nenhuma categoria nova é ampliada em viagem e não há lista IS
         +O própria.                                                     
      65 +- **Fechar brechas exploráveis com dados declarados.** O limite
         + 0 não comprova viagem e a moeda estrangeira também não comprov
         +a. As brechas que restam viram riscos aceitos e expostos na saí
         +da.                                                            
      66 +                                                               
      67 +As justificativas de cada ponto estão nas AMB-020 a AMB-031.   
      68 +                                                               
      69 +**O que isso invalidou:**                                      
      70 +- **Resultados.** O resultado da seção 9 (todo o cálculo do exe
         +mplo); a tabela de limites da RN-009; o motivo de d-013 (`nota_
         +fiscal_ausente` → `categoria_fora_da_politica`); o contrato de 
         +saída (campos novos); a interface da CLI (dois argumentos obrig
         +atórios).                                                      
      71 +- **Código.** `politica.py` deixa de ter constantes de limite, 
         +nota e percentual. `motor.py`, `entrada.py` (categoria reconhec
         +ida passa a depender da tabela aplicada; `moeda` e `centro_cust
         +o` validados), `justificativa.py` (mínimo da nota), `saida.py` 
         +e `cli.py` mudam.                                              
      72 +- **Testes.** `test_politica.py` e `test_exemplo.py` são reescr
         +itos. Os testes de regra que não definem centro de custo contin
         +uam válidos com a tabela `padrao` da v4, cujos valores são igua
         +is aos da 1.9.                                                 
      73 +- **Rastreabilidade.** `test_rastreabilidade.py` passa a exigir
         + testes para a RN-014 a RN-016 e para os 33 casos novos da seçã
         +o 7. A suíte fica vermelha até as tasks do envelope serem concl
         +uídas.                                                         
      74 +                                                               
      75 +**Tasks afetadas:** reabertas por substituição, numeradas a par
         +tir da T-022 em `tasks.md` (a definir depois do `plan.md`):    
      76 +- T-002 (política como dados, não constantes);                 
      77 +- T-009 (validação de `moeda` e `centro_custo`; categoria depen
         +dente da tabela);                                              
      78 +- T-010 e T-015 (tabela aplicada);                             
      79 +- T-016 (mínimo da nota vindo do arquivo, em reais);           
      80 +- T-017 (duplicata com moeda);                                 
      81 +- T-018 (percentual do arquivo, truncamento, limite 0);        
      82 +- T-019 (CLI com `--politica` e `--cambio`);                   
      83 +- T-020 (três tabelas da seção 9).                             
      84 +                                                               
      85 +**Custo:** a medir no fechamento (arquivos tocados à mão × task
         +s reexecutadas), para o relatório.                             
      86 +                                                               
      87 +---                                                            
      88 +                                                               
      89  ## D-006 — Arquivo defeituoso: escape inválido em ocorrência de
          scartada e codificação da entrada: spec 1.8 → 1.9 · `2026-10-01
          `
      90  
      91  **Gatilho:** revisão independente da T-007 (`docs/reviews/T-007
          .md`, revisões 1 e 2, "Decisões necessárias" 1). A seção 4 dizi
          a que escape sem caractere válido "em qualquer chave ou valor" 
          é erro de arquivo; a RN-013 dizia que as ocorrências descartada
          s por chave repetida "nenhuma regra as considera". Para `"obs":
           "\uD800", "obs": "ok"` as duas leituras davam resultados opost
          os (erro de arquivo × despesa processada com aviso). O código d
          a T-006 seguia a segunda sem decisão explícita: só verificava o
          s valores que valeram. Decidido pelo responsável (ponto 1). A r
          odada do `spec-adversary` sobre a primeira redação da 1.9 apont
          ou 3 problemas (1 bloqueante): a codificação da entrada não est
          ava na spec (só no DT-002 do plano), o parêntese `\uD800` a `\u
          DFFF` podia ser lido como exemplo e não como lista, e o alcance
           do descarte em profundidade era ambíguo na RN-013. O responsáv
          el aceitou as 3 recomendações (pontos 2 a 4), que registram na 
          spec o que o plano e o código já faziam. A rodada de confirmaçã
          o apontou 4 problemas (2 bloqueantes): a seção 8 podia ser lida
           como se todo erro de arquivo da RN-002 valesse para a ocorrênc
          ia descartada; "JSON válido" não tinha definição (caractere de 
          controle cru, `NaN`, `01.5`); "par correspondente" e BOM repeti
          do sem resultado. O responsável aceitou as 4 recomendações (pon
          tos 5 a 8). A confirmação final não apontou bloqueante; o único
           achado (limites de profundidade e tamanho que a RFC 8259 deixa
           à implementação) virou risco aceito (ponto 9), depois de o tes
          te mostrar que a leitura quebrava com erro interno a partir de 
          alguns milhares de níveis. Sessão `docs/sessions/18-*`.

  Ran 1 shell command (ctrl+o to expand)

⏺ Terminei os passos 1 e 2: a spec 2.0 e o D-007 no DECISIONS.md estão escritos,
  nada commitado. Como combinado, te mostro as tabelas da seção 9 antes de
  rodar o spec-adversary.

  O que mudou na spec

  - Seções 2 e 3 (objetivo e fora de escopo): um parágrafo sobre a v4 no
    objetivo; "não converte moedas" saiu do fora de escopo e entraram o item C e
    o centro de custo não verificado.
  - Seção 4: a interface ganhou --politica e --cambio, e a entrada ganhou moeda.
    Na saída entram moeda, taxa_cambio, data_cotacao, colaborador.centro_custo
    e o bloco politica; há um motivo novo, cambio_indisponivel. O exemplo JSON
    foi atualizado.
  - Regras:
    - ajustadas: RN-002, 003, 004, 006, 007, 008, 009, 010 e 012;
    - novas: RN-014 (tabela aplicada), RN-015 (moeda e conversão) e RN-016
      (arquivos de política e câmbio).
  - Seção 6: AMB-006, 007, 015 e 017 reescritas; AMB-020 a AMB-031 novas, uma
    por decisão.
  - Seção 7: uma frase de premissa ("salvo indicação: v4, tabela padrao, em
    reais") e 33 casos novos (eram 63, agora são 96).
  - Seção 8: a etapa 2 virou "conversão e arredondamento". A política e o câmbio
    são lidos antes de qualquer despesa.
  - Seção 10: dois riscos reescritos sem valores fixos e cinco riscos novos.

  Seção 9 (contas feitas à mão; as conversões conferi também com Decimal)

  Exemplo (CC-ENG-PLATAFORMA): reembolsado 351,43 (antes 585,43), glosado
  1.510,41. Duas mudanças que não estavam no mapeamento inicial:
  - d-013 (hospedagem de 690,00 sem nota) muda de motivo: de nota_fiscal_ausente
    para categoria_fora_da_politica. A categoria (etapa 5) vem antes da nota
    (etapa 6), e hospedagem é vedada no CC-ENG.
  - d-011 fica fora de viagem, porque a d-010 não comprova mais. Com limite 75
    ela continua aprovada com 33,33.

  despesas-envelope.json (CC-COMERCIAL):

  ┌────────────────┬─────────────┬─────────────┬────────────────────────────┐
  │       id       │ considerado │ reembolsado │      status / motivo       │
  ├────────────────┼─────────────┼─────────────┼────────────────────────────┤
  │ e-001          │             │             │                            │
  │ representação  │ 340,00      │ 300,00      │ parcial                    │
  │ 340            │             │             │                            │
  ├────────────────┼─────────────┼─────────────┼────────────────────────────┤
  │ e-002 22 EUR   │ 130,46      │ 90,00       │ parcial                    │
  ├────────────────┼─────────────┼─────────────┼────────────────────────────┤
  │ e-003 14,50    │ 85,26       │ 85,26       │ aprovado                   │
  │ EUR            │             │             │                            │
  ├────────────────┼─────────────┼─────────────┼────────────────────────────┤
  │ e-004 30 EUR,  │             │             │                            │
  │ sábado → taxa  │ 178,80      │ 90,00       │ parcial                    │
  │ de 17/07       │             │             │                            │
  ├────────────────┼─────────────┼─────────────┼────────────────────────────┤
  │ e-005 40 USD   │ 220,00      │ 0           │ nota_fiscal_ausente        │
  │ sem nota       │             │             │                            │
  ├────────────────┼─────────────┼─────────────┼────────────────────────────┤
  │ e-006 GBP      │ —           │ 0           │ cambio_indisponivel        │
  ├────────────────┼─────────────┼─────────────┼────────────────────────────┤
  │ e-007 hotel    │ 1.200,00    │ 400,00      │ parcial (22/07 e 23/07 em  │
  │ 1.200          │             │             │ viagem)                    │
  ├────────────────┼─────────────┼─────────────┼────────────────────────────┤
  │ e-008 95 em    │ 95,00       │ 95,00       │ aprovado (limite 135)      │
  │ 23/07          │             │             │                            │
  ├────────────────┼─────────────┼─────────────┼────────────────────────────┤
  │ e-009          │ 120,00      │ 0           │ categoria_fora_da_politica │
  │ coworking      │             │             │                            │
  ├────────────────┼─────────────┼─────────────┼────────────────────────────┤
  │ e-010 sem      │ 88,00       │ 88,00       │ aprovado                   │
  │ moeda          │             │             │                            │
  └────────────────┴─────────────┴─────────────┴────────────────────────────┘

  Totais: solicitado 2.457,52 · reembolsado 1.148,26 · glosado 1.309,26.

  despesas-envelope-cc-desconhecido.json (CC-SUPORTE-N2 → padrao): f-001
  aprovado 58,00; f-002 parcial 250,00; f-003 categoria_fora_da_politica; f-004
  12 USD → 65,76 aprovado. Reembolsado 373,76, glosado 250,00.

  Quatro detalhes que fixei ao redigir e precisam do seu ok

  Não estavam nas 17 decisões, mas a spec precisava de alguma resposta. Estão
  marcados no D-007 como "a confirmar":
  1. Despesa com cambio_indisponivel: valor_considerado nulo e fica fora de
     valor_solicitado. Sem cotação não existe valor em reais; é o mesmo
     tratamento de entrada_invalida.
  2. Chave repetida no arquivo de política ou de câmbio: erro de arquivo. O
     aviso de chave repetida da RN-013 continua valendo só para a entrada.
  3. Nomes de categoria no arquivo de política: normalizados pela seção 5, como
     a categoria da despesa. Dois nomes que ficam iguais depois da normalização
     são erro de arquivo.
  4. Limites e mínimo da nota: no máximo 2 casas decimais. versao e vigencia são
     obrigatórias, e uma tabela vazia é válida.

  A suíte fica vermelha a partir de agora. O teste de rastreabilidade
  (test_rastreabilidade.py) já falha: a spec exige testes para RN-014 a RN-016 e
  para os 33 casos novos. Isso é esperado (spec antes do código) e só volta a
  verde quando as tasks do envelope estiverem concluídas.

  Se estiver ok com as tabelas e os 4 detalhes, rodo o spec-adversary na spec
  2.0.

✻ Cogitated for 7m 13s · done 9:02 PM

❯ vamos fazer export e commitar                                                 

⏺ Antes do export, há um problema com o commit único.

  O hook pre-commit roda o pytest sempre que algo em exemplos/ vai no commit. Os
  arquivos do envelope (exemplos/envelope/) entram nessa regra. Com a spec 2.0
  no mesmo commit, o test_rastreabilidade.py falha (RN-014 a RN-016 e 33 casos
  ainda sem teste), e o hook bloqueia. spec.md, DECISIONS.md e o export sozinhos
  passam, porque são só documentação e o pytest não roda.

  Proposta: dois commits, ambos antes do export.
  1. Agora: docs(spec): adiciona os arquivos do envelope da Política v4 em 
     exemplos/envelope.
     - Vai com SEM_EXPORT=1, porque não fecha o bloco.
     - Para o pytest rodar ainda sobre a spec 1.9, eu guardo as mudanças da spec
       com git stash antes e as restauro depois.
  2. Depois do seu /export: docs(spec): spec 2.0 — Política v4 (D-007), com a
     spec, o DECISIONS.md e o export.

  Isso também vai travar as tasks do envelope. Enquanto a spec cobrar testes que
  ainda não existem, todo commit feat(T-NNN) vai ser bloqueado pelo pre-commit.
  Vou tratar isso no plan.md e no tasks.md. Uma opção é a primeira task do
  envelope criar todos os testes novos marcados como falha esperada (xfail);
  cada task seguinte remove a marcação dos seus.

  Os 4 detalhes que fixei na redação continuam marcados como "a confirmar" no
  D-007. Podem ir assim nesse commit e serem confirmados na próxima rodada do
  spec-adversary.

  Faço o commit 1 agora? Se sim, depois você roda /export 
  docs/sessions/37-politica-v4-decisoes-e-spec-2-0.md e eu faço o commit 2.

✻ Crunched for 20s · done 9:04 PM
❯ entao nao precisa, continua o que estavamos fazendo                           

⏺ Combinado: nada de commit por enquanto. Sigo com a revisão adversarial da spec
  2.0.

⏺ spec-adversary(Adversarial review of spec 2.0)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ O spec-adversary está rodando sobre a spec 2.0. Pedi a ele que:
  - confira contradições: procure contradições internas, lacunas e brechas
    novas;
  - refaça as contas à mão: as três tabelas da seção 9 e os 33 casos novos da
    seção 7;
  - julgue os detalhes da redação: diga se os 4 detalhes que fixei são
    consequência das 17 decisões ou decisões novas escondidas;
  - não reabra as 17 decisões, a menos que alguma cause contradição concreta.

  Te aviso quando ele terminar.

✻ Cogitated for 12s · done 9:04 PM

❯ ok, me avisa quando terminar                                                  

⏺ Combinado. Te aviso quando a revisão terminar, com a mesma triagem de antes: o
  que é bloqueante, os números que ele contestar e o veredito sobre os 4
  detalhes.

✻ Worked for 1s · done 9:05 PM

› Message from spec-adversary
  Revisão adversarial da spec 2.0: 10 problemas, 2 bloqueantes, 4 importantes e
  4 menores. As três tabelas da seção 9 e seus totais estão corretos, conferidos
  à mão. Nos 33 casos novos da seção 7 não há número errado, mas dois casos não
  trazem os dados necessários para chegar ao valor esperado (ver o item 8).

  Arquivos lidos:
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md`,
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md`
  (D-007), `/Users/rafaeltxm/repo/sdd-desafio/exemplos/envelope/*`,
  `/Users/rafaeltxm/repo/sdd-desafio/exemplos/despesas-exemplo.json`. Não li
  `src/` nem `tests/`. Não alterei nenhum arquivo.

  ---

  ## Conferência numérica (pedido 4)

  - **Exemplo (`CC-ENG-PLATAFORMA`):** os 14 itens estão corretos.
    - Solicitado: 72,50 + 38,00 + 100,00 + 100,01 + 89,00 + 54,90 + 54,90 +
  41,00 + 480,00 + 33,33 + 47,20 + 690,00 + 61,00 = **1.861,84**.
    - Reembolsado: 72,50 + 2,50 + 80,00 + 54,90 + 33,33 + 47,20 + 61,00 =
  **351,43**.
    - Glosado: **1.510,41**.
  - **Envelope `CC-COMERCIAL`:** os 10 itens estão corretos.
    - Conversões: 22 × 5,93 = 130,46; 14,50 × 5,88 = 85,26; 30 × 5,96 = 178,80;
  40 × 5,50 = 220,00.
    - Solicitado: **2.457,52**. Reembolsado: 300 + 90 + 85,26 + 90 + 400 + 95 +
  88 = **1.148,26**. Glosado: **1.309,26**.
  - **Envelope `CC-SUPORTE-N2`:** os 4 itens estão corretos.
    - Conversão: 12 × 5,48 = 65,76.
    - Solicitado: **623,76**. Reembolsado: **373,76**. Glosado: **250,00**.
  - **Seção 7, 33 casos novos:** os valores que dá para calcular conferem.
  Exemplos: 16,8649 × 5,93 = 100,008857 → 100,01; 33,33 × 1,5 = 49,995 → 49,99;
  200.000.000 × 5,44 = 1.088.000.000,00; o D-3 a partir de 13/07.
  - **AMB-024, AMB-026 e AMB-028:** as contas também conferem (16,70 × 5,96 =
  99,53; 16,70 × 6,01 = 100,37; 10 × 5,93 = 59,30).

  ---

  ### 1. Hospedagem paga em moeda estrangeira comprova viagem? — BLOQUEANTE —
  ambiguidade

  - **Regras afetadas:** RN-010 ("Despesa em moeda estrangeira não comprova
  viagem"), RN-015 ("A moeda não muda nenhuma outra regra: não caracteriza
  viagem"), AMB-023 ("a viagem continua comprovada só por hospedagem com nota").
  - **Cenário de entrada:** tabela `padrao`.
    - Hospedagem de 50,00 EUR com nota em 22/07 (5,95 → 297,50).
    - Alimentação de 80,00 BRL em 23/07.
  - **Comportamento pela interpretação atual:** indefinido.
    - **Leitura A:** o que conta é ser hospedagem com nota, e a moeda não
  importa. 22/07 e 23/07 ficam em viagem, e a alimentação tem limite 90,00,
  `aprovado` com 80,00.
    - **Leitura B:** a frase da RN-010 vale para qualquer despesa em moeda
  estrangeira, inclusive hospedagem. 23/07 fica fora de viagem, e a alimentação
  tem limite 60,00, `parcial` com 60,00.
  - **Por que é um problema:** viagem internacional é justamente o cenário da
  v4, e hotel no exterior pago em EUR ou GBP é o caso típico. A AMB-023 só
  discute a alimentação e-002, sem hospedagem. O caso da seção 7 "Moeda
  estrangeira não comprova viagem" não diz a categoria da despesa em EUR, então
  não resolve.
  - **Pergunta para decisão:** uma hospedagem com nota em moeda estrangeira que
  passa pelas etapas 1 a 7 comprova viagem (A) ou não comprova (B)?

  ### 2. "Data anterior mais próxima" quando a data intermediária existe mas não
  tem a moeda — BLOQUEANTE — ambiguidade

  - **Regra afetada:** RN-015, AMB-024.
  - **Cenário de entrada:**
    - Câmbio: `{"2026-07-13": {"USD": 5.42, "EUR": 5.91}, "2026-07-14": {"USD":
  5.44}}`. O formato é válido pela RN-016.
    - Despesa: alimentação de 20,00 EUR com nota em 15/07, tabela `padrao`.
  - **Comportamento pela interpretação atual:** indefinido.
    - **Leitura A:** vale a data mais próxima que tem cotação **dessa moeda**.
  Usa 13/07 (D-2), 20 × 5,91 = 118,20, e paga 60,00.
    - **Leitura B:** vale a data anterior mais próxima **do arquivo**, que é
  14/07. Como ela não tem EUR, a despesa sai `cambio_indisponivel` e não é paga.
  - **Por que é um problema:** o arquivo é um objeto de data → moedas, então
  datas com só algumas moedas são um formato válido e plausível (publicação
  parcial). A frase "Se essa data não tem cotação para a moeda, usa-se a cotação
  da data anterior mais próxima" pode ser lida das duas formas. O resultado
  muda entre pagar e recusar.
  - **Pergunta para decisão:** a busca de D-1 a D-3 procura a data mais próxima
  com cotação daquela moeda (A), ou a data mais próxima presente no arquivo,
  recusando se ela não tiver a moeda (B)?

  ### 3. `moeda_base` ausente na política ou no câmbio — IMPORTANTE — lacuna

  - **Regra afetada:** RN-016 ("`moeda_base` diferente de `"BRL"`", na política
  e no câmbio).
  - **Cenário de entrada:** `politica-v4.json` sem a chave `moeda_base`. O mesmo
  vale para o câmbio. Todo o resto válido.
  - **Comportamento pela interpretação atual:** indefinido.
    - Para os outros campos, a RN-016 diz "ausente ou ...".
    - Para `moeda_base` diz só "diferente de". Ausente pode contar como
  "diferente de BRL" (erro de arquivo, sem saída) ou como campo opcional
  (processa normalmente).
  - **Por que é um problema:** decide se existe saída ou não, e o código teria
  de escolher sozinho.
  - **Pergunta para decisão:** `moeda_base` é obrigatória nos dois arquivos
  (ausente = erro de arquivo) ou opcional (ausente = aceita)?

  ### 4. Números dos arquivos de política e câmbio: "casas decimais" pela forma
  ou pelo valor, e sem teto — IMPORTANTE — ambiguidade e lacuna

  - **Regras afetadas:** RN-016 (limite e mínimo da nota com "no máximo 2 casas
  decimais"), seção 4 (número vale pelo "valor decimal exato... 72.50 e 72.5 são
  o mesmo valor"), AMB-018 e AMB-026 (justificativa do teto).
  - **Cenário de entrada:**
    - (a) `"limite": 60.000` ou `"limite": 6E1`, ou
  `"nota_fiscal_obrigatoria_acima_de": 1.000E2`.
    - (b) Câmbio com `"USD": 1e999999`, ou política com `"limite": 1e999999` ou
  `"acrescimo_em_viagem_percentual": 1e999999`.
  - **Comportamento pela interpretação atual:**
    - (a) Indefinido. Se "casas decimais" for a forma escrita, `60.000` tem 3
  casas e é erro de arquivo. Se for o valor exato, que é a regra da seção 4 para
  a entrada, é 60 e passa. A RN-016 só herda da seção 4 as regras de "forma"
  (UTF-8, JSON, escapes), e não fica claro se herda também a regra do "valor
  exato".
    - (b) Válido pela RN-016, que não tem teto para taxa, limite ou percentual.
  Então 1,00 USD vira um `valor_considerado` com cerca de um milhão de dígitos.
  Isso contradiz a justificativa da AMB-018 ("o teto garante que todo valor
  aceito é calculado exatamente"), que agora só cobre o `valor` da entrada.
  - **Por que é um problema:**
    - (a) decide entre erro de arquivo e processamento normal para um arquivo
  gerado por ferramenta que grava `60.0` ou `60.000`.
    - (b) deixa o código sem regra para números gigantes que vêm da política ou
  do câmbio.
  - **Pergunta para decisão:**
    - (a) "Mais de 2 casas decimais" se mede pelo valor exato ou pela forma
  escrita?
    - (b) Taxa, limite e percentual têm algum teto ou forma restrita, ou fica
  registrado que a garantia de exatidão da AMB-018 não cobre os arquivos de
  política e câmbio (risco)?

  ### 5. Moeda autodeclarada multiplica o valor reembolsado — IMPORTANTE —
  brecha não registrada

  - **Regras afetadas:** RN-015, seção 10 (não há risco correspondente).
  - **Cenário de entrada:** tabela `padrao`, sem hospedagem.
    - Alimentação de 20,00 com nota em 14/07, mas lançada com `"moeda": "EUR"`.
  Vira 118,60, limite 60,00, e paga 60,00 em vez de 20,00.
    - Transporte de 50,00 com nota em 20/07, lançado como `"USD"`. Vira 275,00 e
  paga 80,00 em vez de 50,00.
  - **Comportamento pela interpretação atual:** a despesa é aceita normalmente.
  Nada na saída sinaliza o problema, exceto `moeda`, `taxa_cambio` e
  `valor_informado`.
  - **Por que é uma brecha:** o campo `moeda` é declarado pelo colaborador, como
  o `centro_custo` e o `tem_nota_fiscal`. Com dados válidos, ele multiplica o
  valor por cerca de 5 a 6 até o teto diário. A seção 10 registra como risco o
  centro de custo autodeclarado e o mesmo gasto lançado em duas moedas, mas não
  a moeda falsa num gasto único. A AMB-023 só discute a moeda como prova de
  viagem.
  - **Pergunta para decisão:** a moeda autodeclarada como multiplicador do valor
  é um risco aceito, a registrar na seção 10 com a justificativa, ou a spec
  deve tratá-la de outra forma?

  ### 6. Os "detalhes fixados na redação" do D-007 incluem decisões novas —
  IMPORTANTE — decisão escondida (pedido 5)

  - **Regras afetadas:** RN-016, AMB-029, AMB-019, seção 4.
  - **Avaliação de cada detalhe:**
    - **`cambio_indisponivel` com `valor_considerado` nulo e fora de
  `valor_solicitado`:** é consequência da decisão, porque sem taxa não existe
  valor em reais. Efeito colateral que vale confirmar: uma despesa fora do
  período **com** cotação entra em `valor_solicitado`; a mesma **sem** cotação
  não entra.
    - **Chave repetida na política e no câmbio = erro de arquivo:** é **decisão
  nova**. Ela inverte a AMB-019, em que a chave repetida não é defeito, mas uma
  correção (vale a última). "Qualquer defeito é erro de arquivo" (ponto 11) não
  resolve isso, porque a AMB-019 diz justamente que a chave repetida não é
  defeito.
    - **No máximo 2 casas decimais em limite e mínimo da nota:** é **decisão
  nova**. A alternativa seria aceitar e arredondar ou truncar. Ver também o item
  4(a).
    - **Normalização dos nomes de categoria do arquivo:** a normalização em si
  já vem da RN-006 ("também normalizadas"). A colisão de dois nomes como erro de
  arquivo é **decisão nova**.
    - **`versao` e `vigencia` obrigatórias:** é **decisão nova**, e há tensão
  com a AMB-029. A vigência "não muda o cálculo", mas a falta dela ou uma data
  inválida impede todo cálculo.
    - **Campos ignorados e tabela vazia válida:** consequência do padrão já
  usado na entrada.
    - **`itens[].moeda` como veio, se for texto:** consequência do padrão já
  usado para `id`, `data` e `categoria`.
  - **Decisões que não aparecem na lista do D-007:**
    - `moeda_base` obrigatória em BRL (ver o item 3);
    - `centros_custo` obrigatório: uma política só com `padrao` é erro de
  arquivo;
    - código de moeda do câmbio com exatamente 3 letras;
    - taxa > 0;
    - `periodicidade` diferente de `dia`/`diaria` como erro.
  - **Cenário que muda o resultado:** política v4 sem `"vigencia"`. Pela
  redação, dá erro de arquivo e não há saída. Se a vigência for só informativa,
  como diz a AMB-029, daria a saída normal com `vigencia` nula.
  - **Pergunta para decisão:** confirmar, um por um, os detalhes marcados como
  decisão nova, inclusive se a ausência de `vigencia` deve impedir a execução.
  Se forem confirmados, eles devem entrar como pontos próprios no D-007, não
  como "consequências"?

  ### 7. Saída de `centro_custo` e `tabela_aplicada` em casos de colisão — MENOR
  — contradição

  - **Regras afetadas:** seção 4 (entrada: "só com espaços → tabela padrão"),
  RN-014 (primeiro a igualdade exata, depois "qualquer outro caso"), seção 4
  (saída: `tabela_aplicada` "como escrito no arquivo, ou `padrao`").
  - **Cenário de entrada:**
    - (a) A política tem a chave `"  "` em `centros_custo`, e o colaborador
  declara `"centro_custo": "  "`.
    - (b) A política tem a chave `"padrao"` em `centros_custo`, e o colaborador
  declara `"centro_custo": "padrao"`.
    - (c) O colaborador declara `"centro_custo": ""`.
  - **Comportamento pela interpretação atual:**
    - (a) A seção 4 manda usar o `padrao`. A RN-014 manda usar a tabela `"  "`,
  porque há igualdade exata.
    - (b) A saída `tabela_aplicada: "padrao"` não diz se foi usada a tabela do
  topo ou a de `centros_custo`.
    - (c) Texto vazio não está listado: não é "só com espaços". Na prática cai
  no `padrao`, a menos que exista a chave `""`.
  - **Pergunta para decisão:** quando o centro de custo é vazio ou só espaços e
  existe uma chave igual no arquivo, vale a seção 4 ou a RN-014? E
  `tabela_aplicada` precisa distinguir o `padrao` do topo de uma chave
  `"padrao"` em `centros_custo`?

  ### 8. Casos da seção 7 sem os dados necessários para chegar ao esperado —
  MENOR — lacuna de aceite

  - **Regra afetada:** seção 7 ("Duplicata em moedas diferentes", "Duplicata em
  moeda estrangeira", "Moeda estrangeira não comprova viagem").
  - **Cenário de entrada:**
    - **"Duplicata em moedas diferentes" e "Duplicata em moeda estrangeira":**
  dizem "mesma data", mas não dão a data. Uma data fora de 13/07 a 28/07 (a
  partir de 31/07) faz as duas despesas saírem `cambio_indisponivel`. Aí o
  esperado "segunda `duplicata`" ou "as duas avaliadas" não acontece.
    - **"Moeda estrangeira não comprova viagem":** não dá a categoria dos 22,00
  EUR. Se for alimentação, os 130,46 consomem os 60,00 do dia, e a alimentação
  de 80,00 BRL sai `recusado` com 0. A linha só diz "limite 60,00".
  - **Pergunta para decisão:** completar data e categoria nesses casos, ou
  deixar a escolha para quem escreve o teste?

  ### 9. `categoria` de saída numa categoria com limite 0 — MENOR — ambiguidade

  - **Regras afetadas:** seção 4 (`itens[].categoria`: "normalizada se
  reconhecida na tabela aplicada"), RN-006, AMB-021.
  - **Cenário de entrada:** `CC-ENG-PLATAFORMA`, `"categoria": "Hospedagem"`,
  com nota.
  - **Comportamento pela interpretação atual:** indefinido.
    - Se uma categoria com limite 0 conta como "reconhecida" (está presente na
  tabela), a saída é `hospedagem`.
    - Se recebe o mesmo tratamento de uma categoria ausente (mesmo motivo
  `categoria_fora_da_politica`), a saída é `Hospedagem`.
    - Os valores não mudam. O campo é contratual.
  - **Pergunta para decisão:** uma categoria com limite 0 é "reconhecida" para
  fins de saída normalizada?

  ### 10. Textos desatualizados depois da v4 — MENOR — contradição de redação
  (pedido 6)

  - **AMB-010, decisão:** "mesma data, categoria, fornecedor e valor" omite a
  moeda, e "valor" agora é o valor na moeda original (RN-007, AMB-028).
  - **AMB-014, decisão:** "A saída mostra o número recebido e o arredondado
  (`valor_considerado`)". Para moeda estrangeira, `valor_considerado` é o valor
  convertido, não o recebido arredondado.
  - **AMB-018, justificativa:** "o teto garante que todo valor aceito é
  calculado exatamente" deixou de ser verdade com a taxa sem teto (ver o item
  4b).
  - **Seção 9, legenda:** "'—' = nulo: o item foi recusado antes do limite
  diário". Mas `data cotação` aparece "—" em itens BRL aprovados (e-008, e-010,
  f-001), por outro motivo (BRL).
  - **Nomes de categoria fixos:** RN-009, RN-010 e RN-012 ainda dependem dos
  nomes `alimentacao`, `transporte_urbano` e `hospedagem`. Isso foi decidido na
  AMB-022, e não reabro. Mas se o financeiro renomear uma categoria no arquivo
  ("muda sem aviso"), a ampliação ou a comprovação de viagem some sem nenhum
  sinal. Nenhum risco da seção 10 registra isso.
  - **Pergunta para decisão:** atualizar essas redações? E o acoplamento aos
  nomes fixos de categoria deve virar risco registrado?

  Não achei outro texto que ainda suponha limites fixos, só BRL ou três
  categorias. Os valores 60, 80, 250 e 100 que aparecem estão sempre marcados
  como "da v4" ou "do `padrao`".

  ---

  **Decidir antes da implementação:** 1, 2.

  **Pode ser decidido depois:** 3, 4, 5, 6 (importantes: convém decidir antes
  das tasks de leitura da política e do câmbio), 7, 8, 9, 10.

⏺ O spec-adversary terminou a revisão da spec 2.0: 10 problemas, sendo 2
  bloqueantes, 4 importantes e 4 menores.

  Contas: as três tabelas da seção 9 e os totais estão corretos, conferidos à
  mão. Nos 33 casos novos da seção 7 não há número errado, mas três deles não
  trazem dados suficientes para chegar ao esperado (achado 8).

  Os meus 4 detalhes da redação: ele confirma que alguns são decisões novas, não
  consequências, e por isso precisam de você:
  - chave repetida nos arquivos de política e câmbio como erro (isso inverte a
    lógica da AMB-019);
  - o máximo de 2 casas decimais;
  - erro quando dois nomes de categoria ficam iguais depois da normalização;
  - versao e vigencia obrigatórias.

  Ele também apontou outras escolhas de redação que entraram sem decisão:
  moeda_base obrigatória, centros_custo obrigatório e taxa maior que zero.
  Tratei como consequência o que era escolha, e vamos decidir cada uma.

  Seguindo uma por uma, começo pelas duas bloqueantes.

  Achado 1: hospedagem paga em moeda estrangeira comprova viagem?

  A RN-010 ficou com a frase "despesa em moeda estrangeira não comprova viagem".
  Tabela padrao: hospedagem de 50 EUR com nota em 22/07 e alimentação de 80,00
  BRL em 23/07.
  - (a) Comprova (minha recomendação). O que comprova viagem é ser hospedagem
    com nota; a moeda é irrelevante. 22/07 e 23/07 ficam em viagem, e a
    alimentação tem limite 90, aprovado com 80.
    - Era o que a decisão 9 queria: a moeda sozinha não prova viagem, mas também
      não tira a prova da hospedagem.
    - Hotel no exterior é justamente o caso típico da v4.
  - (b) Não comprova. Leitura literal da frase atual. Um hotel em Lisboa com
    nota deixaria de ampliar os limites, enquanto um hotel no Brasil amplia.

  Achado 2: data sem a moeda específica

  O arquivo é organizado por data, e cada data lista as moedas cotadas. Pode
  existir uma data que tem USD mas não EUR. Exemplo: o câmbio tem 13/07 (USD e
  EUR) e 14/07 (só USD); a despesa é de 20 EUR em 15/07.
  - (a) A data mais próxima com cotação daquela moeda, até D-3 (minha 
    recomendação). Usa 13/07: 20 × 5,91 = 118,20.
    - É o que "cotação da moeda" significa; a ausência do EUR em 14/07 é só
      falta de publicação daquela moeda.
  - (b) A data mais próxima presente no arquivo. Para em 14/07, que não tem EUR,
    e a despesa sai cambio_indisponivel.

⏺ User answered Claude's questions:
  ⎿  · Achado 1: hospedagem com nota paga em moeda estrangeira comprova viagem? 
     → Comprova (Recomendado)
     · Achado 2: a busca D-1 a D-3 procura o quê? → Data com cotação da moeda 
     (Recomendado)

⏺ Agent "Adversarial review of spec 2.0" finished · 4m 22s

  Read 1 file (ctrl+o to expand)

⏺ Registrei os achados 1 e 2: hospedagem com nota comprova viagem em qualquer
  moeda, e a busca de D-1 a D-3 procura a data mais próxima com cotação daquela
  moeda.

  Achado 6 (com o 3 e o 4a): detalhes dos arquivos de política e câmbio

  Parte do que o adversário chamou de decisão escondida você já decidiu na
  decisão 11. A pergunta listava como defeito, e você escolheu erro de arquivo
  para: limite com 3 casas, taxa ≤ 0, periodicidade desconhecida e ausência de
  padrao. Ele não viu o texto da pergunta. Essas ficam como estão.

  Restam quatro escolhas que foram mesmo minhas:

  a) Chave repetida no arquivo de política ou câmbio. Exemplo: "alimentacao"
  duas vezes na tabela do CC-COMERCIAL.
  - Erro de arquivo (minha recomendação). Na entrada, a chave repetida é tratada
    como correção do colaborador, e o aviso aparece no item. Na política, uma
    repetição muda os limites de todos, e o financeiro não vê o aviso, porque
    ele vai para a saída do reembolso. Melhor parar.
  - Vale a última, com aviso no topo da saída, como a RN-013 faz para a entrada.
    Mais tolerante, mas o limite muda em silêncio para quem mantém a tabela.

  b) versao e vigencia ausentes. Nenhuma das duas muda o cálculo.
  - Opcionais (minha recomendação, mudando a redação atual): ausentes saem nulas
    na saída. Se presentes, precisam ser texto (versao) e data válida
    (vigencia); fora disso, erro. Isso mantém a coerência com a AMB-029: um
    campo que não muda o cálculo não deve impedir o cálculo.
  - Obrigatórias: como está escrito. Garante o registro da política na saída,
    mas bloqueia tudo por um rótulo.

  c) moeda_base e centros_custo ausentes.
  - moeda_base opcional; se presente, precisa ser "BRL" (minha recomendação). O
    que importa é não ser outra moeda: ausente, vale BRL, como diz o comunicado
    ("os limites são sempre em BRL").
  - centros_custo opcional; ausente = nenhum centro de custo (minha 
    recomendação). Todos usam o padrao; uma política só com o padrão é válida.
  - Alternativa: os dois obrigatórios, como está escrito hoje.

  d) "Mais de 2 casas decimais": pelo valor ou pela forma escrita? Exemplo:
  60.000 ou 6E1.
  - Pelo valor (minha recomendação). 60.000 é 60,00 e passa; 60.005 falha. É a
    mesma regra da seção 4: o número vale pelo seu valor exato, não pela forma
    (72.50 = 72.5). Uma ferramenta que grava 60.000 não deve quebrar a execução.

⏺ User answered Claude's questions:
  ⎿  · 6a: chave repetida no arquivo de política ou câmbio? → Erro de arquivo 
     (Recomendado)
     · 6b: versao e vigencia ausentes na política? → Opcionais, nulas 
     (Recomendado)
     · 6c/3: moeda_base e centros_custo ausentes? → Opcionais (Recomendado)
     · 4a: "mais de 2 casas decimais" em limite e mínimo da nota se mede como? →
     Pelo valor (Recomendado)

  Read 1 file (ctrl+o to expand)

⏺ Registrei 6a (chave repetida = erro), 6b (versao e vigencia opcionais), 6c
  (moeda_base e centros_custo opcionais) e 4a (casas decimais medidas pelo
  valor).

  As últimas escolhas importantes

  6d. Dois nomes de categoria iguais depois da normalização (por exemplo,
  "Alimentação" e "alimentacao" na mesma tabela).
  - Erro de arquivo (minha recomendação). Não há como saber qual dos dois
    limites o financeiro quis. É o mesmo raciocínio da chave repetida (6a).
  - Alternativa: comparar os nomes do arquivo sem normalizar, só a despesa
    normalizada. Aí "Alimentação" no arquivo nunca casaria com nada, porque a
    despesa normalizada vira alimentacao.

  6e. Código de moeda no arquivo de câmbio fora do formato ("usd", "US$").
  - Erro de arquivo (minha recomendação). É o mesmo formato exigido na despesa
    (3 letras maiúsculas); um código inválido no arquivo é defeito do arquivo.
  - Alternativa: ignorar essa entrada em silêncio. As despesas naquela moeda
    sairiam cambio_indisponivel, sem pista do motivo.

  4b. Números gigantes no arquivo de política ou câmbio (taxa 1e999999, limite
  1e999999).
  - Aplicar o mesmo teto da AMB-018 (minha recomendação): limite, mínimo da
    nota, percentual e taxa com valor absoluto a partir de 1.000.000.000 → erro
    de arquivo. Mantém a garantia de cálculo exato que hoje só vale para o valor
    da entrada. Nenhuma política ou taxa real chega perto.
  - Registrar como risco e não limitar.

  5. Moeda autodeclarada como multiplicador. O colaborador lança um almoço de
  20,00 reais com "moeda": "EUR", que vira 118,60, e recebe 60,00 em vez de
  20,00 (até o limite do dia).
  - Risco aceito, registrado na seção 10 (minha recomendação). É o mesmo caso do
    centro de custo e da nota fiscal: o sistema confia no que vem na entrada, e
    a saída expõe moeda, taxa_cambio e valor_informado para a conferência
    humana, que compara com a nota.
  - Não há alternativa viável na spec: detectar moeda falsa exigiria ler a
    descrição ou o fornecedor (fora de escopo).

⏺ User answered Claude's questions:
  ⎿  · 6d: dois nomes de categoria que ficam iguais após normalização na mesma 
     tabela? → Erro de arquivo (Recomendado)
     · 6e: código de moeda fora do formato no arquivo de câmbio ("usd", "US$")? 
     → Erro de arquivo (Recomendado)
     · 4b: números gigantes no arquivo de política ou câmbio? → Teto de 1 bilhão
     (Recomendado)
     · 5: moeda autodeclarada usada para multiplicar o valor? → Risco aceito 
     (Recomendado)

  Read 1 file (ctrl+o to expand)

⏺ Registrei as decisões para os itens 7 a 10: centro de custo vazio cai no
  padrão sem checar a tabela, os casos incompletos da seção 7 serão completados,
  categoria com limite 0 ainda sai normalizada, e vou atualizar os textos
  desatualizados além de registrar o risco de reconhecimento por nome das
  categorias.

⏺ User answered Claude's questions:
  ⎿  · 7: centro de custo vazio e chave "padrao" em centros_custo? → Vazio = 
     padrão; chave reservada (Recomendado)
     · 8: completar os 3 casos da seção 7 sem dados (datas das duplicatas, 
     categoria do caso de viagem)? → Completar (Recomendado)
     · 9: categoria com limite 0 sai normalizada na saída? → Sim, reconhecida 
     (Recomendado)
     · 10: reescrever AMB-010/014/018 e legenda da seção 9, e registrar o risco 
     das categorias reconhecidas pelo nome? → Reescrever + risco (Recomendado)

⏺ Todas as 10 decididas. Agora aplico a rodada 2 na spec.

⏺ Bash(python3 - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)
  ⎿  Updated specs/001-motor-reembolso/spec.md (+21 -16)
      54  |---|---|---|---|
      55  | `colaborador.id` | texto | identificador do colaborador | sim
           (erro de arquivo) |
      56  | `colaborador.nome` | texto | nome | sim (erro de arquivo) |
      57 -| `colaborador.centro_custo` | texto ou nulo | centro de custo;
         - escolhe a tabela de limites (RN-014) | não; ausente, nulo ou t
         -exto só com espaços em branco → tabela padrão; qualquer outro t
         -ipo → erro de arquivo |                                        
      57 +| `colaborador.centro_custo` | texto ou nulo | centro de custo;
         + escolhe a tabela de limites (RN-014) | não; ausente, nulo, tex
         +to vazio ou só com espaços em branco → tabela padrão; qualquer 
         +outro tipo → erro de arquivo |                                 
      58  | `periodo.competencia` | texto `AAAA-MM` | rótulo do mês de co
          mpetência; repetido na saída, não usado em cálculo | não |
      59  | `periodo.inicio` | data `AAAA-MM-DD` | primeiro dia do períod
          o (inclusive) | sim (erro de arquivo) |
      60  | `periodo.fim` | data `AAAA-MM-DD` | último dia do período (in
          clusive) | sim (erro de arquivo) |
     ...
      88  | `itens` | lista | um item por elemento de `despesas`, **na me
          sma ordem** |
      89  | `itens[].id` | texto ou nulo | id da despesa como veio, se fo
          r texto; nulo se ausente, se não for texto ou se o elemento não
           é um objeto |
      90  | `itens[].data` | texto ou nulo | data da despesa como veio, s
          e for texto; nulo se ausente, se não for texto ou se o elemento
           não é um objeto |
      91 -| `itens[].categoria` | texto ou nulo | categoria normalizada (
         -RN-006) se reconhecida na tabela aplicada, qualquer que seja o 
         -status ou o motivo do item (inclusive `entrada_invalida`); senã
         -o, como veio, se for texto; nulo se ausente ou não for texto | 
      91 +| `itens[].categoria` | texto ou nulo | categoria normalizada (
         +RN-006) se presente na tabela aplicada (inclusive com limite 0)
         +, qualquer que seja o status ou o motivo do item (inclusive `en
         +trada_invalida`); senão, como veio, se for texto; nulo se ausen
         +te ou não for texto |                                          
      92  | `itens[].valor_informado` | número ou nulo | o número recebid
          o em `valor`, **na moeda da despesa**, sem arredondamento nem c
          onversão; nulo se ausente ou não numérico |
      93  | `itens[].moeda` | texto ou nulo | `BRL` se `moeda` ausente ou
           nula; como veio, se for texto (mesmo fora do formato); nulo se
           não for texto nem nula, ou se o elemento não é um objeto |
      94  | `itens[].taxa_cambio` | número ou nulo | taxa usada na conver
          são (RN-015): 1 para `BRL`; o número do arquivo de câmbio para 
          as demais; **nula se a despesa foi recusada por `entrada_invali
          da` ou `cambio_indisponivel`** |
     ...
      239  
      240  ### RN-010 — Colaborador em viagem
      241  
      242 -**Regra:** uma despesa de `hospedagem` **comprova viagem** qua
          -ndo tem `tem_nota_fiscal` verdadeiro e passou pelas etapas 1 a
          - 7 da seção 8. Uma hospedagem que comprova viagem na data D co
          -loca em viagem as datas **D e D+1** (a noite da diária e o dia
          - seguinte). Em datas em viagem, os limites de `alimentacao` e 
          -`transporte_urbano` são ampliados pelo percentual da política 
          -(RN-009). A condição de viagem vale para todas as despesas da 
          -data, independentemente da ordem em que aparecem na entrada. H
          -ospedagem recusada por `categoria_fora_da_politica` (inclusive
          - por limite 0, AMB-021) não comprova viagem. Despesa em moeda 
          -estrangeira não comprova viagem (AMB-023).                    
      242 +**Regra:** uma despesa de `hospedagem` **comprova viagem** qua
          +ndo tem `tem_nota_fiscal` verdadeiro e passou pelas etapas 1 a
          + 7 da seção 8. Uma hospedagem que comprova viagem na data D co
          +loca em viagem as datas **D e D+1** (a noite da diária e o dia
          + seguinte). Em datas em viagem, os limites de `alimentacao` e 
          +`transporte_urbano` são ampliados pelo percentual da política 
          +(RN-009). A condição de viagem vale para todas as despesas da 
          +data, independentemente da ordem em que aparecem na entrada. H
          +ospedagem recusada por `categoria_fora_da_politica` (inclusive
          + por limite 0, AMB-021) não comprova viagem. A moeda não impor
          +ta para a comprovação: uma hospedagem com nota em moeda estran
          +geira comprova viagem como qualquer outra, e nenhuma outra des
          +pesa comprova viagem por estar em moeda estrangeira (AMB-023).
      243  **Origem:** política do RH, item 6; AMB-004; AMB-021 e AMB-023
            (D-007).
      244  **Aceite** (tabela `padrao` da v4): hospedagem com nota em 14/
           07 → 14/07 e 15/07 em viagem; alimentação de 80,00 em 15/07 → 
           limite 90,00, `aprovado` com 80,00; alimentação de 80,00 em 16
           /07 → limite 60,00, `parcial` com 60,00. Hospedagem de 80,00 *
           *sem** nota em 03/07 → reembolsada pelas regras normais, mas 0
           3/07 e 04/07 **não** ficam em viagem. Hospedagem com nota em 3
           0/06, fora de um período que começa em 01/07 → recusada por `f
           ora_do_periodo`, e 01/07 não fica em viagem. `CC-ENG-PLATAFORM
           A`: hospedagem com nota em 14/07 → `categoria_fora_da_politica
           `; alimentação de 100,00 com nota em 15/07 → limite 75,00, `pa
           rcial` com 75,00. Alimentação de 22,00 EUR com nota em 14/07, 
           sem hospedagem → 14/07 não fica em viagem.
      245  
     ...
      277  ### RN-014 — Tabela aplicada por centro de custo
      278  
      279  **Regra:** cada execução aplica **uma** tabela de limites a to
           das as despesas, escolhida pelo `colaborador.centro_custo`:
      280 -- se o texto de `centro_custo` é **igual, caractere a caracter
          -e**, a uma chave de `centros_custo` do arquivo de política, ap
          -lica-se a tabela desse centro de custo. A comparação é exata: 
          -sem normalização, sem ignorar maiúsculas nem espaços (`"cc-adm
          -"` e `"CC-ADM "` não são `CC-ADM`);                           
      281 -- em qualquer outro caso — centro de custo ausente da tabela, 
          -`centro_custo` ausente, nulo ou só com espaços em branco — apl
          -ica-se a tabela `padrao` do arquivo de política.              
      280 +- se o texto de `centro_custo` (informado, ver abaixo) é **igu
          +al, caractere a caractere**, a uma chave de `centros_custo` do
          + arquivo de política, aplica-se a tabela desse centro de custo
          +. A comparação é exata: sem normalização, sem ignorar maiúscul
          +as nem espaços (`"cc-adm"` e `"CC-ADM "` não são `CC-ADM`);   
      281 +- `centro_custo` ausente, nulo, vazio ou só com espaços em bra
          +nco é "não informado": aplica-se a tabela `padrao`, sem consul
          +tar `centros_custo`;                                          
      282 +- centro de custo informado que não é chave de `centros_custo`
          + (ou arquivo sem `centros_custo`) → tabela `padrao`.          
      283  
      284  A tabela aplicada é **fechada**: suas categorias são as únicas
            reconhecidas (RN-006), seus limites são os únicos usados (RN-
           009). Uma categoria que falta na tabela de um centro de custo 
           **não** é completada pelo `padrao`. A saída informa a tabela a
           plicada em `politica.tabela_aplicada` (seção 4).
      285  **Origem:** Política v4, item A ("aplica-se a política padrão"
           ); AMB-020 (D-007).
     ...
      290  **Regra:**
      291  - A moeda da despesa é o campo `moeda`; ausente ou nulo vale `
           BRL`. Formato inválido é `entrada_invalida` (RN-002).
      292  - `BRL` tem taxa 1, sem consultar o arquivo de câmbio (uma ent
           rada `BRL` no arquivo é ignorada).
      292 -- Para outra moeda, a taxa é a do arquivo de câmbio para essa 
          -moeda **na data da despesa**. Se essa data não tem cotação par
          -a a moeda, usa-se a cotação da data anterior mais próxima **at
          -é 3 dias corridos antes** (D-1, D-2 ou D-3): um sábado ou domi
          -ngo usa a sexta-feira; uma segunda-feira de feriado usa a sext
          -a-feira. Sem cotação de D a D-3 → `recusado`, motivo `cambio_i
          -ndisponivel`. Cotação posterior à data da despesa nunca é usad
          -a.                                                            
      293 +- Para outra moeda, a taxa é a do arquivo de câmbio para essa 
          +moeda **na data da despesa**. Se essa data não tem cotação par
          +a a moeda, usa-se a cotação **dessa moeda** na data anterior m
          +ais próxima que a tenha, **até 3 dias corridos antes** (D-1, D
          +-2 ou D-3); uma data intermediária que só cota outras moedas é
          + ignorada: um sábado ou domingo usa a sexta-feira; uma segunda
          +-feira de feriado usa a sexta-feira. Sem cotação de D a D-3 → 
          +`recusado`, motivo `cambio_indisponivel`. Cotação posterior à 
          +data da despesa nunca é usada.                                
     … 72 more lines (ctrl+o to expand)

⏺ Bash(python3 - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)
  ⎿  57:| `colaborador.centro_custo` | texto ou nulo | centro de custo; esc
     olhe a tabela de limites (RN-014) | não; ausente, nulo, texto vazio ou
      só com espaços em branco → tabela padrão; qualquer outro tipo → erro
     … +13 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/spec.md (+14 -9)
      84  |---|---|---|
      85  | `colaborador` | objeto | `id` e `nome`, copiados da entrada; 
          `centro_custo` copiado se for texto (inclusive só com espaços),
           nulo se ausente ou nulo |
      86  | `periodo` | objeto | `inicio` e `fim`, copiados da entrada; `
          competencia` copiada se for texto (em qualquer formato), nula s
          e ausente ou não for texto |
      87 -| `politica` | objeto | `versao` e `vigencia`, copiadas do arqu
         -ivo de política; `tabela_aplicada`: o centro de custo cuja tabe
         -la foi usada, como escrito no arquivo de política, ou `padrao` 
         -(RN-014) |                                                     
      87 +| `politica` | objeto | `versao` e `vigencia`, copiadas do arqu
         +ivo de política (nulas se ausentes); `tabela_aplicada`: o centr
         +o de custo cuja tabela foi usada, como escrito no arquivo de po
         +lítica, ou `padrao` (RN-014) |                                 
      88  | `itens` | lista | um item por elemento de `despesas`, **na me
          sma ordem** |
      89  | `itens[].id` | texto ou nulo | id da despesa como veio, se fo
          r texto; nulo se ausente, se não for texto ou se o elemento não
           é um objeto |
      90  | `itens[].data` | texto ou nulo | data da despesa como veio, s
          e for texto; nulo se ausente, se não for texto ou se o elemento
           não é um objeto |
     ...
      307  - chave repetida em qualquer objeto (a RN-013 vale só para o a
           rquivo de entrada);
      308  - **política:**
      309    - raiz que não é objeto;
      310 -  - `versao` ausente ou que não é texto não vazio;            
      311 -  - `vigencia` ausente ou que não é data válida `AAAA-MM-DD`; 
      312 -  - `moeda_base` diferente de `"BRL"`;                        
      310 +  - `versao` presente que não é texto não vazio (ausente é vál
          +ida: sai nula);                                               
      311 +  - `vigencia` presente que não é data válida `AAAA-MM-DD` (au
          +sente é válida: sai nula);                                    
      312 +  - `moeda_base` presente e diferente de `"BRL"` (ausente vale
          + `BRL`);                                                      
      313    - `padrao` ausente ou que não é tabela;
      314 -  - `centros_custo` ausente ou que não é objeto cujos valores 
          -são tabelas;                                                  
      314 +  - `centros_custo` presente que não é objeto cujos valores sã
          +o tabelas (ausente: nenhum centro de custo, todos usam o `padr
          +ao`); chave de `centros_custo` igual a `"padrao"`, vazia ou só
          + com espaços em branco (nome reservado ou "não informado", RN-
          +014);                                                         
      315    - `nota_fiscal_obrigatoria_acima_de` ausente, que não é núme
           ro, negativo ou com mais de 2 casas decimais;
      316    - `acrescimo_em_viagem_percentual` ausente, que não é número
            ou negativo;
      317  - **tabela** (o `padrao` e cada valor de `centros_custo`): obj
           eto de categoria → regra. É erro de arquivo:
     ...
      322    - `periodicidade` ausente ou diferente de `"dia"` e `"diaria
           "`, que significam a mesma coisa: limite por data;
      323  - **câmbio:**
      324    - raiz que não é objeto;
      325 -  - `moeda_base` diferente de `"BRL"`;                        
      325 +  - `moeda_base` presente e diferente de `"BRL"` (ausente vale
          + `BRL`);                                                      
      326    - `taxas` ausente ou que não é objeto;
      327    - chave de `taxas` que não é data válida `AAAA-MM-DD`;
      328    - valor de `taxas` que não é objeto;
      329    - código de moeda que não tem exatamente 3 letras maiúsculas
            de `A` a `Z`;
      330    - taxa que não é número ou que é menor ou igual a zero.
      331 +- **qualquer número dos dois arquivos** (limite, mínimo da not
          +a, percentual, taxa) com valor absoluto a partir de 1.000.000.
          +000 — o mesmo teto da AMB-018.                                
      332  
      332 -Campos não listados (`observacao`, `fonte` e outros) são ignor
          -ados. Uma tabela vazia é válida: nenhuma categoria é reconheci
          -da para quem a usa. `vigencia` não muda o cálculo: é copiada p
          -ara a saída (AMB-029).                                        
      333 +"Casas decimais" e o teto se medem pelo **valor exato** do núm
          +ero, como na seção 4, não pela forma escrita: `60.000` e `6E1`
          + são 60,00 e valem; `60.005` tem 3 casas e é erro de arquivo. 
      334 +                                                              
      335 +Campos não listados (`observacao`, `fonte` e outros) são ignor
          +ados. Uma tabela vazia é válida: nenhuma categoria é reconheci
          +da para quem a usa. `versao` e `vigencia` não mudam o cálculo:
          + são copiadas para a saída, nulas se ausentes (AMB-029).      
      336  **Origem:** Política v4, itens A e B; AMB-029, AMB-031 (D-007)
           .
     … 18 more lines (ctrl+o to expand)

⏺ A spec está atualizada. Agora o D-007 recebe a rodada 2 no lugar da lista "a
  confirmar".

⏺ Bash(python3 - <<'EOF'
      import re…)
  ⎿  100
      specs/001-motor-reembolso/DECISIONS.md |  89 +++++++
      specs/001-motor-reembolso/spec.md      | 436 ++++++++++++++++++++++++
     … +2 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/DECISIONS.md (+24 -11)
      25  - **Limite 0 (ponto 2).** A recomendação inicial ("categoria ve
          dada, mas comprova viagem") era incoerente com a seção 8. A rev
          isão expôs o erro, e a decisão ficou "categoria vedada, não com
          prova viagem".
      26  - **Limite ampliado (ponto 10c).** O responsável perguntou se a
          rredondar o limite poderia interagir com a nota fiscal. Não pod
          e: a nota compara o valor da despesa, antes do limite, na AMB-0
          08. Mesmo assim, o responsável escolheu truncar, pelo argumento
           de que o limite é um teto.
      27  
      28 -A recomendação para a vigência (ponto 15) mudou de "recusar" pa
         -ra "informativa" depois que o ponto 11 tornou a política um arg
         -umento explícito. Sessão `docs/sessions/36-*`, continuada na `3
         -7-*`.                                                          
      28 +A recomendação para a vigência (ponto 15) mudou de "recusar" pa
         +ra "informativa" depois que o ponto 11 tornou a política um arg
         +umento explícito. Sessão `docs/sessions/37-*`.                 
      29  
      30  **O que mudou na spec** (numeração dos pontos = numeração da re
          visão adversarial):
      31  
     ...
      49  | 16 | Item C (aprovação manual) | — | não implementado; com a 
          v4, nunca dispara por item (máximo de 400,00) | seção 3, AMB-03
          0 |
      50  | 17 | Textos que a v4 contradiz | "não converte moedas", "sem 
          representação", "100,00 fixo", riscos com valores fixos | reesc
          ritos: seção 3, AMB-006, AMB-007, AMB-015, AMB-017, riscos de f
          racionamento e hospedagem irrisória sem valores fixos; 5 riscos
           novos | seções 3, 6, 10 |
      51  
      52 -**Detalhes fixados na redação** (consequências das decisões aci
         -ma, a confirmar na próxima rodada do `spec-adversary`):        
      53 -- A despesa recusada por `cambio_indisponivel` tem `valor_consi
         -derado` nulo e fica fora de `valor_solicitado`, como `entrada_i
         -nvalida`. Sem cotação, não existe valor em reais.              
      54 -- Arquivos de política e câmbio:                               
      55 -  - chave repetida é erro de arquivo (a RN-013 vale só para a e
         -ntrada);                                                       
      56 -  - limites e mínimo da nota com no máximo 2 casas decimais;   
      57 -  - nomes de categoria do arquivo normalizados pela seção 5; do
         -is nomes iguais depois da normalização são erro de arquivo;    
      58 -  - `versao` texto não vazio e `vigencia` data válida obrigatór
         -ias;                                                           
      59 -  - campos não listados são ignorados; tabela vazia é válida.  
      60 -- `itens[].moeda` sai como veio quando é texto, mesmo fora do f
         -ormato (`eur`), e nula quando tem outro tipo.                  
      52 +**Segunda rodada do `spec-adversary` (sobre a redação da 2.0):*
         +* 10 problemas, sendo 2 bloqueantes, 4 importantes e 4 menores.
         + As três tabelas da seção 9 e os casos novos da seção 7 confere
         +m à mão.                                                       
      53 +                                                               
      54 +A rodada mostrou que parte dos "detalhes fixados na redação" er
         +am decisões novas, não consequências das 17. Alguns já tinham s
         +ido decididos no ponto 11, cuja pergunta listava como defeito l
         +imite com 3 casas, taxa ≤ 0, periodicidade desconhecida e falta
         + de `padrao`. Os demais o responsável decidiu um a um:         
      55 +                                                               
      56 +| # | Ponto | Decisão | Onde |                                 
      57 +|---|---|---|---|                                              
      58 +| R2-1 | Hospedagem paga em moeda estrangeira comprova viagem? 
         +(**bloqueante**) | sim, como qualquer hospedagem com nota; a mo
         +eda, sozinha, nunca comprova | RN-010, RN-015, AMB-023, seção 7
         + |                                                             
      59 +| R2-2 | Busca D-1 a D-3 quando a data intermediária não cota a
         + moeda (**bloqueante**) | procura a data mais próxima com cotaç
         +ão **daquela moeda** | RN-015, AMB-024, seção 7 |              
      60 +| R2-3 / R2-6c | `moeda_base` e `centros_custo` ausentes | opci
         +onais: `moeda_base` ausente vale BRL (presente e diferente de B
         +RL é erro); sem `centros_custo`, todos usam o `padrao` | RN-016
         + |                                                             
      61 +| R2-4a | "Mais de 2 casas decimais": pela forma ou pelo valor 
         +| pelo valor exato (`60.000` vale) | RN-016 |                  
      62 +| R2-4b | Números gigantes na política ou no câmbio | mesmo tet
         +o de 1 bilhão da AMB-018 → erro de arquivo | RN-016, AMB-018 | 
      63 +| R2-5 | Moeda autodeclarada como multiplicador do valor | risc
         +o aceito | seção 10 |                                          
      64 +| R2-6a | Chave repetida na política ou no câmbio | erro de arq
         +uivo (a RN-013 vale só para a entrada) | RN-016 |              
      65 +| R2-6b | `versao` e `vigencia` ausentes | opcionais, saem nula
         +s; presentes com tipo ou formato errado → erro | seção 4, RN-01
         +6, AMB-029 |                                                   
      66 +| R2-6d | Dois nomes de categoria iguais depois da normalização
         + | erro de arquivo | RN-016 |                                  
      67 +| R2-6e | Código de moeda fora do formato no câmbio | erro de a
         +rquivo | RN-016 |                                              
      68 +| R2-7 | `centro_custo` vazio; chave `"padrao"` em `centros_cus
         +to` | vazio ou só espaços → `padrao`, sem consultar `centros_cu
         +sto`; chave `"padrao"`, vazia ou só espaços em `centros_custo` 
         +→ erro de arquivo | seção 4, RN-014, RN-016 |                  
      69 +| R2-8 | Casos da seção 7 sem data ou sem categoria | completad
         +os (duplicatas em 14/07; transporte em EUR no caso de viagem); 
         +4 casos novos | seção 7 |                                      
      70 +| R2-9 | Categoria com limite 0 sai normalizada? | sim, está na
         + tabela aplicada | seção 4 |                                   
      71 +| R2-10 | Textos desatualizados | AMB-010, AMB-014, AMB-018 e l
         +egenda da seção 9 reescritos; risco novo: categorias reconhecid
         +as pelo nome | seções 6, 9, 10 |                               
     … 13 more lines (ctrl+o to expand)

⏺ As 10 decisões da segunda rodada estão aplicadas na spec e no D-007; nada foi
  commitado.

  O que mudou na spec:
  - Hospedagem em moeda estrangeira comprova viagem como qualquer hospedagem com
    nota (RN-010, RN-015, AMB-023).
  - A busca de D-1 a D-3 procura a data mais próxima que tem cotação daquela
    moeda (RN-015, AMB-024).
  - RN-016 (arquivos de política e câmbio):
    - versao, vigencia, moeda_base e centros_custo passam a ser opcionais;
    - as casas decimais são medidas pelo valor (60.000 vale);
    - teto de 1 bilhão para limites, mínimo da nota, percentual e taxa;
    - chave repetida, colisão de nomes de categoria e código de moeda inválido
      são erro de arquivo;
    - "padrao" é nome reservado em centros_custo.
  - Centro de custo vazio ou só com espaços usa o padrao, sem consultar
    centros_custo (seção 4, RN-014).
  - Seção 7: os três casos incompletos foram corrigidos e entraram quatro novos
    (hospedagem em EUR, data intermediária sem a moeda, chave "padrao"
    reservada, política sem versão nem vigência). Agora são 100 casos: 63
    anteriores e 37 novos.
  - Redação e riscos:
    - AMB-010, AMB-014, AMB-018 e a legenda da seção 9 foram reescritas;
    - dois riscos novos na seção 10: moeda autodeclarada como multiplicador e
      categorias reconhecidas pelo nome.
  - D-007: a lista "a confirmar" virou a tabela da segunda rodada (R2-1 a
    R2-10). Ela diz quais pontos você já tinha decidido na decisão 11 e quais
    decidiu agora.

  As tabelas da seção 9 não mudaram, e o adversário confirmou as contas.

  Próximo passo sugerido: uma rodada curta de confirmação do spec-adversary, só
  sobre as mudanças da segunda rodada, antes do commit. Nas revisões anteriores
  (D-005, D-006), a confirmação final achou problemas na redação nova. Quer que
  eu rode, ou prefere fazer o export e commitar a spec agora?

✻ Baked for 13m 6s · done 9:17 PM

❯ roda a confirmação do spec-adversary                                          

⏺ spec-adversary(Confirmation review of spec 2.0)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ A rodada de confirmação do spec-adversary está rodando. Ela não reabre nada já
  decidido. O que pedi:
  - conferir se as decisões R2-1 a R2-10 foram aplicadas em todos os lugares que
    afetam;
  - apontar contradição ou brecha que a redação nova tenha criado;
  - refazer à mão as contas dos 7 casos da seção 7 que foram criados ou
    corrigidos nesta rodada.

  Te aviso quando terminar.
✻ Cooked for 11s · done 9:18 PM

❯ ok, me avisa quando terminar                                                  

⏺ Combinado, te aviso quando ela terminar. Se não houver nada bloqueante, sigo
  direto para o export e o commit da spec.

✻ Brewed for 1s · done 9:19 PM

› Message from spec-adversary
  Resumo: 3 problemas, nenhum BLOQUEANTE e nenhum IMPORTANTE. Os três são
  MENORES.

  As decisões R2-1 a R2-10 estão aplicadas na spec 2.0 de forma completa e
  coerente. Não sobrou texto antigo que as contradiga. Também conferi à mão os
  números dos casos novos e dos corrigidos, e todos batem.

  ## 1. Conferência das decisões R2-1 a R2-10

  | # | Onde a decisão aparece | Situação |
  |---|---|---|
  | R2-1 | RN-010, RN-015 (último item), AMB-023, seção 3 (linha 36), seção 7
  (linha 692), seção 8 (consequências) | ok |
  | R2-2 | RN-015 ("dessa moeda", "data intermediária que só cota outras moedas
  é ignorada"), AMB-024, seção 7 (linha 693); a tabela de motivos da seção 4
  continua compatível | ok |
  | R2-3 / R2-6c | RN-016 (`moeda_base` e `centros_custo`), RN-014 ("ou arquivo
  sem `centros_custo`"), aceite da RN-016 | ok |
  | R2-4a | RN-016: "valor exato", `60.000` e `6E1` valem, `60.005` é erro | ok
  |
  | R2-4b | RN-016 (teto de 1 bilhão), justificativa da AMB-018 | ok (ver achado
  2) |
  | R2-5 | risco "Moeda autodeclarada como multiplicador" na seção 10 | ok |
  | R2-6a | RN-016 ("a RN-013 vale só para o arquivo de entrada"), seção 7
  (linha 700) | ok |
  | R2-6b | seção 4 (saída `politica`), RN-016, AMB-029, seção 7 (linha 695) |
  ok (ver achado 3) |
  | R2-6d, R2-6e | RN-016 | ok |
  | R2-7 | seção 4 (entrada e saída de `centro_custo`), RN-014, RN-016, seção 7
  (linhas 669 e 694) | ok. A AMB-020 diz "ausente, nulo ou só com espaços" e
  omite "vazio", mas a RN-014 cobre o vazio. Não é contradição. |
  | R2-8 | casos de duplicata em 14/07 e transporte em EUR | ok. Um caso novo
  repete o defeito que a R2-8 corrigiu (achado 1). |
  | R2-9 | `itens[].categoria` na seção 4: "inclusive com limite 0" | ok |
  | R2-10 | AMB-010 (moeda), AMB-014, AMB-018, legenda da seção 9, risco
  "Categorias reconhecidas pelo nome" | ok |

  ## 2. Números conferidos à mão (câmbio de `exemplos/envelope/cambio.json`)

  **Casos novos**
  - **Hospedagem em moeda estrangeira:** 50,00 × 5,95 (EUR em 22/07) = 297,50.
  Passa do mínimo, mas tem nota. Limite do `padrao` 250,00 → `parcial` com
  250,00. Ficam em viagem 22/07 e 23/07. A alimentação de 80,00 em 23/07 tem
  limite 90,00 → `aprovado` com 80,00. Confere.
  - **Data intermediária sem a moeda:** em 14/07 não há EUR. Usa 13/07 (D-2):
  20,00 × 5,91 = 118,20, `data_cotacao` 2026-07-13. Confere, com a ressalva do
  achado 1.
  - **Centro de custo reservado** e **Política sem versão nem vigência:**
  coerentes com a RN-016 e com a saída da seção 4.

  **Casos corrigidos**
  - **Duplicata em moedas diferentes:** 22 EUR × 5,93 = 130,46 e 22 USD × 5,44 =
  119,68. Moedas diferentes, então não são duplicatas e as duas são avaliadas.
  Confere.
  - **Duplicata em moeda estrangeira:** 22,001 e 22,00, arredondados em EUR, dão
  22,00 nos dois → a segunda é `duplicata`. Em reais seriam 130,47 e 130,46,
  mas a RN-007 não compara em reais. Confere.
  - **Moeda estrangeira não comprova viagem:** transporte 22 EUR = 130,46 com
  nota. 14/07 fica fora de viagem. Alimentação de 80,00 com limite 60,00 →
  `parcial` com 60,00. Confere.

  **Também conferi:**
  - seção 7: 16,8649 × 5,93 = 100,008857; 200000000 × 5,44 = 1.088.000.000,00;
  40 × 5,50 = 220,00;
  - riscos da seção 10: 70,00 e 120,00 por dia;
  - totais do envelope: 2.457,52 e 1.148,26.

  ## 3. Problemas

  ### 1. "Data intermediária sem a moeda": o caso está incompleto e o câmbio
  usado é ambíguo — MENOR — lacuna
  - **Onde:** seção 7, linha 693 ("câmbio com 13/07 (EUR 5,91) e 14/07 só com
  USD; 20,00 EUR em 15/07").
  - **Cenário:** o preâmbulo da seção 7 diz que os casos usam `cambio.json`,
  salvo indicação na linha. Esse arquivo tem EUR 5,88 em 15/07.
    - Se a linha só modifica 13/07 e 14/07, a cotação de 15/07 continua lá:
  valor 117,60 e `data_cotacao` 2026-07-15.
    - Se a linha substitui o arquivo inteiro, como no caso vizinho que diz
  "câmbio só com 13/07", o resultado é 118,20.
  - O caso também não diz categoria nem `tem_nota_fiscal`. Com 118,20, sem nota,
  o resultado é `nota_fiscal_ausente`; com nota, a alimentação sai `parcial`
  com 60,00. É o mesmo tipo de defeito que a R2-8 corrigiu.
  - Os valores que o caso afirma (`valor_considerado` e `data_cotacao`) não
  dependem do status. O impacto fica só na montagem do teste.
  - **Pergunta:** o câmbio desse caso é só 13/07 e 14/07, ou é o `cambio.json`
  com essas duas datas alteradas? E quais são a categoria e a nota da despesa?

  ### 2. RN-016 valida dados que a própria spec manda ignorar — MENOR —
  ambiguidade
  - **Onde:** RN-016 diz que a taxa "≤ 0 → erro" e que "qualquer número dos dois
  arquivos" com valor absoluto a partir de 1 bilhão é erro. A RN-015 diz que
  "uma entrada `BRL` no arquivo é ignorada", e o fim da RN-016 diz que "campos
  não listados (`observacao`, `fonte`…) são ignorados".
  - **Cenário A:** o câmbio traz `"2026-07-14": {"BRL": 0, "EUR": 5.93}`. Pela
  RN-016 é erro de arquivo; pela RN-015 a entrada é ignorada e a execução segue.
  - **Cenário B:** uma regra da política traz `"observacao": 1e999999`. Pelo
  texto "qualquer número dos dois arquivos" é erro de arquivo; pelo parêntese
  "(limite, mínimo da nota, percentual, taxa)" e por "campos não listados são
  ignorados", a execução segue.
  - **Pergunta:** a validação da RN-016 (taxa positiva e teto) vale também para
  a entrada `BRL` do câmbio e para números em campos ignorados, ou só para os
  valores que entram no cálculo?

  ### 3. `null` e texto só com espaços nos campos opcionais da política e do
  câmbio — MENOR — ambiguidade
  - **Onde:** RN-016: "`versao` presente que não é texto não vazio", "`vigencia`
  presente que não é data válida", "`moeda_base` presente e diferente de
  `"BRL"`", "`centros_custo` presente que não é objeto".
  - **Cenário:** uma política com `"vigencia": null` ou `"centros_custo": null`.
  Lida ao pé da letra, a regra dá erro de arquivo, porque o campo está presente
  e não tem o tipo certo.
  - Na entrada, a spec segue outra convenção: `null` vale como ausente em
  `centro_custo` e em `moeda`. A saída da seção 4 só diz "nulas se ausentes".
  - Caso parecido: `"versao": "  "`. É "texto não vazio" ao pé da letra, mas em
  outros pontos a spec trata "vazio ou só com espaços" como uma coisa só.
  - **Pergunta:** nos campos opcionais da política e do câmbio, `null` equivale
  a ausente ou é erro de arquivo? E `versao` só com espaços em branco é válida?

  ## Listas finais
  1. **Decidir antes da implementação:** nenhum. Não há BLOQUEANTE.
  2. **Pode ser decidido depois:** 1, 2 e 3. O achado 1 precisa estar resolvido
  antes de escrever o teste desse caso de borda.

  Arquivos lidos:
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md`,
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md`,
  `/Users/rafaeltxm/repo/sdd-desafio/exemplos/envelope/cambio.json`,
  `/Users/rafaeltxm/repo/sdd-desafio/exemplos/envelope/politica-v4.json`.

⏺ A confirmação terminou sem nada bloqueante e sem nada importante. As decisões
  R2-1 a R2-10 estão aplicadas de forma completa e coerente, e as contas dos
  casos novos e corrigidos batem. Sobraram 3 achados menores, de redação:

  1. Caso "Data intermediária sem a moeda" incompleto.
  - O caso não diz se o câmbio é só 13/07 e 14/07, ou se é o cambio.json, que
    tem EUR em 15/07. Também falta a categoria e a nota da despesa.
  - Minha recomendação: o câmbio desse caso é só 13/07 e 14/07, e a despesa é
    uma alimentação com nota. O resultado fica 118,20, parcial com 60,00.

  2. Validação de números que a spec manda ignorar.
  - Uma entrada BRL com taxa 0 no câmbio é ignorada pela RN-015, mas pela RN-016
    seria erro. O mesmo vale para um número gigante num campo ignorado, como
    observacao.
  - Minha recomendação: a validação vale para todos os campos listados na
    RN-016, inclusive taxas de moedas que nenhuma despesa usa. A entrada BRL e
    os campos não listados ficam totalmente ignorados, sem validação.

  3. null e texto só com espaços nos campos opcionais da política e do câmbio.
  - Minha recomendação: null equivale a ausente, como em centro_custo e moeda.
    versao só com espaços é erro, porque "texto não vazio" significa ter algum
    caractere fora do espaço em branco, a mesma regra de colaborador.nome.

⏺ User answered Claude's questions:
  ⎿  · Achado 1: caso "Data intermediária sem a moeda"? → Só 13/07 e 14/07; 
     alimentação com nota (Recomendado)
     · Achado 2: validação (taxa > 0, teto) vale para a entrada BRL do câmbio e 
     para campos ignorados? → Não; só campos listados (Recomendado)
     · Achado 3: null e só espaços nos campos opcionais da política/câmbio? → 
     null = ausente; versao só espaços = erro (Recomendado)

⏺ Agent "Confirmation review of spec 2.0" finished · 1m 57s

⏺ Bash(python3 - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)
  ⎿   M specs/001-motor-reembolso/DECISIONS.md
      M specs/001-motor-reembolso/spec.md
     ?? exemplos/envelope/
  ⎿  Updated specs/001-motor-reembolso/DECISIONS.md (+8 -0)
      70  | R2-9 | Categoria com limite 0 sai normalizada? | sim, está na
           tabela aplicada | seção 4 |
      71  | R2-10 | Textos desatualizados | AMB-010, AMB-014, AMB-018 e l
          egenda da seção 9 reescritos; risco novo: categorias reconhecid
          as pelo nome | seções 6, 9, 10 |
      72  
      73 +**Rodada de confirmação:** nenhum problema bloqueante ou import
         +ante. As decisões R2-1 a R2-10 conferem em todos os lugares, e 
         +os números dos casos novos e corrigidos também. Três achados me
         +nores, decididos pelo responsável:                             
      74 +                                                               
      75 +| # | Ponto | Decisão | Onde |                                 
      76 +|---|---|---|---|                                              
      77 +| R3-1 | Caso "Data intermediária sem a moeda" sem câmbio fecha
         +do, categoria e nota | câmbio só com 13/07 e 14/07; alimentação
         + com nota → 118,20, `parcial` com 60,00 | seção 7 |            
      78 +| R3-2 | A validação vale para a entrada `BRL` do câmbio e para
         + campos ignorados? | não: valida todos os campos listados (incl
         +usive taxas não usadas); `BRL` e campos não listados são ignora
         +dos sem validação | RN-016 |                                   
      79 +| R3-3 | `null` e texto só com espaços nos campos opcionais | `
         +null` = ausente; `versao` só com espaços = erro (a mesma regra 
         +de `colaborador.nome`) | RN-016 |                              
      80 +                                                               
      81  Também ficou confirmado que a despesa com `cambio_indisponivel`
           tem `valor_considerado` nulo e fica fora de `valor_solicitado`
          : sem cotação, não existe valor em reais.
      82  
      83  **Por quê:** o comunicado manda ler a política de fora do códig
          o e converter pela taxa da data. As decisões seguem três princí
          pios já usados na 1.x:
  ⎿  Updated specs/001-motor-reembolso/spec.md (+5 -3)
      307  - chave repetida em qualquer objeto (a RN-013 vale só para o a
           rquivo de entrada);
      308  - **política:**
      309    - raiz que não é objeto;
      310 -  - `versao` presente que não é texto não vazio (ausente é vál
          -ida: sai nula);                                               
      310 +  - `versao` presente que não é texto com algum caractere fora
          + do espaço em branco (só espaços é erro; ausente é válida: sai
          + nula);                                                       
      311    - `vigencia` presente que não é data válida `AAAA-MM-DD` (au
           sente é válida: sai nula);
      312    - `moeda_base` presente e diferente de `"BRL"` (ausente vale
            `BRL`);
      313    - `padrao` ausente ou que não é tabela;
     ...
      328    - valor de `taxas` que não é objeto;
      329    - código de moeda que não tem exatamente 3 letras maiúsculas
            de `A` a `Z`;
      330    - taxa que não é número ou que é menor ou igual a zero.
      331 -- **qualquer número dos dois arquivos** (limite, mínimo da not
          -a, percentual, taxa) com valor absoluto a partir de 1.000.000.
          -000 — o mesmo teto da AMB-018.                                
      331 +- limite, mínimo da nota, percentual ou taxa com valor absolut
          +o a partir de 1.000.000.000 — o mesmo teto da AMB-018.        
      332 +                                                              
      333 +Nos campos opcionais (`versao`, `vigencia`, `moeda_base`, `cen
          +tros_custo`), `null` vale como ausente, como `centro_custo` e 
          +`moeda` na entrada. A validação vale para todos os campos list
          +ados acima, inclusive taxas de moedas que nenhuma despesa usa;
          + a entrada `BRL` do câmbio (RN-015) e os campos não listados s
          +ão ignorados sem nenhuma validação (`"BRL": 0` ou `"observacao
          +": 1e999999` não são erro).                                   
      334  
      335  "Casas decimais" e o teto se medem pelo **valor exato** do núm
           ero, como na seção 4, não pela forma escrita: `60.000` e `6E1`
            são 60,00 e valem; `60.005` tem 3 casas e é erro de arquivo.
      336  
     ...
      692  | Duplicata em moeda estrangeira | 22.001 EUR e 22.00 EUR, ali
           mentação com nota, mesmo fornecedor, em 14/07 | segunda `dupli
           cata` | RN-007 |
      693  | Moeda estrangeira não comprova viagem | transporte de 22,00 
           EUR com nota em 14/07; alimentação 80,00 em BRL em 14/07 | 14/
           07 fora de viagem; alimentação limite 60,00, `parcial` com 60,
           00 | RN-010 |
      694  | Hospedagem em moeda estrangeira | hospedagem de 50,00 EUR co
           m nota em 22/07; alimentação 80,00 em BRL em 23/07 | hospedage
           m 297,50, `parcial` com 250,00; 22/07 e 23/07 em viagem; alime
           ntação limite 90,00, `aprovado` com 80,00 | RN-010, RN-015 |
      693 -| Data intermediária sem a moeda | câmbio com 13/07 (EUR 5,91)
          - e 14/07 só com USD; 20,00 EUR em 15/07 | usa 13/07: `valor_co
          -nsiderado` 118,20, `data_cotacao` 2026-07-13 | RN-015 |       
      695 +| Data intermediária sem a moeda | câmbio só com 13/07 (USD 5,
          +42, EUR 5,91) e 14/07 (só USD 5,44); alimentação de 20,00 EUR 
          +com nota em 15/07 | usa 13/07: `valor_considerado` 118,20, `da
          +ta_cotacao` 2026-07-13; `parcial` com 60,00 | RN-015 |        
      696  | Centro de custo reservado no arquivo | política com chave `"
           padrao"` em `centros_custo` | erro de arquivo | RN-016 |
      697  | Política sem versão nem vigência | arquivo de política sem `
           versao` e sem `vigencia` | processamento normal; `politica.ver
           sao` e `politica.vigencia` nulas | RN-016 |
      698  | Política sem tabela padrão | arquivo de política sem `padrao
           ` | erro de arquivo | RN-016 |

⏺ Bash(sed -i '' 's/\*\*Status:\*\* em revisão (Política v4)/**Status:**
      aprovada para planejamento (Política v4)/'
      specs/001-motor-reembolso/spec.md && sed -n 3p spec…)
  ⎿  **Versão:** 2.0 · **Status:** aprovada para planejamento (Política v4)
      · **Última alteração:** 2026-10-02 (ver `DECISIONS.md` D-001 a D-007)
     36-export-no-commit-de-fim-de-bloco.md
  ⎿  Updated specs/001-motor-reembolso/spec.md (+1 -1)
      1  # Spec — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 2.0 · **Status:** em revisão (Política v4) · **Últim
        -a alteração:** 2026-10-02 (ver `DECISIONS.md` D-001 a D-007)    
      3 +**Versão:** 2.0 · **Status:** aprovada para planejamento (Políti
        +ca v4) · **Última alteração:** 2026-10-02 (ver `DECISIONS.md` D-
        +001 a D-007)                                                    
      4  
      5  > **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ
         . Nenhuma linha
      6  > aqui pode citar linguagem, biblioteca, classe, função ou estru
         tura de pasta.

⏺ Os três achados menores da confirmação estão aplicados, e não sobrou nada
  bloqueante. A spec 2.0 está marcada como "aprovada para planejamento":
  - Caso "Data intermediária sem a moeda": câmbio só com 13/07 e 14/07;
    alimentação com nota → 118,20, parcial com 60,00.
  - RN-016: valida todos os campos listados, inclusive taxas que nenhuma despesa
    usa. A entrada BRL do câmbio e os campos não listados ficam totalmente
    ignorados.
  - Campos opcionais: null vale como ausente, e versao só com espaços é erro.
  - D-007: ganhou a tabela da rodada de confirmação (R3-1 a R3-3).

  Este bloco termina aqui (spec 2.0 + D-007). Para o commit único:

  1. Rode /export docs/sessions/37-politica-v4-spec-2-0.md.
  2. Eu commito spec.md, DECISIONS.md e o export como docs(spec): spec 2.0 — 
     Política v4 (D-007).

  O pytest não roda nesse commit porque ele só tem documentação, então a
  rastreabilidade vermelha não bloqueia.

  Os arquivos de exemplos/envelope/ ficam fora deste commit. Qualquer commit que
  inclua exemplos/ dispara o pytest, que hoje falha na rastreabilidade (RN-014
  a RN-016 e os 37 casos novos ainda sem teste). Eles entram junto com a
  primeira task do envelope. O próximo bloco, plan.md e tasks, precisa resolver
  isso, porque o mesmo bloqueio vai atingir todos os commits feat(T-NNN).

✻ Brewed for 4m 0s · done 9:21 PM