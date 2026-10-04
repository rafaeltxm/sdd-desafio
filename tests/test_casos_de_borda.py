"""Casos de borda da seção 7 da spec: um caso por linha, `id` = coluna "Caso"."""

from decimal import Decimal

import pytest
import simplejson

from conftest import construir_cambio, construir_entrada, construir_politica
from conftest import construir_despesa as despesa
from reembolso.cli import main


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


def _caso_moeda_em_minusculas(saida):
    # RN-002 / AMB-025: comparado como veio, sem normalização → inválida
    (item,) = saida["itens"]
    _recusado_entrada_invalida(item)
    assert item["moeda"] == "eur"


def _caso_moeda_de_tipo_errado(saida):
    # RN-002: não é texto nem nula → inválida, `moeda` nula na saída
    (item,) = saida["itens"]
    _recusado_entrada_invalida(item)
    assert item["moeda"] is None


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


def _hospedagem(**campos):
    padrao = dict(id="h", categoria="hospedagem", fornecedor="Hotel",
                  valor=Decimal("200.00"), tem_nota_fiscal=True)
    padrao.update(campos)
    return despesa(**padrao)


def _em_viagem(item, limite):
    assert (item["em_viagem"], item["limite_diario"]) == (True, limite)


def _caso_limite_de_nota_em_viagem(saida):
    # RN-008: 110,00 > 100,00 sem nota, mesmo em viagem → recusado antes do limite
    _, transporte = saida["itens"]
    assert (transporte["status"], transporte["motivo"]) == (
        "recusado", "nota_fiscal_ausente",
    )
    assert (transporte["em_viagem"], transporte["limite_diario"]) == (None, None)


def _caso_hospedagem_duplicata_so_uma_com_nota(saida):
    # RN-007: a com nota é a original; RN-010: comprova 14/07 e 15/07;
    # alimentação 80,00 em 15/07 ≤ 90,00 → aprovado
    itens = {item["id"]: item for item in saida["itens"]}
    assert itens["sem"]["motivo"] == "duplicata"
    _em_viagem(itens["com"], Decimal("250.00"))
    _em_viagem(itens["a"], Decimal("90.00"))
    assert itens["a"]["status"] == "aprovado"


def _caso_hospedagem_varias_diarias(saida):
    # RN-012: uma diária, min(480,00; 250,00) = 250,00 → parcial; RN-010: 14 e 15/07
    hospedagem, a15, a16 = saida["itens"]
    assert (hospedagem["valor_reembolsado"], hospedagem["status"]) == (
        Decimal("250.00"), "parcial",
    )
    _em_viagem(hospedagem, Decimal("250.00"))
    assert a15["em_viagem"] is True
    assert a16["em_viagem"] is False


def _caso_dia_seguinte_a_diaria(saida):
    # 15/07 = D+1 em viagem: 80,00 ≤ 90,00 → aprovado
    _, alimentacao = saida["itens"]
    _em_viagem(alimentacao, Decimal("90.00"))
    assert (alimentacao["valor_reembolsado"], alimentacao["status"]) == (
        Decimal("80.00"), "aprovado",
    )


def _caso_dois_dias_depois_da_diaria(saida):
    # 16/07 = D+2 fora de viagem: min(80,00; 60,00) = 60,00 → parcial
    _, alimentacao = saida["itens"]
    assert (alimentacao["em_viagem"], alimentacao["limite_diario"]) == (
        False, Decimal("60.00"),
    )
    assert (alimentacao["valor_reembolsado"], alimentacao["status"]) == (
        Decimal("60.00"), "parcial",
    )


def _caso_hospedagem_sem_nota_ate_100(saida):
    # 80,00 ≤ 100,00 sem nota → segue, aprovado; não comprova viagem:
    # alimentação min(90,00; 60,00) = 60,00 → parcial
    hospedagem, alimentacao = saida["itens"]
    assert (hospedagem["valor_reembolsado"], hospedagem["status"]) == (
        Decimal("80.00"), "aprovado",
    )
    assert hospedagem["em_viagem"] is False
    assert (alimentacao["em_viagem"], alimentacao["limite_diario"]) == (
        False, Decimal("60.00"),
    )
    assert (alimentacao["valor_reembolsado"], alimentacao["status"]) == (
        Decimal("60.00"), "parcial",
    )


