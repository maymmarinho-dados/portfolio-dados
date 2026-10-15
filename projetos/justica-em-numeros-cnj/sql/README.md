# Consultas SQL — Justiça em Números (CNJ)

Esta pasta contém um fluxo exploratório em três etapas para trabalhar com a tabela `basedosdados.br_cnj_datajud.tribunal_ano`. As consultas foram escritas para BigQuery Standard SQL.

> **Status:** os scripts são uma base de exploração. Antes de interpretar números, valide os campos no esquema da tabela e mapeie cada `sigla_indicador` ao seu nome, fórmula, unidade e polaridade oficiais. A consulta analítica depende dos campos `ano`, `sigla_tribunal`, `sigla_indicador` e `valor`; o esquema completo ainda não foi confirmado.

## Ordem recomendada

1. `00_inspecao_esquema.sql`
2. `01_perfil_indicadores.sql`
3. Consulte o dicionário de códigos e ajuste os campos, se necessário.
4. `02_evolucao_ranking.sql`

## 00 — Inspeção do esquema (`00_inspecao_esquema.sql`)

### Para que serve

Consulta `INFORMATION_SCHEMA.COLUMNS` para mostrar as colunas físicas da tabela, seus tipos BigQuery, nulabilidade e ordem no esquema. É o primeiro passo porque os erros anteriores mostraram que nomes supostos como `grau` não são necessariamente colunas reais da tabela.

### O que entrega

Uma linha por coluna, com:

- `column_name`: nome do campo;
- `data_type`: tipo de dados declarado no BigQuery;
- `is_nullable`: se o campo admite nulo;
- `ordinal_position`: posição do campo no esquema.

### Como usar

Use essa saída para confirmar os nomes reais e corrigir as consultas seguintes. Procure dimensões além de tribunal, ano e indicador: se existirem, elas podem explicar várias linhas para a mesma combinação aparentemente duplicada.

## 01 — Perfil dos indicadores (`01_perfil_indicadores.sql`)

### Para que serve

Faz um inventário preliminar por `sigla_indicador`, resumindo volume de linhas, cobertura temporal, quantidade de tribunais e valores que não são convertidos para número.

### Como funciona

- Agrupa registros por sigla do indicador;
- conta as linhas e os anos distintos;
- encontra o primeiro e o último ano encontrados;
- conta tribunais distintos;
- tenta converter `valor` para `FLOAT64` com `SAFE_CAST` e conta como inválidos ou nulos os valores cuja conversão retorna `NULL`.

### O que entrega

| Campo de saída | Leitura |
|---|---|
| `sigla_indicador` | Código encontrado para o indicador; requer consulta ao dicionário oficial para obter descrição e unidade. |
| `quantidade_linhas` | Número de observações da sigla na tabela, não necessariamente número de casos judiciais. |
| `quantidade_anos` | Número de anos distintos com linhas para a sigla. |
| `primeiro_ano`, `ultimo_ano` | Limites observados na extração, sem afirmar cobertura completa entre eles. |
| `quantidade_tribunais` | Tribunais distintos encontrados para a sigla. |
| `valores_nao_numericos_ou_nulos` | Linhas em que `SAFE_CAST(valor AS FLOAT64)` resulta nulo; pode incluir nulo original ou conteúdo não numérico. |

### Como interpretar

Este perfil ajuda a escolher um indicador e detectar cobertura incompleta ou problemas de conversão. Ele **não** informa ainda o significado da sigla, a unidade ou se o indicador é favorável quando cresce. Isso vem do dicionário/metodologia CNJ.

## 02 — Evolução e ranking (`02_evolucao_ranking.sql`)

### Para que serve

Produz uma tabela analítica por ano, tribunal e indicador com valor, mudança anual e ranking descritivo. Inclui verificações de duplicidade/conflito na granularidade proposta.

### Parâmetros

- `ano_inicial`: primeiro ano exibido; default `2015`.
- `ano_final`: último ano exibido; default `2025`.
- `indicador_filtro`: sigla para restringir a análise. Em `NULL`, considera todas as siglas.

A consulta lê o ano imediatamente anterior a `ano_inicial` para poder calcular a primeira variação do período. Essa observação anterior não aparece na saída final, porque o resultado é filtrado de volta ao intervalo solicitado.

