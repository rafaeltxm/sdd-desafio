"""argparse, leitura do arquivo, gravação atômica da saída e códigos de saída."""

import argparse
import os
import secrets
import sys
from pathlib import Path

from reembolso.entrada import ler_entrada
from reembolso.leitura import ErroDeArquivo
from reembolso.motor import calcular
from reembolso.saida import para_texto

SUCESSO = 0
ERRO_DE_ARQUIVO = 1  # DT-007; o erro de uso sai com 2, padrão do `argparse`


def _argumentos() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="reembolso")
    subcomandos = parser.add_subparsers(dest="subcomando", required=True)
    calcular_ = subcomandos.add_parser("calcular")
    calcular_.add_argument("--input", required=True, type=Path)
    calcular_.add_argument("--output", required=True, type=Path)
    return parser


def _ler(caminho: Path) -> bytes:
    try:
        return caminho.read_bytes()
    except OSError as erro:
        raise ErroDeArquivo(
            f"não foi possível ler o arquivo de entrada {caminho}: {erro.strerror}"
        ) from erro


def _gravar_atomico(caminho: Path, conteudo: bytes) -> None:
    """Temporário no mesmo diretório + `os.replace`; em falha, remove o temporário
    e a saída fica como estava (DT-006)."""
    temporario = caminho.with_name(f".{caminho.name}.{secrets.token_hex(8)}.tmp")
    try:
        with open(temporario, "xb") as arquivo:
            arquivo.write(conteudo)
        os.replace(temporario, caminho)
    except OSError as erro:
        temporario.unlink(missing_ok=True)
        raise ErroDeArquivo(
            f"não foi possível gravar o arquivo de saída {caminho}: {erro.strerror}"
        ) from erro


def main(argv: list[str] | None = None) -> int:
    argumentos = _argumentos().parse_args(argv)
    try:
        # todo o processamento em memória antes de tocar a saída (DT-006)
        resultado = calcular(ler_entrada(_ler(argumentos.input)))
        _gravar_atomico(argumentos.output, para_texto(resultado).encode("utf-8"))
    except ErroDeArquivo as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return ERRO_DE_ARQUIVO
    return SUCESSO
