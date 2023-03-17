from django.test import TestCase, Client
from posts.models import Post, Group, User


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user('name')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(slug='slug')
        cls.post = Post.objects.create(author=cls.user)
        cls.template_404 = 'core/404.html'

    def test_home_url_exists_at_desired_location(self):
        """Главная страница доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_home_url_exists_at_desired_location2(self):
        """Страница /group/<slug:slug>/ доступна любому пользователю."""
        response = self.guest_client.get('/group/slug/')
        self.assertEqual(response.status_code, 200)

    def test_urls_authorized_user(self):
        """Доступ страниц авторизованному пользователю."""
        url_names = {
            '/profile/<str:username>/': '/profile/name/',
            '/posts/<int:post_id>/': f'/posts/{self.post.id}/',
            '/posts/<int:post_id>/edit/': f'/posts/{self.post.id}/edit/',
            '/create/': '/create/',
        }
        for url_adress, url_test_adress in url_names.items():
            with self.subTest(url_adress=url_adress):
                response = self.authorized_client.get(url_test_adress)
                self.assertEqual(response.status_code, 200)

    def test_urls(self):
        """Соответствие шаблонов адресам"""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/slug/': 'posts/group_list.html',
            '/profile/name/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page(self):
        """Запрос к несуществующей странице вернет ошибку 404
            и при этом будет использован кастомный шаблон."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, self.template_404)
