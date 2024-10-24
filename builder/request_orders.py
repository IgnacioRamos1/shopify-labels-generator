import requests
from utils.utils import ApiException
import re


def fetch_orders_for_store(shop_name, shop_url, access_token, date):
    try:
        print('Starting fetch_orders_for_store function')
        date = date.strftime('%Y-%m-%dT%H:%M:%S%z')
        endpoint = f"https://{shop_url}/admin/api/2022-01/orders.json"
        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
        params = {
            'financial_status': 'paid',
            'fulfillment_status': 'unfulfilled',
            'created_at_min': date,
            'limit': 250,
        }

       # Loop through all pages of orders
        all_orders = []
        response = requests.get(endpoint, headers=headers, params=params)

        orders = response.json().get('orders', [])
        all_orders.extend(orders)

        if response.status_code != 200:
            raise ApiException(f"Error fetching orders for {shop_name}: {response.text}")
        if not orders:
            return None        

        while True:
            if response.headers.get('link'):
                # Obtener el encabezado link de la respuesta
                link_header = response.headers.get('link')

                # Usar una expresión regular para buscar el enlace con el atributo rel=next
                next_link = re.search(r'<(.*?)>; rel="next"', link_header)

                # Si hay un enlace con el atributo rel=next, obtener la URL
                if next_link:
                    next_url = next_link.group(1)

                    # Usar la URL de la página siguiente para hacer la solicitud
                    response = requests.get(next_url, headers=headers)

                    # Check for errors
                    if response.status_code != 200:
                        raise ApiException(f"Error fetching orders for {shop_name}: {response.text}")

                    orders = response.json().get('orders', [])
                    all_orders.extend(orders)
                else:
                    break # No hay más páginas
            else:
                break

        all_orders_info = []
        error_counter = 0

        print(all_orders[0])

        for order in all_orders:
            try:
                order_dict = {}
                shipping_address = order.get('shipping_address', {})
                customer = order.get('customer', {})

                if not shipping_address or not customer:
                    error_counter += 1
                    print(f"Error procesando el pedido {order.get('id', 'Desconocido')}: falta información de dirección o cliente")
                    continue
                
                order_dict['first_name'] = customer.get('first_name', '')
                order_dict['last_name'] = customer.get('last_name', '')
                order_dict['street'] = shipping_address.get('company', '')
                order_dict['number'] = shipping_address.get('address1', '')
                order_dict['apartment'] = shipping_address.get('address2', '')
                order_dict['city'] = shipping_address.get('city', '')
                order_dict['province_code'] = shipping_address.get('province_code', '')
                order_dict['country'] = shipping_address.get('country', '')
                order_dict['zip_code'] = shipping_address.get('zip', '')
                
                if not order['shipping_address'].get('phone'):
                    order_dict['phone'] = '0'
                else:
                    order_dict['phone'] = order['shipping_address']['phone']

                order_items = []  # Lista para almacenar los elementos de la orden

                for item in order.get('line_items', []):
                    item_info = {
                        'item': item['name'],
                        'item_id': item.get('product_id', ''),
                        'order_id': order['id'],
                        'price': order['total_price'],
                        'quantity': item['quantity'],
                        'email': order['customer']['email'] if order.get('customer') else '',
                    }
                    order_items.append(item_info)
                order_dict['order_number'] = order.get('order_number', '')

                order_dict['items'] = order_items  # Agregar la lista de elementos al diccionario principal
                all_orders_info.append(order_dict)  # Agregar el diccionario al listado de todas las órdenes
            
            except KeyError as e:
                error_counter += 1
                print(f"Error procesando el pedido {order.get('id', 'Desconocido')}: falta la clave {e}")

        print(f"Total errors: {error_counter}")
        print('Finished fetch_orders_for_store function')
        return all_orders_info

    except Exception as e:
        raise Exception(f"Error in fetch_orders_for_store function for {shop_name}: {e}")
