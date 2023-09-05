from process_orders import process_orders
from utils import get_parameter

import asyncio
import json


def lambda_handler(event, context):
    try:
        credentials = get_parameter('shopify_credentials')
        credentials = json.loads(credentials)

        asyncio.get_event_loop().run_until_complete(process_orders(credentials))

        return {
            'statusCode': 200,
            'body': "CSV files generated and saved to S3"
        }

    except Exception as e:
        raise e
