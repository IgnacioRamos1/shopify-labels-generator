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
            item_name = clean_text(order['item'])
            if item_name not in family_group:
                # If the item name is not in the dictionary, add it and initialize it as an empty list
                family_group[item_name] = []

            # Append the order to the list
            family_group[item_name].append(order)

        print('Finished filter_and_group_by_family function')

        return family_group

    except Exception as e:
        raise Exception(f"Error in filter_and_group_by_family function: {e}")
