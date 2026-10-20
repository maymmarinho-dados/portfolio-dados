# Roteiro de apresentação — Dashboard Justiça em Números no Looker Studio

> **Status:** roteiro-modelo. O dashboard e os resultados devem ser preenchidos após executar as consultas e validar os números. Substitua todos os campos entre colchetes antes de gravar ou publicar. Não apresente placeholders como achados.

## Objetivo e duração

Roteiro falado de aproximadamente **4 a 5 minutos** para demonstrar um dashboard de análise exploratória dos indicadores agregados do Justiça em Números, do CNJ. A sequência acompanha a leitura recomendada: contexto e definição, evolução temporal, comparação sob recorte equivalente e qualidade/cobertura.

## Preparação antes da gravação

- Escolha **um único código de indicador** e confirme sua descrição, unidade, fórmula, recorte e polaridade no catálogo e na documentação oficial do CNJ.
- Execute e valide as consultas SQL do projeto. Registre a data de extração e confira `status_qualidade`; não use linhas conflitantes ou sem valor numérico para sustentar conclusões.
- No Looker Studio, configure filtros coerentes com os campos disponíveis: `ano`, `ramo_justica`, `sigla_tribunal` e, se o relatório não for específico a um único indicador, `sigla_indicador`.
- Mostre a unidade em títulos ou subtítulos. Não misture indicadores de unidades diferentes na mesma escala.
- Substitua os trechos entre colchetes pelas informações realmente observadas. Se ainda não houver dashboard executado, use este documento somente como plano de apresentação.

## Roteiro falado

### 1. Abertura e pergunta de negócio — 30 a 45 segundos

**Na tela:** página inicial do relatório, título do indicador, descrição curta, unidade e filtros selecionados.

**Fala:**

“Olá! Neste projeto analiso dados públicos do **Justiça em Números, do Conselho Nacional de Justiça**, usando SQL, Google BigQuery, a Base dos Dados e Looker Studio. A pergunta que orienta o dashboard é: **[pergunta analítica específica]**. Para manter a comparação consistente, esta visualização acompanha o indicador **[sigla — nome por extenso]**, medido em **[unidade confirmada]**, no recorte de **[ramo/escopo confirmado]**, entre **[ano inicial] e [ano final]**.”

### 2. Como ler os filtros — 30 a 40 segundos

**Na tela:** demonstre os controles de ano, ramo e tribunal; mostre o indicador fixo ou seu filtro, conforme o desenho do relatório.

**Fala:**

“Os filtros permitem explorar os dados sem perder o contexto. Primeiro seleciono o período; depois, quando aplicável, o ramo da Justiça e o tribunal. O indicador está **[fixo neste relatório / selecionável neste controle]**. Ao fazer uma comparação, mantenho o mesmo indicador, o mesmo ano e um recorte comparável. Isso evita colocar medidas distintas na mesma análise.”

### 3. Evolução temporal — 45 a 60 segundos

**Na tela:** gráfico de linhas com `ano` no eixo horizontal e `valor_indicador` no vertical. Mostre a unidade no título/eixo e selecione um tribunal ou poucos tribunais para facilitar a leitura.

**Fala:**

“Neste gráfico de linhas, cada ponto representa o valor anual do indicador para **[tribunal ou seleção exibida]**. Observando o período, vemos **[descrever apenas a mudança comprovada: estabilidade, aumento, queda ou oscilação]**. A variação percentual só é interpretada quando há observação no ano imediatamente anterior e o denominador não é zero. Uma lacuna na série significa ausência de observação disponível para aquele recorte; não significa valor igual a zero.”

### 4. Comparação entre tribunais — 45 a 60 segundos

**Na tela:** barras horizontais para um ano e ramo selecionados, ordenadas por valor. Limite a quantidade exibida se houver muitos tribunais e informe que a ordenação é decrescente.

**Fala:**

“Esta comparação mostra **[ano]** e **[ramo da Justiça]** para o mesmo indicador. As barras estão ordenadas do maior para o menor valor, e o painel permite identificar **[descrição objetiva do padrão efetivamente visível]**. Essa ordem é um ranking descritivo do valor, não uma classificação automática de desempenho. Para dizer se um valor maior é desejável, é necessário considerar a polaridade e a metodologia oficial do indicador.”

