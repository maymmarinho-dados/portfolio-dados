# Dicionário de dados — Justiça em Números (CNJ)

## Fonte e granularidade

| Atributo | Descrição |
|---|---|
| Organização responsável | Conselho Nacional de Justiça (CNJ) |
| Fonte de acesso | Base dos Dados, BigQuery |
| Tabela | `basedosdados.br_cnj_datajud.tribunal_ano` |
| Conteúdo | Indicadores agregados do Poder Judiciário por tribunal e ano, com códigos de indicadores e atributos auxiliares no dataset. A descrição geral informa também recortes por grau e fase processual. |
| Cobertura descrita | Brasil, 2009–2025 |
| Granularidade documentada | Uma linha por ano + tribunal + ramo da Justiça + indicador. O schema oficial declara essa combinação única. |

A página da Base dos Dados informa que o dataset inclui indicadores como casos novos, casos pendentes, taxa de congestionamento, índice de atendimento à demanda e IPC-Jus, além de tabelas auxiliares de tribunais e dicionário de códigos. Ela também observa que códigos institucionais podem variar entre anos.

## Campos da tabela

O schema e o SQL de transformação publicados pela Base dos Dados confirmam os cinco campos abaixo. A consulta `00_inspecao_esquema.sql` do projeto permite verificar os tipos e a unicidade diretamente no BigQuery atual. A definição de chave única é documental até que essa consulta seja executada.

| Campo | Definição de trabalho | Uso analítico | Confiança / validação |
|---|---|---|---|
| `ano` | `INT64`, ano de referência da estatística. | Filtro temporal e ordenação da série. | Confirmado no SQL de transformação oficial. |
| `sigla_tribunal` | `STRING`, sigla do tribunal a que a estatística se refere. | Identificação da unidade judiciária. | Integra a chave única. Códigos institucionais podem variar entre anos. |
| `ramo_justica` | `STRING`, ramo sob o qual o CNJ reporta a estatística. | Estratificação e comparações entre unidades do mesmo ramo. | Integra a chave única; a fonte cita STM reportado em dois ramos. |
| `sigla_indicador` | `STRING`, código do indicador estatístico do CNJ. | Identificação da métrica e dos recortes codificados. | Grau e fase processual são codificados no sufixo do código, não em campos separados nesta tabela. |
| `valor` | `FLOAT64`, valor numérico do indicador. | Métrica de origem para variação e ranking. | Unidade e significado dependem do código e do dicionário auxiliar. |

**Chave única documentada:** (`ano`, `sigla_tribunal`, `ramo_justica`, `sigla_indicador`). O schema oficial associa a tabela a um teste de unicidade dessa combinação. Execute a consulta de validação do repositório para confirmar o estado da tabela corrente.

### Consulta para inspecionar colunas e tipos

```sql
SELECT
  column_name,
  data_type,
  is_nullable,
  ordinal_position
FROM `basedosdados.br_cnj_datajud.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'tribunal_ano'
ORDER BY ordinal_position;
```

Depois de confirmar os campos, as siglas disponíveis podem ser inventariadas assim:

```sql
SELECT
  sigla_indicador,
  COUNT(*) AS linhas,
  MIN(ano) AS primeiro_ano,
  MAX(ano) AS ultimo_ano,
  COUNT(DISTINCT sigla_tribunal) AS tribunais,
  COUNT(DISTINCT ramo_justica) AS ramos_justica
