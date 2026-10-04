"""Leitura do arquivo de câmbio e busca da cotação (plan seção 4, DT-014, DT-015)."""

from datetime import date, timedelta
from decimal import Decimal
from types import MappingProxyType

from reembolso.leitura import (
    ErroDeArquivo,
    e_codigo_de_moeda,
    e_data,
    e_numero,
    ler_json,
    rejeitar_chaves_repetidas,
)
from reembolso.modelo import Cambio, Cotacao
from reembolso.politica import MOEDA_BASE, VALOR_ABSOLUTO_MAXIMO

DIAS_ANTERIORES_ACEITOS_NA_COTACAO = 4  # RN-015, AMB-024: D-1 a D-4


def _taxa(valor, caminho: str) -> Decimal:
    """Taxa da RN-016: tipo → sinal → teto (DT-015); maior que zero."""
    if not e_numero(valor):
        raise ErroDeArquivo(f"{caminho} não é número")
    valor = Decimal(valor)
    if valor <= 0:
        raise ErroDeArquivo(f"{caminho} menor ou igual a zero")
    if valor >= VALOR_ABSOLUTO_MAXIMO:
        raise ErroDeArquivo(f"{caminho} a partir de {VALOR_ABSOLUTO_MAXIMO}")
    return valor


def ler_cambio(conteudo: bytes) -> Cambio:
    """Bytes do arquivo de câmbio → `Cambio` (RN-016, DT-015)."""
    raiz = ler_json(conteudo)
    rejeitar_chaves_repetidas(raiz)
    if not isinstance(raiz, dict):
        raise ErroDeArquivo("raiz não é objeto")

    moeda_base = raiz.get("moeda_base")
    if moeda_base is not None and moeda_base != MOEDA_BASE:
        raise ErroDeArquivo(f'moeda_base diferente de "{MOEDA_BASE}"')

    taxas = raiz.get("taxas")
    if not isinstance(taxas, dict):
        raise ErroDeArquivo("taxas ausente ou não é objeto")
    por_data: dict[date, MappingProxyType[str, Decimal]] = {}
    for texto_data, moedas in taxas.items():
        caminho_data = f"taxas.{texto_data}"
        data = e_data(texto_data)
        if data is None:
            raise ErroDeArquivo(f"{caminho_data}: chave não é data válida AAAA-MM-DD")
        if not isinstance(moedas, dict):
            raise ErroDeArquivo(f"{caminho_data} não é objeto")
        por_moeda: dict[str, Decimal] = {}
        for moeda, taxa in moedas.items():
            if moeda == MOEDA_BASE:
                continue  # ignorada sem validação (RN-015, RN-016)
            caminho = f"{caminho_data}.{moeda}"
            if not e_codigo_de_moeda(moeda):
                raise ErroDeArquivo(
                    f"{caminho}: código de moeda não tem 3 letras de A a Z"
                )
            por_moeda[moeda] = _taxa(taxa, caminho)
        por_data[data] = MappingProxyType(por_moeda)
    return Cambio(taxas=MappingProxyType(por_data))


def cotacao(cambio: Cambio, moeda: str, data: date) -> Cotacao | None:
    """Cotação da `moeda` na `data`, ou na anterior mais próxima até D-4 (DT-014)."""
    if moeda == MOEDA_BASE:
        return Cotacao(Decimal(1), None)
    for dias in range(DIAS_ANTERIORES_ACEITOS_NA_COTACAO + 1):
        try:
            dia = data - timedelta(days=dias)
        except OverflowError:
            return None  # antes de 0001-01-01 não há data anterior
        taxa = cambio.taxas.get(dia, {}).get(moeda)
        if taxa is not None:
            return Cotacao(taxa, dia)
    return None
