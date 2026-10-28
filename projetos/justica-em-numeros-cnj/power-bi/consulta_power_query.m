// Power Query M — cole no Editor Avançado de uma Consulta em Branco.
// Troque o caminho abaixo pelo local onde salvou dados_fluxo_cnj_powerbi.csv.
let
    Fonte = Csv.Document(
        File.Contents("C:\\CAMINHO\\dados_fluxo_cnj_powerbi.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(
        Cabecalhos,
        {
            {"ano", Int64.Type},
            {"justica", type text},
            {"sigla_tribunal", type text},
            {"seq_orgao", Int64.Type},
            {"tipo_registro", type text},
            {"cn1_casos_novos_1g", type number},
            {"cp1_casos_pendentes_1g", type number},
            {"tbaix1_processos_baixados_1g", type number},
            {"iad1_atendimento_demanda_1g", type number},
            {"tc1_congestionamento_1g", type number},
            {"cn2_casos_novos_2g", type number},
            {"cp2_casos_pendentes_2g", type number},
            {"tbaix2_processos_baixados_2g", type number},
            {"iad2_atendimento_demanda_2g", type number},
            {"tc2_congestionamento_2g", type number},
            {"cnje_casos_novos_juizados", type number},
            {"cpje_casos_pendentes_juizados", type number},
            {"tbaixje_processos_baixados_juizados", type number},
            {"iadje_atendimento_demanda_juizados", type number},
            {"tcje_congestionamento_juizados", type number}
        },
        "en-US"
    )
in
    Tipos
