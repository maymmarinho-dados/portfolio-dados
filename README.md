# Portfólio de Dados

![Banner do portfólio de dados](assets/banner-portfolio-dados.png)

Bem-vinda ao meu portfólio de projetos práticos de análise de dados, SQL e engenharia analítica com fontes públicas. Cada projeto documenta o problema de negócio, as fontes, a lógica analítica, as validações e as limitações. Os resultados observados são incluídos após a execução e revisão das consultas.

> **Em desenvolvimento:** o projeto Justiça em Números já inclui um pacote de dados e medidas para Power BI, com prévia estática e testes de consistência reproduzíveis. O relatório interativo ainda precisa ser montado no Power BI Desktop; a validação SQL no BigQuery também está pendente.

## Projetos

### Justiça em Números — indicadores do Poder Judiciário

Análise dos indicadores do CNJ por tribunal e ano, com consultas BigQuery e pacote importável para Power BI sobre fluxo processual. Inclui preparação de dados, medidas DAX e verificações de qualidade.

- **Tecnologias:** SQL, Google BigQuery, Power BI, DAX, Power Query, Python e dados públicos do CNJ/Base dos Dados.
- **Foco analítico:** evolução temporal, comparabilidade e qualidade dos dados.
- **Status:** CSV CNJ preparado e validado contra linhas detalhadas; prévia do dashboard disponível. O `.pbix` e a validação na tabela corrente do BigQuery ainda estão pendentes.
- **Comece por:** [README do projeto](projetos/justica-em-numeros-cnj/README.md) · [pacote Power BI](projetos/justica-em-numeros-cnj/power-bi/README.md) · [prévia do dashboard](projetos/justica-em-numeros-cnj/power-bi/dashboard_preview.png) · [guia das consultas SQL](projetos/justica-em-numeros-cnj/sql/README.md) · [catálogo dos indicadores](projetos/justica-em-numeros-cnj/docs/catalogo-indicadores.md).

## Tecnologias e temas

**SQL** · **Google BigQuery** · **Power BI** · **DAX** · **Power Query** · **Python** · **dados públicos** · **análise exploratória**

## Contato

[LinkedIn](https://www.linkedin.com/in/mayara-duarte-a7492318a/)

## Sobre este portfólio

Este repositório reúne estudos reproduzíveis. Cada análise deve distinguir fatos observados de hipóteses, identificar a origem dos dados e explicar as limitações que afetam a interpretação. O objetivo é mostrar não apenas consultas SQL, mas também raciocínio analítico, documentação e comunicação de resultados.
