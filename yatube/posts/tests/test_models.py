from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверка корректной работы __str__ моделей."""
        models_str_method = {
            PostModelTest.post: self.post.text[:15],
            PostModelTest.group: self.group.title,
        }
        for model, str_method in models_str_method.items():
            with self.subTest(model=model):
                self.assertEqual(str(model), str_method)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Текст публикации',
            'pub_date': 'Дата публикации',
            'author': 'Автор публикации',
            'group': 'Сообщество',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Введите текст публикации',
            'group': 'Сообщество, к которому будет относиться публикация'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).help_text,
                    expected_value)
