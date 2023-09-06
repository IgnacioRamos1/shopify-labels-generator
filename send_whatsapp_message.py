import requests
from utils import get_parameter
from urllib.parse import quote

token = get_parameter('whatsapp_token')


def send_whatsapp_group_message(date, shop, total_orders_count, s3_presigned_url, group_chat_id):
    try:
        url = "https://api.ultramsg.com/instance60273/messages/document"

        # group_chat_id = "120363150899530481@g.us"

        # The group_chat_id is now coming from the function parameter, so no need to get it again

        filename = f"{date} - {shop} - {total_orders_count} Ordenes.zip"
        s3_presigned_url = quote(s3_presigned_url, safe='')

        # Use the group_chat_id in the payload
        whatsapp_payload = f"token={token}&to={group_chat_id}&filename={filename}&document={s3_presigned_url}&caption="
        whatsapp_payload = whatsapp_payload.encode('utf8').decode('iso-8859-1')

        headers = {'content-type': 'application/x-www-form-urlencoded'}

        requests.request("POST", url, data=whatsapp_payload, headers=headers)

    except Exception as e:
        raise Exception(f"Error in send_whatsapp_message function: {e}")


def send_whatsapp_message(group_chat_id, body):
    try:
        url = "https://api.ultramsg.com/instance60273/messages/chat"

        # group_chat_id = "120363150899530481@g.us"

        payload = f"token={token}&to={group_chat_id}&body={body}"
        payload = payload.encode('utf8').decode('iso-8859-1')
        headers = {'content-type': 'application/x-www-form-urlencoded'}

        requests.request("POST", url, data=payload, headers=headers)

    except Exception as e:
        raise Exception(f"Error in send_whatsapp_message function: {e}")
