from decimal import Decimal

from reembolso import politica
from reembolso.modelo import Motivo, Status


def test_rn009_limites_conferem_tabela_da_spec():
    """RN-009 / AMB-006: limite diário normal e em viagem por categoria; a hospedagem
    não amplia em viagem."""
    # Tabela da RN-009, transcrita: (normal, em viagem)
    esperado = {
        "alimentacao": (Decimal("60.00"), Decimal("90.00")),
        "transporte_urbano": (Decimal("80.00"), Decimal("120.00")),
        "hospedagem": (Decimal("250.00"), Decimal("250.00")),
    }
    obtido = {
        categoria: (limite.normal, limite.viagem)
        for categoria, limite in politica.LIMITES_DIARIOS.items()
    }
    assert obtido == esperado


def test_rn006_tres_categorias_reconhecidas():
    """RN-006: só alimentacao, transporte_urbano e hospedagem são reconhecidas,
    na forma normalizada."""
    assert politica.CATEGORIAS_RECONHECIDAS == {
        "alimentacao",
        "transporte_urbano",
        "hospedagem",
    }


def test_rn008_valor_de_nota_e_100():
    """RN-008 / AMB-007: nota obrigatória acima de 100,00 (fixo, não amplia
    em viagem)."""
    assert politica.VALOR_ACIMA_DO_QUAL_EXIGE_NOTA == Decimal("100.00")


def test_rn002_teto_de_um_bilhao():
    """RN-002 / AMB-018: valor absoluto a partir de 1.000.000.000,00 é
    entrada_invalida."""
    assert politica.VALOR_ABSOLUTO_MAXIMO == Decimal("1000000000.00")


def test_rn010_viagem_cobre_d_e_d_mais_1():
    """RN-010: hospedagem com nota na data D põe em viagem D e D+1."""
    assert politica.CATEGORIA_QUE_COMPROVA_VIAGEM == "hospedagem"
    # D e D+1 → um dia após a data da hospedagem
    assert politica.DIAS_EM_VIAGEM_APOS_HOSPEDAGEM == 1


def test_motivos_na_ordem_da_secao_8():
    """Seção 4 (códigos de motivo) / seção 8: códigos na ordem das etapas."""
    # Tabela "Códigos de motivo" da seção 4, na ordem das etapas 1, 3, 4, 5, 6, 7, 9
    assert [m.value for m in Motivo] == [
        "entrada_invalida",
        "valor_invalido",
        "fora_do_periodo",
        "categoria_fora_da_politica",
        "nota_fiscal_ausente",
        "duplicata",
        "limite_diario_excedido",
    ]


def test_rn011_status_da_saida():
    """RN-011: status aprovado, parcial ou recusado."""
    assert [s.value for s in Status] == ["aprovado", "parcial", "recusado"]


def test_constantes_monetarias_sao_decimal():
    """RN-003 / DT-001: toda constante monetária da política é Decimal, nunca float."""
    monetarias = [
        politica.VALOR_ACIMA_DO_QUAL_EXIGE_NOTA,
        politica.VALOR_ABSOLUTO_MAXIMO,
    ]
    for limite in politica.LIMITES_DIARIOS.values():
        monetarias += [limite.normal, limite.viagem]
    assert all(type(v) is Decimal for v in monetarias)
