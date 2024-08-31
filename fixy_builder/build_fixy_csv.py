import pandas as pd
from utils.clean_text import clean_text, clean_zip_code, clean_email
from .fixy_clean_text import fixy_clean_phone
from .fix_postal_code_for_fixy import correct_province_by_postal_code_for_fixy


def generate_csv_from_orders_for_fixy(grouped_orders, product_attributes, fixy_service_id, fixy_client_id, fixy_branch_code, fixy_company, fixy_sender):
    try:
        columns = [
            "productos.descripcion",
            "caja",
            "tipo_operacion",
            "sector",
            "cliente_id",
            "servicio_id",
            "codigo_sucursal",
            "datosEnvios.pago_en",
            "datosEnvios.valor_declarado",
            "datosEnvios.contrareembolso",
            "datosEnvios.confirmada",
            "trabajo",
            "remito",
            "sender.empresa",
            "sender.remitente",
            "sender.calle",
            "sender.altura",
            "sender.localidad",
            "sender.provincia",
            "sender.cp",
            "comprador.apellido_nombre",
            "comprador.calle",
            "comprador.altura",
            "comprador.piso",
            "comprador.dpto",
            "comprador.localidad",
            "comprador.provincia",
            "comprador.cp",
            "comprador.celular",
            "comprador.email",
            "comprador.other_info",
            "comprador.fecha_servicio",
            "comprador.hora_desde",
            "comprador.hora_hasta",
            "comprador.obs1",
            "datosEnvios.bultos",
            "datosEnvios.peso",
            "datosEnvios.observaciones",
            "datosEnvios.guiaAgente",
        ]

        not_added_floor_length = []
        not_added_missing_street_or_number = []
        not_added_products = []
        formatted_data = pd.DataFrame(columns=columns)
        multiple_orders_data = pd.DataFrame(columns=columns)

        order_counter = 0

        # Iterate over each product and its orders
        for product_id, orders in grouped_orders.items():
            for order in orders:
                # Check if street or number is missing
                if not clean_text(order.get("street")) or not clean_text(order.get("number")):
                    reason = "Missing street *(NOT ADDED)*" if not order.get("street") else "Missing street number *(NOT ADDED)*"
                    product = {
                        'item': clean_text(order['item']),
                        'person': clean_text(f"{order['first_name']} {order['last_name']}"),
                        'reason': reason
                    }
                    not_added_missing_street_or_number.append(product)
                    order['exclude'] = True
                    continue

                # Check if the product is in the JSON
                attributes_list = product_attributes.get(str(order['item_id']))
                if not attributes_list:
                    reason = "No attributes found in JSON file"
                    product = {
                        'item': clean_text(order['item']),
                        'item_id': order['item_id'],
                        'order_id': order['order_id'],
                        'reason': reason
                    }
                    not_added_products.append(product)
                    # Mark all orders for this product as 'exclude'
                    for single_order in grouped_orders[product['item_id']]:
                        single_order['exclude'] = True
                    continue

                if len(attributes_list) == 1:
                    attributes = attributes_list[0]
                else:
                    attributes = next((attr for attr in attributes_list if attr['name'] == clean_text(order['item'])), None)
                    if not attributes:
                        reason = "No matching attribute found for product name"
                        product = {
                            'item': clean_text(order['item']),
                            'item_id': order['item_id'],
                            'order_id': order['order_id'],
                            'reason': reason
                        }
                        not_added_products.append(product)
                        for single_order in grouped_orders[product['item_id']]:
                            single_order['exclude'] = True
                        continue

                order_counter += 1

                # Prepare the row for a single product
                row_data = {
                    "tipo_operacion": "ENTREGA",
                    "sector": "OP",
                    "cliente_id": fixy_client_id,
                    "servicio_id": fixy_service_id,
                    "codigo_sucursal": fixy_branch_code,
                    "datosEnvios.pago_en": "ORIGEN",
                    "datosEnvios.valor_declarado": round(attributes["price"] * order["quantity"], 2),
                    "datosEnvios.confirmada": "1",
                    "trabajo": "",
                    "remito": "",
                    "sender.empresa": fixy_company,
                    "sender.remitente": fixy_sender,
                    "sender.calle": "Albarellos",
                    "sender.altura": "1916",
                    "sender.localidad": "MARTINEZ",
                    "sender.provincia": "BUENOS AIRES",
                    "sender.cp": "1640",
                    "comprador.apellido_nombre": clean_text(f"{order['last_name']} {order['first_name']}"),
                    "comprador.calle": clean_text(order["street"]),
                    "comprador.altura": clean_text(str(order["number"])),
                    "comprador.dpto": "",
                    "comprador.localidad": clean_text(order["city"]),
                    "comprador.provincia": correct_province_by_postal_code_for_fixy(order["province_code"], clean_zip_code(order["zip_code"])),
                    "comprador.cp": clean_zip_code(order["zip_code"]),
                    "comprador.celular": fixy_clean_phone(order["phone"]),
                    "comprador.email": clean_email(order["email"]),
                    "comprador.fecha_servicio": "",
                    "comprador.hora_desde": "",
                    "comprador.hora_hasta": "",
                    "comprador.obs1": "",
                    "datosEnvios.bultos": "1",
                    "datosEnvios.peso": round(attributes["weight"] * order["quantity"], 2),
                    "datosEnvios.observaciones": "",
                    "datosEnvios.guiaAgente": order_counter,
                    "datosEnvios.contrareembolso": (order["price"]).split(".")[0],
                }

                apartment = clean_text(order.get("apartment", ""))
                if len(apartment) > 3:
                    row_data["comprador.other_info"] = apartment
                    row_data["comprador.piso"] = ""
                else:
                    row_data["comprador.other_info"] = ""
                    row_data["comprador.piso"] = apartment

                # Add the row to the single-product DataFrame
                formatted_data.loc[len(formatted_data)] = row_data

                # Handle multiple orders for the same buyer
                buyer_orders = multiple_orders_data[
                    (multiple_orders_data['comprador.apellido_nombre'] == row_data['comprador.apellido_nombre']) &
                    (multiple_orders_data['comprador.calle'] == row_data['comprador.calle']) &
                    (multiple_orders_data['comprador.altura'] == row_data['comprador.altura'])
                ]

                if not buyer_orders.empty:
                    # If there are existing orders for the buyer, update the existing row
                    existing_index = buyer_orders.index[0]
                    multiple_orders_data.at[existing_index, 'datosEnvios.peso'] = round(
                        multiple_orders_data.at[existing_index, 'datosEnvios.peso'] + row_data['datosEnvios.peso'],
                        2
                    )
                    multiple_orders_data.at[existing_index, 'datosEnvios.observaciones'] += f", {order['item']}"
                else:
                    # Otherwise, add a new row for the buyer
                    row_data['datosEnvios.observaciones'] = order['item']
                    multiple_orders_data.loc[len(multiple_orders_data)] = row_data

        # Convert DataFrames to CSV strings
        single_product_output = formatted_data.to_csv(index=False, sep=';')
        multiple_orders_output = multiple_orders_data.to_csv(index=False, sep=';')

        for product_id, orders in grouped_orders.items():
            for order in orders:
                product_name = f"{clean_text(order['item'])}"
                break
            break

        return single_product_output, multiple_orders_output, not_added_products, not_added_floor_length, not_added_missing_street_or_number, product_name

    except Exception as e:
        raise Exception(f"Error in generate_csv_from_orders function: {e}")
