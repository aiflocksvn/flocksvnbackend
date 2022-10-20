import json

import requests

from apps.dashboard.models import IdentityVerification
from apps.media_center.models import Media
from utils.auths import basic_auth_value


class Jumio:
    pass


def _jumio_initial_url_request(data, credential=None, base_url=None, headers: dict = {}):
    if not base_url:
        base_url = 'https://core-sgp.jumio.com/api/v4/initiate'
    headers.setdefault('Accept', 'application/json')
    headers.setdefault('Content-Type', 'application/json')
    headers.setdefault('User-Agent', 'customer-portal')
    if credential:
        headers.setdefault('Authorization', basic_auth_value(**credential))
    elif not headers.get('Authorization', None):
        raise AttributeError('please add credential of jumio service')
    data = json.dumps(data)
    response = requests.post(base_url, headers=headers, data=data)
    return response


def generate_jumio_verification_url(customer_internal_red, user_ref, locale='en'):
    """
    workflowId
    Value	Verification type	Capture method
    100	    ID only	            camera + upload
    101	    ID only	            camera only
    102	    ID only	            upload only
    200	    ID + Identity	    camera + upload
    201	    ID + Identity	    camera only

    202	    ID + Identity	    upload only   Note Working
    """
    base_url = 'https://core-sgp.jumio.com/api/v4/initiate'
    credential = {
        'username': "4247f9d9-3883-4438-844b-fcb4a0cc00fe",
        "password": "upGwRtJygOgXj3xlEh6HRA14qwNCUDlB"
    }
    data = {
        "customerInternalReference": str(customer_internal_red),
        "userReference": str(user_ref),
        "workflowId": 202,
        "locale": locale,
        'tokenLifetimeInMinutes': 6
    }

    response = _jumio_initial_url_request(credential=credential, base_url=base_url, data=data)

    return response


def set_final_verification_status(validate_data: dict):
    id_verification = validate_data['document']['status']

    if id_verification == 'APPROVED_VERIFIED':

        identity_verification = validate_data['verification'].get('identityVerification', None)
        if identity_verification:
            if (identity_verification['similarity'] == "MATCH") and (identity_verification['validity'] == 'true'):
                validate_data['verification_status'] = IdentityVerification.DONE

            else:
                validate_data['verification_status'] = IdentityVerification.FAILED

        else:
            validate_data['verification_status'] = IdentityVerification.DONE
    else:
        validate_data['verification_status'] = IdentityVerification.FAILED


def _fetch_jumio(url, **kwargs):
    credential = {
        'username': "4247f9d9-3883-4438-844b-fcb4a0cc00fe",
        "password": "upGwRtJygOgXj3xlEh6HRA14qwNCUDlB"
    }

    headers = {
        'Authorization': basic_auth_value(**credential)
    }
    responses = requests.get(url, headers=headers, **kwargs)
    return responses


def retrieve_transaction_detail(key):
    details_url = f'https://core-sgp.jumio.com/api/netverify/v2/scans/{key}/data/'
    result = _fetch_jumio(details_url)
    return result


def retrieve_transaction_images(key):
    images_url = f'https://core-sgp.jumio.com/api/netverify/v2/scans/{key}/images'
    result = _fetch_jumio(images_url)
    return result


def download_identity_image(url):
    return _fetch_jumio(url, stream=True)


def upload_media_center(image_raw, user_id):
    import tempfile
    img_temp = tempfile.NamedTemporaryFile(delete=True)
    img_temp.write(image_raw)
    img_temp.flush()
    media = Media(upload_by_id=user_id, security_permission='admin')
    media.file.save('test_name.jpeg', img_temp, save=True)
    media.save()
    return media
