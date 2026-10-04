"""Resultado → dicionário na ordem da seção 4 da spec → texto JSON."""

import simplejson

from reembolso.modelo import ItemResultado, Resultado


def _item(item: ItemResultado) -> dict:
    """Campos de `itens[]` na ordem da tabela de saída da seção 4 da spec."""
    return {
        "id": item.id,
        "data": item.data,
        "categoria": item.categoria,
        "valor_informado": item.valor_informado,
        "moeda": item.moeda,
        "taxa_cambio": item.taxa_cambio,
        "data_cotacao": item.data_cotacao,
        "valor_considerado": item.valor_considerado,
        "valor_reembolsado": item.valor_reembolsado,
        "status": item.status.value,
        "motivo": item.motivo.value if item.motivo is not None else None,
        "em_viagem": item.em_viagem,
        "limite_diario": item.limite_diario,
        "justificativa": item.justificativa,
        "avisos": list(item.avisos),
    }


def para_dicionario(resultado: Resultado) -> dict:
    """Campos do topo na ordem da tabela de saída da seção 4 da spec (DT-008)."""
    return {
        "colaborador": {
            "id": resultado.colaborador.id,
            "nome": resultado.colaborador.nome,
            "centro_custo": resultado.colaborador.centro_custo,
        },
        # ordem do exemplo da seção 4 da spec
        "periodo": {
            "competencia": resultado.periodo.competencia,
            "inicio": resultado.periodo.inicio_texto,
            "fim": resultado.periodo.fim_texto,
        },
        "politica": {
            "versao": resultado.politica.versao,
            "vigencia": resultado.politica.vigencia,
            "tabela_aplicada": resultado.politica.tabela_aplicada,
        },
        "itens": [_item(item) for item in resultado.itens],
        "totais": {
            "valor_solicitado": resultado.totais.valor_solicitado,
            "valor_reembolsado": resultado.totais.valor_reembolsado,
            "valor_glosado": resultado.totais.valor_glosado,
        },
        "avisos": list(resultado.avisos),
    }


def para_texto(resultado: Resultado) -> str:
    """Texto JSON determinístico: `Decimal` como número exato (DT-001), UTF-8 sem
    escape de não ASCII, `indent=2` e quebra de linha final (DT-008)."""
    return (
        simplejson.dumps(
            para_dicionario(resultado),
            use_decimal=True,
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
