"""Aceite com o arquivo de exemplo: primeira tabela da seção 9 da spec 2.0
(RN-001 a RN-014), DT-001.

A tabela abaixo é a da seção 9 da spec, transcrita à mão ("—" = `None`).
`centro_custo` `CC-ENG-PLATAFORMA` → tabela dele (alimentação 75,00;
transporte 80,00; hospedagem com limite 0, vedada pela AMB-021). Nenhuma data
em viagem: a única hospedagem com nota (d-010) é recusada na etapa 5.
"""

from decimal import Decimal
from pathlib import Path

import pytest
import simplejson

from reembolso.cli import main

EXEMPLOS = Path(__file__).resolve().parent.parent / "exemplos"
EXEMPLO = EXEMPLOS / "despesas-exemplo.json"
POLITICA = EXEMPLOS / "envelope" / "politica-v4.json"
CAMBIO = EXEMPLOS / "envelope" / "cambio.json"

D = Decimal

# id, considerado, em viagem, limite, reembolsado, status, motivo
TABELA_SECAO_9 = [
    # 03/07: 72,50 ≤ 75,00 → aprovado; saldo 75,00 − 72,50 = 2,50
    ("d-001", D("72.50"), False, D("75.00"), D("72.50"), "aprovado", None),
    # mesmo dia de d-001: min(38,00; 2,50) = 2,50 → parcial
    ("d-002", D("38.00"), False, D("75.00"), D("2.50"), "parcial",
     "limite_diario_excedido"),
    # 100,00 sem nota não passa de 100,00 (RN-008); min(100,00; 80,00) = 80,00
    ("d-003", D("100.00"), False, D("80.00"), D("80.00"), "parcial",
     "limite_diario_excedido"),
    # 100,01 > 100,00 sem nota (RN-008)
    ("d-004", D("100.01"), None, None, D("0.00"), "recusado",
     "nota_fiscal_ausente"),
    # coworking não está na tabela CC-ENG-PLATAFORMA (RN-006)
    ("d-005", D("89.00"), None, None, D("0.00"), "recusado",
     "categoria_fora_da_politica"),
    # 54,90 ≤ 75,00
    ("d-006", D("54.90"), False, D("75.00"), D("54.90"), "aprovado", None),
    # mesma data, categoria, fornecedor e valor de d-006 (RN-007)
    ("d-007", D("54.90"), None, None, D("0.00"), "recusado", "duplicata"),
    # 15/04 fora de [01/07, 31/07] (RN-005)
    ("d-008", D("41.00"), None, None, D("0.00"), "recusado", "fora_do_periodo"),
    # −45,00 ≤ 0 (RN-004)
    ("d-009", D("-45.00"), None, None, D("0.00"), "recusado", "valor_invalido"),
    # hospedagem com limite 0 no CC-ENG-PLATAFORMA (AMB-021): etapa 5
    ("d-010", D("480.00"), None, None, D("0.00"), "recusado",
     "categoria_fora_da_politica"),
    # 33,333 → 33,33 (RN-003); 15/07 fora de viagem (d-010 não comprova): 75,00
    ("d-011", D("33.33"), False, D("75.00"), D("33.33"), "aprovado", None),
    # sábado conta como dia comum; 47,20 ≤ 75,00
    ("d-012", D("47.20"), False, D("75.00"), D("47.20"), "aprovado", None),
    # hospedagem vedada: etapa 5 antes da nota (etapa 6)
    ("d-013", D("690.00"), None, None, D("0.00"), "recusado",
     "categoria_fora_da_politica"),
    # ALIMENTACAO → alimentacao (RN-006); 61,00 ≤ 75,00
    ("d-014", D("61.00"), False, D("75.00"), D("61.00"), "aprovado", None),
]

CAMPOS_MONETARIOS_ITEM = ("valor_considerado", "valor_reembolsado", "limite_diario")


def _calcular(saida: Path) -> None:
    assert main([
        "calcular",
        "--input", str(EXEMPLO),
        "--politica", str(POLITICA),
        "--cambio", str(CAMBIO),
        "--output", str(saida),
    ]) == 0


@pytest.fixture(scope="module")
def saida_exemplo(tmp_path_factory):
    """Saída da CLI para o arquivo de exemplo, lida com `Decimal` (DT-001)."""
    saida = tmp_path_factory.mktemp("exemplo") / "saida.json"
    _calcular(saida)
    return simplejson.loads(saida.read_text(encoding="utf-8"), use_decimal=True)


