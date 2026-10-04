"""Nota fiscal obrigatória acima de R$ 100: RN-008 / AMB-007 / AMB-008 (etapa 6
da seção 8).

Período padrão do `conftest`: 2026-07-01 a 2026-07-31.
"""

from decimal import Decimal

from conftest import construir_politica


def _recusado_nota_fiscal_ausente(item):
    # RN-008: recusado, `nota_fiscal_ausente`, sem reembolso; recusado antes do
    # limite diário (etapa 6 < etapa 9) → `em_viagem` e `limite_diario` nulos
    # (seção 4)
    assert (item["status"], item["motivo"]) == ("recusado", "nota_fiscal_ausente")
    assert item["valor_reembolsado"] == 0
    assert (item["em_viagem"], item["limite_diario"]) == (None, None)


def test_rn008_exatamente_100_sem_nota_segue(avaliar, despesa):
    """RN-008 / AMB-007: 100,00 sem nota não é "acima de" 100,00 → segue;
    transporte: min(100,00; 80,00) = 80,00, `parcial`."""
    (item,) = avaliar(
        despesa(
            categoria="transporte_urbano",
            valor=Decimal("100.00"),
            tem_nota_fiscal=False,
        )
    )["itens"]

    assert (item["status"], item["motivo"]) == ("parcial", "limite_diario_excedido")
    assert item["valor_reembolsado"] == Decimal("80.00")
    assert item["limite_diario"] == Decimal("80.00")


def test_rn008_um_centavo_acima_sem_nota_e_recusado(avaliar, despesa):
    """RN-008 / AMB-008: 100,01 > 100,00 sem nota → `nota_fiscal_ausente`,
    recusa inteira (não paga até 100,00)."""
    (item,) = avaliar(
        despesa(valor=Decimal("100.01"), tem_nota_fiscal=False)
    )["itens"]

    _recusado_nota_fiscal_ausente(item)
    assert item["valor_considerado"] == Decimal("100.01")


def test_rn008_um_centavo_acima_com_nota_segue(avaliar, despesa):
    """RN-008: 100,01 com nota → segue; hospedagem: 100,01 ≤ 250,00 →
    `aprovado`."""
    (item,) = avaliar(
        despesa(categoria="hospedagem", valor=Decimal("100.01"), tem_nota_fiscal=True)
    )["itens"]

    assert (item["status"], item["motivo"]) == ("aprovado", None)
    assert item["valor_reembolsado"] == Decimal("100.01")


def test_rn008_compara_valor_arredondado_abaixo_segue(avaliar, despesa):
    """RN-008 / AMB-008: compara o `valor_considerado`: 100,004 → 100,00
    (RN-003) sem nota → segue; hospedagem: 100,00 ≤ 250,00 → `aprovado`."""
    (item,) = avaliar(
        despesa(
            categoria="hospedagem", valor=Decimal("100.004"), tem_nota_fiscal=False
        )
    )["itens"]

    assert item["valor_considerado"] == Decimal("100.00")
    assert (item["status"], item["valor_reembolsado"]) == (
        "aprovado", Decimal("100.00"),
    )


def test_rn008_compara_valor_arredondado_acima_recusa(avaliar, despesa):
    """RN-008 / AMB-008: 100,005 → 100,01 (RN-003, metade para cima) sem nota
    → `nota_fiscal_ausente`."""
    (item,) = avaliar(
        despesa(
            categoria="hospedagem", valor=Decimal("100.005"), tem_nota_fiscal=False
        )
    )["itens"]

    assert item["valor_considerado"] == Decimal("100.01")
    _recusado_nota_fiscal_ausente(item)


def test_rn008_recusada_nao_consome_limite(avaliar, despesa):
    """RN-008 / seção 8: alimentação de 150,00 sem nota recusada na etapa 6 não
    consome limite; a seguinte de 50,00 no mesmo dia: min(50,00; 60,00) =
    50,00, `aprovado`."""
    saida = avaliar(
        despesa(id="a", valor=Decimal("150.00"), tem_nota_fiscal=False),
        despesa(id="b", valor=Decimal("50.00"), fornecedor="Cantina"),
    )
    item_a, item_b = saida["itens"]

    _recusado_nota_fiscal_ausente(item_a)
    assert (item_b["status"], item_b["valor_reembolsado"]) == (
        "aprovado", Decimal("50.00"),
    )
    # seção 4: solicitado = 150,00 + 50,00 = 200,00; reembolsado 50,00;
    # glosado 150,00
    assert saida["totais"] == {
        "valor_solicitado": Decimal("200.00"),
        "valor_reembolsado": Decimal("50.00"),
        "valor_glosado": Decimal("150.00"),
    }


def test_rn008_comparacao_antes_do_limite(avaliar, despesa):
    """RN-008 / AMB-008: compara o valor individual antes do limite: transporte
    de 110,00 sem nota é recusado, embora o limite (80,00) o cortaria abaixo de
    100,00."""
    (item,) = avaliar(
        despesa(
            categoria="transporte_urbano",
            valor=Decimal("110.00"),
            tem_nota_fiscal=False,
        )
    )["itens"]

    _recusado_nota_fiscal_ausente(item)


def test_rn008_categoria_vem_antes_da_nota(avaliar, despesa):
    """RN-008 / RN-006: categoria desconhecida acima de 100,00 sem nota →
    `categoria_fora_da_politica` (etapa 5 vem antes da etapa 6)."""
    (item,) = avaliar(
        despesa(categoria="coworking", valor=Decimal("150.00"), tem_nota_fiscal=False)
    )["itens"]

    assert (item["status"], item["motivo"]) == (
        "recusado", "categoria_fora_da_politica",
    )


def test_rn008_periodo_vem_antes_da_nota(avaliar, despesa):
    """RN-008 / RN-005: fora do período acima de 100,00 sem nota →
    `fora_do_periodo` (etapa 4 vem antes da etapa 6)."""
    (item,) = avaliar(
        despesa(data="2026-04-15", valor=Decimal("150.00"), tem_nota_fiscal=False)
    )["itens"]

    assert (item["status"], item["motivo"]) == ("recusado", "fora_do_periodo")



def _politica_com_minimo_50():
    return construir_politica(nota_fiscal_obrigatoria_acima_de=Decimal("50.00"))


def test_rn008_minimo_vem_do_arquivo_de_politica(avaliar, despesa):
    """RN-008 / AMB-027 (aceite): política com mínimo 50,00 → 50,01 sem nota é
    `nota_fiscal_ausente` (com o 100,00 da v4, seguiria)."""
    (item,) = avaliar(
        despesa(valor=Decimal("50.01"), tem_nota_fiscal=False),
        politica=_politica_com_minimo_50(),
    )["itens"]

    # 50,01 > 50,00 sem nota
    _recusado_nota_fiscal_ausente(item)


def test_rn008_exatamente_o_minimo_do_arquivo_sem_nota_segue(avaliar, despesa):
    """RN-008 / AMB-007 / AMB-027: com mínimo 50,00, 50,00 sem nota não é
    "acima de" → segue; 50,00 ≤ 60,00 → `aprovado`."""
    (item,) = avaliar(
        despesa(valor=Decimal("50.00"), tem_nota_fiscal=False),
        politica=_politica_com_minimo_50(),
    )["itens"]

    assert (item["status"], item["valor_reembolsado"]) == ("aprovado", Decimal("50.00"))
