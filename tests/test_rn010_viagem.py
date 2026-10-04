"""Colaborador em viagem: RN-010 / AMB-004 / AMB-006 / AMB-016 (etapa 8 da seção 8).

Período padrão do `conftest`: 2026-07-01 a 2026-07-31.
"""

from decimal import Decimal

import pytest


def _hospedagem(**campos):
    padrao = dict(id="h", categoria="hospedagem", fornecedor="Hotel",
                  valor=Decimal("200.00"), tem_nota_fiscal=True)
    padrao.update(campos)
    return padrao


def _resumo(item):
    return (item["valor_reembolsado"], item["status"], item["motivo"])


def test_rn010_hospedagem_com_nota_poe_d_e_d_mais_1_em_viagem(avaliar, despesa):
    """RN-010 / AMB-004 (aceite): hospedagem com nota em 14/07 → 14/07 e 15/07 em
    viagem; 13/07 e 16/07 não."""
    itens = avaliar(
        despesa(**_hospedagem(data="2026-07-14")),
        despesa(id="a13", data="2026-07-13", valor=Decimal("10.00")),
        despesa(id="a14", data="2026-07-14", valor=Decimal("10.00")),
        despesa(id="a15", data="2026-07-15", valor=Decimal("10.00")),
        despesa(id="a16", data="2026-07-16", valor=Decimal("10.00")),
    )["itens"]

    # D = 14/07 → {14/07, 15/07}
    assert [item["em_viagem"] for item in itens] == [True, False, True, True, False]


def test_rn010_alimentacao_no_dia_seguinte_tem_limite_de_viagem(avaliar, despesa):
    """RN-010 (aceite): alimentação 80,00 em 15/07, depois da diária de 14/07 →
    limite 90,00, `aprovado` com 80,00."""
    _, alimentacao = avaliar(
        despesa(**_hospedagem(data="2026-07-14")),
        despesa(id="a", data="2026-07-15", valor=Decimal("80.00")),
    )["itens"]

    # 15/07 = D+1 → em viagem; 80,00 ≤ 90,00 → aprovado
    assert alimentacao["em_viagem"] is True
    assert alimentacao["limite_diario"] == Decimal("90.00")
    assert _resumo(alimentacao) == (Decimal("80.00"), "aprovado", None)


def test_rn010_alimentacao_dois_dias_depois_tem_limite_normal(avaliar, despesa):
    """RN-010 (aceite): alimentação 80,00 em 16/07, dois dias depois da diária de
    14/07 → limite 60,00, `parcial` com 60,00."""
    _, alimentacao = avaliar(
        despesa(**_hospedagem(data="2026-07-14")),
        despesa(id="a", data="2026-07-16", valor=Decimal("80.00")),
    )["itens"]

    # 16/07 = D+2 → fora de viagem; min(80,00; 60,00) = 60,00 → parcial
    assert alimentacao["em_viagem"] is False
    assert alimentacao["limite_diario"] == Decimal("60.00")
    assert _resumo(alimentacao) == (
        Decimal("60.00"), "parcial", "limite_diario_excedido",
    )


def test_rn010_transporte_em_viagem_tem_limite_120(avaliar, despesa):
    """RN-010 / RN-009: transporte em data em viagem → limite 120,00."""
    _, transporte = avaliar(
        despesa(**_hospedagem(data="2026-07-14")),
        despesa(id="t", data="2026-07-14", categoria="transporte_urbano",
                fornecedor="Táxi", valor=Decimal("130.00")),
    )["itens"]

    # 14/07 em viagem; min(130,00; 120,00) = 120,00 → parcial
    assert transporte["em_viagem"] is True
    assert transporte["limite_diario"] == Decimal("120.00")
    assert _resumo(transporte) == (
        Decimal("120.00"), "parcial", "limite_diario_excedido",
    )


def test_rn010_hospedagem_em_viagem_continua_com_limite_250(avaliar, despesa):
    """RN-010 / AMB-006: hospedagem em data em viagem não amplia: limite 250,00."""
    (hospedagem,) = avaliar(
        despesa(**_hospedagem(data="2026-07-14", valor=Decimal("300.00"))),
    )["itens"]

    # a própria hospedagem põe 14/07 em viagem; min(300,00; 250,00) = 250,00
    assert hospedagem["em_viagem"] is True
    assert hospedagem["limite_diario"] == Decimal("250.00")
    assert _resumo(hospedagem) == (
        Decimal("250.00"), "parcial", "limite_diario_excedido",
    )


