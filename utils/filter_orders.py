from utils.clean_text import clean_text


def filter_and_group_by_family(orders):
    """
    Filters and groups orders by item names.
    :param orders: List of orders.
    :return: Dictionary with orders grouped by item names.
    """
    try:
        print('Starting filter_and_group_by_family function')
        # Dictionary to hold orders grouped by item name
        family_group = {}
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

            # Iterate through items in the order
            for item in order['items']:
                if item['item_id'] not in family_group:
                    family_group[item['item_id']] = []

                # Append the order information to the list
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

        print('Finished filter_and_group_by_family function')
        return family_group

    except Exception as e:
        raise Exception(f"Error in filter_and_group_by_family function: {e}")
