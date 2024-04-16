from builder.process_orders import process_orders
from utils.utils import send_messages_to_sqs

import os
import json
import logging
import boto3
from datetime import datetime
import pytz

from mongo_db.get_stores_id import get_stores_id
from mongo_db.get_store import get_store

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

sns_client = boto3.client('sns')

date = datetime.now().strftime('%Y-%m-%d')

stage = os.environ['STAGE']
sns_topic_arn = f'arn:aws:sns:sa-east-1:421852645480:LambdaErrorNotifications-{stage}'


def trigger_shop_processing(event, context):
    try:
        print('Inicio de trigger_shop_processing')
        # Verificar si el stage es prod
        if stage == 'prod':
            # Obtener el día de la semana actual en UTC-3
            today = datetime.now(tz=pytz.timezone('America/Argentina/Buenos_Aires')).weekday()

            # Verificar si el día es distinto de viernes o sábado
            if today not in (4, 5):
                # Obtener la lista de tiendas de la base de datos
                shop_ids = get_stores_id()

                # Enviar un mensaje a SQS por cada tienda
                send_messages_to_sqs(shop_ids)

                return {
                    'statusCode': 200,
                    'body': f"Triggered processing for {len(shop_ids)} shops."
                }
            else:
                # No hacer nada si el día es viernes o sábado
                return {
                    'statusCode': 200,
                    'body': f"No processing triggered for today."
                }
        else:
            # Obtener la lista de tiendas de la base de datos
            shop_ids = get_stores_id()

            # Enviar un mensaje a SQS por cada tienda
            send_messages_to_sqs(shop_ids)

            return {
                'statusCode': 200,
                'body': f"Triggered processing for {len(shop_ids)} shops."
            }

    except Exception as e:
        error_message = f'Error in trigger_shop_processing function: {e}'
        logger.error(error_message)

        # Publicar mensaje de error en SNS
        sns_client.publish(
            TopicArn=sns_topic_arn,
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
            shop_id = message_body['shop_id']

            store = get_store(shop_id)

            # Procesar órdenes para esta tienda
            process_orders(store)
            print('Fin de procesamiento de tienda')

        return {
            'statusCode': 200,
            'body': "CSV files generated and saved to S3"
        }
    except Exception as e:
        error_message = f'Error in process_shop function: {e}'
        logger.error(error_message)

        # Publicar mensaje de error en SNS
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=error_message,
            Subject=f'Error in process_shop function {date} - {store["name"]}'
        )
        return {
            'statusCode': 500,
            'body': str(e)
        }
