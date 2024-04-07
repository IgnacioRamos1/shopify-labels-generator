from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.append(os.path.abspath('..'))


from utils.db_connection import dev_engine
from manual_store import Store
from manual_product import Product

# Crear una sesión
Session = sessionmaker(bind=dev_engine)
session = Session()


def delete_store_and_products(store_id):
    try:
        # Eliminar todos los productos asociados al store_id
        session.query(Product).filter(Product.store_id == store_id).delete()

        # Eliminar la tienda
        store = session.get(Store, store_id)
        if store:
            session.delete(store)

        # Confirmar los cambios
        session.commit()
        print(f"Todos los productos y la tienda con ID {store_id} han sido eliminados.")
    except Exception as e:
        # En caso de error, revertir los cambios
        session.rollback()
        print(f"Error al eliminar la tienda y sus productos: {e}")
    finally:
        # Cerrar la sesión
        session.close()

if __name__ == "__main__":
    # Recibir el store_id como input del usuario
    store_id = input("Ingrese el ID de la tienda a eliminar: ")
    delete_store_and_products(store_id)
