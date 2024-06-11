import json
import boto3
import os

stage = os.environ['STAGE']

def trigger_processing(event, context):
    try:
        print('Triggering processing for today.')
        lambda_client = boto3.client('lambda')
        lambda_client.invoke(
            FunctionName=f'shopify-csv-generator-{stage}-triggerProcessing',
            InvocationType='Event',
            Payload=json.dumps({})
        )
        return {
            'statusCode': 200,
            'body': f"Triggered processing for today."
            }

    except Exception as e:
        print(f'Error in trigger_processing function: {e}')
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }

