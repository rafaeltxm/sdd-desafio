"""Etapas 2 a 9 da seção 8 da spec: Entrada → Resultado."""

from datetime import date, timedelta
from decimal import Decimal

from reembolso.cambio import cotacao
from reembolso.dinheiro import arredondar, contexto_exato
from reembolso.justificativa import justificar
from reembolso.modelo import (
    Cambio,
    Cotacao,
    Despesa,
    DespesaInvalida,
    Entrada,
    ItemResultado,
    Motivo,
    Periodo,
    Politica,
    PoliticaAplicada,
    Resultado,
    Status,
    TabelaAplicada,
    Totais,
)
from reembolso.politica import (
    CATEGORIA_QUE_COMPROVA_VIAGEM,
    DIAS_EM_VIAGEM_APOS_HOSPEDAGEM,
    categoria_de_saida,
    limite_diario,
    tabela_aplicada,
)

ZERO = Decimal("0.00")


def _converter(valor: Decimal, taxa: Decimal) -> Decimal:
    """Etapa 2 (RN-003, RN-015, AMB-026): `valor` × taxa, produto exato (DT-012),
    arredondado ao centavo uma única vez, em reais."""
    with contexto_exato():
        return arredondar(valor * taxa)


def _taxa_e_data(cotacao_usada: Cotacao | None) -> tuple[Decimal | None, str | None]:
    """`taxa_cambio` e `data_cotacao` da saída (seção 4); nulas sem cotação."""
    if cotacao_usada is None:
        return None, None
    data = cotacao_usada.data
    return cotacao_usada.taxa, data.isoformat() if data is not None else None


def _status(
    considerado: Decimal, reembolsado: Decimal
) -> tuple[Status, Motivo | None]:
    """RN-011 pelos valores; corte do limite → `limite_diario_excedido` (RN-009)."""
    if reembolsado == considerado:
        return Status.APROVADO, None
    if reembolsado > 0:
        return Status.PARCIAL, Motivo.LIMITE_DIARIO_EXCEDIDO
    return Status.RECUSADO, Motivo.LIMITE_DIARIO_EXCEDIDO


def _item_invalido(
    despesa: DespesaInvalida, tabela: TabelaAplicada, politica: Politica
) -> ItemResultado:
    """Etapa 1 (RN-002): recusado, `entrada_invalida`, sem valor considerado."""
    status, motivo = Status.RECUSADO, Motivo.ENTRADA_INVALIDA
    categoria = categoria_de_saida(despesa.categoria_texto, tabela)  # seção 4
    return ItemResultado(
        id=despesa.id,
        data=despesa.data_texto,
        categoria=categoria,
        valor_informado=despesa.valor_informado,
        moeda=despesa.moeda_saida,
        taxa_cambio=None,
        data_cotacao=None,
        valor_considerado=None,
        valor_reembolsado=ZERO,
        status=status,
        motivo=motivo,
        em_viagem=None,
        limite_diario=None,
        justificativa=justificar(
            status,
            motivo,
            data=None,
            categoria=categoria,
            valor_considerado=None,
            valor_reembolsado=ZERO,
            limite_diario=None,
            nota_fiscal_acima_de=politica.nota_fiscal_acima_de,
        ),
        avisos=despesa.avisos,
    )


def _item_recusado(
    despesa: Despesa,
    cotacao_usada: Cotacao | None,
    considerado: Decimal | None,
    motivo: Motivo,
    tabela: TabelaAplicada,
    politica: Politica,
) -> ItemResultado:
    """Etapas 2 a 7: recusado antes do limite diário; não consome limite.

    Sem cotação (etapa 2), `cotacao_usada` e `considerado` são `None`."""
    status = Status.RECUSADO
    categoria = categoria_de_saida(despesa.categoria_texto, tabela)  # seção 4
    taxa, data_cotacao = _taxa_e_data(cotacao_usada)
    return ItemResultado(
        id=despesa.id,
        data=despesa.data_texto,
        categoria=categoria,
        valor_informado=despesa.valor_informado,
        moeda=despesa.moeda,
        taxa_cambio=taxa,
        data_cotacao=data_cotacao,
        valor_considerado=considerado,
        valor_reembolsado=ZERO,
        status=status,
        motivo=motivo,
        em_viagem=None,
        limite_diario=None,
        justificativa=justificar(
            status,
            motivo,
            data=despesa.data,
            categoria=categoria,
            valor_considerado=considerado,
            valor_reembolsado=ZERO,
            limite_diario=None,
            nota_fiscal_acima_de=politica.nota_fiscal_acima_de,
            moeda=despesa.moeda,
            taxa_cambio=taxa,
            data_cotacao=cotacao_usada.data if cotacao_usada is not None else None,
        ),
        avisos=despesa.avisos,
    )