def test_rn010_hospedagem_sem_nota_e_reembolsada_mas_nao_comprova_viagem(
    avaliar, despesa
):
    """RN-010 / AMB-004 (aceite): hospedagem de 80,00 sem nota em 03/07 →
    reembolsada pelas regras normais; 03/07 e 04/07 não ficam em viagem."""
    hospedagem, a03, a04 = avaliar(
        despesa(**_hospedagem(data="2026-07-03", valor=Decimal("80.00"),
                              tem_nota_fiscal=False)),
        despesa(id="a03", data="2026-07-03", valor=Decimal("90.00")),
        despesa(id="a04", data="2026-07-04", valor=Decimal("90.00")),
    )["itens"]

    # 80,00 ≤ 100,00 → não exige nota (RN-008); 80,00 ≤ 250,00 → aprovado
    assert _resumo(hospedagem) == (Decimal("80.00"), "aprovado", None)
    assert hospedagem["em_viagem"] is False
    # sem nota não comprova viagem: min(90,00; 60,00) = 60,00 nos dois dias
    for item in (a03, a04):
        assert item["em_viagem"] is False
        assert item["limite_diario"] == Decimal("60.00")
        assert _resumo(item) == (Decimal("60.00"), "parcial", "limite_diario_excedido")


def test_rn010_hospedagem_fora_do_periodo_nao_comprova_viagem(avaliar, despesa):
    """RN-010 / RN-005 (aceite): hospedagem com nota em 30/06, período desde 01/07
    → `fora_do_periodo`, e 01/07 não fica em viagem."""
    hospedagem, alimentacao = avaliar(
        despesa(**_hospedagem(data="2026-06-30")),
        despesa(id="a", data="2026-07-01", valor=Decimal("80.00")),
    )["itens"]

    # recusada na etapa 4 → não comprova viagem; min(80,00; 60,00) = 60,00
    assert (hospedagem["status"], hospedagem["motivo"]) == (
        "recusado", "fora_do_periodo",
    )
    assert (hospedagem["em_viagem"], hospedagem["limite_diario"]) == (None, None)
    assert alimentacao["em_viagem"] is False
    assert _resumo(alimentacao) == (
        Decimal("60.00"), "parcial", "limite_diario_excedido",
    )


def test_rn010_hospedagem_duplicata_nao_comprova_viagem(avaliar, despesa):
    """RN-010 / RN-007 / AMB-016: hospedagem com nota recusada como `duplicata` na
    etapa 7 não comprova viagem por si; a original, com nota, comprova D e D+1."""
    original, copia, alimentacao = avaliar(
        despesa(**_hospedagem(id="h1", data="2026-07-14")),
        despesa(**_hospedagem(id="h2", data="2026-07-14")),
        despesa(id="a", data="2026-07-15", valor=Decimal("80.00")),
    )["itens"]

    assert (copia["status"], copia["motivo"]) == ("recusado", "duplicata")
    assert (copia["em_viagem"], copia["limite_diario"]) == (None, None)
    # a original com nota passou pelas etapas 1 a 7 → 14/07 e 15/07 em viagem
    assert original["em_viagem"] is True
    assert alimentacao["em_viagem"] is True
    assert _resumo(alimentacao) == (Decimal("80.00"), "aprovado", None)


def test_rn010_duplicatas_de_hospedagem_sem_nota_nao_comprovam_viagem(
    avaliar, despesa
):
    """RN-010 / RN-007: duas cópias de hospedagem de 90,00 sem nota → a original
    segue, mas sem nota não comprova viagem; a outra é `duplicata`."""
    original, copia, alimentacao = avaliar(
        despesa(**_hospedagem(id="h1", data="2026-07-14", valor=Decimal("90.00"),
                              tem_nota_fiscal=False)),
        despesa(**_hospedagem(id="h2", data="2026-07-14", valor=Decimal("90.00"),
                              tem_nota_fiscal=False)),
        despesa(id="a", data="2026-07-14", valor=Decimal("80.00")),
    )["itens"]

    assert copia["motivo"] == "duplicata"
    assert original["em_viagem"] is False
    # 14/07 fora de viagem: min(80,00; 60,00) = 60,00
    assert alimentacao["em_viagem"] is False
    assert _resumo(alimentacao) == (
        Decimal("60.00"), "parcial", "limite_diario_excedido",
    )


@pytest.mark.parametrize("sem_nota_primeiro", [True, False])
def test_rn010_duplicata_de_hospedagem_so_uma_com_nota_comprova_viagem(
    avaliar, despesa, sem_nota_primeiro
):
    """RN-010 / RN-007 (aceite): hospedagem 90,00 sem nota e a mesma com nota, em
    qualquer ordem → a com nota é a original e comprova viagem."""
    sem = despesa(**_hospedagem(id="sem", data="2026-07-14", valor=Decimal("90.00"),
                                tem_nota_fiscal=False))
    com = despesa(**_hospedagem(id="com", data="2026-07-14", valor=Decimal("90.00")))
    hospedagens = [sem, com] if sem_nota_primeiro else [com, sem]
    saida = avaliar(
        *hospedagens, despesa(id="a", data="2026-07-15", valor=Decimal("80.00")),
    )
    itens = {item["id"]: item for item in saida["itens"]}

    assert itens["sem"]["motivo"] == "duplicata"
    assert itens["com"]["em_viagem"] is True
    # 15/07 = D+1 em viagem: 80,00 ≤ 90,00 → aprovado
    assert itens["a"]["em_viagem"] is True
    assert _resumo(itens["a"]) == (Decimal("80.00"), "aprovado", None)


