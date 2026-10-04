 ▐▛███▛█   Claude Code v2.1.287
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~/repo/sdd-desafio

  Get to finished work sooner with Opus 5.5. Switch anytime with /model.

❯ /clear                                                                        

❯ roda o spec-adversary na spec final                                           

⏺ spec-adversary(Revisão adversarial da spec final)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ Comecei a revisão do spec-adversary na spec final
  (specs/001-motor-reembolso/spec.md). Ela também lê o DECISIONS.md, o plan.md e
  os exemplos do envelope, e deixa de fora o que já foi decidido. Ela ainda
  está rodando. Quando terminar, trago os problemas numerados com a severidade e
  as perguntas. As decisões ficam com você.

✻ Cogitated for 6s · done 4:03 PM

› Message from spec-adversary
  Resumo: 7 problemas encontrados, nenhum BLOQUEANTE (3 IMPORTANTES, 4 MENORES).
  Para todos os cenários abaixo, a spec 2.0 tem leitura literal, ou a lacuna
  atinge só casos raros. O que falta é decidir se o resultado literal é o
  desejado e registrar isso na spec.

  Arquivos lidos:
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md`,
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md`
  (D-001 a D-007, inclusive as rodadas R2 e R3),
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/plan.md` (seções
  4 e 5), os arquivos de `/Users/rafaeltxm/repo/sdd-desafio/exemplos/envelope/`
  e a política v3 em `/Users/rafaeltxm/repo/sdd-desafio/DESAFIO.md`. Conferi à
  mão os totais do `despesas-envelope.json` (2.457,52 / 1.148,26 / 1.309,26) e
  eles batem com a seção 9. Não li `src/` nem `tests/`.

  ---

  ### 1. O mesmo gasto lançado em duas categorias não é duplicata, e um gasto
  pode ser dividido entre categorias — IMPORTANTE — brecha

  - **Regra afetada:** RN-007, AMB-010, AMB-017, AMB-028; seção 10 (risco
  "Quase-duplicatas").
  - **Cenário de entrada:** `centro_custo` `CC-COMERCIAL`, período de julho,
  tudo em BRL, 03/07 fora de viagem.
    - (a) d-1: `alimentacao`, "Casa Trindade", 85,00, `tem_nota_fiscal` true.
  d-2: `representacao`, "Casa Trindade", 85,00, `tem_nota_fiscal` true.
    - (b) Um jantar real de 390,00 lançado como d-1 `alimentacao` 90,00 mais d-2
  `representacao` 300,00, mesmo fornecedor, os dois com nota.
    - (c) Com a tabela `padrao`: `transporte_urbano` "Bolt" 50,00 e
  `alimentacao` "Bolt" 50,00 no mesmo dia.
  - **Comportamento pela interpretação atual:** a categoria normalizada faz
  parte da chave da duplicata, então nenhum desses pares é duplicata.
    - (a) As duas são aprovadas com 85,00 cada: 170,00 por um gasto de 85,00.
    - (b) As duas são aprovadas: 390,00. Lançado inteiro numa categoria só, o
  gasto renderia 300,00 (`representacao`) ou 90,00 (`alimentacao`).
    - (c) As duas são aprovadas: 100,00.
  - **Por que é uma brecha:** um lançamento repetido, com data, fornecedor,
  valor e moeda idênticos, escapa da RN-007 só por trocar a categoria. A AMB-017
  convida a lançar refeição como `representacao`, o que torna a troca plausível
  no `CC-COMERCIAL`. O risco aceito de quase-duplicatas (seção 10) cita data
  vizinha, centavo e grafia do fornecedor, mas não a categoria. A seção 3 não
  lista a categoria como campo autodeclarado aceito, como faz com o centro de
  custo, a moeda e a nota fiscal.
  - **Pergunta para decisão:** um gasto com mesmos data, fornecedor, moeda e
  valor, lançado em categorias diferentes, é duplicata ou não? E dividir um
  mesmo gasto entre duas categorias do mesmo dia é um risco aceito, que deve ser
  registrado na seção 10?

  ### 2. A janela de D-3 não cobre a terça de Carnaval: despesa legítima em
  moeda estrangeira sem cotação — IMPORTANTE — lacuna/ambiguidade

  - **Regra afetada:** RN-015, AMB-024; seção 10 (risco "Cotação de até 3 dias
  antes").
  - **Cenário de entrada:** câmbio com `"2027-02-05": {"EUR": 6.00}` (sexta) e
  `"2027-02-10": {"EUR": 6.05}` (quarta de Cinzas); segunda 08/02 e terça 09/02
  sem PTAX. Período de 2027-02-01 a 2027-02-28, tabela `padrao`.
    - d-1: `alimentacao` 10,00 EUR com nota em 2027-02-09.
    - d-2: a mesma despesa em 2027-02-08.
  - **Comportamento pela interpretação atual:**
    - d-1: D-1 a D-3 (08, 07 e 06/02) não têm EUR, então o item é
  `cambio_indisponivel`, recusado e fica fora de `valor_solicitado`.
    - d-2: a busca chega a 05/02 (D-3), 60,00, `aprovado` com 60,00.
  - **Por que é um problema:** a AMB-024 justifica os 3 dias por cobrirem "fim
  de semana e feriado de segunda ou sexta adjacente". Dois feriados seguidos
  colados ao fim de semana são recorrentes (Carnaval) e caem fora da janela. O
  risco da seção 10 descreve só "lacuna do arquivo" em dia útil, não o
  calendário bancário. Uma despesa real, com nota e dentro do período, é
  recusada por inteiro, sem caminho de reembolso.
  - **Pergunta para decisão:** a recusa por `cambio_indisponivel` em datas cujo
  último dia útil cai antes de D-3 (como a terça de Carnaval) é um risco aceito
  que deve ser registrado? Ou a janela da AMB-024 precisa ser revista?

  ### 3. `descricao` com tipo diferente de texto (inclusive `null`) não tem
  resultado definido — IMPORTANTE — ambiguidade

  - **Regra afetada:** seção 4 (tabela de entrada: `descricao`, tipo "texto",
  não obrigatória), RN-002 (lista de "Despesa inválida").
  - **Cenário de entrada:** `alimentacao` 45,00 BRL em 03/07, `tem_nota_fiscal`
  false, `"descricao": null` (ou `17`, ou `{}`).
  - **Comportamento pela interpretação atual:** indefinido.
    - Pela lista da RN-002, que não cita `descricao`, a despesa é válida e sai
  `aprovado` com 45,00.
    - Pela coluna de tipo da seção 4, que declara "texto", ela pode ser lida
  como `entrada_invalida`, com 0,00 e fora dos totais.
  - **Por que é um problema:** para os outros campos opcionais (`moeda`,
  `centro_custo`, `competencia`), a spec diz explicitamente o que acontece com
  `null` e com outro tipo; para `descricao`, não diz. `"descricao": null` é
  comum em arquivos exportados por sistemas, e a escolha muda aprovado/recusado.
  - **Pergunta para decisão:** `descricao` ausente, nula ou de outro tipo torna
  a despesa inválida, ou o campo é aceito com qualquer tipo, já que nunca é
  lido?

  ### 4. A fórmula de status da RN-011 conflita com a RN-004 quando
  `valor_considerado` é 0,00 — MENOR — contradição

  - **Regra afetada:** RN-011, RN-004, seção 4 (tabela de motivos).
  - **Cenário de entrada:** `alimentacao`, `valor` 0.004 BRL (ou 0), em 03/07.
  - **Comportamento pela interpretação atual:** `valor_considerado` é 0,00 e
  `valor_reembolsado` é 0.
    - Pela RN-011, valem ao mesmo tempo "aprovado quando reembolsado =
  considerado" (0 = 0) e "recusado quando reembolsado = 0".
    - A tabela de motivos e a RN-004 dizem `recusado`/`valor_invalido`.
    - Um item `aprovado` teria motivo nulo, o que também conflita com o motivo
  `valor_invalido`.
  - **Por que é um problema:** o texto da RN-011 aceita duas classificações para
  o mesmo item. Hoje, só a tabela de motivos resolve o conflito, e a fórmula da
  RN-011 é exatamente o que o aceite dela manda verificar ("nenhum item com
  status incompatível com os seus valores").
  - **Pergunta para decisão:** a fórmula da RN-011 vale só para os itens que
  chegam ao limite diário (etapa 9)? Ou qual das duas cláusulas prevalece quando
  `valor_considerado` é 0?

  ### 5. "Data válida `AAAA-MM-DD`": quais dígitos e qual intervalo do
  calendário — MENOR — lacuna

  - **Regra afetada:** RN-002 (`data`, `periodo.inicio`/`fim`), RN-016
  (`vigencia`, chaves de `taxas`), RN-010 (D+1), RN-015 (D-3).
  - **Cenário de entrada:**
    - (a) `"data": "٢٠٢٦-٠٧-٠٣"` (algarismos arábico-índicos, que a seção 5
  trata como "dígito decimal").
    - (b) `"data": "0000-01-01"`.
    - (c) período de 9999-12-01 a 9999-12-31, com hospedagem com nota em
  9999-12-31: D+1 não existe no calendário.
  - **Comportamento pela interpretação atual:** indefinido.
    - (a) e (b) podem ser `entrada_invalida` ou datas válidas.
    - (c) não diz se a marcação de viagem simplesmente ignora o D+1 ou se o caso
  é outra coisa.
    - Nos três, o plano escolhe um comportamento (dígitos ASCII, corte no
  calendário), mas a spec não.
  - **Por que é um problema:** a spec é minuciosa sobre dígitos Unicode na
  normalização e sobre a forma de `moeda` (A a Z), mas nunca fecha o conjunto de
  dígitos nem o intervalo de datas aceitas. O efeito prático é pequeno.
  - **Pergunta para decisão:** a data exige dígitos ASCII e algum intervalo de
  anos? E o que acontece com D+1 e D-3 quando eles saem do calendário?

  ### 6. Argumentos de linha de comando repetidos ou desconhecidos — MENOR —
  lacuna

  - **Regra afetada:** seção 4 (Interface, erro de uso), AMB-031.
  - **Cenário de entrada:**
    - `calcular --input e.json --politica politica-v4.json --politica
  outra-v4.json --cambio c.json --output s.json`, sendo que as duas políticas
  têm `"versao": "v4"` e limites diferentes.
    - Variante: um argumento desconhecido (`--verbose`) ou um argumento
  posicional sobrando.
  - **Comportamento pela interpretação atual:** indefinido. A seção 4 só define
  como erro de uso o subcomando errado e a falta de argumentos. Com a política
  repetida, o resultado depende de qual ocorrência vale, e a saída só registra
  `versao`/`vigencia`, não o caminho. Então resultados diferentes saem com a
  mesma identificação.
  - **Por que é um problema:** a AMB-031 justifica os argumentos obrigatórios
  com "tudo o que entra no cálculo aparece na linha de comando, e a mesma linha
  de comando dá sempre o mesmo resultado". Uma linha com duas políticas mostra
  as duas e usa uma, sem dizer qual.
  - **Pergunta para decisão:** argumento repetido, desconhecido ou sobrando é
  erro de uso? Se não for, qual ocorrência vale?

  ### 7. Hospedagem de várias noites num lançamento só põe em viagem apenas D e
  D+1 — MENOR — lacuna de registro

  - **Regra afetada:** RN-010, RN-012, AMB-005; seção 10 ("Datas de entrada e
  saída de hospedagem").
  - **Cenário de entrada:** tabela `padrao`.
    - Hospedagem de 750,00 com nota em 14/07, descrição "3 noites".
    - `alimentacao` de 80,00 com nota em 16/07.
  - **Comportamento pela interpretação atual:** só 14/07 e 15/07 ficam em
  viagem. A alimentação de 16/07 tem limite de 60,00 e sai `parcial` com 60,00;
  se 16/07 estivesse em viagem, sairia `aprovado` com 80,00. No envelope, a
  e-007 ("Hotel Londres - 3 noites", 22/07) deixa 24/07 fora de viagem.
  - **Por que é um problema:** o resultado literal está definido, mas a decisão
  provisória da seção 10 registra só a consequência no valor da hospedagem
  (250,00 de 480,00), não a perda da ampliação nos dias seguintes da mesma
  estadia. O conferente não tem esse efeito documentado.
  - **Pergunta para decisão:** a perda da ampliação em viagem a partir de D+2,
  numa estadia lançada como um único lançamento, é uma consequência aceita que
  deve ser registrada junto à decisão provisória da AMB-005?

  ---

  **1. Decidir antes da implementação:** nenhum (nenhum achado é BLOQUEANTE; a
  implementação até a T-034 já está concluída).

  **2. Pode ser decidido depois:** 1, 2, 3 (IMPORTANTES; o 1 e o 3 mudam
  aprovado/recusado ou valores em cenários plausíveis, então vale decidir
  primeiro), 4, 5, 6, 7 (MENORES).

⏺ A revisão do spec-adversary na spec 2.0 achou 7 problemas, nenhum bloqueante:
  3 importantes e 4 menores. A spec tem leitura literal para todos os cenários,
  então falta decidir se esse resultado é o desejado e registrar na spec. Ele
  não leu src/ nem tests/. Os totais do envelope na seção 9 batem com os
  cálculos à mão dele (2.457,52 / 1.148,26 / 1.309,26).

  Importantes

  1. Mesmo gasto lançado em categorias diferentes não conta como duplicata 
  (RN-007, AMB-017/028)
  A categoria faz parte da chave da duplicata. Exemplo: "Casa Trindade" 85,00 em
  alimentacao e de novo em representacao no mesmo dia: as duas despesas são
  aprovadas e o reembolso dá 170,00. Também dá para dividir um jantar de 390,00
  entre as duas categorias e receber tudo. Lançado numa categoria só, ele
  renderia 300,00 ou 90,00.
  - Decisão: o mesmo gasto (data, fornecedor, moeda e valor iguais) em
    categorias diferentes é duplicata? Dividir um gasto entre categorias entra
    como risco aceito na seção 10?

  2. A janela de D-3 não cobre a terça de Carnaval (RN-015, AMB-024)
  Despesa em EUR na terça 09/02/2027: D-1 a D-3 caem em segunda de Carnaval,
  domingo e sábado, nenhum com cotação. O item é recusado por
  cambio_indisponivel, sem nenhum caminho para ser reembolsado.
  - Decisão: isso fica como risco aceito registrado, ou a janela da AMB-024
    precisa mudar?

  3. descricao com valor null ou tipo diferente de texto (seção 4, RN-002)
  A RN-002 não cita o campo, então a despesa seria válida. Mas a coluna de tipo
  da seção 4 diz "texto", o que abre a leitura de entrada_invalida. null é comum
  em arquivo exportado por sistema.
  - Decisão: a despesa vira inválida, ou aceitamos qualquer tipo, já que o motor
    nunca lê esse campo?

  Menores

  4. A fórmula de status da RN-011 conflita com a RN-004 quando 
  valor_considerado é 0,00. Com reembolsado = considerado = 0, a fórmula aceita
  tanto aprovado quanto recusado. Hoje, só a tabela de motivos resolve.
  - Decisão: a fórmula vale só a partir da etapa 9, ou qual cláusula prevalece?

  5. Formato da data. A spec não diz se aceita dígitos fora do ASCII (como
  ٢٠٢٦-...), datas como 0000-01-01, nem o que fazer quando D+1 ou D-3 sai do
  calendário (9999-12-31). O plan já escolhe um comportamento, mas a spec não
  fixa nenhum.

  6. Argumento de linha de comando repetido, desconhecido ou sobrando. Exemplo:
  --politica passado duas vezes. A saída registra só versao/vigencia, então dois
  resultados diferentes sairiam com a mesma identificação, o que vai contra a
  AMB-031.
  - Decisão: isso é erro de uso?

  7. Hospedagem de várias noites num lançamento só (AMB-005). Só D e D+1 ficam
  em viagem. A partir de D+2, a alimentação usa o limite normal. A e-007 do
  envelope tem esse efeito em 24/07, e a decisão provisória na seção 10 não
  registra isso.

  Próximo passo

  Pela regra do projeto, cada decisão vai para a spec e ganha entrada no
  DECISIONS.md antes de mexer no código. Eu decidiria primeiro o 1 e o 3, porque
  mudam aprovado/recusado em casos plausíveis. Me diga a decisão de cada item e
  eu escrevo as mudanças.

✻ Sautéed for 13s · done 4:09 PM

⏺ Agent "Revisão adversarial da spec final" finished · 5m 26s

※ recap: Rodei a revisão adversarial da spec final: 7 problemas, nenhum bloqueante, 3 importantes. Falta você decidir cada um, começando pelo 1 (duplicata entre categorias) e pelo 3 (`descricao` nula), para eu registrar na spec e no `DECISIONS.md`. (disable recaps in /config)

❯ vamos decidir um a um, me passa cada caso                                     

  Searched for 1 pattern, listed 1 directory, ran 1 shell command (ctrl+o to expand)

⏺ Começando pelo caso 1 de 7.

  Caso 1 — Mesmo gasto lançado em categorias diferentes

  Hoje (RN-007): a chave da duplicata é data + categoria + fornecedor + moeda +
  valor na moeda da despesa. A política do RH só diz "Duplicatas devem ser
  tratadas" (item 8), então a inclusão da categoria na chave foi uma escolha
  nossa na AMB-010.

  O agente apontou duas brechas diferentes:

  - (a) Repetição com a categoria trocada: "Casa Trindade" 85,00 em alimentacao
    e de novo em representacao no mesmo dia. As duas são pagas, total 170,00.
  - (b) Divisão de um gasto: um jantar de 390,00 lançado como 90,00 em
    alimentacao mais 300,00 em representacao. As duas são pagas, total 390,00.
    Lançado numa categoria só, renderia 300,00 ou 90,00.

  Detalhes que pesam:
  - Tirar a categoria da chave resolve só a (a). Na (b) os valores são
    diferentes, então nenhuma regra exata de duplicata pega. Pegar a (b)
    exigiria uma regra nova de soma por fornecedor e dia, ou seja, uma regra
    inventada.
  - Tirar a categoria também passaria a recusar gastos legítimos que coincidem,
    como Bolt corrida 50,00 e Bolt Food 50,00 no mesmo dia. Hoje esses dois não
    são duplicata.
  - Conferi os dois arquivos de despesas do envelope: não há nenhum par com
    mesma data, fornecedor, valor e moeda em categorias diferentes. As duas
    opções dão o mesmo resultado na seção 9.

  Minha recomendação: manter a regra como está e registrar (a) e (b) como risco
  aceito na seção 10, com uma linha no DECISIONS.md. A justificativa é a mesma
  das quase-duplicatas: a política não define o critério, e o critério
  alternativo recusaria gastos legítimos. Nesse caminho, não muda código.

  Se você preferir tirar a categoria da chave, isso mexe na RN-007, na AMB-010 e
  nos testes. Precisa de uma task nova em tasks.md e de outra rodada do
  spec-adversary.

  Qual das duas?

✻ Brewed for 31m 28s · done 4:34 PM

❯ mantém e registra como risco aceito, próximo caso                             

  Ran 1 shell command (ctrl+o to expand)

⏺ Update(specs/001-motor-reembolso/spec.md)
  ⎿  Added 1 line
      819  - **Centro de custo autodeclarado** (AMB-020): o `centro_custo
           ` vem da mesma entrada que o colaborador produz; declarar `CC-
           COMERCIAL` dá alimentação 90,00, transporte 150,00 e hospedage
           m 400,00, e escrever `"cc-adm"` em vez de `CC-ADM` troca a tab
           ela pelo `padrao` (mais generosa para o `CC-ADM`). Aceito pelo
            mesmo motivo do `tem_nota_fiscal`: o sistema não tem cadastro
            para conferir (seção 3); a saída expõe `colaborador.centro_cu
           sto` e `politica.tabela_aplicada` para a conferência humana.
      820  - **Viagem internacional sem hospedagem lançada** (AMB-023): q
           uem está no exterior sem hospedagem na entrada (hotel pago pel
           a empresa por outro meio, por exemplo) não tem os limites ampl
           iados; no envelope, o almoço de Lisboa e-002 recebe 90,00 de 1
           30,46. Aceito porque a moeda é declarada e, como prova de viag
           em, abriria brecha maior; mitigação definitiva é a indicação e
           xplícita de viagem (seção 3).
      821  - **Mesmo gasto lançado em moedas diferentes** (AMB-028): 10,0
           0 EUR e 59,30 BRL do mesmo gasto não são duplicatas e as duas 
           são pagas até o limite do dia. Aceito porque comparar em reais
            acoplaria a duplicata ao câmbio e só pegaria a conversão manu
           al que batesse ao centavo.
      822 +- **Mesmo gasto lançado em categorias diferentes** (AMB-010): 
          +a categoria normalizada faz parte da chave da duplicata (RN-00
          +7). O mesmo gasto relançado com outra categoria não é duplicat
          +a: "Casa Trindade" 85,00 em `alimentacao` e de novo em `repres
          +entacao` no mesmo dia são pagas as duas (170,00). Um gasto tam
          +bém pode ser dividido entre categorias: um jantar de 390,00 la
          +nçado como 90,00 em `alimentacao` e 300,00 em `representacao` 
          +no `CC-COMERCIAL` recebe 390,00, contra 300,00 ou 90,00 se lan
          +çado numa categoria só. Aceito porque a política só diz que du
          +plicatas "devem ser tratadas": tirar a categoria da chave recu
          +saria gastos legítimos que coincidem (corrida e entrega de com
          +ida do mesmo aplicativo, de mesmo valor, no mesmo dia) e ainda
          + não pegaria a divisão, que exigiria uma regra de soma por for
          +necedor e dia, inventada. A saída expõe `categoria` por item p
          +ara a conferência humana.                                     
      823  - **Política aplicada fora da vigência** (AMB-029): a execução
            aplica o arquivo de política recebido a todas as despesas, me
           smo às anteriores à `vigencia`. Aceito porque quem executa esc
           olhe a política explicitamente (`--politica`) e a saída regist
           ra `politica.versao` e `politica.vigencia`.
      824  - **Cotação de até 3 dias antes** (AMB-024): uma despesa em di
           a útil cuja cotação falta no arquivo (lacuna do arquivo, não f
           im de semana) usa a de até 3 dias antes sem aviso, exceto pela
            `data_cotacao` na saída. Aceito porque o arquivo declara publ
           icar só em dias úteis e a diferença de taxa em 3 dias é pequen
           a; lacunas maiores viram `cambio_indisponivel`.
      825  - **Moeda autodeclarada como multiplicador** (AMB-025): a `moe
           da` vem da entrada; um gasto de 20,00 reais lançado como `"EUR
           "` vira 118,60 e recebe até o limite do dia (60,00 no `padrao`
           ). Aceito pelo mesmo motivo do `tem_nota_fiscal` e do `centro_
           custo`: o sistema não verifica a nota nem lê a descrição (seçã
           o 3); a saída expõe `moeda`, `taxa_cambio` e `valor_informado`
            para a conferência humana comparar com a nota.

  Ran 1 shell command (ctrl+o to expand)

