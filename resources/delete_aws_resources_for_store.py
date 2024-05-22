import boto3
from botocore.exceptions import ClientError

import sys
import os
sys.path.append(os.path.abspath('..'))

dynamodb_client = boto3.client('dynamodb', region_name='sa-east-1')

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')


def table_exists(table_name):
    try:
        response = dynamodb_client.describe_table(TableName=table_name)
        return True  # La tabla existe
    except ClientError as e:
        if e.response['Error']['Code'] == "ResourceNotFoundException":
            return False  # La tabla no existe
        else:
            raise  # Otro error, eleva la excepción


def delete_store_dynamo_db(store_name):
    store_name = store_name.replace(" ", "_")

    table_names = [
        f"{store_name}_order_cache_dev",
        f"{store_name}_order_cache_prod"
    ]

    for table_name in table_names:
        if not table_exists(table_name):
            print(f"Table {table_name} does not exist. Skipping deletion.")
            print('------------------------------------')
            continue

        try:
            dynamodb_client.delete_table(TableName=table_name)
            print(f"Table {table_name} deleted successfully.")
            print('------------------------------------')
        except ClientError as e:
            print(f"Error deleting DynamoDB table {table_name}: {e}")
            print('------------------------------------')
    

def delete_s3_bucket_contents(bucket_name):
    bucket = s3.Bucket(bucket_name)
    bucket.objects.all().delete()


def delete_s3_bucket(bucket_name):
    try:
        # Vacía el contenido del bucket primero
        delete_s3_bucket_contents(bucket_name)
        # Elimina el bucket
        s3_client.delete_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} eliminado exitosamente.")
    except s3_client.exceptions.NoSuchBucket:
        print(f"El bucket {bucket_name} no existe.")
    except Exception as e:
        print(f"Error al eliminar el bucket {bucket_name}: {e}")


def delete_store_s3_resources(store_name):
    bucket_name_dev = f"{store_name}-dev".lower().replace(" ", "-")
    bucket_name_prod = f"{store_name}-prod".lower().replace(" ", "-")

    # Eliminar buckets de desarrollo y producción
    for bucket_name in [bucket_name_dev, bucket_name_prod]:
        delete_s3_bucket(bucket_name)
        print('------------------------------------')


def delete_aws_resources(store_name):
    delete_store_dynamo_db(store_name)
    delete_store_s3_resources(store_name)
