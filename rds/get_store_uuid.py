from sqlalchemy.orm import sessionmaker
from rds.utils.db_connection import engine
from rds.domain.store import Store  # Asume que este es tu modelo SQLAlchemy para la tienda


Session = sessionmaker(bind=engine)


def get_all_stores_uuid():
    with Session() as session:
        # Utiliza la consulta ORM de SQLAlchemy en lugar de SQL crudo
        stores = session.query(Store.id).all()
        stores_uuid = [str(store.id) for store in stores]
    return stores_uuid

