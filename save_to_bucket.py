from request_orders import request_orders
from filter_orders import filter_and_group_by_family
from build_csv import generate_csv_from_orders
from send_email import send_email, send_products_missing_email
from utils import load_product_attributes, create_zip_in_memory, bucket_exists, get_parameter, generate_presigned_url
from dynamodb_cache import check_order_processed, mark_order_as_processed
from send_whatsapp_message import send_whatsapp_message

import boto3
from datetime import datetime
import asyncio


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
            return None, None, []

        product_attributes = load_product_attributes(shop)
        csv_output, not_added = generate_csv_from_orders({shop: {product: unprocessed_orders}}, product_attributes)

        # Define filename based on shop, date, and product
        date_str = datetime.now().strftime('%Y-%m-%d')
        file_name = f"{shop} - {date_str} - {product}.csv"
        
        # Mark each order as processed only if it's not marked as 'exclude'
        for order in unprocessed_orders:
            if not order.get('exclude', False):
                mark_order_as_processed(shop, order["order_id"], order["item_id"])

        return csv_output, file_name, not_added

    except Exception as e:
        raise Exception(f"Error in async_save_to_s3 function: {e}")


async def process_orders(credentials):
    try:
        date = datetime.now().strftime('%Y-%m-%d')
        total_orders, total_orders_count = await request_orders(credentials)
        grouped_orders = filter_and_group_by_family(total_orders)
        from_email = get_parameter('from_email')

        all_not_added = []

        for shop in grouped_orders:
            tasks = []
            in_memory_csvs = {}
            orders_breakdown = {}
            
            for product, orders in grouped_orders[shop].items():
                # Removed 'credentials' from the function call
                task = asyncio.ensure_future(async_save_to_s3(shop, product, grouped_orders))
                tasks.append(task)

            completed_tasks = await asyncio.gather(*tasks)
            
            for csv_data, file_name, not_added in completed_tasks:
                all_not_added.extend(not_added)
                if csv_data and file_name and len(csv_data.splitlines()) > 1:
                    in_memory_csvs[file_name] = csv_data

            for file_name, csv_content in in_memory_csvs.items():
                product_name = file_name.split('-')[2].strip()
                orders_breakdown[product_name] = len(csv_content.splitlines()) - 1

            total_orders_count[shop] = sum(orders_breakdown.values())

            if in_memory_csvs:
                _, zip_buffer = create_zip_in_memory(shop, in_memory_csvs)
                save_to_s3(shop, zip_buffer.getvalue(), f"{date}.zip")
                '''
                Send the ZIP file to the email address associated with the shop

                to_email = [store["email"] for store in credentials if store["shop_name"] == shop][0]
                send_email(zip_buffer, f"{date}.zip", from_email, to_email, shop, total_orders_count[shop], date, orders_breakdown)
                '''
                formatted_shop_name = shop.lower().replace(" ", "-")
                s3_presigned_url = generate_presigned_url(formatted_shop_name, f"{date}.zip")
                send_whatsapp_message(date, shop, total_orders_count, s3_presigned_url)


        if all_not_added:
            to_email = [store["email"] for store in credentials if store["shop_name"] == shop][0]
            send_products_missing_email(from_email, to_email, all_not_added)

    except Exception as e:
        raise Exception(f"Error in updated_process_orders function: {e}")
