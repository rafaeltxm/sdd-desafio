"""Tabela aplicada por centro de custo: RN-014, AMB-020.

Salvo indicação, a política é a `politica-v4.json` transcrita
(`construir_politica`).
"""

from decimal import Decimal

import pytest
import simplejson

from conftest import construir_politica
from reembolso.politica import ler_politica, tabela_aplicada


def _politica(**sobrescritas):
    documento = construir_politica(**sobrescritas)
    return ler_politica(simplejson.dumps(documento, use_decimal=True).encode())


def test_rn014_centro_de_custo_da_tabela_usa_a_tabela_dele():
    """RN-014: `"CC-COMERCIAL"` é chave de `centros_custo` → tabela dele."""
    tabela = tabela_aplicada(_politica(), "CC-COMERCIAL")

    assert tabela.nome == "CC-COMERCIAL"
    # limites da tabela CC-COMERCIAL da v4, não os do padrao
    assert tabela.limites == {
        "alimentacao": Decimal("90.00"),
        "transporte_urbano": Decimal("150.00"),
        "hospedagem": Decimal("400.00"),
        "representacao": Decimal("300.00"),
    }


@pytest.mark.parametrize(
    "centro_custo",
    [
        pytest.param("CC-SUPORTE-N2", id="fora-da-tabela"),
        pytest.param("cc-adm", id="minusculas"),
        pytest.param("CC-ADM ", id="espaco-no-fim"),
        pytest.param(None, id="nulo-ou-ausente"),
        pytest.param("", id="vazio"),
        pytest.param("  ", id="so-espacos"),
    ],
)
def test_rn014_centro_de_custo_nao_informado_ou_fora_da_tabela_usa_o_padrao(
    centro_custo,
):
    """RN-014 / AMB-020: comparação exata; não informado ou sem chave → padrao."""
    tabela = tabela_aplicada(_politica(), centro_custo)

    assert tabela.nome == "padrao"
    # tabela padrao da v4
    assert tabela.limites == {
        "alimentacao": Decimal("60.00"),
        "transporte_urbano": Decimal("80.00"),
        "hospedagem": Decimal("250.00"),
    }


@pytest.mark.parametrize("centros_custo", [None, "ausente"])
def test_rn014_politica_sem_centros_custo_usa_o_padrao_para_todos(centros_custo):
    """RN-014: arquivo sem `centros_custo` → `padrao` para qualquer centro."""
    documento = construir_politica(centros_custo=centros_custo)
    if centros_custo == "ausente":
        del documento["centros_custo"]
    politica = ler_politica(simplejson.dumps(documento, use_decimal=True).encode())

    for centro_custo in ("CC-COMERCIAL", "CC-ADM", None):
        assert tabela_aplicada(politica, centro_custo).nome == "padrao"


def test_rn014_tabela_fechada_nao_completa_com_o_padrao():
    """RN-014 / AMB-020: `CC-ADM` não tem `hospedagem`, mesmo havendo no padrao."""
    politica = _politica()
    assert "hospedagem" in tabela_aplicada(politica, None).limites

    tabela = tabela_aplicada(politica, "CC-ADM")

    assert tabela.nome == "CC-ADM"
    # só as duas categorias escritas para CC-ADM na v4
    assert tabela.limites == {
        "alimentacao": Decimal("45.00"),
        "transporte_urbano": Decimal("60.00"),
    }


def test_rn014_chave_com_espaco_no_arquivo_e_comparada_como_escrita():
    """RN-014: comparação caractere a caractere, sem tirar espaços de nenhum lado."""
    padrao = construir_politica()["padrao"]
    politica = _politica(centros_custo={"CC-X ": padrao})

    # "CC-X " é a chave exata → tabela dela, com o nome como escrito no arquivo
    assert tabela_aplicada(politica, "CC-X ").nome == "CC-X "
    # "CC-X" não é igual a "CC-X " → padrao
    assert tabela_aplicada(politica, "CC-X").nome == "padrao"


# --- ponta a ponta: o motor usa a tabela aplicada (Aceite da RN-014) ---


def _resumo(item):
    return (item["limite_diario"], item["valor_reembolsado"], item["status"])


def test_rn014_cc_comercial_alimentacao_85_tem_limite_90(avaliar, despesa):
    """RN-014 (aceite): `"CC-COMERCIAL"` → tabela dele; alimentação 85,00 →
    limite 90,00, `aprovado`."""
    saida = avaliar(despesa(valor=Decimal("85.00")), centro_custo="CC-COMERCIAL")

    assert saida["politica"]["tabela_aplicada"] == "CC-COMERCIAL"
    (item,) = saida["itens"]
    # 85,00 ≤ 90,00 (alimentação do CC-COMERCIAL) → aprovado com 85,00
    assert _resumo(item) == (Decimal("90.00"), Decimal("85.00"), "aprovado")


