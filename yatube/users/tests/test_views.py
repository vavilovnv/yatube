# users/tests/test_views.py
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_users_page_accessible_by_name(self):
        """Проверка, что URL доступен по namespace"""
        namespaces = [
            'users:login',
            'users:signup'
        ]
        for namespace in namespaces:
            with self.subTest(address=namespace):
                response = self.guest_client.get(reverse(namespace))
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_users_page_uses_correct_template(self):
        """При запросе к namespace применяется соответствующий шаблон"""
        namespaces_templates = {
            'users:login': 'users/login.html',
            'users:signup': 'users/signup.html'
        }
        for namespace, template in namespaces_templates.items():
            with self.subTest(address=namespace):
                response = self.guest_client.get(reverse(namespace))
                self.assertTemplateUsed(response, template)
