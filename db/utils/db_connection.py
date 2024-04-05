from sqlalchemy import create_engine
from utils.utils import get_parameter

HOST = get_parameter('db_host')
PORT = get_parameter('db_port')
DATABASE = get_parameter('db_name')
USER = get_parameter('db_username')
PASSWORD = get_parameter('db_password')


conf = {
    'host': HOST,
    'port': PORT,
    'database': DATABASE,
    'user': USER,
    'password': PASSWORD
}

engine = create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

