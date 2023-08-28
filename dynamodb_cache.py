import boto3
import time

# Constantes
REGION = "sa-east-1"

# Crea el cliente de DynamoDB
dynamodb_client = boto3.client('dynamodb', region_name=REGION)


def initialize_cache_table(shop_name):
    """
    Inicializa la tabla de caché para una tienda específica en DynamoDB.
    Si la tabla ya existe, simplemente la devuelve.
    """
    shop_name = shop_name.replace(" ", "_").replace(".", "_")
    table_name = f"{shop_name}_order_cache"
    
    # Verifica si la tabla ya existe
    existing_tables = dynamodb_client.list_tables()["TableNames"]
    if table_name in existing_tables:
        return table_name
    
    # Si no existe, crea una nueva tabla
    table = dynamodb_client.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'order_id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'product_id',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'order_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'product_id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    # Espera a que la tabla esté activa
    while True:
        response = dynamodb_client.describe_table(TableName=table_name)
        status = response["Table"]["TableStatus"]
        if status == "ACTIVE":
            break
        time.sleep(5)  # Pausa por 5 segundos antes de verificar nuevamente

    return table_name



def check_order_processed(shop_name, order_id, product_id):
    """
    Comprueba si un pedido específico ya ha sido procesado.
    """
    table_name = initialize_cache_table(shop_name)
    
    response = dynamodb_client.get_item(
        TableName=table_name,
        Key={
            'order_id': {'S': str(order_id)},
            'product_id': {'S': str(product_id)}
        }
    )
    
    return 'Item' in response

def mark_order_as_processed(shop_name, order_id, product_id):
    """
    Marca un pedido como procesado.
    """
    table_name = initialize_cache_table(shop_name)
    dynamodb_client.put_item(
        TableName=table_name,
        Item={
            'order_id': {'S': str(order_id)},
            'product_id': {'S': str(product_id)}
        }
    )
