# posts/tests/test_views.py
import shutil
import tempfile

from os import path
from random import randint
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.conf import settings
from django.urls import reverse
from django import forms
from posts.models import Post, Group, Comment, Follow

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-group',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Тестовый комментарий'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    # Вспомогательная функция для проверки полей из контекста
    # и тестового поста
    def check_object_fields(self, post_context, post_test):
        fields = {
            post_context.text: post_test.text,
            post_context.pub_date: post_test.pub_date,
            post_context.author: post_test.author,
            post_context.group: post_test.group,
            post_context.image: post_test.image,
        }
        for context_field, post_field in fields.items():
            with self.subTest(context_field=context_field):
                self.assertEqual(context_field, post_field)

    def test_pages_uses_correct_template(self):
        """Проверка того, что во view-функциях используются
        корректные html-шаблоны"""
        templates_pages_names = {
            reverse(
                'posts:posts_index'
            ): path.join('posts', 'index.html'),
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.post.author}
            ): path.join('posts', 'profile.html'),
            reverse(
                'posts:post_create'
            ): path.join('posts', 'create_post.html'),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTests.post.id}
            ): path.join('posts', 'create_post.html'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.post.group.slug}
            ): path.join('posts', 'group_list.html'),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTests.post.id}
            ): path.join('posts', 'post_detail.html'),
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse('posts:posts_index'))
        PostPagesTests.check_object_fields(
            self,
            response.context['page_obj'][0],
            PostPagesTests.post
        )

    def test_group_list_show_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом"""
        response = self.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.post.group.slug}
            )
        )
        PostPagesTests.check_object_fields(
            self,
            response.context['page_obj'][0],
            PostPagesTests.post
        )

    def test_profile_show_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом"""
        response = self.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.post.author}
            )
        )
        PostPagesTests.check_object_fields(
            self,
            response.context['page_obj'][0],
            PostPagesTests.post
        )

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail.html сформирован с правильным контекстом"""
        response = self.guest_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTests.post.id}
            )
        )
        PostPagesTests.check_object_fields(
            self,
            response.context.get('post'),
            PostPagesTests.post
        )

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit.html сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTests.post.id}
            )
        )
        fields_instance = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for field, instance in fields_instance.items():
            with self.subTest(field=field):
                self.assertIsInstance(
                    response.context.get('form').fields.get(field),
                    instance
                )

    def test_post_create_show_correct_context(self):
        """Шаблон post_create.html сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        fields_instance = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for field, instance in fields_instance.items():
            with self.subTest(field=field):
                self.assertIsInstance(
                    response.context.get('form').fields.get(field),
                    instance
                )

    def test_post_with_group_is_exist_on_index_page(self):
        """Проверка наличия поста с указанной группой на странице index.html"""
        self.guest_client.get(
            reverse('posts:posts_index')
        )
        self.assertTrue(
            Post.objects.filter(group=PostPagesTests.group).count() == 1
        )

    def test_post_with_group_is_exist_on_group_list_page(self):
        """Проверка наличия поста с указанной группой на странице
        group_list.html"""
        self.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.post.group.slug}
            )
        )
        self.assertTrue(
            Post.objects.filter(group=PostPagesTests.group).count() == 1
        )

    def test_post_with_group_is_exist_on_profile_page(self):
        """Проверка наличия поста с указанной группой на странице
        profile.html"""
        self.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.post.author}
            )
        )
        self.assertTrue(
            Post.objects.filter(
                group=PostPagesTests.group,
                author=PostPagesTests.post.author
            ).count() == 1
        )

    def test_comment_is_exist_on_post_detail_page(self):
        """Проверка наличия комментария автора на странице post_detail.html"""
        self.guest_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTests.post.id}
            )
        )
        self.assertTrue(
            Comment.objects.filter(
                post=PostPagesTests.post,
                author=PostPagesTests.user,
                text=PostPagesTests.comment.text
            ).count() == 1
        )


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-group',
            description='Тестовое описание для первой группы',
        )
        cls.another_group = Group.objects.create(
            title='test_group2',
            slug='test-group2',
            description='Тестовое описание для второй группы',
        )
        cls.posts = []
        for i in range(1, 14):
            cls.posts.append(
                Post(
                    author=cls.user,
                    text=f'Test post {i} for verification',
                    group=cls.group,
                )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_index_first_page_contains_ten_records(self):
        """Paginator выводит на страницу index.html 10 постов"""
        response = self.client.get(reverse('posts:posts_index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_three_records(self):
        """Paginator выводит на вторую страницу index.html
        остаток из трех постов"""
        response = self.client.get(reverse('posts:posts_index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_records(self):
        """Paginator выводит на страницу group_list.html 10 постов"""
        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_three_records(self):
        """Paginator выводит на вторую страницу group_list.html
        остаток из трех постов"""
        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        """Paginator выводит на страницу profile.html 10 постов"""
        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.user}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_three_records(self):
        """Paginator выводит на вторую страницу profile.html
        остаток из трех постов"""
        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.user}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_contains_zero_records_for_another_group(self):
        """Paginator выводит на страницу group_list.html ноль постов
        если постов с такой группой не создавалось"""
        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.another_group.slug}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 0)


class CacheTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-group',
            description='Тестовое описание группы',
        )
        cls.count_posts = 10
        cls.posts = []
        for i in range(1, cls.count_posts):
            cls.posts.append(
                Post(
                    author=cls.user,
                    text=f'Cool post {i} to test cache',
                    group=cls.group,
                )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def test_index_page_cache(self):
        """Проверка кэширования главной страницы"""
        response = self.guest_client.get(reverse('posts:posts_index'))
        post = Post.objects.get(pk=randint(1, CacheTests.count_posts))
        post.delete()
        # проверяем наличие текста удаленного поста в контенте
        response = self.guest_client.get(reverse('posts:posts_index'))
        self.assertContains(response, post.text)
        # чистим кэш и проверяем, что текст удаленного поста
        # исчез из контента
        cache.clear()
        response = self.guest_client.get(reverse('posts:posts_index'))
        self.assertNotContains(response, post.text)


class FollowTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_follower = User.objects.create_user(
            username='user_follower'
        )
        cls.user_following = User.objects.create_user(
            username='user_following'
        )
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_following,
            text='Cool post to test subscriptions',
            group=cls.group,
        )

    def setUp(self):
        self.auth_client_follower = Client()
        self.auth_client_follower.force_login(self.user_follower)
        self.auth_client_following = Client()
        self.auth_client_following.force_login(self.user_following)

    def test_auth_user_can_follow(self):
        '''Авторизованный пользователь может подписываться на автора'''
        self.auth_client_follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': FollowTests.user_following.username}
            )
        )
        count_following = Follow.objects.all().count()
        self.assertEqual(count_following, 1)

    def test_auth_user_can_unfollow(self):
        '''Авторизованный пользователь может отписаться от автора'''
        self.auth_client_follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': FollowTests.user_following.username}
            )
        )
        self.auth_client_follower.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': FollowTests.user_following.username}
            )
        )
        count_following = Follow.objects.all().count()
        self.assertEqual(count_following, 0)

    def test_subscription_feed(self):
        """Новая запись пользователя появляется в ленте подписчиков
        и не появляется в ленте тех, кто не подписан"""
        Follow.objects.create(
            user=FollowTests.user_follower,
            author=FollowTests.user_following
        )
        response = self.auth_client_follower.get('/follow/')
        posts = response.context['page_obj']
        self.assertEqual(
            posts[0].text,
            'Cool post to test subscriptions'
        )
        # проверяем подписку на собственные посты
        response = self.auth_client_following.get('/follow/')
        self.assertNotContains(
            response,
            'Cool post to test subscriptions'
        )

    def test_follow_yourself(self):
        """Проверка, что нельзя подписаться на самого себя"""
        response = self.auth_client_following.get(
            reverse(
                'posts:profile_follow',
                args={self.user_following}
            )
        )
        self.assertEqual(response.status_code, 302)
