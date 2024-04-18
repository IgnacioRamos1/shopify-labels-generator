import pymongo
import os
from bson import ObjectId

import sys
import os
sys.path.append(os.path.abspath('..'))


if 'AWS_EXECUTION_ENV' in os.environ:
    from utils.utils import get_parameter
    ATLAS_URI = get_parameter('shopify_atlas_uri')
    DB_NAME = get_parameter('shopify_db_name')

else:
    from dotenv import load_dotenv
    load_dotenv()

    ATLAS_URI = os.getenv('ATLAS_URI')
    DB_NAME = os.getenv('DB_NAME')


class Database:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if Database._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Database._instance = self
            self.client = pymongo.MongoClient(ATLAS_URI)
            self.db = self.client[DB_NAME]
            self.stores = self.db['stores']

    def add_store(self, store):
        self.stores.insert_one(store)
        print('Store added successfully')
    
    def add_stores(self, stores):
        self.stores.insert_many(stores)
        print('Stores added successfully')

    def get_stores(self):
        return self.stores.find()

    def get_store(self, store_id):
        if isinstance(store_id, str):
            store_id = ObjectId(store_id)
        return self.stores.find_one({'_id': store_id})
    
    def update_store(self, store_id, store):
        if isinstance(store_id, str):
            store_id = ObjectId(store_id)
        self.stores.update_one({'_id': store_id}, {'$set': store})
        print('Store updated successfully')

    def delete_store(self, store_id):
        if isinstance(store_id, str):
            store_id = ObjectId(store_id)
        self.stores.delete_one({'_id': store_id})
        print('Store deleted successfully')

    def add_product(self, store_id, product):
        if isinstance(store_id, str):
            store_id = ObjectId(store_id)
        self.stores.update_one({'_id': store_id}, {'$push': {'products': product}})
        print(f'Product {product["name"]} added successfully')
    
    def update_product(self, store_id, product):
        if isinstance(store_id, str):
            store_id = ObjectId(store_id)
        self.stores.update_one({'_id': store_id, 'products.name': product['name']}, {'$set': {'products.$': product}})
        print('Product updated successfully')

    def delete_product(self, store_id, product_name):
        if isinstance(store_id, str):
            store_id = ObjectId(store_id)
        self.stores.update_one({'_id': store_id}, {'$pull': {'products': {'name': product_name}}})
        print('Product deleted successfully')
    
    def close_connection(self):
        self.client.close()
    