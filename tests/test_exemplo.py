"""Aceite com os arquivos de exemplo: as três tabelas da seção 9 da spec
(RN-001 a RN-016), DT-001.

As tabelas abaixo são as da seção 9 da spec, transcritas à mão ("—" = `None`).

- `despesas-exemplo.json`: `CC-ENG-PLATAFORMA` → tabela dele (alimentação
  75,00; transporte 80,00; hospedagem com limite 0, vedada pela AMB-021).
  Nenhuma data em viagem: a única hospedagem com nota (d-010) é recusada na
  etapa 5. Todas as despesas em reais.
- `envelope/despesas-envelope.json`: `CC-COMERCIAL` → tabela dele
  (alimentação 90,00, em viagem 135,00; hospedagem 400,00; representação
  300,00). Datas em viagem: 22/07 e 23/07, pela hospedagem e-007 com nota.
- `envelope/despesas-envelope-cc-desconhecido.json`: `CC-SUPORTE-N2`, ausente
  da política → `padrao` (alimentação 60,00; transporte 80,00; hospedagem
  250,00). Datas em viagem: 17/07 e 18/07, pela hospedagem f-002 com nota.
"""

from decimal import Decimal
from pathlib import Path

import pytest
import simplejson

from reembolso.cli import main

EXEMPLOS = Path(__file__).resolve().parent.parent / "exemplos"
EXEMPLO = EXEMPLOS / "despesas-exemplo.json"
ENVELOPE = EXEMPLOS / "envelope" / "despesas-envelope.json"
CC_DESCONHECIDO = EXEMPLOS / "envelope" / "despesas-envelope-cc-desconhecido.json"
POLITICA = EXEMPLOS / "envelope" / "politica-v4.json"
CAMBIO = EXEMPLOS / "envelope" / "cambio.json"

ARQUIVOS = [EXEMPLO, ENVELOPE, CC_DESCONHECIDO]
IDS_ARQUIVOS = ["exemplo", "envelope", "cc-desconhecido"]

D = Decimal
BRL = ("BRL", D("1"), None)  # moeda, taxa, data da cotação de um item em reais