def _motivo_de_recusa(
    despesa: Despesa,
    considerado: Decimal,
    periodo: Periodo,
    tabela: TabelaAplicada,
    politica: Politica,
) -> Motivo | None:
    """Etapas 3 a 6 da seção 8, nesta ordem; a primeira que recusa encerra."""
    if considerado <= 0:  # RN-004
        return Motivo.VALOR_INVALIDO
    if not periodo.inicio <= despesa.data <= periodo.fim:  # RN-005, AMB-009
        return Motivo.FORA_DO_PERIODO
    # RN-006, RN-014, AMB-012, AMB-021: ausente da tabela aplicada ou com limite 0
    limite = tabela.limites.get(despesa.categoria)
    if limite is None or limite == 0:
        return Motivo.CATEGORIA_FORA_DA_POLITICA
    # RN-008, AMB-007, AMB-008, AMB-027: valor individual, antes do limite
    if considerado > politica.nota_fiscal_acima_de and not despesa.tem_nota_fiscal:
        return Motivo.NOTA_FISCAL_AUSENTE
    return None


def _separar_duplicatas(
    despesas: list[Despesa],
) -> tuple[list[Despesa], list[Despesa]]:
    """Etapa 7 (RN-007, AMB-010, AMB-028): agrupa por (data, categoria,
    fornecedor, moeda, `valor` arredondado na moeda da despesa); a original é a
    primeira com nota fiscal, ou a primeira na ordem da entrada. Devolve
    (originais, duplicatas)."""
    grupos: dict[tuple[date, str, str, str, Decimal], list[Despesa]] = {}
    for despesa in sorted(despesas, key=lambda d: d.posicao):
        chave = (
            despesa.data,
            despesa.categoria,
            despesa.fornecedor,
            despesa.moeda,
            arredondar(despesa.valor_informado),
        )
        grupos.setdefault(chave, []).append(despesa)
    originais, duplicatas = [], []
    for grupo in grupos.values():
        original = next((d for d in grupo if d.tem_nota_fiscal), grupo[0])
        originais.append(original)
        duplicatas.extend(d for d in grupo if d is not original)
    return originais, duplicatas


def _dias_em_viagem(despesas: list[Despesa]) -> set[date]:
    """Etapa 8 (RN-010, AMB-004): {D, D+1} de cada hospedagem com nota fiscal
    entre as despesas que passaram pelas etapas 1 a 7."""
    dias = set()
    for despesa in despesas:
        if (
            despesa.categoria == CATEGORIA_QUE_COMPROVA_VIAGEM
            and despesa.tem_nota_fiscal
        ):
            for dias_depois in range(DIAS_EM_VIAGEM_APOS_HOSPEDAGEM + 1):
                # D+1 depois de 9999-12-31 não existe: nenhuma despesa cai nele
                if despesa.data <= date.max - timedelta(days=dias_depois):
                    dias.add(despesa.data + timedelta(days=dias_depois))
    return dias


