"""Constantes da política (plan seção 4)."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class LimiteDiario:
    normal: Decimal
    viagem: Decimal


# RN-009: (normal, em viagem). Valores em viagem escritos por extenso, como na
# tabela da spec; a hospedagem não amplia (AMB-006).
LIMITES_DIARIOS = {
    "alimentacao": LimiteDiario(normal=Decimal("60.00"), viagem=Decimal("90.00")),
    "transporte_urbano": LimiteDiario(
        normal=Decimal("80.00"), viagem=Decimal("120.00")
    ),
    "hospedagem": LimiteDiario(normal=Decimal("250.00"), viagem=Decimal("250.00")),
}
CATEGORIAS_RECONHECIDAS = frozenset(LIMITES_DIARIOS)  # RN-006
VALOR_ACIMA_DO_QUAL_EXIGE_NOTA = Decimal("100.00")  # RN-008 (estritamente maior)
CATEGORIA_QUE_COMPROVA_VIAGEM = "hospedagem"  # RN-010
DIAS_EM_VIAGEM_APOS_HOSPEDAGEM = 1  # RN-010: D e D+1
# RN-002 / AMB-018: valor absoluto a partir dele é entrada_invalida
VALOR_ABSOLUTO_MAXIMO = Decimal("1000000000")
