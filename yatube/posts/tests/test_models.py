from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):

    def test_models_have_correct_object_names(self):
        """В модели Post корректно работает __str__."""
        long_post = Post(
            text='Не более 15 символов может уместиться в превью'
        )
        post = Post(text='Короткий пост')
        self.assertEqual(str(long_post), 'Не более 15 сим')
        self.assertEqual(str(post), 'Короткий пост')

    def test_models_have_correct_object_names2(self):
        """В модели Group корректно работает __str__."""
        group = Group(title="Тестовая группа")
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_verbose_name(self):
        """Корректный verbose_name у полей модели Post."""
        def test_verbose_name_values(field):
            return Post._meta.get_field(field).verbose_name
        self.assertEqual(test_verbose_name_values('text'), 'Текст поста_v')
        self.assertEqual(test_verbose_name_values('group'), 'Группа_v')
        self.assertEqual(test_verbose_name_values('author'),
                         'Автор публикации_v')

    def test_help_text(self):
        """Корректный help_text у полей модели Post."""
        def test_help_text_values(field):
            return Post._meta.get_field(field).help_text
        self.assertEqual(test_help_text_values('text'),
                         'Введите текст поста_h')
        self.assertEqual(test_help_text_values('group'),
                         'Группа, к которой будет относиться пост_h')

    # def test_verbose_name_values(self):
    #     """Корректный verbose_name у полей модели Post."""
    #     field_values = {
    #         'text': 'Текст поста_v',
    #         'author': 'Автор публикации_v',
    #         'group': 'Группа_v',
    #     }
    #     for field, value in field_values.items():
    #         with self.subTest(field=field):
    #             verbose = Post._meta.get_field(field).verbose_name
    #             self.assertEqual(verbose, value)

    # def test_help_text_values(self):
    #     """Корректный help_text у полей модели Post."""
    #     field_values = {
    #         'text': 'Введите текст поста_h',
    #         'group': 'Группа, к которой будет относиться пост_h',
    #     }
    #     for field, value in field_values.items():
    #         with self.subTest(field=field):
    #             help_text = Post._meta.get_field(field).help_text
    #             self.assertEqual(help_text, value)
