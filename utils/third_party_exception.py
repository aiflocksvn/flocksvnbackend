from utils.exceptions import GeneralBadRequest


def google_error_parse(errors: dict):
    errors = errors['error']
    try:
        message_codes, messages = str(errors['message']).split(':')
    except ValueError:
        message_codes = messages = errors['message']
    raise GeneralBadRequest(detail=messages, code=message_codes)
