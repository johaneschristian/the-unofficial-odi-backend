from datetime import datetime
import phonenumbers
import re

DATETIME_FORMAT = '%Y-%m-%d'
email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


def validate_date_format(date_text) -> bool:
    date_text = date_text.split('T')[0]
    try:
        datetime.strptime(date_text, DATETIME_FORMAT)
        return True
    except ValueError:
        return False


def get_date_from_string(date_text):
    date_text = date_text.split('T')[0]
    date_text_datetime = datetime.strptime(date_text, DATETIME_FORMAT)
    return date_text_datetime.date()


def validate_phone_number(phone_number_string) -> bool:
    phone_number = phonenumbers.parse(phone_number_string)
    return phonenumbers.is_possible_number(phone_number)


def validate_password(password):
    validation_result = {
        'is_valid': True,
        'message': None
    }
    if len(password) < 8:
        validation_result['is_valid'] = False
        validation_result['message'] = 'Password length must be at least 8 characters'
    elif not any(character.isupper() for character in password):
        validation_result['is_valid'] = False
        validation_result['message'] = 'Password length must contain at least 1 uppercase character'
    elif not any(character.islower() for character in password):
        validation_result['is_valid'] = False
        validation_result['message'] = 'Password length must contain at least 1 lowercase character'
    elif not any(character.isdigit() for character in password):
        validation_result['is_valid'] = False
        validation_result['message'] = 'Password length must contain at least 1 number character'
    return validation_result


def validate_email(email):
    return re.fullmatch(email_regex, email)


def caller():
    return validate_password('')
