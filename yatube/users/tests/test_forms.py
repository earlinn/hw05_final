from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User

TEST_USERNAME = 'test-user'
TEST_PASSWORD = 'testpassword'


class UserFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_create_user(self):
        """
        Создаётся новый пользователь при заполнении формы
        reverse('users:signup').
        """
        user_count = User.objects.count()
        form_data = {
            'username': TEST_USERNAME,
            'password1': TEST_PASSWORD,
            'password2': TEST_PASSWORD,
        }
        response = self.guest_client.post(
            reverse('users:signup'), data=form_data, follow=True)
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertTrue(User.objects.filter(username=TEST_USERNAME).exists())
