# Dicionário de dados — Justiça em Números (CNJ)

## Fonte e granularidade

| Atributo | Descrição |
|---|---|
| Organização responsável | Conselho Nacional de Justiça (CNJ) |
| Fonte de acesso | Base dos Dados, BigQuery |
| Tabela | `basedosdados.br_cnj_datajud.tribunal_ano` |
| Conteúdo | Indicadores agregados do Poder Judiciário por tribunal e ano, com códigos de indicadores e atributos auxiliares no dataset. A descrição geral informa também recortes por grau e fase processual. |
| Cobertura descrita | Brasil, 2009–2025 |
| Granularidade da análise proposta | Ano + tribunal + indicador, sujeita a ajuste conforme dimensões físicas da tabela. |

A página da Base dos Dados informa que o dataset inclui indicadores como casos novos, casos pendentes, taxa de congestionamento, índice de atendimento à demanda e IPC-Jus, além de tabelas auxiliares de tribunais e dicionário de códigos. Ela também observa que códigos institucionais podem variar entre anos.

## Campos usados no script

**Validação pendente:** não foi possível confirmar todo o esquema físico pelo catálogo extraído. O BigQuery sugeriu `sigla_indicador` como nome de campo e rejeitou `grau` na tabela consultada. A coluna `valor` e os tipos precisam ser conferidos na aba **Esquema** ou em `INFORMATION_SCHEMA` antes de serem tratados como definitivos.

| Campo | Definição de trabalho | Uso analítico | Confiança / validação |
|---|---|---|---|
| `ano` | Ano de referência do indicador. | Filtro temporal e ordenação da série. | Nome usado pela consulta; confirmar nome e tipo. |
| `sigla_tribunal` | Código/sigla associado ao tribunal. | Identificação da unidade judiciária e agrupamento. | Nome usado pela consulta; validar domínio e mudanças de códigos por ano. |
| `sigla_indicador` | Código curto para o indicador estatístico. | Seleção e partição de comparações por métrica. | Nome sugerido pelo BigQuery em erro anterior; validar tipo e catálogo de códigos. |
| `valor` | Medida correspondente à sigla de indicador, se este for o campo real. | Valor de origem para variação e ranking. | Nome e tipo ainda precisam de confirmação; unidade depende do indicador. |
| `grau` | Possível dimensão de grau/instância. | Recorte analítico caso exista em tabela ou campo apropriado. | BigQuery retornou “Unrecognized name”; não utilizar como coluna desta tabela sem encontrar nome alternativo. |
| `fase` | Possível dimensão de fase processual. | Recorte analítico caso exista no esquema. | Não confirmada na tabela. |

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
  COUNT(DISTINCT sigla_tribunal) AS tribunais
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
| `valor_ano_anterior` | `LAG(valor_indicador)` por tribunal e indicador, ordenado por ano. | Pode ser de ano não consecutivo quando há lacuna, exceto se o SQL validar a continuidade. |
| `variacao_absoluta` | Valor atual menos valor anterior. | Diferença na unidade original. |
| `variacao_percentual` | `(valor atual - valor anterior) / ABS(valor anterior)`. | Proporção; `0.10` equivale a 10%. Indefinida se o anterior for zero/ausente. |
| `ranking_no_indicador` | `DENSE_RANK` dentro do mesmo ano e indicador, do maior para o menor valor. | Ordenação matemática, não avaliação automática de melhor/pior tribunal. Aplicar polaridade para interpretar. |
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
- [Glossário dos Indicadores de Desempenho — CNJ, fevereiro de 2026](https://www.cnj.jus.br/wp-content/uploads/2026/02/glossario-indicadores-desempenho-13-02-2026.pdf)
- [Base de dados do Justiça em Números — CNJ](https://www.cnj.jus.br/pesquisas-judiciarias/justica-em-numeros/base-de-dados/)
