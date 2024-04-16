from sqlalchemy.orm import sessionmaker
from rds.utils.db_connection import dev_engine, prod_engine
from rds.domain.store import Store 
import os

STAGE = os.environ.get("STAGE")

if STAGE == "dev":
    engine = dev_engine
elif STAGE == "prod":
    engine = prod_engine


def get_store(store_id):
    Session = sessionmaker(bind=engine)
    with Session() as session:
        store = session.query(Store).filter(Store.id == store_id).first()
    return store

