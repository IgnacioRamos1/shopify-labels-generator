import pandas as pd
from utils.clean_text import clean_text, clean_phone, clean_zip_code, clean_email
from fixy_builder.fix_postal_code_for_fixy import correct_province_by_postal_code_for_fixy


def generate_csv_from_orders_for_oca(grouped_orders, product_attributes):
    print('generando csv para OCA')
    try:
        columns = [
            "Destinatario - Apellido",
            "Destinatario - Nombre",
            "Destinatario - TipoDocumento",
            "Destinatario - Documento",
            "Destinatario - Calle",
            "Destinatario - Número",
            "Destinatario - Piso",
            "Destinatario - Depto.",
            "Destinatario - Código Postal",
            "Destinatario - Localidad",
            "Destinatario - Provincia",
            "Destinatario - Teléfono",
            "Destinatario - Email",
            "Paquete - Cantidad",
            "Paquete - Peso [kg]",
            "Paquete - Alto [cm]",
            "Paquete - Largo [cm]",
            "Paquete - Ancho [cm]",
            "Valor Asegurado",
            "Número de Operativa",
            "Número de Remito",
            "Observaciones"
        ]
        not_added_floor_length = []
        not_added_missing_street_or_number = []
        not_added_products = []
        formatted_data = pd.DataFrame(columns=columns)
        # Iterate over each product and its orders
        for product_id, orders in grouped_orders.items():
            # Iterate over each order
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

                # Check for floor value length
                floor_length = len(clean_text(order.get("apartment", "")))
                if floor_length > 3:
                    reason = f"Demasiados caracteres en el piso ({floor_length})"
                    product = {
                        'item': clean_text(order['item']),
                        'person': clean_text(f"{order['first_name']} {order['last_name']}"),
                        'reason': reason
                    }
                    not_added_floor_length.append(product)
                    # No continuamos porque queremos que se corrija manualmente el piso, por lo tanto lo agregamos al CSV

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
                    # Check if the product name matches the JSON
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

                        # Mark all orders for this product as 'exclude'
                        for single_order in grouped_orders[product['item_id']]:
                            single_order['exclude'] = True
                        continue

                row_data = {
                    "Destinatario - Apellido": clean_text(order.get("last_name")),
                    "Destinatario - Nombre": clean_text(order.get("first_name")),
                    "Destinatario - TipoDocumento": "",
                    "Destinatario - Documento": "",
                    "Destinatario - Calle": clean_text(order.get("street")),
                    "Destinatario - Número": clean_text(str(order["number"])),
                    "Destinatario - Piso": clean_text(order.get("apartment", "")),
                    "Destinatario - Depto.": "",
                    "Destinatario - Código Postal": clean_zip_code(order.get("zip_code")),
                    "Destinatario - Localidad": clean_text(order.get("city")),
                    "Destinatario - Provincia": correct_province_by_postal_code_for_fixy(order["province_code"], clean_zip_code(order["zip_code"])),
                    "Destinatario - Teléfono": clean_phone(order.get("phone")),
                    "Destinatario - Email": clean_email(order.get("email")),
                    "Paquete - Cantidad": order.get("quantity"),
                    "Paquete - Peso [kg]": round(attributes.get("weight") * order.get("quantity"), 2),
                    "Paquete - Alto [cm]": round(attributes.get("height") * order.get("quantity"), 2),
                    "Paquete - Largo [cm]": round(attributes.get("length") * order.get("quantity"), 2),
                    "Paquete - Ancho [cm]": round(attributes.get("width") * order.get("quantity"), 2),
                    "Valor Asegurado": "",
                    "Número de Operativa": "422039",
                    "Número de Remito": order.get("order_number"),
                    "Observaciones": round(attributes["price"] * order["quantity"], 2)
                }

                # Add the row to the DataFrame
                formatted_data.loc[len(formatted_data)] = row_data

        output = formatted_data.to_csv(index=False, sep=';')

        for product_id, orders in grouped_orders.items():
            for order in orders:
                product_name = f"{clean_text(order['item'])}"
                break
            break
        
        return output, not_added_products, not_added_floor_length, not_added_missing_street_or_number, product_name

    except Exception as e:
        raise Exception(f"Error in generate_csv_from_orders function: {e}")
