from utils import bucket_exists

import boto3


def save_to_s3(bucket_name, content, file_name):
    try:
        # Convert the bucket name to a valid S3 bucket name
        bucket_name = bucket_name.lower().replace(" ", "-")

        # Initialize the S3 client
        s3 = boto3.client('s3', region_name='sa-east-1')

        # Check if the bucket exists
        if not bucket_exists(bucket_name):
            s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'sa-east-1'})

        # Determine the content type based on the file extension
        content_type = 'application/zip' if file_name.endswith('.zip') else 'text/csv'

        # Upload the content to the bucket
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=content, ContentType=content_type)

        return f"File saved to {bucket_name}/{file_name}"

    except Exception as e:
        raise Exception(f"Error in save_to_s3 function: {e}")
