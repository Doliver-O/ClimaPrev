from flask import Flask, jsonify
import pandas as pd
import boto3
from datetime import datetime
import io
from flask import Blueprint, render_template, jsonify,request,send_file, Flask
import joblib
import numpy as np
from .ML_regression import regression, get_latest_file_key, carregar_dados_s3
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import plotly.express as px
import plotly.io as pio
import requests
import openmeteo_requests
import requests_cache
from retry_requests import retry

main = Blueprint('main', __name__)

load_dotenv()

# Configurações AWS

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_REGION = 'sa-east-1'  # Região São Paulo
BUCKET_NAME = 'climaprev'

# Conexão com S3
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)




# Função para coletar dados (exemplo com open-meteo)
def coletar_dados(latitude, longitude, cidade):


    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m", "relative_humidity_2m", "precipitation_probability",
            "precipitation", "rain", "visibility", "surface_pressure", "pressure_msl"
        ],
        "timezone": "auto",
        "paste_days": 55,
        "forecast_days": 7 
    }

    # Chamando a API com `verify=False` para contornar problemas de SSL
    #response = requests.get(url, params=params, verify=False)

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    hourly = response.Hourly()
    data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
        "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
        "precipitation_probability": hourly.Variables(2).ValuesAsNumpy(),
        "precipitation": hourly.Variables(3).ValuesAsNumpy(),
        "rain": hourly.Variables(4).ValuesAsNumpy(),
        "visibility": hourly.Variables(5).ValuesAsNumpy()
    }

    df = pd.DataFrame(data)
    return df


# Função para salvar no S3
def salvar_s3(df, nome_arquivo):
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=nome_arquivo,
        Body=buffer.getvalue()
    )


@main.route('/')
def index():
    return render_template('index.html', title='Página Inicial')

@main.route('/dados_meteorologia')
#@login_required
def dados_meteo():
    return render_template('dados_meteorologia.html', title='Dados Meteorologicos')

#Endpoints ligadoss em salvar os dados no S3 AWS

coordenadas = {
    "sao-paulo": {"latitude": -23.5505, "longitude": -46.6333},
    "rio-de-janeiro": {"latitude": -22.9068, "longitude": -43.1729},
    "brasilia": {"latitude": -15.8267, "longitude": -47.9218},
    "salvador": {"latitude": -12.9777, "longitude": -38.5016},
    "fortaleza": {"latitude": -3.7172, "longitude": -38.5433},
    "nova-york": {"latitude": 40.7128, "longitude": -74.0060},
    "londres": {"latitude": 51.5074, "longitude": -0.1278},
    "toquio": {"latitude": 35.6895, "longitude": 139.6917},
    "paris": {"latitude": 48.8566, "longitude": 2.3522},
    "sydney": {"latitude": -33.8688, "longitude": 151.2093}
}

@main.route('/coletar', methods=['POST'])
def coletar():
    cidade = request.json.get('cidade')

    if cidade not in coordenadas:
        return jsonify({'error': 'Cidade não encontrada'}), 400

    lat = coordenadas[cidade]['latitude']
    lon = coordenadas[cidade]['longitude']

    data_atual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    nome_arquivo = f'dados_coletados/meteorologia_{data_atual}_{cidade}.csv'

  

    df = coletar_dados(lat, lon, cidade)
    salvar_s3(df, nome_arquivo)

    regression()
    predict()
    
    return jsonify({'message': f'Dados coletados e salvos para {cidade} com sucesso!', 'linhas': len(df)})

@main.route('/listar-arquivos')
def listar_arquivos():
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix='dados_coletados/')
    arquivos = [item['Key'] for item in response.get('Contents', [])]

    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix='dataset-final/')
    arquivos2 = [item['Key'] for item in response.get('Contents', [])]

    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix='modelos/')
    arquivos3 = [item['Key'] for item in response.get('Contents', [])]
    return jsonify(arquivos,arquivos2,arquivos3)


@main.route('/ler-arquivo/<arquivo>')
def ler_arquivo(arquivo):
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=f'dados_coletados/{arquivo}')
    df = pd.read_csv(obj['Body'])
    return df.to_json(orient='records')

BUCKET = 'climaprev'
MODEL_KEY = 'modelos/modelo_precipitacao.joblib'

def carregar_modelo():
    obj = s3.get_object(Bucket=BUCKET, Key=MODEL_KEY)
    bytes_modelo = obj['Body'].read()
    modelo = joblib.load(io.BytesIO(bytes_modelo))
    return modelo



#modelo = joblib.load('modelo_precipitacao.joblib')


'''
@main.route('/predict', methods=['POST'])
def predict():
    # Obter os dados do formulário
    dados = request.form.to_dict()
    # Converter para DataFrame
    #features = modelo.feature_names_in_
    #print(features)
    df_input = pd.DataFrame(dados, index=[0])
    
    
    # Fazer a previsão
    pred = modelo.predict(df_input)
    print(dados)


    # Aqui você poderá criar gráficos ou métricas a partir da predição
    grafico = criar_grafico(df_input, pred)
    
    return render_template('dados_meteorologia.html', pred=pred, grafico=grafico)
'''




def fazer_previsao():
    key_s3 = get_latest_file_key(BUCKET,'dataset-final',s3)
    obj = s3.get_object(Bucket=BUCKET, Key=key_s3)
    # Carregar os dados do CSV direto ao pandas
    df = pd.read_csv(io.BytesIO(obj['Body'].read()), parse_dates=['date'])
    
    # Obter a data de amanhã
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')

    # Filtrar os dados para o dia de amanhã
    df_tomorrow = df[df['date'].dt.date == tomorrow.date()]

    # Selecionar as features
    features = df_tomorrow[['temperature_2m', 'relative_humidity_2m', 'precipitation_probability', 'rain']]
    cidade = df_tomorrow['cidade'].iloc[0].replace("-"," ").upper().replace(".CSV","")
    print(cidade)
    
    modelo = carregar_modelo()
    # Fazer a previsão
    previsoes = modelo.predict(features)

    # Adicionar as previsões ao DataFrame
    df_tomorrow['previsão_chuva'] = previsoes

    return df_tomorrow, cidade

@main.route('/predict')
def predict():
        # Fazer previsões e obter o DataFrame
    df_previsao = fazer_previsao()
    print(type(df_previsao[0]))
    df_previsao2 = df_previsao[0]
    cidade = df_previsao[1]

    # Plotar as previsões
    fig = px.line(df_previsao2, x='date', y='previsão_chuva', title='Previsão de Chuva para Amanhã')
    fig.update_layout(
    xaxis_title='Horas',
    yaxis_title='Precipitação (mm)')

    #fig.update_xaxes(tickmode='linear', dtick='24')

    grafico = pio.to_html(fig, full_html=False)

    return render_template('dados_meteorologia.html', grafico=grafico, cidade=cidade)


