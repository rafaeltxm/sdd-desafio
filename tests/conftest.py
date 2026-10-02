"""Construtores de entrada mínima válida (plan seção 6, Fixtures).

Cada teste declara só o que importa ao caso: os campos passados sobrescrevem
os padrões. Os documentos são dicionários prontos para `simplejson.dumps(...,
use_decimal=True)`; valores numéricos são `Decimal`.
"""

from decimal import Decimal

import pytest
import simplejson

from reembolso.entrada import ler_entrada
from reembolso.motor import calcular
from reembolso.saida import para_dicionario


def construir_despesa(**campos):
    """Despesa com todos os campos obrigatórios da seção 4 da spec."""
    documento = {
        "id": "d-1",
        "data": "2026-07-03",
        "categoria": "alimentacao",
        "fornecedor": "Restaurante",
        "valor": Decimal("10.00"),
        "tem_nota_fiscal": True,
    }
    documento.update(campos)
    return documento


def construir_entrada(despesas=(), colaborador=None, periodo=None):
    """Documento com `colaborador`, `periodo` e `despesas` (seção 4 da spec)."""
    return {
        "colaborador": colaborador if colaborador is not None else {
            "id": "c-1",
            "nome": "Ana",
        },
        "periodo": periodo if periodo is not None else {
            "inicio": "2026-07-01",
            "fim": "2026-07-31",
        },
        "despesas": list(despesas),
    }


@pytest.fixture
def despesa():
    return construir_despesa


@pytest.fixture
def entrada():
    return construir_entrada


def processar(texto_json: str) -> dict:
    """Texto JSON da entrada → motor → dicionário da saída (seção 4 da spec)."""
    return para_dicionario(calcular(ler_entrada(texto_json.encode())))


def avaliar(*despesas, **cabecalho) -> dict:
    """Despesas (dicionários) numa entrada mínima válida → saída de `processar`."""
    documento = construir_entrada(despesas, **cabecalho)
    return processar(simplejson.dumps(documento, use_decimal=True))


@pytest.fixture(name="processar")
def _processar():
    return processar


@pytest.fixture(name="avaliar")
def _avaliar():
    return avaliar
