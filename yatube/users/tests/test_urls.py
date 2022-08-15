# users/tests/test_urls.py
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from http import HTTPStatus

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_anonimous_users_url_uses_correct_template(self):
        """URL-адреса users используют корректные шаблоны
        для незарегистрированных пользователей"""
        templates_url_names = {
            'users/login.html': '/auth/login/',
            'users/signup.html': '/auth/signup/'
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_author_url_exists_at_desired_location(self):
        """Проверка доступности адресов приложения users"""
        adresses = [
            '/auth/login/',
            '/auth/signup/'
        ]
        for address in adresses:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)
