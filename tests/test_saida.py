"""Serialização da saída: seção 4 da spec (Saída), DT-001, DT-008."""

from datetime import date
from decimal import Decimal

import simplejson

from reembolso.modelo import (
    Colaborador,
    ItemResultado,
    Motivo,
    Periodo,
    Resultado,
    Status,
    Totais,
)
from reembolso.saida import para_dicionario, para_texto

# Ordem das linhas da tabela "Saída" da seção 4 da spec.
CAMPOS_DO_TOPO = ["colaborador", "periodo", "itens", "totais", "avisos"]
CAMPOS_DO_ITEM = [
    "id",
    "data",
    "categoria",
    "valor_informado",
    "valor_considerado",
    "valor_reembolsado",
    "status",
    "motivo",
    "em_viagem",
    "limite_diario",
    "justificativa",
    "avisos",
]
CAMPOS_DOS_TOTAIS = ["valor_solicitado", "valor_reembolsado", "valor_glosado"]


def item(**campos):
    padrao = dict(
        id="d-1",
        data="2026-07-03",
        categoria="alimentacao",
        valor_informado=Decimal("45.00"),
        valor_considerado=Decimal("45.00"),
        valor_reembolsado=Decimal("45.00"),
        status=Status.APROVADO,
        motivo=None,
        em_viagem=False,
        limite_diario=Decimal("60.00"),
        justificativa="Aprovado.",
        avisos=(),
    )
    padrao.update(campos)
    return ItemResultado(**padrao)


def item_entrada_invalida():
    return item(
        id=None,
        data=None,
        categoria=None,
        valor_informado=None,
        valor_considerado=None,
        valor_reembolsado=Decimal("0"),
        status=Status.RECUSADO,
        motivo=Motivo.ENTRADA_INVALIDA,
        em_viagem=None,
        limite_diario=None,
        justificativa="Recusado.",
    )


def resultado(itens=(), avisos=(), competencia="2026-07", nome="Ana"):
    return Resultado(
        colaborador=Colaborador(id="c-1", nome=nome),
        periodo=Periodo(
            inicio=date(2026, 7, 1),
            fim=date(2026, 7, 31),
            inicio_texto="2026-07-01",
            fim_texto="2026-07-31",
            competencia=competencia,
        ),
        itens=list(itens),
        totais=Totais(
            valor_solicitado=Decimal("45.00"),
            valor_reembolsado=Decimal("45.00"),
            valor_glosado=Decimal("0.00"),
        ),
        avisos=tuple(avisos),
    )


def ler(texto):
    """Lê o texto de volta preservando a ordem das chaves e os números exatos."""
    return simplejson.loads(texto, use_decimal=True, object_pairs_hook=list)


def test_ordem_dos_campos_do_topo_igual_a_tabela_da_spec():
    """Seção 4 / DT-008: campos do topo na ordem da tabela de saída."""
    pares = ler(para_texto(resultado(itens=[item()])))
    assert [chave for chave, _ in pares] == CAMPOS_DO_TOPO
    assert list(para_dicionario(resultado())) == CAMPOS_DO_TOPO


def test_ordem_dos_campos_de_itens_igual_a_tabela_da_spec():
    """Seção 4 / DT-008: campos de `itens[]` na ordem da tabela de saída."""
    pares = dict(ler(para_texto(resultado(itens=[item(), item_entrada_invalida()]))))
    for item_lido in pares["itens"]:
        assert [chave for chave, _ in item_lido] == CAMPOS_DO_ITEM


def test_conteudo_de_colaborador_periodo_e_totais():
    """Seção 4: `colaborador` com `id` e `nome`; `periodo` com `inicio` e `fim`
    copiados e `competencia`; `totais` com os três valores."""
    dicionario = para_dicionario(resultado())
    assert dicionario["colaborador"] == {"id": "c-1", "nome": "Ana"}
    assert dicionario["periodo"] == {
        "competencia": "2026-07",
        "inicio": "2026-07-01",
        "fim": "2026-07-31",
    }
    assert list(dicionario["totais"]) == CAMPOS_DOS_TOTAIS
    assert dicionario["totais"] == {
        "valor_solicitado": Decimal("45.00"),
        "valor_reembolsado": Decimal("45.00"),
        "valor_glosado": Decimal("0.00"),
    }


def test_status_e_motivo_saem_como_codigo_em_texto():
    """Seção 4: `status` e `motivo` são os códigos em texto da tabela de motivos."""
    texto = para_texto(
        resultado(
            itens=[
                item(
                    valor_reembolsado=Decimal("15.00"),
                    status=Status.PARCIAL,
                    motivo=Motivo.LIMITE_DIARIO_EXCEDIDO,
                )
            ]
        )
    )
    lido = simplejson.loads(texto)["itens"][0]
    assert lido["status"] == "parcial"
    assert lido["motivo"] == "limite_diario_excedido"


