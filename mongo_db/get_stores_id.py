from .database import Database


def get_stores_id():
    print('Getting stores id')
    database = Database.get_instance()
    stores = database.get_stores()
    stores_id = [str(store['_id']) for store in stores]

    return stores_id
