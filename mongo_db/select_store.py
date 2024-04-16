from database import Database


def select_store():
    database = Database.get_instance()
    stores = database.get_stores()
    stores = list(stores)
    print('Select a store:')
    print('---------------------------------')
    for i, store in enumerate(stores):
        print(f"{i + 1}. {store['name']}")
    print('---------------------------------')
    store_number = int(input('Enter the number of the store: '))
    print('---------------------------------')
    
    # We are returning the store object
    return stores[store_number - 1]
