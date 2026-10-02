"""bytes → JSON → Entrada; erros de arquivo e despesas inválidas (RN-002, RN-013)."""

import re
from collections import Counter
from datetime import date
from decimal import Decimal

import simplejson

from reembolso.modelo import Colaborador, Periodo


class ErroDeArquivo(Exception):
    """Erro de arquivo da RN-002: nenhuma saída é gravada."""


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
    if texto.startswith("\ufeff"):
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


def _aviso(caminho: str, n: int) -> str:
    return f"chave repetida: {caminho} ({n} ocorrências; valeu a última)"


def _filho(caminho: str | None, chave: str) -> str:
    """Chaves separadas por ponto; `None` é o início (a chave `""` é uma chave)."""
    return chave if caminho is None else f"{caminho}.{chave}"


def _percorrer(valor, caminho: str | None, avisos: list[str], ao_descer=None) -> None:
    """Avisos de chave repetida em `valor`, na ordem do arquivo (RN-013, DT-010).

    Avisa na primeira ocorrência de cada chave repetida e desce só no valor da
    última, na posição dela; valores descartados nunca são visitados.
    """
    if isinstance(valor, ObjetoJson):
        ocorrencias = Counter(chave for chave, _ in valor.pares)
        vistas: Counter[str] = Counter()
        for chave, _ in valor.pares:
            vistas[chave] += 1
            if vistas[chave] == 1 and ocorrencias[chave] > 1:
                avisos.append(_aviso(_filho(caminho, chave), ocorrencias[chave]))
            if vistas[chave] == ocorrencias[chave]:
                if ao_descer is None or not ao_descer(chave, valor[chave]):
                    _percorrer(valor[chave], _filho(caminho, chave), avisos)
    elif isinstance(valor, list):
        for posicao, item in enumerate(valor):
            _percorrer(item, f"{caminho or ''}[{posicao}]", avisos)


def avisos_de_chave_repetida(documento):
    """Avisos da RN-013: (avisos do topo, avisos de cada elemento de `despesas`).

    O topo usa caminho a partir da raiz; cada elemento da lista `despesas` da
    raiz usa caminho a partir da despesa (`valor`, `[0].a`).
    """
    topo: list[str] = []
    por_despesa: list[tuple[str, ...]] = []

    def separar_despesas(chave, valor) -> bool:
        if chave != "despesas" or not isinstance(valor, list):
            return False
        for elemento in valor:
            avisos: list[str] = []
            _percorrer(elemento, None, avisos)
            por_despesa.append(tuple(avisos))
        return True

    _percorrer(documento, None, topo, ao_descer=separar_despesas)
    return tuple(topo), tuple(por_despesa)


_FORMATO_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def _data(valor) -> date | None:
    """Data válida `AAAA-MM-DD` com dígitos ASCII, ou `None` (DT-003)."""
    if not isinstance(valor, str) or not _FORMATO_DATA.fullmatch(valor):
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError:
        return None


def _tem_texto(valor) -> bool:
    """Texto com algum caractere fora do espaço em branco (White_Space, RN-002).

    `str.isspace()` também aceita U+001C a U+001F, que não são White_Space (DT-003).
    """
    return isinstance(valor, str) and any(
        not c.isspace() or c in "\x1c\x1d\x1e\x1f" for c in valor
    )


def validar_cabecalho(documento) -> tuple[Colaborador, Periodo, list]:
    """`colaborador`, `periodo` e `despesas` da raiz; erro → `ErroDeArquivo` (RN-002).

    Valida só os valores que valeram por chave repetida (RN-013, D-006). Os
    elementos de `despesas` são devolvidos sem validar (etapa 1 da seção 8).
    """
    raiz = documento if isinstance(documento, dict) else {}

    colaborador = raiz.get("colaborador")
    if not isinstance(colaborador, dict):
        raise ErroDeArquivo("colaborador ausente ou não é objeto")
    for campo in ("id", "nome"):
        if not _tem_texto(colaborador.get(campo)):
            raise ErroDeArquivo(f"colaborador.{campo} ausente ou vazio")

    periodo = raiz.get("periodo")
    if not isinstance(periodo, dict):
        periodo = {}
    datas = {}
    for campo in ("inicio", "fim"):
        datas[campo] = _data(periodo.get(campo))
        if datas[campo] is None:
            raise ErroDeArquivo(f"periodo.{campo} ausente ou não é data AAAA-MM-DD")
    if datas["inicio"] > datas["fim"]:
        raise ErroDeArquivo("periodo.inicio posterior a periodo.fim")

    despesas = raiz.get("despesas")
    if not isinstance(despesas, list):
        raise ErroDeArquivo("despesas ausente ou não é lista")

    competencia = periodo.get("competencia")
    return (
        Colaborador(id=colaborador["id"], nome=colaborador["nome"]),
        Periodo(
            inicio=datas["inicio"],
            fim=datas["fim"],
            inicio_texto=periodo["inicio"],
            fim_texto=periodo["fim"],
            competencia=competencia if isinstance(competencia, str) else None,
        ),
        despesas,
    )