def _caso_hospedagem_sem_nota_acima_de_100(saida):
    # RN-008 recusa na etapa 6 → não comprova viagem: limite 60,00 na mesma data
    hospedagem, alimentacao = saida["itens"]
    assert hospedagem["motivo"] == "nota_fiscal_ausente"
    assert (alimentacao["em_viagem"], alimentacao["limite_diario"]) == (
        False, Decimal("60.00"),
    )


def _caso_hospedagem_fora_do_periodo(saida):
    # RN-005 recusa na etapa 4 → 01/07 não fica em viagem
    hospedagem, alimentacao = saida["itens"]
    _recusado_fora_do_periodo(hospedagem)
    assert (alimentacao["em_viagem"], alimentacao["limite_diario"]) == (
        False, Decimal("60.00"),
    )


def _caso_alimentacao_antes_da_hospedagem(saida):
    # etapa 8 antes da 9: data em viagem; 80,00 ≤ 90,00 → aprovado
    alimentacao, _ = saida["itens"]
    _em_viagem(alimentacao, Decimal("90.00"))
    assert (alimentacao["valor_reembolsado"], alimentacao["status"]) == (
        Decimal("80.00"), "aprovado",
    )


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
    pytest.param(
        _json(_hospedagem(data="2026-07-14"),
              despesa(id="t", data="2026-07-14", categoria="transporte_urbano",
                      fornecedor="Táxi", valor=Decimal("110.00"),
                      tem_nota_fiscal=False)),
        _caso_limite_de_nota_em_viagem,
        id="Limite de nota em viagem",
    ),
    pytest.param(
        _json(_hospedagem(id="sem", data="2026-07-14", valor=Decimal("90.00"),
                          tem_nota_fiscal=False),
              _hospedagem(id="com", data="2026-07-14", valor=Decimal("90.00")),
              despesa(id="a", data="2026-07-15", valor=Decimal("80.00"))),
        _caso_hospedagem_duplicata_so_uma_com_nota,
        id="Duplicata de hospedagem só uma com nota",
    ),
    pytest.param(
        _json(_hospedagem(id="com", data="2026-07-14", valor=Decimal("90.00")),
              _hospedagem(id="sem", data="2026-07-14", valor=Decimal("90.00"),
                          tem_nota_fiscal=False),
              despesa(id="a", data="2026-07-15", valor=Decimal("80.00"))),
        _caso_hospedagem_duplicata_so_uma_com_nota,
        id="Duplicata de hospedagem só uma com nota (ordem inversa)",
    ),
    pytest.param(
        _json(_hospedagem(data="2026-07-14", valor=Decimal("480.00"),
                          descricao="2 diarias"),
              despesa(id="a15", data="2026-07-15", valor=Decimal("10.00")),
              despesa(id="a16", data="2026-07-16", valor=Decimal("10.00"))),
        _caso_hospedagem_varias_diarias,
        id="Hospedagem com várias diárias na descrição",
    ),
    pytest.param(
        _json(_hospedagem(data="2026-07-14"),
              despesa(id="a", data="2026-07-15", valor=Decimal("80.00"))),
        _caso_dia_seguinte_a_diaria,
        id="Dia seguinte à diária",
    ),
    pytest.param(
        _json(_hospedagem(data="2026-07-14"),
              despesa(id="a", data="2026-07-16", valor=Decimal("80.00"))),
        _caso_dois_dias_depois_da_diaria,
        id="Dois dias depois da diária",
    ),
    pytest.param(
        _json(_hospedagem(data="2026-07-03", valor=Decimal("80.00"),
                          tem_nota_fiscal=False),
              despesa(id="a", data="2026-07-03", valor=Decimal("90.00"))),
        _caso_hospedagem_sem_nota_ate_100,
        id="Hospedagem sem nota até 100",
    ),
    pytest.param(
        _json(_hospedagem(data="2026-07-14", valor=Decimal("690.00"),
                          tem_nota_fiscal=False),
              despesa(id="a", data="2026-07-14", valor=Decimal("80.00"))),
        _caso_hospedagem_sem_nota_acima_de_100,
        id="Hospedagem sem nota acima de 100",
    ),
    pytest.param(
        _json(_hospedagem(data="2026-06-30"),
              despesa(id="a", data="2026-07-01", valor=Decimal("80.00"))),
        _caso_hospedagem_fora_do_periodo,
        id="Hospedagem fora do período",
    ),
    pytest.param(
        _json(despesa(id="a", data="2026-07-14", valor=Decimal("80.00")),
              _hospedagem(data="2026-07-14")),
        _caso_alimentacao_antes_da_hospedagem,
        id="Alimentação antes da hospedagem na entrada, mesma data",
    ),
    pytest.param(
        _json(despesa(moeda="eur")),
        _caso_moeda_em_minusculas,
        id="Moeda em minúsculas",
    ),
    pytest.param(
        _json(despesa(moeda=978)),
        _caso_moeda_de_tipo_errado,
        id="Moeda de tipo errado",
    ),
]


