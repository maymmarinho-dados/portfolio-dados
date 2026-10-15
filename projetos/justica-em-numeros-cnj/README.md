# Justiça em Números — indicadores do Poder Judiciário

**Análise exploratória em SQL dos indicadores publicados pelo Conselho Nacional de Justiça (CNJ), com acesso pela Base dos Dados e execução no Google BigQuery.**

> **Status: em validação.** O esquema e as siglas de indicadores precisam ser confirmados no BigQuery antes de usar resultados numéricos como conclusões. Este repositório não apresenta insights quantitativos ainda não executados.

## Pergunta de negócio

Como os indicadores do Justiça em Números variam entre tribunais ao longo do tempo, e quais cuidados são necessários para comparar essas métricas corretamente?

A análise foi planejada para responder:

1. Como um indicador selecionado evolui por tribunal em anos consecutivos?
2. Quais tribunais têm maiores ou menores valores do mesmo indicador e ano?
3. Onde há lacunas temporais, valores não numéricos ou possíveis conflitos de granularidade?
4. A comparação permanece válida após consultar unidade, fórmula, recorte e polaridade oficiais?

## Fonte e escopo

- **Base:** [Justiça em Números (DataJud) — Base dos Dados](https://basedosdados.org/dataset/60de97a5-aae7-4cda-871f-b314b497d768).
- **Tabela de trabalho:** `basedosdados.br_cnj_datajud.tribunal_ano`.
- **Fonte institucional:** [Conselho Nacional de Justiça](https://www.cnj.jus.br/pesquisas-judiciarias/justica-em-numeros/).
- **Cobertura descrita no catálogo:** Brasil, 2009–2025.
- **Granularidade considerada inicialmente:** ano + tribunal + indicador. Ela deve ser ajustada se o esquema mostrar dimensões adicionais.

## O que este projeto entrega

- Consultas BigQuery Standard SQL para descoberta do esquema, perfil das siglas e análise exploratória da série.
- [Dicionário de dados](docs/dicionario-de-dados.md), com definições conceituais, unidades/polaridades a mapear e validações necessárias.
- [Guia das consultas](sql/README.md), com entradas, etapas, campos entregues e limites de interpretação.

## Estrutura

```text
justica-em-numeros-cnj/
├── README.md
├── docs/
│   └── dicionario-de-dados.md
└── sql/
    ├── README.md
    ├── 00_inspecao_esquema.sql
    ├── 01_perfil_indicadores.sql
    └── 02_evolucao_ranking.sql
```

## Como reproduzir

1. No BigQuery, fixe o projeto público `basedosdados` e abra `br_cnj_datajud.tribunal_ano`.
2. Rode [`00_inspecao_esquema.sql`](sql/00_inspecao_esquema.sql). Confirme nomes, tipos e dimensões.
3. Se os campos esperados existirem ou forem ajustados, rode [`01_perfil_indicadores.sql`](sql/01_perfil_indicadores.sql) para identificar siglas e cobertura.
4. Consulte os dicionários auxiliares do dataset e do CNJ para obter a descrição, fórmula, unidade, escopo e polaridade de cada indicador escolhido.
5. Atualize a chave analítica se houver outras dimensões. Depois execute [`02_evolucao_ranking.sql`](sql/02_evolucao_ranking.sql) para o indicador validado.
6. Registre a data de extração e documente os resultados, as limitações e a unidade de cada número antes de publicar.

Detalhes de cada script: [guia das consultas SQL](sql/README.md).

## Decisões de análise

- Cada comparação deve ocorrer dentro do **mesmo indicador**, período e recorte comparável.
- A variação percentual é calculada apenas quando existe observação no ano imediatamente anterior e o denominador não é zero.
- Valores múltiplos na chave proposta devem ser investigados; podem refletir recortes omitidos, não erros da fonte.
- O ranking é descritivo e ordena o maior valor primeiro. Não significa automaticamente melhor ou pior desempenho.
- Nulos não são tratados como zero.
- A polaridade depende do indicador. Por exemplo, o CNJ descreve o Índice de Atendimento à Demanda como “quanto maior, melhor”, enquanto algumas taxas de congestionamento têm interpretação inversa.

## Resultados

**Ainda não publicados.** Esta seção será preenchida após confirmar o esquema, escolher um indicador com definição oficial, executar a consulta e validar a interpretação. Quando concluída, inclua resultados quantificados e uma visualização, sem extrapolar além do recorte analisado.

## Tecnologias

`SQL` · `Google BigQuery` · `Base dos Dados` · `CNJ`

## Sugestão de publicação no LinkedIn

> Estou desenvolvendo uma análise de dados públicos do **Justiça em Números, do CNJ**, usando SQL no Google BigQuery e a Base dos Dados.
>
> Neste projeto, investiguei **[indicador e período]** por **[recorte comparável]**, com foco em **[pergunta de negócio]**. Antes da análise, validei o esquema, as siglas, a unidade e a granularidade dos dados.
>
> **Resultado observado:** [inclua aqui um achado que tenha sido executado e validado].
>
> Código e documentação: [link para este projeto no GitHub]
>
> #SQL #BigQuery #DadosAbertos #CNJ #Analytics

## Referências

- [Dataset Justiça em Números (DataJud) — Base dos Dados](https://basedosdados.org/dataset/60de97a5-aae7-4cda-871f-b314b497d768)
- [Glossário dos Indicadores de Desempenho — CNJ, fevereiro de 2026](https://www.cnj.jus.br/wp-content/uploads/2026/02/glossario-indicadores-desempenho-13-02-2026.pdf)
- [Base de dados do Justiça em Números — CNJ](https://www.cnj.jus.br/pesquisas-judiciarias/justica-em-numeros/base-de-dados/)
