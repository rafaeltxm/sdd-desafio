"""CLI: seção 4 da spec (Interface), RN-002 (erro de arquivo), DT-006, DT-007."""

from decimal import Decimal

import pytest
import simplejson

from conftest import construir_despesa, construir_entrada
from reembolso.cli import main

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


def _calcular(entrada, saida) -> int:
    return executar("calcular", "--input", str(entrada), "--output", str(saida))


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
        ("calcular", "--output", "{saida}"),
        ("calcular", "--input", "{entrada}"),
        ("processar", "--input", "{entrada}", "--output", "{saida}"),
        (),
    ],
    ids=["sem --input", "sem --output", "subcomando diferente", "sem subcomando"],
)
def test_erro_de_uso_codigo_2_sem_saida(tmp_path, capsys, argumentos):
    """Seção 4 (Interface): erro de uso → mensagem, código 2 (DT-007), sem saída."""
    entrada = tmp_path / "entrada.json"
    entrada.write_text(ENTRADA_VALIDA, encoding="utf-8")
    saida = tmp_path / "saida.json"
    preenchidos = [a.format(entrada=entrada, saida=saida) for a in argumentos]

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
