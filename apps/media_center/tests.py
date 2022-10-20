from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from utils.test_utils import AuthMixin


class MediaCenterTest(AuthMixin, APITestCase):
    upload_url = reverse('media_upload')

    def test_upload_filed(self):
        file = open('utils/test_upload_file.jpeg', 'rb')
        response = self.client.post(self.upload_url, data={'file': file})


    def test_validation(self):
        # self.client.
        pass

    def test_filesystem(self):
        pass
