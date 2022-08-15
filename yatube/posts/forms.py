from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        data = self.cleaned_data['text']
        character_number = 20
        if len(data) < character_number:
            raise forms.ValidationError(
                f'Минимальная длина сообщения {character_number} символов.'
            )
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        data = self.cleaned_data['text']
        character_number = 5
        if len(data) < character_number:
            raise forms.ValidationError(
                f'Минимальная длина комментария {character_number} символов.'
            )
        return data