### Etapas internas (CTEs)

1. **`fonte`**: limita a janela temporal, aplica o filtro opcional e converte `valor` para número com `SAFE_CAST`.
2. **`qualidade`**: agrupa por ano, tribunal e sigla; conta registros, valores numéricos distintos e conversões nulas. Só define `valor_indicador` quando existe exatamente um valor numérico distinto. Se houver conflito, deixa o valor nulo.
3. **`valores_validos`**: retira chaves com zero ou mais de um valor distinto. Esses conflitos não entram nas variações nem no ranking.
4. **`serie`**: usa `LAG` para recuperar ano e valor anteriores dentro de cada tribunal e indicador.
5. **`metricas`**: calcula variação absoluta e percentual apenas quando a linha anterior é do ano imediatamente precedente. O percentual fica nulo se o ano não for consecutivo, se não houver anterior ou se o anterior for zero.
6. **`ranked`**: aplica `DENSE_RANK` por ano e indicador, do maior valor para o menor. Empates compartilham a mesma posição e a posição seguinte não é pulada.

### Colunas entregues

| Campo | Conteúdo |
|---|---|
| `ano` | Ano da observação atual. |
| `sigla_tribunal` | Tribunal associado ao registro. |
| `sigla_indicador` | Código da métrica; mapear no dicionário oficial. |
| `valor_indicador` | Valor numérico observado para a chave analítica. Unidade depende do indicador. |
| `ano_anterior` | Ano da observação anterior usada pelo `LAG`; pode não ser consecutivo. |
| `valor_ano_anterior` | Valor da observação anterior. |
| `variacao_absoluta` | Valor atual menos anterior; só calculada em anos consecutivos. |
| `variacao_percentual` | Variação relativa ao módulo do valor anterior; uma proporção como `0.10` representa 10%. |
| `ranking_maior_valor` | Posição em ordem decrescente dentro do mesmo ano e indicador. Não é um ranking de eficiência. |
| `quantidade_registros` | Quantas linhas fonte foram agrupadas para a chave proposta. |
| `quantidade_valores_distintos` | Quantidade de valores numéricos distintos observados para a chave. |
| `quantidade_valores_invalidos` | Quantos valores não puderam ser convertidos em número ou eram nulos. |

### O que o analista pode fazer com a saída

- observar a trajetória anual de um indicador por tribunal;
- identificar altas e quedas entre anos consecutivos;
- comparar valores de tribunais para o mesmo indicador e ano;
- localizar chaves que concentraram vários registros ou tiveram valores não numéricos;
- decidir quais casos precisam de investigação antes de consolidar resultados.

### Limitações e validações obrigatórias

- O ranking vai de maior para menor valor, **não** de pior para melhor nem de melhor para pior. A polaridade varia por indicador.
- O valor não tem unidade própria sem o mapeamento da sigla. Não compare indicadores distintos entre si.
- A consulta assume uma chave composta por `ano`, `sigla_tribunal` e `sigla_indicador`. Se o esquema contiver dimensões adicionais, inclua-as no agrupamento, nas funções de janela e no ranking. Caso contrário, recortes diferentes podem ser tratados indevidamente como conflitos.
- Um ou mais valores distintos na mesma chave podem indicar dimensão omitida, não erro da fonte.
- `01_perfil_indicadores.sql` conta nulos/conversões inválidas; em `02_evolucao_ranking.sql`, esses registros não constituem valor numérico distinto. Chaves sem exatamente um valor numérico distinto são excluídas da série final.
- Os scripts foram revisados estaticamente, mas ainda precisam ser executados no BigQuery depois de validar o esquema real.

## Fonte e documentação

- [Tabela Justiça em Números (DataJud) — Base dos Dados](https://basedosdados.org/dataset/60de97a5-aae7-4cda-871f-b314b497d768)
- [Dicionário de dados deste projeto](../docs/dicionario-de-dados.md)
- [Glossário dos Indicadores de Desempenho — CNJ](https://www.cnj.jus.br/wp-content/uploads/2026/02/glossario-indicadores-desempenho-13-02-2026.pdf)
