-- 01 — Inventário das siglas e cobertura temporal
-- Execute após confirmar os nomes das colunas em 00_inspecao_esquema.sql.
-- Se o esquema usar nomes diferentes, substitua-os nesta consulta.

SELECT
  sigla_indicador,
  COUNT(*) AS quantidade_linhas,
  COUNT(DISTINCT ano) AS quantidade_anos,
  MIN(ano) AS primeiro_ano,
  MAX(ano) AS ultimo_ano,
  COUNT(DISTINCT sigla_tribunal) AS quantidade_tribunais,
  COUNTIF(SAFE_CAST(valor AS FLOAT64) IS NULL) AS valores_nao_numericos_ou_nulos
FROM `basedosdados.br_cnj_datajud.tribunal_ano`
GROUP BY sigla_indicador
ORDER BY sigla_indicador;
