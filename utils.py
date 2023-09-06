import zipfile
import boto3
from botocore.exceptions import NoCredentialsError
import json
import os
import io

from datetime import datetime

ssm_client = boto3.client('ssm')


def load_product_attributes(shop_name):
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(base_path, 'products_json', f"{shop_name}_products.json")

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


def create_zip_in_memory(shop, csv_files):
    try:
        date_str = datetime.now().strftime('%Y-%m-%d')
        zip_name = f"{shop}-{date_str}.zip"
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
            for file_name, data in csv_files.items():
                zip_file.writestr(file_name, data)

        zip_buffer.seek(0)
        return zip_name, zip_buffer

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

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3', region_name='sa-east-1')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except NoCredentialsError:
        return None

    return response


def list_shop_secrets():
    try:
        client = boto3.client('secretsmanager', region_name='sa-east-1')
        response = client.list_secrets()

        shop_secrets = []
        for secret in response['SecretList']:
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


def send_messages_to_sqs(shop_names):
    try:
        sqs = boto3.client('sqs')
        queue_name = get_parameter('sqs_queue_name')
        queue_url = get_sqs_queue_url(queue_name)

        # Dividir shop_names en grupos de 10
        batches = [shop_names[i:i + 10] for i in range(0, len(shop_names), 10)]

        for batch in batches:
            entries = [{
                'Id': str(i),
                'MessageBody': json.dumps({"shop_name": name})
            } for i, name in enumerate(batch)]

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
