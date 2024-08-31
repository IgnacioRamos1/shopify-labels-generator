

def filter_and_group_by_family(orders):
    """
    Filters and groups orders by item names. Orders with multiple items are grouped under 'multiple_orders',
    while orders with a single item are grouped by the item ID.
    :param orders: List of orders.
    :return: Dictionary with orders grouped by item names and a separate group for orders with multiple items.
    """
    try:
        print('Starting filter_and_group_by_family function')
        # Dictionary to hold orders grouped by item name
        family_group = {}
        multiple_orders = []

        for order in orders:
            # Extracting customer information
            customer_info = {
                'first_name': order['first_name'],
                'last_name': order['last_name'],
                'street': order['street'],
                'number': order['number'],
                'apartment': order['apartment'],
                'city': order['city'],
                'province_code': order['province_code'],
                'country': order['country'],
                'zip_code': order['zip_code'],
                'phone': order['phone'],
            }

            # Check if the order contains multiple items
            if len(order['items']) > 1:
                # Append to the multiple_orders list
                for item in order['items']:
                    order_info = {
                        'item': item['item'],
                        'item_id': item['item_id'],
                        'order_id': item['order_id'],
                        'price': item['price'],
                        'quantity': item['quantity'],
                        'email': item['email'],
                        **customer_info,  # Include customer information in the order details
                    }
                    multiple_orders.append(order_info)
            else:
                # Single item orders
                item = order['items'][0]
                if item['item_id'] not in family_group:
                    family_group[item['item_id']] = []

                order_info = {
                    'item': item['item'],
                    'item_id': item['item_id'],
                    'order_id': item['order_id'],
                    'price': item['price'],
                    'quantity': item['quantity'],
                    'email': item['email'],
                    **customer_info,  # Include customer information in the order details
                }

                family_group[item['item_id']].append(order_info)

        # Add the multiple orders group to the dictionary
        if multiple_orders:
            family_group['multiple_orders'] = multiple_orders

        print('Finished filter_and_group_by_family function')
        return family_group

    except Exception as e:
        raise Exception(f"Error in filter_and_group_by_family function: {e}")
