-- 00 — Inspeção do esquema e validação da granularidade
-- BigQuery Standard SQL
-- Fonte: models/br_cnj_datajud/schema.yml e SQL oficial da Base dos Dados.
-- Execute o script inteiro. Os resultados aparecem em conjuntos separados.

-- 1) Esquema físico: nomes e tipos das colunas publicadas.
SELECT
  column_name,
  data_type,
  is_nullable,
  ordinal_position
FROM `basedosdados.br_cnj_datajud.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'tribunal_ano'
ORDER BY ordinal_position;

-- 2) Integridade da chave e frequência observada por combinação.
-- Chave oficial proposta: ano + sigla_tribunal + ramo_justica + sigla_indicador.
WITH por_chave AS (
  SELECT
    ano,
    sigla_tribunal,
    ramo_justica,
    sigla_indicador,
    COUNT(*) AS ocorrencias
  FROM `basedosdados.br_cnj_datajud.tribunal_ano`
  GROUP BY ano, sigla_tribunal, ramo_justica, sigla_indicador
),
resumo AS (
  SELECT
    COUNT(*) AS quantidade_chaves,
    COUNTIF(ocorrencias > 1) AS chaves_repetidas,
    SUM(ocorrencias) AS quantidade_linhas,
    MAX(ocorrencias) AS maximo_linhas_por_chave
  FROM por_chave
),
qualidade_nulos AS (
  SELECT
    COUNTIF(
      ano IS NULL
      OR sigla_tribunal IS NULL
      OR ramo_justica IS NULL
      OR sigla_indicador IS NULL
    ) AS linhas_com_chave_nula,
    COUNTIF(valor IS NULL) AS linhas_com_valor_nulo
  FROM `basedosdados.br_cnj_datajud.tribunal_ano`
)
SELECT *
FROM resumo
CROSS JOIN qualidade_nulos;

-- 3) Detalhe das chaves repetidas. Esperado: zero linhas se a unicidade
-- documentada pela Base dos Dados também se confirmar na tabela consultada.
SELECT
  ano,
  sigla_tribunal,
  ramo_justica,
  sigla_indicador,
  COUNT(*) AS quantidade_linhas,
  ARRAY_AGG(DISTINCT valor IGNORE NULLS ORDER BY valor) AS valores_distintos
FROM `basedosdados.br_cnj_datajud.tribunal_ano`
GROUP BY ano, sigla_tribunal, ramo_justica, sigla_indicador
HAVING COUNT(*) > 1
ORDER BY ano, sigla_tribunal, ramo_justica, sigla_indicador;
