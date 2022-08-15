# posts/tests/test_models.py
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test-slug',
            description='Test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для тестирования записей модели.',
            group=cls.group
        )

    def test_post_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__"""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_post_verbose_names(self):
        """Проверяем, что verbose_name полей совпадает с ожидаемым"""
        post = PostModelTest.post
        field_verboses = {
            'group': 'Группа',
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_post_help_text(self):
        """Проверяем, help_text полей совпадает с ожидаемым"""
        post = PostModelTest.post
        field_help_texts = {
            'group': 'Группа, к которой будет относиться пост',
            'text': 'Введите текст поста'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test-slug',
            description='Test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для тестирования комментариев.',
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий для проверки.'
        )

    def test_comment_models_have_correct_object_names(self):
        """Проверяем, что у модели корректно работает __str__"""
        comment = CommentModelTest.comment
        expected_object_name = comment.text[:20]
        self.assertEqual(expected_object_name, str(comment))

    def test_comment_verbose_names(self):
        """Проверяем, что verbose_name полей совпадает с ожидаемым"""
        comment = CommentModelTest.comment
        field_verboses = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Текст комментария',
            'created': 'Дата публикации',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected)

    def test_comment_help_text(self):
        """Проверяем, что help_text полей совпадает с ожидаемым"""
        comment = CommentModelTest.comment
        field_help_texts = {
            'post': 'Пост, к которому относится комментарий',
            'text': 'Введите текст комментария'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).help_text, expected)


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='follower')
        cls.following = User.objects.create_user(username='following')
        cls.follow = Follow.objects.create(
            user=cls.follower,
            author=cls.following
        )

    def test_follow_models_have_correct_object_names(self):
        """Проверяем, что у модели корректно работает __str__"""
        follow = FollowModelTest.follow
        expected_object_name = (f'Подписка {FollowModelTest.follower.username}'
                                f' на {FollowModelTest.following.username}')
        self.assertEqual(expected_object_name, str(follow))

    def test_follow_comment_verbose_names(self):
        """Проверяем, что verbose_name полей совпадает с ожидаемым"""
        follow = FollowModelTest.follow
        field_verboses = {
            'user': 'Пользователь',
            'author': 'Автор',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    follow._meta.get_field(value).verbose_name, expected)