FROM `basedosdados.br_cnj_datajud.tribunal_ano`
GROUP BY sigla_indicador
ORDER BY sigla_indicador;
```

## Indicadores de negócio — definições conceituais

As descrições a seguir representam conceitos do CNJ. Elas não substituem o mapeamento da sigla exata usada na tabela: use o dicionário auxiliar para identificar código, fórmula, unidade, escopo e polaridade de cada indicador.

| Conceito | Significado | Unidade / polaridade | Cuidado de interpretação |
|---|---|---|---|
| **Casos novos (Cn)** | Processos que ingressaram no período conforme as regras estatísticas do CNJ. | Geralmente contagem; não é uma medida isolada de qualidade. | Comparar apenas o mesmo período e recorte processual. |
| **Casos baixados (TBaix)** | Processos que foram registrados como baixados segundo as regras do CNJ. | Geralmente contagem. | “Baixado” é um conceito estatístico-administrativo e não equivale necessariamente a julgamento de mérito ou solução substantiva. |
| **Casos pendentes (Cp)** | Processos que permanecem pendentes ao final do período conforme o recorte e as regras do indicador. | Geralmente contagem. | Algumas métricas excluem processos suspensos/sobrestados ou determinadas classes, conforme sua fórmula. |
| **Taxa de congestionamento** | Percentual relativo dos processos que permaneceram pendentes entre os que tramitaram no período. Há variantes, como líquida e específica de execuções fiscais. | Em geral, proporção ou percentual; para as variantes citadas no glossário CNJ, menor é melhor. | Não misturar variantes. Confirmar a fórmula e se a coluna armazena `0–1` ou `0–100`. |
| **Índice de Atendimento à Demanda (IAD)** | Relação entre processos baixados e casos novos (`TBaix / Cn`). | Percentual/proporção; CNJ indica que valor igual ou superior a 100% corresponde a vazão pelo menos igual ao ingresso, e classifica maior como melhor. | Conferir escala e consistência dos recortes no numerador e denominador. |
| **IPC-Jus** | Índice de Produtividade Comparada da Justiça, indicador composto/comparativo publicado pelo CNJ. | Índice; escala e metodologia dependem da documentação e ano de referência. | Não tratar como contagem, nem recalcular sem a metodologia do CNJ. Comparabilidade temporal deve ser confirmada. |

## Campos derivados da análise

| Campo derivado | Cálculo | Interpretação |
|---|---|---|
| `valor_indicador` | Valor limpo/consolidado da chave analítica. | Unidade é definida pelo indicador; não comparar entre métricas distintas. |
| `valor_ano_anterior` | `LAG(valor_indicador)` por tribunal, ramo e indicador, ordenado por ano. | Pode ser de ano não consecutivo quando há lacuna, exceto se o SQL validar a continuidade. |
| `variacao_absoluta` | Valor atual menos valor anterior. | Diferença na unidade original. |
| `variacao_percentual` | `(valor atual - valor anterior) / ABS(valor anterior)`. | Proporção; `0.10` equivale a 10%. Indefinida se o anterior for zero/ausente. |
| `ranking_maior_valor` | `DENSE_RANK` dentro do mesmo ano, ramo e indicador, do maior para o menor valor. | Ordenação matemática, não avaliação automática de melhor/pior tribunal. Aplicar polaridade para interpretar. |
| `quantidade_registros` | Número de linhas da chave agrupada. | Sinal para investigar granularidade, duplicatas e dimensões omitidas. |
| `quantidade_valores_distintos` | Número de valores numéricos distintos na chave. | Mais de um pode indicar conflito ou dimensões legítimas não consideradas. |
| `status_qualidade` | Classificação derivada das contagens de consistência. | Regra analítica do projeto, não dado original do CNJ. |

## Regras para análise e publicação

1. A unidade de `valor` depende da sigla do indicador; nunca a inferir apenas do número.
2. Não usar `AVG`/`MAX` para resolver duplicidade sem entender as dimensões e a granularidade.
3. Não fazer ranking conjunto de indicadores com unidades diferentes.
4. Interpretar ranking à luz da polaridade: por exemplo, IAD e taxa de congestionamento têm direções desejáveis distintas.
5. Não substituir ausência por zero sem justificativa metodológica.
6. Registrar período, data de extração, definições, filtros, exclusões e eventuais mudanças metodológicas.
7. Comparações entre tribunais podem requerer estratificação por ramo ou outras dimensões; não assumir que todos são pares comparáveis.

## Referências

- [Dataset Justiça em Números (DataJud) — Base dos Dados](https://basedosdados.org/dataset/60de97a5-aae7-4cda-871f-b314b497d768)
- [Schema YAML oficial — Base dos Dados](https://github.com/basedosdados/pipelines/blob/main/models/br_cnj_datajud/schema.yml)
- [SQL oficial de transformação — Base dos Dados](https://github.com/basedosdados/pipelines/blob/main/models/br_cnj_datajud/br_cnj_datajud__tribunal_ano.sql)
- [Glossário dos Indicadores de Desempenho — CNJ, fevereiro de 2026](https://www.cnj.jus.br/wp-content/uploads/2026/02/glossario-indicadores-desempenho-13-02-2026.pdf)
- [Base de dados do Justiça em Números — CNJ](https://www.cnj.jus.br/pesquisas-judiciarias/justica-em-numeros/base-de-dados/)
