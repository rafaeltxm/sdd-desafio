import pytest

from reembolso.normalizacao import normalizar_texto


@pytest.mark.parametrize(
    "texto",
    [
        "Transporte Urbano",
        "transporte-urbano",
        " TRANSPORTE__urbano ",
        "Transporte – Urbano",  # travessão (U+2013)
    ],
)
def test_secao5_exemplos_transporte_urbano(texto):
    """Seção 5 / AMB-011: exemplos da spec que viram `transporte_urbano`."""
    # passo 1 (caixa) e passo 3 (pontas somem; espaço, hífen, `__`, " – " → um `_`)
    assert normalizar_texto(texto) == "transporte_urbano"


@pytest.mark.parametrize("texto", ["Pão  Quente", "pao-quente"])
def test_secao5_exemplos_pao_quente(texto):
    """Seção 5 / AMB-011: exemplos da spec que viram `pao_quente`."""
    # passo 2 (`ã` → `a`) e passo 3 (dois espaços ou hífen → um `_`)
    assert normalizar_texto(texto) == "pao_quente"


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("Padaria (Centro)", "padaria_centro"),  # " (" → `_`; ")" na ponta some
        ("McDonald's", "mcdonald_s"),  # "'" interno → `_`
        ("Straße", "strasse"),  # passo 1: equivalência completa de caixa
        ("Padaria Nº 1", "padaria_nº_1"),  # º é letra (categoria Unicode "letra")
        ("Padaria N° 1", "padaria_n_1"),  # ° é símbolo → separador
        ("Loja²", "loja"),  # ² não é dígito decimal → separador na ponta
        ("Smørrebrød", "smørrebrød"),  # passo 2: ø sem decomposição canônica
        ("-", ""),  # só separadores → vazio
    ],
)
def test_secao5_demais_exemplos_da_spec(texto, esperado):
    """Seção 5 (spec 1.8, D-005): exemplos de pontuação, `ß`, `ø` e texto vazio."""
    assert normalizar_texto(texto) == esperado


def test_secao5_pontuacao_interna_distingue_mcdonalds():
    """Seção 5 passo 3: `"McDonald's"` → `mcdonald_s`, diferente de `mcdonalds`."""
    assert normalizar_texto("McDonald's") != normalizar_texto("McDonalds")


def test_secao5_acento_precomposto_e_combinante_dao_o_mesmo_resultado():
    """Seção 5 passo 2 / AMB-011: "qualquer que seja a forma como o caractere foi
    codificado" — `ç`/`ã` pré-compostos e base + marca combinante são iguais."""
    precomposto = "alimentação"  # ç (U+00E7), ã (U+00E3)
    combinante = "alimentação"  # c + U+0327, a + U+0303
    assert precomposto != combinante
    assert normalizar_texto(precomposto) == "alimentacao"
    assert normalizar_texto(combinante) == "alimentacao"


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("ç", "c"),
        ("Ç", "c"),
        ("ô", "o"),
        ("ü", "u"),
        ("ñ", "n"),
        ("á", "a"),
        ("Bistrô", "bistro"),
    ],
)
def test_secao5_diacriticos_da_spec_viram_letra_base(texto, esperado):
    """Seção 5 passo 2: `á`→`a`, `ç`→`c`, `ô`→`o`, `ü`→`u`, `ñ`→`n`
    (e caixa, passo 1)."""
    assert normalizar_texto(texto) == esperado


@pytest.mark.parametrize(
    "texto",
    [
        "́alimentacao",  # sinal solto no início
        "alimentacao-́",  # sinal sobre hífen no fim
        "alimentacao️",  # seletor de variação
    ],
)
def test_secao5_sinal_combinante_solto_e_descartado(texto):
    """Seção 5 passo 2 (D-005): todo sinal combinante é descartado, acompanhe ele
    uma letra ou não; depois, o hífen do fim é separador na ponta (passo 3)."""
    assert normalizar_texto(texto) == "alimentacao"


@pytest.mark.parametrize(("texto", "esperado"), [("ø", "ø"), ("ł", "ł"), ("đ", "đ")])
def test_secao5_letra_sem_decomposicao_canonica_fica_como_esta(texto, esperado):
    """Seção 5 passo 2 (D-005): letra cujo traço faz parte dela fica como está."""
    assert normalizar_texto(texto) == esperado
    assert normalizar_texto("Smørrebrød") != normalizar_texto("Smorrebrod")


@pytest.mark.parametrize(
    "texto",
    [
        "\talimentacao",
        "alimentacao\t",
        "\nalimentacao\n",
        "\r\nalimentacao\r\n",
        " alimentacao ",  # espaço não separável
        "​alimentacao​",  # espaço de largura zero
        "﻿alimentacao",  # BOM
        "\x1calimentacao\x00",  # caracteres de controle
        " \t \n alimentacao \n \t ",
    ],
)
def test_secao5_separador_de_qualquer_tipo_nas_pontas_e_removido(texto):
    """Seção 5 passo 3: espaço em branco de qualquer tipo, invisível e controle nas
    pontas são separadores e são removidos (não viram `_`)."""
    assert normalizar_texto(texto) == "alimentacao"


@pytest.mark.parametrize(
    "texto",
    ["-Bistro", "_Bistro", "Bistro -", "Bistro_", " -_Bistro", "\t-Bistro- "],
)
def test_secao5_hifen_e_sublinhado_nas_pontas_sao_removidos(texto):
    """Seção 5 passo 3 (D-005): exemplos da spec; hífen e sublinhado nas pontas,
    em qualquer mistura com espaço, são removidos."""
    assert normalizar_texto(texto) == "bistro"


