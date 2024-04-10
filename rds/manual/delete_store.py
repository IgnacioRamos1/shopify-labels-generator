from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.append(os.path.abspath('../..'))


from rds.utils.db_connection import dev_engine
from manual_store import Store
from manual_product import Product
from select_store import seleccionar_tienda
from resources.delete_aws_resources_for_store import delete_aws_resources

# Crear una sesión
Session = sessionmaker(bind=dev_engine)
session = Session()


def delete_store(store_id):
    try:
        choice = str(input("Desea eliminar también los recursos de AWS? (y/n):"))

        if choice == 'y':
            print('------------------------------------')
            # Eliminar los recursos de AWS
            delete_aws_resources(session, store_id)

        elif choice == 'n':
            print('------------------------------------')
            print("No se eliminarán los recursos de AWS.")
            print('------------------------------------')
        
        else:
            print("Opción inválida. No se eliminarán los recursos de AWS.")
            print('------------------------------------')

        choice = str(input("Desea eliminar la tienda y sus productos? (y/n):"))

        if choice == 'y':
            print('------------------------------------')
            # Eliminar todos los productos asociados al store_id
            session.query(Product).filter(Product.store_id == store_id).delete()

            # Eliminar la tienda
            store = session.get(Store, store_id)
            if store:
                session.delete(store)

            # Confirmar los cambios
            session.commit()
            print(f"Todos los productos y la tienda con ID {store_id} han sido eliminados.")
            print('------------------------------------')
        
        elif choice == 'n':
            print('------------------------------------')
            print("No se eliminarán la tienda ni sus productos.")
            print('------------------------------------')
        
        else:
            print('------------------------------------')
            print("Opción inválida. No se eliminarán la tienda ni sus productos.")
            print('------------------------------------')
        
    except Exception as e:
        # En caso de error, revertir los cambios
        session.rollback()
        print(f"Error al eliminar la tienda y sus productos: {e}")
    finally:
        # Cerrar la sesión
        session.close()

if __name__ == "__main__":
    # Recibir el store_id como input del usuario
    print('------------------------------------')
    store_id = seleccionar_tienda(session)
    store_name = session.get(Store, store_id).name
    print('Seleccionaste la tienda:', store_name)
    print('------------------------------------')
    delete_store(store_id)
