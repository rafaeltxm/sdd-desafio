"""Forma comum aos três arquivos: JSON estrito, escapes e testes de tipo (DT-011)."""

import re
from collections import Counter
from datetime import date
from decimal import Decimal

import simplejson


class ErroDeArquivo(Exception):
    """Erro de arquivo da RN-002 e da RN-016: nenhuma saída é gravada."""


class ObjetoJson(dict):
    """Objeto JSON: vale a última ocorrência de cada chave; guarda os pares (DT-010)."""

    def __init__(self, pares):
        super().__init__(pares)
        self.pares = tuple(pares)


def _tem_substituto_isolado(texto: str) -> bool:
    """Caractere entre U+D800 e U+DFFF: escape sem caractere válido (seção 4)."""
    return any("\ud800" <= c <= "\udfff" for c in texto)


def _verificar_textos(valor) -> None:
    """Percorre chaves e textos do documento, inclusive descartados (DT-002, D-006)."""
    if isinstance(valor, str):
        if _tem_substituto_isolado(valor):
            raise ErroDeArquivo("texto com escape que não forma caractere válido")
    elif isinstance(valor, ObjetoJson):
        for chave, item in valor.pares:
            _verificar_textos(chave)
            _verificar_textos(item)
    elif isinstance(valor, list):
        for item in valor:
            _verificar_textos(item)


def ler_json(conteudo: bytes):
    """Bytes → documento JSON estrito, números em `Decimal` (DT-001, DT-002)."""
    try:
        texto = conteudo.decode("utf-8-sig")
    except UnicodeDecodeError as erro:
        raise ErroDeArquivo("arquivo não está em UTF-8 válido") from erro
    if texto.startswith("﻿"):
        # `utf-8-sig` removeu o único BOM ignorado; um segundo é JSON inválido (D-006)
        raise ErroDeArquivo("arquivo não é JSON válido: BOM repetido no início")
    try:
        documento = simplejson.loads(
            texto,
            use_decimal=True,
            parse_int=Decimal,
            object_pairs_hook=ObjetoJson,
        )
        _verificar_textos(documento)
    except simplejson.JSONDecodeError as erro:
        raise ErroDeArquivo(f"arquivo não é JSON válido: {erro}") from erro
    except RecursionError as erro:
        # limite de aninhamento não fixado pela spec (seção 10, D-006)
        raise ErroDeArquivo("arquivo com aninhamento profundo demais") from erro
    return documento


def _filho(caminho: str | None, chave: str) -> str:
    """Chaves separadas por ponto; `None` é o início (a chave `""` é uma chave)."""
    return chave if caminho is None else f"{caminho}.{chave}"


def rejeitar_chaves_repetidas(valor, caminho: str | None = None) -> None:
    """Chave repetida em qualquer objeto → `ErroDeArquivo` com o caminho (DT-010).

    Percorre todos os pares, inclusive os valores descartados, na ordem do arquivo.
    """
    if isinstance(valor, ObjetoJson):
        vistas: Counter[str] = Counter()
        for chave, item in valor.pares:
            vistas[chave] += 1
            if vistas[chave] == 2:
                raise ErroDeArquivo(f"chave repetida: {_filho(caminho, chave)}")
            rejeitar_chaves_repetidas(item, _filho(caminho, chave))
    elif isinstance(valor, list):
        for posicao, item in enumerate(valor):
            rejeitar_chaves_repetidas(item, f"{caminho or ''}[{posicao}]")


_FORMATO_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_FORMATO_MOEDA = re.compile(r"[A-Z]{3}")


def e_numero(valor) -> bool:
    """Número JSON: `Decimal` ou `int`, e não `bool` (DT-003)."""
    return isinstance(valor, Decimal | int) and not isinstance(valor, bool)


def e_data(valor) -> date | None:
    """Data válida `AAAA-MM-DD` com dígitos ASCII, ou `None` (DT-003)."""
    if not isinstance(valor, str) or not _FORMATO_DATA.fullmatch(valor):
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError:
        return None


def tem_texto(valor) -> bool:
    """Texto com algum caractere fora do espaço em branco (White_Space, RN-002).

    `str.isspace()` também aceita U+001C a U+001F, que não são White_Space (DT-003).
    """
    return isinstance(valor, str) and any(
        not c.isspace() or c in "\x1c\x1d\x1e\x1f" for c in valor
    )


def e_codigo_de_moeda(valor) -> bool:
    """`str` com exatamente 3 letras de A a Z, sem normalização (DT-003, AMB-025)."""
    return isinstance(valor, str) and _FORMATO_MOEDA.fullmatch(valor) is not None


def tem_ate_2_casas(valor: Decimal) -> bool:
    """No máximo 2 casas decimais pelo valor exato: `60.000` sim, `60.005` não (DT-003).

    Chamar só depois do teto da RN-016, que garante que o `quantize` cabe na precisão.
    """
    return valor == valor.quantize(Decimal("0.01"))