### 5. Qualidade e cobertura — 40 a 55 segundos

**Na tela:** tabela com `status_qualidade`, `quantidade_registros` e `quantidade_valores_distintos`; acrescente cobertura por ano ou cartão de quantidade de anos observados, se disponível.

**Fala:**

“Além dos valores, o relatório expõe a qualidade e a cobertura. A tabela destaca **[resumo real de linhas válidas, alertas ou ausências]**. Registros com conflito, conversão inválida ou ausência não são tratados automaticamente como zero. Antes de publicar uma conclusão, verifico esses alertas e consulto a definição oficial. **[Se nenhum alerta foi observado após execução, informe o resultado e a data da checagem; caso contrário, descreva o que precisa ser investigado.]**”

### 6. Conclusão e próximos passos — 30 a 45 segundos

**Na tela:** visão geral do dashboard e links para o repositório, SQL e documentação.

**Fala:**

“Em resumo, esta análise responde **[resposta concisa sustentada pelos dados]**, dentro do recorte **[período, indicador e população/unidade analisada]**. A principal limitação é **[limitação verificada: cobertura, comparabilidade, definição, qualidade ou outra]**. O projeto também publica as consultas SQL, o dicionário e as regras de tratamento para que a análise seja reproduzível. O código e a documentação estão em **[link do projeto no GitHub]**. Obrigada!”

## Sugestão de composição no Looker Studio

1. **Cabeçalho:** título do projeto, nome e unidade do indicador, fonte e data da extração.
2. **Filtros:** ano, ramo da Justiça e tribunal; indicador fixo ou selecionável, evitando misturar escalas.
3. **Visão geral:** cartões para período selecionado, número de tribunais com observações e variação anual — somente se os cálculos e o contexto estiverem validados.
4. **Série temporal:** linha por ano, usando poucos tribunais simultaneamente ou pequenos múltiplos.
5. **Comparativo:** barras horizontais para o mesmo ano, ramo e indicador, em ordem explicitamente descrita.
6. **Qualidade e cobertura:** tabela de alertas e visualização dos anos disponíveis. Mantenha valores ausentes distintos de zero.
7. **Rodapé metodológico:** fonte, definição do indicador, filtros aplicados, data de atualização e limitações.

## Campos que precisam ser preenchidos antes de apresentar

| Campo | Preencher com |
|---|---|
| Indicador | Sigla e nome conforme o dicionário CNJ/Base dos Dados |
| Unidade | Unidade/metodologia confirmada para a sigla exata |
| Recorte | Ramo, grau/fase codificados ou outro escopo confirmado |
| Período | Anos efetivamente retornados após executar a consulta |
| Achado da série | Padrão medido, sem inferir causalidade |
| Achado comparativo | Comparação sob o mesmo ano, ramo e indicador |
| Qualidade | Resultado observado nos testes e status de qualidade |
| Limitações | Cobertura, comparabilidade e ressalvas realmente identificadas |
| Data da extração | Data em que a consulta foi executada |
| Links | Dashboard publicado e repositório do projeto |

## Cuidados para a publicação no portfólio

- Não grave números fictícios nem mantenha os campos `[entre colchetes]` na versão publicada.
- Diferencie o que a consulta mediu de hipóteses sobre as causas das variações; o dashboard, por si só, não demonstra causalidade.
- Não chame o tribunal com maior/menor valor de “melhor” ou “pior” sem metodologia que sustente essa avaliação.
- Não compare indicadores com unidades, fórmulas ou recortes diferentes.
- Inclua uma captura legível do dashboard no README depois de construí-lo e valide os filtros e totais exibidos.

## Referências do projeto

- [Projeto Justiça em Números — CNJ](../README.md)
- [Guia das consultas SQL](../sql/README.md)
- [Catálogo e regras de tratamento dos indicadores](catalogo-indicadores.md)
- [Dicionário de dados](dicionario-de-dados.md)