@pytest.mark.parametrize(("texto", "verificar"), CASOS)
def test_caso_de_borda(processar, texto, verificar):
    """Seção 7 da spec: comportamento esperado de cada caso."""
    verificar(processar(texto))


# --- tabela aplicada por centro de custo e política (RN-014, RN-006, RN-016) ---


def _resumo(item):
    return (item["limite_diario"], item["valor_reembolsado"], item["status"])


def _fora_da_politica(item):
    # RN-006: recusado na etapa 5, antes do limite diário
    assert (item["status"], item["motivo"]) == (
        "recusado", "categoria_fora_da_politica",
    )
    assert (item["em_viagem"], item["limite_diario"]) == (None, None)


def _caso_centro_de_custo_da_tabela(saida):
    # CC-COMERCIAL: alimentação 90,00; 85,00 ≤ 90,00 → aprovado
    assert saida["politica"]["tabela_aplicada"] == "CC-COMERCIAL"
    (item,) = saida["itens"]
    assert _resumo(item) == (Decimal("90.00"), Decimal("85.00"), "aprovado")


def _caso_centro_de_custo_fora_da_tabela(saida):
    # padrao: alimentação 60,00; min(65,00; 60,00) = 60,00 → parcial
    assert saida["politica"]["tabela_aplicada"] == "padrao"
    (item,) = saida["itens"]
    assert _resumo(item) == (Decimal("60.00"), Decimal("60.00"), "parcial")


def _caso_centro_de_custo_com_grafia_diferente(saida):
    # "cc-adm" ≠ "CC-ADM" → padrao: 50,00 ≤ 60,00 → aprovado
    assert saida["politica"]["tabela_aplicada"] == "padrao"
    (item,) = saida["itens"]
    assert _resumo(item) == (Decimal("60.00"), Decimal("50.00"), "aprovado")


def _caso_centro_de_custo_so_com_espacos(saida):
    # "  " = não informado → padrao; copiado como veio na saída
    assert saida["politica"]["tabela_aplicada"] == "padrao"
    assert saida["colaborador"]["centro_custo"] == "  "


def _caso_categoria_ausente_da_tabela_do_cc(saida):
    # CC-ADM sem hospedagem → etapa 5; não comprova viagem: 15/07 com limite
    # normal 45,00; min(70,00; 45,00) = 45,00 → parcial
    hospedagem, alimentacao = saida["itens"]
    _fora_da_politica(hospedagem)
    assert alimentacao["em_viagem"] is False
    assert _resumo(alimentacao) == (Decimal("45.00"), Decimal("45.00"), "parcial")


def _caso_categoria_com_limite_zero(saida):
    # CC-ENG-PLATAFORMA hospedagem 0 → etapa 5 (AMB-021); 15/07 fora de viagem:
    # limite 75,00; min(100,00; 75,00) = 75,00 → parcial
    hospedagem, alimentacao = saida["itens"]
    _fora_da_politica(hospedagem)
    assert alimentacao["em_viagem"] is False
    assert _resumo(alimentacao) == (Decimal("75.00"), Decimal("75.00"), "parcial")


def _caso_representacao_fora_do_cc(saida):
    # CC-SUPORTE-N2 → padrao, que não tem representação
    (item,) = saida["itens"]
    _fora_da_politica(item)


