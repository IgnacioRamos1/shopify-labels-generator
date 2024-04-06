from sqlalchemy import create_engine
import os


if 'AWS_EXECUTION_ENV' in os.environ:
    from utils.utils import get_parameter
    HOST = get_parameter('db_host')
    PORT = get_parameter('db_port')
    DATABASE = get_parameter('db_name')
    USER = get_parameter('db_username')
    PASSWORD = get_parameter('db_password')
else:
    from dotenv import load_dotenv
    load_dotenv()

    HOST = os.getenv('DB_HOST')
    PORT = os.getenv('DB_PORT')
    DATABASE = os.getenv('DB_NAME')
    USER = os.getenv('DB_USERNAME')
    PASSWORD = os.getenv('DB_PASSWORD')

conf = {
    'host': HOST,
    'port': PORT,
    'database': DATABASE,
    'user': USER,
    'password': PASSWORD
}

engine = create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

