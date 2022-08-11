from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': 'Текст публикации',
            'group': 'Сообщество'
        }
        help_texts = {
            'text': 'Введите текст публикации',
            'group': 'Сообщество, к которой будет относиться публикация'
        }
