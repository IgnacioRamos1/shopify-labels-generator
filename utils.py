import zipfile
import boto3
import json
import os
import io

from datetime import datetime


def load_product_attributes(shop_name):
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(base_path, 'products_json', f"{shop_name}_products.json")
        
        with open(filename, 'r') as f:
            return json.load(f)

    except Exception as e:
        raise Exception(f"Error in load_product_attributes function: {e}")


def bucket_exists(bucket_name):
    try:
        s3 = boto3.client('s3', region_name='sa-east-1')
        buckets = s3.list_buckets()
        return any(bucket['Name'] == bucket_name for bucket in buckets.get('Buckets', []))

    except Exception as e:
        raise Exception(f"Error in bucket_exists function: {e}")


def create_zip_in_memory(shop, csv_files):
    try:
        date_str = datetime.now().strftime('%Y-%m-%d')
        zip_name = f"{shop}-{date_str}.zip"
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
            for file_name, data in csv_files.items():
                zip_file.writestr(file_name, data)
        
        zip_buffer.seek(0)
        return zip_name, zip_buffer

    except Exception as e:
        raise Exception(f"Error in create_zip_in_memory function: {e}")
