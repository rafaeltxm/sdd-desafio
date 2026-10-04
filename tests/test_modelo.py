"""Enums do modelo: códigos de `status` e `motivo` da seção 4 da spec."""

from reembolso.modelo import Motivo, Status


def test_motivos_na_ordem_da_secao_8():
    """Seção 4 (códigos de motivo) / seção 8: códigos na ordem das etapas."""
    # Tabela "Códigos de motivo" da seção 4, na ordem das etapas 1 a 7 e 9
    assert [m.value for m in Motivo] == [
        "entrada_invalida",
        "cambio_indisponivel",
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
