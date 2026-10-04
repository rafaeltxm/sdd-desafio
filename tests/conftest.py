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


def _regra(limite, periodicidade="dia", **extras):
    return {"limite": Decimal(limite), "periodicidade": periodicidade, **extras}


def construir_politica(**sobrescritas):
    """`exemplos/envelope/politica-v4.json` transcrita (plan seção 6).

    Os campos passados sobrescrevem os da raiz; cada chamada devolve um
    documento novo, que o teste pode alterar.
    """
    documento = {
        "versao": "v4",
        "vigencia": "2026-07-01",
        "moeda_base": "BRL",
        "padrao": {
            "alimentacao": _regra("60.00"),
            "transporte_urbano": _regra("80.00"),
            "hospedagem": _regra("250.00", "diaria"),
        },
        "centros_custo": {
            "CC-ENG-PLATAFORMA": {
                "alimentacao": _regra("75.00"),
                "transporte_urbano": _regra("80.00"),
                "hospedagem": _regra(
                    "0.00", "diaria", observacao="nao reembolsavel"
                ),
            },
            "CC-COMERCIAL": {
                "alimentacao": _regra("90.00"),
                "transporte_urbano": _regra("150.00"),
                "hospedagem": _regra("400.00", "diaria"),
                "representacao": _regra("300.00"),
            },
            "CC-ADM": {
                "alimentacao": _regra("45.00"),
                "transporte_urbano": _regra("60.00"),
            },
        },
        "nota_fiscal_obrigatoria_acima_de": Decimal("100.00"),
        "acrescimo_em_viagem_percentual": Decimal("50"),
    }
    documento.update(sobrescritas)
    return documento


def construir_cambio(**sobrescritas):
    """`exemplos/envelope/cambio.json` transcrito (plan seção 6).

    Os campos passados sobrescrevem os da raiz (ex. `taxas=...`); cada chamada
    devolve um documento novo, que o teste pode alterar.
    """
    cotacoes = {
        "2026-07-13": ("5.42", "5.91"),
        "2026-07-14": ("5.44", "5.93"),
        "2026-07-15": ("5.39", "5.88"),
        "2026-07-16": ("5.41", "5.90"),
        "2026-07-17": ("5.47", "5.96"),
        "2026-07-20": ("5.50", "6.01"),
        "2026-07-21": ("5.48", "5.99"),
        "2026-07-22": ("5.45", "5.95"),
        "2026-07-23": ("5.44", "5.94"),
        "2026-07-24": ("5.46", "5.97"),
        "2026-07-27": ("5.52", "6.03"),
        "2026-07-28": ("5.51", "6.02"),
    }
    documento = {
        "moeda_base": "BRL",
        "fonte": "Banco Central - PTAX de fechamento",
        "observacao": "Cotacoes publicadas apenas em dias uteis bancarios.",
        "taxas": {
            data: {"USD": Decimal(usd), "EUR": Decimal(eur)}
            for data, (usd, eur) in cotacoes.items()
        },
    }
    documento.update(sobrescritas)
    return documento


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
