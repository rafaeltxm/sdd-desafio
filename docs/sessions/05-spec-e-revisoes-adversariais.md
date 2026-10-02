> **Nota sobre este arquivo:** trecho de um único `/export` da sessão do Claude Code
> (exportado como `_completo.md` e recortado). Cobre do fim de `04-skill-task-hooks-e-revisor.md`
> até o commit `bdb1eec`: avaliação do tooling, escrita da spec 1.0 (`c8bcad9`), primeira rodada do
> `spec-adversary` + análise dos dados → 13 decisões (spec 1.1, `d35f68d`, D-001), segunda rodada →
> 6 decisões (spec 1.2, `bdb1eec`, D-002).
> Nenhuma linha do export foi alterada — apenas recortada.

 ▐▛███▛█   Claude Code v2.1.287
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~/repo/sdd-desafio

  Opus 5.5 is now your default model and it draws down usage faster than Sonnet 5. Switch anytime with /model.
  [... trecho anterior em 01 a 04 ...]

❯ /export docs/sessions/_completo.md                                            
  ⎿  Conversation exported to:
     /Users/rafaeltxm/repo/sdd-desafio/docs/sessions/_completo.md

❯ pode cortar                                                                   
  ⎿  1 agent type available

  Ran 1 shell command (ctrl+o to expand)

