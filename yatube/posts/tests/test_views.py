import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse
from django import forms

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая публикация',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def post_view_test(self, request, bool=False):
        if bool is True:
            context = request.context['post']
        else:
            context = request.context['page_obj'][0]
        context_fields = {
            context.author: self.post.author,
            context.pub_date: self.post.pub_date,
            context.text: self.post.text,
            context.group: self.post.group,
            context.image: self.post.image,
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        # Проверка количества постов в базе
        self.assertEqual(Post.objects.count(), 1)
        response = self.authorized_client.get(reverse('posts:index'))
        # Проверка вывода публикаций на страницу index
        self.assertEqual(len(response.context['page_obj']), 1)
        # Проверка контекста шаблона
        self.post_view_test(response)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        # Проверка количества постов в базе
        self.assertEqual(Post.objects.count(), 1)
        response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.group.slug,)))
        # Проверка контекста шаблона group_list
        self.post_view_test(response)
        self.assertEqual(response.context['group'], self.group)
        # Проверка вывода публикаций на страницу group_list
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        # Проверка количества постов в базе
        self.assertEqual(Post.objects.count(), 1)
        response = self.authorized_client.get(
            reverse('posts:profile', args=(self.user.username,)))
        # Проверка контекста шаблона profile
        self.post_view_test(response)
        self.assertEqual(response.context['author'], self.post.author)
        self.assertEqual(response.context['profile_posts'].count(), 1)
        # Проверка вывода публикаций на страницу profile
        user2 = User.objects.create_user(username='auth2')
        self.assertEqual(len(response.context['page_obj']), 1)
        response = self.client.get(
            reverse('posts:profile', args=(user2.username,)))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        # Проверка количества постов в базе
        self.assertEqual(Post.objects.count(), 1)
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=(self.post.id,)))
        # Проверка контекста шаблона post_detail
        self.post_view_test(response, True)

    def test_post_create_and_post_edit_page_show_correct_context(self):
        """Шаблон post_create и post_edit
        сформирован с правильным контекстом.
        """
        # Проверка форм post_create и post_edit
        post_create_edit_names = (
            ('posts:post_create', None),
            ('posts:post_edit', (self.post.id,))
        )
        for reverse_name, args in post_create_edit_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(
                    reverse(reverse_name, args=args))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], PostForm)
                # Проверка полей форм post_create и post_edit
                form_fields = {
                    'text': forms.fields.CharField,
                    'group': forms.fields.ChoiceField,
                    'image': forms.fields.ImageField,
                }
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get('form').fields[value]
                        self.assertIsInstance(form_field, expected)

    def test_post_create_with_group_show_correct_context(self):
        """Если при создании публикации указать группу, то публикация
        появляется на главной странице сайта, на странице выбранной группы,
        в профайле пользователя.
        """
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        Post.objects.create(
            author=self.user,
            text='Тестовая публикация 2',
            group=self.group,
        )
        self.assertEqual(Post.objects.count(), 1)
        group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug2',
            description='Тестовое описание 2',
        )
        response = self.client.get(
            reverse('posts:group_list', args=(group2.slug,)))
        self.assertEqual(len(response.context['page_obj']), 0)
        self.assertEqual(Post.objects.first().group, self.group)
        response = self.client.get(
            reverse('posts:group_list', args=(self.group.slug,)))
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_index_page_show_correct_context(self):
        """Проверка cache страницы index."""
        cached_response_content = self.authorized_client.get(
            reverse('posts:index'))
        self.assertEqual(Post.objects.count(), 1)
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        self.assertEqual(cached_response_content.content, self.authorized_client.get(
            reverse('posts:index')).content)
        cache.clear()
        self.assertNotEqual(cached_response_content.content, self.authorized_client.get(
            reverse('posts:index')).content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.NUMBER_OF_TEST_POSTS = 13
        Post.objects.bulk_create([
            Post(
                author=cls.user,
                text=f'Тестовый пост {post_num}',
                group=cls.group,
            )
            for post_num in range(cls.NUMBER_OF_TEST_POSTS)
        ])

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator_pages_contains_correct_count_of_records(self):
        """Проверка paginator: количество постов
        на первой странице равно 10, на второй 3.
        """
        posts_namespaces = (
            ('posts:index', None),
            ('posts:group_list', (self.group.slug,)),
            ('posts:profile', (self.user.username,)),
        )
        paginator_pages_posts_numbers = (
            ('?page=1', settings.NUMBER_OF_POSTS),
            ('?page=2', self.NUMBER_OF_TEST_POSTS - settings.NUMBER_OF_POSTS)
        )
        for name, args in posts_namespaces:
            with self.subTest(name=name):
                for page, posts_number in paginator_pages_posts_numbers:
                    with self.subTest(page=page):
                        response = self.client.get(
                            reverse(name, args=args) + page)
                        self.assertEqual(
                            len(response.context['page_obj']), posts_number)
