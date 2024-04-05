import zipfile
import boto3
from botocore.exceptions import NoCredentialsError
import json
import os
import io


ssm_client = boto3.client('ssm')


class ApiException(Exception):
    pass


def load_product_attributes(shop_name):
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(base_path, '..', 'products_json', f"{shop_name}_products.json")

        with open(filename, 'r') as f:
            return json.load(f)

    except Exception as e:
        raise Exception(f"Error in load_product_attributes function: {e}")


def bucket_exists(bucket_name):
    try:
        s3 = boto3.client('s3', region_name='sa-east-1')
        buckets = s3.list_buckets()
        return any(bucket['Name'] == bucket_name for bucket in buckets.get('Buckets', []))

    except Exception as e:
        raise Exception(f"Error in bucket_exists function: {e}")


def create_zip_in_memory(csv_files):
    try:
        print('Starting create_zip_in_memory function')
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
            for file_name, data in csv_files.items():
                zip_file.writestr(file_name, data)

        zip_buffer.seek(0)
        print('Finished create_zip_in_memory function')
        return zip_buffer

    except Exception as e:
        raise Exception(f"Error in create_zip_in_memory function: {e}")


def get_parameter(name):
    """Retrieve a parameter from AWS Systems Manager Parameter Store."""
    try:
        response = ssm_client.get_parameter(Name=name, WithDecryption=True)
        return response['Parameter']['Value']

    except ssm_client.exceptions.ParameterNotFound:
        raise Exception(f"Parameter {name} not found in Parameter Store.")

    except ssm_client.exceptions.InternalServerError:
        raise Exception("Internal server error while fetching parameter from Parameter Store.")

    except Exception as e:
        raise Exception(f"Error retrieving parameter from Parameter Store: {e}")


def generate_presigned_url(bucket_name, object_name, expiration=3600):
    """
    Generate a presigned URL to share an S3 object.

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """
    print('Starting generate_presigned_url function')
    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3', region_name='sa-east-1')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
        print('Finished generate_presigned_url function')
        return response

    except NoCredentialsError:
        raise Exception('Credentials not available')


def list_shop_secrets():
    try:
        client = boto3.client('secretsmanager', region_name='sa-east-1')
        paginator = client.get_paginator('list_secrets')
        shop_secrets = []

        # Itera a través de todas las páginas de la respuesta paginada
        for page in paginator.paginate():
            for secret in page['SecretList']:
                if secret['Name'].startswith('shop_secret_'):
                    shop_secrets.append(secret['Name'].replace('shop_secret_', ''))

        return shop_secrets

    except Exception as e:
        raise Exception(f"Error in list_shop_secrets function: {e}")


def get_sqs_queue_url(queue_name):
    try:
        sqs = boto3.client('sqs')
        response = sqs.get_queue_url(QueueName=queue_name)
        return response['QueueUrl']

    except Exception as e:
        raise Exception(f"Error in get_sqs_queue_url function: {e}")


def send_messages_to_sqs(shop_uuids):
    try:
        sqs = boto3.client('sqs')
        queue_name = os.environ['SQS_QUEUE_NAME']
        queue_url = get_sqs_queue_url(queue_name)

        # Dividir shop_names en grupos de 10
        batches = [shop_uuids[i:i + 10] for i in range(0, len(shop_uuids), 10)]

        for batch in batches:
            entries = [{
                'Id': str(i),
                'MessageBody': json.dumps({"shop_uuid": uuid})
            } for i, uuid in enumerate(batch)]

            sqs.send_message_batch(QueueUrl=queue_url, Entries=entries)

    except Exception as e:
        raise Exception(f"Error in send_messages_to_sqs function: {e}")


def get_secret(shop_name):
    try:
        client = boto3.client('secretsmanager', region_name='sa-east-1')
        response = client.get_secret_value(SecretId=shop_name)
        return json.loads(response['SecretString'])

    except Exception as e:
        raise Exception(f"Error in get_secret function: {e}")
