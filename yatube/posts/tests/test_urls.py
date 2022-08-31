from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus

from ..models import Comment, Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
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
        cls.comment = Comment.objects.create(
            post= cls.post,
            author= cls.user,
            text= 'Тестовый комментарий',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.reverse_names = (
            ('posts:index', None),
            ('posts:group_list', (self.group.slug,)),
            ('posts:profile', (self.user.username,)),
            ('posts:post_detail', (self.post.id,)),
            ('posts:post_create', None),
            ('posts:post_edit', (self.post.id,)),
            ('posts:follow_index', None),
        )

    def test_post_namespaces_uses_correct_template(self):
        """Проверка шаблонов для namespaces приложения posts."""
        reverse_names_templates = (
            ('posts:index', None, 'posts/index.html'),
            ('posts:group_list', (self.group.slug,), 'posts/group_list.html'),
            ('posts:profile', (self.user.username,), 'posts/profile.html'),
            ('posts:post_detail', (self.post.id,), 'posts/post_detail.html'),
            ('posts:post_create', None, 'posts/create_post.html'),
            ('posts:post_edit', (self.post.id,), 'posts/create_post.html'),
            ('posts:follow_index', None, 'posts/follow.html'),
        )
        for reverse_name, args, template in reverse_names_templates:
            with self.subTest(reverse_name=reverse_name):
                self.assertTemplateUsed(
                    self.authorized_client.get(reverse(
                        reverse_name, args=args)), template)

    def test_404_page_available(self):
        """Проверка доступности страницы 404."""
        self.assertEqual(
            self.client.get('unexisting_page/').status_code,
            HTTPStatus.NOT_FOUND.value)

    def test_404_page_uses_correct_template(self):
        """Страница 404 использует кастомный шаблон."""
        self.assertTemplateUsed(
            self.client.get('unexisting_page/'),
            'core/404.html')

    def test_posts_namespaces_matches_correct_urls(self):
        """Проверка namespaces совпадают с hardcod urls приложения posts."""
        reverse_names_urls = (
            ('posts:index', None, '/'),
            ('posts:group_list', (self.group.slug,),
                f'/group/{self.group.slug}/'),
            ('posts:profile', (self.user.username,),
                f'/profile/{self.user.username}/'),
            ('posts:post_detail', (self.post.id,), f'/posts/{self.post.id}/'),
            ('posts:post_create', None, '/create/'),
            ('posts:post_edit', (self.post.id,),
                f'/posts/{self.post.id}/edit/'),
            ('posts:follow_index', None, '/follow/'),
        )
        for reverse_name, args, url in reverse_names_urls:
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(reverse(reverse_name, args=args), url)

    def test_posts_namespaces_available_for_author_at_desired_location(self):
        """Проверка доступности страниц для автора."""
        for reverse_name, args in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(
                    self.authorized_client.get(reverse(
                        reverse_name, args=args)).status_code,
                    HTTPStatus.OK.value)

    def test_posts_names_available_for_nonauthor_and_redirects(self):
        """Проверка доступности страниц для неавтора.
        Если post_edit то редирект на post_detail.
        """
        user2 = User.objects.create_user(username='test_user')
        self.authorized_client.force_login(user2)
        for reverse_name, args in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                if reverse_name == 'posts:post_edit':
                    self.assertRedirects(
                        self.authorized_client.get(
                            reverse(reverse_name, args=args), follow=True),
                        reverse('posts:post_detail', args=(self.post.id,)))
                else:
                    self.assertEqual(
                        self.authorized_client.get(reverse(
                            reverse_name, args=args)).status_code,
                        HTTPStatus.OK.value)

    def test_posts_names_available_for_anonymous_and_redirects(self):
        """Проверка доступности страниц для неавторизоавнного пользователя.
        Если post_create или post_edit то редирект на login. Если follow_index
        то 302 статус.
        """
        for reverse_name, args in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                if reverse_name in ['posts:post_create', 'posts:post_edit']:
                    redirect_to_login = reverse('users:login')
                    redirect_reverse_name = reverse(reverse_name, args=args)
                    self.assertRedirects(
                        self.client.get(
                            reverse(reverse_name, args=args), follow=True),
                        f'{redirect_to_login}?next={redirect_reverse_name}')
                elif reverse_name == 'posts:follow_index':
                    self.assertEqual(self.client.get(
                        reverse(reverse_name, args=args)).status_code,
                        HTTPStatus.FOUND.value)
                else:
                    self.assertEqual(self.client.get(
                        reverse(reverse_name, args=args)).status_code,
                        HTTPStatus.OK.value)
