"""Arquivos de política e de câmbio: RN-016, AMB-029, AMB-031, DT-015."""

from datetime import date
from decimal import Decimal

import pytest
import simplejson

from conftest import construir_cambio, construir_politica
from reembolso.cambio import ler_cambio
from reembolso.leitura import ErroDeArquivo
from reembolso.politica import ler_politica

# --- política -----------------------------------------------------------------


def _bytes(documento) -> bytes:
    return simplejson.dumps(documento, use_decimal=True).encode()


def _com(caminho, valor):
    """Política v4 com `valor` no `caminho` (tupla de chaves) da raiz."""
    documento = construir_politica()
    alvo = documento
    for chave in caminho[:-1]:
        alvo = alvo[chave]
    alvo[caminho[-1]] = valor
    return documento


def _sem(caminho):
    """Política v4 sem a chave no fim do `caminho`."""
    documento = construir_politica()
    alvo = documento
    for chave in caminho[:-1]:
        alvo = alvo[chave]
    del alvo[caminho[-1]]
    return documento


def _erro_de_arquivo(conteudo: bytes) -> str:
    with pytest.raises(ErroDeArquivo) as erro:
        ler_politica(conteudo)
    return str(erro.value)


@pytest.mark.parametrize(
    ("trecho", "defeito", "esperado"),
    [
        pytest.param(b'"v4"', b'"v\xe9"', "UTF-8", id="utf8_invalido"),
        pytest.param(b'"v4"', b'"v4",', "JSON", id="json_invalido"),
        pytest.param(b'"v4"', b'"\\ud800"', "escape", id="escape_sem_par"),
    ],
)
def test_rn016_politica_com_forma_invalida_e_erro_de_arquivo(trecho, defeito, esperado):
    """RN-016: a política segue a forma do arquivo de entrada (UTF-8, JSON, escapes)."""
    # a v4, válida no resto: o erro só pode vir da forma
    texto = _bytes(construir_politica()).replace(trecho, defeito, 1)
    assert esperado in _erro_de_arquivo(texto)


def test_rn016_politica_com_categoria_repetida_na_mesma_tabela():
    """RN-016: chave repetida em qualquer objeto da política é erro, sem RN-013."""
    texto = (
        '{"padrao": {"alimentacao": {"limite": 60, "periodicidade": "dia"}, '
        '"alimentacao": {"limite": 90, "periodicidade": "dia"}}, '
        '"nota_fiscal_obrigatoria_acima_de": 100, "acrescimo_em_viagem_percentual": 50}'
    )
    assert "padrao.alimentacao" in _erro_de_arquivo(texto.encode())


def test_rn016_politica_com_versao_repetida_na_raiz():
    """RN-016: chave repetida na raiz da política é erro, mesmo com valores válidos."""
    texto = _bytes(construir_politica())[:-1] + b', "versao": "v5"}'
    assert "versao" in _erro_de_arquivo(texto)


