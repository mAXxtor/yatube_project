from django.test import TestCase
from django.urls import reverse
from django import forms

from ..forms import CreationForm


class UsersViewTests(TestCase):
    def test_user_signup_page_show_correct_context(self):
        """Шаблон users:singup сформирован с правильным контекстом."""
        response = self.client.get(reverse('users:signup'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], CreationForm)
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
            'password1': forms.fields.CharField,
            'password2': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields[value]
                self.assertIsInstance(form_field, expected)
