from process_orders import process_orders
from utils import get_secret, list_shop_secrets, send_messages_to_sqs

import json
import logging
import boto3
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

sns_client = boto3.client('sns')

date = datetime.now().strftime('%Y-%m-%d')


def trigger_shop_processing(event, context):
    try:
        # Obtener la lista de tiendas desde Secrets Manager
        shop_names = list_shop_secrets()

        # Enviar un mensaje a SQS por cada tienda
        send_messages_to_sqs(shop_names)

        return {
            'statusCode': 200,
            'body': f"Triggered processing for {len(shop_names)} shops."
        }
    except Exception as e:
        error_message = f'Error in trigger_shop_processing function: {e}'
        logger.error(error_message)

        # Publicar mensaje de error en SNS
        sns_client.publish(
            TopicArn='arn:aws:sns:sa-east-1:421852645480:LambdaErrorNotifications',
            Message=error_message,
            Subject=f'Error in trigger_shop_processing function {date}'
        )

        return {
            'statusCode': 500,
            'body': str(e)
        }


def process_shop(event, context):
    try:
        # Procesar cada mensaje en el evento de SQS
        for record in event['Records']:
            print('Inicio de procesamiento de tienda')
            message_body = json.loads(record['body'])
            shop_name = message_body['shop_name']

            # Recuperar las credenciales para esta tienda específica
            credentials = get_secret(f'shop_secret_{shop_name}')
            # Procesar órdenes para esta tienda
            process_orders(credentials)
            print('Fin de procesamiento de tienda')

        return {
            'statusCode': 200,
            'body': "CSV files generated and saved to S3"
        }
    except Exception as e:
        error_message = f'Error in store {shop_name} in process_shop function: {e}'
        logger.error(error_message)

        # Publicar mensaje de error en SNS
        sns_client.publish(
            TopicArn='arn:aws:sns:sa-east-1:421852645480:LambdaErrorNotifications',
            Message=error_message,
            Subject=f'Error in process_shop function {date}'
        )
        return {
            'statusCode': 500,
            'body': str(e)
        }