⏺ Caso 1 ficou registrado na seção 10 da spec. A entrada no DECISIONS.md (D-008)
  e a mudança de versão eu deixo para o fim, juntando os 7 casos num registro
  só.

  Caso 2 — Terça de Carnaval sem cotação (RN-015, AMB-024)

  Hoje: sem cotação na data, a regra usa a cotação da mesma moeda em D-1, D-2 ou
  D-3. Se nenhum desses dias tiver cotação, o item sai cambio_indisponivel: é
  recusado e fica fora dos totais. A justificativa da AMB-024 diz que os 3 dias
  cobrem "fim de semana e feriado de segunda ou sexta adjacente".

  O problema: no Carnaval não tem PTAX na segunda nem na terça. Uma despesa em
  EUR na terça 09/02/2027 olha D-1 (seg), D-2 (dom) e D-3 (sáb), e nenhum desses
  dias tem cotação. A última cotação é a de sexta, que é D-4. Resultado: uma
  despesa real, com nota, é recusada por inteiro. Já na segunda 08/02, a sexta é
  D-3 e a despesa passa.

  Opções:

  - A) Manter os 3 dias e registrar como risco aceito. Só muda a documentação. O
    ponto fraco é que a justificativa atual promete cobrir feriado, e o
    Carnaval é previsível e acontece todo ano. O conferente teria que tratar
    esse caso por fora.
  - B) Ampliar a janela para 4 dias (D-1 a D-4). Cobre a terça de Carnaval e
    qualquer feriado de segunda ou terça colado no fim de semana. O risco de
    usar taxa velha cresce em um dia só. Muda a RN-015, a AMB-024, o aceite e a
    constante em cambio.py, e o caso de borda entra na seção 7. Precisa de uma
    task nova em tasks.md, revisão do revisor-de-task e nova rodada do
    spec-adversary.
  - C) Sem limite: usar a última cotação anterior, qualquer que seja. Não
    recomendo. Volta o problema que a AMB-024 quis evitar: uma lacuna de semanas
    no arquivo passaria em silêncio com uma taxa velha.

  Impacto no envelope: nenhum. O cambio.json vai de 13/07 a 28/07 sem lacunas
  além dos fins de semana, então A e B dão o mesmo resultado na seção 9.

  Minha recomendação: B. Diferente do caso 1, aqui a regra recusa uma despesa
  legítima sem nenhum caminho para reembolso, num caso que se repete todo ano. A
  mudança no código é pequena, porque é só uma constante de interpretação. Se
  você preferir não abrir task nova agora, A é defensável, desde que a
  justificativa da AMB-024 seja corrigida para não prometer o que não cobre.

  Qual das três?

✻ Churned for 29s · done 4:36 PM

❯ B, amplia pra 4 dias, próximo caso                                            

  Searched for 1 pattern, ran 1 shell command (ctrl+o to expand)

⏺ Bash(uv run python - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)
  ⎿   specs/001-motor-reembolso/spec.md | 18 ++++++++++--------
      1 file changed, 10 insertions(+), 8 deletions(-)
  ⎿  Updated specs/001-motor-reembolso/spec.md (+9 -8)
      115  | Código | Quando | Status resultante |
      116  |---|---|---|
      117  | `entrada_invalida` | elemento que não é objeto; campo obriga
           tório ausente ou com tipo/formato errado; `moeda` fora do form
           ato; ou `valor` com valor absoluto a partir de 1.000.000.000,0
           0 (RN-002) | `recusado` |
      118 -| `cambio_indisponivel` | moeda diferente de `BRL` sem cotação
          - no arquivo de câmbio na data da despesa nem nos 3 dias anteri
          -ores (RN-015) | `recusado` |                                  
      118 +| `cambio_indisponivel` | moeda diferente de `BRL` sem cotação
          + no arquivo de câmbio na data da despesa nem nos 4 dias anteri
          +ores (RN-015) | `recusado` |                                  
      119  | `valor_invalido` | valor considerado menor ou igual a zero (
           RN-004) | `recusado` |
      120  | `fora_do_periodo` | data fora de `[inicio, fim]` (RN-005) | 
           `recusado` |
      121  | `categoria_fora_da_politica` | categoria ausente da tabela a
           plicada ou com limite 0 nela (RN-006, RN-014) | `recusado` |
     ...
      290  **Regra:**
      291  - A moeda da despesa é o campo `moeda`; ausente ou nulo vale `
           BRL`. Formato inválido é `entrada_invalida` (RN-002).
      292  - `BRL` tem taxa 1, sem consultar o arquivo de câmbio (uma ent
           rada `BRL` no arquivo é ignorada).
      293 -- Para outra moeda, a taxa é a do arquivo de câmbio para essa 
          -moeda **na data da despesa**. Se essa data não tem cotação par
          -a a moeda, usa-se a cotação **dessa moeda** na data anterior m
          -ais próxima que a tenha, **até 3 dias corridos antes** (D-1, D
          --2 ou D-3); uma data intermediária que só cota outras moedas é
          - ignorada: um sábado ou domingo usa a sexta-feira; uma segunda
          --feira de feriado usa a sexta-feira. Sem cotação de D a D-3 → 
          -`recusado`, motivo `cambio_indisponivel`. Cotação posterior à 
          -data da despesa nunca é usada.                                
      293 +- Para outra moeda, a taxa é a do arquivo de câmbio para essa 
          +moeda **na data da despesa**. Se essa data não tem cotação par
          +a a moeda, usa-se a cotação **dessa moeda** na data anterior m
          +ais próxima que a tenha, **até 4 dias corridos antes** (D-1, D
          +-2, D-3 ou D-4); uma data intermediária que só cota outras moe
          +das é ignorada: um sábado ou domingo usa a sexta-feira; uma se
          +gunda-feira de feriado usa a sexta-feira; a terça-feira de Car
          +naval (segunda e terça sem cotação) usa a sexta-feira. Sem cot
          +ação de D a D-4 → `recusado`, motivo `cambio_indisponivel`. Co
          +tação posterior à data da despesa nunca é usada.              
      294  - Moeda bem formada que não aparece no arquivo de câmbio (incl
           usive código que não existe na ISO 4217, como `XYZ`) → `cambio
           _indisponivel`. Não há lista própria de códigos ISO.
      295  - Taxa é "reais por uma unidade da moeda": `valor_considerado`
            = `valor` × taxa, arredondado uma vez (RN-003).
      296  - Uma despesa recusada por `cambio_indisponivel` tem `valor_co
           nsiderado`, `taxa_cambio`, `data_cotacao`, `em_viagem` e `limi
           te_diario` nulos, e não entra nos totais.
      297  - A moeda não muda nenhuma outra regra: por si só não caracter
           iza viagem, nem impede que uma hospedagem com nota a comprove 
           (AMB-023); todos os limites e o mínimo da nota são comparados 
           em reais.
      298  
      299  **Origem:** Política v4, item B; AMB-024, AMB-025, AMB-026 (D-
           007).
      300 -**Aceite** (`cambio.json` do envelope): 22,00 EUR em 14/07 → t
          -axa 5,93, `data_cotacao` 2026-07-14, `valor_considerado` 130,4
          -6. 30,00 EUR em 18/07 (sábado) → taxa 5,96 de 17/07, `valor_co
          -nsiderado` 178,80. Sem `moeda` → `BRL`, taxa 1, `data_cotacao`
          - nula. `"moeda": null` → `BRL`. 55,00 GBP em 21/07 → `cambio_i
          -ndisponivel`, `valor_considerado` nulo, fora de `valor_solicit
          -ado`. USD em 2026-07-12 (nenhuma cotação de 09/07 a 12/07) → `
          -cambio_indisponivel`. Câmbio só com 13/07: USD em 16/07 → usa 
          -13/07 (D-3); USD em 17/07 → `cambio_indisponivel` (D-4).      
      300 +**Aceite** (`cambio.json` do envelope): 22,00 EUR em 14/07 → t
          +axa 5,93, `data_cotacao` 2026-07-14, `valor_considerado` 130,4
          +6. 30,00 EUR em 18/07 (sábado) → taxa 5,96 de 17/07, `valor_co
          +nsiderado` 178,80. Sem `moeda` → `BRL`, taxa 1, `data_cotacao`
          + nula. `"moeda": null` → `BRL`. 55,00 GBP em 21/07 → `cambio_i
          +ndisponivel`, `valor_considerado` nulo, fora de `valor_solicit
          +ado`. USD em 2026-07-12 (nenhuma cotação de 08/07 a 12/07) → `
          +cambio_indisponivel`. Câmbio só com 13/07: USD em 17/07 → usa 
          +13/07 (D-4); USD em 18/07 → `cambio_indisponivel` (D-5). Câmbi
          +o com EUR em 05/02/2027 (sexta) e nada em 08/02 e 09/02 (Carna
          +val): EUR em 09/02 → usa 05/02 (D-4).                         
      301  
      302  ### RN-016 — Arquivos de política e de câmbio
      303  
     ...
      534  
      535  **Texto original do RH:** "A conversão usa a taxa da data da d
           espesa, não a taxa de hoje." No arquivo: "Cotações publicadas 
           apenas em dias úteis bancários", de 13/07 a 28/07.
      536  **O que não está claro:** que taxa usar num fim de semana ou f
           eriado (e-004, sábado 18/07), e numa data sem nenhuma cotação 
           próxima no arquivo. A escolha muda a aprovação, não só o valor
           : 16,70 EUR sem nota num sábado dá 99,53 com a taxa de sexta (
           não exige nota) e 100,37 com a de segunda (`nota_fiscal_ausent
           e`).
      537 -**Decisão:** usa a cotação da moeda na data; sem ela, a da mes
          -ma moeda na data anterior mais próxima que a tenha, até 3 dias
          - corridos antes; sem nenhuma, `cambio_indisponivel`. Nunca uma
          - cotação posterior.                                           
      538 -**Justificativa:** é a prática da PTAX: a cotação vigente num 
          -sábado é a de sexta. A cotação posterior ainda não existia na 
          -data da despesa. O limite de 3 dias cobre fim de semana e feri
          -ado de segunda ou sexta adjacente; sem limite, uma lacuna de s
          -emanas no arquivo passaria em silêncio com uma taxa velha.    
      537 +**Decisão:** usa a cotação da moeda na data; sem ela, a da mes
          +ma moeda na data anterior mais próxima que a tenha, até 4 dias
          + corridos antes; sem nenhuma, `cambio_indisponivel`. Nunca uma
          + cotação posterior. (Até a spec 2.0 eram 3 dias; ampliado na D
          +-008.)                                                        
      538 +**Justificativa:** é a prática da PTAX: a cotação vigente num 
          +sábado é a de sexta. A cotação posterior ainda não existia na 
          +data da despesa. O limite de 4 dias cobre fim de semana com fe
          +riado de segunda ou sexta adjacente e também os dois dias de C
          +arnaval (segunda e terça sem PTAX), em que a última cotação da
          + terça é a de sexta, D-4; com 3 dias, uma despesa legítima na 
          +terça de Carnaval seria recusada sem caminho de reembolso; sem
          + limite, uma lacuna de semanas no arquivo passaria em silêncio
          + com uma taxa velha.                                          
      539  **Regra afetada:** RN-015
      540  
      541  ### AMB-025 — Moeda sem cotação, mal escrita ou nula (D, F)
     ...
      678  | Moeda nula | `"moeda": null`, alimentação 45,00 | como `BRL`
           : `moeda` `BRL`, `taxa_cambio` 1, `data_cotacao` nula, `aprova
           do` com 45,00 | RN-015 |
      679  | Moeda estrangeira com cotação | 22,00 EUR em 14/07, alimenta
           ção com nota | taxa 5,93, `data_cotacao` 2026-07-14; `valor_co
           nsiderado` 130,46; `parcial` com 60,00 | RN-015, RN-003 |
      680  | Moeda estrangeira em sábado | 30,00 EUR em 18/07 (sábado), a
           limentação com nota | taxa 5,96 de 17/07; `data_cotacao` 2026-
           07-17; `valor_considerado` 178,80 | RN-015 |
      681 -| Cotação exatamente 3 dias antes | câmbio só com 13/07 (USD 5
          -,42); 10,00 USD em 16/07 | usa 13/07; `valor_considerado` 54,2
          -0 | RN-015 |                                                  
      682 -| Cotação 4 dias antes | câmbio só com 13/07; 10,00 USD em 17/
          -07 | `cambio_indisponivel`; `valor_considerado` nulo; fora dos
          - totais | RN-015 |                                            
      681 +| Cotação exatamente 4 dias antes | câmbio só com 13/07 (USD 5
          +,42); 10,00 USD em 17/07 | usa 13/07; `valor_considerado` 54,2
          +0 | RN-015 |                                                  
     … 12 more lines (ctrl+o to expand)

  Searched for 1 pattern (ctrl+o to expand)

