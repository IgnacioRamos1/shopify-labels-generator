import boto3
import base64


def send_email(zip_buffer, zip_name, from_email, to_email, shop):
    """
    Send the in-memory ZIP file as an email attachment using AWS SES.
    """
    ses = boto3.client('ses', region_name='sa-east-1')
    
    subject = "CSV Files"
    body = "Please find attached the CSV files."
    attachment = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')
    
    msg = {
        'Data': f"""Subject: {shop} CSV Files
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
