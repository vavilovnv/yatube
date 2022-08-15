# posts/tests/tests_form.py
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings

from posts.models import Post, Group, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_and_redirect(self):
        """При отправке валидной формы со страницы post_create
        создаётся новая запись в базе данных"""
        text_post = 'Тестовый текст для проверки создания поста.'
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        if isinstance(small_gif, bytes):
            uploaded = SimpleUploadedFile(
                name='small.gif',
                content=small_gif,
                content_type='image/gif'
            )
            form_data = {
                'text': text_post,
                'group': PostFormTests.group.id,
                'image': uploaded
            }
        else:
            form_data = {
                'text': text_post,
                'group': PostFormTests.group.id
            }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        filtered_posts = Post.objects.filter(
            text=text_post,
            group=PostFormTests.group,
            author=PostFormTests.user
        )
        # проверяем, что количество постов увеличилось на один
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # проверяем, что пост создался с переданными в форму данными
        self.assertTrue(filtered_posts.exists())
        # проверяем, что созданный пост по дате является последним
        max_post = max(Post.objects.all(), key=lambda p: p.pub_date)
        self.assertTrue(filtered_posts[0].pub_date == max_post.pub_date)
        # проверяем, что созданный пост содержит картинку
        self.assertTrue(filtered_posts[0].image == 'posts/small.gif')
        # проверяем редирект
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostFormTests.user}
            )
        )

    def test_change_post_and_redirect(self):
        """При отправке валидной формы со страницы post_edit
        происходит изменение поста с post_id в базе данных"""
        posts_count = Post.objects.count()
        changed_text = 'Измененный текст для проверки изменения поста.'
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostFormTests.post.id}
            ),
            data={'text': changed_text},
            follow=True
        )
        # проверка того, что новых постов не появилось
        self.assertEqual(Post.objects.count(), posts_count)
        # проверка того, что редирект выполнен
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostFormTests.post.id}
            )
        )
        # проверка того, что тексты в прежнем и измененном посте не совпадают
        post = Post.objects.get(pk=PostFormTests.post.id)
        self.assertTrue(post.text == changed_text)
