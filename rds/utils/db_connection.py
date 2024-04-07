from sqlalchemy import create_engine
import os

# Cargar variables de entorno si no se está ejecutando en AWS Lambda
if 'AWS_EXECUTION_ENV' not in os.environ:
    from dotenv import load_dotenv
    load_dotenv()

# Función para crear un engine de SQLAlchemy
def create_db_engine(stage):
    if 'AWS_EXECUTION_ENV' in os.environ:
        from utils.utils import get_parameter
        HOST = get_parameter(f'{stage}_db_host')
        PORT = get_parameter('db_port')
        DATABASE = get_parameter(f'{stage}_db_name')
        USER = get_parameter(f'{stage}_db_username')
        PASSWORD = get_parameter(f'{stage}_db_password')
    else:
        HOST = os.getenv(f'{stage.upper()}_DB_HOST')
        PORT = os.getenv(f'DB_PORT')
        DATABASE = os.getenv(f'{stage.upper()}_DB_NAME')
        USER = os.getenv(f'{stage.upper()}_DB_USERNAME')
        PASSWORD = os.getenv(f'{stage.upper()}_DB_PASSWORD')

    return create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

# Crear engines para desarrollo y producción
dev_engine = create_db_engine('dev')
prod_engine = create_db_engine('prod')
