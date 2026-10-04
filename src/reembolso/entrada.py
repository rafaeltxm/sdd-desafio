"""bytes → JSON → Entrada; erros de arquivo e despesas inválidas (RN-002, RN-013)."""

from collections import Counter
from decimal import Decimal

from reembolso.leitura import (
    ErroDeArquivo,
    ObjetoJson,
    e_codigo_de_moeda,
    e_data,
    e_numero,
    ler_json,
    tem_texto,
)
from reembolso.modelo import Colaborador, Despesa, DespesaInvalida, Entrada, Periodo
from reembolso.normalizacao import normalizar_texto
from reembolso.politica import MOEDA_BASE, VALOR_ABSOLUTO_MAXIMO


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
        if not tem_texto(colaborador.get(campo)):
            raise ErroDeArquivo(f"colaborador.{campo} ausente ou vazio")
    centro_custo = colaborador.get("centro_custo")
    if centro_custo is not None and not isinstance(centro_custo, str):
        raise ErroDeArquivo("colaborador.centro_custo não é texto nem nulo")

    periodo = raiz.get("periodo")
    if not isinstance(periodo, dict):
        periodo = {}
    datas = {}
    for campo in ("inicio", "fim"):
        datas[campo] = e_data(periodo.get(campo))
        if datas[campo] is None:
            raise ErroDeArquivo(f"periodo.{campo} ausente ou não é data AAAA-MM-DD")
    if datas["inicio"] > datas["fim"]:
        raise ErroDeArquivo("periodo.inicio posterior a periodo.fim")

    despesas = raiz.get("despesas")
    if not isinstance(despesas, list):
        raise ErroDeArquivo("despesas ausente ou não é lista")

    competencia = periodo.get("competencia")
    return (
        Colaborador(
            id=colaborador["id"], nome=colaborador["nome"], centro_custo=centro_custo
        ),
        Periodo(
            inicio=datas["inicio"],
            fim=datas["fim"],
            inicio_texto=periodo["inicio"],
            fim_texto=periodo["fim"],
            competencia=competencia if isinstance(competencia, str) else None,
        ),
        despesas,
    )


def validar_despesa(
    posicao: int, elemento, avisos: tuple[str, ...]
) -> Despesa | DespesaInvalida:
    """Etapa 1 da seção 8: elemento de `despesas` → `Despesa` ou `DespesaInvalida`.

    Aplica a RN-002 (despesa inválida), o teto da AMB-018 ao número recebido e
    o formato da `moeda` (AMB-025).
    """
    if not isinstance(elemento, dict):
        return DespesaInvalida(posicao, None, None, None, None, None, avisos)

    id_ = elemento.get("id")
    data_texto = elemento.get("data")
    categoria = elemento.get("categoria")
    fornecedor = elemento.get("fornecedor")
    valor = elemento.get("valor")
    tem_nota_fiscal = elemento.get("tem_nota_fiscal")
    # ausente ou nula → BRL; senão comparada como veio, sem normalização (AMB-025)
    moeda = elemento.get("moeda")
    if moeda is None:
        moeda = MOEDA_BASE

    data = e_data(data_texto)
    valida = (
        tem_texto(id_)
        and data is not None
        and tem_texto(categoria)
        and normalizar_texto(categoria) != ""
        and tem_texto(fornecedor)
        and normalizar_texto(fornecedor) != ""
        and e_numero(valor)
        # `copy_abs` é exato, sem o arredondamento do contexto decimal
        and Decimal(valor).copy_abs() < VALOR_ABSOLUTO_MAXIMO
        and type(tem_nota_fiscal) is bool
        and e_codigo_de_moeda(moeda)
    )
    if not valida:
        return DespesaInvalida(
            posicao=posicao,
            id=id_ if isinstance(id_, str) else None,
            data_texto=data_texto if isinstance(data_texto, str) else None,
            categoria_texto=categoria if isinstance(categoria, str) else None,
            valor_informado=Decimal(valor) if e_numero(valor) else None,
            moeda_saida=moeda if isinstance(moeda, str) else None,
            avisos=avisos,
        )
    return Despesa(
        posicao=posicao,
        id=id_,
        data=data,
        data_texto=data_texto,
        categoria_texto=categoria,
        categoria=normalizar_texto(categoria),
        fornecedor=normalizar_texto(fornecedor),
        valor_informado=Decimal(valor),
        moeda=moeda,
        tem_nota_fiscal=tem_nota_fiscal,
        avisos=avisos,
    )


def ler_entrada(conteudo: bytes) -> Entrada:
    """Bytes → `Entrada`: cabeçalho, despesas validadas e avisos (RN-002, RN-013)."""
    documento = ler_json(conteudo)
    colaborador, periodo, despesas = validar_cabecalho(documento)
    avisos_topo, avisos_por_despesa = avisos_de_chave_repetida(documento)
    return Entrada(
        colaborador=colaborador,
        periodo=periodo,
        despesas=[
            validar_despesa(posicao, elemento, avisos)
            for posicao, (elemento, avisos) in enumerate(
                zip(despesas, avisos_por_despesa, strict=True)
            )
        ],
        avisos=avisos_topo,
    )
