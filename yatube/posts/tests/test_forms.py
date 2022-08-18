from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from ..forms import PostForm

User = get_user_model()


class PostCreateFormTests(TestCase):
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
            text='Тестовая публикация 1',
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Posts."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовая публикация 2',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={'author': 'auth'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user.id,
                text=f'{form_data["text"]}',
                group=self.group.id
            ).exists()
        )

    def test_create_post_form_fields_label(self):
        """Проверка label полей формы создания публикации."""
        title_labels_forms = {
            self.form.fields['text'].label: 'Текст публикации',
            self.form.fields['group'].label: 'Сообщество',
        }
        for label, form in title_labels_forms.items():
            with self.subTest(label=label):
                self.assertEquals(label, form)

    def test_create_post_form_fields_help_text(self):
        """Проверка help_text полей формы создания публикации."""
        help_texts_forms = {
            self.form.fields['text'].help_text: 'Введите текст публикации',
            self.form.fields['group'].help_text:
                'Сообщество, к которому будет относиться публикация',
        }
        for help_text, form in help_texts_forms.items():
            with self.subTest(help_text=help_text):
                self.assertEquals(help_text, form)

    def test_create_post(self):
        """При отправке валидной формы со страницы редактирования поста
        происходит изменение поста с post_id в базе данных.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Публикация 2 отредактирована',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args=(f'{posts_count}',)),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                author=self.user.id,
                text=f'{form_data["text"]}',
                group=self.group.id
            ).exists()
        )
