from sqlalchemy.orm import sessionmaker
from rds.utils.db_connection import engine
from rds.domain.product import Product
from rds.utils.validate_uuid import is_valid_uuid


Session = sessionmaker(bind=engine)


def get_all_products_for_store(store_id):
    print("Getting all products for store with ID:", store_id)
    if not is_valid_uuid(store_id):
        return "Invalid UUID"

    products_dict = {}
    with Session() as session:
        products = session.query(Product).filter(Product.store_id == store_id).all()

        for product in products:
            # Convierte el product_id a string para ser consistente con tus claves de diccionario
            product_id_str = str(product.product_id)
            
            # Verifica si el product_id ya existe en el diccionario
            if product_id_str not in products_dict:
                # Si no existe, crea una nueva entrada con una lista que contiene el primer conjunto de atributos
                products_dict[product_id_str] = [{
                    "name": product.name,
                    "type": product.type,
                    "width": product.width,
                    "height": product.height,
                    "length": product.length,
                    "weight": product.weight,
                    "price": product.price
                }]
            else:
                # Si ya existe, añade este conjunto de atributos a la lista existente
                products_dict[product_id_str].append({
                    "name": product.name,
                    "type": product.type,
                    "width": product.width,
                    "height": product.height,
                    "length": product.length,
                    "weight": product.weight,
                    "price": product.price
                })
    print("Products retrieved successfully!")
    return products_dict
