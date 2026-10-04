"""Testes de tipo e chaves repetidas de `leitura.py`: DT-003, DT-010."""

from decimal import Decimal

import pytest

from reembolso.leitura import (
    ErroDeArquivo,
    e_codigo_de_moeda,
    ler_json,
    rejeitar_chaves_repetidas,
    tem_ate_2_casas,
)


def test_e_codigo_de_moeda_aceita_3_maiusculas():
    """DT-003: `EUR` casa [A-Z]{3} inteiro → código de moeda."""
    assert e_codigo_de_moeda("EUR")


@pytest.mark.parametrize(
    "valor",
    [
        "eur",  # minúsculas: sem normalização (AMB-025)
        " EUR",  # espaço na ponta
        "EUR\n",  # `fullmatch`, não `$`
        "EURO",  # 4 letras
        "R$",  # símbolo, 2 caracteres
        "",
        978,  # código numérico ISO não é texto
        "ÉUR",  # letra fora do intervalo ASCII A-Z
    ],
)
def test_e_codigo_de_moeda_recusa_fora_do_formato(valor):
    """DT-003: só `str` com exatamente 3 letras de A a Z."""
    assert not e_codigo_de_moeda(valor)


@pytest.mark.parametrize("texto", ["60.000", "6E1", "0"])
def test_tem_ate_2_casas_compara_pelo_valor_exato(texto):
    """DT-003: 60.000 = 60,00 e 6E1 = 60 → no máximo 2 casas pelo valor."""
    assert tem_ate_2_casas(Decimal(texto))


@pytest.mark.parametrize("texto", ["60.005", "1E-999999"])
def test_tem_ate_2_casas_recusa_mais_de_2_casas(texto):
    """DT-003: 60,005 tem 3 casas; 10^-999999 é diferente de 0,00."""
    assert not tem_ate_2_casas(Decimal(texto))


@pytest.mark.parametrize(
    ("texto", "caminho"),
    [
        (b'{"versao": "4", "versao": "5"}', "versao"),
        (b'{"taxas": {"2026-07-01": {"EUR": 6, "EUR": 7}}}', "taxas.2026-07-01.EUR"),
        (b'{"taxas": [{"a": 1}, {"b": 1, "b": 2}]}', "taxas[1].b"),
    ],
    ids=["topo", "aninhado", "dentro_de_lista"],
)
def test_rejeitar_chaves_repetidas_levanta_erro_com_caminho(texto, caminho):
    """DT-010: chave repetida em qualquer objeto → erro com o caminho."""
    with pytest.raises(ErroDeArquivo, match=caminho.replace("[", r"\[")):
        rejeitar_chaves_repetidas(ler_json(texto))


def test_rejeitar_chaves_repetidas_ve_valor_descartado():
    """DT-010: percorre todos os pares, inclusive o valor que não valeu."""
    texto = b'{"a": {"x": 1, "x": 2}, "a": 3}'
    with pytest.raises(ErroDeArquivo, match="a.x"):
        rejeitar_chaves_repetidas(ler_json(texto))


def test_rejeitar_chaves_repetidas_sem_repeticao_nao_levanta():
    """DT-010: mesma chave em objetos diferentes não é repetição."""
    texto = b'{"a": {"x": 1}, "b": {"x": 1}, "c": [{"x": 1}, {"x": 2}]}'
    rejeitar_chaves_repetidas(ler_json(texto))
