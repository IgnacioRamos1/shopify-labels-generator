import boto3


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

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception(f"Error sending email: {response}")

        print('Finished send_products_missing_email function')

        return response

    except Exception as e:
        raise Exception(f"Error in send_products_missing_email function: {e}")