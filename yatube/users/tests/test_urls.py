from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.reverse_names = (
            ('users:signup', None),
            ('users:login', None),
            ('users:password_change', None),
            ('users:password_change_done', None),
            ('users:password_reset_form', None),
            ('users:password_reset_done', None),
            ('users:password_reset_confirm', ('uidb64', 'token',)),
            ('users:password_reset_complete', None),
            ('users:logout', None),
        )

    def test_users_namespaces_uses_correct_template(self):
        """Проверка шаблонов для namespaces приложения users."""
        reverse_names_templates = (
            ('users:signup', None, 'users/signup.html'),
            ('users:login', None, 'users/login.html'),
            ('users:password_change', None,
                'users/password_change_form.html'),
            ('users:password_change_done', None,
                'users/password_change_done.html'),
            ('users:password_reset_form', None,
                'users/password_reset_form.html'),
            ('users:password_reset_done', None,
                'users/password_reset_done.html'),
            ('users:password_reset_confirm', ('uidb64', 'token',),
                'users/password_reset_confirm.html'),
            ('users:password_reset_complete', None,
                'users/password_reset_complete.html'),
            ('users:logout', None, 'users/logged_out.html'),
        )
        for reverse_name, args, template in reverse_names_templates:
            with self.subTest(reverse_name=reverse_name):
                self.assertTemplateUsed(
                    self.authorized_client.get(reverse(
                        reverse_name, args=args)), template)

    def test_users_namespaces_matches_correct_urls(self):
        """Проверка namespaces совпадают с hardcod urls приложения users."""
        reverse_names_urls = (
            ('users:signup', None, '/auth/signup/'),
            ('users:login', None, '/auth/login/'),
            ('users:password_change', None, '/auth/password_change/'),
            ('users:password_change_done', None,
                '/auth/password_change/done/'),
            ('users:password_reset_form', None, '/auth/password_reset/'),
            ('users:password_reset_done', None, '/auth/password_reset/done/'),
            ('users:password_reset_confirm', ('uidb64', 'token',),
                '/auth/reset/uidb64/token/'),
            ('users:password_reset_complete', None, '/auth/reset/done/'),
            ('users:logout', None, '/auth/logout/'),
        )
        for reverse_name, args, url in reverse_names_urls:
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(reverse(reverse_name, args=args), url)

    def test_users_pages_available_for_anonymous_and_redirects(self):
        """Проверка доступности страниц приложения users для
        неавторизованных пользователей. Если password_change или
        password_change_done, то редирект на login.
        """
        for reverse_name, args in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                if reverse_name in ['users:password_change',
                                    'users:password_change_done']:
                    redirect_to_login = '/auth/login/?next='
                    redirect_reverse_name = reverse(reverse_name, args=args)
                    self.assertRedirects(
                        self.client.get(reverse(
                            reverse_name, args=args), follow=True),
                        f'{redirect_to_login}{redirect_reverse_name}')
                else:
                    self.assertEqual(
                        self.client.get(reverse(
                            reverse_name, args=args)).status_code,
                        HTTPStatus.OK.value)

    def test_users_pages_available_for_authorized(self):
        """Проверка доступности страниц приложения users для
        авторизованных пользователей.
        """
        for reverse_name, args in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(
                    self.authorized_client.get(reverse(
                        reverse_name, args=args)).status_code,
                    HTTPStatus.OK.value)
