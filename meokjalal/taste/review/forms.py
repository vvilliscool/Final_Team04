from msilib.schema import RadioButton
from django import forms

from .models import Comment, Review

from django_starfield import Stars


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            'content',
        )
        widgets = {
            'content': forms.TextInput(
                attrs={
                    'class': 'content',
                    'placeholder': '댓글 달기...',
                }
            )
        }


    def clean_content(self):
        data = self.cleaned_data['content']
        errors = []
        if data == '':
            errors.append(forms.ValidationError('댓글 내용을 입력해주세요'))
        elif len(data) > 50:
            errors.append(forms.ValidationError('댓글 내용은 50자 이하로 입력해주세요'))
        if errors:
            raise forms.ValidationError(errors)
        return data




class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = (
            'photo',
            'content',
            'service',
            'taste',
            'cleaned',
            'price',
        )
        widgets = {
            'service':Stars,
            'taste':Stars,
            'cleaned':Stars,
            'price':Stars,
        }
        labels={
            'service':'서비스',
            'taste':'맛',
            'cleaned':'위생상태',
            'price':'가격',
        }