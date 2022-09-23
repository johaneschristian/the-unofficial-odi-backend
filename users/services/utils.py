from datetime import datetime
import phonenumbers

DATETIME_FORMAT = '%a %b %d %Y %H:%M:%S GMT+0700'


def validate_date_format(date_text) -> bool:
    try:
        datetime.strptime(date_text, DATETIME_FORMAT)
        return True
    except ValueError:
        return False


def get_date_from_string(date_text):
    date_text_datetime = datetime.strptime(date_text, DATETIME_FORMAT)
    return date_text_datetime.date()


def validate_phone_number(phone_number_string) -> bool:
    phone_number = phonenumbers.parse(phone_number_string)
    return phonenumbers.is_possible_number(phone_number)


def validate_password(password):
    is_valid_message = [True, None]
    if len(password) < 8:
        is_valid_message[0] = False
        is_valid_message[1] = 'Password length must be at least 8 characters'
    # Validate Capital
    # Validate lowercase
    # Validate number
