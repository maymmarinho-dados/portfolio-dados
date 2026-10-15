-- 00 — Inspeção do esquema físico da tabela
-- Execute primeiro. Não depende de presumir campos de negócio.

SELECT
  column_name,
  data_type,
  is_nullable,
  ordinal_position
FROM `basedosdados.br_cnj_datajud.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'tribunal_ano'
ORDER BY ordinal_position;
