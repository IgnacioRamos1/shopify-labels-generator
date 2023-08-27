from request_orders import request_orders
from filter_orders import filter_and_group_by_family
from build_csv import generate_csv_from_orders

import boto3
from datetime import datetime
import asyncio

import json
import os


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
        print(f"Bucket {bucket_name} doesn't exist")
        try:
            s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'sa-east-1'})
            print(f"Bucket {bucket_name} created")
        except Exception as e:
            print(f"Error creating bucket: {e}")
            return

    # Definir el nombre del archivo basado en la fecha y nombre del producto
    date_str = datetime.now().strftime('%Y-%m-%d')
    file_name = f"{bucket_name} - {date_str} - {item_name}.csv"

    # Subir el contenido al bucket
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=content)

    return f"File saved to {bucket_name}/{file_name}"


async def async_save_to_s3(shop, product, grouped_data):
    # Load product attributes for the current shop
    product_attributes = load_product_attributes(shop)
    csv_output = generate_csv_from_orders({shop: {product: grouped_data[shop][product]}}, product_attributes)
    result = save_to_s3(shop, csv_output, product)
    print(result)


async def process_orders(credentials):
    # Obtener las órdenes
    total_orders = await request_orders(credentials)
    grouped_orders = filter_and_group_by_family(total_orders)
    
    # Lista para almacenar las tareas asincrónicas
    tasks = []
    
    # Para cada tienda y producto, crea una tarea para generar y guardar el CSV de manera asincrónica
    for shop in grouped_orders:
        for product in grouped_orders[shop]:
            task = asyncio.ensure_future(async_save_to_s3(shop, product, grouped_orders))
            tasks.append(task)

    # Ejecuta todas las tareas en paralelo
    await asyncio.gather(*tasks)
