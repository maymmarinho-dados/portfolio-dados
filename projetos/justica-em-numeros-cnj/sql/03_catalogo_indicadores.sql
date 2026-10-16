-- 03 — Catálogo dos indicadores e tratamento SQL
-- BigQuery Standard SQL
-- O dicionário oficial tem uma linha por código da coluna sigla_indicador.
DECLARE indicador_filtro STRING DEFAULT 'tc';

-- A) Lista completa: código e descrição publicada pelo CNJ.
SELECT
  d.chave AS sigla_indicador,
  d.valor AS descricao_cnj,
  NULLIF(TRIM(d.cobertura_temporal), '') AS cobertura_temporal
FROM `basedosdados.br_cnj_datajud.dicionario` AS d
WHERE d.id_tabela = 'tribunal_ano'
  AND d.nome_coluna = 'sigla_indicador'
ORDER BY d.chave;

-- B) Lista completa com cobertura efetivamente observada na tabela de fatos.
-- Indicadores sem observações materializadas continuam aparecendo com zero.
WITH dicionario AS (
  SELECT
    chave AS sigla_indicador,
    valor AS descricao_cnj
  FROM `basedosdados.br_cnj_datajud.dicionario`
  WHERE id_tabela = 'tribunal_ano'
    AND nome_coluna = 'sigla_indicador'
),
observado AS (
  SELECT
    sigla_indicador,
    COUNT(*) AS quantidade_observacoes,
    COUNT(DISTINCT ano) AS quantidade_anos,
    MIN(ano) AS primeiro_ano_observado,
    MAX(ano) AS ultimo_ano_observado,
    COUNT(DISTINCT sigla_tribunal) AS quantidade_tribunais,
    COUNT(DISTINCT ramo_justica) AS quantidade_ramos
  FROM `basedosdados.br_cnj_datajud.tribunal_ano`
  GROUP BY sigla_indicador
)
SELECT
  d.sigla_indicador,
  d.descricao_cnj,
  COALESCE(o.quantidade_observacoes, 0) AS quantidade_observacoes,
  COALESCE(o.quantidade_anos, 0) AS quantidade_anos,
  o.primeiro_ano_observado,
  o.ultimo_ano_observado,
  COALESCE(o.quantidade_tribunais, 0) AS quantidade_tribunais,
  COALESCE(o.quantidade_ramos, 0) AS quantidade_ramos
FROM dicionario AS d
LEFT JOIN observado AS o USING (sigla_indicador)
ORDER BY d.sigla_indicador;

-- C) Exemplo de série de um código.
-- Troque o valor da variável no início do script pelo código desejado.

SELECT
  f.ano,
  f.sigla_tribunal,
  f.ramo_justica,
  f.sigla_indicador,
  d.valor AS descricao_cnj,
  f.valor
FROM `basedosdados.br_cnj_datajud.tribunal_ano` AS f
LEFT JOIN `basedosdados.br_cnj_datajud.dicionario` AS d
  ON d.id_tabela = 'tribunal_ano'
  AND d.nome_coluna = 'sigla_indicador'
  AND d.chave = f.sigla_indicador
WHERE f.sigla_indicador = LOWER(TRIM(indicador_filtro))
ORDER BY f.ano, f.ramo_justica, f.sigla_tribunal;
