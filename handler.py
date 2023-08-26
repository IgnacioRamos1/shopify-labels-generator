from request_orders import request_orders
from filter_orders import filter_and_group_by_family
from build_csv import generate_csv_from_orders
from save_to_bucket import save_to_s3

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

    # For each shop, generate the CSV and save it to S3
    for shop in grouped_orders:
        for product in grouped_orders[shop]:
            csv_output = generate_csv_from_orders({shop: {product: grouped_orders[shop][product]}})
            save_to_s3(shop, csv_output, product)

    return {
        'statusCode': 200,
        'body': "CSV files generated and saved to S3"
    }
