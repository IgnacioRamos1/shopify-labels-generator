from builder.request_orders import fetch_orders_for_store
from utils.filter_orders import filter_and_group_by_family
from utils.send_email import send_products_missing_email
from utils.utils import create_zip_in_memory, get_parameter, generate_presigned_url
from utils.send_whatsapp_message import send_whatsapp_group_message, send_whatsapp_message
from storage.save_to_bucket import save_to_s3
from builder.generate_unprocessed_orders import generate_unprocessed_orders_csv

from datetime import datetime
import os

stage = os.environ['STAGE']


def process_orders(credentials):
    try:
        print('Iniciando proceso de ordenes para', credentials['shop_name'])
        date = datetime.now().strftime('%Y-%m-%d')
        print('Inicio de recuperacion de ordenes')
        total_orders = fetch_orders_for_store(credentials['shop_name'], credentials['shop_url'], credentials['access_token'], credentials['date'])
        print('Fin de recuperacion de ordenes')
        print('Agrupando ordenes')
        grouped_orders = filter_and_group_by_family(total_orders)
        print('Fin de agrupamiento de ordenes')
        from_email = get_parameter('from_email')
        to_email = get_parameter('to_email')

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

        group_chat_id = credentials['group_chat_id']

        # Si se generó un CSV y hay errores en el piso.
        if in_memory_csvs and all_not_added_floor_length:
            print('Hay errores en el piso, enviando mensaje')
            message = "\n".join([f"{order['person']} - {order['item']} - {order['reason']}" for order in all_not_added_floor_length])
            body = f'Los siguientes pedidos tienen errores en su Piso:\n\n{message}'
            send_whatsapp_message(group_chat_id, body)
            print('Mensaje enviado')

        # Si se generó un CSV y hay errores en la calle o número.
        if in_memory_csvs and all_not_added_missing_street_or_number:
            print('Hay errores en la calle o número, enviando mensaje')
            message = "\n".join([f"{order['person']} - {order['item']} - {order['reason']}" for order in all_not_added_missing_street_or_number])
            body = f'Los siguientes pedidos tienen errores en su Calle o Numero:\n\n{message}'
            send_whatsapp_message(group_chat_id, body)
            print('Mensaje enviado')

        # Si no se generó un CSV pero hay error en la calle o número.
        if not in_memory_csvs and all_not_added_missing_street_or_number:
            print('No se generó un CSV pero hay error en la calle o número, enviando mensaje')
            message = "\n".join([f"{order['person']} - {order['item']} - {order['reason']}" for order in all_not_added_missing_street_or_number])
            send_whatsapp_message(group_chat_id, message)
            print('Mensaje enviado')

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

        # Send the ZIP file via WhatsApp
        print('Enviando mensaje de WhatsApp')
        send_whatsapp_group_message(date, shop, total_orders_count, s3_presigned_url, group_chat_id)
        print('Mensaje de WhatsApp enviado')
        print('Se ha terminado de procesar las ordenes', shop, date)

    except Exception as e:
        raise Exception(f"Error en la función process_orders: {e}")