⏺ Caso 2 já está na spec, em todas as partes: o motivo na seção 4, a RN-015 com
  regra e aceite, a AMB-024 com decisão e justificativa, a seção 7 e o risco na
  seção 10.

  Na seção 7, mudei os casos de borda "Cotação exatamente 3 dias antes" e
  "Cotação 4 dias antes" para "4 dias" e "5 dias", e entrou a linha nova "Terça
  de Carnaval". Por isso o test_rastreabilidade.py vai falhar até a task de
  código. O ajuste do código, do plan.md e do tasks.md vira uma task nova. Eu
  proponho essa task no fim, junto com o D-008.

  Caso 3 — descricao com null ou tipo diferente de texto (seção 4, RN-002)

  Hoje na spec:
  - A seção 4 descreve descricao como "texto, descrição livre; não usada em
    regras", não obrigatória.
  - A lista de despesa inválida da RN-002 não cita descricao.
  - Com isso, "descricao": null, 17 ou {} têm duas leituras possíveis: despesa
    válida ou entrada_invalida.

  O que o código faz hoje: conferi, src/ não lê descricao em lugar nenhum. Na
  prática, qualquer tipo é aceito e a despesa segue normalmente.

  Opções:
  - A) Aceitar qualquer tipo, inclusive null e ausente. Basta deixar isso
    explícito na seção 4 e na RN-002, sem mudar o código. É coerente com a seção
    3: o motor nunca lê a descrição, então ela não pode ser motivo de recusa.
  - B) Exigir texto quando presente (null vale como ausente) e tratar outro tipo
    como entrada_invalida. Segue o padrão de moeda e centro_custo. O problema é
    que recusa uma despesa legítima por causa de um campo que nenhuma regra
    usa. Também precisaria de task nova, teste e linha na seção 7.

  Minha recomendação: A. Recusar um reembolso por causa do tipo de um campo
  ignorado seria uma regra sem origem na política. null vem com frequência de
  exportação de sistema e isso afetaria dados reais. A decisão só documenta o
  que o código já faz.

  Qual das duas?

✻ Crunched for 42s · done 4:37 PM

❯ pode seguir a recomendação                                                    

⏺ Bash(uv run python - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)
  ⎿  192:### RN-004 — Valor deve ser positivo
     193-
     194-**Regra:** despesa com `valor_considerado` (em reais, RN-003) meno
     … +36 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/spec.md (+3 -1)
      62  | `despesas[].id` | texto | identificador da despesa | sim (`en
          trada_invalida`) |
      63  | `despesas[].data` | data `AAAA-MM-DD` | data em que a despesa
           ocorreu | sim (`entrada_invalida`) |
      64  | `despesas[].categoria` | texto | categoria da despesa | sim (
          `entrada_invalida`) |
      65 -| `despesas[].descricao` | texto | descrição livre; não usada e
         -m regras | não |                                               
      65 +| `despesas[].descricao` | qualquer | descrição livre; não usad
         +a em regras e nunca validada: ausente, nula ou de qualquer tipo
         +, a despesa segue (RN-002) | não |                             
      66  | `despesas[].fornecedor` | texto | estabelecimento; usado na d
          etecção de duplicatas | sim (`entrada_invalida`) |
      67  | `despesas[].valor` | número | valor na moeda da despesa | sim
           (`entrada_invalida`) |
      68  | `despesas[].moeda` | texto ou nulo | código ISO 4217 da moeda
           do `valor`: exatamente 3 letras maiúsculas de `A` a `Z` (RN-01
          5) | não; ausente ou nulo → `BRL`; outro tipo ou outro formato 
          → `entrada_invalida` |
     ...
      178  - Uma despesa recusada por `entrada_invalida` tem `valor_consi
           derado`, `taxa_cambio`, `data_cotacao`, `em_viagem` e `limite_
           diario` nulos, e não entra nos totais.
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
      181 +- `descricao` nunca torna a despesa inválida: ausente, nula, t
          +exto ou de qualquer outro tipo (número, booleano, lista, objet
          +o), ela é ignorada, como um campo extra (seção 3: o sistema nã
          +o lê a descrição).                                            
      182  - Campos extras, no arquivo ou nas despesas, são ignorados.
      183  **Origem:** necessidade operacional (a política não trata entr
           ada malformada); pontos 7 e 9 de D-001; AMB-018; D-005; AMB-02
           0 e AMB-025 (D-007).
      184  **Aceite:** despesa sem `tem_nota_fiscal` com `valor` 33.333 →
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
           00 (o teto vale para o número recebido). `"moeda": "eur"` → `e
           ntrada_invalida`, `moeda` `eur` na saída. `"moeda": 978` → `en
           trada_invalida`, `moeda` nula na saída. `"centro_custo": 17` →
            erro de arquivo.
     ...
      685  | Moeda sem cotação no arquivo | 55,00 GBP em 21/07 | `cambio_
           indisponivel`; `moeda` `GBP`; `taxa_cambio` e `valor_considera
           do` nulos; fora de `valor_solicitado` | RN-015 |
      686  | Moeda em minúsculas | `"moeda": "eur"` | `entrada_invalida`;
            `moeda` `eur` na saída | RN-002 |
      687  | Moeda de tipo errado | `"moeda": 978` | `entrada_invalida`; 
           `moeda` nula na saída | RN-002 |
      688 +| Descrição nula ou de outro tipo | alimentação 45,00 em 03/07
          + sem nota, com `"descricao": null`; a mesma com `"descricao": 
          +17` e com `"descricao": {}` | as três `aprovado` com 45,00 (ca
          +da uma num arquivo próprio) | RN-002 |                        
      689  | Sem cotação e fora do período | 10,00 USD em 15/04, período 
           de julho | `cambio_indisponivel` (etapa 2 antes da 4) | RN-015
            |
      690  | Conversão arredondada uma vez | 16,8649 EUR em 14/07, alimen
           tação sem nota | 100,008857 → `valor_considerado` 100,01 → `no
           ta_fiscal_ausente` | RN-003, RN-008 |
      691  | Nota fiscal comparada em reais | 40,00 USD em 20/07, transpo
           rte sem nota | 220,00 → `nota_fiscal_ausente` | RN-008 |

  Searched for 2 patterns (ctrl+o to expand)

⏺ Caso 3 entrou na spec: a seção 4 mudou o tipo para "qualquer, nunca validada",
  a RN-002 ganhou uma linha explícita e a seção 7 ganhou o caso "Descrição nula
  ou de outro tipo". O código não muda. O caso de borda novo pede uma linha em
  test_casos_de_borda.py, que entra na mesma task do caso 2.

  Caso 4 — Fórmula de status da RN-011 × RN-004 com valor_considerado 0,00

  Hoje (RN-011): a regra define o status só pela comparação dos valores:
  - aprovado quando reembolsado = considerado;
  - parcial quando 0 < reembolsado < considerado;
  - recusado quando reembolsado = 0.

  O problema: com valor 0 ou 0.004 BRL, considerado e reembolsado valem 0. As
  cláusulas "aprovado" e "recusado" valem ao mesmo tempo. A RN-004 diz
  recusado/valor_invalido, e um item aprovado não pode ter motivo. A fórmula
  também não cobre os outros recusados: um negativo (-45 vs. reembolsado 0) e
  entrada_invalida (considerado nulo).

  O que o código faz hoje: em src/reembolso/motor.py:56-59, a fórmula só é
  aplicada a quem chega ao limite diário (etapa 9). Recusa nas etapas 1 a 7 já
  sai recusado com o motivo da etapa. Chegar à etapa 9 garante considerado > 0,
  então ali não há ambiguidade. Portanto o código já segue a leitura correta, e
  o problema está só no texto da spec.

  Opções:
  - A) Reescrever a RN-011 em duas partes. (1) Uma despesa recusada numa etapa
    de 1 a 7 da seção 8 é recusado com o motivo dessa etapa. (2) Para quem chega
    à etapa 9 (considerado > 0 garantido), vale a fórmula. O aceite passa a
    citar os dois casos. Só muda o texto da spec, não o código.
  - B) Manter a fórmula como regra geral e acrescentar "exceto quando há motivo 
    de recusa de etapa anterior". Dá o mesmo resultado, mas a regra fica escrita
    de trás para frente: a exceção cobre a maioria dos motivos.

  Minha recomendação: A. A regra passa a dizer o que o código e a seção 8 já
  fazem, e acaba a leitura dupla.

  Pode seguir com A?

✻ Crunched for 27s · done 4:39 PM

❯ pode seguir a recomendação                                                    

⏺ Bash(uv run python - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)  ⎿  59:| `periodo.inicio` | data `AAAA-MM-DD` | primeiro dia do período (i
     nclusive) | sim (erro de arquivo) |
     60:| `periodo.fim` | data `AAAA-MM-DD` | último dia do período (inclus
     … +67 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/spec.md (+7 -3)
      246  
      247  ### RN-011 — Status e justificativa
      248  
      249 -**Regra:** `aprovado` quando `valor_reembolsado = valor_consid
          -erado`; `parcial` quando `0 < valor_reembolsado < valor_consid
          -erado`; `recusado` quando `valor_reembolsado = 0`. Todo item `
          -parcial` ou `recusado` tem um `motivo` da tabela da seção 4; t
          -odo item tem uma `justificativa` em texto.                    
      250 -**Origem:** objetivo do sistema.                              
      251 -**Aceite:** nenhum item da saída tem status incompatível com o
          -s seus valores.                                               
      249 +**Regra:** o status é decidido em duas partes, seguindo a seçã
          +o 8:                                                          
      250 +- despesa recusada numa das etapas 1 a 7 da seção 8 é `recusad
          +o`, com o motivo dessa etapa e `valor_reembolsado` 0, qualquer
          + que seja o seu `valor_considerado` (nulo, negativo, zero ou p
          +ositivo);                                                     
      251 +- despesa que chega à etapa 9 (limite diário), cujo `valor_con
          +siderado` é sempre maior que zero (RN-004), é `aprovado` quand
          +o `valor_reembolsado = valor_considerado`; `parcial`, motivo `
          +limite_diario_excedido`, quando `0 < valor_reembolsado < valor
          +_considerado`; `recusado`, motivo `limite_diario_excedido`, qu
          +ando `valor_reembolsado = 0`.                                 
      252 +                                                              
      253 +Todo item `parcial` ou `recusado` tem um `motivo` da tabela da
          + seção 4; todo item `aprovado` tem `motivo` nulo; todo item te
          +m uma `justificativa` em texto.                               
      254 +**Origem:** objetivo do sistema; D-008 (antes, a fórmula única
          + admitia `aprovado` e `recusado` ao mesmo tempo com `valor_con
          +siderado` 0,00).                                              
      255 +**Aceite:** `valor` 0 ou 0.004 BRL → `recusado`, `valor_invali
          +do` (nunca `aprovado`, embora reembolsado = considerado = 0). 
          +`valor` -45.00 → `recusado`, `valor_invalido`. Despesa na etap
          +a 9 com 45,00 e limite livre → `aprovado`; com 30,00 e 15,00 l
          +ivres → `parcial` com 15,00; com limite esgotado → `recusado`,
          + `limite_diario_excedido`. Nenhum item da saída tem status inc
          +ompatível com essas duas partes.                              
      256  
      257  ### RN-012 — Hospedagem: um lançamento é uma diária
      258  

  Ran 1 shell command (ctrl+o to expand)

⏺ RN-011 reescrita na spec: a regra agora tem as duas partes, o motivo nulo para
  aprovado ficou explícito e o aceite cobre valor 0, 0.004 e -45. O código não
  muda.

  Caso 5 — O que é "data válida AAAA-MM-DD" (RN-002, RN-016, RN-010, RN-015)

  O problema: a spec diz "data válida AAAA-MM-DD", mas deixa três pontos em
  aberto:
  - se aceita dígitos de outra escrita ("٢٠٢٦-٠٧-٠٣"). A seção 5 chama esses
    caracteres de "dígito decimal", o que abre a dúvida;
  - se aceita o ano 0000 ("0000-01-01");
  - o que acontece quando D+1 (viagem) ou D-4 (câmbio) cai fora do calendário,
    por exemplo uma hospedagem em 9999-12-31.

  O que o código já faz (veio do plan, DT-003 e DT-014, mas não está na spec):
  - src/reembolso/leitura.py:89-106 só aceita dígitos ASCII 0-9, pela regex.
    Datas de 0001-01-01 a 9999-12-31, as do calendário gregoriano; 0000-01-01 é
    inválida;
  - src/reembolso/motor.py:199: o D+1 que passaria de 9999-12-31 é simplesmente
    ignorado e só D fica em viagem;
  - src/reembolso/cambio.py:75: a busca que voltaria antes de 0001-01-01 para
    ali, como se não houvesse cotação.

  Opções:
  - A) Levar para a spec o que o código já faz. Data válida = dígitos ASCII, ano
    0001 a 9999 e data que existe no calendário; D+1 e D-n fora do calendário
    não existem: a viagem marca só D, e a busca do câmbio para ali. O texto
    entra uma vez na RN-002 e é citado pela RN-016, RN-010 e RN-015. O código
    não muda.
  - B) Restringir a uma faixa de anos "realista" (por exemplo, 1900 a 2100).
    Seria regra inventada, sem origem na política, e exigiria mudar o código.

  Minha recomendação: A. O efeito prático é quase nulo, e o objetivo é só que a
  spec diga o que o sistema já faz.

  Pode seguir com A?

✻ Worked for 24s · done 4:39 PM

❯ pode seguir com a A                                                           

