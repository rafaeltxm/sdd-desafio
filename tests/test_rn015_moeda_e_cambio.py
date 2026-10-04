"""Moeda e conversão: RN-015, AMB-024, AMB-025, DT-014; etapa 2 da seção 8.

Salvo indicação, o câmbio é o `cambio.json` do envelope (`construir_cambio`),
com cotações de USD e EUR só em dias úteis, de 13/07 (segunda) a 28/07, e a
política é a v4 com a tabela `padrao` (alimentação 60,00).
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


def test_rn015_cotacao_ate_4_dias_antes():
    """RN-015 / AMB-024: câmbio só com 13/07; USD em 17/07 usa 13/07 (D-4)."""
    cambio = _cambio(taxas={"2026-07-13": {"USD": Decimal("5.42")}})
    # 17/07 - 4 dias = 13/07: ainda dentro da janela D a D-4
    assert cotacao(cambio, "USD", date(2026, 7, 17)) == Cotacao(
        Decimal("5.42"), date(2026, 7, 13)
    )


def test_rn015_cotacao_5_dias_antes_nao_serve():
    """RN-015 / AMB-024: câmbio só com 13/07; USD em 18/07 → sem cotação (D-5)."""
    cambio = _cambio(taxas={"2026-07-13": {"USD": Decimal("5.42")}})
    # 18/07 - 5 dias = 13/07: fora da janela D a D-4
    assert cotacao(cambio, "USD", date(2026, 7, 18)) is None


def test_rn015_terca_de_carnaval_usa_a_sexta():
    """RN-015 / AMB-024: câmbio só com 05/02/2027 (sexta); EUR em 09/02/2027
    (terça de Carnaval) usa 05/02 (D-4)."""
    cambio = _cambio(taxas={"2027-02-05": {"EUR": Decimal("6.00")}})
    # 09/02 - 4 dias = 05/02; 06/02 a 08/02 sem cotação
    assert cotacao(cambio, "EUR", date(2027, 2, 9)) == Cotacao(
        Decimal("6.00"), date(2027, 2, 5)
    )


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
    """RN-015 / DT-014: em 0001-01-02 não há D-2 a D-4; a busca para sem erro."""
    cambio = _cambio(taxas={"0001-01-01": {"USD": Decimal("5.42")}})
    assert cotacao(cambio, "USD", date(1, 1, 2)) == Cotacao(
        Decimal("5.42"), date(1, 1, 1)
    )
    assert cotacao(cambio, "EUR", date(1, 1, 2)) is None


# --- ponta a ponta: etapa 2 da seção 8 (motor) ---


def _conversao(item):
    return (
        item["moeda"], item["taxa_cambio"], item["data_cotacao"],
        item["valor_considerado"],
    )


def _recusado_cambio_indisponivel(item):
    # RN-015: recusado na etapa 2; sem valor em reais nem taxa (seção 4)
    assert (item["status"], item["motivo"]) == ("recusado", "cambio_indisponivel")
    assert item["valor_reembolsado"] == 0
    for campo in (
        "valor_considerado", "taxa_cambio", "data_cotacao", "em_viagem",
        "limite_diario",
    ):
        assert item[campo] is None, campo


def test_rn015_eur_na_propria_data_convertido(avaliar, despesa):
    """RN-015 (aceite): 22,00 EUR em 14/07 → taxa 5,93, `data_cotacao`
    2026-07-14, `valor_considerado` 130,46."""
    (item,) = avaliar(
        despesa(data="2026-07-14", valor=Decimal("22.00"), moeda="EUR")
    )["itens"]

    # 22,00 × 5,93 = 130,46; min(130,46; 60,00) = 60,00
    assert _conversao(item) == ("EUR", Decimal("5.93"), "2026-07-14",
                                Decimal("130.46"))
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("60.00"),
                                                          "parcial")


def test_rn015_eur_no_sabado_usa_a_cotacao_de_sexta(avaliar, despesa):
    """RN-015 / AMB-024 (aceite): 30,00 EUR em 18/07 (sábado) → taxa 5,96 de
    17/07, `valor_considerado` 178,80."""
    (item,) = avaliar(
        despesa(data="2026-07-18", valor=Decimal("30.00"), moeda="EUR")
    )["itens"]

    # sem cotação em 18/07; 17/07 (D-1) tem EUR 5,96: 30,00 × 5,96 = 178,80
    assert _conversao(item) == ("EUR", Decimal("5.96"), "2026-07-17",
                                Decimal("178.80"))


@pytest.mark.parametrize(
    "campos",
    [pytest.param({}, id="ausente"), pytest.param({"moeda": None}, id="nula"),
     pytest.param({"moeda": "BRL"}, id="BRL")],
)
def test_rn015_brl_tem_taxa_1_e_data_cotacao_nula(avaliar, despesa, campos):
    """RN-015 / AMB-025 (aceite): sem `moeda` ou `null` → `BRL`, taxa 1,
    `data_cotacao` nula; o valor não muda."""
    (item,) = avaliar(despesa(valor=Decimal("45.00"), **campos))["itens"]

    # 45,00 × 1 = 45,00 ≤ 60,00 → aprovado
    assert _conversao(item) == ("BRL", 1, None, Decimal("45.00"))
    assert item["status"] == "aprovado"


def test_rn015_brl_ignora_o_arquivo_de_cambio(avaliar, despesa):
    """RN-015: `BRL` no arquivo de câmbio é ignorado; a taxa continua 1."""
    cambio = construir_cambio(taxas={"2026-07-03": {"BRL": Decimal("7")}})
    (item,) = avaliar(despesa(valor=Decimal("45.00")), cambio=cambio)["itens"]

    assert _conversao(item) == ("BRL", 1, None, Decimal("45.00"))


def test_rn015_gbp_sem_cotacao_e_cambio_indisponivel(avaliar, despesa):
    """RN-015 / AMB-025 (aceite): 55,00 GBP em 21/07 → `cambio_indisponivel`,
    nulos, fora de `valor_solicitado`; a moeda e o valor informado saem."""
    saida = avaliar(
        despesa(data="2026-07-21", valor=Decimal("55.00"), moeda="GBP")
    )

    (item,) = saida["itens"]
    _recusado_cambio_indisponivel(item)
    assert (item["moeda"], item["valor_informado"]) == ("GBP", Decimal("55.00"))
    # seção 4: valor_considerado nulo não entra no solicitado
    assert saida["totais"] == {
        "valor_solicitado": 0, "valor_reembolsado": 0, "valor_glosado": 0,
    }


def test_rn015_usd_sem_cotacao_nos_4_dias_anteriores(avaliar, despesa):
    """RN-015 / AMB-024 (aceite): USD em 12/07 (nenhuma cotação de 08/07 a
    12/07; a de 13/07 é posterior) → `cambio_indisponivel`."""
    (item,) = avaliar(despesa(data="2026-07-12", moeda="USD"))["itens"]

    _recusado_cambio_indisponivel(item)


def test_rn015_codigo_fora_da_iso_e_cambio_indisponivel(avaliar, despesa):
    """RN-015 / AMB-025: `XYZ` é bem formado e não está no câmbio →
    `cambio_indisponivel` (sem lista ISO própria)."""
    (item,) = avaliar(despesa(data="2026-07-14", moeda="XYZ"))["itens"]

    _recusado_cambio_indisponivel(item)


def test_rn015_cotacao_d4_e_d5_no_motor(avaliar, despesa):
    """RN-015 / AMB-024 (aceite): câmbio só com 13/07; 10,00 USD em 17/07 usa
    13/07 (D-4); em 18/07 → `cambio_indisponivel` (D-5)."""
    cambio = construir_cambio(taxas={"2026-07-13": {"USD": Decimal("5.42")}})
    d4, d5 = avaliar(
        despesa(id="a", data="2026-07-17", valor=Decimal("10.00"), moeda="USD"),
        despesa(id="b", data="2026-07-18", valor=Decimal("10.00"), moeda="USD"),
        cambio=cambio,
    )["itens"]

    # 10,00 × 5,42 = 54,20
    assert _conversao(d4) == ("USD", Decimal("5.42"), "2026-07-13",
                              Decimal("54.20"))
    _recusado_cambio_indisponivel(d5)


def test_rn015_terca_de_carnaval_no_motor(avaliar, despesa):
    """RN-015 / AMB-024 (aceite): câmbio só com 05/02/2027 (EUR 6,00); 10,00 EUR
    em 09/02/2027 (terça de Carnaval) → `data_cotacao` 2027-02-05, 60,00."""
    cambio = construir_cambio(taxas={"2027-02-05": {"EUR": Decimal("6.00")}})
    (item,) = avaliar(
        despesa(data="2027-02-09", valor=Decimal("10.00"), moeda="EUR"),
        cambio=cambio,
        periodo={"inicio": "2027-02-01", "fim": "2027-02-28"},
    )["itens"]

    # 10,00 × 6,00 = 60,00 ≤ 60,00 (alimentação, padrao) → aprovado
    assert _conversao(item) == ("EUR", Decimal("6.00"), "2027-02-05",
                                Decimal("60.00"))
    assert (item["status"], item["valor_reembolsado"]) == ("aprovado",
                                                          Decimal("60.00"))


def test_rn015_cambio_indisponivel_nao_consome_limite_nem_soma(avaliar, despesa):
    """RN-015 / seção 4: a despesa sem cotação não consome limite e fica fora
    de `valor_solicitado`; a alimentação em BRL do mesmo dia não muda."""
    saida = avaliar(
        despesa(id="g", data="2026-07-21", valor=Decimal("55.00"), moeda="GBP"),
        despesa(id="b", data="2026-07-21", valor=Decimal("50.00"), fornecedor="B"),
    )

    _, brl = saida["itens"]
    # 50,00 ≤ 60,00 → aprovado; solicitado = 50,00 (GBP fora)
    assert (brl["valor_reembolsado"], brl["status"]) == (Decimal("50.00"),
                                                        "aprovado")
    assert saida["totais"] == {
        "valor_solicitado": Decimal("50.00"),
        "valor_reembolsado": Decimal("50.00"),
        "valor_glosado": Decimal("0.00"),
    }


def test_rn015_sem_cotacao_e_fora_do_periodo_e_cambio_indisponivel(
    avaliar, despesa
):
    """RN-015 / seção 8: sem cotação e fora do período → `cambio_indisponivel`
    (etapa 2 antes da 4)."""
    (item,) = avaliar(despesa(data="2026-04-15", moeda="USD"))["itens"]

    _recusado_cambio_indisponivel(item)


def test_rn015_sem_cotacao_e_valor_negativo_e_cambio_indisponivel(
    avaliar, despesa
):
    """RN-015 / seção 8: sem cotação e valor negativo → `cambio_indisponivel`
    (etapa 2 antes da 3)."""
    (item,) = avaliar(
        despesa(data="2026-07-21", valor=Decimal("-10.00"), moeda="GBP")
    )["itens"]

    _recusado_cambio_indisponivel(item)


def test_rn015_despesa_invalida_em_eur_tem_taxa_nula(avaliar, despesa):
    """RN-002 / RN-015 / seção 8: despesa inválida em EUR (sem
    `tem_nota_fiscal`) → `entrada_invalida` na etapa 1, com `taxa_cambio` e
    `data_cotacao` nulas, embora 14/07 tenha cotação de EUR."""
    documento = despesa(data="2026-07-14", moeda="EUR")
    del documento["tem_nota_fiscal"]
    (item,) = avaliar(documento)["itens"]

    assert (item["status"], item["motivo"]) == ("recusado", "entrada_invalida")
    assert item["moeda"] == "EUR"
    assert (item["taxa_cambio"], item["data_cotacao"], item["valor_considerado"]) == (
        None, None, None,
    )


def test_rn015_hospedagem_em_moeda_estrangeira_comprova_viagem(avaliar, despesa):
    """RN-015 / RN-010 / AMB-023: hospedagem de 50,00 EUR com nota em 22/07 →
    297,50, `parcial` com 250,00; 23/07 em viagem (limite 90,00)."""
    hospedagem, alimentacao = avaliar(
        despesa(id="h", data="2026-07-22", categoria="hospedagem",
                valor=Decimal("50.00"), moeda="EUR"),
        despesa(id="a", data="2026-07-23", valor=Decimal("80.00")),
    )["itens"]

    # 50,00 × 5,95 = 297,50; min(297,50; 250,00) = 250,00
    assert hospedagem["valor_considerado"] == Decimal("297.50")
    assert (hospedagem["valor_reembolsado"], hospedagem["status"]) == (
        Decimal("250.00"), "parcial",
    )
    # 23/07 = D+1: 60,00 × 1,5 = 90,00; 80,00 ≤ 90,00 → aprovado
    assert (alimentacao["em_viagem"], alimentacao["limite_diario"]) == (
        True, Decimal("90.00"),
    )
    assert alimentacao["status"] == "aprovado"


def test_rn015_taxa_e_valores_da_saida_do_motor_sao_decimal(avaliar, despesa):
    """RN-015 / DT-001: na saída real do motor, `taxa_cambio` (EUR e BRL) e os
    valores monetários convertidos são `Decimal`, nunca `float`."""
    saida = avaliar(
        despesa(id="e", data="2026-07-14", valor=Decimal("22.00"), moeda="EUR"),
        despesa(id="b", data="2026-07-14", valor=Decimal("10.00"), fornecedor="B"),
    )

    for item in saida["itens"]:
        for campo in ("taxa_cambio", "valor_considerado", "valor_reembolsado",
                      "limite_diario"):
            assert type(item[campo]) is Decimal, campo
    assert all(type(v) is Decimal for v in saida["totais"].values())


@pytest.mark.parametrize(
    ("campos", "motivo"),
    [
        # 22,00 GBP sem cotação → etapa 2
        ({"moeda": "GBP"}, "cambio_indisponivel"),
        # -10,00 EUR × 5,95 = -59,50 ≤ 0 → etapa 3, com a taxa preenchida
        ({"moeda": "EUR", "valor": Decimal("-10.00")}, "valor_invalido"),
    ],
)
def test_rn015_hospedagem_recusada_antes_do_limite_nao_comprova_viagem(
    avaliar, despesa, campos, motivo
):
    """RN-015 / RN-010 / seção 8: hospedagem com nota recusada na etapa 2 ou 3
    não comprova viagem; a recusada na etapa 3 sai com a taxa (seção 4)."""
    hospedagem, alimentacao = avaliar(
        despesa(**{"id": "h", "data": "2026-07-22", "categoria": "hospedagem",
                   "valor": Decimal("22.00"), **campos}),
        despesa(id="a", data="2026-07-23", valor=Decimal("80.00")),
    )["itens"]

    assert hospedagem["motivo"] == motivo
    if motivo == "valor_invalido":
        assert (hospedagem["taxa_cambio"], hospedagem["data_cotacao"]) == (
            Decimal("5.95"), "2026-07-22",
        )
    # 23/07 fora de viagem: limite 60,00; min(80,00; 60,00) = 60,00
    assert (alimentacao["em_viagem"], alimentacao["limite_diario"]) == (
        False, Decimal("60.00"),
    )
