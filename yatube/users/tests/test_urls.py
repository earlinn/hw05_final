from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus

from posts.models import User

TEST_USERNAME = 'test-user'


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.page_reverse_names = [
            reverse('users:login'),
            reverse('users:signup'),
            reverse('users:password_change'),
            reverse('users:password_change_done'),
            reverse('users:password_reset_form'),
            reverse('users:password_reset_done'),
            reverse('users:password_reset_confirm', kwargs={
                'uidb64': 'uidb64', 'token': 'token'}),
            reverse('users:password_reset_complete'),
            reverse('users:logout')
        ]
        cls.pages_templates = {
            reverse('users:login'): 'users/login.html',
            reverse('users:signup'): 'users/signup.html',
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_confirm', kwargs={
                'uidb64': 'uidb64', 'token': 'token'}):
                'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
            reverse('users:logout'): 'users/logged_out.html',
        }

    def setUp(self):
        self.user = User.objects.create_user(username=TEST_USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_exist_at_desired_locations_authorized(self):
        """
        Страницы доступны авторизованному пользователю (возвращают статус 200).
        """
        for page in UserURLTests.page_reverse_names:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Страница {page} недоступна!'
                )

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        for reverse_name, template in UserURLTests.pages_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Проблема с шаблоном на странице {reverse_name}!')
