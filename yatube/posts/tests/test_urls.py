# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache

from http import HTTPStatus
from os import path

from posts.models import Post, Group

User = get_user_model()

HTTP_STATUS_OK = HTTPStatus.OK.value


def get_description_http_response(response):
    return (f'{HTTPStatus(response.status_code).phrase} - '
            f'{HTTPStatus(response.status_code).description}')


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.another_user = User.objects.create_user(username='test_user2')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(self.another_user)
        cache.clear()

    def test_urls_exists(self):
        """Проверяем страницы доступные любому пользователю:
        /,
        /group/<slug:slug>/,
        /profile/<str:username>/,
        posts/<int:post_id>/"""
        url_names = [
            '/',
            f'/group/{PostURLTests.post.group.slug}/',
            f'/profile/{PostURLTests.post.author}/',
            f'/posts/{PostURLTests.post.id}/',
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTP_STATUS_OK,
                    get_description_http_response(response)
                )

    def test_url_post_edit_exists_if_user_is_author(self):
        """Страница /posts/<int:post_id>/edit/ доступна автору поста."""
        address = f'/posts/{PostURLTests.post.id}/edit/'
        response = self.authorized_client.get(address)
        self.assertEqual(
            response.status_code,
            HTTP_STATUS_OK,
            get_description_http_response(response)
        )

    def test_redirect_url_if_user_is_not_author(self):
        """Страница /posts/<int:post_id>/edit/ недоступна не автору поста."""
        address = f'/posts/{PostURLTests.post.id}/edit/'
        guest_address = f'/posts/{PostURLTests.post.id}/'
        response = self.another_authorized_client.get(address)
        self.assertRedirects(response, guest_address)

    def test_redirect_url_post_edit_if_user_is_anonimous(self):
        """Страница /posts/<int:post_id>/edit/ недоступна
        не авторизованному пользователю."""
        address = f'/posts/{PostURLTests.post.id}/edit/'
        guest_address = (f'/auth/login/?next=/posts/'
                         f'{PostURLTests.post.id}/edit/')
        response = self.guest_client.get(address)
        self.assertRedirects(response, guest_address)

    def test_url_create_exists_if_user_is_auth(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(
            response.status_code,
            HTTP_STATUS_OK,
            get_description_http_response(response)
        )

    def test_non_exists_url(self):
        """Страница /unexisting_page/ недоступна любому пользователю."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            get_description_http_response(response)
        )

    def test_url_comment_exists_if_user_is_authorized(self):
        """Страница /posts/<int:post_id>/comment/ доступна
        зарегистрированному пользователю."""
        address = f'/posts/{PostURLTests.post.id}/comment/'
        response = self.authorized_client.get(address)
        self.assertEqual(
            response.status_code,
            HTTP_STATUS_OK,
            get_description_http_response(response)
        )

    def test_redirect_url_comment_if_user_is_anonimous(self):
        """При попытке незарегистрированного пользователя обратиться
        к странице /posts/<int:post_id>/comment/ сработает редирект
        на страницу авторизации."""
        address = f'/posts/{PostURLTests.post.id}/comment/'
        response = self.guest_client.get(address)
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND,
            get_description_http_response(response)
        )

    def test_urls_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        template = path.join('posts', 'group_list.html')
        templates_url_names = {
            path.join('posts', 'index.html'): '/',
            path.join('posts', 'group_list.html'):
            f'/group/{PostURLTests.post.group.slug}/',
            path.join('posts', 'profile.html'):
            f'/profile/{PostURLTests.post.author}/',
            path.join('posts', 'post_detail.html'):
            f'/posts/{PostURLTests.post.id}/',
            path.join('posts', 'create_post.html'): '/create/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
