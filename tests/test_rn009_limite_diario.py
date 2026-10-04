"""Limite diário por categoria: RN-009, AMB-001, AMB-002, AMB-003, AMB-006, AMB-017.

Os casos de alimentação e transporte usam datas sem hospedagem com nota (fora de
viagem); os limites em viagem estão em `test_rn010_viagem.py`.
"""

from decimal import Decimal

import pytest
import simplejson

from conftest import construir_politica
from reembolso.politica import ler_politica, limite_diario, tabela_aplicada


def _resumo(item):
    return item["valor_reembolsado"], item["status"], item["motivo"]


def test_rn009_soma_do_dia_passa_do_limite_corta_a_ultima(avaliar, despesa):
    """RN-009 / AMB-001 / AMB-002 / AMB-003 / AMB-017: 72,50 e depois 38,00."""
    # "Almoço com cliente" é alimentação comum, com o limite normal (AMB-017)
    primeira, segunda = avaliar(
        despesa(id="d-001", valor=Decimal("72.50"), descricao="Almoco com cliente"),
        despesa(id="d-002", valor=Decimal("38.00"), fornecedor="Cantina"),
    )["itens"]

    # min(72,50; 60,00) = 60,00 → parcial; saldo 0
    assert _resumo(primeira) == (Decimal("60.00"), "parcial", "limite_diario_excedido")
    # saldo já era 0 → recusado com limite_diario_excedido
    assert _resumo(segunda) == (Decimal("0"), "recusado", "limite_diario_excedido")


def test_rn009_ordem_invertida_corta_a_ultima(avaliar, despesa):
    """RN-009 / AMB-003: 38,00 e depois 72,50 → consumo na ordem da entrada."""
    primeira, segunda = avaliar(
        despesa(id="d-002", valor=Decimal("38.00"), fornecedor="Cantina"),
        despesa(id="d-001", valor=Decimal("72.50")),
    )["itens"]

    # min(38,00; 60,00) = 38,00 → aprovado; saldo 22,00
    assert _resumo(primeira) == (Decimal("38.00"), "aprovado", None)
    # min(72,50; 22,00) = 22,00 → parcial
    assert _resumo(segunda) == (Decimal("22.00"), "parcial", "limite_diario_excedido")


@pytest.mark.parametrize(
    ("categoria", "limite"),
    [
        ("alimentacao", Decimal("60.00")),
        ("transporte_urbano", Decimal("80.00")),
        ("hospedagem", Decimal("250.00")),
    ],
)
def test_rn009_limite_normal_de_cada_categoria(avaliar, despesa, categoria, limite):
    """RN-009 / AMB-006: limites normais 60,00, 80,00 e 250,00."""
    # 300,00 com nota passa de todos os limites → parcial com o limite
    (item,) = avaliar(despesa(categoria=categoria, valor=Decimal("300.00")))["itens"]

    assert item["limite_diario"] == limite
    assert _resumo(item) == (limite, "parcial", "limite_diario_excedido")


def test_rn009_categorias_diferentes_na_mesma_data_nao_dividem_limite(
    avaliar, despesa
):
    """RN-009: o limite é por combinação de data e categoria."""
    alimentacao, transporte = avaliar(
        despesa(id="a", categoria="alimentacao", valor=Decimal("60.00")),
        despesa(id="t", categoria="transporte_urbano", valor=Decimal("80.00")),
    )["itens"]

    # cada uma esgota exatamente o seu limite, sem tirar do da outra
    assert _resumo(alimentacao) == (Decimal("60.00"), "aprovado", None)
    assert _resumo(transporte) == (Decimal("80.00"), "aprovado", None)


def test_rn009_datas_diferentes_nao_dividem_limite(avaliar, despesa):
    """RN-009: o limite é por data; outro dia tem saldo cheio."""
    dia3, dia4 = avaliar(
        despesa(id="a", data="2026-07-03", valor=Decimal("60.00")),
        despesa(id="b", data="2026-07-04", valor=Decimal("60.00")),
    )["itens"]

    assert _resumo(dia3) == (Decimal("60.00"), "aprovado", None)
    assert _resumo(dia4) == (Decimal("60.00"), "aprovado", None)


def test_rn009_limite_por_data_nao_depende_de_adjacencia(avaliar, despesa):
    """RN-009 / AMB-003: o saldo do dia é consumido pela ordem da entrada,
    mesmo com despesas de outras datas no meio."""
    a, b, c = avaliar(
        despesa(id="a", data="2026-07-03", valor=Decimal("50.00")),
        despesa(id="b", data="2026-07-04", valor=Decimal("50.00")),
        despesa(id="c", data="2026-07-03", valor=Decimal("50.00"), fornecedor="X"),
    )["itens"]

    assert _resumo(a) == (Decimal("50.00"), "aprovado", None)
    assert _resumo(b) == (Decimal("50.00"), "aprovado", None)
    # saldo de 03/07: 60,00 − 50,00 = 10,00
    assert _resumo(c) == (Decimal("10.00"), "parcial", "limite_diario_excedido")


