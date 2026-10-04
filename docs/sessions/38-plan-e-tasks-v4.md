 ▐▛███▛█   Claude Code v2.1.287
▝▜██████▀  Opus 5.5 · Claude Pro
 ▝▝   ▝▝   ~/repo/sdd-desafio

  Get to finished work sooner with Opus 5.5. Switch anytime with /model.

❯ /clear                                                                        

❯ segue o plan                                                                  

  Read 2 files, ran 4 shell commands (ctrl+o to expand)

⏺ Contexto: a spec 2.0 já está commitada, e o próximo bloco é atualizar o
  plan.md (e depois as tasks da Fase 5) para a Política v4. Agora vou ler as
  tasks, o código e os arquivos do envelope.

  Searched for 1 pattern, read 1 file, ran 5 shell commands (ctrl+o to expand)

⏺ Já li a spec 2.0, o D-007 e o código atual. Agora vou escrever o plan.md 2.0.

⏺ Write(specs/001-motor-reembolso/plan.md)
  ⎿  Added 245 lines, removed 77 lines
       1  # Plano Técnico — Motor de Cálculo de Reembolso
       2  
       3 -**Versão:** 1.2 · **Baseado na spec:** 1.9                     
       3 +**Versão:** 2.0 · **Baseado na spec:** 2.0 (Política v4, D-007)
       4  
       5  > Aqui mora o COMO. Este arquivo pode e deve falar de linguagem
          , biblioteca e
       6  > arquitetura. O que ele **não** pode é introduzir regra de neg
          ócio nova — se
       7  > apareceu uma, ela pertence à `spec.md`.
       8  
       9 +**O que mudou da 1.2 para a 2.0:** a política deixa de ser cons
         +tante no código e passa a ser um arquivo lido a cada execução, 
         +com uma tabela por centro de custo, e as despesas podem vir em 
         +moeda estrangeira, convertidas por um arquivo de câmbio (spec 2
         +.0, RN-014 a RN-016). No plano, isso muda o seguinte:          
      10 +- a arquitetura ganha `leitura.py` (forma comum aos três arquiv
         +os) e `cambio.py`;                                             
      11 +- `politica.py` passa de constantes a leitor e validador do arq
         +uivo de política;                                              
      12 +- o modelo ganha `Politica`, `Cambio` e os campos novos da saíd
         +a;                                                             
      13 +- o motor recebe a tabela aplicada e o câmbio;                 
      14 +- a CLI recebe `--politica` e `--cambio`.                      
      15 +                                                               
      16 +Ficam iguais a stack, a gravação atômica e a serialização deter
         +minística. As decisões novas são DT-011 a DT-016. DT-001, DT-00
         +2, DT-005, DT-007 e DT-009 foram atualizadas.                  
      17 +                                                               
      18  ---
      19  
      20  ## 1. Stack
      21  
      22 +Nenhuma dependência nova na 2.0: política e câmbio são JSON, li
         +dos pelo mesmo `simplejson` estrito da entrada.                
      23 +                                                               
      24  | Escolha | O quê | Por quê | O que descartei e por quê |
      25  |---|---|---|---|
      26  | Linguagem | Python ≥ 3.12, projeto gerenciado com `uv` (`pypr
          oject.toml` + `uv.lock`) | `Decimal` e `datetime.date` na bibli
          oteca padrão cobrem dinheiro e datas sem dependência; `uv` fixa
           a versão do Python (o do sistema é 3.9) e já é o que os hooks 
          de `.githooks/` usam | Node/TypeScript: sem tipo decimal nativo
          , teria que trazer biblioteca para o ponto mais sensível do pro
          jeto |
      27  | Testes | `pytest` | Testes como funções simples, `parametrize
          ` para tabelas de casos (seção 7 da spec), `tmp_path` para a CL
          I | `unittest`: mais cerimônia por teste, sem ganho |
      28  | Lint | `ruff` (regras `E`, `F`, `I`, `B`, `UP`) | Já exigido 
          pelo `pre-commit`; um só binário para lint e ordenação de impor
          ts | `flake8` + `isort`: duas ferramentas para o mesmo papel |
      18 -| Parsing/validação | `simplejson` com `use_decimal=True` (leit
         -ura e escrita), `object_pairs_hook` para chaves repetidas (DT-0
         -10) + validação manual campo a campo | Lê `33.333` direto como 
         -`Decimal("33.333")`, sem passar por `float`, e escreve `Decimal
         -` como número JSON exato; o hook entrega os pares de cada objet
         -o na ordem do arquivo, inclusive os repetidos. A validação prec
         -isa produzir **item `entrada_invalida`** por despesa, não exceç
         -ão — regra fina demais para um validador de schema | `json` da 
         -biblioteca padrão: lê com `parse_float=Decimal`, mas não escrev
         -e `Decimal` como número — teria que converter para `float` na s
         -aída e `valor_informado` perderia dígitos além do 17º. `pydanti
         -c`/`jsonschema`: rejeitam o documento inteiro ou exigem contorn
         -os para "erro vira item" e para copiar campos de tipo errado co
         -mo nulo |                                                      
      19 -| Aritmética monetária | `decimal.Decimal`, `quantize(Decimal("
         -0.01"), ROUND_HALF_UP)` | Exato ao centavo; `ROUND_HALF_UP` do 
         -Python arredonda a metade **afastando do zero** (-0,005 → -0,01
         -), exatamente a RN-003 | `float`: `1.005` é guardado como `1.00
         -499…` e `round(1.005, 2)` dá 1,00 (a RN-003 exige 1,01); `round
         -(0.125, 2)` dá 0,12, porque `round` arredonda a metade para o p
         -ar. Centavos em `int`: exige arredondar na conversão de qualque
         -r forma, e o número informado (33,333) não cabe em centavos |  
      20 -| CLI | `argparse` (biblioteca padrão) | Um subcomando, duas op
         -ções obrigatórias; erro de uso já sai com código 2 e mensagem e
         -m stderr | `click`/`typer`: dependência a mais para uma interfa
         -ce fixa e mínima |                                             
      29 +| Parsing/validação | `simplejson` com `use_decimal=True` (leit
         +ura e escrita), `object_pairs_hook` para chaves repetidas (DT-0
         +10) + validação manual campo a campo, para os três arquivos | L
         +ê `33.333` direto como `Decimal("33.333")`, sem passar por `flo
         +at`, e escreve `Decimal` como número JSON exato; o hook entrega
         + os pares de cada objeto na ordem do arquivo, inclusive os repe
         +tidos (aviso na entrada, erro na política e no câmbio). A valid
         +ação da entrada precisa produzir **item `entrada_invalida`** po
         +r despesa, não exceção — regra fina demais para um validador de
         + schema | `json` da biblioteca padrão: lê com `parse_float=Deci
         +mal`, mas não escreve `Decimal` como número — teria que convert
         +er para `float` na saída e `valor_informado` perderia dígitos a
         +lém do 17º. `pydantic`/`jsonschema`: rejeitam o documento intei
         +ro ou exigem contornos para "erro vira item" e para copiar camp
         +os de tipo errado como nulo; para política e câmbio, um schema 
         +não expressa "casas decimais pelo valor exato", "nomes de categ
         +oria distintos depois de normalizar" nem chave repetida |      
      30 +| Aritmética monetária | `decimal.Decimal`; arredondamento com 
         +`quantize(Decimal("0.01"), ROUND_HALF_UP)`; produtos exatos em 
         +contexto local (DT-012); limite em viagem com `ROUND_DOWN` (DT-
         +013) | Exato ao centavo; `ROUND_HALF_UP` do Python arredonda a 
         +metade **afastando do zero** (-0,005 → -0,01), exatamente a RN-
         +003 | `float`: `1.005` é guardado como `1.00499…` e `round(1.00
         +5, 2)` dá 1,00 (a RN-003 exige 1,01); `round(0.125, 2)` dá 0,12
         +, porque `round` arredonda a metade para o par. Centavos em `in
         +t`: exige arredondar na conversão de qualquer forma, e o número
         + informado (33,333) não cabe em centavos |                     
      31 +| CLI | `argparse` (biblioteca padrão) | Um subcomando, quatro 
         +opções obrigatórias; erro de uso já sai com código 2 e mensagem
         + em stderr | `click`/`typer`: dependência a mais para uma inter
         +face fixa e mínima |                                           
      32  
      33  ## 2. Arquitetura
      34  
      35  ```
      25 -arquivo JSON ─▶ cli ─▶ entrada ─▶ motor ─▶ saida ─▶ cli ─▶ arqu
         -ivo JSON                                                       
      26 -               (I/O)  (parse +    (regras,  (monta     (gravaçã
         -o                                                              
      27 -                       validação)  puro)     dicionário) atômic
         -a)                                                             
      28 -                         │           │                         
      29 -                         └── normalizacao, politica, justificat
         -iva ──┘                                                        
      36 +entrada  ─┐                                                    
      37 +política ─┼─▶ cli ─▶ entrada / politica / cambio ─▶ motor ─▶ sa
         +ida ─▶ cli ─▶ arquivo JSON                                     
      38 +câmbio   ─┘  (I/O)   (forma: leitura; conteúdo:     (regras,  (
         +monta     (gravação                                            
      39 +                      RN-002/013, RN-016)            puro)     
         +dicionário) atômica)                                           
      40 +                                  │                    │       
      41 +                                  └── normalizacao, politica, c
         +ambio, justificativa ──┘                                       
      42  ```
      43  
      44  | Módulo (`src/reembolso/`) | Responsabilidade | Faz I/O? |
      45  |---|---|---|
      34 -| `cli.py` | `argparse`, lê bytes do arquivo, chama o pipeline,
         - grava a saída de forma atômica, mapeia erros para mensagem + c
         -ódigo de saída | sim |                                         
      35 -| `entrada.py` | bytes → JSON (`Decimal`) → `Entrada`. Resolve 
         -chaves repetidas e gera os avisos (RN-013); erros de arquivo da
         - RN-002 viram `ErroDeArquivo`; despesa inválida vira `DespesaIn
         -valida` (etapa 1 da seção 8) | não |                           
      46 +| `cli.py` | `argparse`, lê os bytes dos três arquivos, chama o
         + pipeline, grava a saída de forma atômica, mapeia erros para me
         +nsagem + código de saída | sim |                               
      47 +| `leitura.py` | **novo.** Forma comum aos três arquivos (seção
         + 4 da spec, RN-016): bytes → JSON estrito com `Decimal` e `Obje
         +toJson` (DT-002, DT-010), `ErroDeArquivo`, verificação de escap
         +es e os testes de tipo da DT-003 (`e_numero`, `e_data`, `tem_te
         +xto`). Sai de `entrada.py`, sem mudar o comportamento (DT-011) 
         +| não |                                                        
      48 +| `entrada.py` | documento → `Entrada`. Resolve chaves repetida
         +s e gera os avisos (RN-013); erros de cabeçalho da RN-002 (incl
         +usive `centro_custo` de tipo errado) viram `ErroDeArquivo`; des
         +pesa inválida (inclusive `moeda` mal formada) vira `DespesaInva
         +lida` (etapa 1 da seção 8). **Não conhece a política:** guarda 
         +a categoria como veio, e quem decide se ela é reconhecida é o m
         +otor (seção 3) | não |                                         
      49 +| `politica.py` | documento → `Politica` (RN-016, parte da polí
         +tica); escolha da tabela aplicada (RN-014); limite diário norma
         +l e em viagem (RN-009, DT-013); as constantes de interpretação 
         +que a spec fixa e o arquivo não traz (seção 4 deste plano) | nã
         +o |                                                            
      50 +| `cambio.py` | **novo.** Documento → `Cambio` (RN-016, parte d
         +o câmbio); busca da cotação de D a D-3 (RN-015, DT-014) | não |
      51  | `normalizacao.py` | `normalizar_texto()` — os passos da seção
           5 da spec | não |
      37 -| `politica.py` | constantes da política (seção 4 deste plano) 
         -| não |                                                        
      38 -| `motor.py` | etapas 2 a 9 da seção 8; recebe `Entrada`, devol
         -ve `Resultado` | não |                                         
      52 +| `motor.py` | etapas 2 a 9 da seção 8; recebe `Entrada`, `Poli
         +tica` e `Cambio` e devolve `Resultado` | não |                 
      53  | `justificativa.py` | frase em português para cada item (texto
           não contratual) | não |
      54  | `saida.py` | `Resultado` → dicionário na ordem de campos da s
          eção 4 da spec → texto JSON | não |
      55  | `modelo.py` | dataclasses e enums compartilhados (seção 3) | 
          não |
      56  
      43 -**Fronteiras:** só `cli.py` toca disco, `sys.argv`, `stderr` e 
         -código de saída. Todo o resto é função pura de dados para dados
         -, testável sem arquivo. A regra de negócio fica concentrada em 
         -`motor.py` + `politica.py` + `normalizacao.py`; `entrada.py` só
         - aplica a RN-002 (forma da entrada). Uma mudança de política me
         -xe em `politica.py`; uma mudança de regra mexe em `motor.py`; u
         -ma mudança de formato de entrada mexe em `entrada.py`; uma muda
         -nça de formato de saída mexe em `saida.py`.                    
      57 +**Fronteiras:** só `cli.py` toca disco, `sys.argv`, `stderr` e 
         +código de saída. Todo o resto é função pura de dados para dados
         +, testável sem arquivo. A regra de negócio fica concentrada em 
         +`motor.py`, `politica.py`, `cambio.py` e `normalizacao.py`. `en
         +trada.py` só aplica a RN-002 e a RN-013, e `leitura.py` só a fo
         +rma do arquivo.                                                
      58  
      45 -Comando final: `uv run reembolso calcular --input <entrada> --o
         -utput <saída>` (entry point `reembolso = "reembolso.cli:main"` 
         -no `pyproject.toml`).                                          
      59 +Impacto de cada tipo de mudança:                               
      60 +- **Valor da política** (limite, mínimo da nota, percentual, no
         +va categoria ou centro de custo): muda só o arquivo de política
         +, sem código.                                                  
      61 +- **Interpretação da política** (quais categorias ampliam em vi
         +agem, a janela da cotação): muda `politica.py` ou `cambio.py`. 
      62 +- **Regra:** muda `motor.py`.                                  
      63 +- **Formato de entrada ou saída:** muda `entrada.py` ou `saida.
         +py`.                                                           
      64  
      65 +**Ordem de leitura e erros:** a CLI lê e valida a entrada, depo
         +is a política e depois o câmbio, tudo antes de calcular. O prim
         +eiro erro encerra a execução, com uma mensagem que nomeia o arq
         +uivo (DT-007). A spec não fixa qual erro aparece quando há mais
         + de um. Basta que nenhum gere saída.                           
      66 +                                                               
      67 +Comando final: `uv run reembolso calcular --input <entrada> --p
         +olitica <política> --cambio <câmbio> --output <saída>` (entry p
         +oint `reembolso = "reembolso.cli:main"` no `pyproject.toml`).  
      68 +                                                               
      69  ## 3. Modelo de dados
      70  
      49 -Todas as estruturas são `@dataclass(frozen=True)`; valores mone
         -tários são sempre `Decimal`.                                   
      71 +Todas as estruturas são `@dataclass(frozen=True)`; valores mone
         +tários e taxas são sempre `Decimal`. Mapeamentos dentro das dat
         +aclasses (tabelas, taxas) são montados uma vez na leitura e nun
         +ca alterados depois.                                           
      72  
      73  ```python
      74  class Status(StrEnum):   APROVADO, PARCIAL, RECUSADO
      75  class Motivo(StrEnum):   # na ordem das etapas da seção 8 da sp
          ec
      54 -    ENTRADA_INVALIDA, VALOR_INVALIDO, FORA_DO_PERIODO, CATEGORI
         -A_FORA_DA_POLITICA,                                            
      55 -    NOTA_FISCAL_AUSENTE, DUPLICATA, LIMITE_DIARIO_EXCEDIDO     
      76 +    ENTRADA_INVALIDA, CAMBIO_INDISPONIVEL, VALOR_INVALIDO, FORA
         +_DO_PERIODO,                                                   
      77 +    CATEGORIA_FORA_DA_POLITICA, NOTA_FISCAL_AUSENTE, DUPLICATA,
         + LIMITE_DIARIO_EXCEDIDO                                        
      78  
      57 -Colaborador(id: str, nome: str)                                
      79 +# --- entrada ---                                              
      80 +Colaborador(id: str, nome: str, centro_custo: str | None)   # t
         +exto como veio, ou None se ausente/nulo                        
      81  Periodo(inicio: date, fim: date, inicio_texto: str, fim_texto: 
          str, competencia: str | None)
      82  
      83  Despesa(                       # passou pela etapa 1 (validação
          )
     ...
       86      categoria_texto: str,      # como veio
       87      categoria: str,            # normalizada (seção 5 da spec)
       88      fornecedor: str,           # normalizado
       66 -    valor_informado: Decimal,                                 
       89 +    valor_informado: Decimal,  # na moeda da despesa          
       90 +    moeda: str,                # "BRL" se ausente ou nula; sen
          +ão 3 letras A–Z                                               
       91      tem_nota_fiscal: bool,
       92      avisos: tuple[str, ...],   # RN-013
       93  )
       94  DespesaInvalida(               # recusada na etapa 1
       95      posicao: int,
       96      id: str | None, data_texto: str | None,
       73 -    categoria_saida: str | None,   # normalizada se reconhecid
          -a; senão texto como veio; senão None                          
       97 +    categoria_texto: str | None,   # como veio, se texto; o mo
          +tor decide se sai normalizada                                 
       98      valor_informado: Decimal | None,
       99 +    moeda_saida: str | None,       # "BRL" se ausente/nula; co
          +mo veio, se texto; senão None                                 
      100      avisos: tuple[str, ...],
      101  )
      102  Entrada(colaborador, periodo, despesas: list[Despesa | Despesa
           Invalida],
      103          avisos: tuple[str, ...])      # chaves repetidas fora 
           das despesas
      104  
      105 +# --- política e câmbio (RN-014 a RN-016) ---                 
      106 +Tabela = Mapping[str, Decimal]        # categoria normalizada 
          +→ limite diário normal                                        
      107 +Politica(versao: str | None, vigencia: str | None,            
      108 +         padrao: Tabela, centros_custo: Mapping[str, Tabela], 
          +  # chave como escrita no arquivo                             
      109 +         nota_fiscal_acima_de: Decimal, acrescimo_em_viagem_pe
          +rcentual: Decimal)                                            
      110 +TabelaAplicada(nome: str, limites: Tabela)   # nome: chave de 
          +`centros_custo` ou "padrao"                                   
      111 +Cambio(taxas: Mapping[date, Mapping[str, Decimal]])   # sem a 
          +entrada "BRL" (ignorada, RN-016)                              
      112 +Cotacao(taxa: Decimal, data: date | None)            # data No
          +ne para BRL                                                   
      113 +                                                              
      114 +# --- saída ---                                               
      115  ItemResultado(                 # espelha `itens[]` da seção 4 
           da spec, campo a campo
       81 -    id, data, categoria, valor_informado, valor_considerado, v
          -alor_reembolsado,                                             
      116 +    id, data, categoria, valor_informado, moeda, taxa_cambio, 
          +data_cotacao,                                                 
      117 +    valor_considerado, valor_reembolsado,                     
      118      status: Status, motivo: Motivo | None, em_viagem: bool | N
           one,
      119      limite_diario: Decimal | None, justificativa: str, avisos:
            tuple[str, ...],
      120  )
      121  Totais(valor_solicitado, valor_reembolsado, valor_glosado)
       86 -Resultado(colaborador, periodo, itens: list[ItemResultado], to
          -tais, avisos: tuple[str, ...])                                
      122 +PoliticaAplicada(versao: str | None, vigencia: str | None, tab
          +ela_aplicada: str)                                            
      123 +Resultado(colaborador, periodo, politica: PoliticaAplicada, it
          +ens: list[ItemResultado],                                     
      124 +          totais, avisos: tuple[str, ...])                    
      125  ```
      126  
       89 -A justificativa é gerada a partir dos campos contratuais do it
          -em já decidido (status, motivo, valores, limite, data), nunca 
          -o contrário: nenhuma decisão depende do texto.                
      127 +A justificativa é gerada a partir dos campos contratuais do it
          +em já decidido (status, motivo, valores, limite, data, moeda, 
          +taxa), nunca o contrário: nenhuma decisão depende do texto.   
      128  
      129 +**A categoria de saída é decidida no motor, não na entrada.** 
          +Na 1.x, `entrada.py` normalizava a categoria de uma despesa in
          +válida comparando com uma lista fixa. Desde a 2.0, "reconhecid
          +a" significa "presente na tabela aplicada, inclusive com limit
          +e 0" (seção 4 da spec), e a tabela depende do `centro_custo` e
          + do arquivo de política. Por isso `entrada.py` guarda só o tex
          +to como veio, e o motor aplica a mesma função (`categoria_de_s
          +aida(texto, tabela)`) a todo item, válido ou não. Assim a entr
          +ada não depende da política, e a regra da seção 4 fica num lug
          +ar só.                                                        
      130 +                                                              
      131  ## 4. Como a política é representada
      132  
       93 -Constantes em `politica.py`, um único módulo, com os valores *
          -*literais** da spec:                                          
      133 +Desde a 2.0 (AMB-031), **os números da política vêm do arquivo
          + `--politica`**. `politica.py` não tem mais limites, mínimo da
          + nota nem percentual: lê o arquivo, valida pela RN-016 e devol
          +ve uma `Politica` (seção 3). As tabelas são indexadas pela cat
          +egoria **normalizada**, porque a comparação com a despesa é se
          +mpre feita depois da normalização (RN-006). Dois nomes que nor
          +malizam igual na mesma tabela são erro de arquivo, então a ind
          +exação nunca perde uma regra. Os centros de custo são indexado
          +s pela chave **como escrita**, porque a comparação com o `cent
          +ro_custo` é exata (RN-014).                                   
      134  
      135 +Ficam em `politica.py` só as constantes de **interpretação**, 
          +que a spec fixa e o arquivo não traz:                         
      136 +                                                              
      137  ```python
       96 -LIMITES_DIARIOS = {          # RN-009: (normal, em viagem)    
       97 -    "alimentacao":       LimiteDiario(normal=Decimal("60.00"),
          -  viagem=Decimal("90.00")),                                   
       98 -    "transporte_urbano": LimiteDiario(normal=Decimal("80.00"),
          -  viagem=Decimal("120.00")),                                  
       99 -    "hospedagem":        LimiteDiario(normal=Decimal("250.00")
          -, viagem=Decimal("250.00")),                                  
      100 -}                                                             
      101 -CATEGORIAS_RECONHECIDAS = frozenset(LIMITES_DIARIOS)          
          -# RN-006                                                      
      102 -VALOR_ACIMA_DO_QUAL_EXIGE_NOTA = Decimal("100.00")            
          -# RN-008 (estritamente maior)                                 
      138 +CATEGORIAS_AMPLIADAS_EM_VIAGEM = frozenset({"alimentacao", "tr
          +ansporte_urbano"})  # RN-009, AMB-006, AMB-022                
      139  CATEGORIA_QUE_COMPROVA_VIAGEM = "hospedagem"                  
           # RN-010
      140  DIAS_EM_VIAGEM_APOS_HOSPEDAGEM = 1                            
           # RN-010: D e D+1
      105 -VALOR_ABSOLUTO_MAXIMO = Decimal("1000000000")                 
          -# RN-002 / AMB-018 (a partir dele: entrada_invalida)          
      141 +VALOR_ABSOLUTO_MAXIMO = Decimal("1000000000")                 
          +# RN-002, RN-016, AMB-018 (a partir dele: inválido)           
      142 +NOME_DA_TABELA_PADRAO = "padrao"                              
          +# RN-014, RN-016                                              
      143 +PERIODICIDADES = frozenset({"dia", "diaria"})                 
          +# RN-012, RN-016: as duas = limite por data                   
      144 +MOEDA_BASE = "BRL"                                            
          +# RN-015, RN-016                                              
      145  ```
      146  
      108 -Os limites em viagem ficam escritos por extenso (90,00 / 120,0
          -0 / 250,00), e não calculados como `normal × 1,5`: a tabela da
          - RN-009 é a fonte, e a hospedagem não amplia (AMB-006). Um tes
          -te confere `politica.py` contra a tabela da spec.             
      147 +E em `cambio.py`:                                             
      148  
      110 -**Descartado:** arquivo de configuração (YAML/JSON) com a polí
          -tica. Não há requisito de trocar a política sem novo deploy; e
          -xigiria validar o próprio arquivo de política e testar combina
          -ções inválidas. Como a política já está isolada num módulo sem
          - lógica, migrar para configuração depois custa um leitor e um 
          -teste.                                                        
      149 +```python                                                     
      150 +DIAS_ANTERIORES_ACEITOS_NA_COTACAO = 3                        
          +# RN-015, AMB-024: D-1 a D-3                                  
      151 +```                                                           
      152  
      153 +**Funções** (todas puras):                                    
      154 +- `ler_politica(documento) -> Politica`: aplica a parte da RN-
          +016 sobre a política (DT-015).                                
      155 +- `tabela_aplicada(politica, centro_custo) -> TabelaAplicada`:
          + aplica a RN-014. Se `centro_custo` tem texto fora do espaço e
          +m branco e é chave exata de `centros_custo`, usa essa tabela; 
          +em qualquer outro caso, usa o `padrao`.                       
      156 +- `limite_diario(tabela_aplicada, categoria, em_viagem, percen
          +tual) -> Decimal`: aplica a RN-009 com a DT-013.              
      157 +- `categoria_de_saida(texto, tabela) -> str | None`: aplica a 
          +seção 4. Devolve a forma normalizada se ela está na tabela, se
          +não o texto como veio, e `None` se não é texto.               
      158 +- `ler_cambio(documento) -> Cambio` e `cotacao(cambio, moeda, 
          +data) -> Cotacao | None` (em `cambio.py`): aplicam a RN-016 e 
          +a RN-015 (DT-014).                                            
      159 +                                                              
      160 +**Descartado:**                                               
      161 +- **Manter constantes como "padrão de fábrica" e o arquivo com
          +o sobrescrita.** Seriam duas fontes da verdade, e a AMB-020 de
          +cide que o padrão é o bloco `padrao` do arquivo. Um limite esq
          +uecido no código mudaria o resultado sem nada visível mudar (A
          +MB-031).                                                      
      162 +- **Indexar as tabelas pelo nome como escrito no arquivo.** Ob
          +rigaria a normalizar a cada consulta, e dois nomes equivalente
          +s passariam pela validação.                                   
      163 +- **Ler a política dentro de `motor.py`.** Misturaria validaçã
          +o de arquivo com regra de reembolso, e o motor deixaria de ser
          + testável com uma `Politica` construída à mão.                
      164 +                                                              
      165  ## 5. Decisões técnicas
      166  
      167  ### DT-001 — Dinheiro em `Decimal` lido direto do texto JSON
      168  
      116 -**Contexto:** RN-003 exige arredondar a metade afastando do ze
          -ro e cálculos exatos ao centavo; `valor_informado` é o número 
          -recebido (33.333).                                            
      117 -**Decisão:** o JSON é lido com `simplejson.loads(..., use_deci
          -mal=True)`, então todo número com parte decimal chega como `De
          -cimal` construído do texto, ou seja, com o valor decimal exato
          - escrito no arquivo (seção 4 da spec); inteiros também, via `p
          -arse_int=Decimal` (evita o limite de 4.300 dígitos na conversã
          -o de texto para `int` do Python). `valor` com `abs(valor) >= V
          -ALOR_ABSOLUTO_MAXIMO` é `entrada_invalida` (RN-002) — comparaç
          -ão exata entre `Decimal`, válida para qualquer expoente. `valo
          -r_considerado = valor_informado.quantize(Decimal("0.01"), ROUN
          -D_HALF_UP)`. Toda conta (saldo do limite, totais) é feita entr
          -e `Decimal` já quantizados, então soma e subtração são exatas.
          - A saída escreve `Decimal` como número JSON (`use_decimal=True
          -`).                                                           
      169 +**Contexto:** RN-003 exige arredondar a metade afastando do ze
          +ro e cálculos exatos ao centavo; `valor_informado` é o número 
          +recebido (33.333), na moeda da despesa.                       
      170 +**Decisão:** os três arquivos são lidos com `simplejson.loads(
          +..., use_decimal=True)`, então todo número com parte decimal c
          +hega como `Decimal` construído do texto, ou seja, com o valor 
          +decimal exato escrito no arquivo (seção 4 da spec); inteiros t
          +ambém, via `parse_int=Decimal` (evita o limite de 4.300 dígito
          +s na conversão de texto para `int` do Python). `valor` com `ab
          +s(valor) >= VALOR_ABSOLUTO_MAXIMO` é `entrada_invalida` (RN-00
          +2), e limite, mínimo, percentual ou taxa a partir do mesmo tet
          +o é erro de arquivo (RN-016) — comparação exata entre `Decimal
          +`, válida para qualquer expoente. `valor_considerado` = `arred
          +ondar(valor_informado × taxa)`, com o produto exato (DT-012) e
          + `quantize(Decimal("0.01"), ROUND_HALF_UP)`. Toda conta poster
          +ior (saldo do limite, totais) é feita entre `Decimal` já quant
          +izados, então soma e subtração são exatas. A saída escreve `De
          +cimal` como número JSON (`use_decimal=True`); `taxa_cambio` sa
          +i como o `Decimal` lido do câmbio, com o valor exato.         
      171  **Alternativa descartada:** `float` com arredondamento no fim 
           (`round(1.005, 2) == 1.0`), e `json` padrão com conversão para
            `float` só na saída (perde dígitos de `valor_informado`).
      119 -**Consequência:** fácil garantir a RN-003 e os totais da seção
          - 9 ao centavo. Com o teto da RN-002, todo valor aceito tem no 
          -máximo 12 dígitos depois de quantizado, e as somas cabem com f
          -olga na precisão padrão do `Decimal` (28 dígitos): nenhuma con
          -ta arredonda em silêncio nem levanta `InvalidOperation`. Exige
          - cuidado para nunca misturar `float` (proibido em `motor.py`; 
          -um teste de propriedade verifica que nenhum campo monetário da
          - saída é `float`). A forma escrita na saída pode diferir da en
          -trada (`72.50` → `72.5`, ou `45.00` → `45.00`), o que a spec p
          -ermite (seção 4: "como veio" é o valor numérico).             
      172 +**Consequência:** com o teto da RN-002 e da RN-016, todo `valo
          +r_considerado` fica abaixo de 10^18 (um bilhão vezes uma taxa 
          +abaixo de um bilhão), com até 20 dígitos depois de quantizado.
          + As somas cabem na precisão padrão do `Decimal` (28 dígitos), 
          +salvo em entradas absurdas com centenas de milhões de despesas
          + desse tamanho, que já não existem por causa do tamanho do arq
          +uivo. Exige cuidado para nunca misturar `float` (proibido em `
          +motor.py`; um teste de propriedade verifica que nenhum campo m
          +onetário da saída é `float`). A forma escrita na saída pode di
          +ferir da entrada (`72.50` → `72.5`, ou `45.00` → `45.00`), o q
          +ue a spec permite (seção 4: "como veio" é o valor numérico).  
      173  
      174  ### DT-002 — Rejeitar o que não é JSON estrito
      175  
      123 -**Contexto:** RN-002: arquivo que não é JSON válido é erro de 
          -arquivo. O `json` da biblioteca padrão aceita `NaN`, `Infinity
          -` e `-Infinity`, que não são JSON.                            
      124 -**Decisão:** `simplejson` ≥ 4 já os rejeita na leitura por pad
          -rão (`allow_nan=False`); a versão mínima fica fixada no `pypro
          -ject.toml` e um teste garante que `"valor": NaN` é erro de arq
          -uivo, para a proteção não sumir numa troca de versão. Erro de 
          -parse → `ErroDeArquivo`. Bytes decodificados como UTF-8 estrit
          -o (`utf-8-sig`, aceitando um BOM, que a RFC 8259 permite ignor
          -ar); falha de decodificação → `ErroDeArquivo`. O `simplejson` 
          -também descarta um U+FEFF inicial por conta própria, o que far
          -ia dois BOMs passarem; por isso um U+FEFF que sobra depois do 
          -`utf-8-sig` → `ErroDeArquivo` (spec 1.9, D-006). Caractere de 
          -controle cru em texto e números fora da gramática (`01.5`, `.5
          -`, `1.`, `+1`) já são rejeitados pelo parser estrito (`strict=
          -True`, padrão). O parser e o percurso de `entrada.py` são recu
          -rsivos: aninhamento além do limite de recursão do Python (~1.0
          -00 níveis) levanta `RecursionError`, convertido em `ErroDeArqu
          -ivo` (risco aceito na seção 10 da spec, D-006). O parser aceit
          -a em silêncio um escape `\ud800` sem par (vira um caractere su
          -bstituto isolado na `str`, que a gravação em UTF-8 recusaria d
          -epois); por isso, depois do parse, `entrada.py` percorre todas
          - as chaves e textos — inclusive os das ocorrências descartadas
          - por chave repetida, pelos pares guardados no `ObjetoJson` (DT
          --010; spec 1.9, D-006) — e levanta `ErroDeArquivo` se algum co
          -ntiver caractere entre U+D800 e U+DFFF (seção 4 da spec). Pare
          -s de escapes válidos já chegam combinados num único caractere.
      176 +**Contexto:** RN-002 e RN-016: arquivo que não é JSON válido é
          + erro de arquivo, e os três arquivos seguem as mesmas regras d
          +e forma. O `json` da biblioteca padrão aceita `NaN`, `Infinity
          +` e `-Infinity`, que não são JSON.                            
      177 +**Decisão:** vale igual para entrada, política e câmbio, todos
          + lidos pela mesma função de `leitura.py` (DT-011).            
      178 +- **Valores não JSON:** o `simplejson` ≥ 4 já rejeita `NaN` e 
          +`Infinity` na leitura por padrão (`allow_nan=False`). A versão
          + mínima fica fixada no `pyproject.toml`, e um teste garante qu
          +e `"valor": NaN` é erro de arquivo, para a proteção não sumir 
          +numa troca de versão. Erro de parse → `ErroDeArquivo`.        
      179 +- **Codificação e BOM:** os bytes são decodificados como UTF-8
          + estrito (`utf-8-sig`, aceitando um BOM, que a RFC 8259 permit
          +e ignorar). Falha de decodificação → `ErroDeArquivo`. O `simpl
          +ejson` também descarta um U+FEFF inicial por conta própria, o 
          +que faria dois BOMs passarem; por isso um U+FEFF que sobra dep
          +ois do `utf-8-sig` → `ErroDeArquivo` (spec 1.9, D-006).       
      180 +- **Gramática:** caractere de controle cru em texto e números 
          +fora da gramática (`01.5`, `.5`, `1.`, `+1`) já são rejeitados
          + pelo parser estrito (`strict=True`, padrão).                 
      181 +- **Aninhamento:** o parser e os percursos são recursivos. Ani
          +nhamento além do limite de recursão do Python (~1.000 níveis) 
          +levanta `RecursionError`, convertido em `ErroDeArquivo` (risco
          + aceito na seção 10 da spec, D-006).                          
      182 +- **Escapes sem par:** o parser aceita em silêncio um escape `
          +\ud800` sem par, que vira um caractere substituto isolado na `
          +str` e seria recusado depois, na gravação em UTF-8. Por isso, 
          +depois do parse, a leitura percorre todas as chaves e textos, 
          +inclusive os das ocorrências descartadas por chave repetida (p
          +elos pares guardados no `ObjetoJson`, DT-010; spec 1.9, D-006)
          +. Se algum contiver caractere entre U+D800 e U+DFFF, levanta `
          +ErroDeArquivo` (seção 4 da spec). Pares de escapes válidos já 
          +chegam combinados num único caractere.                        
      183 +                                                              
      184  **Alternativa descartada:** aceitar `NaN` e tratar como "valor
            não é número" na despesa: transformaria arquivo inválido em p
           rocessamento normal.
      126 -**Consequência:** `"valor": NaN` encerra a execução sem saída,
          - como qualquer JSON inválido.                                 
      185 +**Consequência:** `"valor": NaN` encerra a execução sem saída,
          + como qualquer JSON inválido. O mesmo vale para `"limite": NaN
          +` ou uma taxa `Infinity`.                                     
      186  
      187  ### DT-003 — Validação de tipo sem as armadilhas do Python
      188  
      130 -**Contexto:** RN-002 exige `valor` número e `tem_nota_fiscal` 
          -booleano. Em Python, `True` é `int`; `date.fromisoformat` (3.1
          -1+) aceita `20260701` e outros formatos ISO; `strptime("%Y-%m-
          -%d")` aceita `2026-7-1`; `\d` casa dígitos não ASCII.         
      131 -**Decisão:**                                                  
      189 +**Contexto:** RN-002 exige `valor` número e `tem_nota_fiscal` 
          +booleano; RN-016 exige limite, mínimo, percentual e taxa númer
          +os e `vigencia` e chaves de `taxas` datas. Em Python, `True` é
          + `int`; `date.fromisoformat` (3.11+) aceita `20260701` e outro
          +s formatos ISO; `strptime("%Y-%m-%d")` aceita `2026-7-1`; `\d`
          + casa dígitos não ASCII; `str.isupper()` aceita letras acentua
          +das.                                                          
      190 +**Decisão:** os testes de tipo ficam em `leitura.py` e valem p
          +ara os três arquivos:                                         
      191  - número = `Decimal` ou `int`, **e não** `bool`;
      192  - booleano = `type(x) is bool`;
      134 -- data = casa `^[0-9]{4}-[0-9]{2}-[0-9]{2}$` **e** `date.fromi
          -soformat` aceita (rejeita 2026-02-30);                        
      135 -- texto obrigatório = `str` com algum caractere fora do espaço
          - em branco da RN-002 (propriedade White_Space do Unicode). **N
          -ão** usar `strip()`/`isspace()` puros: eles também tratam U+00
          -1C a U+001F como espaço, e a spec diz que não são; usar `c.iss
          -pace() and c not in "\x1c\x1d\x1e\x1f"`.                      
      136 -**Alternativa descartada:** `isinstance(x, (int, float))` e `f
          -romisoformat` sozinho — aceitariam `"valor": true` e `"data": 
          -"20260703"`.                                                  
      137 -**Consequência:** cada armadilha vira um caso de teste de `ent
          -rada.py`.                                                     
      193 +- data = casa `^[0-9]{4}-[0-9]{2}-[0-9]{2}$` **e** `date.fromi
          +soformat` aceita (rejeita 2026-02-30 e 2026-07-32);           
      194 +- texto obrigatório = `str` com algum caractere fora do espaço
          + em branco da RN-002 (propriedade White_Space do Unicode). **N
          +ão** usar `strip()`/`isspace()` puros: eles também tratam U+00
          +1C a U+001F como espaço, e a spec diz que não são; usar `c.iss
          +pace() and c not in "\x1c\x1d\x1e\x1f"`;                      
      195 +- código de moeda (`moeda` na entrada, códigos em `taxas`) = `
          +str` que casa `[A-Z]{3}` com `re.fullmatch` (classe com interv
          +alo ASCII explícito; `"EUR\n"` não casa com `fullmatch`, ao co
          +ntrário de `$`), sem normalização (AMB-025);                  
      196 +- "no máximo 2 casas decimais" (RN-016) = `x == x.quantize(Dec
          +imal("0.01"))`, testado **depois** do teto, que garante que o 
          +`quantize` cabe na precisão. É comparação pelo valor exato: `6
          +0.000` e `6E1` passam, `60.005` e `1E-999999` não.            
      197  
      198 +**Alternativa descartada:** `isinstance(x, (int, float))` e `f
          +romisoformat` sozinho — aceitariam `"valor": true` e `"data": 
          +"20260703"`. Contar casas pelo expoente (`as_tuple().exponent 
          +>= -2`) recusaria `60.000`, que a spec aceita.                
      199 +**Consequência:** cada armadilha vira um caso de teste, em `en
          +trada.py` ou nos leitores de política e câmbio.               
      200 +                                                              
      201  ### DT-004 — Normalização de texto com `unicodedata`
      202  
      203  **Contexto:** seção 5 da spec, 3 passos (caixa, acentos, só le
           tras e algarismos), "qualquer que seja a forma como o caracter
           e foi codificado".
      142 -**Decisão:** `casefold()` (equivalência completa de caixa, `ß`
          - → `ss`) → `unicodedata.normalize("NFD")` e remoção de todo ca
          -ractere de categoria `M*` (sinais combinantes, com ou sem letr
          -a) → todo caractere que não é de categoria `L*` (letra, inclui
          - `Lm`/`Lo` como `º` e `ʼ`) nem `Nd` (algarismo decimal, sem co
          -nversão para ASCII) vira espaço → `"_".join(texto.split())` (p
          -ontas somem, sequências internas viram um `_`). O NFD decompõe
          - tanto `á` pré-composto (U+00E1) quanto `a` + acento combinant
          -e (U+0301) para a mesma sequência, cobrindo as duas codificaçõ
          -es; letras sem decomposição canônica (`ø`, `ł`) ficam como est
          -ão, como a spec define. Texto que resulta vazio é tratado pela
          - validação (`entrada.py`, RN-002).                            
      204 +**Decisão:** `casefold()` (equivalência completa de caixa, `ß`
          + → `ss`) → `unicodedata.normalize("NFD")` e remoção de todo ca
          +ractere de categoria `M*` (sinais combinantes, com ou sem letr
          +a) → todo caractere que não é de categoria `L*` (letra, inclui
          + `Lm`/`Lo` como `º` e `ʼ`) nem `Nd` (algarismo decimal, sem co
          +nversão para ASCII) vira espaço → `"_".join(texto.split())` (p
          +ontas somem, sequências internas viram um `_`). O NFD decompõe
          + tanto `á` pré-composto (U+00E1) quanto `a` + acento combinant
          +e (U+0301) para a mesma sequência, cobrindo as duas codificaçõ
          +es; letras sem decomposição canônica (`ø`, `ł`) ficam como est
          +ão, como a spec define. Texto que resulta vazio é tratado pela
          + validação (`entrada.py`, RN-002; `politica.py`, RN-016).     
      205  **Alternativa descartada:** tabela manual de acentos (`á→a`, .
           ..): incompleta por construção; `NFKD`: também desfaz compatib
           ilidades (ligaduras, larguras, `²` → `2`) que a spec não pede 
           (seção 10); lista de separadores (`[\s\-_]`): deixa travessões
           , invisíveis e pontuação sem resultado definido (D-005).
      144 -**Consequência:** uma função pura, usada por RN-006, RN-007 e 
          -pela validação da RN-002, testada com os exemplos da seção 5 e
          - os casos de borda de categoria e fornecedor.                 
      206 +**Consequência:** uma função pura, usada por RN-006, RN-007, p
          +ela validação da RN-002 e pela indexação das tabelas da RN-016
          +, testada com os exemplos da seção 5 e os casos de borda de ca
          +tegoria e fornecedor.                                         
      207  
      208  ### DT-005 — Pipeline em duas fases, espelhando a seção 8
      209  
      148 -**Contexto:** as etapas 1 a 6 decidem cada despesa isoladament
          -e; as etapas 7 a 9 dependem do conjunto (duplicatas, viagem, s
          -aldo do dia).                                                 
      149 -**Decisão:**                                                  
      150 -1. **Fase individual:** para cada despesa, na ordem, aplica um
          -a lista ordenada de verificações (`valor_invalido`, `fora_do_p
          -eriodo`, `categoria_fora_da_politica`, `nota_fiscal_ausente`);
          - a primeira recusa encerra. A ordem da lista é a ordem da seçã
          -o 8.                                                          
      151 -2. **Duplicatas:** agrupa as sobreviventes por `(data, categor
          -ia, fornecedor, valor_considerado)`; em cada grupo, a original
          - é a primeira com `tem_nota_fiscal`, ou a primeira por `posica
          -o`; as demais recebem `duplicata`.                            
      152 -3. **Viagem:** `dias_em_viagem` = `{D, D+1}` para cada hospeda
          -gem sobrevivente com nota. Calculado **antes** de qualquer lim
          -ite, então independe da ordem na entrada.                     
      153 -4. **Limite:** percorre as sobreviventes por `posicao`, com sa
          -ldo por `(data, categoria)`; reembolsado = `min(valor_consider
          -ado, saldo)`; status pela RN-011.                             
      154 -**Alternativa descartada:** uma passada única despesa a despes
          -a: a viagem de uma hospedagem que aparece depois da alimentaçã
          -o do mesmo dia não seria vista (caso de borda "Alimentação ant
          -es da hospedagem").                                           
      155 -**Consequência:** reordenar ou inserir uma etapa individual é 
          -mexer numa lista; cada fase é testável isoladamente.          
      210 +**Contexto:** as etapas 1 a 6 decidem cada despesa isoladament
          +e; as etapas 7 a 9 dependem do conjunto (duplicatas, viagem, s
          +aldo do dia). Desde a 2.0, a etapa 2 converte a moeda, e as et
          +apas 5, 6 e 9 consultam a tabela aplicada.                    
      211 +**Decisão:** antes das etapas, o motor escolhe a tabela aplica
          +da uma vez (`tabela_aplicada(politica, colaborador.centro_cust
          +o)`, RN-014). Depois:                                         
      212 +1. **Fase individual:** para cada despesa, na ordem:          
      213 +   - **Conversão (etapa 2):** `cotacao(cambio, moeda, data)`. 
          +Se não há cotação, recusa com `cambio_indisponivel`. Se há, ca
          +lcula `valor_considerado = arredondar(produto_exato(valor_info
          +rmado, taxa))` (DT-012).                                      
      214 +   - **Verificações (etapas 3 a 6):** aplica uma lista ordenad
          +a de verificações (`valor_invalido`, `fora_do_periodo`, `categ
          +oria_fora_da_politica`, `nota_fiscal_ausente`), e a primeira r
          +ecusa encerra. A ordem da lista é a ordem da seção 8. A catego
          +ria é recusada se não está na tabela aplicada **ou** se o limi
          +te dela é 0 (AMB-021). A nota compara com `politica.nota_fisca
          +l_acima_de`.                                                  
      215 +2. **Duplicatas:** agrupa as sobreviventes por `(data, categor
          +ia, fornecedor, moeda, arredondar(valor_informado))`. O valor 
          +é arredondado **na moeda da despesa**, sem a taxa (RN-007, AMB
          +-028). Em cada grupo, a original é a primeira com `tem_nota_fi
          +scal`, ou a primeira por `posicao`; as demais recebem `duplica
          +ta`.                                                          
      216 +3. **Viagem:** `dias_em_viagem` = `{D, D+1}` para cada hospeda
          +gem sobrevivente com nota, em qualquer moeda. É calculado **an
          +tes** de qualquer limite, então independe da ordem na entrada.
          + A hospedagem vedada ou ausente da tabela já saiu na etapa 5, 
          +então não comprova viagem.                                    
      217 +4. **Limite:** percorre as sobreviventes por `posicao`, com sa
          +ldo por `(data, categoria)`. O limite vem de `limite_diario(ta
          +bela, categoria, em_viagem, percentual)` (DT-013). Reembolsado
          + = `min(valor_considerado, saldo)`, e o status sai pela RN-011
          +.                                                             
      218  
      219 +Todo item, inclusive o inválido, recebe a categoria de saída d
          +e `categoria_de_saida(texto, tabela)` (seção 3). Os totais som
          +am `valor_considerado` só dos itens em que ele não é nulo e é 
          +maior que zero. Os nulos são os itens recusados por `entrada_i
          +nvalida` e por `cambio_indisponivel` (seção 4).               
      220 +                                                              
      221 +**Alternativa descartada:** uma passada única despesa a despes
          +a: a viagem de uma hospedagem que aparece depois da alimentaçã
          +o do mesmo dia não seria vista (caso de borda "Alimentação ant
          +es da hospedagem"). Converter na etapa 1 (`entrada.py`): a ent
          +rada passaria a depender do câmbio, e a falta de cotação virar
          +ia `entrada_invalida`, que é outro motivo.                    
      222 +**Consequência:** reordenar ou inserir uma etapa individual co
          +ntinua sendo mexer numa lista; a 2.0 insere a conversão na fre
          +nte dela sem mexer nas demais.                                
      223 +                                                              
      224  ### DT-006 — Gravação atômica da saída
      225  
      226  **Contexto:** em erro de arquivo, a saída não pode ser criada 
           nem alterada, inclusive se a falha for na gravação (RN-002, se
           ção 4).
      160 -**Decisão:** todo o processamento e a serialização acontecem e
          -m memória antes de tocar o disco. A gravação escreve num arqui
          -vo temporário no **mesmo diretório** da saída e faz `os.replac
          -e` para o nome final; em qualquer falha, remove o temporário. 
          -Pasta inexistente ou sem permissão falha na criação do temporá
          -rio, antes de qualquer alteração.                             
      227 +**Decisão:** os três arquivos são lidos e todo o processamento
          + e a serialização acontecem em memória antes de tocar o disco.
          + A gravação escreve num arquivo temporário no **mesmo diretóri
          +o** da saída e faz `os.replace` para o nome final; em qualquer
          + falha, remove o temporário. Pasta inexistente ou sem permissã
          +o falha na criação do temporário, antes de qualquer alteração.
      228  **Alternativa descartada:** `open(output, "w")` direto: trunca
            o arquivo existente antes de escrever; uma falha no meio deix
           a arquivo parcial.
      229  **Consequência:** o arquivo de saída ou fica como estava, ou é
            substituído inteiro.
      230  
      231  ### DT-007 — Códigos de saída e mensagens
      232  
      233  **Contexto:** a spec exige só "código diferente de 0" e "mensa
           gem de erro".
      167 -**Decisão:** `0` sucesso; `1` erro de arquivo (mensagem `erro:
          - <descrição>` em stderr); `2` erro de uso (padrão do `argparse
          -`). Nenhuma exceção não tratada chega ao usuário como stack tr
          -ace por um erro previsto na RN-002.                           
      168 -**Alternativa descartada:** um único código para tudo: perderi
          -a a distinção útil para scripts, sem custo para cumpri-la.    
      169 -**Consequência:** os testes de CLI conferem `!= 0` (contrato) 
          -e o código exato (este plano).                                
      234 +**Decisão:**                                                  
      235 +- **Códigos:** `0` sucesso; `1` erro de arquivo, em qualquer u
          +m dos três arquivos de leitura ou na gravação; `2` erro de uso
          +, inclusive falta de `--politica` ou `--cambio` (padrão do `ar
          +gparse`).                                                     
      236 +- **Mensagem:** `erro: <arquivo>: <descrição>` em stderr, onde
          + `<arquivo>` é `entrada`, `política`, `câmbio` ou `saída`, e a
          + descrição diz o campo quando houver (ex.: `erro: política: ce
          +ntros_custo.CC-ADM.alimentacao.limite com mais de 2 casas deci
          +mais`). Os leitores levantam `ErroDeArquivo` com a descrição, 
          +e a CLI acrescenta o nome do arquivo.                         
      237 +- **Sem stack trace:** nenhuma exceção não tratada chega ao us
          +uário como stack trace por um erro previsto na RN-002 ou na RN
          +-016.                                                         
      238  
      239 +**Alternativa descartada:** um único código para tudo: perderi
          +a a distinção útil para scripts, sem custo para cumpri-la. Um 
          +código por arquivo: a spec não pede, e scripts que já tratam `
          +1` quebrariam.                                                
      240 +**Consequência:** os testes de CLI conferem `!= 0` (contrato) 
          +e o código exato (este plano). O texto da mensagem não é testa
          +do além do prefixo `erro:` e do nome do arquivo.              
      241 +                                                              
      242  ### DT-008 — Serialização determinística
      243  
      173 -**Contexto:** critério de aceite "a mesma entrada sempre produ
          -z a mesma saída".                                             
      174 -**Decisão:** itens na ordem de `posicao`; campos de cada objet
          -o na ordem da tabela da seção 4 da spec; `ensure_ascii=False`,
          - UTF-8, `indent=2`, quebra de linha final. Nenhuma decisão dep
          -ende de ordem de iteração de `set`; agrupamentos usam `dict` (
          -ordem de inserção).                                           
      244 +**Contexto:** critério de aceite "a mesma entrada, com a mesma
          + política e o mesmo câmbio, sempre produz a mesma saída".     
      245 +**Decisão:** itens na ordem de `posicao`; campos de cada objet
          +o na ordem da tabela da seção 4 da spec (topo: `colaborador`, 
          +`periodo`, `politica`, `itens`, `totais`, `avisos`; item: `id`
          +, `data`, `categoria`, `valor_informado`, `moeda`, `taxa_cambi
          +o`, `data_cotacao`, `valor_considerado`, `valor_reembolsado`, 
          +`status`, `motivo`, `em_viagem`, `limite_diario`, `justificati
          +va`, `avisos`); `ensure_ascii=False`, UTF-8, `indent=2`, quebr
          +a de linha final. Nenhuma decisão depende de ordem de iteração
          + de `set`; agrupamentos usam `dict` (ordem de inserção). A bus
          +ca da cotação percorre datas por aritmética (`data - timedelta
          +(dias)`), não por iteração sobre as chaves do câmbio.         
      246  **Consequência:** saída idêntica byte a byte entre execuções; 
           testável comparando duas execuções.
      247  
      248  ### DT-009 — Formatação de valores na justificativa
      249  
      250  **Contexto:** a justificativa é em português e não contratual 
           (seção 4), mas o exemplo da spec usa `45,00` e `03/07`.
      180 -**Decisão:** função própria em `justificativa.py` formata `Dec
          -imal` como `1.234,56` e datas como `DD/MM`, sem depender de `l
          -ocale` do sistema (que mudaria a saída entre máquinas e quebra
          -ria a DT-008).                                                
      251 +**Decisão:** função própria em `justificativa.py` formata `Dec
          +imal` como `1.234,56` e datas como `DD/MM`, sem depender de `l
          +ocale` do sistema (que mudaria a saída entre máquinas e quebra
          +ria a DT-008). Desde a 2.0, `justificar` não importa nada de `
          +politica.py`: o mínimo da nota chega como argumento, vindo da 
          +`Politica`. Para despesa em moeda estrangeira, a frase pode ci
          +tar a conversão (`22,00 EUR × 5,93 = 130,46`). A taxa é format
          +ada com as casas que tiver, sem arredondar, porque não é valor
          + monetário (seção 4).                                         
      252  **Consequência:** os testes conferem que toda justificativa é 
           texto não vazio; o conteúdo exato não é testado, para não tran
           sformar texto livre em contrato.
      253  
      254  ### DT-010 — Chaves repetidas pelo `object_pairs_hook`
      255  
      185 -**Contexto:** RN-013: vale a última ocorrência de uma chave re
          -petida, com aviso de texto fixo, caminho e ordem definidos. Um
          - `dict` comum descarta as ocorrências anteriores sem deixar ra
          -stro.                                                         
      186 -**Decisão:** o `object_pairs_hook` monta cada objeto como `Obj
          -etoJson` (subclasse de `dict`, preenchido pela última ocorrênc
          -ia), que guarda também a lista original de pares. Depois do pa
          -rse, `entrada.py` percorre o documento seguindo essa lista: ao
          - passar pela **primeira** ocorrência de uma chave repetida, em
          -ite o aviso; desce só no valor da ocorrência que valeu. Assim 
          -os avisos saem na ordem do arquivo, e valores descartados nunc
          -a são visitados. O percurso começa em cada elemento de `despes
          -as` com caminho relativo (avisos do item; elemento que é lista
          - começa por `[i]`; listas encadeadas viram `[i][j]`) e no rest
          -ante com caminho a partir da raiz (avisos do topo). As chaves 
          -comparadas são as `str` já decodificadas pelo parser, sem `uni
          -codedata.normalize` (RN-013); como o percurso só desce no valo
          -r que valeu, ocorrências dentro de valores descartados não ent
          -ram no `<n>` nem na ordem.                                    
      256 +**Contexto:** RN-013: na entrada, vale a última ocorrência de 
          +uma chave repetida, com aviso de texto fixo, caminho e ordem d
          +efinidos. RN-016: na política e no câmbio, chave repetida em q
          +ualquer objeto é erro de arquivo. Um `dict` comum descarta as 
          +ocorrências anteriores sem deixar rastro.                     
      257 +**Decisão:** o `object_pairs_hook` monta cada objeto como `Obj
          +etoJson` (subclasse de `dict`, preenchido pela última ocorrênc
          +ia), que guarda também a lista original de pares.             
      258 +- **Entrada:** depois do parse, `entrada.py` percorre o docume
          +nto seguindo essa lista. Ao passar pela **primeira** ocorrênci
          +a de uma chave repetida, emite o aviso, e desce só no valor da
          + ocorrência que valeu. Assim os avisos saem na ordem do arquiv
          +o, e valores descartados nunca são visitados.                 
      259 +- **Caminhos:** o percurso começa em cada elemento de `despesa
          +s` com caminho relativo, para os avisos do item. Um elemento q
          +ue é lista começa por `[i]`, e listas encadeadas viram `[i][j]
          +`. No restante, o caminho parte da raiz, para os avisos do top
          +o.                                                            
      260 +- **Comparação de chaves:** as chaves comparadas são as `str` 
          +já decodificadas pelo parser, sem `unicodedata.normalize` (RN-
          +013). Como o percurso só desce no valor que valeu, ocorrências
          + dentro de valores descartados não entram no `<n>` nem na orde
          +m.                                                            
      261 +- **Política e câmbio:** `leitura.py` oferece `rejeitar_chaves
          +_repetidas(documento)`, que percorre **todos** os `ObjetoJson`
          + pelos pares e levanta `ErroDeArquivo` na primeira chave que a
          +parece duas vezes no mesmo objeto, com o caminho na mensagem. 
      262 +                                                              
      263  **Alternativa descartada:** detectar repetição no texto bruto 
           com expressão regular ou um tokenizador próprio — reescreveria
            o parser; e `parse` padrão + segunda leitura: duas fontes da 
           verdade para o mesmo arquivo.
      188 -**Consequência:** o resto do código vê `dict` comum; a RN-013 
          -fica inteira em `entrada.py`, testável com strings JSON curtas
          -.                                                             
      264 +**Consequência:** o resto do código vê `dict` comum. A RN-013 
          +fica inteira em `entrada.py`, e a rejeição da RN-016 é uma fun
          +ção de 10 linhas sobre a mesma estrutura, todas testáveis com 
          +strings JSON curtas.                                          
      265  
      266 +### DT-011 — Forma do arquivo num módulo comum (`leitura.py`) 
      267 +                                                              
      268 +**Contexto:** RN-016: política e câmbio "seguem as mesmas regr
          +as de forma do arquivo de entrada" (UTF-8, BOM, JSON estrito, 
          +escapes). Na 1.2, tudo isso está em `entrada.py` (`ler_json`, 
          +`ObjetoJson`, `ErroDeArquivo`, `_data`, `_tem_texto`, `_numero
          +`), que o plano restringe à RN-002 e à RN-013.                
      269 +**Decisão:** mover para `leitura.py`, **sem mudar comportament
          +o**, `ler_json`, `ObjetoJson`, `ErroDeArquivo`, a verificação 
          +de escapes e os testes de tipo da DT-003 (públicos: `e_numero`
          +, `e_data`, `tem_texto`, `e_codigo_de_moeda`, `tem_ate_2_casas
          +`). `entrada.py`, `politica.py` e `cambio.py` importam de lá. 
          +Os testes da forma (`test_leitura_json.py`) passam a importar 
          +de `leitura.py`. A mudança é um `refactor` com a suíte verde a
          +ntes e depois.                                                
      270 +**Alternativa descartada:** `politica.py` e `cambio.py` import
          +arem de `entrada.py`: criaria dependência da política para a e
          +ntrada, e a regra "entrada.py só aplica RN-002 e RN-013" deixa
          +ria de ser verdadeira. Duplicar a leitura: três cópias de uma 
          +regra que a spec declara única.                               
      271 +**Consequência:** as três leituras ficam iguais por construção
          +. Um único teste por armadilha de forma cobre os três arquivos
          +, e cada leitor só precisa de um teste de integração que mostr
          +e que usa `ler_json`.                                         
      272 +                                                              
      273 +### DT-012 — Produto exato na conversão                       
      274 +                                                              
      275 +**Contexto:** RN-003 e AMB-026: o `valor` é multiplicado pela 
          +taxa e o **produto exato** é arredondado uma única vez. A prec
          +isão padrão do `Decimal` é de 28 dígitos, e um produto com mai
          +s dígitos é arredondado **em silêncio**, pela regra do context
          +o (`ROUND_HALF_EVEN`), antes do `quantize`. Um exemplo verific
          +ado: `999999999.99999999999 × 5.123456789123456789` tem 39 díg
          +itos e sai com 28. Um duplo arredondamento pode mudar o centav
          +o. O mesmo vale para o expoente: `1E-999999 × 5.93` passa do `
          +Emin` padrão e vira subnormal.                                
      276 +**Decisão:** `produto_exato(a, b)` em `motor.py` calcula `a * 
          +b` num `decimal.localcontext` com `prec = len(a.as_tuple().dig
          +its) + len(b.as_tuple().digits)` (o número de dígitos de um pr
          +oduto nunca passa da soma dos dígitos dos fatores), `Emin = MI
          +N_EMIN`, `Emax = MAX_EMAX` e `traps` em `Inexact`, `Rounded` e
          + `InvalidOperation`. Se o produto não for exato, isso é um def
          +eito do código, e a exceção sobe sem ser tratada. O `quantize`
          + da RN-003 roda depois, no contexto padrão: o resultado tem no
          + máximo 20 dígitos (DT-001). Para `BRL`, a taxa é `Decimal(1)`
          + e o produto é o próprio `valor`, pelo mesmo caminho, sem ramo
          + especial.                                                    
      277 +**Alternativa descartada:** aumentar a precisão do contexto gl
          +obal: afetaria todo o programa e continuaria finita. Arredonda
          +r `valor` antes de multiplicar: contraria a AMB-026 (16,8649 E
          +UR dá 99,98, não 100,01).                                     
      278 +**Consequência:** a conversão é exata para qualquer número ace
          +ito. Testes: o caso 16,8649 × 5,93 → 100,01, o caso 0,001 × 5,
          +93 → 0,01, o caso `1E-999999` em EUR → `valor_invalido`, e um 
          +par de fatores com mais de 28 dígitos no produto, conferido co
          +ntra a conta feita à mão.                                     
      279 +                                                              
      280 +### DT-013 — Limite em viagem: produto exato e truncamento    
      281 +                                                              
      282 +**Contexto:** RN-009 e AMB-022: o limite em viagem é o limite 
          +normal × (1 + percentual / 100), **truncado** ao centavo, e só
          + para `alimentacao` e `transporte_urbano`. O percentual pode t
          +er qualquer número de casas (RN-016 só exige número não negati
          +vo abaixo do teto).                                           
      283 +**Decisão:** em `politica.py`, `limite_diario` faz o seguinte:
      284 +- devolve o limite normal se `em_viagem` é falso ou se a categ
          +oria não está em `CATEGORIAS_AMPLIADAS_EM_VIAGEM`;            
      285 +- senão, calcula `produto_exato(limite, 100 + percentual)` (DT
          +-012) e divide por 100, uma divisão exata em decimal que só mo
          +ve o expoente (`scaleb(-2)`);                                 
      286 +- aplica `quantize(Decimal("0.01"), ROUND_DOWN)`. Como o limit
          +e e o percentual não são negativos, `ROUND_DOWN` (em direção a
          +o zero) é o truncamento da spec.                              
      287 +                                                              
      288 +`produto_exato` fica em `leitura.py`? Não: fica num módulo de 
          +aritmética só se surgir um terceiro uso. Por ora `politica.py`
          + o importa de `motor.py`? Também não, porque criaria ciclo (`m
          +otor` importa `politica`). **Decisão final:** `produto_exato` 
          +e `arredondar` ficam em `politica.py`, ao lado das constantes 
          +de arredondamento. `motor.py` os importa.                     
      289 +**Alternativa descartada:** `ROUND_FLOOR`: igual para não nega
          +tivos, mas esconde a intenção. Escrever 90,00 e 120,00 por ext
          +enso, como na 1.2: os valores agora vêm do arquivo.           
      290 +**Consequência:** 33,33 com 50% dá 49,99, e 60,00 com 50% dá 9
          +0,00, iguais à tabela da RN-009. Os testes de limite da 1.x co
          +ntinuam valendo com a tabela `padrao` da v4.                  
      291 +                                                              
      292 +### DT-014 — Busca da cotação de D a D-3                      
      293 +                                                              
      294 +**Contexto:** RN-015 e AMB-024: a cotação é a da moeda na data
          + da despesa. Se essa data não tem cotação **dessa moeda**, usa
          +-se a data anterior mais próxima que a tenha, até D-3, nunca u
          +ma data posterior. `BRL` tem taxa 1 sem consultar o arquivo.  
      295 +**Decisão:** `cotacao(cambio, moeda, data)` em `cambio.py`:   
      296 +- se `moeda == MOEDA_BASE`, devolve `Cotacao(Decimal(1), None)
          +`;                                                            
      297 +- senão, para `dias` de 0 a `DIAS_ANTERIORES_ACEITOS_NA_COTACA
          +O`, calcula `d = data - timedelta(days=dias)` e devolve `Cotac
          +ao(taxas[d][moeda], d)` na primeira data em que existe `taxas[
          +d][moeda]`;                                                   
      298 +- devolve `None` se nenhuma das quatro datas tem a moeda;     
      299 +- se `data - timedelta` sair do calendário (antes de 0001-01-0
          +1), para a busca ali: nenhuma data anterior existe.           
      300 +                                                              
      301 +**Alternativa descartada:** ordenar as datas do arquivo e proc
          +urar a anterior mais próxima com busca binária: mais código pa
          +ra o mesmo resultado com, no máximo, 4 consultas a dicionário.
          + E a janela fixa deixa explícito o "até 3 dias".              
      302 +**Consequência:** uma data intermediária que só cota outras mo
          +edas é pulada naturalmente (caso de borda "Data intermediária 
          +sem a moeda"). `data_cotacao` sai de `Cotacao.data.isoformat()
          +`, que é igual ao texto do arquivo, porque a chave foi validad
          +a como `AAAA-MM-DD` com dígitos ASCII (DT-003).               
      303 +                                                              
      304 +### DT-015 — Validação dos arquivos de política e câmbio      
      305 +                                                              
      306 +**Contexto:** RN-016 lista os defeitos que são erro de arquivo
          +. Qualquer um encerra a execução.                             
      307 +**Decisão:** `ler_politica` e `ler_cambio` recebem o documento
          + já lido por `leitura.ler_json` e chamam `rejeitar_chaves_repe
          +tidas` (DT-010). Depois validam campo a campo, **na ordem da l
          +ista da RN-016**, e levantam `ErroDeArquivo` no primeiro defei
          +to, com o caminho do campo na mensagem (DT-007).              
      308 +                                                              
      309 +Regras de implementação que a RN-016 deixa implícitas:        
      310 +- **Campos opcionais** (`versao`, `vigencia`, `moeda_base`, `c
          +entros_custo`): `raiz.get(campo) is None` cobre ausente e `nul
          +l`, que valem a mesma coisa.                                  
      311 +- **`moeda_base`:** presente tem de ser exatamente a `str` `"B
          +RL"`. `"brl"` e `1` são erro.                                 
      312 +- **Tabela:** é um objeto (`dict`). Cada nome de categoria é n
          +ormalizado (`normalizar_texto`). Nome vazio depois da normaliz
          +ação, ou repetido entre nomes normalizados da mesma tabela, é 
          +erro. Cada regra é objeto com `limite` (número, ≥ 0, abaixo do
          + teto, até 2 casas) e `periodicidade` em `PERIODICIDADES`. Os 
          +demais campos da regra são ignorados sem validação.           
      313 +- **Chaves de `centros_custo`:** `"padrao"`, texto vazio ou só
          + com espaço em branco (`not tem_texto(chave)`) são erro. Qualq
          +uer outro texto é aceito como está.                           
      314 +- **Números:** a ordem dos testes é tipo → sinal → teto → casa
          +s, para que o `quantize` do teste de casas só rode em número a
          +baixo do teto (DT-003). O mínimo da nota tem o mesmo teste do 
          +limite. O percentual não tem limite de casas. A taxa precisa s
          +er maior que 0.                                               
      315 +- **Câmbio:** a chave `"BRL"` dentro de uma data é pulada **an
          +tes** de qualquer validação (`"BRL": 0` não é erro). As demais
          + chaves precisam ser código de moeda (DT-003). Campos da raiz 
          +fora de `moeda_base` e `taxas` são ignorados.                 
      316 +- **`-0`:** como limite, mínimo ou percentual, vale 0, porque 
          +`Decimal("-0") < 0` é falso. Um limite `-0` é uma categoria ve
          +dada (AMB-021). A spec trata o número pelo valor, e o valor é 
          +zero.                                                         
      317 +                                                              
      318 +**Alternativa descartada:** acumular todos os defeitos e lista
          +r de uma vez: a spec só exige que haja erro, e listar tudo exi
          +giria decidir como continuar depois de um tipo errado.        
      319 +**Consequência:** cada linha da RN-016 vira pelo menos um test
          +e de `ErroDeArquivo`, em `tests/test_rn016_arquivos_de_politic
          +a_e_cambio.py`.                                               
      320 +                                                              
      321 +### DT-016 — Rastreabilidade com pendências durante a Fase 5  
      322 +                                                              
      323 +**Contexto:** desde a spec 2.0, `test_rastreabilidade.py` falh
          +a: a RN-014 a RN-016 e 37 casos da seção 7 ainda não têm teste
          + (D-007). O `pre-commit` roda a suíte inteira, então **todo** 
          +commit `feat(T-NNN)` da Fase 5 seria bloqueado até a última ta
          +sk, e o fluxo de um commit por task deixaria de funcionar.    
      324 +**Decisão:** a primeira task da Fase 5 cria em `test_rastreabi
          +lidade.py` um registro explícito e **estrito** de pendências: 
      325 +                                                              
      326 +```python                                                     
      327 +PENDENTES = {            # some quando a Fase 5 terminar (DT-0
          +16)                                                           
      328 +    "RN-014": "T-0NN",                                        
      329 +    "Centro de custo da tabela": "T-0NN",                     
      330 +    ...                                                       
      331 +}                                                             
      332 +```                                                           
      333 +                                                              
      334 +- Uma regra ou caso **sem** teste só é aceito se estiver em `P
          +ENDENTES`.                                                    
      335 +- Uma pendência que **já tem** teste faz a suíte falhar, como 
          +um `xfail(strict=True)`. Assim, a task que escreve o teste é o
          +brigada a tirar a pendência no mesmo commit.                  
      336 +- Uma pendência que não está mais na spec também faz a suíte f
          +alhar.                                                        
      337 +- A última task da Fase 5 apaga `PENDENTES` e o código que o l
          +ê, e a rastreabilidade volta a ser a da 1.x.                  
      338 +                                                              
      339 +**Alternativa descartada:**                                   
      340 +- **`SEM_PYTEST` ou `--no-verify` nos commits:** perderia a pr
          +oteção do hook justamente nas tasks que mudam regra.          
      341 +- **Escrever de uma vez os testes dos 37 casos, marcados `xfai
          +l`:** os esperados seriam escritos antes do desenho de cada ta
          +sk, e a revisão por task perderia o foco.                     
      342 +- **Uma única task com toda a v4:** um commit gigante, sem rev
          +isão por regra.                                               
      343 +                                                              
      344 +**Consequência:** a suíte fica verde em todo commit da Fase 5.
          + O dono de cada pendência fica visível no código, e uma pendên
          +cia esquecida ou já resolvida quebra a suíte. A tabela de Cobe
          +rtura do `tasks.md` é preenchida pela mesma lista.            
      345 +                                                              
      346  ## 6. Estratégia de testes
      347  
      348  - **Nível e proporção:**
      193 -  - **Unitários (~70%)** — `normalizacao`, `entrada` (cada ite
          -m da RN-002 e cada armadilha da DT-003), `motor` (uma regra po
          -r arquivo), sem disco.                                        
      194 -  - **Integração (~20%)** — `entrada → motor → saida` com `exe
          -mplos/despesas-exemplo.json` contra a tabela da seção 9 da spe
          -c, transcrita à mão para o teste (nunca copiada da saída do pr
          -ograma), e totais 1.861,84 / 585,43 / 1.276,41.               
      195 -  - **Ponta a ponta (~10%)** — `cli.main([...])` com `tmp_path
          -`: código de saída, arquivo criado, arquivo preexistente intac
          -to em erro, erro de uso, pasta inexistente, determinismo byte 
          -a byte.                                                       
      196 -- **Cada `RN-NNN` da spec tem teste?** Um arquivo por regra (`
          -tests/test_rn001_um_resultado_por_despesa.py`, …, `test_rn013_
          -chave_repetida.py`), cobrindo pelo menos o **Aceite** da regra
          -. `tests/test_rastreabilidade.py` lê a `spec.md`, extrai todos
          - os `RN-NNN` e falha se algum não aparecer no nome ou na docst
          -ring de pelo menos um teste.                                  
      349 +  - **Unitários (~70%)** — `normalizacao`; `leitura` (cada arm
          +adilha de forma e de tipo, DT-002 e DT-003); `entrada` (cada i
          +tem da RN-002, inclusive `moeda` e `centro_custo`); `politica`
          + e `cambio` (cada linha da RN-016, escolha da tabela, limite e
          +m viagem, busca da cotação), com documentos JSON curtos e sem 
          +disco; `motor` (uma regra por arquivo), com `Politica` e `Camb
          +io` construídos.                                              
      350 +  - **Integração (~20%)** — `entrada → motor → saida` com os *
          +*três** arquivos da seção 9 da spec (`exemplos/despesas-exempl
          +o.json`, `exemplos/envelope/despesas-envelope.json`, `exemplos
          +/envelope/despesas-envelope-cc-desconhecido.json`), com `polit
          +ica-v4.json` e `cambio.json`. As três tabelas da seção 9 e seu
          +s totais são transcritos à mão para o teste, nunca copiados da
          + saída do programa.                                           
      351 +  - **Ponta a ponta (~10%)** — `cli.main([...])` com `tmp_path
          +`: código de saída, arquivo criado, arquivo preexistente intac
          +to em erro de qualquer um dos três arquivos de leitura, erro d
          +e uso (inclusive sem `--politica` ou `--cambio`), pasta inexis
          +tente, determinismo byte a byte.                              
      352 +- **Cada `RN-NNN` da spec tem teste?** Um arquivo por regra (`
          +tests/test_rn001_um_resultado_por_despesa.py`, …, `test_rn014_
          +tabela_aplicada.py`, `test_rn015_moeda_e_cambio.py`, `test_rn0
          +16_arquivos_de_politica_e_cambio.py`), cobrindo pelo menos o *
          +*Aceite** da regra. `tests/test_rastreabilidade.py` lê a `spec
          +.md`, extrai todos os `RN-NNN` e falha se algum não aparecer n
          +o nome ou na docstring de pelo menos um teste (com as pendênci
          +as da DT-016 durante a Fase 5).                               
      353  - **Casos de borda da seção 7 da spec:** `tests/test_casos_de_
           borda.py`, um teste parametrizado por linha da tabela, com `id
           ` igual ao texto da coluna "Caso". `test_rastreabilidade.py` t
           ambém extrai a coluna "Caso" da seção 7 e falha se algum caso 
           não tiver teste com esse `id` — caso novo na spec sem teste qu
           ebra a suíte.
      198 -- **Nomenclatura:** `test_rnNNN_<comportamento>` com docstring
          - `"""RN-NNN / AMB-NNN: <o que a spec diz>"""`; o esperado de c
          -ada teste tem um comentário com a conta feita a partir da spec
          - (ex.: `# 72,50 + 38,00 > 60,00 → 60,00 e 0`). O nome remete à
          - regra; a docstring, à decisão.                               
      199 -- **Fixtures:** um construtor de entrada mínima válida em `tes
          -ts/conftest.py` (`entrada(despesas=[...])`, `despesa(**campos)
          -`), para cada teste declarar só o que importa ao caso.        
      354 +- **Nomenclatura:** `test_rnNNN_<comportamento>` com docstring
          + `"""RN-NNN / AMB-NNN: <o que a spec diz>"""`; o esperado de c
          +ada teste tem um comentário com a conta feita a partir da spec
          + (ex.: `# 22,00 × 5,93 = 130,46 > 60,00 → 60,00`). O nome reme
          +te à regra; a docstring, à decisão.                           
      355 +- **Fixtures** (`tests/conftest.py`):                         
      356 +  - **Entrada:** os construtores `entrada(...)` e `despesa(**c
          +ampos)` continuam, e `entrada` ganha `centro_custo`.          
      357 +  - **Política e câmbio:** construtores novos `construir_polit
          +ica(**sobrescritas)` e `construir_cambio(taxas=...)` geram doc
          +umentos válidos. O padrão de cada um é o conteúdo de `exemplos
          +/envelope/politica-v4.json` e `cambio.json` **transcrito** no 
          +`conftest.py`, não lido do disco, para um teste de regra não m
          +udar se alguém editar o exemplo.                              
      358 +  - **Pipeline:** `processar(texto_json, politica=None, cambio
          +=None)` usa a v4 e o câmbio do envelope quando não recebe outr
          +os. Por isso os testes da 1.x, que não definem centro de custo
          + nem moeda, continuam válidos sem mudança: a tabela `padrao` d
          +a v4 tem os mesmos valores da 1.9, e o mínimo da nota também (
          +D-007).                                                       
      359 +- **Testes da 1.x afetados:**                                 
      360 +  - `test_politica.py` (constantes) é substituído pelos testes
          + da RN-014 e da RN-016.                                       
      361 +  - `test_exemplo.py` é reescrito com as três tabelas da seção
          + 9.                                                           
      362 +  - `test_cli.py` e os casos de borda que chamam `main` passam
          + a incluir `--politica` e `--cambio`.                         
      363 +  - Os testes de saída ganham os campos novos.                
      364  
      365  ## 7. Riscos
      366  
      367  | Risco | Probabilidade | O que faço se acontecer |
      368  |---|---|---|
      369  | `float` entrar por acidente numa conta (ex.: literal `0.01`,
            `round()`) | média | Teste de propriedade sobre a saída (nenh
           um valor monetário é `float`); ruff + revisão no `revisor-de-t
           ask`; constantes só como `Decimal("…")` |
      206 -| Implementação divergir da ordem da seção 8 (ex.: duplicata a
          -ntes da nota) | média | Casos de borda que só passam na ordem 
          -certa (relançamento com nota, duplicata de hospedagem com só u
          -ma nota, alimentação antes da hospedagem) |                   
      207 -| Valor gigante (`1e999999`, inteiro com milhares de dígitos) 
          -quebrar a leitura ou o cálculo | baixa | Resolvido na spec 1.4
          - (AMB-018, D-004): `entrada_invalida`. No código, `parse_int=D
          -ecimal` e o teto testado antes de qualquer `quantize`; casos d
          -e borda com `1e999999` e inteiro de 5.000 dígitos |           
      208 -| Chave repetida passar sem aviso (ex.: uma troca de parser qu
          -e não chame o `object_pairs_hook`) | baixa | Resolvido na spec
          - 1.4 (RN-013, D-004); os testes da RN-013 quebram se o aviso s
          -umir |                                                        
      209 -| Envelope do Dia 2 mudar política, regra ou formato | alta (é
          - certo) | Fronteiras da seção 2: política em `politica.py`, re
          -gras em `motor.py` com etapas em lista ordenada, formato em `e
          -ntrada.py`/`saida.py`; rastreabilidade automática (seção 6) ap
          -onta os testes afetados |                                     
      370 +| Produto da conversão ou do limite em viagem arredondado em s
          +ilêncio pela precisão do contexto | média | DT-012: contexto l
          +ocal exato com `Inexact` e `Rounded` como trap; teste com prod
          +uto de mais de 28 dígitos |                                   
      371 +| Implementação divergir da ordem da seção 8 (ex.: duplicata a
          +ntes da nota, câmbio depois do período) | média | Casos de bor
          +da que só passam na ordem certa (relançamento com nota, duplic
          +ata de hospedagem com só uma nota, alimentação antes da hosped
          +agem, "Sem cotação e fora do período") |                      
      372 +| Categoria de saída de despesa inválida divergir da dos itens
          + válidos (duas regras de "reconhecida") | média | Seção 3: uma
          + só função `categoria_de_saida`, chamada pelo motor para todo 
          +item; caso "Categoria reconhecível em despesa inválida" com `C
          +C-COMERCIAL` e `representacao` |                              
      373 +| Testes da 1.x passarem a depender do conteúdo de `exemplos/e
          +nvelope/` e quebrarem se o exemplo mudar | baixa | Política e 
          +câmbio padrão transcritos no `conftest.py` (seção 6); só os te
          +stes de aceite da seção 9 leem os arquivos de exemplo |       
      374 +| Suíte vermelha bloquear todo commit da Fase 5 | certa sem aç
          +ão | DT-016: pendências explícitas e estritas, removidas na úl
          +tima task |                                                   
      375 +| Valor gigante (`1e999999`, inteiro com milhares de dígitos) 
          +quebrar a leitura ou o cálculo | baixa | Resolvido na spec 1.4
          + (AMB-018, D-004) e estendido aos números da política e do câm
          +bio na 2.0 (RN-016); `parse_int=Decimal` e o teto testado ante
          +s de qualquer `quantize` |                                    
      376 +| Chave repetida passar sem aviso na entrada, ou sem erro na p
          +olítica e no câmbio (ex.: uma troca de parser que não chame o 
          +`object_pairs_hook`) | baixa | Testes da RN-013 e da RN-016 qu
          +ebram se o aviso ou o erro sumirem |                          
      377 +| Nova mudança de política (outro centro de custo, outra categ
          +oria, outro percentual) | alta | Absorvida sem código: só o ar
          +quivo muda. O que ainda exige código está listado na seção 4 (
          +constantes de interpretação) e no risco "Categorias reconhecid
          +as pelo nome" da seção 10 da spec |                           
      378  | Testes passarem por concordarem com o código, não com a spec
            | média | Esperados calculados à mão a partir da spec (skill 
           `/task`, passo 4); `revisor-de-task` confere teste contra spec
            antes do commit |

⏺ Deixei um trecho de raciocínio solto no DT-013. Vou trocá-lo por uma decisão
  direta: um módulo pequeno, dinheiro.py, para os arredondamentos.

⏺ Update(specs/001-motor-reembolso/plan.md)
  ⎿  Added 2 lines, removed 2 lines
      283  **Decisão:** em `politica.py`, `limite_diario` faz o seguinte:
      284  - devolve o limite normal se `em_viagem` é falso ou se a categ
           oria não está em `CATEGORIAS_AMPLIADAS_EM_VIAGEM`;
      285  - senão, calcula `produto_exato(limite, 100 + percentual)` (DT
           -012) e divide por 100, uma divisão exata em decimal que só mo
           ve o expoente (`scaleb(-2)`);
      286 -- aplica `quantize(Decimal("0.01"), ROUND_DOWN)`. Como o limit
          -e e o percentual não são negativos, `ROUND_DOWN` (em direção a
          -o zero) é o truncamento da spec.                              
      286 +- aplica `truncar` (`quantize(Decimal("0.01"), ROUND_DOWN)`). 
          +Como o limite e o percentual não são negativos, `ROUND_DOWN` (
          +em direção ao zero) é o truncamento da spec.                  
      287  
      288 -`produto_exato` fica em `leitura.py`? Não: fica num módulo de 
          -aritmética só se surgir um terceiro uso. Por ora `politica.py`
          - o importa de `motor.py`? Também não, porque criaria ciclo (`m
          -otor` importa `politica`). **Decisão final:** `produto_exato` 
          -e `arredondar` ficam em `politica.py`, ao lado das constantes 
          -de arredondamento. `motor.py` os importa.                     
      288 +`produto_exato`, `arredondar` (RN-003) e `truncar` ficam em `d
          +inheiro.py` (seção 2), usado por `motor.py` e `politica.py`. S
          +e ficassem em `motor.py`, `politica.py` teria de importá-lo, e
          + `motor` já importa `politica`.                               
      289  **Alternativa descartada:** `ROUND_FLOOR`: igual para não nega
           tivos, mas esconde a intenção. Escrever 90,00 e 120,00 por ext
           enso, como na 1.2: os valores agora vêm do arquivo.
      290  **Consequência:** 33,33 com 50% dá 49,99, e 60,00 com 50% dá 9
           0,00, iguais à tabela da RN-009. Os testes de limite da 1.x co
           ntinuam valendo com a tabela `padrao` da v4.
      291  

⏺ Update(specs/001-motor-reembolso/plan.md)
  ⎿  Added 1 line, removed 1 line
      273  ### DT-012 — Produto exato na conversão
      274  
      275  **Contexto:** RN-003 e AMB-026: o `valor` é multiplicado pela 
           taxa e o **produto exato** é arredondado uma única vez. A prec
           isão padrão do `Decimal` é de 28 dígitos, e um produto com mai
           s dígitos é arredondado **em silêncio**, pela regra do context
           o (`ROUND_HALF_EVEN`), antes do `quantize`. Um exemplo verific
           ado: `999999999.99999999999 × 5.123456789123456789` tem 39 díg
           itos e sai com 28. Um duplo arredondamento pode mudar o centav
           o. O mesmo vale para o expoente: `1E-999999 × 5.93` passa do `
           Emin` padrão e vira subnormal.
      276 -**Decisão:** `produto_exato(a, b)` em `motor.py` calcula `a * 
          -b` num `decimal.localcontext` com `prec = len(a.as_tuple().dig
          -its) + len(b.as_tuple().digits)` (o número de dígitos de um pr
          -oduto nunca passa da soma dos dígitos dos fatores), `Emin = MI
          -N_EMIN`, `Emax = MAX_EMAX` e `traps` em `Inexact`, `Rounded` e
          - `InvalidOperation`. Se o produto não for exato, isso é um def
          -eito do código, e a exceção sobe sem ser tratada. O `quantize`
          - da RN-003 roda depois, no contexto padrão: o resultado tem no
          - máximo 20 dígitos (DT-001). Para `BRL`, a taxa é `Decimal(1)`
          - e o produto é o próprio `valor`, pelo mesmo caminho, sem ramo
          - especial.                                                    
      276 +**Decisão:** `produto_exato(a, b)` em `dinheiro.py` calcula `a
          + * b` num `decimal.localcontext` com `prec = len(a.as_tuple().
          +digits) + len(b.as_tuple().digits)` (o número de dígitos de um
          + produto nunca passa da soma dos dígitos dos fatores), `Emin =
          + MIN_EMIN`, `Emax = MAX_EMAX` e `traps` em `Inexact`, `Rounded
          +` e `InvalidOperation`. Se o produto não for exato, isso é um 
          +defeito do código, e a exceção sobe sem ser tratada. O `quanti
          +ze` da RN-003 roda depois, no contexto padrão: o resultado tem
          + no máximo 20 dígitos (DT-001). Para `BRL`, a taxa é `Decimal(
          +1)` e o produto é o próprio `valor`, pelo mesmo caminho, sem r
          +amo especial.                                                 
      277  **Alternativa descartada:** aumentar a precisão do contexto gl
           obal: afetaria todo o programa e continuaria finita. Arredonda
           r `valor` antes de multiplicar: contraria a AMB-026 (16,8649 E
           UR dá 99,98, não 100,01).
      278  **Consequência:** a conversão é exata para qualquer número ace
           ito. Testes: o caso 16,8649 × 5,93 → 100,01, o caso 0,001 × 5,
           93 → 0,01, o caso `1E-999999` em EUR → `valor_invalido`, e um 
           par de fatores com mais de 28 dígitos no produto, conferido co
           ntra a conta feita à mão.
      279  

⏺ Update(specs/001-motor-reembolso/plan.md)
  ⎿  Added 1 line
      49  | `politica.py` | documento → `Politica` (RN-016, parte da polí
          tica); escolha da tabela aplicada (RN-014); limite diário norma
          l e em viagem (RN-009, DT-013); as constantes de interpretação 
          que a spec fixa e o arquivo não traz (seção 4 deste plano) | nã
          o |
      50  | `cambio.py` | **novo.** Documento → `Cambio` (RN-016, parte d
          o câmbio); busca da cotação de D a D-3 (RN-015, DT-014) | não |
      51  | `normalizacao.py` | `normalizar_texto()` — os passos da seção
           5 da spec | não |
      52 +| `dinheiro.py` | **novo.** `arredondar` (RN-003), `truncar` (R
         +N-009) e `produto_exato` (DT-012, DT-013): a aritmética de `Dec
         +imal` usada pelo motor e pela política, sem regra de negócio al
         +ém do modo de arredondamento | não |                           
      53  | `motor.py` | etapas 2 a 9 da seção 8; recebe `Entrada`, `Poli
          tica` e `Cambio` e devolve `Resultado` | não |
      54  | `justificativa.py` | frase em português para cada item (texto
           não contratual) | não |
      55  | `saida.py` | `Resultado` → dicionário na ordem de campos da s
          eção 4 da spec → texto JSON | não |

⏺ Update(specs/001-motor-reembolso/plan.md)
  ⎿  Added 1 line, removed 1 line
       7  > apareceu uma, ela pertence à `spec.md`.
       8  
       9  **O que mudou da 1.2 para a 2.0:** a política deixa de ser cons
          tante no código e passa a ser um arquivo lido a cada execução, 
          com uma tabela por centro de custo, e as despesas podem vir em 
          moeda estrangeira, convertidas por um arquivo de câmbio (spec 2
          .0, RN-014 a RN-016). No plano, isso muda o seguinte:
      10 -- a arquitetura ganha `leitura.py` (forma comum aos três arquiv
         -os) e `cambio.py`;                                             
      10 +- a arquitetura ganha `leitura.py` (forma comum aos três arquiv
         +os), `cambio.py` e `dinheiro.py` (aritmética exata);           
      11  - `politica.py` passa de constantes a leitor e validador do arq
          uivo de política;
      12  - o modelo ganha `Politica`, `Cambio` e os campos novos da saíd
          a;
      13  - o motor recebe a tabela aplicada e o câmbio;

  Ran 1 shell command (ctrl+o to expand)

⏺ Reescrevi o specs/001-motor-reembolso/plan.md para a versão 2.0, baseada na
  spec 2.0. Ainda não commitei nada: a ideia é fechar o bloco com plan e tasks
  juntos.

  O que mudou no plano:
  - Política vem do arquivo: politica.py passa a ler e validar o arquivo
    (RN-016), escolher a tabela (RN-014) e calcular o limite em viagem. No
    código ficam só as constantes de interpretação que o arquivo não traz, como
    as categorias que ampliam em viagem, hospedagem, D+1 e o teto.
  - Módulos novos:
    - leitura.py: a forma comum aos três arquivos (UTF-8, JSON estrito, escapes,
      testes de tipo), tirada de entrada.py sem mudar o comportamento (DT-011);
    - cambio.py: leitura do câmbio e busca da cotação de D a D-3 (DT-014);
    - dinheiro.py: arredondar, truncar e multiplicar de forma exata.
  - Categoria de saída decidida no motor: "reconhecida" agora depende da tabela
    aplicada, então entrada.py guarda o texto como veio e o motor decide para
    todo item, inclusive os inválidos.
  - DT-012, produto exato: testei e confirmei que o contexto padrão do Decimal
    arredonda em silêncio produtos com mais de 28 dígitos, por exemplo
    999999999.99999999999 × 5.123456789123456789. Sem um contexto local exato, a
    conversão pode arredondar duas vezes, o que a RN-003 proíbe.
  - DT-015: o que a RN-016 deixa implícito, como null valer ausente, a entrada
    BRL do câmbio ser pulada antes de validar e a ordem tipo → sinal → teto →
    casas.

  Pontos que você precisa olhar antes das tasks:
  1. DT-016, a suíte vermelha. Hoje o pytest falha em 2 testes de
     rastreabilidade (647 passam), e isso bloquearia todo feat(T-NNN) da Fase 5.
     Proponho que a primeira task crie uma lista PENDENTES (regra ou caso →
     task dona) em test_rastreabilidade.py. A lista é estrita: uma pendência que
     já tem teste quebra a suíte. A última task apaga a lista. As alternativas
     descartadas estão no DT-016.
  2. O CLAUDE.md contradiz a spec 2.0. Ele lista "conversão de moeda" e
     "categoria de representação" como fora de escopo, mostra o comando sem
     --politica e --cambio e diz que as constantes da política vivem em
     politica.py. Precisa de um docs(claude) neste bloco ou numa task.
  3. Defaults do conftest.py. A política e o câmbio padrão dos testes ficam
     transcritos lá, sem ler de exemplos/envelope/. Assim os testes da 1.x
     continuam válidos sem mudança, porque a tabela padrao da v4 tem os mesmos
     valores da 1.9.

  O próximo passo é a Fase 5 do tasks.md, numerada a partir da T-022. Ela
  substitui as tasks que o D-007 lista e começa pelo refactor do leitura.py e
  pelas pendências. Sigo com as tasks, ou você quer revisar o plano antes?

✻ Churned for 5m 40s · done Friday 9:29 PM

※ recap: Estamos adaptando o motor à Política v4, e o plan.md 2.0 está escrito, mas ainda não foi commitado. O próximo passo é você revisar o plano, sobretudo a lista de pendências do DT-016, para eu seguir com as tasks da Fase 5 a partir da T-022. (disable recaps in /config)

❯ vamos revisar o plano                                                         

⏺ Your organization has disabled Claude subscription access for Claude 
  Code · Use an Anthropic API key instead, or ask your admin to enable 
  access

✻ Brewed for 0s · done 2:26 PM

❯ arrumei minha assinatura ao claude, vamos continuar na revisao do plano       

⏺ Vou reler o plano contra a spec e o código procurando furos. Antes, quero
  confirmar uma suspeita sobre o DT-013.

  Ran 1 shell command (ctrl+o to expand)
  ⎿  1 skill available

⏺ Confirmei que 100 + percentual arredonda silenciosamente no contexto padrão,
  repetindo o mesmo defeito do DT-012 no DT-013 do plano. Vou corrigir isso
  junto com outros três pontos que encontrei ao revisar o plano contra a spec.

  Searched for 1 pattern (ctrl+o to expand)

⏺ Bash(uv run python - <<'EOF'
      from pathlib import Path…)
  ⎿  Updated specs/001-motor-reembolso/plan.md (+17 -17)
      27  | Testes | `pytest` | Testes como funções simples, `parametrize
          ` para tabelas de casos (seção 7 da spec), `tmp_path` para a CL
          I | `unittest`: mais cerimônia por teste, sem ganho |
      28  | Lint | `ruff` (regras `E`, `F`, `I`, `B`, `UP`) | Já exigido 
          pelo `pre-commit`; um só binário para lint e ordenação de impor
          ts | `flake8` + `isort`: duas ferramentas para o mesmo papel |
      29  | Parsing/validação | `simplejson` com `use_decimal=True` (leit
          ura e escrita), `object_pairs_hook` para chaves repetidas (DT-0
          10) + validação manual campo a campo, para os três arquivos | L
          ê `33.333` direto como `Decimal("33.333")`, sem passar por `flo
          at`, e escreve `Decimal` como número JSON exato; o hook entrega
           os pares de cada objeto na ordem do arquivo, inclusive os repe
          tidos (aviso na entrada, erro na política e no câmbio). A valid
          ação da entrada precisa produzir **item `entrada_invalida`** po
          r despesa, não exceção — regra fina demais para um validador de
           schema | `json` da biblioteca padrão: lê com `parse_float=Deci
          mal`, mas não escreve `Decimal` como número — teria que convert
          er para `float` na saída e `valor_informado` perderia dígitos a
          lém do 17º. `pydantic`/`jsonschema`: rejeitam o documento intei
          ro ou exigem contornos para "erro vira item" e para copiar camp
          os de tipo errado como nulo; para política e câmbio, um schema 
          não expressa "casas decimais pelo valor exato", "nomes de categ
          oria distintos depois de normalizar" nem chave repetida |
      30 -| Aritmética monetária | `decimal.Decimal`; arredondamento com 
         -`quantize(Decimal("0.01"), ROUND_HALF_UP)`; produtos exatos em 
         -contexto local (DT-012); limite em viagem com `ROUND_DOWN` (DT-
         -013) | Exato ao centavo; `ROUND_HALF_UP` do Python arredonda a 
         -metade **afastando do zero** (-0,005 → -0,01), exatamente a RN-
         -003 | `float`: `1.005` é guardado como `1.00499…` e `round(1.00
         -5, 2)` dá 1,00 (a RN-003 exige 1,01); `round(0.125, 2)` dá 0,12
         -, porque `round` arredonda a metade para o par. Centavos em `in
         -t`: exige arredondar na conversão de qualquer forma, e o número
         - informado (33,333) não cabe em centavos |                     
      30 +| Aritmética monetária | `decimal.Decimal`; arredondamento com 
         +`quantize(Decimal("0.01"), ROUND_HALF_UP)`; toda conta em conte
         +xto exato (DT-012); limite em viagem com `ROUND_DOWN` (DT-013) 
         +| Exato ao centavo; `ROUND_HALF_UP` do Python arredonda a metad
         +e **afastando do zero** (-0,005 → -0,01), exatamente a RN-003 |
         + `float`: `1.005` é guardado como `1.00499…` e `round(1.005, 2)
         +` dá 1,00 (a RN-003 exige 1,01); `round(0.125, 2)` dá 0,12, por
         +que `round` arredonda a metade para o par. Centavos em `int`: e
         +xige arredondar na conversão de qualquer forma, e o número info
         +rmado (33,333) não cabe em centavos |                          
      31  | CLI | `argparse` (biblioteca padrão) | Um subcomando, quatro 
          opções obrigatórias; erro de uso já sai com código 2 e mensagem
           em stderr | `click`/`typer`: dependência a mais para uma inter
          face fixa e mínima |
      32  
      33  ## 2. Arquitetura
     ...
      49  | `politica.py` | documento → `Politica` (RN-016, parte da polí
          tica); escolha da tabela aplicada (RN-014); limite diário norma
          l e em viagem (RN-009, DT-013); as constantes de interpretação 
          que a spec fixa e o arquivo não traz (seção 4 deste plano) | nã
          o |
      50  | `cambio.py` | **novo.** Documento → `Cambio` (RN-016, parte d
          o câmbio); busca da cotação de D a D-3 (RN-015, DT-014) | não |
      51  | `normalizacao.py` | `normalizar_texto()` — os passos da seção
           5 da spec | não |
      52 -| `dinheiro.py` | **novo.** `arredondar` (RN-003), `truncar` (R
         -N-009) e `produto_exato` (DT-012, DT-013): a aritmética de `Dec
         -imal` usada pelo motor e pela política, sem regra de negócio al
         -ém do modo de arredondamento | não |                           
      52 +| `dinheiro.py` | **novo.** `contexto_exato()` (DT-012), `arred
         +ondar` (RN-003) e `truncar` (RN-009, DT-013): a aritmética de `
         +Decimal` usada pelo motor e pela política, sem regra de negócio
         + além do modo de arredondamento | não |                        
      53  | `motor.py` | etapas 2 a 9 da seção 8; recebe `Entrada`, `Poli
          tica` e `Cambio` e devolve `Resultado` | não |
      54  | `justificativa.py` | frase em português para cada item (texto
           não contratual) | não |
      55  | `saida.py` | `Resultado` → dicionário na ordem de campos da s
          eção 4 da spec → texto JSON | não |
     ...
      63  - **Regra:** muda `motor.py`.
      64  - **Formato de entrada ou saída:** muda `entrada.py` ou `saida.
          py`.
      65  
      66 -**Ordem de leitura e erros:** a CLI lê e valida a entrada, depo
         -is a política e depois o câmbio, tudo antes de calcular. O prim
         -eiro erro encerra a execução, com uma mensagem que nomeia o arq
         -uivo (DT-007). A spec não fixa qual erro aparece quando há mais
         - de um. Basta que nenhum gere saída.                           
      66 +**Ordem de leitura e erros:** a CLI lê os bytes dos três arquiv
         +os e valida a política, depois o câmbio e depois a entrada, tud
         +o antes de calcular. Política e câmbio vêm antes porque a seção
         + 8 da spec os valida "antes de qualquer despesa", e `entrada.py
         +` já valida as despesas (etapa 1). A diferença não é observável
         +, já que todo erro encerra a execução sem saída, mas o código f
         +ica na ordem da spec. O primeiro erro encerra a execução, com u
         +ma mensagem que nomeia o arquivo (DT-007). A spec não fixa qual
         + erro aparece quando há mais de um. Basta que nenhum gere saída
         +.                                                              
      67  
      68  Comando final: `uv run reembolso calcular --input <entrada> --p
          olitica <política> --cambio <câmbio> --output <saída>` (entry p
          oint `reembolso = "reembolso.cli:main"` no `pyproject.toml`).
      69  
     ...
      152  ```
      153  
      154  **Funções** (todas puras):
      155 -- `ler_politica(documento) -> Politica`: aplica a parte da RN-
          -016 sobre a política (DT-015).                                
      155 +- `ler_politica(conteudo: bytes) -> Politica`: aplica a parte 
          +da RN-016 sobre a política (DT-015).                          
      156  - `tabela_aplicada(politica, centro_custo) -> TabelaAplicada`:
            aplica a RN-014. Se `centro_custo` tem texto fora do espaço e
           m branco e é chave exata de `centros_custo`, usa essa tabela; 
           em qualquer outro caso, usa o `padrao`.
      157  - `limite_diario(tabela_aplicada, categoria, em_viagem, percen
           tual) -> Decimal`: aplica a RN-009 com a DT-013.
      158  - `categoria_de_saida(texto, tabela) -> str | None`: aplica a 
           seção 4. Devolve a forma normalizada se ela está na tabela, se
           não o texto como veio, e `None` se não é texto.
      159 -- `ler_cambio(documento) -> Cambio` e `cotacao(cambio, moeda, 
          -data) -> Cotacao | None` (em `cambio.py`): aplicam a RN-016 e 
          -a RN-015 (DT-014).                                            
      159 +- `ler_cambio(conteudo: bytes) -> Cambio` e `cotacao(cambio, m
          +oeda, data) -> Cotacao | None` (em `cambio.py`): aplicam a RN-
          +016 e a RN-015 (DT-014).                                      
      160  
      161  **Descartado:**
      162  - **Manter constantes como "padrão de fábrica" e o arquivo com
           o sobrescrita.** Seriam duas fontes da verdade, e a AMB-020 de
           cide que o padrão é o bloco `padrao` do arquivo. Um limite esq
           uecido no código mudaria o resultado sem nada visível mudar (A
           MB-031).
     ...
      168  ### DT-001 — Dinheiro em `Decimal` lido direto do texto JSON
      169  
      170  **Contexto:** RN-003 exige arredondar a metade afastando do ze
           ro e cálculos exatos ao centavo; `valor_informado` é o número 
           recebido (33.333), na moeda da despesa.
     … 61 more lines (ctrl+o to expand)

⏺ Revisei o plano contra a spec e corrigi quatro problemas no plan.md: um bug de
  arredondamento silencioso em percentuais longos (resolvido com um contexto
  decimal exato), uma ressalva obsoleta sobre soma de dígitos, a ordem de
  validação (agora política → câmbio → entrada, conforme a spec) e a
  padronização das assinaturas dos leitores para bytes. Também verifiquei se
  havia regra de negócio indevida no plano e não encontrei nada além de um caso
  já previsto na spec; restam duas decisões que são suas.

⏺ User answered Claude's questions:
  ⎿  · DT-016: como deixar os commits da Fase 5 passarem pelo pre-commit 
     enquanto a rastreabilidade não fecha? → Lista PENDENTES (Recomendado)
     · O CLAUDE.md contradiz a spec 2.0 (moeda e representação aparecem como 
     fora de escopo, o comando não tem --politica/--cambio, as fronteiras dos 
     módulos mudaram). Quando atualizar? → Neste bloco (Recomendado)

⏺ Fico com as duas recomendações. O DT-016 já está escrito assim no plano. Agora
  atualizo o CLAUDE.md.

⏺ Bash(uv run python - <<'EOF'
      from pathlib import Path…)  ⎿   CLAUDE.md                         |  30 ++--
      specs/001-motor-reembolso/plan.md | 323 +++++++++++++++++++++++++++++
     ---------
      2 files changed, 266 insertions(+), 87 deletions(-)
  ⎿  Updated CLAUDE.md (+20 -10)
       3  ## O projeto
       4  
       5  Motor de cálculo de reembolso de despesas corporativas. CLI que
           lê um JSON de
       6 -despesas e emite um JSON com o valor reembolsável e a justifica
         -tiva de cada item.                                             
       6 +despesas, um arquivo de política (limites por centro de custo) 
         +e um arquivo de                                                
       7 +câmbio, e emite um JSON com o valor reembolsável e a justificat
         +iva de cada item.                                              
       8  
       9  ## Fonte da verdade
      10  
     ...
      72  - Linguagem: Python ≥ 3.12 gerenciado com `uv` (`pyproject.toml
          ` + `uv.lock`);
      73    o Python do sistema é 3.9, então sempre via `uv run`. Dependê
          ncia de runtime
      74    só `simplejson` ≥ 4; o resto é biblioteca padrão (`decimal`, 
          `argparse`, `unicodedata`).
      74 -- Rodar: `uv run reembolso calcular --input <entrada> --output 
         -<saída>`                                                       
      75 +- Rodar: `uv run reembolso calcular --input <entrada> --politic
         +a <política> --cambio <câmbio> --output <saída>`               
      76 +  (exemplos: `exemplos/envelope/politica-v4.json` e `exemplos/e
         +nvelope/cambio.json`)                                          
      77  - Testes: `uv run pytest -q`
      78  - Lint: `uv run ruff check .` (regras `E`, `F`, `I`, `B`, `UP`)
      79  - Pacote em `src/reembolso/`, testes em `tests/` (módulos e fro
          nteiras: `plan.md` seção 2).
     ...
       84  
       85  - **Dinheiro é `Decimal`, nunca `float`** (DT-001): lido diret
           o do texto JSON
       86    (`simplejson`, `use_decimal=True`), arredondado só com
       85 -  `quantize(Decimal("0.01"), ROUND_HALF_UP)` (RN-003). Um test
          -e de propriedade                                              
       87 +  `quantize(Decimal("0.01"), ROUND_HALF_UP)` (RN-003). Toda co
          +nta com dinheiro,                                             
       88 +  taxa ou percentual roda em `dinheiro.contexto_exato()` (DT-0
          +12): o contexto                                               
       89 +  padrão arredonda em silêncio além de 28 dígitos. Um teste de
          + propriedade                                                  
       90    garante que nenhum valor monetário da saída é `float`.
       91  - **Fronteiras dos módulos** (plan seção 2): só `cli.py` faz I
           /O (disco, argv,
       92    stderr, código de saída); o resto é função pura. Regra de ne
           gócio fica em
       89 -  `motor.py` + `politica.py` + `normalizacao.py`; constantes d
          -a política só em                                              
       90 -  `politica.py`; `entrada.py` só aplica a RN-002 e a RN-013.  
       91 -- **Erros** (DT-007, RN-002): problema no arquivo ou no cabeça
          -lho → `ErroDeArquivo`,                                        
       92 -  mensagem `erro: ...` em stderr, código 1, saída não criada n
          -em alterada                                                   
       93 +  `motor.py` + `politica.py` + `cambio.py` + `normalizacao.py`
          +. **Os números da                                             
       94 +  política (limites, mínimo da nota, percentual) vêm do arquiv
          +o `--politica`,                                               
       95 +  nunca do código**; só as constantes de interpretação (plan s
          +eção 4) ficam em                                              
       96 +  `politica.py` e `cambio.py`. `leitura.py` só aplica a forma 
          +do arquivo (UTF-8,                                            
       97 +  JSON estrito, escapes, tipos), comum aos três; `entrada.py` 
          +só aplica a RN-002                                            
       98 +  e a RN-013.                                                 
       99 +- **Erros** (DT-007, RN-002, RN-016): problema em qualquer dos
          + três arquivos ou                                             
      100 +  no cabeçalho da entrada → `ErroDeArquivo`, mensagem `erro: <
          +arquivo>: ...` em stderr, código 1, saída não criada nem alter
          +ada                                                           
     … 14 more lines (ctrl+o to expand)

⏺ Revisão do plano fechada. O CLAUDE.md também está atualizado para a spec 2.0.
  Nada foi commitado ainda.

  No CLAUDE.md:
  - Projeto e comando: a descrição do projeto e o comando calcular agora incluem
    --politica e --cambio, com os caminhos dos arquivos de exemplo.
  - Dinheiro: toda conta com dinheiro, taxa ou percentual roda em
    dinheiro.contexto_exato() (DT-012).
  - Fronteiras:
    - os números da política vêm do arquivo --politica, nunca do código;
    - cambio.py entra no grupo da regra de negócio;
    - leitura.py fica só com a forma do arquivo, comum aos três.
  - Erros: passam a valer para os três arquivos (RN-016), com mensagem erro: 
    <arquivo>: ....
  - Fora de escopo:
    - saíram conversão de moeda e categoria de representação, que agora estão no
      escopo;
    - entraram câmbio externo, verificação do centro de custo contra cadastro e
      fila de aprovação manual (item C da v4);
    - feriado e fim de semana passam a afetar só a escolha da cotação.

  O DT-016 fica como estava: a primeira task da Fase 5 cria a lista PENDENTES.

  O próximo passo é escrever a Fase 5 do tasks.md, numerada a partir da T-022.
  Ela fecha o bloco num commit só, com plan.md, CLAUDE.md, tasks.md e os
  arquivos de exemplos/envelope/. Antes desse commit vou pedir o /export da
  sessão. Sigo para as tasks?

✻ Cogitated for 2m 7s · done 2:31 PM

❯ segue para as tasks                                                           

  Ran 1 shell command (ctrl+o to expand)

⏺ Vou levantar quais casos de borda estão pendentes, porque cada um precisa de
  uma task dona:

  Ran 1 shell command (ctrl+o to expand)

⏺ Os 37 casos pendentes batem com o D-007. Agora escrevo a Fase 5.

⏺ Bash(cat > /private/tmp/claude-501/-Users-rafaeltxm-repo-sdd-desafio/189f9935-
      53e6-4885-9842-d69fe892da58/scratchpad/fase5.md <<'EOF'
      ## Fase 5 — Envelope: Política…)
  ⎿  168:## Fase 4 — Saída e CLI
     194:## Fase 5 — Envelope: Política v4 (spec 2.0, D-007)
     205:- [ ] **T-022** — Pendências da rastreabilidade: `PENDENTES` em `t
     … +57 lines (ctrl+o to expand)
  ⎿  Updated specs/001-motor-reembolso/tasks.md (+204 -5)
      1  # Tasks — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.2 · **Baseado em:** spec 1.9, plan 1.2            
      3 +**Versão:** 2.0 · **Baseado em:** spec 2.0, plan 2.0            
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
         - com `id` igual ao texto da coluna "Caso". As 63 linhas estão d
         -istribuídas entre as tasks; nenhuma fica sem dono.             
      19 +- **Casos de borda:** linhas da tabela da seção 7 da spec que a
         + task cobre, cada uma um caso de `tests/test_casos_de_borda.py`
         + com `id` igual ao texto da coluna "Caso". As 100 linhas (63 da
         + 1.x e 37 da 2.0) estão distribuídas entre as tasks; nenhuma fi
         +ca sem dono.                                                   
      20  
      21  O esperado de todo teste é calculado à mão a partir da spec, nu
          nca copiado da saída do programa.
      22  
     ...
      191  
      192  ---
      193  
      194 -## Fase 5 — Envelope (criar no Dia 2)                         
      194 +## Fase 5 — Envelope: Política v4 (spec 2.0, D-007)           
      195  
      196 -<Novas tasks a partir da mudança de requisito. Numeração conti
          -nua de onde parou —                                           
      197 -não reinicie e não renumere as antigas: a numeração é o eixo d
          -a rastreabilidade.>                                           
      196 +Tasks da mudança de requisito do Dia 2 (D-007, plan 2.0). As t
          +asks da 1.x **não são desmarcadas**: as que o D-007 lista como
          + afetadas são substituídas pelas tasks abaixo, e cada uma diz 
          +o que substitui. A ordem mantém a suíte verde em todo commit: 
      197 +1. **Fundação:** pendências da rastreabilidade (DT-016), `leit
          +ura.py` e `dinheiro.py`.                                      
      198 +2. **Peças puras:** leitores de política e câmbio, seleção da 
          +tabela e limite.                                              
      199 +3. **Ligação:** a CLI recebe os dois arquivos, e depois o moto
          +r passa a usá-los.                                            
      200 +4. **Moeda:** validação, depois conversão, depois duplicata.  
      201 +5. **Fechamento:** aceite com os três arquivos e fim das pendê
          +ncias.                                                        
      202 +                                                              
      203 +Cada task que escreve o teste de uma regra ou de um caso pende
          +nte tira a pendência de `PENDENTES` no mesmo commit (DT-016). 
          +O dono de cada pendência é a task que lista o caso em **Casos 
          +de borda**, ou a regra em **Remove pendência**.               
      204 +                                                              
      205 +- [ ] **T-022** — Pendências da rastreabilidade: `PENDENTES` e
          +m `tests/test_rastreabilidade.py`, com RN-014, RN-015, RN-016 
          +e os 37 casos novos da seção 7, cada um com a task dona (DT-01
          +6); arquivos de `exemplos/envelope/` versionados.             
      206 +  - **Tipo:** estrutura                                       
      207 +  - **Atende:** DT-016, seção 9 da spec (rastreabilidade)     
      208 +  - **Depende de:** T-021                                     
      209 +  - **Aceite:** `uv run pytest -q` verde. `tests/test_rastreab
          +ilidade.py` passa e ganha:                                    
      210 +    - `test_pendencia_com_teste_falha`: uma pendência que já t
          +em teste faz a verificação falhar;                            
      211 +    - `test_pendencia_fora_da_spec_falha`: uma pendência que n
          +ão está na spec faz a verificação falhar;                     
      212 +    - `test_dono_da_pendencia_e_task_da_fase_5`: todo dono é u
          +ma task `T-022` a `T-034` existente em `tasks.md`.            
     … 187 more lines (ctrl+o to expand)

⏺ Agora confiro que cada um dos 37 casos tem exatamente uma task dona, com o
  nome idêntico ao da spec:

  Ran 1 shell command (ctrl+o to expand)

⏺ Escrevi a Fase 5 no tasks.md: são 13 tasks, da T-022 à T-034. Conferi com um
  script que cada um dos 37 casos de borda novos tem exatamente uma task dona,
  com o nome igual ao da spec.

  ┌───────┬─────────────────────────────────────────────────┬───────────────┐
  │ Task  │                      O quê                      │     Tipo      │
  ├───────┼─────────────────────────────────────────────────┼───────────────┤
  │ T-022 │ Lista PENDENTES da rastreabilidade (DT-016) e   │ estrutura     │
  │       │ versionamento de exemplos/envelope/             │               │
  ├───────┼─────────────────────────────────────────────────┼───────────────┤
  │ T-023 │ leitura.py: forma do arquivo e testes de tipo   │ estrutura     │
  │       │ tirados de entrada.py, sem mudar comportamento  │ (refactor)    │
  ├───────┼─────────────────────────────────────────────────┼───────────────┤
  │ T-024 │ dinheiro.py: contexto exato, arredondar e       │ regra         │
  │       │ truncar                                         │               │
  ├───────┼─────────────────────────────────────────────────┼───────────────┤
  │ T-025 │ Leitor do arquivo de política (RN-016)          │ regra         │
  ├───────┼─────────────────────────────────────────────────┼───────────────┤
  │ T-026 │ Leitor do câmbio e busca da cotação de D a D-3  │ regra         │
  │       │ (RN-016, RN-015)                                │               │
  ├───────┼─────────────────────────────────────────────────┼───────────────┤
  │ T-027 │ Tabela aplicada, limite em viagem truncado e    │ regra         │
  │       │ categoria de saída (RN-014, RN-009)             │               │
  ├───────┼─────────────────────────────────────────────────┼───────────────┤
  │ T-028 │ CLI com --politica e --cambio; 8 casos de erro  │ estrutura     │
  │       │ de arquivo                                      │               │
  ├───────┼─────────────────────────────────────────────────┼───────────────┤
  │ T-029 │ Motor passa a usar a tabela aplicada; exemplo   │ regra         │
  │       │ recalculado para 351,43; 11 casos               │               │
  ├───────┼─────────────────────────────────────────────────┼───────────────┤
  │ T-030 │ Validação de moeda na entrada; 2 casos          │ regra         │
  ├───────┼─────────────────────────────────────────────────┼───────────────┤
  │ T-031 │ Conversão e cambio_indisponivel; 14 casos       │ regra         │
  ├───────┼─────────────────────────────────────────────────┼───────────────┤
  │ T-032 │ Duplicata compara a moeda; 2 casos              │ regra         │
  ├───────┼─────────────────────────────────────────────────┼───────────────┤
  │ T-033 │ Aceite com as tabelas do envelope e do centro   │ regra         │
  │       │ de custo desconhecido                           │               │
  ├───────┼─────────────────────────────────────────────────┼───────────────┤
  │ T-034 │ Fim das pendências e tabela de Cobertura        │ estrutura     │
  │       │ atualizada                                      │               │
  └───────┴─────────────────────────────────────────────────┴───────────────┘

  Pontos do desenho:
  - Suíte verde em todo commit. A T-028 já passa os dois arquivos ao motor, mas
    ele só começa a usá-los na T-029. Assim, o test_exemplo continua com a
    tabela da 1.9 até a T-029 reescrevê-lo, no mesmo commit em que o resultado
    muda.
  - Tasks antigas continuam marcadas. As da 1.x não foram desmarcadas: cada task
    nova diz qual delas substitui, como o D-007 previa.
  - Um intervalo com comportamento errado. Entre a T-031 e a T-032, a duplicata
    ainda ignora a moeda. Nenhum teste afirma o contrário nesse intervalo.
    Separei as duas para a revisão ficar focada; se preferir, junto as duas numa
    task só.
  - Exemplos fora deste commit. Os arquivos de exemplos/envelope/ ficam para a
    T-022, porque qualquer commit com exemplos/ dispara o pytest, que hoje está
    vermelho.

  O commit deste bloco leva plan.md, tasks.md, CLAUDE.md e o export da sessão.
  Ele fecha um bloco, então o hook exige o export junto. Para seguir:

  1. Rode /export docs/sessions/38-plan-e-tasks-v4.md.
  2. Eu commito tudo como docs(plan): plan 2.0 e tasks da Fase 5 (Política v4),
     com o CLAUDE.md e o export no mesmo commit.

  Depois disso, paro e só começo a T-022 quando você mandar.

✻ Cogitated for 3m 5s · done 2:34 PM