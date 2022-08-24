from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class CreationFormTests(TestCase):
    def test_user_signup(self):
        """При заполнении формы users:signup
        создаётся новый пользователь.
        """
        form_data = {
            'first_name': 'TestName',
            'last_name': 'TestSurname',
            'username': 'TestUsername',
            'email': 'test@email.ru',
            'password1': 'testpassword',
            'password2': 'testpassword'
        }
        self.assertEqual(User.objects.count(), 0)
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), 1)
        test_user = User.objects.first()
        self.assertEqual(test_user.first_name, form_data['first_name'],
                         'First_name пользователя не совпадает')
        self.assertEqual(test_user.last_name, form_data['last_name'],
                         'Last_name пользователя не совпадает')
        self.assertEqual(test_user.username, form_data['username'],
                         'Username пользователя не совпадает')
        self.assertEqual(test_user.email, form_data['email'],
                         'Email пользователя не совпадает')
