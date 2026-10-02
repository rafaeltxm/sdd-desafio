"""Status e justificativa: RN-011."""

from decimal import Decimal


def test_rn011_status_compativel_com_os_valores_em_todos_os_itens(avaliar, despesa):
    """RN-011: aprovado ⇔ reembolsado = considerado; parcial ⇔ 0 < r < c;
    recusado ⇔ r = 0; motivo nulo só em aprovado; toda justificativa não vazia."""
    saida = avaliar(
        # 03/07 alimentação: 45,00 aprovado; 30,00 parcial com 15,00; 10,00 recusado
        despesa(id="a", valor=Decimal("45.00")),
        despesa(id="b", valor=Decimal("30.00"), fornecedor="B"),
        despesa(id="c", valor=Decimal("10.00"), fornecedor="C"),
        # 04/07 transporte: exatamente 80,00 → aprovado
        despesa(id="d", data="2026-07-04", categoria="transporte_urbano",
                valor=Decimal("80.00")),
    )

    status = [item["status"] for item in saida["itens"]]
    assert status == ["aprovado", "parcial", "recusado", "aprovado"]

    for item in saida["itens"]:
        considerado = item["valor_considerado"]
        reembolsado = item["valor_reembolsado"]
        if item["status"] == "aprovado":
            assert reembolsado == considerado
            assert item["motivo"] is None
        elif item["status"] == "parcial":
            assert 0 < reembolsado < considerado
            assert item["motivo"] is not None
        else:
            assert item["status"] == "recusado"
            assert reembolsado == 0
            assert item["motivo"] is not None
        assert item["justificativa"].strip()


def test_rn011_valores_dos_status(avaliar, despesa):
    """RN-011 / RN-009: o reembolso de cada status confere com o saldo do dia."""
    a, b, c = avaliar(
        despesa(id="a", valor=Decimal("45.00")),
        despesa(id="b", valor=Decimal("30.00"), fornecedor="B"),
        despesa(id="c", valor=Decimal("10.00"), fornecedor="C"),
    )["itens"]

    # 45,00 ≤ 60,00 → 45,00; saldo 15,00
    assert (a["valor_reembolsado"], a["motivo"]) == (Decimal("45.00"), None)
    # min(30,00; 15,00) = 15,00; saldo 0
    assert (b["valor_reembolsado"], b["motivo"]) == (
        Decimal("15.00"), "limite_diario_excedido",
    )
    # saldo 0 → 0
    assert (c["valor_reembolsado"], c["motivo"]) == (
        Decimal("0"), "limite_diario_excedido",
    )
