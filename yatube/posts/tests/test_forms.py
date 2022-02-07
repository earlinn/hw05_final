import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from ..forms import CommentForm, PostForm
from ..models import Comment, Post, User

TEST_USERNAME = 'test-user'
TEST_POST_TEXT = 'Тестовый текст поста'
TEST_POST_NEW_TEXT = 'Новый текст поста'
TEST_COMMENT_TEXT = 'Тестовый текст комментария'
TEST_IMAGE = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00'
    b'\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
    b'\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME)
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_create_post(self):
        """
        Валидная форма создаёт новую запись Post в базе данных,
        затем происходит перенаправление на страницу профиля.
        """
        post_count = Post.objects.count()
        small_gif = TEST_IMAGE
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': TEST_POST_TEXT,
            'author': PostFormTests.user,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': TEST_USERNAME})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=TEST_POST_TEXT,
                author=PostFormTests.user,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма изменяет пост с post_id в базе данных."""
        self.existing_post = Post.objects.create(
            text=TEST_POST_TEXT, author=PostFormTests.user)
        post_count = Post.objects.count()
        very_small_gif = TEST_IMAGE
        uploaded = SimpleUploadedFile(
            name='very_small.gif',
            content=very_small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': TEST_POST_NEW_TEXT,
            'author': PostFormTests.user,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': self.existing_post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.existing_post.id}))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                text=TEST_POST_NEW_TEXT,
                author=PostFormTests.user,
                image='posts/very_small.gif'
            ).exists()
        )


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME)
        cls.post = Post.objects.create(text=TEST_POST_TEXT, author=cls.user)
        cls.form = CommentForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(CommentFormTests.user)

    def test_create_comment(self):
        """
        Валидная форма создаёт новый Comment в базе данных,
        затем происходит перенаправление на страницу информации о посте.
        """
        comment_count = Comment.objects.count()
        form_data = {
            'text': TEST_COMMENT_TEXT,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': CommentFormTests.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': CommentFormTests.post.id}
            )
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=TEST_COMMENT_TEXT,
            ).exists()
        )
