"""Limite diário por categoria: RN-009, AMB-001, AMB-002, AMB-003, AMB-006, AMB-017.

Até a T-018 não há viagem: os casos usam datas sem hospedagem com nota, ou não
conferem `em_viagem`/limite de alimentação e transporte nessas datas.
"""

from decimal import Decimal

import pytest


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
