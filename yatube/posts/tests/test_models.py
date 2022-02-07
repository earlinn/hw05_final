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
        cls.object_as_string = {
            cls.post: cls.post.text[:15],
            cls.group: cls.group.title,
            cls.comment: cls.comment.text,
        }
        cls.field_verboses = {
            cls.post: {
                'text': 'Текст поста',
                'pub_date': 'Дата публикации',
                'author': 'Автор',
                'group': 'Группа',
                'image': 'Картинка',
            },
            cls.comment: {
                'post': 'Пост',
                'author': 'Автор комментария',
                'text': 'Текст комментария',
                'created': 'Дата создания',
            },
        }
        cls.field_help_texts = {
            cls.post: {
                'text': 'Текст нового поста',
                'group': 'Группа, к которой будет относиться пост',
            },
            cls.comment: {
                'text': 'Введите текст комментария',
            },
        }

    def test_models_have_correct_object_names(self):
        """У моделей приложения posts корректно работает __str__."""
        for object, string in PostModelTest.object_as_string.items():
            with self.subTest(object=object):
                self.assertEqual(str(object), string)

    def test_models_verbose_names(self):
        """Verbose name в полях моделей совпадают с ожидаемым."""
        for object, verboses_dict in PostModelTest.field_verboses.items():
            for field, verbose_name in verboses_dict.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        object._meta.get_field(field).verbose_name,
                        verbose_name
                    )

    def test_models_help_texts(self):
        """Help text в полях моделей совпадают с ожидаемым."""
        for object, help_text_dict in PostModelTest.field_help_texts.items():
            for field, help_text in help_text_dict.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        object._meta.get_field(field).help_text,
                        help_text
                    )
