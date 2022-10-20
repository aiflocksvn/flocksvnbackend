from base64 import b64encode


def credential_to_b64encode(username, password):
    return f'{b64encode(f"{username}:{password}".encode()).decode()}'


def basic_auth_value(username, password):
    return f'Basic {credential_to_b64encode(username, password)}'