def test_decimal_sai_como_numero_json_exato():
    """DT-001 / seção 4: `valor_informado` 33.333 sai como o número 33.333."""
    texto = para_texto(resultado(itens=[item(valor_informado=Decimal("33.333"))]))
    assert '"valor_informado": 33.333,' in texto
    lido = simplejson.loads(texto, use_decimal=True)
    assert lido["itens"][0]["valor_informado"] == Decimal("33.333")


def test_decimal_com_expoente_enorme_sai_como_numero():
    """DT-001 / seção 4: 1e999999 pode sair escrito como 1E+999999, mas como
    número, não texto nem infinito."""
    texto = para_texto(resultado(itens=[item(valor_informado=Decimal("1E+999999"))]))
    assert '"valor_informado": 1E+999999,' in texto
    lido = simplejson.loads(texto, use_decimal=True)
    assert lido["itens"][0]["valor_informado"] == Decimal("1E+999999")


def test_nenhum_valor_monetario_e_float():
    """DT-001: nenhum campo monetário do dicionário de saída é `float`."""
    dicionario = para_dicionario(resultado(itens=[item()]))
    monetarios = [
        dicionario["itens"][0][campo]
        for campo in (
            "valor_informado",
            "valor_considerado",
            "valor_reembolsado",
            "limite_diario",
        )
    ] + list(dicionario["totais"].values())
    assert all(type(valor) is Decimal for valor in monetarios)


def test_campos_nulos_saem_null():
    """Seção 4: campos nulos de item `entrada_invalida` e `competencia` nula
    saem `null`."""
    texto = para_texto(resultado(itens=[item_entrada_invalida()], competencia=None))
    lido = simplejson.loads(texto)
    assert lido["periodo"]["competencia"] is None
    item_lido = lido["itens"][0]
    for campo in (
        "id",
        "data",
        "categoria",
        "valor_informado",
        "valor_considerado",
        "em_viagem",
        "limite_diario",
    ):
        assert item_lido[campo] is None, campo
    assert '"motivo": "entrada_invalida"' in texto
    assert '"em_viagem": null' in texto
    # item aprovado: motivo nulo (RN-011)
    assert simplejson.loads(para_texto(resultado(itens=[item()])))["itens"][0][
        "motivo"
    ] is None


def test_em_viagem_sai_como_booleano():
    """Seção 4: `em_viagem` é booleano no item avaliado no limite."""
    texto = para_texto(resultado(itens=[item(em_viagem=True)]))
    assert '"em_viagem": true' in texto


def test_avisos_sai_lista_vazia_sem_aviso():
    """Seção 4 / RN-013: `avisos` do topo e do item são lista vazia sem aviso."""
    lido = simplejson.loads(para_texto(resultado(itens=[item()])))
    assert lido["avisos"] == []
    assert lido["itens"][0]["avisos"] == []


def test_avisos_saem_lista_de_textos_na_ordem():
    """Seção 4 / RN-013: avisos saem como lista de textos, na ordem recebida."""
    avisos_item = (
        "chave repetida: extra (2 ocorrências; valeu a última)",
        "chave repetida: obs (2 ocorrências; valeu a última)",
    )
    avisos_topo = ("chave repetida: colaborador.nome (2 ocorrências; valeu a última)",)
    lido = simplejson.loads(
        para_texto(resultado(itens=[item(avisos=avisos_item)], avisos=avisos_topo))
    )
    assert lido["itens"][0]["avisos"] == list(avisos_item)
    assert lido["avisos"] == list(avisos_topo)


def test_quebra_de_linha_em_texto_sai_escapada():
    """Seção 4: uma quebra de linha dentro de um texto sai como `\\n`."""
    texto = para_texto(resultado(nome="Ana\nMaria"))
    assert '"nome": "Ana\\nMaria"' in texto


def test_caractere_nao_ascii_sai_em_utf8_sem_escape():
    """Seção 4 / DT-008: `ensure_ascii=False` — acento e emoji saem como o
    próprio caractere, sem `\\u`."""
    texto = para_texto(resultado(nome="João 😀"))
    assert '"nome": "João 😀"' in texto
    assert "\\u" not in texto
    assert texto.encode("utf-8").decode("utf-8") == texto


def test_indentacao_de_dois_espacos_e_quebra_de_linha_final():
    """DT-008: `indent=2` e quebra de linha final."""
    texto = para_texto(resultado())
    assert texto.startswith('{\n  "colaborador": {\n    "id": "c-1",')
    assert texto.endswith("}\n")
    assert not texto.endswith("\n\n")


def test_mesma_entrada_mesmo_texto_byte_a_byte():
    """DT-008: o mesmo `Resultado` gera o mesmo texto, byte a byte."""
    itens = [item(), item_entrada_invalida(), item(avisos=("a", "b"))]
    primeiro = para_texto(resultado(itens=itens)).encode("utf-8")
    segundo = para_texto(resultado(itens=itens)).encode("utf-8")
    assert primeiro == segundo
