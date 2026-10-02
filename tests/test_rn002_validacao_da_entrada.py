"""Validação da entrada: RN-002, seção 4 da spec (Entrada), DT-003."""

from datetime import date
from decimal import Decimal

import pytest
import simplejson

from reembolso.entrada import ErroDeArquivo, ler_entrada, ler_json, validar_cabecalho
from reembolso.modelo import Colaborador, Despesa, DespesaInvalida


def _validar(documento):
    """Documento → texto JSON → leitura → validação do cabeçalho."""
    texto = simplejson.dumps(documento, use_decimal=True, ensure_ascii=False)
    return validar_cabecalho(ler_json(texto.encode()))


def _validar_texto(texto):
    return validar_cabecalho(ler_json(texto.encode()))


# --- cabeçalho (T-008) ---


def test_rn002_cabecalho_valido_copia_colaborador_e_periodo(entrada):
    """RN-002 / seção 4: cabeçalho válido → colaborador e período copiados."""
    colaborador, periodo, despesas = _validar(entrada())
    assert colaborador == Colaborador(id="c-1", nome="Ana")
    assert periodo.inicio == date(2026, 7, 1)
    assert periodo.fim == date(2026, 7, 31)
    assert periodo.inicio_texto == "2026-07-01"
    assert periodo.fim_texto == "2026-07-31"
    # competencia ausente → nula (seção 4, saída)
    assert periodo.competencia is None
    assert despesas == []


def test_rn002_colaborador_ausente_e_erro_de_arquivo(entrada):
    """RN-002: `colaborador` ausente → erro de arquivo."""
    documento = entrada()
    del documento["colaborador"]
    with pytest.raises(ErroDeArquivo):
        _validar(documento)


@pytest.mark.parametrize("raiz", ["[]", "null", "1", '"x"'])
def test_rn002_raiz_que_nao_e_objeto_nao_tem_colaborador(raiz):
    """RN-002: raiz que não é objeto não tem `colaborador` → erro de arquivo."""
    with pytest.raises(ErroDeArquivo):
        _validar_texto(raiz)


@pytest.mark.parametrize("colaborador", [None, "c-1", ["c-1", "Ana"], 1])
def test_rn002_colaborador_que_nao_e_objeto_nao_tem_id_nome(entrada, colaborador):
    """RN-002: `colaborador` que não é objeto não tem `id`/`nome` → erro."""
    documento = entrada()
    documento["colaborador"] = colaborador
    with pytest.raises(ErroDeArquivo):
        _validar(documento)


@pytest.mark.parametrize("campo", ["id", "nome"])
def test_rn002_colaborador_sem_id_ou_nome_e_erro_de_arquivo(entrada, campo):
    """RN-002: `colaborador` sem `id`/`nome` → erro de arquivo."""
    documento = entrada()
    del documento["colaborador"][campo]
    with pytest.raises(ErroDeArquivo):
        _validar(documento)


@pytest.mark.parametrize("campo", ["id", "nome"])
@pytest.mark.parametrize("valor", [17, True, None, ["Ana"], {"x": "Ana"}])
def test_rn002_colaborador_id_ou_nome_nao_texto_e_erro_de_arquivo(
    entrada, campo, valor
):
    """RN-002: `colaborador.id`/`nome` que não é texto → erro de arquivo."""
    documento = entrada()
    documento["colaborador"][campo] = valor
    with pytest.raises(ErroDeArquivo):
        _validar(documento)


@pytest.mark.parametrize("campo", ["id", "nome"])
@pytest.mark.parametrize(
    "valor",
    [
        "",
        "  ",
        "\t",
        "\n\r",
        "\u0085",  # NEL: White_Space
        " ",  # espaço não separável: White_Space
        "   ",
        " 　",  # espaço eme, espaço ideográfico: White_Space
    ],
)
def test_rn002_colaborador_id_ou_nome_vazio_ou_so_espacos_e_erro_de_arquivo(
    entrada, campo, valor
):
    """RN-002: `id`/`nome` vazio ou só com espaços em branco (White_Space) → erro."""
    documento = entrada()
    documento["colaborador"][campo] = valor
    with pytest.raises(ErroDeArquivo):
        _validar(documento)


