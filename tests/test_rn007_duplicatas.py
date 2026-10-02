"""Duplicatas: RN-007 / AMB-010 / AMB-016 (etapa 7 da seção 8).

Período padrão do `conftest`: 2026-07-01 a 2026-07-31.
"""

from decimal import Decimal

import pytest


def _avaliado(item, reembolsado):
    # passou pela etapa 7 e chegou ao limite (etapa 9): `aprovado`, valores
    # preenchidos
    assert (item["status"], item["motivo"]) == ("aprovado", None)
    assert item["valor_reembolsado"] == reembolsado
    assert item["em_viagem"] is False
    assert item["limite_diario"] is not None


def _recusado_duplicata(item):
    # RN-007: recusado, `duplicata`, sem reembolso; recusado antes do limite
    # diário (etapa 7 < etapa 9) → `em_viagem` e `limite_diario` nulos (seção 4)
    assert (item["status"], item["motivo"]) == ("recusado", "duplicata")
    assert item["valor_reembolsado"] == 0
    assert (item["em_viagem"], item["limite_diario"]) == (None, None)


def test_rn007_d006_d007_segunda_e_duplicata(avaliar, despesa):
    """RN-007 (aceite): d-006 e d-007, mesmos data, categoria, fornecedor e
    54,90, ambas com nota → d-006 avaliada, d-007 `duplicata`."""
    saida = avaliar(
        despesa(id="d-006", fornecedor="Bistro Central", valor=Decimal("54.90")),
        despesa(id="d-007", fornecedor="Bistro Central", valor=Decimal("54.90")),
    )
    d006, d007 = saida["itens"]

    # 54,90 ≤ 60,00 (limite de alimentação) → aprovado com 54,90
    _avaliado(d006, Decimal("54.90"))
    _recusado_duplicata(d007)
    assert d007["valor_considerado"] == Decimal("54.90")


def test_rn007_id_descricao_e_nota_nao_entram_na_comparacao(avaliar, despesa):
    """RN-007: `id`, `descricao` e `tem_nota_fiscal` diferentes não impedem a
    duplicata (≤ 100,00, sem exigência de nota)."""
    saida = avaliar(
        despesa(id="a", descricao="almoço", valor=Decimal("40.00"),
                tem_nota_fiscal=True),
        despesa(id="b", descricao="almoço com equipe", valor=Decimal("40.00"),
                tem_nota_fiscal=False),
    )
    a, b = saida["itens"]

    _avaliado(a, Decimal("40.00"))
    _recusado_duplicata(b)


@pytest.mark.parametrize("com_nota_primeiro", [True, False])
def test_rn007_original_e_a_primeira_com_nota_em_qualquer_ordem(
    avaliar, despesa, com_nota_primeiro
):
    """RN-007 / AMB-010: valor ≤ 100,00, uma cópia sem nota e outra com nota →
    a com nota é a original e a sem nota `duplicata`, nas duas ordens."""
    com_nota = despesa(id="com", valor=Decimal("45.00"), tem_nota_fiscal=True)
    sem_nota = despesa(id="sem", valor=Decimal("45.00"), tem_nota_fiscal=False)
    ordem = [com_nota, sem_nota] if com_nota_primeiro else [sem_nota, com_nota]
    itens = {item["id"]: item for item in avaliar(*ordem)["itens"]}

    _avaliado(itens["com"], Decimal("45.00"))
    _recusado_duplicata(itens["sem"])


@pytest.mark.parametrize("sem_nota_primeiro", [True, False])
def test_rn007_relancamento_com_nota_acima_de_100_nao_e_duplicata(
    avaliar, despesa, sem_nota_primeiro
):
    """RN-007 / RN-008 / AMB-016: táxi 110,00 sem nota e o mesmo com nota → a
    sem nota sai na etapa 6 (`nota_fiscal_ausente`) e não participa da etapa 7;
    a com nota segue avaliada, nas duas ordens."""
    campos = dict(categoria="transporte_urbano", fornecedor="Táxi",
                  valor=Decimal("110.00"))
    sem_nota = despesa(id="sem", tem_nota_fiscal=False, **campos)
    com_nota = despesa(id="com", tem_nota_fiscal=True, **campos)
    ordem = [sem_nota, com_nota] if sem_nota_primeiro else [com_nota, sem_nota]
    itens = {item["id"]: item for item in avaliar(*ordem)["itens"]}

    assert (itens["sem"]["status"], itens["sem"]["motivo"]) == (
        "recusado", "nota_fiscal_ausente",
    )
    # min(110,00; 80,00) = 80,00 → parcial pelo limite de transporte
    com = itens["com"]
    assert (com["status"], com["motivo"]) == ("parcial", "limite_diario_excedido")
    assert com["valor_reembolsado"] == Decimal("80.00")


def test_rn007_nenhuma_com_nota_original_e_a_primeira(avaliar, despesa):
    """RN-007: nenhuma cópia com nota (≤ 100,00) → a primeira na ordem da
    entrada é a original."""
    saida = avaliar(
        despesa(id="a", valor=Decimal("30.00"), tem_nota_fiscal=False),
        despesa(id="b", valor=Decimal("30.00"), tem_nota_fiscal=False),
    )
    a, b = saida["itens"]

    _avaliado(a, Decimal("30.00"))
    _recusado_duplicata(b)