def test_rn010_hospedagem_acima_de_100_sem_nota_nao_comprova_viagem(
    avaliar, despesa
):
    """RN-010 / RN-008: hospedagem de 690,00 sem nota → `nota_fiscal_ausente`; a
    data não fica em viagem."""
    hospedagem, alimentacao = avaliar(
        despesa(**_hospedagem(data="2026-07-14", valor=Decimal("690.00"),
                              tem_nota_fiscal=False)),
        despesa(id="a", data="2026-07-14", valor=Decimal("80.00")),
    )["itens"]

    assert hospedagem["motivo"] == "nota_fiscal_ausente"
    assert alimentacao["em_viagem"] is False
    assert alimentacao["limite_diario"] == Decimal("60.00")


def test_rn010_hospedagem_que_recebe_zero_no_limite_comprova_viagem(
    avaliar, despesa
):
    """RN-010 / AMB-016: a terceira hospedagem do dia, com nota, recebe 0 no limite
    (etapa 9), mas passou pelas etapas 1 a 7 → comprova viagem (D+1 em viagem)."""
    _, _, h3, alimentacao = avaliar(
        despesa(**_hospedagem(id="h1", data="2026-07-14", fornecedor="Hotel A",
                              valor=Decimal("200.00"))),
        despesa(**_hospedagem(id="h2", data="2026-07-14", fornecedor="Hotel B",
                              valor=Decimal("50.00"))),
        despesa(**_hospedagem(id="h3", data="2026-07-14", fornecedor="Hotel C",
                              valor=Decimal("40.00"))),
        despesa(id="a", data="2026-07-15", valor=Decimal("80.00")),
    )["itens"]

    # 200,00 + 50,00 = 250,00 → h3 recebe min(40,00; 0,00) = 0 → recusado
    assert _resumo(h3) == (Decimal("0"), "recusado", "limite_diario_excedido")
    assert h3["em_viagem"] is True
    # 15/07 = D+1 em viagem: 80,00 ≤ 90,00 → aprovado
    assert alimentacao["em_viagem"] is True
    assert _resumo(alimentacao) == (Decimal("80.00"), "aprovado", None)


def test_rn010_alimentacao_antes_da_hospedagem_na_entrada_esta_em_viagem(
    avaliar, despesa
):
    """RN-010 / AMB-016 (seção 8, etapa 8 antes da 9): alimentação 80,00 e depois
    hospedagem com nota, mesma data → alimentação em viagem, `aprovado` com 80,00."""
    alimentacao, _ = avaliar(
        despesa(id="a", data="2026-07-14", valor=Decimal("80.00")),
        despesa(**_hospedagem(data="2026-07-14")),
    )["itens"]

    # viagem determinada antes do limite: 80,00 ≤ 90,00 → aprovado
    assert alimentacao["em_viagem"] is True
    assert alimentacao["limite_diario"] == Decimal("90.00")
    assert _resumo(alimentacao) == (Decimal("80.00"), "aprovado", None)


def test_rn010_hospedagem_no_ultimo_dia_poe_dia_seguinte_fora_do_periodo(
    avaliar, despesa
):
    """RN-010 / RN-005: hospedagem com nota em 31/07 põe 01/08 em viagem, sem efeito:
    a despesa de 01/08 é `fora_do_periodo` antes do limite."""
    hospedagem, alimentacao = avaliar(
        despesa(**_hospedagem(data="2026-07-31")),
        despesa(id="a", data="2026-08-01", valor=Decimal("80.00")),
    )["itens"]

    assert hospedagem["em_viagem"] is True
    # recusada na etapa 4 → `em_viagem` nulo, não verdadeiro (seção 4)
    assert (alimentacao["status"], alimentacao["motivo"]) == (
        "recusado", "fora_do_periodo",
    )
    assert (alimentacao["em_viagem"], alimentacao["limite_diario"]) == (None, None)


