from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from http import HTTPStatus

from posts.models import Group, Post

User = get_user_model()


class UsersURLTests(TestCase):
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

    def test_public_users_urls_exists_at_desired_location(self):
        """Проверка доступности страниц приложения users для
        неавторизованных пользователей.
        """
        urls_status_codes = {
            '/auth/signup/': HTTPStatus.OK.value,
            '/auth/login/': HTTPStatus.OK.value,
            '/auth/password_reset/': HTTPStatus.OK.value,
            '/auth/password_reset/done/': HTTPStatus.OK.value,
            '/auth/reset/some_uidb64/some_token/': HTTPStatus.OK.value,
            '/auth/reset/done/': HTTPStatus.OK.value,
            '/auth/logout/': HTTPStatus.OK.value,
        }
        for url, status in urls_status_codes.items():
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest_client.get(url).status_code, status)

    def test_password_change_url_exists_authorized_at_desired_location(self):
        """Проверка доступности страницы /password_change/ авторизованному
        пользователю.
        """
        self.assertEqual(
            self.authorized_client.get('/auth/password_change/').status_code,
            HTTPStatus.OK.value
        )

    def test_password_change_done_url_exists_authorized(self):
        """Проверка доступности страницы /password_change/done/ авторизованному
        пользователю.
        """
        self.assertEqual(
            self.authorized_client.get(
                '/auth/password_change/done/').status_code,
            HTTPStatus.OK.value
        )

    def test_password_change_url_redirect_anonymous_on_login(self):
        """Страница по адресу /password_change/ перенаправит анонимного
        пользователя на страницу логина.
        """
        self.assertRedirects(
            self.guest_client.get('/auth/password_change/', follow=True),
            '/auth/login/?next=/auth/password_change/'
        )

    def test_password_change_done_url_redirect_anonymous_on_login(self):
        """Страница по адресу /password_change/done/ перенаправит анонимного
        пользователя на страницу логина.
        """
        self.assertRedirects(
            self.guest_client.get('/auth/password_change/done/', follow=True),
            ('/auth/login/?next=/auth/password_change/done/')
        )

    def test_users_url_uses_correct_template(self):
        """Проверка шаблонов для адресов приложения users."""
        urls_templates_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/some_uidb64/some_token/':
                'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for url, template in urls_templates_names.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_client.get(url), template)
