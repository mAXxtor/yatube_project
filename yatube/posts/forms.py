from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст публикации',
            'group': 'Сообщество',
            'image': 'Изображение'
        }
        help_texts = {
            'text': 'Введите текст публикации',
            'group': 'Сообщество, к которому будет относиться публикация',
            'image': 'Добавьте изображение'
        }
