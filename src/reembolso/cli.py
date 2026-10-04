"""argparse, leitura dos três arquivos, gravação atômica da saída e códigos de
saída."""

import argparse
import os
import secrets
import sys
from collections.abc import Callable
from pathlib import Path

from reembolso.cambio import ler_cambio
from reembolso.entrada import ler_entrada
from reembolso.leitura import ErroDeArquivo
from reembolso.motor import calcular
from reembolso.politica import ler_politica
from reembolso.saida import para_texto

SUCESSO = 0
ERRO_DE_ARQUIVO = 1  # DT-007; o erro de uso sai com 2, padrão do `argparse`


class _UmaVez(argparse.Action):
    """Opção aceita uma vez só, separada ou `--opção=valor`; nunca vale "a última
    ocorrência" (seção 4 da spec, Interface)."""

    def __call__(self, parser, namespace, valor, opcao=None):
        if getattr(namespace, self.dest) is not None:
            parser.error(f"argumento {opcao} repetido")
        setattr(namespace, self.dest, valor)


def _argumentos() -> argparse.ArgumentParser:
    # prefixo abreviado (`--inp`) é argumento desconhecido (seção 4, Interface)
    parser = argparse.ArgumentParser(prog="reembolso", allow_abbrev=False)
    subcomandos = parser.add_subparsers(dest="subcomando", required=True)
    calcular_ = subcomandos.add_parser("calcular", allow_abbrev=False)
    for opcao in ("--input", "--politica", "--cambio", "--output"):
        calcular_.add_argument(opcao, required=True, type=Path, action=_UmaVez)
    return parser


def _ler[T](nome: str, caminho: Path, leitor: Callable[[bytes], T]) -> T:
    """Bytes do arquivo → `leitor`; o erro ganha o nome do arquivo (DT-007)."""
    try:
        conteudo = caminho.read_bytes()
    except OSError as erro:
        raise ErroDeArquivo(
            f"{nome}: não foi possível ler {caminho}: {erro.strerror}"
        ) from erro
    try:
        return leitor(conteudo)
    except ErroDeArquivo as erro:
        raise ErroDeArquivo(f"{nome}: {erro}") from erro


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
            f"saída: não foi possível gravar {caminho}: {erro.strerror}"
        ) from erro


def main(argv: list[str] | None = None) -> int:
    argumentos = _argumentos().parse_args(argv)
    try:
        # política e câmbio antes de qualquer despesa (seção 8 da spec); todo o
        # processamento em memória antes de tocar a saída (DT-006)
        politica = _ler("política", argumentos.politica, ler_politica)
        cambio = _ler("câmbio", argumentos.cambio, ler_cambio)
        entrada = _ler("entrada", argumentos.input, ler_entrada)
        resultado = calcular(entrada, politica, cambio)
        _gravar_atomico(argumentos.output, para_texto(resultado).encode("utf-8"))
    except ErroDeArquivo as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return ERRO_DE_ARQUIVO
    return SUCESSO
