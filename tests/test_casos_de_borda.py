"""Casos de borda da seção 7 da spec: um caso por linha, `id` = coluna "Caso"."""

from decimal import Decimal

import pytest
import simplejson

from conftest import construir_despesa as despesa
from conftest import construir_entrada


def _json(*despesas, **cabecalho):
    """Despesas numa entrada mínima válida → texto JSON."""
    return simplejson.dumps(construir_entrada(despesas, **cabecalho), use_decimal=True)


def _sem_nota(**campos):
    documento = despesa(**campos)
    del documento["tem_nota_fiscal"]
    return documento


def _recusado_entrada_invalida(item):
    # RN-002: recusado, `entrada_invalida`, nulos, sem reembolso
    assert (item["status"], item["motivo"]) == ("recusado", "entrada_invalida")
    assert item["valor_considerado"] is None
    assert item["valor_reembolsado"] == 0
    assert (item["em_viagem"], item["limite_diario"]) == (None, None)


def _fora_dos_totais(saida):
    assert saida["totais"] == {
        "valor_solicitado": 0, "valor_reembolsado": 0, "valor_glosado": 0,
    }


def _caso_duas_alimentacoes_acima_do_limite(saida):
    # 72,50 + 38,00 > 60,00 → 60,00 parcial e 0 recusado
    a, b = saida["itens"]
    assert (a["valor_reembolsado"], a["status"]) == (Decimal("60.00"), "parcial")
    assert (b["valor_reembolsado"], b["status"], b["motivo"]) == (
        Decimal("0"), "recusado", "limite_diario_excedido",
    )


def _caso_valor_no_limite_diario(saida):
    # 60,00 = limite → aprovado com 60,00
    (item,) = saida["itens"]
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("60.00"), "aprovado")


def _caso_um_centavo_acima_do_limite_diario(saida):
    # min(60,01; 60,00) = 60,00 → parcial
    (item,) = saida["itens"]
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("60.00"), "parcial")


def _caso_duas_hospedagens_na_mesma_data(saida):
    # 200,00 aprovado; min(100,00; 250,00 − 200,00) = 50,00 parcial
    a, b = saida["itens"]
    assert (a["valor_reembolsado"], a["status"]) == (Decimal("200.00"), "aprovado")
    assert (b["valor_reembolsado"], b["status"]) == (Decimal("50.00"), "parcial")


def _caso_tres_casas_decimais(saida):
    (item,) = saida["itens"]
    assert item["valor_informado"] == Decimal("33.333")
    assert item["valor_considerado"] == Decimal("33.33")


def _caso_arredondamento_da_metade(saida):
    (item,) = saida["itens"]
    assert item["valor_considerado"] == Decimal("10.01")


def _caso_lista_vazia(saida):
    assert saida["itens"] == []
    assert saida["totais"] == {
        "valor_solicitado": 0, "valor_reembolsado": 0, "valor_glosado": 0,
    }


def _caso_despesa_em_sabado(saida):
    # 18/07/2026 é sábado; avaliada normalmente: 47,20 ≤ 60,00 → aprovado
    (item,) = saida["itens"]
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("47.20"), "aprovado")


def _caso_campo_obrigatorio_ausente(saida):
    # sem `tem_nota_fiscal` → inválida, fora dos totais; a outra segue: 50,00 aprovado
    invalida, valida = saida["itens"]
    _recusado_entrada_invalida(invalida)
    assert (valida["status"], valida["valor_reembolsado"]) == (
        "aprovado", Decimal("50.00"),
    )
    assert saida["totais"]["valor_solicitado"] == Decimal("50.00")


def _caso_elemento_que_nao_e_objeto(saida):
    (item,) = saida["itens"]
    _recusado_entrada_invalida(item)
    assert (item["id"], item["data"]) == (None, None)


def _caso_campo_extra(saida):
    # `noites` ignorado: uma diária, min(480,00; 250,00) = 250,00 → parcial
    (item,) = saida["itens"]
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("250.00"), "parcial")


def _caso_campo_com_tipo_errado(saida):
    (item,) = saida["itens"]
    _recusado_entrada_invalida(item)
    assert item["id"] is None


def _caso_texto_vazio_em_campo_obrigatorio(saida):
    # `fornecedor` "", "   " e "-"
    assert len(saida["itens"]) == 3
    for item in saida["itens"]:
        _recusado_entrada_invalida(item)


def _caso_competencia_nao_textual(saida):
    assert saida["periodo"]["competencia"] is None
    (item,) = saida["itens"]
    # 10,00 ≤ 60,00 → aprovado
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("10.00"), "aprovado")


def _caso_texto_com_escapes_validos(saida):
    (item,) = saida["itens"]
    assert item["data"] == "2026-07-03"
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("10.00"), "aprovado")


def _caso_categoria_reconhecivel_em_despesa_invalida(saida):
    (item,) = saida["itens"]
    _recusado_entrada_invalida(item)
    assert item["categoria"] == "alimentacao"


def _caso_valor_a_partir_de_um_bilhao(saida):
    (item,) = saida["itens"]
    _recusado_entrada_invalida(item)
    assert item["valor_informado"] == Decimal("1000000000")
    _fora_dos_totais(saida)


