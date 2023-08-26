import aiohttp
import asyncio

async def fetch_orders_for_store(session, shop_name, shop_url, access_token):
    endpoint = f"https://{shop_url}/admin/api/2022-01/orders.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    params = {
        'financial_status': 'paid',
        'fulfillment_status': 'unfulfilled',
    }
    
    async with session.get(endpoint, headers=headers, params=params) as response:
        orders = await response.json()

        orders_list = []
        for order in orders.get('orders', []):
            order_dict = {}
            order_dict['item'] = order['line_items'][0]['name']
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
        
        print(order_dict)
        return shop_name, orders_list

async def request_orders(credentials):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_orders_for_store(session, cred['shop_name'], cred['shop_url'], cred['access_token']) for cred in credentials]
        results = await asyncio.gather(*tasks)
        
    # Convert list of tuples to dictionary
    orders_by_store = {shop: orders for shop, orders in results}
    return orders_by_store
