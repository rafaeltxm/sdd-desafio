"""Frase em português para cada item (texto não contratual)."""

from datetime import date
from decimal import Decimal

from reembolso.modelo import Motivo, Status


def formatar_reais(valor: Decimal) -> str:
    """`Decimal` como `1.234,56`, sem `locale` (DT-009)."""
    return format(valor, ",.2f").translate(str.maketrans(",.", ".,"))


def formatar_data(data: date) -> str:
    """Data como `DD/MM`, sem `locale` (DT-009)."""
    return f"{data.day:02d}/{data.month:02d}"


def justificar(
    status: Status,
    motivo: Motivo | None,
    *,
    data: date | None,
    categoria: str | None,
    valor_considerado: Decimal | None,
    valor_reembolsado: Decimal,
    limite_diario: Decimal | None,
    nota_fiscal_acima_de: Decimal,
) -> str:
    """Frase de um item já decidido, a partir dos seus campos contratuais.

    `nota_fiscal_acima_de` é o mínimo da nota da política (DT-009). Nenhuma
    decisão depende deste texto (plan seção 3).
    """
    if status is Status.APROVADO:
        return (
            f"Aprovado integralmente: {formatar_reais(valor_considerado)} dentro do"
            f" limite diário de {formatar_reais(limite_diario)}."
        )
    if motivo is Motivo.ENTRADA_INVALIDA:
        return (
            "Recusado: despesa inválida (não é objeto, falta campo obrigatório,"
            " campo com tipo ou formato errado, ou valor fora do teto)."
        )
    if motivo is Motivo.VALOR_INVALIDO:
        return (
            f"Recusado: valor considerado de {formatar_reais(valor_considerado)}"
            " não é positivo."
        )
    if motivo is Motivo.FORA_DO_PERIODO:
        return (
            f"Recusado: a data {formatar_data(data)} está fora do período de"
            " competência."
        )
    if motivo is Motivo.CATEGORIA_FORA_DA_POLITICA:
        return f"Recusado: a categoria {categoria} não é reconhecida pela política."
    if motivo is Motivo.NOTA_FISCAL_AUSENTE:
        return (
            f"Recusado: {formatar_reais(valor_considerado)} está acima de"
            f" {formatar_reais(nota_fiscal_acima_de)} e não tem nota fiscal."
        )
    if motivo is Motivo.DUPLICATA:
        return (
            f"Recusado: duplicata de outra despesa de {categoria} em"
            f" {formatar_data(data)} com o mesmo fornecedor e o mesmo valor."
        )
    # limite_diario_excedido: parcial, ou recusado se o saldo já era zero (RN-009)
    rotulo = "Parcial" if status is Status.PARCIAL else "Recusado"
    return (
        f"{rotulo}: restavam {formatar_reais(valor_reembolsado)} do limite diário de"
        f" {formatar_reais(limite_diario)} de {categoria} em {formatar_data(data)}."
    )
