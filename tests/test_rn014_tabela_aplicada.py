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
