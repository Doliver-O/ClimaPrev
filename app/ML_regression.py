import boto3
import pandas as pd
import io
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib



def get_latest_file_key(bucket_name, prefix, s3):
    """
    Busca o arquivo mais recente no bucket com prefixo definido.
    """
    s3 = s3
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if 'Contents' not in response:
        raise ValueError(f"Nenhum arquivo encontrado em s3://{bucket_name}/{prefix}")
    
    # Ordena por última modificação, descrescente (mais recente primeiro)
    arquivos = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
    return arquivos[0]['Key']

def carregar_dados_s3(bucket, file_key, s3):
    """
    Baixa e carrega CSV do S3 direto no Pandas DataFrame
    """
    s3 = s3
    obj = s3.get_object(Bucket=bucket, Key=file_key)
    return pd.read_csv(io.BytesIO(obj['Body'].read()))

def salvar_modelo_s3(model, bucket, model_key, s3):
    """
    Salva objeto joblib no S3
    """
    buffer = io.BytesIO()
    joblib.dump(model, buffer)
    buffer.seek(0)
    s3 = s3
    s3.put_object(Bucket=bucket, Key=model_key, Body=buffer.getvalue())
    print(f"Modelo salvo em s3://{bucket}/{model_key}")

def regression():
    # Configurações AWS
    AWS_ACCESS_KEY = 'AKIAUJH6C5GGCB35HOHY'
    AWS_SECRET_KEY = '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'
    AWS_REGION = 'sa-east-1'  # Região São Paulo
    BUCKET_NAME = 'climaprev'

    # Conexão com S3
    s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
    )

    # Variáveis - ajuste seu bucket e prefixo dos dados
    bucket = 'climaprev'
    prefix_arquivo = 'dataset-final/'

    print("Buscando arquivo mais recente no S3...")
    file_key = get_latest_file_key(bucket, prefix_arquivo, s3)
    print(f"Arquivo encontrado: {file_key}")

    print("Carregando dados...")
    df = carregar_dados_s3(bucket, file_key, s3)

    # Defina suas features e target - ajuste conforme seu dataset
    X = df['temperature_2m', 'relative_humidity_2m', 'surface_pressure', 'pressure_msl']  # Exemplo
    y = df['precipitation']  # Exemplo

    print("Dividindo dados treino e teste...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Treinando modelo RandomForestRegressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    print("Avaliação do modelo...")
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"MSE: {mse}")

    print("Salvando modelo treinado no S3...")
    salvar_modelo_s3(model, bucket, 'modelos/modelo_precipitacao.joblib', s3)

if __name__ == "__main__":
    regression()
