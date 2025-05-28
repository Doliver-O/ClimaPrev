# Previsão de Precipitação em Tempo Real

## Descrição do Projeto

Este projeto consiste em uma aplicação web que coleta dados meteorológicos de uma API externa, processa esses dados e utiliza um modelo de aprendizado de máquina para prever a precipitação do dia seguinte, hora a hora.

## Tecnologias Utilizadas

- **Flask**: Para criar a aplicação web e a API.
- **joblib**: Para salvar e carregar o modelo de Machine Learning.
- **Pandas**: Para manipulação de dados.
- **Plotly**: Para visualização dos dados em gráficos.
- **AWS**:
  - **S3**: Para armazenamento de dados.
  - **Lambda**: Para processamento de dados.
- **API-Meteo**: Fonte de dados meteorológicos.

## Funcionalidades

- Selecionar uma cidade de uma lista de opções.
- Coletar dados meteorológicos para os últimos 55 dias.
- Processar e tratar os dados para treinamento do modelo.
- Fazer previsões de precipitação para o dia seguinte.
- Exibir os resultados em um gráfico interativo.

## API

Esta aplicação web expõe uma API que permite interagir com os dados meteorológicos e fazer previsões de precipitação. A seguir estão os endpoints disponíveis.

### Endpoints

#### 1. Coletar Dados Meteorológicos

- **URL**: `/coletar`
- **Método**: `POST`
- **Descrição**: Coleta dados meteorológicos de uma cidade específica a partir da API Open-Meteo e salva os dados em um bucket S3 da AWS.

- **Parâmetros de Entrada** (no corpo da requisição):
  - `cidade` (string): Nome da cidade para a qual os dados meteorológicos devem ser coletados. Deve ser uma das seguintes opções:
    - `"sao-paulo"`
    - `"rio-de-janeiro"`
    - `"brasilia"`
    - `"salvador"`
    - `"fortaleza"`
    - `"nova-york"`
    - `"londres"`
    - `"toquio"`
    - `"paris"`
    - `"sydney"`

- **Exemplo de Corpo da Requisição**:
    ```json
    {
      "cidade": "sao-paulo"
    }
    ```

- **Resposta**:
  - **Sucesso**: 
    ```json
    {
      "message": "Dados coletados e salvos para sao-paulo com sucesso!",
      "linhas": 100
    }
    ```
  - **Erro**:
    ```json
    {
      "error": "Cidade não encontrada"
    }
    ```

#### 2. Listar Arquivos no S3

- **URL**: `/listar-arquivos`
- **Método**: `GET`
- **Descrição**: Lista todos os arquivos armazenados em diferentes diretórios no bucket S3.

- **Resposta**:
```json
{
    "arquivos": ["dados_coletados/meteorologia-2022.csv", ...],
    "arquivos2": ["dataset-final/dataset1.csv", ...],
    "arquivos3": ["modelos/modelo_precipitacao.joblib", ...]
}

#### 3. Ler Arquivo

- **URL**: `/ler-arquivo/<arquivo>`
- **Método**: `GET`
- **Descrição**: Lê um arquivo específico armazenado no S3 e retorna seus dados em formato JSON.

- **Parâmetros de URL**:
  - `arquivo` (string): Nome do arquivo a ser lido do bucket S3.

- **Resposta**:
```json
[
    {"date": "2025-06-09T06:00", "temperature_2m": 20, ...},
    ...
]

#### 4. Fazer Previsão de Chuva

- **URL**: `/predict`
- **Método**: `GET`
- **Descrição**: Faz a previsão de precipitação para o dia seguinte, baseando-se nos dados coletados e salvos.

- **Resposta**: O usuário é redirecionado para uma página que contém um gráfico da previsão de chuva.
  
- **Gráfico**: As previsões são apresentadas visualmente em um gráfico interativo.

## Fluxo do Projeto

O fluxo do projeto pode ser dividido nas seguintes etapas principais:

1. **Entrada do Usuário**:
   - O usuário acessa a aplicação web.
   - O usuário escolhe uma cidade de uma lista de opções disponíveis.

2. **Coleta de Dados Meteorológicos**:
   - Após a seleção da cidade, a aplicação aciona a **API Open-Meteo** para coletar dados:
     - Dados históricos dos últimos 55 dias.
     - Previsões para os próximos dias.
   - Os dados obtidos são armazenados em um arquivo CSV.

3. **Armazenamento em S3**:
   - O arquivo CSV que contém os dados coletados é salvo em um bucket **AWS S3**.

4. **Processamento de Dados**:
   - Um **AWS Lambda** é acionado para processar o arquivo CSV, transformando os dados em um formato adequado para o treinamento do modelo de Machine Learning.

5. **Treinamento do Modelo**:
   - O modelo de Machine Learning é treinado utilizando os dados tratados.
   - O modelo treinado é salvo em formato **Joblib** para uso futuro.

6. **Previsão de Precipitação**:
   - Quando o usuário solicita a previsão:
     - A aplicação carrega o modelo treinado.
     - Os dados recentes coletados são usados como entrada para o modelo.
     - O modelo gera previsões de precipitação para o dia seguinte, hora a hora.

7. **Exibição de Resultados**:
   - O resultado da previsão (precipitação) é plotado em um gráfico interativo utilizando **Plotly**.
   - O gráfico é apresentado ao usuário na interface da aplicação web.

8. **Interação Adicional**:
   - O usuário pode solicitar previsões para outras cidades, repetindo o processo.

### Diagrama Esquemático


[Usuário] 
    ↓
[Escolha da Cidade]
    ↓
[Coleta de Dados (API Open-Meteo)]
    ↓
[Armazenamento em S3]
    ↓
[AWS Lambda (Processamento de Dados)]
    ↓
[Modelo de Machine Learning Treinado]
    ↓
[Previsão de Precipitação]
    ↓
[Exibição de Gráfico](Resultados)
