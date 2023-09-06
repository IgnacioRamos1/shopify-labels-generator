from request_orders import request_orders
from filter_orders import filter_and_group_by_family
from send_email import send_products_missing_email
from utils import create_zip_in_memory, get_parameter, generate_presigned_url
from send_whatsapp_message import send_whatsapp_group_message, send_whatsapp_message
from save_to_bucket import generate_unprocessed_orders_csv, save_to_s3

from datetime import datetime


def process_orders(credentials):
    try:
        date = datetime.now().strftime('%Y-%m-%d')
        total_orders = request_orders(credentials)
        grouped_orders = filter_and_group_by_family(total_orders)
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
            csv_data, file_name, not_added_products, not_added_floor_length, not_added_missing_street_or_number = generate_unprocessed_orders_csv(shop, product, grouped_orders)

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
            message = "\n".join([f"{order['person']} - {order['item']} - {order['reason']}" for order in all_not_added_floor_length])
            body = f'Los siguientes pedidos tienen errores en su Piso:\n\n{message}'
            send_whatsapp_message(group_chat_id, body)

        # Si se generó un CSV y hay errores en la calle o número.
        if in_memory_csvs and all_not_added_missing_street_or_number:
            message = "\n".join([f"{order['person']} - {order['item']} - {order['reason']}" for order in all_not_added_missing_street_or_number])
            body = f'Los siguientes pedidos tienen errores en su Calle o Numero:\n\n{message}'
            send_whatsapp_message(group_chat_id, body)

        # Si no se generó un CSV pero hay error en la calle o número.
        if not in_memory_csvs and all_not_added_missing_street_or_number:
            message = "\n".join([f"{order['person']} - {order['item']} - {order['reason']}" for order in all_not_added_missing_street_or_number])
            send_whatsapp_message(group_chat_id, message)

        # Send the unadded products by email.
        if all_not_added_products:
            send_products_missing_email(from_email, to_email, all_not_added_products, shop, date)

        # If no CSVs are generated, end the execution.
        if not in_memory_csvs:
            print('No hay un csv generado', shop, date)
            return

        print('Continuo con la ejecución')
        # Continue with the process of creating the zip file and sending it via WhatsApp if we get to this point.
        _, zip_buffer = create_zip_in_memory(shop, in_memory_csvs)

        # Save the ZIP file to S3
        save_to_s3(shop, zip_buffer.getvalue(), f"{date}.zip")

        formatted_shop_name = shop.lower().replace(" ", "-")

        # Generate a presigned URL for the ZIP file
        s3_presigned_url = generate_presigned_url(formatted_shop_name, f"{date}.zip")

        # Send the ZIP file via WhatsApp
        send_whatsapp_group_message(date, shop, total_orders_count, s3_presigned_url, group_chat_id)
        print('Se ha terminado de procesar las ordenes', shop, date)

    except Exception as e:
        raise Exception(f"Error en la función process_orders: {e}")
