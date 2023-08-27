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

    # Valores ficticios para los campos que aún no hemos discutido
    tipo_producto = "CP"
    largo = 30
    ancho = 20
    altura = 10
    peso = 0.62
    valor_del_contenido = 1000

    # Populate the DataFrame
    for items in grouped_orders.values():
        for orders in items.values():
            for order in orders:
                # Get the attributes for the current order from the JSON data
                attributes = product_attributes.get(clean_text(order['item']))
                if not attributes:
                    print(f"Original: {repr(order['item'])}")
                    print(f"Cleaned: {repr(clean_text(order['item']))}")
                    continue

                row_data = {
                    "tipo_producto(obligatorio)": attributes.get("tipo_producto", tipo_producto),
                    "largo(obligatorio en CM)": attributes.get("largo", largo) * order["quantity"],
                    "ancho(obligatorio en CM)": attributes.get("ancho", ancho) * order["quantity"],
                    "altura(obligatorio en CM)": attributes.get("altura", altura) * order["quantity"],
                    "peso(obligatorio en KG)": attributes.get("peso", peso) * order["quantity"],
                    "valor_del_contenido(obligatorio en pesos argentinos": attributes.get("precio", valor_del_contenido) * order["quantity"],

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
