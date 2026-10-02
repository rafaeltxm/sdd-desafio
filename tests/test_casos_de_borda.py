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


def _recusado_valor_invalido(item):
    # RN-004: recusado, `valor_invalido`, sem reembolso, nulos de antes do limite
    assert (item["status"], item["motivo"]) == ("recusado", "valor_invalido")
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


def _caso_estorno(saida):
    # -45,00 → `valor_invalido`; não altera o dia: 50,00 aprovado; saldo 10,00;
    # min(30,00; 10,00) = 10,00 parcial
    a, estorno, b = saida["itens"]
    _recusado_valor_invalido(estorno)
    assert (a["status"], a["valor_reembolsado"]) == ("aprovado", Decimal("50.00"))
    assert (b["status"], b["valor_reembolsado"]) == ("parcial", Decimal("10.00"))
    assert saida["totais"]["valor_solicitado"] == Decimal("80.00")


def _caso_valor_zero(saida):
    (item,) = saida["itens"]
    _recusado_valor_invalido(item)


def _caso_arredondamento_da_metade_negativa(saida):
    # -0,005 → -0,01 (metade afasta do zero) → `valor_invalido`
    (item,) = saida["itens"]
    assert item["valor_considerado"] == Decimal("-0.01")
    _recusado_valor_invalido(item)


def _caso_valor_minusculo(saida):
    # 10^-999999 → 0,00 → `valor_invalido`; informado copiado sem arredondar
    (item,) = saida["itens"]
    assert item["valor_considerado"] == Decimal("0.00")
    assert item["valor_informado"] == Decimal("1E-999999")
    _recusado_valor_invalido(item)


def _recusado_fora_do_periodo(item):
    # RN-005: recusado, `fora_do_periodo`, sem reembolso, nulos de antes do limite
    assert (item["status"], item["motivo"]) == ("recusado", "fora_do_periodo")
    assert item["valor_reembolsado"] == 0
    assert (item["em_viagem"], item["limite_diario"]) == (None, None)


def _caso_primeiro_e_ultimo_dia_do_periodo(saida):
    # `inicio` e `fim` inclusive → seguem; 41,00 ≤ 60,00 → aprovado
    for item in saida["itens"]:
        assert (item["status"], item["valor_reembolsado"]) == (
            "aprovado", Decimal("41.00"),
        )


def _caso_fora_do_periodo(saida):
    (item,) = saida["itens"]
    _recusado_fora_do_periodo(item)


def _caso_categoria_tratada_como(categoria, limite):
    def verificar(saida):
        # RN-006: reconhecida → normalizada na saída e limite da categoria;
        # 10,00 ≤ limite → aprovado
        for item in saida["itens"]:
            assert item["categoria"] == categoria
            assert item["limite_diario"] == limite
            assert item["status"] == "aprovado"
    return verificar


def _caso_valor_no_limite_de_nota(saida):
    # RN-008: 100,00 não é > 100,00 → segue; RN-009: min(100,00; 80,00) = 80,00
    (item,) = saida["itens"]
    assert (item["status"], item["motivo"]) == ("parcial", "limite_diario_excedido")
    assert item["valor_reembolsado"] == Decimal("80.00")


def _caso_um_centavo_acima_do_limite_de_nota(saida):
    # RN-008: 100,01 > 100,00 sem nota → recusado antes do limite
    (item,) = saida["itens"]
    assert (item["status"], item["motivo"]) == ("recusado", "nota_fiscal_ausente")
    assert item["valor_reembolsado"] == 0
    assert (item["em_viagem"], item["limite_diario"]) == (None, None)


def _aviso(caminho, n):
    return f"chave repetida: {caminho} ({n} ocorrências; valeu a última)"