def test_exemplo_um_item_por_despesa_na_ordem(saida_exemplo):
    """RN-001 / seção 9: 14 itens, na ordem das despesas do exemplo."""
    assert [item["id"] for item in saida_exemplo["itens"]] == [
        linha[0] for linha in TABELA_SECAO_9
    ]


@pytest.mark.parametrize(
    "linha", TABELA_SECAO_9, ids=[linha[0] for linha in TABELA_SECAO_9]
)
def test_exemplo_linha_da_tabela_da_secao_9(saida_exemplo, linha):
    """Seção 9 (RN-001 a RN-014): cada item do exemplo bate com a sua linha da
    tabela (considerado, em viagem, limite, reembolsado, status, motivo)."""
    id_, considerado, em_viagem, limite, reembolsado, status, motivo = linha
    item = next(i for i in saida_exemplo["itens"] if i["id"] == id_)

    # `==` aceitaria 0 no lugar de False: o tipo é conferido à parte (seção 4)
    assert type(item["em_viagem"]) is type(em_viagem)
    assert (
        item["valor_considerado"],
        item["em_viagem"],
        item["limite_diario"],
        item["valor_reembolsado"],
        item["status"],
        item["motivo"],
    ) == (considerado, em_viagem, limite, reembolsado, status, motivo)


def test_exemplo_totais(saida_exemplo):
    """Seção 9: totais 1.861,84 / 351,43 / 1.510,41."""
    # solicitado: considerados > 0 (todos menos d-009) =
    #   72,50 + 38,00 + 100,00 + 100,01 + 89,00 + 54,90 + 54,90 + 41,00
    #   + 480,00 + 33,33 + 47,20 + 690,00 + 61,00 = 1.861,84
    # reembolsado: 72,50 + 2,50 + 80,00 + 54,90 + 33,33 + 47,20 + 61,00 = 351,43
    # glosado: 1.861,84 − 351,43 = 1.510,41
    assert saida_exemplo["totais"] == {
        "valor_solicitado": D("1861.84"),
        "valor_reembolsado": D("351.43"),
        "valor_glosado": D("1510.41"),
    }


def test_exemplo_politica_e_colaborador(saida_exemplo):
    """Seção 9 / RN-014: `politica` = `v4` / `2026-07-01` / `CC-ENG-PLATAFORMA`;
    `colaborador.centro_custo` copiado da entrada."""
    assert saida_exemplo["politica"] == {
        "versao": "v4",
        "vigencia": "2026-07-01",
        "tabela_aplicada": "CC-ENG-PLATAFORMA",
    }
    assert saida_exemplo["colaborador"]["centro_custo"] == "CC-ENG-PLATAFORMA"


def test_exemplo_sem_avisos(saida_exemplo):
    """Seção 9 / RN-013: o exemplo não tem chave repetida → `avisos` vazio no
    topo e em todos os itens."""
    assert saida_exemplo["avisos"] == []
    assert [item["avisos"] for item in saida_exemplo["itens"]] == [[]] * 14


def test_determinismo_byte_a_byte(tmp_path):
    """Seção 9: a mesma entrada sempre produz a mesma saída — duas execuções da
    CLI geram arquivos idênticos byte a byte."""
    primeira = tmp_path / "primeira.json"
    segunda = tmp_path / "segunda.json"
    _calcular(primeira)
    _calcular(segunda)

    assert primeira.read_bytes() == segunda.read_bytes()


def test_nenhum_valor_monetario_e_float(tmp_path):
    """Seção 4 / DT-001: todo valor monetário calculado da saída é exato ao
    centavo — lido com `Decimal`, nenhum tem mais de 2 casas (um `float` vazado
    no cálculo apareceria como 0.30000000000000004) e nenhum é `bool`.

    A leitura com `use_decimal=True` já devolve `Decimal` para todo número com
    parte decimal: a detecção de `float` vem do `quantize`, não do tipo."""
    saida = tmp_path / "saida.json"
    _calcular(saida)
    lida = simplejson.loads(saida.read_text(encoding="utf-8"), use_decimal=True)

    monetarios = list(lida["totais"].values())
    for item in lida["itens"]:
        monetarios += [item[campo] for campo in CAMPOS_MONETARIOS_ITEM]
    monetarios = [valor for valor in monetarios if valor is not None]

    assert monetarios
    for valor in monetarios:
        assert type(valor) is Decimal
        assert valor == valor.quantize(D("0.01"))
