import pandas as pd
from clean_text import clean_text, clean_phone, clean_zip_code
from fix_postal_code import correct_province_by_postal_code


def generate_csv_from_orders(grouped_orders, product_attributes):
    columns = [
        "tipo_producto(obligatorio)", "largo(obligatorio en CM)", "ancho(obligatorio en CM)", 
        "altura(obligatorio en CM)", "peso(obligatorio en KG)", "valor_del_contenido(obligatorio en pesos argentinos)",
        "provincia_destino(obligatorio)", "sucursal_destino(obligatorio solo en caso de no ingresar localidad de destino)",
        "localidad_destino(obligatorio solo en caso de no ingresar sucursal de destino)", 
        "calle_destino(obligatorio solo en caso de no ingresar sucursal de destino)", 
        "altura_destino(obligatorio solo en caso de no ingresar sucursal de destino)", 
        "piso(opcional solo en caso de no ingresar sucursal de destino)", 
        "dpto(opcional solo en caso de no ingresar sucursal de destino)", 
        "codpostal_destino(obligatorio solo en caso de no ingresar sucursal de destino)", 
        "destino_nombre(obligatorio)", "destino_email(obligatorio debe ser un email valido)", 
        "cod_area_tel(opcional)", "tel(opcional)", "cod_area_cel(obligatorio)", "cel(obligatorio)"
    ]

    not_added_products = []
    formatted_data = pd.DataFrame(columns=columns)
    for items in grouped_orders.values():
        if not items:
            continue

        for orders in items.values():
            for order in orders:
                # Check if street or number is missing
                if not clean_text(order.get("street")) or not clean_text(order.get("number")):
                    reason = "Missing street" if not order.get("street") else "Missing street number"
                    product = {
                        'item': clean_text(order['item']),
                        'item_id': order['item_id'],
                        'order_id': order['order_id'],
                        'reason': reason
                    }
                    not_added_products.append(product)
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
                    order['exclude'] = True
                    continue
                
                # Check if the product name matches the JSON
                attributes = next((attr for attr in attributes_list if attr['nombre'] == clean_text(order['item'])), None)
                if not attributes:
                    reason = "No matching attribute found for product name"
                    product = {
                        'item': clean_text(order['item']),
                        'item_id': order['item_id'],
                        'order_id': order['order_id'],
                        'reason': reason
                    }
                    not_added_products.append(product)
                    order['exclude'] = True
                    continue

                row_data = {
                    "tipo_producto(obligatorio)": attributes["tipo_producto"],
                    "largo(obligatorio en CM)": round(attributes["largo"] * order["quantity"], 2),
                    "ancho(obligatorio en CM)": round(attributes["ancho"] * order["quantity"], 2),
                    "altura(obligatorio en CM)": round(attributes["alto"] * order["quantity"], 2),
                    "peso(obligatorio en KG)": round(attributes["peso"] * order["quantity"], 2),
                    "valor_del_contenido(obligatorio en pesos argentinos)": round(attributes["precio"] * order["quantity"], 2),
                    "provincia_destino(obligatorio)": correct_province_by_postal_code(order["province_code"],clean_zip_code(order["zip_code"])),
                    "sucursal_destino(obligatorio solo en caso de no ingresar localidad de destino)": "",
                    "localidad_destino(obligatorio solo en caso de no ingresar sucursal de destino)": clean_text(order["city"]),
                    "calle_destino(obligatorio solo en caso de no ingresar sucursal de destino)": clean_text(order["street"]),
                    "altura_destino(obligatorio solo en caso de no ingresar sucursal de destino)": clean_text(str(order["number"])),
                    "piso(opcional solo en caso de no ingresar sucursal de destino)": clean_text(order.get("apartment", "")),
                    "dpto(opcional solo en caso de no ingresar sucursal de destino)": "",
                    "codpostal_destino(obligatorio solo en caso de no ingresar sucursal de destino)": clean_zip_code(order["zip_code"]),
                    "destino_nombre(obligatorio)": clean_text(f"{order['first_name']} {order['last_name']}"),
                    "destino_email(obligatorio debe ser un email valido)": order["email"],
                    "cod_area_tel(opcional)": "",
                    "tel(opcional)": "",
                    "cod_area_cel(obligatorio)": "54",
                    "cel(obligatorio)": clean_phone(order["phone"])
                }
                formatted_data.loc[len(formatted_data)] = row_data

    output = formatted_data.to_csv(index=False, sep=';')
    return output, not_added_products
