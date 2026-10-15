# Justiça em Números — análise de indicadores do CNJ

> Projeto de portfólio em SQL para explorar a evolução dos indicadores do Poder Judiciário brasileiro, com foco inicial em comparabilidade temporal, rankings contextualizados e qualidade dos dados.

## Objetivo de negócio

Transformar os indicadores anuais do relatório **Justiça em Números**, do Conselho Nacional de Justiça (CNJ), em uma análise reproduzível que ajude a responder:

1. Como os indicadores selecionados evoluem por tribunal ao longo do tempo?
2. Quais tribunais apresentam valores mais altos ou mais baixos no mesmo indicador e ano?
3. A variação observada é realmente entre anos consecutivos?
4. Existem linhas duplicadas, valores inválidos ou conflitos na granularidade analisada?

## Fonte de dados

- **Plataforma:** [Base dos Dados](https://basedosdados.org/)
- **Tabela consultada:** `basedosdados.br_cnj_datajud.tribunal_ano`
- **Fonte institucional:** [CNJ — Justiça em Números](https://www.cnj.jus.br/pesquisas-judiciarias/justica-em-numeros/)
- **Cobertura descrita pela Base dos Dados:** 2009–2025, Brasil. A descrição do dataset informa indicadores por tribunal e ano, com recortes e tabelas auxiliares disponíveis no conjunto.

## Estrutura

```text
justica-em-numeros-cnj/
├── README.md
├── docs/
│   └── dicionario-de-dados.md
└── sql/
    ├── 00_inspecao_esquema.sql
    ├── 01_perfil_indicadores.sql
    └── 02_evolucao_ranking.sql
```

## Como executar

1. No BigQuery, localize o projeto público `basedosdados` e a tabela `br_cnj_datajud.tribunal_ano`.
2. Execute `sql/00_inspecao_esquema.sql` e confira nomes e tipos físicos das colunas.
3. Execute `sql/01_perfil_indicadores.sql` para conferir cobertura e domínio das siglas.
4. Confira o dicionário de códigos oficial da base para mapear sigla, descrição, unidade, fórmula e polaridade.
5. Execute `sql/02_evolucao_ranking.sql` apenas depois de validar que os campos `ano`, `sigla_tribunal`, `sigla_indicador` e `valor` correspondem ao esquema e que a chave analítica considera todas as dimensões existentes.

## Decisões analíticas

- A comparação é feita **dentro do mesmo indicador**. Valores de indicadores distintos podem usar escalas e unidades incompatíveis.
- A variação anual só é calculada quando há observação no ano imediatamente anterior.
- O script sinaliza conflitos na combinação de campos utilizada. Não escolhe média ou máximo para ocultá-los.
- Um ranking do maior valor para o menor **não implica melhor desempenho**. É preciso considerar a polaridade e a definição oficial do indicador.
- Ausência de dado permanece nula; não é convertida em zero.

## Estado da análise e limitação atual

O SQL encontra-se em fase de **exploração e validação do esquema**. Na sessão de desenvolvimento, o BigQuery apontou `sigla_indicador` como nome válido em sugestão de erro e rejeitou `grau` como coluna da tabela consultada. A lista completa de colunas, seus tipos, as siglas e as unidades ainda deve ser validada no BigQuery antes de apresentar resultados numéricos como conclusões.

A descrição da Base dos Dados menciona recortes por grau e fase e recomenda consultar dicionários/diretórios porque códigos institucionais podem variar. Portanto, múltiplas linhas por tribunal-ano-indicador podem refletir dimensões legítimas, e não necessariamente duplicidade. A chave da análise deve ser atualizada se o esquema revelar dimensões adicionais.

## Próximas melhorias

- Mapear automaticamente as siglas usando a tabela auxiliar de indicadores do dataset.
- Adicionar descrição, unidade, fórmula e polaridade ao resultado por meio de `JOIN` com o dicionário correto.
- Selecionar um indicador de negócio principal e produzir gráfico temporal por ramo/grupo comparável, após validar o cadastro de tribunais.
- Acrescentar testes para unicidade da chave, anos consecutivos, nulos e mudança de códigos institucionais.
- Registrar uma data de extração e a definição oficial do indicador analisado.

## Tecnologias

`SQL` · `Google BigQuery` · `Base dos Dados` · `CNJ`

## Referências

- [Dataset Justiça em Números (DataJud) — Base dos Dados](https://basedosdados.org/dataset/60de97a5-aae7-4cda-871f-b314b497d768)
- [Glossário dos Indicadores de Desempenho — CNJ, versão de fevereiro de 2026](https://www.cnj.jus.br/wp-content/uploads/2026/02/glossario-indicadores-desempenho-13-02-2026.pdf)
- [Base de dados do Justiça em Números — CNJ](https://www.cnj.jus.br/pesquisas-judiciarias/justica-em-numeros/base-de-dados/)
