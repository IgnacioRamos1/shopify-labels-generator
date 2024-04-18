import sys
import os
sys.path.append(os.path.abspath('..'))

from database import Database
from select_store import select_store


def add_new_product(database):
    store = select_store()
    
    choice = str(input('Do you want to add a new product (y/n)? '))

    while choice != 'y' and choice != 'n':
        choice = str(input('Please enter a valid choice (y/n): '))
    
    while choice == 'y':
        product_id = input('Enter the ID of the product: ')
        name = input('Enter the name of the product: ')
        type = "CP"
        width = float(input('Enter the width of the product: '))
        height = float(input('Enter the height of the product: '))
        length = float(input('Enter the length of the product: '))
        weight = float(input('Enter the weight of the product: '))
        price = 1000

        new_product = {
            'id': product_id,
            'name': name,
            'type': type,
            'width': width,
            'height': height,
            'length': length,
            'weight': weight,
            'price': price
        }

        database.add_product(store['_id'], new_product)

        choice = str(input('Do you want to add a new product (y/n)? '))
        while choice != 'y' and choice != 'n':
            choice = str(input('Please enter a valid choice (y/n): '))
        
        print('---------------------------------')    


if __name__ == '__main__':
    database = Database.get_instance()
    add_new_product(database)
    database.close_connection()