@pytest.mark.parametrize(
    "nome",
    [
        "​",  # espaço de largura zero: não é White_Space
        "​​",
        "﻿",  # BOM no meio do texto: não é White_Space
        "\u001f",  # controle sem White_Space
        "\u001c\u001d\u001e",
        " Ana ",  # espaço só nas pontas: há caractere fora do espaço em branco
    ],
)
def test_rn002_nome_sem_white_space_e_valido_e_copiado_como_veio(entrada, nome):
    """RN-002: U+200B, BOM e U+001C a U+001F não são espaço em branco → válido."""
    colaborador, _, _ = _validar(entrada(colaborador={"id": "c-1", "nome": nome}))
    # `nome` não passa pela normalização: copiado como veio (RN-002)
    assert colaborador.nome == nome


def test_rn002_colaborador_id_hifen_e_valido(entrada):
    """RN-002: `id` não é normalizado; `"-"` é texto válido."""
    colaborador, _, _ = _validar(entrada(colaborador={"id": "-", "nome": "Ana"}))
    assert colaborador.id == "-"


def test_rn002_centro_custo_ausente_e_valido(entrada):
    """Seção 4: `colaborador.centro_custo` não é obrigatório."""
    colaborador, _, _ = _validar(entrada(colaborador={"id": "c-1", "nome": "Ana"}))
    assert colaborador == Colaborador(id="c-1", nome="Ana")


def test_rn002_centro_custo_de_qualquer_tipo_e_ignorado(entrada):
    """Seção 4: `centro_custo` não é obrigatório nem usado; tipo não é verificado."""
    colaborador, _, _ = _validar(
        entrada(colaborador={"id": "c-1", "nome": "Ana", "centro_custo": 17})
    )
    assert colaborador == Colaborador(id="c-1", nome="Ana")


@pytest.mark.parametrize("campo", ["inicio", "fim"])
def test_rn002_periodo_sem_inicio_ou_fim_e_erro_de_arquivo(entrada, campo):
    """RN-002: `periodo.inicio` ou `periodo.fim` ausentes → erro de arquivo."""
    documento = entrada()
    del documento["periodo"][campo]
    with pytest.raises(ErroDeArquivo):
        _validar(documento)


def test_rn002_periodo_ausente_e_erro_de_arquivo(entrada):
    """RN-002: sem `periodo` não há `periodo.inicio` → erro de arquivo."""
    documento = entrada()
    del documento["periodo"]
    with pytest.raises(ErroDeArquivo):
        _validar(documento)


@pytest.mark.parametrize("periodo", [None, "2026-07", ["2026-07-01", "2026-07-31"]])
def test_rn002_periodo_que_nao_e_objeto_e_erro_de_arquivo(entrada, periodo):
    """RN-002: `periodo` que não é objeto não tem `inicio`/`fim` → erro de arquivo."""
    documento = entrada()
    documento["periodo"] = periodo
    with pytest.raises(ErroDeArquivo):
        _validar(documento)


@pytest.mark.parametrize("campo", ["inicio", "fim"])
@pytest.mark.parametrize(
    "valor",
    [
        "2026-7-1",  # sem zero à esquerda
        "20260701",  # ISO básico, sem hífens
        "2026-02-30",  # dia inexistente
        "2026-13-01",  # mês inexistente
        "2026-07-01T00:00:00",
        "2026-07-01 ",
        "2026-07-01\n",
        " 2026-07-01",
        "",
        "٢٠٢٦-07-01",  # dígitos arábico-índicos (não ASCII)
        "２０２６-０７-０１",  # dígitos de largura total
        "2026/07/01",
        "01-07-2026",
        20260701,
        None,
        True,
    ],
)
def test_rn002_inicio_ou_fim_que_nao_e_data_aaaa_mm_dd_e_erro_de_arquivo(
    entrada, campo, valor
):
    """RN-002 / DT-003: `inicio`/`fim` que não é data válida `AAAA-MM-DD` → erro."""
    documento = entrada()
    documento["periodo"][campo] = valor
    with pytest.raises(ErroDeArquivo):
        _validar(documento)


