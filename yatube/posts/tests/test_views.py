import shutil
import tempfile

from django.conf import settings
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache
from posts.models import Group, Post, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('name')
        cls.group = Group.objects.create(slug='slug')
        cls.post = Post.objects.create(author=cls.user,
                                       group=cls.group)
        cls.templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': 'slug'},
            )
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user1 = User.objects.create_user(username='follower')
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)
        self.user2 = User.objects.create_user(username='notfollower')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        cache.clear()

    def posts_check_all_fields(self, post):
        """Корректность полей поста."""
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)
            self.assertEqual(post.image, self.post.image)

    def test_posts_pages_use_correct_template(self):
        """Использует ли адрес URL соответствующий шаблон."""
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_context_index_template(self):
        """
        Формирование шаблона index с верным контекстом.
        Отображается ли созданный пост на главной странице.
        """
        response = self.authorized_client.get(reverse('posts:index'))
        self.posts_check_all_fields(response.context['page_obj'][0])
        last_post = response.context['page_obj'][0]
        self.assertEqual(last_post, self.post)

    def test_posts_context_group_list_template(self):
        """
        Формирование шаблона group_list с верным контекстом.
        Отображается ли созданный пост на странице группы.
        """
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug},
            )
        )
        test_group = response.context['group']
        self.posts_check_all_fields(response.context['page_obj'][0])
        test_post = str(response.context['page_obj'][0])
        self.assertEqual(test_group, self.group)
        self.assertEqual(test_post, str(self.post))

    def test_posts_context_post_create_template(self):
        """
        Формирование шаблона create_post с верным контекстом.
        """
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_posts_context_post_edit_template(self):
        """
        Формирование шаблона post_edit с верным контекстом.
        """
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id},
            )
        )
        form_fields = {'text': forms.fields.CharField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_context_profile_template(self):
        """
        Формирование шаблона profile с верным контекстом.
        """
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            )
        )
        profile = {'username': self.post.author}
        for value, expected in profile.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, expected)
        self.posts_check_all_fields(response.context['page_obj'][0])
        test_page = response.context['page_obj'][0]
        self.assertEqual(test_page, self.user.posts.all()[0])

    def test_posts_context_post_detail_template(self):
        """
        Формирование шаблона post_detail с верным контекстом.
        """
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id},
            )
        )
        profile = {'post': self.post}
        for value, expected in profile.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, expected)

    def test_posts_not_from_foreign_group(self):
        """
        Попадение нового поста в чужую группу
        """
        response = self.authorized_client.get(reverse('posts:index'))
        self.posts_check_all_fields(response.context['page_obj'][0])
        post = response.context['page_obj'][0]
        group = post.group
        self.assertEqual(group, self.group)

    def test_index_page_cache_correct(self):
        """Кеш главной страницы работает правильно."""
        response = self.authorized_client.get(reverse('posts:index'))
        temp_post = Post.objects.get(id=1)
        temp_post.delete()
        new_response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, new_response.content)
        cache.clear()
        new_new_response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, new_new_response.content)

    def test_authorized_user_can_follow_unfollow(self):
        """Авторизованный пользователь может подписываться на других
        пользователей и удалять их из подписок."""
        author = self.user
        user = self.user1
        self.authorized_client1.get(
            reverse('posts:profile_follow',
                    kwargs={'username': author.username})
        )
        self.assertTrue(Follow.objects.filter(user=user,
                                              author=author).exists())
        self.authorized_client1.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': author.username})
        )
        self.assertFalse(Follow.objects.filter(user=user,
                                               author=author).exists())

    def test_post_appears_in_feed(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан."""
        author = self.user
        user1 = self.user1
        user2 = self.user2
        self.authorized_client1.get(
            reverse('posts:profile_follow',
                    kwargs={'username': author.username})
        )
        authors1 = Follow.objects.values_list('author').filter(user=user1)
        post_list1 = Post.objects.filter(author__in=authors1)
        post1 = Post.objects.create(author=author,)
        self.assertIn(post1, post_list1)
        authors2 = Follow.objects.values_list('author').filter(user=user2)
        post_list2 = Post.objects.filter(author__in=authors2)
        self.assertNotIn(post1, post_list2)


class PostsPaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('Тестовый пользователь')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        for count in range(13):
            cls.post = Post.objects.create(author=cls.user)
        cache.clear()

    def test_posts_if_first_page_has_ten_records(self):
        """Содержание на первой страницы 10 записей."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page_obj').object_list), 10)

    def test_posts_if_second_page_has_three_records(self):
        """Содержание на второй странице 3-х записей."""
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context.get('page_obj').object_list), 3)
