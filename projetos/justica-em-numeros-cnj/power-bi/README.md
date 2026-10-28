# Dashboard Power BI — Fluxo processual do Judiciário

Este pacote prepara a análise para montar no Power BI um dashboard de **casos novos, pendentes, baixados, Índice de Atendimento à Demanda (IAD) e Taxa de Congestionamento**, com recortes de 1º grau, 2º grau e Juizados Especiais.

> **Estado da entrega:** os dados públicos foram preparados e passaram pelas verificações descritas abaixo. Este ambiente não executa o Power BI Desktop, portanto não foi criado nem validado um arquivo `.pbix`. O CSV, as medidas DAX, o script de atualização e o roteiro de montagem estão prontos para abrir no Power BI Desktop e salvar o relatório como `.pbix`.

## Arquivos

- [`dados_fluxo_cnj_powerbi.csv`](dados_fluxo_cnj_powerbi.csv): base tratada de 1.595 linhas, 2009–2025, pronta para importar.
- [`preparar_base_powerbi.py`](preparar_base_powerbi.py): baixa o ZIP oficial do CNJ e recria o CSV sem bibliotecas extras.
- [`medidas_dax.dax`](medidas_dax.dax): medidas dos três recortes processuais e comparação por tribunal.
- [`consulta_power_query.m`](consulta_power_query.m): alternativa para definir tipos pelo Editor Avançado do Power Query.
- [`validar_base_powerbi.py`](validar_base_powerbi.py): repete os testes de chave, reconciliação de totais e fórmulas.
- [`gerar_previa.py`](gerar_previa.py): recria a imagem estática do layout (requer `matplotlib`).
- [Prévia estática do layout](dashboard_preview.png): proposta visual calculada com os dados CNJ; não é uma captura de um relatório interativo do Power BI.

## Fonte e granularidade