def test_rn002_data_com_escapes_e_valida(entrada):
    """Seção 4: texto vale depois de decodificados os escapes (`\\u002d` é `-`)."""
    texto = (
        '{"colaborador": {"id": "c-1", "nome": "Ana"}, '
        '"periodo": {"inicio": "2026\\u002d07\\u002d01", "fim": "2026-07-31"}, '
        '"despesas": []}'
    )
    _, periodo, _ = _validar_texto(texto)
    assert periodo.inicio == date(2026, 7, 1)
    assert periodo.inicio_texto == "2026-07-01"


def test_rn002_inicio_posterior_a_fim_e_erro_de_arquivo(entrada):
    """RN-002: `inicio` posterior a `fim` → erro de arquivo."""
    # 2026-08-01 > 2026-07-31
    with pytest.raises(ErroDeArquivo):
        _validar(entrada(periodo={"inicio": "2026-08-01", "fim": "2026-07-31"}))


def test_rn002_inicio_um_dia_depois_de_fim_e_erro_de_arquivo(entrada):
    """RN-002: `inicio` = `fim` + 1 dia → posterior → erro de arquivo."""
    with pytest.raises(ErroDeArquivo):
        _validar(entrada(periodo={"inicio": "2026-07-02", "fim": "2026-07-01"}))


def test_rn002_inicio_igual_a_fim_e_valido(entrada):
    """RN-002: só `inicio` posterior a `fim` é erro; período de um dia é válido."""
    _, periodo, _ = _validar(
        entrada(periodo={"inicio": "2026-07-15", "fim": "2026-07-15"})
    )
    assert periodo.inicio == periodo.fim == date(2026, 7, 15)


def test_rn002_despesas_ausente_e_erro_de_arquivo(entrada):
    """RN-002: `despesas` ausente → erro de arquivo."""
    documento = entrada()
    del documento["despesas"]
    with pytest.raises(ErroDeArquivo):
        _validar(documento)


@pytest.mark.parametrize("despesas", [None, {}, "[]", 0, True])
def test_rn002_despesas_que_nao_e_lista_e_erro_de_arquivo(entrada, despesas):
    """RN-002: `despesas` que não é lista → erro de arquivo."""
    documento = entrada()
    documento["despesas"] = despesas
    with pytest.raises(ErroDeArquivo):
        _validar(documento)


def test_rn002_despesas_vazia_e_valida(entrada):
    """Seção 4: `despesas` pode ser vazia."""
    _, _, despesas = _validar(entrada(despesas=[]))
    assert despesas == []


def test_rn002_despesas_devolvida_sem_validar_elementos(entrada):
    """RN-002: elemento inválido de `despesas` não é erro de arquivo (etapa 1)."""
    _, _, despesas = _validar(entrada(despesas=[None, 1, {"id": 17}]))
    assert despesas == [None, 1, {"id": 17}]


def test_rn002_competencia_numero_sai_nula_sem_erro(entrada):
    """RN-002 / seção 4: `competencia` 202607 (não texto) → nula, sem erro."""
    _, periodo, _ = _validar(
        entrada(
            periodo={"competencia": 202607, "inicio": "2026-07-01", "fim": "2026-07-31"}
        )
    )
    assert periodo.competencia is None


@pytest.mark.parametrize("competencia", [None, True, ["2026-07"], {"m": 7}])
def test_rn002_competencia_nao_texto_sai_nula_sem_erro(entrada, competencia):
    """RN-002: `competencia` nunca causa erro; se não for texto, sai nula."""
    _, periodo, _ = _validar(
        entrada(
            periodo={
                "competencia": competencia,
                "inicio": "2026-07-01",
                "fim": "2026-07-31",
            }
        )
    )
    assert periodo.competencia is None


