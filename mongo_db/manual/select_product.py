import sys
import os
sys.path.append(os.path.abspath('..'))

from database import Database


def select_product(store_id):
    database = Database.get_instance()
    store = database.get_store(store_id)
    print('Select a product:')
    print('---------------------------------')
    for i, product in enumerate(store['products']):
        print(f"{i + 1}. {product['name']}")
    print('---------------------------------')
    product_number = int(input('Enter the number of the product: '))
    print('---------------------------------')

    # We are returning the product object
    return store['products'][product_number - 1]

