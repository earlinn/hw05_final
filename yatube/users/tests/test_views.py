from django.test import Client, TestCase
from django.urls import reverse
from django import forms


class UsersViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_signup_page_context_contains_creation_form(self):
        """
        На страницу signup в контексте передаётся форма для создания
        нового пользователя.
        """
        response = self.guest_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
