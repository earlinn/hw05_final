from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus

from ..models import Group, Post, User

TEST_USERNAME = 'test-user'
TEST_POST_TEXT = 'Тестовый текст поста'
TEST_GROUP_TITLE = 'Тестовая группа'
TEST_GROUP_SLUG = 'test-slug'
TEST_GROUP_DESCRIPTION = 'Тестовое описание группы'
TEST_USER_NON_AUTHOR_USERNAME = 'test-empty-user'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME)
        cls.group = Group.objects.create(
            title=TEST_GROUP_TITLE,
            slug=TEST_GROUP_SLUG,
            description=TEST_GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=TEST_POST_TEXT,
            author=cls.user,
            group=cls.group
        )
        cls.public_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': TEST_GROUP_SLUG}),
            reverse('posts:profile', kwargs={'username': TEST_USERNAME}),
            reverse('posts:post_detail', kwargs={
                'post_id': PostURLTests.post.id})
        ]
        cls.pages_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': TEST_GROUP_SLUG}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': TEST_USERNAME}):
                'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': PostURLTests.post.id}):
                'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': PostURLTests.post.id}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def test_public_pages_exist_at_desired_locations(self):
        """
        Общедоступные страницы доступны любому пользователю
        (возвращают статус 200).
        """
        for page in PostURLTests.public_pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Страница {page} недоступна!'
                )

    def test_post_create_page_exists_at_desired_location_authorized(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_page_redirect_anonymous_on_login_page(self):
        """
        Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get(
            reverse('posts:post_create'), follow=True)
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next={reverse('posts:post_create')}")

    def test_post_edit_page_exists_at_desired_location_author(self):
        """Страница /<post_id>/edit/ доступна автору поста."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit', kwargs={'post_id': PostURLTests.post.id}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_page_redirect_non_author_on_post_detail_page(self):
        """
        Страница /<post_id>/edit/ перенаправит пользователя, не являющегося
        автором поста, на страницу с информацией о данном посте.
        """
        non_author_user = User.objects.create_user(
            username=TEST_USER_NON_AUTHOR_USERNAME)
        non_author_client = Client()
        non_author_client.force_login(non_author_user)
        response = non_author_client.get(
            reverse(
                'posts:post_edit', kwargs={'post_id': PostURLTests.post.id}),
            follow=True)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail', kwargs={'post_id': PostURLTests.post.id}))

    def test_post_edit_page_redirect_anonymous_on_login_page(self):
        """
        Страница /<post_id>/edit/ перенаправит анонимного пользователя
        на страницу логина.
        """
        post_edit_page = reverse(
            'posts:post_edit', kwargs={'post_id': PostURLTests.post.id})
        response = self.guest_client.get(post_edit_page, follow=True)
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next={post_edit_page}")

    def test_unexisting_page_is_unavailable(self):
        """Несуществующая страница недоступна (возвращает статус 404)."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_comment_page_redirect_anonymous_on_login_page(self):
        """
        Страница /<post_id>/comment/ перенаправит анонимного пользователя
        на страницу логина.
        """
        post_comment_page = reverse(
            'posts:add_comment', kwargs={'post_id': PostURLTests.post.id})
        response = self.guest_client.get(post_comment_page, follow=True)
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next={post_comment_page}")

    def test_follow_index_page_exists_at_desired_location_authorized(self):
        """Страница /follow/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_follow_index_page_redirect_anonymous_on_login_page(self):
        """
        Страница /follow/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get(
            reverse('posts:follow_index'), follow=True)
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next={reverse('posts:follow_index')}")

    def test_profile_follow_page_redirects_anonymous_on_login_page(self):
        """
        Страница /profile/<str:username>/follow/ перенаправит
        анонимного пользователя на страницу логина.
        """
        profile_follow_page = reverse(
            'posts:profile_follow', kwargs={'username': PostURLTests.user})
        response = self.guest_client.get(profile_follow_page, follow=True)
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next={profile_follow_page}"
        )

    def test_profile_unfollow_page_redirects_anonymous_on_login_page(self):
        """
        Страница /profile/<str:username>/unfollow/ перенаправит
        анонимного пользователя на страницу логина.
        """
        profile_unfollow_page = reverse(
            'posts:profile_unfollow', kwargs={'username': PostURLTests.user})
        response = self.guest_client.get(profile_unfollow_page, follow=True)
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next={profile_unfollow_page}"
        )

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        for reverse_name, template in PostURLTests.pages_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
