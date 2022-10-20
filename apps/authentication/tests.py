# Create your tests here.
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.authentication.models import SystemUser
from utils.test_utils import TestUtils, CustomAPITestCase
from utils.token_utils import CustomToken


class EmailTest(CustomAPITestCase):
    fixtures = ['run/fixtures/test_data/email_smtp.json']
    sign_up_url = reverse('email_sign_up')
    sign_in_url = reverse('email_sing_in')
    verify_url = reverse('email_verify')
    resend_verify_url = reverse('email_resend_verify')

    def _sing_up_email(self, data):
        response = self.client.post(self.sign_up_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def _sing_in_email(self, data):
        response = self.client.post(self.sign_in_url, data={'email': data['email'], 'password': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post(self.sign_in_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _database_user(self, data):
        UserModel = get_user_model()
        user_instance: SystemUser = UserModel.objects.last()
        self.assertEqual(user_instance.first_name, data['first_name'])
        self.assertEqual(user_instance.last_name, data['last_name'])
        self.assertEqual(user_instance.email, data['email'])
        self.assertTrue(user_instance.check_password(data['password']))
        self.assertFalse(user_instance.is_verified)
        return user_instance

    def _outbox_verify_mail(self):
        mail_box = mail.outbox
        self.assertEqual(len(mail_box), 1)
        # token validation
        email_message = mail_box.pop()
        self.assertIsInstance(email_message, EmailMultiAlternatives)
        email_body, _ = email_message.alternatives[0]
        soup = BeautifulSoup(email_body, "html.parser")
        url = soup.find("a", test_id='token_route')['href']
        parsed_url = urlparse(url).query
        token_value = parse_qs(parsed_url)['token'][0]
        is_valid, payload = CustomToken.validate_token(token_value, CustomToken.EMAIL_VERIFY)
        self.assertTrue(is_valid)
        return token_value

    def _resent_verify_email(self, data):
        response = self.client.post(self.resend_verify_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._outbox_verify_mail()

    def _verify_email(self, token_value, user_instance):
        response = self.client.post(self.verify_url, data={'token': token_value}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_instance.refresh_from_db()
        self.assertTrue(user_instance.is_verified)

    def test_email_auth(self):
        data = {
            'password': 'Apple123#',
            'email': 'noreplay.earlybird@gmail.com',
            'first_name': 'noreplay.earlybird@gmail.com',
            'last_name': 'noreplay.earlybird@gmail.com',
        }
        self._sing_up_email(data)
        user_instance = self._database_user(data)
        token_value = self._outbox_verify_mail()
        self._resent_verify_email(data)
        self._verify_email(token_value=token_value, user_instance=user_instance)
        self._sing_in_email(data)

    def test_required_fields(self):
        sign_up_url = self.sign_up_url
        response = self.client.post(sign_up_url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        required_field = TestUtils.render_required_fields(response.data)
        self.assertListEqual(required_field, ['email', 'password'])

    def test_email_unique(self):
        sign_up_url = self.sign_up_url
        data1 = {
            'password': 'Apple123#',
            'email': 'noreplay.earlybird@gmail.com',
            'first_name': 'noreplay.earlybird@gmail.com',
            'last_name': 'noreplay.earlybird@gmail.com',
        }
        self.client.post(sign_up_url, data=data1, format='json')
        response2 = self.client.post(sign_up_url, data=data1, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)


class JwtTest(APITestCase):
    def test_refresh_token(self):
        pass

    def test_black_list_token(self):
        pass

    def test_custom_token(self):
        pass


class OAuthTest(APITestCase):
    def test_google(self):
        pass

    def test_facebook(self):
        pass


class PasswordResetTest(APITestCase):
    fixtures = TestUtils.custom_initial_test_fixture('email_smtp')

    def validate_reset_mail(self):
        mail_box = mail.outbox
        self.assertEqual(len(mail_box), 1)
        email_message = mail_box.pop()
        self.assertIsInstance(email_message, EmailMultiAlternatives)
        email_body, _ = email_message.alternatives[0]
        soup = BeautifulSoup(email_body, "html.parser")
        url = soup.find("a", test_id='token_route')['href']
        parsed_url = urlparse(url).query
        token_value = parse_qs(parsed_url)['token'][0]
        is_valid, payload = CustomToken.validate_token(token_value, CustomToken.EMAIL_RESET_PASSWORD)
        self.assertTrue(is_valid)
        return token_value

    def test_password_reset(self):
        data = {
            'email': "test@mail.com",
            'password': "Apple123#",
        }
        user = SystemUser.objects.create_user_with_email(**data)
        response = self.client.post(reverse('email_reset_password'), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = self.validate_reset_mail()
        new_data = {'token': token, 'password': "Salam1234"}
        response = self.client.post(reverse('email_reset_password_confirm'),
                                    data=new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = SystemUser.objects.get(id=user.id)
        self.assertTrue(user.check_password(new_data['password']))

        response = self.client.post(reverse('email_reset_password_confirm'),
                                    data=new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileTest(APITestCase):
    def test_profile(self):
        pass
