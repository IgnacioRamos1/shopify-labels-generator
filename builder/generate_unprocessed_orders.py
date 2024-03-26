from builder.build_csv import generate_csv_from_orders
from new_builder.new_build_csv import new_generate_csv_from_orders
from utils.utils import load_product_attributes
from storage.dynamodb_cache import check_order_processed, mark_order_as_processed, get_or_create_table_name

from datetime import datetime


def generate_unprocessed_orders_csv(shop, product, grouped_data, fixy_status, fixy_service_id, fixy_client_id, fixy_branch_code, fixy_company, fixy_sender):
    try:
        print('Getting table name for product', product)
        # Ensure the DynamoDB table exists
        table_name = get_or_create_table_name(shop)
        print('Table name:', table_name)

        # Check if the product exists in the grouped_data
        if product not in grouped_data:
            return None, None, [], [], []

        unprocessed_orders = []
        # Check if each order has been processed
        print('Checking if order has been processed')
        for order in grouped_data[product]:
            if order["item_id"]:
                is_processed = check_order_processed(table_name, order["order_id"], order["item_id"])
                # If the order has not been processed, add it to the list
                if not is_processed:
                    unprocessed_orders.append(order)
            else:
                continue

        print('Finished checking if order has been processed')

        # Si todas las órdenes ya han sido procesadas, devolver vacío.
        if not unprocessed_orders:
            print('Todas las ordenes ya han sido procesadas')
            return None, None, [], [], []

        # Cargar los atributos del producto
        product_attributes = load_product_attributes(shop)

        # Llamar a la función que genera el CSV a partir de las órdenes no procesadas pasando cada producto y sus órdenes y los atributos del producto
        if fixy_status == 'True':
            print('Generando CSV v2.0 de ordenes no procesadas')
            csv_output, not_added_products, not_added_floor_length, not_added_missing_street_or_number = new_generate_csv_from_orders({product: unprocessed_orders}, product_attributes, fixy_service_id, fixy_client_id, fixy_branch_code, fixy_company, fixy_sender)
        else:
            print('Generando CSV de ordenes no procesadas')
            csv_output, not_added_products, not_added_floor_length, not_added_missing_street_or_number = generate_csv_from_orders({product: unprocessed_orders}, product_attributes)

        # Si el output del CSV es 1 (tiene solo el header), significa que no se ha añadido ningún producto.
        if len(csv_output.splitlines()) <= 1:
            return None, None, not_added_products, not_added_floor_length, not_added_missing_street_or_number

        # Define filename based on shop, date, and product
        date_str = datetime.now().strftime('%Y-%m-%d')
        file_name = f"{shop} - {date_str} - {product}.csv"

        # Mark each order as processed only if it's not marked as 'exclude'
        print('Marcando ordenes como procesadas')
        for order in unprocessed_orders:
            if not order.get('exclude', False):
                mark_order_as_processed(table_name, order["order_id"], order["item_id"])
        print('Ordenes marcadas como procesadas')

        print('Finalizado generación de CSV de ordenes no procesadas')
        return csv_output, file_name, not_added_products, not_added_floor_length, not_added_missing_street_or_number

    except Exception as e:
        raise Exception(f"Error en la función generate_unprocessed_orders_csv: {e}")
