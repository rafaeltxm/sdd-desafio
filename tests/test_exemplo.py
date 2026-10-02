"""Aceite com o arquivo de exemplo: seção 9 da spec (RN-001 a RN-012), DT-001.

A tabela abaixo é a da seção 9 da spec, transcrita à mão ("—" = `None`).
Datas em viagem: 14/07 e 15/07, pela hospedagem d-010 com nota (RN-010).
"""

from decimal import Decimal
from pathlib import Path

import pytest
import simplejson

from reembolso.cli import main

EXEMPLO = Path(__file__).resolve().parent.parent / "exemplos" / "despesas-exemplo.json"

D = Decimal

# id, considerado, em viagem, limite, reembolsado, status, motivo
TABELA_SECAO_9 = [
    # 72,50 > 60,00 (alimentação fora de viagem) → 60,00
    ("d-001", D("72.50"), False, D("60.00"), D("60.00"), "parcial",
     "limite_diario_excedido"),
    # mesmo dia de d-001: restam 60,00 − 60,00 = 0,00
    ("d-002", D("38.00"), False, D("60.00"), D("0.00"), "recusado",
     "limite_diario_excedido"),
    # 100,00 sem nota não passa de 100,00 (RN-008); 100,00 > 80,00 → 80,00
    ("d-003", D("100.00"), False, D("80.00"), D("80.00"), "parcial",
     "limite_diario_excedido"),
    # 100,01 > 100,00 sem nota (RN-008)
    ("d-004", D("100.01"), None, None, D("0.00"), "recusado",
     "nota_fiscal_ausente"),
    # coworking não está na política (RN-006)
    ("d-005", D("89.00"), None, None, D("0.00"), "recusado",
     "categoria_fora_da_politica"),
    # 54,90 ≤ 60,00
    ("d-006", D("54.90"), False, D("60.00"), D("54.90"), "aprovado", None),
    # mesma data, categoria, fornecedor e valor de d-006 (RN-007)
    ("d-007", D("54.90"), None, None, D("0.00"), "recusado", "duplicata"),
    # 15/04 fora de [01/07, 31/07] (RN-005)
    ("d-008", D("41.00"), None, None, D("0.00"), "recusado", "fora_do_periodo"),
    # −45,00 ≤ 0 (RN-004)
    ("d-009", D("-45.00"), None, None, D("0.00"), "recusado", "valor_invalido"),
    # hospedagem em viagem: 480,00 > 250,00 → 250,00 (RN-012: uma diária)
    ("d-010", D("480.00"), True, D("250.00"), D("250.00"), "parcial",
     "limite_diario_excedido"),
    # 33,333 → 33,33 (RN-003); alimentação em viagem 90,00
    ("d-011", D("33.33"), True, D("90.00"), D("33.33"), "aprovado", None),
    # sábado conta como dia comum; 47,20 ≤ 60,00
    ("d-012", D("47.20"), False, D("60.00"), D("47.20"), "aprovado", None),
    # 690,00 > 100,00 sem nota (RN-008)
    ("d-013", D("690.00"), None, None, D("0.00"), "recusado",
     "nota_fiscal_ausente"),
    # ALIMENTACAO → alimentacao (RN-006); 61,00 > 60,00 → 60,00
    ("d-014", D("61.00"), False, D("60.00"), D("60.00"), "parcial",
     "limite_diario_excedido"),
]

CAMPOS_MONETARIOS_ITEM = ("valor_considerado", "valor_reembolsado", "limite_diario")


def _calcular(saida: Path) -> None:
    assert main(["calcular", "--input", str(EXEMPLO), "--output", str(saida)]) == 0


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
    """Seção 9 (RN-001 a RN-012): cada item do exemplo bate com a sua linha da
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
    """Seção 9: totais 1.861,84 / 585,43 / 1.276,41."""
    # solicitado: considerados > 0 (todos menos d-009) =
    #   72,50 + 38,00 + 100,00 + 100,01 + 89,00 + 54,90 + 54,90 + 41,00
    #   + 480,00 + 33,33 + 47,20 + 690,00 + 61,00 = 1.861,84
    # reembolsado: 60,00 + 80,00 + 54,90 + 250,00 + 33,33 + 47,20 + 60,00 = 585,43
    # glosado: 1.861,84 − 585,43 = 1.276,41
    assert saida_exemplo["totais"] == {
        "valor_solicitado": D("1861.84"),
        "valor_reembolsado": D("585.43"),
        "valor_glosado": D("1276.41"),
    }


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