@pytest.mark.parametrize(
    ("documento", "campo"),
    [
        # raiz
        pytest.param([], "raiz", id="raiz_lista"),
        pytest.param(_com(("versao",), "   "), "versao", id="versao_so_espacos"),
        pytest.param(_com(("versao",), Decimal(4)), "versao", id="versao_numero"),
        pytest.param(_com(("versao",), ""), "versao", id="versao_vazia"),
        pytest.param(
            _com(("vigencia",), "2026-02-30"), "vigencia", id="vigencia_inexistente"
        ),
        pytest.param(
            _com(("vigencia",), "2026-7-1"), "vigencia", id="vigencia_sem_zeros"
        ),
        pytest.param(
            _com(("vigencia",), Decimal(2026)), "vigencia", id="vigencia_numero"
        ),
        pytest.param(
            _com(("moeda_base",), "brl"), "moeda_base", id="moeda_base_minuscula"
        ),
        pytest.param(
            _com(("moeda_base",), Decimal(1)), "moeda_base", id="moeda_base_numero"
        ),
        # tabelas
        pytest.param(_sem(("padrao",)), "padrao", id="padrao_ausente"),
        pytest.param(_com(("padrao",), None), "padrao", id="padrao_nulo"),
        pytest.param(_com(("padrao",), []), "padrao", id="padrao_lista"),
        pytest.param(
            _com(("centros_custo",), []), "centros_custo", id="centros_custo_lista"
        ),
        pytest.param(
            _com(("centros_custo", "CC-ADM"), []),
            "centros_custo.CC-ADM",
            id="centro_de_custo_que_nao_e_tabela",
        ),
        pytest.param(
            _com(("centros_custo", "CC-ADM"), None),
            "centros_custo.CC-ADM",
            id="centro_de_custo_nulo",
        ),
        pytest.param(
            _com(("centros_custo", "padrao"), {}),
            "centros_custo.padrao",
            id="centro_de_custo_padrao",
        ),
        pytest.param(
            _com(("centros_custo", ""), {}),
            "centros_custo.:",
            id="centro_de_custo_vazio",
        ),
        pytest.param(
            _com(("centros_custo", "  "), {}),
            "centros_custo.  :",
            id="centro_de_custo_so_espacos",
        ),
        # números da raiz
        pytest.param(
            _sem(("nota_fiscal_obrigatoria_acima_de",)),
            "nota_fiscal_obrigatoria_acima_de",
            id="minimo_ausente",
        ),
        pytest.param(
            _com(("nota_fiscal_obrigatoria_acima_de",), "100"),
            "nota_fiscal_obrigatoria_acima_de",
            id="minimo_texto",
        ),
        pytest.param(
            _com(("nota_fiscal_obrigatoria_acima_de",), Decimal(-1)),
            "nota_fiscal_obrigatoria_acima_de",
            id="minimo_negativo",
        ),
        pytest.param(
            _com(("nota_fiscal_obrigatoria_acima_de",), Decimal("100.001")),
            "nota_fiscal_obrigatoria_acima_de",
            id="minimo_tres_casas",
        ),
        pytest.param(
            _com(("nota_fiscal_obrigatoria_acima_de",), True),
            "nota_fiscal_obrigatoria_acima_de",
            id="minimo_booleano",
        ),
        pytest.param(
            _sem(("acrescimo_em_viagem_percentual",)),
            "acrescimo_em_viagem_percentual",
            id="percentual_ausente",
        ),
        pytest.param(
            _com(("acrescimo_em_viagem_percentual",), "50"),
            "acrescimo_em_viagem_percentual",
            id="percentual_texto",
        ),
        pytest.param(
            _com(("acrescimo_em_viagem_percentual",), Decimal(-1)),
            "acrescimo_em_viagem_percentual",
            id="percentual_negativo",
        ),
        # regras de categoria
        pytest.param(
            _com(("padrao", "-"), {"limite": Decimal(10), "periodicidade": "dia"}),
            "padrao.-",
            id="categoria_que_normaliza_vazia",
        ),
        pytest.param(
            _com(
                ("padrao", "Alimentação"),
                {"limite": Decimal(10), "periodicidade": "dia"},
            ),
            "padrao.Alimentação",
            id="categorias_iguais_depois_de_normalizar",
        ),
        pytest.param(
            _com(("padrao", "alimentacao"), Decimal(60)),
            "padrao.alimentacao",
            id="regra_que_nao_e_objeto",
        ),
        pytest.param(
            _sem(("padrao", "alimentacao", "limite")),
            "padrao.alimentacao.limite",
            id="limite_ausente",
        ),
        pytest.param(
            _com(("padrao", "alimentacao", "limite"), "60"),
            "padrao.alimentacao.limite",
            id="limite_texto",
        ),
        pytest.param(
            _com(("padrao", "alimentacao", "limite"), True),
            "padrao.alimentacao.limite",
            id="limite_booleano",
        ),
        pytest.param(
            _com(("centros_custo", "CC-ADM", "alimentacao", "limite"), Decimal(-10)),
            "centros_custo.CC-ADM.alimentacao.limite",
            id="limite_negativo",
        ),
        pytest.param(
            _com(("padrao", "alimentacao", "limite"), Decimal("60.005")),
            "padrao.alimentacao.limite",
            id="limite_tres_casas",
        ),
        pytest.param(
            _sem(("padrao", "hospedagem", "periodicidade")),
            "padrao.hospedagem.periodicidade",
            id="periodicidade_ausente",
        ),
        pytest.param(
            _com(("padrao", "hospedagem", "periodicidade"), "mes"),
            "padrao.hospedagem.periodicidade",
            id="periodicidade_mes",
        ),
        # teto (AMB-018): a partir de 1.000.000.000
        pytest.param(
            _com(("padrao", "alimentacao", "limite"), Decimal("1000000000")),
            "padrao.alimentacao.limite",
            id="limite_no_teto",
        ),
        pytest.param(
            _com(("padrao", "alimentacao", "limite"), Decimal("1e999999")),
            "padrao.alimentacao.limite",
            id="limite_gigante",
        ),
        pytest.param(
            _com(("nota_fiscal_obrigatoria_acima_de",), Decimal("1000000000")),
            "nota_fiscal_obrigatoria_acima_de",
            id="minimo_no_teto",
        ),
        pytest.param(
            _com(("nota_fiscal_obrigatoria_acima_de",), Decimal("1e999999")),
            "nota_fiscal_obrigatoria_acima_de",
            id="minimo_gigante",
        ),
        pytest.param(
            _com(("acrescimo_em_viagem_percentual",), Decimal("1000000000")),
            "acrescimo_em_viagem_percentual",
            id="percentual_no_teto",
        ),
        pytest.param(
            _com(("acrescimo_em_viagem_percentual",), Decimal("1e999999")),
            "acrescimo_em_viagem_percentual",
            id="percentual_gigante",
        ),
    ],
)
def test_rn016_politica_invalida_e_erro_de_arquivo_com_o_campo(documento, campo):
    """RN-016 / DT-015: cada defeito da política é erro de arquivo com o campo."""
    assert campo in _erro_de_arquivo(_bytes(documento))


