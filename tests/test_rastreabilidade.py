"""Rastreabilidade spec → testes (seção 9 da spec, plan seção 6).

Lê a `spec.md` e falha se alguma regra `RN-NNN` não aparecer no nome ou na
docstring de um teste, ou se algum valor da coluna "Caso" da seção 7 não for
`id` de um `pytest.param` em `test_casos_de_borda.py`.

Durante a Fase 6 (D-008), uma regra ou caso sem teste só é aceito se estiver em
`PENDENTES`, com a task dona; a pendência que já tem teste ou que não está
mais na spec faz a suíte falhar (DT-016).
"""

import ast
import re
from pathlib import Path

TESTES = Path(__file__).parent
SPEC = TESTES.parent / "specs" / "001-motor-reembolso" / "spec.md"
TASKS = SPEC.with_name("tasks.md")

PENDENTES: dict[str, str] = {  # some quando a Fase 6 terminar (DT-016, D-008)
    "Argumento repetido": "T-036",
    "Argumento desconhecido": "T-036",
    "Argumento sobrando": "T-036",
}
PRIMEIRA_TASK_DA_FASE_6, ULTIMA_TASK_DA_FASE_6 = 35, 36


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


def _tasks_existentes() -> set[str]:
    return set(
        re.findall(
            r"^- \[[ x]\] \*\*(T-\d{3})\*\*", TASKS.read_text(encoding="utf-8"), re.M
        )
    )


def _pendencias_invalidas(
    na_spec: set[str], testados: set[str], pendentes: dict
) -> list[str]:
    """Pendência que já tem teste ou que não está na spec (DT-016)."""
    com_teste = [
        f"{item}: já tem teste, tirar de PENDENTES"
        for item in pendentes
        if item in testados
    ]
    fora = [f"{item}: não está na spec" for item in pendentes if item not in na_spec]
    return com_teste + fora


def _donos_invalidos(pendentes: dict, existentes: set[str]) -> list[str]:
    """Dono que não é uma task da Fase 6 existente em `tasks.md` (DT-016)."""
    invalidos = []
    for item, dono in pendentes.items():
        numero = int(dono.removeprefix("T-"))
        if dono not in existentes or not (
            PRIMEIRA_TASK_DA_FASE_6 <= numero <= ULTIMA_TASK_DA_FASE_6
        ):
            invalidos.append(f"{item}: dono {dono}")
    return invalidos


def test_toda_regra_da_spec_tem_teste():
    """Seção 9: cada regra RN-001 a RN-016 tem pelo menos um teste que a referencia."""
    regras = _regras_da_spec()
    assert regras, "nenhuma regra extraída da spec"
    assert sorted(regras - _regras_testadas() - PENDENTES.keys()) == []


def test_todo_caso_de_borda_da_spec_tem_teste():
    """Seção 9: cada caso de borda da seção 7 tem um teste com `id` igual ao "Caso"."""
    casos = _casos_da_secao_7()
    assert casos, "nenhum caso extraído da seção 7"
    testados = _ids_dos_casos_de_borda()
    assert [
        caso for caso in casos if caso not in testados and caso not in PENDENTES
    ] == []


def test_pendencias_sao_estritas():
    """DT-016: nenhuma pendência já tem teste nem está fora da spec."""
    na_spec = _regras_da_spec() | set(_casos_da_secao_7())
    testados = _regras_testadas() | _ids_dos_casos_de_borda()
    assert _pendencias_invalidas(na_spec, testados, PENDENTES) == []


def test_pendencia_com_teste_falha():
    """DT-016: uma pendência que já tem teste faz a verificação falhar."""
    na_spec = {"RN-900", "Caso inventado"}
    pendentes = {"RN-900": "T-035", "Caso inventado": "T-036"}
    assert _pendencias_invalidas(na_spec, set(), pendentes) == []
    assert _pendencias_invalidas(na_spec, {"RN-900"}, pendentes) != []
    assert _pendencias_invalidas(na_spec, {"Caso inventado"}, pendentes) != []


def test_pendencia_fora_da_spec_falha():
    """DT-016: uma pendência que não está na spec faz a verificação falhar."""
    pendentes = {"RN-900": "T-035", "Caso inventado": "T-036"}
    assert _pendencias_invalidas({"RN-900"}, set(), pendentes) != []
    assert _pendencias_invalidas({"Caso inventado"}, set(), pendentes) != []


def test_dono_da_pendencia_e_task_da_fase_6():
    """DT-016: todo dono de pendência é uma task T-035 ou T-036 do `tasks.md`."""
    existentes = {"T-034", "T-035", "T-036", "T-037"}
    assert _donos_invalidos({"a": "T-035", "b": "T-036"}, existentes) == []
    assert _donos_invalidos({"a": "T-034"}, existentes) != []  # antes da Fase 6
    assert _donos_invalidos({"a": "T-037"}, existentes) != []  # depois da Fase 6
    assert _donos_invalidos({"a": "T-036"}, {"T-035"}) != []  # não existe
    assert _donos_invalidos(PENDENTES, _tasks_existentes()) == []
