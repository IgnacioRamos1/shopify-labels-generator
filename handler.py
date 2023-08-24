from request_orders import request_orders
from filter_orders import filter_and_group_by_family
import asyncio


def lambda_handler(event, context):
    credentials = [
        {
            'shop_name': 'Strawberry Store',
            'shop_url': 'www.strawberrystorearg.com',
            'access_token': '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'
        },
        # Add more stores as needed
    ]

    # Call the asynchronous function and get the result
    total_orders = asyncio.get_event_loop().run_until_complete(request_orders(credentials))

    grouped_orders = filter_and_group_by_family(total_orders)
    
    return {
        'statusCode': 200,
        'body': grouped_orders
    }
