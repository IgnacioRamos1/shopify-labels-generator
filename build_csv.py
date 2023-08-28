import pandas as pd
from clean_text import clean_text, clean_phone


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
        for orders in items.values():
            for order in orders:
                # Get the attributes for the current order from the JSON data
                attributes = product_attributes.get(str(order['item_id']))
                if not attributes:
                    print(f'No attributes found for item {clean_text(order["item"])}')
                    continue
                row_data = {
                    "tipo_producto(obligatorio)": attributes["tipo_producto"],
                    "largo(obligatorio en CM)": attributes["largo"] * order["quantity"],
                    "ancho(obligatorio en CM)": attributes["ancho"] * order["quantity"],
                    "altura(obligatorio en CM)": attributes["alto"] * order["quantity"],
                    "peso(obligatorio en KG)": attributes["peso"] * order["quantity"],
                    "valor_del_contenido(obligatorio en pesos argentinos": attributes["precio"] * order["quantity"],

                    "provincia_destino(obligatorio)": order["province_code"],
                    "sucursal_destino(obligatorio solo en caso de no ingresar localidad de destino)": "",

                    "localidad_destino(obligatorio solo en caso de no ingresar sucursal de destino)": clean_text(order["city"]),
                    "calle_destino(obligatorio solo en caso de no ingresar sucursal de destino)": clean_text(order["street"]),
                    "altura_destino(obligatorio solo en caso de no ingresar sucursal de destino)": order["number"],
                    "piso(opcional solo en caso de no ingresar sucursal de destino)": clean_text(order.get("apartment", "")),
                    "dpto(opcional solo en caso de no ingresar sucursal de destino)": "",

                    "codpostal_destino(obligatorio solo en caso de no ingresar sucursal de destino)": order["zip_code"],
                    "destino_nombre(obligatorio)": clean_text(f"{order['first_name']} {order['last_name']}"),

                    "destino_email(obligatorio debe ser un email valido)": order["email"],
                    "cod_area_tel(opcional)": "",
                    "tel(opcional)": "",
                    "cod_area_cel(obligatorio)": "54",
                    "cel(obligatorio)": clean_phone(order["phone"])
                }
                formatted_data.loc[len(formatted_data)] = row_data

    # Convert the DataFrame to CSV format
    output = formatted_data.to_csv(index=False, sep=';')
    return output
