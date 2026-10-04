"""Chave repetida no arquivo de entrada: RN-013, AMB-019, DT-010 (nível da leitura)."""

from decimal import Decimal

from reembolso.entrada import avisos_de_chave_repetida
from reembolso.leitura import ler_json


def _aviso(caminho, n):
    return f"chave repetida: {caminho} ({n} ocorrências; valeu a última)"


def _documento(despesas="[]", colaborador='{"id": "c-1", "nome": "Ana"}'):
    """Texto JSON da raiz com os trechos dados escritos literalmente."""
    return (
        '{"colaborador": ' + colaborador + ", "
        '"periodo": {"inicio": "2026-07-01", "fim": "2026-07-31"}, '
        '"despesas": ' + despesas + "}"
    )


def _despesa(campos):
    """Despesa com os campos obrigatórios seguidos de `campos` escritos literalmente."""
    return (
        '{"id": "d-1", "data": "2026-07-03", "categoria": "alimentacao", '
        '"fornecedor": "Restaurante", "tem_nota_fiscal": true, ' + campos + "}"
    )


def _ler(texto):
    documento = ler_json(texto.encode())
    topo, por_despesa = avisos_de_chave_repetida(documento)
    return documento, topo, por_despesa


def test_rn013_valor_duas_vezes_vale_a_ultima_com_aviso_no_elemento():
    """RN-013 / AMB-019: vale a última ocorrência; aviso no item, caminho relativo."""
    documento, topo, por_despesa = _ler(
        _documento("[" + _despesa('"valor": 30.00, "valor": 50.00') + "]")
    )
    # 30.00 e depois 50.00 → vale 50.00
    assert documento["despesas"][0]["valor"] == Decimal("50.00")
    assert por_despesa == ((_aviso("valor", 2),),)
    assert topo == ()


def test_rn013_colaborador_nome_repetido_avisa_no_topo_com_caminho_da_raiz():
    """RN-013: chave repetida fora das despesas → aviso no topo, caminho da raiz."""
    documento, topo, por_despesa = _ler(
        _documento(
            "[" + _despesa('"valor": 10.00') + "]",
            colaborador='{"id": "c-1", "nome": "Ana", "nome": "Bia"}',
        )
    )
    assert documento["colaborador"]["nome"] == "Bia"
    assert topo == (_aviso("colaborador.nome", 2),)
    # item sem chave repetida → avisos vazio
    assert por_despesa == ((),)


def test_rn013_valor_tres_vezes_gera_um_aviso_com_3_ocorrencias():
    """RN-013: um aviso por chave repetida, qualquer que seja o número de repetições."""
    documento, _, por_despesa = _ler(
        _documento("[" + _despesa('"valor": 1, "valor": 2, "valor": 3') + "]")
    )
    assert documento["despesas"][0]["valor"] == Decimal(3)
    assert por_despesa == ((_aviso("valor", 3),),)


def test_rn013_despesas_repetida_so_ultima_lista_e_um_aviso_no_topo():
    """RN-013: chaves repetidas dentro de valor descartado não geram aviso."""
    primeira = "[" + _despesa('"valor": 1, "valor": 2') + "]"
    ultima = (
        "[" + _despesa('"valor": 5') + ", " + _despesa('"valor": 6, "valor": 7') + "]"
    )
    texto = (
        '{"colaborador": {"id": "c-1", "nome": "Ana"}, '
        '"periodo": {"inicio": "2026-07-01", "fim": "2026-07-31"}, '
        '"despesas": ' + primeira + ", "
        '"despesas": ' + ultima + "}"
    )
    documento, topo, por_despesa = _ler(texto)
    # só a última lista (2 despesas: 5 e 7) é avaliada
    assert [d["valor"] for d in documento["despesas"]] == [Decimal(5), Decimal(7)]
    # o `valor` repetido da primeira lista não gera aviso; o da última vai ao item
    assert topo == (_aviso("despesas", 2),)
    assert por_despesa == ((), (_aviso("valor", 2),))


def test_rn013_aninhada_no_descartado_e_no_que_valeu_ordem_da_primeira_ocorrencia():
    """RN-013: ordem da 1ª ocorrência; descartado não entra no <n> nem na ordem."""
    campos = (
        '"valor": 10, "extra": {"x": 1, "x": 2}, "obs": "a", "obs": "b", '
        '"extra": {"x": 3, "x": 4}'
    )
    documento, _, por_despesa = _ler(_documento("[" + _despesa(campos) + "]"))
    # extra (1ª ocorrência antes de obs), obs, extra.x (no valor que valeu)
    assert por_despesa == (
        (_aviso("extra", 2), _aviso("obs", 2), _aviso("extra.x", 2)),
    )
    assert documento["despesas"][0]["extra"] == {"x": Decimal(4)}


def test_rn013_chave_com_escape_e_a_mesma_chave_decodificada():
    """RN-013: igualdade depois de decodificar escapes (`\\u0076alor` = `valor`)."""
    texto = _documento("[" + _despesa('"valor": 30.00, "\\u0076alor": 90.00') + "]")
    documento, _, por_despesa = _ler(texto)
    assert documento["despesas"][0]["valor"] == Decimal("90.00")
    assert por_despesa == ((_aviso("valor", 2),),)


