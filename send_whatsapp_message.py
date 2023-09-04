import requests
from utils import get_parameter
from urllib.parse import quote


def send_whatsapp_message(date, shop, total_orders_count, s3_presigned_url):
    try:
        url = "https://api.ultramsg.com/instance60273/messages/document"

        group_chat_id = get_parameter('group_chat_id')
        token = get_parameter('whatsapp_token')

        filename = f"{date}-{shop}-{total_orders_count[shop]}.zip"
        s3_presigned_url = quote(s3_presigned_url, safe='')

        # Send the ZIP file link to WhatsApp
        whatsapp_payload = f"token={token}&to={group_chat_id}&filename={filename}&document={s3_presigned_url}&caption="
        whatsapp_payload = whatsapp_payload.encode('utf8').decode('iso-8859-1')

        headers = {'content-type': 'application/x-www-form-urlencoded'}

        response = requests.request("POST", url, data=whatsapp_payload, headers=headers)

    except Exception as e:
        raise Exception(f"Error in send_whatsapp_message function: {e}")
