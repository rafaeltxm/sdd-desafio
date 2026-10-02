"""Etapas 2 a 9 da seção 8 da spec: Entrada → Resultado."""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from reembolso.justificativa import justificar
from reembolso.modelo import (
    Despesa,
    DespesaInvalida,
    Entrada,
    ItemResultado,
    Motivo,
    Periodo,
    Resultado,
    Status,
    Totais,
)
from reembolso.politica import (
    CATEGORIAS_RECONHECIDAS,
    LIMITES_DIARIOS,
    VALOR_ACIMA_DO_QUAL_EXIGE_NOTA,
)

CENTAVO = Decimal("0.01")
ZERO = Decimal("0.00")


def arredondar(valor: Decimal) -> Decimal:
    """RN-003: 2 casas, metade afastando do zero (`ROUND_HALF_UP`, DT-001)."""
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def _status(
    considerado: Decimal, reembolsado: Decimal
) -> tuple[Status, Motivo | None]:
    """RN-011 pelos valores; corte do limite → `limite_diario_excedido` (RN-009)."""
    if reembolsado == considerado:
        return Status.APROVADO, None
    if reembolsado > 0:
        return Status.PARCIAL, Motivo.LIMITE_DIARIO_EXCEDIDO
    return Status.RECUSADO, Motivo.LIMITE_DIARIO_EXCEDIDO


def _item_invalido(despesa: DespesaInvalida) -> ItemResultado:
    """Etapa 1 (RN-002): recusado, `entrada_invalida`, sem valor considerado."""
    status, motivo = Status.RECUSADO, Motivo.ENTRADA_INVALIDA
    return ItemResultado(
        id=despesa.id,
        data=despesa.data_texto,
        categoria=despesa.categoria_saida,
        valor_informado=despesa.valor_informado,
        valor_considerado=None,
        valor_reembolsado=ZERO,
        status=status,
        motivo=motivo,
        em_viagem=None,
        limite_diario=None,
        justificativa=justificar(
            status,
            motivo,
            data=None,
            categoria=despesa.categoria_saida,
            valor_considerado=None,
            valor_reembolsado=ZERO,
            limite_diario=None,
        ),
        avisos=despesa.avisos,
    )


def _item_recusado(
    despesa: Despesa, considerado: Decimal, motivo: Motivo
) -> ItemResultado:
    """Etapas 3 a 6: recusado antes do limite diário; não consome limite."""
    status = Status.RECUSADO
    # seção 4: normalizada se reconhecida; senão como veio
    categoria = (
        despesa.categoria
        if despesa.categoria in CATEGORIAS_RECONHECIDAS
        else despesa.categoria_texto
    )
    return ItemResultado(
        id=despesa.id,
        data=despesa.data_texto,
        categoria=categoria,
        valor_informado=despesa.valor_informado,
        valor_considerado=considerado,
        valor_reembolsado=ZERO,
        status=status,
        motivo=motivo,
        em_viagem=None,
        limite_diario=None,
        justificativa=justificar(
            status,
            motivo,
            data=despesa.data,
            categoria=categoria,
            valor_considerado=considerado,
            valor_reembolsado=ZERO,
            limite_diario=None,
        ),
        avisos=despesa.avisos,
    )


def _motivo_de_recusa(
    despesa: Despesa, considerado: Decimal, periodo: Periodo
) -> Motivo | None:
    """Etapas 3 a 6 da seção 8, nesta ordem; a primeira que recusa encerra."""
    if considerado <= 0:  # RN-004
        return Motivo.VALOR_INVALIDO
    if not periodo.inicio <= despesa.data <= periodo.fim:  # RN-005, AMB-009
        return Motivo.FORA_DO_PERIODO
    if despesa.categoria not in CATEGORIAS_RECONHECIDAS:  # RN-006, AMB-012
        return Motivo.CATEGORIA_FORA_DA_POLITICA
    # RN-008, AMB-007, AMB-008: valor individual, antes do limite
    if considerado > VALOR_ACIMA_DO_QUAL_EXIGE_NOTA and not despesa.tem_nota_fiscal:
        return Motivo.NOTA_FISCAL_AUSENTE
    return None


def _aplicar_limite(despesas: list[Despesa]) -> dict[int, ItemResultado]:
    """Etapa 9 (RN-009): saldo por (data, categoria), consumido na ordem da entrada."""
    saldos: dict[tuple[date, str], Decimal] = {}
    itens = {}
    for despesa in sorted(despesas, key=lambda d: d.posicao):
        considerado = arredondar(despesa.valor_informado)
        limite = LIMITES_DIARIOS[despesa.categoria].normal
        chave = (despesa.data, despesa.categoria)
        saldo = saldos.get(chave, limite)
        reembolsado = min(considerado, saldo)
        saldos[chave] = saldo - reembolsado
        status, motivo = _status(considerado, reembolsado)
        itens[despesa.posicao] = ItemResultado(
            id=despesa.id,
            data=despesa.data_texto,
            categoria=despesa.categoria,
            valor_informado=despesa.valor_informado,
            valor_considerado=considerado,
            valor_reembolsado=reembolsado,
            status=status,
            motivo=motivo,
            em_viagem=False,
            limite_diario=limite,
            justificativa=justificar(
                status,
                motivo,
                data=despesa.data,
                categoria=despesa.categoria,
                valor_considerado=considerado,
                valor_reembolsado=reembolsado,
                limite_diario=limite,
            ),
            avisos=despesa.avisos,
        )
    return itens


def _totais(itens: list[ItemResultado]) -> Totais:
    """Seção 4: solicitado e reembolsado somados; glosado = diferença (RN-001).

    O solicitado não soma itens recusados por `entrada_invalida` (RN-002) nem
    com `valor_considerado` ≤ 0 (RN-004).
    """
    solicitado = sum(
        (
            item.valor_considerado
            for item in itens
            if item.motivo is not Motivo.ENTRADA_INVALIDA
            and item.valor_considerado > 0
        ),
        ZERO,
    )
    reembolsado = sum((item.valor_reembolsado for item in itens), ZERO)
    return Totais(
        valor_solicitado=solicitado,
        valor_reembolsado=reembolsado,
        valor_glosado=solicitado - reembolsado,
    )


def calcular(entrada: Entrada) -> Resultado:
    """Um item por despesa, na ordem da entrada (RN-001), e os totais."""
    validas = [d for d in entrada.despesas if isinstance(d, Despesa)]
    por_posicao: dict[int, ItemResultado] = {}
    seguem = []
    for despesa in validas:
        considerado = arredondar(despesa.valor_informado)
        motivo = _motivo_de_recusa(despesa, considerado, entrada.periodo)
        if motivo is None:
            seguem.append(despesa)
        else:
            por_posicao[despesa.posicao] = _item_recusado(despesa, considerado, motivo)
    por_posicao.update(_aplicar_limite(seguem))
    itens = [
        por_posicao[d.posicao] if isinstance(d, Despesa) else _item_invalido(d)
        for d in entrada.despesas
    ]
    return Resultado(
        colaborador=entrada.colaborador,
        periodo=entrada.periodo,
        itens=itens,
        totais=_totais(itens),
        avisos=entrada.avisos,
    )
