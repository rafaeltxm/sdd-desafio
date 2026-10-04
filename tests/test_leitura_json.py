"""Leitura do JSON estrito: RN-002, seção 4 da spec (Entrada), DT-001, DT-002."""

from decimal import Decimal

import pytest

from reembolso.leitura import ErroDeArquivo, ler_json


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
        b'{"valor": 01.5}',
        b'{"valor": .5}',
        b'{"valor": 1.}',
        b'{"valor": +1}',
        b'{"obs": "a\tb"}',  # tabulação crua dentro do texto
        b'{"obs": "a\nb"}',  # quebra de linha crua dentro do texto
        b'{"obs": "a\x00b"}',  # U+0000 cru dentro do texto
    ],
)
def test_rn002_json_malformado_e_erro_de_arquivo(texto):
    """RN-002 / D-006: não é JSON válido pela RFC 8259 → erro de arquivo."""
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
        rb'{"nome": "\udc00\ud800"}',  # par em ordem invertida
        b'{"nome": "\\ud800\xf0\x9f\x98\x80"}',  # alto solto antes de emoji cru
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


@pytest.mark.parametrize(
    "texto",
    [
        rb'{"obs": "\ud800", "obs": "ok"}',
        rb'{"despesas": [{"obs": {"x": "\ud800"}, "obs": "ok"}]}',
        rb'{"extra": {"\udc00": 1}, "extra": {}}',
    ],
)
def test_rn002_escape_sem_par_em_ocorrencia_descartada_e_erro_de_arquivo(texto):
    """RN-002 / RN-013 / D-006: escape inválido em ocorrência descartada → erro."""
    with pytest.raises(ErroDeArquivo):
        ler_json(texto)


@pytest.mark.parametrize(
    "escape, caractere",
    [(r"\u0000", "\x00"), (r"\uffff", "\uffff"), (r"\ufdd0", "\ufdd0")],
)
def test_escape_fora_dos_substitutos_forma_caractere_valido(escape, caractere):
    """Seção 4 / D-006: só U+D800 a U+DFFF sem par são inválidos; o resto é válido."""
    documento = ler_json(f'{{"obs": "{escape}"}}'.encode())
    assert documento["obs"] == caractere


def test_segundo_bom_e_erro_de_arquivo():
    """Seção 4 / D-006: só um BOM no início é ignorado; o segundo é erro."""
    with pytest.raises(ErroDeArquivo):
        ler_json(b'\xef\xbb\xbf\xef\xbb\xbf{"a": 1}')


@pytest.mark.parametrize("niveis", [5_000, 100_000])
def test_aninhamento_exagerado_e_erro_de_arquivo(niveis):
    """Seção 10 / D-006: aninhamento de milhares de níveis → erro de arquivo."""
    texto = b'{"extra": ' + b"[" * niveis + b"]" * niveis + b"}"
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
