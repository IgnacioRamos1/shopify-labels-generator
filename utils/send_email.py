import boto3
from botocore.exceptions import NoCredentialsError
import requests
from io import BytesIO
import base64
import os

stage = os.environ['STAGE']


def send_products_missing_email(from_email, to_email, missing_products, shop, date):
    try:
        print('Starting send_products_missing_email function')
        ses = boto3.client('ses', region_name='sa-east-1')

        subject = f"Missing Products {shop} - {date}"
        body = "The following products were not found in the JSON and therefore were not added to the CSV:\n\n"
        for prod in missing_products:
            body += f"Name: {prod['item']}, ID: {prod['item_id']}, Order: {prod['order_id']}, Reason: {prod['reason']}\n"

        msg = {
            'Data': f"""Subject: {subject}
From: {from_email}
To: {to_email}
MIME-Version: 1.0
Content-type: text/plain
Content-Transfer-Encoding: 8bit

{body}
"""
        }

        response = ses.send_raw_email(
            Source=from_email,
            Destinations=[to_email],
            RawMessage=msg
        )

        print('response', response)

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception(f"Error sending email: {response}")

        print('Finished send_products_missing_email function')

        return response

    except Exception as e:
        raise Exception(f"Error in send_products_missing_email function: {e}")


def send_zip_email(from_email, to_email, cc_email, dev_email, shop, date, s3_presigned_url, total_orders_count, floor_errors=None, street_number_errors=None):
    try:
        print('Starting send_zip_email function')

        if stage == 'dev':
            to_email = 'iramosibx@gmail.com'
            cc_email = ''

        ses = boto3.client('ses', region_name='sa-east-1')

        filename = f"{date}_{shop.replace(' ', '_')}_{total_orders_count}_Ordenes.zip"

        subject = f"Productos para {shop} - {date}"

        # Descargar el archivo ZIP desde S3 usando la URL prefirmada
        response = requests.get(s3_presigned_url)
        zip_file_data = BytesIO(response.content)

        body = f"Adjunto encontrarás el archivo ZIP con los productos para {shop} en la fecha {date}.\n\n"
        
        if floor_errors:
            body += "\nErrores en el piso:\n"
            body += "\n".join([f"{order['person']} - {order['item']} - {order['reason']}" for order in floor_errors])
            body += "\n\n"

        if street_number_errors:
            body += "\nErrores en la calle o número:\n"
            body += "\n".join([f"{order['person']} - {order['item']} - {order['reason']}" for order in street_number_errors])

        msg = {
            'Data': f"""Subject: {subject}
From: {from_email}
To: {to_email}
CC: {cc_email}
MIME-Version: 1.0
Content-type: multipart/mixed; boundary=boundary

--boundary
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit

{body}

--boundary
Content-Type: application/zip; name={filename}
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename={filename}

{base64.b64encode(zip_file_data.getvalue()).decode()}
--boundary--
"""
        }

        response = ses.send_raw_email(
            Source=from_email,
            Destinations=[to_email] + cc_email.split(', ') if cc_email else [] + dev_email.split(', ') if dev_email else [],
            RawMessage=msg
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception(f"Error sending email: {response}")

        print('Finished send_zip_email function')

        return response

    except NoCredentialsError:
        raise Exception("No AWS credentials found")
    except Exception as e:
        raise Exception(f"Error in send_zip_email function: {e}")