@pytest.mark.parametrize("competencia", ["julho", "2026-07", "", "  "])
def test_rn002_competencia_texto_em_qualquer_formato_e_copiada(entrada, competencia):
    """Seção 4: `competencia` copiada se for texto, em qualquer formato."""
    _, periodo, _ = _validar(
        entrada(
            periodo={
                "competencia": competencia,
                "inicio": "2026-07-01",
                "fim": "2026-07-31",
            }
        )
    )
    assert periodo.competencia == competencia


def test_rn002_campos_extras_no_cabecalho_sao_ignorados(entrada):
    """RN-002: campos extras no arquivo são ignorados."""
    documento = entrada()
    documento["versao"] = 2
    documento["colaborador"]["email"] = None
    documento["periodo"]["fuso"] = []
    colaborador, periodo, _ = _validar(documento)
    assert colaborador == Colaborador(id="c-1", nome="Ana")
    assert periodo.inicio == date(2026, 7, 1)


def test_rn002_colaborador_corrigido_por_chave_repetida_valida_so_o_que_valeu():
    """RN-013 / D-006: `nome` `""` corrigido por `nome` `"Ana"` → válido, `Ana`."""
    texto = (
        '{"colaborador": {"id": "c-1", "nome": ""}, '
        '"colaborador": {"id": "c-1", "nome": "Ana"}, '
        '"periodo": {"inicio": "2026-07-01", "fim": "2026-07-31"}, '
        '"despesas": []}'
    )
    colaborador, _, _ = _validar_texto(texto)
    assert colaborador == Colaborador(id="c-1", nome="Ana")


def test_rn002_periodo_corrigido_por_chave_repetida_valida_so_o_que_valeu():
    """RN-013 / D-006: `inicio` inválido corrigido por repetição → vale o último."""
    texto = (
        '{"colaborador": {"id": "c-1", "nome": "Ana"}, '
        '"periodo": {"inicio": "2026-02-30", "inicio": "2026-07-01", '
        '"fim": "2026-07-31"}, '
        '"despesas": []}'
    )
    _, periodo, _ = _validar_texto(texto)
    assert periodo.inicio == date(2026, 7, 1)


def test_rn002_valor_valido_seguido_de_invalido_por_chave_repetida_e_erro():
    """RN-013: vale a última ocorrência; `nome` `"Ana"` depois `""` → erro."""
    texto = (
        '{"colaborador": {"id": "c-1", "nome": "Ana", "nome": ""}, '
        '"periodo": {"inicio": "2026-07-01", "fim": "2026-07-31"}, '
        '"despesas": []}'
    )
    with pytest.raises(ErroDeArquivo):
        _validar_texto(texto)


# --- despesa (T-009) ---

_DATAS_INVALIDAS = [
    "2026-7-3",  # sem zero à esquerda
    "20260703",  # ISO básico, sem hífens
    "2026-02-30",  # dia inexistente
    "2026-13-03",  # mês inexistente
    "2026-07-03T00:00:00",
    "2026-07-03 ",
    " 2026-07-03",
    "",
    "٢٠٢٦-07-03",  # dígitos arábico-índicos (não ASCII)
    "２０２６-０７-０３",  # dígitos de largura total
    "2026/07/03",
    "03-07-2026",
]

_SO_ESPACOS = ["", "  ", "\t", "\n\r", "\u0085", "\u00a0", "\u2003\u3000"]


def _despesas(documento):
    """Documento → texto JSON → `ler_entrada` → despesas validadas."""
    texto = simplejson.dumps(documento, use_decimal=True, ensure_ascii=False)
    return ler_entrada(texto.encode()).despesas


def _uma(entrada, despesa_):
    """Valida uma única despesa dentro de uma entrada mínima."""
    (resultado,) = _despesas(entrada(despesas=[despesa_]))
    return resultado


