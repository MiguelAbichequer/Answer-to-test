# QUESTÃO 1

## 1.2 Processamento de Dados: Memória vs. Incremental

Optei pelo processamento em memória, utilizando as funções de leitura da biblioteca *pandas*. Também utilizei a bilioteca *BeautifulSoup* para tornar os dados, que eram carregados como uma estrtura *HTML*, manipuláveis em Python.

 - Para baixar a biblioteca *BeautifulSoup*: `pip install beautifulsoup4`


**Justificativa:** Dada a natureza dos arquivos de demonstrações contábeis trimestrais, o volume de dados filtrado (apenas as contas com prefixo '411') permite o carregamento em memória sem comprometer a estabilidade do sistema. Entretanto, a escalabilidade da solução é limitada.

## 1.3 Identificação de Dados de Sinistros

Filtragem baseada no código da conta contábil (`CD_CONTA_CONTABIL`) iniciando com **'411'**, facilitada pela biblioteca *pandas*.

**Justificativa:** Em vez de depender apenas da descrição textual (que pode variar entre trimestres), o código contábil oferece uma forma mais resiliente para identificar "Despesas com Eventos/Sinistros". 

**Resiliência**: O código lida com variações de extensão (`.csv`, `.txt`, `.xlsx`) para garantir que dados de diferentes trimestres sejam capturados independentemente do formato do arquivo em que estão salvos.

# QUESTÃO 2

## 2.1 Tratamento de Inconsistências (Análise Crítica)

 **Valores Negativos ou Zerados:** Decidi **eliminar** registros com `ValorDespesas <= 0`.

**Justificativa:** Para fins de análise estatística esses valores são dispensáveis, uma vez que correspondem a ruídos no contexto de valores contábeis ou a estornos que distorceriam o somatório final.

**Tratamento da coluna CNPJ:** Com a biblioteca *validate_docbr*, é possível validar automaticamente a coluna que contém os CNPJs. Também eliminei aqueles que preenchidos somente por zero e que não possuem exatamente quatorze dígitos.

 - Para baixar *validate_docbr*: `pip  install  validate-docbr`

## 2.2 Enriquecimento de dados com tratamento de falhas

Utilizei o método com  **`merge()`**  da biblioteca *pandas* com os parâmetros **Left Join** entre a base de despesas e o cadastro de operadoras.

**Justificativa:** Esta estratégia prioriza os dados financeiros.

## 2.3. Agregação com Múltiplas Estratégias

**Decisão:** Ordenação descendente por valor total após a agregação.

**Justificativa:** Escolhi realizar a ordenação em memória no DataFrame final, para economizar operações anteriores, utilizei `dataFrame_agrupado.sort_values(by='Total_Despesas', ascending=False)` 
para ordenar de maneira descendente os dados processados.

# QUESTÃO 3

Por ter um conhecimento menor dessa tecnologia, consegui apenas realizar a criação e importação das tabelas *.csv* geradas nas questões anteriores.

## 3.2 Crie queries DDL para estruturar as tabelas.

**Escolha:** **Opção B: Tabelas Normalizadas Separadas** Optei por separar os dados em duas tabelas distintas: `operadoras_cadastrais` (Dimensão) e `despesas_consolidadas` (Fatos), ligadas por uma chave (`cnpj`).

### Escolha de tipos de dados:

 - Valores Monetários (`valor_despesa`): escolhi o tipo `DECIMAL`. Para valores monetários, o tipo `FLOAT` poderia causar problemas de arredondamento e o tipo `INT` abarca um conjunto numérico menor do que o necessário.
 - Datas (`ano`, `trimestre`): escolhi o tipo `INT`, uma vez que dias e trimestes são valores discretos.
