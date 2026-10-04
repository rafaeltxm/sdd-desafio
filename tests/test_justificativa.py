from datetime import date
from decimal import Decimal

import pytest

from reembolso.justificativa import formatar_data, formatar_reais, justificar
from reembolso.modelo import Motivo, Status

# Pares status × motivo da tabela "Códigos de motivo" da seção 4 da spec, mais
# `aprovado` sem motivo (RN-011). Os campos de cada caso são os que um item com
# esse status e motivo tem na saída (seção 4): recusado antes do limite diário →
# `limite_diario` nulo; `entrada_invalida` → também `valor_considerado` nulo.
COMBINACOES = [
    pytest.param(
        Status.APROVADO, None,
        dict(data=date(2026, 7, 3), categoria="alimentacao",
             valor_considerado=Decimal("45.00"), valor_reembolsado=Decimal("45.00"),
             limite_diario=Decimal("60.00")),
        id="aprovado",
    ),
    pytest.param(
        Status.RECUSADO, Motivo.ENTRADA_INVALIDA,
        dict(data=None, categoria=None, valor_considerado=None,
             valor_reembolsado=Decimal("0"), limite_diario=None),
        id="recusado-entrada_invalida",
    ),
    pytest.param(
        Status.RECUSADO, Motivo.CAMBIO_INDISPONIVEL,
        dict(data=date(2026, 7, 21), categoria="alimentacao", moeda="GBP",
             valor_considerado=None, valor_reembolsado=Decimal("0"),
             limite_diario=None),
        id="recusado-cambio_indisponivel",
    ),
    pytest.param(
        Status.RECUSADO, Motivo.VALOR_INVALIDO,
        dict(data=date(2026, 7, 3), categoria="alimentacao",
             valor_considerado=Decimal("-45.00"), valor_reembolsado=Decimal("0"),
             limite_diario=None),
        id="recusado-valor_invalido",
    ),
    pytest.param(
        Status.RECUSADO, Motivo.FORA_DO_PERIODO,
        dict(data=date(2026, 4, 15), categoria="alimentacao",
             valor_considerado=Decimal("30.00"), valor_reembolsado=Decimal("0"),
             limite_diario=None),
        id="recusado-fora_do_periodo",
    ),
    pytest.param(
        Status.RECUSADO, Motivo.CATEGORIA_FORA_DA_POLITICA,
        dict(data=date(2026, 7, 3), categoria="coworking",
             valor_considerado=Decimal("30.00"), valor_reembolsado=Decimal("0"),
             limite_diario=None),
        id="recusado-categoria_fora_da_politica",
    ),
    pytest.param(
        Status.RECUSADO, Motivo.NOTA_FISCAL_AUSENTE,
        dict(data=date(2026, 7, 3), categoria="transporte_urbano",
             valor_considerado=Decimal("110.00"), valor_reembolsado=Decimal("0"),
             limite_diario=None),
        id="recusado-nota_fiscal_ausente",
    ),
    pytest.param(
        Status.RECUSADO, Motivo.DUPLICATA,
        dict(data=date(2026, 7, 3), categoria="alimentacao",
             valor_considerado=Decimal("54.90"), valor_reembolsado=Decimal("0"),
             limite_diario=None),
        id="recusado-duplicata",
    ),
    pytest.param(
        Status.PARCIAL, Motivo.LIMITE_DIARIO_EXCEDIDO,
        dict(data=date(2026, 7, 3), categoria="alimentacao",
             valor_considerado=Decimal("30.00"), valor_reembolsado=Decimal("15.00"),
             limite_diario=Decimal("60.00")),
        id="parcial-limite_diario_excedido",
    ),
    pytest.param(
        Status.PARCIAL, Motivo.LIMITE_DIARIO_EXCEDIDO,
        dict(data=date(2026, 7, 14), categoria="alimentacao", moeda="EUR",
             taxa_cambio=Decimal("5.93"), data_cotacao=date(2026, 7, 14),
             valor_considerado=Decimal("130.46"),
             valor_reembolsado=Decimal("60.00"), limite_diario=Decimal("60.00")),
        id="parcial-convertido-de-eur",
    ),
    pytest.param(
        Status.RECUSADO, Motivo.LIMITE_DIARIO_EXCEDIDO,
        dict(data=date(2026, 7, 3), categoria="alimentacao",
             valor_considerado=Decimal("38.00"), valor_reembolsado=Decimal("0"),
             limite_diario=Decimal("60.00")),
        id="recusado-limite_diario_excedido",
    ),
]


def test_combinacoes_cobrem_todos_os_motivos():
    """RN-011: a tabela de combinações do teste usa todo motivo da seção 4."""
    usados = {c.values[1] for c in COMBINACOES if c.values[1] is not None}
    assert usados == set(Motivo)


@pytest.mark.parametrize(("status", "motivo", "campos"), COMBINACOES)
def test_rn011_justificativa_nao_vazia_para_todo_status_e_motivo(
    status, motivo, campos
):
    """RN-011 / DT-009: todo item tem uma justificativa em texto; o conteúdo exato
    não é contratual (seção 4), só se confere que é texto não vazio."""
    # o mínimo da nota vem da política (DT-009); 100,00 na v4
    texto = justificar(status, motivo, nota_fiscal_acima_de=Decimal("100.00"),
                       **campos)
    assert isinstance(texto, str)
    assert texto.strip()


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        (Decimal("1234.5"), "1.234,50"),  # aceite da T-004
        (Decimal("45.00"), "45,00"),  # exemplo da seção 4
        (Decimal("0"), "0,00"),
        (Decimal("-45.00"), "-45,00"),
        (Decimal("999999999.99"), "999.999.999,99"),
        (Decimal("1000000000.00"), "1.000.000.000,00"),
    ],
)
def test_formata_decimal_em_reais(valor, esperado):
    """DT-009: `Decimal` como `1.234,56` (ponto no milhar, vírgula nos centavos),
    sem `locale`."""
    assert formatar_reais(valor) == esperado


@pytest.mark.parametrize(
    ("data", "esperado"),
    [
        (date(2026, 7, 3), "03/07"),  # exemplo da seção 4
        (date(2026, 12, 31), "31/12"),
        (date(2026, 1, 1), "01/01"),
    ],
)
def test_formata_data_dd_mm(data, esperado):
    """DT-009: data como `DD/MM`, com dois algarismos cada, sem `locale`."""
    assert formatar_data(data) == esperado