def test_rn002_despesa_valida_vira_despesa(entrada, despesa):
    """RN-002 / seção 5: válida → `Despesa`; categoria e fornecedor normalizados."""
    resultado = _uma(
        entrada,
        despesa(
            id="d-7",
            data="2026-07-03",
            categoria="Transporte Urbano",
            fornecedor="Padaria (Centro)",
            valor=Decimal("33.333"),
            tem_nota_fiscal=False,
        ),
    )
    assert resultado == Despesa(
        posicao=0,
        id="d-7",
        data=date(2026, 7, 3),
        data_texto="2026-07-03",
        categoria_texto="Transporte Urbano",
        # seção 5: "Transporte Urbano" → transporte_urbano;
        # "Padaria (Centro)" → padaria_centro
        categoria="transporte_urbano",
        fornecedor="padaria_centro",
        # sem arredondamento: valor recebido (seção 4, `valor_informado`)
        valor_informado=Decimal("33.333"),
        tem_nota_fiscal=False,
        avisos=(),
    )


def test_rn002_categoria_nao_reconhecida_nao_e_entrada_invalida(entrada, despesa):
    """RN-002 / seção 8: categoria fora da política é etapa 5, não etapa 1."""
    resultado = _uma(entrada, despesa(categoria="Lavanderia"))
    assert isinstance(resultado, Despesa)
    assert resultado.categoria == "lavanderia"
    assert resultado.categoria_texto == "Lavanderia"


@pytest.mark.parametrize(
    "elemento", [None, 1, Decimal("10.5"), "d-1", True, [], [{"id": "d-1"}]]
)
def test_rn002_elemento_que_nao_e_objeto_e_invalido_com_campos_nulos(
    entrada, elemento
):
    """RN-002: elemento de `despesas` que não é objeto → inválida, campos nulos."""
    resultado = _uma(entrada, elemento)
    assert resultado == DespesaInvalida(
        posicao=0,
        id=None,
        data_texto=None,
        categoria_saida=None,
        valor_informado=None,
        avisos=(),
    )


@pytest.mark.parametrize(
    "campo", ["id", "data", "categoria", "fornecedor", "valor", "tem_nota_fiscal"]
)
def test_rn002_campo_obrigatorio_ausente_e_invalido(entrada, despesa, campo):
    """RN-002: falta campo obrigatório da despesa → `entrada_invalida`."""
    documento = despesa()
    del documento[campo]
    assert isinstance(_uma(entrada, documento), DespesaInvalida)


@pytest.mark.parametrize("data", _DATAS_INVALIDAS)
def test_rn002_data_que_nao_e_aaaa_mm_dd_e_invalida_e_copiada(entrada, despesa, data):
    """RN-002 / DT-003: `data` texto mas não data válida → inválida; texto copiado."""
    resultado = _uma(entrada, despesa(data=data))
    assert isinstance(resultado, DespesaInvalida)
    # seção 4: `data` como veio, se for texto
    assert resultado.data_texto == data


@pytest.mark.parametrize("data", [20260703, None, True, ["2026-07-03"]])
def test_rn002_data_nao_texto_e_invalida_e_sai_nula(entrada, despesa, data):
    """RN-002 / seção 4: `data` que não é texto → inválida, `data` nula."""
    resultado = _uma(entrada, despesa(data=data))
    assert isinstance(resultado, DespesaInvalida)
    assert resultado.data_texto is None


def test_rn002_data_com_escapes_na_despesa_e_valida(entrada):
    """Seção 4: `"2026\\u002d07\\u002d03"` é a data `2026-07-03`."""
    texto = (
        '{"colaborador": {"id": "c-1", "nome": "Ana"}, '
        '"periodo": {"inicio": "2026-07-01", "fim": "2026-07-31"}, '
        '"despesas": [{"id": "d-1", "data": "2026\\u002d07\\u002d03", '
        '"categoria": "alimentacao", "fornecedor": "R", "valor": 10, '
        '"tem_nota_fiscal": true}]}'
    )
    (resultado,) = ler_entrada(texto.encode()).despesas
    assert resultado.data == date(2026, 7, 3)
    assert resultado.data_texto == "2026-07-03"


