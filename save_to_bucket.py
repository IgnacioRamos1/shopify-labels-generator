from build_csv import generate_csv_from_orders
from utils import load_product_attributes, bucket_exists
from dynamodb_cache import check_order_processed, mark_order_as_processed, get_or_create_table_name

import boto3
from datetime import datetime


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


def generate_unprocessed_orders_csv(shop, product, grouped_data):
    try:
        # Ensure the DynamoDB table exists
        table_name = get_or_create_table_name(shop)

        # Check if the product exists in the grouped_data
        if product not in grouped_data:
            return None, None, [], [], []

        unprocessed_orders = []
        # Check if each order has been processed
        for order in grouped_data[product]:
            is_processed = check_order_processed(table_name, order["order_id"], order["item_id"])
            # If the order has not been processed, add it to the list
            if not is_processed:
                unprocessed_orders.append(order)

        # Si todas las órdenes ya han sido procesadas, devolver vacío.
        if not unprocessed_orders:
            return None, None, [], [], []

        # Cargar los atributos del producto
        product_attributes = load_product_attributes(shop)

        # Llamar a la función que genera el CSV a partir de las órdenes no procesadas pasando cada producto y sus órdenes y los atributos del producto
        csv_output, not_added_products, not_added_floor_length, not_added_missing_street_or_number = generate_csv_from_orders({product: unprocessed_orders}, product_attributes)

        # Si el output del CSV es 1 (tiene solo el header), significa que no se ha añadido ningún producto.
        if len(csv_output.splitlines()) <= 1:
            return None, None, not_added_products, not_added_floor_length, not_added_missing_street_or_number

        # Define filename based on shop, date, and product
        date_str = datetime.now().strftime('%Y-%m-%d')
        file_name = f"{shop} - {date_str} - {product}.csv"

        # Mark each order as processed only if it's not marked as 'exclude'
        for order in unprocessed_orders:
            if not order.get('exclude', False):
                mark_order_as_processed(table_name, order["order_id"], order["item_id"])

        return csv_output, file_name, not_added_products, not_added_floor_length, not_added_missing_street_or_number

    except Exception as e:
        raise Exception(f"Error en la función generate_unprocessed_orders_csv: {e}")