def test_rn013_forma_composta_e_decomposta_sao_chaves_diferentes():
    """RN-013: comparação caractere a caractere, sem normalização Unicode."""
    # "é" (U+00E9) e "e" + U+0301 → duas chaves distintas, nenhum aviso
    campos = '"valor": 10, "\\u00e9": 1, "e\\u0301": 2'
    documento, topo, por_despesa = _ler(_documento("[" + _despesa(campos) + "]"))
    assert documento["despesas"][0]["é"] == Decimal(1)
    assert documento["despesas"][0]["é"] == Decimal(2)
    assert por_despesa == ((),)
    assert topo == ()


def test_rn013_lista_dentro_de_lista_no_caminho():
    """RN-013: colchetes encadeados, sem ponto entre eles (`m[0][0].x`)."""
    campos = '"valor": 10, "m": [[{"x": 1, "x": 2}]]'
    _, _, por_despesa = _ler(_documento("[" + _despesa(campos) + "]"))
    assert por_despesa == ((_aviso("m[0][0].x", 2),),)


def test_rn013_elemento_de_despesas_que_e_lista_comeca_pela_posicao():
    """RN-013: elemento de `despesas` que é lista → caminho começa por `[0]`."""
    _, topo, por_despesa = _ler(_documento('[[{"a": 1, "a": 2}]]'))
    assert por_despesa == ((_aviso("[0].a", 2),),)
    assert topo == ()


def test_rn013_lista_dentro_de_elemento_lista_encadeia_colchetes():
    """RN-013: elemento-lista com lista dentro → `[0][0].a`."""
    _, _, por_despesa = _ler(_documento('[[[{"a": 1, "a": 2}]]]'))
    assert por_despesa == ((_aviso("[0][0].a", 2),),)


def test_rn013_caminho_com_lista_dentro_de_objeto():
    """RN-013: elemento de lista pela posição a partir de 0 (`extra.lista[1].x`)."""
    campos = '"valor": 10, "extra": {"lista": [{}, {"x": 1, "x": 2}]}'
    _, _, por_despesa = _ler(_documento("[" + _despesa(campos) + "]"))
    assert por_despesa == ((_aviso("extra.lista[1].x", 2),),)


def test_rn013_chave_vazia_aparece_no_caminho_com_o_ponto():
    """RN-013: chaves separadas por ponto, sem escape — a chave `""` também conta."""
    campos = '"valor": 10, "": {"x": 1, "x": 2}'
    texto = _documento(
        "[" + _despesa(campos) + "]",
        colaborador='{"id": "c-1", "nome": "Ana", "": {"n": 1, "n": 2}}',
    )
    _, topo, por_despesa = _ler(texto)
    # despesa: "" + "." + "x" → ".x"; raiz: "colaborador" + "." + "" + "." + "n"
    assert por_despesa == ((_aviso(".x", 2),),)
    assert topo == (_aviso("colaborador..n", 2),)


def test_rn013_despesas_fora_da_raiz_avisa_no_topo():
    """RN-013: só elementos de `despesas` da raiz avisam no item; o resto, no topo."""
    _, topo, por_despesa = _ler(
        _documento(
            "[]",
            colaborador='{"id": "c-1", "nome": "Ana", "despesas": [{"a": 1, "a": 2}]}',
        )
    )
    assert topo == (_aviso("colaborador.despesas[0].a", 2),)
    assert por_despesa == ()


def test_rn013_obs_mil_vezes_sem_separador_de_milhar():
    """RN-013: <n> em algarismos, sem separador de milhar."""
    campos = '"valor": 10, ' + ", ".join(f'"obs": "{i}"' for i in range(1000))
    documento, _, por_despesa = _ler(_documento("[" + _despesa(campos) + "]"))
    assert documento["despesas"][0]["obs"] == "999"
    assert por_despesa == ((_aviso("obs", 1000),),)


def test_rn013_avisos_de_cada_despesa_ficam_no_proprio_elemento():
    """RN-013: aviso vai para o item da despesa onde a chave se repete."""
    despesas = (
        "["
        + _despesa('"valor": 10')
        + ", null, "
        + _despesa('"valor": 1, "valor": 2')
        + "]"
    )
    _, topo, por_despesa = _ler(_documento(despesas))
    # um item por elemento, inclusive o que não é objeto
    assert por_despesa == ((), (), (_aviso("valor", 2),))
    assert topo == ()


def test_rn013_topo_com_caminho_aninhado_e_ordem_do_arquivo():
    """RN-013: avisos do topo na ordem da primeira ocorrência, caminho da raiz."""
    texto = (
        '{"periodo": {"inicio": "2026-07-01", "inicio": "2026-07-02", '
        '"fim": "2026-07-31"}, '
        '"colaborador": {"id": "c-1", "nome": "Ana", "nome": "Bia"}, '
        '"despesas": []}'
    )
    _, topo, por_despesa = _ler(texto)
    assert topo == (_aviso("periodo.inicio", 2), _aviso("colaborador.nome", 2))
    assert por_despesa == ()


