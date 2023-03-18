from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # fields = '__all__'
        fields = ('text', 'group', 'image',)
        labels = {'image': 'Картинка'}
        help_texts = {'image': 'Загрузите картинку'}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Коментарий'}
        help_text = {'text': 'Ваш коментарий'}
