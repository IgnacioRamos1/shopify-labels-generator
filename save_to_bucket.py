from request_orders import request_orders
from filter_orders import filter_and_group_by_family
from build_csv import generate_csv_from_orders
from send_email import send_email, send_products_missing_email
from utils import load_product_attributes, create_zip_in_memory, bucket_exists, get_parameter
from dynamodb_cache import check_order_processed, mark_order_as_processed

import boto3
from datetime import datetime
import asyncio


def save_to_s3(bucket_name, content, item_name):
    try:
        # Convert the bucket name to a valid S3 bucket name
        bucket_name = bucket_name.lower().replace(" ", "-")
        
        # Initialize the S3 client
        s3 = boto3.client('s3', region_name='sa-east-1')

        # Check if the bucket exists
        if not bucket_exists(bucket_name):
            try:
                s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'sa-east-1'})
            except Exception as e:
                raise Exception(f"Error creating bucket: {e}")

        # Define the filename based on date and product name
        date_str = datetime.now().strftime('%Y-%m-%d')
        file_name = f"{bucket_name} - {date_str} - {item_name}.csv"
        s3_key = f"{date_str}/{file_name}"  # Defining the folder/filename structure

        # Upload the content to the bucket
        s3.put_object(Bucket=bucket_name, Key=s3_key, Body=content)

        return f"File saved to {bucket_name}/{s3_key}"

    except Exception as e:
        raise Exception(f"Error in save_to_s3 function: {e}")


async def async_save_to_s3(shop, product, grouped_data, credentials):
    try:
        # Filter orders that have already been processed
        unprocessed_orders = [order for order in grouped_data[shop][product] if not check_order_processed(shop, order["order_id"], order["item_id"])]

        # If all orders for this group have been processed before, return
        if not unprocessed_orders:
            return None, None

        product_attributes = load_product_attributes(shop)
        csv_output, not_added = generate_csv_from_orders({shop: {product: unprocessed_orders}}, product_attributes)

        # If there are products not added, send the missing products email
        if not_added:
            from_email = get_parameter('from_email')  # assuming you have this utility function to get the sender's email
            to_email = [store["email"] for store in credentials if store["shop_name"] == shop][0]  # the email associated with the shop
            send_products_missing_email(from_email, to_email, not_added)

        # Define filename based on shop, date, and product
        date_str = datetime.now().strftime('%Y-%m-%d')
        file_name = f"{shop} - {date_str} - {product}.csv"
        
        # Save to S3
        save_to_s3(shop, csv_output, product)
            
        # Mark each order as processed only if it's not marked as 'exclude'
        for order in unprocessed_orders:
            if not order.get('exclude', False):
                mark_order_as_processed(shop, order["order_id"], order["item_id"])
        
        # Return csv data and filename
        return csv_output, file_name

    except Exception as e:
        raise Exception(f"Error in async_save_to_s3 function: {e}")


async def process_orders(credentials):
    try:
        date = datetime.now().strftime('%d-%m-%Y')
        # Get orders
        total_orders, total_orders_count = await request_orders(credentials)
        grouped_orders = filter_and_group_by_family(total_orders)
        
        # This email will remain constant as the sender's email
        from_email = get_parameter('from_email')

        # For each shop, process orders, generate ZIP and send email
        for shop in grouped_orders:
            # List to store async tasks and in-memory CSV data
            tasks = []
            in_memory_csvs = {}  # To store csv data in memory

            # Update the total_orders_count for this shop by excluding orders with 'exclude' key set to True
            total_orders_count[shop] = sum(1 for order in grouped_orders[shop].values() for item in order if not item.get('exclude', False))
            
            # For each product of the shop, create a task to generate and save the CSV asynchronously
            for product in grouped_orders[shop]:
                task = asyncio.ensure_future(async_save_to_s3(shop, product, grouped_orders, credentials))
                tasks.append(task)

            # Await all tasks to complete
            completed_tasks = await asyncio.gather(*tasks)
            
            for csv_data, file_name in completed_tasks:
                # Check if CSV has more than just a header
                if csv_data and file_name and len(csv_data.splitlines()) > 1:
                    in_memory_csvs[file_name] = csv_data

            # Create ZIP from in-memory CSVs only if we have valid CSVs
            if in_memory_csvs:
                zip_name, zip_buffer = create_zip_in_memory(shop, in_memory_csvs)

                # Retrieve the email associated with the current shop
                to_email = [store["email"] for store in credentials if store["shop_name"] == shop][0]

                # Send email with ZIP for the current shop
                send_email(zip_buffer, zip_name, from_email, to_email, shop, total_orders_count[shop], date)

    except Exception as e:
        raise Exception(f"Error in process_orders function: {e}")
