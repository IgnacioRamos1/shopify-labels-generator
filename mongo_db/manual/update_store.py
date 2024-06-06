import sys
import os
sys.path.append(os.path.abspath('..'))

from database import Database
from manual.select_store import select_store
from utils.security import encrypt_string, decrypt_string


def update_store():
    database = Database()

    store = select_store()

    choice = input('Do you want to update the access token of a store (1), update the owner of a store (2), or update the name of a store (3)? (q to quit): ')
    print('---------------------------------')

    while choice != 'q':
        if choice == '1':
            print(decrypt_string(store['access_token']))
            new_access_token = encrypt_string(input('Enter the new access token of the store: '))
            print('---------------------------------')

            store['access_token'] = new_access_token
            database.update_store(store['_id'], store)

            print(f'Store {store["name"]} access token updated successfully!')

        elif choice == '2':
            new_owner = input('Enter the new owner of the store: ')
            print('---------------------------------')

            store['owner'] = new_owner
            database.update_store(store['_id'], store)

            print(f'Store {store["name"]} owner updated successfully!')

        elif choice == '3':
            new_name = input('Enter the new name of the store: ')
            print('---------------------------------')

            store['name'] = new_name
            database.update_store(store['_id'], store)

            print(f'Store name updated successfully!')

        choice = input('Do you want to update the access token of a store (1), update the owner of a store (2), or update the name of a store (3)? (q to quit): ')
        print('---------------------------------')

    database.close_connection()


if __name__ == '__main__':
    update_store()