@pytest.mark.parametrize("valor", ["10", "10.00", True, False, None, [10], {"v": 10}])
def test_rn002_valor_nao_numero_e_invalido_e_sai_nulo(entrada, despesa, valor):
    """RN-002 / DT-003: `valor` não número (inclusive booleano) → inválida, nulo."""
    resultado = _uma(entrada, despesa(valor=valor))
    assert isinstance(resultado, DespesaInvalida)
    # seção 4: `valor_informado` nulo se não numérico
    assert resultado.valor_informado is None


@pytest.mark.parametrize("tem_nota", [1, 0, "sim", "true", None, [True]])
def test_rn002_tem_nota_fiscal_nao_booleano_e_invalido(entrada, despesa, tem_nota):
    """RN-002 / DT-003: `tem_nota_fiscal` não booleano (`1`, `"sim"`) → inválida."""
    assert isinstance(
        _uma(entrada, despesa(tem_nota_fiscal=tem_nota)), DespesaInvalida
    )


@pytest.mark.parametrize("campo", ["id", "categoria", "fornecedor"])
@pytest.mark.parametrize("valor", [17, True, None, ["x"], {"x": "y"}])
def test_rn002_id_categoria_fornecedor_nao_texto_e_invalido(
    entrada, despesa, campo, valor
):
    """RN-002: `id`/`categoria`/`fornecedor` que não é texto → inválida."""
    assert isinstance(_uma(entrada, despesa(**{campo: valor})), DespesaInvalida)


@pytest.mark.parametrize("campo", ["id", "categoria", "fornecedor"])
@pytest.mark.parametrize("valor", _SO_ESPACOS)
def test_rn002_id_categoria_fornecedor_vazio_ou_so_espacos_e_invalido(
    entrada, despesa, campo, valor
):
    """RN-002: `id`/`categoria`/`fornecedor` vazio ou só White_Space → inválida."""
    assert isinstance(_uma(entrada, despesa(**{campo: valor})), DespesaInvalida)


@pytest.mark.parametrize("id_", ["-", "\u200b", "\u200b\u200b", "\ufeff", "\u001f"])
def test_rn002_id_sem_white_space_e_valido_e_copiado_como_veio(entrada, despesa, id_):
    """RN-002: `id` `"-"` ou só de U+200B é válido; `id` não é normalizado."""
    resultado = _uma(entrada, despesa(id=id_))
    assert isinstance(resultado, Despesa)
    assert resultado.id == id_


@pytest.mark.parametrize("campo", ["categoria", "fornecedor"])
@pytest.mark.parametrize("valor", ["-", "***", "\u200b", "²½", "(-_-)", "\U0001f600"])
def test_rn002_categoria_fornecedor_normalizado_vazio_e_invalido(
    entrada, despesa, campo, valor
):
    """RN-002 / seção 5: texto normalizado vazio (`"-"`, `"***"`) → inválida."""
    assert isinstance(_uma(entrada, despesa(**{campo: valor})), DespesaInvalida)


@pytest.mark.parametrize(
    "valor",
    [
        Decimal("1000000000"),  # exatamente o teto: "a partir de" → inválida
        Decimal("1000000000.00"),
        Decimal("1000000000.001"),
        Decimal("-1000000000"),  # valor absoluto
        Decimal("-1E+12"),
        Decimal("1E+999999"),
        Decimal("1" + "0" * 4999),  # inteiro de 5.000 dígitos
    ],
)
def test_amb018_valor_a_partir_de_um_bilhao_e_invalido(entrada, despesa, valor):
    """RN-002 / AMB-018: `abs(valor) >= 1.000.000.000,00` → inválida; valor guardado."""
    resultado = _uma(entrada, despesa(valor=valor))
    assert isinstance(resultado, DespesaInvalida)
    # seção 4: `valor_informado` é o número recebido, exato
    assert resultado.valor_informado == valor


