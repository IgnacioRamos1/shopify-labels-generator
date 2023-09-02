import boto3
import base64


def send_email(zip_buffer, zip_name, from_email, to_email, shop, total_orders_count, date):
    try:
        ses = boto3.client('ses', region_name='sa-east-1')
        
        subject = "CSV Files"
        body = "Please find attached the CSV files."
        attachment = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')
        
        msg = {
            'Data': f"""Subject: {shop} CSV Files - {total_orders_count} orders - {date}
From: {from_email}
To: {to_email}
MIME-Version: 1.0
Content-type: Multipart/Mixed; boundary="NextPart"

--NextPart
Content-Type: text/plain
Content-Transfer-Encoding: 8bit

{body}

--NextPart
Content-Type: application/zip; name="{zip_name}"
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="{zip_name}"

{attachment}
--NextPart--"""
        }

        response = ses.send_raw_email(
            Source=from_email,
            Destinations=[to_email],
            RawMessage=msg
        )

        return response

    except Exception as e:
        raise Exception(f"Error in send_email function: {e}")


def send_products_missing_email(from_email, to_email, missing_products):
    try:
        ses = boto3.client('ses', region_name='sa-east-1')
        
        subject = "Missing Products in JSON"
        body = "The following products were not found in the JSON and therefore were not added to the CSV:\n\n"
        for prod in missing_products:
            body += f"Name: {prod['item']}, ID: {prod['item_id']}, Order: {prod['order_id']}\n"
        
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

        return response

    except Exception as e:
        raise Exception(f"Error in send_products_missing_email function: {e}")
