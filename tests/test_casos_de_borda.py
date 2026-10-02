"""Casos de borda da seção 7 da spec: um caso por linha, `id` = coluna "Caso"."""

from decimal import Decimal

import pytest

from conftest import construir_despesa as despesa


def _caso_duas_alimentacoes_acima_do_limite(saida):
    # 72,50 + 38,00 > 60,00 → 60,00 parcial e 0 recusado
    a, b = saida["itens"]
    assert (a["valor_reembolsado"], a["status"]) == (Decimal("60.00"), "parcial")
    assert (b["valor_reembolsado"], b["status"], b["motivo"]) == (
        Decimal("0"), "recusado", "limite_diario_excedido",
    )


def _caso_valor_no_limite_diario(saida):
    # 60,00 = limite → aprovado com 60,00
    (item,) = saida["itens"]
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("60.00"), "aprovado")


def _caso_um_centavo_acima_do_limite_diario(saida):
    # min(60,01; 60,00) = 60,00 → parcial
    (item,) = saida["itens"]
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("60.00"), "parcial")


def _caso_duas_hospedagens_na_mesma_data(saida):
    # 200,00 aprovado; min(100,00; 250,00 − 200,00) = 50,00 parcial
    a, b = saida["itens"]
    assert (a["valor_reembolsado"], a["status"]) == (Decimal("200.00"), "aprovado")
    assert (b["valor_reembolsado"], b["status"]) == (Decimal("50.00"), "parcial")


def _caso_tres_casas_decimais(saida):
    (item,) = saida["itens"]
    assert item["valor_informado"] == Decimal("33.333")
    assert item["valor_considerado"] == Decimal("33.33")


def _caso_arredondamento_da_metade(saida):
    (item,) = saida["itens"]
    assert item["valor_considerado"] == Decimal("10.01")


def _caso_lista_vazia(saida):
    assert saida["itens"] == []
    assert saida["totais"] == {
        "valor_solicitado": 0, "valor_reembolsado": 0, "valor_glosado": 0,
    }


def _caso_despesa_em_sabado(saida):
    # 18/07/2026 é sábado; avaliada normalmente: 47,20 ≤ 60,00 → aprovado
    (item,) = saida["itens"]
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("47.20"), "aprovado")


CASOS = [
    pytest.param(
        [despesa(id="a", valor=Decimal("72.50")),
         despesa(id="b", valor=Decimal("38.00"), fornecedor="Cantina")],
        _caso_duas_alimentacoes_acima_do_limite,
        id="Duas alimentações no mesmo dia somando mais que o limite",
    ),
    pytest.param(
        [despesa(valor=Decimal("60.00"))],
        _caso_valor_no_limite_diario,
        id="Valor exatamente no limite diário",
    ),
    pytest.param(
        [despesa(valor=Decimal("60.01"))],
        _caso_um_centavo_acima_do_limite_diario,
        id="Um centavo acima do limite diário",
    ),
    pytest.param(
        [despesa(id="h1", categoria="hospedagem", valor=Decimal("200.00"),
                 fornecedor="Hotel A"),
         despesa(id="h2", categoria="hospedagem", valor=Decimal("100.00"),
                 fornecedor="Hotel B")],
        _caso_duas_hospedagens_na_mesma_data,
        id="Duas hospedagens na mesma data",
    ),
    pytest.param(
        [despesa(valor=Decimal("33.333"))],
        _caso_tres_casas_decimais,
        id="Três casas decimais",
    ),
    pytest.param(
        [despesa(valor=Decimal("10.005"))],
        _caso_arredondamento_da_metade,
        id="Arredondamento da metade",
    ),
    pytest.param([], _caso_lista_vazia, id="Lista de despesas vazia"),
    pytest.param(
        [despesa(data="2026-07-18", valor=Decimal("47.20"))],
        _caso_despesa_em_sabado,
        id="Despesa em sábado",
    ),
]


@pytest.mark.parametrize(("despesas", "verificar"), CASOS)
def test_caso_de_borda(avaliar, despesas, verificar):
    """Seção 7 da spec: comportamento esperado de cada caso."""
    verificar(avaliar(*despesas))
