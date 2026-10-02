"""Um resultado por despesa: RN-001, seção 4 da spec (totais)."""

from datetime import date, timedelta
from decimal import Decimal


def test_rn001_quatorze_despesas_geram_quatorze_itens_na_mesma_ordem(avaliar, despesa):
    """RN-001: entrada com 14 despesas gera 14 itens, na mesma ordem de ids."""
    # ids fora de ordem alfabética, para a ordem da saída não coincidir com um sort
    ids = [f"d-{n:03d}" for n in (7, 3, 14, 1, 9, 2, 12, 5, 10, 4, 13, 6, 11, 8)]
    despesas = [
        despesa(id=id_, data=(date(2026, 7, 1) + timedelta(days=i)).isoformat())
        for i, id_ in enumerate(ids)
    ]

    saida = avaliar(*despesas)

    assert [item["id"] for item in saida["itens"]] == ids


def test_rn001_item_copia_id_data_e_valor_informado(avaliar, despesa):
    """RN-001 / seção 4: `id` e `data` como vieram; `valor_informado` sem arredondar."""
    saida = avaliar(despesa(id="d-x", data="2026-07-18", valor=Decimal("33.333")))

    (item,) = saida["itens"]
    assert item["id"] == "d-x"
    assert item["data"] == "2026-07-18"
    assert item["valor_informado"] == Decimal("33.333")


def test_rn001_valor_glosado_e_solicitado_menos_reembolsado(avaliar, despesa):
    """RN-001 / seção 4: `valor_glosado = valor_solicitado − valor_reembolsado`."""
    saida = avaliar(
        despesa(id="a", valor=Decimal("72.50")),
        despesa(id="b", valor=Decimal("38.00")),
        despesa(id="c", data="2026-07-04", categoria="transporte_urbano",
                valor=Decimal("25.00")),
    )

    totais = saida["totais"]
    # solicitado: 72,50 + 38,00 + 25,00 = 135,50
    assert totais["valor_solicitado"] == Decimal("135.50")
    # reembolsado: 60,00 (limite de alimentação em 03/07) + 0 + 25,00 = 85,00
    assert totais["valor_reembolsado"] == Decimal("85.00")
    # glosado: 135,50 − 85,00 = 50,50
    assert totais["valor_glosado"] == Decimal("50.50")
    assert totais["valor_glosado"] == (
        totais["valor_solicitado"] - totais["valor_reembolsado"]
    )


def test_rn001_valor_solicitado_soma_valor_considerado(avaliar, despesa):
    """RN-001 / RN-003 / seção 4: o solicitado soma `valor_considerado`."""
    saida = avaliar(
        despesa(id="a", valor=Decimal("10.005")),
        despesa(id="b", data="2026-07-04", valor=Decimal("33.333")),
    )

    # 10,01 + 33,33 = 43,34 (não 10,005 + 33,333 = 43,338)
    assert saida["totais"]["valor_solicitado"] == Decimal("43.34")
    assert saida["totais"]["valor_reembolsado"] == Decimal("43.34")
    assert saida["totais"]["valor_glosado"] == Decimal("0")


def test_rn001_colaborador_periodo_e_avisos_do_topo(avaliar, despesa):
    """RN-001 / seção 4: colaborador e período copiados; `avisos` vazio."""
    saida = avaliar(
        despesa(),
        periodo={"competencia": "2026-07", "inicio": "2026-07-01",
                 "fim": "2026-07-31"},
    )

    assert saida["colaborador"] == {"id": "c-1", "nome": "Ana"}
    assert saida["periodo"] == {
        "competencia": "2026-07", "inicio": "2026-07-01", "fim": "2026-07-31",
    }
    assert saida["avisos"] == []
    assert saida["itens"][0]["avisos"] == []
