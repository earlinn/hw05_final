from django.test import TestCase
from http import HTTPStatus


class ViewTests(TestCase):
    def test_404_error_page(self):
        """
        Сервер возвращает код 404 и использует кастомный шаблон,
        если страница не найдена.
        """
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
