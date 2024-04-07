def load_product_attributes(shop_name):
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(base_path, '..', 'products_json', f"{shop_name}_products.json")

        with open(filename, 'r') as f:
            return json.load(f)

    except Exception as e:
        raise Exception(f"Error in load_product_attributes function: {e}")


def list_shop_secrets():
    try:
        client = boto3.client('secretsmanager', region_name='sa-east-1')
        paginator = client.get_paginator('list_secrets')
        shop_secrets = []

        # Itera a través de todas las páginas de la respuesta paginada
        for page in paginator.paginate():
            for secret in page['SecretList']:
                if secret['Name'].startswith('shop_secret_'):
                    shop_secrets.append(secret['Name'].replace('shop_secret_', ''))

        return shop_secrets

    except Exception as e:
        raise Exception(f"Error in list_shop_secrets function: {e}")


def get_secret(shop_name):
    try:
        client = boto3.client('secretsmanager', region_name='sa-east-1')
        response = client.get_secret_value(SecretId=shop_name)
        return json.loads(response['SecretString'])

    except Exception as e:
        raise Exception(f"Error in get_secret function: {e}")
