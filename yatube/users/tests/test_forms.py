# users/tests/test_forms.py
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse, reverse_lazy

User = get_user_model()


class FormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='test_user')

    def setUp(self):
        self.guest_client = Client()

    def test_create_user_from_signup_form(self):
        """При заполнении формы reverse('users:signup')
        создаётся новый пользователь"""
        users_amount = User.objects.count()
        user_data = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'username': 'new_user',
            'email': 'newuser@mail.ru',
            'password1': '5tgbBGT%',
            'password2': '5tgbBGT%',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=user_data,
            follow=True
        )
        self.assertRedirects(response, reverse_lazy('posts:posts_index'))
        self.assertEqual(users_amount + 1, User.objects.count())
