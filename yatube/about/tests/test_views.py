# tests/tests/test_views.py
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """Проверка, что URL доступен по namespace"""
        namespaces = [
            'about:author',
            'about:tech'
        ]
        for namespace in namespaces:
            with self.subTest(address=namespace):
                response = self.guest_client.get(reverse(namespace))
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_about_page_uses_correct_template(self):
        """При запросе к namespace применяется соответствующий шаблон"""
        namespaces_templates = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html'
        }
        for namespace, template in namespaces_templates.items():
            with self.subTest(address=namespace):
                response = self.guest_client.get(reverse(namespace))
                self.assertTemplateUsed(response, template)
