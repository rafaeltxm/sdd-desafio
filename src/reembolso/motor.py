"""Etapas 2 a 9 da seção 8 da spec: Entrada → Resultado."""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from reembolso.justificativa import justificar
from reembolso.modelo import (
    Despesa,
    Entrada,
    ItemResultado,
    Motivo,
    Resultado,
    Status,
    Totais,
)
from reembolso.politica import LIMITES_DIARIOS

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


def _aplicar_limite(despesas: list[Despesa]) -> list[ItemResultado]:
    """Etapa 9 (RN-009): saldo por (data, categoria), consumido na ordem da entrada."""
    saldos: dict[tuple[date, str], Decimal] = {}
    itens = []
    for despesa in sorted(despesas, key=lambda d: d.posicao):
        considerado = arredondar(despesa.valor_informado)
        limite = LIMITES_DIARIOS[despesa.categoria].normal
        chave = (despesa.data, despesa.categoria)
        saldo = saldos.get(chave, limite)
        reembolsado = min(considerado, saldo)
        saldos[chave] = saldo - reembolsado
        status, motivo = _status(considerado, reembolsado)
        itens.append(
            ItemResultado(
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
                avisos=(),
            )
        )
    return itens


def _totais(itens: list[ItemResultado]) -> Totais:
    """Seção 4: solicitado e reembolsado somados; glosado = diferença (RN-001)."""
    solicitado = sum((item.valor_considerado for item in itens), ZERO)
    reembolsado = sum((item.valor_reembolsado for item in itens), ZERO)
    return Totais(
        valor_solicitado=solicitado,
        valor_reembolsado=reembolsado,
        valor_glosado=solicitado - reembolsado,
    )


def calcular(entrada: Entrada) -> Resultado:
    """Um item por despesa, na ordem da entrada (RN-001), e os totais."""
    itens = _aplicar_limite(entrada.despesas)
    return Resultado(
        colaborador=entrada.colaborador,
        periodo=entrada.periodo,
        itens=itens,
        totais=_totais(itens),
        avisos=(),
    )
