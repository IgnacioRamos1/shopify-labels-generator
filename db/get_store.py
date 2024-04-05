from sqlalchemy.orm import sessionmaker
from db.utils.db_connection import engine
from db.domain.store import Store  


def get_store(store_id):
    Session = sessionmaker(bind=engine)
    with Session() as session:
        store = session.query(Store).filter(Store.id == store_id).first()
    return store

