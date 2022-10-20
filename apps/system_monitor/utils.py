import datetime
import os
import uuid

from cryptography.fernet import Fernet
from django.conf import settings
from django.core import management

from .models import Backup


def get_file_size(file):
    '''
        gets the size of given file using stat function of os module
    '''
    return os.stat(file).st_size


def create_backup(note='', media_backup=True, created_by=None):
    '''
    This function back ups data and media file of a project
    For security insurance data files which are credentials, are encrypted
    It takes an optional upload_to_google_drive parameter if true, it uploads data backup file to google drive
    '''

    # making a unique file path for each data and media file
    now = datetime.datetime.now()
    date = now.date()
    time = f'{str(now.hour)}:{str(now.minute)}:{str(now.second)}'
    unique_id = uuid.uuid4()
    relative_data_file_path = f'{created_by}/data/{settings.BACKUP_FILE_PREFIX}-{unique_id}-{date}-{time}-data.psql'
    relative_media_file_path = f'{created_by}/media/{settings.BACKUP_FILE_PREFIX}-{unique_id}-{date}-{time}-media.tar'

    # using django management command to backup data and media using django-dbbackup
    # for more info about django management commands visit: https://docs.djangoproject.com/en/3.2/ref/django-admin/#running-management-commands-from-your-code
    management.call_command(
        'dbbackup', output_filename=relative_data_file_path)
    if media_backup:
        management.call_command(
            'mediabackup', output_filename=relative_media_file_path
        )

    # encypting generated backup file using python cryptography packge
    # for more info visit: https://pypi.org/project/cryptography/
    absolute_data_file_path = f'{settings.BACKUP_PATH}{relative_data_file_path}'
    # key = Fernet.generate_key()
    key = settings.BACKUP_KEY
    fernet_obj = Fernet(key)
    with open(str(absolute_data_file_path), 'rb') as file:
        file_data = file.read()
        encrypted_data = fernet_obj.encrypt(file_data)

    with open(str(absolute_data_file_path), 'wb') as file:
        file.write(encrypted_data)

        # get dat file size in bytes
    file_size_in_bytyes = get_file_size(absolute_data_file_path)
    backup_object = Backup(
        note=note,
        db_file_size=file_size_in_bytyes,
        db_file=relative_data_file_path,
        created_by_id=created_by)
    if media_backup:
        absolute_media_file_path = f'{settings.BACKUP_PATH}{relative_media_file_path}'
        media_file_size_in_bytyes = get_file_size(absolute_media_file_path)
        backup_object.media_file = relative_media_file_path
        backup_object.media_file_size = media_file_size_in_bytyes
    backup_object.save()
    return backup_object


def restore_data_file(data_file_path):
    fernet_object = Fernet(settings.BACKUP_KEY)
    with open(data_file_path, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = fernet_object.decrypt(encrypted_data)
    with open(data_file_path, 'wb') as f:
        f.write(decrypted_data)
    management.call_command("dbrestore", input_path=data_file_path,
                            interactive=False)
    os.remove(data_file_path)


def restore_media_file(media_file_path):
    management.call_command("mediarestore", input_path=media_file_path, uncompress=False,
                            interactive=False)
    os.remove(media_file_path)
    return True
