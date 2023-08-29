from clean_text import clean_text

FAMILY_MAPPING = {
    # Add more mappings as needed
}


def filter_and_group_by_family(orders_by_shop):
    """
    Filters and groups orders by item families.
    :param orders_by_shop: Dictionary with shop names as keys and list of orders as values.
    :return: Dictionary with shop names as keys and orders grouped by families as values.
    """
    grouped_orders = {}
    for shop, orders in orders_by_shop.items():
        # Dictionary to hold orders grouped by family
        family_group = {}
        for order in orders:
            item_name = clean_text(order['item'])
            family = FAMILY_MAPPING.get(item_name, item_name)  # Use the item name as default if no family is found
            if family not in family_group:
                family_group[family] = []
            family_group[family].append(order)
        
        grouped_orders[shop] = family_group
    return grouped_orders
