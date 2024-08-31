from builder.process_orders import process_orders
from utils.utils import send_messages_to_sqs

import os
import json
import logging
import boto3
from datetime import datetime, timedelta
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
        if stage == 'prod':
            # Obtener la fecha y hora actuales en UTC-3 (Buenos Aires)
            now = datetime.now(tz=pytz.timezone('America/Argentina/Buenos_Aires'))
            today = now.weekday()  # 0: Lunes, ..., 6: Domingo
            current_time = now.strftime('%H:%M')
            current_time_obj = datetime.strptime(current_time, '%H:%M')
            
            # Obtener la lista de tiendas de la base de datos
            shop_ids = get_stores_id()

            shops_to_process = []
            
            for shop_id in shop_ids:
                store = get_store(shop_id)
                execution_schedule = store.get('execution_schedule', [])
                
                for schedule in execution_schedule:
                    # Verificar si hoy es uno de los días de ejecución
                    if schedule['day'] == today:
                        for hour in schedule['hours']:
                            scheduled_time_obj = datetime.strptime(hour, '%H:%M')
                            time_difference = current_time_obj - scheduled_time_obj
                            if timedelta(minutes=0) <= time_difference <= timedelta(minutes=10): # 10 minutos de margen
                                shops_to_process.append(shop_id)
                                break
            
            # Enviar un mensaje a SQS por cada tienda a procesar
            send_messages_to_sqs(shops_to_process)

            return {
                'statusCode': 200,
                'body': f"Triggered processing for {len(shops_to_process)} shops."
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
