from sqlalchemy.orm import sessionmaker
from datetime import datetime

from manual_store import Store
from utils.db_connection import engine
from utils.str_to_bool import str_to_bool
from utils.security import encrypt_string


Session = sessionmaker(bind=engine)
session = Session()

choice = str(input("Do you want to add a new store? (y/n): "))

while choice != "y" and choice != "n":
    choice = str(input("Please enter a valid option (y/n): "))

while choice == "y":
    # Solicita los datos de la nueva tienda
    name = str(input("Enter the name of the store: "))
    url = str(input("Enter the URL of the store: "))
    access_token = encrypt_string(str(input("Enter the access token of the store: ")))
    date_input = input("Enter the date of the store (DD-MM-YYYY): ")
    date = datetime.strptime(date_input, "%d-%m-%Y").date()
    to_email = str(input("Enter the email to send the order to: "))
    cc_email = str(input("Enter the email to send the order to (cc): "))
    dev_email = str(input("Enter the email to send the order to (dev): "))
    fixy = str_to_bool(input("Enter the fixy status of the store (True/False): "))
    if fixy:
        fixy_service_id = str(input("Enter the fixy service id of the store: "))
        fixy_client_id = str(input("Enter the fixy client id of the store: "))
        fixy_branch_code = str(input("Enter the fixy branch code of the store: "))
        fixy_company = str(input("Enter the fixy company of the store: "))
        fixy_sender = str(input("Enter the fixy sender of the store: "))
    else:
        fixy_service_id = None
        fixy_client_id = None
        fixy_branch_code = None
        fixy_company = None
        fixy_sender = None

    # Crea una nueva instancia de la clase Store con los datos proporcionados
    nueva_tienda = Store(
        name=name,
        url=url,
        access_token=access_token,
        date=date,
        to_email=to_email,
        cc_email=cc_email,
        dev_email=dev_email,
        fixy=fixy,
        fixy_service_id=fixy_service_id,
        fixy_client_id=fixy_client_id,
        fixy_branch_code=fixy_branch_code,
        fixy_company=fixy_company,
        fixy_sender=fixy_sender
    )

    # Agrega la nueva tienda a la sesión
    session.add(nueva_tienda)

    choice = str(input("Do you want to add another store? (y/n): "))

    while choice != "y" and choice != "n":
        choice = str(input("Please enter a valid option (y/n): "))

# Confirma las transacciones
session.commit()

# Cierra la sesión
session.close()