def _caso_representacao_nao_amplia_em_viagem(saida):
    # 23/07 = D+1 da hospedagem de 22/07: em viagem; representação não amplia
    # (AMB-022): limite 300,00; min(400,00; 300,00) = 300,00 → parcial
    _, representacao = saida["itens"]
    assert representacao["em_viagem"] is True
    assert _resumo(representacao) == (
        Decimal("300.00"), Decimal("300.00"), "parcial",
    )


def _caso_limite_em_viagem_truncado(saida):
    # 15/07 em viagem: 33,33 × 1,5 = 49,995 → truncado 49,99;
    # min(60,00; 49,99) = 49,99 → parcial
    _, alimentacao = saida["itens"]
    assert alimentacao["em_viagem"] is True
    assert _resumo(alimentacao) == (Decimal("49.99"), Decimal("49.99"), "parcial")


def _caso_politica_sem_versao_nem_vigencia(saida):
    assert saida["politica"] == {
        "versao": None, "vigencia": None, "tabela_aplicada": "padrao",
    }
    # processamento normal: 10,00 ≤ 60,00 → aprovado
    assert saida["itens"][0]["status"] == "aprovado"


def _politica_truncada():
    return construir_politica(padrao={
        "alimentacao": {"limite": Decimal("33.33"), "periodicidade": "dia"},
        "hospedagem": {"limite": Decimal("250.00"), "periodicidade": "diaria"},
    })


def _politica_sem_versao_nem_vigencia():
    documento = construir_politica()
    del documento["versao"], documento["vigencia"]
    return documento


CASOS_DE_TABELA_APLICADA = [
    # (texto da entrada, documento da política ou None para a v4, verificação)
    pytest.param(
        _json(despesa(valor=Decimal("85.00")), centro_custo="CC-COMERCIAL"),
        None, _caso_centro_de_custo_da_tabela, id="Centro de custo da tabela",
    ),
    pytest.param(
        _json(despesa(valor=Decimal("65.00")), centro_custo="CC-SUPORTE-N2"),
        None, _caso_centro_de_custo_fora_da_tabela,
        id="Centro de custo fora da tabela",
    ),
    pytest.param(
        _json(despesa(valor=Decimal("50.00")), centro_custo="cc-adm"),
        None, _caso_centro_de_custo_com_grafia_diferente,
        id="Centro de custo com grafia diferente",
    ),
    pytest.param(
        _json(despesa(), centro_custo="  "),
        None, _caso_centro_de_custo_so_com_espacos,
        id="Centro de custo só com espaços",
    ),
    pytest.param(
        _json(_hospedagem(data="2026-07-14", valor=Decimal("300.00")),
              despesa(id="a", data="2026-07-15", valor=Decimal("70.00")),
              centro_custo="CC-ADM"),
        None, _caso_categoria_ausente_da_tabela_do_cc,
        id="Categoria ausente da tabela do centro de custo",
    ),
    pytest.param(
        _json(_hospedagem(data="2026-07-14", valor=Decimal("480.00")),
              despesa(id="a", data="2026-07-15", valor=Decimal("100.00")),
              centro_custo="CC-ENG-PLATAFORMA"),
        None, _caso_categoria_com_limite_zero, id="Categoria com limite zero",
    ),
    pytest.param(
        _json(despesa(categoria="representacao", valor=Decimal("190.00")),
              centro_custo="CC-SUPORTE-N2"),
        None, _caso_representacao_fora_do_cc,
        id="Representação fora do centro de custo que a define",
    ),
    pytest.param(
        _json(_hospedagem(data="2026-07-22"),
              despesa(id="r", data="2026-07-23", categoria="representacao",
                      valor=Decimal("400.00")),
              centro_custo="CC-COMERCIAL"),
        None, _caso_representacao_nao_amplia_em_viagem,
        id="Representação não amplia em viagem",
    ),
    pytest.param(
        _json(_hospedagem(data="2026-07-14"),
              despesa(id="a", data="2026-07-15", valor=Decimal("60.00"))),
        _politica_truncada(), _caso_limite_em_viagem_truncado,
        id="Limite em viagem truncado",
    ),
    pytest.param(
        _json(despesa()), _politica_sem_versao_nem_vigencia(),
        _caso_politica_sem_versao_nem_vigencia,
        id="Política sem versão nem vigência",
    ),
]