def test_amb018_valor_com_expoente_enorme_lido_do_texto_e_invalido():
    """RN-002 / AMB-018: `1e999999` e `-1e12` escritos no arquivo → inválidas."""
    texto = (
        '{"colaborador": {"id": "c-1", "nome": "Ana"}, '
        '"periodo": {"inicio": "2026-07-01", "fim": "2026-07-31"}, '
        '"despesas": ['
        '{"id": "d-1", "data": "2026-07-03", "categoria": "alimentacao", '
        '"fornecedor": "R", "valor": 1e999999, "tem_nota_fiscal": true}, '
        '{"id": "d-2", "data": "2026-07-03", "categoria": "alimentacao", '
        '"fornecedor": "R", "valor": -1e12, "tem_nota_fiscal": true}]}'
    )
    primeira, segunda = ler_entrada(texto.encode()).despesas
    assert isinstance(primeira, DespesaInvalida)
    assert primeira.valor_informado == Decimal("1E+999999")
    assert isinstance(segunda, DespesaInvalida)
    assert segunda.valor_informado == Decimal("-1E+12")


@pytest.mark.parametrize(
    "valor",
    [
        Decimal("999999999.995"),
        Decimal("999999999.99999999999"),
        Decimal("999999999.99"),
        Decimal("-999999999.99"),  # negativo abaixo do teto: segue (RN-004 decide)
        Decimal("-999999999.995"),  # |valor| < teto antes do arredondamento
        Decimal("0"),
    ],
)
def test_amb018_valor_abaixo_de_um_bilhao_e_valido(entrada, despesa, valor):
    """RN-002 / AMB-018: teto sobre o número recebido, antes do arredondamento."""
    resultado = _uma(entrada, despesa(valor=valor))
    assert isinstance(resultado, Despesa)
    assert resultado.valor_informado == valor


def test_rn002_id_numero_e_invalido_com_id_nulo(entrada, despesa):
    """RN-002: `"id": 17` → inválida, `id` nulo; demais campos copiados."""
    resultado = _uma(entrada, despesa(id=17))
    assert resultado == DespesaInvalida(
        posicao=0,
        id=None,
        data_texto="2026-07-03",
        categoria_saida="alimentacao",
        valor_informado=Decimal("10.00"),
        avisos=(),
    )


@pytest.mark.parametrize("categoria", ["ALIMENTACAO", "Alimentação", " alimentação "])
def test_rn002_categoria_reconhecida_em_despesa_invalida_sai_normalizada(
    entrada, despesa, categoria
):
    """RN-002 / RN-006: `"ALIMENTACAO"` sem `tem_nota_fiscal` → `alimentacao`."""
    documento = despesa(categoria=categoria)
    del documento["tem_nota_fiscal"]
    resultado = _uma(entrada, documento)
    assert isinstance(resultado, DespesaInvalida)
    assert resultado.categoria_saida == "alimentacao"


@pytest.mark.parametrize("categoria", ["Lavanderia", "-", "  ", ""])
def test_rn002_categoria_nao_reconhecida_em_despesa_invalida_sai_como_veio(
    entrada, despesa, categoria
):
    """RN-002 / seção 4: categoria não reconhecida, se texto → como veio."""
    documento = despesa(categoria=categoria)
    del documento["tem_nota_fiscal"]
    resultado = _uma(entrada, documento)
    assert isinstance(resultado, DespesaInvalida)
    assert resultado.categoria_saida == categoria


@pytest.mark.parametrize("categoria", [17, None, ["alimentacao"]])
def test_rn002_categoria_nao_texto_em_despesa_invalida_sai_nula(
    entrada, despesa, categoria
):
    """RN-002 / seção 4: `categoria` que não é texto → nula."""
    resultado = _uma(entrada, despesa(categoria=categoria))
    assert isinstance(resultado, DespesaInvalida)
    assert resultado.categoria_saida is None


def test_rn002_despesa_invalida_guarda_textos_e_valor(entrada, despesa):
    """RN-002 / seção 4: sem `tem_nota_fiscal`, 33.333 → `valor_informado` 33.333."""
    documento = despesa(id="d-9", data="2026-07-05", valor=Decimal("33.333"))
    del documento["tem_nota_fiscal"]
    assert _uma(entrada, documento) == DespesaInvalida(
        posicao=0,
        id="d-9",
        data_texto="2026-07-05",
        categoria_saida="alimentacao",
        valor_informado=Decimal("33.333"),
        avisos=(),
    )


