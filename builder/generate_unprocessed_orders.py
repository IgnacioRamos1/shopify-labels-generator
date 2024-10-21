from builder.build_csv import generate_csv_from_orders
from builder.build_oca_csv import generate_csv_from_orders_for_oca
from fixy_builder.build_fixy_csv import generate_csv_from_orders_for_fixy
from dynamo_db.dynamodb_cache import check_order_processed, mark_order_as_processed, get_or_create_table_name

from utils.get_all_products import get_all_products_for_store
from utils.clean_text import clean_text

from datetime import datetime


def generate_unprocessed_orders_csv(store, product_id, grouped_data):
    try:
        table_name = get_or_create_table_name(store["name"])

        if product_id == "multiple_orders":
            unprocessed_orders = []
            for order in grouped_data[product_id]:
                is_processed = check_order_processed(table_name, order["order_id"], order["item_id"])
                if not is_processed:
                    unprocessed_orders.append(order)
            product_name = "Multiple Orders"
        else:
            if product_id not in grouped_data:
                return [], [], [], [], "Unknown Product"

            unprocessed_orders = []
            for order in grouped_data[product_id]:
                if order["item_id"]:
                    is_processed = check_order_processed(table_name, order["order_id"], order["item_id"])
                    if not is_processed:
                        unprocessed_orders.append(order)
                else:
                    continue
            product_name = clean_text(grouped_data[product_id][0]['item']) if grouped_data[product_id] else "Unknown Product"

        if not unprocessed_orders:
            return [], [], [], [], product_name

        if store["type"] == "Fixy":
            order_groups = [unprocessed_orders]
        else:
            order_groups = [unprocessed_orders[i:i + 60] for i in range(0, len(unprocessed_orders), 60)]

        product_attributes = get_all_products_for_store(store)

        outputs = []
        not_added_products = []
        not_added_floor_length = []
        not_added_missing_street_or_number = []
        print('type', store["type"])

        for index, orders_group in enumerate(order_groups):
            if store["type"] == "Fixy":
                csv_output, multiple_orders_output, _not_added_products, _not_added_floor_length, _not_added_missing_street_or_number, product_name = generate_csv_from_orders_for_fixy(
                    {product_id: orders_group},
                    product_attributes,
                    store["fixy_service_id"],
                    store["fixy_client_id"],
                    store["fixy_branch_code"],
                    store["fixy_company"],
                    store["fixy_sender"]
                )
            elif store["type"] == "Oca":
                print('entre a oca')
                csv_output, _not_added_products, _not_added_floor_length, _not_added_missing_street_or_number, product_name = generate_csv_from_orders_for_oca(
                    {product_id: orders_group},
                    product_attributes
                )
                multiple_orders_output = ""
            else:
                print('entre a otros')
                csv_output, _not_added_products, _not_added_floor_length, _not_added_missing_street_or_number, product_name = generate_csv_from_orders(
                    {product_id: orders_group},
                    product_attributes
                )
                multiple_orders_output = ""

            not_added_products.extend(_not_added_products)
            not_added_floor_length.extend(_not_added_floor_length)
            not_added_missing_street_or_number.extend(_not_added_missing_street_or_number)

            if len(csv_output.splitlines()) > 1:
                date_str = datetime.now().strftime('%Y-%m-%d')
                file_name = f"{store['name']} - {date_str} - {product_name} - {index + 1}.csv"
                outputs.append((csv_output, file_name))

            if multiple_orders_output and len(multiple_orders_output.splitlines()) > 1:
                date_str = datetime.now().strftime('%Y-%m-%d')
                file_name = f"{store['name']} - {date_str} - Multiple Orders - {index + 1}.csv"
                outputs.append((multiple_orders_output, file_name))

            for order in orders_group:
                if not order.get('exclude', False):
                    mark_order_as_processed(table_name, order["order_id"], order["item_id"])

        return outputs, not_added_products, not_added_floor_length, not_added_missing_street_or_number, product_name

    except Exception as e:
        raise Exception(f"Error in generate_unprocessed_orders_csv function: {e}")
