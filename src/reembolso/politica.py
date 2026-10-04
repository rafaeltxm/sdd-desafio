"""Leitura do arquivo de política e constantes de interpretação (plan seção 4)."""

from decimal import Decimal
from types import MappingProxyType

from reembolso.dinheiro import arredondar, contexto_exato, truncar
from reembolso.leitura import (
    ErroDeArquivo,
    e_data,
    e_numero,
    ler_json,
    rejeitar_chaves_repetidas,
    tem_ate_2_casas,
    tem_texto,
)
from reembolso.modelo import Politica, Tabela, TabelaAplicada
from reembolso.normalizacao import normalizar_texto

# RN-009, AMB-006, AMB-022: as únicas que ampliam em viagem
CATEGORIAS_AMPLIADAS_EM_VIAGEM = frozenset({"alimentacao", "transporte_urbano"})
CATEGORIA_QUE_COMPROVA_VIAGEM = "hospedagem"  # RN-010
DIAS_EM_VIAGEM_APOS_HOSPEDAGEM = 1  # RN-010: D e D+1
# RN-002, RN-016 / AMB-018: valor absoluto a partir dele é inválido
VALOR_ABSOLUTO_MAXIMO = Decimal("1000000000")
NOME_DA_TABELA_PADRAO = "padrao"  # RN-014, RN-016
# RN-012, RN-016: as duas significam limite por data
PERIODICIDADES = frozenset({"dia", "diaria"})
MOEDA_BASE = "BRL"  # RN-015, RN-016

_AUSENTE = object()


def _numero(objeto: dict, campo: str, caminho: str, *, ate_2_casas: bool) -> Decimal:
    """Número da RN-016: tipo → sinal → teto → casas (DT-015); `-0` vale 0."""
    valor = objeto.get(campo, _AUSENTE)
    if valor is _AUSENTE:
        raise ErroDeArquivo(f"{caminho} ausente")
    if not e_numero(valor):
        raise ErroDeArquivo(f"{caminho} não é número")
    valor = Decimal(valor)
    if valor < 0:
        raise ErroDeArquivo(f"{caminho} negativo")
    if valor >= VALOR_ABSOLUTO_MAXIMO:
        raise ErroDeArquivo(f"{caminho} a partir de {VALOR_ABSOLUTO_MAXIMO}")
    if not ate_2_casas:
        return valor.copy_abs()
    if not tem_ate_2_casas(valor):
        raise ErroDeArquivo(f"{caminho} com mais de 2 casas decimais")
    return arredondar(valor).copy_abs()  # só muda a forma: 60.000 → 60.00


def _tabela(valor, caminho: str) -> Tabela:
    """Tabela da RN-016, indexada pela categoria normalizada (plan seção 4)."""
    if not isinstance(valor, dict):
        raise ErroDeArquivo(f"{caminho} não é tabela")
    limites: dict[str, Decimal] = {}
    for nome, regra in valor.items():
        caminho_regra = f"{caminho}.{nome}"
        categoria = normalizar_texto(nome)
        if not categoria:
            raise ErroDeArquivo(f"{caminho_regra}: nome de categoria vazio")
        if categoria in limites:
            raise ErroDeArquivo(
                f"{caminho_regra}: categoria repetida na tabela ({categoria})"
            )
        if not isinstance(regra, dict):
            raise ErroDeArquivo(f"{caminho_regra} não é objeto")
        limites[categoria] = _numero(
            regra, "limite", f"{caminho_regra}.limite", ate_2_casas=True
        )
        periodicidade = regra.get("periodicidade")
        if not isinstance(periodicidade, str) or periodicidade not in PERIODICIDADES:
            raise ErroDeArquivo(
                f"{caminho_regra}.periodicidade ausente ou diferente de "
                '"dia" e "diaria"'
            )
    return MappingProxyType(limites)


def ler_politica(conteudo: bytes) -> Politica:
    """Bytes do arquivo de política → `Politica` (RN-016, DT-015)."""
    raiz = ler_json(conteudo)
    rejeitar_chaves_repetidas(raiz)
    if not isinstance(raiz, dict):
        raise ErroDeArquivo("raiz não é objeto")

    versao = raiz.get("versao")
    if versao is not None and not tem_texto(versao):
        raise ErroDeArquivo("versao não é texto com algum caractere")
    vigencia = raiz.get("vigencia")
    if vigencia is not None and e_data(vigencia) is None:
        raise ErroDeArquivo("vigencia não é data válida AAAA-MM-DD")
    moeda_base = raiz.get("moeda_base")
    if moeda_base is not None and moeda_base != MOEDA_BASE:
        raise ErroDeArquivo(f'moeda_base diferente de "{MOEDA_BASE}"')

    padrao = _tabela(raiz.get(NOME_DA_TABELA_PADRAO), NOME_DA_TABELA_PADRAO)

    centros = raiz.get("centros_custo")
    if centros is None:
        centros = {}
    elif not isinstance(centros, dict):
        raise ErroDeArquivo("centros_custo não é objeto")
    centros_custo: dict[str, Tabela] = {}
    for chave, tabela in centros.items():
        caminho = f"centros_custo.{chave}"
        if chave == NOME_DA_TABELA_PADRAO or not tem_texto(chave):
            raise ErroDeArquivo(f"{caminho}: nome reservado, vazio ou só com espaços")
        centros_custo[chave] = _tabela(tabela, caminho)

    return Politica(
        versao=versao,
        vigencia=vigencia,
        padrao=padrao,
        centros_custo=MappingProxyType(centros_custo),
        nota_fiscal_acima_de=_numero(
            raiz,
            "nota_fiscal_obrigatoria_acima_de",
            "nota_fiscal_obrigatoria_acima_de",
            ate_2_casas=True,
        ),
        acrescimo_em_viagem_percentual=_numero(
            raiz,
            "acrescimo_em_viagem_percentual",
            "acrescimo_em_viagem_percentual",
            ate_2_casas=False,
        ),
    )


def tabela_aplicada(politica: Politica, centro_custo: str | None) -> TabelaAplicada:
    """RN-014: tabela do centro de custo se for chave exata; senão o `padrao`."""
    if tem_texto(centro_custo) and centro_custo in politica.centros_custo:
        return TabelaAplicada(centro_custo, politica.centros_custo[centro_custo])
    return TabelaAplicada(NOME_DA_TABELA_PADRAO, politica.padrao)


def limite_diario(
    tabela: TabelaAplicada, categoria: str, em_viagem: bool, percentual: Decimal
) -> Decimal:
    """RN-009 / DT-013: limite normal, ou ampliado pelo percentual e truncado."""
    limite = tabela.limites[categoria]
    if not em_viagem or categoria not in CATEGORIAS_AMPLIADAS_EM_VIAGEM:
        return limite
    with contexto_exato():
        ampliado = (limite * (100 + percentual)).scaleb(-2)
    return truncar(ampliado)


def categoria_de_saida(texto, tabela: TabelaAplicada) -> str | None:
    """Seção 4 (`itens[].categoria`): normalizada se está na tabela aplicada
    (inclusive com limite 0); senão o texto como veio; `None` se não é texto."""
    if not isinstance(texto, str):
        return None
    normalizada = normalizar_texto(texto)
    return normalizada if normalizada in tabela.limites else texto
