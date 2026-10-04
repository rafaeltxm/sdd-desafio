"""Busca da cotação: RN-015, AMB-024, AMB-025, DT-014.

Salvo indicação, o câmbio é o `cambio.json` do envelope (`construir_cambio`),
com cotações de USD e EUR só em dias úteis, de 13/07 (segunda) a 28/07.
"""

from datetime import date
from decimal import Decimal

import pytest
import simplejson

from conftest import construir_cambio
from reembolso.cambio import cotacao, ler_cambio
from reembolso.modelo import Cotacao


def _cambio(**sobrescritas):
    documento = construir_cambio(**sobrescritas)
    return ler_cambio(simplejson.dumps(documento, use_decimal=True).encode())


def test_rn015_cotacao_da_propria_data():
    """RN-015: EUR em 14/07 usa a taxa de 14/07 do arquivo (5,93)."""
    assert cotacao(_cambio(), "EUR", date(2026, 7, 14)) == Cotacao(
        Decimal("5.93"), date(2026, 7, 14)
    )


def test_rn015_sabado_usa_a_sexta():
    """RN-015 / AMB-024: EUR em 18/07 (sábado) usa 17/07 (sexta, D-1), 5,96."""
    assert cotacao(_cambio(), "EUR", date(2026, 7, 18)) == Cotacao(
        Decimal("5.96"), date(2026, 7, 17)
    )


def test_rn015_cotacao_ate_3_dias_antes():
    """RN-015 / AMB-024: câmbio só com 13/07; USD em 16/07 usa 13/07 (D-3)."""
    cambio = _cambio(taxas={"2026-07-13": {"USD": Decimal("5.42")}})
    # 16/07 - 3 dias = 13/07: ainda dentro da janela
    assert cotacao(cambio, "USD", date(2026, 7, 16)) == Cotacao(
        Decimal("5.42"), date(2026, 7, 13)
    )


def test_rn015_cotacao_4_dias_antes_nao_serve():
    """RN-015 / AMB-024: câmbio só com 13/07; USD em 17/07 → sem cotação (D-4)."""
    cambio = _cambio(taxas={"2026-07-13": {"USD": Decimal("5.42")}})
    # 17/07 - 4 dias = 13/07: fora da janela D a D-3
    assert cotacao(cambio, "USD", date(2026, 7, 17)) is None


def test_rn015_nunca_usa_cotacao_posterior():
    """RN-015 / AMB-024: USD em 12/07 → sem cotação, nunca a de 13/07."""
    # de 09/07 a 12/07 não há cotação; 13/07 é posterior
    assert cotacao(_cambio(), "USD", date(2026, 7, 12)) is None


@pytest.mark.parametrize("moeda", ["GBP", "XYZ"])
def test_rn015_moeda_fora_do_arquivo_nao_tem_cotacao(moeda):
    """RN-015 / AMB-025: moeda bem formada sem taxa no arquivo → sem cotação."""
    # 21/07 tem cotação, mas só de USD e EUR
    assert cotacao(_cambio(), moeda, date(2026, 7, 21)) is None


def test_rn015_data_intermediaria_sem_a_moeda_e_pulada():
    """RN-015 / AMB-024: 14/07 só cota USD; EUR em 15/07 usa 13/07 (5,91)."""
    cambio = _cambio(
        taxas={
            "2026-07-13": {"USD": Decimal("5.42"), "EUR": Decimal("5.91")},
            "2026-07-14": {"USD": Decimal("5.44")},
        }
    )
    # 15/07 sem cotação; 14/07 sem EUR; 13/07 (D-2) tem EUR
    assert cotacao(cambio, "EUR", date(2026, 7, 15)) == Cotacao(
        Decimal("5.91"), date(2026, 7, 13)
    )


@pytest.mark.parametrize(
    "taxas",
    [
        pytest.param({}, id="cambio_vazio"),
        pytest.param({"2026-07-14": {"BRL": Decimal(7)}}, id="brl_no_arquivo"),
    ],
)
def test_rn015_brl_tem_taxa_1_sem_consultar_o_arquivo(taxas):
    """RN-015 / AMB-025: BRL → taxa 1, data nula; BRL no arquivo é ignorado."""
    assert cotacao(_cambio(taxas=taxas), "BRL", date(2026, 7, 14)) == Cotacao(
        Decimal(1), None
    )


def test_rn015_busca_no_inicio_do_calendario_nao_falha():
    """RN-015 / DT-014: em 0001-01-02 não há D-2 nem D-3; a busca para sem erro."""
    cambio = _cambio(taxas={"0001-01-01": {"USD": Decimal("5.42")}})
    assert cotacao(cambio, "USD", date(1, 1, 2)) == Cotacao(
        Decimal("5.42"), date(1, 1, 1)
    )
    assert cotacao(cambio, "EUR", date(1, 1, 2)) is None