def test_rn016_politica_v4_valida():
    """RN-016 / AMB-029: a v4 vira `Politica`; tabelas pela categoria normalizada."""
    politica = ler_politica(_bytes(construir_politica()))

    assert politica.versao == "v4"
    assert politica.vigencia == "2026-07-01"
    assert politica.padrao == {
        "alimentacao": Decimal("60.00"),
        "transporte_urbano": Decimal("80.00"),
        "hospedagem": Decimal("250.00"),
    }
    assert politica.centros_custo == {
        "CC-ENG-PLATAFORMA": {
            "alimentacao": Decimal("75.00"),
            "transporte_urbano": Decimal("80.00"),
            "hospedagem": Decimal("0.00"),  # `observacao` ignorada
        },
        "CC-COMERCIAL": {
            "alimentacao": Decimal("90.00"),
            "transporte_urbano": Decimal("150.00"),
            "hospedagem": Decimal("400.00"),
            "representacao": Decimal("300.00"),
        },
        "CC-ADM": {
            "alimentacao": Decimal("45.00"),
            "transporte_urbano": Decimal("60.00"),
        },
    }
    assert politica.nota_fiscal_acima_de == Decimal("100.00")
    assert politica.acrescimo_em_viagem_percentual == Decimal("50")


@pytest.mark.parametrize("ausencia", ["sem_campo", "nulo"])
def test_rn016_politica_sem_campos_opcionais_e_valida(ausencia):
    """RN-016 / AMB-029: sem os quatro campos opcionais (ou nulos) → válida."""
    documento = construir_politica()
    for campo in ("versao", "vigencia", "moeda_base", "centros_custo"):
        if ausencia == "sem_campo":
            del documento[campo]
        else:
            documento[campo] = None

    politica = ler_politica(_bytes(documento))

    assert politica.versao is None
    assert politica.vigencia is None
    assert politica.centros_custo == {}  # todos usam o `padrao`
    assert politica.padrao["alimentacao"] == Decimal("60.00")


