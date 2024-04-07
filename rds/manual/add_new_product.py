from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.append(os.path.abspath('..'))

from manual_product import Product
from utils.db_connection import engine
from select_store import seleccionar_tienda

Session = sessionmaker(bind=engine)

# Se solicita el ID de la tienda una vez al principio
with Session() as session:
    store_id = seleccionar_tienda(session)

    choice = str(input("Do you want to add a new product? (y/n): "))

    while choice != "y" and choice != "n":
        choice = str(input("Please enter a valid option (y/n): "))

    while choice == "y":
        # Solicita los datos del nuevo producto
        product_id = int(input("Enter the product ID: "))
        name = str(input("Enter the name of the product: "))
        type = str(input("Enter the type of the product: "))
        width = int(input("Enter the width of the product: "))
        height = int(input("Enter the height of the product: "))
        length = int(input("Enter the length of the product: "))
        weight = float(input("Enter the weight of the product: "))
        price = int(input("Enter the price of the product: "))

        # Crea una nueva instancia de la clase Product con los datos proporcionados
        new_product = Product(
            store_id=store_id,  # Usa el store_id seleccionado previamente
            product_id=product_id,
            name=name,
            type=type,
            width=width,
            height=height,
            length=length,
            weight=weight,
            price=price
        )

        # Agrega el nuevo producto a la sesión y confirma los cambios inmediatamente
        session.add(new_product)
        session.commit()  # Guarda el producto en la base de datos de inmediato

        # Pregunta nuevamente si desea agregar otro producto, sin solicitar el ID de la tienda nuevamente
        choice = str(input("Do you want to add another product to the same store? (y/n): "))

        while choice != "y" and choice != "n":
            choice = str(input("Please enter a valid option (y/n): "))
