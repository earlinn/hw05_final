from django.test import TestCase

from ..models import Comment, Group, Post, User

TEST_USERNAME = 'test-user'
TEST_POST_TEXT = 'Тестовый текст поста'
TEST_GROUP_TITLE = 'Тестовая группа'
TEST_GROUP_SLUG = 'test-slug'
TEST_GROUP_DESCRIPTION = 'Тестовое описание группы'
TEST_COMMENT_TEXT = 'Тестовый текст комментария'


class PostModelTest(TestCase):
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
            author=cls.user,
            text=TEST_POST_TEXT,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text=TEST_COMMENT_TEXT,
        )

    def test_post_have_correct_object_name(self):
        """У модели Post корректно работает __str__."""
        post = PostModelTest.post
        expected_post_name = post.text[:15]
        self.assertEqual(expected_post_name, str(post))

    def test_group_have_correct_object_name(self):
        """У модели Group корректно работает __str__."""
        group = PostModelTest.group
        expected_group_name = group.title
        self.assertEqual(expected_group_name, str(group))

    def test_comment_have_correct_object_name(self):
        """У модели Comment корректно работает __str__."""
        comment = PostModelTest.comment
        expected_comment_name = comment.text
        self.assertEqual(expected_comment_name, str(comment))

    def test_post_verbose_name(self):
        """Verbose_name в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_comment_verbose_name(self):
        """Verbose_name в полях модели Comment совпадает с ожидаемым."""
        comment = PostModelTest.comment
        field_verboses = {
            'post': 'Пост',
            'author': 'Автор комментария',
            'text': 'Текст комментария',
            'created': 'Дата создания',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected)

    def test_post_help_text(self):
        """Help_text в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_comment_help_text(self):
        """Help_text в полях модели Comment совпадает с ожидаемым."""
        comment = PostModelTest.comment
        self.assertEqual(
            comment._meta.get_field('text').help_text,
            'Введите текст комментария'
        )
