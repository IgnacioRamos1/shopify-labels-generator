from builder.build_csv import generate_csv_from_orders
from fixy_builder.build_fixy_csv import generate_csv_from_orders_for_fixy
from dynamo_db.dynamodb_cache import check_order_processed, mark_order_as_processed, get_or_create_table_name

from utils.get_all_products import get_all_products_for_store

from datetime import datetime


def generate_unprocessed_orders_csv(store, product, grouped_data):
    try:
        # Ensure the DynamoDB table exists
        table_name = get_or_create_table_name(store["name"])

        # Check if the product exists in the grouped_data
        if product not in grouped_data:
            return [], [], [], []

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
            return [], [], [], []

        # Solo dividir a las órdenes en grupos de 60 si no son Fixy
        if store["fixy"] == "True":
            order_groups = [unprocessed_orders]  # Procesa todas las órdenes juntas para Fixy
        else:
            print('Dividiendo ordenes en grupos de 60')
            order_groups = [unprocessed_orders[i:i + 60] for i in range(0, len(unprocessed_orders), 60)]
        # Cargar los atributos del producto
        product_attributes = get_all_products_for_store(store)

        outputs = []
        not_added_products = []
        not_added_floor_length = []
        not_added_missing_street_or_number = []

        for index, orders_group in enumerate(order_groups):
            if store["fixy"] == "True":
                print('Generando CSV v2.0 de ordenes no procesadas')
                csv_output, _not_added_products, _not_added_floor_length, _not_added_missing_street_or_number = generate_csv_from_orders_for_fixy(
                    {product: orders_group},
                    product_attributes,
                    store["fixy_service_id"],
                    store["fixy_client_id"],
                    store["fixy_branch_code"],
                    store["fixy_company"],
                    store["fixy_sender"]
                )
            else:
                print('Generando CSV de ordenes no procesadas')
                csv_output, _not_added_products, _not_added_floor_length, _not_added_missing_street_or_number = generate_csv_from_orders(
                    {product: orders_group},
                    product_attributes
                )

            # Actualizar las listas independientemente de si el CSV se va a generar o no.
            not_added_products.extend(_not_added_products)
            not_added_floor_length.extend(_not_added_floor_length)
            not_added_missing_street_or_number.extend(_not_added_missing_street_or_number)

            # Verificar si se debería continuar para generar un archivo CSV.
            if len(csv_output.splitlines()) > 1:
                date_str = datetime.now().strftime('%Y-%m-%d')
                file_name = f"{store['name']} - {date_str} - {product} - {index + 1}.csv"
                outputs.append((csv_output, file_name))

            # Mark each order as processed only if it's not marked as 'exclude'
            print('Marcando ordenes como procesadas')
            for order in orders_group:
                if not order.get('exclude', False):
                    mark_order_as_processed(table_name, order["order_id"], order["item_id"])
            print('Ordenes marcadas como procesadas')

        print('Finalizado generación de CSV de ordenes no procesadas')
        return outputs, not_added_products, not_added_floor_length, not_added_missing_street_or_number

    except Exception as e:
        raise Exception(f"Error en la función generate_unprocessed_orders_csv: {e}")

