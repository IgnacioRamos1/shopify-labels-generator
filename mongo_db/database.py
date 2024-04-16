import pymongo
import os
from bson import ObjectId
from datetime import datetime, timedelta


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

stage = os.environ['STAGE']


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
    
    def update_product(self, product_name, product):
        self.stores.update_one({'products.name': product_name}, {'$set': {'products.$': product}})
        print(f'Product {product["name"]} updated successfully')

    def delete_product(self, store_id, product_name):
        if isinstance(store_id, str):
            store_id = ObjectId(store_id)
        self.stores.update_one({'_id': store_id}, {'$pull': {'products': {'name': product_name}}})
        print('Product deleted successfully')
    
    def close_connection(self):
        self.client.close()


class CacheDatabase:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if CacheDatabase._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            CacheDatabase._instance = self
            self.client = pymongo.MongoClient(ATLAS_URI)
            self.db = self.client[DB_NAME]
            self.stores = self.db[f'orders-cache-{stage}']
            self.ensure_ttl()

    def ensure_ttl(self):
        # Create TTL index for automatically deleting documents after 30 days
        self.stores.create_index("orders.expiry_date", expireAfterSeconds=30*24*3600)

    def check_store_exists(self, store_name):
        return self.stores.find_one({'store_name': store_name}) is not None

    def add_store(self, store_name):
        self.stores.insert_one({'store_name': store_name, 'orders': []})
        print('Store added successfully')
    
    def check_order_processed(self, store_name, order_id, product_id):
        store = self.stores.find_one({'store_name': store_name, 'orders.order_id': order_id, 'orders.product_id': product_id})
        return bool(store)

    def mark_order_as_processed(self, store_name, order_id, product_id):
        # Preparar la fecha de expiración para la orden
        expiry_date = datetime.now() + timedelta(days=30)
        # Preparamos el objeto de la orden que queremos insertar
        order_data = {
            'order_id': order_id,
            'product_id': product_id,
            'expiry_date': expiry_date
        }
        # Intentamos actualizar el documento de la tienda con la nueva orden
        update_result = self.stores.update_one(
            {'store_name': store_name},  # Filtro por el nombre de la tienda
            {'$push': {'orders': order_data}}  # Usamos $push para añadir la orden al array 'orders'
        )
