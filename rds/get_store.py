from sqlalchemy.orm import sessionmaker
from rds.utils.db_connection import engine
from rds.domain.store import Store  


def get_store(store_id):
    Session = sessionmaker(bind=engine)
    with Session() as session:
        store = session.query(Store).filter(Store.id == store_id).first()
    return store

