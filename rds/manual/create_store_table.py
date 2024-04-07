from sqlalchemy.orm import sessionmaker

from manual_store import Base as StoreBase
from manual_product import Base as ProductBase
from utils.db_connection import dev_engine

StoreBase.metadata.create_all(dev_engine)
ProductBase.metadata.create_all(dev_engine)

if __name__ == "__main__":
    Session = sessionmaker(bind=dev_engine)
    session = Session()
