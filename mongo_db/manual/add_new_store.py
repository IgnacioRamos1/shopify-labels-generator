from datetime import datetime

import sys
import os
sys.path.append(os.path.abspath('..'))

from database import Database
from utils.security import encrypt_string
from utils.str_to_bool import str_to_bool


def add_new_store():
    database = Database()

    choice = input('Do you want to add a new store (y/n)? ')

    while choice == 'y':
        store_name = input('Enter the name of the store: ')
        owner_name = input('Enter the name of the store owner: ')
        store_url = input('Enter the URL of the store: ')
        access_token = encrypt_string(input('Enter the access token of the store: '))
        date_input = input('Enter the date of creation (DD-MM-YYYY): ')
        date = datetime.strptime(date_input, '%d-%m-%Y')
        to_email = input('Enter the email to send notifications to: ')
        cc_email = input('Enter the email to send a copy of the notifications to: ')
        dev_email = 'iramosibx@gmail.com'
        fixy = str_to_bool(input('Enter the value of fixy (True/False): '))
        if fixy:
            fixy_service_id = input('Enter the service ID of Fixy: ')
            fixy_client_id = input('Enter the client ID of Fixy: ')
            fixy_branch_code = input('Enter the branch code of Fixy: ')
            fixy_company = input('Enter the company of Fixy: ')
            fixy_sender = input('Enter the sender of Fixy: ')
        else:
            fixy_service_id = None
            fixy_client_id = None
            fixy_branch_code = None
            fixy_company = None
            fixy_sender = None
        
        new_store = {
            'name': store_name,
            'owner': owner_name,
            'url': store_url,
            'access_token': access_token,
            'date': date,
            'to_email': to_email,
            'cc_email': cc_email,
            'dev_email': dev_email,
            'fixy': fixy,
            'fixy_service_id': fixy_service_id,
            'fixy_client_id': fixy_client_id,
            'fixy_branch_code': fixy_branch_code,
            'fixy_company': fixy_company,
            'fixy_sender': fixy_sender
        }
        

        database.add_store(new_store)

        choice = input('Do you want to add a new store (y/n)? ')
        print('---------------------------------')

if __name__ == '__main__':
    add_new_store()  
