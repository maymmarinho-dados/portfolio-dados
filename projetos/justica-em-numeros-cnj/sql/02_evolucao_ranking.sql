-- 02 — Evolução anual e ranking descritivo por indicador
-- BigQuery Standard SQL
--
-- PRÉ-REQUISITO: execute 00_inspecao_esquema.sql e valide estes campos:
--   ano, sigla_tribunal, sigla_indicador, valor
-- Confirme no dicionário CNJ/Base dos Dados a sigla, unidade e polaridade.
-- Se houver outras dimensões na tabela (ex.: ramo, recorte ou fase), inclua-as
-- na chave em CTEs, janelas e agrupamentos antes de interpretar resultados.
--
-- O ranking é do maior valor para o menor; não significa melhor desempenho.

DECLARE ano_inicial INT64 DEFAULT 2015;
DECLARE ano_final INT64 DEFAULT 2025;
DECLARE indicador_filtro STRING DEFAULT NULL; -- NULL = todos; defina sigla real para filtrar.

WITH fonte AS (
  SELECT
    ano,
    sigla_tribunal,
    sigla_indicador,
    SAFE_CAST(valor AS FLOAT64) AS valor_num
  FROM `basedosdados.br_cnj_datajud.tribunal_ano`
  WHERE ano BETWEEN ano_inicial - 1 AND ano_final
    AND (indicador_filtro IS NULL OR sigla_indicador = indicador_filtro)
),

-- Detecta linhas repetidas e conflitos na chave atualmente proposta.
-- Se houver dimensões físicas adicionais, inclua-as antes de consolidar.
qualidade AS (
  SELECT
    ano,
    sigla_tribunal,
    sigla_indicador,
    COUNT(*) AS quantidade_registros,
    COUNT(DISTINCT valor_num) AS quantidade_valores_distintos,
    COUNTIF(valor_num IS NULL) AS quantidade_valores_invalidos,
    CASE
      WHEN COUNT(DISTINCT valor_num) = 1 THEN MIN(valor_num)
      ELSE NULL
    END AS valor_indicador
  FROM fonte
  GROUP BY ano, sigla_tribunal, sigla_indicador
),

-- Só entram valores sem conflito na sequência analítica.
valores_validos AS (
  SELECT *
  FROM qualidade
  WHERE quantidade_valores_distintos = 1
),

serie AS (
  SELECT
    *,
    LAG(ano) OVER (
      PARTITION BY sigla_tribunal, sigla_indicador
      ORDER BY ano
    ) AS ano_anterior,
    LAG(valor_indicador) OVER (
      PARTITION BY sigla_tribunal, sigla_indicador
      ORDER BY ano
    ) AS valor_ano_anterior
  FROM valores_validos
),
metricas AS (
  SELECT
    *,
    CASE
      WHEN ano_anterior = ano - 1
        THEN valor_indicador - valor_ano_anterior
      ELSE NULL
    END AS variacao_absoluta,
    CASE
      WHEN ano_anterior = ano - 1 THEN SAFE_DIVIDE(
        valor_indicador - valor_ano_anterior,
        NULLIF(ABS(valor_ano_anterior), 0)
      )
      ELSE NULL
    END AS variacao_percentual
  FROM serie
),
ranked AS (
  SELECT
    *,
    DENSE_RANK() OVER (
      PARTITION BY ano, sigla_indicador
      ORDER BY valor_indicador DESC
    ) AS ranking_maior_valor
  FROM metricas
)

-- Mantém todas as chaves na saída para que conflitos também sejam visíveis.
-- Métricas e ranking só existem para chaves com exatamente um valor numérico.
SELECT
  q.ano,
  q.sigla_tribunal,
  q.sigla_indicador,
  r.valor_indicador,
  r.ano_anterior,
  r.valor_ano_anterior,
  r.variacao_absoluta,
  r.variacao_percentual,
  r.ranking_maior_valor,
  q.quantidade_registros,
  q.quantidade_valores_distintos,
  q.quantidade_valores_invalidos,
  CASE
    WHEN q.quantidade_valores_distintos = 0
      THEN 'REVISAR: sem valor numérico válido'
    WHEN q.quantidade_valores_distintos > 1
      THEN 'REVISAR: valores conflitantes na chave'
    WHEN q.quantidade_registros > 1 AND q.quantidade_valores_invalidos > 0
      THEN 'ATENÇÃO: duplicados e valores nulos/não numéricos'
    WHEN q.quantidade_registros > 1
      THEN 'ATENÇÃO: múltiplas linhas com valor consistente'
    WHEN q.quantidade_valores_invalidos > 0
      THEN 'ATENÇÃO: valor nulo/não numérico'
    ELSE 'OK'
  END AS status_qualidade
FROM qualidade AS q
LEFT JOIN ranked AS r
  ON q.ano = r.ano
  AND q.sigla_tribunal = r.sigla_tribunal
  AND q.sigla_indicador = r.sigla_indicador
WHERE q.ano BETWEEN ano_inicial AND ano_final
ORDER BY
  q.ano DESC,
  q.sigla_indicador,
  r.ranking_maior_valor,
  q.sigla_tribunal;
