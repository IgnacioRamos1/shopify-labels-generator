import requests
from utils.utils import get_parameter, ApiException
from urllib.parse import quote
import os

token = get_parameter('whatsapp_token')


stage = os.environ['STAGE']


def send_whatsapp_group_message(date, shop, total_orders_count, s3_presigned_url, group_chat_id):
    try:
        print('Starting send_whatsapp_group_message function')
        url = "https://api.ultramsg.com/instance60273/messages/document"

        if stage == 'dev':
            # Si estamos en dev, enviar el mensaje al grupo de testeo
            group_chat_id = "120363150899530481@g.us"

        # The group_chat_id is now coming from the function parameter, so no need to get it again

        filename = f"{date} - {shop} - {total_orders_count} Ordenes.zip"
        s3_presigned_url = quote(s3_presigned_url, safe='')

        # Use the group_chat_id in the payload
        whatsapp_payload = f"token={token}&to={group_chat_id}&filename={filename}&document={s3_presigned_url}&caption="
        whatsapp_payload = whatsapp_payload.encode('utf8').decode('iso-8859-1')

        headers = {'content-type': 'application/x-www-form-urlencoded'}

        response = requests.request("POST", url, data=whatsapp_payload, headers=headers)

        if response.status_code != 200:
            raise ApiException(f"Error sending whatsapp group message: {response.text}")

        print('Finished send_whatsapp_group_message function')

    except Exception as e:
        raise Exception(f"Error in send_whatsapp_message function: {e}")


def send_whatsapp_message(group_chat_id, body):
    try:
        print('Starting send_whatsapp_message function')
        url = "https://api.ultramsg.com/instance60273/messages/chat"

        if stage == 'dev':
            # Si estamos en dev, enviar el mensaje al grupo de testeo
            group_chat_id = "120363150899530481@g.us"

        payload = f"token={token}&to={group_chat_id}&body={body}"
        payload = payload.encode('utf8').decode('iso-8859-1')
        headers = {'content-type': 'application/x-www-form-urlencoded'}

        response = requests.request("POST", url, data=payload, headers=headers)

        if response.status_code != 200:
            raise ApiException(f"Error sending whatsapp message: {response.text}")

        print('Finished send_whatsapp_message function')

    except Exception as e:
        raise Exception(f"Error in send_whatsapp_message function: {e}")