def test_rn013_objeto_sem_repeticao_nenhum_aviso():
    """RN-013: sem chave repetida, nenhum aviso no topo nem nos itens."""
    _, topo, por_despesa = _ler(
        _documento("[" + _despesa('"valor": 10, "extra": {"a": [1, {"b": 2}]}') + "]")
    )
    assert topo == ()
    assert por_despesa == ((),)


# --- Ponta a ponta: avisos na saída (T-012) ---


def test_rn013_saida_valor_repetido_avaliada_com_ultimo_e_aviso_no_item(processar):
    """RN-013 / AMB-019: despesa avaliada com 50,00; aviso em `itens[].avisos`."""
    saida = processar(
        _documento("[" + _despesa('"valor": 30.00, "valor": 50.00') + "]")
    )
    (item,) = saida["itens"]
    # vale 50,00; alimentação fora de viagem, 50,00 ≤ 60,00 → aprovado com 50,00
    assert item["valor_considerado"] == Decimal("50.00")
    assert (item["valor_reembolsado"], item["status"], item["motivo"]) == (
        Decimal("50.00"), "aprovado", None,
    )
    assert item["avisos"] == [_aviso("valor", 2)]
    assert saida["avisos"] == []


def test_rn013_saida_colaborador_nome_repetido_avisa_no_topo_itens_vazios(processar):
    """RN-013: `colaborador.nome` repetido → aviso no topo; itens com `avisos` []."""
    saida = processar(
        _documento(
            "[" + _despesa('"valor": 10.00') + ", "
            + _despesa('"valor": 20.00').replace('"d-1"', '"d-2"') + "]",
            colaborador='{"id": "c-1", "nome": "Ana", "nome": "Bia"}',
        )
    )
    assert saida["colaborador"]["nome"] == "Bia"
    assert saida["avisos"] == [_aviso("colaborador.nome", 2)]
    assert [item["avisos"] for item in saida["itens"]] == [[], []]


def test_rn013_saida_aviso_em_item_recusado_por_entrada_invalida(processar):
    """RN-013: `tem_nota_fiscal` true e depois "sim" → `entrada_invalida` com aviso."""
    despesa = (
        '{"id": "d-1", "data": "2026-07-03", "categoria": "alimentacao", '
        '"fornecedor": "Restaurante", "valor": 10.00, '
        '"tem_nota_fiscal": true, "tem_nota_fiscal": "sim"}'
    )
    saida = processar(_documento("[" + despesa + "]"))
    (item,) = saida["itens"]
    # vale "sim" (não booleano) → RN-002: recusado, `entrada_invalida`
    assert (item["status"], item["motivo"]) == ("recusado", "entrada_invalida")
    assert item["valor_considerado"] is None
    assert item["avisos"] == [_aviso("tem_nota_fiscal", 2)]


def test_rn013_saida_chave_com_escape_parcial_com_aviso(processar):
    """RN-013 / RN-009: `valor` 30,00 e `\\u0076alor` 90,00 → parcial 60,00, aviso."""
    saida = processar(
        _documento("[" + _despesa('"valor": 30.00, "\\u0076alor": 90.00') + "]")
    )
    (item,) = saida["itens"]
    # vale 90,00; alimentação fora de viagem: min(90,00; 60,00) = 60,00 → parcial
    assert item["valor_considerado"] == Decimal("90.00")
    assert (item["valor_reembolsado"], item["status"], item["motivo"]) == (
        Decimal("60.00"), "parcial", "limite_diario_excedido",
    )
    assert item["avisos"] == [_aviso("valor", 2)]


def test_rn013_saida_aviso_nao_muda_status_motivo_nem_valores(processar):
    """RN-013: a mesma despesa com e sem chave repetida dá o mesmo resultado."""
    # `obs` repetida não entra em regra: só `avisos` difere
    com = processar(
        _documento("[" + _despesa('"valor": 75.00, "obs": 1, "obs": 2') + "]")
    )
    sem = processar(_documento("[" + _despesa('"valor": 75.00, "obs": 2') + "]"))
    (item_com,), (item_sem,) = com["itens"], sem["itens"]
    assert item_com["avisos"] == [_aviso("obs", 2)]
    assert {**item_com, "avisos": []} == item_sem
    assert com["totais"] == sem["totais"]


def test_rn013_saida_aviso_em_item_recusado_por_limite(processar):
    """RN-013 / RN-009: aviso aparece também em item recusado pelo limite diário."""
    primeira = _despesa('"valor": 60.00')
    segunda = _despesa('"valor": 10.00, "obs": "a", "obs": "b"').replace(
        '"d-1"', '"d-2"'
    )
    saida = processar(_documento("[" + primeira + ", " + segunda + "]"))
    a, b = saida["itens"]
    # 60,00 consome o limite de 60,00; a segunda: min(10,00; 0,00) = 0 → recusado
    assert (a["status"], a["avisos"]) == ("aprovado", [])
    assert (b["valor_reembolsado"], b["status"], b["motivo"]) == (
        Decimal("0"), "recusado", "limite_diario_excedido",
    )
    assert b["avisos"] == [_aviso("obs", 2)]
