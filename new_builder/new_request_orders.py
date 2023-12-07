import requests
from datetime import datetime
from utils.utils import ApiException


def new_fetch_orders_for_store(shop_name, shop_url, access_token, date):
    try:
        print('Starting fetch_orders_for_store function')
        date = datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%dT%H:%M:%S%z')
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

        flag = True
        while flag:
            if response.headers.get('link'):
                params = {}

                # Usar el enlace con rel=next para obtener la página siguiente
                link_header = requests.utils.parse_header_links(response.headers.get('link'))
                next_link = link_header[0].get('next')
                if next_link:
                    endpoint = next_link['url']
                else:
                    flag = False # No hay más páginas

                response = requests.get(endpoint, headers=headers, params=params)

                # Check for errors
                if response.status_code != 200:
                    raise ApiException(f"Error fetching orders for {shop_name}: {response.text}")

                orders = response.json().get('orders', [])
                all_orders.extend(orders)
            else:
                flag = False

        all_orders_info = []

        for order in all_orders:
            order_dict = {}
            order_dict['first_name'] = order['shipping_address']['first_name']
            order_dict['last_name'] = order['shipping_address']['last_name']
            order_dict['street'] = order['shipping_address']['company']
            order_dict['number'] = order['shipping_address']['address1']
            order_dict['apartment'] = order['shipping_address']['address2']
            order_dict['city'] = order['shipping_address']['city']
            order_dict['province_code'] = order['shipping_address']['province_code']
            order_dict['country'] = order['shipping_address']['country']
            order_dict['zip_code'] = order['shipping_address']['zip']
            
            if not order['shipping_address']['phone']:
                order_dict['phone'] = '0'
            else:
                order_dict['phone'] = order['shipping_address']['phone']

            order_items = []  # Lista para almacenar los elementos de la orden

            for item in order.get('line_items', []):
                item_info = {
                    'item': item['name'],
                    'item_id': item['product_id'],
                    'order_id': order['id'],
                    'price': order['total_price'],
                    'quantity': item['quantity'],
                    'email': order['customer']['email']
                }
                order_items.append(item_info)

            order_dict['items'] = order_items  # Agregar la lista de elementos al diccionario principal
            all_orders_info.append(order_dict)  # Agregar el diccionario al listado de todas las órdenes

        print('Finished fetch_orders_for_store function')
        return all_orders_info

    except Exception as e:
        raise Exception(f"Error in fetch_orders_for_store function for {shop_name}: {e}")
