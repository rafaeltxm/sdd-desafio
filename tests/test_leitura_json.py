"""Leitura do JSON estrito: RN-002, seção 4 da spec (Entrada), DT-001, DT-002."""

from decimal import Decimal

import pytest

from reembolso.entrada import ErroDeArquivo, ler_json


@pytest.mark.parametrize("literal", ["NaN", "Infinity", "-Infinity"])
def test_rn002_nan_e_erro_de_arquivo(literal):
    """RN-002 / DT-002: NaN e infinitos não são JSON válido → erro de arquivo."""
    with pytest.raises(ErroDeArquivo):
        ler_json(f'{{"valor": {literal}}}'.encode())


@pytest.mark.parametrize(
    "texto",
    [
        b"",
        b"{",
        b'{"valor": 10,}',
        b"{'valor': 10}",
        b'{"valor": 10} {}',
        b'{"valor": 010}',
    ],
)
def test_rn002_json_malformado_e_erro_de_arquivo(texto):
    """RN-002: arquivo que não é JSON válido → erro de arquivo."""
    with pytest.raises(ErroDeArquivo):
        ler_json(texto)


@pytest.mark.parametrize(
    "texto",
    [
        b'{"nome": "Jo\xe3o"}',  # Latin-1, não UTF-8
        b'{"nome": "\xed\xa0\x80"}',  # substituto codificado em bytes
        b'{"nome": "\xc3"}',  # sequência truncada
    ],
)
def test_rn002_utf8_invalido_e_erro_de_arquivo(texto):
    """RN-002 / DT-002: bytes fora do UTF-8 não são JSON → erro de arquivo."""
    with pytest.raises(ErroDeArquivo):
        ler_json(texto)


@pytest.mark.parametrize(
    "texto",
    [
        rb'{"nome": "\ud800"}',
        rb'{"nome": "a\udc00b"}',
        rb'{"despesas": [{"id": "x\ud800"}]}',
        rb'{"lista": [["\udfff"]]}',
    ],
)
def test_rn002_escape_sem_par_em_valor_e_erro_de_arquivo(texto):
    """RN-002 / seção 4: escape sem caractere válido em valor → erro de arquivo."""
    with pytest.raises(ErroDeArquivo):
        ler_json(texto)


@pytest.mark.parametrize(
    "texto",
    [
        rb'{"\ud800": 1}',
        rb'{"despesas": [{"a\udc00": "x"}]}',
    ],
)
def test_rn002_escape_sem_par_em_chave_e_erro_de_arquivo(texto):
    """RN-002 / seção 4: escape sem caractere válido em chave → erro de arquivo."""
    with pytest.raises(ErroDeArquivo):
        ler_json(texto)


def test_bom_e_aceito():
    """DT-002: BOM UTF-8 no início é ignorado (RFC 8259)."""
    documento = ler_json(b'\xef\xbb\xbf{"nome": "Jo\xc3\xa3o"}')
    assert documento == {"nome": "João"}


@pytest.mark.parametrize(
    "literal, esperado",
    [
        ("33.333", Decimal("33.333")),
        ("999999999.99999999999", Decimal("999999999.99999999999")),
        ("1e999999", Decimal("1e999999")),
        ("1e-999999", Decimal("1e-999999")),
        ("5" * 5000, Decimal("5" * 5000)),
        ("10", Decimal("10")),
    ],
)
def test_numero_lido_pelo_valor_exato(literal, esperado):
    """Seção 4 / DT-001: número vale pelo valor decimal exato escrito no arquivo."""
    documento = ler_json(f'{{"valor": {literal}}}'.encode())
    valor = documento["valor"]
    assert type(valor) is Decimal
    # comparação exata entre Decimal, sem arredondamento de contexto
    assert valor.compare_total(esperado) == Decimal(0)


def test_escapes_validos_decodificados():
    """Seção 4: texto vale depois de decodificados os escapes; emoji em par = direto."""
    documento = ler_json(
        rb'{"data": "2026\u002d07\u002d03", "emoji": "\ud83d\ude00"}'
    )
    assert documento["data"] == "2026-07-03"
    # U+1F600 escrito como par de escapes é o mesmo caractere escrito direto
    assert documento["emoji"] == "\U0001f600"
    assert documento["emoji"] == ler_json('{"e": "😀"}'.encode())["e"]