def _com_campos(campos, despesas=None, colaborador='{"id": "c-1", "nome": "Ana"}'):
    """Texto JSON com `campos` escritos literalmente numa despesa (chave repetida)."""
    if despesas is None:
        despesas = (
            '[{"id": "d-1", "data": "2026-07-03", "categoria": "alimentacao", '
            '"fornecedor": "Restaurante", "tem_nota_fiscal": true, ' + campos + "}]"
        )
    return (
        '{"colaborador": ' + colaborador + ", "
        '"periodo": {"inicio": "2026-07-01", "fim": "2026-07-31"}, '
        '"despesas": ' + despesas + "}"
    )


def _caso_chave_repetida_na_despesa(saida):
    # vale 50,00 ≤ 60,00 → aprovado; aviso no item, nenhum no topo
    (item,) = saida["itens"]
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("50.00"), "aprovado")
    assert item["avisos"] == [_aviso("valor", 2)]
    assert saida["avisos"] == []


def _caso_chave_repetida_fora_das_despesas(saida):
    assert saida["colaborador"]["nome"] == "Bia"
    assert saida["avisos"] == [_aviso("colaborador.nome", 2)]
    assert saida["itens"][0]["avisos"] == []


def _caso_chave_repetida_dentro_de_valor_descartado(saida):
    # só a última lista (uma despesa de 20,00) é avaliada; `valor` repetido na
    # primeira lista não gera aviso
    (item,) = saida["itens"]
    assert (item["id"], item["valor_reembolsado"]) == ("d-2", Decimal("20.00"))
    assert item["avisos"] == []
    assert saida["avisos"] == [_aviso("despesas", 2)]


def _caso_mesma_chave_aninhada(saida):
    (item,) = saida["itens"]
    assert item["avisos"] == [
        _aviso("extra", 2), _aviso("obs", 2), _aviso("extra.x", 2),
    ]


def _caso_chave_repetida_escrita_com_escape(saida):
    # vale 90,00; min(90,00; 60,00) = 60,00 → parcial
    (item,) = saida["itens"]
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("60.00"), "parcial")
    assert item["avisos"] == [_aviso("valor", 2)]


def _caso_lista_dentro_de_lista(saida):
    (item,) = saida["itens"]
    assert item["avisos"] == [_aviso("m[0][0].x", 2)]


def _caso_chave_repetida_mil_vezes(saida):
    (item,) = saida["itens"]
    assert item["avisos"] == [_aviso("obs", 1000)]


def _caso_chave_repetida_em_elemento_lista(saida):
    (item,) = saida["itens"]
    _recusado_entrada_invalida(item)
    assert item["avisos"] == [_aviso("[0].a", 2)]


def _caso_segunda_duplicata(saida):
    # RN-007: a primeira avaliada (≤ 60,00 → aprovado); a segunda `duplicata`,
    # recusada antes do limite
    a, b = saida["itens"]
    assert (a["status"], a["motivo"]) == ("aprovado", None)
    assert (b["status"], b["motivo"], b["valor_reembolsado"]) == (
        "recusado", "duplicata", Decimal("0"),
    )
    assert (b["em_viagem"], b["limite_diario"]) == (None, None)


def _caso_quase_duplicata(saida):
    # data vizinha / fornecedor diferente: comparação exata → todas avaliadas
    assert [item["status"] for item in saida["itens"]] == ["aprovado"] * 3


def _caso_copias_sem_nota_acima_de_100(saida):
    # etapa 6 antes da 7: as duas recusadas por nota, nenhuma por duplicata
    assert [item["motivo"] for item in saida["itens"]] == [
        "nota_fiscal_ausente", "nota_fiscal_ausente",
    ]


def _caso_relancamento_com_nota(saida):
    # sem nota → `nota_fiscal_ausente` (etapa 6); com nota segue: transporte
    # min(110,00; 80,00) = 80,00 → parcial
    itens = {item["id"]: item for item in saida["itens"]}
    assert itens["sem"]["motivo"] == "nota_fiscal_ausente"
    assert (itens["com"]["status"], itens["com"]["valor_reembolsado"]) == (
        "parcial", Decimal("80.00"),
    )


