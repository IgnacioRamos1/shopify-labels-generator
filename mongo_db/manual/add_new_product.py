import sys
import os
sys.path.append(os.path.abspath('..'))

from database import Database
from select_store import select_store
from select_product import select_product
from manage_product import manage_product


def add_new_product(database):
    store = select_store()
    
    choice = str(input('Do you want to add a new product (1), update an existing product (2) or delete a product (3) (q to quit): '))

    
    while choice != 'q':
        if choice == '1':
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
            
        elif choice == '2':
            product = select_product(store['_id'])

            if product:
                print(f'You have selected the product: {product["name"]}')
                print('-----------------------------------')
                manage_product(store['_id'], product)
            else:
                print('No product selected')

        elif choice == '3':
            product = select_product(store['_id'])

            if product:
                confirm = input(f'Are you sure you want to delete {product["name"]} and all its prices? (y/n): ')
                print('---------------------------------')
                if confirm.lower() == 'y':
                    database.delete_product(store['_id'], product['name'])
                    print(f'Product {product["name"]} deleted successfully!')
                
                else:
                    print('Product not found or not selected.')
        
        elif choice == 'q':
            break

        else:
            print('Invalid choice')

        choice = str(input('Do you want to add a new product (1), update an existing product (2) or delete a product (3) (q to quit): '))
        print('-----------------------------------')


if __name__ == '__main__':
    database = Database.get_instance()
    add_new_product(database)
    database.close_connection()

