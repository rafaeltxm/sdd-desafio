 ▐▛███▛█   Claude Code v2.1.287
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~/repo/sdd-desafio

  Opus 5.5 is now your default model and it draws down usage faster than Sonnet 5. Switch anytime with /model.

❯ /clear                                                                        

❯ segue para o plan.md                                                          

  Read 1 file, listed 3 directories, ran 2 shell commands (ctrl+o to expand)

⏺ Li spec 1.3, DECISIONS e tasks; agora confiro a skill /task e a última sessão
  para alinhar o plano às convenções já fixadas (uv, pytest, ruff).

  Searched for 1 pattern (ctrl+o to expand)

⏺ Stack já está fixada pelos hooks e pela skill (Python + uv + pytest + ruff).
  Escrevo o plan.md agora.

⏺ Write(specs/001-motor-reembolso/plan.md)
  ⎿  Added 161 lines, removed 31 lines
      1  # Plano Técnico — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.0 · **Baseado na spec:** 1.0                      
      3 +**Versão:** 1.0 · **Baseado na spec:** 1.3                      
      4  
      5  > Aqui mora o COMO. Este arquivo pode e deve falar de linguagem,
          biblioteca e
      6  > arquitetura. O que ele **não** pode é introduzir regra de negó
         cio nova — se
     ...
       12  
       13  | Escolha | O quê | Por quê | O que descartei e por quê |
       14  |---|---|---|---|
       15 -| Linguagem | | | |                                           
       16 -| Testes | | | |                                              
       17 -| Parsing/validação | | | |                                   
       18 -| Aritmética monetária | | | |                                
       15 +| Linguagem | Python ≥ 3.12, projeto gerenciado com `uv` (`pyp
          +roject.toml` + `uv.lock`) | `Decimal` e `datetime.date` na bib
          +lioteca padrão cobrem dinheiro e datas sem dependência; `uv` f
          +ixa a versão do Python (o do sistema é 3.9) e já é o que os ho
          +oks de `.githooks/` usam | Node/TypeScript: sem tipo decimal n
          +ativo, teria que trazer biblioteca para o ponto mais sensível 
          +do projeto |                                                  
       16 +| Testes | `pytest` | Testes como funções simples, `parametriz
          +e` para tabelas de casos (seção 7 da spec), `tmp_path` para a 
          +CLI | `unittest`: mais cerimônia por teste, sem ganho |       
       17 +| Lint | `ruff` (regras `E`, `F`, `I`, `B`, `UP`) | Já exigido
          + pelo `pre-commit`; um só binário para lint e ordenação de imp
          +orts | `flake8` + `isort`: duas ferramentas para o mesmo papel
          + |                                                            
       18 +| Parsing/validação | `simplejson` com `use_decimal=True` (lei
          +tura e escrita) + validação manual campo a campo | Lê `33.333`
          + direto como `Decimal("33.333")`, sem passar por `float`, e es
          +creve `Decimal` como número JSON exato. A validação precisa pr
          +oduzir **item `entrada_invalida`** por despesa, não exceção — 
          +regra fina demais para um validador de schema | `json` da bibl
          +ioteca padrão: lê com `parse_float=Decimal`, mas não escreve `
          +Decimal` como número — teria que converter para `float` na saí
          +da e `valor_informado` perderia dígitos além do 17º. `pydantic
          +`/`jsonschema`: rejeitam o documento inteiro ou exigem contorn
          +os para "erro vira item" e para copiar campos de tipo errado c
          +omo nulo |                                                    
       19 +| Aritmética monetária | `decimal.Decimal`, `quantize(Decimal(
          +"0.01"), ROUND_HALF_UP)` | Exato ao centavo; `ROUND_HALF_UP` d
          +o Python arredonda a metade **afastando do zero** (-0,005 → -0
          +,01), exatamente a RN-003 | `float`: `10.005` vira `10.00499…`
          + e arredonda para 10,00 — viola a RN-003 já no caso de aceite.
          + Centavos em `int`: exige arredondar na conversão de qualquer 
          +forma, e o número informado (33,333) não cabe em centavos |   
       20 +| CLI | `argparse` (biblioteca padrão) | Um subcomando, duas o
          +pções obrigatórias; erro de uso já sai com código 2 e mensagem
          + em stderr | `click`/`typer`: dependência a mais para uma inte
          +rface fixa e mínima |                                         
       21  
       20 -<A linha de aritmética monetária não é decoração. Ponto flutua
          -nte em dinheiro é                                             
       21 -a fonte de bug mais previsível deste projeto.>                
       22 -                                                              
       22  ## 2. Arquitetura
       23  
       25 -<Diagrama em blocos ou lista. Quais são as peças, o que cada u
          -ma faz, como                                                  
       26 -conversam. Uma tela, não uma tese.>                           
       27 -                                                              
       24  ```
       29 -entrada JSON → <...> → <...> → saída JSON                     
       25 +arquivo JSON ─▶ cli ─▶ entrada ─▶ motor ─▶ saida ─▶ cli ─▶ arq
          +uivo JSON                                                     
       26 +               (I/O)  (parse +    (regras,  (monta     (gravaç
          +ão                                                            
       27 +                       validação)  puro)     dicionário) atômi
          +ca)                                                           
       28 +                         │           │                        
       29 +                         └── normalizacao, politica, justifica
          +tiva ──┘                                                      
       30  ```
       31  
       32 -**Fronteiras:** <o que é núcleo de regra de negócio puro e o q
          -ue é I/O. Onde                                                
       33 -essa linha está desenhada determina o quanto o sistema vai res
          -istir a mudança                                               
       34 -de requisito.>                                                
       32 +| Módulo (`src/reembolso/`) | Responsabilidade | Faz I/O? |   
       33 +|---|---|---|                                                 
       34 +| `cli.py` | `argparse`, lê bytes do arquivo, chama o pipeline
          +, grava a saída de forma atômica, mapeia erros para mensagem +
          + código de saída | sim |                                      
       35 +| `entrada.py` | bytes → JSON (`Decimal`) → `Entrada`. Erros d
          +e arquivo da RN-002 viram `ErroDeArquivo`; despesa inválida vi
          +ra `DespesaInvalida` (etapa 1 da seção 8) | não |             
       36 +| `normalizacao.py` | `normalizar_texto()` — os 4 passos da se
          +ção 5 da spec | não |                                         
       37 +| `politica.py` | constantes da política (seção 4 deste plano)
          + | não |                                                      
       38 +| `motor.py` | etapas 2 a 9 da seção 8; recebe `Entrada`, devo
          +lve `Resultado` | não |                                       
       39 +| `justificativa.py` | frase em português para cada item (text
          +o não contratual) | não |                                     
       40 +| `saida.py` | `Resultado` → dicionário na ordem de campos da 
          +seção 4 da spec → texto JSON | não |                          
       41 +| `modelo.py` | dataclasses e enums compartilhados (seção 3) |
          + não |                                                        
       42  
       43 +**Fronteiras:** só `cli.py` toca disco, `sys.argv`, `stderr` e
          + código de saída. Todo o resto é função pura de dados para dad
          +os, testável sem arquivo. A regra de negócio fica concentrada 
          +em `motor.py` + `politica.py` + `normalizacao.py`; `entrada.py
          +` só aplica a RN-002 (forma da entrada). Uma mudança de políti
          +ca mexe em `politica.py`; uma mudança de regra mexe em `motor.
          +py`; uma mudança de formato de entrada mexe em `entrada.py`; u
          +ma mudança de formato de saída mexe em `saida.py`.            
       44 +                                                              
       45 +Comando final: `uv run reembolso calcular --input <entrada> --
          +output <saída>` (entry point `reembolso = "reembolso.cli:main"
          +` no `pyproject.toml`).                                       
       46 +                                                              
       47  ## 3. Modelo de dados
       48  
       38 -<Estruturas internas. Como uma despesa é representada, como um
          - resultado de                                                 
       39 -avaliação é representado, o que carrega a justificativa.>     
       49 +Todas as estruturas são `@dataclass(frozen=True)`; valores mon
          +etários são sempre `Decimal`.                                 
       50  
       51 +```python                                                     
       52 +class Status(StrEnum):   APROVADO, PARCIAL, RECUSADO          
       53 +class Motivo(StrEnum):   # na ordem das etapas da seção 8 da s
          +pec                                                           
       54 +    ENTRADA_INVALIDA, VALOR_INVALIDO, FORA_DO_PERIODO, CATEGOR
          +IA_FORA_DA_POLITICA,                                          
       55 +    NOTA_FISCAL_AUSENTE, DUPLICATA, LIMITE_DIARIO_EXCEDIDO    
       56 +                                                              
       57 +Colaborador(id: str, nome: str)                               
       58 +Periodo(inicio: date, fim: date, inicio_texto: str, fim_texto:
          + str, competencia: str | None)                                
       59 +                                                              
       60 +Despesa(                       # passou pela etapa 1 (validaçã
          +o)                                                            
       61 +    posicao: int,              # índice em `despesas` — ordem 
          +da entrada                                                    
       62 +    id: str, data: date, data_texto: str,                     
       63 +    categoria_texto: str,      # como veio                    
       64 +    categoria: str,            # normalizada (seção 5 da spec)
       65 +    fornecedor: str,           # normalizado                  
       66 +    valor_informado: Decimal,                                 
       67 +    tem_nota_fiscal: bool,                                    
       68 +)                                                             
       69 +DespesaInvalida(               # recusada na etapa 1          
       70 +    posicao: int,                                             
       71 +    id: str | None, data_texto: str | None,                   
       72 +    categoria_saida: str | None,   # normalizada se reconhecid
          +a; senão texto como veio; senão None                          
       73 +    valor_informado: Decimal | None,                          
       74 +)                                                             
       75 +Entrada(colaborador, periodo, despesas: list[Despesa | Despesa
          +Invalida])                                                    
       76 +                                                              
       77 +ItemResultado(                 # espelha `itens[]` da seção 4 
          +da spec, campo a campo                                        
       78 +    id, data, categoria, valor_informado, valor_considerado, v
          +alor_reembolsado,                                             
       79 +    status: Status, motivo: Motivo | None, em_viagem: bool | N
          +one,                                                          
       80 +    limite_diario: Decimal | None, justificativa: str,        
       81 +)                                                             
       82 +Totais(valor_solicitado, valor_reembolsado, valor_glosado)    
       83 +Resultado(colaborador, periodo, itens: list[ItemResultado], to
          +tais)                                                         
       84 +```                                                           
       85 +                                                              
       86 +A justificativa é gerada a partir dos campos contratuais do it
          +em já decidido (status, motivo, valores, limite, data), nunca 
          +o contrário: nenhuma decisão depende do texto.                
       87 +                                                              
       88  ## 4. Como a política é representada
       89  
       43 -<Os limites vivem onde? Constantes no código, arquivo de confi
          -guração, tabela?                                              
       44 -Esta decisão é a que mais barato ou mais caro vai custar se a 
          -política mudar.>                                              
       90 +Constantes em `politica.py`, um único módulo, com os valores *
          +*literais** da spec:                                          
       91  
       92 +```python                                                     
       93 +LIMITES_DIARIOS = {          # RN-009: (normal, em viagem)    
       94 +    "alimentacao":       LimiteDiario(normal=Decimal("60.00"),
          +  viagem=Decimal("90.00")),                                   
       95 +    "transporte_urbano": LimiteDiario(normal=Decimal("80.00"),
          +  viagem=Decimal("120.00")),                                  
       96 +    "hospedagem":        LimiteDiario(normal=Decimal("250.00")
          +, viagem=Decimal("250.00")),                                  
       97 +}                                                             
       98 +CATEGORIAS_RECONHECIDAS = frozenset(LIMITES_DIARIOS)          
          +# RN-006                                                      
       99 +VALOR_ACIMA_DO_QUAL_EXIGE_NOTA = Decimal("100.00")            
          +# RN-008 (estritamente maior)                                 
      100 +CATEGORIA_QUE_COMPROVA_VIAGEM = "hospedagem"                  
          +# RN-010                                                      
      101 +DIAS_EM_VIAGEM_APOS_HOSPEDAGEM = 1                            
          +# RN-010: D e D+1                                             
      102 +```                                                           
      103 +                                                              
      104 +Os limites em viagem ficam escritos por extenso (90,00 / 120,0
          +0 / 250,00), e não calculados como `normal × 1,5`: a tabela da
          + RN-009 é a fonte, e a hospedagem não amplia (AMB-006). Um tes
          +te confere `politica.py` contra a tabela da spec.             
      105 +                                                              
      106 +**Descartado:** arquivo de configuração (YAML/JSON) com a polí
          +tica. Não há requisito de trocar a política sem novo deploy; e
          +xigiria validar o próprio arquivo de política e testar combina
          +ções inválidas. Como a política já está isolada num módulo sem
          + lógica, migrar para configuração depois custa um leitor e um 
          +teste.                                                        
      107 +                                                              
      108  ## 5. Decisões técnicas
      109  
       48 -### DT-001 — <decisão>                                        
      110 +### DT-001 — Dinheiro em `Decimal` lido direto do texto JSON  
      111  
       50 -**Contexto:** <o que forçou a escolha>                        
       51 -**Decisão:** <o que foi decidido>                             
       52 -**Alternativa descartada:** <e por quê>                       
       53 -**Consequência:** <o que isso torna fácil e o que torna difíci
          -l>                                                            
      112 +**Contexto:** RN-003 exige arredondar a metade afastando do ze
          +ro e cálculos exatos ao centavo; `valor_informado` é o número 
          +recebido (33.333).                                            
      113 +**Decisão:** o JSON é lido com `simplejson.loads(..., use_deci
          +mal=True)`, então todo número com parte decimal chega como `De
          +cimal` construído do texto; inteiros são convertidos para `Dec
          +imal`. `valor_considerado = valor_informado.quantize(Decimal("
          +0.01"), ROUND_HALF_UP)`. Toda conta (saldo do limite, totais) 
          +é feita entre `Decimal` já quantizados, então soma e subtração
          + são exatas. A saída escreve `Decimal` como número JSON (`use_
          +decimal=True`).                                               
      114 +**Alternativa descartada:** `float` com arredondamento no fim 
          +(`round(10.005, 2) == 10.0`), e `json` padrão com conversão pa
          +ra `float` só na saída (perde dígitos de `valor_informado`).  
      115 +**Consequência:** fácil garantir a RN-003 e os totais da seção
          + 9 ao centavo. Exige cuidado para nunca misturar `float` (proi
          +bido em `motor.py`; um teste de propriedade verifica que nenhu
          +m campo monetário da saída é `float`). A forma escrita na saíd
          +a pode diferir da entrada (`72.50` → `72.5`, ou `45.00` → `45.
          +00`), o que a spec permite (seção 4: "como veio" é o valor num
          +érico).                                                       
      116  
       55 -### DT-002 — ...                                              
      117 +### DT-002 — Rejeitar o que não é JSON estrito                
      118  
      119 +**Contexto:** RN-002: arquivo que não é JSON válido é erro de 
          +arquivo. O parser do Python aceita `NaN`, `Infinity` e `-Infin
          +ity`, que não são JSON.                                       
      120 +**Decisão:** `parse_constant` levanta erro → `ErroDeArquivo`. 
          +Bytes decodificados como UTF-8 estrito (`utf-8-sig`, aceitando
          + BOM, que a RFC 8259 permite ignorar); falha de decodificação 
          +→ `ErroDeArquivo`.                                            
      121 +**Alternativa descartada:** aceitar `NaN` e tratar como "valor
          + não é número" na despesa: transformaria arquivo inválido em p
          +rocessamento normal.                                          
      122 +**Consequência:** `"valor": NaN` encerra a execução sem saída,
          + como qualquer JSON inválido.                                 
      123 +                                                              
      124 +### DT-003 — Validação de tipo sem as armadilhas do Python    
      125 +                                                              
      126 +**Contexto:** RN-002 exige `valor` número e `tem_nota_fiscal` 
          +booleano. Em Python, `True` é `int`; `date.fromisoformat` (3.1
          +1+) aceita `20260701` e outros formatos ISO; `strptime("%Y-%m-
          +%d")` aceita `2026-7-1`; `\d` casa dígitos não ASCII.         
      127 +**Decisão:**                                                  
      128 +- número = `Decimal` ou `int`, **e não** `bool`;              
      129 +- booleano = `type(x) is bool`;                               
      130 +- data = casa `^[0-9]{4}-[0-9]{2}-[0-9]{2}$` **e** `date.fromi
          +soformat` aceita (rejeita 2026-02-30);                        
      131 +- texto obrigatório = `str` com `strip()` não vazio (o `strip(
          +)` sem argumento remove todo espaço em branco Unicode, inclusi
          +ve o não separável).                                          
      132 +**Alternativa descartada:** `isinstance(x, (int, float))` e `f
          +romisoformat` sozinho — aceitariam `"valor": true` e `"data": 
          +"20260703"`.                                                  
      133 +**Consequência:** cada armadilha vira um caso de teste de `ent
          +rada.py`.                                                     
      134 +                                                              
      135 +### DT-004 — Normalização de texto com `unicodedata`          
      136 +                                                              
      137 +**Contexto:** seção 5 da spec, 4 passos, "qualquer que seja a 
          +forma como o caractere foi codificado".                       
      138 +**Decisão:** `strip()` → `casefold()` → `unicodedata.normalize
          +("NFD")` e remoção dos caracteres de categoria `Mn` (marcas co
          +mbinantes) → `re.sub(r"[\s\-_]+", "_", ...)`. O NFD decompõe t
          +anto `á` pré-composto (U+00E1) quanto `a` + acento combinante 
          +(U+0301) para a mesma sequência, cobrindo as duas codificações
          +.                                                             
      139 +**Alternativa descartada:** tabela manual de acentos (`á→a`, .
          +..): incompleta por construção; `NFKD`: também desfaz compatib
          +ilidades (ligaduras, larguras) que a spec não pede.           
      140 +**Consequência:** uma função pura, usada por RN-006 e RN-007, 
          +testada com os exemplos da seção 5 e os casos de borda de cate
          +goria e fornecedor.                                           
      141 +                                                              
      142 +### DT-005 — Pipeline em duas fases, espelhando a seção 8     
      143 +                                                              
      144 +**Contexto:** as etapas 1 a 6 decidem cada despesa isoladament
          +e; as etapas 7 a 9 dependem do conjunto (duplicatas, viagem, s
          +aldo do dia).                                                 
      145 +**Decisão:**                                                  
      146 +1. **Fase individual:** para cada despesa, na ordem, aplica um
          +a lista ordenada de verificações (`valor_invalido`, `fora_do_p
          +eriodo`, `categoria_fora_da_politica`, `nota_fiscal_ausente`);
          + a primeira recusa encerra. A ordem da lista é a ordem da seçã
          +o 8.                                                          
      147 +2. **Duplicatas:** agrupa as sobreviventes por `(data, categor
          +ia, fornecedor, valor_considerado)`; em cada grupo, a original
          + é a primeira com `tem_nota_fiscal`, ou a primeira por `posica
          +o`; as demais recebem `duplicata`.                            
      148 +3. **Viagem:** `dias_em_viagem` = `{D, D+1}` para cada hospeda
          +gem sobrevivente com nota. Calculado **antes** de qualquer lim
          +ite, então independe da ordem na entrada.                     
      149 +4. **Limite:** percorre as sobreviventes por `posicao`, com sa
          +ldo por `(data, categoria)`; reembolsado = `min(valor_consider
          +ado, saldo)`; status pela RN-011.                             
      150 +**Alternativa descartada:** uma passada única despesa a despes
          +a: a viagem de uma hospedagem que aparece depois da alimentaçã
          +o do mesmo dia não seria vista (caso de borda "Alimentação ant
          +es da hospedagem").                                           
      151 +**Consequência:** reordenar ou inserir uma etapa individual é 
          +mexer numa lista; cada fase é testável isoladamente.          
      152 +                                                              
      153 +### DT-006 — Gravação atômica da saída                        
      154 +                                                              
      155 +**Contexto:** em erro de arquivo, a saída não pode ser criada 
          +nem alterada, inclusive se a falha for na gravação (RN-002, se
          +ção 4).                                                       
      156 +**Decisão:** todo o processamento e a serialização acontecem e
          +m memória antes de tocar o disco. A gravação escreve num arqui
          +vo temporário no **mesmo diretório** da saída e faz `os.replac
          +e` para o nome final; em qualquer falha, remove o temporário. 
          +Pasta inexistente ou sem permissão falha na criação do temporá
          +rio, antes de qualquer alteração.                             
      157 +**Alternativa descartada:** `open(output, "w")` direto: trunca
          + o arquivo existente antes de escrever; uma falha no meio deix
          +a arquivo parcial.                                            
      158 +**Consequência:** o arquivo de saída ou fica como estava, ou é
          + substituído inteiro.                                         
      159 +                                                              
      160 +### DT-007 — Códigos de saída e mensagens                     
      161 +                                                              
      162 +**Contexto:** a spec exige só "código diferente de 0" e "mensa
          +gem de erro".                                                 
      163 +**Decisão:** `0` sucesso; `1` erro de arquivo (mensagem `erro:
          + <descrição>` em stderr); `2` erro de uso (padrão do `argparse
          +`). Nenhuma exceção não tratada chega ao usuário como stack tr
          +ace por um erro previsto na RN-002.                           
      164 +**Alternativa descartada:** um único código para tudo: perderi
          +a a distinção útil para scripts, sem custo para cumpri-la.    
      165 +**Consequência:** os testes de CLI conferem `!= 0` (contrato) 
          +e o código exato (este plano).                                
      166 +                                                              
      167 +### DT-008 — Serialização determinística                      
      168 +                                                              
      169 +**Contexto:** critério de aceite "a mesma entrada sempre produ
          +z a mesma saída".                                             
      170 +**Decisão:** itens na ordem de `posicao`; campos de cada objet
          +o na ordem da tabela da seção 4 da spec; `ensure_ascii=False`,
          + UTF-8, `indent=2`, quebra de linha final. Nenhuma decisão dep
          +ende de ordem de iteração de `set`; agrupamentos usam `dict` (
          +ordem de inserção).                                           
      171 +**Consequência:** saída idêntica byte a byte entre execuções; 
          +testável comparando duas execuções.                           
      172 +                                                              
      173 +### DT-009 — Formatação de valores na justificativa           
      174 +                                                              
      175 +**Contexto:** a justificativa é em português e não contratual 
          +(seção 4), mas o exemplo da spec usa `45,00` e `03/07`.       
      176 +**Decisão:** função própria em `justificativa.py` formata `Dec
          +imal` como `1.234,56` e datas como `DD/MM`, sem depender de `l
          +ocale` do sistema (que mudaria a saída entre máquinas e quebra
          +ria a DT-008).                                                
      177 +**Consequência:** os testes conferem que toda justificativa é 
          +texto não vazio; o conteúdo exato não é testado, para não tran
          +sformar texto livre em contrato.                              
      178 +                                                              
      179  ## 6. Estratégia de testes
      180  
       59 -- **Nível:** <unitário, integração, ponta a ponta — e a propor
          -ção entre eles>                                               
       60 -- **Cada `RN-NNN` da spec tem teste?** <como você garante isso
          ->                                                             
       61 -- **Casos de borda da seção 7 da spec:** <cobertos como>      
       62 -- **Nomenclatura:** <como o nome do teste remete ao requisito 
          -— isso é o que                                                
       63 -  fecha a rastreabilidade na correção>                        
      181 +- **Nível e proporção:**                                      
      182 +  - **Unitários (~70%)** — `normalizacao`, `entrada` (cada ite
          +m da RN-002 e cada armadilha da DT-003), `motor` (uma regra po
          +r arquivo), sem disco.                                        
      183 +  - **Integração (~20%)** — `entrada → motor → saida` com `exe
          +mplos/despesas-exemplo.json` contra a tabela da seção 9 da spe
          +c, transcrita à mão para o teste (nunca copiada da saída do pr
          +ograma), e totais 1.861,84 / 585,43 / 1.276,41.               
      184 +  - **Ponta a ponta (~10%)** — `cli.main([...])` com `tmp_path
          +`: código de saída, arquivo criado, arquivo preexistente intac
          +to em erro, erro de uso, pasta inexistente, determinismo byte 
          +a byte.                                                       
      185 +- **Cada `RN-NNN` da spec tem teste?** Um arquivo por regra (`
          +tests/test_rn001_um_resultado_por_despesa.py`, …, `test_rn012_
          +hospedagem_uma_diaria.py`), cobrindo pelo menos o **Aceite** d
          +a regra. `tests/test_rastreabilidade.py` lê a `spec.md`, extra
          +i todos os `RN-NNN` e falha se algum não aparecer no nome ou n
          +a docstring de pelo menos um teste.                           
      186 +- **Casos de borda da seção 7 da spec:** `tests/test_casos_de_
          +borda.py`, um teste parametrizado por linha da tabela, com `id
          +` igual ao texto da coluna "Caso". `test_rastreabilidade.py` t
          +ambém extrai a coluna "Caso" da seção 7 e falha se algum caso 
          +não tiver teste com esse `id` — caso novo na spec sem teste qu
          +ebra a suíte.                                                 
      187 +- **Nomenclatura:** `test_rnNNN_<comportamento>` com docstring
          + `"""RN-NNN / AMB-NNN: <o que a spec diz>"""`; o esperado de c
          +ada teste tem um comentário com a conta feita a partir da spec
          + (ex.: `# 72,50 + 38,00 > 60,00 → 60,00 e 0`). O nome remete à
          + regra; a docstring, à decisão.                               
      188 +- **Fixtures:** um construtor de entrada mínima válida em `tes
          +ts/conftest.py` (`entrada(despesas=[...])`, `despesa(**campos)
          +`), para cada teste declarar só o que importa ao caso.        
      189  
      190  ## 7. Riscos
      191  
      192  | Risco | Probabilidade | O que faço se acontecer |
      193  |---|---|---|
       69 -| | | |                                                       
      194 +| `float` entrar por acidente numa conta (ex.: literal `0.01`,
          + `round()`) | média | Teste de propriedade sobre a saída (nenh
          +um valor monetário é `float`); ruff + revisão no `revisor-de-t
          +ask`; constantes só como `Decimal("…")` |                     
      195 +| Implementação divergir da ordem da seção 8 (ex.: duplicata a
          +ntes da nota) | média | Casos de borda que só passam na ordem 
          +certa (relançamento com nota, duplicata de hospedagem com só u
          +ma nota, alimentação antes da hospedagem) |                   
      196 +| Valores numéricos absurdamente grandes (ex.: `1e999999`) ou 
          +inteiros com mais de 4.300 dígitos | baixa | O contexto padrão
          + do `Decimal` (28 dígitos) arredondaria somas em silêncio e `q
          +uantize` levantaria `InvalidOperation`; o Python recusa conver
          +ter inteiros gigantes. A spec não define limite superior para 
          +`valor` — **lacuna levada ao responsável**; até decidir, conta
          +s em contexto com `Inexact` como armadilha, para nunca arredon
          +dar em silêncio |                                             
      197 +| Chave repetida num objeto JSON (ex.: dois `"valor"` na mesma
          + despesa) | baixa | O parser fica com a última ocorrência, em 
          +silêncio. A spec não trata — **lacuna levada ao responsável** 
          +(aceitar a última, ou erro) |                                 
      198 +| Envelope do Dia 2 mudar política, regra ou formato | alta (é
          + certo) | Fronteiras da seção 2: política em `politica.py`, re
          +gras em `motor.py` com etapas em lista ordenada, formato em `e
          +ntrada.py`/`saida.py`; rastreabilidade automática (seção 6) ap
          +onta os testes afetados |                                     
      199 +| Testes passarem por concordarem com o código, não com a spec
          + | média | Esperados calculados à mão a partir da spec (skill 
          +`/task`, passo 4); `revisor-de-task` confere teste contra spec
          + antes do commit |                                            

⏺ Vou conferir as afirmações técnicas do plano antes de te mostrar.

  Ran 1 shell command (ctrl+o to expand)

⏺ Duas correções no texto: o simplejson 4.x já rejeita NaN por padrão, e o
  exemplo round(10.005, 2) está errado (o resultado é 10.01). Confiro um exemplo
  que falha de verdade.

  Ran 1 shell command (ctrl+o to expand)

⏺ Bash(cd /Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso && python3
      - <<'EOF'
      p="plan.md"; s=open(p).read()…)
  ⎿  Updated specs/001-motor-reembolso/plan.md (+4 -4)
      16  | Testes | `pytest` | Testes como funções simples, `parametrize
          ` para tabelas de casos (seção 7 da spec), `tmp_path` para a CL
          I | `unittest`: mais cerimônia por teste, sem ganho |
      17  | Lint | `ruff` (regras `E`, `F`, `I`, `B`, `UP`) | Já exigido 
          pelo `pre-commit`; um só binário para lint e ordenação de impor
          ts | `flake8` + `isort`: duas ferramentas para o mesmo papel |
      18  | Parsing/validação | `simplejson` com `use_decimal=True` (leit
          ura e escrita) + validação manual campo a campo | Lê `33.333` d
          ireto como `Decimal("33.333")`, sem passar por `float`, e escre
          ve `Decimal` como número JSON exato. A validação precisa produz
          ir **item `entrada_invalida`** por despesa, não exceção — regra
           fina demais para um validador de schema | `json` da biblioteca
           padrão: lê com `parse_float=Decimal`, mas não escreve `Decimal
          ` como número — teria que converter para `float` na saída e `va
          lor_informado` perderia dígitos além do 17º. `pydantic`/`jsonsc
          hema`: rejeitam o documento inteiro ou exigem contornos para "e
          rro vira item" e para copiar campos de tipo errado como nulo |
      19 -| Aritmética monetária | `decimal.Decimal`, `quantize(Decimal("
         -0.01"), ROUND_HALF_UP)` | Exato ao centavo; `ROUND_HALF_UP` do 
         -Python arredonda a metade **afastando do zero** (-0,005 → -0,01
         -), exatamente a RN-003 | `float`: `10.005` vira `10.00499…` e a
         -rredonda para 10,00 — viola a RN-003 já no caso de aceite. Cent
         -avos em `int`: exige arredondar na conversão de qualquer forma,
         - e o número informado (33,333) não cabe em centavos |          
      19 +| Aritmética monetária | `decimal.Decimal`, `quantize(Decimal("
         +0.01"), ROUND_HALF_UP)` | Exato ao centavo; `ROUND_HALF_UP` do 
         +Python arredonda a metade **afastando do zero** (-0,005 → -0,01
         +), exatamente a RN-003 | `float`: `1.005` é guardado como `1.00
         +499…` e `round(1.005, 2)` dá 1,00 (a RN-003 exige 1,01); `round
         +(0.125, 2)` dá 0,12, porque `round` arredonda a metade para o p
         +ar. Centavos em `int`: exige arredondar na conversão de qualque
         +r forma, e o número informado (33,333) não cabe em centavos |  
      20  | CLI | `argparse` (biblioteca padrão) | Um subcomando, duas op
          ções obrigatórias; erro de uso já sai com código 2 e mensagem e
          m stderr | `click`/`typer`: dependência a mais para uma interfa
          ce fixa e mínima |
      21  
      22  ## 2. Arquitetura
     ...
      111  
      112  **Contexto:** RN-003 exige arredondar a metade afastando do ze
           ro e cálculos exatos ao centavo; `valor_informado` é o número 
           recebido (33.333).
      113  **Decisão:** o JSON é lido com `simplejson.loads(..., use_deci
           mal=True)`, então todo número com parte decimal chega como `De
           cimal` construído do texto; inteiros são convertidos para `Dec
           imal`. `valor_considerado = valor_informado.quantize(Decimal("
           0.01"), ROUND_HALF_UP)`. Toda conta (saldo do limite, totais) 
           é feita entre `Decimal` já quantizados, então soma e subtração
            são exatas. A saída escreve `Decimal` como número JSON (`use_
           decimal=True`).
      114 -**Alternativa descartada:** `float` com arredondamento no fim 
          -(`round(10.005, 2) == 10.0`), e `json` padrão com conversão pa
          -ra `float` só na saída (perde dígitos de `valor_informado`).  
      114 +**Alternativa descartada:** `float` com arredondamento no fim 
          +(`round(1.005, 2) == 1.0`), e `json` padrão com conversão para
          + `float` só na saída (perde dígitos de `valor_informado`).    
      115  **Consequência:** fácil garantir a RN-003 e os totais da seção
            9 ao centavo. Exige cuidado para nunca misturar `float` (proi
           bido em `motor.py`; um teste de propriedade verifica que nenhu
           m campo monetário da saída é `float`). A forma escrita na saíd
           a pode diferir da entrada (`72.50` → `72.5`, ou `45.00` → `45.
           00`), o que a spec permite (seção 4: "como veio" é o valor num
           érico).
      116  
      117  ### DT-002 — Rejeitar o que não é JSON estrito
      118  
      119 -**Contexto:** RN-002: arquivo que não é JSON válido é erro de 
          -arquivo. O parser do Python aceita `NaN`, `Infinity` e `-Infin
          -ity`, que não são JSON.                                       
      120 -**Decisão:** `parse_constant` levanta erro → `ErroDeArquivo`. 
          -Bytes decodificados como UTF-8 estrito (`utf-8-sig`, aceitando
          - BOM, que a RFC 8259 permite ignorar); falha de decodificação 
          -→ `ErroDeArquivo`.                                            
      119 +**Contexto:** RN-002: arquivo que não é JSON válido é erro de 
          +arquivo. O `json` da biblioteca padrão aceita `NaN`, `Infinity
          +` e `-Infinity`, que não são JSON.                            
      120 +**Decisão:** `simplejson` ≥ 4 já os rejeita na leitura por pad
          +rão (`allow_nan=False`); a versão mínima fica fixada no `pypro
          +ject.toml` e um teste garante que `"valor": NaN` é erro de arq
          +uivo, para a proteção não sumir numa troca de versão. Erro de 
          +parse → `ErroDeArquivo`. Bytes decodificados como UTF-8 estrit
          +o (`utf-8-sig`, aceitando BOM, que a RFC 8259 permite ignorar)
          +; falha de decodificação → `ErroDeArquivo`.                   
      121  **Alternativa descartada:** aceitar `NaN` e tratar como "valor
            não é número" na despesa: transformaria arquivo inválido em p
           rocessamento normal.
      122  **Consequência:** `"valor": NaN` encerra a execução sem saída,
            como qualquer JSON inválido.
      123  

⏺ Escrevi o specs/001-motor-reembolso/plan.md (versão 1.0, baseado na spec 1.3).
  Ainda não fiz commit.

  O que o plano define
  - Stack: Python 3.12 com uv, pytest e ruff. Os hooks e a skill /task já usavam
    essas ferramentas.
  - Dinheiro: é guardado como Decimal desde a leitura do arquivo. Isso usa a
    biblioteca simplejson com use_decimal, assim um valor como 33.333 nunca vira
    float, e a saída grava valor_informado exato. Com float, round(1.005, 2) dá
    1,00, mas a RN-003 exige 1,01.
  - Arquitetura: só cli.py lê e grava arquivos. As regras ficam em motor.py, os
    valores da política em politica.py e a validação de entrada (RN-002) em
    entrada.py. Separei assim para que a mudança do envelope do Dia 2 caia num
    lugar só.
  - Ordem das regras: o motor roda em duas fases. A primeira avalia cada despesa
    sozinha (etapas 1 a 6). A segunda olha o conjunto: duplicatas, depois
    viagem e por fim o limite diário. A viagem é marcada antes de aplicar
    qualquer limite, então uma hospedagem que vem depois da alimentação do mesmo
    dia ainda conta.
  - Detalhes técnicos que viraram decisão (DT-001 a DT-009):
    - True não é aceito como número.
    - A data exige exatamente o formato AAAA-MM-DD (o Python 3.12 aceitaria
      20260701).
    - O arquivo de saída é gravado num temporário e só depois substitui o final.
      Assim, um arquivo de saída que já existia nunca fica pela metade.
    - NaN no JSON é erro de arquivo.
  - Testes: um arquivo de teste por regra RN. Os casos de borda da seção 7 ficam
    numa tabela, cada um identificado pelo texto da coluna "Caso". Um teste de
    rastreabilidade lê a spec.md e falha se alguma regra RN ou algum caso de
    borda ficar sem teste.

  Conferi rodando os comportamentos do Python e do simplejson que o plano usa.
  Dois pontos estavam errados no primeiro rascunho e já corrigi no arquivo: o
  exemplo de arredondamento com float e a forma de rejeitar NaN.

  Decisões suas: duas lacunas da spec

  Não são bloqueantes para as tasks, mas mudam o resultado de entradas válidas.
  Por isso não decidi sozinho; deixei as duas registradas como risco no plano.
  1. Não há limite superior para valor. Um valor como 1e999999, ou um inteiro
     com mais de 4.300 dígitos, quebra o Decimal e o Python. Hoje esse caso
     terminaria com erro em vez de virar item entrada_invalida. Uma opção é
     tratar como entrada_invalida.
  2. Chave repetida no JSON (por exemplo, dois "valor" na mesma despesa). Hoje
     vale a última, sem aviso. As opções são aceitar a última ou tratar como
     erro.

  Se decidir mexer nelas, isso vira mudança na spec (D-004) antes do tasks.md.
  Se não, faço o commit docs(plan): plano técnico 1.0 sobre a spec 1.3 e sigo
  para o tasks.md. Como fazer?

✻ Crunched for 3m 40s · done 10:00 PM

❯ vamos corrigir, tratar como entrada_invalida para nao quebrar o codigo, tem   
  que aceitar a última, mas avisar o motivo da primeira nao ser aceita          

⏺ Antes de editar a spec, preciso que você decida dois pontos. Sem eles a regra
  não dá para testar.

⏺ User answered Claude's questions:
  ⎿  · A partir de que valor uma despesa passa a ser 'grande demais' e vira 
     entrada_invalida? A spec precisa de um número exato para dar para testar. 
     Vale para valores positivos e negativos: hoje um -1e999999 sai como 
     valor_invalido e passaria a sair como entrada_invalida. → ≥ 1 bilhão 
     (Recommended)
     · Quando uma chave vem repetida no JSON, vale a última ocorrência. Onde 
     avisar que a primeira foi descartada? → Campo `avisos` na saída 
     (Recommended)

⏺ Decidido: valor absoluto a partir de 1 bilhão vira entrada_invalida, e os
  avisos vão num campo avisos na saída. Isso muda a spec (v1.4, D-004). Começo
  pela spec e depois ajusto o plano.

  Ran 1 shell command (ctrl+o to expand)

⏺ Agora aplico a v1.4 na spec: teto de valor na RN-002, RN-013 nova, campo
  avisos, AMB-018/019 e casos de borda.

⏺ Bash(cd /Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso && python3
      - <<'EOF'
      p="spec.md"; s=open(p).read()…)
  ⎿  488:- [ ] Cada regra RN-001 a RN-013 tem pelo menos um teste automatiz
     ado que a referencia.
  ⎿  Updated specs/001-motor-reembolso/spec.md (+58 -10)
      1  # Spec — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.3 · **Status:** aprovada para planejamento · **Últ
        -ima alteração:** 2026-10-01 (ver `DECISIONS.md` D-001 a D-003)  
      3 +**Versão:** 1.4 · **Status:** aprovada para planejamento · **Últ
        +ima alteração:** 2026-10-01 (ver `DECISIONS.md` D-001 a D-004)  
      4  
      5  > **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ
         . Nenhuma linha
      6  > aqui pode citar linguagem, biblioteca, classe, função ou estru
         tura de pasta.
     ...
      65  
      66  Campos não listados acima são ignorados.
      67  
      68 +Se um mesmo objeto do arquivo traz a mesma chave mais de uma ve
         +z, vale a última ocorrência, e a saída avisa que as anteriores 
         +foram descartadas (RN-013).                                    
      69 +                                                               
      70  ### Saída
      71  
      72  | Campo | Tipo | Significado |
     ...
      84  | `itens[].motivo` | texto ou nulo | código do motivo (tabela a
          baixo); nulo quando `aprovado` |
      85  | `itens[].em_viagem` | booleano ou nulo | se a data estava em 
          viagem (RN-010); nulo se o item foi recusado antes do limite di
          ário |
      86  | `itens[].limite_diario` | número ou nulo | limite diário apli
          cado à categoria naquela data; nulo se o item foi recusado ante
          s do limite diário |
      85 -| `itens[].justificativa` | texto | frase em português explican
         -do a decisão. Texto livre: **não é contratual**; os campos acim
         -a são |                                                        
      87 +| `itens[].justificativa` | texto | frase em português explican
         +do a decisão. Texto livre: **não é contratual**; os demais camp
         +os são |                                                       
      88 +| `itens[].avisos` | lista de textos | avisos de chave repetida
         + dentro da despesa (RN-013); lista vazia se não houver |       
      89  | `totais.valor_solicitado` | número | soma de `valor_considera
          do` dos itens **não recusados por `entrada_invalida` e com `val
          or_considerado` maior que zero** |
      90  | `totais.valor_reembolsado` | número | soma de `valor_reembols
          ado` |
      91  | `totais.valor_glosado` | número | `valor_solicitado − valor_r
          eembolsado` |
      92 +| `avisos` | lista de textos | avisos de chave repetida fora da
         +s despesas (RN-013); lista vazia se não houver |               
      93  
      94  Todos os valores monetários **calculados** da saída (`valor_con
          siderado`, `valor_reembolsado`, `limite_diario` e totais) são e
          m reais, com no máximo 2 casas decimais e exatos ao centavo. `v
          alor_informado` é a única exceção: é a cópia do número recebido
           (ex.: 33.333). Como a entrada é um número, "como veio" se refe
          re ao valor numérico, não à forma escrita (72.50 e 72.5 são o m
          esmo valor).
      95  
     ...
       97  
       98  | Código | Quando | Status resultante |
       99  |---|---|---|
       96 -| `entrada_invalida` | elemento que não é objeto, ou campo obr
          -igatório ausente ou com tipo/formato errado (RN-002) | `recusa
          -do` |                                                         
      100 +| `entrada_invalida` | elemento que não é objeto; campo obriga
          +tório ausente ou com tipo/formato errado; ou `valor` com valor
          + absoluto a partir de 1.000.000.000,00 (RN-002) | `recusado` |
      101  | `valor_invalido` | valor considerado menor ou igual a zero (
           RN-004) | `recusado` |
      102  | `fora_do_periodo` | data fora de `[inicio, fim]` (RN-005) | 
           `recusado` |
      103  | `categoria_fora_da_politica` | categoria não reconhecida (RN
           -006) | `recusado` |
     ...
      115      { "id": "d-1", "data": "2026-07-03", "categoria": "aliment
           acao",
      116        "valor_informado": 45.0, "valor_considerado": 45.0, "val
           or_reembolsado": 45.0,
      117        "status": "aprovado", "motivo": null, "em_viagem": false
           , "limite_diario": 60.0,
      114 -      "justificativa": "Aprovado integralmente: 45,00 dentro d
          -o limite diário de 60,00." },                                 
     … 101 more lines (ctrl+o to expand)

⏺ Falta registrar no resultado esperado da seção 9 que, no exemplo, todos os
  avisos saem vazios. Depois escrevo a D-004.

⏺ Bash(python3 - <<'EOF'
      p="spec.md"; s=open(p).read()…)
  ⎿  Updated specs/001-motor-reembolso/DECISIONS.md (+21 -0)
      10  
      11  ---
      12  
      13 +## D-004 — Valor gigante e chave repetida: spec 1.3 → 1.4 · `20
         +26-10-01`                                                      
      14 +                                                               
      15 +**Gatilho:** escrita do `plan.md` 1.0. Ao verificar como o códi
         +go leria o arquivo, apareceram duas entradas válidas no formato
         + cujo resultado a spec não definia. O responsável decidiu as du
         +as (sessão `docs/sessions/07-*`).                              
      16 +                                                               
      17 +**O que mudou na spec:**                                       
      18 +                                                               
      19 +| # | Ponto | De (1.3) | Para (1.4) | Onde |                   
      20 +|---|---|---|---|---|                                          
      21 +| 1 | `valor` sem limite superior (ex.: 1e999999) | indefinido;
         + o cálculo exato ao centavo não é possível para qualquer número
         +, e a execução seria interrompida | valor absoluto a partir de 
         +1.000.000.000,00, comparado com o número recebido → `entrada_in
         +valida` (também se negativo, antes de `valor_invalido`) | RN-00
         +2, seção 4 (motivos), AMB-018, seção 7 |                       
      22 +| 2 | Chave repetida num objeto (ex.: dois `valor`) | indefinid
         +o; a leitura ficaria com uma delas em silêncio | vale a última 
         +ocorrência; cada chave repetida gera aviso com texto fixo em `i
         +tens[].avisos` (dentro da despesa) ou `avisos` do topo (fora) |
         + RN-013 (nova), seção 4 (entrada e saída), seção 8, AMB-019, se
         +ção 7 |                                                        
      23 +                                                               
      24 +**Por quê:** o ponto 1 deixaria uma despesa derrubar a execução
         + inteira, contra o tratamento por item da RN-002; recusar como 
         +`entrada_invalida` preserva as demais. O ponto 2 muda o reembol
         +so conforme a ocorrência escolhida; a última ocorrência foi a e
         +scolhida, e o descarte fica visível ao conferente em campo cont
         +ratual, em vez de texto livre na justificativa ou no terminal. 
      25 +                                                               
      26 +**O que isso invalidou:** nenhum código ou teste (ainda não exi
         +stem). Formato de saída: dois campos novos (`itens[].avisos`, `
         +avisos`), sempre presentes. Nenhum valor do resultado esperado 
         +do exemplo mudou (seção 9; `avisos` vazios). Casos de borda nov
         +os: 7 linhas na seção 7. Critério de aceite da seção 9 passa a 
         +citar RN-001 a RN-013. `plan.md` passa a se basear na 1.4.     
      27 +                                                               
      28 +**Tasks afetadas:** nenhuma (o `tasks.md` ainda não foi escrito
         +).                                                             
      29 +                                                               
      30 +**Custo:** 3 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`); 2
         + pontos decididos na mesma sessão. Nova rodada do `spec-adversa
         +ry` sobre a 1.4, por mudar o formato de saída.                 
      31 +                                                               
      32 +---                                                            
      33 +                                                               
      34  ## D-003 — Validação final antes do plano: spec 1.2 → 1.3 · `20
          26-10-01`
      35  
      36  **Gatilho:** conferência da spec 1.2 (commit `bdb1eec`) antes d
          e iniciar o `plan.md`, pedida pelo responsável. Saíram uma cont
          radição interna e três lacunas de contrato. As quatro recomenda
          ções foram aceitas pelo responsável (sessão `docs/sessions/06-*
          `).
  ⎿  Updated specs/001-motor-reembolso/spec.md (+2 -0)
      512  
      513  Totais: `valor_solicitado` = 1.861,84 · `valor_reembolsado` = 
           585,43 · `valor_glosado` = 1.276,41.
      514  
      515 +O arquivo de exemplo não tem chave repetida: `avisos` vazio em
          + todos os itens e no topo.                                    
      516 +                                                              
      517  ## 10. O que fica em aberto
      518  
      519  ### Decisões provisórias

⏺ Agora atualizo o plan.md para a 1.4.

⏺ Bash(python3 - <<'EOF'
      p="plan.md"; s=open(p).read()…)
  ⎿  124:**Decisão:** `simplejson` ≥ 4 já os rejeita na leitura por padrão
     (`allow_nan=False`); a versão mínima fica fixada no `pyproject.toml` e
      um teste garante que `"valor": NaN` é erro de arquivo, para a proteçã
     … +7 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/plan.md (+22 -11)
      1  # Plano Técnico — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.0 · **Baseado na spec:** 1.3                      
      3 +**Versão:** 1.0 · **Baseado na spec:** 1.4                      
      4  
      5  > Aqui mora o COMO. Este arquivo pode e deve falar de linguagem,
          biblioteca e
      6  > arquitetura. O que ele **não** pode é introduzir regra de negó
         cio nova — se
     ...
      15  | Linguagem | Python ≥ 3.12, projeto gerenciado com `uv` (`pypr
          oject.toml` + `uv.lock`) | `Decimal` e `datetime.date` na bibli
          oteca padrão cobrem dinheiro e datas sem dependência; `uv` fixa
           a versão do Python (o do sistema é 3.9) e já é o que os hooks 
          de `.githooks/` usam | Node/TypeScript: sem tipo decimal nativo
          , teria que trazer biblioteca para o ponto mais sensível do pro
          jeto |
      16  | Testes | `pytest` | Testes como funções simples, `parametrize
          ` para tabelas de casos (seção 7 da spec), `tmp_path` para a CL
          I | `unittest`: mais cerimônia por teste, sem ganho |
      17  | Lint | `ruff` (regras `E`, `F`, `I`, `B`, `UP`) | Já exigido 
          pelo `pre-commit`; um só binário para lint e ordenação de impor
          ts | `flake8` + `isort`: duas ferramentas para o mesmo papel |
      18 -| Parsing/validação | `simplejson` com `use_decimal=True` (leit
         -ura e escrita) + validação manual campo a campo | Lê `33.333` d
         -ireto como `Decimal("33.333")`, sem passar por `float`, e escre
         -ve `Decimal` como número JSON exato. A validação precisa produz
         -ir **item `entrada_invalida`** por despesa, não exceção — regra
         - fina demais para um validador de schema | `json` da biblioteca
         - padrão: lê com `parse_float=Decimal`, mas não escreve `Decimal
         -` como número — teria que converter para `float` na saída e `va
         -lor_informado` perderia dígitos além do 17º. `pydantic`/`jsonsc
         -hema`: rejeitam o documento inteiro ou exigem contornos para "e
         -rro vira item" e para copiar campos de tipo errado como nulo | 
      18 +| Parsing/validação | `simplejson` com `use_decimal=True` (leit
         +ura e escrita), `object_pairs_hook` para chaves repetidas (DT-0
         +10) + validação manual campo a campo | Lê `33.333` direto como 
         +`Decimal("33.333")`, sem passar por `float`, e escreve `Decimal
         +` como número JSON exato; o hook entrega os pares de cada objet
         +o na ordem do arquivo, inclusive os repetidos. A validação prec
         +isa produzir **item `entrada_invalida`** por despesa, não exceç
         +ão — regra fina demais para um validador de schema | `json` da 
         +biblioteca padrão: lê com `parse_float=Decimal`, mas não escrev
         +e `Decimal` como número — teria que converter para `float` na s
         +aída e `valor_informado` perderia dígitos além do 17º. `pydanti
         +c`/`jsonschema`: rejeitam o documento inteiro ou exigem contorn
         +os para "erro vira item" e para copiar campos de tipo errado co
         +mo nulo |                                                      
      19  | Aritmética monetária | `decimal.Decimal`, `quantize(Decimal("
          0.01"), ROUND_HALF_UP)` | Exato ao centavo; `ROUND_HALF_UP` do 
          Python arredonda a metade **afastando do zero** (-0,005 → -0,01
          ), exatamente a RN-003 | `float`: `1.005` é guardado como `1.00
          499…` e `round(1.005, 2)` dá 1,00 (a RN-003 exige 1,01); `round
          (0.125, 2)` dá 0,12, porque `round` arredonda a metade para o p
          ar. Centavos em `int`: exige arredondar na conversão de qualque
          r forma, e o número informado (33,333) não cabe em centavos |
      20  | CLI | `argparse` (biblioteca padrão) | Um subcomando, duas op
          ções obrigatórias; erro de uso já sai com código 2 e mensagem e
          m stderr | `click`/`typer`: dependência a mais para uma interfa
          ce fixa e mínima |
      21  
     ...
      32  | Módulo (`src/reembolso/`) | Responsabilidade | Faz I/O? |
      33  |---|---|---|
      34  | `cli.py` | `argparse`, lê bytes do arquivo, chama o pipeline,
           grava a saída de forma atômica, mapeia erros para mensagem + c
          ódigo de saída | sim |
      35 -| `entrada.py` | bytes → JSON (`Decimal`) → `Entrada`. Erros de
         - arquivo da RN-002 viram `ErroDeArquivo`; despesa inválida vira
         - `DespesaInvalida` (etapa 1 da seção 8) | não |                
      35 +| `entrada.py` | bytes → JSON (`Decimal`) → `Entrada`. Resolve 
         +chaves repetidas e gera os avisos (RN-013); erros de arquivo da
         + RN-002 viram `ErroDeArquivo`; despesa inválida vira `DespesaIn
         +valida` (etapa 1 da seção 8) | não |                           
      36  | `normalizacao.py` | `normalizar_texto()` — os 4 passos da seç
          ão 5 da spec | não |
      37  | `politica.py` | constantes da política (seção 4 deste plano) 
          | não |
      38  | `motor.py` | etapas 2 a 9 da seção 8; recebe `Entrada`, devol
          ve `Resultado` | não |
     ...
      65      fornecedor: str,           # normalizado
      66      valor_informado: Decimal,
      67      tem_nota_fiscal: bool,
      68 +    avisos: tuple[str, ...],   # RN-013                        
      69  )
      70  DespesaInvalida(               # recusada na etapa 1
      71      posicao: int,
      72      id: str | None, data_texto: str | None,
      73      categoria_saida: str | None,   # normalizada se reconhecida
          ; senão texto como veio; senão None
      74      valor_informado: Decimal | None,
      75 +    avisos: tuple[str, ...],                                   
      76  )
      75 -Entrada(colaborador, periodo, despesas: list[Despesa | DespesaI
         -nvalida])                                                      
      77 +Entrada(colaborador, periodo, despesas: list[Despesa | DespesaI
         +nvalida],                                                      
      78 +        avisos: tuple[str, ...])      # chaves repetidas fora d
         +as despesas                                                    
      79  
      80  ItemResultado(                 # espelha `itens[]` da seção 4 d
          a spec, campo a campo
     … 59 more lines (ctrl+o to expand)

⏺ Confiro o comportamento do simplejson que a DT-010 e o teto usam.

  Ran 1 shell command (ctrl+o to expand)

⏺ Funciona como o plano descreve. Pelo CLAUDE.md, a mudança no formato de saída
  pede uma rodada do spec-adversary antes do commit. Disparo agora, focada na
  D-004.

⏺ spec-adversary(Revisão adversarial spec 1.4)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ Apliquei as duas decisões na spec (agora na versão 1.4), registrei a D-004 no
  DECISIONS.md e atualizei o plan.md. Ainda não fiz commit.

  Na spec (1.4)
  - Valor gigante (RN-002, AMB-018): se o valor absoluto do número recebido for
    1.000.000.000,00 ou mais, a despesa vira entrada_invalida. Isso vale também
    para negativos: -1e12 sai entrada_invalida, não valor_invalido. O teto é
    comparado antes do arredondamento, então 999999999.995 passa e é considerado
    como 1.000.000.000,00. Uma despesa assim não interrompe mais o
    processamento: só ela é recusada.
  - Chave repetida (RN-013 nova, AMB-019): vale a última ocorrência. Cada chave
    repetida gera um aviso com texto fixo:
    chave repetida: valor (2 ocorrências; valeu a última)
    O aviso vai em itens[].avisos quando a chave está dentro de uma despesa e em
    avisos no topo da saída nos demais casos. Os dois campos sempre aparecem,
    vazios quando não há aviso. Uma chave repetida dentro de um valor que foi
    descartado não gera aviso.
  - Somei 7 casos de borda na seção 7 e incluí avisos no exemplo da seção 4. O
    critério de aceite passou a cobrir da RN-001 à RN-013. O resultado esperado
    do arquivo de exemplo não mudou.

  No plano
  - O teto de valor entrou em politica.py.
  - Números inteiros também passam a ser lidos como Decimal, então um inteiro
    com milhares de dígitos não quebra a leitura.
  - A nova DT-010 descreve como o leitor de JSON detecta as chaves repetidas e
    mantém os avisos na ordem do arquivo.
  - As duas lacunas saíram da tabela de riscos, marcadas como resolvidas pela
    D-004.

  Conferi rodando código esses comportamentos: inteiro de 5.000 dígitos,
  1e999999, a comparação com o teto e a ordem dos avisos com chaves repetidas em
  níveis diferentes.

  Pelo CLAUDE.md, mudança no formato de saída pede nova revisão do
  spec-adversary. Ela está rodando agora, focada na D-004. Quando terminar,
  trago os problemas que ele apontar para você decidir. Só depois faço os
  commits docs(spec) e docs(plan).
✻ Cooked for 3m 7s · done 10:11 PM

❯ ok, me mostra o resultado do spec-adversary                                   

⏺ O spec-adversary ainda está rodando e não devolveu resultado, então ainda não
  tenho nada para te mostrar. Quando ele terminar, eu sou avisado e trago aqui
  todos os problemas que ele apontar, com a severidade e a pergunta de decisão
  de cada um. Até lá não faço nenhum commit.

✻ Cogitated for 3s · done 10:11 PM

❯ ok, me avisa quando terminar                                                  

⏺ Combinado. Quando o spec-adversary terminar, eu sou avisado e trago aqui todos
  os problemas que ele apontar, cada um com a severidade e a pergunta de
  decisão. Os pontos BLOQUEANTES vêm primeiro. Até você decidir, não faço nenhum
  commit.

✻ Baked for 11s · done 10:12 PM

› Message from spec-adversary
  Encontrei 4 problemas na spec 1.4. Um é bloqueante. Li
  `specs/001-motor-reembolso/spec.md` e `DECISIONS.md` (D-004). A spec reflete
  os dois pontos da D-004: RN-002, motivos da seção 4, AMB-018, RN-013, AMB-019,
  as 7 linhas novas da seção 7, a seção 8 e o critério RN-001 a RN-013 da seção
  9.

  ### 1. "Número recebido" não diz com que precisão o número é lido. Afeta o
  teto, o arredondamento e o `valor_informado` — BLOQUEANTE — ambiguidade/lacuna

  - **Regras afetadas:** RN-002 (teto), AMB-018, RN-003, seção 4
  (`valor_informado`), casos novos da seção 7 ("Valor logo abaixo de um bilhão",
  "Valor com expoente enorme").
  - **Cenários de entrada:**
    - (a) hospedagem com nota, `valor` 999999999.995. É o próprio aceite da
  RN-002.
    - (b) `valor` 999999999.99999999999 (abaixo de 1e9 no decimal escrito).
    - (c) `valor` 1e999999 (caso da seção 7).
    - (d) alimentação, `valor` 1e-999999, ou 0.1 seguido de 10.000 dígitos.
  - **Comportamento pela interpretação atual:** indefinido. Pela leitura "valor
  decimal exato do literal":
    - (a) dá `valor_considerado` 1000000000.00, como diz a spec;
    - (b) segue (< 1e9) com `valor_considerado` 1000000000.00;
    - (c) é `entrada_invalida`, mas `valor_informado` tem de ser um número igual
  a 10^999999;
    - (d) dá `valor_invalido` com `valor_informado` 1e-999999.

    Pela leitura "o número como foi lido", com precisão limitada:
    - (a) 999999999.995 lido assim vale cerca de 999999999.99499988…, e o
  arredondamento dá 999999999.99, contra o aceite da spec. O mesmo vale para
  10.005 → 10.00, contra o aceite da RN-003;
    - (b) vira 1e9 e passa a ser `entrada_invalida`;
    - (c) o número não é representável, e `valor_informado` poderia sair
  infinito, nulo ou com erro.
  - **Por que é um problema:** a D-004 criou o teto para garantir cálculo exato
  e evitar que um valor derrube a execução. Mas o teto só limita a magnitude,
  não a precisão: valores minúsculos ou com muitos dígitos continuam aceitos, e
  a AMB-018 afirma que "todo valor aceito é calculado exatamente". Além disso, o
  `valor_informado` é contratual e "sem arredondamento". Para o 1e999999, a
  D-004 resolveu o status, mas a saída ainda precisa copiar um número que o
  próprio gatilho da D-004 diz não ser calculável. O caso da seção 7 não informa
  o `valor_informado` esperado, e por isso o teste obrigatório desse caso não
  tem resultado definido. A fronteira do teto (b) também muda de
  `entrada_invalida` para "segue" conforme a leitura.
  - **Pergunta para decisão:** o teto, o arredondamento e o `valor_informado` se
  baseiam no valor decimal exato escrito no arquivo, qualquer que seja o número
  de dígitos ou o expoente? Se não, qual precisão ou representação vale? E qual
  é o `valor_informado` esperado para `valor` 1e999999 e 1e-999999?

  ### 2. Ordem dos avisos quando a chave repetida também aparece dentro de um
  valor descartado — PODE ESPERAR — ambiguidade

  - **Regra afetada:** RN-013 (itens "Ordem dos avisos" e "Só geram aviso os
  objetos que continuam").
  - **Cenário de entrada:** despesa válida com:
    ```
    "extra": {"x": 1, "x": 2}, "obs": "a", "obs": "b", "extra": {"x": 3, "x": 4}
    ```
  - **Comportamento pela interpretação atual:** indefinido. O aviso de `extra.x`
  existe, porque o segundo `extra` sobrevive e repete `x`. A "primeira
  ocorrência" de `extra.x` no arquivo, porém, pode ser a de dentro do `extra`
  descartado (antes de `obs`) ou só a de dentro do `extra` que valeu (depois de
  `obs`). A lista sai como [`extra`, `extra.x`, `obs`] ou como [`extra`, `obs`,
  `extra.x`]. A mesma dúvida vale para o `<n>`: as ocorrências dentro do valor
  descartado entram na contagem?
  - **Por que é um problema:** os avisos são campo contratual, com ordem
  definida. Duas implementações corretas pela letra produzem listas diferentes,
  e o teste do caso "chave repetida dentro de valor descartado" não fixa isso.
  - **Pergunta para decisão:** para ordenar o aviso de uma chave aninhada e
  contar as ocorrências, valem só as ocorrências dentro do valor que sobreviveu
  ou também as de dentro dos valores descartados?

  ### 3. O formato do caminho não é inequívoco para todas as chaves e estruturas
  válidas — PODE ESPERAR — lacuna

  - **Regra afetada:** RN-013 (item "Caminho" e texto exato do aviso).
  - **Cenários de entrada:**
    - (a) despesa com `"extra": {"a.b": 1, "a.b": 2, "a": {"b": 1, "b": 2}}`.
  Gera dois avisos com o texto idêntico `chave repetida: extra.a.b (2
  ocorrências; valeu a última)`.
    - (b) chave vazia repetida, `"extra": {"": 1, "": 2}`. O caminho seria
  `extra.`?
    - (c) chave com `[`, `]`, `(`, `)`, `;`, aspas ou quebra de linha.
    - (d) elemento de `despesas` que é uma lista, `[[{"a": 1, "a": 2}]]`. O item
  é `entrada_invalida`, e o caminho "a partir da despesa" começaria por índice
  (`[0].a`?), formato que não aparece nos exemplos.
  - **Comportamento pela interpretação atual:** indefinido. A spec não diz como
  escapar ou citar chaves com caracteres especiais, nem como escrever um caminho
  que começa por posição de lista.
  - **Por que é um problema:** o texto do aviso é declarado "exato", logo
  contratual. Caminhos diferentes ficam iguais e não dá para saber qual chave
  foi descartada. Não muda valores.
  - **Pergunta para decisão:** como o caminho representa chaves com ponto,
  colchetes, parênteses, texto vazio ou caracteres de controle, e como começa
  quando o elemento de `despesas` não é objeto? Ou esses casos ficam registrados
  como fora de escopo?

  ### 4. "Igual caractere a caractere": antes ou depois de decodificar os
  escapes? — PODE ESPERAR — ambiguidade

  - **Regra afetada:** RN-013; afeta indiretamente RN-002 e RN-009.
  - **Cenário de entrada:** alimentação em data válida, com nota:
    ```
    "valor": 30.00, "valor": 90.00
    ```
    Variação: chaves extras com o mesmo texto em formas Unicode diferentes
  (composta e decomposta, por exemplo `descrição`).
  - **Comportamento pela interpretação atual:** indefinido.
    - Se a comparação é sobre o texto decodificado, as duas chaves são `valor`.
  Vale 90,00, o reembolso é 60,00 com `parcial` (fora de viagem), e há aviso.
    - Se é sobre a forma escrita, as chaves são diferentes e não há aviso. A
  spec então não diz se `valor` é o campo `valor` (qual das duas vale?) ou um
  campo extra ignorado (vale 30,00, `aprovado`).

    No caso Unicode, "caractere a caractere" deixa em aberto se a composta e a
  decomposta são a mesma chave. Isso só afeta os avisos, porque os campos
  obrigatórios são ASCII.
  - **Por que é um problema:** o reembolso muda (60,00 contra 30,00) e o aviso
  aparece ou some conforme a leitura. O cenário é improvável e exige escrita
  deliberada.
  - **Pergunta para decisão:** a igualdade de chaves da RN-013 compara o texto
  depois de decodificar os escapes ou a forma escrita no arquivo? Formas Unicode
  diferentes do mesmo texto são a mesma chave? E o caminho no aviso usa o texto
  decodificado ou o escrito?

  ---

  1. **Decidir antes da implementação:** 1.
  2. **Pode ser decidido depois:** 2, 3, 4.

⏺ O spec-adversary terminou e apontou 4 problemas na spec 1.4. Um deles é
  bloqueante. Abaixo, cada um com a minha recomendação. As decisões são suas.

  1. BLOQUEANTE: com que precisão o "número recebido" é lido

  A spec não diz se o teto, o arredondamento e o valor_informado usam o número
  exatamente como está escrito no arquivo ou uma versão aproximada dele.
  - Exemplo: lido de forma aproximada, 999999999.995 arredonda para
    999.999.999,99, e não para 1.000.000.000,00 como diz o próprio aceite da
    RN-002. Com 10.005 acontece o mesmo: dá 10,00, contra a RN-003.
  - Exemplo: 999999999.99999999999 fica abaixo do teto se for lido exato, mas
    vira 1e9 e passa a entrada_invalida se for lido aproximado.
  - Lacuna: o caso de borda 1e999999 não informa qual valor_informado se espera.

  Recomendação: escrever na spec que o "número recebido" é o valor decimal exato
  escrito no arquivo, com qualquer quantidade de dígitos e qualquer expoente.
  Já é assim que o plano lê os números (DT-001). O valor_informado reproduz esse
  valor exato, e a forma escrita pode mudar: 1e999999 sai como 1E+999999, que é
  o mesmo número. Eu completaria os casos de borda com o valor_informado
  esperado para 1e999999 e para 1e-999999. Este último dá valor_invalido, porque
  arredonda para 0,00.

  2. Ordem e contagem dos avisos quando a chave também aparece dentro de um 
  valor descartado

  Exemplo: "extra": {"x":1,"x":2}, "obs":"a", "obs":"b", "extra": {"x":3,"x":4}.
  A spec não diz se a ordem e o <n> do aviso de extra.x consideram o x que está
  dentro do primeiro extra, que foi descartado.

  Recomendação: contar só as ocorrências dentro do valor que valeu. Isso é
  coerente com a regra de que valores descartados não geram aviso. No exemplo,
  os avisos saem na ordem [extra, obs, extra.x], e extra.x aparece com 2
  ocorrências.

  3. O caminho nem sempre é inequívoco

  Uma chave chamada "a.b" e o caminho a → b geram o mesmo texto de aviso. Também
  não está definido como escrever uma chave vazia ou com colchetes, nem um
  caminho que começa por posição de lista (quando o elemento de despesas é uma
  lista).

  Recomendação:
  - definir que, quando o elemento de despesas é uma lista, o caminho começa
    pela posição (ex.: [0].a);
  - registrar na seção 10 como risco aceito que chaves com ., [ ou ], ou vazias,
    podem gerar caminhos ambíguos. Isso só acontece com campos extras, que já
    são ignorados. Os campos obrigatórios são palavras simples e nunca causam
    isso.

  Escapar esses caracteres no caminho complicaria um texto que a pessoa que
  confere precisa ler.

  4. "Igual caractere a caractere": antes ou depois de decodificar os escapes

  Exemplo: "valor": 30.00 seguido de "\u0076alor": 90.00. O \u0076 é o código da
  letra v, então a segunda chave também se lê valor. Conforme a leitura, o
  reembolso fica em 60,00 ou em 30,00.

  Recomendação:
  - comparar o texto depois de decodificar os escapes: as duas são valor, vale
    90,00 e sai aviso. É o que o JSON define e o que o leitor já faz;
  - não aplicar normalização Unicode: a forma composta e a decomposta de uma
    letra acentuada contam como chaves diferentes. Isso só afeta campos extras;
  - o caminho do aviso usa o texto decodificado.

  ---

  Se você aceitar as 4 recomendações, aplico tudo como spec 1.5 dentro da mesma
  D-004, porque nada disso foi commitado ainda. Depois rodo de novo o
  spec-adversary só sobre esses pontos e faço os commits docs(spec) e
  docs(plan). Quer mudar alguma delas?

✻ Baked for 23s · done 10:13 PM

⏺ Agent "Revisão adversarial spec 1.4" finished · 2m 12s

❯ aceito as 4 recomendações, pode aplicar                                       

⏺ Aplico as 4 recomendações como spec 1.5, dentro da D-004.

⏺ Bash(python3 - <<'EOF'
      p="spec.md"; s=open(p).read()…)
  ⎿  Updated specs/001-motor-reembolso/DECISIONS.md (+10 -6)
      10  
      11  ---
      12  
      13 -## D-004 — Valor gigante e chave repetida: spec 1.3 → 1.4 · `20
         -26-10-01`                                                      
      13 +## D-004 — Valor gigante e chave repetida: spec 1.3 → 1.5 · `20
         +26-10-01`                                                      
      14  
      15 -**Gatilho:** escrita do `plan.md` 1.0. Ao verificar como o códi
         -go leria o arquivo, apareceram duas entradas válidas no formato
         - cujo resultado a spec não definia. O responsável decidiu as du
         -as (sessão `docs/sessions/07-*`).                              
      15 +**Gatilho:** escrita do `plan.md` 1.0. Ao verificar como o códi
         +go leria o arquivo, apareceram duas entradas válidas no formato
         + cujo resultado a spec não definia. O responsável decidiu as du
         +as (versão 1.4, não commitada). A rodada do `spec-adversary` so
         +bre a 1.4 apontou 4 problemas (1 bloqueante) nas próprias decis
         +ões; o responsável aceitou as 4 recomendações, aplicadas na 1.5
         + (pontos 3 a 6). Sessão `docs/sessions/07-*`.                  
      16  
      17  **O que mudou na spec:**
      18  
      19 -| # | Ponto | De (1.3) | Para (1.4) | Onde |                   
      19 +| # | Ponto | De (1.3) | Para (1.5) | Onde |                   
      20  |---|---|---|---|---|
      21  | 1 | `valor` sem limite superior (ex.: 1e999999) | indefinido;
           o cálculo exato ao centavo não é possível para qualquer número
          , e a execução seria interrompida | valor absoluto a partir de 
          1.000.000.000,00, comparado com o número recebido → `entrada_in
          valida` (também se negativo, antes de `valor_invalido`) | RN-00
          2, seção 4 (motivos), AMB-018, seção 7 |
      22  | 2 | Chave repetida num objeto (ex.: dois `valor`) | indefinid
          o; a leitura ficaria com uma delas em silêncio | vale a última 
          ocorrência; cada chave repetida gera aviso com texto fixo em `i
          tens[].avisos` (dentro da despesa) ou `avisos` do topo (fora) |
           RN-013 (nova), seção 4 (entrada e saída), seção 8, AMB-019, se
          ção 7 |
      23 +| 3 | Precisão do "número recebido" (**bloqueante** na 1.4) | i
         +ndefinida: lido aproximado, 999999999.995 arredondava para 9999
         +99999,99, contra o aceite da própria RN-002 (e 10.005 contra a 
         +RN-003); `valor_informado` de 1e999999 sem esperado | todo núme
         +ro vale pelo valor decimal exato escrito no arquivo, com quaisq
         +uer dígitos e expoente; teto, arredondamento e `valor_informado
         +` usam esse valor | seção 4, RN-003, seção 7 |                 
      24 +| 4 | Ordem e contagem de aviso de chave aninhada que também ap
         +arece em valor descartado | indefinidas | contam só as ocorrênc
         +ias dentro do valor que valeu | RN-013, seção 7 |              
      25 +| 5 | Caminho do aviso | sem regra para elemento de `despesas` 
         +que é lista; chaves com `.`, `[`, `]` ou vazias geram caminhos 
         +ambíguos | lista começa pela posição (`[0].a`); chaves sem esca
         +pe, ambiguidade registrada como risco aceito | RN-013, seção 10
         +, seção 7 |                                                    
      26 +| 6 | Igualdade de chaves | "caractere a caractere" sem dizer s
         +e antes ou depois dos escapes (`"\u0076alor"`) | depois de deco
         +dificar os escapes, sem normalização Unicode; caminho usa o tex
         +to decodificado | RN-013, seção 7 |                            
      27  
      24 -**Por quê:** o ponto 1 deixaria uma despesa derrubar a execução
         - inteira, contra o tratamento por item da RN-002; recusar como 
         -`entrada_invalida` preserva as demais. O ponto 2 muda o reembol
         -so conforme a ocorrência escolhida; a última ocorrência foi a e
         -scolhida, e o descarte fica visível ao conferente em campo cont
         -ratual, em vez de texto livre na justificativa ou no terminal. 
      28 +**Por quê:** o ponto 1 deixaria uma despesa derrubar a execução
         + inteira, contra o tratamento por item da RN-002; recusar como 
         +`entrada_invalida` preserva as demais. O ponto 3 fecha o que o 
         +ponto 1 deixou aberto: o teto limita a magnitude, e a leitura e
         +xata garante que o valor aceito é o escrito. O ponto 2 muda o r
         +eembolso conforme a ocorrência escolhida; a última ocorrência f
         +oi a escolhida, e o descarte fica visível ao conferente em camp
         +o contratual, em vez de texto livre na justificativa ou no term
         +inal. Os pontos 4 a 6 tornam o texto e a ordem dos avisos deter
         +minísticos, já que são contratuais; escapar caracteres no camin
         +ho foi descartado para manter o aviso legível.                 
      29  
      26 -**O que isso invalidou:** nenhum código ou teste (ainda não exi
         -stem). Formato de saída: dois campos novos (`itens[].avisos`, `
         -avisos`), sempre presentes. Nenhum valor do resultado esperado 
         -do exemplo mudou (seção 9; `avisos` vazios). Casos de borda nov
         -os: 7 linhas na seção 7. Critério de aceite da seção 9 passa a 
         -citar RN-001 a RN-013. `plan.md` passa a se basear na 1.4.     
      30 +**O que isso invalidou:** nenhum código ou teste (ainda não exi
         +stem). Formato de saída: dois campos novos (`itens[].avisos`, `
         +avisos`), sempre presentes. Nenhum valor do resultado esperado 
         +do exemplo mudou (seção 9; `avisos` vazios). Casos de borda nov
         +os: 12 linhas na seção 7. Risco aceito novo na seção 10 (caminh
         +o ambíguo). Critério de aceite da seção 9 passa a citar RN-001 
         +a RN-013. `plan.md` passa a se basear na 1.5.                  
      31  
      32  **Tasks afetadas:** nenhuma (o `tasks.md` ainda não foi escrito
          ).
      33  
      30 -**Custo:** 3 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`); 2
         - pontos decididos na mesma sessão. Nova rodada do `spec-adversa
         -ry` sobre a 1.4, por mudar o formato de saída.                 
      34 +**Custo:** 3 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`); 6
         + pontos decididos na mesma sessão. Duas rodadas do `spec-advers
         +ary`: sobre a 1.4 (por mudar o formato de saída) e sobre a 1.5 
         +(pontos 3 a 6).                                                
      35  
      36  ---
      37  
  ⎿  Updated specs/001-motor-reembolso/plan.md (+3 -3)
      1  # Plano Técnico — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.0 · **Baseado na spec:** 1.4                      
      3 +**Versão:** 1.0 · **Baseado na spec:** 1.5                      
      4  
      5  > Aqui mora o COMO. Este arquivo pode e deve falar de linguagem,
          biblioteca e
      6  > arquitetura. O que ele **não** pode é introduzir regra de negó
         cio nova — se
     ...
      114  ### DT-001 — Dinheiro em `Decimal` lido direto do texto JSON
      115  
      116  **Contexto:** RN-003 exige arredondar a metade afastando do ze
           ro e cálculos exatos ao centavo; `valor_informado` é o número 
           recebido (33.333).
      117 -**Decisão:** o JSON é lido com `simplejson.loads(..., use_deci
          -mal=True)`, então todo número com parte decimal chega como `De
          -cimal` construído do texto; inteiros também, via `parse_int=De
          -cimal` (evita o limite de 4.300 dígitos na conversão de texto 
          -para `int` do Python). `valor` com `abs(valor) >= VALOR_ABSOLU
          -TO_MAXIMO` é `entrada_invalida` (RN-002) — comparação exata en
          -tre `Decimal`, válida para qualquer expoente. `valor_considera
          -do = valor_informado.quantize(Decimal("0.01"), ROUND_HALF_UP)`
          -. Toda conta (saldo do limite, totais) é feita entre `Decimal`
          - já quantizados, então soma e subtração são exatas. A saída es
          -creve `Decimal` como número JSON (`use_decimal=True`).        
      117 +**Decisão:** o JSON é lido com `simplejson.loads(..., use_deci
          +mal=True)`, então todo número com parte decimal chega como `De
          +cimal` construído do texto, ou seja, com o valor decimal exato
          + escrito no arquivo (seção 4 da spec); inteiros também, via `p
          +arse_int=Decimal` (evita o limite de 4.300 dígitos na conversã
          +o de texto para `int` do Python). `valor` com `abs(valor) >= V
          +ALOR_ABSOLUTO_MAXIMO` é `entrada_invalida` (RN-002) — comparaç
          +ão exata entre `Decimal`, válida para qualquer expoente. `valo
          +r_considerado = valor_informado.quantize(Decimal("0.01"), ROUN
          +D_HALF_UP)`. Toda conta (saldo do limite, totais) é feita entr
          +e `Decimal` já quantizados, então soma e subtração são exatas.
          + A saída escreve `Decimal` como número JSON (`use_decimal=True
          +`).                                                           
      118  **Alternativa descartada:** `float` com arredondamento no fim 
           (`round(1.005, 2) == 1.0`), e `json` padrão com conversão para
            `float` só na saída (perde dígitos de `valor_informado`).
      119  **Consequência:** fácil garantir a RN-003 e os totais da seção
            9 ao centavo. Com o teto da RN-002, todo valor aceito tem no 
           máximo 12 dígitos depois de quantizado, e as somas cabem com f
           olga na precisão padrão do `Decimal` (28 dígitos): nenhuma con
           ta arredonda em silêncio nem levanta `InvalidOperation`. Exige
            cuidado para nunca misturar `float` (proibido em `motor.py`; 
           um teste de propriedade verifica que nenhum campo monetário da
            saída é `float`). A forma escrita na saída pode diferir da en
           trada (`72.50` → `72.5`, ou `45.00` → `45.00`), o que a spec p
           ermite (seção 4: "como veio" é o valor numérico).
      120  
     ...
      183  ### DT-010 — Chaves repetidas pelo `object_pairs_hook`
      184  
      185  **Contexto:** RN-013: vale a última ocorrência de uma chave re
           petida, com aviso de texto fixo, caminho e ordem definidos. Um
            `dict` comum descarta as ocorrências anteriores sem deixar ra
           stro.
      186 -**Decisão:** o `object_pairs_hook` monta cada objeto como `Obj
          -etoJson` (subclasse de `dict`, preenchido pela última ocorrênc
          -ia), que guarda também a lista original de pares. Depois do pa
          -rse, `entrada.py` percorre o documento seguindo essa lista: ao
          - passar pela **primeira** ocorrência de uma chave repetida, em
          -ite o aviso; desce só no valor da ocorrência que valeu. Assim 
          -os avisos saem na ordem do arquivo, e valores descartados nunc
          -a são visitados. O percurso começa em cada elemento de `despes
          -as` com caminho relativo (avisos do item) e no restante com ca
          -minho a partir da raiz (avisos do topo).                      
      186 +**Decisão:** o `object_pairs_hook` monta cada objeto como `Obj
          +etoJson` (subclasse de `dict`, preenchido pela última ocorrênc
          +ia), que guarda também a lista original de pares. Depois do pa
          +rse, `entrada.py` percorre o documento seguindo essa lista: ao
          + passar pela **primeira** ocorrência de uma chave repetida, em
          +ite o aviso; desce só no valor da ocorrência que valeu. Assim 
          +os avisos saem na ordem do arquivo, e valores descartados nunc
          +a são visitados. O percurso começa em cada elemento de `despes
          +as` com caminho relativo (avisos do item; elemento que é lista
          + começa por `[i]`) e no restante com caminho a partir da raiz 
          +(avisos do topo). As chaves comparadas são as `str` já decodif
          +icadas pelo parser, sem `unicodedata.normalize` (RN-013); como
          + o percurso só desce no valor que valeu, ocorrências dentro de
          + valores descartados não entram no `<n>` nem na ordem.        
      187  **Alternativa descartada:** detectar repetição no texto bruto 
           com expressão regular ou um tokenizador próprio — reescreveria
            o parser; e `parse` padrão + segunda leitura: duas fontes da 
           verdade para o mesmo arquivo.
      188  **Consequência:** o resto do código vê `dict` comum; a RN-013 
           fica inteira em `entrada.py`, testável com strings JSON curtas
           .
      189  
  ⎿  Updated specs/001-motor-reembolso/spec.md (+14 -7)
      1  # Spec — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.4 · **Status:** aprovada para planejamento · **Últ
        -ima alteração:** 2026-10-01 (ver `DECISIONS.md` D-001 a D-004)  
      3 +**Versão:** 1.5 · **Status:** aprovada para planejamento · **Últ
        +ima alteração:** 2026-10-01 (ver `DECISIONS.md` D-001 a D-004)  
      4  
      5  > **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ
         . Nenhuma linha
      6  > aqui pode citar linguagem, biblioteca, classe, função ou estru
         tura de pasta.
     ...
      91  | `totais.valor_glosado` | número | `valor_solicitado − valor_r
          eembolsado` |
      92  | `avisos` | lista de textos | avisos de chave repetida fora da
          s despesas (RN-013); lista vazia se não houver |
      93  
      94 -Todos os valores monetários **calculados** da saída (`valor_con
         -siderado`, `valor_reembolsado`, `limite_diario` e totais) são e
         -m reais, com no máximo 2 casas decimais e exatos ao centavo. `v
         -alor_informado` é a única exceção: é a cópia do número recebido
         - (ex.: 33.333). Como a entrada é um número, "como veio" se refe
         -re ao valor numérico, não à forma escrita (72.50 e 72.5 são o m
         -esmo valor).                                                   
      94 +Todos os valores monetários **calculados** da saída (`valor_con
         +siderado`, `valor_reembolsado`, `limite_diario` e totais) são e
         +m reais, com no máximo 2 casas decimais e exatos ao centavo. `v
         +alor_informado` é a única exceção: é a cópia do número recebido
         + (ex.: 33.333). Todo número da entrada vale pelo seu **valor de
         +cimal exato, como escrito no arquivo**, com qualquer quantidade
         + de dígitos e qualquer expoente, nunca por uma aproximação: é s
         +obre esse valor que se aplicam o teto (RN-002), o arredondament
         +o (RN-003) e a cópia em `valor_informado`. "Como veio" se refer
         +e ao valor numérico, não à forma escrita (72.50 e 72.5 são o me
         +smo valor; 1e999999 pode sair escrito como 1E+999999).         
      95  
      96  **Códigos de motivo** (na ordem das etapas da seção 8):
      97  
     ...
      160  
      161  ### RN-003 — Arredondamento ao centavo
      162  
      163 -**Regra:** antes de qualquer outra regra de valor, `valor` é a
          -rredondado para 2 casas decimais, com a metade arredondada afa
          -stando do zero (0,005 → 0,01; -0,005 → -0,01). Todas as regras
          - usam o valor arredondado (`valor_considerado`), e todos os cá
          -lculos são exatos ao centavo.                                 
      163 +**Regra:** antes de qualquer outra regra de valor, `valor` (pe
          +lo seu valor decimal exato, seção 4) é arredondado para 2 casa
          +s decimais, com a metade arredondada afastando do zero (0,005 
          +→ 0,01; -0,005 → -0,01). Todas as regras usam o valor arredond
          +ado (`valor_considerado`), e todos os cálculos são exatos ao c
          +entavo.                                                       
      164  **Origem:** AMB-014.
      165  **Aceite:** `valor` 33.333 → `valor_considerado` 33.33; `valor
           ` 10.005 → 10.01; `valor` 10.004 → 10.00.
      166  
     ...
      234  
      235  - Chave repetida dentro de um elemento de `despesas`, em qualq
           uer profundidade → aviso em `itens[].avisos` daquele item, com
            o caminho a partir da despesa (ex.: `valor`, `extra.obs`).
      236  - Qualquer outra → aviso em `avisos` do topo da saída, com o c
           aminho a partir da raiz (ex.: `colaborador.nome`, `periodo.ini
           cio`, `despesas`).
      237 -- Caminho: chaves separadas por ponto; elemento de lista indic
          -ado pela posição, a partir de 0, entre colchetes (ex.: `extra.
          -lista[0].x`).                                                 
      237 +- Caminho: chaves separadas por ponto; elemento de lista indic
          +ado pela posição, a partir de 0, entre colchetes (ex.: `extra.
          +lista[0].x`). Se o elemento de `despesas` é uma lista, o camin
          +ho começa pela posição (ex.: `[0].a`). As chaves aparecem como
          + texto, sem aspas nem escape (risco aceito, seção 10).        
      238 +- Igualdade de chaves: compara o texto **depois** de decodific
          +ados os escapes do arquivo (`"\u0076alor"` é a chave `valor`),
          + caractere a caractere, sem normalização Unicode (a forma comp
          +osta e a decomposta de uma letra acentuada são chaves diferent
          +es). O caminho usa o texto decodificado.                      
      239  - Ordem dos avisos de cada lista: a ordem em que a primeira oc
           orrência de cada chave repetida aparece no arquivo.
      239 -- Só geram aviso os objetos que continuam no arquivo depois de
          - aplicada a última ocorrência: chaves repetidas dentro de um v
          -alor descartado não geram aviso.                              
      240 +- Só geram aviso os objetos que continuam no arquivo depois de
          + aplicada a última ocorrência: chaves repetidas dentro de um v
          +alor descartado não geram aviso, nem entram no `<n>` nem na or
          +dem de avisos de chaves com o mesmo caminho no valor que valeu
          +.                                                             
      241  - O aviso não muda status, motivo nem valores, e aparece em qu
           alquer item, inclusive recusado. Em erro de arquivo não há saí
           da, logo não há aviso.
      242  
      243  **Origem:** necessidade operacional (a política não trata o fo
           rmato do arquivo); AMB-019.
      243 -**Aceite:** despesa com `"valor": 30.00` e depois `"valor": 50
          -.00` → avaliada com 50,00; `itens[].avisos` = [`chave repetida
          -: valor (2 ocorrências; valeu a última)`]. `colaborador.nome` 
          -repetido → `avisos` do topo = [`chave repetida: colaborador.no
          -me (2 ocorrências; valeu a última)`]; itens sem chave repetida
          - têm `avisos` vazio. Despesa com `"tem_nota_fiscal": true` e d
          -epois `"tem_nota_fiscal": "sim"` → `entrada_invalida`, com o a
          -viso de `tem_nota_fiscal`. `despesas` repetida na raiz → só a 
          -última lista é avaliada; um aviso `chave repetida: despesas (2
          - ocorrências; valeu a última)` no topo; chaves repetidas dentr
          -o da primeira lista não geram aviso. Chave `valor` três vezes 
          -→ um aviso, com `3 ocorrências`.                              
      244 +**Aceite:** despesa com `"valor": 30.00` e depois `"valor": 50
          +.00` → avaliada com 50,00; `itens[].avisos` = [`chave repetida
          +: valor (2 ocorrências; valeu a última)`]. `colaborador.nome` 
          +repetido → `avisos` do topo = [`chave repetida: colaborador.no
          +me (2 ocorrências; valeu a última)`]; itens sem chave repetida
          + têm `avisos` vazio. Despesa com `"tem_nota_fiscal": true` e d
          +epois `"tem_nota_fiscal": "sim"` → `entrada_invalida`, com o a
          +viso de `tem_nota_fiscal`. `despesas` repetida na raiz → só a 
          +última lista é avaliada; um aviso `chave repetida: despesas (2
          + ocorrências; valeu a última)` no topo; chaves repetidas dentr
          +o da primeira lista não geram aviso. Chave `valor` três vezes 
          +→ um aviso, com `3 ocorrências`. Despesa com `"extra": {"x": 1
          +, "x": 2}, "obs": "a", "obs": "b", "extra": {"x": 3, "x": 4}` 
          +→ avisos, nesta ordem: `extra` (2), `obs` (2), `extra.x` (2). 
          +Alimentação fora de viagem com `"valor": 30.00` e depois `"\u0
          +076alor": 90.00` → vale 90,00, `parcial` com 60,00, aviso de `
          +valor`.                                                       
      245  
      246  ---
      247  
     … 21 more lines (ctrl+o to expand)

⏺ Spec, D-004 e plano atualizados. Disparo a nova rodada do spec-adversary, só
  sobre os pontos 3 a 6.

⏺ spec-adversary(Revisão adversarial spec 1.5)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

⏺ Apliquei as 4 recomendações. A spec agora está na versão 1.5, e a D-004 passou
  a registrar a mudança de 1.3 para 1.5. Ainda não fiz commit.

  O que mudou na spec
  1. Número exato: todo número da entrada vale pelo seu valor decimal exato,
     como está escrito no arquivo, com qualquer quantidade de dígitos e qualquer
     expoente. O teto, o arredondamento e o valor_informado usam esse valor. Os
     casos de borda agora dizem o valor_informado esperado para 1e999999 e
     1e-999999. Também incluí o caso 999999999.99999999999: fica abaixo do teto
     e segue.
  2. Avisos de chave aninhada: só contam as ocorrências dentro do valor que
     valeu. No exemplo do revisor, a ordem dos avisos fica extra, obs, extra.x,
     cada um com 2 ocorrências.
  3. Caminho do aviso: quando o elemento de despesas é uma lista, o caminho
     começa pela posição (ex.: [0].a). As chaves aparecem sem escape. Registrei
     como risco aceito na seção 10 que isso pode gerar caminhos iguais para
     chaves diferentes.
  4. Igualdade de chaves: a comparação é feita depois de decodificar os escapes,
     então "\u0076alor" é a chave valor. Não há normalização Unicode. O caminho
     do aviso usa o texto decodificado.

  Somei mais 5 casos de borda na seção 7; com a 1.4, a D-004 soma 12. O
  resultado esperado do arquivo de exemplo continua igual. No plan.md, atualizei
  a DT-001 e a DT-010 e mudei a referência para a spec 1.5.

  A nova rodada do spec-adversary está rodando, só sobre esses 4 pontos. Também
  pedi que ele confira os valores esperados dos casos de borda novos. Quando ele
  terminar, trago o resultado aqui. Se não houver bloqueante, faço os commits
  docs(spec) e docs(plan).

✻ Churned for 1m 2s · done 10:15 PM

❯ ok, me avisa quando terminar                                                  

⏺ Combinado. Quando a nova rodada do spec-adversary sobre a 1.5 terminar, trago
  aqui os problemas que ele apontar, com os bloqueantes primeiro, ou aviso se
  ele não encontrar nada. Até lá não faço nenhum commit.

✻ Churned for 2s · done 10:16 PM

› Message from spec-adversary
  Resumo: 4 problemas, nenhum bloqueante. Os pontos 3 a 6 da D-004 estão
  refletidos na spec 1.5. Os 12 casos de borda novos da seção 7 (linhas 456 a
  467) batem com as regras.

  **Conferência dos casos de borda novos (seção 7):** todos os valores esperados
  que conferi à mão estão corretos.
  - 999999999.995 e 999999999.99999999999: ficam abaixo do teto pelo valor exato
  e arredondam para 1000000000.00. Como são hospedagem com nota, saem `parcial`
  com 250,00.
  - 1e999999 e -1e12: `entrada_invalida`.
  - 1e-999999: arredonda para 0,00 e sai `valor_invalido`.
  - `valor` 90,00 em alimentação fora de viagem: limite 60,00, sai `parcial` com
  60,00, com aviso `valor`.
  - Ordem `extra`, `obs`, `extra.x`: confere com a regra da "primeira
  ocorrência" combinada com a exclusão do valor descartado.
  - `[0].a`: confere.

  A contagem de 12 linhas novas registrada na D-004 confere. As seções citadas
  em cada ponto da D-004 estão de fato alteradas.

  ---

  ### 1. Escape de "surrogate" isolado (`\ud800`) em chave ou em texto — PODE
  ESPERAR — lacuna

  - **Regra afetada:** RN-013 (igualdade "depois de decodificados os escapes",
  caractere a caractere), RN-002 ("não é JSON válido"), seção 4
  (`id`/`categoria` copiados "como veio").
  - **Cenário de entrada:** despesa
  `{"id":"d-1","data":"2026-07-03","categoria":"alimentacao","fornecedor":"X\ud8
  00","valor":30.00,"tem_nota_fiscal":true,"\ud800":1,"\ud800":2}`.
  - **Comportamento pela interpretação atual:** indefinido. A decodificação de
  `\ud800` não gera um caractere Unicode válido. A spec permite três leituras:
    - (a) é JSON inválido e vira erro de arquivo;
    - (b) é texto válido: a despesa é aprovada e a saída leva o aviso `chave
  repetida: <surrogate> (2 ...)`;
    - (c) `fornecedor` não é texto e a despesa vira `entrada_invalida`.

    "Caractere a caractere" também não diz se a unidade é ponto de código ou
  unidade de codificação. Isso importa para `😀` (par de escapes) contra o emoji
  escrito direto no arquivo.
  - **Por que é um problema:** na leitura (b), o texto copiado para
  `itens[].id`/`fornecedor` ou para o caminho do aviso pode não ser gravável
  como UTF-8. A gravação falharia e a execução inteira cairia. O ponto 1 da
  D-004 foi decidido justamente para evitar que uma despesa derrube a execução.
  Mesmo sendo improvável, é uma entrada válida pela sintaxe do JSON sem
  resultado definido.
  - **Pergunta para decisão:** um escape `\uD800`–`\uDFFF` sem par, em chave ou
  em valor de texto, é erro de arquivo, `entrada_invalida` da despesa ou texto
  aceito? E, no último caso, como ele aparece na saída?

  ### 2. Decodificação de escapes definida só para chaves, não para valores de
  texto — PODE ESPERAR — ambiguidade

  - **Regra afetada:** RN-013 (o ponto 6 fala só de chaves), seção 4 ("como
  veio" é esclarecido só para números), RN-002 (data `AAAA-MM-DD`), RN-007
  (mesma `data`).
  - **Cenário de entrada:** duas despesas iguais, só com a `data` escrita de
  forma diferente: d-1 com `"data":"2026-07-03"`, d-2 com `"data":"2026-07-03"`.
  Ambas em alimentação, mesmo fornecedor, 30,00, com nota. Variante:
  `"id":"d-1"`.
  - **Comportamento pela interpretação atual:** indefinido.
    - Se os valores também são decodificados: d-2 tem data válida e é
  `duplicata` de d-1. O `id` sai `d-1`.
    - Se não são: a data de d-2 não segue `AAAA-MM-DD` e d-2 vira
  `entrada_invalida`. O `id` sairia com a barra invertida literal.

    O passo 3 da normalização cobre a codificação só de letras acentuadas em
  categoria e fornecedor. Não cobre `data`, `id` nem outros caracteres.
  - **Por que é um problema:** ao dizer explicitamente "depois de decodificados"
  só para chaves, o ponto 6 abre espaço para ler o contrário nos valores.
  Também deixa sem definição o que "como veio" significa para texto.
  - **Pergunta para decisão:** nos valores de texto (`id`, `data`, `categoria`,
  `fornecedor`, `competencia`), as regras e as cópias "como veio" usam o texto
  depois de decodificados os escapes, como nas chaves?

  ### 3. Texto exato do aviso não fica determinado em dois pontos — PODE ESPERAR
  — ambiguidade

  - **Regra afetada:** RN-013 (formato do caminho e do `<n>`; o texto é
  contratual).
  - **Cenário de entrada:**
    - (a) despesa com `"m": [[{"x":1,"x":2}]]`. Ou elemento de `despesas` igual
  a `[[{"a":1,"a":2}]]`.
    - (b) uma despesa com a chave `"obs"` repetida 1000 vezes.
  - **Comportamento pela interpretação atual:**
    - (a) Os exemplos só mostram colchete depois de chave (`lista[0].x`) e chave
  depois de colchete (`[0].a`). Para lista dentro de lista, a spec permite
  `m[0][0].x` ou `m[0].[0].x`, e também `[0][0].a` ou `[0].[0].a`.
    - (b) O texto pode ser `1000 ocorrências` ou `1.000 ocorrências`. A spec usa
  separador de milhar em português nos valores em prosa, mas não diz nada sobre
  o `<n>`.
    - Relacionado: "sem aspas nem escape" pode ser lido como "não fazer escape
  em nível de caminho" ou como "gravar caracteres não ASCII e de controle sem o
  escape do JSON na saída". A segunda leitura é impossível para quebra de linha.
  A codificação do arquivo de saída não está definida.
  - **Por que é um problema:** o aviso é contratual e tem "texto exato". Duas
  implementações corretas podem gerar textos diferentes, e um teste de aceitação
  comparando texto falharia em uma delas.
  - **Pergunta para decisão:** qual é a forma do caminho quando uma lista está
  dentro de outra lista? Como o `<n>` é escrito a partir de 1000? "Sem escape"
  se refere só ao caminho ou também à serialização da saída?

  ### 4. A justificativa do risco aceito "caminho ambíguo" está incompleta —
  PODE ESPERAR — brecha

  - **Regra afetada:** RN-013, seção 10 (risco "Caminho ambíguo no aviso de
  chave repetida").
  - **Cenário de entrada:** na raiz, `"periodo":
  {"inicio":"2026-07-01","fim":"2026-07-31"}`, mais a chave extra
  `"periodo.inicio":"x"` repetida duas vezes. Variante: chave extra `"obs\n(5
  ocorrências; valeu a última)"` repetida.
  - **Comportamento pela interpretação atual:** `avisos` do topo recebe `chave
  repetida: periodo.inicio (2 ocorrências; valeu a última)`. É o mesmo texto que
  sairia se o `periodo.inicio` verdadeiro tivesse sido repetido e trocado. Na
  variante, o aviso contém uma quebra de linha e um trecho que imita o formato
  do próprio aviso.
  - **Por que é um problema:** a seção 10 diz que a ambiguidade "só acontece com
  campos extras, que já são ignorados; os campos da seção 4 têm nomes simples".
  O cenário mostra que um campo extra pode gerar um aviso idêntico ao de um
  campo da seção 4 que mexe no cálculo (`periodo.inicio`, `periodo.fim`,
  `colaborador.nome`/`id`). Isso induz o conferente a crer que um dado relevante
  foi trocado, ou esconde um descarte real entre avisos falsos. A regra não
  muda nenhum valor. O que fica impreciso é a descrição do risco aceito, como
  aconteceu no ponto 2 da D-002.
  - **Pergunta para decisão:** o risco aceito inclui avisos de campo extra com
  texto idêntico ao de um campo da seção 4 (e chaves com quebra de linha ou que
  imitam o formato do aviso)? Se inclui, a descrição da seção 10 deve dizer
  isso?

  ---

  **Decidir antes da implementação:** nenhum. Não há bloqueante.

  **Pode ser decidido depois:** 1, 2, 3, 4.

  Arquivos revisados (somente leitura):
  - /Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/spec.md
  - /Users/rafaeltxm/repo/sdd-desafio/specs/001-motor-reembolso/DECISIONS.md

⏺ A segunda rodada do spec-adversary, sobre a 1.5, terminou: nenhum bloqueante.
  Ele refez à mão as contas dos 12 casos de borda novos e todas batem com as
  regras. Apontou 4 problemas que podem esperar. Abaixo, cada um com a minha
  recomendação.

  1. Escape de caractere inválido (\ud800 sozinho)

  Esse escape não forma um caractere de verdade. A spec não diz se ele torna o
  arquivo inválido, se invalida a despesa ou se é aceito como texto. Se for
  aceito, a saída pode não conseguir gravá-lo, e a execução inteira cairia.

  Recomendação: tratar como erro de arquivo, em chave ou em valor. É texto que
  não dá para representar, e assim o comportamento fica definido em qualquer
  posição. Também deixar explícito que "caractere" quer dizer o caractere
  Unicode: um emoji escrito em escapes é igual ao mesmo emoji escrito direto.

  2. Escapes decodificados só nas chaves, não nos valores de texto

  O ponto 6 diz que as chaves são comparadas depois de decodificar os escapes,
  mas não diz o mesmo para os valores. Por exemplo, uma data escrita com \u002d
  no lugar do hífen poderia ser lida como válida e repetida, ou como
  entrada_invalida. No relatório, os escapes do exemplo dele apareceram já
  convertidos, por isso as duas datas parecem iguais.

  Recomendação: uma frase geral na seção 4: todo texto da entrada, chave ou 
  valor, vale pelo seu conteúdo depois de decodificados os escapes. É o que o
  JSON define e o que o leitor já faz.

  3. O texto do aviso ainda não é exato em dois pontos

  - Lista dentro de lista: a spec não diz se o caminho é m[0][0].x ou
    m[0].[0].x.
  - <n> a partir de 1000: a spec não diz se sai 1000 ou 1.000.
  - "Sem escape": não está claro se vale só para o caminho ou também para a
    gravação da saída.

  Recomendação:
  - colchetes encadeados sem ponto: m[0][0].x e [0][0].a;
  - <n> só com algarismos, sem separador de milhar: 1000;
  - "sem escape" se refere só ao caminho. A saída é gravada em UTF-8, com os
    escapes que o JSON exige (uma quebra de linha numa chave sai como \n). Isso
    também deixa definida a codificação do arquivo de saída na spec.

  4. A descrição do risco aceito do caminho ambíguo está incompleta

  A seção 10 diz que a ambiguidade só acontece com campos extras. Mas uma chave
  extra chamada "periodo.inicio" e repetida gera exatamente o mesmo aviso que o
  periodo.inicio verdadeiro geraria, e esse campo entra no cálculo. Uma chave
  com quebra de linha também pode imitar o formato do próprio aviso. Nenhum
  valor muda, mas o conferente pode ser enganado.

  Recomendação: manter o risco aceito e reescrever a descrição para incluir
  esses dois casos, para não repetir o erro de justificativa da D-002.

  ---

  São 4 ajustes pequenos de texto, sem mudança de regra de cálculo. Tenho duas
  opções:
  - (a) aplicar agora como spec 1.6, ainda dentro da D-004, já que nada foi
    commitado, e depois fazer os commits docs(spec) e docs(plan) sem nova rodada
    do revisor;
  - (b) fazer os commits como estão e deixar esses pontos para uma D-005.

  Recomendo (a): é pouco texto, e o tasks.md já nasce sobre uma spec fechada.
  Você aceita as 4 recomendações e a opção (a)?

✻ Cogitated for 21s · done 10:18 PM

⏺ Agent "Revisão adversarial spec 1.5" finished · 2m 46s

❯ aceito as 4 recomendações, opção (a), pode aplicar                            

⏺ Aplico os 4 ajustes como spec 1.6. Antes, confiro como o simplejson decodifica
  um escape sem par e um par de escapes.

  Ran 1 shell command (ctrl+o to expand)

⏺ Confirmado: o parser aceita o \ud800 sozinho sem reclamar, e a gravação em
  UTF-8 falharia depois. O plano vai prever uma verificação explícita para isso.
  Aplico as edições.

⏺ Bash(python3 - <<'EOF'
      p="spec.md"; s=open(p).read()…)
  ⎿   M specs/001-motor-reembolso/DECISIONS.md
      M specs/001-motor-reembolso/plan.md
      M specs/001-motor-reembolso/spec.md
     … +5 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/DECISIONS.md (+10 -6)
      10  
      11  ---
      12  
      13 -## D-004 — Valor gigante e chave repetida: spec 1.3 → 1.5 · `20
         -26-10-01`                                                      
      13 +## D-004 — Valor gigante e chave repetida: spec 1.3 → 1.6 · `20
         +26-10-01`                                                      
      14  
      15 -**Gatilho:** escrita do `plan.md` 1.0. Ao verificar como o códi
         -go leria o arquivo, apareceram duas entradas válidas no formato
         - cujo resultado a spec não definia. O responsável decidiu as du
         -as (versão 1.4, não commitada). A rodada do `spec-adversary` so
         -bre a 1.4 apontou 4 problemas (1 bloqueante) nas próprias decis
         -ões; o responsável aceitou as 4 recomendações, aplicadas na 1.5
         - (pontos 3 a 6). Sessão `docs/sessions/07-*`.                  
      15 +**Gatilho:** escrita do `plan.md` 1.0. Ao verificar como o códi
         +go leria o arquivo, apareceram duas entradas válidas no formato
         + cujo resultado a spec não definia. O responsável decidiu as du
         +as (versão 1.4, não commitada). A rodada do `spec-adversary` so
         +bre a 1.4 apontou 4 problemas (1 bloqueante) nas próprias decis
         +ões; o responsável aceitou as 4 recomendações, aplicadas na 1.5
         + (pontos 3 a 6). A rodada sobre a 1.5 apontou 4 problemas, nenh
         +um bloqueante; o responsável aceitou as 4 recomendações, aplica
         +das na 1.6 (pontos 7 a 10). Sessão `docs/sessions/07-*`.       
      16  
      17  **O que mudou na spec:**
      18  
      19 -| # | Ponto | De (1.3) | Para (1.5) | Onde |                   
      19 +| # | Ponto | De (1.3) | Para (1.6) | Onde |                   
      20  |---|---|---|---|---|
      21  | 1 | `valor` sem limite superior (ex.: 1e999999) | indefinido;
           o cálculo exato ao centavo não é possível para qualquer número
          , e a execução seria interrompida | valor absoluto a partir de 
          1.000.000.000,00, comparado com o número recebido → `entrada_in
          valida` (também se negativo, antes de `valor_invalido`) | RN-00
          2, seção 4 (motivos), AMB-018, seção 7 |
      22  | 2 | Chave repetida num objeto (ex.: dois `valor`) | indefinid
          o; a leitura ficaria com uma delas em silêncio | vale a última 
          ocorrência; cada chave repetida gera aviso com texto fixo em `i
          tens[].avisos` (dentro da despesa) ou `avisos` do topo (fora) |
           RN-013 (nova), seção 4 (entrada e saída), seção 8, AMB-019, se
          ção 7 |
     ...
      24  | 4 | Ordem e contagem de aviso de chave aninhada que também ap
          arece em valor descartado | indefinidas | contam só as ocorrênc
          ias dentro do valor que valeu | RN-013, seção 7 |
      25  | 5 | Caminho do aviso | sem regra para elemento de `despesas` 
          que é lista; chaves com `.`, `[`, `]` ou vazias geram caminhos 
          ambíguos | lista começa pela posição (`[0].a`); chaves sem esca
          pe, ambiguidade registrada como risco aceito | RN-013, seção 10
          , seção 7 |
      26  | 6 | Igualdade de chaves | "caractere a caractere" sem dizer s
          e antes ou depois dos escapes (`"\u0076alor"`) | depois de deco
          dificar os escapes, sem normalização Unicode; caminho usa o tex
          to decodificado | RN-013, seção 7 |
      27 +| 7 | Escape sem caractere válido (`\ud800` sem par) | indefini
         +do; aceito pelo parser, a gravação da saída falharia | erro de 
         +arquivo, em chave ou valor; "caractere" é o caractere Unicode |
         + seção 4, RN-002, seção 7 |                                    
      28 +| 8 | Escapes nos valores de texto | o ponto 6 falava só de cha
         +ves | todo texto da entrada, chave ou valor, vale depois de dec
         +odificados os escapes | seção 4, seção 7 |                     
      29 +| 9 | Texto exato do aviso | lista dentro de lista, `<n>` ≥ 100
         +0 e "sem escape" indefinidos | colchetes encadeados (`m[0][0].x
         +`); `<n>` sem separador de milhar; "sem escape" vale só para o 
         +caminho; saída em UTF-8 com os escapes do formato | RN-013, seç
         +ão 4, seção 7 |                                                
      30 +| 10 | Descrição do risco "caminho ambíguo" | dizia que a ambig
         +uidade só afeta campos extras — **justificativa incompleta da 1
         +.5** | inclui aviso de campo extra idêntico ao de campo da seçã
         +o 4 e chave que imita outro aviso | seção 10 |                 
      31  
      28 -**Por quê:** o ponto 1 deixaria uma despesa derrubar a execução
         - inteira, contra o tratamento por item da RN-002; recusar como 
         -`entrada_invalida` preserva as demais. O ponto 3 fecha o que o 
         -ponto 1 deixou aberto: o teto limita a magnitude, e a leitura e
         -xata garante que o valor aceito é o escrito. O ponto 2 muda o r
         -eembolso conforme a ocorrência escolhida; a última ocorrência f
         -oi a escolhida, e o descarte fica visível ao conferente em camp
         -o contratual, em vez de texto livre na justificativa ou no term
         -inal. Os pontos 4 a 6 tornam o texto e a ordem dos avisos deter
         -minísticos, já que são contratuais; escapar caracteres no camin
         -ho foi descartado para manter o aviso legível.                 
      32 +**Por quê:** o ponto 1 deixaria uma despesa derrubar a execução
         + inteira, contra o tratamento por item da RN-002; recusar como 
         +`entrada_invalida` preserva as demais. O ponto 3 fecha o que o 
         +ponto 1 deixou aberto: o teto limita a magnitude, e a leitura e
         +xata garante que o valor aceito é o escrito. O ponto 2 muda o r
         +eembolso conforme a ocorrência escolhida; a última ocorrência f
         +oi a escolhida, e o descarte fica visível ao conferente em camp
         +o contratual, em vez de texto livre na justificativa ou no term
         +inal. Os pontos 4 a 6 tornam o texto e a ordem dos avisos deter
         +minísticos, já que são contratuais; escapar caracteres no camin
         +ho foi descartado para manter o aviso legível. Os pontos 7 a 9 
         +fecham entradas válidas pela sintaxe sem resultado definido; o 
         +10 corrige a descrição de um risco aceito, como o ponto 2 da D-
         +002.                                                           
      33  
      30 -**O que isso invalidou:** nenhum código ou teste (ainda não exi
         -stem). Formato de saída: dois campos novos (`itens[].avisos`, `
         -avisos`), sempre presentes. Nenhum valor do resultado esperado 
         -do exemplo mudou (seção 9; `avisos` vazios). Casos de borda nov
         -os: 12 linhas na seção 7. Risco aceito novo na seção 10 (caminh
         -o ambíguo). Critério de aceite da seção 9 passa a citar RN-001 
         -a RN-013. `plan.md` passa a se basear na 1.5.                  
      34 +**O que isso invalidou:** nenhum código ou teste (ainda não exi
         +stem). Formato de saída: dois campos novos (`itens[].avisos`, `
         +avisos`), sempre presentes. Nenhum valor do resultado esperado 
         +do exemplo mudou (seção 9; `avisos` vazios). Casos de borda nov
         +os: 16 linhas na seção 7. Risco aceito novo na seção 10 (caminh
         +o ambíguo). Critério de aceite da seção 9 passa a citar RN-001 
         +a RN-013. `plan.md` passa a se basear na 1.6.                  
      35  
      36  **Tasks afetadas:** nenhuma (o `tasks.md` ainda não foi escrito
          ).
      37  
      34 -**Custo:** 3 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`); 6
         - pontos decididos na mesma sessão. Duas rodadas do `spec-advers
         -ary`: sobre a 1.4 (por mudar o formato de saída) e sobre a 1.5 
         -(pontos 3 a 6).                                                
      38 +**Custo:** 3 arquivos (`spec.md`, `DECISIONS.md`, `plan.md`); 1
         +0 pontos decididos na mesma sessão. Duas rodadas do `spec-adver
         +sary`: sobre a 1.4 (por mudar o formato de saída) e sobre a 1.5
         + (pontos 3 a 6). Sem rodada sobre a 1.6: os pontos 7 a 10 são a
         +justes de texto sem mudança de regra de cálculo, recomendados p
         +ela própria rodada da 1.5.                                     
      39  
      40  ---
      41  
  ⎿  Updated specs/001-motor-reembolso/plan.md (+3 -3)
      1  # Plano Técnico — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.0 · **Baseado na spec:** 1.5                      
      3 +**Versão:** 1.0 · **Baseado na spec:** 1.6                      
      4  
      5  > Aqui mora o COMO. Este arquivo pode e deve falar de linguagem,
          biblioteca e
      6  > arquitetura. O que ele **não** pode é introduzir regra de negó
         cio nova — se
     ...
      121  ### DT-002 — Rejeitar o que não é JSON estrito
      122  
      123  **Contexto:** RN-002: arquivo que não é JSON válido é erro de 
           arquivo. O `json` da biblioteca padrão aceita `NaN`, `Infinity
           ` e `-Infinity`, que não são JSON.
      124 -**Decisão:** `simplejson` ≥ 4 já os rejeita na leitura por pad
          -rão (`allow_nan=False`); a versão mínima fica fixada no `pypro
          -ject.toml` e um teste garante que `"valor": NaN` é erro de arq
          -uivo, para a proteção não sumir numa troca de versão. Erro de 
          -parse → `ErroDeArquivo`. Bytes decodificados como UTF-8 estrit
          -o (`utf-8-sig`, aceitando BOM, que a RFC 8259 permite ignorar)
          -; falha de decodificação → `ErroDeArquivo`.                   
      124 +**Decisão:** `simplejson` ≥ 4 já os rejeita na leitura por pad
          +rão (`allow_nan=False`); a versão mínima fica fixada no `pypro
          +ject.toml` e um teste garante que `"valor": NaN` é erro de arq
          +uivo, para a proteção não sumir numa troca de versão. Erro de 
          +parse → `ErroDeArquivo`. Bytes decodificados como UTF-8 estrit
          +o (`utf-8-sig`, aceitando BOM, que a RFC 8259 permite ignorar)
          +; falha de decodificação → `ErroDeArquivo`. O parser aceita em
          + silêncio um escape `\ud800` sem par (vira um caractere substi
          +tuto isolado na `str`, que a gravação em UTF-8 recusaria depoi
          +s); por isso, depois do parse, `entrada.py` percorre todas as 
          +chaves e textos e levanta `ErroDeArquivo` se algum contiver ca
          +ractere entre U+D800 e U+DFFF (seção 4 da spec). Pares de esca
          +pes válidos já chegam combinados num único caractere.         
      125  **Alternativa descartada:** aceitar `NaN` e tratar como "valor
            não é número" na despesa: transformaria arquivo inválido em p
           rocessamento normal.
      126  **Consequência:** `"valor": NaN` encerra a execução sem saída,
            como qualquer JSON inválido.
      127  
     ...
      183  ### DT-010 — Chaves repetidas pelo `object_pairs_hook`
      184  
      185  **Contexto:** RN-013: vale a última ocorrência de uma chave re
           petida, com aviso de texto fixo, caminho e ordem definidos. Um
            `dict` comum descarta as ocorrências anteriores sem deixar ra
           stro.
      186 -**Decisão:** o `object_pairs_hook` monta cada objeto como `Obj
          -etoJson` (subclasse de `dict`, preenchido pela última ocorrênc
          -ia), que guarda também a lista original de pares. Depois do pa
          -rse, `entrada.py` percorre o documento seguindo essa lista: ao
          - passar pela **primeira** ocorrência de uma chave repetida, em
          -ite o aviso; desce só no valor da ocorrência que valeu. Assim 
          -os avisos saem na ordem do arquivo, e valores descartados nunc
          -a são visitados. O percurso começa em cada elemento de `despes
          -as` com caminho relativo (avisos do item; elemento que é lista
          - começa por `[i]`) e no restante com caminho a partir da raiz 
          -(avisos do topo). As chaves comparadas são as `str` já decodif
          -icadas pelo parser, sem `unicodedata.normalize` (RN-013); como
          - o percurso só desce no valor que valeu, ocorrências dentro de
          - valores descartados não entram no `<n>` nem na ordem.        
      186 +**Decisão:** o `object_pairs_hook` monta cada objeto como `Obj
          +etoJson` (subclasse de `dict`, preenchido pela última ocorrênc
          +ia), que guarda também a lista original de pares. Depois do pa
          +rse, `entrada.py` percorre o documento seguindo essa lista: ao
          + passar pela **primeira** ocorrência de uma chave repetida, em
          +ite o aviso; desce só no valor da ocorrência que valeu. Assim 
          +os avisos saem na ordem do arquivo, e valores descartados nunc
          +a são visitados. O percurso começa em cada elemento de `despes
          +as` com caminho relativo (avisos do item; elemento que é lista
          + começa por `[i]`; listas encadeadas viram `[i][j]`) e no rest
          +ante com caminho a partir da raiz (avisos do topo). As chaves 
          +comparadas são as `str` já decodificadas pelo parser, sem `uni
          +codedata.normalize` (RN-013); como o percurso só desce no valo
          +r que valeu, ocorrências dentro de valores descartados não ent
          +ram no `<n>` nem na ordem.                                    
      187  **Alternativa descartada:** detectar repetição no texto bruto 
           com expressão regular ou um tokenizador próprio — reescreveria
            o parser; e `parse` padrão + segunda leitura: duas fontes da 
           verdade para o mesmo arquivo.
      188  **Consequência:** o resto do código vê `dict` comum; a RN-013 
           fica inteira em `entrada.py`, testável com strings JSON curtas
           .
      189  
  ⎿  Updated specs/001-motor-reembolso/spec.md (+14 -5)
      1  # Spec — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.5 · **Status:** aprovada para planejamento · **Últ
        -ima alteração:** 2026-10-01 (ver `DECISIONS.md` D-001 a D-004)  
      3 +**Versão:** 1.6 · **Status:** aprovada para planejamento · **Últ
        +ima alteração:** 2026-10-01 (ver `DECISIONS.md` D-001 a D-004)  
      4  
      5  > **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ
         . Nenhuma linha
      6  > aqui pode citar linguagem, biblioteca, classe, função ou estru
         tura de pasta.
     ...
      67  
      68  Se um mesmo objeto do arquivo traz a mesma chave mais de uma ve
          z, vale a última ocorrência, e a saída avisa que as anteriores 
          foram descartadas (RN-013).
      69  
      70 +Todo texto da entrada, chave ou valor, vale pelo seu conteúdo *
         +*depois de decodificados os escapes** do arquivo (`"2026\u002d0
         +7\u002d03"` é a data `2026-07-03`), e "caractere" é o caractere
         + Unicode (um emoji escrito como par de escapes é igual ao mesmo
         + emoji escrito diretamente). Um escape que não forma caractere 
         +Unicode válido (`\uD800` a `\uDFFF` sem o par correspondente), 
         +em qualquer chave ou valor, é erro de arquivo (RN-002).        
      71 +                                                               
      72  ### Saída
      73  
      74  | Campo | Tipo | Significado |
     ...
       93  | `totais.valor_glosado` | número | `valor_solicitado − valor_
           reembolsado` |
       94  | `avisos` | lista de textos | avisos de chave repetida fora d
           as despesas (RN-013); lista vazia se não houver |
       95  
       94 -Todos os valores monetários **calculados** da saída (`valor_co
          -nsiderado`, `valor_reembolsado`, `limite_diario` e totais) são
          - em reais, com no máximo 2 casas decimais e exatos ao centavo.
          - `valor_informado` é a única exceção: é a cópia do número rece
          -bido (ex.: 33.333). Todo número da entrada vale pelo seu **val
          -or decimal exato, como escrito no arquivo**, com qualquer quan
          -tidade de dígitos e qualquer expoente, nunca por uma aproximaç
          -ão: é sobre esse valor que se aplicam o teto (RN-002), o arred
          -ondamento (RN-003) e a cópia em `valor_informado`. "Como veio"
          - se refere ao valor numérico, não à forma escrita (72.50 e 72.
          -5 são o mesmo valor; 1e999999 pode sair escrito como 1E+999999
          -).                                                            
       96 +Todos os valores monetários **calculados** da saída (`valor_co
          +nsiderado`, `valor_reembolsado`, `limite_diario` e totais) são
          + em reais, com no máximo 2 casas decimais e exatos ao centavo.
          + `valor_informado` é a única exceção: é a cópia do número rece
          +bido (ex.: 33.333). O arquivo de saída é gravado em UTF-8, com
          + os escapes que o formato exige (uma quebra de linha dentro de
          + um texto sai como `\n`).                                     
       97 +                                                              
       98 +Todo número da entrada vale pelo seu **valor decimal exato, co
          +mo escrito no arquivo**, com qualquer quantidade de dígitos e 
          +qualquer expoente, nunca por uma aproximação: é sobre esse val
          +or que se aplicam o teto (RN-002), o arredondamento (RN-003) e
          + a cópia em `valor_informado`. "Como veio" se refere ao valor 
          +numérico, não à forma escrita (72.50 e 72.5 são o mesmo valor;
          + 1e999999 pode sair escrito como 1E+999999).                  
       99  
      100  **Códigos de motivo** (na ordem das etapas da seção 8):
      101  
     ...
      154  ### RN-002 — Validação da entrada
      155  
      156  **Regra:**
      153 -- **Erro de arquivo** (o arquivo de saída não é criado nem alt
          -erado): arquivo de entrada ausente ou que não é JSON válido; `
          -colaborador` ausente ou sem `id`/`nome` em texto, ou com `id`/
          -`nome` vazio ou só com espaços em branco; `periodo.inicio`, `p
          -eriodo.fim` ou `despesas` ausentes; `inicio` ou `fim` que não 
          -são datas válidas `AAAA-MM-DD`; `inicio` posterior a `fim`; `d
          -espesas` que não é lista; arquivo de saída que não pode ser gr
          -avado. `periodo.competencia` nunca causa erro: se não for text
          -o, sai nula.                                                  
      157 +- **Erro de arquivo** (o arquivo de saída não é criado nem alt
          +erado): arquivo de entrada ausente ou que não é JSON válido; t
          +exto, em chave ou valor, com escape que não forma caractere Un
          +icode válido (seção 4); `colaborador` ausente ou sem `id`/`nom
          +e` em texto, ou com `id`/`nome` vazio ou só com espaços em bra
          +nco; `periodo.inicio`, `periodo.fim` ou `despesas` ausentes; `
          +inicio` ou `fim` que não são datas válidas `AAAA-MM-DD`; `inic
          +io` posterior a `fim`; `despesas` que não é lista; arquivo de 
          +saída que não pode ser gravado. `periodo.competencia` nunca ca
          +usa erro: se não for texto, sai nula.                         
      158  - **Despesa inválida** (vira item `recusado` com motivo `entra
           da_invalida`; as demais despesas seguem): elemento de `despesa
           s` que não é um objeto; falta `id`, `data`, `categoria`, `forn
           ecedor`, `valor` ou `tem_nota_fiscal`; `data` não é data válid
           a `AAAA-MM-DD`; `valor` não é número; `tem_nota_fiscal` não é 
           booleano; `id`, `categoria` ou `fornecedor` não são texto, ou 
           são texto vazio ou só com espaços em branco; `valor` com valor
            absoluto maior ou igual a 1.000.000.000,00 (um bilhão), compa
           rado com o número recebido, antes do arredondamento (AMB-018).
      159  - Na saída de uma despesa inválida, `id`, `data` e `categoria`
            são copiados se forem texto e saem nulos caso contrário (tipo
            errado, ausente ou elemento que não é objeto); a `categoria`,
            se reconhecida, sai normalizada, como em qualquer item (seção
            4).
      160  - Uma despesa recusada por `entrada_invalida` tem `valor_consi
           derado` nulo, `em_viagem` e `limite_diario` nulos, e não entra
            nos totais.
     ...
      238  
      239  - Chave repetida dentro de um elemento de `despesas`, em qualq
           uer profundidade → aviso em `itens[].avisos` daquele item, com
            o caminho a partir da despesa (ex.: `valor`, `extra.obs`).
      240  - Qualquer outra → aviso em `avisos` do topo da saída, com o c
           aminho a partir da raiz (ex.: `colaborador.nome`, `periodo.ini
           cio`, `despesas`).
      237 -- Caminho: chaves separadas por ponto; elemento de lista indic
          -ado pela posição, a partir de 0, entre colchetes (ex.: `extra.
          -lista[0].x`). Se o elemento de `despesas` é uma lista, o camin
          -ho começa pela posição (ex.: `[0].a`). As chaves aparecem como
          - texto, sem aspas nem escape (risco aceito, seção 10).        
      241 +- Caminho: chaves separadas por ponto; elemento de lista indic
          +ado pela posição, a partir de 0, entre colchetes (ex.: `extra.
          +lista[0].x`). Se o elemento de `despesas` é uma lista, o camin
          +ho começa pela posição (ex.: `[0].a`). Lista dentro de lista: 
          +colchetes encadeados, sem ponto entre eles (ex.: `m[0][0].x`, 
          +`[0][0].a`). As chaves aparecem no caminho como texto, sem asp
          +as nem escape (risco aceito, seção 10); a gravação do aviso no
          + arquivo de saída segue a seção 4.                            
      242 +- `<n>`: em algarismos, sem separador de milhar (ex.: `1000 oc
          +orrências`).                                                  
      243  - Igualdade de chaves: compara o texto **depois** de decodific
           ados os escapes do arquivo (`"\u0076alor"` é a chave `valor`),
            caractere a caractere, sem normalização Unicode (a forma comp
           osta e a decomposta de uma letra acentuada são chaves diferent
           es). O caminho usa o texto decodificado.
     … 24 more lines (ctrl+o to expand)

⏺ Commit da spec e da D-004 primeiro, depois o do plano.

  Ran 1 shell command (ctrl+o to expand)
  ⎿  PostToolUse:Bash says: 📝 Fim do bloco de trabalho ("docs(plan): plano 
     técnico 1.0 sobre a spec 1.6"). Exporte a sessão antes de continuar:
        /export docs/sessions/07-<descricao-curta>.md
        e commite com: docs(sessions): export da sessão 07

⏺ Apliquei os 4 ajustes (spec 1.6) e fiz os dois commits locais. Não enviei para
  o GitHub.

  - 1eb808c docs(spec): a spec vai da 1.3 direto para a 1.6, e a D-004 registra
    os 10 pontos decididos nesta sessão. Os ajustes desta última rodada foram:
    - Escape sem caractere válido (\ud800 sozinho), em chave ou em valor: vira
      erro de arquivo.
    - Escapes em todo texto da entrada: chaves e valores valem pelo conteúdo
      depois de decodificar os escapes. "Caractere" quer dizer caractere
      Unicode.
    - Texto do aviso: lista dentro de lista fica m[0][0].x, e o <n> sai sem
      separador de milhar (1000). O "sem escape" vale só para o caminho. O
      arquivo de saída é gravado em UTF-8, com os escapes que o JSON exige.
    - Risco do caminho ambíguo: a descrição agora inclui o aviso de um campo
      extra que fica idêntico ao de um campo da seção 4, e a chave que imita
      outro aviso.
    - Somei mais 4 casos de borda; a D-004 soma 16 no total. O resultado
      esperado do arquivo de exemplo não mudou.
  - bf1df44 docs(plan): o plano técnico 1.0, baseado na spec 1.6. Ao conferir,
    vi que o leitor de JSON aceita o \ud800 sozinho sem reclamar e que a
    gravação em UTF-8 falharia depois. Por isso o plano prevê uma verificação
    explícita de todos os textos logo depois da leitura.

  Não rodei o spec-adversary sobre a 1.6. Os ajustes só mudam texto, nenhuma
  regra de cálculo, e vieram da própria rodada da 1.5. Isso está registrado na
  D-004.

  Os commits fecham este bloco de trabalho. Antes do tasks.md, exporte a sessão
  com /export docs/sessions/07-<descricao-curta>.md. Depois eu faço o commit
  docs(sessions): export da sessão 07. Sugestão de nome: 07-plan-e-spec-v1.6.md.

✻ Baked for 18m 56s · done 10:21 PM