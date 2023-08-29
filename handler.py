from save_to_bucket import process_orders

import asyncio


def lambda_handler(event, context):
    try:
        credentials = [
            {
                'shop_name': 'Strawberry Store',
                'shop_url': 'www.strawberrystorearg.com',
                'access_token': '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'
            },
            # Add more stores as needed
        ]

        asyncio.get_event_loop().run_until_complete(process_orders(credentials))

        return {
            'statusCode': 200,
            'body': "CSV files generated and saved to S3"
        }

    except Exception as e:
        # This is a placeholder. We will add error notification here.
        raise e
