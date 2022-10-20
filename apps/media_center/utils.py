import os


def path_and_rename(instance, filename):

    upload_to = ''
    if instance.security_permission == instance.PUBLIC:
        upload_to = 'public/'

    ext = filename.split('.')[-1]
    upload_to += f'{instance.upload_by.pk}'
    filename = '{}.{}'.format(instance.pk, ext)

    return os.path.join(upload_to, filename)


def detect_file_type(content_type):
    pass
