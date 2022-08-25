import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse
from http import HTTPStatus

from ..models import Group, Post
from ..forms import PostForm

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Posts."""
        Post.objects.all().delete()
        test_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='test.gif',
            content=test_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовая публикация',
            'group': self.group.id,
            'image': uploaded,
        }
        self.assertEqual(Post.objects.count(), 0)
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile', args=(self.post.author,)))
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.author, self.user,
                         'Автор редактируемой публикации не совпадает')
        self.assertEqual(post.group.id, form_data['group'],
                         'Сообщество редактируемой публикации не совпадает')
        self.assertEqual(post.text, form_data['text'],
                         'Текст редактируемой публикации не совпадает')
        self.assertEqual(post.image.name, f'posts/{form_data["image"].name}',
                         'Изображение редактируемой публикации не совпадает')

    def test_create_post_form_fields_label(self):
        """Проверка label полей формы создания публикации."""
        title_labels_forms = {
            self.form.fields['text'].label: 'Текст публикации',
            self.form.fields['group'].label: 'Сообщество',
            self.form.fields['image'].label: 'Изображение',
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
            self.form.fields['image'].help_text: 'Добавьте изображение',
        }
        for help_text, form in help_texts_forms.items():
            with self.subTest(help_text=help_text):
                self.assertEquals(help_text, form)

    def test_post_edit(self):
        """При отправке валидной формы со страницы редактирования публикации
        происходит изменение поста с post_id в базе данных.
        """
        test_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='test2.gif',
            content=test_gif,
            content_type='image/gif'
        )
        group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug2',
            description='Тестовое описание 2',
        )
        # Проверка, что публикация одна
        self.assertEqual(Post.objects.count(), 1)
        form_data = {
            'text': 'Публикация 2 отредактирована',
            'group': group2.id,
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        # Проверка, что количество публикаций не изменилось
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.author, self.post.author,
                         'Автор редактируемой публикации не совпадает')
        self.assertEqual(post.group.id, form_data['group'],
                         'Сообщество редактируемой публикации не совпадает')
        self.assertEqual(post.text, form_data['text'],
                         'Текст редактируемой публикации не совпадает')
        self.assertEqual(post.image.name, f'posts/{form_data["image"].name}',
                         'Изображение редактируемой публикации не совпадает')
        # Проверка доступности старой группы после редактирования публикации
        self.assertEqual(self.client.get(
            reverse('posts:group_list', args=(self.group.slug,))).status_code,
            HTTPStatus.OK.value
        )
        # Проверка на пустоту paginator старой группы
        response = self.client.get(
            reverse('posts:group_list', args=(self.group.slug,)))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_post_create_unavailable_anonymous(self):
        """При отправке валидной формы со страницы создания публикации
        неавторизованным пользователем добавление в БД не происходит.
        """
        # Проверка, что публикация одна
        self.assertEqual(Post.objects.count(), 1)
        form_data = {
            'text': 'Публикация 2',
            'group': self.group.id,
        }
        self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверка, что количество публикаций не изменилось
        self.assertEqual(Post.objects.count(), 1)