A base vem do arquivo `JN_23-Jun-2026.csv`, distribuído no pacote oficial do [CNJ de 23 de junho de 2026](https://www.cnj.jus.br/wp-content/uploads/2026/06/23-jun-2026.zip). A publicação do Justiça em Números 2026 é identificada pelo CNJ como ano-base 2025. O arquivo contém informações por ano, ramo/Justiça, sigla e sequência de órgão, além de muitas métricas; este pacote seleciona somente 15 indicadores para os três recortes.

A linha conserva a chave `ano + justica + sigla_tribunal + seq_orgao`. `tipo_registro` separa as linhas de consolidação de Justiça (`seq_orgao` 999991 ou 999992) das linhas de tribunal. **Não some as duas categorias juntas:** isso duplicaria observações. Para totais por ramo e cartões agregados, use `TOTAL_JUSTICA`; para barras por tribunal, use `TRIBUNAL`.

As métricas de taxa vêm em proporção decimal: por exemplo, `0.70` deve ser exibido como `70%`. `nd`, `n/a` e valores não numéricos viram campos vazios/nulos, não zero.

## Importar no Power BI Desktop

1. Baixe o CSV e salve-o em uma pasta local. Se estiver usando GitHub, abra o arquivo do CSV e use **Download raw file** ou baixe o repositório ZIP.
2. Abra o Power BI Desktop. Selecione **Obter dados → Texto/CSV**, escolha `dados_fluxo_cnj_powerbi.csv` e confira a prévia. Use UTF-8 e vírgula como delimitador; depois escolha **Transformar Dados** ou **Carregar**.
3. No Power Query, confirme os tipos: `ano` e `seq_orgao` como número inteiro; categorias como texto; métricas como número decimal. Como os decimais do CSV usam ponto, defina localidade **English (United States)** para conversão numérica, ou use o arquivo `consulta_power_query.m` e substitua o caminho pelo caminho local do CSV.
4. Renomeie a consulta/tabela para **`FatoFluxo`** e selecione **Fechar e Aplicar**.
5. Em **Modelagem → Nova medida**, copie as medidas de `medidas_dax.dax` uma por vez. O arquivo usa `;` como separador de argumentos para a configuração pt-BR; se o Power BI instalado exigir vírgulas, troque o separador dos argumentos nas fórmulas. Formate as medidas IAD e congestionamento como **Percentual**. Os campos `iad*` e `tc*` no CSV são valores-fonte de conferência; as medidas DAX recalculam as taxas a partir dos volumes para produzir taxas ponderadas em visões agregadas.
6. Monte as páginas sugeridas abaixo, confira os slicers e totais e salve o projeto como `justica-em-numeros-fluxo-processual.pbix`.

## Desenho recomendado do relatório

### Página 1 — Visão geral do 1º grau

- **Filtros:** ano (seleção única), `justica` e, opcionalmente, sigla do tribunal.
- **Cartões:** casos novos, casos pendentes, processos baixados, IAD e taxa de congestionamento. Use as medidas sem sufixo `- Tribunal`, que contam somente linhas consolidadas.
- **Linha temporal:** casos novos, pendentes e baixados por ano, usando as medidas consolidadas e a dimensão `ano`.
- **Barras horizontais:** casos novos ou baixados por `sigla_tribunal`, em ano selecionado, usando as medidas com sufixo `- Tribunal`. Não inclua as siglas agregadas `TJ`, `TRT`, `TRF`, `TRE` etc. junto das siglas individuais.

### Página 2 — Comparação de tribunais

Compare as unidades **no mesmo ano, ramo e recorte processual**. Faça visuais separados para contagens, IAD e congestionamento, usando as medidas de 1º grau com sufixo `- Tribunal`. IAD e taxa de congestionamento são proporções, não devem ser somadas. Em uma comparação geral por Justiça, preserve `justica` como categoria para não misturar contextos institucionais diferentes.

### Página 3 — 2º grau e Juizados Especiais

Monte dois blocos separados de cartões e séries temporais: 2º grau (`cn2`, `cp2`, `tbaix2`, `iad2`, `tc2`) e Juizados (`cnje`, `cpje`, `tbaixje`, `iadje`, `tcje`). Use as medidas consolidadas por ano e ramo da Justiça. Não some recortes de 1º grau, 2º grau e Juizados: podem representar âmbitos processuais sobrepostos.

## Validações feitas nesta preparação

- A leitura do arquivo produziu **1.595 linhas**, com anos entre **2009 e 2025**, e não encontrou duplicidades na chave `ano + justica + sigla + seq_orgao`.
- Nos anos e ramos com valores disponíveis, os totais consolidados da fonte coincidiram com a soma das linhas detalhadas para casos novos, pendentes e baixados: **96 comparações para 1º grau, 81 para 2º grau e 34 para Juizados**, sem diferença.
- As fórmulas `IAD = baixados / casos novos` e `congestionamento = pendentes / (pendentes + baixados)` reproduziram as taxas publicadas nas linhas consolidadas, com diferença máxima abaixo de `0.000000000000006` decorrente de precisão de ponto flutuante.
- Essas verificações testam a extração e consistência interna do arquivo de junho de 2026. Não substituem validação de definições metodológicas por indicador nem a conferência de cobertura com o BigQuery.

## Cuidados de interpretação

- Os cartões somam linhas agregadas por ramo; ao filtrar um ramo, o cartão passa a mostrar somente aquele ramo.
- Não use `AVERAGE` das taxas dos tribunais para obter uma taxa nacional. Recalcule IAD e congestionamento sobre os volumes somados, como fazem as medidas DAX.
- Não mostre simultaneamente linhas `TOTAL_JUSTICA` e `TRIBUNAL` em um mesmo visual de soma.
- Variação em uma taxa não explica por si só sua causa; evite linguagem causal sem análise adicional.
- O código do tribunal pode não ser comparável ao longo de toda a série. Confira as mudanças de cobertura e metodologia antes de interpretar tendência.

## Publicação no portfólio

Depois de montar e conferir o `.pbix`, salve uma captura de cada página em `power-bi/`, atualize este arquivo com o link de compartilhamento (se for público) e registre data de atualização e filtros. Se não puder compartilhar um link público do Power BI Service, publique as capturas e o `.pbix` apenas se o repositório e o arquivo forem destinados à divulgação pública. Não inclua credenciais, dados pessoais ou arquivos privados.

## Referências

- [CNJ — Justiça em Números](https://www.cnj.jus.br/pesquisas-judiciarias/justica-em-numeros/) — identifica Justiça em Números 2026 como ano-base 2025.
- [Pacote oficial CNJ de 23/06/2026](https://www.cnj.jus.br/wp-content/uploads/2026/06/23-jun-2026.zip) — inclui `JN_23-Jun-2026.csv` e `Variaveis.csv`.
- [Glossário de Indicadores de Desempenho — CNJ](https://www.cnj.jus.br/wp-content/uploads/2026/02/glossario-indicadores-desempenho-13-02-2026.pdf).
- [Catálogo e regras de tratamento do projeto](../docs/catalogo-indicadores.md).
- [Dicionário de dados do projeto](../docs/dicionario-de-dados.md).
