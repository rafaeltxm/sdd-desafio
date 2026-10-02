"""Rastreabilidade spec → testes (seção 9 da spec, plan seção 6).

Lê a `spec.md` e falha se alguma regra `RN-NNN` não aparecer no nome ou na
docstring de um teste, ou se algum valor da coluna "Caso" da seção 7 não for
`id` de um `pytest.param` em `test_casos_de_borda.py`.
"""

import ast
import re
from pathlib import Path

TESTES = Path(__file__).parent
SPEC = TESTES.parent / "specs" / "001-motor-reembolso" / "spec.md"


def _regras_da_spec() -> set[str]:
    return set(re.findall(r"RN-\d{3}", SPEC.read_text(encoding="utf-8")))


def _casos_da_secao_7() -> list[str]:
    texto = SPEC.read_text(encoding="utf-8")
    secao = re.search(r"^## 7\..*?(?=^## 8\.)", texto, re.M | re.S).group(0)
    linhas = [linha for linha in secao.splitlines() if linha.startswith("|")]
    # linhas[0] é o cabeçalho ("Caso" na primeira coluna); linhas[1], o separador
    assert linhas[0].split("|")[1].strip() == "Caso"
    return [linha.split("|")[1].strip() for linha in linhas[2:]]


def _funcoes_de_teste():
    for arquivo in sorted(TESTES.glob("test_*.py")):
        if arquivo.name == Path(__file__).name:
            continue
        arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            if isinstance(no, ast.FunctionDef) and no.name.startswith("test_"):
                yield no


def _regras_testadas() -> set[str]:
    regras = set()
    for funcao in _funcoes_de_teste():
        # nome `test_rnNNN_...` → RN-NNN; docstring cita `RN-NNN` por extenso
        regras |= {f"RN-{n}" for n in re.findall(r"rn(\d{3})", funcao.name)}
        regras |= set(re.findall(r"RN-\d{3}", ast.get_docstring(funcao) or ""))
    return regras


def _ids_dos_casos_de_borda() -> set[str]:
    arvore = ast.parse((TESTES / "test_casos_de_borda.py").read_text(encoding="utf-8"))
    ids = set()
    for no in ast.walk(arvore):
        if (
            isinstance(no, ast.Call)
            and isinstance(no.func, ast.Attribute)
            and no.func.attr == "param"
        ):
            for argumento in no.keywords:
                if argumento.arg == "id" and isinstance(argumento.value, ast.Constant):
                    ids.add(argumento.value.value)
    return ids


def test_toda_regra_da_spec_tem_teste():
    """Seção 9: cada regra RN-001 a RN-013 tem pelo menos um teste que a referencia."""
    regras = _regras_da_spec()
    assert regras, "nenhuma regra extraída da spec"
    assert sorted(regras - _regras_testadas()) == []


def test_todo_caso_de_borda_da_spec_tem_teste():
    """Seção 9: cada caso de borda da seção 7 tem um teste com `id` igual ao "Caso"."""
    casos = _casos_da_secao_7()
    assert casos, "nenhum caso extraído da seção 7"
    assert [caso for caso in casos if caso not in _ids_dos_casos_de_borda()] == []
