from .database import Database


def get_store(store_id):
    database = Database.get_instance()
    store = database.get_store(store_id)
    print('Store:', store)

    return store
