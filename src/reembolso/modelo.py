"""Dataclasses e enums compartilhados (plan seção 3)."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum


class Status(StrEnum):
    APROVADO = "aprovado"
    PARCIAL = "parcial"
    RECUSADO = "recusado"


class Motivo(StrEnum):
    """Na ordem das etapas da seção 8 da spec."""

    ENTRADA_INVALIDA = "entrada_invalida"
    VALOR_INVALIDO = "valor_invalido"
    FORA_DO_PERIODO = "fora_do_periodo"
    CATEGORIA_FORA_DA_POLITICA = "categoria_fora_da_politica"
    NOTA_FISCAL_AUSENTE = "nota_fiscal_ausente"
    DUPLICATA = "duplicata"
    LIMITE_DIARIO_EXCEDIDO = "limite_diario_excedido"


@dataclass(frozen=True)
class Colaborador:
    id: str
    nome: str
    centro_custo: str | None  # texto como veio, ou None se ausente/nulo


@dataclass(frozen=True)
class Periodo:
    inicio: date
    fim: date
    inicio_texto: str
    fim_texto: str
    competencia: str | None


@dataclass(frozen=True)
class Despesa:
    """Despesa que passou pela etapa 1 (validação)."""

    posicao: int  # índice em `despesas` — ordem da entrada
    id: str
    data: date
    data_texto: str
    categoria_texto: str  # como veio
    categoria: str  # normalizada (seção 5 da spec)
    fornecedor: str  # normalizado
    valor_informado: Decimal
    tem_nota_fiscal: bool
    avisos: tuple[str, ...]  # RN-013


@dataclass(frozen=True)
class DespesaInvalida:
    """Despesa recusada na etapa 1."""

    posicao: int
    id: str | None
    data_texto: str | None
    categoria_texto: str | None  # como veio, se texto; o motor decide a saída
    valor_informado: Decimal | None
    avisos: tuple[str, ...]


@dataclass(frozen=True)
class Entrada:
    colaborador: Colaborador
    periodo: Periodo
    despesas: list[Despesa | DespesaInvalida]
    avisos: tuple[str, ...]  # chaves repetidas fora das despesas


Tabela = Mapping[str, Decimal]  # categoria normalizada → limite diário normal


@dataclass(frozen=True)
class Politica:
    """Arquivo de política validado (RN-016)."""

    versao: str | None
    vigencia: str | None  # texto como veio no arquivo
    padrao: Tabela
    centros_custo: Mapping[str, Tabela]  # chave como escrita no arquivo
    nota_fiscal_acima_de: Decimal
    acrescimo_em_viagem_percentual: Decimal


@dataclass(frozen=True)
class TabelaAplicada:
    """Tabela escolhida pelo centro de custo (RN-014)."""

    nome: str  # chave de `centros_custo` como escrita no arquivo, ou "padrao"
    limites: Tabela


@dataclass(frozen=True)
class Cambio:
    """Arquivo de câmbio validado (RN-016), sem a entrada `BRL` (ignorada)."""

    taxas: Mapping[date, Mapping[str, Decimal]]


@dataclass(frozen=True)
class Cotacao:
    """Taxa usada na conversão (RN-015); `data` é `None` para `BRL`."""

    taxa: Decimal
    data: date | None


@dataclass(frozen=True)
class ItemResultado:
    """Espelha `itens[]` da seção 4 da spec, campo a campo."""

    id: str | None
    data: str | None
    categoria: str | None
    valor_informado: Decimal | None
    valor_considerado: Decimal | None
    valor_reembolsado: Decimal
    status: Status
    motivo: Motivo | None
    em_viagem: bool | None
    limite_diario: Decimal | None
    justificativa: str
    avisos: tuple[str, ...]


@dataclass(frozen=True)
class Totais:
    valor_solicitado: Decimal
    valor_reembolsado: Decimal
    valor_glosado: Decimal


@dataclass(frozen=True)
class PoliticaAplicada:
    """`politica` da saída (seção 4 da spec)."""

    versao: str | None
    vigencia: str | None
    tabela_aplicada: str


@dataclass(frozen=True)
class Resultado:
    colaborador: Colaborador
    periodo: Periodo
    politica: PoliticaAplicada
    itens: list[ItemResultado]
    totais: Totais
    avisos: tuple[str, ...]