def test_rn014_cc_fora_da_tabela_alimentacao_65_tem_limite_60(avaliar, despesa):
    """RN-014 (aceite): `"CC-SUPORTE-N2"` não é chave → `padrao`; alimentação
    65,00 → limite 60,00, `parcial` com 60,00."""
    saida = avaliar(despesa(valor=Decimal("65.00")), centro_custo="CC-SUPORTE-N2")

    assert saida["politica"]["tabela_aplicada"] == "padrao"
    (item,) = saida["itens"]
    # min(65,00; 60,00) = 60,00 → parcial
    assert _resumo(item) == (Decimal("60.00"), Decimal("60.00"), "parcial")
    assert item["motivo"] == "limite_diario_excedido"


def test_rn014_sem_centro_custo_usa_o_padrao(avaliar, despesa):
    """RN-014 (aceite): sem `centro_custo` → `padrao` (alimentação 60,00)."""
    saida = avaliar(despesa(valor=Decimal("65.00")))

    assert saida["politica"]["tabela_aplicada"] == "padrao"
    # min(65,00; 60,00) = 60,00
    assert _resumo(saida["itens"][0]) == (
        Decimal("60.00"), Decimal("60.00"), "parcial",
    )


def test_rn014_cc_com_grafia_diferente_usa_o_padrao(avaliar, despesa):
    """RN-014 (aceite): `"cc-adm"` não é `CC-ADM` → `padrao`; alimentação 50,00
    → limite 60,00 (não 45,00 do CC-ADM), `aprovado`."""
    saida = avaliar(despesa(valor=Decimal("50.00")), centro_custo="cc-adm")

    assert saida["politica"]["tabela_aplicada"] == "padrao"
    # 50,00 ≤ 60,00 → aprovado
    assert _resumo(saida["itens"][0]) == (
        Decimal("60.00"), Decimal("50.00"), "aprovado",
    )


def test_rn014_cc_adm_hospedagem_e_fora_da_politica(avaliar, despesa):
    """RN-014 / AMB-020 (aceite): `"CC-ADM"` com hospedagem de 300,00 com nota →
    `categoria_fora_da_politica` (não 250,00 do `padrao`: tabela fechada)."""
    saida = avaliar(
        despesa(categoria="hospedagem", valor=Decimal("300.00"), tem_nota_fiscal=True),
        centro_custo="CC-ADM",
    )

    assert saida["politica"]["tabela_aplicada"] == "CC-ADM"
    (item,) = saida["itens"]
    assert (item["status"], item["motivo"], item["valor_reembolsado"]) == (
        "recusado", "categoria_fora_da_politica", Decimal("0"),
    )
    assert (item["em_viagem"], item["limite_diario"]) == (None, None)


def test_rn014_politica_na_saida_copia_versao_e_vigencia(avaliar, despesa):
    """RN-014 / AMB-029 / seção 4: `politica` = `versao` e `vigencia` do arquivo
    e `tabela_aplicada` como escrita no arquivo de política."""
    saida = avaliar(despesa(), centro_custo="CC-COMERCIAL")

    assert saida["politica"] == {
        "versao": "v4", "vigencia": "2026-07-01", "tabela_aplicada": "CC-COMERCIAL",
    }


def test_rn014_politica_sem_versao_nem_vigencia_sai_nula(avaliar, despesa):
    """RN-016 / AMB-029: política sem `versao` nem `vigencia` → nulas na saída;
    o cálculo não muda (10,00 ≤ 60,00 → aprovado)."""
    politica = construir_politica()
    del politica["versao"], politica["vigencia"]

    saida = avaliar(despesa(), politica=politica)

    assert saida["politica"] == {
        "versao": None, "vigencia": None, "tabela_aplicada": "padrao",
    }
    assert saida["itens"][0]["status"] == "aprovado"


@pytest.mark.parametrize(
    ("centro_custo", "esperado"),
    [
        pytest.param("CC-COMERCIAL", "CC-COMERCIAL", id="texto"),
        pytest.param("cc-adm", "cc-adm", id="texto-fora-da-tabela"),
        pytest.param("  ", "  ", id="so-espacos"),
        pytest.param("", "", id="vazio"),
        pytest.param(None, None, id="nulo"),
    ],
)
def test_rn014_colaborador_centro_custo_copiado_na_saida(
    avaliar, despesa, centro_custo, esperado
):
    """Seção 4: `colaborador.centro_custo` copiado se texto (inclusive só com
    espaços); nulo se nulo."""
    saida = avaliar(despesa(), centro_custo=centro_custo)

    assert saida["colaborador"] == {
        "id": "c-1", "nome": "Ana", "centro_custo": esperado,
    }


def test_rn014_colaborador_sem_centro_custo_sai_nulo(avaliar, despesa):
    """Seção 4: `colaborador.centro_custo` ausente → nulo na saída."""
    saida = avaliar(despesa())

    assert saida["colaborador"]["centro_custo"] is None
