"""Hospedagem: um lançamento é uma diária — RN-012, AMB-005."""

from decimal import Decimal


def test_rn012_hospedagem_de_480_com_duas_diarias_na_descricao_e_uma_diaria(
    avaliar, despesa
):
    """RN-012 / AMB-005: 480,00 com nota, "2 diarias" → uma diária: parcial, 250,00."""
    (item,) = avaliar(
        despesa(categoria="hospedagem", data="2026-07-14", valor=Decimal("480.00"),
                descricao="2 diarias", tem_nota_fiscal=True),
    )["itens"]

    # min(480,00; 250,00) = 250,00 → parcial
    assert item["valor_reembolsado"] == Decimal("250.00")
    assert item["status"] == "parcial"
    assert item["motivo"] == "limite_diario_excedido"
    assert item["limite_diario"] == Decimal("250.00")


def test_rn012_campo_extra_nao_conta_diarias(avaliar, despesa):
    """RN-012 / RN-002: `"noites": 2` é ignorado; continua uma diária de 250,00."""
    (item,) = avaliar(
        despesa(categoria="hospedagem", valor=Decimal("480.00"), noites=2),
    )["itens"]

    assert item["valor_reembolsado"] == Decimal("250.00")
    assert item["status"] == "parcial"


def test_rn012_duas_hospedagens_na_mesma_data_dividem_o_limite(avaliar, despesa):
    """RN-012 / RN-009: várias hospedagens na mesma data dividem 250,00."""
    primeira, segunda = avaliar(
        despesa(id="h1", categoria="hospedagem", valor=Decimal("200.00"),
                fornecedor="Hotel A"),
        despesa(id="h2", categoria="hospedagem", valor=Decimal("100.00"),
                fornecedor="Hotel B"),
    )["itens"]

    # 200,00 ≤ 250,00 → aprovado; saldo 50,00
    assert primeira["valor_reembolsado"] == Decimal("200.00")
    assert primeira["status"] == "aprovado"
    # min(100,00; 50,00) = 50,00 → parcial
    assert segunda["valor_reembolsado"] == Decimal("50.00")
    assert segunda["status"] == "parcial"
    assert segunda["motivo"] == "limite_diario_excedido"


def test_rn012_hospedagem_de_480_poe_em_viagem_so_d_e_d_mais_1(avaliar, despesa):
    """RN-012 / RN-010 / AMB-005 (aceite): 480,00 com nota em 14/07, "2 diarias" →
    uma diária: 14/07 e 15/07 em viagem, 16/07 não."""
    hospedagem, a15, a16 = avaliar(
        despesa(id="h", categoria="hospedagem", data="2026-07-14",
                valor=Decimal("480.00"), descricao="2 diarias", tem_nota_fiscal=True),
        despesa(id="a15", data="2026-07-15", valor=Decimal("10.00")),
        despesa(id="a16", data="2026-07-16", valor=Decimal("10.00")),
    )["itens"]

    # uma diária em D = 14/07 → {14/07, 15/07}; a descrição não estende a 16/07
    assert hospedagem["em_viagem"] is True
    assert a15["em_viagem"] is True
    assert a16["em_viagem"] is False
