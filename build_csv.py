import csv
from io import StringIO


def generate_csv_from_orders(grouped_orders):
    # Creamos un buffer en memoria para escribir el CSV
    output = StringIO()
    writer = csv.writer(output, delimiter=';')

    # Escribimos la cabecera del CSV
    headers = [
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
    writer.writerow(headers)

    # Valores ficticios para los campos que aún no hemos discutido
    tipo_producto = "CP"
    largo = 30
    ancho = 20
    altura = 10
    peso = 0.62
    valor_del_contenido = 1000
    
    # Iteramos sobre las órdenes agrupadas y escribimos cada línea del CSV
    for shop, items in grouped_orders.items():
        for family, orders in items.items():
            for order in orders:
                row = [
                    tipo_producto, largo, ancho, altura, peso, valor_del_contenido,
                    order["province_code"], "", order["city"], order["street"], order["number"],
                    order.get("apartment", ""), "", order["zip_code"], 
                    f"{order['first_name']} {order['last_name']}", order["email"], 
                    "", "", order["phone"][:2], order["phone"][2:]
                ]
                writer.writerow(row)
                
    # Regresamos el contenido del CSV como una cadena
    return output.getvalue()
