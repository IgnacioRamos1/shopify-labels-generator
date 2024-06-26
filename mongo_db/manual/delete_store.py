
import sys
import os
sys.path.append(os.path.abspath('..'))

from database import Database
from select_store import select_store
sys.path.append(os.path.abspath('../..'))
from resources.delete_aws_resources_for_store import delete_aws_resources


def delete_store(database):
    store = select_store()

    choice = input(f'Are you sure you want to delete the store {store["name"]}? (y/n): ')

    if choice == 'y':
        delete_aws_resources(store['name'])
        database.delete_store(store['_id'])


if __name__ == '__main__':
    database = Database()
    delete_store(database)
    database.close_connection()
