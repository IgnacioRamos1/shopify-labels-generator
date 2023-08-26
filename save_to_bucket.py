import boto3
from datetime import datetime


def save_to_s3(bucket_name, content, item_name):
    # Convert the bucket name to a valid S3 bucket name
    bucket_name = bucket_name.lower().replace(" ", "-")
    
    # Inicializar el cliente de S3
    s3 = boto3.client('s3', region_name='sa-east-1')

    # Verificar si el bucket existe
    try:
        s3.head_bucket(Bucket=bucket_name)
    except:
        # Si el bucket no existe, lo creamos especificando la ubicación
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'sa-east-1'})

    # Definir el nombre del archivo basado en la fecha y nombre del producto
    date_str = datetime.now().strftime('%Y-%m-%d')
    file_name = f"{bucket_name} - {date_str} - {item_name}.csv"

    # Subir el contenido al bucket
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=content)

    return f"File saved to {bucket_name}/{file_name}"