def _caso_abaixo_do_teto_segue(saida):
    # arredonda para 1.000.000.000,00; hospedagem: min(…; 250,00) = 250,00 → parcial
    (item,) = saida["itens"]
    assert item["valor_considerado"] == Decimal("1000000000.00")
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("250.00"), "parcial")


def _caso_valor_negativo_gigante(saida):
    (item,) = saida["itens"]
    _recusado_entrada_invalida(item)


def _caso_valor_com_expoente_enorme(saida):
    (item,) = saida["itens"]
    _recusado_entrada_invalida(item)
    assert item["valor_informado"] == Decimal("1E+999999")


CASOS = [
    pytest.param(
        _json(despesa(id="a", valor=Decimal("72.50")),
              despesa(id="b", valor=Decimal("38.00"), fornecedor="Cantina")),
        _caso_duas_alimentacoes_acima_do_limite,
        id="Duas alimentações no mesmo dia somando mais que o limite",
    ),
    pytest.param(
        _json(despesa(valor=Decimal("60.00"))),
        _caso_valor_no_limite_diario,
        id="Valor exatamente no limite diário",
    ),
    pytest.param(
        _json(despesa(valor=Decimal("60.01"))),
        _caso_um_centavo_acima_do_limite_diario,
        id="Um centavo acima do limite diário",
    ),
    pytest.param(
        _json(despesa(id="h1", categoria="hospedagem", valor=Decimal("200.00"),
                      fornecedor="Hotel A"),
              despesa(id="h2", categoria="hospedagem", valor=Decimal("100.00"),
                      fornecedor="Hotel B")),
        _caso_duas_hospedagens_na_mesma_data,
        id="Duas hospedagens na mesma data",
    ),
    pytest.param(
        _json(despesa(valor=Decimal("33.333"))),
        _caso_tres_casas_decimais,
        id="Três casas decimais",
    ),
    pytest.param(
        _json(despesa(valor=Decimal("10.005"))),
        _caso_arredondamento_da_metade,
        id="Arredondamento da metade",
    ),
    pytest.param(_json(), _caso_lista_vazia, id="Lista de despesas vazia"),
    pytest.param(
        _json(despesa(data="2026-07-18", valor=Decimal("47.20"))),
        _caso_despesa_em_sabado,
        id="Despesa em sábado",
    ),
    pytest.param(
        _json(_sem_nota(id="a", valor=Decimal("33.333")),
              despesa(id="b", valor=Decimal("50.00"))),
        _caso_campo_obrigatorio_ausente,
        id="Campo obrigatório ausente",
    ),
    pytest.param(
        _json(None), _caso_elemento_que_nao_e_objeto, id="Elemento que não é objeto"
    ),
    pytest.param(
        _json(despesa(categoria="hospedagem", valor=Decimal("480.00"), noites=2)),
        _caso_campo_extra,
        id="Campo extra",
    ),
    pytest.param(
        _json(despesa(id=17)), _caso_campo_com_tipo_errado, id="Campo com tipo errado"
    ),
    pytest.param(
        _json(despesa(id="a", fornecedor=""), despesa(id="b", fornecedor="   "),
              despesa(id="c", fornecedor="-")),
        _caso_texto_vazio_em_campo_obrigatorio,
        id="Texto vazio em campo obrigatório",
    ),
    pytest.param(
        _json(despesa(), periodo={"competencia": 202607, "inicio": "2026-07-01",
                                  "fim": "2026-07-31"}),
        _caso_competencia_nao_textual,
        id="Competência não textual",
    ),
    pytest.param(
        _json(despesa(data="DATA")).replace('"DATA"', r'"2026\u002d07\u002d03"'),
        _caso_texto_com_escapes_validos,
        id="Texto com escapes válidos",
    ),
    pytest.param(
        _json(_sem_nota(categoria="ALIMENTACAO")),
        _caso_categoria_reconhecivel_em_despesa_invalida,
        id="Categoria reconhecível em despesa inválida",
    ),
    pytest.param(
        _json(despesa(valor=Decimal("1000000000"))),
        _caso_valor_a_partir_de_um_bilhao,
        id="Valor a partir de um bilhão",
    ),
    pytest.param(
        _json(despesa(categoria="hospedagem", valor=Decimal("999999999.995"))),
        _caso_abaixo_do_teto_segue,
        id="Valor logo abaixo de um bilhão",
    ),
    pytest.param(
        _json(despesa(valor=Decimal("1"))).replace('"valor": 1', '"valor": -1e12'),
        _caso_valor_negativo_gigante,
        id="Valor negativo gigante",
    ),
    pytest.param(
        _json(despesa(valor=Decimal("1"))).replace('"valor": 1', '"valor": 1e999999'),
        _caso_valor_com_expoente_enorme,
        id="Valor com expoente enorme",
    ),
    pytest.param(
        _json(despesa(categoria="hospedagem",
                      valor=Decimal("999999999.99999999999"))),
        _caso_abaixo_do_teto_segue,
        id="Muitas casas logo abaixo do teto",
    ),
]


@pytest.mark.parametrize(("texto", "verificar"), CASOS)
def test_caso_de_borda(processar, texto, verificar):
    """Seção 7 da spec: comportamento esperado de cada caso."""
    verificar(processar(texto))
