from sqlalchemy.orm import sessionmaker
from rds.utils.db_connection import dev_engine, prod_engine
from rds.domain.store import Store  # Asume que este es tu modelo SQLAlchemy para la tienda
import os

STAGE = os.environ.get("STAGE")

if STAGE == "dev":
    engine = dev_engine
elif STAGE == "prod":
    engine = prod_engine


Session = sessionmaker(bind=engine)


def get_all_stores_uuid():
    with Session() as session:
        # Utiliza la consulta ORM de SQLAlchemy en lugar de SQL crudo
        stores = session.query(Store.id).all()
        stores_uuid = [str(store.id) for store in stores]
    return stores_uuid

