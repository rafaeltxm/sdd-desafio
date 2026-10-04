"""Arredondamento ao centavo: RN-003, AMB-014."""

from decimal import Decimal, localcontext

import pytest
import simplejson

from conftest import (
    construir_cambio,
    construir_despesa,
    construir_entrada,
    construir_politica,
)
from reembolso.cambio import ler_cambio
from reembolso.entrada import ler_entrada
from reembolso.motor import calcular
from reembolso.politica import ler_politica
from reembolso.saida import para_dicionario


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


@pytest.mark.parametrize(
    ("valor", "considerado"),
    [
        # RN-003 Aceite: 16,8649 × 5,93 = 100,008857 → 100,01
        # (arredondar antes daria 16,86 × 5,93 = 99,98)
        (Decimal("16.8649"), Decimal("100.01")),
        # RN-003 Aceite: 0,001 × 5,93 = 0,00593 → 0,01
        (Decimal("0.001"), Decimal("0.01")),
    ],
)
def test_rn003_conversao_arredondada_uma_vez_em_reais(
    avaliar, despesa, valor, considerado
):
    """RN-003 / AMB-026: o valor exato em EUR é multiplicado pela taxa (5,93 em
    14/07) e o produto é arredondado uma única vez, em reais."""
    (item,) = avaliar(
        despesa(data="2026-07-14", valor=valor, moeda="EUR")
    )["itens"]

    assert item["valor_considerado"] == considerado
    assert item["valor_informado"] == valor


def test_rn003_produto_com_mais_de_28_digitos_e_exato(avaliar, despesa):
    """RN-003 / DT-012: o produto é exato, sem a precisão padrão de 28 dígitos.

    Câmbio com USD 2 em 14/07; 50,002499999999999999999999999999 USD sem nota."""
    cambio = construir_cambio(taxas={"2026-07-14": {"USD": Decimal("2")}})
    (item,) = avaliar(
        despesa(data="2026-07-14", valor=Decimal("50.002499999999999999999999999999"),
                moeda="USD", tem_nota_fiscal=False),
        cambio=cambio,
    )["itens"]

    # exato: 100,004999999999999999999999999998 → 100,00 (com 28 dígitos o
    # produto viraria 100,0050000… → 100,01, e exigiria nota)
    assert item["valor_considerado"] == Decimal("100.00")
    assert item["motivo"] != "nota_fiscal_ausente"


def _calcular_com_precisao_6(*despesas, politica=None) -> dict:
    """Lê entrada, v4 (ou `politica`) e câmbio no contexto padrão e chama só o
    motor dentro de um contexto ambiente de 6 dígitos (DT-012)."""
    def _bytes(documento):
        return simplejson.dumps(documento, use_decimal=True).encode()

    entrada = ler_entrada(_bytes(construir_entrada(despesas)))
    politica = ler_politica(_bytes(politica or construir_politica()))
    cambio = ler_cambio(_bytes(construir_cambio()))
    with localcontext(prec=6):
        resultado = calcular(entrada, politica, cambio)
    return para_dicionario(resultado)


def test_rn003_saldo_do_limite_nao_depende_do_contexto_de_quem_chama():
    """RN-003 / RN-009 / DT-012: o saldo por data e categoria é exato mesmo com o
    motor chamado num contexto ambiente de 6 dígitos.

    Política com alimentação 1.234.567,89 no `padrao`; duas despesas no mesmo dia
    e na mesma categoria, com nota."""
    politica = construir_politica()
    politica["padrao"]["alimentacao"]["limite"] = Decimal("1234567.89")
    primeira, segunda = _calcular_com_precisao_6(
        construir_despesa(id="d-1", fornecedor="A", valor=Decimal("0.01")),
        construir_despesa(id="d-2", fornecedor="B", valor=Decimal("1234567.89")),
        politica=politica,
    )["itens"]

    # saldo depois da primeira: 1.234.567,89 - 0,01 = 1.234.567,88 (9 dígitos;
    # com prec=6 viraria 1.234.570, maior que a despesa, e a segunda sairia aprovada)
    assert primeira["status"] == "aprovado"
    assert primeira["valor_reembolsado"] == Decimal("0.01")
    # segunda: min(1.234.567,89; 1.234.567,88) = 1.234.567,88 → parcial (RN-011)
    assert segunda["status"] == "parcial"
    assert segunda["motivo"] == "limite_diario_excedido"
    assert segunda["valor_reembolsado"] == Decimal("1234567.88")


def test_rn003_totais_nao_dependem_do_contexto_de_quem_chama():
    """RN-003 / RN-001 / DT-012: os totais são exatos mesmo com o motor chamado
    num contexto ambiente de 6 dígitos.

    v4 (`padrao`, alimentação 60,00); duas despesas com nota em dias diferentes."""
    totais = _calcular_com_precisao_6(
        construir_despesa(id="d-1", data="2026-07-03", valor=Decimal("1234.56")),
        construir_despesa(id="d-2", data="2026-07-04", valor=Decimal("99999.99")),
    )["totais"]

    # solicitado: 1.234,56 + 99.999,99 = 101.234,55 (com prec=6: 101.235)
    assert totais["valor_solicitado"] == Decimal("101234.55")
    # reembolsado: 60,00 + 60,00 = 120,00 (cada dia limitado a 60,00)
    assert totais["valor_reembolsado"] == Decimal("120.00")
    # glosado: 101.234,55 - 120,00 = 101.114,55 (com prec=6: 101.115)
    assert totais["valor_glosado"] == Decimal("101114.55")
