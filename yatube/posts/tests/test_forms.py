import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache

from posts.forms import PostForm
from posts.models import Group, Post, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user('name')
        cls.group = Group.objects.create(slug='slug')
        cls.post = Post.objects.create(author=cls.author)
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        cache.clear()

    def test_posts_forms_create_post(self):
        """Cоздание формы поста."""
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertEqual(Post.objects.count(), 2)
        self.assertTrue(Post.objects.filter(
            text='Текст поста',
            group=self.group.id,
            image=self.post.image
        ).exists())

    def test_posts_forms_edit_post(self):
        """Редактирование поста."""
        form_data = {
            'text': 'Новый текст поста',
            'group': self.group.id,
        }
        self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id},
        ), data=form_data)
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id},
        ))
        self.assertEqual(response.context['post'].text, 'Новый текст поста')
        self.assertTrue(Post.objects.filter(
            text='Новый текст поста',
            group=self.group.id,
        ).exists())

    def test_creating_post_with_image(self):
        """Создание записи поста с вложенной картинкой"""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст поста с картинкой',
            'group': self.group.id,
            'image': uploaded
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertTrue(Post.objects.filter(
            text='Текст поста с картинкой',
            group=self.group.id,
            image='posts/small.gif'
        ).exists())

    def test_add_comment_authorized_client(self):
        """Запись комментария у авторизованного пользователя."""
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertTrue(Comment.objects.filter(id=1).exists())

    def test_add_comment_guest_client(self):
        """Отсутствие записи комментария у неавторизованного пользователя."""
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertFalse(Comment.objects.filter(id=1).exists())
