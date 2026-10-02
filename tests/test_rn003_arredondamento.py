"""Arredondamento ao centavo: RN-003, AMB-014."""

from decimal import Decimal

import pytest


@pytest.mark.parametrize(
    ("valor", "considerado"),
    [
        # RN-003 Aceite: 33.333 → 33,33 (terceira casa 3 < 5)
        (Decimal("33.333"), Decimal("33.33")),
        # metade afastando do zero: 10,005 → 10,01
        (Decimal("10.005"), Decimal("10.01")),
        # abaixo da metade: 10,004 → 10,00
        (Decimal("10.004"), Decimal("10.00")),
        # metade com mais casas: 0,005 → 0,01 (exemplo da regra), 12,3450 → 12,35
        (Decimal("0.005"), Decimal("0.01")),
        (Decimal("12.3450"), Decimal("12.35")),
    ],
)
def test_rn003_valor_considerado_arredondado_ao_centavo(
    avaliar, despesa, valor, considerado
):
    """RN-003 / AMB-014: `valor` arredondado a 2 casas, metade afastando do zero."""
    (item,) = avaliar(despesa(valor=valor))["itens"]

    assert item["valor_considerado"] == considerado
    # exatamente 2 casas decimais (seção 4: exatos ao centavo)
    assert item["valor_considerado"].as_tuple().exponent == -2
    # valor_informado é o número recebido, sem arredondamento (seção 4)
    assert item["valor_informado"] == valor


def test_rn003_regras_usam_o_valor_arredondado(avaliar, despesa):
    """RN-003: o limite diário usa `valor_considerado`, não o número recebido."""
    # 60,004 → 60,00, exatamente o limite de alimentação: aprovado com 60,00
    (item,) = avaliar(despesa(valor=Decimal("60.004")))["itens"]
    assert item["valor_considerado"] == Decimal("60.00")
    assert item["valor_reembolsado"] == Decimal("60.00")
    assert item["status"] == "aprovado"

    # 60,005 → 60,01, um centavo acima: parcial com 60,00
    (item,) = avaliar(despesa(valor=Decimal("60.005")))["itens"]
    assert item["valor_considerado"] == Decimal("60.01")
    assert item["valor_reembolsado"] == Decimal("60.00")
    assert item["status"] == "parcial"