⏺ Bash(uv run python - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)
  ⎿  41:### Interface
     42-
     43-`<comando> calcular --input <arquivo de entrada> --politica <arquiv
     … +24 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/spec.md (+3 -2)
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
      181  - `descricao` nunca torna a despesa inválida: ausente, nula, t
           exto ou de qualquer outro tipo (número, booleano, lista, objet
           o), ela é ignorada, como um campo extra (seção 3: o sistema nã
           o lê a descrição).
      182 +- **Data válida `AAAA-MM-DD`**, nesta regra e em toda a spec (
          +RN-016, `vigencia` e chaves de `taxas`): texto de exatamente 1
          +0 caracteres, com 4, 2 e 2 dígitos ASCII (`0` a `9`) separados
          + por `-`, que forma uma data existente no calendário gregorian
          +o entre 0001-01-01 e 9999-12-31. Dígitos de outras escritas (`
          +"٢٠٢٦-٠٧-٠٣"`), ano `0000`, `"2026-7-3"`, `"20260703"` e `"202
          +6-02-30"` não são datas válidas. Diferente da normalização da 
          +seção 5, que aceita algarismos de qualquer escrita em texto li
          +vre.                                                          
      183  - Campos extras, no arquivo ou nas despesas, são ignorados.
      184  **Origem:** necessidade operacional (a política não trata entr
           ada malformada); pontos 7 e 9 de D-001; AMB-018; D-005; AMB-02
           0 e AMB-025 (D-007).
      185  **Aceite:** despesa sem `tem_nota_fiscal` com `valor` 33.333 →
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
           00 (o teto vale para o número recebido). `"moeda": "eur"` → `e
           ntrada_invalida`, `moeda` `eur` na saída. `"moeda": 978` → `en
           trada_invalida`, `moeda` nula na saída. `"centro_custo": 17` →
            erro de arquivo.
     ...
      241  
      242  ### RN-010 — Colaborador em viagem
      243  
      243 -**Regra:** uma despesa de `hospedagem` **comprova viagem** qua
          -ndo tem `tem_nota_fiscal` verdadeiro e passou pelas etapas 1 a
          - 7 da seção 8. Uma hospedagem que comprova viagem na data D co
          -loca em viagem as datas **D e D+1** (a noite da diária e o dia
          - seguinte). Em datas em viagem, os limites de `alimentacao` e 
          -`transporte_urbano` são ampliados pelo percentual da política 
          -(RN-009). A condição de viagem vale para todas as despesas da 
          -data, independentemente da ordem em que aparecem na entrada. H
          -ospedagem recusada por `categoria_fora_da_politica` (inclusive
          - por limite 0, AMB-021) não comprova viagem. A moeda não impor
          -ta para a comprovação: uma hospedagem com nota em moeda estran
          -geira comprova viagem como qualquer outra, e nenhuma outra des
          -pesa comprova viagem por estar em moeda estrangeira (AMB-023).
      244 +**Regra:** uma despesa de `hospedagem` **comprova viagem** qua
          +ndo tem `tem_nota_fiscal` verdadeiro e passou pelas etapas 1 a
          + 7 da seção 8. Uma hospedagem que comprova viagem na data D co
          +loca em viagem as datas **D e D+1** (a noite da diária e o dia
          + seguinte); se D é 9999-12-31, D+1 não existe e só D fica em v
          +iagem. Em datas em viagem, os limites de `alimentacao` e `tran
          +sporte_urbano` são ampliados pelo percentual da política (RN-0
          +09). A condição de viagem vale para todas as despesas da data,
          + independentemente da ordem em que aparecem na entrada. Hosped
          +agem recusada por `categoria_fora_da_politica` (inclusive por 
          +limite 0, AMB-021) não comprova viagem. A moeda não importa pa
          +ra a comprovação: uma hospedagem com nota em moeda estrangeira
          + comprova viagem como qualquer outra, e nenhuma outra despesa 
          +comprova viagem por estar em moeda estrangeira (AMB-023).     
      245  **Origem:** política do RH, item 6; AMB-004; AMB-021 e AMB-023
            (D-007).
      246  **Aceite** (tabela `padrao` da v4): hospedagem com nota em 14/
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
      247  
     ...
      296  **Regra:**
      297  - A moeda da despesa é o campo `moeda`; ausente ou nulo vale `
           BRL`. Formato inválido é `entrada_invalida` (RN-002).
      298  - `BRL` tem taxa 1, sem consultar o arquivo de câmbio (uma ent
           rada `BRL` no arquivo é ignorada).
      298 -- Para outra moeda, a taxa é a do arquivo de câmbio para essa 
          -moeda **na data da despesa**. Se essa data não tem cotação par
          -a a moeda, usa-se a cotação **dessa moeda** na data anterior m
          -ais próxima que a tenha, **até 4 dias corridos antes** (D-1, D
          --2, D-3 ou D-4); uma data intermediária que só cota outras moe
          -das é ignorada: um sábado ou domingo usa a sexta-feira; uma se
          -gunda-feira de feriado usa a sexta-feira; a terça-feira de Car
          -naval (segunda e terça sem cotação) usa a sexta-feira. Sem cot
          -ação de D a D-4 → `recusado`, motivo `cambio_indisponivel`. Co
          -tação posterior à data da despesa nunca é usada.              
      299 +- Para outra moeda, a taxa é a do arquivo de câmbio para essa 
          +moeda **na data da despesa**. Se essa data não tem cotação par
          +a a moeda, usa-se a cotação **dessa moeda** na data anterior m
          +ais próxima que a tenha, **até 4 dias corridos antes** (D-1, D
          +-2, D-3 ou D-4); uma data intermediária que só cota outras moe
          +das é ignorada: um sábado ou domingo usa a sexta-feira; uma se
          +gunda-feira de feriado usa a sexta-feira; a terça-feira de Car
          +naval (segunda e terça sem cotação) usa a sexta-feira. Datas a
          +nteriores a 0001-01-01 não existem: a busca para ali (em 0001-
          +01-02, só D e D-1 são consultadas). Sem cotação de D a D-4 → `
          +recusado`, motivo `cambio_indisponivel`. Cotação posterior à d
          +ata da despesa nunca é usada.                                 
      300  - Moeda bem formada que não aparece no arquivo de câmbio (incl
           usive código que não existe na ISO 4217, como `XYZ`) → `cambio
           _indisponivel`. Não há lista própria de códigos ISO.
      301  - Taxa é "reais por uma unidade da moeda": `valor_considerado`
            = `valor` × taxa, arredondado uma vez (RN-003).
      302  - Uma despesa recusada por `cambio_indisponivel` tem `valor_co
           nsiderado`, `taxa_cambio`, `data_cotacao`, `em_viagem` e `limi
           te_diario` nulos, e não entra nos totais.

⏺ Now check how the CLI handles repeated/unknown args today.

  Ran 2 shell commands (ctrl+o to expand)

⏺ A spec agora define "data válida" uma única vez, na RN-002, e esse texto vale
  para a spec inteira. Também ficou registrado o limite do calendário na RN-010
  (D+1 depois de 9999-12-31) e na RN-015 (busca antes de 0001-01-01). O código
  não muda.

  Caso 6 — Argumento repetido, desconhecido ou sobrando (seção 4, AMB-031)

  Hoje na spec: erro de uso é só subcomando errado ou argumento ausente. A
  AMB-031 justifica os argumentos obrigatórios com "a mesma linha de comando dá
  sempre o mesmo resultado".

  Testei a CLI com o envelope:

  ┌───────────────────────────────────┬─────────────────────────────────────┐
  │         Linha de comando          │           Resultado hoje            │
  ├───────────────────────────────────┼─────────────────────────────────────┤
  │ --verbose a mais                  │ erro de uso, código 2, saída não    │
  │                                   │ criada ✔                            │
  ├───────────────────────────────────┼─────────────────────────────────────┤
  │ argumento posicional sobrando     │ erro de uso, código 2, saída não    │
  │ (extra)                           │ criada ✔                            │
  ├───────────────────────────────────┼─────────────────────────────────────┤
  │ --politica nao-existe.json        │ código 0 e saída gravada: vale a    │
  │ --politica politica-v4.json no    │ última ocorrência, sem nenhum aviso │
  │ meio                              │                                     │
  ├───────────────────────────────────┼─────────────────────────────────────┤
  │ --politica politica-v4.json       │ erro de arquivo, porque leu a       │
  │ --politica nao-existe.json        │ segunda                             │
  ├───────────────────────────────────┼─────────────────────────────────────┤
  │ o mesmo --politica repetido no    │ erro de uso, por uma                │
  │ fim da linha                      │ particularidade do argparse         │
  └───────────────────────────────────┴─────────────────────────────────────┘

  Ou seja: o argumento desconhecido ou sobrando já é tratado direito, só falta
  escrever isso na spec. O repetido é o problema real: a linha mostra duas
  políticas, usa uma delas em silêncio, e o comportamento ainda depende da
  posição na linha.

  Opções:
  - A) Argumento repetido, desconhecido ou sobrando é erro de uso. Para o
    desconhecido e o sobrando, a spec só passa a dizer o que o código já faz.
    Para o repetido, o código muda pouco: o cli.py passa a recusar a segunda
    ocorrência de --input, --politica, --cambio ou --output. Entra um caso de
    borda na seção 7. Precisa de task, mas é uma task de estrutura (CLI), então
    não passa pelo revisor-de-task.
  - B) Documentar "vale a última ocorrência" e registrar como risco aceito. Não
    muda código, mas contraria a justificativa da AMB-031 e deixa o caso
    inconsistente: no fim da linha, o argumento repetido dá erro.

  Minha recomendação: A. O comportamento fica previsível e coerente com a
  AMB-031, e a mudança cabe na mesma task nova dos casos 2 e 3.

  Pode seguir com A?

✻ Baked for 30s · done 4:40 PM

❯ pode seguir com A                                                             

⏺ Bash(cd /Users/rafaeltxm/repo/sdd-desafio && uv run python - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)
  ⎿  812:- **Datas de entrada e saída de hospedagem.** A solução correta pa
     ra AMB-005 exige mudar o formato de entrada. Decisão provisória: um la
     nçamento = uma diária. Consequência conhecida: uma hospedagem de 480,0
     … +25 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/spec.md (+3 -2)
      44  
      45  - Sucesso: grava o arquivo de saída e termina com código 0.
      46  - Erro de arquivo (RN-002 para a entrada, RN-016 para a polític
          a e o câmbio), inclusive quando o arquivo de saída não pode ser
           gravado: não cria nem altera o arquivo de saída (se já existia
          , permanece como estava), escreve uma mensagem de erro e termin
          a com código diferente de 0.
      47 -- Erro de uso (subcomando diferente de `calcular`, `--input`, `
         ---politica`, `--cambio` ou `--output` ausentes): mesmo comporta
         -mento do erro de arquivo. Os cinco argumentos são sempre obriga
         -tórios, inclusive quando todas as despesas são em reais (AMB-03
         -1).                                                            
      47 +- Erro de uso (subcomando diferente de `calcular`; `--input`, `
         +--politica`, `--cambio` ou `--output` ausentes; qualquer um del
         +es repetido, mesmo com o mesmo arquivo; argumento desconhecido 
         +ou sobrando): mesmo comportamento do erro de arquivo. Nunca val
         +e "a última ocorrência": uma linha de comando que mostra duas p
         +olíticas não é executada. Os cinco argumentos são sempre obriga
         +tórios, inclusive quando todas as despesas são em reais (AMB-03
         +1).                                                            
      48  
      49  ### Entrada
      50  
     ...
      596  
      597  **Texto original do RH:** "O motor precisa ler a política de f
           ora, não de dentro do código." / "As taxas estão em `cambio.js
           on`."
      598  **O que não está claro:** se os arquivos são argumentos, camin
           hos fixos ou parte da entrada; se o câmbio é exigido quando to
           das as despesas são em reais; o que fazer com um arquivo defei
           tuoso.
      599 -**Decisão:** dois argumentos obrigatórios, `--politica` e `--c
          -ambio`, sempre; qualquer defeito em um deles é erro de arquivo
          - (RN-016).                                                    
      599 +**Decisão:** dois argumentos obrigatórios, `--politica` e `--c
          +ambio`, sempre; qualquer defeito em um deles é erro de arquivo
          + (RN-016). Argumento repetido, desconhecido ou sobrando é erro
          + de uso (seção 4; D-008).                                     
      600  **Justificativa:** tudo o que entra no cálculo aparece na linh
           a de comando, e a mesma linha de comando dá sempre o mesmo res
           ultado (seção 9). Um caminho implícito faria o resultado mudar
            sem nada visível mudar. Com política ou câmbio defeituosos ne
           nhum cálculo é confiável; recusar despesa por despesa esconder
           ia o defeito atrás de recusas.
      601  **Regra afetada:** seção 4, RN-016
      602  
     ...
      690  | Moeda sem cotação no arquivo | 55,00 GBP em 21/07 | `cambio_
           indisponivel`; `moeda` `GBP`; `taxa_cambio` e `valor_considera
           do` nulos; fora de `valor_solicitado` | RN-015 |
      691  | Moeda em minúsculas | `"moeda": "eur"` | `entrada_invalida`;
            `moeda` `eur` na saída | RN-002 |
      692  | Moeda de tipo errado | `"moeda": 978` | `entrada_invalida`; 
           `moeda` nula na saída | RN-002 |
      693 +| Argumento repetido | `calcular --input e.json --politica pol
          +itica-v4.json --politica outra.json --cambio c.json --output s
          +.json` (e a mesma linha com o `--politica` repetido no fim, ou
          + com o mesmo arquivo nas duas vezes) | erro de uso; código dif
          +erente de 0; saída não criada nem alterada | seção 4, AMB-031 
          +|                                                             
      694  | Descrição nula ou de outro tipo | alimentação 45,00 em 03/07
            sem nota, com `"descricao": null`; a mesma com `"descricao": 
           17` e com `"descricao": {}` | as três `aprovado` com 45,00 (ca
           da uma num arquivo próprio) | RN-002 |
      695  | Sem cotação e fora do período | 10,00 USD em 15/04, período 
           de julho | `cambio_indisponivel` (etapa 2 antes da 4) | RN-015
            |
      696  | Conversão arredondada uma vez | 16,8649 EUR em 14/07, alimen
           tação sem nota | 100,008857 → `valor_considerado` 100,01 → `no
           ta_fiscal_ausente` | RN-003, RN-008 |

  Ran 1 shell command (ctrl+o to expand)

⏺ Caso 6 entrou na spec: a seção 4 lista agora o argumento repetido, o
  desconhecido e o sobrando como erro de uso, a AMB-031 cita a decisão e a seção
  7 ganhou o caso "Argumento repetido". A mudança no cli.py vai para a task
  nova.

  Caso 7 — Hospedagem de várias noites lançada uma vez só (RN-010, AMB-005)

  Hoje: pela decisão provisória da AMB-005, cada lançamento conta como uma
  diária. A hospedagem com nota põe em viagem só D e D+1. A seção 10 registra
  uma única consequência, a do valor: e-007, "3 noites", recebe 400,00 de
  1.200,00.

  A consequência que ficou de fora: os dias seguintes da mesma estadia perdem a
  ampliação dos limites de viagem. Exemplo no padrao: hospedagem "3 noites" em
  14/07, com nota, e alimentação de 80,00 em 16/07. O dia 16/07 não conta como
  viagem, então o limite é 60,00 e a alimentação sai parcial com 60,00. Se o dia
  contasse como viagem, sairia aprovado com 80,00.

  No envelope: a e-007 deixa o dia 24/07 fora de viagem. A única despesa desse
  dia é a e-009, de coworking, categoria que não tem ampliação. Nenhum valor da
  seção 9 muda. O exemplo original também não tem despesa nesse cenário.

  Opções:
  - A) Registrar a consequência na decisão provisória da seção 10, ao lado da
    que já existe, com o exemplo acima e a nota de que no envelope ela não muda
    nada. Muda só o texto. A solução de verdade continua sendo a mesma de antes:
    datas de entrada e saída na entrada, o que exige mudar o formato e por isso
    fica como evolução.
  - B) Inferir as noites a partir da descricao. Não recomendo: a seção 3 proíbe
    ler a descrição, e o formato de entrada é fixo.

  Minha recomendação: A, porque é a única opção dentro do escopo.

  Pode seguir com A? Depois disso, fecho o D-008, subo a versão para 2.1 e
  proponho a task nova com os ajustes de código dos casos 2, 3 e 6.

✻ Crunched for 20s · done 4:43 PM

❯ pode seguir com A                                                             

  Ran 2 shell commands (ctrl+o to expand)

