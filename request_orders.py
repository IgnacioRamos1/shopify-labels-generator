import requests
from datetime import datetime


def fetch_orders_for_store(shop_name, shop_url, access_token, date):
    try:
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
        }

        response = requests.get(endpoint, headers=headers, params=params)
        orders = response.json()

        orders_list = []
        for order in orders.get('orders', []):
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

        return shop_name, orders_list

    except Exception as e:
        raise Exception(f"Error in fetch_orders_for_store function for {shop_name}: {e}")


def request_orders(credentials):
    try:
        shop_orders = fetch_orders_for_store(credentials['shop_name'], credentials['shop_url'], credentials['access_token'], credentials['date'])

        # Return all orders for the shop
        return shop_orders[1]

    except Exception as e:
        raise Exception(f"Error in request_orders function: {e}")
