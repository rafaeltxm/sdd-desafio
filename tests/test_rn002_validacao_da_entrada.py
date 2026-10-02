"""Validação da entrada: RN-002, seção 4 da spec (Entrada), DT-003."""

from datetime import date

import pytest
import simplejson

from reembolso.entrada import ErroDeArquivo, ler_json, validar_cabecalho
from reembolso.modelo import Colaborador


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
