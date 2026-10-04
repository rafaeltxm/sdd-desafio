"""Aritmética de `Decimal` de `dinheiro.py`: RN-003, RN-009, DT-012, DT-013."""

from decimal import Decimal, Inexact, InvalidOperation, Subnormal

import pytest

from reembolso.dinheiro import arredondar, contexto_exato, truncar


@pytest.mark.parametrize(
    ("valor", "taxa", "esperado"),
    [
        # 16,8649 × 5,93 = 100,008857 → 100,01 (arredondar antes daria 99,98)
        ("16.8649", "5.93", "100.01"),
        # 0,001 × 5,93 = 0,00593 → 0,01
        ("0.001", "5.93", "0.01"),
    ],
)
def test_rn003_produto_exato_arredondado_uma_vez(valor, taxa, esperado):
    """RN-003 / AMB-026: o produto exato é arredondado uma única vez."""
    with contexto_exato():
        produto = Decimal(valor) * Decimal(taxa)
    assert arredondar(produto) == Decimal(esperado)


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        ("10.005", "10.01"),  # metade afastando do zero
        ("-0.005", "-0.01"),  # metade afastando do zero, negativo
        ("10.004", "10.00"),
    ],
)
def test_rn003_arredondar_metade_afastando_do_zero(valor, esperado):
    """RN-003: 2 casas, a metade arredondada afastando do zero."""
    assert arredondar(Decimal(valor)) == Decimal(esperado)


def test_produto_com_mais_de_28_digitos_e_exato():
    """DT-012 / RN-003: produto de 39 dígitos não é arredondado pelo contexto."""
    # (10^9 - 10^-11) × 5.123456789123456789
    #   = 5123456789.123456789 - 0.00000000005123456789123456789
    #   = 5123456789.12345678894876543210876543211   (39 dígitos)
    # com 28 dígitos sairia 5123456789.123456788948765432
    with contexto_exato():
        produto = Decimal("999999999.99999999999") * Decimal("5.123456789123456789")
    assert produto == Decimal("5123456789.12345678894876543210876543211")
    assert arredondar(produto) == Decimal("5123456789.12")


def test_soma_com_mais_de_28_casas_e_exata():
    """DT-012 / DT-013: `100 + percentual` com 41 casas não perde a última."""
    # 100 + 10^-41 = 100,(40 zeros)1; com 28 dígitos sairia 100,0…0
    percentual = Decimal("0." + "0" * 40 + "1")
    with contexto_exato():
        soma = Decimal(100) + percentual
    assert soma == Decimal("100." + "0" * 40 + "1")
    assert soma != Decimal(100)


@pytest.mark.parametrize(
    ("valor", "taxa", "esperado"),
    [
        # 10^-999999 × 5,93 = 5,93 × 10^-999999
        ("1E-999999", "5.93", "5.93E-999999"),
        # 10^-999999 × 0,593 = 5,93 × 10^-1000000: abaixo do Emin padrão
        ("1E-999999", "0.593", "5.93E-1000000"),
    ],
)
def test_produto_com_expoente_minimo(valor, taxa, esperado):
    """DT-012 / AMB-026: expoente mínimo sem subnormal, valor exato."""
    with contexto_exato() as contexto:
        produto = Decimal(valor) * Decimal(taxa)
        assert not contexto.flags[Subnormal]
    assert produto == Decimal(esperado)
    # RN-004: em reais, arredonda para 0,00
    assert arredondar(produto) == Decimal("0.00")


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        ("49.995", "49.99"),  # 33,33 × 1,5 = 49,995 → truncado, não 50,00
        ("90.00", "90.00"),  # 60,00 × 1,5 já no centavo
        ("49.9999999", "49.99"),
    ],
)
def test_rn009_truncar(valor, esperado):
    """RN-009 / DT-013: limite em viagem truncado ao centavo, nunca para cima."""
    assert truncar(Decimal(valor)) == Decimal(esperado)


def test_conta_inexata_levanta_erro():
    """DT-012: conta inexata no contexto exato não arredonda em silêncio."""
    # 1/3 não tem representação decimal finita. Com `prec = MAX_PREC`, o
    # CPython levanta `MemoryError` antes de tentar; com prec menor, `Inexact`.
    with pytest.raises((Inexact, MemoryError)), contexto_exato():
        Decimal(1) / Decimal(3)


def test_arredondamento_implicito_levanta_inexact():
    """DT-012: no contexto exato, conta que precisaria arredondar levanta `Inexact`."""
    # 1,23 em décimos perderia o 3: sem o trap, sairia 1,2 em silêncio
    with pytest.raises(Inexact), contexto_exato():
        Decimal("1.23").quantize(Decimal("0.1"))


def test_operacao_invalida_levanta_invalid_operation():
    """DT-012: operação inválida no contexto exato levanta exceção, não `NaN`."""
    # 0/0 é indefinido; sem o trap, sairia `NaN` em silêncio
    with pytest.raises(InvalidOperation), contexto_exato():
        Decimal(0) / Decimal(0)


def test_contexto_exato_nao_altera_o_contexto_global():
    """DT-012: o contexto exato é local; o contexto padrão continua com 28 dígitos."""
    with contexto_exato():
        pass
    assert Decimal(1) / Decimal(3) == Decimal("0.3333333333333333333333333333")