@pytest.mark.parametrize(
    ("escrito", "esperado"),
    [
        ("60.000", "60.00"),  # 3 casas na forma, 2 pelo valor
        ("6E1", "60.00"),
        ("-0", "0.00"),  # -0 vale 0: categoria vedada (AMB-021, DT-015)
        ("999999999.99", "999999999.99"),  # logo abaixo do teto
    ],
)
def test_rn016_limite_valido_pelo_valor_exato(escrito, esperado):
    """RN-016: casas decimais e teto se medem pelo valor exato do número."""
    texto = _bytes(construir_politica()).replace(
        b'"alimentacao": {"limite": 60.00',
        b'"alimentacao": {"limite": ' + escrito.encode(),
        1,
    )
    limite = ler_politica(texto).padrao["alimentacao"]
    assert limite == Decimal(esperado)
    assert not limite.is_signed()


def test_rn016_numeros_da_raiz_com_minimo_e_percentual_extremos():
    """RN-016: `-0` vale 0; percentual sem limite de casas; logo abaixo do teto vale."""
    documento = construir_politica(
        nota_fiscal_obrigatoria_acima_de=Decimal("-0"),
        acrescimo_em_viagem_percentual=Decimal("999999999.123456789"),
    )
    politica = ler_politica(_bytes(documento))
    assert politica.nota_fiscal_acima_de == 0
    assert not politica.nota_fiscal_acima_de.is_signed()
    assert politica.acrescimo_em_viagem_percentual == Decimal("999999999.123456789")

    documento = construir_politica(
        nota_fiscal_obrigatoria_acima_de=Decimal("999999999.99"),
        acrescimo_em_viagem_percentual=Decimal("-0"),
    )
    politica = ler_politica(_bytes(documento))
    assert politica.nota_fiscal_acima_de == Decimal("999999999.99")
    assert politica.acrescimo_em_viagem_percentual == 0
    assert not politica.acrescimo_em_viagem_percentual.is_signed()


def test_rn016_periodicidade_diaria_em_qualquer_categoria():
    """RN-016 / RN-012: `dia` e `diaria` são o mesmo, em qualquer categoria."""
    documento = _com(("padrao", "alimentacao", "periodicidade"), "diaria")
    assert ler_politica(_bytes(documento)).padrao["alimentacao"] == Decimal("60.00")


def test_rn016_tabelas_vazias_sao_validas():
    """RN-016: tabela vazia é válida; nenhuma categoria é reconhecida nela."""
    documento = construir_politica(padrao={}, centros_custo={"CC-VAZIO": {}})
    politica = ler_politica(_bytes(documento))
    assert politica.padrao == {}
    assert politica.centros_custo == {"CC-VAZIO": {}}


def test_rn016_campos_nao_listados_sao_ignorados_sem_validacao():
    """RN-016: `observacao` numa regra e campo desconhecido na raiz são ignorados."""
    documento = construir_politica(fonte=Decimal("1e999999"))
    documento["padrao"]["alimentacao"]["observacao"] = Decimal("1e999999")
    politica = ler_politica(_bytes(documento))
    assert politica.padrao["alimentacao"] == Decimal("60.00")


def test_rn016_categoria_indexada_pela_forma_normalizada():
    """RN-016 / RN-006: a tabela é indexada pelo nome da categoria normalizado."""
    documento = construir_politica(
        padrao={"Transporte Urbano": {"limite": Decimal(80), "periodicidade": "dia"}}
    )
    padrao = ler_politica(_bytes(documento)).padrao
    assert padrao == {"transporte_urbano": Decimal("80")}