⏺ Bash(grep -c -i "icloud" _completo.md; {
      cat <<'EOF'…)
  ⎿  0
         1578 04-skill-task-hooks-e-revisor.md
     01-setup.md
     … +3 lines (ctrl+o to expand)
  ⎿  2 files changed (binary, mode only or too large to show)

  Pushed to main (ctrl+o to expand)

⏺ Cortei o export e fiz o commit e o push: d06f301 docs(sessions): export da 
  sessão 04 — skill task, hooks e revisor-de-task.

  - Ponto de corte: comecei no ponto exato onde o 03 termina (o primeiro /export
    do _completo.md), não no pedido da skill task, como eu tinha dito. Assim a
    divisão dos exports 02 e 03 também fica registrada e não há buraco entre os
    arquivos. O 04 vai até os quatro commits de ferramentas.
  - Nota no topo: igual à dos anteriores, dizendo que é um recorte, de onde até
    onde vai e que nenhuma linha foi alterada.
  - Antes de publicar: conferi que o seu e-mail do iCloud não aparece. Apaguei o
    _completo.md, que nunca entrou num commit.
  - Hooks: o post-commit ficou em silêncio, porque esse commit é o próprio
    export.

  docs/sessions/ tem agora quatro exports, do 01 ao 04, e o repositório não tem
  nada pendente.

  Próximo bloco, a Fase 1: as suas decisões de A1 a A15, mais a ordem de
  aplicação das regras. A lista com as minhas recomendações está no
  02-ambiguidades-e-tooling.md. Pode responder algo como "ok em tudo, exceto A5
  = ⓑ".

✻ Churned for 27s · done 8:43 PM

❯ ok, tem algo que eu preciso avalair do que foi criado? somente reiniciar o    
  claude ne?                                                                    

⏺ Não precisa nem reiniciar: o Claude Code já carregou tudo nesta sessão. O
  revisor-de-task apareceu na lista de subagentes, a skill /task está disponível
  e o hook do lembrete de export disparou no último commit. Reinicie só se
  algum deles sumir.

  Vale avaliar, por ordem de importância:

  1. Ler você mesmo os arquivos de ferramenta:
     - .claude/agents/revisor-de-task.md
     - .claude/agents/spec-adversary.md
     - .claude/skills/task/SKILL.md

     A rubrica penaliza material gerado e aceito sem revisão. Além disso, você
     vai citá-los na seção de Delegação do relatório. Uns 10 minutos de leitura
     bastam. Se algo não for como você quer, me diga e eu ajusto.
  2. Duas decisões que ficaram implícitas:
     - Marcação da tarefa em commit separado (docs(tasks): conclui T-NNN). Você
       aprovou o commit da skill sem comentar esse ponto, então ficou valendo o
       commit separado.
     - Teste e código no mesmo commit. Como o pre-commit roda o pytest, não dá
       para fazer o commit de um teste que ainda falha. A skill já faz teste e
       código juntos, mas é bom você saber, porque o DESAFIO.md mostra
       test(T-003) como commit separado.
  3. O e-mail do Git: rrafaeltxm@gmail.com, com dois "r". Se for erro de
     digitação, convém corrigir antes que os commits da spec e do código saiam
     com ele.
  4. Pendências que já estão no roteiro:
     - No README.md, explicar que cada clone precisa rodar git config 
       core.hooksPath .githooks uma vez.
     - No CLAUDE.md, a seção "Stack e comandos" ainda está com <...>. Ela é
       preenchida na fase do plan.md.

  Fora isso, pode seguir para a Fase 1 com as suas decisões de A1 a A15.

✻ Sautéed for 12s · done 8:45 PM

❯ ok em tudo, vamos para a fase 1                                               

⏺ Antes de escrever a spec, falta uma decisão: a A5. Para ela eu não deixei uma
  recomendação única, só duas opções, então o "ok em tudo" não a resolve. Ela
  também muda a A4, porque define quais dias contam como "em viagem".

⏺ User declined to answer questions
  ⎿  · A5 — Uma despesa de hospedagem pode representar várias diárias (d-010 
     "Hotel Rio - 2 diarias" R$ 480; d-013 "Airbnb 3 noites" R$ 690), mas a 
     entrada não tem campo de quantidade. Como o sistema deve tratar? (ⓑ 1 
     lançamento = 1 diária / ⓐ Ler nº de diárias da descrição / ⓒ Recusar 
     multi-diária)

⏺ Claro. O que você quer esclarecer sobre a A5?

  Para ajudar, este é o problema em uma linha: a entrada não diz quantas diárias
  uma despesa de hospedagem representa. Isso aparece só no texto da descrição
  (d-010 "2 diarias", R$ 480; d-013 "3 noites", R$ 690). O limite da política é
  "R$ 250 por diária", então o valor reembolsado depende de quantas diárias
  contamos.

  As três opções eram:
  - ⓑ tratar cada lançamento como 1 diária: o d-010 paga R$ 250 dos R$ 480;
  - ⓐ ler o número de diárias na descrição: o d-010 conta como 2 diárias e paga
    os R$ 480;
  - ⓒ recusar lançamentos que agrupam várias diárias.

  Pode perguntar o que quiser, ou propor outra saída.

✻ Cooked for 18s · done 8:53 PM

❯ o mais ideal seria deixar o usuario lançar a data de entrada e saida e o      
  controle de diarias ficar no sistema                                          

⏺ Do ponto de vista do produto, a sua ideia é a solução certa: com datas de
  entrada e saída, o sistema calcula as diárias sem ler texto livre e sabe
  exatamente quais dias foram de viagem. O problema é uma restrição do desafio.

  O DESAFIO.md fixa o formato de entrada: "A entrada está definida em
  exemplos/despesas-exemplo.json. Respeite esse formato." Além disso, o produto
  é testado com casos ocultos do instrutor, escritos nesse formato, sem datas de
  entrada e saída. Então:

  - Trocar o formato (exigir as datas): quebra a interface fixa, e todos os
    casos ocultos de hospedagem falhariam.
  - Acrescentar as datas como campos opcionais: é compatível, porque uma entrada
    sem esses campos continua válida. Mas, nos casos do instrutor, os campos
    nunca vêm. Ou seja, a A5 continua precisando de uma regra para quando as 
    datas não vêm, e essa é a regra que vai ser avaliada.

  Existem dois caminhos coerentes com a sua ideia:

  1. Registrar como fora de escopo. A spec diz que o certo seria informar as
     datas, que o formato fixo não permite, e que isso fica como recomendação de
     evolução. Para o formato atual, você escolhe ⓐ, ⓑ ou ⓒ. É o mais simples e
     mostra na spec que você enxergou a solução ideal.
  2. Campos opcionais data_entrada e data_saida na hospedagem. Quando vierem, as
     diárias são calculadas como saída menos entrada. Quando não vierem, vale
     ⓐ, ⓑ ou ⓒ. É mais completo, mas aumenta o escopo (validação das datas,
     saída antes da entrada, estadia que passa do fim do período...), e cada um
     desses casos vira mais uma ambiguidade a decidir.

  Minha recomendação é o caminho 1, com ⓑ como regra: cada lançamento é uma
  diária. ⓑ é a única opção que não depende de interpretar a descrição, e é
  coerente com a sua ideia: se o sistema não recebe as datas, não deve adivinhar
  as diárias a partir do texto. Fica registrado que, nesse formato, o d-010
  paga R$ 250 dos R$ 480.

  Qual você prefere? E, com campos opcionais ou não, a regra para quando as
  datas não vêm: ⓐ, ⓑ ou ⓒ?

✻ Crunched for 12s · done 8:54 PM

❯ ok, isso é um ponto importante, preciso que lembre pontue que eu não esteja   
  dando posicionamentos que quebrem a logica dos dados                          

  Ran 1 shell command, wrote 1 memory (ctrl+o to expand)

⏺ Anotado na memória do projeto: a partir de agora, eu sinalizo qualquer
  conflito entre suas decisões e as regras fixas antes de seguir. Interpreto seu
  "ok" como caminho 1 + ⓑ (cada hospedagem como diária, datas fora de escopo) e
  vou ler os modelos da spec e do DECISIONS.md para começar a escrever.

  Read 2 files (ctrl+o to expand)
⏺ Tenho o que preciso. Vou escrever a spec.md com as suas decisões. Onde a spec
  exigiu um detalhe que não foi decidido, vou listá-lo no fim para você revisar.

⏺ Write(specs/001-motor-reembolso/spec.md)
  ⎿  Added 359 lines, removed 38 lines
      1  # Spec — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.0 · **Status:** rascunho · **Última alteração:** `
        -<data>`                                                         
      3 +**Versão:** 1.0 · **Status:** rascunho para revisão · **Última a
        +lteração:** 2026-10-01                                          
      4  
      5  > **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ
         . Nenhuma linha
      6  > aqui pode citar linguagem, biblioteca, classe, função ou estru
         tura de pasta.
     ...
       13  
       14  ## 1. Problema
       15  
       16 -<Duas ou três frases. Quem sofre hoje, com o quê, e por quê is
          -so custa caro.>                                               
       16 +Hoje o financeiro confere manualmente, item por item, as despe
          +sas de cada colaborador contra a política de reembolso do RH. 
          +O processo é lento, e como a política é ambígua, cada pessoa a
          + interpreta de um jeito: o mesmo conjunto de despesas pode ger
          +ar valores diferentes dependendo de quem confere.             
       17  
       18  ## 2. Objetivo
       19  
       20 -<Uma frase. O que passa a ser verdade quando isto existir.>   
       20 +Dado o conjunto de despesas de um colaborador num período, cal
          +cular de forma determinística quanto é reembolsável e justific
          +ar a decisão sobre cada despesa, aplicando uma interpretação ú
          +nica e documentada da política.                               
       21  
       22  ## 3. Fora de escopo
       23  
       24 -<Lista explícita. Este bloco vale ponto: ele impede o agente d
          -e inventar feature                                            
       25 -e impede você de mover a trave depois.>                       
       24 +- Não aprova, paga nem integra com sistemas de pagamento ou fo
          +lha: só calcula e justifica.                                  
       25 +- Não processa mais de um colaborador ou mais de um período po
          +r execução.                                                   
       26 +- Não verifica a autenticidade da nota fiscal; confia no indic
          +ador `tem_nota_fiscal`.                                       
       27 +- Não lê nem interpreta o texto livre de `descricao` (nem para
          + contar diárias, ver AMB-005).                                
       28 +- Não converte moedas: todos os valores são em reais.         
       29 +- Não guarda histórico entre execuções: duplicatas só são dete
          +ctadas dentro da mesma entrada.                               
       30 +- Não aceita campos adicionais na entrada para datas de entrad
          +a/saída de hospedagem. Seria a solução ideal para AMB-005, mas
          + o formato de entrada é fixo; fica registrado como evolução re
          +comendada.                                                    
       31 +- Não trata feriados nem fins de semana de forma especial (AMB
          +-015).                                                        
       32  
       27 -- Não faz `<...>`                                             
       28 -- Não faz `<...>`                                             
       29 -                                                              
       33  ## 4. Entrada e saída
       34  
       32 -**Entrada:** conforme `exemplos/despesas-exemplo.json`. Campos
          - e significado:                                               
       35 +### Interface                                                 
       36  
       37 +`<comando> calcular --input <arquivo de entrada> --output <arq
          +uivo de saída>`                                               
       38 +                                                              
       39 +- Sucesso: grava o arquivo de saída e termina com código 0.   
       40 +- Erro de arquivo (RN-002): não grava o arquivo de saída, escr
          +eve uma mensagem de erro e termina com código diferente de 0. 
       41 +                                                              
       42 +### Entrada                                                   
       43 +                                                              
       44 +Formato fixo, conforme `exemplos/despesas-exemplo.json`.      
       45 +                                                              
       46  | Campo | Tipo | Significado | Obrigatório |
       47  |---|---|---|---|
       36 -| | | | |                                                     
       48 +| `colaborador.id` | texto | identificador do colaborador | si
          +m |                                                           
       49 +| `colaborador.nome` | texto | nome | sim |                   
       50 +| `colaborador.centro_custo` | texto | centro de custo | não |
       51 +| `periodo.competencia` | texto `AAAA-MM` | rótulo do mês de c
          +ompetência; repetido na saída, não usado em cálculo | não |   
       52 +| `periodo.inicio` | data `AAAA-MM-DD` | primeiro dia do perío
          +do (inclusive) | sim |                                        
       53 +| `periodo.fim` | data `AAAA-MM-DD` | último dia do período (i
          +nclusive) | sim |                                             
       54 +| `despesas` | lista | despesas a avaliar (pode ser vazia) | s
          +im |                                                          
       55 +| `despesas[].id` | texto | identificador da despesa | sim |  
       56 +| `despesas[].data` | data `AAAA-MM-DD` | data em que a despes
          +a ocorreu | sim |                                             
       57 +| `despesas[].categoria` | texto | categoria da despesa | sim 
          +|                                                             
       58 +| `despesas[].descricao` | texto | descrição livre; não usada 
          +em regras | não |                                             
       59 +| `despesas[].fornecedor` | texto | estabelecimento; usado na 
          +detecção de duplicatas | sim |                                
       60 +| `despesas[].valor` | número | valor em reais | sim |        
       61 +| `despesas[].tem_nota_fiscal` | booleano | se há nota fiscal 
          +| sim |                                                       
       62  
       38 -**Saída:** definida por mim. Estrutura e significado de cada c
          -ampo:                                                         
       63 +### Saída                                                     
       64  
       65  | Campo | Tipo | Significado |
       66  |---|---|---|
       42 -| | | |                                                       
       67 +| `colaborador` | objeto | `id` e `nome`, copiados da entrada 
          +|                                                             
       68 +| `periodo` | objeto | `competencia`, `inicio` e `fim`, copiad
          +os da entrada |                                               
       69 +| `itens` | lista | um item por despesa da entrada, **na mesma
          + ordem** |                                                    
       70 +| `itens[].id` | texto | id da despesa |                      
       71 +| `itens[].data` | texto | data da despesa como veio na entrad
          +a |                                                           
       72 +| `itens[].categoria` | texto | categoria normalizada (RN-006)
          + ou como veio, se não reconhecida |                           
       73 +| `itens[].valor_informado` | número ou nulo | valor exatament
          +e como veio na entrada (nulo se ausente ou não numérico) |    
       74 +| `itens[].valor_considerado` | número ou nulo | valor arredon
          +dado ao centavo (RN-003); nulo se ausente ou não numérico |   
       75 +| `itens[].valor_reembolsado` | número | quanto será reembolsa
          +do (0 se recusado) |                                          
       76 +| `itens[].status` | texto | `aprovado`, `parcial` ou `recusad
          +o` (RN-011) |                                                 
       77 +| `itens[].motivo` | texto ou nulo | código do motivo (tabela 
          +abaixo); nulo quando `aprovado` |                             
       78 +| `itens[].em_viagem` | booleano ou nulo | se a data estava em
          + viagem (RN-010); nulo se o item foi recusado antes do limite 
          +diário |                                                      
       79 +| `itens[].limite_diario` | número ou nulo | limite diário apl
          +icado à categoria naquela data; nulo se o item foi recusado an
          +tes do limite diário |                                        
       80 +| `itens[].justificativa` | texto | frase em português explica
          +ndo a decisão. Texto livre: não é contratual, os campos acima 
          +são |                                                         
       81 +| `totais.valor_solicitado` | número | soma de `valor_consider
          +ado` dos itens com valor válido (maior que zero) |            
       82 +| `totais.valor_reembolsado` | número | soma de `valor_reembol
          +sado` |                                                       
       83 +| `totais.valor_glosado` | número | `valor_solicitado − valor_
          +reembolsado` |                                                
       84  
       44 -<Cole um exemplo de saída para uma entrada pequena. Vale mais 
          -que três parágrafos.>                                         
       85 +Todos os valores monetários da saída são em reais, com no máxi
          +mo 2 casas decimais e exatos ao centavo.                      
       86  
       87 +**Códigos de motivo:**                                        
       88 +                                                              
       89 +| Código | Quando | Status resultante |                       
       90 +|---|---|---|                                                 
       91 +| `entrada_invalida` | campo obrigatório ausente ou com tipo/f
          +ormato errado (RN-002) | `recusado` |                         
       92 +| `valor_invalido` | valor considerado menor ou igual a zero (
          +RN-004) | `recusado` |                                        
       93 +| `fora_do_periodo` | data fora de `[inicio, fim]` (RN-005) | 
          +`recusado` |                                                  
       94 +| `categoria_fora_da_politica` | categoria não reconhecida (RN
          +-006) | `recusado` |                                          
       95 +| `duplicata` | repete uma despesa anterior (RN-007) | `recusa
          +do` |                                                         
       96 +| `nota_fiscal_ausente` | valor acima de 100,00 sem nota (RN-0
          +08) | `recusado` |                                            
       97 +| `limite_diario_excedido` | o limite diário cortou parte ou t
          +odo o valor (RN-009) | `parcial`, ou `recusado` se nada restou
          + |                                                            
       98 +                                                              
       99 +**Exemplo** (entrada com duas despesas de alimentação no mesmo
          + dia, fora de viagem):                                        
      100 +                                                              
      101 +```json                                                       
      102 +{                                                             
      103 +  "colaborador": { "id": "c-1", "nome": "Ana" },              
      104 +  "periodo": { "competencia": "2026-07", "inicio": "2026-07-01
          +", "fim": "2026-07-31" },                                     
      105 +  "itens": [                                                  
      106 +    { "id": "d-1", "data": "2026-07-03", "categoria": "aliment
          +acao",                                                        
      107 +      "valor_informado": 45.0, "valor_considerado": 45.0, "val
          +or_reembolsado": 45.0,                                        
      108 +      "status": "aprovado", "motivo": null, "em_viagem": false
          +, "limite_diario": 60.0,                                      
      109 +      "justificativa": "Aprovado integralmente: 45,00 dentro d
          +o limite diário de 60,00." },                                 
      110 +    { "id": "d-2", "data": "2026-07-03", "categoria": "aliment
          +acao",                                                        
      111 +      "valor_informado": 30.0, "valor_considerado": 30.0, "val
          +or_reembolsado": 15.0,                                        
      112 +      "status": "parcial", "motivo": "limite_diario_excedido",
          + "em_viagem": false, "limite_diario": 60.0,                   
      113 +      "justificativa": "Parcial: restavam 15,00 do limite diár
          +io de 60,00 de alimentação em 03/07." }                       
      114 +  ],                                                          
      115 +  "totais": { "valor_solicitado": 75.0, "valor_reembolsado": 6
          +0.0, "valor_glosado": 15.0 }                                  
      116 +}                                                             
      117 +```                                                           
      118 +                                                              
      119  ## 5. Regras de negócio
      120  
       48 -Cada regra recebe um ID (`RN-001`, ...). As tasks vão referenc
          -iar esses IDs.                                                
      121 +As regras são aplicadas a cada despesa na ordem da seção 8. A 
          +primeira regra que recusa uma despesa encerra a avaliação dela
          +: cada despesa recusada tem exatamente um motivo.             
      122  
       50 -### RN-001 — <nome da regra>                                  
      123 +### RN-001 — Um resultado por despesa                         
      124  
       52 -**Regra:** <enunciado sem ambiguidade>                        
       53 -**Origem:** política do RH, item `<n>`                        
       54 -**Aceite:** <como verificar que está implementada — normalment
          -e um caso concreto com números>                               
      125 +**Regra:** a saída tem exatamente um item para cada despesa da
          + entrada, na mesma ordem, inclusive as recusadas. Os totais se
          +guem as fórmulas da seção 4.                                  
      126 +**Origem:** objetivo do sistema ("justifica cada decisão").   
      127 +**Aceite:** entrada com 14 despesas gera 14 itens, na mesma or
          +dem de ids; `valor_glosado = valor_solicitado − valor_reembols
          +ado`.                                                         
      128  
       56 -### RN-002 — ...                                              
      129 +### RN-002 — Validação da entrada                             
      130  
      131 +**Regra:**                                                    
      132 +- **Erro de arquivo** (nenhuma saída é gerada): arquivo ausent
          +e ou que não é JSON válido; `periodo.inicio`, `periodo.fim` ou
          + `despesas` ausentes; `inicio` ou `fim` que não são datas váli
          +das `AAAA-MM-DD`; `inicio` posterior a `fim`; `despesas` que n
          +ão é lista.                                                   
      133 +- **Despesa inválida** (vira item `recusado` com motivo `entra
          +da_invalida`): falta `id`, `data`, `categoria`, `fornecedor`, 
          +`valor` ou `tem_nota_fiscal`; `data` não é data válida `AAAA-M
          +M-DD`; `valor` não é número; `tem_nota_fiscal` não é booleano;
          + `categoria` ou `fornecedor` não são texto.                   
      134 +**Origem:** necessidade operacional (a política não trata entr
          +ada malformada).                                              
      135 +**Aceite:** despesa sem `tem_nota_fiscal` → `recusado`, `entra
          +da_invalida`, e as demais despesas são processadas normalmente
          +. Arquivo com `inicio` = `2026-07-31` e `fim` = `2026-07-01` →
          + nenhuma saída, código de saída diferente de 0.               
      136 +                                                              
      137 +### RN-003 — Arredondamento ao centavo                        
      138 +                                                              
      139 +**Regra:** antes de qualquer outra regra de valor, `valor` é a
          +rredondado para 2 casas decimais, com a metade arredondada par
          +a cima (0,005 → 0,01). Todas as regras usam o valor arredondad
          +o (`valor_considerado`), e todos os cálculos são exatos ao cen
          +tavo.                                                         
      140 +**Origem:** AMB-014.                                          
      141 +**Aceite:** `valor` 33.333 → `valor_considerado` 33.33; `valor
          +` 10.005 → 10.01; `valor` 10.004 → 10.00.                     
      142 +                                                              
      143 +### RN-004 — Valor deve ser positivo                          
      144 +                                                              
      145 +**Regra:** despesa com `valor_considerado` menor ou igual a ze
          +ro é `recusado` com motivo `valor_invalido`. Ela não abate, nã
          +o soma e não consome limite de nenhuma outra despesa.         
      146 +**Origem:** AMB-013.                                          
      147 +**Aceite:** `valor` -45.00 → `recusado`, `valor_invalido`, `va
          +lor_reembolsado` 0; demais despesas do mesmo dia não mudam. `v
          +alor` 0.004 (arredonda para 0,00) → `valor_invalido`.         
      148 +                                                              
      149 +### RN-005 — Período de competência                           
      150 +                                                              
      151 +**Regra:** a `data` da despesa precisa estar entre `periodo.in
          +icio` e `periodo.fim`, incluindo os dois extremos. Fora disso:
          + `recusado`, motivo `fora_do_periodo`.                        
      152 +**Origem:** política do RH, item 7; AMB-009.                  
      153 +**Aceite:** período 2026-07-01 a 2026-07-31: data 2026-04-15 →
          + `fora_do_periodo`; datas 2026-07-01 e 2026-07-31 → seguem par
          +a as próximas regras.                                         
      154 +                                                              
      155 +### RN-006 — Categorias da política                           
      156 +                                                              
      157 +**Regra:** a categoria é comparada depois de remover espaços n
          +o início e no fim e ignorando maiúsculas/minúsculas. Só três c
          +ategorias são reconhecidas: `alimentacao`, `transporte_urbano`
          + e `hospedagem`. Na saída, categorias reconhecidas aparecem ne
          +ssa forma normalizada. Qualquer outra (incluindo variações com
          + acento, como `alimentação`) → `recusado`, motivo `categoria_f
          +ora_da_politica`.                                             
      158 +**Origem:** política do RH, item 9; AMB-011; AMB-012.         
      159 +**Aceite:** `ALIMENTACAO` e `" Alimentacao "` → tratadas como 
          +`alimentacao`; `coworking` → `categoria_fora_da_politica`.    
      160 +                                                              
      161 +### RN-007 — Duplicatas                                       
      162 +                                                              
      163 +**Regra:** duas despesas são duplicatas quando têm a mesma `da
          +ta`, a mesma categoria normalizada, o mesmo `fornecedor` (comp
          +arado sem espaços nas pontas e ignorando maiúsculas/minúsculas
          +) e o mesmo `valor_considerado`. `id` e `descricao` não entram
          + na comparação. Entre despesas duplicatas, só a primeira na or
          +dem da entrada segue avaliada; as seguintes são `recusado`, mo
          +tivo `duplicata`. Só despesas que passaram por RN-002 a RN-006
          + participam da comparação. Uma duplicata recusada não consome 
          +limite.                                                       
      164 +**Origem:** política do RH, item 8; AMB-010.                  
      165 +**Aceite:** d-006 e d-007 (mesmos data, categoria, fornecedor 
          +e valor 54,90) → d-006 avaliada normalmente, d-007 `recusado`,
          + `duplicata`. Mesmos dados com fornecedor diferente → não são 
          +duplicatas.                                                   
      166 +                                                              
      167 +### RN-008 — Nota fiscal obrigatória acima de R$ 100          
      168 +                                                              
      169 +**Regra:** despesa com `valor_considerado` estritamente maior 
          +que 100,00 e `tem_nota_fiscal` falso → `recusado`, motivo `not
          +a_fiscal_ausente`. A comparação usa o valor da despesa individ
          +ual, antes de qualquer limite. A despesa recusada não consome 
          +limite nem caracteriza viagem.                                
      170 +**Origem:** política do RH, item 5; AMB-007; AMB-008.         
      171 +**Aceite:** 100,00 sem nota → segue para o limite diário; 100,
          +01 sem nota → `nota_fiscal_ausente`; 100,01 com nota → segue. 
      172 +                                                              
      173 +### RN-009 — Limite diário por categoria                      
      174 +                                                              
      175 +**Regra:** para cada combinação de data e categoria, a soma re
          +embolsada das despesas que chegaram a esta regra não pode pass
          +ar do limite diário:                                          
      176 +                                                              
      177 +| Categoria | Limite diário normal | Limite diário em viagem (
          +RN-010) |                                                     
      178 +|---|---|---|                                                 
      179 +| `alimentacao` | 60,00 | 90,00 |                             
      180 +| `transporte_urbano` | 80,00 | 120,00 |                      
      181 +| `hospedagem` | 250,00 | 250,00 (não amplia, AMB-006) |      
      182 +                                                              
      183 +O limite é consumido pelas despesas na ordem da entrada: cada 
          +despesa recebe `mínimo(valor_considerado, saldo restante do li
          +mite)`. Se recebe o valor inteiro → `aprovado`; se recebe part
          +e → `parcial`, motivo `limite_diario_excedido`; se o saldo já 
          +era zero → `recusado`, motivo `limite_diario_excedido`.       
      184 +**Origem:** política do RH, itens 1, 2, 3 e 4; AMB-001; AMB-00
          +2; AMB-003.                                                   
      185 +**Aceite:** alimentação, mesmo dia, fora de viagem: 72,50 e de
          +pois 38,00 → primeira `parcial` com 60,00, segunda `recusado` 
          +com 0. Ordem invertida (38,00 e depois 72,50) → primeira `apro
          +vado` com 38,00, segunda `parcial` com 22,00.                 
      186 +                                                              
      187 +### RN-010 — Colaborador em viagem                            
      188 +                                                              
      189 +**Regra:** uma data está "em viagem" quando existe na entrada 
          +uma despesa de `hospedagem` nessa mesma data que chegou ao lim
          +ite diário (não foi recusada por RN-002 a RN-008). Em datas em
          + viagem, os limites de `alimentacao` e `transporte_urbano` são
          + ampliados em 50% (tabela da RN-009). Cada despesa de hospedag
          +em cobre apenas a sua própria data (RN-012). A condição de via
          +gem vale para todas as despesas da data, independentemente da 
          +ordem em que aparecem na entrada.                             
      190 +**Origem:** política do RH, item 6; AMB-004.                  
      191 +**Aceite:** hospedagem válida em 14/07 + alimentação de 80,00 
          +em 14/07 → limite 90,00, alimentação `aprovado` com 80,00. Ali
          +mentação de 80,00 em 15/07 sem hospedagem em 15/07 → limite 60
          +,00, `parcial` com 60,00. Hospedagem de 14/07 recusada por not
          +a fiscal → 14/07 não está em viagem.                          
      192 +                                                              
      193 +### RN-011 — Status e justificativa                           
      194 +                                                              
      195 +**Regra:** `aprovado` quando `valor_reembolsado = valor_consid
          +erado`; `parcial` quando `0 < valor_reembolsado < valor_consid
          +erado`; `recusado` quando `valor_reembolsado = 0`. Todo item `
          +parcial` ou `recusado` tem um `motivo` da tabela da seção 4; t
          +odo item tem uma `justificativa` em texto.                    
      196 +**Origem:** objetivo do sistema.                              
      197 +**Aceite:** nenhum item da saída tem status incompatível com o
          +s seus valores.                                               
      198 +                                                              
      199 +### RN-012 — Hospedagem: um lançamento é uma diária           
      200 +                                                              
      201 +**Regra:** cada despesa de `hospedagem` é tratada como uma diá
          +ria na sua `data`, qualquer que seja o valor ou a descrição. V
          +árias hospedagens na mesma data dividem o mesmo limite diário 
          +de 250,00 (RN-009).                                           
      202 +**Origem:** política do RH, item 3; AMB-005.                  
      203 +**Aceite:** hospedagem de 480,00 com nota ("2 diarias" na desc
          +rição) → `parcial` com 250,00; data em viagem só no dia da des
          +pesa.                                                         
      204 +                                                              
      205  ---
      206  
      207  ## 6. Ambiguidades identificadas e decisões
      208  
       62 -> **Esta seção é o coração da spec e vale a maior parte dos 25
          - pontos do critério 1.**                                      
       63 -> Uma ambiguidade que você resolveu no código sem registrar aq
          -ui conta como                                                 
       64 -> não resolvida.                                              
      209 +Tipo: **U** = unidade de aplicação · **F** = fronteira · **D**
          + = dado ausente.                                              
      210  
       66 -### AMB-001 — <o que a política deixou em aberto>             
      211 +### AMB-001 — Limite "por dia" é por despesa ou pela soma do d
          +ia? (U)                                                       
      212  
       68 -**Texto original do RH:** "<citação literal>"                 
       69 -**O que não está claro:** <as duas ou mais leituras possíveis>
       70 -**Decisão:** <o que o sistema faz>                            
       71 -**Justificativa:** <por quê — uma linha; critério de negócio, 
          -não de conveniência técnica>                                  
       72 -**Regra afetada:** RN-00X                                     
      213 +**Texto original do RH:** "Alimentação tem limite de R$ 60 por
          + dia." (idem itens 2 e 3)                                     
      214 +**O que não está claro:** se cada despesa pode ir até 60,00, o
          +u se a soma das despesas do dia é que não pode passar de 60,00
          + (d-001 + d-002 no mesmo dia: 72,50 + 38,00).                 
      215 +**Decisão:** o limite vale para a soma de todas as despesas da
          + mesma categoria na mesma data.                               
      216 +**Justificativa:** "por dia" descreve um teto diário; aplicar 
          +por despesa permitiria contornar o limite fracionando a despes
          +a.                                                            
      217 +**Regra afetada:** RN-009                                     
      218  
       74 -### AMB-002 — ...                                             
      219 +### AMB-002 — "Reembolsadas parcialmente" = paga até o limite 
          +ou recusa? (F)                                                
      220  
       76 -<A política tem no mínimo oito. Se você achou menos, releia   
       77 -`exemplos/despesas-exemplo.json` — cada item daquele arquivo e
          -xiste por um motivo.>                                         
      221 +**Texto original do RH:** "Despesas acima do limite são reembo
          +lsadas parcialmente."                                         
      222 +**O que não está claro:** se paga o valor do limite e corta o 
          +excedente, ou se recusa a despesa inteira.                    
      223 +**Decisão:** paga até o limite e corta só o excedente.        
      224 +**Justificativa:** "parcialmente" significa que parte é paga; 
          +recusar tudo contradiria o texto.                             
      225 +**Regra afetada:** RN-009                                     
      226  
      227 +### AMB-003 — Como dividir o limite entre várias despesas do m
          +esmo dia? (U)                                                 
      228 +                                                              
      229 +**Texto original do RH:** (não tratado)                       
      230 +**O que não está claro:** quando a soma do dia passa do limite
          +, de qual despesa sai o corte. A entrada não tem horário.     
      231 +**Decisão:** as despesas consomem o limite na ordem em que apa
          +recem na entrada; o corte cai nas últimas.                    
      232 +**Justificativa:** é o único critério determinístico disponíve
          +l nos dados e reproduz a conferência item a item feita hoje.  
      233 +**Regra afetada:** RN-009                                     
      234 +                                                              
      235 +### AMB-004 — O que caracteriza "em viagem"? (D)              
      236 +                                                              
      237 +**Texto original do RH:** "Colaborador em viagem tem limites a
          +mpliados em 50%."                                             
      238 +**O que não está claro:** a entrada não tem campo de viagem.  
      239 +**Decisão:** uma data está em viagem se há na entrada uma hosp
          +edagem válida (não recusada antes do limite) nessa data.      
      240 +**Justificativa:** hospedagem é a única evidência objetiva de 
          +viagem nos dados; uma hospedagem recusada não comprova a viage
          +m.                                                            
      241 +**Regra afetada:** RN-010                                     
      242 +                                                              
      243 +### AMB-005 — Uma despesa de hospedagem com várias diárias (D,
          + U)                                                           
      244 +                                                              
      245 +**Texto original do RH:** "Hospedagem tem limite de R$ 250 por
          + diária."                                                     
      246 +**O que não está claro:** a entrada não informa quantas diária
          +s uma despesa representa; essa informação só aparece em texto 
          +livre (d-010 "2 diarias", d-013 "3 noites").                  
      247 +**Decisão:** cada lançamento de hospedagem é uma diária, na da
          +ta da despesa. A descrição não é interpretada.                
      248 +**Justificativa:** sem campo estruturado, contar diárias a par
          +tir de texto livre seria adivinhar; a solução correta (datas d
          +e entrada e saída) exige mudar o formato de entrada, que é fix
          +o (seção 3).                                                  
      249 +**Regra afetada:** RN-012, RN-010                             
      250 +                                                              
      251 +### AMB-006 — O acréscimo de 50% vale para a hospedagem? (U)  
      252 +                                                              
      253 +**Texto original do RH:** "Colaborador em viagem tem limites a
          +mpliados em 50%."                                             
      254 +**O que não está claro:** se "limites" inclui o de hospedagem,
          + que já pressupõe viagem.                                     
      255 +**Decisão:** não; a hospedagem tem sempre limite de 250,00 por
          + diária.                                                      
      256 +**Justificativa:** toda hospedagem já é viagem; ampliar o limi
          +te dela tornaria o valor de 250,00 da política inalcançável na
          + prática.                                                     
      257 +**Regra afetada:** RN-009                                     
      258 +                                                              
      259 +### AMB-007 — "Acima de R$ 100": exatamente 100,00 exige nota?
          + (F)                                                          
      260 +                                                              
      261 +**Texto original do RH:** "Nota fiscal é obrigatória acima de 
          +R$ 100."                                                      
      262 +**O que não está claro:** se 100,00 está incluído (d-003 = 100
          +,00 e d-004 = 100,01, ambos sem nota).                        
      263 +**Decisão:** só exige nota quando o valor é estritamente maior
          + que 100,00.                                                  
      264 +**Justificativa:** leitura literal de "acima de".             
      265 +**Regra afetada:** RN-008                                     
      266 +                                                              
      267 +### AMB-008 — O que acontece sem a nota obrigatória, e sobre q
          +ual valor se compara? (F, U)                                  
      268 +                                                              
      269 +**Texto original do RH:** "Nota fiscal é obrigatória acima de 
          +R$ 100."                                                      
      270 +**O que não está claro:** se a despesa sem nota é recusada int
          +eira ou paga até 100,00; e se o 100,00 se compara ao valor da 
          +despesa, ao valor já limitado ou à soma do dia.               
      271 +**Decisão:** recusa a despesa inteira; compara com o valor ind
          +ividual da despesa (arredondado), antes de qualquer limite.   
      272 +**Justificativa:** "obrigatória" é condição para reembolsar; c
          +omparar antes do limite impede que o corte do limite "esconda"
          + a falta de nota.                                             
      273 +**Regra afetada:** RN-008                                     
      274 +                                                              
      275 +### AMB-009 — "Lançadas dentro do período de competência" (D, 
          +F)                                                            
      276 +                                                              
      277 +**Texto original do RH:** "Despesas devem ser lançadas dentro 
          +do período de competência."                                   
      278 +**O que não está claro:** a entrada não tem data de lançamento
          +, só a data da despesa; e se os extremos do período estão incl
          +uídos.                                                        
      279 +**Decisão:** a data da despesa precisa estar entre `inicio` e 
          +`fim`, ambos inclusive.                                       
      280 +**Justificativa:** a data da despesa é o único dado disponível
          +; o período informado é fechado nos dois extremos.            
      281 +**Regra afetada:** RN-005                                     
      282 +                                                              
      283 +### AMB-010 — O que é duplicata e como tratá-la? (U)          
      284 +                                                              
      285 +**Texto original do RH:** "Duplicatas devem ser tratadas."    
      286 +**O que não está claro:** quais campos definem uma duplicata (
          +d-006 e d-007 só diferem no id) e o que fazer com ela.        
      287 +**Decisão:** mesma data, categoria, fornecedor e valor; a prim
          +eira na ordem da entrada é avaliada, as demais são recusadas c
          +om motivo `duplicata`.                                        
      288 +**Justificativa:** o id é gerado no lançamento e não identific
          +a o gasto; recusar com motivo explícito deixa visível um event
          +ual gasto legítimo repetido, para o colaborador contestar.    
      289 +**Regra afetada:** RN-007                                     
      290 +                                                              
      291 +### AMB-011 — Categoria com grafia diferente (F)              
      292 +                                                              
      293 +**Texto original do RH:** (não tratado)                       
      294 +**O que não está claro:** se `ALIMENTACAO` (d-014) é a mesma c
          +ategoria que `alimentacao`.                                   
      295 +**Decisão:** ignora maiúsculas/minúsculas e espaços nas pontas
          +; não ignora acentos.                                         
      296 +**Justificativa:** diferença de caixa é erro de digitação ineq
          +uívoco; acentos e outras variações não são presumidos.        
      297 +**Regra afetada:** RN-006                                     
      298 +                                                              
      299 +### AMB-012 — Categoria fora da política: recusar ou omitir? (
          +U)                                                            
      300 +                                                              
      301 +**Texto original do RH:** "Categorias fora da política não são
          + reembolsáveis."                                              
      302 +**O que não está claro:** se a despesa some do resultado ou ap
          +arece recusada.                                               
      303 +**Decisão:** aparece na saída como `recusado`, motivo `categor
          +ia_fora_da_politica`.                                         
      304 +**Justificativa:** o objetivo é justificar cada decisão; omiti
          +r esconderia a despesa do colaborador.                        
      305 +**Regra afetada:** RN-006, RN-001                             
      306 +                                                              
      307 +### AMB-013 — Valor negativo (estorno) (D)                    
      308 +                                                              
      309 +**Texto original do RH:** (não tratado)                       
      310 +**O que não está claro:** d-009 tem valor -45,00 ("estorno"): 
          +se abate do dia, se é ignorado ou se é erro.                  
      311 +**Decisão:** valor menor ou igual a zero é recusado com motivo
          + `valor_invalido` e não afeta nenhuma outra despesa.          
      312 +**Justificativa:** o sistema calcula reembolso de despesas; es
          +torno não é despesa e não há como saber a qual despesa ele se 
          +refere.                                                       
      313 +**Regra afetada:** RN-004                                     
      314 +                                                              
      315 +### AMB-014 — Valor com mais de 2 casas decimais (F)          
      316 +                                                              
      317 +**Texto original do RH:** (não tratado)                       
      318 +**O que não está claro:** d-011 tem 33,333: arredondar, trunca
          +r ou recusar, e quando.                                       
      319 +**Decisão:** arredonda para o centavo, metade para cima, antes
          + de qualquer regra.                                           
      320 +**Justificativa:** reembolso é pago em centavos; arredondar no
          + início garante que todas as regras usem o mesmo valor.       
      321 +**Regra afetada:** RN-003                                     
      322 +                                                              
      323 +### AMB-015 — Despesa em fim de semana (D)                    
      324 +                                                              
      325 +**Texto original do RH:** (não tratado)                       
      326 +**O que não está claro:** d-012 é um almoço de sábado ("plantã
          +o"); a política não diz se despesas em fim de semana são aceit
          +as.                                                           
      327 +**Decisão:** dia da semana não afeta o reembolso.             
      328 +**Justificativa:** a política não restringe; criar a restrição
          + seria inventar regra.                                        
      329 +**Regra afetada:** nenhuma (registrado em Fora de escopo)     
      330 +                                                              
      331 +### AMB-016 — Em que ordem as regras se aplicam? (U)          
      332 +                                                              
      333 +**Texto original do RH:** (não tratado)                       
      334 +**O que não está claro:** quando várias regras incidem na mesm
          +a despesa, a ordem muda o resultado (ex.: se uma duplicata ou 
          +uma despesa sem nota consome o limite do dia).                
      335 +**Decisão:** ordem da seção 8; a primeira recusa encerra a ava
          +liação da despesa; só despesas que chegam ao limite diário o c
          +onsomem.                                                      
      336 +**Justificativa:** despesa recusada não é reembolsável e, port
          +anto, não deve tirar limite de uma despesa válida.            
      337 +**Regra afetada:** todas                                      
      338 +                                                              
      339  ---
      340  
      341  ## 7. Casos de borda
      342  
      343  | Caso | Entrada | Comportamento esperado | Regra |
      344  |---|---|---|---|
       85 -| | | | |                                                     
      345 +| Duas alimentações no mesmo dia somando mais que o limite | 7
          +2,50 e 38,00 em 03/07, fora de viagem | 60,00 `parcial` e 0 `r
          +ecusado` (`limite_diario_excedido`) | RN-009 |                
      346 +| Valor exatamente no limite de nota | 100,00 sem nota, transp
          +orte | não exige nota; limite 80,00 → `parcial` com 80,00 | RN
          +-008, RN-009 |                                                
      347 +| Um centavo acima do limite de nota | 100,01 sem nota | `recu
          +sado`, `nota_fiscal_ausente` | RN-008 |                       
      348 +| Valor exatamente no limite diário | alimentação 60,00 | `apr
          +ovado` com 60,00 | RN-009 |                                   
      349 +| Um centavo acima do limite diário | alimentação 60,01 | `par
          +cial` com 60,00 | RN-009 |                                    
      350 +| Primeiro e último dia do período | datas iguais a `inicio` e
          + a `fim` | dentro do período | RN-005 |                       
      351 +| Um dia fora do período | `fim` + 1 dia | `fora_do_periodo` |
          + RN-005 |                                                     
      352 +| Categoria em maiúsculas | `ALIMENTACAO` | tratada como `alim
          +entacao` | RN-006 |                                           
      353 +| Categoria com acento | `alimentação` | `categoria_fora_da_po
          +litica` | RN-006 |                                            
      354 +| Duplicata exata | mesmos data, categoria, fornecedor, valor 
          +| segunda `duplicata` | RN-007 |                              
      355 +| Quase duplicata | mesmo valor, fornecedor diferente | as dua
          +s avaliadas | RN-007 |                                        
      356 +| Duplicata depois de despesa recusada por nota | 1ª: 150,00 s
          +em nota; 2ª: idêntica | 1ª `nota_fiscal_ausente`; 2ª `duplicat
          +a` | RN-007, seção 8 |                                        
      357 +| Estorno | -45,00 | `valor_invalido`; não altera o dia | RN-0
          +04 |                                                          
      358 +| Valor zero | 0,00 | `valor_invalido` | RN-004 |             
      359 +| Três casas decimais | 33,333 | considerado 33,33 | RN-003 | 
      360 +| Arredondamento da metade | 10,005 | considerado 10,01 | RN-0
          +03 |                                                          
      361 +| Hospedagem com várias diárias na descrição | 480,00 "2 diari
          +as", com nota | 1 diária: `parcial` com 250,00 | RN-012 |     
      362 +| Hospedagem sem nota acima de 100 | 690,00 sem nota | `nota_f
          +iscal_ausente`; data não fica em viagem | RN-008, RN-010 |    
      363 +| Alimentação antes da hospedagem na entrada, mesma data | ali
          +mentação 80,00 e depois hospedagem válida, mesma data | data e
          +m viagem: alimentação `aprovado` com 80,00 (limite 90,00) | RN
          +-010 |                                                        
      364 +| Duas hospedagens na mesma data | 200,00 e 100,00, com nota |
          + 200,00 `aprovado`; 50,00 `parcial` | RN-012, RN-009 |        
      365 +| Campo obrigatório ausente | despesa sem `tem_nota_fiscal` | 
          +`entrada_invalida`; demais processadas | RN-002 |             
      366 +| Lista de despesas vazia | `despesas: []` | `itens` vazio, to
          +tais 0 | RN-001 |                                             
      367 +| Despesa em sábado | 18/07 (sábado) | avaliada normalmente | 
          +AMB-015 |                                                     
      368  
      369  ## 8. Ordem de aplicação das regras
      370  
       89 -<Quando duas regras incidem sobre a mesma despesa, qual vale p
          -rimeiro? A ordem                                              
       90 -muda o resultado. Declarar isso separa spec boa de spec média.
          ->                                                             
      371 +Cada despesa passa pelas etapas abaixo, nesta ordem. A primeir
          +a etapa que a recusa encerra a avaliação dela.                
      372  
      373 +1. **Validação da despesa** — RN-002 (`entrada_invalida`).    
      374 +2. **Arredondamento** — RN-003.                               
      375 +3. **Valor positivo** — RN-004 (`valor_invalido`).            
      376 +4. **Período** — RN-005 (`fora_do_periodo`).                  
      377 +5. **Categoria** — RN-006 (`categoria_fora_da_politica`).     
      378 +6. **Duplicata** — RN-007 (`duplicata`), comparando só com des
          +pesas anteriores que passaram pelas etapas 1 a 5.             
      379 +7. **Nota fiscal** — RN-008 (`nota_fiscal_ausente`).          
      380 +8. **Viagem** — RN-010: com todas as despesas já avaliadas pel
          +as etapas 1 a 7, marca as datas em viagem.                    
      381 +9. **Limite diário** — RN-009, por data e categoria, consumind
          +o o limite na ordem da entrada.                               
      382 +                                                              
      383 +Consequências: despesas recusadas nas etapas 1 a 7 não consome
          +m limite; uma hospedagem recusada nas etapas 1 a 7 não caracte
          +riza viagem; a viagem é determinada antes de qualquer limite s
          +er aplicado.                                                  
      384 +                                                              
      385  ## 9. Critérios de aceite
      386  
      387  O sistema está pronto quando:
      388  
       96 -- [ ] <critério verificável, sem ler código>                  
       97 -- [ ] <...>                                                   
      389 +- [ ] Processa `exemplos/despesas-exemplo.json` e produz exata
          +mente o resultado da tabela abaixo.                           
      390 +- [ ] Cada caso de borda da seção 7 tem um teste automatizado 
          +que passa.                                                    
      391 +- [ ] Cada regra RN-001 a RN-012 tem pelo menos um teste autom
          +atizado que a referencia.                                     
      392 +- [ ] A mesma entrada sempre produz a mesma saída.            
      393 +- [ ] Entradas com erro de arquivo (RN-002) terminam com códig
          +o diferente de 0 e não geram arquivo de saída.                
      394  
      395 +**Resultado esperado para `exemplos/despesas-exemplo.json`** (
          +nenhuma data do exemplo fica em viagem):                      
      396 +                                                              
      397 +| id | considerado | limite | reembolsado | status | motivo | 
      398 +|---|---|---|---|---|---|                                     
      399 +| d-001 | 72,50 | 60,00 | 60,00 | parcial | limite_diario_exce
          +dido |                                                        
      400 +| d-002 | 38,00 | 60,00 | 0,00 | recusado | limite_diario_exce
          +dido |                                                        
      401 +| d-003 | 100,00 | 80,00 | 80,00 | parcial | limite_diario_exc
          +edido |                                                       
      402 +| d-004 | 100,01 | — | 0,00 | recusado | nota_fiscal_ausente |
      403 +| d-005 | 89,00 | — | 0,00 | recusado | categoria_fora_da_poli
          +tica |                                                        
      404 +| d-006 | 54,90 | 60,00 | 54,90 | aprovado | — |              
      405 +| d-007 | 54,90 | — | 0,00 | recusado | duplicata |           
      406 +| d-008 | 41,00 | — | 0,00 | recusado | fora_do_periodo |     
      407 +| d-009 | -45,00 | — | 0,00 | recusado | valor_invalido |     
      408 +| d-010 | 480,00 | 250,00 | 250,00 | parcial | limite_diario_e
          +xcedido |                                                     
      409 +| d-011 | 33,33 | 60,00 | 33,33 | aprovado | — |              
      410 +| d-012 | 47,20 | 60,00 | 47,20 | aprovado | — |              
      411 +| d-013 | 690,00 | — | 0,00 | recusado | nota_fiscal_ausente |
      412 +| d-014 | 61,00 | 60,00 | 60,00 | parcial | limite_diario_exce
          +dido |                                                        
      413 +                                                              
      414 +Totais: `valor_solicitado` = 1.861,84 · `valor_reembolsado` = 
          +585,43 · `valor_glosado` = 1.276,41.                          
      415 +                                                              
      416 +> d-011 (café no hotel em 15/07) não está em viagem: d-010 é u
          +ma diária só em 14/07 (AMB-005).                              
      417 +                                                              
      418  ## 10. O que fica em aberto
      419  
      101 -<Perguntas que você não conseguiu responder e a decisão provis
          -ória que tomou.                                               
      102 -Honestidade aqui vale ponto — spec que finge não ter buraco é 
          -spec que esconde buraco.>                                     
      420 +- **Datas de entrada e saída de hospedagem.** A solução corret
          +a para AMB-005 exige mudar o formato de entrada. Decisão provi
          +sória: um lançamento = uma diária. Consequência conhecida: d-0
          +10 recebe 250,00 de 480,00 mesmo se forem de fato duas diárias
          +.                                                             
      421 +- **Ids repetidos na entrada.** A política não trata. Decisão 
          +provisória: despesas com o mesmo `id` são avaliadas normalment
          +e, cada uma pelo seu conteúdo; a saída repete o id.           
      422 +- **`competencia` inconsistente com `inicio`/`fim`.** Decisão 
          +provisória: o período vale por `inicio` e `fim`; `competencia`
          + só é repetida na saída.                                      
      423 +- **Estorno vinculado a uma despesa.** Se o formato um dia tro
          +uxer referência à despesa original, AMB-013 deve ser revista. 

⏺ Escrevi a primeira versão da specs/001-motor-reembolso/spec.md e ainda não fiz
  o commit, porque as decisões são suas e você precisa revisá-la antes.

  O que ela contém:
  - 12 regras, de RN-001 a RN-012;
  - 16 ambiguidades (as 15 da lista mais a ordem de aplicação das regras), cada
    uma com o texto do RH, a decisão, a justificativa e o tipo da rubrica
    (unidade de aplicação, fronteira ou dado ausente);
  - 23 casos de borda;
  - a ordem das regras em 9 etapas;
  - o formato de saída;
  - o resultado esperado para o exemplo, item por item. Totais: solicitado R$
    1.861,84, reembolsado R$ 585,43 e glosado R$ 1.276,41.

  Consequências das suas decisões que vale olhar com atenção:
  - d-002 (jantar de R$ 38,00 em 03/07) recebe zero. O almoço de R$ 72,50, que
    vem antes na entrada, já consome todo o limite de R$ 60,00 do dia (A1 + A3).
  - d-011 (café no hotel em 15/07) não conta como viagem. Com cada lançamento
    valendo uma diária (A5), a hospedagem d-010 cobre só o dia 14/07. Nenhuma
    data do exemplo fica em viagem.
  - d-003 (R$ 100,00 sem nota) é aceito, mas recebe só R$ 80,00, porque é o
    limite diário de transporte.

  Detalhes que eu precisei decidir e você não aprovou explicitamente. Por favor,
  confirme ou troque cada um:

  1. Formato de saída inteiro: campos, códigos de motivo, status
     aprovado/parcial/recusado, totais e itens na ordem da entrada.
  2. Entrada malformada (RN-002): um problema no arquivo (JSON inválido, período
     inválido) interrompe tudo, sem gerar saída. Um problema numa despesa
     recusa só ela, com o motivo entrada_invalida.
  3. Valor zero também é recusado como valor_invalido. A sua decisão A13 falava
     só de valor negativo.
  4. Acento não é ignorado: alimentação com acento cai em categoria fora da
     política. A A11 aprovou ignorar só maiúsculas, minúsculas e espaços.
  5. Duplicata: o fornecedor é comparado sem diferenciar maiúsculas e
     minúsculas. Uma despesa recusada por falta de nota ainda conta como a
     "primeira" do par, então a cópia seguinte é recusada como duplicata.
  6. Viagem: só uma hospedagem não recusada caracteriza viagem, e isso vale para
     a data inteira, independentemente da ordem das despesas na entrada.
  7. Duas hospedagens na mesma data dividem o mesmo limite de R$ 250,00.
  8. Limite já esgotado: a despesa fica recusado com o motivo
     limite_diario_excedido.
  9. Pontos em aberto (seção 10), com decisão provisória: ids repetidos na
     entrada, e competencia que não bate com inicio/fim.

  Próximos passos, depois do seu ok:
  1. Commit docs(spec): primeira versão com 16 ambiguidades resolvidas. Guardar
     esta versão antes de qualquer revisão dá o "antes e depois" que a seção
     Descrição do relatório pede.
  2. Rodar o spec-adversary contra ela. As perguntas bloqueantes viram decisões
     suas, depois uma nova versão da spec e uma entrada no DECISIONS.md.

  Confirma os nove pontos acima, ou quer mudar algum?

✻ Churned for 3m 20s · done 9:08 PM

❯ preciso que voce analise todos os dados, refine, veja as ambiguidades,        
  padroes e questoes possiveis, e depois passamos passo a passo com eu dando    
  minha visao se faz sentido                                                    

⏺ Vou fazer a análise em duas frentes que se complementam:
  1. A minha leitura: cruzo de novo cada item do despesas-exemplo.json com a
     política e com a spec, procurando padrões e o que cada linha quer testar.
  2. Uma revisão independente pelo spec-adversary, que você criou para isto: ele
     lê só a spec, sem o contexto desta conversa, e tenta burlar as regras.

  No fim, junto as duas numa lista única para passarmos ponto a ponto.

⏺ spec-adversary(Revisão adversarial da spec v1)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ O spec-adversary está rodando. Enquanto isso, já tenho a minha parte da
  análise. O achado mais importante até agora é o d-008: a descrição diz "Almoco
  de abril lancado com atraso". Numa leitura literal, a política fala em
  despesas "lançadas dentro do período". O lançamento foi feito em julho, dentro
  do período; a despesa é que é de abril. Pela regra que adotamos, ele é
  recusado, mas a leitura literal aceitaria. Vale uma discussão.

  Assim que o revisor terminar, junto os achados dele com os meus, sem
  repetições, numa lista ordenada para passarmos um a um.

✻ Worked for 40s · done 9:12 PM

❯ ok, aguardo a lista completa                                                  

⏺ O spec-adversary ainda está rodando. Assim que ele terminar, eu monto a lista
  completa e mando aqui, sem você precisar pedir de novo.

✻ Cooked for 2s · done 9:14 PM

› Message from spec-adversary
  Encontrei 9 problemas. 2 são bloqueantes.

  Critério que usei: marquei como BLOQUEANTE só o que a spec não define ou
  define de forma contraditória, porque aí o código teria de inventar a regra.
  As brechas 3, 4 e 5 têm comportamento literal definido e por isso ficaram como
  PODE ESPERAR. Ainda assim, mudam o valor reembolsado em cenários plausíveis:
  se a decisão mudar depois da implementação, testes e valores mudam.

  Arquivos lidos:
  /Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md,
  /Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md,
  /Users/rafaeltxm/repo/sdd-desafio/exemplos/despesas-exemplo.json,
  /Users/rafaeltxm/repo/sdd-desafio/DESAFIO.md. Não li src/ nem tests/.

  Conferi o cálculo da seção 9 à mão: os totais 1.861,84 / 585,43 / 1.276,41
  batem com as regras. Todas as 9 cláusulas da política do RH têm tratamento na
  spec.

  ---

  ### 1. Item recusado por `entrada_invalida`: `valor_considerado`, `categoria`
  e totais ficam indefinidos — BLOQUEANTE — contradição / ambiguidade

  - **Regra afetada:** RN-002, RN-003, seção 4 (`valor_considerado`,
  `categoria`, `totais.valor_solicitado`), seção 8, caso de borda "Campo
  obrigatório ausente".
  - **Cenário de entrada:** período 2026-07-01 a 2026-07-31; d-1 = {data
  2026-07-03, categoria " Alimentacao ", fornecedor "X", valor 33.333, sem o
  campo `tem_nota_fiscal`}.
  - **Comportamento pela interpretação atual:** indefinido.
    - A seção 8 diz que a primeira etapa que recusa encerra a avaliação. A
  validação é a etapa 1 e o arredondamento é a etapa 2, então RN-003 nunca roda
  para d-1.
    - A seção 4 diz que `valor_considerado` só é nulo "se ausente ou não
  numérico". Por essa leitura ele seria 33.33.
    - Resultado possível A: `valor_considerado` = 33.33, entra em
  `valor_solicitado` e `valor_glosado` = 33.33.
    - Resultado possível B: `valor_considerado` nulo (ou 33.333), fica fora de
  `valor_solicitado` e o glosado é 0.
    - O mesmo vale para `categoria`: a normalização é a etapa 5, que não foi
  alcançada. A saída pode ser "alimentacao" ou " Alimentacao ".
  - **Por que é um problema:** o caso de borda da seção 7 ("despesa sem
  `tem_nota_fiscal`") exige teste automatizado, e os totais desse teste dependem
  da leitura escolhida. A expressão "valor válido (maior que zero)" pode
  significar "positivo" ou "passou na validação".
  - **Pergunta para decisão:** quando uma despesa é recusada na etapa 1 mas o
  `valor` é numérico e positivo, `valor_considerado` é preenchido (arredondado
  ou não), esse valor entra em `valor_solicitado`/`valor_glosado`, e `categoria`
  sai normalizada ou como veio?

  ### 2. `valor_informado` "exatamente como veio" contradiz "no máximo 2 casas
  decimais" — BLOQUEANTE — contradição

  - **Regra afetada:** seção 4 (`itens[].valor_informado` versus a frase "Todos
  os valores monetários da saída são em reais, com no máximo 2 casas decimais e
  exatos ao centavo").
  - **Cenário de entrada:** d-011 do próprio exemplo, com valor 33.333.
  - **Comportamento pela interpretação atual:** indefinido.
    - Pela definição do campo, `valor_informado` = 33.333.
    - Pela regra geral de valores monetários, ele teria no máximo 2 casas, o que
  exigiria arredondar ou truncar e deixaria de ser "como veio".
    - Variação na mesma linha: "exatamente como veio" também não fica claro para
  72.50 versus 72.5. O JSON não preserva a forma textual do número.
  - **Por que é um problema:** o arquivo de exemplo, que é critério de aceite,
  cai exatamente nesse caso. O teste de contrato teria de escolher uma das duas
  leituras.
  - **Pergunta para decisão:** `valor_informado` está isento da regra de 2 casas
  decimais? E "exatamente como veio" se refere ao valor numérico ou à
  representação textual?

  ### 3. A exigência de nota fiscal é contornável fracionando ou subdeclarando a
  despesa — PODE ESPERAR (comportamento definido, impacto alto) — brecha

  - **Regra afetada:** RN-008, AMB-008 (justificativa), AMB-001 (justificativa
  antifracionamento).
  - **Cenário de entrada:**
    - (a) Hospedagem em 2026-07-14, fornecedor "Hotel Y", três lançamentos sem
  nota: 100,00, 99,99 e 50,01. O mesmo cenário com um único lançamento de 250,00
  sem nota é a comparação.
    - (b) Alimentação em 2026-07-03, fora de viagem, sem nota: um lançamento de
  150,00, comparado com dois lançamentos de 100,00 e 50,00, ou com um único
  lançamento declarado como 100,00.
  - **Comportamento pela interpretação atual:**
    - (a) Os três lançamentos passam por RN-008, cada um com valor ≤ 100. Não
  são duplicatas porque os valores diferem. O reembolso é 250,00 sem nenhuma
  nota. O lançamento único de 250,00 seria recusado com 0.
    - (b) O lançamento de 150,00 é recusado com 0. Os dois lançamentos, ou o
  lançamento de 100,00, recebem 60,00.
  - **Por que é uma brecha:**
    - A AMB-008 escolheu comparar o valor individual para impedir que o limite
  "esconda" a falta de nota. Só que fracionar produz o mesmo efeito.
    - A AMB-001 justifica o limite por soma justamente para evitar
  fracionamento, e RN-008 não segue a mesma lógica.
    - Para alimentação (limite de 60 a 90) e transporte fora de viagem (80), o
  limite é sempre ≤ 100. Basta lançar ≤ 100,00 para receber o limite inteiro sem
  nota. Na prática, RN-008 só funciona como controle para hospedagem e para
  transporte em viagem.
  - **Pergunta para decisão:** a exigência de nota deve continuar sendo avaliada
  só por lançamento individual, sabendo que fracionar ou subdeclarar a
  contorna? Ou deve considerar algum agrupamento, como data + categoria ou data
  + categoria + fornecedor?

  ### 4. "Em viagem" pode ser ativado por uma hospedagem de valor irrisório e
  sem nota — PODE ESPERAR (comportamento definido, impacto alto) — brecha

  - **Regra afetada:** RN-010, AMB-004, RN-012.
  - **Cenário de entrada:** em 2026-07-03:
    - hospedagem 0,01, sem nota, fornecedor "Z";
    - alimentação 90,00, com nota;
    - transporte_urbano 120,00, com nota.
  - **Comportamento pela interpretação atual:** a hospedagem de 0,01 passa por
  RN-004 e RN-008 (≤ 100 dispensa nota) e chega ao limite, então a data fica em
  viagem. O reembolso é 0,01 + 90,00 + 120,00 = 210,01. Sem a hospedagem, seria
  60,00 + 80,00 = 140,00. Gastar 0,01 aumenta o teto em 70,00. O mesmo acontece
  com qualquer hospedagem até 100,00 sem nota.
  - **Variação no sentido oposto (subreembolso):**
    - Hospedagem de 1 noite lançada em 14/07; alimentação de 80,00 em 15/07, no
  dia do retorno → 15/07 não está em viagem e o reembolso é 60,00.
    - Se a hospedagem for paga e lançada no checkout (15/07), é 14/07 que deixa
  de estar em viagem.
    - A spec não diz se a `data` da hospedagem é a noite ou o pagamento. Hoje o
  efeito só aparece como consequência registrada para d-010, que tem várias
  diárias.
  - **Por que é uma brecha:** a AMB-004 trata a hospedagem como "evidência
  objetiva" de viagem, mas a spec aceita como prova um lançamento sem nota e de
  qualquer valor positivo.
  - **Pergunta para decisão:** qualquer hospedagem que chega ao limite deve
  caracterizar viagem, ou a caracterização exige alguma condição adicional? Além
  disso, a `data` de uma hospedagem representa a noite de pernoite ou a data do
  pagamento?

  ### 5. Relançar uma despesa já corrigida com nota é recusado como duplicata, e
  o resultado depende da ordem — PODE ESPERAR — brecha / inconsistência

  - **Regra afetada:** RN-007, RN-008, seção 8 (etapa 6 antes da 7), caso de
  borda "Duplicata depois de despesa recusada por nota".
  - **Cenário de entrada:** transporte_urbano em 2026-07-20 (dia em viagem,
  limite 120), fornecedor "TaxiApp":
    - d-1: 110,00, `tem_nota_fiscal` false;
    - d-2: 110,00, `tem_nota_fiscal` true. É o mesmo gasto relançado com a nota.
  - **Comportamento pela interpretação atual:**
    - `tem_nota_fiscal` não faz parte da chave de duplicata. d-1 é recusada por
  `nota_fiscal_ausente` e d-2 por `duplicata`. Reembolso: 0.
    - Com a ordem invertida, d-2 é aprovada com 110,00 e d-1 vira duplicata.
    - Contraste: se d-1 tivesse sido recusada por `entrada_invalida` (por
  exemplo, sem `tem_nota_fiscal`), ela não participaria da comparação e d-2
  seria aprovada.
  - **Por que é um problema:** o mesmo conjunto de despesas rende 0 ou 110,00
  dependendo da ordem. Corrigir um erro de validação é aceito, mas corrigir a
  falta de nota não é. O caso de borda da seção 7 só cobre a cópia idêntica (as
  duas sem nota).
  - **Pergunta para decisão:** uma despesa recusada por `nota_fiscal_ausente`
  deve impedir que um lançamento idêntico com nota seja avaliado? O valor de
  `tem_nota_fiscal` deve influenciar qual ocorrência vale?

  ### 6. Quase-duplicatas escapam com variações mínimas — PODE ESPERAR — brecha

  - **Regra afetada:** RN-007, AMB-010.
  - **Cenário de entrada:** alimentação 54,90 com nota, "Bistro Central", em
  2026-07-09. Depois, o mesmo gasto relançado com uma destas variações:
    - (a) data 2026-07-10;
    - (b) fornecedor "Bistrô Central" ou "Bistro  Central" (espaço duplo no
  meio);
    - (c) valor 54,91.
  - **Comportamento pela interpretação atual:** nenhuma das variações é
  duplicata. Em (a), o gasto vai para outro dia com saldo cheio e as duas
  despesas recebem 54,90, total de 109,80. Em (b) e (c), a segunda despesa
  recebe o saldo do dia (5,10 ou 5,09).
  - **Por que é uma brecha:** a chave exige igualdade exata de data, valor e
  fornecedor (só ignora espaços nas pontas e maiúsculas/minúsculas). O ganho é
  maior quando o relançamento vai para uma data vizinha sem gasto. A spec não
  diz que isso é aceito conscientemente.
  - **Pergunta para decisão:** é intencional que despesas idênticas em datas
  diferentes, ou com fornecedor de grafia levemente diferente (acento, espaços
  internos), nunca sejam tratadas como duplicata?

  ### 7. Nota da seção 9 contradiz RN-010 sobre d-010 — PODE ESPERAR —
  contradição

  - **Regra afetada:** RN-010, RN-012 (aceite), seção 9 ("nenhuma data do
  exemplo fica em viagem").
  - **Cenário de entrada:** d-010 do exemplo: hospedagem de 480,00 com nota, em
  2026-07-14.
  - **Comportamento pela interpretação atual:**
    - d-010 chega ao limite diário, então por RN-010 o dia 14/07 está em viagem
  e `em_viagem` de d-010 é true.
    - O aceite de RN-012 confirma: "data em viagem só no dia da despesa".
    - A seção 9 afirma o contrário: nenhuma data do exemplo fica em viagem.
    - Os valores não mudam, porque não há alimentação nem transporte em 14/07.
  Muda apenas o campo `em_viagem` de d-010.
  - **Por que é um problema:** um teste de aceite que verifique `em_viagem` no
  exemplo teria duas fontes conflitantes na spec.
  - **Pergunta para decisão:** qual é o `em_viagem` esperado para d-010 no
  resultado do exemplo, e o texto da seção 9 deve continuar como está?

  ### 8. Entrada estruturalmente malformada sem resultado definido — PODE
  ESPERAR — lacuna

  - **Regra afetada:** RN-002, seção 3 ("Não aceita campos adicionais..."),
  seção 4 (tipos de `itens[].id`, `itens[].data`, `itens[].categoria`,
  `colaborador`).
  - **Cenário de entrada:**
    - (a) `colaborador` ausente ou sem `id`/`nome`. A tabela de entrada marca
  esses campos como obrigatórios, mas RN-002 não os lista nem como erro de
  arquivo nem como despesa inválida.
    - (b) um elemento de `despesas` que é `null`, número ou string, e não um
  objeto.
    - (c) uma despesa sem `id` ou sem `data`. A saída declara esses campos como
  "texto", sem previsão de nulo.
    - (d) uma despesa com um campo extra, como `"noites": 2` ou
  `"data_checkout": "..."`.
  - **Comportamento pela interpretação atual:** indefinido.
    - (a) Pode ser erro de arquivo (exit ≠ 0) ou processamento normal com
  colaborador nulo na saída.
    - (b) e (c) Presumivelmente `entrada_invalida`, mas o schema de saída não
  consegue representar o item.
    - (d) "Não aceita" pode significar recusa, como `entrada_invalida` ou erro
  de arquivo, ou apenas que o campo é ignorado. A RN-002 lista as condições de
  invalidez de forma exaustiva e não inclui campos extras. No caso de
  hospedagem, uma leitura dá 0 e a outra dá até 250,00.
  - **Por que é um problema:** o código teria de escolher entre gerar ou não a
  saída e qual valor colocar em campos declarados como não nulos. São casos
  improváveis porque o formato de entrada é fixo.
  - **Pergunta para decisão:** qual é o resultado para `colaborador` ausente,
  para um elemento de `despesas` que não é objeto, para `id`/`data` ausentes
  (que tipo esses campos assumem na saída) e para campos não previstos numa
  despesa?

  ### 9. DECISIONS.md sem nenhuma entrada, enquanto a spec tem alterações não
  commitadas — PODE ESPERAR — lacuna (processo)

  - **Regra afetada:** nenhuma regra de negócio. Afeta a rastreabilidade de spec
  → DECISIONS.
  - **Cenário:** o git status mostra `spec.md` modificado em relação ao commit
  anterior. O DECISIONS.md tem só os placeholders do template (D-001 e D-002
  vazios). A seção 10 da spec também traz "decisões provisórias" (ids repetidos,
  `competencia` inconsistente) que não estão registradas em lugar nenhum além
  dela.
  - **Comportamento atual:** não dá para saber, pelos artefatos, o que mudou
  entre a versão commitada e esta 1.0 nem por quê. Não verifiquei o diff porque
  o escopo era só leitura dos arquivos.
  - **Por que é um problema:** se esta versão altera regras de uma versão já
  commitada, a mudança não tem registro. Isso contraria o próprio cabeçalho do
  DECISIONS.md.
  - **Pergunta para decisão:** esta versão 1.0 é tratada como versão inicial,
  sem entrada no log, ou as diferenças em relação à versão commitada precisam
  ser registradas no DECISIONS.md?

  ---

  **Decidir antes da implementação:** 1, 2

  **Pode ser decidido depois:** 3, 4, 5, 6, 7, 8, 9 (3, 4 e 5 alteram o valor
  reembolsado em cenários plausíveis)

⏺ Lista completa: análise dos dados mais a revisão do spec-adversary

  O revisor conferiu o resultado esperado do exemplo à mão e os totais (1.861,84
  / 585,43 / 1.276,41) batem. Ele também confirmou que as 9 cláusulas da
  política têm tratamento na spec. Encontrou 9 problemas, 2 bloqueantes. Juntei
  com os meus achados, sem repetições: são 13 pontos em 3 blocos.

  Um registro para o relatório: o item 11 é um erro meu que o revisor pegou.
  Escrevi na seção 9 que "nenhuma data do exemplo fica em viagem", mas pela
  própria RN-010 o dia 14/07 fica, por causa do d-010. É um caso concreto para a
  seção de Discernimento, com o trecho na sessão exportada.

  Bloco A: regras de negócio (mudam valores)

  1. d-008, "lançado com atraso" (meu)
  - Problema: a política diz "lançadas dentro do período". Este almoço foi
    lançado em julho, mas é de abril. Numa leitura literal, seria aceito.
  - Recomendação: manter a data da despesa como critério. Todo item da entrada
    já está, por definição, lançado no relatório do período. Se "lançada"
    quisesse dizer "estar no relatório", a regra 7 nunca recusaria nada e seria
    inútil.

  2. O que caracteriza "em viagem" (revisor nº 4 e meu)
  - (a) Hospedagem irrisória: uma hospedagem de R$ 0,01 sem nota ativa a viagem
    e aumenta o teto do dia em R$ 70,00.
  - (b) Dia do checkout: uma diária em 14/07 significa pernoite de 14 para 15. O
    café no hotel em 15/07 (d-011) aponta claramente para isso.
  - (c) Outros indícios: "corrida aeroporto" (d-003) também sugere viagem, mas
    está só na descrição, que não lemos.
  - Opções:
    - para (a): aceitar a brecha conscientemente, ou exigir hospedagem com nota 
      fiscal para caracterizar viagem;
    - para (b): a viagem cobre só a data da diária, ou a data da diária e o dia
      seguinte.

  3. Nota fiscal contornável fracionando a despesa (revisor nº 3 e meu)
  - Problema: três lançamentos de hospedagem sem nota (100,00 + 99,99 + 50,01)
    recebem R$ 250,00. Um lançamento único de 250,00 sem nota receberia zero.
    Para alimentação e transporte fora de viagem, o limite já é menor que 100,
    então a exigência de nota quase nunca atua.
  - Recomendação: manter a verificação por lançamento e registrar a brecha como 
    conhecida. Agrupar por dia recusaria despesas pequenas legítimas sem nota
    (duas corridas de 60,00, por exemplo).
  - Para deixar explícito na spec: o valor de R$ 100 da nota não é ampliado em
    viagem. Hoje a spec só deixa isso implícito.

  4. Duplicata contra relançamento com nota (revisor nº 5 e nº 6)
  - Problema: um táxi de 110,00 sem nota, seguido do mesmo táxi relançado com
    nota, dá zero, porque o segundo vira duplicata. Na ordem inversa, dá 110,00.
  - Recomendação: inverter as etapas 6 e 7. A nota fiscal é verificada antes da
    duplicata, e uma despesa recusada por falta de nota sai da comparação.
    Assim:
    - o relançamento com nota é aprovado, em qualquer ordem;
    - duas cópias sem nota acima de 100 são as duas recusadas por nota;
    - duas cópias de até 100 continuam sendo uma aprovada e outra duplicata.
  - Quase-duplicatas (data vizinha, "Bistrô" com acento, 54,91): aceitar
    conscientemente e registrar. Comparação aproximada seria inventar regra.

  5. Valor zero e acentos na categoria (pontos meus ainda não aprovados)
  - Valor zero: é recusado como valor_invalido. Recomendo manter.
  - Acento: alimentação com acento hoje cai em categoria fora da política.
    Recomendo passar a ignorar acentos também, pelo mesmo raciocínio das
    maiúsculas: é a mesma categoria, sem dúvida nenhuma.

  6. d-001, "Almoço com cliente" (meu, impacto baixo)
  - Problema: é uma refeição de representação, possivelmente para mais de uma
    pessoa. A política não tem essa categoria.
  - Recomendação: tratar como alimentação normal, com o limite do colaborador, e
    registrar.

  Bloco B: contrato de saída e validação (os 2 bloqueantes do revisor estão 
  aqui)

  7. Despesa recusada por entrada_invalida, revisor nº 1, ⚠️ bloqueante
  - Problema: a spec não define o que preencher em valor_considerado e
    categoria, nem se o valor entra nos totais.
  - Recomendação: valor_considerado nulo, categoria como veio, fora dos totais.

  8. valor_informado "exatamente como veio" contra "no máximo 2 casas", revisor 
  nº 2, ⚠️ bloqueante
  - Problema: as duas regras se contradizem no d-011, que tem 33.333.
  - Recomendação: o campo fica isento da regra de 2 casas e guarda o valor
    numérico recebido (33.333). O formato do texto, como 72.50 ou 72.5, não é
    garantido.

  9. Entrada malformada (revisor nº 8)
  - Recomendação:
    - colaborador ausente: erro de arquivo;
    - um elemento de despesas que não é objeto: entrada_invalida;
    - id ou data ausentes: podem ser nulos na saída;
    - campos extras: ignorados.

  10. Formato de saída e limite esgotado (meus pontos 1 e 8)
  - Confirmar os campos, os códigos de motivo, os três status e os totais.
  - Confirmar que uma despesa sem saldo de limite fica recusado com o motivo
    limite_diario_excedido.

  Bloco C: correções e processo

  11. Erro na seção 9 (revisor nº 7): corrigir para em_viagem = true no d-010
  (14/07). Não exige decisão.

  12. DECISIONS.md vazio (revisor nº 9)
  - Recomendação: a v1.0 é a versão inicial. Fazemos o commit dela antes das
    mudanças, para guardar o "antes" que a seção Descrição do relatório pede, e
    todas as mudanças desta revisão viram a entrada D-001.

  13. Pontos em aberto da seção 10 (ids repetidos, competencia inconsistente):
  manter as decisões provisórias.

  ---

  Ordem proposta: começar pelo Bloco A, em que as decisões são de negócio e são
  suas, e deixar os Blocos B e C para o fim, porque são mais técnicos.

  Ponto 1, d-008: você concorda em manter a data da despesa como critério de
  período (recusar), ou prefere a leitura literal de "lançada"?

✻ Crunched for 5m 1s · done 9:16 PM

⏺ Agent "Revisão adversarial da spec v1" finished · 3m 37s

❯ vamos passando por cada cenario e vou falando                                 

⏺ Combinado. Vou apresentar um ponto por vez, com o cenário concreto, e espero a
  sua visão antes de seguir.

  ---

  Ponto 1 de 13: d-008, "lançado com atraso"

  O dado:
  d-008  data 2026-04-15  alimentacao  41,00  com nota
         descrição: "Almoco de abril lancado com atraso"
  período do relatório: 2026-07-01 a 2026-07-31

  A política: "Despesas devem ser lançadas dentro do período de competência."

  As duas leituras:

  ┌────────────┬────────────────────────────┬──────────────────────────────┐
  │  Leitura   │        O que conta         │            d-008             │
  ├────────────┼────────────────────────────┼──────────────────────────────┤
  │ A, atual   │ a data da despesa precisa  │ ❌ recusado                  │
  │ da spec    │ estar dentro do período    │ (fora_do_periodo), R$ 0,00   │
  ├────────────┼────────────────────────────┼──────────────────────────────┤
  │ B, literal │ a despesa precisa ter sido │ ✅ seguiria para as outras   │
  │            │  lançada dentro do período │ regras, R$ 41,00             │
  └────────────┴────────────────────────────┴──────────────────────────────┘

  Por que recomendo a A: a entrada não tem data de lançamento. Para a leitura B,
  teríamos de supor que tudo o que está no relatório de julho foi lançado em
  julho. Aí a regra 7 da política nunca recusaria nada e seria letra morta, e
  despesas de qualquer mês antigo entrariam sem limite de tempo.

  O custo da A: quem esquece de lançar uma despesa no mês certo perde o
  reembolso, porque não existe regra de tolerância para lançamento atrasado. Se
  você quiser uma tolerância (aceitar despesas de até N dias antes do início do
  período, por exemplo), seria uma regra nova, e o valor de N teria de ser
  decidido por você, já que a política não dá base para ele.

  O que você acha: A (recusar), B (aceitar) ou outra visão?

✻ Baked for 8s · done 9:18 PM

❯ A, recusar pela data da despesa                                               

⏺ ✅ Ponto 1 decidido: A. O critério é a data da despesa, e o d-008 é recusado.
  Vou reforçar a justificativa na AMB-009 com o argumento de que a regra viraria
  letra morta.

  ---

  Ponto 2 de 13: o que caracteriza "em viagem"

  Hoje a spec diz que uma data está em viagem se há uma hospedagem válida nessa 
  data. Há duas perguntas separadas.

  2a. Uma hospedagem de qualquer valor, sem nota, prova viagem?

  03/07  hospedagem         0,01  sem nota   ← ativa "em viagem"
  03/07  alimentacao       90,00  com nota
  03/07  transporte_urbano 120,00 com nota

  ┌─────────────────────────────┬───────────────┬──────────────────────────┐
  │            Opção            │   03/07 em    │        Reembolso         │
  │                             │    viagem?    │                          │
  ├─────────────────────────────┼───────────────┼──────────────────────────┤
  │ Atual: qualquer hospedagem  │ sim           │ 0,01 + 90,00 + 120,00 =  │
  │ válida                      │               │ 210,01                   │
  ├─────────────────────────────┼───────────────┼──────────────────────────┤
  │ Só hospedagem com nota      │ não           │ 0,01 + 60,00 + 80,00 =   │
  │ fiscal                      │               │ 140,01                   │
  └─────────────────────────────┴───────────────┴──────────────────────────┘

  Gastando R$ 0,01 numa "hospedagem", o colaborador ganha R$ 70,00 a mais de
  teto. Exigir nota fiscal fecha a brecha, porque uma hospedagem com nota é
  evidência real. O custo: uma hospedagem legítima de até R$ 100 sem nota (uma
  pousada barata, por exemplo) é reembolsada, mas não amplia os limites do dia.

  2b. Uma diária cobre só o dia do pernoite ou também o dia seguinte?

  d-010  14/07  hospedagem  480,00  "Hotel Rio - 2 diarias"   (hotel Copa Sul)
  d-011  15/07  alimentacao  33,33  "Cafe da manha hotel"     (hotel Copa Sul)

  ┌──────────────────────────┬─────────────┬───────────────────────────────┐
  │          Opção           │  Dias em    │            Efeito             │
  │                          │   viagem    │                               │
  ├──────────────────────────┼─────────────┼───────────────────────────────┤
  │ Atual: só a data da      │ 14/07       │ 15/07 tem limites normais (60 │
  │ diária                   │             │  e 80)                        │
  ├──────────────────────────┼─────────────┼───────────────────────────────┤
  │ Data da diária e o dia   │ 14/07 e     │ 15/07 tem limites ampliados   │
  │ seguinte                 │ 15/07       │ (90 e 120)                    │
  └──────────────────────────┴─────────────┴───────────────────────────────┘

  Uma diária em 14/07 é a noite de 14 para 15, e o colaborador acorda em viagem
  no dia 15, o dia do checkout. O próprio exemplo mostra isso: café da manhã no
  mesmo hotel em 15/07. No exemplo não muda nenhum valor, porque o d-011 (R$
  33,33) fica abaixo dos dois limites. Mas muda o campo em_viagem, e muda
  valores em casos ocultos (um almoço de R$ 80 no dia do retorno, por exemplo).

  A segunda opção é coerente com a decisão de "um lançamento = uma diária": ela
  não lê a descrição, só assume que toda diária tem uma noite e, portanto, um
  dia seguinte.

  Minha recomendação: em 2a, exigir nota fiscal; em 2b, considerar a data da
  diária e o dia seguinte.

  Qual é a sua visão sobre 2a e 2b?

✻ Cooked for 11s · done 9:19 PM

❯ 2a exigir nota, 2b diária e dia seguinte                                      

⏺ ✅ Ponto 2 decidido. Para caracterizar viagem, a hospedagem precisa ter nota
  fiscal. A viagem cobre a data da diária e o dia seguinte.

  Uma consequência que vou registrar como caso de borda: uma hospedagem em
  30/06, fora do período, é recusada e por isso não coloca o dia 01/07 em
  viagem. Ela só valeria como prova se fosse aceita. Isso é coerente com a sua
  decisão 2a. Se preferir outro tratamento, me avise.

  ---

  Ponto 3 de 13: fracionar para escapar da nota fiscal

  Hoje a nota é verificada lançamento por lançamento: só é exigida quando um
  único lançamento passa de R$ 100.

  Cenário A — hospedagem fracionada, 14/07, sem nota:
    100,00 + 99,99 + 50,01   → cada um ≤ 100, nenhum exige nota → recebe 250,00
  Cenário B — mesma hospedagem num lançamento só, sem nota:
    250,00                   → exige nota → recebe 0,00

  Opção: Atual: por lançamento
  Como funciona: cada despesa acima de 100 exige nota
  Cenário A: 250,00
  Efeito colateral: brecha do fracionamento, registrada como conhecida
  ────────────────────────────────────────
  Opção: Pela soma do dia na categoria
  Como funciona: se a soma do dia passa de 100, todas as despesas daquele dia e
  categoria exigem nota
  Cenário A: 0,00
  Efeito colateral: duas corridas legítimas de 60,00 sem nota (soma 120) seriam
  as duas recusadas

  Há um detalhe que reduz a brecha: fora de viagem, os limites de alimentação
  (60) e de transporte (80) já são menores que 100. Fracionar essas despesas não
  rende mais do que o limite do dia. A brecha só gera dinheiro de verdade na
  hospedagem (limite de 250) e no transporte em viagem (limite de 120).

  Minha recomendação: manter a verificação por lançamento e registrar a brecha
  na spec como risco conhecido e aceito. A política diz "nota fiscal obrigatória
  acima de R$ 100", e a leitura mais natural é por despesa. Pela soma, despesas
  pequenas e honestas seriam punidas.

  3b. Para deixar explícito na spec

  O valor de R$ 100 da nota não muda em viagem: a ampliação de 50% vale só para
  os limites diários. Confirma?

  Qual é a sua visão sobre 3 e 3b?

✻ Baked for 11s · done 9:21 PM

❯ 3 manter por lançamento, 3b confirmo                                          

⏺ ✅ Ponto 3 decidido. A nota continua sendo verificada por lançamento, e a
  brecha do fracionamento fica registrada como risco conhecido e aceito. 3b: o
  valor de R$ 100 não muda em viagem.

  ---

  Ponto 4 de 13: duplicata e relançamento com nota

  4a. Despesa relançada com nota fiscal

  20/07 (em viagem, limite de transporte 120,00), fornecedor TaxiApp:
    d-1  transporte  110,00  SEM nota
    d-2  transporte  110,00  COM nota   ← o mesmo táxi, relançado com a nota

  Hoje a duplicata é verificada antes da nota fiscal (etapa 6), e a nota depois
  (etapa 7):

  ┌──────────────────┬──────────────────────────┬───────────┬──────────────┐
  │      Ordem       │           d-1            │    d-2    │    Total     │
  ├──────────────────┼──────────────────────────┼───────────┼──────────────┤
  │ Atual: duplicata │ nota_fiscal_ausente      │ duplicata │ 0,00         │
  │  antes da nota   │                          │  ❌       │              │
  ├──────────────────┼──────────────────────────┼───────────┼──────────────┤
  │ Atual, com a     │                          │           │              │
  │ ordem da entrada │ duplicata                │ aprovado  │ 110,00       │
  │  invertida       │                          │           │              │
  ├──────────────────┼──────────────────────────┼───────────┼──────────────┤
  │ Proposta: nota   │ nota_fiscal_ausente (sai │ aprovado  │ 110,00 em    │
  │ antes da         │  da comparação)          │ ✅        │ qualquer     │
  │ duplicata        │                          │           │ ordem        │
  └──────────────────┴──────────────────────────┴───────────┴──────────────┘

  Com a proposta, o resultado não depende mais da ordem da entrada, e corrigir a
  falta de nota passa a funcionar. Os outros casos continuam iguais:
  - duas cópias idênticas sem nota acima de 100: as duas recusadas por nota;
  - duas cópias idênticas de até 100 (o d-006 e o d-007 do exemplo): uma
    aprovada e a outra recusada como duplicata. O exemplo não muda.

  4b. Quase-duplicatas

  09/07  alimentacao  54,90  "Bistro Central"
  ...e o mesmo almoço relançado com UMA variação:
    (a) data 10/07         → não é duplicata, recebe 54,90 de novo
    (b) "Bistrô Central"   → não é duplicata, recebe o saldo do dia (5,10)
    (c) valor 54,91        → não é duplicata, recebe o saldo do dia (5,09)

  Detectar esses casos exigiria uma comparação aproximada (datas vizinhas, nomes
  "parecidos"), e qualquer critério de "parecido" seria inventar regra, com o
  risco de recusar despesas legítimas, como dois almoços no mesmo restaurante em
  dias seguidos.

  Minha recomendação:
  - 4a: inverter a ordem, verificando a nota antes da duplicata.
  - 4b: manter a comparação exata e registrar as quase-duplicatas como risco
    conhecido.

  Uma pergunta ligada a isso: no fornecedor, ignorar acentos também (Bistrô
  igual a Bistro)? Isso depende da sua resposta no ponto 5, que é a mesma
  questão para a categoria. Se você decidir ignorar acentos lá, faz sentido
  aplicar aqui também.

  Qual é a sua visão sobre 4a e 4b?

✻ Cogitated for 10s · done 9:29 PM

❯ 4a inverter a ordem, 4b manter exata                                          

⏺ ✅ Ponto 4 decidido.
  - 4a: a nota fiscal é verificada antes da duplicata, e uma despesa recusada
    por falta de nota sai da comparação.
  - 4b: a comparação continua exata, e as quase-duplicatas ficam registradas
    como risco conhecido.

  ---

  Ponto 5 de 13: valor zero e acentos

  5a. Despesa com valor zero

  d-x  12/07  alimentacao  0,00  com nota
  d-y  12/07  alimentacao  0,004 com nota   → arredonda para 0,00

  A sua decisão A13 tratou o valor negativo (estorno) como inválido. O zero
  ficou de fora.

  ┌───────────────────────────┬─────────────────────────────────────────────┐
  │           Opção           │                  Resultado                  │
  ├───────────────────────────┼─────────────────────────────────────────────┤
  │ Recusar como              │ aparece na saída como recusado, com motivo  │
  │ valor_invalido (como está │ explícito                                   │
  │  na spec)                 │                                             │
  ├───────────────────────────┼─────────────────────────────────────────────┤
  │                           │ aparece como "aprovado" sem reembolsar      │
  │ Aprovar com R$ 0,00       │ nada, o que é estranho, porque status e     │
  │                           │ valor ficam incoerentes                     │
  └───────────────────────────┴─────────────────────────────────────────────┘

  Minha recomendação: recusar. Uma despesa de R$ 0,00 não é despesa,
  provavelmente é um erro de lançamento.

  5b. Acentos na categoria e no fornecedor

  categoria "alimentação"           (com ç e ã)
  fornecedor "Bistrô Central" vs "Bistro Central"

  ┌───────────────────────┬────────────────────────────┬────────────────────┐
  │         Opção         │        alimentação         │    "Bistrô" e      │
  │                       │                            │      "Bistro"      │
  ├───────────────────────┼────────────────────────────┼────────────────────┤
  │ Atual: ignorar só     │                            │                    │
  │ maiúsculas e          │ ❌                         │ são fornecedores   │
  │ minúsculas e os       │ categoria_fora_da_politica │ diferentes         │
  │ espaços nas pontas    │                            │                    │
  ├───────────────────────┼────────────────────────────┼────────────────────┤
  │ Ignorar também os     │                            │ mesmo fornecedor,  │
  │ acentos               │ ✅ vira alimentacao        │ então pode ser     │
  │                       │                            │ duplicata          │
  └───────────────────────┴────────────────────────────┴────────────────────┘

  No exemplo, o d-014 usa ALIMENTACAO em maiúsculas: o caso testado é variação
  de escrita. Os casos ocultos do instrutor "exercitam as mesmas ambiguidades
  com valores diferentes", então uma variação com acento é plausível. Recusar
  alimentação seria punir o colaborador por escrever a palavra corretamente em
  português.

  Minha recomendação: ignorar acentos também, tanto na categoria quanto no
  fornecedor (pela mesma regra de normalização).

  Qual é a sua visão sobre 5a e 5b?

✻ Cogitated for 8s · done 9:31 PM

❯ 5a recusar, 5b ignorar acentos também                                         

⏺ ✅ Ponto 5 decidido.
  - 5a: valor zero é recusado como valor_invalido.
  - 5b: acentos são ignorados na categoria e no fornecedor, junto com
    maiúsculas, minúsculas e os espaços nas pontas. A mesma regra vale para os
    dois.

  ---

  Ponto 6 de 13: d-001, "Almoço com cliente"

  d-001  03/07  alimentacao  72,50  "Almoco com cliente"  (Restaurante Tavola)
  d-002  03/07  alimentacao  38,00  "Jantar apos reuniao" (Cantina do Porto)

  O valor alto (R$ 72,50) sugere que o colaborador pagou também a refeição do
  cliente. A política não tem categoria de representação (refeição com cliente)
  nem limite por pessoa.

  ┌────────────────┬───────────────┬────────────────────────────┬──────────┐
  │     Opção      │ Como funciona │           d-001            │  d-002   │
  ├────────────────┼───────────────┼────────────────────────────┼──────────┤
  │ Tratar como    │ limite de     │                            │          │
  │ alimentação    │ 60,00 do      │ 60,00 parcial              │ 0,00     │
  │ normal (spec   │ colaborador   │                            │ recusado │
  │ atual)         │ para o dia    │                            │          │
  ├────────────────┼───────────────┼────────────────────────────┼──────────┤
  │                │ o limite é    │                            │          │
  │ Limite por     │ multiplicado  │ ?                          │ ?        │
  │ pessoa         │ pelo número   │                            │          │
  │                │ de pessoas    │                            │          │
  ├────────────────┼───────────────┼────────────────────────────┼──────────┤
  │ Categoria de   │ fora das      │                            │ segue    │
  │ representação  │ categorias da │ categoria_fora_da_politica │ normal   │
  │                │  política     │                            │          │
  └────────────────┴───────────────┴────────────────────────────┴──────────┘

  Com limite por pessoa, a entrada não tem o número de pessoas: teríamos de ler
  a descrição, e você já decidiu não interpretar texto livre (ponto A5). Com
  categoria de representação, a categoria do lançamento é alimentacao, e
  transformá-la em outra também exigiria ler a descrição.

  Minha recomendação: tratar como alimentação normal e registrar na spec que a
  política não prevê representação. Fica como recomendação de evolução, da mesma
  forma que as datas de entrada e saída de hospedagem.

  Repare na consequência que já aparece na spec: o almoço consome todo o limite
  do dia, e o jantar d-002 recebe zero.

  Qual é a sua visão?

✻ Cogitated for 7s · done 9:32 PM

❯ alimentação normal, registrar representação como evolução                     

⏺ ✅ Ponto 6 decidido. É alimentação normal, com o limite do colaborador. A
  representação (refeição com cliente) fica registrada como evolução fora de
  escopo.

  Com isso, o Bloco A (regras de negócio) está fechado. Agora vem o Bloco B, 
  contrato de saída, com os dois bloqueantes do revisor.

  ---

  Ponto 7 de 13: o que sai numa despesa malformada ⚠️ bloqueante

  d-1  data 03/07  categoria " Alimentacao "  fornecedor "X"  valor 33.333
       (falta o campo tem_nota_fiscal)

  A validação é a etapa 1, e a primeira recusa encerra a avaliação da despesa.
  Então essa despesa nunca chega ao arredondamento (etapa 2) nem à normalização
  da categoria (etapa 5). Pela spec atual, não dá para saber o que vai nestes
  campos:

  ┌───────────────────────┬──────────────────────────┬──────────────────────┐
  │         Campo         │  Opção A (recomendada)   │       Opção B        │
  ├───────────────────────┼──────────────────────────┼──────────────────────┤
  │ valor_considerado     │ nulo: a despesa não foi  │ 33,33: arredonda     │
  │                       │ avaliada                 │ mesmo assim          │
  ├───────────────────────┼──────────────────────────┼──────────────────────┤
  │ categoria             │ como veio (" Alimentacao │ normalizada          │
  │                       │  ")                      │ (alimentacao)        │
  ├───────────────────────┼──────────────────────────┼──────────────────────┤
  │ entra em              │ não                      │ sim, então glosa     │
  │ valor_solicitado?     │                          │ 33,33                │
  ├───────────────────────┼──────────────────────────┼──────────────────────┤
  │ status / motivo       │ recusado /               │ igual                │
  │                       │ entrada_invalida         │                      │
  └───────────────────────┴──────────────────────────┴──────────────────────┘

  Por que recomendo a A: uma despesa que não passou na validação não é uma
  despesa válida. Somá-la ao "valor solicitado" misturaria um erro de dados com
  uma glosa (o valor que deixa de ser reembolsado). Com a opção A, a regra fica
  simples: só entra nos totais quem passou da etapa 1 com valor positivo.

  Na mesma linha, os totais ficam assim:
  - valor_solicitado = soma do valor_considerado das despesas que passaram da 
    validação e têm valor maior que zero;
  - uma despesa recusada por valor inválido (negativo ou zero) também fica fora,
    como já era.

  Qual é a sua visão?

✻ Cooked for 8s · done 9:33 PM

❯ opção A, nulo e fora dos totais                                               
⏺ ✅ Ponto 7 decidido: A. Numa despesa malformada, valor_considerado fica nulo,
  a categoria sai como veio e o valor fica fora dos totais.

  ---

  Ponto 8 de 13: valor_informado ⚠️ bloqueante

  A spec diz duas coisas que se contradizem:
  - valor_informado = "valor exatamente como veio na entrada";
  - "todos os valores monetários da saída têm no máximo 2 casas decimais".

  O próprio exemplo cai no conflito:
  d-011  valor 33.333   → valor_informado = 33.333 (como veio) ou 33.33 (2 
  casas)?

  Há também um detalhe técnico que vale explicar: o JSON guarda números, não o
  texto que foi digitado. 72.50 e 72.5 são o mesmo número, então "exatamente
  como veio" só pode significar o mesmo número, não a mesma escrita.

  ┌─────────────────┬──────────────────────────┬───────────────────────────┐
  │      Opção      │          d-011           │        Comentário         │
  ├─────────────────┼──────────────────────────┼───────────────────────────┤
  │ A: manter o     │                          │                           │
  │ campo, isento   │ valor_informado 33.333 e │ mostra o arredondamento   │
  │ da regra de 2   │  valor_considerado 33.33 │ de forma transparente     │
  │ casas           │                          │                           │
  ├─────────────────┼──────────────────────────┼───────────────────────────┤
  │ B: remover o    │ só valor_considerado     │ saída mais simples, mas   │
  │ campo           │ 33.33                    │ perde a evidência do que  │
  │                 │                          │ veio na entrada           │
  └─────────────────┴──────────────────────────┴───────────────────────────┘

  Minha recomendação: a opção A. A regra de 2 casas passa a valer para todos os 
  valores calculados (considerado, reembolsado, limite, totais), e
  valor_informado é a única exceção, por ser uma cópia do número recebido. Para
  a revisão do financeiro, ver 33.333 → 33.33 lado a lado explica a decisão sem
  precisar ler a spec.

  Qual é a sua visão?

✻ Churned for 6s · done 9:34 PM

❯ opção A, manter isento das 2 casas                                            

⏺ ✅ Ponto 8 decidido: A. valor_informado guarda o número recebido e fica isento
  da regra de 2 casas. Todos os valores calculados continuam com no máximo 2
  casas.

  ---

  Ponto 9 de 13: entrada malformada no arquivo

  São quatro situações que a spec não define:

  #: 9a
  Situação: colaborador ausente, ou sem id/nome
  Recomendação: erro de arquivo: nenhuma saída, código de saída diferente de 0
  Por quê: sem saber de quem é o reembolso, não faz sentido calcular nada
  ────────────────────────────────────────
  #: 9b
  Situação: um elemento da lista despesas que não é um objeto (null, 42,
  "texto")
  Recomendação: vira item recusado / entrada_invalida, e as demais despesas são
  processadas
  Por quê: um item ruim não deve derrubar o relatório inteiro, igual ao ponto 7
  ────────────────────────────────────────
  #: 9c
  Situação: despesa sem id ou sem data
  Recomendação: entrada_invalida, com id e data nulos na saída
  Por quê: hoje a saída diz que esses campos são sempre texto; passam a aceitar
  nulo
  ────────────────────────────────────────
  #: 9d
  Situação: despesa com um campo a mais (ex.: "noites": 2, "data_checkout": 
  "...")
  Recomendação: o campo extra é ignorado: a despesa é avaliada normalmente
  Por quê: respeita o formato fixo sem punir quem mandou informação a mais

  Sobre a 9d, há um ponto ligado à sua visão do ponto A5: ignorar o campo
  significa que, mesmo que alguém mande "noites": 2, a hospedagem continua
  valendo uma diária. É coerente com o formato fixo. A alternativa seria recusar
  a despesa com campo extra, e aí perderíamos uma hospedagem legítima por
  excesso de informação.

  Qual é a sua visão sobre 9a, 9b, 9c e 9d?

✻ Sautéed for 7s · done 9:34 PM

❯ 9a erro de arquivo, 9b, 9c e 9d conforme recomendado                          

⏺ ✅ Ponto 9 decidido.
  - 9a: colaborador ausente ou incompleto é erro de arquivo.
  - 9b: um elemento que não é objeto vira entrada_invalida, e as demais despesas
    seguem.
  - 9c: id e data podem sair nulos.
  - 9d: campos extras são ignorados.

  ---

  Ponto 10 de 13: confirmar o formato de saída

  Este é o resumo do contrato de saída, já com as decisões dos pontos 7, 8 e 9:

  colaborador   { id, nome }                       ← copiados da entrada
  periodo       { competencia, inicio, fim }       ← copiados da entrada
  itens[]       um por despesa, na MESMA ORDEM da entrada:
    id, data              ← como vieram (podem ser nulos, 9c)
    categoria             ← normalizada, ou como veio se não 
  reconhecida/inválida
    valor_informado       ← número recebido (isento de 2 casas, ponto 8)
    valor_considerado     ← arredondado ao centavo; nulo se inválida (ponto 7)
    valor_reembolsado     ← 0 se recusado
    status                ← aprovado | parcial | recusado
    motivo                ← código (abaixo); nulo se aprovado
    em_viagem             ← true/false; nulo se recusado antes do limite
    limite_diario         ← limite aplicado; nulo se recusado antes do limite
    justificativa         ← frase em português (texto livre, não contratual)
  totais        { valor_solicitado, valor_reembolsado, valor_glosado }

  Códigos de motivo: entrada_invalida, valor_invalido, fora_do_periodo,
  categoria_fora_da_politica, nota_fiscal_ausente, duplicata,
  limite_diario_excedido. A ordem acompanha as etapas, já com nota antes de
  duplicata (ponto 4a).

  10a. Status quando o limite do dia já se esgotou:
  d-002  03/07  alimentacao  38,00  → o d-001 já consumiu os 60,00 do dia

  ┌─────────────────────────────────────┬───────────────────────────────────┐
  │                Opção                │               d-002               │
  ├─────────────────────────────────────┼───────────────────────────────────┤
  │ recusado + limite_diario_excedido   │ coerente com a regra "reembolsado │
  │ (spec atual)                        │  = 0 → recusado"                  │
  ├─────────────────────────────────────┼───────────────────────────────────┤
  │ parcial com 0,00                    │ "parcial" sem pagar nada fica     │
  │                                     │ incoerente                        │
  └─────────────────────────────────────┴───────────────────────────────────┘

  10b. Justificativa como texto livre: os testes verificam os campos (status,
  motivo e valores), não a frase. Isso evita que uma mudança de redação quebre
  os testes.

  Minha recomendação: confirmar o formato como está, 10a = recusado, e 10b =
  texto livre não contratual.

  Qual é a sua visão? Quer mudar algum campo?

✻ Sautéed for 9s · done 9:35 PM

❯ confirmo o formato, 10a recusado, 10b texto livre                             

⏺ ✅ Ponto 10 decidido. O formato está confirmado. 10a: limite esgotado dá
  recusado. 10b: a justificativa é texto livre e não contratual.

  O Bloco B está fechado. Faltam três pontos de processo, no Bloco C, que dá
  para decidir de uma vez.

  ---

  Pontos 11 a 13: correções e processo

  11. A correção do meu erro na seção 9, já com as suas decisões novas

  Com as decisões 2a (viagem exige nota) e 2b (diária e dia seguinte), o
  resultado do exemplo muda assim:

  ┌───────┬──────────────────┬─────────────────────────────┬────────────────┐
  │  id   │      antes       │           depois            │    por quê     │
  ├───────┼──────────────────┼─────────────────────────────┼────────────────┤
  │       │ em_viagem =      │                             │                │
  │ d-010 │ false (o erro    │ true                        │ hospedagem com │
  │       │ que o revisor    │                             │  nota em 14/07 │
  │       │ pegou)           │                             │                │
  ├───────┼──────────────────┼─────────────────────────────┼────────────────┤
  │       │ em_viagem false, │ em_viagem true, limite      │ 15/07 é o dia  │
  │ d-011 │  limite 60,00    │ 90,00                       │ seguinte à     │
  │       │                  │                             │ diária         │
  ├───────┼──────────────────┼─────────────────────────────┼────────────────┤
  │       │                  │ continua recusado           │ não tem nota   │
  │ d-013 │ —                │ (nota_fiscal_ausente) e não │ (2a)           │
  │       │                  │  gera viagem                │                │
  └───────┴──────────────────┴─────────────────────────────┴────────────────┘

  Os valores e os totais não mudam: 1.861,84 / 585,43 / 1.276,41. O café d-011
  (R$ 33,33) fica abaixo dos dois limites. Não há decisão aqui, é só para você
  conferir.

  12. Como registrar esta revisão no DECISIONS.md

  Recomendação:
  1. Fazer o commit da v1.0 como está agora: docs(spec): primeira versão....
     Esse é o "antes".
  2. Aplicar todas as decisões de hoje e criar a v1.1, com a entrada D-001 no
     DECISIONS.md. A entrada cita o que mudou em cada regra, o gatilho ("revisão
     adversarial e análise dos dados com o responsável") e o erro da seção 9
     que o revisor pegou.
  3. Fazer o commit da v1.1: docs(spec): ... mais DECISIONS.md.

  Assim, o histórico do Git mostra a evolução da spec, que é exatamente o que a
  seção Descrição do relatório pede ("cole a primeira versão e a versão final").

  13. Os pontos em aberto da seção 10
  - Ids repetidos: cada despesa é avaliada pelo próprio conteúdo, e a saída
    repete o id.
  - competencia que não bate com inicio/fim: o período vale por inicio/fim, e
    competencia só é repetida.

  Recomendação: manter as duas como decisões provisórias, registradas.

  Você confirma 11, 12 e 13? Com isso eu faço o commit da v1.0, aplico tudo e te
  mostro o diff da v1.1 antes do segundo commit.

✻ Sautéed for 11s · done 9:35 PM

❯ confirmo 11, 12 e 13, pode seguir                                             

⏺ Primeiro, o commit da v1.0 como está, para guardar o "antes".

  Ran 1 shell command (ctrl+o to expand)
  ⎿  PostToolUse:Bash says: 📝 Fim do bloco de trabalho ("docs(spec): primeira 
     versão com 16 ambiguidades resolvidas"). Exporte a sessão antes de 
     continuar:
        /export docs/sessions/05-<descricao-curta>.md
        e commite com: docs(sessions): export da sessão 05

⏺ O lembrete de export surgiu porque docs(spec) fecha um bloco, mas vou seguir
  conforme autorizado: aplico agora as decisões de hoje na spec e deixo o export
  para depois da v1.1.

⏺ Write(specs/001-motor-reembolso/spec.md)
  ⎿  Added 131 lines, removed 98 lines
      1  # Spec — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.0 · **Status:** rascunho para revisão · **Última a
        -lteração:** 2026-10-01                                          
      3 +**Versão:** 1.1 · **Status:** aprovada para planejamento · **Últ
        +ima alteração:** 2026-10-01 (ver `DECISIONS.md` D-001)          
      4  
      5  > **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ
         . Nenhuma linha
      6  > aqui pode citar linguagem, biblioteca, classe, função ou estru
         tura de pasta.
     ...
      24  - Não aprova, paga nem integra com sistemas de pagamento ou fol
          ha: só calcula e justifica.
      25  - Não processa mais de um colaborador ou mais de um período por
           execução.
      26  - Não verifica a autenticidade da nota fiscal; confia no indica
          dor `tem_nota_fiscal`.
      27 -- Não lê nem interpreta o texto livre de `descricao` (nem para 
         -contar diárias, ver AMB-005).                                  
      27 +- Não lê nem interpreta o texto livre de `descricao` (nem para 
         +contar diárias, AMB-005, nem para identificar refeição com clie
         +nte, AMB-017).                                                 
      28  - Não converte moedas: todos os valores são em reais.
      29  - Não guarda histórico entre execuções: duplicatas só são detec
          tadas dentro da mesma entrada.
      30 -- Não aceita campos adicionais na entrada para datas de entrada
         -/saída de hospedagem. Seria a solução ideal para AMB-005, mas o
         - formato de entrada é fixo; fica registrado como evolução recom
         -endada.                                                        
      30 +- Não usa campos além dos previstos na seção 4; campos extras s
         +ão ignorados (RN-002). Em particular, não usa datas de entrada 
         +e saída de hospedagem: seriam a solução ideal para AMB-005, mas
         + o formato de entrada é fixo. Fica registrado como evolução rec
         +omendada.                                                      
      31 +- Não tem categoria nem limite de representação (refeição com c
         +liente): fica registrado como evolução recomendada (AMB-017).  
      32  - Não trata feriados nem fins de semana de forma especial (AMB-
          015).
      33  
      34  ## 4. Entrada e saída
     ...
       46  
       47  | Campo | Tipo | Significado | Obrigatório |
       48  |---|---|---|---|
       48 -| `colaborador.id` | texto | identificador do colaborador | si
          -m |                                                           
       49 -| `colaborador.nome` | texto | nome | sim |                   
       49 +| `colaborador.id` | texto | identificador do colaborador | si
          +m (erro de arquivo) |                                         
       50 +| `colaborador.nome` | texto | nome | sim (erro de arquivo) | 
       51  | `colaborador.centro_custo` | texto | centro de custo | não |
       52  | `periodo.competencia` | texto `AAAA-MM` | rótulo do mês de c
           ompetência; repetido na saída, não usado em cálculo | não |
       52 -| `periodo.inicio` | data `AAAA-MM-DD` | primeiro dia do perío
          -do (inclusive) | sim |                                        
       53 -| `periodo.fim` | data `AAAA-MM-DD` | último dia do período (i
          -nclusive) | sim |                                             
       54 -| `despesas` | lista | despesas a avaliar (pode ser vazia) | s
          -im |                                                          
       55 -| `despesas[].id` | texto | identificador da despesa | sim |  
       56 -| `despesas[].data` | data `AAAA-MM-DD` | data em que a despes
          -a ocorreu | sim |                                             
       57 -| `despesas[].categoria` | texto | categoria da despesa | sim 
          -|                                                             
       53 +| `periodo.inicio` | data `AAAA-MM-DD` | primeiro dia do perío
          +do (inclusive) | sim (erro de arquivo) |                      
       54 +| `periodo.fim` | data `AAAA-MM-DD` | último dia do período (i
          +nclusive) | sim (erro de arquivo) |                           
       55 +| `despesas` | lista | despesas a avaliar (pode ser vazia) | s
          +im (erro de arquivo) |                                        
       56 +| `despesas[].id` | texto | identificador da despesa | sim (`e
          +ntrada_invalida`) |                                           
       57 +| `despesas[].data` | data `AAAA-MM-DD` | data em que a despes
          +a ocorreu | sim (`entrada_invalida`) |                        
       58 +| `despesas[].categoria` | texto | categoria da despesa | sim 
          +(`entrada_invalida`) |                                        
       59  | `despesas[].descricao` | texto | descrição livre; não usada 
           em regras | não |
       59 -| `despesas[].fornecedor` | texto | estabelecimento; usado na 
          -detecção de duplicatas | sim |                                
       60 -| `despesas[].valor` | número | valor em reais | sim |        
       61 -| `despesas[].tem_nota_fiscal` | booleano | se há nota fiscal 
          -| sim |                                                       
       60 +| `despesas[].fornecedor` | texto | estabelecimento; usado na 
          +detecção de duplicatas | sim (`entrada_invalida`) |           
       61 +| `despesas[].valor` | número | valor em reais | sim (`entrada
          +_invalida`) |                                                 
       62 +| `despesas[].tem_nota_fiscal` | booleano | se há nota fiscal 
          +| sim (`entrada_invalida`) |                                  
       63  
       64 +Campos não listados acima são ignorados.                      
       65 +                                                              
       66  ### Saída
       67  
       68  | Campo | Tipo | Significado |
       69  |---|---|---|
       70  | `colaborador` | objeto | `id` e `nome`, copiados da entrada 
           |
       68 -| `periodo` | objeto | `competencia`, `inicio` e `fim`, copiad
          -os da entrada |                                               
       69 -| `itens` | lista | um item por despesa da entrada, **na mesma
          - ordem** |                                                    
       70 -| `itens[].id` | texto | id da despesa |                      
       71 -| `itens[].data` | texto | data da despesa como veio na entrad
          -a |                                                           
       72 -| `itens[].categoria` | texto | categoria normalizada (RN-006)
          - ou como veio, se não reconhecida |                           
       73 -| `itens[].valor_informado` | número ou nulo | valor exatament
          -e como veio na entrada (nulo se ausente ou não numérico) |    
       74 -| `itens[].valor_considerado` | número ou nulo | valor arredon
          -dado ao centavo (RN-003); nulo se ausente ou não numérico |   
       71 +| `periodo` | objeto | `competencia` (ou nulo, se ausente), `i
          +nicio` e `fim`, copiados da entrada |                         
       72 +| `itens` | lista | um item por elemento de `despesas`, **na m
          +esma ordem** |                                                
       73 +| `itens[].id` | texto ou nulo | id da despesa como veio; nulo
          + se ausente ou se o elemento não é um objeto |                
       74 +| `itens[].data` | texto ou nulo | data da despesa como veio; 
          +nulo se ausente ou se o elemento não é um objeto |            
       75 +| `itens[].categoria` | texto ou nulo | categoria normalizada 
          +(RN-006) se reconhecida; senão, como veio (nulo se ausente) | 
       76 +| `itens[].valor_informado` | número ou nulo | o número recebi
          +do em `valor`, sem arredondamento; nulo se ausente ou não numé
          +rico |                                                        
       77 +| `itens[].valor_considerado` | número ou nulo | valor arredon
          +dado ao centavo (RN-003); **nulo se a despesa foi recusada por
          + `entrada_invalida`** |                                       
       78  | `itens[].valor_reembolsado` | número | quanto será reembolsa
           do (0 se recusado) |
       79  | `itens[].status` | texto | `aprovado`, `parcial` ou `recusad
           o` (RN-011) |
       80  | `itens[].motivo` | texto ou nulo | código do motivo (tabela 
           abaixo); nulo quando `aprovado` |
       81  | `itens[].em_viagem` | booleano ou nulo | se a data estava em
            viagem (RN-010); nulo se o item foi recusado antes do limite 
           diário |
       82  | `itens[].limite_diario` | número ou nulo | limite diário apl
           icado à categoria naquela data; nulo se o item foi recusado an
           tes do limite diário |
       80 -| `itens[].justificativa` | texto | frase em português explica
          -ndo a decisão. Texto livre: não é contratual, os campos acima 
          -são |                                                         
       81 -| `totais.valor_solicitado` | número | soma de `valor_consider
          -ado` dos itens com valor válido (maior que zero) |            
       83 +| `itens[].justificativa` | texto | frase em português explica
          +ndo a decisão. Texto livre: **não é contratual**; os campos ac
          +ima são |                                                     
       84 +| `totais.valor_solicitado` | número | soma de `valor_consider
          +ado` dos itens **não recusados por `entrada_invalida` e com `v
          +alor_considerado` maior que zero** |                          
       85  | `totais.valor_reembolsado` | número | soma de `valor_reembol
           sado` |
       86  | `totais.valor_glosado` | número | `valor_solicitado − valor_
           reembolsado` |
       87  
       85 -Todos os valores monetários da saída são em reais, com no máxi
          -mo 2 casas decimais e exatos ao centavo.                      
       88 +Todos os valores monetários **calculados** da saída (`valor_co
          +nsiderado`, `valor_reembolsado`, `limite_diario` e totais) são
          + em reais, com no máximo 2 casas decimais e exatos ao centavo.
          + `valor_informado` é a única exceção: é a cópia do número rece
          +bido (ex.: 33.333). Como a entrada é um número, "como veio" se
          + refere ao valor numérico, não à forma escrita (72.50 e 72.5 s
          +ão o mesmo valor).                                            
       89  
       87 -**Códigos de motivo:**                                        
       90 +**Códigos de motivo** (na ordem das etapas da seção 8):       
       91  
       92  | Código | Quando | Status resultante |
       93  |---|---|---|
       91 -| `entrada_invalida` | campo obrigatório ausente ou com tipo/f
          -ormato errado (RN-002) | `recusado` |                         
       94 +| `entrada_invalida` | elemento que não é objeto, ou campo obr
          +igatório ausente ou com tipo/formato errado (RN-002) | `recusa
          +do` |                                                         
       95  | `valor_invalido` | valor considerado menor ou igual a zero (
           RN-004) | `recusado` |
       96  | `fora_do_periodo` | data fora de `[inicio, fim]` (RN-005) | 
           `recusado` |
       97  | `categoria_fora_da_politica` | categoria não reconhecida (RN
           -006) | `recusado` |
       95 -| `duplicata` | repete uma despesa anterior (RN-007) | `recusa
          -do` |                                                         
       98  | `nota_fiscal_ausente` | valor acima de 100,00 sem nota (RN-0
           08) | `recusado` |
       99 +| `duplicata` | repete uma despesa anterior (RN-007) | `recusa
          +do` |                                                         
      100  | `limite_diario_excedido` | o limite diário cortou parte ou t
           odo o valor (RN-009) | `parcial`, ou `recusado` se nada restou
            |
      101  
      102  **Exemplo** (entrada com duas despesas de alimentação no mesmo
            dia, fora de viagem):
     ...
      123  
      124  As regras são aplicadas a cada despesa na ordem da seção 8. A 
           primeira regra que recusa uma despesa encerra a avaliação dela
           : cada despesa recusada tem exatamente um motivo.
      125  
      126 +**Normalização de texto** (usada em RN-006 e RN-007): remover 
          +espaços no início e no fim, ignorar maiúsculas/minúsculas e ig
          +norar acentos e cedilha (letras acentuadas e `ç` comparadas co
          +mo a letra base: `á`→`a`, `ç`→`c`, `ô`→`o`). Espaços internos 
          +não são alterados.                                            
      127 +                                                              
      128  ### RN-001 — Um resultado por despesa
      129  
      125 -**Regra:** a saída tem exatamente um item para cada despesa da
          - entrada, na mesma ordem, inclusive as recusadas. Os totais se
          -guem as fórmulas da seção 4.                                  
      130 +**Regra:** a saída tem exatamente um item para cada elemento d
          +e `despesas`, na mesma ordem, inclusive os recusados. Os totai
          +s seguem as fórmulas da seção 4.                              
      131  **Origem:** objetivo do sistema ("justifica cada decisão").
      132  **Aceite:** entrada com 14 despesas gera 14 itens, na mesma or
           dem de ids; `valor_glosado = valor_solicitado − valor_reembols
           ado`.
      133  
      134  ### RN-002 — Validação da entrada
      135  
      136  **Regra:**
      132 -- **Erro de arquivo** (nenhuma saída é gerada): arquivo ausent
          -e ou que não é JSON válido; `periodo.inicio`, `periodo.fim` ou
          - `despesas` ausentes; `inicio` ou `fim` que não são datas váli
          -das `AAAA-MM-DD`; `inicio` posterior a `fim`; `despesas` que n
          -ão é lista.                                                   
      133 -- **Despesa inválida** (vira item `recusado` com motivo `entra
          -da_invalida`): falta `id`, `data`, `categoria`, `fornecedor`, 
          -`valor` ou `tem_nota_fiscal`; `data` não é data válida `AAAA-M
          -M-DD`; `valor` não é número; `tem_nota_fiscal` não é booleano;
          - `categoria` ou `fornecedor` não são texto.                   
      134 -**Origem:** necessidade operacional (a política não trata entr
          -ada malformada).                                              
      135 -**Aceite:** despesa sem `tem_nota_fiscal` → `recusado`, `entra
          -da_invalida`, e as demais despesas são processadas normalmente
          -. Arquivo com `inicio` = `2026-07-31` e `fim` = `2026-07-01` →
          - nenhuma saída, código de saída diferente de 0.               
      137 +- **Erro de arquivo** (nenhuma saída é gerada): arquivo ausent
          +e ou que não é JSON válido; `colaborador` ausente ou sem `id`/
          +`nome` em texto; `periodo.inicio`, `periodo.fim` ou `despesas`
          + ausentes; `inicio` ou `fim` que não são datas válidas `AAAA-M
          +M-DD`; `inicio` posterior a `fim`; `despesas` que não é lista.
      138 +- **Despesa inválida** (vira item `recusado` com motivo `entra
          +da_invalida`; as demais despesas seguem): elemento de `despesa
          +s` que não é um objeto; falta `id`, `data`, `categoria`, `forn
          +ecedor`, `valor` ou `tem_nota_fiscal`; `data` não é data válid
          +a `AAAA-MM-DD`; `valor` não é número; `tem_nota_fiscal` não é 
          +booleano; `id`, `categoria` ou `fornecedor` não são texto.    
      139 +- Uma despesa recusada por `entrada_invalida` tem `valor_consi
          +derado` nulo, categoria como veio, `em_viagem` e `limite_diari
          +o` nulos, e não entra nos totais.                             
      140 +- Campos extras, no arquivo ou nas despesas, são ignorados.   
      141 +**Origem:** necessidade operacional (a política não trata entr
          +ada malformada); pontos 7 e 9 de D-001.                       
      142 +**Aceite:** despesa sem `tem_nota_fiscal` com `valor` 33.333 →
          + `recusado`, `entrada_invalida`, `valor_informado` 33.333, `va
          +lor_considerado` nulo, fora de `valor_solicitado`; as demais d
          +espesas são processadas normalmente. Elemento `null` em `despe
          +sas` → item com `id` e `data` nulos, `entrada_invalida`. Arqui
          +vo sem `colaborador` → nenhuma saída, código diferente de 0. H
          +ospedagem com campo extra `"noites": 2` → avaliada como uma di
          +ária (RN-012).                                                
      143  
      144  ### RN-003 — Arredondamento ao centavo
      145  
     ...
      149  
      150  ### RN-004 — Valor deve ser positivo
      151  
      145 -**Regra:** despesa com `valor_considerado` menor ou igual a ze
          -ro é `recusado` com motivo `valor_invalido`. Ela não abate, nã
          -o soma e não consome limite de nenhuma outra despesa.         
      152 +**Regra:** despesa com `valor_considerado` menor ou igual a ze
          +ro é `recusado` com motivo `valor_invalido`. Ela não abate, nã
          +o soma nos totais e não consome limite de nenhuma outra despes
          +a.                                                            
      153  **Origem:** AMB-013.
      147 -**Aceite:** `valor` -45.00 → `recusado`, `valor_invalido`, `va
          -lor_reembolsado` 0; demais despesas do mesmo dia não mudam. `v
          -alor` 0.004 (arredonda para 0,00) → `valor_invalido`.         
      154 +**Aceite:** `valor` -45.00 → `recusado`, `valor_invalido`, `va
          +lor_reembolsado` 0; demais despesas do mesmo dia não mudam. `v
          +alor` 0 → `valor_invalido`. `valor` 0.004 (arredonda para 0,00
          +) → `valor_invalido`.                                         
      155  
      156  ### RN-005 — Período de competência
      157  
     ...
      161  
      162  ### RN-006 — Categorias da política
      163  
      157 -**Regra:** a categoria é comparada depois de remover espaços n
          -o início e no fim e ignorando maiúsculas/minúsculas. Só três c
          -ategorias são reconhecidas: `alimentacao`, `transporte_urbano`
          - e `hospedagem`. Na saída, categorias reconhecidas aparecem ne
          -ssa forma normalizada. Qualquer outra (incluindo variações com
          - acento, como `alimentação`) → `recusado`, motivo `categoria_f
          -ora_da_politica`.                                             
      164 +**Regra:** a categoria é comparada depois da normalização de t
          +exto (seção 5). Só três categorias são reconhecidas: `alimenta
          +cao`, `transporte_urbano` e `hospedagem`. Na saída, categorias
          + reconhecidas aparecem nessa forma normalizada. Qualquer outra
          + → `recusado`, motivo `categoria_fora_da_politica`.           
      165  **Origem:** política do RH, item 9; AMB-011; AMB-012.
      159 -**Aceite:** `ALIMENTACAO` e `" Alimentacao "` → tratadas como 
          -`alimentacao`; `coworking` → `categoria_fora_da_politica`.    
      166 +**Aceite:** `ALIMENTACAO`, `" Alimentacao "` e `alimentação` →
          + tratadas como `alimentacao`; `coworking` → `categoria_fora_da
          +_politica`.                                                   
      167  
      168  ### RN-007 — Duplicatas
      169  
      163 -**Regra:** duas despesas são duplicatas quando têm a mesma `da
          -ta`, a mesma categoria normalizada, o mesmo `fornecedor` (comp
          -arado sem espaços nas pontas e ignorando maiúsculas/minúsculas
          -) e o mesmo `valor_considerado`. `id` e `descricao` não entram
          - na comparação. Entre despesas duplicatas, só a primeira na or
          -dem da entrada segue avaliada; as seguintes são `recusado`, mo
          -tivo `duplicata`. Só despesas que passaram por RN-002 a RN-006
          - participam da comparação. Uma duplicata recusada não consome 
          -limite.                                                       
      170 +**Regra:** duas despesas são duplicatas quando têm a mesma `da
          +ta`, a mesma categoria normalizada, o mesmo `fornecedor` norma
          +lizado (seção 5) e o mesmo `valor_considerado`. `id`, `descric
          +ao` e `tem_nota_fiscal` não entram na comparação. Só participa
          +m da comparação despesas que passaram pelas etapas 1 a 6 da se
          +ção 8 (inclusive a nota fiscal): uma despesa recusada antes di
          +sso não é "original" de ninguém. Entre duplicatas, só a primei
          +ra na ordem da entrada segue avaliada; as seguintes são `recus
          +ado`, motivo `duplicata`, e não consomem limite. A comparação 
          +é exata: datas, valores ou fornecedores diferentes após a norm
          +alização não são duplicatas (risco aceito, seção 10).         
      171  **Origem:** política do RH, item 8; AMB-010.
      165 -**Aceite:** d-006 e d-007 (mesmos data, categoria, fornecedor 
          -e valor 54,90) → d-006 avaliada normalmente, d-007 `recusado`,
          - `duplicata`. Mesmos dados com fornecedor diferente → não são 
          -duplicatas.                                                   
      172 +**Aceite:** d-006 e d-007 (mesmos data, categoria, fornecedor 
          +e valor 54,90, ambas com nota) → d-006 avaliada normalmente, d
          +-007 `duplicata`. Táxi de 110,00 sem nota seguido do mesmo táx
          +i com nota → o primeiro `nota_fiscal_ausente`, o segundo segue
          + avaliado (não é duplicata), em qualquer ordem. "Bistro Centra
          +l" e "Bistrô Central" → mesmo fornecedor.                     
      173  
      174  ### RN-008 — Nota fiscal obrigatória acima de R$ 100
      175  
      169 -**Regra:** despesa com `valor_considerado` estritamente maior 
          -que 100,00 e `tem_nota_fiscal` falso → `recusado`, motivo `not
          -a_fiscal_ausente`. A comparação usa o valor da despesa individ
          -ual, antes de qualquer limite. A despesa recusada não consome 
          -limite nem caracteriza viagem.                                
      176 +**Regra:** despesa com `valor_considerado` estritamente maior 
          +que 100,00 e `tem_nota_fiscal` falso → `recusado`, motivo `not
          +a_fiscal_ausente`. A comparação usa o valor da despesa individ
          +ual, antes de qualquer limite. O valor de 100,00 é fixo: não é
          + ampliado em viagem. A despesa recusada não consome limite, nã
          +o caracteriza viagem e não participa da comparação de duplicat
          +as.                                                           
      177  **Origem:** política do RH, item 5; AMB-007; AMB-008.
      171 -**Aceite:** 100,00 sem nota → segue para o limite diário; 100,
          -01 sem nota → `nota_fiscal_ausente`; 100,01 com nota → segue. 
      178 +**Aceite:** 100,00 sem nota → segue; 100,01 sem nota → `nota_f
          +iscal_ausente`; 100,01 com nota → segue; transporte de 110,00 
          +sem nota em data em viagem → `nota_fiscal_ausente`.           
      179  
      180  ### RN-009 — Limite diário por categoria
      181  
     ...
      193  
      194  ### RN-010 — Colaborador em viagem
      195  
      189 -**Regra:** uma data está "em viagem" quando existe na entrada 
          -uma despesa de `hospedagem` nessa mesma data que chegou ao lim
          -ite diário (não foi recusada por RN-002 a RN-008). Em datas em
          - viagem, os limites de `alimentacao` e `transporte_urbano` são
          - ampliados em 50% (tabela da RN-009). Cada despesa de hospedag
          -em cobre apenas a sua própria data (RN-012). A condição de via
          -gem vale para todas as despesas da data, independentemente da 
          -ordem em que aparecem na entrada.                             
      196 +**Regra:** uma despesa de `hospedagem` **comprova viagem** qua
          +ndo tem `tem_nota_fiscal` verdadeiro e passou pelas etapas 1 a
          + 7 da seção 8. Uma hospedagem que comprova viagem na data D co
          +loca em viagem as datas **D e D+1** (a noite da diária e o dia
          + seguinte). Em datas em viagem, os limites de `alimentacao` e 
          +`transporte_urbano` são ampliados em 50% (tabela da RN-009). A
          + condição de viagem vale para todas as despesas da data, indep
          +endentemente da ordem em que aparecem na entrada.             
      197  **Origem:** política do RH, item 6; AMB-004.
      191 -**Aceite:** hospedagem válida em 14/07 + alimentação de 80,00 
          -em 14/07 → limite 90,00, alimentação `aprovado` com 80,00. Ali
          -mentação de 80,00 em 15/07 sem hospedagem em 15/07 → limite 60
          -,00, `parcial` com 60,00. Hospedagem de 14/07 recusada por not
          -a fiscal → 14/07 não está em viagem.                          
      198 +**Aceite:** hospedagem com nota em 14/07 → 14/07 e 15/07 em vi
          +agem; alimentação de 80,00 em 15/07 → limite 90,00, `aprovado`
          + com 80,00; alimentação de 80,00 em 16/07 → limite 60,00, `par
          +cial` com 60,00. Hospedagem de 80,00 **sem** nota em 03/07 → r
          +eembolsada pelas regras normais, mas 03/07 e 04/07 **não** fic
          +am em viagem. Hospedagem com nota em 30/06, fora de um período
          + que começa em 01/07 → recusada por `fora_do_periodo`, e 01/07
          + não fica em viagem.                                          
      199  
      200  ### RN-011 — Status e justificativa
      201  
     ...
      205  
      206  ### RN-012 — Hospedagem: um lançamento é uma diária
      207  
      201 -**Regra:** cada despesa de `hospedagem` é tratada como uma diá
          -ria na sua `data`, qualquer que seja o valor ou a descrição. V
          -árias hospedagens na mesma data dividem o mesmo limite diário 
          -de 250,00 (RN-009).                                           
      208 +**Regra:** cada despesa de `hospedagem` é tratada como uma diá
          +ria na sua `data`, qualquer que seja o valor, a descrição ou c
          +ampos extras. Várias hospedagens na mesma data dividem o mesmo
          + limite diário de 250,00 (RN-009).                            
      209  **Origem:** política do RH, item 3; AMB-005.
      203 -**Aceite:** hospedagem de 480,00 com nota ("2 diarias" na desc
          -rição) → `parcial` com 250,00; data em viagem só no dia da des
          -pesa.                                                         
      210 +**Aceite:** hospedagem de 480,00 com nota em 14/07 ("2 diarias
          +" na descrição) → `parcial` com 250,00; 14/07 e 15/07 em viage
          +m (RN-010).                                                   
      211  
      212  ---
      213  
     ...
      235  
      236  **Texto original do RH:** (não tratado)
      237  **O que não está claro:** quando a soma do dia passa do limite
           , de qual despesa sai o corte. A entrada não tem horário.
      231 -**Decisão:** as despesas consomem o limite na ordem em que apa
          -recem na entrada; o corte cai nas últimas.                    
      238 +**Decisão:** as despesas consomem o limite na ordem em que apa
          +recem na entrada; o corte cai nas últimas. Se o saldo acabou, 
          +a despesa é `recusado` com `limite_diario_excedido`.          
      239  **Justificativa:** é o único critério determinístico disponíve
           l nos dados e reproduz a conferência item a item feita hoje.
      240  **Regra afetada:** RN-009
      241  
      242  ### AMB-004 — O que caracteriza "em viagem"? (D)
      243  
      244  **Texto original do RH:** "Colaborador em viagem tem limites a
           mpliados em 50%."
      238 -**O que não está claro:** a entrada não tem campo de viagem.  
      239 -**Decisão:** uma data está em viagem se há na entrada uma hosp
          -edagem válida (não recusada antes do limite) nessa data.      
      240 -**Justificativa:** hospedagem é a única evidência objetiva de 
          -viagem nos dados; uma hospedagem recusada não comprova a viage
          -m.                                                            
      245 +**O que não está claro:** a entrada não tem campo de viagem. T
          +ambém não está claro se uma hospedagem barata e sem nota basta
          + como prova, e se o dia seguinte ao pernoite conta (d-011, caf
          +é no hotel em 15/07, depois da diária de 14/07).              
      246 +**Decisão:** uma hospedagem **com nota fiscal** que não foi re
          +cusada antes do limite comprova viagem na data dela e no dia s
          +eguinte.                                                      
      247 +**Justificativa:** hospedagem é a única evidência objetiva de 
          +viagem nos dados, e só a nota a torna verificável (sem a exigê
          +ncia, uma hospedagem de 0,01 ampliaria o teto do dia em 70,00)
          +; uma diária é uma noite, então o colaborador acorda em viagem
          + no dia seguinte.                                             
      248  **Regra afetada:** RN-010
      249  
      250  ### AMB-005 — Uma despesa de hospedagem com várias diárias (D,
            U)
      251  
      252  **Texto original do RH:** "Hospedagem tem limite de R$ 250 por
            diária."
      253  **O que não está claro:** a entrada não informa quantas diária
           s uma despesa representa; essa informação só aparece em texto 
           livre (d-010 "2 diarias", d-013 "3 noites").
      247 -**Decisão:** cada lançamento de hospedagem é uma diária, na da
          -ta da despesa. A descrição não é interpretada.                
      254 +**Decisão:** cada lançamento de hospedagem é uma diária, na da
          +ta da despesa. A descrição e campos extras não são interpretad
          +os.                                                           
      255  **Justificativa:** sem campo estruturado, contar diárias a par
           tir de texto livre seria adivinhar; a solução correta (datas d
           e entrada e saída) exige mudar o formato de entrada, que é fix
           o (seção 3).
      256  **Regra afetada:** RN-012, RN-010
      257  
     ...
      267  
      268  **Texto original do RH:** "Nota fiscal é obrigatória acima de 
           R$ 100."
      269  **O que não está claro:** se 100,00 está incluído (d-003 = 100
           ,00 e d-004 = 100,01, ambos sem nota).
      263 -**Decisão:** só exige nota quando o valor é estritamente maior
          - que 100,00.                                                  
      264 -**Justificativa:** leitura literal de "acima de".             
      270 +**Decisão:** só exige nota quando o valor é estritamente maior
          + que 100,00. O valor de 100,00 não é ampliado em viagem.      
      271 +**Justificativa:** leitura literal de "acima de"; a ampliação 
          +da política (item 6) fala de limites de reembolso, não da exig
          +ência de nota.                                                
      272  **Regra afetada:** RN-008
      273  
      274  ### AMB-008 — O que acontece sem a nota obrigatória, e sobre q
           ual valor se compara? (F, U)
     ...
      276  **Texto original do RH:** "Nota fiscal é obrigatória acima de 
           R$ 100."
      277  **O que não está claro:** se a despesa sem nota é recusada int
           eira ou paga até 100,00; e se o 100,00 se compara ao valor da 
           despesa, ao valor já limitado ou à soma do dia.
      278  **Decisão:** recusa a despesa inteira; compara com o valor ind
           ividual da despesa (arredondado), antes de qualquer limite.
      272 -**Justificativa:** "obrigatória" é condição para reembolsar; c
          -omparar antes do limite impede que o corte do limite "esconda"
          - a falta de nota.                                             
      279 +**Justificativa:** "obrigatória" é condição para reembolsar; c
          +omparar antes do limite impede que o corte do limite "esconda"
          + a falta de nota; comparar pela soma do dia recusaria despesas
          + pequenas legítimas sem nota (duas corridas de 60,00). A brech
          +a do fracionamento é aceita conscientemente (seção 10).       
      280  **Regra afetada:** RN-008
      281  
      282  ### AMB-009 — "Lançadas dentro do período de competência" (D, 
           F)
      283  
      284  **Texto original do RH:** "Despesas devem ser lançadas dentro 
           do período de competência."
      278 -**O que não está claro:** a entrada não tem data de lançamento
          -, só a data da despesa; e se os extremos do período estão incl
          -uídos.                                                        
      285 +**O que não está claro:** a entrada não tem data de lançamento
          +, só a data da despesa (d-008: "Almoco de abril lancado com at
          +raso", data 15/04 num relatório de julho); e se os extremos do
          + período estão incluídos.                                     
      286  **Decisão:** a data da despesa precisa estar entre `inicio` e 
           `fim`, ambos inclusive.
      280 -**Justificativa:** a data da despesa é o único dado disponível
          -; o período informado é fechado nos dois extremos.            
      287 +**Justificativa:** toda despesa da entrada já está "lançada" n
          +o relatório do período; se "lançada" significasse só isso, a r
          +egra nunca recusaria nada e despesas de qualquer mês antigo en
          +trariam. A data da despesa é o único dado que dá sentido à reg
          +ra.                                                           
      288  **Regra afetada:** RN-005
      289  
      290  ### AMB-010 — O que é duplicata e como tratá-la? (U)
      291  
      292  **Texto original do RH:** "Duplicatas devem ser tratadas."
      286 -**O que não está claro:** quais campos definem uma duplicata (
          -d-006 e d-007 só diferem no id) e o que fazer com ela.        
      287 -**Decisão:** mesma data, categoria, fornecedor e valor; a prim
          -eira na ordem da entrada é avaliada, as demais são recusadas c
          -om motivo `duplicata`.                                        
      288 -**Justificativa:** o id é gerado no lançamento e não identific
          -a o gasto; recusar com motivo explícito deixa visível um event
          -ual gasto legítimo repetido, para o colaborador contestar.    
      293 +**O que não está claro:** quais campos definem uma duplicata (
          +d-006 e d-007 só diferem no id), o que fazer com ela, e se uma
          + despesa relançada com a nota fiscal que faltava é duplicata d
          +a original.                                                   
      294 +**Decisão:** mesma data, categoria, fornecedor e valor (texto 
          +normalizado, comparação exata); a nota fiscal é verificada ant
          +es, e só despesas que passaram por ela são comparadas; a prime
          +ira na ordem da entrada é avaliada, as demais são recusadas co
          +m motivo `duplicata`.                                         
      295 +**Justificativa:** o id é gerado no lançamento e não identific
          +a o gasto; verificar a nota antes torna o resultado independen
          +te da ordem e permite corrigir uma nota faltante; recusar com 
          +motivo explícito deixa visível um eventual gasto legítimo repe
          +tido, para o colaborador contestar.                           
      296  **Regra afetada:** RN-007
      297  
      298  ### AMB-011 — Categoria com grafia diferente (F)
      299  
      300  **Texto original do RH:** (não tratado)
      294 -**O que não está claro:** se `ALIMENTACAO` (d-014) é a mesma c
          -ategoria que `alimentacao`.                                   
      295 -**Decisão:** ignora maiúsculas/minúsculas e espaços nas pontas
          -; não ignora acentos.                                         
      296 -**Justificativa:** diferença de caixa é erro de digitação ineq
          -uívoco; acentos e outras variações não são presumidos.        
      297 -**Regra afetada:** RN-006                                     
      301 +**O que não está claro:** se `ALIMENTACAO` (d-014) é a mesma c
          +ategoria que `alimentacao`; e uma grafia com acento (`alimenta
          +ção`).                                                        
      302 +**Decisão:** ignora maiúsculas/minúsculas, espaços nas pontas 
          +e acentos/cedilha (normalização da seção 5). A mesma normaliza
          +ção vale para o fornecedor.                                   
      303 +**Justificativa:** são variações de escrita da mesma palavra; 
          +recusar `alimentação` puniria quem escreve corretamente em por
          +tuguês.                                                       
      304 +**Regra afetada:** RN-006, RN-007                             
      305  
      306  ### AMB-012 — Categoria fora da política: recusar ou omitir? (
           U)
      307  
     ...
      311  **Justificativa:** o objetivo é justificar cada decisão; omiti
           r esconderia a despesa do colaborador.
      312  **Regra afetada:** RN-006, RN-001
      313  
      307 -### AMB-013 — Valor negativo (estorno) (D)                    
      314 +### AMB-013 — Valor negativo (estorno) ou zero (D)            
      315  
      316  **Texto original do RH:** (não tratado)
      310 -**O que não está claro:** d-009 tem valor -45,00 ("estorno"): 
          -se abate do dia, se é ignorado ou se é erro.                  
      311 -**Decisão:** valor menor ou igual a zero é recusado com motivo
          - `valor_invalido` e não afeta nenhuma outra despesa.          
      312 -**Justificativa:** o sistema calcula reembolso de despesas; es
          -torno não é despesa e não há como saber a qual despesa ele se 
          -refere.                                                       
      317 +**O que não está claro:** d-009 tem valor -45,00 ("estorno"): 
          +se abate do dia, se é ignorado ou se é erro. Também não está c
          +laro o que fazer com valor zero.                              
      318 +**Decisão:** valor menor ou igual a zero é recusado com motivo
          + `valor_invalido` e não afeta nenhuma outra despesa nem os tot
          +ais.                                                          
      319 +**Justificativa:** o sistema calcula reembolso de despesas; es
          +torno não é despesa e não há como saber a qual despesa ele se 
          +refere; valor zero não é despesa e provavelmente é erro de lan
          +çamento.                                                      
      320  **Regra afetada:** RN-004
      321  
      322  ### AMB-014 — Valor com mais de 2 casas decimais (F)
      323  
      324  **Texto original do RH:** (não tratado)
      325  **O que não está claro:** d-011 tem 33,333: arredondar, trunca
           r ou recusar, e quando.
      319 -**Decisão:** arredonda para o centavo, metade para cima, antes
          - de qualquer regra.                                           
      326 +**Decisão:** arredonda para o centavo, metade para cima, antes
          + de qualquer regra. A saída mostra o número recebido (`valor_i
          +nformado`) e o arredondado (`valor_considerado`).             
      327  **Justificativa:** reembolso é pago em centavos; arredondar no
            início garante que todas as regras usem o mesmo valor.
      328  **Regra afetada:** RN-003
      329  
     ...
      338  ### AMB-016 — Em que ordem as regras se aplicam? (U)
      339  
      340  **Texto original do RH:** (não tratado)
      334 -**O que não está claro:** quando várias regras incidem na mesm
          -a despesa, a ordem muda o resultado (ex.: se uma duplicata ou 
          -uma despesa sem nota consome o limite do dia).                
      341 +**O que não está claro:** quando várias regras incidem na mesm
          +a despesa, a ordem muda o resultado (ex.: se uma duplicata ou 
          +uma despesa sem nota consome o limite do dia, ou se uma despes
          +a sem nota impede o relançamento com nota).                   
      342  **Decisão:** ordem da seção 8; a primeira recusa encerra a ava
           liação da despesa; só despesas que chegam ao limite diário o c
           onsomem.
      336 -**Justificativa:** despesa recusada não é reembolsável e, port
          -anto, não deve tirar limite de uma despesa válida.            
      343 +**Justificativa:** despesa recusada não é reembolsável e, port
          +anto, não deve tirar limite de uma despesa válida nem bloquear
          + uma correção.                                                
      344  **Regra afetada:** todas
      345  
      346 +### AMB-017 — Refeição com cliente (U)                        
      347 +                                                              
      348 +**Texto original do RH:** (não tratado)                       
      349 +**O que não está claro:** d-001 é "Almoco com cliente" (72,50)
          +: pode incluir a refeição de outra pessoa; a política não prev
          +ê representação nem limite por pessoa.                        
      350 +**Decisão:** é alimentação do colaborador, com o limite diário
          + normal.                                                      
      351 +**Justificativa:** a entrada não informa número de pessoas nem
          + uma categoria de representação; identificá-las exigiria inter
          +pretar a descrição. Fica registrado como evolução recomendada 
          +(seção 3).                                                    
      352 +**Regra afetada:** RN-009                                     
      353 +                                                              
      354  ---
      355  
      356  ## 7. Casos de borda
     ...
      360  | Duas alimentações no mesmo dia somando mais que o limite | 7
           2,50 e 38,00 em 03/07, fora de viagem | 60,00 `parcial` e 0 `r
           ecusado` (`limite_diario_excedido`) | RN-009 |
      361  | Valor exatamente no limite de nota | 100,00 sem nota, transp
           orte | não exige nota; limite 80,00 → `parcial` com 80,00 | RN
           -008, RN-009 |
      362  | Um centavo acima do limite de nota | 100,01 sem nota | `recu
           sado`, `nota_fiscal_ausente` | RN-008 |
      363 +| Limite de nota em viagem | transporte 110,00 sem nota em dat
          +a em viagem | `nota_fiscal_ausente` (o 100,00 não amplia) | RN
          +-008 |                                                        
      364  | Valor exatamente no limite diário | alimentação 60,00 | `apr
           ovado` com 60,00 | RN-009 |
      365  | Um centavo acima do limite diário | alimentação 60,01 | `par
           cial` com 60,00 | RN-009 |
      366  | Primeiro e último dia do período | datas iguais a `inicio` e
            a `fim` | dentro do período | RN-005 |
      367  | Um dia fora do período | `fim` + 1 dia | `fora_do_periodo` |
            RN-005 |
      368 +| Despesa antiga lançada no período | d-008, data 15/04 num pe
          +ríodo de julho | `fora_do_periodo` | RN-005 |                 
      369  | Categoria em maiúsculas | `ALIMENTACAO` | tratada como `alim
           entacao` | RN-006 |
      353 -| Categoria com acento | `alimentação` | `categoria_fora_da_po
          -litica` | RN-006 |                                            
      354 -| Duplicata exata | mesmos data, categoria, fornecedor, valor 
          -| segunda `duplicata` | RN-007 |                              
      355 -| Quase duplicata | mesmo valor, fornecedor diferente | as dua
          -s avaliadas | RN-007 |                                        
      356 -| Duplicata depois de despesa recusada por nota | 1ª: 150,00 s
          -em nota; 2ª: idêntica | 1ª `nota_fiscal_ausente`; 2ª `duplicat
          -a` | RN-007, seção 8 |                                        
      370 +| Categoria com acento | `alimentação` | tratada como `aliment
          +acao` | RN-006 |                                              
      371 +| Duplicata exata | mesmos data, categoria, fornecedor, valor 
          +(≤ 100) | segunda `duplicata` | RN-007 |                      
      372 +| Fornecedor com acento | "Bistro Central" e "Bistrô Central",
          + demais campos iguais | segunda `duplicata` | RN-007 |        
      373 +| Quase duplicata | mesmo valor, data vizinha ou fornecedor di
          +ferente | as duas avaliadas | RN-007 |                        
      374 +| Cópias idênticas sem nota acima de 100 | duas despesas de 15
          +0,00 sem nota | as duas `nota_fiscal_ausente` | RN-008, RN-007
          + |                                                            
      375 +| Relançamento com nota | 110,00 sem nota e depois o mesmo com
          + nota (ou ordem inversa) | sem nota `nota_fiscal_ausente`; com
          + nota segue avaliada | RN-007, RN-008 |                       
      376  | Estorno | -45,00 | `valor_invalido`; não altera o dia | RN-0
           04 |
      377  | Valor zero | 0,00 | `valor_invalido` | RN-004 |
      359 -| Três casas decimais | 33,333 | considerado 33,33 | RN-003 | 
      378 +| Três casas decimais | 33,333 | `valor_informado` 33.333, `va
          +lor_considerado` 33,33 | RN-003 |                             
      379  | Arredondamento da metade | 10,005 | considerado 10,01 | RN-0
           03 |
      361 -| Hospedagem com várias diárias na descrição | 480,00 "2 diari
          -as", com nota | 1 diária: `parcial` com 250,00 | RN-012 |     
      380 +| Hospedagem com várias diárias na descrição | 480,00 "2 diari
          +as", com nota, em 14/07 | 1 diária: `parcial` com 250,00; 14/0
          +7 e 15/07 em viagem | RN-012, RN-010 |                        
      381 +| Dia seguinte à diária | hospedagem com nota em 14/07; alimen
          +tação 80,00 em 15/07 | 15/07 em viagem: limite 90,00, `aprovad
          +o` com 80,00 | RN-010 |                                       
      382 +| Dois dias depois da diária | hospedagem com nota em 14/07; a
          +limentação 80,00 em 16/07 | limite 60,00, `parcial` com 60,00 
          +| RN-010 |                                                    
      383 +| Hospedagem sem nota até 100 | hospedagem 80,00 sem nota em 0
          +3/07; alimentação 90,00 em 03/07 | hospedagem `aprovado` com 8
          +0,00; 03/07 não fica em viagem; alimentação `parcial` com 60,0
          +0 | RN-010 |                                                  
      384  | Hospedagem sem nota acima de 100 | 690,00 sem nota | `nota_f
           iscal_ausente`; data não fica em viagem | RN-008, RN-010 |
      363 -| Alimentação antes da hospedagem na entrada, mesma data | ali
          -mentação 80,00 e depois hospedagem válida, mesma data | data e
          -m viagem: alimentação `aprovado` com 80,00 (limite 90,00) | RN
          --010 |                                                        
      385 +| Hospedagem fora do período | hospedagem com nota em 30/06, p
          +eríodo desde 01/07 | `fora_do_periodo`; 01/07 não fica em viag
          +em | RN-005, RN-010 |                                         
      386 +| Alimentação antes da hospedagem na entrada, mesma data | ali
          +mentação 80,00 e depois hospedagem com nota, mesma data | data
          + em viagem: alimentação `aprovado` com 80,00 (limite 90,00) | 
          +RN-010 |                                                      
      387  | Duas hospedagens na mesma data | 200,00 e 100,00, com nota |
            200,00 `aprovado`; 50,00 `parcial` | RN-012, RN-009 |
      365 -| Campo obrigatório ausente | despesa sem `tem_nota_fiscal` | 
          -`entrada_invalida`; demais processadas | RN-002 |             
      388 +| Campo obrigatório ausente | despesa sem `tem_nota_fiscal` | 
          +`entrada_invalida`, `valor_considerado` nulo, fora dos totais;
          + demais processadas | RN-002 |                                
      389 +| Elemento que não é objeto | `null` dentro de `despesas` | it
          +em com `id` e `data` nulos, `entrada_invalida` | RN-002 |     
      390 +| Campo extra | hospedagem com `"noites": 2` | campo ignorado;
          + uma diária | RN-002, RN-012 |                                
      391 +| Colaborador ausente | arquivo sem `colaborador` | erro de ar
          +quivo: sem saída, código diferente de 0 | RN-002 |            
      392  | Lista de despesas vazia | `despesas: []` | `itens` vazio, to
           tais 0 | RN-001 |
      393  | Despesa em sábado | 18/07 (sábado) | avaliada normalmente | 
           AMB-015 |
      394  
     ...
      401  3. **Valor positivo** — RN-004 (`valor_invalido`).
      402  4. **Período** — RN-005 (`fora_do_periodo`).
      403  5. **Categoria** — RN-006 (`categoria_fora_da_politica`).
      378 -6. **Duplicata** — RN-007 (`duplicata`), comparando só com des
          -pesas anteriores que passaram pelas etapas 1 a 5.             
      379 -7. **Nota fiscal** — RN-008 (`nota_fiscal_ausente`).          
      404 +6. **Nota fiscal** — RN-008 (`nota_fiscal_ausente`).          
      405 +7. **Duplicata** — RN-007 (`duplicata`), comparando só com des
          +pesas anteriores que passaram pelas etapas 1 a 6.             
      406  8. **Viagem** — RN-010: com todas as despesas já avaliadas pel
           as etapas 1 a 7, marca as datas em viagem.
      407  9. **Limite diário** — RN-009, por data e categoria, consumind
           o o limite na ordem da entrada.
      408  
      383 -Consequências: despesas recusadas nas etapas 1 a 7 não consome
          -m limite; uma hospedagem recusada nas etapas 1 a 7 não caracte
          -riza viagem; a viagem é determinada antes de qualquer limite s
          -er aplicado.                                                  
      409 +Consequências: despesas recusadas nas etapas 1 a 7 não consome
          +m limite; uma despesa sem nota recusada na etapa 6 não impede 
          +que o relançamento com nota seja avaliado; uma hospedagem recu
          +sada nas etapas 1 a 7, ou sem nota, não caracteriza viagem; a 
          +viagem é determinada antes de qualquer limite ser aplicado.   
      410  
      411  ## 9. Critérios de aceite
      412  
     ...
      418  - [ ] A mesma entrada sempre produz a mesma saída.
      419  - [ ] Entradas com erro de arquivo (RN-002) terminam com códig
           o diferente de 0 e não geram arquivo de saída.
      420  
      395 -**Resultado esperado para `exemplos/despesas-exemplo.json`** (
          -nenhuma data do exemplo fica em viagem):                      
      421 +**Resultado esperado para `exemplos/despesas-exemplo.json`** (
          +datas em viagem: 14/07 e 15/07, pela hospedagem d-010 com nota
          +):                                                            
      422  
      397 -| id | considerado | limite | reembolsado | status | motivo | 
      398 -|---|---|---|---|---|---|                                     
      399 -| d-001 | 72,50 | 60,00 | 60,00 | parcial | limite_diario_exce
          -dido |                                                        
      400 -| d-002 | 38,00 | 60,00 | 0,00 | recusado | limite_diario_exce
          -dido |                                                        
      401 -| d-003 | 100,00 | 80,00 | 80,00 | parcial | limite_diario_exc
          -edido |                                                       
      402 -| d-004 | 100,01 | — | 0,00 | recusado | nota_fiscal_ausente |
      403 -| d-005 | 89,00 | — | 0,00 | recusado | categoria_fora_da_poli
          -tica |                                                        
      404 -| d-006 | 54,90 | 60,00 | 54,90 | aprovado | — |              
      405 -| d-007 | 54,90 | — | 0,00 | recusado | duplicata |           
      406 -| d-008 | 41,00 | — | 0,00 | recusado | fora_do_periodo |     
      407 -| d-009 | -45,00 | — | 0,00 | recusado | valor_invalido |     
      408 -| d-010 | 480,00 | 250,00 | 250,00 | parcial | limite_diario_e
          -xcedido |                                                     
      409 -| d-011 | 33,33 | 60,00 | 33,33 | aprovado | — |              
      410 -| d-012 | 47,20 | 60,00 | 47,20 | aprovado | — |              
      411 -| d-013 | 690,00 | — | 0,00 | recusado | nota_fiscal_ausente |
      412 -| d-014 | 61,00 | 60,00 | 60,00 | parcial | limite_diario_exce
          -dido |                                                        
      423 +| id | considerado | em viagem | limite | reembolsado | status
          + | motivo |                                                   
      424 +|---|---|---|---|---|---|---|                                 
      425 +| d-001 | 72,50 | não | 60,00 | 60,00 | parcial | limite_diari
          +o_excedido |                                                  
      426 +| d-002 | 38,00 | não | 60,00 | 0,00 | recusado | limite_diari
          +o_excedido |                                                  
      427 +| d-003 | 100,00 | não | 80,00 | 80,00 | parcial | limite_diar
          +io_excedido |                                                 
      428 +| d-004 | 100,01 | — | — | 0,00 | recusado | nota_fiscal_ausen
          +te |                                                          
      429 +| d-005 | 89,00 | — | — | 0,00 | recusado | categoria_fora_da_
          +politica |                                                    
      430 +| d-006 | 54,90 | não | 60,00 | 54,90 | aprovado | — |        
      431 +| d-007 | 54,90 | — | — | 0,00 | recusado | duplicata |       
      432 +| d-008 | 41,00 | — | — | 0,00 | recusado | fora_do_periodo | 
      433 +| d-009 | -45,00 | — | — | 0,00 | recusado | valor_invalido | 
      434 +| d-010 | 480,00 | sim | 250,00 | 250,00 | parcial | limite_di
          +ario_excedido |                                               
      435 +| d-011 | 33,33 | sim | 90,00 | 33,33 | aprovado | — |        
      436 +| d-012 | 47,20 | não | 60,00 | 47,20 | aprovado | — |        
      437 +| d-013 | 690,00 | — | — | 0,00 | recusado | nota_fiscal_ausen
          +te |                                                          
      438 +| d-014 | 61,00 | não | 60,00 | 60,00 | parcial | limite_diari
          +o_excedido |                                                  
      439  
      440 +("—" = nulo: o item foi recusado antes do limite diário.)     
      441 +                                                              
      442  Totais: `valor_solicitado` = 1.861,84 · `valor_reembolsado` = 
           585,43 · `valor_glosado` = 1.276,41.
      443  
      416 -> d-011 (café no hotel em 15/07) não está em viagem: d-010 é u
          -ma diária só em 14/07 (AMB-005).                              
      417 -                                                              
      444  ## 10. O que fica em aberto
      445  
      446 +### Decisões provisórias                                      
      447 +                                                              
      448  - **Datas de entrada e saída de hospedagem.** A solução corret
           a para AMB-005 exige mudar o formato de entrada. Decisão provi
           sória: um lançamento = uma diária. Consequência conhecida: d-0
           10 recebe 250,00 de 480,00 mesmo se forem de fato duas diárias
           .
      449  - **Ids repetidos na entrada.** A política não trata. Decisão 
           provisória: despesas com o mesmo `id` são avaliadas normalment
           e, cada uma pelo seu conteúdo; a saída repete o id.
      450  - **`competencia` inconsistente com `inicio`/`fim`.** Decisão 
           provisória: o período vale por `inicio` e `fim`; `competencia`
            só é repetida na saída.
      451  - **Estorno vinculado a uma despesa.** Se o formato um dia tro
           uxer referência à despesa original, AMB-013 deve ser revista.
      452 +                                                              
      453 +### Riscos conhecidos e aceitos                               
      454 +                                                              
      455 +- **Fracionamento para escapar da nota fiscal** (AMB-008): trê
          +s hospedagens sem nota de 100,00 + 99,99 + 50,01 na mesma data
          + recebem 250,00, enquanto uma de 250,00 sem nota recebe 0. O g
          +anho é limitado aos casos em que o limite diário passa de 100,
          +00 (hospedagem e transporte em viagem). Aceito para não recusa
          +r despesas pequenas legítimas sem nota.                       
      456 +- **Quase-duplicatas** (AMB-010): o mesmo gasto relançado com 
          +data vizinha, valor diferente em um centavo ou fornecedor com 
          +outra grafia (além de caixa, acentos e espaços nas pontas) não
          + é detectado. Aceito porque qualquer critério aproximado seria
          + regra inventada e poderia recusar gastos legítimos repetidos.

⏺ Agora a entrada D-001 no DECISIONS.md.

⏺ Write(specs/001-motor-reembolso/DECISIONS.md)
  ⎿  Added 25 lines, removed 23 lines
      10  
      11  ---
      12  
      13 -## D-002 — <título curto> · `<data>`                           
      13 +## D-001 — Revisão adversarial e análise dos dados: spec 1.0 → 
         +1.1 · `2026-10-01`                                             
      14  
      15 -**Gatilho:** <o que provocou: envelope lacrado / erro descobert
         -o na implementação /                                           
      16 -ambiguidade que só apareceu ao testar / o Claude apontou uma co
         -ntradição>                                                     
      15 +**Gatilho:** revisão da spec 1.0 (commit `c8bcad9`) antes do pl
         +ano, em duas frentes: o subagente `spec-adversary` (9 problemas
         +, 2 bloqueantes) e uma nova análise item a item de `exemplos/de
         +spesas-exemplo.json`. Os 13 pontos resultantes foram decididos 
         +um a um pelo responsável (sessão `docs/sessions/05-*`).        
      16  
      18 -**O que mudou na spec:** <de → para, citando o ID da regra>    
      19 -                                                               
      20 -**Por quê:**                                                   
      21 -                                                               
      22 -**O que isso invalidou:** <requisitos, decisões técnicas, teste
         -s que caíram>                                                  
      23 -                                                               
      24 -**Tasks afetadas:** <as que precisaram ser refeitas + as novas 
         -criadas>                                                       
      25 -                                                               
      26 -**Custo:** <quantos arquivos tocados, quanto tempo>            
      27 -                                                               
      28 ----                                                            
      29 -                                                               
      30 -## D-001 — <título curto> · `<data>`                           
      31 -                                                               
      32 -**Gatilho:**                                                   
      33 -                                                               
      17  **O que mudou na spec:**
      18  
      36 -**Por quê:**                                                   
      19 +| # | Ponto | De (1.0) | Para (1.1) | Onde |                   
      20 +|---|---|---|---|---|                                          
      21 +| 1 | d-008 "lançado com atraso" | recusa pela data da despesa 
         +| **mantido**; justificativa reforçada (a regra seria letra mor
         +ta na leitura literal) | AMB-009 |                             
      22 +| 2a | Prova de viagem | qualquer hospedagem válida | só hosped
         +agem **com nota fiscal** | RN-010, AMB-004 |                   
      23 +| 2b | Dias em viagem | só a data da diária | data da diária **
         +e o dia seguinte** | RN-010, RN-012, AMB-004 |                 
      24 +| 3 | Nota fiscal fracionada | por lançamento, sem menção ao ri
         +sco | **mantido** por lançamento; brecha registrada como risco 
         +aceito | AMB-008, seção 10 |                                   
      25 +| 3b | Valor de 100,00 em viagem | implícito | explícito: **não
         + amplia** | RN-008, AMB-007 |                                  
      26 +| 4a | Ordem nota × duplicata | duplicata (6) antes da nota (7)
         + | **nota (6) antes da duplicata (7)**; despesa sem nota sai da
         + comparação | RN-007, RN-008, seção 8, AMB-010, AMB-016 |      
      27 +| 4b | Quase-duplicatas | não mencionado | comparação exata **m
         +antida**; registrado como risco aceito | RN-007, seção 10 |    
      28 +| 5a | Valor zero | `valor_invalido` (não aprovado explicitamen
         +te) | **confirmado** | RN-004, AMB-013 |                       
      29 +| 5b | Acentos | não ignorados (`alimentação` recusada) | **ign
         +orados** na categoria e no fornecedor | seção 5 (normalização),
         + RN-006, RN-007, AMB-011 |                                     
      30 +| 6 | d-001 "Almoço com cliente" | não tratado | alimentação no
         +rmal; representação como evolução | AMB-017 (nova), seção 3 |  
      31 +| 7 | Campos de despesa `entrada_invalida` | indefinidos | `val
         +or_considerado` nulo, categoria como veio, **fora dos totais** 
         +| RN-002, seção 4 |                                            
      32 +| 8 | `valor_informado` × 2 casas | contraditórios | `valor_inf
         +ormado` isento; é o número recebido | seção 4 |                
      33 +| 9 | Entrada malformada | lacunas | `colaborador` ausente = er
         +ro de arquivo; elemento não-objeto = `entrada_invalida`; `id`/`
         +data` podem ser nulos; campos extras ignorados | RN-002, seção 
         +4 |                                                            
      34 +| 10 | Formato de saída | proposto | **confirmado**; limite esg
         +otado = `recusado`; justificativa não contratual | seção 4, RN-
         +009 |                                                          
      35 +| 11 | Seção 9 (resultado do exemplo) | "nenhuma data em viagem
         +" — **erro**: contradizia a RN-010 para d-010 | 14/07 e 15/07 e
         +m viagem; d-011 com limite 90,00. Valores e totais inalterados 
         +| seção 9 |                                                    
      36 +| 13 | Pontos em aberto | — | ids repetidos e `competencia` inc
         +onsistente mantidos como decisões provisórias | seção 10 |     
      37  
      38 -**O que isso invalidou:**                                      
      38 +**Por quê:** os dois bloqueantes (7 e 8) obrigariam o código a 
         +inventar regra; as brechas 2a, 3 e 4 mudavam valores em cenário
         +s plausíveis; o item 11 era um erro de redação da 1.0 apontado 
         +pelo `spec-adversary`.                                         
      39  
      40 -**Tasks afetadas:**                                            
      40 +**O que isso invalidou:** nenhum código ou teste (ainda não exi
         +stiam). Na spec: a etapa 6/7 da ordem de aplicação, a definição
         + de viagem, o caso de borda "duplicata depois de despesa recusa
         +da por nota" (agora as duas cópias são `nota_fiscal_ausente`) e
         + o caso "categoria com acento" (agora reconhecida).            
      41  
      42 -**Custo:**                                                     
      42 +**Tasks afetadas:** nenhuma (o `tasks.md` ainda não foi escrito
         +).                                                             
      43 +                                                               
      44 +**Custo:** 2 arquivos (`spec.md`, `DECISIONS.md`); revisão de 1
         +3 pontos numa sessão.                                          

  Ran 1 shell command (ctrl+o to expand)

⏺ Fiz o commit da v1.0 (c8bcad9) e apliquei as suas 13 decisões. A v1.1 está
  pronta para você revisar e ainda não tem commit.

  Mudanças na spec.md (v1.0 → v1.1):

  ┌────────────────────────────────────┬────────────────────────────────────┐
  │               Ponto                │             Onde está              │
  ├────────────────────────────────────┼────────────────────────────────────┤
  │ 1. d-008 recusado pela data da     │ AMB-009, justificativa reforçada   │
  │ despesa                            │                                    │
  ├────────────────────────────────────┼────────────────────────────────────┤
  │ 2a e 2b. Viagem só com hospedagem  │ RN-010, RN-012, AMB-004, mais 4    │
  │ com nota, cobrindo a data da       │ casos de borda novos               │
  │ diária e o dia seguinte            │                                    │
  ├────────────────────────────────────┼────────────────────────────────────┤
  │ 3 e 3b. Nota por lançamento; o     │ RN-008, AMB-007, AMB-008, seção 10 │
  │ valor de 100 não amplia em viagem  │  "Riscos aceitos"                  │
  ├────────────────────────────────────┼────────────────────────────────────┤
  │ 4a. Nota verificada antes da       │ seção 8 (etapas 6 e 7 trocadas),   │
  │ duplicata                          │ RN-007, tabela de motivos          │
  ├────────────────────────────────────┼────────────────────────────────────┤
  │ 4b. Comparação exata de duplicatas │ RN-007, seção 10 "Riscos aceitos"  │
  ├────────────────────────────────────┼────────────────────────────────────┤
  │ 5a e 5b. Valor zero recusado;      │ regra de normalização nova no      │
  │ acentos ignorados                  │ início da seção 5, usada pela      │
  │                                    │ RN-006 e pela RN-007               │
  ├────────────────────────────────────┼────────────────────────────────────┤
  │ 6. Refeição com cliente            │ AMB-017 nova, seção 3 (evolução    │
  │                                    │ recomendada)                       │
  ├────────────────────────────────────┼────────────────────────────────────┤
  │ 7, 8 e 9. Contrato de saída e      │ RN-002 reescrita; seção 4 com      │
  │ entrada malformada                 │ campos que podem ser nulos e regra │
  │                                    │  dos totais                        │
  ├────────────────────────────────────┼────────────────────────────────────┤
  │ 10. Formato confirmado             │ seção 4, RN-009                    │
  ├────────────────────────────────────┼────────────────────────────────────┤
  │ 11. Correção do meu erro           │ seção 9: 14/07 e 15/07 em viagem,  │
  │                                    │ e o d-011 com limite 90,00         │
  ├────────────────────────────────────┼────────────────────────────────────┤
  │ 13. Pontos em aberto               │ seção 10                           │
  └────────────────────────────────────┴────────────────────────────────────┘

  A spec tem agora 17 ambiguidades e 34 casos de borda. O resultado do exemplo
  continua com os mesmos totais: R$ 1.861,84 solicitados, R$ 585,43 reembolsados
  e R$ 1.276,41 glosados.

  No DECISIONS.md, a entrada D-001 tem uma tabela "de → para" com os 13 pontos.
  Ela registra:
  - o que cada mudança invalidou: a ordem das etapas e dois casos de borda que
    mudaram de resultado;
  - o erro da seção 9 que o revisor pegou.

  Sugestão antes do commit: rodar o spec-adversary mais uma vez, agora sobre a
  v1.1. Nesta revisão mudaram regras importantes (viagem, ordem das etapas,
  normalização), e mudanças assim costumam abrir brechas novas. Assim teríamos
  uma segunda rodada de evidência para o relatório.

  Como prefere seguir?
  1. Você lê o diff (git diff), e eu faço o commit docs(spec): v1.1 aplica 
     decisões da revisão adversarial (D-001).
  2. Primeiro roda o spec-adversary na v1.1, e o commit vem depois.

✻ Churned for 2m 44s · done 9:38 PM

❯ opção 2, roda o spec-adversary na v1.1                                        

⏺ spec-adversary(Revisão adversarial da spec v1.1)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ O spec-adversary está revisando a v1.1. Pedi atenção especial ao que mudou
  nesta versão:
  - a definição de viagem;
  - a nova ordem das etapas;
  - a normalização com acentos;
  - a entrada malformada;
  - os totais.

  Também pedi que ele não repita o que a D-001 já registra como resolvido ou
  como risco aceito.

  Assim que ele terminar, trago os achados e passamos por eles um a um, como
  antes.

✻ Sautéed for 12s · done 9:39 PM

› Message from spec-adversary
  Resumo: encontrei 6 problemas na spec 1.1. Um é bloqueante (o nº 1).

  Arquivos lidos:
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md`,
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md`,
  `/Users/rafaeltxm/repo/sdd-desafio/exemplos/despesas-exemplo.json` e
  `/Users/rafaeltxm/repo/sdd-desafio/DESAFIO.md` (seção da política). Não li
  `src/` nem `tests/` e não alterei nenhum arquivo.

  Conferi as contas da seção 9. Elas batem com a spec 1.1: solicitado 1.861,84,
  reembolsado 585,43, glosado 1.276,41, e d-011 com limite 90,00. Os 9 itens da
  política do RH têm tratamento na spec.

  ---

  ### 1. Uma duplicata de hospedagem de até 100,00 faz a viagem depender da
  ordem da entrada — BLOQUEANTE — contradição

  - **Regras afetadas:** RN-007, RN-008, RN-010, seção 8 (etapas 6 a 8),
  AMB-010, AMB-004.
  - **Cenário de entrada:** período de 01/07 a 31/07.
    - `h-1`: 14/07, hospedagem, fornecedor "Pousada Sol", 90,00,
  `tem_nota_fiscal` false
    - `h-2`: 14/07, hospedagem, fornecedor "Pousada Sol", 90,00,
  `tem_nota_fiscal` true (relançamento com a nota)
    - `a-1`: 15/07, alimentação, 80,00, com nota
  - **Comportamento pela leitura literal:**
    - Na ordem h-1, h-2, a-1: h-1 tem até 100,00, então passa da etapa 6 mesmo
  sem nota. h-2 vira `duplicata`, porque a RN-007 não compara `tem_nota_fiscal`.
  Pela RN-010, h-1 não comprova viagem (está sem nota) e h-2 também não (foi
  recusada na etapa 7). Resultado: 14/07 e 15/07 ficam fora de viagem, e a-1 sai
  `parcial` com 60,00.
    - Na ordem h-2, h-1, a-1: h-2 é a original e comprova viagem. 14/07 e 15/07
  ficam em viagem, e a-1 sai `aprovado` com 80,00.
    - A mesma diferença vale para transporte (80,00 contra 120,00). No total,
  são até +70,00 por dia, em dois dias.
  - **Por que é um problema:** a AMB-010 justifica pôr a nota antes da duplicata
  dizendo que isso "torna o resultado independente da ordem e permite corrigir
  uma nota faltante". A RN-010 diz que a viagem vale "independentemente da ordem
  em que aparecem na entrada". Abaixo de 100,00 a etapa 6 não filtra nada.
  Então as duas cópias chegam à etapa 7, e é a ordem que decide qual
  `tem_nota_fiscal` sobrevive. Esse campo pesa justamente na prova de viagem.
  Corrigir a nota de uma hospedagem barata não funciona se a cópia sem nota veio
  antes. Um teste escrito a partir da justificativa espera um resultado; um
  teste escrito a partir da regra literal espera outro.
  - **Pergunta para decisão:** quando duas hospedagens são duplicatas pela
  RN-007 e só uma tem nota, a data fica em viagem ou não? E o resultado pode
  depender da ordem da entrada?

  ### 2. Uma hospedagem de valor irrisório com nota declarada amplia os limites
  por dois dias — PODE ESPERAR — brecha

  - **Regras afetadas:** RN-010, AMB-004 (justificativa), RN-003, seção 3 (a
  spec confia em `tem_nota_fiscal`).
  - **Cenário de entrada:** 14/07, hospedagem, 0,01 (ou `valor` 0.005, que
  arredonda para 0,01), `tem_nota_fiscal` true. Alimentação de 90,00 e
  transporte de 120,00 em 14/07 e também em 15/07, todos com nota.
  - **Comportamento pela leitura literal:** a hospedagem é aprovada com 0,01 e
  põe 14/07 e 15/07 em viagem. As outras quatro despesas são aprovadas inteiras:
  são 140,00 a mais do que fora de viagem, por 0,01 declarado.
  - **Por que é um problema:** a AMB-004 diz que exigir nota fecha o caso
  "hospedagem de 0,01 ampliaria o teto do dia em 70,00". Mas a nota é só um
  booleano informado pelo próprio colaborador, que a seção 3 manda aceitar sem
  verificar. Então a exigência não fecha o caso. Com o dia seguinte, ele ainda
  dobrou. A justificativa registrada não corresponde ao efeito da regra, e o
  caso não aparece entre os riscos aceitos da seção 10.
  - **Pergunta para decisão:** uma hospedagem com nota declarada e valor
  irrisório deve comprovar viagem em D e D+1? Se deve, isso entra como risco
  aceito na seção 10?

  ### 3. A normalização de texto não diz o que conta como "espaço" e "acento",
  nem trata separadores internos — PODE ESPERAR — ambiguidade

  - **Regras afetadas:** seção 5 (normalização de texto), RN-006, RN-007,
  AMB-011.
  - **Cenários de entrada:**
    - (a) categoria `"Transporte Urbano"` ou `"transporte-urbano"`, 50,00, com
  nota;
    - (b) categoria `"alimentacao\t"` (tab no fim) ou `"alimentacao"` seguida de
  espaço não separável;
    - (c) fornecedor `"Pão  Quente"` (dois espaços) contra `"Pao Quente"`, com
  os outros campos iguais;
    - (d) `"alimentação"` escrita com acento combinante (forma decomposta) em
  vez do caractere pré-composto; letras como `ü` e `ñ`.
  - **Comportamento pela leitura literal:**
    - (a) é recusada com `categoria_fora_da_politica`, porque os espaços
  internos não são alterados e `_` não é tratado.
    - (b) depende de tab ou espaço não separável contar como "espaço".
    - (c) não é duplicata.
    - (d) depende do que conta como "acento": os exemplos só citam `á`, `ç` e
  `ô`.
  - **Por que é um problema:** a AMB-011 justifica a normalização dizendo que
  "recusar `alimentação` puniria quem escreve corretamente em português".
  "Transporte urbano" é exatamente como o RH escreveu o item 2 da política, mas
  é recusada. Em (b) e (d), duas implementações razoáveis aprovam ou recusam a
  mesma despesa.
  - **Pergunta para decisão:** quais caracteres a normalização remove ou
  equipara (espaços em branco além do espaço comum, marcas de acento em geral,
  `_`, `-` e espaço entre palavras)? `transporte urbano` deve ser reconhecida?

  ### 4. O schema de saída não cobre campos com o tipo errado na entrada — PODE
  ESPERAR — lacuna

  - **Regras afetadas:** seção 4 (Saída: `itens[].id`, `itens[].data`,
  `itens[].categoria`, `periodo.competencia`), RN-002, RN-003.
  - **Cenários de entrada:**
    - despesa com `"id": 17`, `"data": 20260703` ou `"categoria":
  ["alimentacao"]`;
    - `periodo.competencia` igual a `202607` (número) ou `"julho"`;
    - despesa com `valor` -0.005.
  - **Comportamento pela leitura literal:**
    - As três despesas viram `entrada_invalida`. Mas a saída manda copiar `id`,
  `data` e `categoria` "como veio", e o schema declara esses campos como "texto
  ou nulo". Copiar 17 ou um array viola o tipo; trocar por nulo viola o "como
  veio".
    - `competencia` "copiada da entrada" não tem tipo nem formato definido na
  saída.
    - Para -0.005, "metade para cima" pode dar -0,00 ou -0,01. Os dois
  resultados são `valor_invalido`, mas `valor_considerado` sai diferente.
    - A interface também não diz o que acontece se o arquivo de saída não puder
  ser gravado: ele não está na lista de erros de arquivo da RN-002.
  - **Por que é um problema:** os valores reembolsados não mudam, mas a saída
  deixa de ser determinística ou de seguir o contrato do schema. A seção 9 exige
  "a mesma entrada sempre produz a mesma saída".
  - **Pergunta para decisão:** quando `id`, `data`, `categoria` ou `competencia`
  vêm com tipo não textual, a saída copia o valor, troca por nulo ou converte
  para texto? Como fica o arredondamento da metade em valores negativos? Falha
  ao gravar a saída é erro de arquivo?

  ### 5. Texto vazio passa como campo obrigatório válido — PODE ESPERAR — lacuna

  - **Regras afetadas:** RN-002, RN-007.
  - **Cenário de entrada:** duas despesas em 09/07, alimentação, 30,00, com
  nota, `fornecedor` `""` (ou `"   "`), e `id` `""` em ambas.
  - **Comportamento pela leitura literal:** os campos são "texto", então nenhuma
  das duas é `entrada_invalida`. Depois da normalização os fornecedores ficam
  iguais, então a segunda vira `duplicata`. Se uma tiver fornecedor `""` e a
  outra `"Padaria"`, as duas são avaliadas.
  - **Por que é um problema:** o fornecedor é obrigatório justamente porque
  serve para detectar duplicatas. Um texto vazio cumpre o tipo e anula esse
  papel. Um `id` vazio torna o item da saída impossível de identificar.
  - **Pergunta para decisão:** texto vazio, ou só com espaços, em `id`,
  `categoria` ou `fornecedor` conta como campo presente ou como
  `entrada_invalida`?

  ### 6. O DECISIONS.md diz "13 pontos", mas a tabela da D-001 não tem o ponto
  12 — PODE ESPERAR — lacuna (rastreabilidade)

  - **Regra afetada:** nenhuma regra de negócio. Afeta a D-001.
  - **Cenário de entrada:** não se aplica.
  - **Comportamento atual:** a tabela vai do item 11 direto para o 13. O texto
  diz que "os 13 pontos resultantes foram decididos um a um".
  - **Por que é um problema:** não dá para saber se o ponto 12 foi decidido sem
  ser registrado, se foi descartado ou se é só um erro de numeração. Assim, não
  se consegue confirmar que a spec 1.1 reflete todas as decisões.
  - **Pergunta para decisão:** o que foi o ponto 12 e qual foi a decisão sobre
  ele?

  ---

  **Decidir antes da implementação:** 1.

  **Pode ser decidido depois:** 2, 3, 4, 5, 6.

⏺ O spec-adversary terminou a revisão da v1.1. Ele confirmou de novo os totais
  da seção 9 e encontrou 6 problemas, 1 bloqueante. Uma constatação honesta
  antes de começarmos: dois dos achados são falhas minhas na v1.1, e vou
  registrá-las para o relatório.
  - Nº 6: a tabela da D-001 pula do ponto 11 para o 13. Esqueci de incluir o
    ponto 12, que foi a sua decisão de processo (commit da v1.0 como "antes" e
    D-001 para as mudanças). Correção simples, sem decisão.
  - Nº 2: escrevi na AMB-004 que exigir nota "fecha" a brecha da hospedagem de
    R$ 0,01. Não fecha: a nota é só uma marcação que o próprio colaborador
    informa.

  Vamos aos pontos, começando pelo bloqueante.

  ---

  Ponto 1 de 5: duplicata de hospedagem de até R$ 100 ⚠️ bloqueante

  h-1  14/07  hospedagem  "Pousada Sol"  90,00  SEM nota
  h-2  14/07  hospedagem  "Pousada Sol"  90,00  COM nota   ← relançamento com a 
  nota
  a-1  15/07  alimentacao                80,00  com nota

  Como 90,00 está abaixo de 100, a etapa da nota não recusa o h-1. As duas
  cópias chegam juntas à etapa de duplicata, e a ordem decide qual sobrevive:

  ┌──────────┬────────────────┬───────────────────────┬────────────────┐
  │  Ordem   │   Sobrevive    │ Viagem em 14 e 15/07? │      a-1       │
  ├──────────┼────────────────┼───────────────────────┼────────────────┤
  │ h-1, h-2 │ h-1 (sem nota) │ ❌ não                │ 60,00 parcial  │
  ├──────────┼────────────────┼───────────────────────┼────────────────┤
  │ h-2, h-1 │ h-2 (com nota) │ ✅ sim                │ 80,00 aprovado │
  └──────────┴────────────────┴───────────────────────┴────────────────┘

  Isso contradiz o que você decidiu no ponto 4a (o resultado não deve depender
  da ordem). As opções:

  Opção: A
  Regra: entre duplicatas, vale a primeira que tem nota fiscal; se nenhuma
  tiver,
  vale a primeira na ordem
  Efeito: sempre sobrevive o h-2, e há viagem nas duas ordens. Paga 90,00 uma
  vez
  ────────────────────────────────────────
  Opção: B
  Regra: tem_nota_fiscal passa a fazer parte da comparação de duplicatas
  Efeito: h-1 e h-2 deixam de ser duplicatas, e as duas são pagas (90,00 +
  90,00): reembolso em dobro ❌
  ────────────────────────────────────────
  Opção: C
  Regra: a prova de viagem considera também a cópia descartada como duplicata,
  se
  tiver nota
  Efeito: viagem nas duas ordens, mas sobrevive (e é paga) a cópia sem nota.
  Funciona, mas a regra fica mais complicada de explicar

  Minha recomendação: a A. Ela segue a mesma lógica do ponto 4a ("corrigir a
  nota funciona"), elimina a dependência da ordem e não paga em dobro.

  Qual é a sua visão?

✻ Sautéed for 14s · done 9:42 PM

⏺ Agent "Revisão adversarial da spec v1.1" finished · 2m 32s

❯ opção A, vale a primeira com nota                                             

⏺ ✅ Ponto 1 decidido: A. Entre duplicatas, vale a primeira que tem nota fiscal;
  se nenhuma tiver, vale a primeira na ordem da entrada.

  ---

  Ponto 2 de 5: hospedagem irrisória com nota declarada

  14/07  hospedagem   0,01  COM nota (declarada)   ← põe 14/07 e 15/07 em viagem
  14/07  alimentacao 90,00 · transporte 120,00
  15/07  alimentacao 90,00 · transporte 120,00

  Com R$ 0,01 de hospedagem, o colaborador ganha R$ 140,00 a mais de teto em
  dois dias. A exigência de nota (ponto 2a) só funciona se a nota existir de
  fato, mas o sistema confia no campo tem_nota_fiscal sem verificar nada (seção
  3, fora de escopo).

  Opção: A: aceitar como risco
  Regra: mantém a regra; corrige a justificativa da AMB-004 (que hoje diz que a
  nota "fecha" a brecha) e registra o caso em "Riscos aceitos"
  Problema: a brecha continua, mas fica declarada
  ────────────────────────────────────────
  Opção: B: valor mínimo de hospedagem para provar viagem
  Regra: ex.: só prova viagem se a hospedagem for de pelo menos R$ X
  Problema: o valor X não existe na política: seria regra inventada, e qualquer
  número seria arbitrário
  ────────────────────────────────────────
  Opção: C: viagem só com hospedagem acima de R$ 100
  Regra: usa o valor da própria política (acima de 100, a nota é obrigatória)
  Problema: reaproveita um número da política com outro sentido, e uma pousada
  legítima de R$ 90 deixaria de provar viagem

  O sistema não verifica a nota em nenhuma regra, então qualquer controle
  baseado em tem_nota_fiscal depende da boa-fé de quem lança. Isso vale para a
  regra de nota da política inteira, não só para a viagem. Quem detecta uma nota
  declarada que não existe é a conferência humana, que já está fora do escopo.

  Minha recomendação: a A. Corrijo a justificativa para não prometer mais do que
  a regra entrega e registro o caso como risco aceito: "a prova de viagem
  depende do tem_nota_fiscal declarado; uma hospedagem de valor irrisório com
  nota declarada amplia os limites de D e D+1".

  Qual é a sua visão?

✻ Churned for 5m 49s · done 9:45 PM

❯ criar uma flag de em_viagem iria contra as regras do desafio ne?              

⏺ Sim. Uma flag em_viagem na entrada vai contra as regras do desafio, pelos
  mesmos motivos das datas de entrada e saída de hospedagem:

  1. O formato de entrada é fixo: "respeite esse formato". Um campo novo
     obrigatório quebra a interface.
  2. Como campo opcional, também não resolveria: os casos ocultos do instrutor
     seguem o formato do exemplo, sem a flag. Nesses casos, a viagem continuaria
     vindo da regra da hospedagem, e a brecha seria a mesma.
  3. Contradiz a sua decisão 9d: campos extras são ignorados. Para aceitar a
     flag, teríamos de abrir uma exceção nessa regra.

  Na saída, a flag já existe: itens[].em_viagem mostra, item por item, se a data
  foi considerada em viagem. Isso é permitido, porque a saída é você quem
  define. É ela que permite ao financeiro conferir e contestar um caso como o da
  hospedagem de R$ 0,01.

  Dá para registrar a sua ideia como evolução recomendada, junto com as datas de
  hospedagem e a representação: "informar viagem explicitamente na entrada (por
  exemplo, uma flag ou um código de viagem aprovada) eliminaria a inferência
  por hospedagem e a brecha do ponto 2".

  Então, para o formato atual, a pergunta continua a mesma. No ponto 2:
  - A: aceitar como risco (minha recomendação);
  - B: valor mínimo inventado;
  - C: só hospedagem acima de R$ 100 prova viagem.

  E registro a flag na entrada como evolução?

✻ Baked for 8s · done 9:45 PM

❯ opção A, e registra a flag como evolução                                      
⏺ ✅ Ponto 2 decidido: A. É um risco aceito. Corrijo a justificativa da AMB-004
  e registro a flag em_viagem na entrada como evolução recomendada.

  ---

  Ponto 3 de 5: o que exatamente a normalização de texto faz

  Hoje a spec diz: "remover espaços nas pontas, ignorar maiúsculas e minúsculas,
  ignorar acentos e cedilha (á→a, ç→c, ô→o); espaços internos não são
  alterados". O revisor achou quatro lacunas:

  ┌─────┬───────────────────────────┬───────────────┬───────────────────────┐
  │  #  │          Entrada          │     Hoje      │       Problema        │
  ├─────┼───────────────────────────┼───────────────┼───────────────────────┤
  │     │ categoria "Transporte     │ ❌ categoria  │ é exatamente como o   │
  │ a   │ Urbano" ou                │ fora da       │ RH escreveu o item 2  │
  │     │ "transporte-urbano"       │ política      │ da política, e mesmo  │
  │     │                           │               │ assim é recusada      │
  ├─────┼───────────────────────────┼───────────────┼───────────────────────┤
  │     │ "alimentacao" com um tab  │               │ depende do que conta  │
  │ b   │ ou um espaço especial no  │ indefinido    │ como "espaço"         │
  │     │ fim                       │               │                       │
  ├─────┼───────────────────────────┼───────────────┼───────────────────────┤
  │     │ fornecedor "Pão  Quente"  │ não são       │ espaços internos      │
  │ c   │ (dois espaços) e "Pao     │ duplicatas    │ fazem diferença       │
  │     │ Quente"                   │               │                       │
  ├─────┼───────────────────────────┼───────────────┼───────────────────────┤
  │     │ ü, ñ, ou um acento        │               │ a spec só dá três     │
  │ d   │ gravado de outra forma no │ indefinido    │ exemplos de acento    │
  │     │  arquivo                  │               │                       │
  └─────┴───────────────────────────┴───────────────┴───────────────────────┘

  Proposta de regra completa, a mesma para categoria e fornecedor:
  1. remover qualquer espaço em branco (espaço, tab, espaço especial) do início
     e do fim;
  2. ignorar maiúsculas e minúsculas;
  3. toda letra com acento ou sinal (á, ç, ô, ü, ñ...) vale como a letra sem
     sinal, qualquer que seja a forma como foi gravada no arquivo;
  4. qualquer sequência de espaços, hífens ou sublinhados no meio vale como um
     único separador.

  ┌─────────────────────────────────────────┬───────────────────────────────┐
  │                 Entrada                 │        Com a proposta         │
  ├─────────────────────────────────────────┼───────────────────────────────┤
  │ "Transporte Urbano",                    │                               │
  │ "transporte-urbano",                    │ ✅ transporte_urbano          │
  │ "TRANSPORTE_URBANO"                     │                               │
  ├─────────────────────────────────────────┼───────────────────────────────┤
  │ "alimentacao\t"                         │ ✅ alimentacao                │
  ├─────────────────────────────────────────┼───────────────────────────────┤
  │ "Pão  Quente" e "Pao Quente"            │ mesmo fornecedor, então podem │
  │                                         │  ser duplicata                │
  ├─────────────────────────────────────────┼───────────────────────────────┤
  │ "coworking"                             │ ❌ continua fora da política  │
  └─────────────────────────────────────────┴───────────────────────────────┘

  O item 4 é o único com algum risco: no fornecedor, "Pão-Quente" e "Pão Quente"
  passam a ser o mesmo. Esse risco é baixo, porque para ser duplicata a data, a
  categoria e o valor também precisam ser iguais.

  Minha recomendação: adotar a regra completa (itens 1 a 4).

  Qual é a sua visão?

✻ Cogitated for 12s · done 9:46 PM

❯ adotar a regra completa, itens 1 a 4                                          

⏺ ✅ Ponto 3 decidido. A regra completa de normalização vale para categoria e
  fornecedor: espaços em branco nas pontas, maiúsculas e minúsculas, todos os
  acentos e separadores internos.

  ---

  Ponto 4 de 5: campos com tipo errado e detalhes do contrato

  São quatro detalhes que não mudam nenhum valor reembolsado, mas deixam a saída
  indefinida:

  #: 4a
  Situação: despesa com "id": 17, "data": 20260703 ou "categoria": 
  ["alimentacao"] (tipo errado)
  Recomendação: a despesa é entrada_invalida, e o campo de tipo errado sai nulo
  Por quê: mantém o contrato da saída (esses campos são sempre "texto ou nulo");

  a posição na lista ainda identifica o item, porque a ordem é a da entrada
  ────────────────────────────────────────
  #: 4b
  Situação: periodo.competencia como número (202607) ou texto fora do padrão
  ("julho")
  Recomendação: se for texto, é copiado como veio; se não for texto, sai nulo.
  Não é erro de arquivo
  Por quê: competencia não entra em nenhum cálculo, então não deve derrubar o
  relatório
  ────────────────────────────────────────
  #: 4c
  Situação: arredondamento de valor negativo com a metade (-0.005)
  Recomendação: "metade para cima" passa a ser "metade afastando do zero": 0,005

  → 0,01 e -0,005 → -0,01
  Por quê: define o caso negativo sem mudar nada nos positivos; o item é
  recusado
  como valor_invalido de qualquer jeito
  ────────────────────────────────────────
  #: 4d
  Situação: o arquivo de saída não pode ser gravado (pasta inexistente, sem
  permissão)
  Recomendação: erro de arquivo: mensagem de erro e código de saída diferente de

  0
  Por quê: coerente com os outros erros de arquivo da RN-002

  Minha recomendação: adotar as quatro como estão.

  Qual é a sua visão?

✻ Worked for 10s · done 9:46 PM

❯ adotar as quatro conforme recomendado                                         

⏺ ✅ Ponto 4 decidido.
  - 4a: um campo com tipo errado sai nulo.
  - 4b: competencia é copiada se for texto; senão, sai nula.
  - 4c: o arredondamento usa "metade afastando do zero".
  - 4d: falha ao gravar a saída é erro de arquivo.

  ---

  Ponto 5 de 5: texto vazio em campo obrigatório

  d-1  09/07  alimentacao  30,00  com nota  fornecedor ""     id ""
  d-2  09/07  alimentacao  30,00  com nota  fornecedor "   "  id ""

  Hoje esses campos estão presentes e são texto, então passam na validação.
  Depois da normalização, os dois fornecedores ficam vazios e iguais, e o d-2
  vira duplicata do d-1. E se o d-1 tivesse fornecedor "" e o d-2 "Padaria", os
  dois seriam avaliados. Ou seja, um fornecedor vazio desliga a detecção de
  duplicatas, e um id vazio deixa o item sem identificação na saída.

  ┌───────────────┬─────────────────────────────────────────────────────────┐
  │     Opção     │                          Regra                          │
  ├───────────────┼─────────────────────────────────────────────────────────┤
  │ A: vazio é    │ id, categoria ou fornecedor vazios, ou só com espaços   │
  │ inválido      │ em branco, são recusados como entrada_invalida          │
  ├───────────────┼─────────────────────────────────────────────────────────┤
  │ B: vazio é    │ mantém como está, e o comportamento acima fica          │
  │ válido        │ registrado                                              │
  └───────────────┴─────────────────────────────────────────────────────────┘

  Minha recomendação: a A. A política exige esses campos justamente porque são
  usados (identificação, categoria, duplicata), e um texto vazio é o mesmo que
  um campo ausente. A categoria vazia já seria recusada como fora da política,
  mas com a opção A o motivo fica mais preciso.

  Ponto 6 (só correção, sem decisão): completo a tabela da D-001 com o ponto 12,
  que foi a sua decisão de processo: commit da v1.0 como "antes" e D-001 para
  as mudanças.

  Qual é a sua visão sobre o ponto 5?

✻ Crunched for 7s · done 9:47 PM

❯ opção A, vazio é inválido                                                     

⏺ ✅ Ponto 5 decidido: A. Texto vazio, ou só com espaços, em id, categoria ou
  fornecedor é entrada_invalida.

  As cinco decisões desta segunda rodada estão fechadas. Para manter o histórico
  limpo, vou:
  1. completar o ponto 12 na D-001 e fazer o commit da v1.1 como está;
  2. aplicar esta segunda rodada como v1.2, com uma entrada D-002.

  Assim o Git mostra as três versões da spec: 1.0 → 1.1 → 1.2.

⏺ Update(specs/001-motor-reembolso/DECISIONS.md)
  ⎿  Added 1 line
      33  | 9 | Entrada malformada | lacunas | `colaborador` ausente = er
          ro de arquivo; elemento não-objeto = `entrada_invalida`; `id`/`
          data` podem ser nulos; campos extras ignorados | RN-002, seção 
          4 |
      34  | 10 | Formato de saída | proposto | **confirmado**; limite esg
          otado = `recusado`; justificativa não contratual | seção 4, RN-
          009 |
      35  | 11 | Seção 9 (resultado do exemplo) | "nenhuma data em viagem
          " — **erro**: contradizia a RN-010 para d-010 | 14/07 e 15/07 e
          m viagem; d-011 com limite 90,00. Valores e totais inalterados 
          | seção 9 |
      36 +| 12 | Registro desta revisão | — | commit da 1.0 (`c8bcad9`) p
         +reservado como "antes"; mudanças registradas nesta entrada D-00
         +1 e aplicadas na 1.1 | `DECISIONS.md` |                        
      37  | 13 | Pontos em aberto | — | ids repetidos e `competencia` inc
          onsistente mantidos como decisões provisórias | seção 10 |
      38  
      39  **Por quê:** os dois bloqueantes (7 e 8) obrigariam o código a 
          inventar regra; as brechas 2a, 3 e 4 mudavam valores em cenário
          s plausíveis; o item 11 era um erro de redação da 1.0 apontado 
          pelo `spec-adversary`.

  Ran 1 shell command (ctrl+o to expand)
  ⎿  PostToolUse:Bash says: 📝 Fim do bloco de trabalho ("docs(spec): v1.1 
     aplica decisões da revisão adversarial (D-001)"). Exporte a sessão antes de
     continuar:
        /export docs/sessions/05-<descricao-curta>.md
        e commite com: docs(sessions): export da sessão 05

⏺ A v1.1 está no commit d35f68d. Agora vou aplicar a segunda rodada (v1.2), que
  ainda faz parte do mesmo bloco que você autorizou.

  Searched for 1 pattern (ctrl+o to expand)

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      1  # Spec — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.1 · **Status:** aprovada para planejamento · **Últ
        -ima alteração:** 2026-10-01 (ver `DECISIONS.md` D-001)          
      3 +**Versão:** 1.2 · **Status:** aprovada para planejamento · **Últ
        +ima alteração:** 2026-10-01 (ver `DECISIONS.md` D-001 e D-002)  
      4  
      5  > **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ
         . Nenhuma linha
      6  > aqui pode citar linguagem, biblioteca, classe, função ou estru
         tura de pasta.

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line
      29  - Não guarda histórico entre execuções: duplicatas só são detec
          tadas dentro da mesma entrada.
      30  - Não usa campos além dos previstos na seção 4; campos extras s
          ão ignorados (RN-002). Em particular, não usa datas de entrada 
          e saída de hospedagem: seriam a solução ideal para AMB-005, mas
           o formato de entrada é fixo. Fica registrado como evolução rec
          omendada.
      31  - Não tem categoria nem limite de representação (refeição com c
          liente): fica registrado como evolução recomendada (AMB-017).
      32 +- Não recebe indicação explícita de viagem na entrada (ex.: um 
         +indicador `em_viagem` ou um código de viagem aprovada): a viage
         +m é inferida da hospedagem (RN-010). Uma indicação explícita el
         +iminaria a inferência e o risco registrado na seção 10; fica re
         +gistrada como evolução recomendada, pois exige mudar o formato 
         +fixo.                                                          
      33  - Não trata feriados nem fins de semana de forma especial (AMB-
          015).
      34  
      35  ## 4. Entrada e saída

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      39  `<comando> calcular --input <arquivo de entrada> --output <arqu
          ivo de saída>`
      40  
      41  - Sucesso: grava o arquivo de saída e termina com código 0.
      42 -- Erro de arquivo (RN-002): não grava o arquivo de saída, escre
         -ve uma mensagem de erro e termina com código diferente de 0.   
      42 +- Erro de arquivo (RN-002), inclusive quando o arquivo de saída
         + não pode ser gravado: não deixa arquivo de saída, escreve uma 
         +mensagem de erro e termina com código diferente de 0.          
      43  
      44  ### Entrada
      45  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      69  | Campo | Tipo | Significado |
      70  |---|---|---|
      71  | `colaborador` | objeto | `id` e `nome`, copiados da entrada |
      72 -| `periodo` | objeto | `competencia` (ou nulo, se ausente), `in
         -icio` e `fim`, copiados da entrada |                           
      72 +| `periodo` | objeto | `inicio` e `fim`, copiados da entrada; `
         +competencia` copiada se for texto (em qualquer formato), nula s
         +e ausente ou não for texto |                                   
      73  | `itens` | lista | um item por elemento de `despesas`, **na me
          sma ordem** |
      74  | `itens[].id` | texto ou nulo | id da despesa como veio; nulo 
          se ausente ou se o elemento não é um objeto |
      75  | `itens[].data` | texto ou nulo | data da despesa como veio; n
          ulo se ausente ou se o elemento não é um objeto |

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 3 lines, removed 3 lines
      71  | `colaborador` | objeto | `id` e `nome`, copiados da entrada |
      72  | `periodo` | objeto | `inicio` e `fim`, copiados da entrada; `
          competencia` copiada se for texto (em qualquer formato), nula s
          e ausente ou não for texto |
      73  | `itens` | lista | um item por elemento de `despesas`, **na me
          sma ordem** |
      74 -| `itens[].id` | texto ou nulo | id da despesa como veio; nulo 
         -se ausente ou se o elemento não é um objeto |                  
      75 -| `itens[].data` | texto ou nulo | data da despesa como veio; n
         -ulo se ausente ou se o elemento não é um objeto |              
      76 -| `itens[].categoria` | texto ou nulo | categoria normalizada (
         -RN-006) se reconhecida; senão, como veio (nulo se ausente) |   
      74 +| `itens[].id` | texto ou nulo | id da despesa como veio, se fo
         +r texto; nulo se ausente, se não for texto ou se o elemento não
         + é um objeto |                                                 
      75 +| `itens[].data` | texto ou nulo | data da despesa como veio, s
         +e for texto; nulo se ausente, se não for texto ou se o elemento
         + não é um objeto |                                             
      76 +| `itens[].categoria` | texto ou nulo | categoria normalizada (
         +RN-006) se reconhecida; senão, como veio, se for texto; nulo se
         + ausente ou não for texto |                                    
      77  | `itens[].valor_informado` | número ou nulo | o número recebid
          o em `valor`, sem arredondamento; nulo se ausente ou não numéri
          co |
      78  | `itens[].valor_considerado` | número ou nulo | valor arredond
          ado ao centavo (RN-003); **nulo se a despesa foi recusada por `
          entrada_invalida`** |
      79  | `itens[].valor_reembolsado` | número | quanto será reembolsad
          o (0 se recusado) |

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 8 lines, removed 1 line
      124  
      125  As regras são aplicadas a cada despesa na ordem da seção 8. A 
           primeira regra que recusa uma despesa encerra a avaliação dela
           : cada despesa recusada tem exatamente um motivo.
      126  
      127 -**Normalização de texto** (usada em RN-006 e RN-007): remover 
          -espaços no início e no fim, ignorar maiúsculas/minúsculas e ig
          -norar acentos e cedilha (letras acentuadas e `ç` comparadas co
          -mo a letra base: `á`→`a`, `ç`→`c`, `ô`→`o`). Espaços internos 
          -não são alterados.                                            
      127 +**Normalização de texto** (usada em RN-006 e RN-007), aplicada
          + nesta ordem:                                                 
      128  
      129 +1. remover todo espaço em branco do início e do fim (espaço co
          +mum, tabulação, quebra de linha, espaço não separável e demais
          + caracteres de espaço em branco);                             
      130 +2. ignorar maiúsculas/minúsculas;                             
      131 +3. toda letra com acento ou sinal diacrítico é comparada como 
          +a letra base, qualquer que seja a forma como o caractere foi c
          +odificado no arquivo (`á`→`a`, `ç`→`c`, `ô`→`o`, `ü`→`u`, `ñ`→
          +`n`);                                                         
      132 +4. toda sequência interna de espaços em branco, hífens (`-`) e
          + sublinhados (`_`) vale como um único `_`.                    
      133 +                                                              
      134 +Exemplos: `"Transporte Urbano"`, `"transporte-urbano"` e `" TR
          +ANSPORTE__urbano "` → `transporte_urbano`; `"Pão  Quente"` e `
          +"pao-quente"` → `pao_quente`.                                 
      135 +                                                              
      136  ### RN-001 — Um resultado por despesa
      137  
      138  **Regra:** a saída tem exatamente um item para cada elemento d
           e `despesas`, na mesma ordem, inclusive os recusados. Os totai
           s seguem as fórmulas da seção 4.

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 3 lines, removed 2 lines
      142  ### RN-002 — Validação da entrada
      143  
      144  **Regra:**
      145 -- **Erro de arquivo** (nenhuma saída é gerada): arquivo ausent
          -e ou que não é JSON válido; `colaborador` ausente ou sem `id`/
          -`nome` em texto; `periodo.inicio`, `periodo.fim` ou `despesas`
          - ausentes; `inicio` ou `fim` que não são datas válidas `AAAA-M
          -M-DD`; `inicio` posterior a `fim`; `despesas` que não é lista.
      146 -- **Despesa inválida** (vira item `recusado` com motivo `entra
          -da_invalida`; as demais despesas seguem): elemento de `despesa
          -s` que não é um objeto; falta `id`, `data`, `categoria`, `forn
          -ecedor`, `valor` ou `tem_nota_fiscal`; `data` não é data válid
          -a `AAAA-MM-DD`; `valor` não é número; `tem_nota_fiscal` não é 
          -booleano; `id`, `categoria` ou `fornecedor` não são texto.    
      145 +- **Erro de arquivo** (nenhuma saída é deixada): arquivo de en
          +trada ausente ou que não é JSON válido; `colaborador` ausente 
          +ou sem `id`/`nome` em texto; `periodo.inicio`, `periodo.fim` o
          +u `despesas` ausentes; `inicio` ou `fim` que não são datas vál
          +idas `AAAA-MM-DD`; `inicio` posterior a `fim`; `despesas` que 
          +não é lista; arquivo de saída que não pode ser gravado. `perio
          +do.competencia` nunca causa erro: se não for texto, sai nula. 
      146 +- **Despesa inválida** (vira item `recusado` com motivo `entra
          +da_invalida`; as demais despesas seguem): elemento de `despesa
          +s` que não é um objeto; falta `id`, `data`, `categoria`, `forn
          +ecedor`, `valor` ou `tem_nota_fiscal`; `data` não é data válid
          +a `AAAA-MM-DD`; `valor` não é número; `tem_nota_fiscal` não é 
          +booleano; `id`, `categoria` ou `fornecedor` não são texto, ou 
          +são texto vazio ou só com espaços em branco.                  
      147 +- Na saída de uma despesa inválida, `id`, `data` e `categoria`
          + são copiados se forem texto e saem nulos caso contrário (tipo
          + errado, ausente ou elemento que não é objeto).               
      148  - Uma despesa recusada por `entrada_invalida` tem `valor_consi
           derado` nulo, categoria como veio, `em_viagem` e `limite_diari
           o` nulos, e não entra nos totais.
      149  - Campos extras, no arquivo ou nas despesas, são ignorados.
      150  **Origem:** necessidade operacional (a política não trata entr
           ada malformada); pontos 7 e 9 de D-001.

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      148  - Uma despesa recusada por `entrada_invalida` tem `valor_consi
           derado` nulo, categoria como veio, `em_viagem` e `limite_diari
           o` nulos, e não entra nos totais.
      149  - Campos extras, no arquivo ou nas despesas, são ignorados.
      150  **Origem:** necessidade operacional (a política não trata entr
           ada malformada); pontos 7 e 9 de D-001.
      151 -**Aceite:** despesa sem `tem_nota_fiscal` com `valor` 33.333 →
          - `recusado`, `entrada_invalida`, `valor_informado` 33.333, `va
          -lor_considerado` nulo, fora de `valor_solicitado`; as demais d
          -espesas são processadas normalmente. Elemento `null` em `despe
          -sas` → item com `id` e `data` nulos, `entrada_invalida`. Arqui
          -vo sem `colaborador` → nenhuma saída, código diferente de 0. H
          -ospedagem com campo extra `"noites": 2` → avaliada como uma di
          -ária (RN-012).                                                
      151 +**Aceite:** despesa sem `tem_nota_fiscal` com `valor` 33.333 →
          + `recusado`, `entrada_invalida`, `valor_informado` 33.333, `va
          +lor_considerado` nulo, fora de `valor_solicitado`; as demais d
          +espesas são processadas normalmente. Elemento `null` em `despe
          +sas` → item com `id` e `data` nulos, `entrada_invalida`. Arqui
          +vo sem `colaborador` → nenhuma saída, código diferente de 0. H
          +ospedagem com campo extra `"noites": 2` → avaliada como uma di
          +ária (RN-012). Despesa com `"id": 17` → `entrada_invalida`, `i
          +d` nulo na saída. Despesa com `fornecedor` `"   "` → `entrada_
          +invalida`. `competencia` 202607 (número) → processamento norma
          +l, `competencia` nula na saída. Caminho de saída em pasta inex
          +istente → nenhuma saída, código diferente de 0.               
      152  
      153  ### RN-003 — Arredondamento ao centavo
      154  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      152  
      153  ### RN-003 — Arredondamento ao centavo
      154  
      155 -**Regra:** antes de qualquer outra regra de valor, `valor` é a
          -rredondado para 2 casas decimais, com a metade arredondada par
          -a cima (0,005 → 0,01). Todas as regras usam o valor arredondad
          -o (`valor_considerado`), e todos os cálculos são exatos ao cen
          -tavo.                                                         
      155 +**Regra:** antes de qualquer outra regra de valor, `valor` é a
          +rredondado para 2 casas decimais, com a metade arredondada afa
          +stando do zero (0,005 → 0,01; -0,005 → -0,01). Todas as regras
          + usam o valor arredondado (`valor_considerado`), e todos os cá
          +lculos são exatos ao centavo.                                 
      156  **Origem:** AMB-014.
      157  **Aceite:** `valor` 33.333 → `valor_considerado` 33.33; `valor
           ` 10.005 → 10.01; `valor` 10.004 → 10.00.
      158  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      172  
      173  **Regra:** a categoria é comparada depois da normalização de t
           exto (seção 5). Só três categorias são reconhecidas: `alimenta
           cao`, `transporte_urbano` e `hospedagem`. Na saída, categorias
            reconhecidas aparecem nessa forma normalizada. Qualquer outra
            → `recusado`, motivo `categoria_fora_da_politica`.
      174  **Origem:** política do RH, item 9; AMB-011; AMB-012.
      175 -**Aceite:** `ALIMENTACAO`, `" Alimentacao "` e `alimentação` →
          - tratadas como `alimentacao`; `coworking` → `categoria_fora_da
          -_politica`.                                                   
      175 +**Aceite:** `ALIMENTACAO`, `" Alimentacao "`, `"alimentacao\t"
          +` e `alimentação` → tratadas como `alimentacao`; `"Transporte 
          +Urbano"` e `"transporte-urbano"` → `transporte_urbano`; `cowor
          +king` → `categoria_fora_da_politica`.                         
      176  
      177  ### RN-007 — Duplicatas
      178  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      176  
      177  ### RN-007 — Duplicatas
      178  
      179 -**Regra:** duas despesas são duplicatas quando têm a mesma `da
          -ta`, a mesma categoria normalizada, o mesmo `fornecedor` norma
          -lizado (seção 5) e o mesmo `valor_considerado`. `id`, `descric
          -ao` e `tem_nota_fiscal` não entram na comparação. Só participa
          -m da comparação despesas que passaram pelas etapas 1 a 6 da se
          -ção 8 (inclusive a nota fiscal): uma despesa recusada antes di
          -sso não é "original" de ninguém. Entre duplicatas, só a primei
          -ra na ordem da entrada segue avaliada; as seguintes são `recus
          -ado`, motivo `duplicata`, e não consomem limite. A comparação 
          -é exata: datas, valores ou fornecedores diferentes após a norm
          -alização não são duplicatas (risco aceito, seção 10).         
      179 +**Regra:** duas despesas são duplicatas quando têm a mesma `da
          +ta`, a mesma categoria normalizada, o mesmo `fornecedor` norma
          +lizado (seção 5) e o mesmo `valor_considerado`. `id`, `descric
          +ao` e `tem_nota_fiscal` não entram na comparação. Só participa
          +m da comparação despesas que passaram pelas etapas 1 a 6 da se
          +ção 8 (inclusive a nota fiscal): uma despesa recusada antes di
          +sso não é "original" de ninguém. Dentro de cada grupo de despe
          +sas duplicatas entre si, segue avaliada uma só, a **original**
          +: a primeira na ordem da entrada que tem `tem_nota_fiscal` ver
          +dadeiro; se nenhuma do grupo tem, a primeira na ordem da entra
          +da. Todas as outras do grupo são `recusado`, motivo `duplicata
          +`, e não consomem limite nem comprovam viagem. Assim, qual cóp
          +ia sobrevive não depende da ordem quando só uma delas tem nota
          +. A comparação é exata: datas, valores ou fornecedores diferen
          +tes após a normalização não são duplicatas (risco aceito, seçã
          +o 10).                                                        
      180  **Origem:** política do RH, item 8; AMB-010.
      181  **Aceite:** d-006 e d-007 (mesmos data, categoria, fornecedor 
           e valor 54,90, ambas com nota) → d-006 avaliada normalmente, d
           -007 `duplicata`. Táxi de 110,00 sem nota seguido do mesmo táx
           i com nota → o primeiro `nota_fiscal_ausente`, o segundo segue
            avaliado (não é duplicata), em qualquer ordem. "Bistro Centra
           l" e "Bistrô Central" → mesmo fornecedor.
      182  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      178  
      179  **Regra:** duas despesas são duplicatas quando têm a mesma `da
           ta`, a mesma categoria normalizada, o mesmo `fornecedor` norma
           lizado (seção 5) e o mesmo `valor_considerado`. `id`, `descric
           ao` e `tem_nota_fiscal` não entram na comparação. Só participa
           m da comparação despesas que passaram pelas etapas 1 a 6 da se
           ção 8 (inclusive a nota fiscal): uma despesa recusada antes di
           sso não é "original" de ninguém. Dentro de cada grupo de despe
           sas duplicatas entre si, segue avaliada uma só, a **original**
           : a primeira na ordem da entrada que tem `tem_nota_fiscal` ver
           dadeiro; se nenhuma do grupo tem, a primeira na ordem da entra
           da. Todas as outras do grupo são `recusado`, motivo `duplicata
           `, e não consomem limite nem comprovam viagem. Assim, qual cóp
           ia sobrevive não depende da ordem quando só uma delas tem nota
           . A comparação é exata: datas, valores ou fornecedores diferen
           tes após a normalização não são duplicatas (risco aceito, seçã
           o 10).
      180  **Origem:** política do RH, item 8; AMB-010.
      181 -**Aceite:** d-006 e d-007 (mesmos data, categoria, fornecedor 
          -e valor 54,90, ambas com nota) → d-006 avaliada normalmente, d
          --007 `duplicata`. Táxi de 110,00 sem nota seguido do mesmo táx
          -i com nota → o primeiro `nota_fiscal_ausente`, o segundo segue
          - avaliado (não é duplicata), em qualquer ordem. "Bistro Centra
          -l" e "Bistrô Central" → mesmo fornecedor.                     
      181 +**Aceite:** d-006 e d-007 (mesmos data, categoria, fornecedor 
          +e valor 54,90, ambas com nota) → d-006 avaliada normalmente, d
          +-007 `duplicata`. Táxi de 110,00 sem nota seguido do mesmo táx
          +i com nota → o primeiro `nota_fiscal_ausente`, o segundo segue
          + avaliado (não é duplicata), em qualquer ordem. Hospedagem de 
          +90,00 sem nota e a mesma com nota, em qualquer ordem → a com n
          +ota é a original (comprova viagem, RN-010), a sem nota é `dupl
          +icata`. "Bistro Central" e "Bistrô Central" → mesmo fornecedor
          +.                                                             
      182  
      183  ### RN-008 — Nota fiscal obrigatória acima de R$ 100
      184  
⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      253  **Texto original do RH:** "Colaborador em viagem tem limites a
           mpliados em 50%."
      254  **O que não está claro:** a entrada não tem campo de viagem. T
           ambém não está claro se uma hospedagem barata e sem nota basta
            como prova, e se o dia seguinte ao pernoite conta (d-011, caf
           é no hotel em 15/07, depois da diária de 14/07).
      255  **Decisão:** uma hospedagem **com nota fiscal** que não foi re
           cusada antes do limite comprova viagem na data dela e no dia s
           eguinte.
      256 -**Justificativa:** hospedagem é a única evidência objetiva de 
          -viagem nos dados, e só a nota a torna verificável (sem a exigê
          -ncia, uma hospedagem de 0,01 ampliaria o teto do dia em 70,00)
          -; uma diária é uma noite, então o colaborador acorda em viagem
          - no dia seguinte.                                             
      256 +**Justificativa:** hospedagem é a única evidência objetiva de 
          +viagem nos dados, e exigir a nota a torna verificável na confe
          +rência humana; uma diária é uma noite, então o colaborador aco
          +rda em viagem no dia seguinte. A exigência **não** elimina o a
          +buso: o sistema confia no `tem_nota_fiscal` declarado (seção 3
          +), então uma hospedagem irrisória com nota declarada ainda amp
          +lia os limites de D e D+1 (risco aceito, seção 10).           
      257  **Regra afetada:** RN-010
      258  
      259  ### AMB-005 — Uma despesa de hospedagem com várias diárias (D,
            U)

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 2 lines, removed 2 lines
      300  
      301  **Texto original do RH:** "Duplicatas devem ser tratadas."
      302  **O que não está claro:** quais campos definem uma duplicata (
           d-006 e d-007 só diferem no id), o que fazer com ela, e se uma
            despesa relançada com a nota fiscal que faltava é duplicata d
           a original.
      303 -**Decisão:** mesma data, categoria, fornecedor e valor (texto 
          -normalizado, comparação exata); a nota fiscal é verificada ant
          -es, e só despesas que passaram por ela são comparadas; a prime
          -ira na ordem da entrada é avaliada, as demais são recusadas co
          -m motivo `duplicata`.                                         
      304 -**Justificativa:** o id é gerado no lançamento e não identific
          -a o gasto; verificar a nota antes torna o resultado independen
          -te da ordem e permite corrigir uma nota faltante; recusar com 
          -motivo explícito deixa visível um eventual gasto legítimo repe
          -tido, para o colaborador contestar.                           
      303 +**Decisão:** mesma data, categoria, fornecedor e valor (texto 
          +normalizado, comparação exata); a nota fiscal é verificada ant
          +es, e só despesas que passaram por ela são comparadas; a origi
          +nal é a primeira com nota fiscal (ou, se nenhuma tem, a primei
          +ra na ordem da entrada), e as demais são recusadas com motivo 
          +`duplicata`.                                                  
      304 +**Justificativa:** o id é gerado no lançamento e não identific
          +a o gasto; verificar a nota antes e preferir a cópia com nota 
          +tornam o resultado independente da ordem e permitem corrigir u
          +ma nota faltante, inclusive abaixo de 100,00, onde a nota impo
          +rta para comprovar viagem; recusar com motivo explícito deixa 
          +visível um eventual gasto legítimo repetido, para o colaborado
          +r contestar.                                                  
      305  **Regra afetada:** RN-007
      306  
      307  ### AMB-011 — Categoria com grafia diferente (F)

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      308  
      309  **Texto original do RH:** (não tratado)
      310  **O que não está claro:** se `ALIMENTACAO` (d-014) é a mesma c
           ategoria que `alimentacao`; e uma grafia com acento (`alimenta
           ção`).
      311 -**Decisão:** ignora maiúsculas/minúsculas, espaços nas pontas 
          -e acentos/cedilha (normalização da seção 5). A mesma normaliza
          -ção vale para o fornecedor.                                   
      311 +**Decisão:** normalização completa da seção 5: espaços em bran
          +co nas pontas, maiúsculas/minúsculas, qualquer acento ou sinal
          + diacrítico, e separadores internos (espaço, hífen, sublinhado
          +) equivalentes. A mesma normalização vale para o fornecedor.  
      312  **Justificativa:** são variações de escrita da mesma palavra; 
           recusar `alimentação` puniria quem escreve corretamente em por
           tuguês.
      313  **Regra afetada:** RN-006, RN-007
      314  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      309  **Texto original do RH:** (não tratado)
      310  **O que não está claro:** se `ALIMENTACAO` (d-014) é a mesma c
           ategoria que `alimentacao`; e uma grafia com acento (`alimenta
           ção`).
      311  **Decisão:** normalização completa da seção 5: espaços em bran
           co nas pontas, maiúsculas/minúsculas, qualquer acento ou sinal
            diacrítico, e separadores internos (espaço, hífen, sublinhado
           ) equivalentes. A mesma normalização vale para o fornecedor.
      312 -**Justificativa:** são variações de escrita da mesma palavra; 
          -recusar `alimentação` puniria quem escreve corretamente em por
          -tuguês.                                                       
      312 +**Justificativa:** são variações de escrita da mesma palavra; 
          +recusar `alimentação` puniria quem escreve corretamente em por
          +tuguês, e recusar `Transporte Urbano` recusaria a grafia que o
          + próprio RH usou na política.                                 
      313  **Regra afetada:** RN-006, RN-007
      314  
      315  ### AMB-012 — Categoria fora da política: recusar ou omitir? (
           U)

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      332  
      333  **Texto original do RH:** (não tratado)
      334  **O que não está claro:** d-011 tem 33,333: arredondar, trunca
           r ou recusar, e quando.
      335 -**Decisão:** arredonda para o centavo, metade para cima, antes
          - de qualquer regra. A saída mostra o número recebido (`valor_i
          -nformado`) e o arredondado (`valor_considerado`).             
      335 +**Decisão:** arredonda para o centavo, metade afastando do zer
          +o, antes de qualquer regra. A saída mostra o número recebido (
          +`valor_informado`) e o arredondado (`valor_considerado`).     
      336  **Justificativa:** reembolso é pago em centavos; arredondar no
            início garante que todas as regras usem o mesmo valor.
      337  **Regra afetada:** RN-003
      338  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 2 lines
      377  | Despesa antiga lançada no período | d-008, data 15/04 num pe
           ríodo de julho | `fora_do_periodo` | RN-005 |
      378  | Categoria em maiúsculas | `ALIMENTACAO` | tratada como `alim
           entacao` | RN-006 |
      379  | Categoria com acento | `alimentação` | tratada como `aliment
           acao` | RN-006 |
      380 +| Categoria com separador diferente | `"Transporte Urbano"`, `
          +"transporte-urbano"` | tratada como `transporte_urbano` | RN-0
          +06 |                                                          
      381 +| Categoria com tabulação no fim | `"alimentacao\t"` | tratada
          + como `alimentacao` | RN-006 |                                
      382  | Duplicata exata | mesmos data, categoria, fornecedor, valor 
           (≤ 100) | segunda `duplicata` | RN-007 |
      383  | Fornecedor com acento | "Bistro Central" e "Bistrô Central",
            demais campos iguais | segunda `duplicata` | RN-007 |
      384  | Quase duplicata | mesmo valor, data vizinha ou fornecedor di
           ferente | as duas avaliadas | RN-007 |

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 2 lines
      381  | Categoria com tabulação no fim | `"alimentacao\t"` | tratada
            como `alimentacao` | RN-006 |
      382  | Duplicata exata | mesmos data, categoria, fornecedor, valor 
           (≤ 100) | segunda `duplicata` | RN-007 |
      383  | Fornecedor com acento | "Bistro Central" e "Bistrô Central",
            demais campos iguais | segunda `duplicata` | RN-007 |
      384 +| Fornecedor com espaços internos | "Pão  Quente" e "Pao Quent
          +e", demais campos iguais | segunda `duplicata` | RN-007 |     
      385 +| Duplicata de hospedagem só uma com nota | hospedagem 90,00 s
          +em nota e a mesma com nota, mesma data, em qualquer ordem | a 
          +com nota é a original e comprova viagem; a sem nota é `duplica
          +ta` | RN-007, RN-010 |                                        
      386  | Quase duplicata | mesmo valor, data vizinha ou fornecedor di
           ferente | as duas avaliadas | RN-007 |
      387  | Cópias idênticas sem nota acima de 100 | duas despesas de 15
           0,00 sem nota | as duas `nota_fiscal_ausente` | RN-008, RN-007
            |
      388  | Relançamento com nota | 110,00 sem nota e depois o mesmo com
            nota (ou ordem inversa) | sem nota `nota_fiscal_ausente`; com
            nota segue avaliada | RN-007, RN-008 |

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line
      390  | Valor zero | 0,00 | `valor_invalido` | RN-004 |
      391  | Três casas decimais | 33,333 | `valor_informado` 33.333, `va
           lor_considerado` 33,33 | RN-003 |
      392  | Arredondamento da metade | 10,005 | considerado 10,01 | RN-0
           03 |
      393 +| Arredondamento da metade negativa | -0,005 | considerado -0,
          +01; `valor_invalido` | RN-003, RN-004 |                       
      394  | Hospedagem com várias diárias na descrição | 480,00 "2 diari
           as", com nota, em 14/07 | 1 diária: `parcial` com 250,00; 14/0
           7 e 15/07 em viagem | RN-012, RN-010 |
      395  | Dia seguinte à diária | hospedagem com nota em 14/07; alimen
           tação 80,00 em 15/07 | 15/07 em viagem: limite 90,00, `aprovad
           o` com 80,00 | RN-010 |
      396  | Dois dias depois da diária | hospedagem com nota em 14/07; a
           limentação 80,00 em 16/07 | limite 60,00, `parcial` com 60,00 
           | RN-010 |

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 4 lines
      402  | Campo obrigatório ausente | despesa sem `tem_nota_fiscal` | 
           `entrada_invalida`, `valor_considerado` nulo, fora dos totais;
            demais processadas | RN-002 |
      403  | Elemento que não é objeto | `null` dentro de `despesas` | it
           em com `id` e `data` nulos, `entrada_invalida` | RN-002 |
      404  | Campo extra | hospedagem com `"noites": 2` | campo ignorado;
            uma diária | RN-002, RN-012 |
      405 +| Campo com tipo errado | `"id": 17` | `entrada_invalida`; `id
          +` nulo na saída | RN-002 |                                    
      406 +| Texto vazio em campo obrigatório | `fornecedor` `""` ou `"  
          + "` | `entrada_invalida` | RN-002 |                           
      407 +| Competência não textual | `competencia` 202607 | processamen
          +to normal; `competencia` nula na saída | RN-002 |             
      408 +| Saída não gravável | caminho de saída em pasta inexistente |
          + erro de arquivo: código diferente de 0 | RN-002 |            
      409  | Colaborador ausente | arquivo sem `colaborador` | erro de ar
           quivo: sem saída, código diferente de 0 | RN-002 |
      410  | Lista de despesas vazia | `despesas: []` | `itens` vazio, to
           tais 0 | RN-001 |
      411  | Despesa em sábado | 18/07 (sábado) | avaliada normalmente | 
           AMB-015 |

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line, removed 1 line
      420  4. **Período** — RN-005 (`fora_do_periodo`).
      421  5. **Categoria** — RN-006 (`categoria_fora_da_politica`).
      422  6. **Nota fiscal** — RN-008 (`nota_fiscal_ausente`).
      423 -7. **Duplicata** — RN-007 (`duplicata`), comparando só com des
          -pesas anteriores que passaram pelas etapas 1 a 6.             
      423 +7. **Duplicata** — RN-007 (`duplicata`), comparando só despesa
          +s que passaram pelas etapas 1 a 6; em cada grupo de duplicatas
          +, a original é a primeira com nota fiscal (ou a primeira na or
          +dem, se nenhuma tem).                                         
      424  8. **Viagem** — RN-010: com todas as despesas já avaliadas pel
           as etapas 1 a 7, marca as datas em viagem.
      425  9. **Limite diário** — RN-009, por data e categoria, consumind
           o o limite na ordem da entrada.
      426  

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 2 lines, removed 1 line
      471  ### Riscos conhecidos e aceitos
      472  
      473  - **Fracionamento para escapar da nota fiscal** (AMB-008): trê
           s hospedagens sem nota de 100,00 + 99,99 + 50,01 na mesma data
            recebem 250,00, enquanto uma de 250,00 sem nota recebe 0. O g
           anho é limitado aos casos em que o limite diário passa de 100,
           00 (hospedagem e transporte em viagem). Aceito para não recusa
           r despesas pequenas legítimas sem nota.
      474 -- **Quase-duplicatas** (AMB-010): o mesmo gasto relançado com 
          -data vizinha, valor diferente em um centavo ou fornecedor com 
          -outra grafia (além de caixa, acentos e espaços nas pontas) não
          - é detectado. Aceito porque qualquer critério aproximado seria
          - regra inventada e poderia recusar gastos legítimos repetidos.
      474 +- **Viagem por hospedagem irrisória com nota declarada** (AMB-
          +004): uma hospedagem de 0,01 com `tem_nota_fiscal` verdadeiro 
          +põe D e D+1 em viagem e amplia os limites de alimentação e tra
          +nsporte em até 70,00 por dia (140,00 nos dois dias). Aceito po
          +rque o sistema não verifica notas (seção 3) e qualquer valor m
          +ínimo seria regra inventada; a saída expõe `em_viagem` por ite
          +m para a conferência humana. Mitigação definitiva: indicação e
          +xplícita de viagem na entrada (evolução, seção 3).            
      475 +- **Quase-duplicatas** (AMB-010): o mesmo gasto relançado com 
          +data vizinha, valor diferente em um centavo ou fornecedor com 
          +outra grafia (além do que a normalização da seção 5 cobre) não
          + é detectado. Aceito porque qualquer critério aproximado seria
          + regra inventada e poderia recusar gastos legítimos repetidos.

⏺ Agora a entrada D-002 no DECISIONS.md.

⏺ Update(specs/001-motor-reembolso/DECISIONS.md)
  ⎿  Added 28 lines
      10  
      11  ---
      12  
      13 +## D-002 — Segunda revisão adversarial: spec 1.1 → 1.2 · `2026-
         +10-01`                                                         
      14 +                                                               
      15 +**Gatilho:** nova rodada do `spec-adversary` sobre a 1.1 (commi
         +t `d35f68d`), focada no que a D-001 mudou: 6 problemas, 1 bloqu
         +eante. Decididos um a um pelo responsável (sessão `docs/session
         +s/05-*`).                                                      
      16 +                                                               
      17 +**O que mudou na spec:**                                       
      18 +                                                               
      19 +| # | Ponto | De (1.1) | Para (1.2) | Onde |                   
      20 +|---|---|---|---|---|                                          
      21 +| 1 | Duplicata de hospedagem ≤ 100,00 em que só uma cópia tem 
         +nota (**bloqueante**) | sobrevivia a primeira na ordem; com a c
         +ópia sem nota primeiro, a viagem sumia — contradizia a justific
         +ativa da D-001 (4a) de independência da ordem | a original é a 
         +**primeira com nota fiscal**; se nenhuma tem, a primeira na ord
         +em | RN-007, seção 8 (etapa 7), AMB-010 |                      
      22 +| 2 | Hospedagem irrisória com nota declarada | AMB-004 afirmav
         +a que exigir nota fechava a brecha — **erro de justificativa da
         + 1.1** (a nota é só declarada) | regra mantida; justificativa c
         +orrigida; registrado como risco aceito; indicação explícita de 
         +viagem na entrada registrada como evolução (o formato fixo não 
         +permite) | AMB-004, seção 3, seção 10 |                        
      23 +| 3 | Normalização de texto | só espaço comum nas pontas e 3 ex
         +emplos de acento; separadores internos preservados (`Transporte
         + Urbano`, como o RH escreveu, era recusada) | regra completa em
         + 4 passos: espaços em branco de qualquer tipo nas pontas, caixa
         +, qualquer diacrítico (independentemente da codificação), espaç
         +o/hífen/sublinhado internos = um `_` | seção 5, RN-006, AMB-011
         + |                                                             
      24 +| 4a | Campo com tipo errado (`"id": 17`) | "como veio" × "text
         +o ou nulo" | `entrada_invalida`; campo sai nulo se não for text
         +o | RN-002, seção 4 |                                          
      25 +| 4b | `competencia` não textual | indefinido | copiada se for 
         +texto; nula caso contrário; nunca é erro | RN-002, seção 4 |   
      26 +| 4c | Arredondamento da metade negativa | "metade para cima" |
         + "metade afastando do zero" (-0,005 → -0,01); positivos inalter
         +ados | RN-003, AMB-014 |                                       
      27 +| 4d | Falha ao gravar a saída | não listada | erro de arquivo 
         +| RN-002, seção 4 (Interface) |                                
      28 +| 5 | Texto vazio em `id`/`categoria`/`fornecedor` | aceito com
         +o texto | `entrada_invalida` | RN-002 |                        
      29 +| 6 | D-001 sem o ponto 12 | tabela pulava do 11 ao 13 — **erro
         + de registro** | linha 12 incluída na D-001 antes do commit da 
         +1.1 | `DECISIONS.md` |                                         
      30 +                                                               
      31 +**Por quê:** o ponto 1 obrigaria o código a escolher entre a re
         +gra literal e a justificativa; os pontos 3, 4 e 5 deixavam saíd
         +as indefinidas ou não determinísticas; os pontos 2 e 6 eram err
         +os de redação/registro da revisão anterior.                    
      32 +                                                               
      33 +**O que isso invalidou:** nenhum código ou teste (ainda não exi
         +stem). Nenhum valor do resultado esperado do exemplo mudou (seç
         +ão 9). Casos de borda novos: 10 linhas na seção 7.             
      34 +                                                               
      35 +**Tasks afetadas:** nenhuma (o `tasks.md` ainda não foi escrito
         +).                                                             
      36 +                                                               
      37 +**Custo:** 2 arquivos (`spec.md`, `DECISIONS.md`); 6 pontos dec
         +ididos na mesma sessão.                                        
      38 +                                                               
      39 +---                                                            
      40 +                                                               
      41  ## D-001 — Revisão adversarial e análise dos dados: spec 1.0 → 
          1.1 · `2026-10-01`
      42  
      43  **Gatilho:** revisão da spec 1.0 (commit `c8bcad9`) antes do pl
          ano, em duas frentes: o subagente `spec-adversary` (9 problemas
          , 2 bloqueantes) e uma nova análise item a item de `exemplos/de
          spesas-exemplo.json`. Os 13 pontos resultantes foram decididos 
          um a um pelo responsável (sessão `docs/sessions/05-*`).

  Ran 1 shell command (ctrl+o to expand)

⏺ A v1.2 está aplicada e ainda não tem commit.

  Mudanças na spec.md (v1.1 → v1.2):

  ┌────────────────────────────┬────────────────────────────────────────────┐
  │           Ponto            │                    Onde                    │
  ├────────────────────────────┼────────────────────────────────────────────┤
  │ 1. Entre duplicatas, vale  │ RN-007, seção 8 (etapa 7), AMB-010 e um    │
  │ a primeira com nota fiscal │ caso de borda novo com a hospedagem de     │
  │                            │ 90,00                                      │
  ├────────────────────────────┼────────────────────────────────────────────┤
  │ 2. Hospedagem irrisória    │ AMB-004 com a justificativa corrigida;     │
  │ como risco aceito          │ seção 10 "Riscos aceitos"; seção 3 com a   │
  │                            │ flag em_viagem como evolução               │
  ├────────────────────────────┼────────────────────────────────────────────┤
  │                            │ seção 5, agora em 4 passos com exemplos    │
  │ 3. Normalização completa   │ (Transporte Urbano → transporte_urbano);   │
  │                            │ RN-006 e AMB-011                           │
  ├────────────────────────────┼────────────────────────────────────────────┤
  │ 4a a 4d. Tipo errado,      │                                            │
  │ competencia, metade        │ RN-002, RN-003, seção 4 (Interface e       │
  │ negativa, saída não        │ Saída), AMB-014                            │
  │ gravável                   │                                            │
  ├────────────────────────────┼────────────────────────────────────────────┤
  │ 5. Texto vazio é inválido  │ RN-002                                     │
  ├────────────────────────────┼────────────────────────────────────────────┤
  │ 6. Ponto 12 na D-001       │ já entrou no commit da v1.1 (d35f68d)      │
  └────────────────────────────┴────────────────────────────────────────────┘

  São 10 casos de borda novos na seção 7. O resultado do exemplo não mudou
  (1.861,84 / 585,43 / 1.276,41).

  No DECISIONS.md, a entrada D-002 tem a tabela "de → para" com os 6 pontos e
  marca explicitamente os dois erros meus: a justificativa da AMB-004 e o ponto
  12 que faltava. Junto com o erro da seção 9 da primeira rodada, são três casos
  concretos para a seção de Discernimento do relatório.

  Proposta de próximos passos:
  1. Commit docs(spec): v1.2 aplica segunda revisão adversarial (D-002).
  2. Não rodar uma terceira rodada agora. A segunda já trouxe achados menores, a
     maioria detalhes de contrato, e o FAQ recomenda fechar a spec perto do
     meio-dia ("paralisia de especificação também custa nota"). O que surgir
     depois entra pelo DECISIONS.md.
  3. Exportar a sessão, já que o lembrete apareceu duas vezes: /export 
     docs/sessions/_completo.md, e eu corto o 05 a partir do fim do 04.
  4. Depois, o plan.md.

  Posso fazer o commit da v1.2?

✻ Cooked for 1m 52s · done 9:49 PM

❯ sim, faz o commit da v1.2                                                     

  Pushed to main (ctrl+o to expand)
  ⎿  PostToolUse:Bash says: 📝 Fim do bloco de trabalho ("docs(spec): v1.2 
     aplica segunda revisão adversarial (D-002)"). Exporte a sessão antes de 
     continuar:
        /export docs/sessions/05-<descricao-curta>.md
        e commite com: docs(sessions): export da sessão 05

⏺ Fiz o commit da v1.2 (bdb1eec) e o push. A pasta de trabalho está limpa. O
  histórico da spec no GitHub mostra a evolução:

  bdb1eec  docs(spec): v1.2 aplica segunda revisão adversarial (D-002)
  d35f68d  docs(spec): v1.1 aplica decisões da revisão adversarial (D-001)
  c8bcad9  docs(spec): primeira versão com 16 ambiguidades resolvidas

  A spec está fechada para o planejamento. Este é um fim de bloco, então antes
  do plan.md, exporte a sessão:

  /export docs/sessions/_completo.md

  Eu corto o 05 a partir do ponto em que o 04 termina. Ele vai cobrir a
  avaliação do que foi criado, a escrita da spec, as duas rodadas do
  spec-adversary e os 18 pontos que você decidiu. Depois faço o commit
  docs(sessions): export da sessão 05.

✻ Cooked for 10s · done 9:50 PM