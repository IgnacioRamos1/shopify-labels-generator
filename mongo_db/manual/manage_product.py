from database import Database


def manage_product(store_id, product):
    database = Database.get_instance()

    choice = input('Do you want to update the product (1), delete the product (2) or quit (q): ')

    while choice != 'q':
        if choice == '1':
            update_choice = input('Do you want to update the name (1), the dimensions (2), the weight (3) or the price (4) (q to quit): ')

            if update_choice == '1':
                name = input('Enter the new name: ')
                product['name'] = name
                database.update_product(store_id, product)

            elif update_choice == '2':
                width = float(input('Enter the new width: '))
                height = float(input('Enter the new height: '))
                length = float(input('Enter the new length: '))
                product['width'] = width
                product['height'] = height
                product['length'] = length
                database.update_product(store_id, product)

            elif update_choice == '3':
                weight = float(input('Enter the new weight: '))
                product['weight'] = weight
                database.update_product(store_id, product)

            elif update_choice == '4':
                price = float(input('Enter the new price: '))
                product['price'] = price
                database.update_product(store_id, product)
            
            elif update_choice == 'q':
                break

            else:
                print('Invalid choice')

        elif choice == '2':
            database.delete_product(store_id, product["name"])
            break

        elif choice == 'q':
            break

        else:
            print('Invalid choice')


