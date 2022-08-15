# about/tests/test_urls.py
from django.test import Client, TestCase
from http import HTTPStatus


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_uses_correct_template(self):
        """Проверка использования корректных шаблонов
        для адреса /about/author/."""
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/'
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности страниц по переданным адресам"""
        addresses = [
            '/about/author/',
            '/about/tech/'
        ]
        for address in addresses:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)
