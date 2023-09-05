from build_csv import generate_csv_from_orders
from utils import load_product_attributes, bucket_exists
from dynamodb_cache import check_order_processed, mark_order_as_processed

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


async def async_save_to_s3(shop, product, grouped_data):
    try:
        unprocessed_orders = [order for order in grouped_data[shop][product] if not check_order_processed(shop, order["order_id"], order["item_id"])]
        if not unprocessed_orders:
            return None, None, [], []

        product_attributes = load_product_attributes(shop)
        csv_output, not_added_products, not_added_orders = generate_csv_from_orders({shop: {product: unprocessed_orders}}, product_attributes)

        # Define filename based on shop, date, and product
        date_str = datetime.now().strftime('%Y-%m-%d')
        file_name = f"{shop} - {date_str} - {product}.csv"
        
        # Mark each order as processed only if it's not marked as 'exclude'
        for order in unprocessed_orders:
            if not order.get('exclude', False):
                mark_order_as_processed(shop, order["order_id"], order["item_id"])

        return csv_output, file_name, not_added_products, not_added_orders

    except Exception as e:
        raise Exception(f"Error in async_save_to_s3 function: {e}")
