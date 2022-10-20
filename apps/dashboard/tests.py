from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.authentication.models import SystemUser
from apps.company.models import Company
from apps.investment.models import InvestmentProfile
from apps.learning_board.models import BlogPost, BlogCategory
from apps.system_settings.models import SmtpConfig, SocialApp, SystemOption
from utils.test_utils import ViewSetPITestMixin, DashboardAPITestMixin, TestUtils


class DashboardUserTestTest(ViewSetPITestMixin, APITestCase):
    fixtures = TestUtils.custom_initial_test_fixture('dashboard_users')
    base_name = 'dashboard_users'
    query_set = SystemUser.objects.filter(role='admin')
    test_data: dict = {
        'first_name': "admin2",
        'last_name': "admin_last",
        'email': "admin2@email.com",
        'password': "Apple123#",
    }

    def test_sign_in(self):
        credential1 = {
            'email': 'email1@salam.com',
            'password': 'Apple123#'
        }
        credential2 = {
            'email': 'email2@salam.com',
            'password': 'Apple123#'
        }
        credential3 = {
            'email': 'email3@salam.com',
            'password': 'Apple123#'
        }
        SystemUser.objects.create_user_with_email(**credential1, role='admin', is_verified=True)
        response = self.client.post(reverse('dashboard_users-sign_in'),
                                    data=credential1, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        SystemUser.objects.create_user_with_email(**credential2, role='client', is_verified=True)
        response = self.client.post(reverse('dashboard_users-sign_in'),
                                    data=credential2, format='json')
        self.assertTrue(response.status_code >= 400 and response.status_code <= 499)

        SystemUser.objects.create_user_with_email(**credential3, role='admin', is_verified=False)
        response = self.client.post(reverse('dashboard_users-sign_in'),
                                    data=credential3, format='json')
        self.assertTrue(response.status_code >= 400 and response.status_code <= 499)

    def test_me_profile(self):
        self.set_credential(self)
        response = self.client.get(reverse('dashboard_users-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_profile(self):
        data = {
            'first_name': "Ahmad",
            'last_name': "Ahmadian",
            'email': "a1@gmail.com",
        }
        user, _ = self.set_credential(self)
        response = self.client.patch(reverse('dashboard_users-me'), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(user.first_name, data['first_name'])
        self.assertNotEqual(user.last_name, data['last_name'])
        self.assertNotEqual(user.email, data['email'])

    def test_change_password(self):
        user, cred = self.set_credential(self)
        new_cred = {
            'current_password': cred['password'],
            'new_password': "Salam123#",
        }
        response = self.client.post(reverse('dashboard_users-change_pass'), new_cred, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = SystemUser.objects.get(id=user.id)
        self.assertTrue(user.check_password(new_cred['new_password']))


class BlogTest(ViewSetPITestMixin, DashboardAPITestMixin, APITestCase):
    fixtures = TestUtils.custom_initial_test_fixture(['dashboard_blog', 'dashboard_users', 'dashboard_blog_category'])
    base_name = 'dashboard_blog'
    query_set = BlogPost.objects.all()

    test_data = None

    def get_test_data_create(self):
        user = SystemUser.objects.last().id
        category_id = BlogCategory.objects.last().id
        data = {
            "author": user,
            "created_at": "2022-04-07T07:12:39.023Z",
            "modified_at": "2022-04-07T07:12:39.023Z",
            "title": "Edge writer so thus value. Prepare rather window.\nSuch grow class human money. Least single approach tough result.\nLate city according sound.\nHe create people hospital space seem.",
            "category": category_id,
            "excerpt": "Nice full parent trade lawyer name.",
            "raw_content": "Member themselves such range team.",
            "content": "Low Mrs listen design.",
            "post_status": "draft",
            "comment_status": "close"
        }
        return data

    def get_test_data_update(self):
        return self.get_test_data_create()


class BlogCategoryTest(ViewSetPITestMixin, DashboardAPITestMixin, APITestCase):
    fixtures = TestUtils.custom_initial_test_fixture(['dashboard_blog_category'])
    base_name = 'dashboard_blog_category'
    query_set = BlogCategory.objects.all()
    test_data: dict = {
        'name': "test"
    }


class SmtpConfigTest(ViewSetPITestMixin, DashboardAPITestMixin, APITestCase):
    fixtures = TestUtils.custom_initial_test_fixture('email_smtp')
    base_name = 'dashboard_email_server'
    query_set = SmtpConfig.objects.all()
    test_data: dict = {
        "use_tls": True,
        "host": "smtp.gmail.com",
        "port": 587,
        "host_user": "noreplay.earlybird@gmail.com",
        "host_password": "iyjqqfpdodaetyrf",
        "use_ssl": False,
        "default": True,
        "used_for": "confirm_mail"
    }


class SocialAppTest(ViewSetPITestMixin, DashboardAPITestMixin, APITestCase):
    fixtures = TestUtils.custom_initial_test_fixture('social_app')
    base_name = 'dashboard_social_app'
    query_set = SocialApp.objects.all()
    test_data: dict = {
        "provider": "google",
        "client_id": "671922347867-5aeg3ltqsi7prbnq9sshsrfghl47mj6m.apps.googleusercontent.com",
        "client_secret": "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",
    }


class SystemOptionTest(ViewSetPITestMixin, DashboardAPITestMixin, APITestCase):
    fixtures = TestUtils.custom_initial_test_fixture('system_options')
    base_name = 'dashboard_system_option'
    query_set = SystemOption.objects.all()
    lookup_field = 'option_name'
    test_data: dict = {
        "option_name": "web_logo",
        "option_value": "noreplay.earlybird@gmail.com",
        "context": "server"
    }


class IdentityVerificationTest(APITestCase):
    def test_identity_record_created(self):
        user = SystemUser.objects.create_user_with_email(email='salam@gmail', password="Apple123#")
        identity = getattr(user, 'identity', None)
        self.assertIsNotNone(identity)
        self.assertEqual(identity.verification_status, 'pre_pending')
        ViewSetPITestMixin.set_credential(self)
        response = self.client.get(reverse('dashboard_verification-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('dashboard_verification-detail', args=(identity.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DashboardInvestmentProfileTest(APITestCase):
    test_data = {
        "investor_id_number": "32145",
        "investor_name": "alokozay",
        "investor_email": "alkozay@gmail.com",
        "investor_address": "herat",
        "investor_phone": "0799"}

    def test_investment(self):
        user = SystemUser.objects.create_user_with_email(email='salam@gmail', password="Apple123#")
        invest_profile = InvestmentProfile.objects.create(**self.test_data, user=user
                                                          )
        qs = InvestmentProfile.objects.all()
        self.assertEqual(qs.count(), 1)
        ViewSetPITestMixin.set_credential(self)
        response = self.client.get(reverse('dashboard_investment-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('dashboard_investment-detail', args=(invest_profile.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DashboardCompanyTest(APITestCase):
    test_data = {
        "company_name": "sadfasf",
        "entrepreneur_name": ['asdfasd', 'asdf'],
        "website": "asdfasdf",
        "email": "salam@gmail.com",
        "address": "asdfasdf",
        "phone_number": "asdfasdf",
        "github": None,
    }

    def test_company(self):
        user = SystemUser.objects.create_user_with_email(email='salam@gmail', password="Apple123#")
        company_profile = Company.objects.create(**self.test_data, user=user
                                                 )
        qs = Company.objects.all()
        self.assertEqual(qs.count(), 1)
        ViewSetPITestMixin.set_credential(self)
        response = self.client.get(reverse('dashboard_company-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('dashboard_company-detail', args=(company_profile.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
