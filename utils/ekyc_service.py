import requests


def verify_client(file_data: dict, data={}, api_key='defd4a864c4049e7b5f9b9ed3edc032e'):
    verify_url = 'https://ekyc.mdcsoftware.com.vn/api/v2/verify'
    headers = {
        'api-key': api_key
    }
    response = requests.post(verify_url, headers=headers, data=data, files=file_data)
    return response
