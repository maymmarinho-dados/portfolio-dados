# Catálogo de indicadores — Justiça em Números

O arquivo [`indicadores_disponiveis_2026-06.csv`](indicadores_disponiveis_2026-06.csv) contém **1.305 códigos de indicadores** e suas descrições conforme `Variaveis.csv`, distribuído pelo CNJ no [pacote de dados de 23 de junho de 2026](https://www.cnj.jus.br/wp-content/uploads/2026/06/23-jun-2026.zip). A lista foi obtida das colunas métricas do arquivo original, excluindo as dimensões de ano/tribunal/Justiça e os atributos cadastrais do tribunal. O [código oficial de tratamento da Base dos Dados](https://github.com/basedosdados/pipelines/blob/main/models/br_cnj_datajud/code/clean.py) confirma esse processo de extração.

Esse catálogo é uma lista de códigos e descrições, **não** uma lista de 1.305 KPIs já calculados nem de 1.305 linhas da tabela. Cada linha da tabela `tribunal_ano` representa um valor para ano, tribunal, ramo da Justiça e código de indicador. Muitos códigos têm recortes codificados no próprio sufixo, como grau ou fase processual, conforme o [schema oficial](https://github.com/basedosdados/pipelines/blob/main/models/br_cnj_datajud/schema.yml). A descrição do catálogo não substitui a consulta à metodologia oficial para obter fórmula, unidade, denominador e interpretação.

## Famílias e exemplos

Alguns exemplos encontrados no arquivo oficial:

- **Fluxo processual:** `cn1` — casos novos no 1º grau; `cp` — casos pendentes; `tbaix` — total de processos baixados.
- **Congestionamento:** `tc` — taxa de congestionamento; há códigos específicos por grau, fase ou ramo/recorte.
- **Atendimento à demanda:** `iad` — processos baixados por caso novo; existem variantes como `iad1`, `iad2` e `iadje`.
- **Produtividade:** `ipm` — índice de produtividade dos magistrados; `ips` — índice de produtividade dos servidores.
- **Eficiência comparada:** `eff` — IPC-Jus, com códigos próprios para recortes, como `eff1` e `eff2`.
- **Outros temas:** despesas e assistência judiciária, composição/atividade processual por classe, execução, recursos, duração e recortes institucionais.

Os exemplos acima são somente uma amostra. Consulte o CSV para as 1.305 linhas e o dicionário no BigQuery para a versão corrente.

## Consultar a lista completa no BigQuery

A tabela auxiliar `basedosdados.br_cnj_datajud.dicionario` associa códigos e rótulos. Para os códigos de indicadores de `tribunal_ano`, filtre `id_tabela = 'tribunal_ano'` e `nome_coluna = 'sigla_indicador'`. A implementação oficial gera esses registros a partir do arquivo `Variaveis.csv` do CNJ.

```sql
SELECT
  chave AS sigla_indicador,
  valor AS descricao_cnj,
  NULLIF(TRIM(cobertura_temporal), '') AS cobertura_temporal
FROM `basedosdados.br_cnj_datajud.dicionario`
WHERE id_tabela = 'tribunal_ano'
  AND nome_coluna = 'sigla_indicador'
ORDER BY chave;
```

Para conferir códigos com observações materializadas, use a consulta **B** de [`03_catalogo_indicadores.sql`](../sql/03_catalogo_indicadores.sql). Ela faz `LEFT JOIN` do catálogo para os fatos e informa anos, tribunais e ramos observados. Códigos com zero observações não devem ser tratados como medição igual a zero.

## Regras de tratamento SQL

### 1. Mantenha o código do indicador junto com a descrição

Não elimine `sigla_indicador` depois de trazer `descricao_cnj`. O código identifica a métrica e possibilita filtros e validações. Use o dicionário para exibir descrições legíveis, sem presumir que códigos semelhantes sejam a mesma medida.

### 2. Respeite a chave e o recorte

A chave documentada da tabela é `ano + sigla_tribunal + ramo_justica + sigla_indicador`. Preserve `ramo_justica` em `GROUP BY`, `JOIN` e funções de janela. O CNJ reporta alguns tribunais sob mais de um ramo, com valores distintos. Grau e fase processual aparecem codificados nos sufixos de `sigla_indicador`, não em colunas próprias da tabela. [1]

### 3. Não some ou compare métricas diferentes sem metodologia

O campo `valor` é numérico (`FLOAT64`), mas a unidade varia: há contagens, taxas, índices e métricas com denominadores diferentes. Filtre um código por vez para análises temporais ou compare somente recortes equivalentes. Não some as 1.305 métricas nem faça rankings misturando códigos.

### 4. Preserve valores e trate ausência como ausência

A Base dos Dados transforma o campo numérico e descarta as linhas em que a fonte apresenta sentinelas como `nd`, `n/a` e `Inf`. Portanto, a ausência de uma linha não pode ser interpretada automaticamente como zero. Não converta nulos em zero nem remova outliers antes de verificar a definição do indicador. [O pipeline público](https://github.com/basedosdados/pipelines/blob/main/models/br_cnj_datajud/code/clean.py) descreve e implementa esse tratamento.

### 5. Use o dicionário como rótulo, não como fórmula completa

A descrição `valor` do dicionário explica o código; a tabela auxiliar não oferece necessariamente uma coluna separada de fórmula ou unidade. Para interpretar proporções, produtividade e IPC-Jus, consulte a fórmula, a escala e a polaridade no glossário/metodologia CNJ. Preserve o valor original até confirmar se uma taxa está armazenada em proporção ou percentual.

### 6. Evite multiplicação de linhas no JOIN

Filtre o dicionário para uma única tabela e coluna antes do `JOIN`. A Base dos Dados documenta unicidade por tabela, coluna e código. Se seu resultado aumentar de linhas após o `JOIN`, verifique a cardinalidade do dicionário e evite agregar antes de investigar.

## Referências

- [Dataset Justiça em Números (DataJud) — Base dos Dados](https://basedosdados.org/dataset/60de97a5-aae7-4cda-871f-b314b497d768)
- [Pipeline de limpeza do CNJ — Base dos Dados](https://github.com/basedosdados/pipelines/blob/main/models/br_cnj_datajud/code/clean.py)
- [Schema oficial do dataset CNJ — Base dos Dados](https://github.com/basedosdados/pipelines/blob/main/models/br_cnj_datajud/schema.yml)
- [Arquivo oficial mais recente de dados do Justiça em Números — CNJ](https://www.cnj.jus.br/wp-content/uploads/2026/06/23-jun-2026.zip)
- [Glossário dos Indicadores de Desempenho — CNJ, fevereiro de 2026](https://www.cnj.jus.br/wp-content/uploads/2026/02/glossario-indicadores-desempenho-13-02-2026.pdf)