def test_secao5_categoria_com_hifen_no_fim_e_reconhecivel():
    """Seção 5 passo 3 (D-005) / AMB-011: `"alimentacao-"` → `alimentacao`."""
    assert normalizar_texto("alimentacao-") == "alimentacao"


@pytest.mark.parametrize(
    "texto",
    [
        "transporte - urbano",
        "transporte_-_urbano",
        "transporte \t-_ urbano",
        "transporte\n\nurbano",
        "transporte---urbano",
        "transporte urbano",  # espaço não separável interno
        "transporte—urbano",  # travessão (U+2014)
        "transporte/urbano",
        "transporte . & . urbano",
    ],
)
def test_secao5_mistura_de_separadores_internos_vira_um_sublinhado(texto):
    """Seção 5 passo 3: toda sequência interna de caracteres que não são letra nem
    algarismo vale como um único `_`."""
    assert normalizar_texto(texto) == "transporte_urbano"


def test_secao5_sequencias_internas_separadas_viram_um_sublinhado_cada():
    """Seção 5 passo 3: cada sequência interna vira um `_`, independentemente."""
    # "Pão  Quente - Centro": "  " → "_", " - " → "_"
    assert normalizar_texto("Pão  Quente - Centro") == "pao_quente_centro"


def test_secao5_algarismos_sao_mantidos():
    """Seção 5 passo 3: algarismos decimais contam, como as letras."""
    # "Loja-1" e "Loja 1": hífen e espaço internos → `_`; "1" fica
    assert normalizar_texto("Loja-1") == "loja_1"
    assert normalizar_texto("Loja 1") == "loja_1"


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("Café Ωμέγα", "cafe_ωμεγα"),  # grego: caixa e acento tirados, letras ficam
        ("Кафе Москва", "кафе_москва"),  # cirílico
        ("Loja ٣", "loja_٣"),  # ٣: algarismo decimal árabe-índico
    ],
)
def test_secao5_letras_de_qualquer_alfabeto_e_algarismos_decimais_contam(
    texto, esperado
):
    """Seção 5 passo 3: "só letras (de qualquer alfabeto) e algarismos decimais
    contam" — letra não latina e algarismo decimal não ASCII são mantidos."""
    assert normalizar_texto(texto) == esperado


@pytest.mark.parametrize("texto", ["Loja²", "Loja½", "Loja Ⅻ", "² Loja"])
def test_secao5_numero_que_nao_e_algarismo_decimal_e_separador(texto):
    """Seção 5 passo 3: `²`, `½` e `Ⅻ` não são algarismos decimais → separadores
    (nas pontas, removidos)."""
    assert normalizar_texto(texto) == "loja"


@pytest.mark.parametrize("texto", ["-", "***", " - ", "_", "", "́"])
def test_secao5_texto_so_de_separadores_fica_vazio(texto):
    """Seção 5 (D-005): texto só de separadores normaliza para vazio (a recusa como
    `entrada_invalida` é da RN-002, na validação)."""
    assert normalizar_texto(texto) == ""


def test_secao5_texto_ja_normalizado_fica_igual():
    """Seção 5: as categorias da política já estão na forma normalizada."""
    for texto in ("alimentacao", "transporte_urbano", "hospedagem"):
        assert normalizar_texto(texto) == texto


def test_secao5_ordinal_e_letra_e_grau_e_separador():
    """Seção 5 passo 3 (D-005 ponto 8): `"Padaria Nº 1"` ≠ `"Padaria N° 1"`."""
    assert normalizar_texto("Padaria Nº 1") != normalizar_texto("Padaria N° 1")


def test_secao5_letra_modificadora_e_letra_e_apostrofo_e_separador():
    """Seção 5 passo 3 (D-005 ponto 8): `ʼ` (U+02BC) é letra; `’` (U+2019) é
    pontuação → separador."""
    assert normalizar_texto("McDonald\u02bcs") == "mcdonald\u02bcs"
    assert normalizar_texto("McDonald\u2019s") == "mcdonald_s"


@pytest.mark.parametrize(
    "texto",
    [
        "alimentaःcao",  # Mc: marca com espaço próprio (devanágari)
        "alimentacao⃝",  # Me: marca envolvente
    ],
)
def test_secao5_marcas_com_espaco_proprio_e_envolventes_sao_descartadas(texto):
    """Seção 5 passo 2 (D-005 ponto 8): todo sinal combinante da categoria
    "marca" — sem espaço próprio, com espaço próprio ou envolvente — é descartado."""
    assert normalizar_texto(texto) == "alimentacao"


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("ali​mentacao", "ali_mentacao"),  # espaço de largura zero
        ("Bistro Cen­tral", "bistro_cen_tral"),  # hífen suave
        ("Bistrо Central", "bistrо_central"),  # о cirílico é outra letra
    ],
)
def test_secao5_invisivel_no_meio_e_separador_e_letra_parecida_e_distinta(
    texto, esperado
):
    """Seção 5 passo 3 / seção 10 (risco aceito): invisível no meio da palavra é
    separador (não é removido); `о` cirílico é letra distinta de `o`."""
    assert normalizar_texto(texto) == esperado
    assert normalizar_texto(texto) != normalizar_texto("Bistro Central")
