from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..models import Group, Post

User = get_user_model()


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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_namespaces_uses_correct_template(self):
        """Проверка шаблонов для namespaces приложения posts."""
        reverse_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}):
            'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'author':
                            f'{self.user.username}'}):
            'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'}):
            'posts/create_post.html',
        }
        for reverse_name, template in reverse_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertTemplateUsed(
                    self.authorized_client.get(reverse_name), template)

    def test_index_page_show_correct_context(self):
        """Шаблон index и posts/includes/post_card сформирован
        с правильным контекстом.
        """
        post2 = Post.objects.create(
            author=self.user,
            text='Тестовый пост 2',
            group=self.group,
        )
        # Проверка контекста шаблона
        response = self.authorized_client.get(reverse('posts:index'))
        second_object = response.context['page_obj'][1]
        context_fields = {
            f'{second_object.author.get_full_name}':
                f'{self.post.author.get_full_name}',
            f'{second_object.pub_date}': f'{self.post.pub_date}',
            f'{second_object.text}': f'{self.post.text}',
            f'{second_object.id}': f'{self.post.id}',
            f'{second_object.group.slug}': f'{self.post.group.slug}',
            f'{second_object.group.title}': f'{self.post.group.title}',
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)
        # Проверка вывода публикаций на страницу index
        posts_on_index = response.context.get('page_obj').object_list
        self.assertEqual(posts_on_index, [post2, self.post])

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        # Проверка контекста шаблона group_list
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}))
        context_fields = {
            f'{response.context["group"].title}': f'{self.group.title}',
            f'{response.context["group"].description}':
                f'{self.group.description}',
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)
        # Проверка вывода публикаций на страницу group_list
        group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug2',
            description='Тестовое описание 2',
        )
        post2 = Post.objects.create(
            author=self.user,
            text='Тестовый пост 2',
            group=group2,
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{group2.slug}'}))
        group_posts = response.context.get('page_obj').object_list
        self.assertEqual(group_posts, [post2])

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        # Проверка контекста шаблона profile
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'author': f'{self.user.username}'}))
        context_author = response.context['author']
        context_profile_posts = response.context['profile_posts']
        context_fields = {
            f'{context_author.get_full_name}':
                f'{self.post.author.get_full_name}',
            f'{context_profile_posts.count()}': '1',
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)
        # Проверка вывода публикаций на страницу profile
        user2 = User.objects.create_user(username='auth2')
        post2 = Post.objects.create(
            author=user2,
            text='Тестовый пост 2',
            group=self.group,
        )
        response = self.guest_client.get(
            reverse('posts:profile',
                    kwargs={'author': f'{user2.username}'}))
        user2_posts = response.context.get('page_obj').object_list
        self.assertEqual(user2_posts, [post2])

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        # Проверка контекста шаблона post_detail
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}))
        context_post = response.context['post']
        context_fields = {
            f'{context_post}': f'{self.post.__str__}',
            f'{context_post.pub_date}': f'{self.post.pub_date}',
            f'{context_post.group.slug}': f'{self.post.group.slug}',
            f'{context_post.group.title}': f'{self.post.group.title}',
            f'{context_post.author}': f'{self.post.author}',
            f'{context_post.author.get_full_name}':
                f'{self.post.author.get_full_name}',
            f'{context_post.author.posts.count()}':
                f'{self.post.author.posts.count()}',
            f'{context_post.text}': f'{self.post.text}',
            f'{context_post.pk}': f'{self.post.id}',
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)
        # Проверка вывода публикации на страницу post_detail
        post2 = Post.objects.create(
            author=self.user,
            text='Тестовый пост 2',
            group=self.group,
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{post2.id}'}))
        self.assertEqual(response.context.get('post'), post2)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        # В контекст шаблона post_edit передается корректная форма
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields[value]
                self.assertIsInstance(form_field, expected)
        # В контекст шаблона post_edit передаются данные редактериуемого поста
        group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug2',
            description='Тестовое описание 2',
        )
        post2 = Post.objects.create(
            author=self.user,
            text='Тестовый пост 2',
            group=group2,
        )
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{post2.id}'}))
        form_fields = {
            'text': f'{post2.text}',
            'group': group2.id,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').initial[value]
                self.assertEqual(form_field, expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        # В контекст шаблона post_create передается корректная форма
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_create_with_group_exists_at_desired_location(self):
        """Если при создании публикации указать группу, то публикация
        появляется на главной странице сайта, на странице выбранной группы,
        в профайле пользователя.
        """
        group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug2',
            description='Тестовое описание 2',
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовая публикация 2',
            'group': group2.id,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Созданная публикация появляется на главной странице
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            response.context['page_obj'][0], Post.objects.filter(id=2)[0])
        # Созданная публикация появляется на странице выбранной группы
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{group2.slug}'}))
        self.assertEqual(
            response.context['page_obj'][0], Post.objects.filter(id=2)[0])
        # Созданная публикация появляется на странице профайла пользователя
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'author': f'{self.user.username}'}))
        self.assertEqual(
            response.context['page_obj'][0], Post.objects.filter(id=2)[0])
        # Публикация не попала в чужую группу
        self.assertFalse(
            Post.objects.filter(id=2) in Post.objects.filter(group=1))


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
        number_of_posts = 13
        for post_num in range(number_of_posts):
            Post.objects.create(
                author=cls.user,
                text='Тестовый пост %s' % post_num,
                group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_pages_contains_ten_records(self):
        """Проверка paginator: количество постов
        на первой странице равно 10.
        """
        response_index = self.guest_client.get(reverse('posts:index'))
        response_group_list = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}))
        response_profile = self.guest_client.get(
            reverse('posts:profile',
                    kwargs={'author': f'{self.user.username}'}))
        page_response_paginator = {
            response_index: 10,
            response_group_list: 10,
            response_profile: 10,
        }
        for value, expected in page_response_paginator.items():
            with self.subTest(value=value):
                self.assertEqual(len(value.context['page_obj']), expected)

    def test_second_page_contains_three_records(self):
        """Проверка paginator: количество постов на второй странице равно 3."""
        response_index = self.guest_client.get(
            reverse('posts:index') + '?page=2')
        response_group_list = self.guest_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}) + '?page=2')
        response_profile = self.guest_client.get(
            reverse('posts:profile',
                    kwargs={'author': f'{self.user.username}'}) + '?page=2')
        page_response_paginator = {
            response_index: 3,
            response_group_list: 3,
            response_profile: 3,
        }
        for value, expected in page_response_paginator.items():
            with self.subTest(value=value):
                self.assertEqual(len(value.context['page_obj']), expected)