@pytest.mark.parametrize(("texto", "politica", "verificar"), CASOS_DE_TABELA_APLICADA)
def test_caso_de_borda_de_tabela_aplicada(processar, texto, politica, verificar):
    """Seção 7 da spec: casos da tabela aplicada por centro de custo (RN-014,
    RN-006, RN-009, RN-010) e da política sem versão nem vigência (RN-016)."""
    verificar(processar(texto, politica))


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


def _caso_moeda_nula(saida):
    # null = BRL: taxa 1, sem data de cotação; 45,00 ≤ 60,00 → aprovado
    (item,) = saida["itens"]
    assert _conversao(item) == ("BRL", 1, None, Decimal("45.00"))
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("45.00"),
                                                          "aprovado")


def _caso_moeda_estrangeira_com_cotacao(saida):
    # 22,00 × 5,93 = 130,46; min(130,46; 60,00) = 60,00 → parcial
    (item,) = saida["itens"]
    assert _conversao(item) == ("EUR", Decimal("5.93"), "2026-07-14",
                                Decimal("130.46"))
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("60.00"),
                                                          "parcial")


def _caso_moeda_estrangeira_em_sabado(saida):
    # 18/07 sem cotação → 17/07 (D-1): 30,00 × 5,96 = 178,80
    (item,) = saida["itens"]
    assert _conversao(item) == ("EUR", Decimal("5.96"), "2026-07-17",
                                Decimal("178.80"))


def _caso_cotacao_3_dias_antes(saida):
    # 16/07 - 3 = 13/07: 10,00 × 5,42 = 54,20
    (item,) = saida["itens"]
    assert _conversao(item) == ("USD", Decimal("5.42"), "2026-07-13",
                                Decimal("54.20"))


def _caso_cambio_indisponivel_fora_dos_totais(saida):
    (item,) = saida["itens"]
    _recusado_cambio_indisponivel(item)
    _fora_dos_totais(saida)


def _caso_moeda_sem_cotacao_no_arquivo(saida):
    # GBP não está no câmbio
    (item,) = saida["itens"]
    _recusado_cambio_indisponivel(item)
    assert item["moeda"] == "GBP"
    _fora_dos_totais(saida)


def _caso_sem_cotacao_e_fora_do_periodo(saida):
    # etapa 2 (câmbio) antes da etapa 4 (período)
    (item,) = saida["itens"]
    _recusado_cambio_indisponivel(item)


def _caso_conversao_arredondada_uma_vez(saida):
    # 16,8649 × 5,93 = 100,008857 → 100,01 > 100,00 sem nota
    (item,) = saida["itens"]
    assert item["valor_considerado"] == Decimal("100.01")
    assert (item["status"], item["motivo"]) == ("recusado", "nota_fiscal_ausente")


def _caso_nota_fiscal_comparada_em_reais(saida):
    # 40,00 × 5,50 = 220,00 > 100,00 sem nota
    (item,) = saida["itens"]
    assert item["valor_considerado"] == Decimal("220.00")
    assert (item["status"], item["motivo"]) == ("recusado", "nota_fiscal_ausente")


def _caso_valor_estrangeiro_minusculo(saida):
    # 0,001 × 5,93 = 0,00593 → 0,01 > 0; 0,01 ≤ 60,00 → aprovado
    (item,) = saida["itens"]
    assert item["valor_considerado"] == Decimal("0.01")
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("0.01"),
                                                          "aprovado")


def _caso_teto_na_moeda_original(saida):
    # 200.000.000 < 1 bilhão na moeda original: segue;
    # 200.000.000 × 5,44 = 1.088.000.000,00; min(…; 60,00) = 60,00
    (item,) = saida["itens"]
    assert item["valor_considerado"] == Decimal("1088000000.00")
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("60.00"),
                                                          "parcial")


def _caso_moeda_estrangeira_nao_comprova_viagem(saida):
    # sem hospedagem: 14/07 fora de viagem; min(80,00; 60,00) = 60,00
    _, alimentacao = saida["itens"]
    assert alimentacao["em_viagem"] is False
    assert _resumo(alimentacao) == (Decimal("60.00"), Decimal("60.00"), "parcial")


