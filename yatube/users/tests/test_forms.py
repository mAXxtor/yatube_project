from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import CreationForm

User = get_user_model()


class CreationFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.form = CreationForm()

    def setUp(self):
        self.guest_client = Client()

    def test_create_post(self):
        """При заполнении формы reverse('users:signup')
        создаётся новый пользователь.
        """
        users_count = User.objects.count()
        form_data = {
            'first_name': 'TestName',
            'last_name': 'TestSurname',
            'username': 'TestUsername',
            'email': 'test@email.ru',
            'password1': 'testpassword',
            'password2': 'testpassword'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name=f'{form_data["first_name"]}',
                last_name=f'{form_data["last_name"]}',
                username=f'{form_data["username"]}',
                email=f'{form_data["email"]}'
            ).exists()
        )