⏺ Bash(uv run python - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)
  ⎿   specs/001-motor-reembolso/DECISIONS.md | 32 +++++++++++++++++++++++++
      specs/001-motor-reembolso/spec.md      | 44 +++++++++++++++++++++----
     ---------
      2 files changed, 59 insertions(+), 17 deletions(-)
  ⎿  Updated specs/001-motor-reembolso/DECISIONS.md (+32 -0)
      10  
      11  ---
      12  
      13 +## D-008 — Revisão adversarial da spec final: spec 2.0 → 2.1 · 
         +`2026-10-04`                                                   
      14 +                                                               
      15 +**Gatilho:** rodada do `spec-adversary` sobre a spec 2.0 depois
         + de concluída a implementação (até T-034, commit `240afe5`): 7 
         +problemas, nenhum bloqueante (3 importantes, 4 menores). Decidi
         +dos um a um pelo responsável.                                  
      16 +                                                               
      17 +**O que mudou na spec** (numeração = numeração da revisão):    
      18 +                                                               
      19 +| # | Ponto | De (2.0) | Para (2.1) | Onde |                   
      20 +|---|---|---|---|---|                                          
      21 +| 1 | Mesmo gasto em categorias diferentes; gasto dividido entr
         +e categorias (importante) | não mencionado | **mantido**: a cat
         +egoria segue na chave da duplicata; as duas brechas registradas
         + como risco aceito | seção 10 |                                
      22 +| 2 | Terça de Carnaval sem cotação (importante) | janela D-1 a
         + D-3: despesa legítima na terça de Carnaval → `cambio_indisponi
         +vel` | janela **D-1 a D-4**; justificativa da AMB-024 corrigida
         + | seção 4 (motivos), RN-015, AMB-024, seção 7, seção 10 |     
      23 +| 3 | `descricao` nula ou de outro tipo (importante) | tipo "te
         +xto" na seção 4 × RN-002 omissa | nunca valida: ausente, nula o
         +u de qualquer tipo, a despesa segue | seção 4, RN-002, seção 7 
         +|                                                              
      24 +| 4 | RN-011 × RN-004 com `valor_considerado` 0,00 (menor) | fó
         +rmula única admitia `aprovado` e `recusado` ao mesmo tempo | du
         +as partes: recusa nas etapas 1 a 7 → `recusado` com o motivo da
         + etapa; fórmula só na etapa 9 | RN-011 |                       
      25 +| 5 | O que é "data válida" (menor) | não definido na spec (só 
         +no plan, DT-003/DT-014) | dígitos ASCII, 0001-01-01 a 9999-12-3
         +1, data existente; D+1 e D-n fora do calendário não existem | R
         +N-002, RN-010, RN-015 |                                        
      26 +| 6 | Argumento de CLI repetido, desconhecido ou sobrando (meno
         +r) | indefinido; o repetido valia a última ocorrência, em silên
         +cio | erro de uso, nunca "a última ocorrência" | seção 4 (Inter
         +face), AMB-031, seção 7 |                                      
      27 +| 7 | Hospedagem de várias noites e a viagem a partir de D+2 (m
         +enor) | só a consequência no valor registrada | consequência na
         + viagem registrada junto à decisão provisória da AMB-005 | seçã
         +o 10 |                                                         
      28 +                                                               
      29 +**Por quê:**                                                   
      30 +- **Pontos 2 e 6:** recusavam uma despesa legítima sem caminho 
         +de reembolso (2) ou executavam em silêncio uma linha de comando
         + ambígua, contra a AMB-031 (6).                                
      31 +- **Pontos 3, 4 e 5:** a spec admitia duas leituras. Em todos, 
         +a decisão é a leitura que o código já seguia.                  
      32 +- **Pontos 1 e 7:** o resultado literal era o desejado, mas o r
         +isco não estava registrado. No ponto 1, tirar a categoria da ch
         +ave recusaria gastos legítimos coincidentes e ainda não pegaria
         + a divisão do gasto.                                           
      33 +                                                               
      34 +**O que isso invalidou:**                                      
      35 +- **Código:** `DIAS_ANTERIORES_ACEITOS_NA_COTACAO` (3 → 4) em `
         +cambio.py`, com o `plan.md` (seção 4, DT-014); `cli.py` passa a
         + recusar argumento repetido. Os pontos 1, 3, 4, 5 e 7 não mudam
         + código.                                                       
      36 +- **Testes:** em `test_rn015_moeda_e_cambio.py`, os testes de D
         +-3/D-4 passam a D-4/D-5. Seção 7: "Cotação exatamente 3 dias an
         +tes" e "Cotação 4 dias antes" renomeados para 4 e 5 dias; novos
         + "Terça de Carnaval", "Descrição nula ou de outro tipo" e "Argu
         +mento repetido" (100 → 103 casos).                             
      37 +- **Envelope:** nenhum valor da seção 9 muda. O câmbio não tem 
         +lacuna além de fim de semana, nenhum par de despesas difere só 
         +na categoria e a única despesa de 24/07 é de `coworking`.      
      38 +                                                               
      39 +**Tasks afetadas:** nova task para os pontos 2, 3 e 6 (código, 
         +testes, plan, Cobertura).                                      
      40 +                                                               
      41 +**Custo:** 2 arquivos nesta mudança (`spec.md`, `DECISIONS.md`)
         +; 7 pontos decididos na mesma sessão.                          
      42 +                                                               
      43 +---                                                            
      44 +                                                               
      45  ## D-007 — Política de Reembolso v4 (envelope do Dia 2): spec 1
          .9 → 2.0 · `2026-10-02`
      46  
      47  **Gatilho:** mudança de requisito do RH, "Política de Reembolso
           v4" (`exemplos/envelope/00-ENVELOPE-LACRADO.md`), com os arqui
          vos `politica-v4.json`, `cambio.json`, `despesas-envelope.json`
           e `despesas-envelope-cc-desconhecido.json`. Três itens:
  ⎿  Updated specs/001-motor-reembolso/spec.md (+2 -2)
      1  # Spec — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 2.0 · **Status:** aprovada para planejamento (Políti
        -ca v4) · **Última alteração:** 2026-10-02 (ver `DECISIONS.md` D-
        -001 a D-007)                                                    
      3 +**Versão:** 2.1 · **Status:** aprovada para planejamento (Políti
        +ca v4) · **Última alteração:** 2026-10-04 (ver `DECISIONS.md` D-
        +001 a D-008)                                                    
      4  
      5  > **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ
         . Nenhuma linha
      6  > aqui pode citar linguagem, biblioteca, classe, função ou estru
         tura de pasta.
     ...
      809  
      810  ### Decisões provisórias
      811  
      812 -- **Datas de entrada e saída de hospedagem.** A solução corret
          -a para AMB-005 exige mudar o formato de entrada. Decisão provi
          -sória: um lançamento = uma diária. Consequência conhecida: uma
          - hospedagem de 480,00 "2 diarias" recebe 250,00 no `padrao` me
          -smo se forem de fato duas diárias (no envelope, e-007 "3 noite
          -s" recebe 400,00 de 1.200,00).                                
      812 +- **Datas de entrada e saída de hospedagem.** A solução corret
          +a para AMB-005 exige mudar o formato de entrada. Decisão provi
          +sória: um lançamento = uma diária. Consequência conhecida: uma
          + hospedagem de 480,00 "2 diarias" recebe 250,00 no `padrao` me
          +smo se forem de fato duas diárias (no envelope, e-007 "3 noite
          +s" recebe 400,00 de 1.200,00). Segunda consequência: só D e D+
          +1 ficam em viagem (RN-010), então os dias seguintes da mesma e
          +stadia perdem a ampliação dos limites. Hospedagem "3 noites" c
          +om nota em 14/07 e alimentação de 80,00 em 16/07, no `padrao`:
          + 16/07 fora de viagem, limite 60,00, `parcial` com 60,00 (em v
          +iagem seria `aprovado` com 80,00). No envelope, a e-007 deixa 
          +24/07 fora de viagem, mas a única despesa desse dia (e-009, `c
          +oworking`) não amplia, e nenhum valor da seção 9 muda.        
      813  - **Ids repetidos na entrada.** A política não trata. Decisão 
           provisória: despesas com o mesmo `id` são avaliadas normalment
           e, cada uma pelo seu conteúdo; a saída repete o id.
      814  - **`competencia` inconsistente com `inicio`/`fim`.** Decisão 
           provisória: o período vale por `inicio` e `fim`; `competencia`
            só é repetida na saída.
      815  - **Estorno vinculado a uma despesa.** Se o formato um dia tro
           uxer referência à despesa original, AMB-013 deve ser revista.

  Ran 1 shell command (ctrl+o to expand)

⏺ Os 7 casos estão registrados.

  O que mudou:
  - Spec, agora 2.1: caso 7 na seção 10, cabeçalho da versão atualizado. A seção
    7 foi de 100 para 103 casos de borda.
  - DECISIONS.md: nova entrada D-008, com a tabela dos 7 pontos e o que cada um
    invalidou. Conferi o envelope: nenhum valor da seção 9 muda.

  Estado dos testes: uv run pytest -q dá 992 passando e 1 falhando. A falha é a
  esperada: test_rastreabilidade.py não acha teste para os casos de borda novos
  e renomeados da seção 7. Ela só some quando as tasks abaixo forem
  implementadas.

  Tasks propostas (ainda não escrevi no tasks.md)

  T-035 — Janela da cotação D-4 e descricao de qualquer tipo (tipo: regra, passa
  pelo revisor-de-task)
  - Atende: RN-015, AMB-024, RN-002, D-008 (pontos 2 e 3).
  - Código: DIAS_ANTERIORES_ACEITOS_NA_COTACAO vai de 3 para 4 em cambio.py. No
    plan.md, a seção 4 e a DT-014 passam a dizer "D-4".
  - Aceite:
    - test_rn015_moeda_e_cambio.py: com câmbio só de 13/07, USD em 17/07 usa
      13/07 (D-4) e USD em 18/07 dá cambio_indisponivel (D-5). EUR na terça de
      Carnaval (09/02/2027) usa 05/02, valor_considerado 60,00.
    - test_casos_de_borda.py: linhas renomeadas para "Cotação exatamente 4 dias
      antes" e "Cotação 5 dias antes"; linhas novas "Terça de Carnaval" e
      "Descrição nula ou de outro tipo" (null, 17, {}, todas aprovado com
      45,00).

  T-036 — Argumento de CLI repetido é erro de uso (tipo: estrutura, sem revisão)
  - Atende: seção 4 (Interface), AMB-031, D-008 (ponto 6).
  - Código: cli.py recusa a segunda ocorrência de --input, --politica, --cambio
    ou --output.
  - Aceite:
    - test_cli.py: argumento repetido no meio e no fim da linha, inclusive com o
      mesmo arquivo nas duas vezes, dá código diferente de 0, saída não criada
      e saída que já existia sem alteração. Argumento desconhecido e posicional
      sobrando também (já funcionam hoje; o teste só fixa o comportamento).
    - test_casos_de_borda.py: linha "Argumento repetido".
  - Inclui a tabela de Cobertura atualizada: seção 7 com 103 casos.

  Dois pontos para você decidir antes de seguir

  1. Nova rodada do spec-adversary. O CLAUDE.md pede uma rodada depois de
     mudança relevante na spec, e a janela D-4 e a RN-011 reescrita contam como
     relevantes. Recomendo rodar antes de escrever as tasks.
  2. Ordem dos commits. O hook pre-commit roda o pytest. Por isso, o commit
     docs(spec) com docs(decisions) sozinho é bloqueado pela rastreabilidade. O
     mecanismo PENDENTES, que permitia isso, foi removido na T-034. Vejo dois
     caminhos:
     - (a) Um commit docs(spec) com spec, DECISIONS.md e tasks.md só depois que
       T-035 e T-036 passarem, e em seguida os commits das tasks.
     - (b) Trazer de volta temporariamente o PENDENTES para os 5 casos, como na
       D-007, e remover de novo na T-036.

     Eu iria de (a): dá menos código provisório, e a ordem da história continua
     spec → tasks → código.

  Posso rodar o spec-adversary na 2.1 e escrever as duas tasks no tasks.md?

✻ Sautéed for 54s · done 4:46 PM

❯ vamos decidir os pontos primeiros                                             

⏺ Então um de cada vez.

  Ponto 1 — Nova rodada do spec-adversary na 2.1

  Contexto: o CLAUDE.md pede uma nova rodada "depois de qualquer mudança
  relevante na spec". A D-008 mudou três coisas que alteram comportamento:
  - a janela do câmbio foi para D-4, o que muda resultados;
  - a RN-011 foi reescrita em duas partes;
  - a interface da CLI ganhou mais um erro de uso.

  Os outros quatro pontos só documentaram o que o código já fazia ou registraram
  riscos aceitos.

  Opções:
  - A) Rodar agora, antes de escrever as tasks. Se a rodada achar algo, por
    exemplo uma interação da janela D-4 com outro caso de borda, a correção vai
    para a spec antes de as tasks serem escritas, e as tasks já nascem certas.
    Custa uma rodada a mais, de uns 5 minutos.
  - B) Escrever as tasks primeiro e rodar a revisão depois, antes do commit. O
    resultado é o mesmo se a revisão não achar nada. Se achar, as tasks precisam
    ser reescritas.
  - C) Não rodar, por entender que a mudança é pequena e localizada. Não
    recomendo: a regra do CLAUDE.md existe justamente para mudanças que parecem
    pequenas, e a D-007 teve uma segunda rodada pelo mesmo motivo.

  Minha recomendação: A. Quero que a rodada olhe só o que mudou na D-008 (o diff
  da 2.0 para a 2.1), sem repetir os 7 pontos que você já decidiu.

  Qual das três?

✻ Churned for 7s · done 4:58 PM

❯ pode ser A                                                                    

⏺ spec-adversary(Revisão adversarial da spec 2.1)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ Comecei o spec-adversary na 2.1, olhando só o diff da D-008. Enquanto ele
  roda, vamos ao segundo ponto.

  Ponto 2 — Ordem dos commits com o pre-commit bloqueando

  O problema: o hook pre-commit roda o pytest. A spec 2.1 tem 5 casos de borda
  sem teste: 2 renomeados e 3 novos. Por isso o test_rastreabilidade.py falha, e
  qualquer commit fica bloqueado até as tasks estarem implementadas. Isso vale
  também para o commit docs(spec).

  Opções:
  - A) Implementar primeiro e commitar na ordem da história. T-035 e T-036 são
    implementadas na árvore de trabalho. Com tudo verde, saem três commits em
    sequência:
    a. docs(spec), com spec, DECISIONS.md e tasks.md;
    b. feat(T-035);
    c. feat(T-036).

    Para o primeiro commit passar no hook, faço o stage só dos docs e uso git 
    stash --keep-index para tirar o código do caminho. Não precisa de código
    provisório, e o git log fica spec → tasks → código.
    O cuidado é que, no commit 1, os testes rodam sem as mudanças de código.
    Então esse commit só passa se os testes novos estiverem em
    feat(T-035)/feat(T-036), e não no commit de docs. Isso é inviável: sem os
    testes, a rastreabilidade falha. Na prática, A só funciona se o commit 1 
    levar junto as linhas novas de test_casos_de_borda.py, o que mistura doc e 
    teste.
  - B) Trazer de volta o PENDENTES temporariamente (DT-016, como na D-007):
    a. docs(spec) com spec, DECISIONS.md e tasks.md, mais uma linha em
       test_rastreabilidade.py com os 5 nomes pendentes. O hook passa.
    b. feat(T-035) remove do PENDENTES os casos dela.
    c. feat(T-036) remove os últimos e apaga o PENDENTES de novo.

    O código provisório é pequeno e tem dono, a T-036. A ordem spec → tasks →
    código fica limpa, e cada commit passa no hook sem truque.
  - C) Um commit docs(spec) com SEM_EXPORT/--no-verify. Não recomendo: pular o
    hook é exatamente o que o projeto quer evitar.

  Corrigindo o que eu disse antes: recomendei A, mas ao detalhar vi que ela não
  fecha sem misturar teste no commit de docs. Minha recomendação agora é B. Ela
  reaproveita um mecanismo que já foi usado e documentado, e cada commit fica
  coerente e verde.

  Qual das duas?

✻ Cooked for 19s · done 5:01 PM

❯ beleza, pode fazer conforme a melhor recomendacao                             

  Ran 1 shell command (ctrl+o to expand)

⏺ Vou com a opção B, usando o PENDENTES temporário. Já conferi como ele estava
  antes da T-034 (e0d9bfa): trago de volta o mecanismo com dono por task e com a
  checagem de "pendência que já tem teste faz a suíte falhar", e só para os 5
  casos da D-008.

  Ainda não escrevi nada no tasks.md nem no test_rastreabilidade.py. No ponto 1
  combinamos rodar o spec-adversary antes das tasks, e ele ainda está rodando.
  Quando ele terminar, eu trago o resultado. Se não houver nada a decidir, sigo
  com:
  1. as tasks T-035 e T-036 no tasks.md;
  2. o PENDENTES com os 5 casos, com T-035 e T-036 como donas;
  3. a suíte rodando verde, e então paro para você aprovar o commit docs(spec).

✻ Cogitated for 9s · done 5:04 PM

