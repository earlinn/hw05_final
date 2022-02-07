import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse
from django import forms

from ..models import Comment, Follow, Group, Post, User

TEST_USERNAME = 'test-user'
TEST_POST_TEXT = 'Тестовый текст поста'
TEST_GROUP_TITLE = 'Тестовая группа'
TEST_GROUP_SLUG = 'test-slug'
TEST_GROUP_DESCRIPTION = 'Тестовое описание группы'
TEST_SECOND_GROUP_TITLE = 'Вторая тестовая группа'
TEST_SECOND_GROUP_SLUG = 'test-slug-2'
TEST_SECOND_GROUP_DESCRIPTION = 'Тестовое описание второй группы'
TEST_COMMENT_TEXT = 'Тестовый текст комментария'
TEST_FOLLOWER_USERNAME = 'test-follower-user'
TEST_FOLLOWING_USERNAME = 'test-following-user'
TEST_FOLLOWER_POST_TEXT = 'Тестовый текст поста Подписчика'
TEST_FOLLOWING_POST_TEXT = 'Тестовый текст поста Автора'
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME)
        cls.group = Group.objects.create(
            title=TEST_GROUP_TITLE,
            slug=TEST_GROUP_SLUG,
            description=TEST_GROUP_DESCRIPTION,
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text=TEST_POST_TEXT,
            author=cls.user,
            group=cls.group,
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text=TEST_COMMENT_TEXT,
        )
        cls.pages_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': TEST_GROUP_SLUG}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': TEST_USERNAME}):
                'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewsTests.post.id}):
                'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': PostViewsTests.post.id}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewsTests.user)

    def test_pages_use_correct_templates(self):
        """URL-адреса используют соответствующие шаблоны."""
        for reverse_name, template in PostViewsTests.pages_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_list_is_1(self):
        """На страницу index передается ожидаемое количество постов."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.context['page_obj'].paginator.count, 1)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post.text, TEST_POST_TEXT)
        self.assertEqual(first_post.author, PostViewsTests.user)
        self.assertEqual(first_post.group, PostViewsTests.group)
        self.assertEqual(first_post.image, PostViewsTests.post.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': TEST_GROUP_SLUG}))
        first_post = response.context['page_obj'][0]
        self.assertEqual(response.context['group'].title, TEST_GROUP_TITLE)
        self.assertEqual(response.context['group'].slug, TEST_GROUP_SLUG)
        self.assertEqual(
            response.context['group'].description, TEST_GROUP_DESCRIPTION)
        self.assertEqual(first_post.text, TEST_POST_TEXT)
        self.assertEqual(first_post.author, PostViewsTests.user)
        self.assertEqual(first_post.group, PostViewsTests.group)
        self.assertEqual(first_post.image, PostViewsTests.post.image)

    def test_post_is_not_in_the_wrong_group(self):
        """
        Пост, принадлежащий к Тестовой группе, не попадёт на страницу второй
        тестовой группы (количество постов во второй тестовой группе = 0).
        """
        self.second_group = Group.objects.create(
            title=TEST_SECOND_GROUP_TITLE,
            slug=TEST_SECOND_GROUP_SLUG,
            description=TEST_GROUP_DESCRIPTION,
        )
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': TEST_SECOND_GROUP_SLUG}))
        self.assertEqual(
            response.context['group'].slug, self.second_group.slug)
        self.assertEqual(response.context['page_obj'].paginator.count, 0)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': TEST_USERNAME}))
        first_post = response.context['page_obj'][0]
        self.assertEqual(response.context['author'].username, TEST_USERNAME)
        self.assertFalse(response.context['following'])
        self.assertEqual(first_post.text, TEST_POST_TEXT)
        self.assertEqual(first_post.author, PostViewsTests.user)
        self.assertEqual(first_post.group, PostViewsTests.group)
        self.assertEqual(first_post.image, PostViewsTests.post.image)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': PostViewsTests.post.id}))
        self.assertEqual(response.context['post'].text, TEST_POST_TEXT)
        self.assertEqual(response.context['post'].author, PostViewsTests.user)
        self.assertEqual(response.context['post'].group, PostViewsTests.group)
        self.assertEqual(
            response.context['post'].image, PostViewsTests.post.image)
        self.assertIsInstance(
            response.context['form'].fields['text'],
            forms.fields.CharField
        )
        self.assertEqual(
            response.context['comments'][0], PostViewsTests.comment)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': PostViewsTests.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['is_edit'], True)
        self.assertEqual(response.context['post'].text, TEST_POST_TEXT)
        self.assertEqual(response.context['post'].author, PostViewsTests.user)
        self.assertEqual(response.context['post'].group, PostViewsTests.group)
        self.assertEqual(
            response.context['post'].image, PostViewsTests.post.image)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsCacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewsCacheTest.user)

    def test_template_cached_index_page_show_correct_context(self):
        """
        Кешированная в шаблоне главная страница показывает новый пост не сразу,
        но после очистки кеша этот пост появляется на главной странице.
        """
        response_first = self.authorized_client.get(reverse('posts:index'))
        Post.objects.create(
            text=TEST_POST_TEXT, author=PostViewsCacheTest.user)
        response_cached = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response_first.context, response_cached.context)
        self.assertEqual(response_first.content, response_cached.content)
        cache.clear()
        response_cleared = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            response_cached.context['page_obj'][0],
            response_cleared.context['page_obj'][0])
        self.assertNotEqual(response_cached.content, response_cleared.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME)
        cls.group = Group.objects.create(
            title=TEST_GROUP_TITLE,
            slug=TEST_GROUP_SLUG,
            description=TEST_GROUP_DESCRIPTION,
        )
        cls.total_posts_count = 13
        cls.first_page_posts_count = 10
        cls.second_page_posts_count = 3
        Post.objects.bulk_create(Post(
            text=f'Тестовый пост {post}', author=cls.user, group=cls.group
        ) for post in range(cls.total_posts_count))

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_first_page_contains_ten_records(self):
        """На первой странице десять постов."""
        paginator_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': TEST_GROUP_SLUG}),
            reverse('posts:profile', kwargs={'username': TEST_USERNAME})
        ]
        for page in paginator_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(
                    len(response.context['page_obj']),
                    PaginatorViewsTest.first_page_posts_count)

    def test_second_page_contains_three_records(self):
        """На второй странице три поста."""
        paginator_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': TEST_GROUP_SLUG}),
            reverse('posts:profile', kwargs={'username': TEST_USERNAME})
        ]
        for page in paginator_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    PaginatorViewsTest.second_page_posts_count)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(
            username=TEST_FOLLOWER_USERNAME)
        cls.following = User.objects.create_user(
            username=TEST_FOLLOWING_USERNAME)
        cls.follower_post = Post.objects.create(
            text=TEST_FOLLOWER_POST_TEXT,
            author=cls.follower,
        )
        cls.following_post = Post.objects.create(
            text=TEST_FOLLOWING_POST_TEXT,
            author=cls.following,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_follower = Client()
        self.authorized_follower.force_login(FollowViewsTest.follower)
        self.authorized_following = Client()
        self.authorized_following.force_login(FollowViewsTest.following)

    def test_authorized_user_can_follow(self):
        """Авторизованный пользователь может подписываться на других."""
        follow_count = Follow.objects.count()
        response_follow = self.authorized_follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': FollowViewsTest.following}
            )
        )
        response_get_following_profile = self.authorized_follower.get(
            reverse(
                'posts:profile',
                kwargs={'username': FollowViewsTest.following}
            )
        )
        self.assertRedirects(
            response_follow,
            reverse(
                'posts:profile', kwargs={'username': FollowViewsTest.following}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=FollowViewsTest.follower,
                author=FollowViewsTest.following
            ).exists()
        )
        self.assertTrue(response_get_following_profile.context['following'])

    def test_authorized_user_can_unfollow(self):
        """Авторизованный пользователь может отписываться от других."""
        Follow.objects.create(
            user=FollowViewsTest.follower, author=FollowViewsTest.following)
        follow_count = Follow.objects.count()
        response_unfollow = self.authorized_follower.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': FollowViewsTest.following}
            )
        )
        self.assertRedirects(
            response_unfollow,
            reverse(
                'posts:profile', kwargs={'username': FollowViewsTest.following}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=FollowViewsTest.follower,
                author=FollowViewsTest.following
            ).exists()
        )
        response_get_unfollowed_profile = self.authorized_follower.get(
            reverse(
                'posts:profile',
                kwargs={'username': FollowViewsTest.following}
            )
        )
        self.assertFalse(response_get_unfollowed_profile.context['following'])

    def test_follow_index_page_shows_correct_context_to_a_follower(self):
        """
        Новая запись пользователя появляется в ленте тех, кто на него подписан.
        """
        # a follower follows an author
        Follow.objects.create(
            user=FollowViewsTest.follower, author=FollowViewsTest.following)
        # the follower hits the follow_index page
        response_follower = self.authorized_follower.get(
            reverse('posts:follow_index'))
        # the follow_index page shows correct context to the follower
        # (the posts of the following author)
        first_post = response_follower.context['page_obj'][0]
        self.assertEqual(first_post.text, TEST_FOLLOWING_POST_TEXT)
        self.assertEqual(first_post.author, FollowViewsTest.following)

    def test_follow_index_page_shows_correct_context_to_a_non_follower(self):
        """
        Новая запись пользователя не появляется в ленте тех,
        кто на него не подписан.
        """
        # the author hits the follow_index page
        response_following = self.authorized_following.get(
            reverse('posts:follow_index'))
        # the follow_index page shows correct context to the author
        # (no posts, because the author doesn't follow anyone)
        self.assertEqual(
            response_following.context['page_obj'].paginator.count, 0)
