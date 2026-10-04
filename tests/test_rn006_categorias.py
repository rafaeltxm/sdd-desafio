"""Categorias da política: RN-006 / AMB-011 / AMB-012 (etapa 5 da seção 8).

Período padrão do `conftest`: 2026-07-01 a 2026-07-31.
"""

from decimal import Decimal

import pytest
import simplejson

from conftest import construir_politica
from reembolso.politica import categoria_de_saida, ler_politica, tabela_aplicada


def _recusado_fora_da_politica(item):
    # RN-006: recusado, `categoria_fora_da_politica`, sem reembolso; recusado
    # antes do limite diário (etapa 5 < etapa 9) → `em_viagem` e `limite_diario`
    # nulos (seção 4)
    assert (item["status"], item["motivo"]) == (
        "recusado", "categoria_fora_da_politica",
    )
    assert item["valor_reembolsado"] == 0
    assert (item["em_viagem"], item["limite_diario"]) == (None, None)


@pytest.mark.parametrize(
    "categoria",
    [
        pytest.param("ALIMENTACAO", id="maiusculas"),
        pytest.param(" Alimentacao ", id="espacos-nas-pontas"),
        pytest.param("alimentacao\t", id="tabulacao-no-fim"),
        pytest.param("alimentação", id="acento"),
    ],
)
def test_rn006_grafias_de_alimentacao_sao_reconhecidas(avaliar, despesa, categoria):
    """RN-006 / AMB-011: grafias de alimentação → `alimentacao` na saída e
    limite de alimentação: 72,50 → min(72,50; 60,00) = 60,00, `parcial`."""
    (item,) = avaliar(despesa(categoria=categoria, valor=Decimal("72.50")))["itens"]

    assert item["categoria"] == "alimentacao"
    assert item["limite_diario"] == Decimal("60.00")
    assert (item["status"], item["motivo"]) == ("parcial", "limite_diario_excedido")
    assert item["valor_reembolsado"] == Decimal("60.00")


@pytest.mark.parametrize(
    "categoria",
    [
        pytest.param("Transporte Urbano", id="espaco"),
        pytest.param("transporte-urbano", id="hifen"),
    ],
)
def test_rn006_grafias_de_transporte_urbano_sao_reconhecidas(
    avaliar, despesa, categoria
):
    """RN-006 / AMB-011: separador diferente → `transporte_urbano` na saída e
    limite de transporte: 90,00 → min(90,00; 80,00) = 80,00, `parcial`."""
    (item,) = avaliar(despesa(categoria=categoria, valor=Decimal("90.00")))["itens"]

    assert item["categoria"] == "transporte_urbano"
    assert item["limite_diario"] == Decimal("80.00")
    assert (item["status"], item["motivo"]) == ("parcial", "limite_diario_excedido")
    assert item["valor_reembolsado"] == Decimal("80.00")


def test_rn006_hospedagem_e_reconhecida(avaliar, despesa):
    """RN-006: `HOSPEDAGEM` → `hospedagem`, limite 250,00; 200,00 → `aprovado`."""
    (item,) = avaliar(despesa(categoria="HOSPEDAGEM", valor=Decimal("200.00")))[
        "itens"
    ]

    assert item["categoria"] == "hospedagem"
    assert item["limite_diario"] == Decimal("250.00")
    assert (item["status"], item["valor_reembolsado"]) == (
        "aprovado", Decimal("200.00"),
    )


def test_rn006_categoria_desconhecida_e_recusada_e_aparece(avaliar, despesa):
    """RN-006 / AMB-012: `coworking` → `categoria_fora_da_politica`; o item
    aparece na saída (não é omitido), com `categoria` como veio."""
    outra = despesa(id="b", valor=Decimal("30.00"), fornecedor="Cantina")
    saida = avaliar(
        despesa(id="a", categoria="coworking", valor=Decimal("45.00")), outra
    )

    # RN-001: 2 despesas → 2 itens, mesma ordem
    item, item_b = saida["itens"]
    assert (item["id"], item_b["id"]) == ("a", "b")
    _recusado_fora_da_politica(item)
    assert item["categoria"] == "coworking"
    assert item["valor_considerado"] == Decimal("45.00")
    # a outra despesa segue: 30,00 ≤ 60,00 → aprovado
    assert (item_b["status"], item_b["valor_reembolsado"]) == (
        "aprovado", Decimal("30.00"),
    )
    # seção 4: solicitado = 45,00 + 30,00 = 75,00 (considerado > 0, não
    # `entrada_invalida`); reembolsado 0 + 30,00 = 30,00; glosado 45,00
    assert saida["totais"] == {
        "valor_solicitado": Decimal("75.00"),
        "valor_reembolsado": Decimal("30.00"),
        "valor_glosado": Decimal("45.00"),
    }


