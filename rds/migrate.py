from sqlalchemy.orm import sessionmaker
from manual.manual_product import Product
from manual.manual_store import Store
from utils.db_connection import dev_engine, prod_engine

DevSession = sessionmaker(bind=dev_engine)
ProdSession = sessionmaker(bind=prod_engine)

dev_session = DevSession()
prod_session = ProdSession()

# Sincronizar la tabla Store
store_ids_dev = {store_instance.id for store_instance in dev_session.query(Store).all()}
store_ids_prod = {store_instance.id for store_instance in prod_session.query(Store).all()}

# Identificar las tiendas que necesitan ser eliminadas en prod
stores_to_delete = store_ids_prod - store_ids_dev

# Eliminar primero los productos asociados a las tiendas que se eliminarán
for store_id in stores_to_delete:
    # Eliminar productos asociados en producción
    products_to_delete = prod_session.query(Product).filter(Product.store_id == store_id).all()
    for product in products_to_delete:
        prod_session.delete(product)

# Ahora, eliminar las tiendas identificadas utilizando Session.get() en lugar de query().get()
for store_id in stores_to_delete:
    store_to_delete = prod_session.get(Store, store_id)
    if store_to_delete:
        prod_session.delete(store_to_delete)

# Sincronizar las tiendas de dev a prod (actualizaciones y nuevas adiciones)
for store_instance in dev_session.query(Store).all():
    prod_session.merge(store_instance)

# Sincronizar la tabla Product
product_ids_dev = {product_instance.id for product_instance in dev_session.query(Product).all()}
product_ids_prod = {product_instance.id for product_instance in prod_session.query(Product).all()}

# Identificar los productos que necesitan ser eliminados en prod
products_to_delete = product_ids_prod - product_ids_dev

# Eliminar los productos identificados en producción
for product_id in products_to_delete:
    product_to_delete = prod_session.query(Product).get(product_id)
    if product_to_delete:
        prod_session.delete(product_to_delete)

# Sincronizar los productos de dev a prod (actualizaciones y nuevas adiciones)
for product_instance in dev_session.query(Product).all():
    prod_session.merge(product_instance)

# Confirmar los cambios en producción
prod_session.commit()

# Cerrar las sesiones
dev_session.close()
prod_session.close()