def _relancamento(sem_nota_primeiro):
    campos = dict(categoria="transporte_urbano", fornecedor="Táxi",
                  valor=Decimal("110.00"))
    sem = despesa(id="sem", tem_nota_fiscal=False, **campos)
    com = despesa(id="com", tem_nota_fiscal=True, **campos)
    return _json(*([sem, com] if sem_nota_primeiro else [com, sem]))


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
    pytest.param(
        _json(despesa(id="a", valor=Decimal("50.00"), fornecedor="A"),
              despesa(id="e", valor=Decimal("-45.00"), fornecedor="A"),
              despesa(id="b", valor=Decimal("30.00"), fornecedor="B")),
        _caso_estorno,
        id="Estorno",
    ),
    pytest.param(
        _json(despesa(valor=Decimal("0.00"))), _caso_valor_zero, id="Valor zero"
    ),
    pytest.param(
        _json(despesa(valor=Decimal("-0.005"))),
        _caso_arredondamento_da_metade_negativa,
        id="Arredondamento da metade negativa",
    ),
    pytest.param(
        _json(despesa(valor=Decimal("1"))).replace('"valor": 1', '"valor": 1e-999999'),
        _caso_valor_minusculo,
        id="Valor minúsculo",
    ),
    pytest.param(
        _json(despesa(id="a", data="2026-07-01", valor=Decimal("41.00")),
              despesa(id="b", data="2026-07-31", valor=Decimal("41.00"))),
        _caso_primeiro_e_ultimo_dia_do_periodo,
        id="Primeiro e último dia do período",
    ),
    pytest.param(
        # fim 31/07 + 1 dia = 01/08
        _json(despesa(data="2026-08-01")),
        _caso_fora_do_periodo,
        id="Um dia fora do período",
    ),
    pytest.param(
        # d-008: 41,00 em 15/04, período de julho
        _json(despesa(id="d-008", data="2026-04-15", valor=Decimal("41.00"))),
        _caso_fora_do_periodo,
        id="Despesa antiga lançada no período",
    ),
    pytest.param(
        _json(despesa(categoria="ALIMENTACAO")),
        _caso_categoria_tratada_como("alimentacao", Decimal("60.00")),
        id="Categoria em maiúsculas",
    ),
    pytest.param(
        _json(despesa(categoria="alimentação")),
        _caso_categoria_tratada_como("alimentacao", Decimal("60.00")),
        id="Categoria com acento",
    ),
    pytest.param(
        _json(despesa(id="a", categoria="Transporte Urbano"),
              despesa(id="b", categoria="transporte-urbano", data="2026-07-04")),
        _caso_categoria_tratada_como("transporte_urbano", Decimal("80.00")),
        id="Categoria com separador diferente",
    ),
    pytest.param(
        _json(despesa(categoria="alimentacao\t")),
        _caso_categoria_tratada_como("alimentacao", Decimal("60.00")),
        id="Categoria com tabulação no fim",
    ),
    pytest.param(
        _json(despesa(categoria="transporte_urbano", valor=Decimal("100.00"),
                      tem_nota_fiscal=False)),
        _caso_valor_no_limite_de_nota,
        id="Valor exatamente no limite de nota",
    ),
    pytest.param(
        _json(despesa(valor=Decimal("100.01"), tem_nota_fiscal=False)),
        _caso_um_centavo_acima_do_limite_de_nota,
        id="Um centavo acima do limite de nota",
    ),
    pytest.param(
        _json(despesa(id="d-006", fornecedor="Bistro Central", valor=Decimal("54.90")),
              despesa(id="d-007", fornecedor="Bistro Central", valor=Decimal("54.90"))),
        _caso_segunda_duplicata,
        id="Duplicata exata",
    ),
    pytest.param(
        _json(despesa(id="a", fornecedor="Bistro Central", valor=Decimal("54.90")),
              despesa(id="b", fornecedor="Bistrô Central", valor=Decimal("54.90"))),
        _caso_segunda_duplicata,
        id="Fornecedor com acento",
    ),
    pytest.param(
        _json(despesa(id="a", fornecedor="Pão  Quente", valor=Decimal("12.00")),
              despesa(id="b", fornecedor="Pao Quente", valor=Decimal("12.00"))),
        _caso_segunda_duplicata,
        id="Fornecedor com espaços internos",
    ),
    pytest.param(
        _json(despesa(id="a", fornecedor="Bistro Central", valor=Decimal("20.00")),
              despesa(id="b", fornecedor="Bistro Central", valor=Decimal("20.00"),
                      data="2026-07-04"),
              despesa(id="c", fornecedor="Bistro Centro", valor=Decimal("20.00"))),
        _caso_quase_duplicata,
        id="Quase duplicata",
    ),
    pytest.param(
        _json(despesa(id="a", valor=Decimal("150.00"), tem_nota_fiscal=False),
              despesa(id="b", valor=Decimal("150.00"), tem_nota_fiscal=False)),
        _caso_copias_sem_nota_acima_de_100,
        id="Cópias idênticas sem nota acima de 100",
    ),
    pytest.param(
        _relancamento(sem_nota_primeiro=True),
        _caso_relancamento_com_nota,
        id="Relançamento com nota",
    ),
    pytest.param(
        _relancamento(sem_nota_primeiro=False),
        _caso_relancamento_com_nota,
        id="Relançamento com nota (ordem inversa)",
    ),
    pytest.param(
        _com_campos('"valor": 30.00, "valor": 50.00'),
        _caso_chave_repetida_na_despesa,
        id="Chave repetida na despesa",
    ),
    pytest.param(
        _com_campos('"valor": 10.00',
                    colaborador='{"id": "c-1", "nome": "Ana", "nome": "Bia"}'),
        _caso_chave_repetida_fora_das_despesas,
        id="Chave repetida fora das despesas",
    ),
    pytest.param(
        '{"colaborador": {"id": "c-1", "nome": "Ana"}, '
        '"periodo": {"inicio": "2026-07-01", "fim": "2026-07-31"}, '
        '"despesas": [{"id": "d-1", "data": "2026-07-03", '
        '"categoria": "alimentacao", "fornecedor": "R", "tem_nota_fiscal": true, '
        '"valor": 1, "valor": 2}], '
        '"despesas": [{"id": "d-2", "data": "2026-07-03", '
        '"categoria": "alimentacao", "fornecedor": "R", "tem_nota_fiscal": true, '
        '"valor": 20.00}]}',
        _caso_chave_repetida_dentro_de_valor_descartado,
        id="Chave repetida dentro de valor descartado",
    ),
    pytest.param(
        _com_campos('"valor": 10.00, "extra": {"x": 1, "x": 2}, "obs": "a", '
                    '"obs": "b", "extra": {"x": 3, "x": 4}'),
        _caso_mesma_chave_aninhada,
        id="Mesma chave aninhada no valor descartado e no que valeu",
    ),
    pytest.param(
        _com_campos('"valor": 30.00, "\\u0076alor": 90.00'),
        _caso_chave_repetida_escrita_com_escape,
        id="Chave repetida escrita com escape",
    ),
    pytest.param(
        _com_campos('"valor": 10.00, "m": [[{"x": 1, "x": 2}]]'),
        _caso_lista_dentro_de_lista,
        id="Lista dentro de lista no caminho",
    ),
    pytest.param(
        _com_campos('"valor": 10.00, '
                    + ", ".join(f'"obs": "{i}"' for i in range(1000))),
        _caso_chave_repetida_mil_vezes,
        id="Chave repetida mil vezes",
    ),
    pytest.param(
        _com_campos("", despesas='[[{"a": 1, "a": 2}]]'),
        _caso_chave_repetida_em_elemento_lista,
        id="Chave repetida em elemento que é lista",
    ),
]


@pytest.mark.parametrize(("texto", "verificar"), CASOS)
def test_caso_de_borda(processar, texto, verificar):
    """Seção 7 da spec: comportamento esperado de cada caso."""
    verificar(processar(texto))
