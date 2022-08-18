from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_public_posts_urls_exists_at_desired_location(self):
        """Проверка доступности страниц для неавторизованных пользователей."""
        urls_status_codes = {
            '/': HTTPStatus.OK.value,
            f'/group/{self.group.slug}/': HTTPStatus.OK.value,
            f'/profile/{self.user.username}/': HTTPStatus.OK.value,
            f'/posts/{self.post.id}/': HTTPStatus.OK.value,
            'unexisting_page/': HTTPStatus.NOT_FOUND.value,
        }
        for url, status in urls_status_codes.items():
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest_client.get(url).status_code, status)

    def test_post_create_url_exists_authorized_at_desired_location(self):
        """Проверка доступности страницы /create/ авторизованному
        пользователю.
        """
        self.assertEqual(
            self.authorized_client.get('/create/').status_code,
            HTTPStatus.OK.value
        )

    def test_post_edit_url_exists_author_at_desired_location(self):
        """Проверка доступности страницы /posts/<post_id>/edit/ автору."""
        self.assertEqual(
            self.authorized_client.get(
                f'/posts/{self.post.id}/edit/').status_code,
            HTTPStatus.OK.value
        )

    def test_post_create_url_redirect_anonymous_on_login(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        self.assertRedirects(
            self.guest_client.get('/create/', follow=True),
            '/auth/login/?next=/create/'
        )

    def test_post_edit_url_redirect_anonymous_on_login(self):
        """Страница по адресу /posts/<post_id>/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        self.assertRedirects(
            self.guest_client.get(f'/posts/{self.post.id}/edit/', follow=True),
            (f'/auth/login/?next=/posts/{self.post.id}/edit/')
        )

    def test_posts_url_uses_correct_template(self):
        """Проверка шаблонов для адресов приложения posts."""
        urls_templates_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }
        for url, template in urls_templates_names.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_client.get(url), template)
