from request_orders import request_orders
from filter_orders import filter_and_group_by_family
from build_csv import generate_csv_from_orders
from send_email import send_email_with_zip

import boto3
from datetime import datetime
import asyncio
import zipfile

import json
import os
import io


def load_product_attributes(shop_name):
    """Load product attributes from the store's corresponding JSON file."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(base_path, 'products_json', f"{shop_name}_products.json")
    
    with open(filename, 'r') as f:
        return json.load(f)
    

def bucket_exists(bucket_name):
    """Check if S3 bucket exists."""
    s3 = boto3.client('s3', region_name='sa-east-1')
    buckets = s3.list_buckets()
    return any(bucket['Name'] == bucket_name for bucket in buckets.get('Buckets', []))


def save_to_s3(bucket_name, content, item_name):
    # Convert the bucket name to a valid S3 bucket name
    bucket_name = bucket_name.lower().replace(" ", "-")
    
    # Inicializar el cliente de S3
    s3 = boto3.client('s3', region_name='sa-east-1')

    # Check if the bucket exists
    if not bucket_exists(bucket_name):
        try:
            s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'sa-east-1'})
        except Exception as e:
            return f"Error creating bucket: {e}"

    # Definir el nombre del archivo basado en la fecha y nombre del producto
    date_str = datetime.now().strftime('%Y-%m-%d')
    file_name = f"{bucket_name} - {date_str} - {item_name}.csv"
    s3_key = f"{date_str}/{file_name}"  # Aquí estamos definiendo la estructura de carpeta/nombre_del_archivo

    # Subir el contenido al bucket
    s3.put_object(Bucket=bucket_name, Key=s3_key, Body=content)

    return f"File saved to {bucket_name}/{s3_key}"


async def async_save_to_s3(shop, product, grouped_data):
    # Load product attributes for the current shop
    product_attributes = load_product_attributes(shop)
    csv_output = generate_csv_from_orders({shop: {product: grouped_data[shop][product]}}, product_attributes)
    
    # Define filename based on shop, date, and product
    date_str = datetime.now().strftime('%Y-%m-%d')
    file_name = f"{shop} - {date_str} - {product}.csv"
    
    # Save to S3
    save_to_s3(shop, csv_output, product)
    
    # Return csv data and filename
    return csv_output, file_name


def create_zip_in_memory(shop, csv_files):
    date_str = datetime.now().strftime('%Y-%m-%d')
    zip_name = f"{shop}-{date_str}.zip"
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for file_name, data in csv_files.items():
            zip_file.writestr(file_name, data)
    
    zip_buffer.seek(0)
    return zip_name, zip_buffer


async def process_orders(credentials):
    # Get orders
    total_orders = await request_orders(credentials)
    grouped_orders = filter_and_group_by_family(total_orders)
    
    # List to store async tasks and in-memory CSV data
    tasks = []
    in_memory_csvs = {}  # To store csv data in memory
    
    # For each shop and product, create a task to generate and save the CSV asynchronously
    for shop in grouped_orders:
        for product in grouped_orders[shop]:
            task = asyncio.ensure_future(async_save_to_s3(shop, product, grouped_orders))
            tasks.append(task)

    # Await all tasks to complete
    completed_tasks = await asyncio.gather(*tasks)
    
    for csv_data, file_name in completed_tasks:
        in_memory_csvs[file_name] = csv_data

    # Create ZIP from in-memory CSVs
    zip_name, zip_buffer = create_zip_in_memory(shop, in_memory_csvs)

    # TODO: Save emails to parameter store
    from_email = "envioshopify@gmail.com"
    to_email = "iramosibx@gmail.com"

    send_email_with_zip(zip_buffer, zip_name, from_email, to_email)
