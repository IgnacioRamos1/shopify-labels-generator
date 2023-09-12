import requests
from datetime import datetime
from utils.utils import ApiException


def fetch_orders_for_store(shop_name, shop_url, access_token, date):
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

        all_orders = []
        # Loop through all pages of orders
        all_orders = []
        while endpoint:
            response = requests.get(endpoint, headers=headers, params=params)

            # Check for errors
            if response.status_code != 200:
                raise ApiException(f"Error fetching orders for {shop_name}: {response.text}")

            orders = response.json().get('orders', [])
            all_orders.extend(orders)

            # Check for the next page link
            link_header = response.headers.get('Link', '')
            if 'rel="next"' in link_header:
                print('Fetching next page')
                # Extract the URL for the next page
                endpoint = link_header.split(';')[0].strip('<>')
                # Clear out the params since the next page URL already contains all the necessary information
                params = {}
            else:
                print('No more pages')
                endpoint = None

        orders_list = []
        print('Building orders list')
        for order in all_orders:
            for item in order.get('line_items', []):
                order_dict = {}
                order_dict['item'] = item['name']
                order_dict['item_id'] = item['product_id']
                order_dict['order_id'] = order['id']
                order_dict['quantity'] = item['quantity']
                order_dict['first_name'] = order['customer']['default_address']['first_name']
                order_dict['last_name'] = order['customer']['default_address']['last_name']
                order_dict['email'] = order['customer']['email']
                order_dict['street'] = order['customer']['default_address']['company']
                order_dict['number'] = order['customer']['default_address']['address1']
                order_dict['apartment'] = order['customer']['default_address']['address2']
                order_dict['city'] = order['customer']['default_address']['city']
                order_dict['province_code'] = order['customer']['default_address']['province_code']
                order_dict['country'] = order['customer']['default_address']['country']
                order_dict['zip_code'] = order['customer']['default_address']['zip']
                order_dict['phone'] = order['customer']['default_address']['phone']
                orders_list.append(order_dict)
        print('Finished building orders list')
        return orders_list

    except Exception as e:
        raise Exception(f"Error in fetch_orders_for_store function for {shop_name}: {e}")
