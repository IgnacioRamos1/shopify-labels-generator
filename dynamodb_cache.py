import boto3
import time
from datetime import datetime, timedelta

# Constantes
REGION = "sa-east-1"

# Crea el cliente de DynamoDB
dynamodb_client = boto3.client('dynamodb', region_name=REGION)


def set_ttl_for_table(table_name):
    try:
        print(f"Setting TTL for table {table_name}...")
        dynamodb_client.update_time_to_live(
            TableName=table_name,
            TimeToLiveSpecification={
                'Enabled': True,
                'AttributeName': 'expiry_date'
            }
        )
    except Exception as e:
        raise Exception(f"Error in set_ttl_for_table function: {e}")


def create_table(table_name):
    try:
        print(f"Creating table {table_name}...")

        try:
            # Create a new table
            dynamodb_client.create_table(
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
                BillingMode='PAY_PER_REQUEST'
            )
        except Exception as e:
            raise Exception(f"Error in create_table function: {e}")

        # Wait for the table to be active
        while True:
            response = dynamodb_client.describe_table(TableName=table_name)
            status = response["Table"]["TableStatus"]
            if status == "ACTIVE":
                break
            time.sleep(5)  # Pause for 5 seconds before checking again

        print('Table created successfully!')
        # Set TTL for the table
        set_ttl_for_table(table_name)

        return table_name

    except Exception as e:
        raise Exception(f"Error in create_table function: {e}")


def check_order_processed(table_name, order_id, product_id):
    try:
        # Check if the item exists in the table
        response = dynamodb_client.get_item(
            TableName=table_name,
            Key={
                'order_id': {'S': str(order_id)},
                'product_id': {'S': str(product_id)}
            }
        )

        # Return True if the item exists, False otherwise
        return 'Item' in response

    except Exception as e:
        raise Exception(f"Error in check_order_processed function: {e}")


def mark_order_as_processed(table_name, order_id, product_id):
    try:
        # Add the item to the table
        expiry_date = int((datetime.now() + timedelta(days=30)).timestamp())  # TTL set for 30 days from now
        dynamodb_client.put_item(
            TableName=table_name,
            Item={
                'order_id': {'S': str(order_id)},
                'product_id': {'S': str(product_id)},
                'expiry_date': {'N': str(expiry_date)}  # New TTL attribute
            }
        )

    except Exception as e:
        raise Exception(f"Error in mark_order_as_processed function: {e}")


def check_table_exists(shop_name):
    try:
        shop_name = shop_name.replace(" ", "_").replace(".", "_")
        table_name = f"{shop_name}_order_cache"

        # Check if the table already exists
        existing_tables = dynamodb_client.list_tables()["TableNames"]

        if table_name in existing_tables:
            return table_name

    except Exception as e:
        raise Exception(f"Error in check_table_exists function: {e}")


def get_or_create_table_name(shop_name):
    try:
        shop_name = shop_name.replace(" ", "_").replace(".", "_")
        table_name = f"{shop_name}_order_cache"

        if not check_table_exists(shop_name):
            # Here, create the table because it doesn't exist.
            create_table(table_name)

        return table_name

    except Exception as e:
        raise Exception(f"Error in get_or_create_table_name function: {e}")
