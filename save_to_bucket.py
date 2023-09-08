from utils import bucket_exists

import boto3
import time
import os

stage = os.environ['STAGE']


def set_bucket_lifecycle(bucket_name, retries=3, delay=5):
    try:
        print('Starting set_bucket_lifecycle function')
        print('bucket_name', bucket_name)
        s3 = boto3.client('s3', region_name='sa-east-1')

        lifecycle_policy = {
            "Rules": [
                {
                    "ID": "ExpireOldFiles",
                    "Status": "Enabled",
                    "Expiration": {"Days": 30},
                    "Prefix": ''  # Esto aplica la regla a todos los objetos en el bucket
                }
            ]
        }

        for i in range(retries):
            try:
                s3.put_bucket_lifecycle_configuration(Bucket=bucket_name, LifecycleConfiguration=lifecycle_policy)
                print('Bucket lifecycle policy set successfully')
                return
            except Exception as e:
                if i < retries - 1:  # i es 0-indexed
                    print(f"Error setting lifecycle. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise Exception(f"Error setting lifecycle: {e}")

    except Exception as e:
        print(f"Error in set_bucket_lifecycle function: {e}")
        raise Exception(f"Error in set_bucket_lifecycle function: {e}")


def save_to_s3(bucket_name, content, file_name):
    try:
        print('Starting save_to_s3 function')
        # Convert the bucket name to a valid S3 bucket name
        bucket_name = f'{bucket_name}-{stage}'
        bucket_name = bucket_name.lower().replace(" ", "-")

        # Initialize the S3 client
        s3 = boto3.client('s3', region_name='sa-east-1')

        # Check if the bucket exists
        if not bucket_exists(bucket_name):
            print('Bucket does not exist, creating it')
            s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'sa-east-1'})
            set_bucket_lifecycle(bucket_name)
            print('Bucket created')

        # Determine the content type based on the file extension
        content_type = 'application/zip' if file_name.endswith('.zip') else 'text/csv'

        print('Uploading file to S3')
        # Upload the content to the bucket
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=content, ContentType=content_type)
        print('File uploaded to S3')

        return f"File saved to {bucket_name}/{file_name}"

    except Exception as e:
        raise Exception(f"Error in save_to_s3 function: {e}")
