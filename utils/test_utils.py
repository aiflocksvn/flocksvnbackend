import os
from uuid import UUID

from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.models import SystemUser


class TestUtils:

    @staticmethod
    def custom_initial_test_fixture(files_name):
        base_pth = settings.INITIAL_TEST_FIXTURES_PATH
        file_list = None
        if type(files_name) == list:
            file_name_list = [item for item in files_name]
            file_list = list(map(lambda x: f'{base_pth}/{x}.json', file_name_list))
        elif type(files_name) == str:
            file_list = [f'{base_pth}/{files_name}.json']
        return file_list

    @staticmethod
    def all_initial_test_fixture():
        base_pth = settings.INITIAL_TEST_FIXTURES_PATH
        files_name = os.listdir(base_pth)
        file_name_list = [item for item in files_name]
        file_list = list(map(lambda x: f'{base_pth}/{x}', file_name_list))
        return file_list

    def render_required_fields(data: dict):
        req_fields = []
        for key, value in data.items():
            if value:
                for item in value:
                    if isinstance(item, ErrorDetail) and item.code == 'required':
                        req_fields.append(key)
        return req_fields


class AuthMixin:
    def setUp(self) -> None:
        user = SystemUser.objects.create_superuser(email='salwam@gmail.com', password='Apple123#')
        refresh = RefreshToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))


class ViewSetPITestMixin:
    lookup_field = 'id'
    request_format = 'json'
    append_credential = True

    base_name = None
    query_set = None
    test_data: dict = None

    def get_latest_object_lookup_value(self):
        last_obj = self.get_queryset().last()
        lookup_field = getattr(last_obj, self.lookup_field)
        if isinstance(lookup_field, UUID):
            lookup_field = str(lookup_field)
        return lookup_field

    def get_test_data_update(self):
        return self.test_data

    def get_list_url(self):
        return reverse(f'{self.base_name}-list')

    def get_detail_url(self, arg):
        return reverse(f'{self.base_name}-detail', args=(arg,))

    def get_queryset(self):
        return self.query_set

    @staticmethod
    def set_credential(self):
        cred = dict(
            email='salwam@gmail.com', password='Apple123#', role='admin'
        )
        user = SystemUser.objects.create_superuser(**cred)
        refresh = RefreshToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
        return user, cred

    def get_test_data_create(self):
        return self.test_data

    def test_create(self, ):
        url = self.get_list_url()
        if self.append_credential:
            self.set_credential(self)
        response = self.client.post(url, data=self.get_test_data_create(), format=self.request_format)
        res_status = response.status_code
        self.assertNotEqual(res_status, status.HTTP_404_NOT_FOUND)
        res_data = response.data
        key = res_data.get(self.lookup_field, None)
        self.assertEqual(res_status, status.HTTP_201_CREATED)
        self.assertTrue(self.get_queryset().filter(**{self.lookup_field: key}))

    def test_read_one(self):
        lookup_field = self.get_latest_object_lookup_value()
        url = self.get_detail_url(lookup_field)
        if self.append_credential:
            self.set_credential(self)
        response = self.client.get(url, fomrat=self.request_format)
        res_status = response.status_code
        self.assertNotEqual(res_status, status.HTTP_404_NOT_FOUND)
        res_data = response.data
        self.assertEqual(res_status, status.HTTP_200_OK)
        self.assertEqual(res_data[self.lookup_field], lookup_field)
        return res_status, res_data

    def test_delete(self):
        lookup_field = self.get_latest_object_lookup_value()
        url = self.get_detail_url(lookup_field)
        if self.append_credential:
            self.set_credential(self)
        response = self.client.delete(url, fomat=self.request_format)
        res_status = response.status_code
        res_data = response.data
        self.assertEqual(res_status, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.get_queryset().filter(**{self.lookup_field: lookup_field}).exists())
        return res_status, res_data

    def test_read_all(self):
        url = self.get_list_url()
        if self.append_credential:
            self.set_credential(self)
        response = self.client.get(url, format=self.request_format)
        res_status = response.status_code
        res_data = response.data
        db_instance_count = self.get_queryset().count()
        self.assertEqual(res_status, status.HTTP_200_OK)
        self.assertEqual(res_data['count'], db_instance_count)
        return res_status, res_data

    def test_update(self):
        lookup_field = self.get_latest_object_lookup_value()
        url = self.get_detail_url(lookup_field)
        data = self.get_test_data_update().copy()
        if self.append_credential:
            self.set_credential(self)
        response = self.client.put(url, data=data, format=self.request_format)
        res_status = response.status_code
        self.assertEqual(res_status, status.HTTP_200_OK)


class CustomAPITestCase(APITestCase):
    pass


class DashboardAPITestMixin:
    def auth_permission(self, url):
        admin_user = SystemUser.objects.create_superuser(email='admin@emial.com', password='Apple123#')
        client_user = SystemUser.objects.create_user_with_email(email='client@email.com', password='Apple123#')
        admin_token = RefreshToken.for_user(admin_user).access_token
        client_token = RefreshToken.for_user(client_user).access_token
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + str(client_token))
        client_token_response = self.client.post(url, format='json')
        self.assertEqual(client_token_response, status.HTTP_401_UNAUTHORIZED)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + str(admin_token))
        admin_token_response = self.client.post(url, format='json')
        self.assertNotEqual(admin_token_response, status.HTTP_401_UNAUTHORIZED)