def test_rn016_centro_de_custo_indexado_pela_chave_como_escrita():
    """RN-016: a chave de `centros_custo` fica como veio (plan seção 4)."""
    documento = construir_politica(centros_custo={" cc-adm ": {}})
    assert list(ler_politica(_bytes(documento)).centros_custo) == [" cc-adm "]


# --- câmbio -------------------------------------------------------------------


def _cambio_com(caminho, valor):
    """Câmbio do envelope com `valor` no `caminho` (tupla de chaves) da raiz."""
    documento = construir_cambio()
    alvo = documento
    for chave in caminho[:-1]:
        alvo = alvo[chave]
    alvo[caminho[-1]] = valor
    return documento


def _erro_no_cambio(conteudo: bytes) -> str:
    with pytest.raises(ErroDeArquivo) as erro:
        ler_cambio(conteudo)
    return str(erro.value)


@pytest.mark.parametrize(
    ("documento", "campo"),
    [
        pytest.param([], "raiz", id="raiz_lista"),
        pytest.param(
            construir_cambio(moeda_base="USD"), "moeda_base", id="moeda_base_usd"
        ),
        pytest.param(
            construir_cambio(moeda_base="brl"), "moeda_base", id="moeda_base_minuscula"
        ),
        pytest.param(construir_cambio(taxas=None), "taxas", id="taxas_nulas"),
        pytest.param(
            {"moeda_base": "BRL", "fonte": "PTAX"}, "taxas", id="taxas_ausentes"
        ),
        pytest.param(construir_cambio(taxas=[]), "taxas", id="taxas_lista"),
        pytest.param(
            _cambio_com(("taxas", "2026-07-32"), {"USD": Decimal("5.40")}),
            "taxas.2026-07-32",
            id="data_inexistente",
        ),
        pytest.param(
            _cambio_com(("taxas", "2026-7-13"), {"USD": Decimal("5.40")}),
            "taxas.2026-7-13",
            id="data_sem_zeros",
        ),
        pytest.param(
            _cambio_com(("taxas", "2026-07-13"), Decimal("5.42")),
            "taxas.2026-07-13",
            id="data_que_nao_e_objeto",
        ),
        pytest.param(
            _cambio_com(("taxas", "2026-07-13", "usd"), Decimal("5.42")),
            "taxas.2026-07-13.usd",
            id="codigo_minusculo",
        ),
        pytest.param(
            _cambio_com(("taxas", "2026-07-13", "US"), Decimal("5.42")),
            "taxas.2026-07-13.US",
            id="codigo_de_2_letras",
        ),
        pytest.param(
            _cambio_com(("taxas", "2026-07-13", "USD"), Decimal(0)),
            "taxas.2026-07-13.USD",
            id="taxa_zero",
        ),
        pytest.param(
            _cambio_com(("taxas", "2026-07-13", "USD"), Decimal("-0")),
            "taxas.2026-07-13.USD",
            id="taxa_menos_zero",
        ),
        pytest.param(
            _cambio_com(("taxas", "2026-07-13", "USD"), Decimal("-5.4")),
            "taxas.2026-07-13.USD",
            id="taxa_negativa",
        ),
        pytest.param(
            _cambio_com(("taxas", "2026-07-13", "USD"), "5.4"),
            "taxas.2026-07-13.USD",
            id="taxa_texto",
        ),
        pytest.param(
            _cambio_com(("taxas", "2026-07-13", "USD"), True),
            "taxas.2026-07-13.USD",
            id="taxa_booleana",
        ),
        # teto (AMB-018): a partir de 1.000.000.000
        pytest.param(
            _cambio_com(("taxas", "2026-07-28", "EUR"), Decimal("1000000000")),
            "taxas.2026-07-28.EUR",
            id="taxa_no_teto",
        ),
        pytest.param(
            _cambio_com(("taxas", "2026-07-28", "EUR"), Decimal("1e999999")),
            "taxas.2026-07-28.EUR",
            id="taxa_gigante",
        ),
    ],
)
def test_rn016_cambio_invalido_e_erro_de_arquivo_com_o_campo(documento, campo):
    """RN-016 / DT-015: cada defeito do câmbio é erro de arquivo com o campo."""
    assert campo in _erro_no_cambio(_bytes(documento))