def test_rn006_categoria_desconhecida_sai_como_veio(avaliar, despesa):
    """RN-006 / seção 4: categoria não reconhecida sai como veio, sem
    normalização (`" Coworking "` continua `" Coworking "`)."""
    (item,) = avaliar(despesa(categoria=" Coworking "))["itens"]

    _recusado_fora_da_politica(item)
    assert item["categoria"] == " Coworking "


def test_rn006_periodo_vem_antes_da_categoria(avaliar, despesa):
    """RN-006 / RN-005: categoria desconhecida fora do período →
    `fora_do_periodo` (etapa 4 vem antes da etapa 5)."""
    (item,) = avaliar(despesa(data="2026-04-15", categoria="coworking"))["itens"]

    assert (item["status"], item["motivo"]) == ("recusado", "fora_do_periodo")


def test_rn006_valor_invalido_vem_antes_da_categoria(avaliar, despesa):
    """RN-006 / RN-004: categoria desconhecida com valor ≤ 0 → `valor_invalido`
    (etapa 3 vem antes da etapa 5)."""
    (item,) = avaliar(despesa(categoria="coworking", valor=Decimal("0")))["itens"]

    assert (item["status"], item["motivo"]) == ("recusado", "valor_invalido")


@pytest.mark.parametrize(
    "categoria",
    [
        # seção 10: espaço de largura zero é separador → `ali_mentacao`
        pytest.param("ali\u200bmentacao", id="largura-zero"),
        # seção 10: largura total não é desfeita pela normalização
        pytest.param("ＡＬＩＭＥＮＴＡＣＡＯ", id="largura-total"),
    ],
)
def test_rn006_riscos_aceitos_saem_fora_da_politica(avaliar, despesa, categoria):
    """RN-006 / seção 10 (riscos aceitos): `"ali\\u200bmentacao"` e categoria em
    largura total → `categoria_fora_da_politica`, `categoria` como veio."""
    (item,) = avaliar(despesa(categoria=categoria))["itens"]

    _recusado_fora_da_politica(item)
    assert item["categoria"] == categoria


# --- categoria_de_saida (seção 4, `itens[].categoria`) ---


def _tabela(centro_custo=None):
    documento = construir_politica()
    politica = ler_politica(simplejson.dumps(documento, use_decimal=True).encode())
    return tabela_aplicada(politica, centro_custo)


@pytest.mark.parametrize(
    ("texto", "centro_custo", "esperado"),
    [
        # normaliza para `alimentacao`, presente no padrao
        pytest.param("ALIMENTACAO", None, "alimentacao", id="reconhecida"),
        # presente em CC-ENG-PLATAFORMA com limite 0: ainda reconhecida
        pytest.param(
            "hospedagem", "CC-ENG-PLATAFORMA", "hospedagem", id="limite-zero"
        ),
        # grafia não normalizada: o limite 0 não tira a categoria da tabela
        pytest.param(
            "HOSPEDAGEM", "CC-ENG-PLATAFORMA", "hospedagem", id="limite-zero-grafia"
        ),
        # `representacao` só existe em CC-COMERCIAL: no padrao sai como veio
        pytest.param(
            "representacao", None, "representacao", id="de-outra-tabela"
        ),
        pytest.param(
            "Representacao", None, "Representacao", id="de-outra-tabela-como-veio"
        ),
        pytest.param("Coworking", None, "Coworking", id="fora-de-todas"),
        pytest.param(17, None, None, id="nao-texto"),
        pytest.param(None, None, None, id="ausente"),
    ],
)
def test_rn006_categoria_de_saida(texto, centro_custo, esperado):
    """RN-006 / AMB-021 / seção 4: normalizada se presente na tabela aplicada
    (inclusive com limite 0); senão como veio, se texto; senão nula."""
    assert categoria_de_saida(texto, _tabela(centro_custo)) == esperado


