from build_csv import generate_csv_from_orders
from utils import load_product_attributes
from dynamodb_cache import check_order_processed, mark_order_as_processed, get_or_create_table_name

from datetime import datetime


def generate_unprocessed_orders_csv(shop, product, grouped_data):
    try:
        # Ensure the DynamoDB table exists
        table_name = get_or_create_table_name(shop)

        # Check if the product exists in the grouped_data
        if product not in grouped_data:
            return None, None, [], [], []

        unprocessed_orders = []
        # Check if each order has been processed
        print('Checking if order has been processed')
        print('Grouped data', grouped_data)
        for order in grouped_data[product]:
            is_processed = check_order_processed(table_name, order["order_id"], order["item_id"])
            # If the order has not been processed, add it to the list
            if not is_processed:
                unprocessed_orders.append(order)
        print('Finished checking if order has been processed')

        print('Unprocessed orders', unprocessed_orders)

        # Si todas las órdenes ya han sido procesadas, devolver vacío.
        if not unprocessed_orders:
            print('Todas las ordenes ya han sido procesadas')
            return None, None, [], [], []

        # Cargar los atributos del producto
        product_attributes = load_product_attributes(shop)

        # Llamar a la función que genera el CSV a partir de las órdenes no procesadas pasando cada producto y sus órdenes y los atributos del producto
        print('Generando CSV')
        csv_output, not_added_products, not_added_floor_length, not_added_missing_street_or_number = generate_csv_from_orders({product: unprocessed_orders}, product_attributes)
        print('CSV generado')

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
