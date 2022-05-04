from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()

# Ver.1
# class LoginForm(forms.Form):
#     username = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 'class': 'form-control',
#             }
#         ),
#         label="ID"
#     )
#     password = forms.CharField(
#         widget=forms.PasswordInput(
#             attrs={
#                 'class': 'form-control',
#             }
#         )
#     )


# class SignupForm(forms.Form):
#     username = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 'class': 'form-control',
#             }
#         ),
#         label="ID"
#     )
#     password1 = forms.CharField(
#         widget=forms.PasswordInput(
#             attrs={
#                 'class': 'form-control',
#             }
#         ),
#         label="Password"
#     )
#     # 비밀번호 확인을 위한 필드
#     password2 = forms.CharField(
#         widget=forms.PasswordInput(
#             attrs={
#                 'class': 'form-control',
#             }
#         ),
#         label="Confirm Password"
#     )
    
#     # 닉네임
#     nickname = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 'class': 'form-control',
#             }
#         )
#     )


#     # 이메일 
#     email = forms.EmailField(
#         widget=forms.EmailInput(
#             attrs={
#                 'class': 'form-control',
#             }
#         )
#     )   

#     # username필드의 검증에 id가 이미 사용중인지 여부 검사
#     def clean_username(self):
#         username = self.cleaned_data['username']
#         if User.objects.filter(username=username).exists():
#             raise forms.ValidationError('아이디가 이미 사용중입니다')
#         return username

#     # password1와 password2의 값이 일치하는지 유효성 검사
#     def clean_password2(self):
#         password1 = self.cleaned_data['password1']
#         password2 = self.cleaned_data['password2']
#         if password1 != password2:
#             raise forms.ValidationError('비밀번호와 비밀번호 확인란의 값이 일치하지 않습니다')
#         return password2

#     # email필드의 검증에 email 이미 사용중인지 여부 검사
#     def clean_email(self):
#         email = self.cleaned_data['email']
#         if User.objects.filter(email=email).exists():
#             raise forms.ValidationError('해당 이메일은 이미 사용중입니다')
#         return email

#     # nickname필드의 검증에 nickname이 이미 사용중인지 여부 검사
#     def clean_nickname(self):
#         nickname = self.cleaned_data['nickname']
#         if User.objects.filter(last_name=nickname).exists():
#             raise forms.ValidationError('해당 닉네임은 이미 사용중입니다')
#         return nickname

#     # 자신이 가진 username과 password를 사용해서 유저 생성 후 반환하는 메서드
#     def signup(self):
#         if self.is_valid():
#             return User.objects.create_user(
#                 username=self.cleaned_data['username'],
#                 password=self.cleaned_data['password2'],
#                 last_name=self.cleaned_data['nickname'],
#                 email=self.cleaned_data['email'],
#             )


# Ver.2
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        class_update_fields = ['username', 'password']
        for field_name in class_update_fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control'
            })


class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        class_update_fields = ['password1', 'password2']
        for field_name in class_update_fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = User
        fields = (
            'username',
            'password1',
            'password2',
            'img_profile',
            'nickname',
            'gender',
            'email',
            'birth_date',
        )
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'gender': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'nickname': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'birth_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                }
            )
        }
        labels={
            'img_profile':'프로필 사진',
            'nickname':'별명',
            'gender':'성별',
            'email':'이메일',
        }