def _caso_hospedagem_em_moeda_estrangeira(saida):
    # 50,00 × 5,95 = 297,50; min(297,50; 250,00) = 250,00 → parcial
    # 23/07 = D+1: 60,00 × 1,5 = 90,00; 80,00 ≤ 90,00 → aprovado
    hospedagem, alimentacao = saida["itens"]
    assert hospedagem["valor_considerado"] == Decimal("297.50")
    assert hospedagem["em_viagem"] is True
    assert _resumo(hospedagem) == (Decimal("250.00"), Decimal("250.00"), "parcial")
    assert alimentacao["em_viagem"] is True
    assert _resumo(alimentacao) == (Decimal("90.00"), Decimal("80.00"), "aprovado")


def _caso_data_intermediaria_sem_a_moeda(saida):
    # 15/07 sem cotação; 14/07 só USD; 13/07 EUR 5,91: 20,00 × 5,91 = 118,20;
    # min(118,20; 60,00) = 60,00 → parcial
    (item,) = saida["itens"]
    assert _conversao(item) == ("EUR", Decimal("5.91"), "2026-07-13",
                                Decimal("118.20"))
    assert (item["valor_reembolsado"], item["status"]) == (Decimal("60.00"),
                                                          "parcial")


_SO_13_07 = {"2026-07-13": {"USD": Decimal("5.42")}}

CASOS_DE_CAMBIO = [
    # (texto da entrada, documento do câmbio ou None para o do envelope, verificação)
    pytest.param(
        _json(despesa(valor=Decimal("45.00"), moeda=None)),
        None, _caso_moeda_nula, id="Moeda nula",
    ),
    pytest.param(
        _json(despesa(data="2026-07-14", valor=Decimal("22.00"), moeda="EUR")),
        None, _caso_moeda_estrangeira_com_cotacao,
        id="Moeda estrangeira com cotação",
    ),
    pytest.param(
        _json(despesa(data="2026-07-18", valor=Decimal("30.00"), moeda="EUR")),
        None, _caso_moeda_estrangeira_em_sabado,
        id="Moeda estrangeira em sábado",
    ),
    pytest.param(
        _json(despesa(data="2026-07-16", valor=Decimal("10.00"), moeda="USD")),
        construir_cambio(taxas=_SO_13_07), _caso_cotacao_3_dias_antes,
        id="Cotação exatamente 3 dias antes",
    ),
    pytest.param(
        _json(despesa(data="2026-07-17", valor=Decimal("10.00"), moeda="USD")),
        construir_cambio(taxas=_SO_13_07), _caso_cambio_indisponivel_fora_dos_totais,
        id="Cotação 4 dias antes",
    ),
    pytest.param(
        _json(despesa(data="2026-07-21", valor=Decimal("55.00"), moeda="GBP")),
        None, _caso_moeda_sem_cotacao_no_arquivo,
        id="Moeda sem cotação no arquivo",
    ),
    pytest.param(
        _json(despesa(data="2026-04-15", valor=Decimal("10.00"), moeda="USD")),
        None, _caso_sem_cotacao_e_fora_do_periodo,
        id="Sem cotação e fora do período",
    ),
    pytest.param(
        _json(despesa(data="2026-07-14", valor=Decimal("16.8649"), moeda="EUR",
                      tem_nota_fiscal=False)),
        None, _caso_conversao_arredondada_uma_vez,
        id="Conversão arredondada uma vez",
    ),
    pytest.param(
        _json(despesa(data="2026-07-20", categoria="transporte_urbano",
                      valor=Decimal("40.00"), moeda="USD", tem_nota_fiscal=False)),
        None, _caso_nota_fiscal_comparada_em_reais,
        id="Nota fiscal comparada em reais",
    ),
    pytest.param(
        _json(despesa(data="2026-07-14", valor=Decimal("0.001"), moeda="EUR")),
        None, _caso_valor_estrangeiro_minusculo, id="Valor estrangeiro minúsculo",
    ),
    pytest.param(
        _json(despesa(data="2026-07-14", valor=Decimal("200000000"), moeda="USD")),
        None, _caso_teto_na_moeda_original, id="Teto na moeda original",
    ),
    pytest.param(
        _json(despesa(id="t", data="2026-07-14", categoria="transporte_urbano",
                      valor=Decimal("22.00"), moeda="EUR"),
              despesa(id="a", data="2026-07-14", valor=Decimal("80.00"))),
        None, _caso_moeda_estrangeira_nao_comprova_viagem,
        id="Moeda estrangeira não comprova viagem",
    ),
    pytest.param(
        _json(_hospedagem(data="2026-07-22", valor=Decimal("50.00"), moeda="EUR"),
              despesa(id="a", data="2026-07-23", valor=Decimal("80.00"))),
        None, _caso_hospedagem_em_moeda_estrangeira,
        id="Hospedagem em moeda estrangeira",
    ),
    pytest.param(
        _json(despesa(data="2026-07-15", valor=Decimal("20.00"), moeda="EUR")),
        construir_cambio(taxas={
            "2026-07-13": {"USD": Decimal("5.42"), "EUR": Decimal("5.91")},
            "2026-07-14": {"USD": Decimal("5.44")},
        }),
        _caso_data_intermediaria_sem_a_moeda, id="Data intermediária sem a moeda",
    ),
]


