from sqlalchemy.orm import sessionmaker

from manual_store import Base as StoreBase
from manual_product import Base as ProductBase
from utils.db_connection import dev_engine, prod_engine

StoreBase.metadata.create_all(dev_engine)
ProductBase.metadata.create_all(dev_engine)

StoreBase.metadata.create_all(prod_engine)
ProductBase.metadata.create_all(prod_engine)

if __name__ == "__main__":
    dev_session_maker = sessionmaker(bind=dev_engine)
    dev_session = dev_session_maker()
    prod_session_maker = sessionmaker(bind=prod_engine)
    prod_session = prod_session_maker()

