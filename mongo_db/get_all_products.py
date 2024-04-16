from mongo_db.database import Database


def get_store_products(store_id):
    database = Database.get_instance()
    store = database.get_store(store_id)
    
    return store['products']
