"""Categorias da política: RN-006 / AMB-011 / AMB-012 (etapa 5 da seção 8).

Período padrão do `conftest`: 2026-07-01 a 2026-07-31.
"""

from decimal import Decimal

import pytest


def _recusado_fora_da_politica(item):
    # RN-006: recusado, `categoria_fora_da_politica`, sem reembolso; recusado
    # antes do limite diário (etapa 5 < etapa 9) → `em_viagem` e `limite_diario`
    # nulos (seção 4)
    assert (item["status"], item["motivo"]) == (
        "recusado", "categoria_fora_da_politica",
    )
    assert item["valor_reembolsado"] == 0
    assert (item["em_viagem"], item["limite_diario"]) == (None, None)


@pytest.mark.parametrize(
    "categoria",
    [
        pytest.param("ALIMENTACAO", id="maiusculas"),
        pytest.param(" Alimentacao ", id="espacos-nas-pontas"),
        pytest.param("alimentacao\t", id="tabulacao-no-fim"),
        pytest.param("alimentação", id="acento"),
    ],
)
def test_rn006_grafias_de_alimentacao_sao_reconhecidas(avaliar, despesa, categoria):
    """RN-006 / AMB-011: grafias de alimentação → `alimentacao` na saída e
    limite de alimentação: 72,50 → min(72,50; 60,00) = 60,00, `parcial`."""
    (item,) = avaliar(despesa(categoria=categoria, valor=Decimal("72.50")))["itens"]

    assert item["categoria"] == "alimentacao"
    assert item["limite_diario"] == Decimal("60.00")
    assert (item["status"], item["motivo"]) == ("parcial", "limite_diario_excedido")
    assert item["valor_reembolsado"] == Decimal("60.00")


@pytest.mark.parametrize(
    "categoria",
    [
        pytest.param("Transporte Urbano", id="espaco"),
        pytest.param("transporte-urbano", id="hifen"),
    ],
)
def test_rn006_grafias_de_transporte_urbano_sao_reconhecidas(
    avaliar, despesa, categoria
):
    """RN-006 / AMB-011: separador diferente → `transporte_urbano` na saída e
    limite de transporte: 90,00 → min(90,00; 80,00) = 80,00, `parcial`."""
    (item,) = avaliar(despesa(categoria=categoria, valor=Decimal("90.00")))["itens"]

    assert item["categoria"] == "transporte_urbano"
    assert item["limite_diario"] == Decimal("80.00")
    assert (item["status"], item["motivo"]) == ("parcial", "limite_diario_excedido")
    assert item["valor_reembolsado"] == Decimal("80.00")


def test_rn006_hospedagem_e_reconhecida(avaliar, despesa):
    """RN-006: `HOSPEDAGEM` → `hospedagem`, limite 250,00; 200,00 → `aprovado`."""
    (item,) = avaliar(despesa(categoria="HOSPEDAGEM", valor=Decimal("200.00")))[
        "itens"
    ]

    assert item["categoria"] == "hospedagem"
    assert item["limite_diario"] == Decimal("250.00")
    assert (item["status"], item["valor_reembolsado"]) == (
        "aprovado", Decimal("200.00"),
    )


def test_rn006_categoria_desconhecida_e_recusada_e_aparece(avaliar, despesa):
    """RN-006 / AMB-012: `coworking` → `categoria_fora_da_politica`; o item
    aparece na saída (não é omitido), com `categoria` como veio."""
    outra = despesa(id="b", valor=Decimal("30.00"), fornecedor="Cantina")
    saida = avaliar(
        despesa(id="a", categoria="coworking", valor=Decimal("45.00")), outra
    )

    # RN-001: 2 despesas → 2 itens, mesma ordem
    item, item_b = saida["itens"]
    assert (item["id"], item_b["id"]) == ("a", "b")
    _recusado_fora_da_politica(item)
    assert item["categoria"] == "coworking"
    assert item["valor_considerado"] == Decimal("45.00")
    # a outra despesa segue: 30,00 ≤ 60,00 → aprovado
    assert (item_b["status"], item_b["valor_reembolsado"]) == (
        "aprovado", Decimal("30.00"),
    )
    # seção 4: solicitado = 45,00 + 30,00 = 75,00 (considerado > 0, não
    # `entrada_invalida`); reembolsado 0 + 30,00 = 30,00; glosado 45,00
    assert saida["totais"] == {
        "valor_solicitado": Decimal("75.00"),
        "valor_reembolsado": Decimal("30.00"),
        "valor_glosado": Decimal("45.00"),
    }


def test_rn006_categoria_desconhecida_sai_como_veio(avaliar, despesa):
    """RN-006 / seção 4: categoria não reconhecida sai como veio, sem
    normalização (`" Coworking "` continua `" Coworking "`)."""
    (item,) = avaliar(despesa(categoria=" Coworking "))["itens"]

    _recusado_fora_da_politica(item)
    assert item["categoria"] == " Coworking "


def test_rn006_periodo_vem_antes_da_categoria(avaliar, despesa):
    """RN-006 / RN-005: categoria desconhecida fora do período →
    `fora_do_periodo` (etapa 4 vem antes da etapa 5)."""
    (item,) = avaliar(despesa(data="2026-04-15", categoria="coworking"))["itens"]

    assert (item["status"], item["motivo"]) == ("recusado", "fora_do_periodo")


def test_rn006_valor_invalido_vem_antes_da_categoria(avaliar, despesa):
    """RN-006 / RN-004: categoria desconhecida com valor ≤ 0 → `valor_invalido`
    (etapa 3 vem antes da etapa 5)."""
    (item,) = avaliar(despesa(categoria="coworking", valor=Decimal("0")))["itens"]

    assert (item["status"], item["motivo"]) == ("recusado", "valor_invalido")


@pytest.mark.parametrize(
    "categoria",
    [
        # seção 10: espaço de largura zero é separador → `ali_mentacao`
        pytest.param("ali\u200bmentacao", id="largura-zero"),
        # seção 10: largura total não é desfeita pela normalização
        pytest.param("ＡＬＩＭＥＮＴＡＣＡＯ", id="largura-total"),
    ],
)
def test_rn006_riscos_aceitos_saem_fora_da_politica(avaliar, despesa, categoria):
    """RN-006 / seção 10 (riscos aceitos): `"ali\\u200bmentacao"` e categoria em
    largura total → `categoria_fora_da_politica`, `categoria` como veio."""
    (item,) = avaliar(despesa(categoria=categoria))["itens"]

    _recusado_fora_da_politica(item)
    assert item["categoria"] == categoria
