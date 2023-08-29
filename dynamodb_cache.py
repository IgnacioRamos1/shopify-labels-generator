import boto3
import time

# Constantes
REGION = "sa-east-1"

# Crea el cliente de DynamoDB
dynamodb_client = boto3.client('dynamodb', region_name=REGION)


def initialize_cache_table(shop_name):
    try:
        shop_name = shop_name.replace(" ", "_").replace(".", "_")
        table_name = f"{shop_name}_order_cache"
        
        # Check if the table already exists
        existing_tables = dynamodb_client.list_tables()["TableNames"]
        if table_name in existing_tables:
            return table_name
        
        # If not, create a new table
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
        
        # Wait for the table to be active
        while True:
            response = dynamodb_client.describe_table(TableName=table_name)
            status = response["Table"]["TableStatus"]
            if status == "ACTIVE":
                break
            time.sleep(5)  # Pause for 5 seconds before checking again
        
        return table_name

    except Exception as e:
        raise Exception(f"Error in initialize_cache_table function: {e}")


def check_order_processed(shop_name, order_id, product_id):
    try:
        table_name = initialize_cache_table(shop_name)
        
        response = dynamodb_client.get_item(
            TableName=table_name,
            Key={
                'order_id': {'S': str(order_id)},
                'product_id': {'S': str(product_id)}
            }
        )
        
        return 'Item' in response

    except Exception as e:
        raise Exception(f"Error in check_order_processed function: {e}")


def mark_order_as_processed(shop_name, order_id, product_id):
    try:
        table_name = initialize_cache_table(shop_name)
        dynamodb_client.put_item(
            TableName=table_name,
            Item={
                'order_id': {'S': str(order_id)},
                'product_id': {'S': str(product_id)}
            }
        )

    except Exception as e:
        raise Exception(f"Error in mark_order_as_processed function: {e}")