# --- categorias da tabela aplicada (RN-006 / RN-014 / AMB-020 / AMB-021) ---


def test_rn006_representacao_no_padrao_e_fora_da_politica(avaliar, despesa):
    """RN-006 / AMB-020 (aceite): com o `padrao`, `representacao` →
    `categoria_fora_da_politica` (existe só no CC-COMERCIAL); sai como veio."""
    (item,) = avaliar(despesa(categoria="representacao"))["itens"]

    _recusado_fora_da_politica(item)
    assert item["categoria"] == "representacao"


def test_rn006_representacao_no_cc_comercial_e_reconhecida(avaliar, despesa):
    """RN-006 / AMB-017 (aceite): com `CC-COMERCIAL`, `Representação` →
    `representacao`, limite 300,00; 190,00 com nota → `aprovado`."""
    (item,) = avaliar(
        despesa(categoria="Representação", valor=Decimal("190.00")),
        centro_custo="CC-COMERCIAL",
    )["itens"]

    assert item["categoria"] == "representacao"
    # 190,00 ≤ 300,00 → aprovado
    assert (item["limite_diario"], item["valor_reembolsado"], item["status"]) == (
        Decimal("300.00"), Decimal("190.00"), "aprovado",
    )


def test_rn006_hospedagem_no_cc_adm_e_fora_da_politica(avaliar, despesa):
    """RN-006 / AMB-020 (aceite): com `CC-ADM`, `hospedagem` (ausente da tabela)
    → `categoria_fora_da_politica`; sai como veio."""
    (item,) = avaliar(
        despesa(categoria="Hospedagem", valor=Decimal("90.00")),
        centro_custo="CC-ADM",
    )["itens"]

    _recusado_fora_da_politica(item)
    # ausente da tabela aplicada → como veio
    assert item["categoria"] == "Hospedagem"


def test_rn006_hospedagem_com_limite_zero_e_fora_da_politica(avaliar, despesa):
    """RN-006 / AMB-021 (aceite): com `CC-ENG-PLATAFORMA`, `hospedagem` tem
    limite 0 → `categoria_fora_da_politica` (etapa 5, não limite diário); está na
    tabela, então sai normalizada."""
    (item,) = avaliar(
        despesa(categoria="HOSPEDAGEM", valor=Decimal("90.00")),
        centro_custo="CC-ENG-PLATAFORMA",
    )["itens"]

    _recusado_fora_da_politica(item)
    assert item["categoria"] == "hospedagem"


def test_rn006_limite_zero_vem_antes_da_nota(avaliar, despesa):
    """RN-006 / AMB-021 / seção 8: hospedagem com limite 0, acima de 100,00 sem
    nota → `categoria_fora_da_politica` (etapa 5 antes da 6)."""
    (item,) = avaliar(
        despesa(categoria="hospedagem", valor=Decimal("690.00"),
                tem_nota_fiscal=False),
        centro_custo="CC-ENG-PLATAFORMA",
    )["itens"]

    _recusado_fora_da_politica(item)


@pytest.mark.parametrize(
    ("categoria", "centro_custo", "esperado"),
    [
        # `representacao` está no CC-COMERCIAL → normalizada
        pytest.param("Representacao", "CC-COMERCIAL", "representacao",
                     id="reconhecida-no-cc"),
        # não está no padrao → como veio
        pytest.param("Representacao", None, "Representacao", id="fora-do-padrao"),
        # limite 0 ainda é presença na tabela → normalizada
        pytest.param("HOSPEDAGEM", "CC-ENG-PLATAFORMA", "hospedagem",
                     id="limite-zero"),
        # não é texto → nula
        pytest.param(17, "CC-COMERCIAL", None, id="nao-texto"),
    ],
)
def test_rn006_categoria_de_despesa_invalida_depende_da_tabela_aplicada(
    avaliar, despesa, categoria, centro_custo, esperado
):
    """RN-006 / RN-002 / seção 4: despesa inválida (sem `tem_nota_fiscal`) sai com
    a categoria normalizada se presente na tabela aplicada; senão como veio."""
    documento = despesa(categoria=categoria)
    del documento["tem_nota_fiscal"]

    (item,) = avaliar(documento, centro_custo=centro_custo)["itens"]

    assert (item["status"], item["motivo"]) == ("recusado", "entrada_invalida")
    assert item["categoria"] == esperado