def test_rn010_limite_de_nota_nao_amplia_em_viagem(avaliar, despesa):
    """RN-010 / RN-008 / AMB-007: transporte de 110,00 sem nota em data em viagem
    → `nota_fiscal_ausente` (o 100,00 não amplia)."""
    _, transporte = avaliar(
        despesa(**_hospedagem(data="2026-07-14")),
        despesa(id="t", data="2026-07-14", categoria="transporte_urbano",
                fornecedor="Táxi", valor=Decimal("110.00"), tem_nota_fiscal=False),
    )["itens"]

    assert (transporte["status"], transporte["motivo"]) == (
        "recusado", "nota_fiscal_ausente",
    )
    assert (transporte["em_viagem"], transporte["limite_diario"]) == (None, None)


def test_rn010_duas_hospedagens_em_datas_seguidas_cobrem_tres_dias(avaliar, despesa):
    """RN-010: a união dos {D, D+1} de cada hospedagem: 14/07 e 15/07 → 14, 15 e 16/07
    em viagem; 17/07 não."""
    itens = avaliar(
        despesa(**_hospedagem(id="h14", data="2026-07-14")),
        despesa(**_hospedagem(id="h15", data="2026-07-15")),
        despesa(id="a16", data="2026-07-16", valor=Decimal("10.00")),
        despesa(id="a17", data="2026-07-17", valor=Decimal("10.00")),
    )["itens"]

    assert [item["em_viagem"] for item in itens] == [True, True, True, False]


def test_rn010_hospedagem_no_ultimo_dia_representavel(avaliar, despesa):
    """RN-010: hospedagem com nota em 9999-12-31 (período até essa data) → a data
    fica em viagem; o D+1 não existe e não interrompe o processamento."""
    (hospedagem,) = avaliar(
        despesa(**_hospedagem(data="9999-12-31", valor=Decimal("50.00"))),
        periodo={"inicio": "9999-12-01", "fim": "9999-12-31"},
    )["itens"]

    # 50,00 ≤ 250,00 → aprovado; D em viagem
    assert hospedagem["em_viagem"] is True
    assert _resumo(hospedagem) == (Decimal("50.00"), "aprovado", None)


def test_rn010_hospedagem_com_limite_zero_nao_comprova_viagem(avaliar, despesa):
    """RN-010 / AMB-021 (aceite): `CC-ENG-PLATAFORMA`, hospedagem com nota em
    14/07 → `categoria_fora_da_politica`; alimentação de 100,00 com nota em 15/07
    → fora de viagem, limite 75,00, `parcial` com 75,00."""
    hospedagem, alimentacao = avaliar(
        despesa(**_hospedagem(data="2026-07-14", valor=Decimal("480.00"))),
        despesa(id="a", data="2026-07-15", valor=Decimal("100.00"),
                tem_nota_fiscal=True),
        centro_custo="CC-ENG-PLATAFORMA",
    )["itens"]

    assert (hospedagem["status"], hospedagem["motivo"]) == (
        "recusado", "categoria_fora_da_politica",
    )
    # 15/07 fora de viagem: limite normal 75,00; min(100,00; 75,00) = 75,00
    assert (alimentacao["em_viagem"], alimentacao["limite_diario"]) == (
        False, Decimal("75.00"),
    )
    assert _resumo(alimentacao) == (
        Decimal("75.00"), "parcial", "limite_diario_excedido",
    )


def test_rn010_cc_comercial_alimentacao_em_viagem_tem_limite_135(avaliar, despesa):
    """RN-010 / RN-009 (aceite): `CC-COMERCIAL`, hospedagem com nota em 14/07;
    alimentação de 140,00 em 15/07 → limite 135,00 (90,00 × 1,5)."""
    _, alimentacao = avaliar(
        despesa(**_hospedagem(data="2026-07-14")),
        despesa(id="a", data="2026-07-15", valor=Decimal("140.00")),
        centro_custo="CC-COMERCIAL",
    )["itens"]

    # 90,00 × (1 + 50/100) = 135,00; min(140,00; 135,00) = 135,00
    assert (alimentacao["em_viagem"], alimentacao["limite_diario"]) == (
        True, Decimal("135.00"),
    )
    assert _resumo(alimentacao) == (
        Decimal("135.00"), "parcial", "limite_diario_excedido",
    )


def test_rn010_moeda_estrangeira_nao_comprova_viagem(avaliar, despesa):
    """RN-010 / AMB-023 (aceite): alimentação de 22,00 EUR com nota em 14/07,
    sem hospedagem → 14/07 não fica em viagem."""
    (item,) = avaliar(
        despesa(data="2026-07-14", valor=Decimal("22.00"), moeda="EUR")
    )["itens"]

    # 22,00 × 5,93 = 130,46; fora de viagem: limite 60,00 → parcial com 60,00
    assert (item["em_viagem"], item["limite_diario"]) == (False, Decimal("60.00"))
    assert _resumo(item) == (Decimal("60.00"), "parcial", "limite_diario_excedido")