def test_rn002_campo_ausente_sai_nulo_na_despesa_invalida(entrada, despesa):
    """Seção 4: `id`, `data`, `categoria` e `valor` ausentes → nulos."""
    assert _uma(entrada, {"fornecedor": "R", "tem_nota_fiscal": True}) == (
        DespesaInvalida(
            posicao=0,
            id=None,
            data_texto=None,
            categoria_saida=None,
            valor_informado=None,
            avisos=(),
        )
    )


def test_rn002_campo_extra_na_despesa_e_ignorado(entrada, despesa):
    """RN-002: hospedagem com `"noites": 2` e `descricao` → campos ignorados."""
    com_extra = _uma(
        entrada,
        despesa(categoria="hospedagem", noites=2, descricao=None, obs={"a": [1]}),
    )
    sem_extra = _uma(entrada, despesa(categoria="hospedagem"))
    assert isinstance(com_extra, Despesa)
    assert com_extra == sem_extra


def test_rn002_despesas_mantem_posicao_e_ordem(entrada, despesa):
    """RN-001 / RN-002: uma despesa inválida não afeta as demais; ordem mantida."""
    resultado = _despesas(
        entrada(despesas=[despesa(id="a"), None, despesa(id="c", valor="1")])
    )
    assert [type(r) for r in resultado] == [Despesa, DespesaInvalida, DespesaInvalida]
    assert [r.posicao for r in resultado] == [0, 1, 2]
    assert [r.id for r in resultado] == ["a", None, "c"]


def test_rn013_avisos_anexados_a_despesa_valida_e_invalida_e_ao_topo():
    """RN-013: avisos de cada elemento vão para a despesa; os demais, para o topo."""
    texto = (
        '{"colaborador": {"id": "c-1", "nome": "Ana", "nome": "Ana"}, '
        '"periodo": {"inicio": "2026-07-01", "fim": "2026-07-31"}, '
        '"despesas": ['
        '{"id": "d-1", "data": "2026-07-03", "categoria": "alimentacao", '
        '"fornecedor": "R", "valor": 50, "valor": 10, "tem_nota_fiscal": true}, '
        '{"id": "d-2", "id": "d-2"}, '
        '[{"a": 1, "a": 2}]]}'
    )
    entrada_lida = ler_entrada(texto.encode())
    primeira, segunda, terceira = entrada_lida.despesas
    assert entrada_lida.avisos == (
        "chave repetida: colaborador.nome (2 ocorrências; valeu a última)",
    )
    assert isinstance(primeira, Despesa)
    # vale a última: 10
    assert primeira.valor_informado == Decimal("10")
    assert primeira.avisos == (
        "chave repetida: valor (2 ocorrências; valeu a última)",
    )
    assert isinstance(segunda, DespesaInvalida)
    assert segunda.avisos == ("chave repetida: id (2 ocorrências; valeu a última)",)
    # seção 7: elemento-lista → inválida, aviso `[0].a`
    assert isinstance(terceira, DespesaInvalida)
    assert terceira.avisos == ("chave repetida: [0].a (2 ocorrências; valeu a última)",)


def test_rn002_ler_entrada_devolve_colaborador_e_periodo(entrada):
    """RN-002: `ler_entrada` junta cabeçalho validado, despesas e avisos."""
    lida = ler_entrada(
        simplejson.dumps(entrada(), use_decimal=True).encode()
    )
    assert lida.colaborador == Colaborador(id="c-1", nome="Ana")
    assert lida.periodo.inicio == date(2026, 7, 1)
    assert lida.despesas == []
    assert lida.avisos == ()


def test_rn002_ler_entrada_propaga_erro_de_arquivo(entrada):
    """RN-002: erro de arquivo do cabeçalho continua erro de arquivo."""
    documento = entrada()
    del documento["colaborador"]
    with pytest.raises(ErroDeArquivo):
        ler_entrada(simplejson.dumps(documento).encode())
