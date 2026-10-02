"""Valor positivo: RN-004 / AMB-013 (etapa 3 da seção 8)."""

from decimal import Decimal

import pytest


def _recusado_valor_invalido(item):
    # RN-004: recusado, `valor_invalido`, sem reembolso; recusado antes do limite
    # diário (etapa 3 < etapa 9) → `em_viagem` e `limite_diario` nulos (seção 4)
    assert (item["status"], item["motivo"]) == ("recusado", "valor_invalido")
    assert item["valor_reembolsado"] == 0
    assert (item["em_viagem"], item["limite_diario"]) == (None, None)


def test_rn004_estorno_recusado_com_valor_invalido(avaliar, despesa):
    """RN-004 / AMB-013: -45,00 → `recusado`, `valor_invalido`, reembolsado 0."""
    saida = avaliar(despesa(valor=Decimal("-45.00")))

    (item,) = saida["itens"]
    _recusado_valor_invalido(item)
    # RN-003: -45,00 já tem 2 casas → considerado -45,00
    assert item["valor_informado"] == Decimal("-45.00")
    assert item["valor_considerado"] == Decimal("-45.00")
    # seção 4: solicitado só soma considerado > 0 → 0; reembolsado 0; glosado 0
    assert saida["totais"] == {
        "valor_solicitado": 0, "valor_reembolsado": 0, "valor_glosado": 0,
    }


def test_rn004_estorno_nao_altera_as_demais_despesas_do_dia(avaliar, despesa):
    """RN-004 / AMB-013: as demais despesas do mesmo dia têm o mesmo resultado
    que teriam sem o estorno; ele não abate, não soma e não consome limite."""
    a = despesa(id="a", valor=Decimal("50.00"), fornecedor="A")
    estorno = despesa(id="e", valor=Decimal("-45.00"), fornecedor="A")
    b = despesa(id="b", valor=Decimal("30.00"), fornecedor="B")

    com_estorno = avaliar(a, estorno, b)
    sem_estorno = avaliar(a, b)

    item_a, item_e, item_b = com_estorno["itens"]
    _recusado_valor_invalido(item_e)
    # alimentação, 03/07, limite 60,00: 50,00 aprovado; saldo 10,00;
    # min(30,00; 10,00) = 10,00 → parcial (o -45,00 não devolve saldo)
    assert (item_a["status"], item_a["valor_reembolsado"]) == (
        "aprovado", Decimal("50.00"),
    )
    assert (item_b["status"], item_b["valor_reembolsado"]) == (
        "parcial", Decimal("10.00"),
    )
    assert [item_a, item_b] == sem_estorno["itens"]
    # solicitado 50,00 + 30,00 = 80,00; reembolsado 60,00; glosado 20,00
    assert com_estorno["totais"] == {
        "valor_solicitado": Decimal("80.00"),
        "valor_reembolsado": Decimal("60.00"),
        "valor_glosado": Decimal("20.00"),
    }
    assert com_estorno["totais"] == sem_estorno["totais"]


@pytest.mark.parametrize(
    ("valor", "considerado"),
    [
        # RN-004: 0 → considerado 0,00
        pytest.param(Decimal("0"), Decimal("0.00"), id="zero"),
        # RN-003: 0,004 arredonda para 0,00
        pytest.param(Decimal("0.004"), Decimal("0.00"), id="0.004"),
        # RN-003: metade afasta do zero: -0,005 → -0,01
        pytest.param(Decimal("-0.005"), Decimal("-0.01"), id="-0.005"),
        # seção 7 "Valor minúsculo": 10^-999999 arredonda para 0,00
        pytest.param(Decimal("1E-999999"), Decimal("0.00"), id="1e-999999"),
    ],
)
def test_rn004_valor_considerado_nao_positivo_e_valor_invalido(
    avaliar, despesa, valor, considerado
):
    """RN-004 / RN-003: o teste é sobre o `valor_considerado` (após arredondar)."""
    saida = avaliar(despesa(valor=valor))

    (item,) = saida["itens"]
    _recusado_valor_invalido(item)
    assert item["valor_informado"] == valor
    assert item["valor_considerado"] == considerado
    # considerado ≤ 0 → fora de `valor_solicitado` (seção 4)
    assert saida["totais"]["valor_solicitado"] == 0


@pytest.mark.parametrize(
    ("categoria", "categoria_saida"),
    [
        # seção 4: reconhecida → normalizada (seção 5)
        pytest.param("ALIMENTACAO", "alimentacao", id="reconhecida"),
        # seção 4: não reconhecida → como veio
        pytest.param("Coworking ", "Coworking ", id="nao-reconhecida"),
    ],
)
def test_rn004_categoria_na_saida_do_item_valor_invalido(
    avaliar, despesa, categoria, categoria_saida
):
    """RN-004 / seção 4: `categoria` normalizada se reconhecida, senão como veio,
    qualquer que seja o motivo; -45,00 vem antes da categoria (etapa 3 < 5)."""
    (item,) = avaliar(despesa(categoria=categoria, valor=Decimal("-45.00")))["itens"]

    _recusado_valor_invalido(item)
    assert item["categoria"] == categoria_saida


def test_rn004_um_centavo_e_positivo(avaliar, despesa):
    """RN-004 / RN-003: 0,005 → considerado 0,01 > 0 → segue; 0,01 ≤ 60,00 →
    `aprovado` com 0,01 (fronteira logo acima de zero)."""
    (item,) = avaliar(despesa(valor=Decimal("0.005")))["itens"]

    assert item["valor_considerado"] == Decimal("0.01")
    assert (item["status"], item["valor_reembolsado"]) == ("aprovado", Decimal("0.01"))