def test_rn007_duplicata_nao_consome_limite(avaliar, despesa):
    """RN-007 / AMB-016: alimentação 54,90 + duplicata 54,90 → a original
    `aprovado` com 54,90 (a duplicata não tira saldo); uma terceira despesa de
    5,10 no dia ainda cabe: 60,00 − 54,90 = 5,10."""
    saida = avaliar(
        despesa(id="dup", valor=Decimal("54.90"), tem_nota_fiscal=False),
        despesa(id="orig", valor=Decimal("54.90"), tem_nota_fiscal=True),
        despesa(id="outra", fornecedor="Cantina", valor=Decimal("5.10")),
    )
    dup, orig, outra = saida["itens"]

    _recusado_duplicata(dup)
    _avaliado(orig, Decimal("54.90"))
    _avaliado(outra, Decimal("5.10"))


def test_rn007_tres_copias_uma_original_duas_duplicatas(avaliar, despesa):
    """RN-007: três cópias com nota → a primeira original, as outras duas
    `duplicata`."""
    saida = avaliar(*(despesa(id=i, valor=Decimal("20.00")) for i in "abc"))
    a, b, c = saida["itens"]

    _avaliado(a, Decimal("20.00"))
    _recusado_duplicata(b)
    _recusado_duplicata(c)


def test_rn007_fornecedor_com_acento_e_o_mesmo(avaliar, despesa):
    """RN-007 / AMB-011 (aceite): "Bistro Central" e "Bistrô Central" → mesmo
    fornecedor normalizado (seção 5) → a segunda `duplicata`."""
    saida = avaliar(
        despesa(id="a", fornecedor="Bistro Central", valor=Decimal("54.90")),
        despesa(id="b", fornecedor="Bistrô Central", valor=Decimal("54.90")),
    )
    a, b = saida["itens"]

    _avaliado(a, Decimal("54.90"))
    _recusado_duplicata(b)


def test_rn007_categoria_comparada_normalizada(avaliar, despesa):
    """RN-007: "alimentacao" e "Alimentação" → mesma categoria normalizada
    (RN-006) → a segunda `duplicata`."""
    saida = avaliar(
        despesa(id="a", categoria="alimentacao", valor=Decimal("25.00")),
        despesa(id="b", categoria="Alimentação", valor=Decimal("25.00")),
    )
    a, b = saida["itens"]

    _avaliado(a, Decimal("25.00"))
    _recusado_duplicata(b)


def test_rn007_valor_comparado_e_o_considerado(avaliar, despesa):
    """RN-007 / RN-003: 25.004 e 25.00 → `valor_considerado` 25,00 nos dois →
    a segunda `duplicata`."""
    saida = avaliar(
        despesa(id="a", valor=Decimal("25.004")),
        despesa(id="b", valor=Decimal("25.00")),
    )
    a, b = saida["itens"]

    _avaliado(a, Decimal("25.00"))
    _recusado_duplicata(b)


@pytest.mark.parametrize(
    "diferenca",
    [
        {"data": "2026-07-04"},
        {"fornecedor": "Cantina"},
        {"valor": Decimal("20.01")},
        {"categoria": "transporte_urbano"},
    ],
    ids=["data", "fornecedor", "valor", "categoria"],
)
def test_rn007_quase_duplicata_nao_e_duplicata(avaliar, despesa, diferenca):
    """RN-007 / seção 10: comparação exata — data, fornecedor, valor (um
    centavo) ou categoria diferente → as duas avaliadas (20,00 + 20,01 ≤ 60,00,
    sem corte de limite)."""
    base = dict(fornecedor="Bistro Central", valor=Decimal("20.00"))
    saida = avaliar(despesa(id="a", **base), despesa(id="b", **{**base, **diferenca}))

    assert [item["status"] for item in saida["itens"]] == ["aprovado", "aprovado"]


def test_rn007_copias_sem_nota_acima_de_100_sao_ambas_nota_fiscal_ausente(
    avaliar, despesa
):
    """RN-007 / RN-008 / AMB-016 (seção 7, "Cópias idênticas sem nota acima de
    100"): duas de 150,00 sem nota → as duas saem na etapa 6
    (`nota_fiscal_ausente`), nenhuma chega à etapa 7."""
    saida = avaliar(
        despesa(id="a", valor=Decimal("150.00"), tem_nota_fiscal=False),
        despesa(id="b", valor=Decimal("150.00"), tem_nota_fiscal=False),
    )

    assert [(i["status"], i["motivo"]) for i in saida["itens"]] == [
        ("recusado", "nota_fiscal_ausente"), ("recusado", "nota_fiscal_ausente"),
    ]


def test_rn007_copia_invalida_nao_e_original(avaliar, despesa):
    """RN-007 / AMB-016: cópia anterior recusada na etapa 1 (`tem_nota_fiscal`
    `"sim"` → `entrada_invalida`) não é original de ninguém; a cópia válida
    seguinte segue avaliada."""
    saida = avaliar(
        despesa(id="a", valor=Decimal("40.00"), tem_nota_fiscal="sim"),
        despesa(id="b", valor=Decimal("40.00"), tem_nota_fiscal=True),
    )
    a, b = saida["itens"]

    assert a["motivo"] == "entrada_invalida"
    _avaliado(b, Decimal("40.00"))


def test_rn007_duplicata_entra_no_valor_solicitado(avaliar, despesa):
    """RN-007 / seção 4: duplicata tem `valor_considerado` > 0 e não é
    `entrada_invalida` → entra em `valor_solicitado`; solicitado 54,90 + 54,90
    = 109,80, reembolsado 54,90, glosado 54,90."""
    saida = avaliar(
        despesa(id="a", valor=Decimal("54.90")),
        despesa(id="b", valor=Decimal("54.90")),
    )

    assert saida["totais"] == {
        "valor_solicitado": Decimal("109.80"),
        "valor_reembolsado": Decimal("54.90"),
        "valor_glosado": Decimal("54.90"),
    }