@pytest.mark.parametrize(("texto", "cambio", "verificar"), CASOS_DE_CAMBIO)
def test_caso_de_borda_de_cambio(processar, texto, cambio, verificar):
    """Seção 7 da spec: casos de moeda e conversão (RN-015, RN-003, RN-004,
    RN-008, RN-010) e da ordem das etapas (seção 8)."""
    verificar(processar(texto, None, cambio))


def _cli(*argumentos: str) -> int:
    """`main` da CLI; erro de uso do `argparse` vira o código do `SystemExit`."""
    try:
        return main(list(argumentos))
    except SystemExit as saida:
        return saida.code


_SEM_COLABORADOR = simplejson.dumps(
    {k: v for k, v in construir_entrada().items() if k != "colaborador"}
)
_SAIDA_ANTERIOR = b"saida anterior\n"

CASOS_DA_CLI = [
    # (texto da entrada, saída preexistente?, pasta da saída existe?, usar --output?)
    pytest.param(_json(), False, False, True, id="Saída não gravável"),
    pytest.param(_SEM_COLABORADOR, False, True, True, id="Colaborador ausente"),
    pytest.param(
        _json(colaborador={"id": "", "nome": "Ana"}), False, True, True,
        id="Colaborador com texto vazio",
    ),
    pytest.param(
        _json(colaborador={"id": "c-1", "nome": "  "}), False, True, True,
        id="Colaborador com texto vazio (nome)",
    ),
    pytest.param(_SEM_COLABORADOR, True, True, True, id="Saída preexistente com erro"),
    pytest.param(
        _json(despesa()).replace('"Restaurante"', '"X\\ud800"'), False, True, True,
        id="Escape sem caractere válido",
    ),
    pytest.param(
        _json().replace('"despesas"', '"\\ud800": 1, "despesas"'), False, True, True,
        id="Escape sem caractere válido (chave)",
    ),
    pytest.param(_json(), True, True, False, id="Erro de uso"),
    pytest.param(
        _json(despesa(), centro_custo=17), False, True, True,
        id="Centro de custo de tipo errado",
    ),
]


@pytest.mark.parametrize(
    ("texto", "saida_preexistente", "pasta_existe", "com_output"), CASOS_DA_CLI
)
def test_caso_de_borda_da_cli(tmp_path, texto, saida_preexistente, pasta_existe,
                              com_output):
    """Seção 7 da spec: erro de arquivo (RN-002) e erro de uso (seção 4) terminam
    com código diferente de 0 e não criam nem alteram o arquivo de saída."""
    entrada = tmp_path / "entrada.json"
    entrada.write_text(texto, encoding="utf-8")
    pasta = tmp_path / "saidas"
    if pasta_existe:
        pasta.mkdir()
    saida = pasta / "saida.json"
    if saida_preexistente:
        saida.write_bytes(_SAIDA_ANTERIOR)
    politica = tmp_path / "politica.json"
    politica.write_text(_politica(), encoding="utf-8")
    cambio = tmp_path / "cambio.json"
    cambio.write_text(_cambio(), encoding="utf-8")
    argumentos = ["calcular", "--input", str(entrada), "--politica", str(politica),
                  "--cambio", str(cambio)]
    if com_output:
        argumentos += ["--output", str(saida)]

    assert _cli(*argumentos) != 0
    if saida_preexistente:
        assert saida.read_bytes() == _SAIDA_ANTERIOR
    else:
        assert not saida.exists()


