from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов приложения about."""
        url_status_codes = {
            '/about/author/': HTTPStatus.OK.value,
            '/about/tech/': HTTPStatus.OK.value,
        }
        for url, status in url_status_codes.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблонов для адресов приложения about."""
        urls_templates_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url, template in urls_templates_names.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.guest_client.get(url), template)


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи namespace, доступен."""
        names_status_codes = {
            reverse('about:author'): HTTPStatus.OK.value,
            reverse('about:tech'): HTTPStatus.OK.value,
        }
        for name, status in names_status_codes.items():
            with self.subTest(name=name):
                self.assertEqual(
                    self.guest_client.get(name).status_code, status)

    def test_about_page_uses_correct_template(self):
        """При запросе к about
        применяются корректные шаблоны."""
        names_templates = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for name, template in names_templates.items():
            with self.subTest(name=name):
                self.assertTemplateUsed(self.guest_client.get(name), template)
