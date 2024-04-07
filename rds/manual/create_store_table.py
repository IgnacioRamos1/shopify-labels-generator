from sqlalchemy.orm import sessionmaker

from manual_store import Base as StoreBase
from manual_product import Base as ProductBase
from utils.db_connection import engine


StoreBase.metadata.create_all(engine)
ProductBase.metadata.create_all(engine)

if __name__ == "__main__":
    Session = sessionmaker(bind=engine)
    session = Session()