def _politica(**sobrescritas):
    return simplejson.dumps(construir_politica(**sobrescritas), use_decimal=True)


def _cambio(**sobrescritas):
    return simplejson.dumps(construir_cambio(**sobrescritas), use_decimal=True)


def _politica_com(caminho, valor):
    """Política v4 com `valor` no `caminho` (tupla de chaves) → texto JSON."""
    documento = construir_politica()
    alvo = documento
    for chave in caminho[:-1]:
        alvo = alvo[chave]
    alvo[caminho[-1]] = valor
    return simplejson.dumps(documento, use_decimal=True)


def _politica_sem_padrao():
    documento = construir_politica()
    del documento["padrao"]
    return simplejson.dumps(documento, use_decimal=True)


_AUSENTE = None  # arquivo que não existe no disco
_LIMITE = ("padrao", "alimentacao", "limite")

CASOS_DE_POLITICA_E_CAMBIO = [
    # (texto da política, texto do câmbio, argumento omitido)
    pytest.param(
        _politica_com(("centros_custo", "padrao"),
                      construir_politica()["padrao"]),
        _cambio(), None, id="Centro de custo reservado no arquivo",
    ),
    pytest.param(_politica_sem_padrao(), _cambio(), None,
                 id="Política sem tabela padrão"),
    pytest.param(_politica_com(_LIMITE, Decimal("-10")), _cambio(), None,
                 id="Limite inválido na política"),
    pytest.param(_politica_com(_LIMITE, "60"), _cambio(), None,
                 id="Limite inválido na política (texto)"),
    pytest.param(_politica_com(_LIMITE, Decimal("60.005")), _cambio(), None,
                 id="Limite inválido na política (3 casas)"),
    pytest.param(
        _politica_com(("padrao", "alimentacao", "periodicidade"), "mes"),
        _cambio(), None, id="Periodicidade desconhecida",
    ),
    pytest.param(
        _politica(),
        _cambio(taxas={"2026-07-13": {"USD": Decimal("0"), "EUR": Decimal("5.91")}}),
        None, id="Taxa de câmbio não positiva",
    ),
    pytest.param(
        _politica().replace(
            '"padrao": {', '"padrao": {"alimentacao": {"limite": 60.00, '
            '"periodicidade": "dia"}, ', 1,
        ),
        _cambio(), None, id="Chave repetida na política",
    ),
    pytest.param(_politica(), _AUSENTE, None,
                 id="Câmbio ausente com despesas em reais"),
    pytest.param(_politica(), _cambio(), "--politica", id="Sem argumento de política"),
]


@pytest.mark.parametrize(
    ("texto_politica", "texto_cambio", "omitido"), CASOS_DE_POLITICA_E_CAMBIO
)
def test_caso_de_borda_de_politica_e_cambio(tmp_path, capsys, texto_politica,
                                            texto_cambio, omitido):
    """Seção 7 da spec: erro de arquivo na política ou no câmbio (RN-016) e
    chamada sem `--politica` (seção 4, AMB-031) terminam com código diferente
    de 0 e não criam o arquivo de saída."""
    entrada = tmp_path / "entrada.json"
    # todas as despesas em BRL: o câmbio é exigido mesmo assim (AMB-031)
    entrada.write_text(_json(despesa()), encoding="utf-8")
    arquivos = {}
    for argumento, nome, texto in (("--politica", "politica.json", texto_politica),
                                   ("--cambio", "cambio.json", texto_cambio)):
        arquivos[argumento] = tmp_path / nome
        if texto is not _AUSENTE:
            arquivos[argumento].write_text(texto, encoding="utf-8")
    saida = tmp_path / "saida.json"
    argumentos = {"--input": entrada, **arquivos, "--output": saida}
    if omitido is not None:
        del argumentos[omitido]

    assert _cli("calcular", *(str(x) for par in argumentos.items() for x in par)) != 0
    assert not saida.exists()
    if omitido is None:
        # erro de arquivo, não de uso: a mensagem segue a DT-007
        assert capsys.readouterr().err.startswith("erro: ")
