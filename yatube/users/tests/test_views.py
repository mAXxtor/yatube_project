from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from http import HTTPStatus

from posts.models import Group, Post

User = get_user_model()


class UsersViewTests(TestCase):
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

    def test_users_namespaces_exists_at_desired_location(self):
        """Проверка доступности страниц приложения users по URL,
        генерируемому при помощи namespace.
        """
        names_status_codes = {
            reverse('users:signup'): HTTPStatus.OK.value,
            reverse('users:login'): HTTPStatus.OK.value,
            reverse('users:password_change'): HTTPStatus.OK.value,
            reverse('users:password_change_done'): HTTPStatus.OK.value,
            reverse('users:password_reset_form'): HTTPStatus.OK.value,
            reverse('users:password_reset_done'): HTTPStatus.OK.value,
            reverse('users:password_reset_confirm', args=('uid64', 'token')):
                HTTPStatus.OK.value,
            reverse('users:password_reset_complete'): HTTPStatus.OK.value,
            reverse('users:logout'): HTTPStatus.OK.value,
        }
        for name, status in names_status_codes.items():
            with self.subTest(name=name):
                self.assertEqual(
                    self.authorized_client.get(name).status_code, status)

    def test_users_namespaces_uses_correct_template(self):
        """Проверка шаблонов для namespaces приложения users."""
        reverse_names_templates = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_confirm', args=('uid64', 'token')):
                'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        for reverse_name, template in reverse_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertTemplateUsed(
                    self.authorized_client.get(reverse_name), template)

    def test_user_signup_page_show_correct_context(self):
        """Шаблон users:singup сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields[value]
                self.assertIsInstance(form_field, expected)
