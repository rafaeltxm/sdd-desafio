"""Aritmética de `Decimal` usada pelo motor e pela política (DT-012, DT-013)."""

from contextlib import AbstractContextManager
from decimal import (
    MAX_EMAX,
    MAX_PREC,
    MIN_EMIN,
    ROUND_DOWN,
    ROUND_HALF_UP,
    Context,
    Decimal,
    Inexact,
    InvalidOperation,
    Rounded,
    localcontext,
)

CENTAVO = Decimal("0.01")


def contexto_exato() -> AbstractContextManager[Context]:
    """DT-012: contexto local em que soma, subtração e multiplicação são exatas.

    Precisão e expoentes máximos; conta inexata levanta exceção em vez de
    arredondar em silêncio.
    """
    return localcontext(
        Context(
            prec=MAX_PREC,
            Emin=MIN_EMIN,
            Emax=MAX_EMAX,
            traps=[Inexact, Rounded, InvalidOperation],
        )
    )


def _quantizar(valor: Decimal, modo: str) -> Decimal:
    """`quantize` ao centavo no contexto exato; o arredondamento é o pedido."""
    with contexto_exato() as contexto:
        contexto.traps[Inexact] = contexto.traps[Rounded] = False
        return valor.quantize(CENTAVO, rounding=modo)


def arredondar(valor: Decimal) -> Decimal:
    """RN-003: 2 casas, metade afastando do zero (`ROUND_HALF_UP`, DT-001)."""
    return _quantizar(valor, ROUND_HALF_UP)


def truncar(valor: Decimal) -> Decimal:
    """RN-009 / DT-013: 2 casas, descartando as demais (`ROUND_DOWN`)."""
    return _quantizar(valor, ROUND_DOWN)