› Message from spec-adversary
  Resumo: encontrei 4 problemas, nenhum BLOQUEANTE e nenhum IMPORTANTE (4
  MENORES). A redação das 7 decisões da D-008 está coerente com o resto da spec.
  Os resultados da seção 9 continuam valendo.

  Não consegui rodar `git diff` porque não tenho shell. Fiz a comparação pela
  tabela da D-008 e li a spec 2.1 inteira
  (`/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md`).

  **O que conferi e está certo**
  - **Janela de 4 dias:** não sobrou nenhum "3 dias" nem "D-3" com sentido de
  regra. A seção 4 (motivo `cambio_indisponivel`: "nos 4 dias anteriores"), a
  RN-015, a AMB-024 (diz "até a spec 2.0 eram 3 dias"), a seção 7 e a seção 10
  estão alinhadas.
  - **Aceite da RN-015 "USD em 2026-07-12 (nenhuma cotação de 08/07 a 12/07)":**
  corresponde exatamente à janela D a D-4.
  - **Casos da seção 7 sobre a janela:** "Cotação 5 dias antes" (18/07 com
  câmbio só em 13/07), "Sem cotação e fora do período" (15/04) e "Data
  intermediária sem a moeda" continuam corretos com 4 dias.
  - **Calendário de 2027:** 05/02/2027 é sexta e 09/02/2027 é a terça de
  Carnaval (Páscoa em 28/03/2027). A conta 10,00 × 6,00 = 60,00 bate.
  - **Contagem de casos:** a seção 7 tem 103 linhas, como a D-008 declara.
  - **Seção 9:** `cambio.json` só tem lacunas de fim de semana (18-19/07 e
  25-26/07). A e-004 (sábado, 18/07) usa 17/07 = D-1 em qualquer janela ≥ 1, e a
  e-006 (GBP) não tem cotação em nenhuma data. O exemplo é todo em BRL. Nenhum
  par de despesas do envelope difere só na categoria, e a única despesa de 24/07
  é a e-009 (`coworking`). Nenhum valor das três tabelas muda.
  - **RN-011 em duas partes:** está coerente com a seção 4 (tabela de motivos,
  `motivo` nulo só em `aprovado`), com a RN-004 e com a seção 8. A AMB-021
  garante que nenhuma despesa chega à etapa 9 com limite 0, então não aparece
  status incompatível.
  - **Fim do calendário (RN-010 e RN-015):** é coerente com a definição de data
  da RN-002, que exclui o ano 0000.
  - **Seção 10:** o exemplo novo da consequência na viagem (hospedagem "3
  noites", alimentação de 80,00 em 16/07 → 60,00) e a nota da e-007 em 24/07
  batem.

  ---

  ### 1. "Data existente no calendário gregoriano" admite duas leituras antes de
  1582 — MENOR — ambiguidade

  - **Referência:** RN-002 (definição de data válida), que vale também para
  RN-005, RN-010, RN-015 e RN-016 (`vigencia`, chaves de `taxas`).
  - **Exemplo:** uma despesa com `"data": "1582-10-10"` ou `"1500-02-29"`, ou um
  câmbio com a chave `"1582-10-10"`. Pelo gregoriano estendido para trás,
  `1582-10-10` existe e `1500-02-29` não (1500 não é bissexto). Pelo gregoriano
  histórico, os dias 05 a 14/10/1582 não existem, e nenhuma data antes de
  15/10/1582 é gregoriana. A resposta muda `entrada_invalida` × avaliação
  normal, erro de arquivo × câmbio válido, e também a contagem de D-n e D+1
  quando ela atravessa outubro de 1582. Nenhum dado realista chega lá. Mesmo
  assim, a spec fixou de propósito os extremos 0001-01-01 e 9999-12-31, e isso
  só faz sentido no gregoriano estendido.
  - **Pergunta:** o "calendário gregoriano" da RN-002 é o estendido para trás
  (todas as datas de 0001-01-01 a 9999-12-31, com a regra de bissexto
  gregoriana), ou o histórico (com o salto de 1582)? A spec deve dizer isso?

  ### 2. Erro de uso: formas de argumento que a spec não classifica — MENOR —
  lacuna

  - **Referência:** seção 4 (Interface), AMB-031, seção 7 (casos "Erro de uso" e
  "Argumento repetido").
  - **Exemplo:** a spec diz que argumento "desconhecido" é erro de uso, mas não
  define o que é "conhecido". Linhas que ela não classifica:
    - (a) `calcular --input=e.json --politica p.json --cambio c.json --output
  s.json` (forma com `=`);
    - (b) `calcular --inp e.json ...` (prefixo abreviado de `--input`);
    - (c) `calcular --help` ou `-h` (ajuda é erro de uso com código diferente de
  0, ou sucesso?);
    - (d) `--` antes dos argumentos, ou as opções antes do subcomando (`--input
  e.json calcular ...`).

    Nenhuma delas muda valores. A garantia da D-008 ("uma linha que mostra duas
  políticas não é executada") se mantém em qualquer leitura, porque repetir pela
  forma abreviada ou com `=` ou é repetição ou é argumento desconhecido. O que
  muda é o código de saída e se a saída é gravada. Além disso, a seção 7 não tem
  caso para "argumento desconhecido" nem para "argumento sobrando", só para o
  repetido. Pelo critério da seção 9, essas duas partes da regra nova ficam sem
  teste exigido.
  - **Pergunta:** as formas `--opção=valor` e `--prefixo` abreviado contam como
  argumento conhecido ou desconhecido? `--help`/`-h` é erro de uso (código
  diferente de 0) ou outro comportamento? Argumento desconhecido e argumento
  sobrando devem ganhar casos próprios na seção 7?

  ### 3. "`descricao` nunca validada" × erros de forma dentro da `descricao` —
  MENOR — ambiguidade de redação

  - **Referência:** seção 4 (tabela de entrada, linha `descricao`: "nunca
  validada: ausente, nula ou de qualquer tipo, a despesa segue"), RN-002 (tópico
  sobre `descricao`), seção 4 sobre escapes, RN-013.
  - **Exemplo:** uma despesa válida com `"descricao": "Almoço \uD800"`. Pela
  seção 4 e pela RN-002 (escape que não forma caractere, "em qualquer chave ou
  valor"), o arquivo inteiro é erro de arquivo e não há saída. Lida
  isoladamente, a linha da tabela ("nunca validada… a despesa segue") permite
  entender que a despesa segue. O mesmo vale para `"descricao": {"x": 1, "x":
  2}`: a descrição é "ignorada", mas gera o aviso `descricao.x` (RN-013). O
  resultado literal é o mesmo de qualquer campo extra, e a RN-002 limita o
  efeito a "nunca torna a despesa inválida". A tensão está só no texto da
  tabela.
  - **Pergunta:** "nunca validada" vale só para as validações de despesa da
  RN-002 (tipo, presença), mantendo para a `descricao` os erros de forma do
  arquivo e os avisos de chave repetida? A tabela da seção 4 deve dizer isso?

  ### 4. Exemplos novos sem todos os dados que fixam o resultado — MENOR —
  ambiguidade

  - **Referência:** aceite da RN-015 e caso "Terça de Carnaval" na seção 7;
  risco "Mesmo gasto lançado em categorias diferentes" na seção 10.
  - **Exemplos:**
    - (a) "câmbio com EUR 6,00 em 05/02/2027, sem 08/02 e 09/02" não diz que
  também não há 06/02 e 07/02 (nem outras datas). O D-4 declarado só acontece se
  o arquivo tiver apenas 05/02 dentro da janela. A coluna de resultado também
  não dá status nem reembolso: 60,00 contra o limite de 60,00 → `aprovado` com
  60,00, que dá para deduzir mas não está escrito. Os casos vizinhos ("Cotação
  exatamente 4 dias antes" e "Data intermediária sem a moeda") dizem "câmbio só
  com".
    - (b) Na seção 10, "jantar de 390,00 = 90,00 em `alimentacao` + 300,00 em
  `representacao` no `CC-COMERCIAL` recebe 390,00, contra 300,00 ou 90,00 se
  lançado numa categoria só" pressupõe que a data está fora de viagem e que os
  itens têm nota. Em viagem, lançado só como alimentação, o jantar receberia
  135,00, não 90,00; sem nota, os 300,00 seriam `nota_fiscal_ausente`.
  - **Pergunta:** o caso do Carnaval deve dizer "câmbio só com 05/02/2027" e
  trazer o status esperado? O exemplo do risco deve declarar "fora de viagem,
  com nota"? Ou essas omissões são aceitáveis como estão?

  ---

  1. **Decidir antes da implementação:** nenhum. Não há BLOQUEANTE.
  2. **Pode ser decidido depois:** 1, 2, 3, 4.

  Arquivos lidos:
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md`,
  `/Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md`
  (D-008 e D-007),
  `/Users/rafaeltxm/repo/sdd-desafio/exemplos/envelope/cambio.json`,
  `/Users/rafaeltxm/repo/sdd-desafio/exemplos/envelope/despesas-envelope.json`,
  `/Users/rafaeltxm/repo/sdd-desafio/exemplos/envelope/despesas-envelope-cc-desc
  onhecido.json`.

  Ran 1 shell command (ctrl+o to expand)

⏺ Agent "Revisão adversarial da spec 2.1" finished · 2m 38s

⏺ A rodada do spec-adversary na 2.1 achou 4 problemas, todos menores, sem
  bloqueante nem importante. A redação das 7 decisões da D-008 está coerente com
  o resto da spec: não sobrou nenhum "3 dias"/"D-3", a seção 7 tem 103 casos,
  as datas do Carnaval de 2027 estão certas e nenhum valor da seção 9 muda.

  Como antes, vamos um a um.

  R2-1 — "Calendário gregoriano" antes de 1582

  O problema: "data existente no calendário gregoriano" tem duas leituras.
  - Gregoriano estendido para trás: 1582-10-10 existe e 1500-02-29 não existe.
  - Gregoriano histórico: os dias 05 a 14/10/1582 não existem, e nenhuma data
    antes de 15/10/1582 é gregoriana.

  A diferença muda se uma data é válida ou não, mas só para datas sem nenhum
  realismo. O próprio agente nota que os extremos 0001-01-01 e 9999-12-31 que a
  spec fixou só fazem sentido no estendido.

  O que o código faz: usa o estendido, porque date.fromisoformat é o gregoriano
  proléptico.

  Opções:
  - A) Escrever "gregoriano estendido para trás (proléptico)" na definição da
    RN-002. Muda uma palavra, o código fica igual.
  - B) Deixar como está. A leitura histórica entra em conflito com os extremos
    já fixados.

  Minha recomendação: A. Custa uma palavra e acaba com a leitura dupla.

  Para você já ir vendo o próximo: no caso R2-2, sobre formas de argumento da
  CLI, testei agora como a CLI se comporta. --input=x funciona. O prefixo
  abreviado --inp também é aceito, porque o argparse aceita abreviações por
  padrão. --help sai com código 0 sem gravar saída. -- e opções antes do
  subcomando dão erro de uso.

  O ponto que importa: com a abreviação ativa, --input a --inp b é uma repetição
  disfarçada. A T-036 precisa pegar esse caso também, ou então desligar as
  abreviações. Detalho isso quando chegarmos lá.

  Pode seguir com A no R2-1?
✻ Brewed for 3m 2s · done 5:04 PM

❯ pode seguir com A                                                             

⏺ Bash(cd /Users/rafaeltxm/repo/sdd-desafio && uv run python - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)
  ⎿  Updated specs/001-motor-reembolso/spec.md (+1 -1)
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
      181  - `descricao` nunca torna a despesa inválida: ausente, nula, t
           exto ou de qualquer outro tipo (número, booleano, lista, objet
           o), ela é ignorada, como um campo extra (seção 3: o sistema nã
           o lê a descrição).
      182 -- **Data válida `AAAA-MM-DD`**, nesta regra e em toda a spec (
          -RN-016, `vigencia` e chaves de `taxas`): texto de exatamente 1
          -0 caracteres, com 4, 2 e 2 dígitos ASCII (`0` a `9`) separados
          - por `-`, que forma uma data existente no calendário gregorian
          -o entre 0001-01-01 e 9999-12-31. Dígitos de outras escritas (`
          -"٢٠٢٦-٠٧-٠٣"`), ano `0000`, `"2026-7-3"`, `"20260703"` e `"202
          -6-02-30"` não são datas válidas. Diferente da normalização da 
          -seção 5, que aceita algarismos de qualquer escrita em texto li
          -vre.                                                          
      182 +- **Data válida `AAAA-MM-DD`**, nesta regra e em toda a spec (
          +RN-016, `vigencia` e chaves de `taxas`): texto de exatamente 1
          +0 caracteres, com 4, 2 e 2 dígitos ASCII (`0` a `9`) separados
          + por `-`, que forma uma data existente no calendário gregorian
          +o estendido para trás (proléptico: a regra de bissexto gregori
          +ana vale para todos os anos, sem o salto de outubro de 1582), 
          +entre 0001-01-01 e 9999-12-31. `1582-10-10` é válida; `1500-02
          +-29` não é. Dígitos de outras escritas (`"٢٠٢٦-٠٧-٠٣"`), ano `
          +0000`, `"2026-7-3"`, `"20260703"` e `"2026-02-30"` não são dat
          +as válidas. Diferente da normalização da seção 5, que aceita a
          +lgarismos de qualquer escrita em texto livre.                 
      183  - Campos extras, no arquivo ou nas despesas, são ignorados.
      184  **Origem:** necessidade operacional (a política não trata entr
           ada malformada); pontos 7 e 9 de D-001; AMB-018; D-005; AMB-02
           0 e AMB-025 (D-007).
      185  **Aceite:** despesa sem `tem_nota_fiscal` com `valor` 33.333 →
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
           00 (o teto vale para o número recebido). `"moeda": "eur"` → `e
           ntrada_invalida`, `moeda` `eur` na saída. `"moeda": 978` → `en
           trada_invalida`, `moeda` nula na saída. `"centro_custo": 17` →
            erro de arquivo.

⏺ RN-002 atualizada: agora diz "gregoriano estendido para trás (proléptico)" e
  traz os exemplos 1582-10-10 (válida) e 1500-02-29 (inválida).

  R2-2 — O que é argumento "conhecido" na CLI

  O problema: a 2.1 diz que argumento desconhecido é erro de uso, mas não define
  o que é conhecido. Além disso, a seção 7 só tem caso para o argumento
  repetido. O desconhecido e o sobrando ficam sem teste exigido.

  O que a CLI faz hoje (testei com o envelope):

  ┌────────────────────────────────┬────────────────────────────────────────┐
  │             Forma              │                  Hoje                  │
  ├────────────────────────────────┼────────────────────────────────────────┤
  │ --input=e.json                 │ aceito, código 0                       │
  ├────────────────────────────────┼────────────────────────────────────────┤
  │ --inp e.json (prefixo          │ aceito, código 0                       │
  │ abreviado)                     │                                        │
  ├────────────────────────────────┼────────────────────────────────────────┤
  │ calcular --help / -h           │ mostra a ajuda, código 0, não grava    │
  │                                │ saída                                  │
  ├────────────────────────────────┼────────────────────────────────────────┤
  │ -- antes dos argumentos        │ erro de uso, código 2                  │
  ├────────────────────────────────┼────────────────────────────────────────┤
  │ opção antes do subcomando      │ erro de uso, código 2                  │
  └────────────────────────────────┴────────────────────────────────────────┘

  Minha proposta, em quatro partes:
  - (a) --opção=valor é a mesma opção. É a forma padrão de CLI, não traz risco e
    deixa o código como está.
  - (b) O prefixo abreviado vira argumento desconhecido, ou seja, erro de uso.
    As abreviações aceitas dependem de quais opções existem: se um dia surgir
    --input-extra, --inp deixa de funcionar. Elas também permitem repetição
    disfarçada (--input a --inp b). No código, basta allow_abbrev=False no
    cli.py.
  - (c) --help/-h mostra a ajuda e sai com código 0, sem ler arquivo e sem 
    gravar saída. Ajuda não é erro, e não executa cálculo, então não fere a
    AMB-031.
  - (d) Novos casos na seção 7:
    - "Argumento desconhecido": --verbose e --inp;
    - "Argumento sobrando": posicional extra.

    Os dois esperam erro de uso, código diferente de 0 e saída não criada nem
    alterada. A seção 7 passa de 103 para 105 casos.

  Tudo isso entra na T-036, que continua sendo task de estrutura.

  Alternativa: manter as abreviações e só detectar a repetição pelo destino do
  argumento. Funciona, mas deixa o "conhecido" dependente de quais opções
  existem.

  Pode seguir com (a) a (d)?

✻ Sautéed for 14s · done 5:08 PM

❯ pode seguir com a e d                                                         

⏺ Antes de escrever, preciso confirmar uma coisa. "a e d" quer dizer só os itens
  (a) e (d), ou todos, de (a) a (d)? Se for só (a) e (d), ficam três coisas em
  aberto:

  - (b) Prefixo abreviado (--inp): fica aceito como hoje? Nesse caso, a T-036
    precisa detectar a repetição disfarçada (--input a --inp b) pelo destino do
    argumento, e --inp sai do caso "Argumento desconhecido".
  - (c) --help/-h: sem decisão, a spec não diz o que acontece. Hoje mostra a
    ajuda e sai com código 0.

  Qual das duas leituras?

✻ Brewed for 5s · done 5:13 PM

❯ pode seguir conforme falando, de a d                                          

⏺ Bash(uv run python - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)
  ⎿  9:| `despesas[].descricao` | qualquer | descrição livre; não usada em
     regras e nunca validada: ausente, nula ou de qualquer tipo, a despesa
     segue (RN-002) | não |
     … +8 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/spec.md (+5 -1)
      44  
      45  - Sucesso: grava o arquivo de saída e termina com código 0.
      46  - Erro de arquivo (RN-002 para a entrada, RN-016 para a polític
          a e o câmbio), inclusive quando o arquivo de saída não pode ser
           gravado: não cria nem altera o arquivo de saída (se já existia
          , permanece como estava), escreve uma mensagem de erro e termin
          a com código diferente de 0.
      47 -- Erro de uso (subcomando diferente de `calcular`; `--input`, `
         ---politica`, `--cambio` ou `--output` ausentes; qualquer um del
         -es repetido, mesmo com o mesmo arquivo; argumento desconhecido 
         -ou sobrando): mesmo comportamento do erro de arquivo. Nunca val
         -e "a última ocorrência": uma linha de comando que mostra duas p
         -olíticas não é executada. Os cinco argumentos são sempre obriga
         -tórios, inclusive quando todas as despesas são em reais (AMB-03
         -1).                                                            
      47 +- Erro de uso (subcomando diferente de `calcular`; `--input`, `
         +--politica`, `--cambio` ou `--output` ausentes; qualquer um del
         +es repetido, mesmo com o mesmo arquivo; argumento desconhecido 
         +ou sobrando): mesmo comportamento do erro de arquivo. Nunca val
         +e "a última ocorrência": uma linha de comando que mostra duas p
         +olíticas não é executada.                                      
      48 +- Argumento conhecido é exatamente `--input`, `--politica`, `--
         +cambio` ou `--output`, escrito por inteiro, seguido do valor co
         +mo argumento separado ou na forma `--opção=valor` (as duas form
         +as são a mesma opção, inclusive para a repetição). Prefixo abre
         +viado (`--inp`), `--` e opção antes do subcomando são argumento
         +s desconhecidos.                                               
      49 +- Ajuda (`-h` ou `--help`, antes ou depois do subcomando): most
         +ra o uso e termina com código 0, sem ler nenhum arquivo e sem c
         +riar nem alterar o arquivo de saída. Os cinco argumentos são se
         +mpre obrigatórios, inclusive quando todas as despesas são em re
         +ais (AMB-031).                                                 
      50  
      51  ### Entrada
      52  
     ...
      693  | Moeda em minúsculas | `"moeda": "eur"` | `entrada_invalida`;
            `moeda` `eur` na saída | RN-002 |
      694  | Moeda de tipo errado | `"moeda": 978` | `entrada_invalida`; 
           `moeda` nula na saída | RN-002 |
      695  | Argumento repetido | `calcular --input e.json --politica pol
           itica-v4.json --politica outra.json --cambio c.json --output s
           .json` (e a mesma linha com o `--politica` repetido no fim, ou
            com o mesmo arquivo nas duas vezes) | erro de uso; código dif
           erente de 0; saída não criada nem alterada | seção 4, AMB-031 
           |
      696 +| Argumento desconhecido | linha completa com `--verbose` a ma
          +is; e a linha com `--inp e.json` no lugar de `--input e.json` 
          +| erro de uso; código diferente de 0; saída não criada nem alt
          +erada | seção 4 |                                             
      697 +| Argumento sobrando | linha completa com um argumento posicio
          +nal a mais (`extra`) | erro de uso; código diferente de 0; saí
          +da não criada nem alterada | seção 4 |                        
      698  | Descrição nula ou de outro tipo | alimentação 45,00 em 03/07
            sem nota, com `"descricao": null`; a mesma com `"descricao": 
           17` e com `"descricao": {}` | as três `aprovado` com 45,00 (ca
           da uma num arquivo próprio) | RN-002 |
      699  | Sem cotação e fora do período | 10,00 USD em 15/04, período 
           de julho | `cambio_indisponivel` (etapa 2 antes da 4) | RN-015
            |
      700  | Conversão arredondada uma vez | 16,8649 EUR em 14/07, alimen
           tação sem nota | 100,008857 → `valor_considerado` 100,01 → `no
           ta_fiscal_ausente` | RN-003, RN-008 |

⏺ Spec atualizada para o R2-2:
  - a Interface agora define o que é argumento conhecido, que --opção=valor é a
    mesma opção, que prefixo abreviado, -- e opção antes do subcomando são
    desconhecidos, e que --help sai com código 0 sem tocar em arquivo;
  - a seção 7 ganhou os casos "Argumento desconhecido" e "Argumento sobrando" e
    agora tem 105 casos.

  O código muda no cli.py: allow_abbrev=False e detecção de repetição. Isso fica
  na T-036.

  R2-3 — "descricao nunca validada" × erros de forma do arquivo

  O problema: a linha da tabela da seção 4 diz "nunca validada: ausente, nula ou
  de qualquer tipo, a despesa segue". Lida sozinha, ela pode sugerir duas
  coisas que não valem:
  - que "descricao": "Almoço \uD800" não causa erro. Mas um escape inválido em
    qualquer valor é erro de arquivo, pela seção 4 e pela RN-002;
  - que "descricao": {"x": 1, "x": 2} não gera aviso. Mas gera o aviso de chave
    repetida descricao.x (RN-013).

  O resultado literal está definido, porque o tópico da RN-002 limita o efeito a
  "nunca torna a despesa inválida". O problema é só de redação na tabela. O
  código já segue a leitura correta: a leitura do arquivo verifica a forma de
  tudo antes de qualquer validação de despesa.

  Proposta: reescrever a célula assim:

  ▎ descrição livre; não usada em regras. Nunca torna a despesa inválida: 
  ▎ ausente, nula ou de qualquer tipo, a despesa segue (RN-002). Como todo o 
  ▎ arquivo, continua sujeita aos erros de forma (UTF-8, JSON, escapes) e ao 
  ▎ aviso de chave repetida (RN-013).

  A mesma ressalva entra no tópico da RN-002. O código não muda.

  Pode seguir?

✻ Baked for 15s · done 5:14 PM

❯ sim                                                                           

⏺ Bash(uv run python - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)
  ⎿  81:Todo texto da entrada, chave ou valor, vale pelo seu conteúdo **dep
     ois de decodificados os escapes** do arquivo (`"2026\u002d07\u002d03"`
      é a data `2026-07-03`), e "caractere" é o caractere Unicode (um emoji
     … +47 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/spec.md (+2 -2)
      64  | `despesas[].id` | texto | identificador da despesa | sim (`en
          trada_invalida`) |
      65  | `despesas[].data` | data `AAAA-MM-DD` | data em que a despesa
           ocorreu | sim (`entrada_invalida`) |
      66  | `despesas[].categoria` | texto | categoria da despesa | sim (
          `entrada_invalida`) |
      67 -| `despesas[].descricao` | qualquer | descrição livre; não usad
         -a em regras e nunca validada: ausente, nula ou de qualquer tipo
         -, a despesa segue (RN-002) | não |                             
      67 +| `despesas[].descricao` | qualquer | descrição livre; não usad
         +a em regras. Nunca torna a despesa inválida: ausente, nula ou d
         +e qualquer tipo, a despesa segue (RN-002). Como todo o arquivo,
         + continua sujeita aos erros de forma (UTF-8, JSON, escapes) e a
         +o aviso de chave repetida (RN-013) | não |                     
      68  | `despesas[].fornecedor` | texto | estabelecimento; usado na d
          etecção de duplicatas | sim (`entrada_invalida`) |
      69  | `despesas[].valor` | número | valor na moeda da despesa | sim
           (`entrada_invalida`) |
      70  | `despesas[].moeda` | texto ou nulo | código ISO 4217 da moeda
           do `valor`: exatamente 3 letras maiúsculas de `A` a `Z` (RN-01
          5) | não; ausente ou nulo → `BRL`; outro tipo ou outro formato 
          → `entrada_invalida` |
     ...
      180  - Uma despesa recusada por `entrada_invalida` tem `valor_consi
           derado`, `taxa_cambio`, `data_cotacao`, `em_viagem` e `limite_
           diario` nulos, e não entra nos totais.
      181  - Espaço em branco, nesta regra e em toda a spec, é o caracter
           e com a propriedade White_Space do Unicode (espaço comum, tabu
           lação, quebra de linha, espaço não separável e semelhantes). T
           abulação, quebra de linha (LF, CR) e NEL têm essa propriedade 
           e são espaço em branco. Espaço de largura zero, BOM e caracter
           es de controle sem essa propriedade (como U+001C a U+001F) não
            são espaço em branco: um `id` ou `nome` feito só deles é text
           o válido.
      182  - `id` (da despesa e do colaborador) e `nome` não passam pela 
           normalização da seção 5: só são repetidos, nunca comparados. U
           m `id` `"-"` é válido.
      183 -- `descricao` nunca torna a despesa inválida: ausente, nula, t
          -exto ou de qualquer outro tipo (número, booleano, lista, objet
          -o), ela é ignorada, como um campo extra (seção 3: o sistema nã
          -o lê a descrição).                                            
      183 +- `descricao` nunca torna a despesa inválida: ausente, nula, t
          +exto ou de qualquer outro tipo (número, booleano, lista, objet
          +o), ela é ignorada, como um campo extra (seção 3: o sistema nã
          +o lê a descrição). Como todo o arquivo, a `descricao` continua
          + sujeita aos erros de forma da leitura (UTF-8, JSON, escapes: 
          +`"Almoço \uD800"` é erro de arquivo) e ao aviso de chave repet
          +ida (RN-013: `{"x": 1, "x": 2}` gera o aviso de `descricao.x`)
          +.                                                             
      184  - **Data válida `AAAA-MM-DD`**, nesta regra e em toda a spec (
           RN-016, `vigencia` e chaves de `taxas`): texto de exatamente 1
           0 caracteres, com 4, 2 e 2 dígitos ASCII (`0` a `9`) separados
            por `-`, que forma uma data existente no calendário gregorian
           o estendido para trás (proléptico: a regra de bissexto gregori
           ana vale para todos os anos, sem o salto de outubro de 1582), 
           entre 0001-01-01 e 9999-12-31. `1582-10-10` é válida; `1500-02
           -29` não é. Dígitos de outras escritas (`"٢٠٢٦-٠٧-٠٣"`), ano `
           0000`, `"2026-7-3"`, `"20260703"` e `"2026-02-30"` não são dat
           as válidas. Diferente da normalização da seção 5, que aceita a
           lgarismos de qualquer escrita em texto livre.
      185  - Campos extras, no arquivo ou nas despesas, são ignorados.
      186  **Origem:** necessidade operacional (a política não trata entr
           ada malformada); pontos 7 e 9 de D-001; AMB-018; D-005; AMB-02
           0 e AMB-025 (D-007).

⏺ Pronto: a célula da tabela da seção 4 e o tópico da RN-002 agora têm a
  ressalva sobre os erros de forma e o aviso de chave repetida, com os dois
  exemplos. O código não muda.

  R2-4 — Exemplos novos sem todos os dados que fixam o resultado

  O problema: dois exemplos que escrevi na 2.1 dependem de premissas que não
  estão escritas.

  (a) Caso "Terça de Carnaval" (seção 7 e aceite da RN-015):
  - O texto diz "câmbio com EUR 6,00 em 05/02/2027, sem 08/02 e 09/02", mas não
    exclui 06/02 e 07/02. Se o arquivo tivesse um sábado com EUR, a busca
    pararia antes. Os casos vizinhos dizem "câmbio só com".
  - O resultado não diz o status nem o valor reembolsado: 60,00 contra o limite
    de 60,00 dá aprovado com 60,00.

  (b) Risco "Mesmo gasto em categorias diferentes" (seção 10): a conta "390,00
  contra 300,00 ou 90,00" só vale fora de viagem e com nota. Em viagem, lançado
  só como alimentação, o jantar receberia 135,00. Sem nota, os 300,00 seriam
  recusados por nota_fiscal_ausente.

  Proposta:
  - (a) O caso passa a dizer "câmbio só com 05/02/2027 (EUR 6,00)", e o
    resultado completo fica "usa 05/02 (D-4); data_cotacao 2027-02-05;
    valor_considerado 60,00; aprovado com 60,00". O mesmo "só com" vai para o
    aceite da RN-015.
  - (b) O exemplo declara "fora de viagem, todas com nota". O exemplo "Casa
    Trindade" também ganha "com nota".

  Só muda a redação, e o resultado dos exemplos fica fixado.

  Pode seguir? Com isso fecho a R2. Depois:
  1. atualizo a D-008 com esta segunda rodada, com as decisões R2-1 a R2-4 e a
     contagem de 105 casos;
  2. escrevo T-035 e T-036 no tasks.md;
  3. ponho o PENDENTES com os 7 casos pendentes e rodo a suíte.

✻ Crunched for 14s · done 5:15 PM

❯ sim                                                                           

⏺ Bash(uv run python - <<'EOF'
      p="specs/001-motor-reembolso/spec.md"…)
  ⎿  # Tasks — Motor de Cálculo de Reembolso

     **Versão:** 2.0 · **Baseado em:** spec 2.0, plan 2.0
     … +50 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/DECISIONS.md (+13 -4)
      26  | 6 | Argumento de CLI repetido, desconhecido ou sobrando (meno
          r) | indefinido; o repetido valia a última ocorrência, em silên
          cio | erro de uso, nunca "a última ocorrência" | seção 4 (Inter
          face), AMB-031, seção 7 |
      27  | 7 | Hospedagem de várias noites e a viagem a partir de D+2 (m
          enor) | só a consequência no valor registrada | consequência na
           viagem registrada junto à decisão provisória da AMB-005 | seçã
          o 10 |
      28  
      29 +**Segunda rodada do `spec-adversary` (sobre a redação da 2.1, s
         +ó o diff da D-008):** 4 problemas, todos menores. A janela D-4 
         +ficou coerente em toda a spec, o calendário de 2027 confere e a
         + seção 9 não muda. Decididos um a um pelo responsável:         
      30 +                                                               
      31 +| # | Ponto | Decisão | Onde |                                 
      32 +|---|---|---|---|                                              
      33 +| R2-1 | "Calendário gregoriano" antes de 1582 | gregoriano est
         +endido para trás (proléptico); `1582-10-10` válida, `1500-02-29
         +` inválida | RN-002 |                                          
      34 +| R2-2 | O que é argumento "conhecido" na CLI | as quatro opçõe
         +s por inteiro, separadas ou `--opção=valor` (mesma opção, inclu
         +sive para repetição); prefixo abreviado, `--` e opção antes do 
         +subcomando são desconhecidos; `-h`/`--help` mostra o uso com có
         +digo 0, sem ler nem gravar arquivo; casos novos "Argumento desc
         +onhecido" e "Argumento sobrando" | seção 4 (Interface), seção 7
         + |                                                             
      35 +| R2-3 | "`descricao` nunca validada" × erros de forma | nunca 
         +torna a despesa inválida, mas segue sujeita aos erros de forma 
         +do arquivo e ao aviso de chave repetida | seção 4, RN-002 |    
      36 +| R2-4 | Exemplos sem todos os dados | caso "Terça de Carnaval"
         + com "câmbio só com" e status; risco da categoria com "fora de 
         +viagem, todas com nota" | RN-015, seção 7, seção 10 |          
      37 +                                                               
      38  **Por quê:**
      39  - **Pontos 2 e 6:** recusavam uma despesa legítima sem caminho 
          de reembolso (2) ou executavam em silêncio uma linha de comando
           ambígua, contra a AMB-031 (6).
      40  - **Pontos 3, 4 e 5:** a spec admitia duas leituras. Em todos, 
          a decisão é a leitura que o código já seguia.
      41  - **Pontos 1 e 7:** o resultado literal era o desejado, mas o r
          isco não estava registrado. No ponto 1, tirar a categoria da ch
          ave recusaria gastos legítimos coincidentes e ainda não pegaria
           a divisão do gasto.
      42  
      43  **O que isso invalidou:**
      35 -- **Código:** `DIAS_ANTERIORES_ACEITOS_NA_COTACAO` (3 → 4) em `
         -cambio.py`, com o `plan.md` (seção 4, DT-014); `cli.py` passa a
         - recusar argumento repetido. Os pontos 1, 3, 4, 5 e 7 não mudam
         - código.                                                       
      36 -- **Testes:** em `test_rn015_moeda_e_cambio.py`, os testes de D
         --3/D-4 passam a D-4/D-5. Seção 7: "Cotação exatamente 3 dias an
         -tes" e "Cotação 4 dias antes" renomeados para 4 e 5 dias; novos
         - "Terça de Carnaval", "Descrição nula ou de outro tipo" e "Argu
         -mento repetido" (100 → 103 casos).                             
      44 +- **Código:** `DIAS_ANTERIORES_ACEITOS_NA_COTACAO` (3 → 4) em `
         +cambio.py`, com o `plan.md` (seção 4, DT-014); `cli.py` passa a
         + recusar argumento repetido (também na forma `--opção=valor`) e
         + prefixo abreviado (R2-2). Os pontos 1, 3, 4, 5, 7, R2-1, R2-3 
         +e R2-4 não mudam código.                                       
      45 +- **Testes:** em `test_rn015_moeda_e_cambio.py`, os testes de D
         +-3/D-4 passam a D-4/D-5. Seção 7: "Cotação exatamente 3 dias an
         +tes" e "Cotação 4 dias antes" renomeados para 4 e 5 dias; novos
         + "Terça de Carnaval", "Descrição nula ou de outro tipo", "Argum
         +ento repetido", "Argumento desconhecido" e "Argumento sobrando"
         + (100 → 105 casos). Até as tasks, os 7 casos sem teste ficam em
         + `PENDENTES` de `test_rastreabilidade.py` (DT-016, reaberto), c
         +om a task dona.                                                
      46  - **Envelope:** nenhum valor da seção 9 muda. O câmbio não tem 
          lacuna além de fim de semana, nenhum par de despesas difere só 
          na categoria e a única despesa de 24/07 é de `coworking`.
      47  
      39 -**Tasks afetadas:** nova task para os pontos 2, 3 e 6 (código, 
         -testes, plan, Cobertura).                                      
      48 +**Tasks afetadas:** T-035 (pontos 2 e 3, regra) e T-036 (ponto 
         +6 e R2-2, estrutura; apaga de novo o `PENDENTES`).             
      49  
      41 -**Custo:** 2 arquivos nesta mudança (`spec.md`, `DECISIONS.md`)
         -; 7 pontos decididos na mesma sessão.                          
      50 +**Custo:** 4 arquivos nesta mudança (`spec.md`, `DECISIONS.md`,
         + `tasks.md`, `tests/test_rastreabilidade.py`); 11 pontos decidi
         +dos na mesma sessão, em duas rodadas.                          
      51  
      52  ---
      53  
  ⎿  Updated specs/001-motor-reembolso/spec.md (+3 -3)
      305  - A moeda não muda nenhuma outra regra: por si só não caracter
           iza viagem, nem impede que uma hospedagem com nota a comprove 
           (AMB-023); todos os limites e o mínimo da nota são comparados 
           em reais.
      306  
      307  **Origem:** Política v4, item B; AMB-024, AMB-025, AMB-026 (D-
           007).
      308 -**Aceite** (`cambio.json` do envelope): 22,00 EUR em 14/07 → t
          -axa 5,93, `data_cotacao` 2026-07-14, `valor_considerado` 130,4
          -6. 30,00 EUR em 18/07 (sábado) → taxa 5,96 de 17/07, `valor_co
          -nsiderado` 178,80. Sem `moeda` → `BRL`, taxa 1, `data_cotacao`
          - nula. `"moeda": null` → `BRL`. 55,00 GBP em 21/07 → `cambio_i
          -ndisponivel`, `valor_considerado` nulo, fora de `valor_solicit
          -ado`. USD em 2026-07-12 (nenhuma cotação de 08/07 a 12/07) → `
          -cambio_indisponivel`. Câmbio só com 13/07: USD em 17/07 → usa 
          -13/07 (D-4); USD em 18/07 → `cambio_indisponivel` (D-5). Câmbi
          -o com EUR em 05/02/2027 (sexta) e nada em 08/02 e 09/02 (Carna
          -val): EUR em 09/02 → usa 05/02 (D-4).                         
      308 +**Aceite** (`cambio.json` do envelope): 22,00 EUR em 14/07 → t
          +axa 5,93, `data_cotacao` 2026-07-14, `valor_considerado` 130,4
          +6. 30,00 EUR em 18/07 (sábado) → taxa 5,96 de 17/07, `valor_co
          +nsiderado` 178,80. Sem `moeda` → `BRL`, taxa 1, `data_cotacao`
          + nula. `"moeda": null` → `BRL`. 55,00 GBP em 21/07 → `cambio_i
          +ndisponivel`, `valor_considerado` nulo, fora de `valor_solicit
          +ado`. USD em 2026-07-12 (nenhuma cotação de 08/07 a 12/07) → `
          +cambio_indisponivel`. Câmbio só com 13/07: USD em 17/07 → usa 
          +13/07 (D-4); USD em 18/07 → `cambio_indisponivel` (D-5). Câmbi
          +o só com 05/02/2027 (sexta; segunda 08/02 e terça 09/02 de Car
          +naval sem cotação): EUR em 09/02 → usa 05/02 (D-4).           
      309  
      310  ### RN-016 — Arquivos de política e de câmbio
      311  
     ...
      688  | Moeda estrangeira em sábado | 30,00 EUR em 18/07 (sábado), a
           limentação com nota | taxa 5,96 de 17/07; `data_cotacao` 2026-
           07-17; `valor_considerado` 178,80 | RN-015 |
      689  | Cotação exatamente 4 dias antes | câmbio só com 13/07 (USD 5
           ,42); 10,00 USD em 17/07 | usa 13/07; `valor_considerado` 54,2
           0 | RN-015 |
      690  | Cotação 5 dias antes | câmbio só com 13/07; 10,00 USD em 18/
           07 | `cambio_indisponivel`; `valor_considerado` nulo; fora dos
            totais | RN-015 |
      691 -| Terça de Carnaval | câmbio com EUR 6,00 em 05/02/2027 (sexta
          -), sem 08/02 e 09/02; período de fevereiro de 2027; 10,00 EUR 
          -em 09/02, alimentação com nota | usa 05/02 (D-4); `data_cotaca
          -o` 2027-02-05; `valor_considerado` 60,00 | RN-015 |           
      691 +| Terça de Carnaval | câmbio só com 05/02/2027 (sexta; EUR 6,0
          +0); período de fevereiro de 2027; 10,00 EUR em 09/02 (terça), 
          +alimentação com nota | usa 05/02 (D-4); `data_cotacao` 2027-02
          +-05; `valor_considerado` 60,00; `aprovado` com 60,00 | RN-015 
          +|                                                             
      692  | Moeda sem cotação no arquivo | 55,00 GBP em 21/07 | `cambio_
           indisponivel`; `moeda` `GBP`; `taxa_cambio` e `valor_considera
           do` nulos; fora de `valor_solicitado` | RN-015 |
      693  | Moeda em minúsculas | `"moeda": "eur"` | `entrada_invalida`;
            `moeda` `eur` na saída | RN-002 |
      694  | Moeda de tipo errado | `"moeda": 978` | `entrada_invalida`; 
           `moeda` nula na saída | RN-002 |
     ...
      832  - **Centro de custo autodeclarado** (AMB-020): o `centro_custo
           ` vem da mesma entrada que o colaborador produz; declarar `CC-
           COMERCIAL` dá alimentação 90,00, transporte 150,00 e hospedage
           m 400,00, e escrever `"cc-adm"` em vez de `CC-ADM` troca a tab
           ela pelo `padrao` (mais generosa para o `CC-ADM`). Aceito pelo
            mesmo motivo do `tem_nota_fiscal`: o sistema não tem cadastro
            para conferir (seção 3); a saída expõe `colaborador.centro_cu
           sto` e `politica.tabela_aplicada` para a conferência humana.
      833  - **Viagem internacional sem hospedagem lançada** (AMB-023): q
           uem está no exterior sem hospedagem na entrada (hotel pago pel
           a empresa por outro meio, por exemplo) não tem os limites ampl
           iados; no envelope, o almoço de Lisboa e-002 recebe 90,00 de 1
           30,46. Aceito porque a moeda é declarada e, como prova de viag
           em, abriria brecha maior; mitigação definitiva é a indicação e
           xplícita de viagem (seção 3).
      834  - **Mesmo gasto lançado em moedas diferentes** (AMB-028): 10,0
           0 EUR e 59,30 BRL do mesmo gasto não são duplicatas e as duas 
           são pagas até o limite do dia. Aceito porque comparar em reais
            acoplaria a duplicata ao câmbio e só pegaria a conversão manu
           al que batesse ao centavo.
      835 -- **Mesmo gasto lançado em categorias diferentes** (AMB-010): 
          -a categoria normalizada faz parte da chave da duplicata (RN-00
          -7). O mesmo gasto relançado com outra categoria não é duplicat
          -a: "Casa Trindade" 85,00 em `alimentacao` e de novo em `repres
          -entacao` no mesmo dia são pagas as duas (170,00). Um gasto tam
          -bém pode ser dividido entre categorias: um jantar de 390,00 la
          -nçado como 90,00 em `alimentacao` e 300,00 em `representacao` 
          -no `CC-COMERCIAL` recebe 390,00, contra 300,00 ou 90,00 se lan
          -çado numa categoria só. Aceito porque a política só diz que du
          -plicatas "devem ser tratadas": tirar a categoria da chave recu
          -saria gastos legítimos que coincidem (corrida e entrega de com
          -ida do mesmo aplicativo, de mesmo valor, no mesmo dia) e ainda
          - não pegaria a divisão, que exigiria uma regra de soma por for
          -necedor e dia, inventada. A saída expõe `categoria` por item p
          -ara a conferência humana.                                     
      835 +- **Mesmo gasto lançado em categorias diferentes** (AMB-010): 
          +a categoria normalizada faz parte da chave da duplicata (RN-00
          +7). O mesmo gasto relançado com outra categoria não é duplicat
          +a: no `CC-COMERCIAL`, fora de viagem e todas com nota, "Casa T
          +rindade" 85,00 em `alimentacao` e de novo em `representacao` n
          +o mesmo dia são pagas as duas (170,00). Um gasto também pode s
          +er dividido entre categorias: nas mesmas condições, um jantar 
          +de 390,00 lançado como 90,00 em `alimentacao` e 300,00 em `rep
          +resentacao` recebe 390,00, contra 300,00 ou 90,00 se lançado n
          +uma categoria só. Aceito porque a política só diz que duplicat
          +as "devem ser tratadas": tirar a categoria da chave recusaria 
          +gastos legítimos que coincidem (corrida e entrega de comida do
          + mesmo aplicativo, de mesmo valor, no mesmo dia) e ainda não p
          +egaria a divisão, que exigiria uma regra de soma por fornecedo
          +r e dia, inventada. A saída expõe `categoria` por item para a 
          +conferência humana.                                           
      836  - **Política aplicada fora da vigência** (AMB-029): a execução
            aplica o arquivo de política recebido a todas as despesas, me
           smo às anteriores à `vigencia`. Aceito porque quem executa esc
           olhe a política explicitamente (`--politica`) e a saída regist
           ra `politica.versao` e `politica.vigencia`.
      837  - **Cotação de até 4 dias antes** (AMB-024): uma despesa em di
           a útil cuja cotação falta no arquivo (lacuna do arquivo, não f
           im de semana nem feriado) usa a de até 4 dias antes sem aviso,
            exceto pela `data_cotacao` na saída. Aceito porque o arquivo 
           declara publicar só em dias úteis e a diferença de taxa em 4 d
           ias é pequena; lacunas maiores viram `cambio_indisponivel`.
      838  - **Moeda autodeclarada como multiplicador** (AMB-025): a `moe
           da` vem da entrada; um gasto de 20,00 reais lançado como `"EUR
           "` vira 118,60 e recebe até o limite do dia (60,00 no `padrao`
           ). Aceito pelo mesmo motivo do `tem_nota_fiscal` e do `centro_
           custo`: o sistema não verifica a nota nem lê a descrição (seçã
           o 3); a saída expõe `moeda`, `taxa_cambio` e `valor_informado`
            para a conferência humana comparar com a nota.

  Ran 1 shell command (ctrl+o to expand)

⏺ Bash(uv run python - <<'EOF'
      p="tests/test_rastreabilidade.py"…)
  ⎿  397-
     398----
     399-
     … +3 lines (ctrl+o to expand)
  ⎿  Updated tests/test_rastreabilidade.py (+86 -2)
       3  Lê a `spec.md` e falha se alguma regra `RN-NNN` não aparecer no
           nome ou na
       4  docstring de um teste, ou se algum valor da coluna "Caso" da se
          ção 7 não for
       5  `id` de um `pytest.param` em `test_casos_de_borda.py`.
       6 +                                                               
       7 +Durante a Fase 6 (D-008), uma regra ou caso sem teste só é acei
         +to se estiver em                                               
       8 +`PENDENTES`, com a task dona; a pendência que já tem teste ou q
         +ue não está                                                    
       9 +mais na spec faz a suíte falhar (DT-016).                      
      10  """
      11  
      12  import ast
     ...
      15  
      16  TESTES = Path(__file__).parent
      17  SPEC = TESTES.parent / "specs" / "001-motor-reembolso" / "spec.
          md"
      18 +TASKS = SPEC.with_name("tasks.md")                             
      19 +                                                               
      20 +PENDENTES: dict[str, str] = {  # some quando a Fase 6 terminar 
         +(DT-016, D-008)                                                
      21 +    "Cotação exatamente 4 dias antes": "T-035",                
      22 +    "Cotação 5 dias antes": "T-035",                           
      23 +    "Terça de Carnaval": "T-035",                              
      24 +    "Descrição nula ou de outro tipo": "T-035",                
      25 +    "Argumento repetido": "T-036",                             
      26 +    "Argumento desconhecido": "T-036",                         
      27 +    "Argumento sobrando": "T-036",                             
      28 +}                                                              
      29 +PRIMEIRA_TASK_DA_FASE_6, ULTIMA_TASK_DA_FASE_6 = 35, 36        
      30  
      31  
      32  def _regras_da_spec() -> set[str]:
     ...
       76      return ids
       77  
       78  
       79 +def _tasks_existentes() -> set[str]:                          
       80 +    return set(                                               
       81 +        re.findall(                                           
       82 +            r"^- \[[ x]\] \*\*(T-\d{3})\*\*", TASKS.read_text(
          +encoding="utf-8"), re.M                                       
       83 +        )                                                     
       84 +    )                                                         
       85 +                                                              
       86 +                                                              
       87 +def _pendencias_invalidas(                                    
     … 73 more lines (ctrl+o to expand)

⏺ Bash(uv run python - <<'EOF'
      p="specs/001-motor-reembolso/tasks.md"…)
  ⎿  ......................................................................
     .. [ 93%]
     .............................................................
     … +7 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+30 -2)
      1  # Tasks — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 2.0 · **Baseado em:** spec 2.0, plan 2.0            
      3 +**Versão:** 2.1 · **Baseado em:** spec 2.1, plan 2.0 (a T-035 le
        +va o plan a 2.1)                                                
      4  
      5  > Cada task é pequena o bastante para virar **um commit**. Se vo
         cê não consegue
      6  > descrever o critério de aceite como "o teste X passa", a task 
         está grande demais.
     ...
      16  - **Atende:** as `RN-`/`AMB-` da spec (e as `DT-` do plano) que
           a task implementa.
      17  - **Depende de:** tasks que precisam estar `[x]` antes.
      18  - **Aceite:** os testes que precisam passar. Arquivos em `tests
          /`; nomes conforme `plan.md` seção 6.
      19 -- **Casos de borda:** linhas da tabela da seção 7 da spec que a
         - task cobre, cada uma um caso de `tests/test_casos_de_borda.py`
         - com `id` igual ao texto da coluna "Caso". As 100 linhas (63 da
         - 1.x e 37 da 2.0) estão distribuídas entre as tasks; nenhuma fi
         -ca sem dono.                                                   
      19 +- **Casos de borda:** linhas da tabela da seção 7 da spec que a
         + task cobre, cada uma um caso de `tests/test_casos_de_borda.py`
         + com `id` igual ao texto da coluna "Caso". As 105 linhas (63 da
         + 1.x, 37 da 2.0 e 5 novas da 2.1; duas da 2.0 renomeadas na 2.1
         +) estão distribuídas entre as tasks; nenhuma fica sem dono.    
      20  
      21  O esperado de todo teste é calculado à mão a partir da spec, nu
          nca copiado da saída do programa.
      22  
     ...
      397  
      398  ---
      399  
      400 +## Fase 6 — Revisão adversarial da spec final (spec 2.1, D-008
          +)                                                             
      401 +                                                              
      402 +Tasks das decisões da D-008 que mudam código ou exigem teste n
          +ovo. Os demais pontos da D-008 só mudaram texto da spec. Os 7 
          +casos novos ou renomeados da seção 7 ficam em `PENDENTES` de `
          +tests/test_rastreabilidade.py` (DT-016, reaberto para esta fas
          +e, donos T-035 e T-036). Cada task tira as suas pendências no 
          +mesmo commit, e a última apaga o `PENDENTES` de novo.         
      403 +                                                              
      404 +- [ ] **T-035** — Janela da cotação D-1 a D-4 e `descricao` de
          + qualquer tipo: `DIAS_ANTERIORES_ACEITOS_NA_COTACAO` de 3 para
          + 4 em `cambio.py`; `plan.md` (seção 4, DT-014, DT-016 reaberto
          +) com "D-4"; testes da janela e da `descricao`.               
      405 +  - **Tipo:** regra                                           
      406 +  - **Atende:** RN-015, AMB-024, RN-002 (`descricao`), D-008 (
          +pontos 2 e 3)                                                 
      407 +  - **Depende de:** T-034                                     
      408 +  - **Aceite:**                                               
      409 +    - `tests/test_rn015_moeda_e_cambio.py`: com câmbio só com 
          +13/07, USD em 17/07 → usa 13/07 (D-4) e USD em 18/07 → `cambio
          +_indisponivel` (D-5); com câmbio só com 05/02/2027 (EUR 6,00),
          + 10,00 EUR em 09/02/2027 → `data_cotacao` 2027-02-05, `valor_c
          +onsiderado` 60,00. Os testes de D-3/D-4 da 2.0 passam a D-4/D-
          +5.                                                            
      410 +    - `tests/test_rn002_validacao_da_entrada.py`: `descricao` 
          +ausente, `null`, `17`, `true`, `[]` e `{}` → a despesa segue n
          +ormalmente; `"descricao": "Almoço \uD800"` → erro de arquivo. 
      411 +    - Nenhum valor da seção 9 muda (`test_exemplo.py` passa se
          +m alteração).                                                 
      412 +  - **Casos de borda:** Cotação exatamente 4 dias antes · Cota
          +ção 5 dias antes · Terça de Carnaval · Descrição nula ou de ou
          +tro tipo (substituem "Cotação exatamente 3 dias antes" e "Cota
          +ção 4 dias antes", cujos `id` saem de `test_casos_de_borda.py`
          +)                                                             
      413 +                                                              
      414 +- [ ] **T-036** — CLI: argumento repetido e prefixo abreviado 
          +são erro de uso; fim das pendências da Fase 6. `cli.py` com `a
          +llow_abbrev=False` e recusa da segunda ocorrência de `--input`
          +, `--politica`, `--cambio` ou `--output`, inclusive na forma `
          +--opção=valor`; `PENDENTES` e o código que o lê apagados de `t
          +est_rastreabilidade.py`; tabela de Cobertura com 105 casos.   
      415 +  - **Tipo:** estrutura                                       
      416 +  - **Atende:** seção 4 (Interface), AMB-031, D-008 (ponto 6, 
          +R2-2), DT-016                                                 
      417 +  - **Depende de:** T-035                                     
      418 +  - **Aceite:** `tests/test_cli.py`:                          
      419 +    - `--politica` repetido no meio e no fim da linha, com arq
          +uivos diferentes e com o mesmo arquivo, e `--input a --input=b
          +` → código diferente de 0, saída não criada e saída que já exi
          +stia sem alteração;                                           
      420 +    - `--inp`, `--verbose`, posicional sobrando, `--` antes do
          +s argumentos e opção antes do subcomando → idem;              
      421 +    - `--input=e.json` (forma com `=`) → sucesso, mesmo result
          +ado da forma separada;                                        
     … 9 more lines (ctrl+o to expand)

  Ran 1 shell command (ctrl+o to expand)

⏺ A R2 está fechada e tudo foi registrado. uv run pytest -q passa com 997 testes
  e uv run ruff check . não acusa nada.

  O que muda neste bloco (4 arquivos, nada commitado ainda):
  - spec.md 2.1: os 7 pontos da D-008 e as 4 decisões da segunda rodada (R2). A
    seção 7 vai de 100 para 105 casos.
  - DECISIONS.md: a D-008 tem as duas tabelas, uma para cada rodada do
    spec-adversary, e diz o que cada ponto invalidou.
  - tasks.md 2.1: nova Fase 6.
    - T-035 (regra): janela D-4 e descricao de qualquer tipo.
    - T-036 (estrutura): CLI com argumento repetido ou prefixo abreviado como
      erro de uso. Ela também apaga o PENDENTES.
  - test_rastreabilidade.py: voltou o PENDENTES estrito com os 7 casos (4 da
    T-035 e 3 da T-036). Os três testes da DT-016 foram adaptados para a Fase 6.

  Para fechar o bloco: este commit, docs(spec): D-008 ..., encerra um bloco,
  então o hook exige o export da sessão no mesmo commit. Rode:

  /export docs/sessions/53-revisao-adversarial-spec-final.md

  Quando o arquivo existir, faço um único commit com os 4 arquivos e o export.
  Depois paro e espero você para começar a T-035.

✻ Worked for 1m 14s · done 5:17 PM