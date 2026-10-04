"""CLI: seção 4 da spec (Interface), RN-002 e RN-016 (erro de arquivo), AMB-031,
DT-006, DT-007."""

from decimal import Decimal
from pathlib import Path

import pytest
import simplejson

from conftest import construir_despesa, construir_entrada, construir_politica
from reembolso.cli import main

ENVELOPE = Path(__file__).resolve().parent.parent / "exemplos" / "envelope"
POLITICA = ENVELOPE / "politica-v4.json"
CAMBIO = ENVELOPE / "cambio.json"

ENTRADA_VALIDA = simplejson.dumps(
    construir_entrada([construir_despesa(valor=Decimal("72.50"))]), use_decimal=True
)
ENTRADA_SEM_COLABORADOR = (
    '{"periodo": {"inicio": "2026-07-01", "fim": "2026-07-31"}, "despesas": []}'
)
CONTEUDO_ANTERIOR = b"conteudo anterior \xff\x00 qualquer\n"


def executar(*argumentos: str) -> int:
    """`main` com os argumentos; erro de uso do `argparse` vira o código do
    `SystemExit`."""
    try:
        return main(list(argumentos))
    except SystemExit as saida:
        return saida.code


def _calcular(entrada, saida, politica=POLITICA, cambio=CAMBIO) -> int:
    return executar(
        "calcular",
        "--input", str(entrada),
        "--politica", str(politica),
        "--cambio", str(cambio),
        "--output", str(saida),
    )


def _politica_sem_padrao(tmp_path) -> Path:
    documento = construir_politica()
    del documento["padrao"]
    caminho = tmp_path / "politica.json"
    caminho.write_text(simplejson.dumps(documento, use_decimal=True), encoding="utf-8")
    return caminho


def test_sucesso_codigo_0_e_saida_igual_a_processar(tmp_path, processar):
    """Seção 4 (Interface): sucesso grava a saída e termina com código 0."""
    entrada = tmp_path / "entrada.json"
    entrada.write_text(ENTRADA_VALIDA, encoding="utf-8")
    saida = tmp_path / "saida.json"

    assert _calcular(entrada, saida) == 0
    # o arquivo gravado é o resultado do pipeline em memória para a mesma entrada
    gravado = simplejson.loads(saida.read_text(encoding="utf-8"), use_decimal=True)
    assert gravado == processar(ENTRADA_VALIDA)
    # 72,50 de alimentação fora de viagem → 60,00 parcial (RN-009)
    assert gravado["itens"][0]["valor_reembolsado"] == Decimal("60.00")


def test_sucesso_substitui_saida_preexistente(tmp_path, processar):
    """Seção 4 (Interface): em sucesso a saída é gravada, mesmo que já exista."""
    entrada = tmp_path / "entrada.json"
    entrada.write_text(ENTRADA_VALIDA, encoding="utf-8")
    saida = tmp_path / "saida.json"
    saida.write_bytes(CONTEUDO_ANTERIOR)

    assert _calcular(entrada, saida) == 0
    gravado = simplejson.loads(saida.read_text(encoding="utf-8"), use_decimal=True)
    assert gravado == processar(ENTRADA_VALIDA)


def test_rn002_entrada_ausente_codigo_1_sem_saida(tmp_path, capsys):
    """RN-002: arquivo de entrada ausente é erro de arquivo; código 1 (DT-007)."""
    saida = tmp_path / "saida.json"

    assert _calcular(tmp_path / "nao_existe.json", saida) == 1
    assert not saida.exists()
    erro = capsys.readouterr().err
    assert erro.startswith("erro: ")
    assert "Traceback" not in erro


def test_rn002_entrada_invalida_codigo_1_sem_saida(tmp_path, capsys):
    """RN-002: arquivo sem `colaborador` é erro de arquivo; código 1 (DT-007)."""
    entrada = tmp_path / "entrada.json"
    entrada.write_text(ENTRADA_SEM_COLABORADOR, encoding="utf-8")
    saida = tmp_path / "saida.json"

    assert _calcular(entrada, saida) == 1
    assert not saida.exists()
    erro = capsys.readouterr().err
    assert erro.startswith("erro: ")
    assert "Traceback" not in erro


@pytest.mark.parametrize(
    "conteudo_entrada",
    [None, ENTRADA_SEM_COLABORADOR.encode(), b"\xff nao e utf-8", b"{nao e json"],
    ids=["entrada ausente", "sem colaborador", "nao UTF-8", "nao JSON"],
)
def test_rn002_erro_de_arquivo_preserva_saida_preexistente(tmp_path, conteudo_entrada):
    """RN-002: em erro de arquivo, a saída preexistente fica intacta byte a byte."""
    entrada = tmp_path / "entrada.json"
    if conteudo_entrada is not None:
        entrada.write_bytes(conteudo_entrada)
    saida = tmp_path / "saida.json"
    saida.write_bytes(CONTEUDO_ANTERIOR)

    assert _calcular(entrada, saida) == 1
    assert saida.read_bytes() == CONTEUDO_ANTERIOR


