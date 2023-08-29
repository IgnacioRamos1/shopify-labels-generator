import re
import unicodedata


def clean_text(text):
    try:
        if not text:
            return ""

        # Convert 'ñ' to 'n'
        text = text.replace('ñ', 'n').replace('Ñ', 'N')

        # Remove accents
        text = ''.join((c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'))
        
        # Remove special characters
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        
        return text

    except Exception as e:
        raise Exception(f"Error in clean_text function: {e}")



def clean_phone(phone):
    """
    Clean the phone number by removing prefixes, non-numeric characters,
    and handling special cases.
    """
    
    try:
        # Convert potential scientific notation to full number string
        phone = "{:.0f}".format(float(phone))
    except ValueError:
        # If it's not a number in scientific notation, proceed as is
        pass

    # Keep a copy of the original phone
    original_phone = phone

    # Remove all non-numeric characters
    phone = re.sub(r'\D', '', phone)
    
    # Remove known prefixes, but ensure length is maintained
    if phone.startswith("549") and len(phone) > 10:
        phone = phone[3:]
    elif phone.startswith("54") and len(phone) > 9:
        phone = phone[2:]
    elif phone.startswith("9") and len(phone) > 6:
        phone = phone[1:]
    
    # Truncate to 10 digits if the phone number is longer, but ensure we don't get just zeros
    if len(phone) > 10:
        phone = phone[-10:]
        if int(phone) == 0:
            phone = original_phone[:10]
    
    # If after cleaning the number is just "0", revert to "0000000000"
    if phone == "0":
        phone = "0000000000"
    
    # Remove trailing comma or .0 if they exist
    if phone.endswith(','):
        phone = phone[:-1]

    if phone.endswith('.0'):
        phone = phone[:-2]
    
    if not phone:
        phone = "1234567890"
    
    return phone


def clean_zip_code(zip_code_str):
    """Remove all non-numeric characters from the zip code."""
    return re.sub(r"[^0-9]", "", zip_code_str)