# id, considerado, em viagem, limite, reembolsado, status, motivo
TABELA_EXEMPLO = [
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

# id, (moeda, taxa, data cotação), considerado, em viagem, limite,
# reembolsado, status, motivo
TABELA_ENVELOPE = [
    # representação 340,00 > 300,00 (não amplia em viagem)
    ("e-001", BRL, D("340.00"), False, D("300.00"), D("300.00"), "parcial",
     "limite_diario_excedido"),
    # 22,00 × 5,93 = 130,46 > 90,00 (14/07 fora de viagem)
    ("e-002", ("EUR", D("5.93"), "2026-07-14"), D("130.46"), False, D("90.00"),
     D("90.00"), "parcial", "limite_diario_excedido"),
    # 14,50 × 5,88 = 85,26; sem nota mas ≤ 100,00 em reais; ≤ 90,00
    ("e-003", ("EUR", D("5.88"), "2026-07-15"), D("85.26"), False, D("90.00"),
     D("85.26"), "aprovado", None),
    # sábado 18/07 sem cotação → 17/07: 30,00 × 5,96 = 178,80 > 90,00
    ("e-004", ("EUR", D("5.96"), "2026-07-17"), D("178.80"), False, D("90.00"),
     D("90.00"), "parcial", "limite_diario_excedido"),
    # 40,00 × 5,50 = 220,00 > 100,00 sem nota (RN-008, em reais)
    ("e-005", ("USD", D("5.50"), "2026-07-20"), D("220.00"), None, None,
     D("0.00"), "recusado", "nota_fiscal_ausente"),
    # GBP não está no câmbio (RN-015)
    ("e-006", ("GBP", None, None), None, None, None, D("0.00"), "recusado",
     "cambio_indisponivel"),
    # hospedagem 1.200,00 > 400,00 (não amplia); comprova 22/07 e 23/07
    ("e-007", BRL, D("1200.00"), True, D("400.00"), D("400.00"), "parcial",
     "limite_diario_excedido"),
    # 23/07 em viagem: 90,00 × 1,5 = 135,00; 95,00 ≤ 135,00
    ("e-008", BRL, D("95.00"), True, D("135.00"), D("95.00"), "aprovado", None),
    # coworking não está na tabela CC-COMERCIAL (RN-006)
    ("e-009", BRL, D("120.00"), None, None, D("0.00"), "recusado",
     "categoria_fora_da_politica"),
    # sem `moeda` → BRL; 88,00 ≤ 90,00
    ("e-010", BRL, D("88.00"), False, D("90.00"), D("88.00"), "aprovado", None),
]

TABELA_CC_DESCONHECIDO = [
    # padrao: alimentação 60,00; 16/07 fora de viagem; 58,00 ≤ 60,00
    ("f-001", BRL, D("58.00"), False, D("60.00"), D("58.00"), "aprovado", None),
    # hospedagem 310,00 > 250,00 (não amplia); comprova 17/07 e 18/07
    ("f-002", BRL, D("310.00"), True, D("250.00"), D("250.00"), "parcial",
     "limite_diario_excedido"),
    # representação não está no padrao (RN-006, RN-014)
    ("f-003", BRL, D("190.00"), None, None, D("0.00"), "recusado",
     "categoria_fora_da_politica"),
    # 12,00 × 5,48 = 65,76 ≤ 80,00 (21/07 fora de viagem)
    ("f-004", ("USD", D("5.48"), "2026-07-21"), D("65.76"), False, D("80.00"),
     D("65.76"), "aprovado", None),
]

CAMPOS_MONETARIOS_ITEM = ("valor_considerado", "valor_reembolsado", "limite_diario")


def _calcular(entrada: Path, saida: Path) -> None:
    assert main([
        "calcular",
        "--input", str(entrada),
        "--politica", str(POLITICA),
        "--cambio", str(CAMBIO),
        "--output", str(saida),
    ]) == 0


def _ler(saida: Path) -> dict:
    return simplejson.loads(saida.read_text(encoding="utf-8"), use_decimal=True)


@pytest.fixture(scope="module")
def saidas(tmp_path_factory):
    """Saída da CLI para cada arquivo, lida com `Decimal` (DT-001)."""
    pasta = tmp_path_factory.mktemp("exemplos")
    lidas = {}
    for entrada, nome in zip(ARQUIVOS, IDS_ARQUIVOS, strict=True):
        saida = pasta / f"{nome}.json"
        _calcular(entrada, saida)
        lidas[nome] = _ler(saida)
    return lidas


def _item(saida: dict, id_: str) -> dict:
    return next(i for i in saida["itens"] if i["id"] == id_)


def _confere_linha(item, considerado, em_viagem, limite, reembolsado, status,
                   motivo):
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


def _confere_cambio(item, moeda, taxa, data_cotacao):
    # `taxa_cambio` 1 do BRL não pode sair como `true` (seção 4)
    assert type(item["taxa_cambio"]) is not bool
    assert (item["moeda"], item["taxa_cambio"], item["data_cotacao"]) == (
        moeda, taxa, data_cotacao,
    )


# --- Exemplo: despesas-exemplo.json ---------------------------------------


def test_exemplo_um_item_por_despesa_na_ordem(saidas):
    """RN-001 / seção 9: 14 itens, na ordem das despesas do exemplo."""
    assert [item["id"] for item in saidas["exemplo"]["itens"]] == [
        linha[0] for linha in TABELA_EXEMPLO
    ]


@pytest.mark.parametrize(
    "linha", TABELA_EXEMPLO, ids=[linha[0] for linha in TABELA_EXEMPLO]
)
def test_exemplo_linha_da_tabela_da_secao_9(saidas, linha):
    """Seção 9 (RN-001 a RN-014): cada item do exemplo bate com a sua linha da
    tabela (considerado, em viagem, limite, reembolsado, status, motivo); todas
    as despesas em reais (`BRL`, taxa 1, sem data de cotação)."""
    id_, *resto = linha
    item = _item(saidas["exemplo"], id_)
    _confere_linha(item, *resto)
    _confere_cambio(item, *BRL)


def test_exemplo_totais(saidas):
    """Seção 9: totais 1.861,84 / 351,43 / 1.510,41."""
    # solicitado: considerados > 0 (todos menos d-009) =
    #   72,50 + 38,00 + 100,00 + 100,01 + 89,00 + 54,90 + 54,90 + 41,00
    #   + 480,00 + 33,33 + 47,20 + 690,00 + 61,00 = 1.861,84
    # reembolsado: 72,50 + 2,50 + 80,00 + 54,90 + 33,33 + 47,20 + 61,00 = 351,43
    # glosado: 1.861,84 − 351,43 = 1.510,41
    assert saidas["exemplo"]["totais"] == {
        "valor_solicitado": D("1861.84"),
        "valor_reembolsado": D("351.43"),
        "valor_glosado": D("1510.41"),
    }


def test_exemplo_politica_e_colaborador(saidas):
    """Seção 9 / RN-014: `politica` = `v4` / `2026-07-01` / `CC-ENG-PLATAFORMA`;
    `colaborador.centro_custo` copiado da entrada."""
    assert saidas["exemplo"]["politica"] == {
        "versao": "v4",
        "vigencia": "2026-07-01",
        "tabela_aplicada": "CC-ENG-PLATAFORMA",
    }
    assert saidas["exemplo"]["colaborador"]["centro_custo"] == "CC-ENG-PLATAFORMA"


# --- Envelope: despesas-envelope.json -------------------------------------


def test_envelope_um_item_por_despesa_na_ordem(saidas):
    """RN-001 / seção 9: 10 itens, na ordem das despesas do envelope."""
    assert [item["id"] for item in saidas["envelope"]["itens"]] == [
        linha[0] for linha in TABELA_ENVELOPE
    ]


@pytest.mark.parametrize(
    "linha", TABELA_ENVELOPE, ids=[linha[0] for linha in TABELA_ENVELOPE]
)
def test_envelope_linha_da_tabela_da_secao_9(saidas, linha):
    """Seção 9 (RN-001 a RN-016): cada item do envelope bate com a sua linha
    da tabela (moeda, taxa, data da cotação, considerado, em viagem, limite,
    reembolsado, status, motivo)."""
    id_, cambio, *resto = linha
    item = _item(saidas["envelope"], id_)
    _confere_cambio(item, *cambio)
    _confere_linha(item, *resto)


def test_envelope_totais(saidas):
    """Seção 9 / RN-015: totais 2.457,52 / 1.148,26 / 1.309,26; e-006
    (`cambio_indisponivel`) fora de `valor_solicitado`."""
    # solicitado: 340,00 + 130,46 + 85,26 + 178,80 + 220,00 + 1.200,00
    #   + 95,00 + 120,00 + 88,00 = 2.457,52 (sem e-006)
    # reembolsado: 300,00 + 90,00 + 85,26 + 90,00 + 400,00 + 95,00 + 88,00
    #   = 1.148,26
    # glosado: 2.457,52 − 1.148,26 = 1.309,26
    assert saidas["envelope"]["totais"] == {
        "valor_solicitado": D("2457.52"),
        "valor_reembolsado": D("1148.26"),
        "valor_glosado": D("1309.26"),
    }


def test_envelope_politica_e_colaborador(saidas):
    """Seção 9 / RN-014: `CC-COMERCIAL` está na política → tabela dele;
    `colaborador.centro_custo` copiado da entrada."""
    assert saidas["envelope"]["politica"] == {
        "versao": "v4",
        "vigencia": "2026-07-01",
        "tabela_aplicada": "CC-COMERCIAL",
    }
    assert saidas["envelope"]["colaborador"]["centro_custo"] == "CC-COMERCIAL"


# --- Envelope: despesas-envelope-cc-desconhecido.json ---------------------


def test_cc_desconhecido_um_item_por_despesa_na_ordem(saidas):
    """RN-001 / seção 9: 4 itens, na ordem das despesas do arquivo."""
    assert [item["id"] for item in saidas["cc-desconhecido"]["itens"]] == [
        linha[0] for linha in TABELA_CC_DESCONHECIDO
    ]


@pytest.mark.parametrize(
    "linha",
    TABELA_CC_DESCONHECIDO,
    ids=[linha[0] for linha in TABELA_CC_DESCONHECIDO],
)
def test_cc_desconhecido_linha_da_tabela_da_secao_9(saidas, linha):
    """Seção 9 (RN-014, RN-015): cada item do arquivo com centro de custo
    desconhecido bate com a sua linha da tabela."""
    id_, cambio, *resto = linha
    item = _item(saidas["cc-desconhecido"], id_)
    _confere_cambio(item, *cambio)
    _confere_linha(item, *resto)


def test_cc_desconhecido_totais(saidas):
    """Seção 9: totais 623,76 / 373,76 / 250,00."""
    # solicitado: 58,00 + 310,00 + 190,00 + 65,76 = 623,76
    # reembolsado: 58,00 + 250,00 + 65,76 = 373,76
    # glosado: 623,76 − 373,76 = 250,00
    assert saidas["cc-desconhecido"]["totais"] == {
        "valor_solicitado": D("623.76"),
        "valor_reembolsado": D("373.76"),
        "valor_glosado": D("250.00"),
    }


def test_cc_desconhecido_politica_e_colaborador(saidas):
    """Seção 9 / RN-014: `CC-SUPORTE-N2` ausente da política → `padrao`;
    `colaborador.centro_custo` copiado da entrada."""
    assert saidas["cc-desconhecido"]["politica"] == {
        "versao": "v4",
        "vigencia": "2026-07-01",
        "tabela_aplicada": "padrao",
    }
    assert (
        saidas["cc-desconhecido"]["colaborador"]["centro_custo"]
        == "CC-SUPORTE-N2"
    )


# --- Os três arquivos -----------------------------------------------------


@pytest.mark.parametrize("nome", IDS_ARQUIVOS)
def test_sem_avisos(saidas, nome):
    """Seção 9 / RN-013: nenhum dos três arquivos tem chave repetida →
    `avisos` vazio no topo e em todos os itens."""
    saida = saidas[nome]
    assert saida["avisos"] == []
    assert all(item["avisos"] == [] for item in saida["itens"])


@pytest.mark.parametrize("entrada", ARQUIVOS, ids=IDS_ARQUIVOS)
def test_determinismo_byte_a_byte(tmp_path, entrada):
    """Seção 9: a mesma entrada, com a mesma política e o mesmo câmbio, sempre
    produz a mesma saída — duas execuções da CLI geram arquivos idênticos byte
    a byte."""
    primeira = tmp_path / "primeira.json"
    segunda = tmp_path / "segunda.json"
    _calcular(entrada, primeira)
    _calcular(entrada, segunda)

    assert primeira.read_bytes() == segunda.read_bytes()


@pytest.mark.parametrize("entrada", ARQUIVOS, ids=IDS_ARQUIVOS)
def test_nenhum_valor_monetario_e_float(tmp_path, entrada):
    """Seção 4 / DT-001: todo valor monetário calculado da saída é exato ao
    centavo — lido com `Decimal`, nenhum tem mais de 2 casas (um `float` vazado
    no cálculo apareceria como 0.30000000000000004) e nenhum é `bool`.

    A leitura com `use_decimal=True` já devolve `Decimal` para todo número com
    parte decimal: a detecção de `float` vem do `quantize`, não do tipo."""
    saida = tmp_path / "saida.json"
    _calcular(entrada, saida)
    lida = _ler(saida)

    monetarios = list(lida["totais"].values())
    for item in lida["itens"]:
        monetarios += [item[campo] for campo in CAMPOS_MONETARIOS_ITEM]
    monetarios = [valor for valor in monetarios if valor is not None]

    assert monetarios
    for valor in monetarios:
        assert type(valor) is Decimal
        assert valor == valor.quantize(D("0.01"))