def test_rn002_pasta_de_saida_inexistente_codigo_1(tmp_path, capsys):
    """RN-002: saída que não pode ser gravada (pasta inexistente) é erro de arquivo."""
    entrada = tmp_path / "entrada.json"
    entrada.write_text(ENTRADA_VALIDA, encoding="utf-8")
    saida = tmp_path / "nao_existe" / "saida.json"

    assert _calcular(entrada, saida) == 1
    assert not saida.parent.exists()
    erro = capsys.readouterr().err
    assert erro.startswith("erro: ")
    assert "Traceback" not in erro


def test_rn002_falha_na_gravacao_nao_deixa_temporario(tmp_path, capsys):
    """RN-002 / DT-006: falha ao substituir a saída não deixa temporário nem
    altera nada.

    A saída é uma pasta: o temporário é criado ao lado e a substituição falha.
    """
    entrada = tmp_path / "entrada.json"
    entrada.write_text(ENTRADA_VALIDA, encoding="utf-8")
    saida = tmp_path / "saida"
    saida.mkdir()
    (saida / "dentro.txt").write_bytes(CONTEUDO_ANTERIOR)
    antes = sorted(p.name for p in tmp_path.iterdir())

    assert _calcular(entrada, saida) == 1
    assert sorted(p.name for p in tmp_path.iterdir()) == antes
    assert [p.name for p in saida.iterdir()] == ["dentro.txt"]
    assert (saida / "dentro.txt").read_bytes() == CONTEUDO_ANTERIOR
    erro = capsys.readouterr().err
    assert erro.startswith("erro: ")
    assert "Traceback" not in erro


def test_rn002_erro_de_entrada_nao_deixa_temporario(tmp_path):
    """RN-002 / DT-006: erro de arquivo na entrada não deixa nada no diretório
    da saída."""
    entrada = tmp_path / "entrada.json"
    entrada.write_text(ENTRADA_SEM_COLABORADOR, encoding="utf-8")
    pasta_saida = tmp_path / "saidas"
    pasta_saida.mkdir()

    assert _calcular(entrada, pasta_saida / "saida.json") == 1
    assert list(pasta_saida.iterdir()) == []


@pytest.mark.parametrize(
    "argumentos",
    [
        ("calcular", "--politica", "{politica}", "--cambio", "{cambio}",
         "--output", "{saida}"),
        ("calcular", "--input", "{entrada}", "--cambio", "{cambio}",
         "--output", "{saida}"),
        ("calcular", "--input", "{entrada}", "--politica", "{politica}",
         "--output", "{saida}"),
        ("calcular", "--input", "{entrada}", "--politica", "{politica}",
         "--cambio", "{cambio}"),
        ("processar", "--input", "{entrada}", "--politica", "{politica}",
         "--cambio", "{cambio}", "--output", "{saida}"),
        (),
    ],
    ids=["sem --input", "sem --politica", "sem --cambio", "sem --output",
         "subcomando diferente", "sem subcomando"],
)
def test_erro_de_uso_codigo_2_sem_saida(tmp_path, capsys, argumentos):
    """Seção 4 (Interface) / AMB-031: erro de uso, inclusive sem `--politica` ou
    sem `--cambio` → mensagem, código 2 (DT-007), sem saída."""
    entrada = tmp_path / "entrada.json"
    entrada.write_text(ENTRADA_VALIDA, encoding="utf-8")
    saida = tmp_path / "saida.json"
    preenchidos = [
        a.format(entrada=entrada, politica=POLITICA, cambio=CAMBIO, saida=saida)
        for a in argumentos
    ]

    assert executar(*preenchidos) == 2
    assert not saida.exists()
    erro = capsys.readouterr().err
    assert erro.strip() != ""
    assert "Traceback" not in erro


def test_erro_de_uso_preserva_saida_preexistente(tmp_path):
    """Seção 4 (Interface): erro de uso não cria nem altera o arquivo de saída."""
    saida = tmp_path / "saida.json"
    saida.write_bytes(CONTEUDO_ANTERIOR)

    assert executar("processar", "--input", "x.json", "--output", str(saida)) == 2
    assert saida.read_bytes() == CONTEUDO_ANTERIOR