@pytest.mark.parametrize(
    ("texto", "campo"),
    [
        pytest.param(
            '{"taxas": {"2026-07-13": {"USD": 5.42}, "2026-07-13": {"USD": 5.44}}}',
            "taxas.2026-07-13",
            id="mesma_data_duas_vezes",
        ),
        pytest.param(
            '{"taxas": {"2026-07-13": {"USD": 5.42, "USD": 5.44}}}',
            "taxas.2026-07-13.USD",
            id="mesma_moeda_duas_vezes_na_data",
        ),
    ],
)
def test_rn016_cambio_com_chave_repetida_e_erro_de_arquivo(texto, campo):
    """RN-016: chave repetida em qualquer objeto do câmbio é erro, sem RN-013."""
    assert campo in _erro_no_cambio(texto.encode())


def test_rn016_cambio_com_forma_invalida_e_erro_de_arquivo():
    """RN-016: o câmbio segue a forma do arquivo de entrada (UTF-8)."""
    texto = _bytes(construir_cambio()).replace(b"PTAX", b"PT\xe9X", 1)
    assert "UTF-8" in _erro_no_cambio(texto)


def test_rn016_cambio_do_envelope_valido():
    """RN-016: o câmbio do envelope vira `Cambio`, com a taxa exata do arquivo."""
    cambio = ler_cambio(_bytes(construir_cambio()))
    assert len(cambio.taxas) == 12
    assert cambio.taxas[date(2026, 7, 17)] == {
        "USD": Decimal("5.47"),
        "EUR": Decimal("5.96"),
    }


@pytest.mark.parametrize(
    "brl",
    [
        pytest.param(Decimal(0), id="brl_zero"),
        pytest.param("x", id="brl_texto"),
    ],
)
def test_rn016_brl_e_campos_nao_listados_ignorados_sem_validacao(brl):
    """RN-016 / RN-015: BRL numa data, `fonte` e `observacao` são ignorados."""
    documento = construir_cambio(fonte=Decimal("1e999999"), observacao=[])
    documento["taxas"]["2026-07-13"]["BRL"] = brl
    cambio = ler_cambio(_bytes(documento))
    # a entrada BRL não entra no `Cambio` (plan seção 3)
    assert cambio.taxas[date(2026, 7, 13)] == {
        "USD": Decimal("5.42"),
        "EUR": Decimal("5.91"),
    }


def test_rn016_cambio_sem_moeda_base_e_valido():
    """RN-016: `moeda_base` ausente ou nula vale BRL."""
    documento = construir_cambio()
    del documento["moeda_base"]
    assert ler_cambio(_bytes(documento)).taxas
    assert ler_cambio(_bytes(construir_cambio(moeda_base=None))).taxas


@pytest.mark.parametrize(
    "taxa",
    [
        pytest.param(Decimal("999999999.999"), id="logo_abaixo_do_teto"),
        pytest.param(Decimal("5.4321987654321"), id="mais_de_2_casas"),
    ],
)
def test_rn016_taxa_valida_pelo_valor_exato(taxa):
    """RN-016: taxa abaixo do teto vale com qualquer número de casas, sem arredondar."""
    # o limite de 2 casas é só do limite e do mínimo da nota; a taxa sai exata
    documento = _cambio_com(("taxas", "2026-07-13", "USD"), taxa)
    assert ler_cambio(_bytes(documento)).taxas[date(2026, 7, 13)]["USD"] == taxa