def test_rn009_item_que_chega_ao_limite_tem_limite_e_em_viagem(avaliar, despesa):
    """RN-009 / seção 4: item avaliado no limite tem `limite_diario` preenchido e
    `em_viagem` falso fora de viagem."""
    (item,) = avaliar(despesa(valor=Decimal("45.00")))["itens"]

    assert item["limite_diario"] == Decimal("60.00")
    assert item["em_viagem"] is False


# --- limite_diario com a tabela aplicada (RN-009, DT-013) ---


def _tabela(centro_custo=None, **sobrescritas):
    documento = construir_politica(**sobrescritas)
    politica = ler_politica(simplejson.dumps(documento, use_decimal=True).encode())
    return tabela_aplicada(politica, centro_custo)


CINQUENTA = Decimal("50")  # acrescimo_em_viagem_percentual da v4


@pytest.mark.parametrize(
    ("categoria", "esperado"),
    [
        ("alimentacao", Decimal("90.00")),  # 60,00 × 1,5 = 90,00
        ("transporte_urbano", Decimal("120.00")),  # 80,00 × 1,5 = 120,00
        ("hospedagem", Decimal("250.00")),  # não amplia (AMB-006)
    ],
)
def test_rn009_limite_em_viagem_da_tabela_padrao(categoria, esperado):
    """RN-009 / AMB-006 / AMB-022: `padrao` da v4 em viagem → 90,00, 120,00 e
    250,00 (hospedagem não amplia)."""
    assert limite_diario(_tabela(), categoria, True, CINQUENTA) == esperado


@pytest.mark.parametrize(
    ("categoria", "esperado"),
    [
        ("alimentacao", Decimal("60.00")),
        ("transporte_urbano", Decimal("80.00")),
        ("hospedagem", Decimal("250.00")),
    ],
)
def test_rn009_limite_fora_de_viagem_e_o_da_tabela(categoria, esperado):
    """RN-009: fora de viagem, o limite é o `limite` da tabela aplicada."""
    assert limite_diario(_tabela(), categoria, False, CINQUENTA) == esperado


@pytest.mark.parametrize(
    ("categoria", "esperado"),
    [
        ("alimentacao", Decimal("135.00")),  # 90,00 × 1,5 = 135,00
        ("representacao", Decimal("300.00")),  # não amplia (AMB-022)
    ],
)
def test_rn009_limite_em_viagem_do_cc_comercial(categoria, esperado):
    """RN-009 / AMB-022: `CC-COMERCIAL` em viagem → alimentação 135,00;
    representação 300,00 (não amplia)."""
    tabela = _tabela("CC-COMERCIAL")
    assert limite_diario(tabela, categoria, True, CINQUENTA) == esperado


def test_rn009_limite_em_viagem_truncado_ao_centavo():
    """RN-009 / AMB-022 / DT-013: alimentação 33,33 com 50% → 49,99."""
    padrao = construir_politica()["padrao"]
    padrao["alimentacao"]["limite"] = Decimal("33.33")
    tabela = _tabela(padrao=padrao)

    # 33,33 × 1,5 = 49,995 → truncado (nunca arredondado para cima) = 49,99
    assert limite_diario(tabela, "alimentacao", True, CINQUENTA) == Decimal("49.99")


def test_rn009_percentual_zero_mantem_o_limite_normal():
    """RN-009: acréscimo de 0% → limite em viagem igual ao normal."""
    tabela = _tabela()
    # 60,00 × (1 + 0/100) = 60,00
    assert limite_diario(tabela, "alimentacao", True, Decimal("0")) == Decimal(
        "60.00"
    )


def test_rn009_percentual_com_mais_de_28_casas_e_exato():
    """RN-009 / DT-012 / DT-013: percentual 50 − 10⁻³⁰ (30 casas) não é
    arredondado antes do truncamento."""
    percentual = Decimal("49." + "9" * 30)  # 50 − 10⁻³⁰
    # 60,00 × (100 + 50 − 10⁻³⁰) / 100 = 90 − 0,6 × 10⁻³⁰ → truncado 89,99.
    # Com a precisão padrão (28 dígitos), 149,99…9 viraria 150 e daria 90,00.
    assert limite_diario(_tabela(), "alimentacao", True, percentual) == Decimal(
        "89.99"
    )


def test_rn009_motor_usa_o_percentual_do_arquivo_de_politica(avaliar, despesa):
    """RN-009 / AMB-022: o acréscimo em viagem vem do arquivo de política, não é
    50 fixo: com 20%, alimentação em viagem no `padrao` → 60,00 × 1,2 = 72,00."""
    politica = construir_politica(acrescimo_em_viagem_percentual=Decimal("20"))

    _, alimentacao = avaliar(
        despesa(id="h", categoria="hospedagem", fornecedor="Hotel",
                data="2026-07-14", valor=Decimal("200.00"), tem_nota_fiscal=True),
        despesa(id="a", data="2026-07-15", valor=Decimal("80.00")),
        politica=politica,
    )["itens"]

    # 15/07 = D+1 em viagem; 60,00 × (1 + 20/100) = 72,00; min(80,00; 72,00) = 72,00
    assert (alimentacao["em_viagem"], alimentacao["limite_diario"]) == (
        True, Decimal("72.00"),
    )
    assert (alimentacao["valor_reembolsado"], alimentacao["status"]) == (
        Decimal("72.00"), "parcial",
    )
