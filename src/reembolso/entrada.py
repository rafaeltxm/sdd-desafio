"""bytes → JSON → Entrada; erros de arquivo e despesas inválidas (RN-002, RN-013)."""

from decimal import Decimal

import simplejson


class ErroDeArquivo(Exception):
    """Erro de arquivo da RN-002: nenhuma saída é gravada."""


def _tem_substituto_isolado(texto: str) -> bool:
    """Caractere entre U+D800 e U+DFFF: escape sem caractere válido (seção 4)."""
    return any("\ud800" <= c <= "\udfff" for c in texto)


def _verificar_textos(valor) -> None:
    """Percorre chaves e textos do documento (DT-002)."""
    if isinstance(valor, str):
        if _tem_substituto_isolado(valor):
            raise ErroDeArquivo("texto com escape que não forma caractere válido")
    elif isinstance(valor, dict):
        for chave, item in valor.items():
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
    try:
        documento = simplejson.loads(texto, use_decimal=True, parse_int=Decimal)
    except simplejson.JSONDecodeError as erro:
        raise ErroDeArquivo(f"arquivo não é JSON válido: {erro}") from erro
    _verificar_textos(documento)
    return documento
