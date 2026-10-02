from datetime import date
from decimal import Decimal

import simplejson


def test_fixture_entrada_minima_e_json_valido(entrada, despesa):
    """Seção 4 da spec (Entrada): o construtor gera colaborador, periodo e despesas
    com os campos obrigatórios e os tipos da tabela, e o documento é JSON válido."""
    documento = entrada(despesas=[despesa()])

    texto = simplejson.dumps(documento, use_decimal=True)
    lido = simplejson.loads(texto, use_decimal=True)
    assert lido == documento

    assert isinstance(lido["colaborador"]["id"], str)
    assert isinstance(lido["colaborador"]["nome"], str)
    inicio = date.fromisoformat(lido["periodo"]["inicio"])
    fim = date.fromisoformat(lido["periodo"]["fim"])
    assert inicio <= fim
    assert isinstance(lido["despesas"], list)

    (item,) = lido["despesas"]
    for campo in ("id", "categoria", "fornecedor"):
        assert isinstance(item[campo], str) and item[campo].strip()
    assert inicio <= date.fromisoformat(item["data"]) <= fim
    assert isinstance(item["valor"], Decimal)
    assert isinstance(item["tem_nota_fiscal"], bool)


def test_construtores_aceitam_sobrescrita(entrada, despesa):
    """Plan seção 6: cada teste declara só o que importa ao caso."""
    assert despesa(valor=Decimal("72.50"))["valor"] == Decimal("72.50")
    assert entrada()["despesas"] == []
    assert despesa() is not despesa()
