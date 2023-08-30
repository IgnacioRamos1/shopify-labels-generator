import pandas as pd
from clean_text import clean_text, clean_phone, clean_zip_code
from fix_postal_code import correct_province_by_postal_code


def generate_csv_from_orders(grouped_orders, product_attributes):
# Define the columns
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

    # Create an empty DataFrame
    formatted_data = pd.DataFrame(columns=columns)

    # Populate the DataFrame
    for items in grouped_orders.values():
        # If item is empty, skip
        if not items:
            continue

        for orders in items.values():
            for order in orders:
                try:
                    # Get the list of attributes for the current order from the JSON data
                    attributes_list = product_attributes.get(str(order['item_id']))
                    if not attributes_list:
                        print(f'No attributes found for item {clean_text(order["item"])}')
                        continue

                    # Find the correct attributes by matching product name
                    attributes = next((attr for attr in attributes_list if attr['nombre'] == clean_text(order['item'])), None)
                    if not attributes:
                        print(f'No matching attribute found for item {clean_text(order["item"])}')
                        continue

                    row_data = {
                        "tipo_producto(obligatorio)": attributes["tipo_producto"],
                        "largo(obligatorio en CM)": attributes["largo"] * order["quantity"],
                        "ancho(obligatorio en CM)": attributes["ancho"] * order["quantity"],
                        "altura(obligatorio en CM)": attributes["alto"] * order["quantity"],
                        "peso(obligatorio en KG)": attributes["peso"] * order["quantity"],
                        "valor_del_contenido(obligatorio en pesos argentinos)": attributes["precio"] * order["quantity"],

                        "provincia_destino(obligatorio)": correct_province_by_postal_code(order["province_code"],clean_zip_code( order["zip_code"])),
                        "sucursal_destino(obligatorio solo en caso de no ingresar localidad de destino)": "",

                        "localidad_destino(obligatorio solo en caso de no ingresar sucursal de destino)": clean_text(order["city"]),
                        "calle_destino(obligatorio solo en caso de no ingresar sucursal de destino)": clean_text(order["street"]),
                        "altura_destino(obligatorio solo en caso de no ingresar sucursal de destino)": order["number"],
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
                except Exception as e:
                    print(f"Error processing order {order['order_id']} for item {order['item_id']}: {str(e)}")


    # Convert the DataFrame to CSV format
    output = formatted_data.to_csv(index=False, sep=';')
    return output