@pytest.mark.parametrize(
    "omitido", ["--politica", "--cambio"], ids=["sem --politica", "sem --cambio"]
)
def test_amb031_sem_politica_ou_cambio_preserva_saida_preexistente(tmp_path, omitido):
    """AMB-031: `--politica` e `--cambio` são sempre obrigatórios; faltar um é erro
    de uso, e a saída preexistente fica intacta."""
    entrada = tmp_path / "entrada.json"
    entrada.write_text(ENTRADA_VALIDA, encoding="utf-8")
    saida = tmp_path / "saida.json"
    saida.write_bytes(CONTEUDO_ANTERIOR)
    argumentos = {
        "--input": str(entrada),
        "--politica": str(POLITICA),
        "--cambio": str(CAMBIO),
        "--output": str(saida),
    }
    del argumentos[omitido]

    assert executar("calcular", *(x for par in argumentos.items() for x in par)) == 2
    assert saida.read_bytes() == CONTEUDO_ANTERIOR


def _arquivos_com_erro(tmp_path, qual):
    """(entrada, política, câmbio) com um defeito no arquivo `qual`."""
    entrada = tmp_path / "entrada.json"
    entrada.write_text(ENTRADA_VALIDA, encoding="utf-8")
    politica, cambio = POLITICA, CAMBIO
    if qual == "política ausente":
        politica = tmp_path / "nao_existe_politica.json"
    elif qual == "política inválida":
        politica = _politica_sem_padrao(tmp_path)
    elif qual == "câmbio ausente":
        # ENTRADA_VALIDA só tem despesa em BRL: o câmbio é exigido mesmo assim
        cambio = tmp_path / "nao_existe_cambio.json"
    elif qual == "entrada inválida":
        entrada.write_text(ENTRADA_SEM_COLABORADOR, encoding="utf-8")
    return entrada, politica, cambio


ERROS_DE_ARQUIVO = [
    pytest.param("política ausente", "erro: política:", id="política ausente"),
    pytest.param("política inválida", "erro: política:", id="política inválida"),
    pytest.param("câmbio ausente", "erro: câmbio:", id="câmbio ausente"),
    pytest.param("entrada inválida", "erro: entrada:", id="entrada inválida"),
]


@pytest.mark.parametrize(("qual", "prefixo"), ERROS_DE_ARQUIVO)
def test_rn016_erro_de_arquivo_codigo_1_sem_saida(tmp_path, capsys, qual, prefixo):
    """RN-016 / AMB-031: política ou câmbio ausente (mesmo com todas as despesas
    em BRL) ou inválido é erro de arquivo: código 1 (DT-007), sem saída, e a
    mensagem nomeia o arquivo."""
    entrada, politica, cambio = _arquivos_com_erro(tmp_path, qual)
    saida = tmp_path / "saida.json"

    assert _calcular(entrada, saida, politica, cambio) == 1
    assert not saida.exists()
    erro = capsys.readouterr().err
    assert erro.startswith(prefixo)
    assert "Traceback" not in erro


@pytest.mark.parametrize(("qual", "prefixo"), ERROS_DE_ARQUIVO)
def test_rn016_erro_de_arquivo_preserva_saida_preexistente(tmp_path, qual, prefixo):
    """RN-016 / RN-002: erro em qualquer dos três arquivos deixa a saída
    preexistente intacta byte a byte."""
    entrada, politica, cambio = _arquivos_com_erro(tmp_path, qual)
    saida = tmp_path / "saida.json"
    saida.write_bytes(CONTEUDO_ANTERIOR)

    assert _calcular(entrada, saida, politica, cambio) == 1
    assert saida.read_bytes() == CONTEUDO_ANTERIOR


def test_rn016_politica_validada_antes_da_entrada(tmp_path, capsys):
    """RN-016 / seção 8: a política é validada antes de qualquer despesa; com a
    política e a entrada inválidas, a mensagem é da política (plan seção 2)."""
    entrada = tmp_path / "entrada.json"
    entrada.write_text(ENTRADA_SEM_COLABORADOR, encoding="utf-8")
    saida = tmp_path / "saida.json"

    assert _calcular(entrada, saida, politica=_politica_sem_padrao(tmp_path)) == 1
    assert capsys.readouterr().err.startswith("erro: política:")


def test_rn002_saida_nao_gravavel_mensagem_da_saida(tmp_path, capsys):
    """RN-002 / DT-007: falha ao gravar a saída tem mensagem `erro: saída:`."""
    entrada = tmp_path / "entrada.json"
    entrada.write_text(ENTRADA_VALIDA, encoding="utf-8")

    assert _calcular(entrada, tmp_path / "nao_existe" / "saida.json") == 1
    assert capsys.readouterr().err.startswith("erro: saída:")