def _aplicar_limite(
    despesas: list[Despesa],
    conversoes: dict[int, tuple[Cotacao, Decimal]],
    dias_em_viagem: set[date],
    tabela: TabelaAplicada,
    politica: Politica,
) -> dict[int, ItemResultado]:
    """Etapa 9 (RN-009): saldo por (data, categoria), consumido na ordem da entrada;
    limite da tabela aplicada, ampliado nas datas da etapa 8 (RN-010, DT-013)."""
    saldos: dict[tuple[date, str], Decimal] = {}
    itens = {}
    for despesa in sorted(despesas, key=lambda d: d.posicao):
        cotacao_usada, considerado = conversoes[despesa.posicao]
        taxa, data_cotacao = _taxa_e_data(cotacao_usada)
        em_viagem = despesa.data in dias_em_viagem
        limite = limite_diario(
            tabela,
            despesa.categoria,
            em_viagem,
            politica.acrescimo_em_viagem_percentual,
        )
        chave = (despesa.data, despesa.categoria)
        saldo = saldos.get(chave, limite)
        reembolsado = min(considerado, saldo)
        saldos[chave] = saldo - reembolsado
        status, motivo = _status(considerado, reembolsado)
        itens[despesa.posicao] = ItemResultado(
            id=despesa.id,
            data=despesa.data_texto,
            categoria=despesa.categoria,
            valor_informado=despesa.valor_informado,
            moeda=despesa.moeda,
            taxa_cambio=taxa,
            data_cotacao=data_cotacao,
            valor_considerado=considerado,
            valor_reembolsado=reembolsado,
            status=status,
            motivo=motivo,
            em_viagem=em_viagem,
            limite_diario=limite,
            justificativa=justificar(
                status,
                motivo,
                data=despesa.data,
                categoria=despesa.categoria,
                valor_considerado=considerado,
                valor_reembolsado=reembolsado,
                limite_diario=limite,
                nota_fiscal_acima_de=politica.nota_fiscal_acima_de,
                moeda=despesa.moeda,
                taxa_cambio=taxa,
                data_cotacao=cotacao_usada.data,
            ),
            avisos=despesa.avisos,
        )
    return itens


def _totais(itens: list[ItemResultado]) -> Totais:
    """Seção 4: solicitado e reembolsado somados; glosado = diferença (RN-001).

    O solicitado só soma `valor_considerado` não nulo e maior que zero: ficam
    fora os recusados por `entrada_invalida` (RN-002) e `cambio_indisponivel`
    (RN-015), que não têm valor em reais, e os com valor ≤ 0 (RN-004).
    """
    solicitado = sum(
        (
            item.valor_considerado
            for item in itens
            if item.valor_considerado is not None and item.valor_considerado > 0
        ),
        ZERO,
    )
    reembolsado = sum((item.valor_reembolsado for item in itens), ZERO)
    return Totais(
        valor_solicitado=solicitado,
        valor_reembolsado=reembolsado,
        valor_glosado=solicitado - reembolsado,
    )


def calcular(entrada: Entrada, politica: Politica, cambio: Cambio) -> Resultado:
    """Um item por despesa, na ordem da entrada (RN-001), e os totais.

    `politica` e `cambio` já validados (RN-016); a tabela aplicada é escolhida
    uma vez (RN-014).
    """
    tabela = tabela_aplicada(politica, entrada.colaborador.centro_custo)
    validas = [d for d in entrada.despesas if isinstance(d, Despesa)]
    por_posicao: dict[int, ItemResultado] = {}
    conversoes: dict[int, tuple[Cotacao, Decimal]] = {}
    seguem = []
    for despesa in validas:
        # etapa 2 (RN-015, AMB-024, AMB-025): sem cotação, nenhuma regra de valor
        cotacao_usada = cotacao(cambio, despesa.moeda, despesa.data)
        if cotacao_usada is None:
            por_posicao[despesa.posicao] = _item_recusado(
                despesa, None, None, Motivo.CAMBIO_INDISPONIVEL, tabela, politica
            )
            continue
        considerado = _converter(despesa.valor_informado, cotacao_usada.taxa)
        conversoes[despesa.posicao] = (cotacao_usada, considerado)
        motivo = _motivo_de_recusa(
            despesa, considerado, entrada.periodo, tabela, politica
        )
        if motivo is None:
            seguem.append(despesa)
        else:
            por_posicao[despesa.posicao] = _item_recusado(
                despesa, cotacao_usada, considerado, motivo, tabela, politica
            )
    originais, duplicatas = _separar_duplicatas(seguem)
    for despesa in duplicatas:
        por_posicao[despesa.posicao] = _item_recusado(
            despesa, *conversoes[despesa.posicao], Motivo.DUPLICATA, tabela, politica
        )
    por_posicao.update(
        _aplicar_limite(
            originais, conversoes, _dias_em_viagem(originais), tabela, politica
        )
    )
    itens = [
        por_posicao[d.posicao]
        if isinstance(d, Despesa)
        else _item_invalido(d, tabela, politica)
        for d in entrada.despesas
    ]
    return Resultado(
        colaborador=entrada.colaborador,
        periodo=entrada.periodo,
        politica=PoliticaAplicada(
            versao=politica.versao,
            vigencia=politica.vigencia,
            tabela_aplicada=tabela.nome,
        ),
        itens=itens,
        totais=_totais(itens),
        avisos=entrada.avisos,
    )
