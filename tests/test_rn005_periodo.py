"""Período de competência: RN-005 / AMB-009 (etapa 4 da seção 8).

Período padrão do `conftest`: 2026-07-01 a 2026-07-31.
"""

from decimal import Decimal

import pytest


def _recusado_fora_do_periodo(item):
    # RN-005: recusado, `fora_do_periodo`, sem reembolso; recusado antes do limite
    # diário (etapa 4 < etapa 9) → `em_viagem` e `limite_diario` nulos (seção 4)
    assert (item["status"], item["motivo"]) == ("recusado", "fora_do_periodo")
    assert item["valor_reembolsado"] == 0
    assert (item["em_viagem"], item["limite_diario"]) == (None, None)


@pytest.mark.parametrize(
    "data",
    [
        # AMB-009: d-008, data da despesa em abril num relatório de julho
        pytest.param("2026-04-15", id="abril"),
        # inicio − 1 dia
        pytest.param("2026-06-30", id="vespera-do-inicio"),
        # fim + 1 dia
        pytest.param("2026-08-01", id="dia-seguinte-ao-fim"),
    ],
)
def test_rn005_data_fora_do_periodo_e_recusada(avaliar, despesa, data):
    """RN-005 / AMB-009: data fora de `[inicio, fim]` → `fora_do_periodo`."""
    saida = avaliar(despesa(data=data, valor=Decimal("41.00")))

    (item,) = saida["itens"]
    _recusado_fora_do_periodo(item)
    assert item["data"] == data
    assert item["valor_considerado"] == Decimal("41.00")
    # seção 4: solicitado soma considerado > 0 não `entrada_invalida` → 41,00;
    # reembolsado 0; glosado 41,00 − 0 = 41,00
    assert saida["totais"] == {
        "valor_solicitado": Decimal("41.00"),
        "valor_reembolsado": 0,
        "valor_glosado": Decimal("41.00"),
    }


@pytest.mark.parametrize(
    "data",
    [
        pytest.param("2026-07-01", id="inicio"),
        pytest.param("2026-07-31", id="fim"),
    ],
)
def test_rn005_extremos_do_periodo_seguem(avaliar, despesa, data):
    """RN-005 / AMB-009: `inicio` e `fim` inclusive → seguem para as próximas
    regras; alimentação 41,00 ≤ limite 60,00 → `aprovado` com 41,00."""
    (item,) = avaliar(despesa(data=data, valor=Decimal("41.00")))["itens"]

    assert (item["status"], item["motivo"]) == ("aprovado", None)
    assert item["valor_reembolsado"] == Decimal("41.00")
    assert (item["em_viagem"], item["limite_diario"]) == (False, Decimal("60.00"))


def test_rn005_valor_invalido_vem_antes_do_periodo(avaliar, despesa):
    """RN-005 / RN-004: valor ≤ 0 fora do período → `valor_invalido`
    (etapa 3 vem antes da etapa 4)."""
    (item,) = avaliar(despesa(data="2026-04-15", valor=Decimal("-45.00")))["itens"]

    assert (item["status"], item["motivo"]) == ("recusado", "valor_invalido")


@pytest.mark.parametrize(
    ("categoria", "categoria_saida"),
    [
        # seção 4: reconhecida → normalizada (seção 5)
        pytest.param("ALIMENTACAO", "alimentacao", id="reconhecida"),
        # seção 4: não reconhecida → como veio; etapa 4 vem antes da 5
        pytest.param("Coworking ", "Coworking ", id="nao-reconhecida"),
    ],
)
def test_rn005_categoria_na_saida_do_item_fora_do_periodo(
    avaliar, despesa, categoria, categoria_saida
):
    """RN-005 / seção 4: `categoria` normalizada se reconhecida, senão como veio;
    categoria desconhecida fora do período → `fora_do_periodo` (etapa 4 < 5)."""
    (item,) = avaliar(despesa(data="2026-04-15", categoria=categoria))["itens"]

    _recusado_fora_do_periodo(item)
    assert item["categoria"] == categoria_saida


def test_rn005_periodo_vem_do_cabecalho(avaliar, despesa):
    """RN-005: a comparação usa `periodo.inicio`/`periodo.fim` da entrada, não
    julho fixo: com período de abril, 15/04 segue e 03/07 é recusada."""
    abril = {"inicio": "2026-04-01", "fim": "2026-04-30"}
    a = despesa(id="a", data="2026-04-15", valor=Decimal("41.00"))
    j = despesa(id="j", data="2026-07-03", valor=Decimal("41.00"))

    item_a, item_j = avaliar(a, j, periodo=abril)["itens"]

    assert (item_a["status"], item_a["motivo"]) == ("aprovado", None)
    _recusado_fora_do_periodo(item_j)
