from builder.request_orders import fetch_orders_for_store
from utils.filter_orders import filter_and_group_by_family
from utils.send_email import send_products_missing_email, send_zip_email
from utils.utils import create_zip_in_memory, get_parameter, generate_presigned_url
from storage.save_to_bucket import save_to_s3
from builder.generate_unprocessed_orders import generate_unprocessed_orders_csv
from new_builder.new_request_orders import new_fetch_orders_for_store

from datetime import datetime
import os

stage = os.environ['STAGE']


def process_orders(credentials):
    try:
        print('Iniciando proceso de ordenes para', credentials['shop_name'])
        date = datetime.now().strftime('%Y-%m-%d')
        print('Inicio de recuperacion de ordenes')
    
        if credentials['shop_name'] == 'Strawberry Store':
            total_orders = new_fetch_orders_for_store(credentials['shop_name'], credentials['shop_url'], credentials['access_token'], credentials['date'])
        else:
            total_orders = fetch_orders_for_store(credentials['shop_name'], credentials['shop_url'], credentials['access_token'], credentials['date'])

        print('Fin de recuperacion de ordenes')
        print('Agrupando ordenes')
        grouped_orders = filter_and_group_by_family(total_orders)
        print('Fin de agrupamiento de ordenes')
        from_email = get_parameter('from_email')
        to_email = credentials['to_email']

        total_orders_count = 0

        all_not_added_products = []
        all_not_added_floor_length = []
        all_not_added_missing_street_or_number = []

        in_memory_csvs = {}

        shop = credentials['shop_name']

        # Generate a CSV file for each product.
        for product in grouped_orders:
            print('Generando CSV')
            csv_data, file_name, not_added_products, not_added_floor_length, not_added_missing_street_or_number = generate_unprocessed_orders_csv(shop, product, grouped_orders)
            print('CSV generado')

            # Add the products and orders not added to the global lists
            all_not_added_products.extend(not_added_products)
            all_not_added_floor_length.extend(not_added_floor_length)
            all_not_added_missing_street_or_number.extend(not_added_missing_street_or_number)

            # If there is generated CSV, add it to the in-memory CSVs dictionary.
            if csv_data and file_name:
                in_memory_csvs[file_name] = csv_data
                # Add the number of orders in the CSV to the total orders count
                total_orders_count += len(csv_data.splitlines()) - 1  # Subtracting 1 for header

        # Send the unadded products by email.
        if all_not_added_products:
            print('Hay productos no agregados, enviando email')
            send_products_missing_email(from_email, to_email, all_not_added_products, shop, date)
            print('Email enviado')

        # If no CSVs are generated, end the execution.
        if not in_memory_csvs:
            print('No hay un csv generado', shop, date)
            return

        # Continue with the process of creating the zip file and sending it via WhatsApp if we get to this point.
        print('Creando ZIP')
        zip_buffer = create_zip_in_memory(in_memory_csvs)
        print('ZIP creado')

        print('Guardando ZIP en S3')
        # Save the ZIP file to S3
        save_to_s3(shop, zip_buffer.getvalue(), f"{date}.zip")
        print('ZIP guardado en S3')

        formatted_shop_name = shop.lower().replace(" ", "-")
        formatted_shop_name = f'{formatted_shop_name}-{stage}'

        print('Generando URL presignada')
        # Generate a presigned URL for the ZIP file
        s3_presigned_url = generate_presigned_url(formatted_shop_name, f"{date}.zip")
        print('URL presignada generada')

        # Send the ZIP file via Email
        print('Enviando email con ZIP')
        send_zip_email(from_email, to_email, shop, date, s3_presigned_url, total_orders_count, all_not_added_floor_length, all_not_added_missing_street_or_number)
        print('Email enviado')
        print('Se ha terminado de procesar las ordenes', shop, date)

    except Exception as e:
        raise Exception(f"Error en la función process_orders: {e}")
