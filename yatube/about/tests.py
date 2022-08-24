from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus


class StaticURLTests(TestCase):
    def test_about_namespaces_uses_correct_template(self):
        """Проверка шаблонов для namespaces приложения about."""
        reverse_names_templates = (
            ('about:author', None, 'about/author.html'),
            ('about:tech', None, 'about/tech.html'),
        )
        for reverse_name, args, template in reverse_names_templates:
            with self.subTest(reverse_name=reverse_name):
                self.assertTemplateUsed(
                    self.client.get(reverse(
                        reverse_name, args=args)), template)

    def test_about_namespaces_matches_correct_urls(self):
        """Проверка namespaces совпадают с hardcod urls приложения about."""
        reverse_names_urls = (
            ('about:author', None, '/about/author/'),
            ('about:tech', None, '/about/tech/'),
        )
        for reverse_name, args, url in reverse_names_urls:
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(reverse(reverse_name, args=args), url)

    def test_about_namespaces_exists_at_desired_location(self):
        """Проверка доступности страниц приложения about."""
        reverse_names = (
            ('about:author', None),
            ('about:tech', None),
        )
        for reverse_name, args in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(
                    self.client.get(reverse(
                        reverse_name, args=args)).status_code,
                    HTTPStatus.OK.value)
